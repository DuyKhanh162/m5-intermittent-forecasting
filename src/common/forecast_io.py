# -*- coding: utf-8 -*-
"""forecast_io.py — Đọc/ghi forecast theo MỐI NỐI #2 (format chung của cả nhóm).

Sở hữu: P1. Mọi model (P3/P4) PHẢI xuất forecast qua `write_forecast` để đảm bảo cùng
format: (series_id, date, d_int, quantile_level, value, model). P5 đọc qua `read_forecast`.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.common import schema


def write_forecast(df: pd.DataFrame, path: str | Path) -> Path:
    """Kiểm tra schema rồi ghi parquet. Trả về đường dẫn đã ghi."""
    schema.assert_forecast_schema(df)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df[schema.FORECAST_COLS].to_parquet(path, index=False)
    return path


def read_forecast(path: str | Path) -> pd.DataFrame:
    """Đọc parquet forecast và kiểm tra schema."""
    df = pd.read_parquet(path)
    schema.assert_forecast_schema(df)
    return df


def quantile_array_to_long(quant_arr: np.ndarray, series_ids: list[str],
                           dates, d_ints, quantile_levels: list[float],
                           model: str) -> pd.DataFrame:
    """Chuyển mảng quantile (n_series, horizon, n_quantiles) -> long format chuẩn.

    dates, d_ints: độ dài = horizon (chung cho mọi chuỗi trong cửa sổ).
    """
    n_series, horizon, nq = quant_arr.shape
    assert horizon == len(dates) == len(d_ints)
    assert nq == len(quantile_levels)
    rows = []
    for i, sid in enumerate(series_ids):
        for h in range(horizon):
            for j, u in enumerate(quantile_levels):
                rows.append((sid, dates[h], d_ints[h], u,
                             max(0.0, float(quant_arr[i, h, j])), model))
    return pd.DataFrame(rows, columns=schema.FORECAST_COLS)
