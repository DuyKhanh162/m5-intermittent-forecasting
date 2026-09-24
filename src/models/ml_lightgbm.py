# -*- coding: utf-8 -*-
"""ml_lightgbm.py — Bước 5B: LightGBM global quantile (Machine Learning).

Sở hữu: **P3**. STUB interface — code tham chiếu đã có trong notebook §4 (cell 4.1-4.2).

Nhiệm vụ P3:
  - Feature leak-free: lag >= HORIZON (28,35,56), rolling kết thúc ở lag-28,
    days-since-last-sale (shift 28), calendar (wday/month/event/snap), giá + price_chg.
    BẪY LEAK: lag < horizon khiến ngày test cần dữ liệu chưa biết -> BẮT BUỘC lag >= 28.
  - Global model: 1 model học chung mọi chuỗi, phân biệt qua feature.
  - 9 quantile bằng quantile regression native (objective='quantile', alpha=level),
    ép không giao nhau (sort theo quantile). -> KHÔNG cần bọc NB.
  - Xuất raw + calibrated (qua src.common.calibration.split_conformal, đồng bộ P5).

Output: outputs/forecasts/lgbm.parquet (+ lgbm_cal.parquet), qua src.common.forecast_io.write_forecast.
"""
from __future__ import annotations

import pandas as pd

from src.data.splits import Window


def build_features(long_df: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """TODO (P3): sinh feature leak-free. Xem notebook §4.1."""
    raise NotImplementedError("P3: xem notebook M5_..._study.ipynb §4.1 (cell 4.1).")


def forecast(long_df: pd.DataFrame, window: Window, cfg: dict | None = None) -> pd.DataFrame:
    """TODO (P3): train 9 model quantile + dự báo test của `window`.

    Trả về forecast long theo MỐI NỐI #2 (dùng forecast_io.write_forecast để lưu).
    Xem notebook §4.2 (cell 4.2).
    """
    raise NotImplementedError("P3: xem notebook §4.2.")
