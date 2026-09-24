# -*- coding: utf-8 -*-
"""Kiểm tra MỐI NỐI #2: forecast_io round-trip + validate schema."""
import numpy as np
import pandas as pd
import pytest

from src.common import schema, forecast_io


def _toy_forecast():
    return pd.DataFrame({
        schema.SERIES_KEY: ["s1", "s1"],
        schema.DATE_KEY: pd.to_datetime(["2016-05-23", "2016-05-23"]),
        schema.DAY_INT_KEY: [1914, 1914],
        "quantile_level": [0.5, 0.9],
        "value": [1.0, 2.0],
        "model": ["toy", "toy"],
    })


def test_write_read_roundtrip(tmp_path):
    df = _toy_forecast()
    p = forecast_io.write_forecast(df, tmp_path / "toy.parquet")
    back = forecast_io.read_forecast(p)
    assert list(back.columns) == schema.FORECAST_COLS
    assert len(back) == 2


def test_write_rejects_missing_column(tmp_path):
    bad = _toy_forecast().drop(columns=["quantile_level"])
    with pytest.raises(ValueError):
        forecast_io.write_forecast(bad, tmp_path / "bad.parquet")


def test_quantile_array_to_long_shape():
    quant = np.zeros((2, 3, 9))          # 2 series, horizon 3, 9 quantile
    q = schema.load_config()["quantiles"]
    df = forecast_io.quantile_array_to_long(
        quant, ["a", "b"], pd.to_datetime(["2016-05-23"] * 3),
        [1914, 1915, 1916], q, "m")
    assert len(df) == 2 * 3 * 9
    assert list(df.columns) == schema.FORECAST_COLS
    schema.assert_forecast_schema(df)
