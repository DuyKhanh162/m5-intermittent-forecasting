# -*- coding: utf-8 -*-
"""sbc.py — Bước 2-3: phân nhóm demand theo SBC (Syntetos-Boylan-Croston).

Sở hữu: **P2**. Đây là bản BASELINE chạy được (P1 seed sẵn để sinh artifact bàn giao
ngay: segment_labels full 30.490 + sample_ids). P2 mở rộng: EDA, tinh chỉnh quy tắc
lấy mẫu, 2 góc báo cáo (balanced & frequency-weighted), nhãn cho bước 9.

Ý tưởng: đo bài toán trên 2 chiều —
  - ADI (Average Demand Interval): khoảng cách TB giữa 2 lần bán != 0 -> độ gián đoạn.
  - CV^2: phương sai tương đối của CỠ bán (chỉ tính trên các kỳ != 0) -> độ loạn.
Cắt tại ADI=1.32, CV^2=0.49 -> 4 nhóm smooth / erratic / intermittent / lumpy.

Chỉ dùng phần TRAIN để tính (tránh rò rỉ). Tính vectorised trên ma trận wide,
KHÔNG melt toàn bộ 30.490 chuỗi (tiết kiệm bộ nhớ).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.common import schema


def compute_adi_cv2(sales_wide: pd.DataFrame, train_days: list[str]) -> pd.DataFrame:
    """Tính ADI, CV^2, zero_rate cho từng chuỗi từ ma trận wide (chỉ phần train).

    sales_wide: DataFrame gốc M5 (mỗi hàng 1 chuỗi, có ID_COLS + các cột d_*).
    Trả về DataFrame: series_id + ID_COLS + [n_nonzero, zero_rate, ADI, CV2].
    """
    mat = sales_wide[train_days].to_numpy(dtype=np.float32)   # (n_series, n_train_days)
    T = mat.shape[1]

    nonzero = mat > 0
    n_nonzero = nonzero.sum(axis=1)
    sum_nz = np.where(nonzero, mat, 0).sum(axis=1)
    mean_nz = np.divide(sum_nz, n_nonzero, out=np.zeros_like(sum_nz), where=n_nonzero > 0)
    sq = np.where(nonzero, mat ** 2, 0).sum(axis=1)
    var_nz = np.divide(sq, n_nonzero, out=np.zeros_like(sq), where=n_nonzero > 0) - mean_nz ** 2
    std_nz = np.sqrt(np.clip(var_nz, 0, None))

    with np.errstate(divide="ignore", invalid="ignore"):
        adi = np.where(n_nonzero > 0, T / n_nonzero, np.inf)
        cv2 = np.where(mean_nz > 0, (std_nz / mean_nz) ** 2, 0.0)

    out = sales_wide[schema.ID_COLS].copy()
    out[schema.SERIES_KEY] = out["id"]
    out["n_nonzero"] = n_nonzero
    out["zero_rate"] = 1.0 - n_nonzero / T
    out["ADI"] = adi
    out["CV2"] = cv2
    return out


def label_segments(df: pd.DataFrame, adi_th: float, cv2_th: float) -> pd.DataFrame:
    """Gán nhãn 4 nhóm SBC dựa trên ngưỡng. Thêm cột `segment`. Trả về df mới."""
    out = df.copy()
    cond = [
        (out.ADI < adi_th) & (out.CV2 < cv2_th),    # smooth
        (out.ADI < adi_th) & (out.CV2 >= cv2_th),   # erratic
        (out.ADI >= adi_th) & (out.CV2 < cv2_th),   # intermittent
        (out.ADI >= adi_th) & (out.CV2 >= cv2_th),  # lumpy
    ]
    out["segment"] = np.select(cond, schema.SEGMENTS, default="intermittent")
    return out


def build_segment_labels(sales_wide: pd.DataFrame, cfg: dict | None = None) -> pd.DataFrame:
    """Pipeline đầy đủ: wide -> nhãn nhóm cho TOÀN BỘ chuỗi.

    Trả về DataFrame: series_id, ADI, CV2, zero_rate, segment (+ ID_COLS).
    """
    cfg = cfg or schema.load_config()
    train_days = schema.day_range(1, cfg["split"]["train_end"])
    df = compute_adi_cv2(sales_wide, train_days)
    df = label_segments(df, cfg["sbc"]["adi_threshold"], cfg["sbc"]["cv2_threshold"])
    return df


def summarize(seg_labels: pd.DataFrame) -> pd.DataFrame:
    """Bảng phân bố nhóm: số chuỗi, %, zero-rate TB, ADI/CV2 trung vị."""
    g = (seg_labels.groupby("segment")
         .agg(n_series=(schema.SERIES_KEY, "size"),
              zero_rate=("zero_rate", "mean"),
              ADI=("ADI", lambda s: np.median(s[np.isfinite(s)])),
              CV2=("CV2", "median"))
         .reindex(schema.SEGMENTS))
    g["pct"] = (g.n_series / g.n_series.sum() * 100).round(1)
    return g


def stratified_sample(seg_labels: pd.DataFrame, cfg: dict | None = None) -> list[str]:
    """Lấy mẫu phân tầng theo quy tắc trong config.

    rule = "keep_rare_cap_common": lấy TOÀN BỘ smooth + erratic (nhóm hiếm, để lực
    thống kê tối đa), cap intermittent + lumpy về `cap`. Deterministic theo seed.

    rule = "balanced": min(có sẵn, cap) mỗi nhóm.
    """
    cfg = cfg or schema.load_config()
    seed = cfg["seed"]
    rule = cfg["sampling"]["rule"]
    cap = cfg["sampling"]["cap"]
    rare = {"smooth", "erratic"}

    picks = []
    for seg, grp in seg_labels.groupby("segment"):
        if rule == "keep_rare_cap_common":
            n = len(grp) if seg in rare else min(len(grp), cap)
        elif rule == "balanced":
            n = min(len(grp), cap)
        else:
            raise ValueError(f"sampling.rule không hỗ trợ: {rule}")
        picks.append(grp.sample(n=n, random_state=seed))
    sample = pd.concat(picks)
    # sắp xếp ổn định để file sample_ids tái lập được y hệt
    return sorted(sample[schema.SERIES_KEY].tolist())
