# -*- coding: utf-8 -*-
"""significance.py — Bước 8: kiểm định độ chênh mô hình (win rule).

Sở hữu: P1 (đồng sở hữu bước 8 với P5). Hàm THUẦN THỐNG KÊ — nhận mảng loss, không I/O.

Vì sao cần: pilot 1 cửa sổ chênh 2-3% nằm trong nhiễu -> không phân biệt được model.
Win rule: chỉ gọi một model "thắng" một nhóm khi chênh lệch **sống sót qua >=3 cửa sổ
rolling-origin VÀ qua một kiểm định (DM hoặc MCB)**. Mặc định là "tương đương".

Hai kiểm định:
  - Diebold-Mariano (DM): so 1 CẶP model trên cùng tập loss. Có hiệu chỉnh HLN cho mẫu nhỏ.
  - MCB (Multiple Comparison with the Best): so NHIỀU model qua thứ hạng trung bình,
    dùng khoảng tới hạn Nemenyi để biết model nào khác biệt có ý nghĩa so với model tốt nhất.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


# --------------------------------------------------------------- Diebold-Mariano
def diebold_mariano(loss_a, loss_b, h: int = 1) -> tuple[float, float]:
    """DM test cho 2 chuỗi loss (thấp = tốt), cùng độ dài.

    Trả về (dm_stat, p_value) hai phía. Quy ước: dm_stat > 0 nghĩa là loss_a > loss_b
    trung bình -> **model B tốt hơn**; dm_stat < 0 -> model A tốt hơn.
    Áp hiệu chỉnh Harvey-Leybourne-Newbold cho mẫu nhỏ; dùng phân phối t (df = n-1).
    """
    d = np.asarray(loss_a, dtype=float) - np.asarray(loss_b, dtype=float)
    d = d[np.isfinite(d)]
    n = len(d)
    if n < 2:
        return np.nan, np.nan
    dbar = d.mean()

    def autocov(k: int) -> float:
        return np.sum((d[k:] - dbar) * (d[: n - k] - dbar)) / n

    var_d = autocov(0) + 2.0 * sum(autocov(k) for k in range(1, h))
    if var_d <= 0:
        return np.nan, np.nan
    dm = dbar / np.sqrt(var_d / n)
    # hiệu chỉnh HLN
    corr = np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    dm_hln = dm * corr
    p = 2.0 * stats.t.cdf(-abs(dm_hln), df=n - 1)
    return float(dm_hln), float(p)


# --------------------------------------------------------------- MCB (Nemenyi)
def _nemenyi_q(k: int, alpha: float) -> float:
    """Giá trị tới hạn q cho Nemenyi = studentized range / sqrt(2), df = inf."""
    q = stats.studentized_range.ppf(1 - alpha, k, np.inf)
    return q / np.sqrt(2.0)


def mcb(loss_matrix, model_names: list[str], alpha: float = 0.05) -> pd.DataFrame:
    """MCB dựa trên thứ hạng trung bình (Nemenyi).

    loss_matrix: mảng (N_items, K_models), thấp = tốt (mỗi hàng 1 chuỗi/quan sát,
    mỗi cột 1 model). Hàng có NaN bị loại (cần cùng tập item cho mọi model).

    Trả về DataFrame theo model: mean_rank, best (bool), critical_distance,
    diff_vs_best (rank_model - rank_best), significant_worse (diff > CD).
    Model có mean_rank thấp nhất = tốt nhất.
    """
    M = np.asarray(loss_matrix, dtype=float)
    if M.ndim != 2 or M.shape[1] != len(model_names):
        raise ValueError("loss_matrix phải là (N_items, K_models) khớp model_names.")
    mask = np.all(np.isfinite(M), axis=1)
    M = M[mask]
    N, K = M.shape
    if N < 2 or K < 2:
        raise ValueError(f"Cần >=2 item và >=2 model (đang N={N}, K={K}).")

    # thứ hạng trong từng hàng (1 = tốt nhất = loss thấp nhất), trung bình cho ties
    ranks = np.apply_along_axis(stats.rankdata, 1, M)
    mean_rank = ranks.mean(axis=0)
    best_idx = int(np.argmin(mean_rank))
    cd = _nemenyi_q(K, alpha) * np.sqrt(K * (K + 1) / (6.0 * N))

    diff = mean_rank - mean_rank[best_idx]
    out = pd.DataFrame({
        "model": model_names,
        "mean_rank": mean_rank,
        "best": [i == best_idx for i in range(K)],
        "critical_distance": cd,
        "diff_vs_best": diff,
        "significant_worse": diff > cd,
    }).sort_values("mean_rank").reset_index(drop=True)
    out.attrs["n_items"] = N
    return out


# ------------------------------------------------------ win-rule (kết hợp rolling + test)
def verdict(margin_pct: float, p_value: float | None,
            n_windows: int, min_windows: int = 3,
            alpha: float = 0.05, margin_th: float = 5.0) -> str:
    """Gắn nhãn theo win rule.

    "thắng rõ"  : đủ >=min_windows cửa sổ VÀ (p_value < alpha) VÀ margin >= margin_th.
    "tương đương": còn lại (mặc định — chênh vài % không phải thắng).
    "chưa đủ dữ liệu": ít hơn min_windows cửa sổ (không được kết luận).
    """
    if n_windows < min_windows:
        return "chưa đủ dữ liệu"
    sig = (p_value is not None) and np.isfinite(p_value) and (p_value < alpha)
    if sig and abs(margin_pct) >= margin_th:
        return "thắng rõ"
    return "tương đương"
