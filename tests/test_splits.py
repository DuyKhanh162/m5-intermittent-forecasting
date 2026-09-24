# -*- coding: utf-8 -*-
"""Kiểm tra bước 4: rolling-origin không rò rỉ, đúng horizon, nằm trong actuals."""
import pandas as pd
import pytest

from src.common import schema
from src.data import splits


def test_rolling_has_at_least_3_windows():
    ws = splits.rolling_windows()
    assert len(ws) >= 3


def test_windows_no_leakage_and_horizon():
    cfg = schema.load_config()
    h = cfg["horizon"]
    max_day = cfg["split"]["max_actual_day"]
    for w in splits.rolling_windows():
        splits.assert_no_leakage(w, h)
        assert w.train_end < w.val_end < w.test_start <= w.test_end
        assert len(w.test_days) == h
        assert w.test_end <= max_day          # không vượt actuals có sẵn


def test_windows_do_not_overlap_on_test():
    ws = splits.rolling_windows()
    spans = [(w.test_start, w.test_end) for w in ws]
    for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
        assert e2 < s1          # cửa sổ sau nằm hoàn toàn trước cửa sổ trước


def test_split_long_partitions_by_dint():
    # long giả: 1 chuỗi, d_int 1..1941
    df = pd.DataFrame({
        schema.SERIES_KEY: ["s"] * 1941,
        schema.DAY_INT_KEY: range(1, 1942),
        schema.TARGET: [1.0] * 1941,
        "segment": ["smooth"] * 1941,
    })
    w = splits.rolling_windows()[0]
    tr, va, te = splits.split_long(df, w)
    assert tr[schema.DAY_INT_KEY].max() == w.train_end
    assert va[schema.DAY_INT_KEY].min() == w.train_end + 1
    assert te[schema.DAY_INT_KEY].min() == w.test_start
    assert te[schema.DAY_INT_KEY].max() == w.test_end
    # không giao nhau
    assert set(tr[schema.DAY_INT_KEY]) & set(te[schema.DAY_INT_KEY]) == set()
