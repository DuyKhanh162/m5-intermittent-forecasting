# -*- coding: utf-8 -*-
"""harness.py — Bước 6-9: đọc mọi forecast -> metric theo model×nhóm -> nhãn thắng/tương đương.

Sở hữu: **P5** (P1 seed skeleton + phần rolling/win-rule vì đồng sở hữu bước 8).

Luồng đầy đủ (khi có forecast của >=3 cửa sổ từ P3/P4):
  1. Với MỖI cửa sổ rolling: đọc forecast từng model (format MỐI NỐI #2), join actuals + segment.
  2. Tính metric mỗi chuỗi: RMSSE, SPL/WSPL, coverage  ->  `src.common.metrics` (P5 hoàn thiện).
  3. (tuỳ chọn) hiệu chuẩn conformal đồng nhất  ->  `src.common.calibration` (P5).
  4. Tổng hợp 2 bảng: balanced-per-segment & frequency-weighted.
  5. Áp win-rule qua các cửa sổ + kiểm định DM/MCB (`src.evaluation.significance`) -> nhãn.

File này CHƯA chạy ra kết quả cuối vì phụ thuộc forecast của P3/P4 (bước 5) + metric của P5
(bước 6-7). P1 giao sẵn: interface + logic rolling/win-rule + hàm nạp forecast đa cửa sổ.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.common import schema
from src.data import splits
from src.evaluation import significance


# ----------------------------------------------------------- nạp forecast
def load_forecasts(forecasts_dir: str | Path, window_tag: str | None = None) -> dict[str, pd.DataFrame]:
    """Đọc mọi file *.parquet trong thư mục forecast -> {model_name: DataFrame}.

    window_tag: nếu forecast lưu theo cửa sổ (vd 'W1'), lọc theo hậu tố tên file
    `<model>__<window_tag>.parquet`. None = đọc tất cả (bố cục pilot 1 cửa sổ).
    """
    d = Path(forecasts_dir)
    out: dict[str, pd.DataFrame] = {}
    for f in sorted(d.glob("*.parquet")):
        stem = f.stem
        if window_tag is not None:
            if not stem.endswith(f"__{window_tag}"):
                continue
            model = stem[: -len(f"__{window_tag}")]
        else:
            model = stem
        df = pd.read_parquet(f)
        schema.assert_forecast_schema(df) if "model" in df.columns else None
        out[model] = df
    return out


def build_actuals(long_df: pd.DataFrame, window: splits.Window) -> pd.DataFrame:
    """Bảng actuals cho phần test của một cửa sổ: series_id, d_int, actual, segment."""
    _, _, test = splits.split_long(long_df, window)
    return (test[[schema.SERIES_KEY, schema.DAY_INT_KEY, schema.TARGET, "segment"]]
            .rename(columns={schema.TARGET: "actual"})
            .reset_index(drop=True))


# ----------------------------------------------- win-rule qua nhiều cửa sổ
def apply_win_rule(per_window_metrics: pd.DataFrame, metric_col: str = "SPL",
                   loss_by_series: dict | None = None) -> pd.DataFrame:
    """Gắn nhãn thắng/tương đương cho từng nhóm, tổng hợp qua các cửa sổ.

    per_window_metrics: cột tối thiểu [window, model, segment, <metric_col>]
        (metric trung bình mỗi (cửa sổ, model, nhóm), thấp = tốt).
    loss_by_series (tuỳ chọn): {(segment): (loss_matrix, model_names)} để chạy MCB;
        nếu có, dùng MCB để xác định "significant_worse"; nếu không, chỉ dùng margin + #cửa sổ.

    Trả về bảng theo nhóm: winner, runner_up, margin_%, n_windows, verdict.
    """
    n_windows = per_window_metrics["window"].nunique()
    rows = []
    for seg, g in per_window_metrics.groupby("segment"):
        # metric trung bình qua các cửa sổ cho từng model
        mean_metric = g.groupby("model")[metric_col].mean().sort_values()
        if mean_metric.empty:
            continue
        winner, best = mean_metric.index[0], mean_metric.iloc[0]
        if len(mean_metric) > 1:
            runner_up, rval = mean_metric.index[1], mean_metric.iloc[1]
            margin = 100 * (rval - best) / best if best > 0 else np.nan
        else:
            runner_up, margin = "-", np.nan

        p_value = None
        if loss_by_series and seg in loss_by_series:
            M, names = loss_by_series[seg]
            res = significance.mcb(M, names)
            # p-value xấp xỉ: dùng cờ significant_worse của á quân so với best
            worse = res.set_index("model")["significant_worse"]
            p_value = 0.01 if worse.get(runner_up, False) else 0.5

        v = significance.verdict(margin_pct=margin or 0.0, p_value=p_value,
                                 n_windows=n_windows)
        rows.append(dict(segment=seg, winner=winner, runner_up=runner_up,
                         margin_pct=round(margin, 1) if pd.notna(margin) else np.nan,
                         n_windows=n_windows, verdict=v))
    return (pd.DataFrame(rows)
            .set_index("segment").reindex(schema.SEGMENTS).dropna(how="all").reset_index())


# ---------------------------------------------------------------- orchestrator (TODO P5)
def run_full_evaluation(*args, **kwargs):  # pragma: no cover
    """TODO (P5): ghép các mảnh trên với metrics.py + calibration.py để ra:
      - 2 bảng model×nhóm (balanced & frequency-weighted), mỗi bảng raw + calibrated;
      - bảng 'model thắng theo nhóm' kèm p-value/nhãn;
      - error analysis + biểu đồ forecast vs actual.
    Xem docstring đầu file cho luồng đầy đủ.
    """
    raise NotImplementedError(
        "run_full_evaluation là phần P5 hoàn thiện (cần metrics.py + forecast >=3 cửa sổ)."
    )
