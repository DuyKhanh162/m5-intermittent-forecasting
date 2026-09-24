# M5 — Dự báo xác suất nhu cầu gián đoạn (Cổ điển · ML · Foundation Model)

Chuyên đề thạc sĩ KHDL. Câu hỏi lõi: **"nhu cầu nào → dùng model nào"**, phân nhóm theo đặc tính
demand (SBC), dự báo xác suất. Dữ liệu: [M5 Walmart](https://www.kaggle.com/competitions/m5-forecasting-accuracy/data).

## Cấu trúc
```
common/      # THỨ CỐ ĐỊNH, dùng chung — không tự sửa
  config.yaml            # mọi tham số: seed, split, quantile, ngưỡng SBC, model FM...
  sample_ids.csv         # danh sách chuỗi mẫu (cố định, seed 42)
  segment_labels.parquet # nhãn 4 nhóm cho toàn bộ 30.490 chuỗi
data/        # KHÔNG commit (tái tạo bằng notebook) — raw/ + processed/ + outputs/
notebooks/
  M5_reference.ipynb     # BẢN MẪU chạy được cả P1→P5 (tham chiếu, copy code từ đây)
  P1.ipynb ... P5.ipynb  # mỗi người 1 file — code phần việc của mình ở đây
docs/plan/   # kế hoạch nghiên cứu (PLAN, PLAN_REVISED, CHANGELOG)
```

## Cách làm việc (mỗi người 1 notebook → không conflict)
- Mỗi người chỉ sửa **notebook của mình** (`P<n>.ipynb`) → không bao giờ đụng file của nhau.
- **Truyền dữ liệu qua FILE, không qua code:** P1 chạy → tạo `data/processed/data_long.parquet`
  + `common/*`. P3/P4 đọc file đó → tạo `data/outputs/forecasts/*.parquet`. P5 đọc các forecast đó
  → ra bảng so sánh. Ai cần output của người trước thì chỉ việc để file đó tồn tại (chạy P1 trước,
  hoặc lấy file từ người P1).
- Mỗi `P<n>.ipynb` có sẵn **cell setup dùng chung** (nạp `common/config.yaml` + dữ liệu) để cả nhóm
  chạy trên đúng một cấu hình. Phần code mẫu nằm trong `M5_reference.ipynb` — copy sang, mở rộng.

## Bắt đầu
```powershell
git clone https://github.com/DuyKhanh162/m5-intermittent-forecasting
cd m5-intermittent-forecasting
pip install -r requirements.txt

# Đặt M5 vào data/raw/ (giải nén m5-forecasting-accuracy.zip): calendar.csv, sell_prices.csv,
# sales_train_evaluation.csv, sample_submission.csv

# Mở notebooks/ trong Jupyter/VS Code. P1 chạy trước (sinh dữ liệu), rồi mọi người chạy file của mình.
```
> Ai làm việc gì: xem cell tiêu đề đầu mỗi `P<n>.ipynb`. Kế hoạch đầy đủ: `docs/plan/PLAN_REVISED.md`.

## Quy tắc
1. Không sửa `common/` (tham số/mẫu/nhãn cố định) nếu chưa báo P1.
2. Không shuffle — tôn trọng trục thời gian. ML dùng **lag ≥ 28**. Chỉ tune/hiệu chuẩn trên validation.
3. Forecast lưu đúng khuôn: cột `series_id, date, d_int, quantile_level, value, model`.
