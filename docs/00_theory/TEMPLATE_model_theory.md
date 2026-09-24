# Template lý thuyết mô hình — Bước 0

> **Ai build phần nào chủ trì lý thuyết phần đó.** Mỗi người copy file này thành
> `docs/00_theory/<Pn>_<ten-model>.md` và điền theo đúng 4 ý dưới. P1 gộp thành 1 tài liệu,
> thống nhất ký hiệu theo [`notation.md`](notation.md). **Deadline nội bộ: 26/9.**

Mỗi mô hình (hoặc họ mô hình) trình bày theo **4 ý bắt buộc**:

## 1. Khái niệm
Model này là gì, thuộc họ nào (cổ điển / ML / foundation), giải quyết bài toán gì.

## 2. Cơ chế / công thức
Cách hoạt động cốt lõi. Công thức chính (dùng ký hiệu thống nhất trong `notation.md`).
Với FM: nói rõ zero-shot vs few-shot, cơ chế sinh quantile.

## 3. Điểm mạnh – điểm yếu & khi nào áp dụng
Ưu/nhược, chi phí tính toán, khi nào nên/không nên dùng.

## 4. Vì sao hợp / không hợp chuỗi gián đoạn
Liên hệ trực tiếp tới bài toán intermittent demand (nhiều số 0). Đây là ý quan trọng nhất.

---

### Ghi chú theo từng họ (điền phần của mình)

- **P3 · ML (LightGBM global quantile):** nhấn cơ chế quantile regression (pinball loss) sinh
  xác suất tự nhiên; bẫy leak lag ≥ horizon.
- **P4 · Cổ điển (Croston/SBA/TSB):** nền Croston (tách cỡ & khoảng cách); SBA sửa thiên lệch;
  TSB cập nhật xác suất có bán. Vì sao phải bọc phân phối (NB) để ra dải.
- **P4 · Foundation (Chronos-Bolt/TTM/Moirai):** **đào sâu nhất** — zero-shot vs few-shot, cơ chế
  ra quantile, kẹp đuôi [0.1,0.9] của Chronos, **cảnh báo rò rỉ pre-training** (đã thấy M5?).
- **P5 · Nền xác suất:** calibration, conformal prediction, kiểm định DM/MCB.
- **P1 · Nền chung:** xem [`P1_foundations.md`](P1_foundations.md).
