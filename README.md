# M5 — Dự báo XÁC SUẤT nhu cầu gián đoạn: So sánh Cổ điển · ML · Foundation Model

Chuyên đề thạc sĩ KHDL. **Câu hỏi lõi: "nhu cầu nào → dùng model nào"** (không phải "model nào
mạnh nhất"), phân nhóm theo đặc tính demand (SBC), dự báo xác suất, có kiểm định thống kê.

Dữ liệu: [M5 Walmart](https://www.kaggle.com/competitions/m5-forecasting-accuracy/data) —
30.490 chuỗi (sản phẩm × cửa hàng), ~1.941 ngày. 95% chuỗi là intermittent + lumpy.

## Bắt đầu nhanh
```bash
pip install -r requirements.txt          # hoặc: make setup
python scripts/download_data.py          # tải/giải nén M5 vào data/raw/
python -m src.data.build_long --scope sample   # sinh data_long mẫu (~30s)  | make data
python -m pytest tests/ -q               # chạy test  | make test
```
> Windows: đặt `set PYTHONUTF8=1` để in tiếng Việt. Nếu không có `make`, dùng lệnh python trực tiếp.

## Quy trình 10 bước (tóm tắt)
0 lý thuyết · 1 chuẩn hoá long · 2–3 phân nhóm SBC + lấy mẫu · 4 split + rolling-origin ·
5 ba họ model · 6 hiệu chuẩn conformal · 7 metric · 8 rolling ≥3 + DM/MCB · 9 bảng khuyến nghị ·
10 báo cáo + slide. Chi tiết: [`docs/plan/PLAN_REVISED.md`](docs/plan/PLAN_REVISED.md).

## Cấu trúc repo
```
configs/        config.yaml + artifact chung (sample_ids, segment_labels)  [COMMIT]
data/           raw/ (tải về) + processed/ (sinh ra)                        [IGNORE]
src/common/     schema, forecast_io, metrics, calibration  (mối nối chung)
src/data/       build_long (bước 1), splits (bước 4)                        — P1
src/segmentation/  sbc (bước 2-3)                                           — P2
src/models/     ml_lightgbm (P3), classical + foundation (P4)  (bước 5)
src/evaluation/ harness (bước 6-9, P5), significance DM/MCB (bước 8, P1)
notebooks/      M5_..._study.ipynb  — pilot tham chiếu (P1→P5 trong 1 file)
outputs/        forecast + metric pilot (tham chiếu)
tests/          unit test (CI) + smoke_test pipeline pilot
docs/           00_theory/ (bước 0), data_dictionary, plan/
```

## Trạng thái hiện tại (P1 đã giao)
- ✅ **Bước 1**: `build_long.py` wide→long + join + feature (scope sample|full).
- ✅ **Bước 4**: `splits.py` rolling-origin **3 cửa sổ** (test 1914–41 / 1886–13 / 1858–85), no-leakage.
- ✅ **Bước 8 (công cụ)**: `significance.py` DM + MCB + win-rule (đã unit-test).
- ✅ Artifact: `configs/sample_ids.csv` (3.474 chuỗi), `configs/segment_labels.parquet` (full 30.490).
- ⏳ **Bước 5** (P3/P4), **6–7 & 9** (P5): stub interface sẵn, trỏ tới cell notebook — chờ triển khai.
- ⏳ **Bước 8 (chạy thật)**: cần forecast của ≥3 cửa sổ từ P3/P4 trước.

## Đóng góp
Đọc [`CONTRIBUTING.md`](CONTRIBUTING.md): GitHub Flow, quy ước branch, mối nối đông cứng, phân công.
