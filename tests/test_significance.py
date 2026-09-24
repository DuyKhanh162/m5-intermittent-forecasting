# -*- coding: utf-8 -*-
"""Kiểm định bước 8: Diebold-Mariano + MCB + win-rule."""
import numpy as np
import pytest

from src.evaluation import significance as sig


def test_dm_detects_clear_winner():
    """Model B loss thấp hơn hẳn -> DM có ý nghĩa, dm_stat > 0 (A tệ hơn)."""
    rng = np.random.RandomState(0)
    loss_a = rng.normal(1.0, 0.1, 200)
    loss_b = rng.normal(0.5, 0.1, 200)
    dm, p = sig.diebold_mariano(loss_a, loss_b)
    assert p < 0.01
    assert dm > 0            # loss_a > loss_b => B tốt hơn


def test_dm_equal_models_not_significant():
    """Hai model gần như trùng loss -> không có ý nghĩa."""
    rng = np.random.RandomState(1)
    base = rng.normal(1.0, 0.1, 200)
    loss_a = base + rng.normal(0, 1e-4, 200)
    loss_b = base + rng.normal(0, 1e-4, 200)
    _, p = sig.diebold_mariano(loss_a, loss_b)
    assert p > 0.05


def test_dm_too_short_returns_nan():
    dm, p = sig.diebold_mariano([1.0], [0.5])
    assert np.isnan(dm) and np.isnan(p)


def test_mcb_ranks_best_lowest_loss():
    """3 model: C < B < A về loss -> C best, mean_rank C nhỏ nhất."""
    rng = np.random.RandomState(2)
    N = 300
    A = rng.normal(3.0, 0.5, N)
    B = rng.normal(2.0, 0.5, N)
    C = rng.normal(1.0, 0.5, N)
    M = np.column_stack([A, B, C])
    res = sig.mcb(M, ["A", "B", "C"])
    assert res.iloc[0]["model"] == "C"
    assert res.iloc[0]["best"]
    # A khác biệt có ý nghĩa so với best
    assert res.set_index("model").loc["A", "significant_worse"]
    assert res.attrs["n_items"] == N


def test_mcb_tied_models_not_significant():
    """Ba model gần như trùng -> không cái nào significant_worse."""
    rng = np.random.RandomState(3)
    base = rng.normal(1.0, 0.5, 300)
    M = np.column_stack([base + rng.normal(0, 1e-3, 300) for _ in range(3)])
    res = sig.mcb(M, ["m1", "m2", "m3"])
    assert not res["significant_worse"].any()


def test_verdict_rules():
    assert sig.verdict(6.0, 0.01, n_windows=3) == "thắng rõ"
    assert sig.verdict(2.0, 0.01, n_windows=3) == "tương đương"   # chênh nhỏ
    assert sig.verdict(6.0, 0.20, n_windows=3) == "tương đương"   # không ý nghĩa
    assert sig.verdict(6.0, 0.01, n_windows=1) == "chưa đủ dữ liệu"
