# -*- coding: utf-8 -*-
"""foundation.py — Bước 5C: Foundation Models (zero-shot, chạy trên mẫu).

Sở hữu: **P4**. STUB interface — code tham chiếu trong notebook §6 (cell 6.1-6.3).

Model (pretrained sẵn, chạy zero-shot, KHÔNG train lại trên M5):
  - Chronos-Bolt (base): ra quantile native, gọi
    `predict_quantiles(inputs=..., prediction_length=..., quantile_levels=...)`.
    LƯU Ý: kẹp đuôi [0.1, 0.9] -> đuôi cực (0.005/0.995) bị ngoại suy, nhờ conformal sửa.
  - TTM (IBM Granite): ra ĐIỂM -> bọc NB (calibration.point_to_quantiles). context 512, PL 96 cắt 28.
  - Moirai-2: STRETCH GOAL (ra quantile native).

CẢNH BÁO RÒ RỈ PRE-TRAINING (chính, không phụ): Chronos/TTM nhiều khả năng đã "thấy" M5 khi
pretrain -> điểm zero-shot có thể bị thổi lên. Mọi kết luận FM phải kèm cảnh báo này.
Few-shot (tuỳ chọn, cần GPU): ablation phụ, ưu tiên TTM rồi Moirai. Đo runtime mỗi FM.

Output: outputs/forecasts/{chronos_bolt,ttm,...}.parquet qua forecast_io.write_forecast.
"""
from __future__ import annotations

import pandas as pd

from src.data.splits import Window


def forecast(long_df: pd.DataFrame, window: Window, cfg: dict | None = None) -> dict[str, pd.DataFrame]:
    """TODO (P4): chạy Chronos-Bolt + TTM zero-shot trên mẫu, đo runtime.

    Trả về {model_name: forecast_long (MỐI NỐI #2)}. Xem notebook §6.1-6.3.
    """
    raise NotImplementedError("P4: xem notebook M5_..._study.ipynb §6 (cell 6.1-6.3).")
