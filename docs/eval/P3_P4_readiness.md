# Khung tiêu chí đánh giá mức sẵn sàng (readiness) của P3 & P4

**Ngày:** 2026-10-07 · **Người soát:** P1 (điều phối) · **Trạng thái:** working tree, chưa commit.

## 0. Mục đích & phạm vi

Trả lời **"P3 và P4 đã đủ tốt để bàn giao cho P5 chưa"** — tức deliverable có **đúng, không rò rỉ,
trung thành với plan (Bước 5), tái lập được, và hành vi thô hợp lý** hay không.

> **KHÔNG** trả lời "model nào thắng / FM có hơn cổ điển không". Đó là việc của P5 (Bước 6–8:
> calibration + metric chính thức + DM/MCB), **sau khi** readiness đạt. Coverage/độ rộng dải ở đây
> là **diagnostic thô CHƯA calibrate**, không phải phán quyết năng lực model.

Chấm theo 6 tiêu chí D1–D6, mỗi tiêu chí: **Đạt / Cảnh báo / Thiếu**, kèm chủ sở hữu và cách kiểm.
Script khách quan: `scripts/verify_p5_inputs.py` (D1, D6) và `scripts/eval_readiness.py` (D4).

---

## 1. Sáu tiêu chí

| # | Tiêu chí | Ngưỡng ĐẠT | Cách kiểm |
|---|---|---|---|
| **D1** | **Hợp đồng lưới** | 3.474 chuỗi × 3 cửa sổ × 9 quantile × 28 ngày; value ≥ 0; không quantile-crossing; có cả test lẫn val | auto (`verify_p5_inputs.py`) |
| **D2** | **An toàn rò rỉ thời gian** | Không shuffle; feature/context chỉ dùng dữ liệu ≤ origin; lag ≥ horizon (ML); FM zero-shot; val thực sự out-of-sample | soát code |
| **D3** | **Trung thành Bước 5** | Đủ họ model được giao; cơ chế sinh quantile đúng spec (native / NB wrap); hạn chế đã biết được ghi nhận (kẹp đuôi Chronos) | soát code + plan |
| **D4** | **Sanity xác suất thô** | Quantile đơn điệu; coverage & zero-rate **có thể giải thích** (lệch do lớp bọc là chấp nhận được, sẽ do conformal sửa); không có giá trị vô lý | auto (`eval_readiness.py`) |
| **D5** | **Tái lập & minh bạch** | Seed cố định; chạy từ `common/config.yaml`; lưu artifact (runtime, config, importance); pin version FM | soát repo |
| **D6** | **Hoàn chỉnh bàn giao** | Đủ 9 model có test + val đúng vị trí/tên hợp đồng (`forecasts/` + `forecasts/val/`) | auto (`verify_p5_inputs.py`) |

---

## 2. Chấm điểm P3 (LightGBM + cổ điển)

| # | Kết quả | Bằng chứng |
|---|---|---|
| D1 | **Đạt** | lgbm + 5 cổ điển đều 2.626.344 dòng, không crossing (`verify_p5_inputs.py`). |
| D2 | **Đạt** | `P3.ipynb` cell 5–8: lag 28/35/56 (≥ H=28), rolling/dsls đều `.shift(H)`, train ≤ `train_end`, không shuffle, audit feature không-NA. Cổ điển (script): fit ≤ origin. |
| D3 | **Đạt** | LightGBM global quantile (pinball, native) + **Croston/SBA/TSB + Naive/SNaive đã nằm trong `P3.ipynb`** (mục "Mô hình cổ điển", cell 12–15, thêm sau phần LightGBM — không sửa cell cũ). Bọc NB đúng spec §3. |
| D4 | **Đạt** | lgbm cov95=0.975, cov50=0.609; cổ điển cov95 0.83–0.98. Zero-rate median: lgbm 3% (quantile liên tục), cổ điển 40–49% (bọc-NB, đúng bản chất gián đoạn). Không giá trị vô lý. |
| D5 | **Đạt** | `p3/lgbm_run_config.json` (pin lightgbm, seed, params), `lgbm_runtime.csv`, `lgbm_feature_importance.parquet`. Cổ điển: script seed từ config; nên lưu thêm runtime (nhỏ). |
| D6 | **Đạt** | test `forecasts/{lgbm,naive,snaive,croston,sba,tsb}.parquet` + val `forecasts/val/<m>.parquet`. |

**P3: ĐỦ.** Code cổ điển đã được gập trực tiếp vào `P3.ipynb` (self-contained; Run All tái tạo đủ 6 model test + val).

## 3. Chấm điểm P4 (Foundation Models)

| # | Kết quả | Bằng chứng |
|---|---|---|
| D1 | **Đạt** | chronos_bolt, ttm, moirai_2 đều 2.626.344 dòng test + val, không crossing. |
| D2 | **Đạt** | `P4.ipynb` cell 11/17/22: context = `sales[d_int ≤ train_end][-ctx:]`, zero-shot (`from_pretrained`, không train lại M5), dispersion NB ước lượng ≤ `train_end`. Val = slice `[0:H]` của cùng predict call ⇒ out-of-sample. |
| D3 | **Đạt (có ghi chú)** | Chronos native quantile + **ghi nhận kẹp đuôi [0.1,0.9]** (cell 34 + biểu đồ 04); TTM point→NB; Moirai native→interp + rearrangement. Few-shot ablation **chưa làm** (plan ghi *tùy chọn*, không chặn). |
| D4 | **Đạt (đúng kỳ vọng)** | chronos/moirai cov95≈0.75 (**thiếu phủ do kẹp đuôi** — đúng như plan dự báo), ttm cov95=0.974 (bọc-NB). Hai FM native lệch **đồng nhất cùng chiều** ⇒ nhất quán, không phải lỗi ngẫu nhiên. Đây chính là lý do Bước 6 bắt buộc conformal. |
| D5 | **Cảnh báo** | Có `*_runtime.csv` + ghi chú rò rỉ pre-training (cell 34). **Nên bổ sung pin version** cụ thể (`chronos-forecasting`, `granite-tsfm`, `uni2ts==2.0.0`) vào artifact/`requirements.txt` để tái lập. |
| D6 | **Đạt** | test đã có sẵn; val sinh bởi **mục 11 trong `P4.ipynb`** (cell native, không phải script ngoài) → `forecasts/val/{chronos_bolt,ttm,moirai_2}.parquet`. |

**P4: ĐỦ** để bàn giao; code val đã gập vào `P4.ipynb` (mục 11, trước Kết luận). Chỉ nên siết **pin version** và (nếu kịp) thêm few-shot ablation như ablation phụ.

---

## 4. Diagnostic coverage thô (căn cứ cho D4 — CHƯA calibrate)

Mục tiêu danh nghĩa: cov50→0.50 · cov67→0.67 · cov95→0.95 · cov99→0.99.

| model | cov50 | cov67 | cov95 | cov99 | w95 | med_zero% | Diễn giải |
|---|---|---|---|---|---|---|---|
| naive | 0.659 | 0.745 | 0.857 | 0.872 | 14.0 | 45.8 | baseline, bọc-NB hơi thiếu phủ |
| snaive | 0.648 | 0.728 | 0.833 | 0.849 | 11.7 | 48.5 | baseline |
| croston | 0.729 | 0.844 | 0.982 | 0.995 | 12.9 | 40.4 | bọc-NB hơi thừa phủ |
| sba | 0.720 | 0.836 | 0.981 | 0.994 | 12.3 | 41.1 | bọc-NB |
| tsb | 0.733 | 0.839 | 0.971 | 0.984 | 12.6 | 42.1 | bọc-NB |
| lgbm | 0.609 | 0.760 | 0.975 | 0.995 | 10.4 | 3.0 | quantile native, dải hẹp hơn, phủ tốt |
| **chronos_bolt** | 0.414 | 0.600 | **0.753** | 0.754 | 6.1 | 3.0 | **thiếu phủ — kẹp đuôi [0.1,0.9]** |
| ttm | 0.702 | 0.819 | 0.974 | 0.990 | 11.8 | 42.2 | point→NB |
| **moirai_2** | 0.405 | 0.576 | **0.751** | 0.753 | 5.9 | 2.7 | **thiếu phủ — cùng cơ chế kẹp đuôi** |

**Đọc bảng này cho đúng:** chênh coverage chủ yếu đến từ **cách vẽ dải** (native kẹp đuôi vs bọc-NB),
không phải năng lực dự báo. Vì vậy nó **không trừ điểm readiness** — trái lại, nó xác nhận pipeline phản
ánh đúng hành vi đã biết và **làm rõ nhiệm vụ của P5**: áp split-conformal chung rồi mới chấm.

---

## 5. Kết luận & quyết định mở

**Kết luận:** cả P3 và P4 **ĐỦ TỐT để bàn giao cho P5** về mặt số liệu, an toàn rò rỉ và trung thành
phương pháp. Không có tiêu chí nào ở mức "Thiếu". Hai điểm "Cảnh báo" là hình thức/tăng cường, không chặn P5.

**Đã xử lý:** code cổ điển gập vào `P3.ipynb` (mục cổ điển) và code FM-val gập vào `P4.ipynb` (mục 11)
— cả hai notebook nay tự chứa, không còn phụ thuộc script sinh output bên ngoài.

**Quyết định mở còn lại (cần P1 + chủ P3/P4 chốt):**
1. **Pin version FM (D5-P4):** bổ sung version cụ thể (`chronos-forecasting`, `granite-tsfm`, `uni2ts==2.0.0`) vào `requirements.txt`/artifact trước khi nộp.
2. **Few-shot ablation (D3-P4):** làm hay bỏ (plan: tùy chọn). Nếu làm → ưu tiên TTM.
3. **`.venv-moirai/`:** không được commit (thêm vào `.gitignore` trước khi commit).

**Công cụ P1 giữ lại** (`scripts/`): `fc_common.py`, `verify_p5_inputs.py` (kiểm hợp đồng test+val),
`eval_readiness.py` (diagnostic coverage). Các script sinh output đã xóa vì đã gập vào notebook của P3/P4.
