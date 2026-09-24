# -*- coding: utf-8 -*-
"""classical.py — Bước 5A: mô hình cổ điển cho nhu cầu gián đoạn.

Sở hữu: **P4**. STUB interface — code tham chiếu trong notebook §5 (cell 5.1-5.3).

Họ model: Naive, SeasonalNaive(7) (tự cài, luôn có); Croston, SBA, TSB (statsforecast/Nixtla).
  - Croston: tách chuỗi thành CỠ bán & KHOẢNG cách, làm mượt riêng; dự báo = cỡ / khoảng cách.
  - SBA = Croston sửa thiên lệch (nhân 1 - alpha/2).
  - TSB = cập nhật XÁC SUẤT có bán mỗi ngày (bắt hàng "chết dần").
Mọi point forecast -> 9 quantile bằng NB (src.common.calibration.point_to_quantiles),
rồi BẮT BUỘC qua split_conformal chung (đồng sở hữu P5). NB không còn là bước cuối.

Output: outputs/forecasts/{naive,snaive,croston,sba,tsb}.parquet qua forecast_io.write_forecast.
"""
from __future__ import annotations

import pandas as pd

from src.data.splits import Window


def forecast(long_df: pd.DataFrame, window: Window, cfg: dict | None = None) -> dict[str, pd.DataFrame]:
    """TODO (P4): sinh point forecast cho từng model cổ điển rồi bung NB -> 9 quantile.

    Trả về {model_name: forecast_long (MỐI NỐI #2)}. Xem notebook §5.1-5.3.
    """
    raise NotImplementedError("P4: xem notebook M5_..._study.ipynb §5 (cell 5.1-5.3).")
