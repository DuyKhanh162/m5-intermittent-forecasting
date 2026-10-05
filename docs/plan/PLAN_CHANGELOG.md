# Changelog cho Plan nghiên cứu — sau khi chạy thử thực tế trên M5

**Ngày:** 2026-09-22
**Nguồn bằng chứng:** notebook `M5_demand_forecasting_study.ipynb` chạy full 800 chuỗi
(SAMPLE_PER_SEGMENT=200 × 4 nhóm, 1 cửa sổ test 28 ngày), các bảng trong `outputs/`
(`metrics_by_model_segment.parquet`, `decision_table.parquet`, `segment_labels.parquet`).

> Mục đích file này: liệt kê **chính xác chỗ cần sửa** trong plan gốc (P1–P5), kèm **vì sao** và
> **bằng chứng số liệu**. Bản plan viết lại đầy đủ nằm ở `PLAN_REVISED.md`.

---

## Bằng chứng cốt lõi (đã kiểm chứng, không lấy lại từ nhận định)

**B1 — Phân bố nhóm demand thực tế trên toàn bộ 30.490 chuỗi** (không cân bằng như plan ngầm giả định):

| Nhóm | Số chuỗi | Tỷ lệ | Zero-rate TB |
|---|---:|---:|---:|
| smooth | 980 | 3.2% | 0.14 |
| erratic | 494 | 1.6% | 0.17 |
| intermittent | 23.096 | 75.7% | 0.74 |
| lumpy | 5.920 | 19.4% | 0.60 |

→ **95% dữ liệu là intermittent + lumpy.** smooth/erratic rất hiếm.

**B2 — SPL (thấp = tốt) & "model thắng" theo nhóm (full 800 chuỗi):**

| Nhóm | Thắng (SPL) | Chênh á quân | Kết luận |
|---|---|---:|---|
| smooth | lgbm | 2.1% | tương đương |
| erratic | chronos_bolt | 2.6% | tương đương |
| intermittent | lgbm | 2.8% | tương đương |
| lumpy | lgbm | 6.4% | thắng rõ |

**B3 — WSPL (dollar-weighted) KHÔNG trùng SPL:** ở erratic, `chronos_bolt=0.305 < lgbm=0.317`
(theo SPL thì lgbm thắng, theo WSPL thì chronos thắng). → **chọn metric chính làm đổi kết luận.**

**B4 — Coverage 95% (mục tiêu 0.95) lệch hệ thống, hai chiều ngược nhau:**

| Model | erratic | interm | lumpy | smooth |
|---|---:|---:|---:|---:|
| chronos_bolt | 0.81 | 0.75 | 0.77 | 0.80 |
| lgbm | 0.96 | 0.97 | 0.97 | 0.98 |
| croston/sba/tsb/ttm | 0.95–0.99 | 0.96–0.99 | 0.95–0.98 | 0.98 |

→ Chronos **thiếu phủ** (kẹp đuôi về [0.1,0.9]); nhóm bọc-NB **thừa phủ**.

**B5 — RMSSE (điểm):** chronos_bolt tốt nhất ở erratic (0.683) & smooth (0.692) và sát nhất ở
intermittent (0.816 vs lgbm 0.818); lgbm tốt nhất ở lumpy (0.749). → FM mạnh ở **độ chính xác điểm**,
nhưng yếu ở **hiệu chuẩn xác suất**.

**B6 — Hạ tầng:** máy CPU-only vẫn chạy hết 8 mô hình. Chronos-Bolt ~7s, TTM ~1–3s cho ~160–800 chuỗi.
API đúng là `predict_quantiles(inputs=...)`. Mọi package (lightgbm, statsforecast, chronos-forecasting,
transformers, granite-tsfm, pyarrow) cài & chạy OK trên CPU.

---

## Thay đổi theo từng mục của plan gốc

### Mục 2 — Câu hỏi nghiên cứu & cách kết luận

- **ĐỔI khung kết luận:** từ "model nào mạnh nhất / FM thắng ở đâu" → **khuyến nghị có điều kiện,
  có kiểm định**. Bằng chứng B2/B3: đa số chênh lệch 2–3% ⇒ *tương đương*, không đủ để tuyên bố thắng.
- **THÊM luật tuyên bố thắng:** chỉ gọi "thắng" khi chênh lệch **sống sót qua rolling-origin ≥3 cửa sổ
  VÀ một kiểm định ý nghĩa (MCB / Diebold-Mariano)**. Mặc định là "tương đương".
- **SỬA kỳ vọng ban đầu:** kỳ vọng "FM suy giảm ở lumpy" — thực tế lgbm thắng lumpy, FM (chronos) đứng
  giữa; kỳ vọng "cổ điển mạnh ở intermittent/lumpy" — đúng một phần: Croston/SBA/TSB **tương đương**
  lgbm ở hai nhóm này với chi phí thấp hơn nhiều. Ghi lại các điểm trái kỳ vọng (B2).
- **THÊM cảnh báo confound:** kết luận về SPL/coverage bị nhiễu bởi *cách sinh quantile* (xem Mục 3).

### Mục 3 — Kiến thức nền tảng

- **THÊM:** "Hiệu chuẩn dự báo xác suất (calibration)" và **conformal prediction** như một khái niệm nền —
  vì đây trở thành trục phân tích chính (B4) và là cơ chế để so sánh công bằng.
- **THÊM:** khái niệm kiểm định độ chênh mô hình (MCB, Diebold-Mariano).

### Mục 4 — Bộ dữ liệu

- **SỬA (quan trọng) về split thực tế:** file `sales_train_evaluation.csv` chỉ có actuals tới **d_1941**.
  Actuals của holdout M5 chính thức (**d_1942–1969**) **không nằm trong** bộ này. → Plan phải nêu rõ:
  dùng split nội bộ **train ≤ d_1885 · val d_1886–1913 · test d_1914–1941**, HOẶC tải bộ actuals cuối
  đã phát hành nếu muốn đúng chuẩn M5.
- **THÊM bảng phân bố nhóm thật (B1)** vào phần đặc điểm dữ liệu, nêu rõ **mất cân bằng 95/5**.

### Mục 5 — Thiết lập chung

- **SỬA cỡ mẫu:** "min(có sẵn, 1000)/nhóm" **bất khả thi** — erratic chỉ 494, smooth chỉ 980 (B1).
  → đổi thành **N ≤ 400/nhóm** (hoặc: lấy toàn bộ erratic+smooth, cap intermittent+lumpy), và **ghi rõ
  mức mất cân bằng** còn lại.
- **THÊM 2 góc báo cáo:** (a) *balanced-per-segment* để chẩn đoán theo đặc tính; (b) *frequency-weighted*
  theo tỷ lệ thật hoặc chạy full 30.490 (cổ điển + LightGBM) để phản ánh vận hành. Vì trung bình gộp trên
  4 nhóm cân bằng đang **thổi phồng smooth/erratic ~30×** so với tần suất thật.
- **NÂNG rolling-origin từ "nếu compute cho phép" → BẮT BUỘC ≥3 cửa sổ.** Bằng chứng B2: 1 cửa sổ +
  chênh 2–3% không phân biệt được mô hình.
- **CHỐT metric chính (pre-register):** chọn **WSPL (dollar-weighted, chuẩn M5 Uncertainty)** làm chính,
  SPL là phụ — vì B3 cho thấy chúng bất đồng. Ghi rõ trước khi xem kết quả.
- **GIỮ:** cùng split/horizon/sample_ids/seed; 3 mối nối đông cứng — nhưng **bổ sung mối nối #3** (xem Mục 3
  bên dưới) thành "giao thức hiệu chuẩn chung" thay vì chỉ "phát quantile cho model điểm".

### Mục 3-nối (giao thức xác suất) — THIẾT KẾ LẠI CHO CÔNG BẰNG

- **VẤN ĐỀ:** mỗi họ mô hình sinh quantile khác nhau ⇒ SPL/coverage đo lẫn cả "lớp bọc":
  LightGBM = quantile regression native; Chronos = native **nhưng kẹp đuôi [0.1,0.9]**; cổ điển + TTM =
  **bọc Negative Binomial**. B4 cho thấy sai lệch hiệu chuẩn đến từ *phương pháp bọc*, không hẳn từ mô hình.
- **ĐỔI:** áp **split-conformal calibration đồng nhất trên cửa sổ validation cho MỌI mô hình** (kể cả
  LightGBM & Chronos); báo cáo **cả bản raw và bản calibrated**. Nhờ đó coverage so sánh được và tách được
  năng lực mô hình khỏi lớp bọc.
- **THÊM:** ghi nhận & xử lý **kẹp đuôi Chronos-Bolt** (chỉ học tới [0.1,0.9]); hạn chế kết luận ở 4 mức
  biên M5 (0.005/0.025/0.975/0.995) hoặc dùng bản calibrated.
- **NÂNG coverage/calibration thành kết quả CHÍNH**, không phải phụ.

### Mục 6 — Phân công

- **P2:** đổi quy tắc sinh mẫu (N≤400/nhóm, xử lý mất cân bằng, sinh cả nhãn cho full 30.490 để weighting).
- **P3 (LightGBM):** giữ; thêm xuất **bản calibrated** theo giao thức chung; native quantile vẫn là điểm mạnh.
- **P4 (cổ điển & FM):** **NB-spec không còn là cách duy nhất** — điểm→phân phối vẫn dùng NB làm bước sinh
  thô, nhưng **bắt buộc đi qua conformal calibration chung** (đồng sở hữu với P5). Ghi rõ cấu hình Chronos
  (`predict_quantiles(inputs=...)`, kẹp đuôi) và pin version `chronos-forecasting`, `granite-tsfm`.
  Moirai-2 để **stretch goal** (chưa kiểm chứng).
- **P5:** thêm (i) **conformal calibration** dùng chung, (ii) **kiểm định ý nghĩa (MCB/DM)** bắt buộc,
  (iii) **hai bảng tổng hợp** balanced & weighted, (iv) coverage là kết quả chính.
- **P1:** giữ; lưu ý downcast & parquet đã chạy tốt; ghi chú ràng buộc actuals ≤ d_1941.

### Mục 5 (phần cứng) & Mục 7 (tham khảo)

- **SỬA giả định phần cứng:** "Colab T4 + fp16 bắt buộc" → **CPU đủ cho pilot** (B6). GPU chỉ cần cho
  **full 30.490 / few-shot / Moirai-2**. Ghi runtime thực đo (Chronos-Bolt ~7s, TTM ~1–3s / vài trăm chuỗi).
- **THÊM lưu ý rò rỉ pre-training** (Chronos/TTM nhiều khả năng đã thấy M5) — nâng từ "gợi ý" lên **cảnh báo
  diễn giải chính** cho mọi kết quả zero-shot.
  - **[ĐÍNH CHÍNH 2026-10-05]** Đã kiểm nguồn: M5 là **tập zero-shot giữ ngoài training** của Chronos/
    Chronos-Bolt (Benchmark II — arXiv:2403.07815) và **không có trong Monash+LibCity** của TTM
    (arXiv:2401.03955) → **rủi ro rò rỉ trực tiếp THẤP**, hạ khỏi mức "cảnh báo chính" (xem PLAN_REVISED Mục 5).
- **THÊM version pinning** cho FM vào phần thiết lập/tham khảo.

---

## Tóm tắt "đổi gì" trong 8 dòng

1. Kết luận: từ "model nào mạnh nhất" → **khuyến nghị có điều kiện, chỉ tuyên bố thắng khi có ý nghĩa thống kê**.
2. Dữ liệu: nêu rõ **test = d_1914–1941** (không có actuals d_1942–1969) và **mất cân bằng 95/5**.
3. Mẫu: **N ≤ 400/nhóm**, báo cáo **cả balanced lẫn weighted/full**.
4. Rolling-origin: **bắt buộc ≥3 cửa sổ**.
5. Metric chính: **chốt WSPL** (SPL phụ) vì hai cái bất đồng.
6. Xác suất: **conformal calibration đồng nhất mọi mô hình**; coverage là kết quả chính; xử lý kẹp đuôi Chronos.
7. Thống kê: **MCB/Diebold-Mariano bắt buộc**.
8. Hạ tầng: **CPU đủ cho pilot**, GPU cho full/few-shot/Moirai; pin version; cảnh báo rò rỉ pre-training.
