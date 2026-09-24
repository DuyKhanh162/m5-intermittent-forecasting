# -*- coding: utf-8 -*-
"""build_long.py — Bước 1: chuẩn hóa dữ liệu M5 từ wide sang long.

Sở hữu: P1. Wide (mỗi chuỗi 1 hàng, mỗi ngày 1 cột) -> Long (mỗi (chuỗi, ngày) 1 hàng),
join calendar + sell_prices, tạo feature nền dùng chung: wday, month, is_event, snap, sell_price.
Chỉ long mới join được calendar/giá và là định dạng model xử lý tự nhiên.

CLI sinh 3 artifact bàn giao cho nhóm:
  - configs/sample_ids.csv          (danh sách chuỗi mẫu, deterministic seed 42)
  - <processed>/segment_labels.parquet   (nhãn nhóm cho TOÀN BỘ 30.490 chuỗi)
  - <processed>/data_long.parquet   (long cho scope đã chọn: sample | full)

Chạy:  python -m src.data.build_long --scope sample
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from src.common import schema
from src.segmentation import sbc

SNAP_MAP = {"CA": "snap_CA", "TX": "snap_TX", "WI": "snap_WI"}


def _resolve_raw_dir(cfg: dict) -> Path:
    """Tìm thư mục raw. Ưu tiên data/raw (config); fallback raw-data/ (bố cục cũ)."""
    root = schema.repo_root()
    primary = root / cfg["paths"]["raw_dir"]
    if (primary / "sales_train_evaluation.csv").exists():
        return primary
    legacy = root / "raw-data"
    if (legacy / "sales_train_evaluation.csv").exists():
        return legacy
    raise FileNotFoundError(
        f"Không thấy sales_train_evaluation.csv trong {primary} hay {legacy}. "
        "Chạy scripts/download_data.py trước."
    )


def load_raw(cfg: dict | None = None):
    """Đọc calendar, sell_prices, sales_train_evaluation (d_1..d_1941)."""
    cfg = cfg or schema.load_config()
    raw = _resolve_raw_dir(cfg)
    calendar = pd.read_csv(raw / "calendar.csv")
    prices = pd.read_csv(raw / "sell_prices.csv")
    sales = pd.read_csv(raw / "sales_train_evaluation.csv")   # tới d_1941
    return calendar, prices, sales


def build_long(sales: pd.DataFrame, calendar: pd.DataFrame, prices: pd.DataFrame,
               seg_labels: pd.DataFrame, series_ids: list[str] | None = None,
               cfg: dict | None = None) -> pd.DataFrame:
    """Xoay wide->long cho các chuỗi trong `series_ids` (None = toàn bộ) + join + feature.

    Trả về DataFrame long đủ cột LONG_COLS (+ event_name_1, sell_price giữ lại để EDA/ML).
    """
    cfg = cfg or schema.load_config()
    d_cols = [c for c in sales.columns if c.startswith("d_")]

    sub = sales if series_ids is None else sales[sales["id"].isin(series_ids)]
    sub = sub.copy()

    long = sub.melt(id_vars=schema.ID_COLS, value_vars=d_cols,
                    var_name="d", value_name=schema.TARGET)
    long = long.merge(calendar[schema.CALENDAR_KEEP], on="d", how="left")
    long = long.merge(prices, on=["store_id", "item_id", "wm_yr_wk"], how="left")

    long[schema.SERIES_KEY] = long["id"]
    long[schema.DATE_KEY] = pd.to_datetime(long["date"])
    long[schema.DAY_INT_KEY] = long["d"].str.slice(2).astype("int32")
    long["is_event"] = long["event_name_1"].notna().astype("int8")

    # SNAP theo bang của chuỗi (mỗi chuỗi lấy đúng cột snap của state_id)
    long["snap"] = 0
    for st, col in SNAP_MAP.items():
        m = long.state_id == st
        long.loc[m, "snap"] = long.loc[m, col].values
    long["snap"] = long["snap"].astype("int8")

    long[schema.TARGET] = long[schema.TARGET].astype("float32")
    long["sell_price"] = long["sell_price"].astype("float32")

    long = long.merge(seg_labels[[schema.SERIES_KEY, "segment"]],
                      on=schema.SERIES_KEY, how="left")
    keep = schema.LONG_COLS + ["event_name_1"]
    long = long[keep].sort_values([schema.SERIES_KEY, schema.DAY_INT_KEY]).reset_index(drop=True)
    return long


def main(scope: str = "sample") -> None:
    cfg = schema.load_config()
    root = schema.repo_root()
    processed = root / cfg["paths"]["processed_dir"]
    processed.mkdir(parents=True, exist_ok=True)
    (root / cfg["paths"]["configs_dir"]).mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    calendar, prices, sales = load_raw(cfg)
    print(f"[1/4] Đọc raw: sales {sales.shape} | {time.time()-t0:.1f}s")

    # --- segment_labels cho TOÀN BỘ 30.490 (vectorised, không melt) ---
    # Lưu vào configs/ (artifact deterministic, COMMIT được) để cả nhóm dùng CHUNG một
    # bộ nhãn, tránh trôi số float32 làm lệch nhãn ở các chuỗi sát ngưỡng giữa các máy.
    seg_labels = sbc.build_segment_labels(sales, cfg)
    seg_out = seg_labels[[schema.SERIES_KEY, "ADI", "CV2", "zero_rate", "segment"]]
    configs_dir = root / cfg["paths"]["configs_dir"]
    seg_out.to_parquet(configs_dir / "segment_labels.parquet", index=False)
    print("[2/4] Phân bố nhóm (toàn bộ 30.490):")
    print(sbc.summarize(seg_labels).round(3).to_string())

    # --- sample_ids theo quy tắc phân tầng ---
    sample_ids = sbc.stratified_sample(seg_labels, cfg)
    pd.DataFrame({schema.SERIES_KEY: sample_ids}).to_csv(
        root / cfg["paths"]["configs_dir"] / "sample_ids.csv", index=False)
    seg_of = seg_labels.set_index(schema.SERIES_KEY)["segment"]
    dist = seg_of.loc[sample_ids].value_counts().reindex(schema.SEGMENTS).to_dict()
    print(f"[3/4] sample_ids: {len(sample_ids)} chuỗi | phân bố {dist}")

    # --- data_long cho scope ---
    ids = None if scope == "full" else sample_ids
    long = build_long(sales, calendar, prices, seg_labels, ids, cfg)
    schema.assert_long_schema(long)
    out_path = processed / ("data_long_full.parquet" if scope == "full" else "data_long.parquet")
    long.to_parquet(out_path, index=False)
    mem = long.memory_usage(deep=True).sum() / 1e6
    print(f"[4/4] data_long ({scope}): {long.shape} ~{mem:.0f}MB -> {out_path.name} "
          f"| tổng {time.time()-t0:.1f}s")


if __name__ == "__main__":
    import sys
    try:            # Windows console mặc định cp1252 -> ép UTF-8 để in tiếng Việt
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Xây data_long M5 (bước 1).")
    ap.add_argument("--scope", choices=["sample", "full"], default="sample",
                    help="sample = chỉ chuỗi mẫu (nhanh); full = toàn bộ 30.490 (nặng).")
    args = ap.parse_args()
    main(args.scope)
