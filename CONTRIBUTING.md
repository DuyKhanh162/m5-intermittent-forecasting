# Quy trình làm việc nhóm (GitHub Flow)

Nhóm 5 người, **P1 điều phối**. Nhánh `main` luôn ở trạng thái chạy được.

## Vòng đời một đầu việc
1. **Tạo issue** theo template (bước nào, ai, phụ thuộc gì, hạn).
2. **Tạo branch** từ `main` theo quy ước: `p<n>/buoc-<k>-<mô-tả-ngắn>`
   - vd: `p3/buoc5-lightgbm-quantile`, `p1/buoc4-rolling-split`.
3. **Commit** nhỏ, thông điệp rõ (tiếng Việt không dấu hoặc tiếng Anh đều được).
4. **Mở Pull Request** vào `main`, điền template PR.
5. **Review**: cần **≥1 approve** + **CI xanh** mới merge được (branch protection bật trên `main`).
6. **Merge** (squash) → xoá branch.

## Mối nối ĐÔNG CỨNG — không tự ý sửa
Đổi các file sau PHẢI báo P1 + cả nhóm (mọi người phụ thuộc vào chúng):
- `src/common/schema.py` — cột, split days, format contract (#1, #2).
- `src/common/forecast_io.py` — đọc/ghi forecast.
- `configs/config.yaml` — hằng số dùng chung (seed, split, quantile, ngưỡng SBC…).
- `configs/segment_labels.parquet`, `configs/sample_ids.csv` — artifact chung (P2 sinh 1 lần).

**Format forecast bắt buộc (MỐI NỐI #2):**
`series_id, date, d_int, quantile_level, value, model` — luôn ghi qua `forecast_io.write_forecast`.

## Nguyên tắc chống rò rỉ (bắt buộc)
- KHÔNG shuffle. Mọi thao tác tôn trọng trục thời gian.
- ML: **lag ≥ horizon (28)** để ngày test không cần dữ liệu chưa biết.
- Hiệu chuẩn/tune chỉ trên **validation**, không đụng **test** sớm.

## Bảng sở hữu theo bước
| Người | Bước | File chính |
|---|---|---|
| **P1** — Dữ liệu & điều phối | 0·1·4·8·10a | `src/common/{schema,forecast_io}.py`, `src/data/{build_long,splits}.py`, `src/evaluation/significance.py` |
| **P2** — Phân nhóm & tổng hợp | 0·2·3·9·10b | `src/segmentation/sbc.py` |
| **P3** — ML | 0·5 | `src/models/ml_lightgbm.py` |
| **P4** — Foundation & Cổ điển | 0·5 | `src/models/{classical,foundation}.py` |
| **P5** — Đánh giá | 0·6·7·8 | `src/common/{metrics,calibration}.py`, `src/evaluation/harness.py` |

Lịch: nền lý thuyết 26/9 · xong toàn bộ (kể cả slide) trước 7/10 · nộp chính thức 15/10.
Chi tiết plan: [`docs/plan/PLAN_REVISED.md`](docs/plan/PLAN_REVISED.md).
