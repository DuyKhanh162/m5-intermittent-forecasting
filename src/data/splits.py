# -*- coding: utf-8 -*-
"""splits.py — Bước 4: chia train/validation/test theo thời gian + rolling-origin.

Sở hữu: P1. Nguyên tắc: KHÔNG shuffle, mọi thao tác tôn trọng trục thời gian.
Test lọt vào train = "nhìn trộm" -> điểm đẹp giả.

Rolling-origin (BẮT BUỘC >=3 cửa sổ theo PLAN_REVISED §5): trượt điểm gốc lùi về
quá khứ, mỗi lần một cửa sổ test 28 ngày mới, để đo model nào ỔN ĐỊNH qua thời gian.
Pilot 1 cửa sổ chênh 2-3% nằm trong nhiễu -> không phân biệt được model.

Tất cả cửa sổ nằm gọn trong actuals có sẵn (<= d_1941).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

from src.common import schema


@dataclass(frozen=True)
class Window:
    """Một cửa sổ rolling-origin. Các mốc là số nguyên ngày (d_int)."""
    name: str
    train_end: int      # train = d_1 .. d_{train_end}
    val_end: int        # val   = d_{train_end+1} .. d_{val_end}
    test_start: int     # = val_end + 1
    test_end: int       # test  = d_{test_start} .. d_{test_end}

    @property
    def train_days(self) -> list[str]:
        return schema.day_range(1, self.train_end)

    @property
    def val_days(self) -> list[str]:
        return schema.day_range(self.train_end + 1, self.val_end)

    @property
    def test_days(self) -> list[str]:
        return schema.day_range(self.test_start, self.test_end)

    def as_dict(self) -> dict:
        return asdict(self)


def rolling_windows(cfg: dict | None = None) -> list[Window]:
    """Sinh danh sách cửa sổ rolling-origin từ config.

    Cửa sổ 1 (gần hiện tại nhất) dùng đúng mốc `split` trong config; các cửa sổ
    sau lùi lại `rolling.step` ngày. Horizon (số ngày test) không đổi giữa các cửa sổ.
    """
    cfg = cfg or schema.load_config()
    s = cfg["split"]
    n = cfg["rolling"]["n_windows"]
    step = cfg["rolling"]["step"]
    horizon = cfg["horizon"]
    max_day = s["max_actual_day"]

    val_len = s["val_end"] - s["train_end"]      # độ dài val (giữ cố định)

    windows: list[Window] = []
    for k in range(n):
        test_end = s["test_end"] - k * step
        test_start = test_end - horizon + 1
        val_end = test_start - 1
        train_end = val_end - val_len
        if train_end < 1:
            raise ValueError(
                f"Cửa sổ {k+1} có train_end={train_end} < 1: giảm n_windows hoặc step."
            )
        if test_end > max_day:
            raise ValueError(
                f"Cửa sổ {k+1} test_end={test_end} > actuals tối đa {max_day}."
            )
        windows.append(Window(
            name=f"W{k+1}", train_end=train_end, val_end=val_end,
            test_start=test_start, test_end=test_end,
        ))
    return windows


def split_long(long_df, window: Window):
    """Chia data_long thành (train, val, test) theo một cửa sổ, dùng cột d_int.

    Trả về 3 DataFrame con (đã lọc theo d_int), không sao chép cột thừa.
    """
    di = long_df[schema.DAY_INT_KEY]
    train = long_df[di <= window.train_end]
    val = long_df[(di > window.train_end) & (di <= window.val_end)]
    test = long_df[(di >= window.test_start) & (di <= window.test_end)]
    return train, val, test


def assert_no_leakage(window: Window, horizon: int | None = None) -> None:
    """Khẳng định cửa sổ hợp lệ: train < val < test, test đúng `horizon` ngày,
    không chồng lấn. Ném AssertionError nếu vi phạm.
    """
    cfg = schema.load_config()
    horizon = horizon or cfg["horizon"]
    assert window.train_end < window.val_end < window.test_start <= window.test_end, (
        f"Thứ tự mốc sai ở {window.name}: {window}"
    )
    assert window.test_start == window.val_end + 1, (
        f"test_start phải liền sau val_end ở {window.name}"
    )
    assert (window.test_end - window.test_start + 1) == horizon, (
        f"Test phải đúng {horizon} ngày ở {window.name}, "
        f"đang là {window.test_end - window.test_start + 1}"
    )
