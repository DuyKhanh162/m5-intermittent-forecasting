# -*- coding: utf-8 -*-
"""calibration.py — Giao thức xác suất công bằng (bước 6).

Sở hữu: **P5** (đồng sở hữu với P4). Hai phần:

  1. point_to_quantiles() — BASELINE (từ pilot): bung point forecast -> 9 quantile bằng
     phân phối Negative Binomial (dispersion theo chuỗi). Dùng cho model điểm (Naive,
     SeasonalNaive, Croston/SBA/TSB, TTM). Đây là bước sinh quantile "thô".

  2. split_conformal() — STUB (P5 hoàn thiện): hiệu chuẩn conformal đồng nhất cho MỌI model
     trên cửa sổ validation, để coverage so sánh được và tách năng lực model khỏi "lớp bọc".
     Báo cáo cả bản raw lẫn calibrated (PLAN_REVISED §5, CHANGELOG mục 3-nối).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from src.common import schema


def fit_nb_dispersion(train_hist: pd.DataFrame) -> dict:
    """Ước lượng dispersion r theo chuỗi từ insample: r = m^2/(v-m) nếu v>m, ngược lại Poisson (inf)."""
    mv = train_hist.groupby(schema.SERIES_KEY)[schema.TARGET].agg(["mean", "var"])

    def _r(row):
        m, v = row["mean"], row["var"]
        return (m * m / (v - m)) if (v > m and m > 0) else np.inf

    return mv.apply(_r, axis=1).to_dict()


def point_to_quantiles(point_df: pd.DataFrame, model: str, disp_r: dict,
                       quantiles: list[float] | None = None) -> pd.DataFrame:
    """point_df: [series_id, date, d_int, value(mean)] -> long 9 quantile (NB/Poisson).

    Trả về format MỐI NỐI #2: [series_id, date, d_int, quantile_level, value, model].
    """
    quantiles = quantiles or schema.load_config()["quantiles"]
    pf = point_df.copy()
    pf["value"] = pf["value"].clip(lower=0).astype(float)
    pf["r"] = pf[schema.SERIES_KEY].map(disp_r).fillna(np.inf)
    mu = pf["value"].to_numpy()
    r = pf["r"].to_numpy()
    finite = np.isfinite(r) & (r > 0)

    out = []
    for u in quantiles:
        qv = np.empty_like(mu)
        if finite.any():
            rr, mm = r[finite], mu[finite]
            p = rr / (rr + np.where(mm > 0, mm, 1e-9))
            qv[finite] = stats.nbinom.ppf(u, rr, p)
        if (~finite).any():
            qv[~finite] = stats.poisson.ppf(u, mu[~finite])
        block = pf[[schema.SERIES_KEY, schema.DATE_KEY, schema.DAY_INT_KEY]].copy()
        block["quantile_level"] = u
        block["value"] = np.nan_to_num(qv, nan=0.0)
        block["model"] = model
        out.append(block)
    return pd.concat(out, ignore_index=True)[schema.FORECAST_COLS]


def split_conformal(*args, **kwargs):  # pragma: no cover
    """TODO (P5): split-conformal calibration đồng nhất trên validation cho MỌI model.

    Ý tưởng: dùng residual/score trên cửa sổ validation để điều chỉnh độ rộng dải sao cho
    coverage danh nghĩa khớp thực tế (distribution-free). Áp CÙNG một thủ tục cho tất cả
    model (kể cả LightGBM native & Chronos kẹp đuôi) -> so sánh coverage công bằng.
    """
    raise NotImplementedError(
        "split_conformal là phần P5 hoàn thiện (bước 6). Xem PLAN_REVISED §5 giao thức xác suất."
    )
