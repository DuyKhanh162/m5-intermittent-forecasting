# -*- coding: utf-8 -*-
"""metrics.py — Bộ đo chung: RMSSE, SPL/WSPL, coverage.

Sở hữu: **P5**. Đây là bản BASELINE lift từ pilot (đã kiểm chứng) để cả nhóm chạy được ngay.
P5 mở rộng: WSPL dollar-weighted chuẩn M5 Uncertainty, tích hợp calibration, hookup MCB/DM,
2 bảng tổng hợp (balanced & frequency-weighted). Xem PLAN_REVISED §5, §7.

Quy ước: mọi metric THẤP = tốt (trừ coverage: gần mức danh nghĩa = tốt).
Metric chính: RMSSE (điểm), WSPL (xác suất, dollar-weighted), Coverage (hiệu chuẩn).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common import schema

# Cặp quantile đối xứng -> mức phủ danh nghĩa (dùng cho coverage)
COV_PAIRS = [(0.25, 0.75, 0.50), (0.165, 0.835, 0.67),
             (0.025, 0.975, 0.95), (0.005, 0.995, 0.99)]


def insample_scales(train_hist: pd.DataFrame) -> pd.DataFrame:
    """Scale naive-1 kiểu M5 cho từng chuỗi (tính từ lần bán đầu tiên).

    train_hist: long [series_id, d_int, sales]. Trả về DataFrame index=series_id,
    cột scale_rmsse (MSE naive) & scale_mae (MAE naive).
    """
    def _scales(y: np.ndarray):
        nz = np.nonzero(y)[0]
        if len(nz) < 2:
            return np.nan, np.nan
        y = y[nz[0]:]
        d = np.diff(y)
        if len(d) == 0:
            return np.nan, np.nan
        return float(np.mean(d ** 2)), float(np.mean(np.abs(d)))

    rows = {}
    for sid, g in train_hist.sort_values(schema.DAY_INT_KEY).groupby(schema.SERIES_KEY):
        rows[sid] = _scales(g[schema.TARGET].to_numpy(dtype=np.float64))
    return pd.DataFrame(rows, index=["scale_rmsse", "scale_mae"]).T


def dollar_weights(long_df: pd.DataFrame, val_end: int, lookback: int = 28) -> pd.Series:
    """Trọng số WSPL = doanh số (sales*price) `lookback` ngày insample cuối, chuẩn hoá tổng=1."""
    win = long_df[(long_df.d_int > val_end - lookback) & (long_df.d_int <= val_end)].copy()
    win["dollar"] = win[schema.TARGET] * win["sell_price"].fillna(0)
    w = win.groupby(schema.SERIES_KEY)["dollar"].sum()
    return w / w.sum() if w.sum() > 0 else w


def pinball(actual: np.ndarray, q: np.ndarray, level: float) -> float:
    """Pinball (quantile) loss trung bình cho một mức quantile."""
    return float(np.mean(np.maximum(level * (actual - q), (level - 1) * (actual - q))))


def evaluate(forecast_df: pd.DataFrame, actual_df: pd.DataFrame,
             scales: pd.DataFrame, quantiles: list[float] | None = None,
             weights: pd.Series | None = None) -> pd.DataFrame:
    """Tính metric mỗi chuỗi cho MỘT model.

    forecast_df: long [series_id, d_int, quantile_level, value, ...].
    actual_df: [series_id, d_int, actual, segment].
    Trả về DataFrame theo series_id: segment, model, RMSSE, SPL, weight, cov50/67/95/99.
    """
    quantiles = quantiles or schema.load_config()["quantiles"]
    model = forecast_df["model"].iloc[0] if "model" in forecast_df else "?"
    piv = (forecast_df.pivot_table(index=[schema.SERIES_KEY, schema.DAY_INT_KEY],
                                   columns="quantile_level", values="value").reset_index())
    m = piv.merge(actual_df, on=[schema.SERIES_KEY, schema.DAY_INT_KEY], how="inner")

    rows = []
    for sid, g in m.groupby(schema.SERIES_KEY):
        a = g["actual"].to_numpy(dtype=float)
        sr = scales["scale_rmsse"].get(sid, np.nan)
        sm = scales["scale_mae"].get(sid, np.nan)
        p50 = g[0.5].to_numpy(dtype=float) if 0.5 in g else np.full_like(a, np.nan)
        rmsse = np.sqrt(np.mean((a - p50) ** 2) / sr) if (sr and sr > 0) else np.nan
        spls = [pinball(a, g[u].to_numpy(float), u) / sm
                for u in quantiles if u in g and sm and sm > 0]
        spl = float(np.mean(spls)) if spls else np.nan
        covs = {}
        for lo, hi, nom in COV_PAIRS:
            if lo in g and hi in g:
                inside = ((a >= g[lo].to_numpy()) & (a <= g[hi].to_numpy())).mean()
                covs[f"cov{int(nom*100)}"] = float(inside)
        w = float(weights.get(sid, np.nan)) if weights is not None else np.nan
        rows.append(dict(series_id=sid, segment=g["segment"].iloc[0], model=model,
                         RMSSE=rmsse, SPL=spl, weight=w, **covs))
    return pd.DataFrame(rows)
