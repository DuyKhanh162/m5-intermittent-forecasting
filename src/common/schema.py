# -*- coding: utf-8 -*-
"""schema.py — Nguồn chân lý (single source of truth) về dữ liệu M5.

Sở hữu: P1 (Dữ liệu & hạ tầng). Đây là MỐI NỐI ĐÔNG CỨNG #1 & #2 của nhóm:
  - Schema dữ liệu long.
  - Format forecast: (series_id, date, d_int, quantile_level, value, model).
Đổi file này PHẢI báo cả nhóm vì mọi module khác phụ thuộc vào nó.

Ràng buộc quan trọng: file `sales_train_evaluation.csv` chỉ có actuals tới **d_1941**.
Actuals holdout M5 chính thức (d_1942..1969) KHÔNG nằm trong bộ này.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

# --------------------------------------------------------------------- paths
def repo_root() -> Path:
    """Trả về thư mục gốc repo (chứa configs/, src/, data/)."""
    here = Path(__file__).resolve()
    for p in [here] + list(here.parents):
        if (p / "configs" / "config.yaml").exists():
            return p
    # fallback: 3 cấp trên src/common/schema.py
    return here.parents[2]


@lru_cache(maxsize=1)
def load_config() -> dict:
    """Đọc configs/config.yaml (cache 1 lần)."""
    cfg_path = repo_root() / "configs" / "config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# --------------------------------------------------------------- column names
# Cột định danh trong file sales_train_evaluation.csv
ID_COLS = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]
TARGET = "sales"
SERIES_KEY = "series_id"          # = cột "id" của M5, đổi tên cho nhất quán
DAY_KEY = "d"                     # nhãn ngày kiểu "d_1"
DAY_INT_KEY = "d_int"            # số nguyên ngày (1..1941) để join/sort
DATE_KEY = "date"

# Thứ tự 4 nhóm demand (dùng nhất quán ở mọi bảng)
SEGMENTS = ["smooth", "erratic", "intermittent", "lumpy"]

# Cột lịch giữ lại khi join
CALENDAR_KEEP = [
    "d", "date", "wm_yr_wk", "wday", "month", "year",
    "event_name_1", "event_type_1", "snap_CA", "snap_TX", "snap_WI",
]

# --- MỐI NỐI #1: cột tối thiểu của bảng data_long ---
LONG_COLS = [
    SERIES_KEY, DATE_KEY, DAY_INT_KEY, TARGET,
    "wday", "month", "is_event", "snap", "sell_price", "segment",
]

# --- MỐI NỐI #2: cột bắt buộc của MỌI file forecast ---
FORECAST_COLS = [SERIES_KEY, DATE_KEY, DAY_INT_KEY, "quantile_level", "value", "model"]


# ------------------------------------------------------------ day utilities
def day_label(i: int) -> str:
    """1 -> 'd_1'."""
    return f"d_{i}"


def day_int(label: str) -> int:
    """'d_1' -> 1."""
    return int(label[2:])


def day_range(start: int, end: int) -> list[str]:
    """[start..end] (bao gồm 2 đầu) -> ['d_start', ..., 'd_end']."""
    return [day_label(i) for i in range(start, end + 1)]


# ------------------------------------------------------- split day accessors
def split_days(cfg: dict | None = None) -> dict[str, list[str]]:
    """Trả về dict train/val/test days cho CỬA SỔ GỐC (window 1).

    Dùng cho các bước không cần rolling. Với rolling nhiều cửa sổ dùng
    `src.data.splits.rolling_windows()`.
    """
    cfg = cfg or load_config()
    s = cfg["split"]
    return {
        "train": day_range(1, s["train_end"]),
        "val": day_range(s["train_end"] + 1, s["val_end"]),
        "test": day_range(s["val_end"] + 1, s["test_end"]),
    }


def assert_forecast_schema(df) -> None:
    """Kiểm tra một DataFrame forecast tuân thủ MỐI NỐI #2."""
    missing = [c for c in FORECAST_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Forecast thiếu cột bắt buộc: {missing}. Cần đủ {FORECAST_COLS}")


def assert_long_schema(df) -> None:
    """Kiểm tra một DataFrame long tuân thủ MỐI NỐI #1."""
    missing = [c for c in LONG_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"data_long thiếu cột bắt buộc: {missing}. Cần đủ {LONG_COLS}")
