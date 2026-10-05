# Plan nghiên cứu (bản chỉnh sửa v2) — So sánh Cổ điển · ML · Foundation Model cho dự báo XÁC SUẤT nhu cầu gián đoạn trong bán lẻ, phân nhóm theo đặc tính nhu cầu

> **Bản v2, 2026-09-22.** Chỉnh sửa từ plan gốc sau khi chạy thử thực tế trên M5
> (notebook `M5_demand_forecasting_study.ipynb`, full 800 chuỗi, 1 cửa sổ). Xem `PLAN_CHANGELOG.md`
> để biết chính xác "đổi gì / vì sao / bằng chứng". Các phần **[MỚI]/[SỬA]** đánh dấu điểm khác plan gốc.

## 1. Giới thiệu bài toán

Nhu cầu bán lẻ theo từng sản phẩm–cửa hàng biến động mạnh và nhiều ngày bằng 0; dự báo sai gây tồn kho
dư thừa hoặc thiếu hàng. Bài toán: dự báo tốt hơn khi dữ liệu nhiều chuỗi gián đoạn, nhiều giá trị 0, và
đặc tính khác nhau giữa các nhóm sản phẩm.

Hai lựa chọn thiết kế giữ nguyên: **dự báo xác suất** (khoảng/quantile) thay vì một điểm, và **phân nhóm
nhu cầu** để so sánh theo từng đặc tính chuỗi thay vì trung bình gộp.

**[SỬA] Bối cảnh dữ liệu thực tế:** trên M5, phân nhóm SBC cho phân bố **rất mất cân bằng** — 95% chuỗi
là intermittent + lumpy, chỉ ~5% là smooth + erratic. Đây là đặc điểm chi phối toàn bộ thiết kế lấy mẫu,
tổng hợp và kết luận (xem Mục 4–5).

## 2. Câu hỏi nghiên cứu & cách kết luận

**Câu hỏi chính (giữ):** mô hình cổ điển, ML và foundation model (FM) hoạt động khác nhau thế nào trên
từng nhóm demand; FM thắng ở đâu, thua ở đâu (zero-shot vs few-shot)?

**[SỬA] Khung kết luận — có điều kiện & có kiểm định.** Sản phẩm cuối là **bảng khuyến nghị "nhu cầu nào
→ dùng model nào"**, KHÔNG phải "model nào mạnh nhất". Bổ sung **luật tuyên bố thắng**:

> Chỉ kết luận một mô hình "thắng" một nhóm khi chênh lệch metric **sống sót qua rolling-origin ≥3 cửa sổ
> VÀ một kiểm định ý nghĩa (MCB hoặc Diebold-Mariano)**. Mặc định là **"tương đương"**; chênh vài % là
> tương đương, không phải thắng.

**[SỬA] Kỳ vọng ban đầu (đã đối chiếu pilot, sẽ tái kiểm ở full-scale):**
- Cổ điển (TSB/SBA/Croston) mạnh ở intermittent/lumpy → *đúng một phần*: **tương đương** LightGBM ở hai
  nhóm này nhưng **chi phí thấp hơn nhiều** (điểm cộng vận hành).
- LightGBM (quantile) mạnh & **ổn định nhất** xuyên các nhóm trong pilot; thắng rõ ở lumpy.
- FM (Chronos-Bolt) **mạnh ở độ chính xác điểm (RMSSE)** ở smooth/erratic, nhưng **hiệu chuẩn xác suất kém**
  (thiếu phủ đuôi). TTM chạy được nhưng chưa nổi bật.
- **Cảnh báo confound:** so sánh SPL/coverage bị nhiễu bởi *cách sinh quantile* của từng họ mô hình
  (xem Mục 5, giao thức xác suất). Phải khử nhiễu này trước khi diễn giải.

Kết quả trái kỳ vọng vẫn báo cáo trung thực.

## 3. Kiến thức nền tảng

Giữ: time-series forecasting (lag, mùa vụ, rolling, split theo thời gian), retail demand forecasting
(giá/khuyến mãi/lễ/mùa vụ), intermittent demand, phân nhóm SBC (ADI, CV²), dự báo xác suất (quantile).

**[MỚI]** Bổ sung hai khối nền:
- **Hiệu chuẩn dự báo xác suất (calibration)** & **conformal prediction** — cơ chế để *(i)* làm coverage
  so sánh được giữa các họ mô hình, *(ii)* tách năng lực mô hình khỏi "lớp bọc" sinh quantile.
- **Kiểm định độ chênh mô hình:** MCB (Multiple Comparison with the Best) và Diebold-Mariano.

## 4. Bộ dữ liệu

Bộ M5 (Walmart): 30.490 chuỗi sản phẩm–cửa hàng (3.049 SP × 10 cửa hàng, 3 bang, 3 ngành), ~1.941 ngày;
kèm `calendar` (lễ, sự kiện, SNAP) và `sell_prices` (giá theo tuần).

**[SỬA] Ràng buộc split thực tế (quan trọng).** File `sales_train_evaluation.csv` chỉ chứa actuals đến
**d_1941**. Actuals holdout M5 chính thức (**d_1942–1969**) **không có** trong bộ này. Vì vậy chốt split
nội bộ, tối đa hoá actuals sẵn có:

| Phần | Ngày | Vai trò |
|---|---|---|
| train | d_1 … d_1885 | huấn luyện |
| validation | d_1886 … d_1913 | tune + **hiệu chuẩn conformal** |
| test | d_1914 … d_1941 (28 ngày) | đánh giá |

*(Nếu muốn đúng chuẩn M5 Uncertainty: tải bộ actuals cuối đã phát hành cho d_1942–1969.)*

**[MỚI] Phân bố nhóm demand thực tế (toàn bộ 30.490 chuỗi):**

| Nhóm | Số chuỗi | Tỷ lệ | Zero-rate TB |
|---|---:|---:|---:|
| smooth | 980 | 3.2% | 0.14 |
| erratic | 494 | 1.6% | 0.17 |
| intermittent | 23.096 | 75.7% | 0.74 |
| lumpy | 5.920 | 19.4% | 0.60 |

→ 95% dữ liệu là intermittent+lumpy; smooth/erratic hiếm → chi phối lấy mẫu & tổng hợp (Mục 5).

## 5. Thiết lập chung

Mọi mô hình chạy trên **cùng split, cùng horizon 28 ngày, cùng danh sách chuỗi mẫu, cùng bộ đo**.

**[SỬA] Lấy mẫu phân tầng.** "min(có sẵn, 1000)/nhóm" **bất khả thi** (erratic chỉ 494, smooth 980).
Thay bằng một trong hai (chốt trong `config.yaml`):
- **(a)** `N ≤ 400`/nhóm (balanced, khả thi cho cả 4 nhóm), hoặc
- **(b)** lấy **toàn bộ** erratic + smooth, cap intermittent + lumpy về cùng cỡ; ghi rõ mức mất cân bằng.
- Pilot đã dùng 200/nhóm (=800 chuỗi) — hợp lệ, dùng làm mốc.

**[MỚI] Hai góc báo cáo (bắt buộc cả hai):**
1. **Balanced-per-segment** — để so sánh theo *đặc tính* chuỗi (trục phân tích chính).
2. **Frequency-weighted / full 30.490** (cổ điển + LightGBM chạy full; FM chạy mẫu) — để phản ánh *vận hành*
   thật, tránh việc trung bình gộp 4 nhóm cân bằng thổi phồng smooth/erratic ~30× so với tần suất thật.

**[SỬA] Rolling-origin: BẮT BUỘC ≥3 cửa sổ test 28 ngày trượt liên tiếp** (không còn "nếu compute cho
phép"). Lý do: pilot 1 cửa sổ cho chênh lệch 2–3% ⇒ không phân biệt được mô hình.

**[SỬA] Metric & pre-registration.**
- **Điểm:** RMSSE (chính), MASE (phụ).
- **Xác suất:** **WSPL (dollar-weighted, chuẩn M5 Uncertainty) là metric CHÍNH**; SPL (unweighted) là phụ.
  *(Chốt trước khi xem kết quả — vì pilot cho thấy WSPL và SPL bất đồng ở nhóm erratic.)*
- **Hiệu chuẩn:** empirical coverage cho các cặp quantile đối xứng — **nâng thành kết quả chính**.
- **Kiểm định:** **MCB hoặc Diebold-Mariano bắt buộc** để gắn nhãn "thắng rõ / tương đương".

**[MỚI] Giao thức xác suất — hiệu chuẩn công bằng cho MỌI mô hình.**
Vấn đề: mỗi họ sinh quantile khác nhau (LightGBM native; Chronos native nhưng **kẹp đuôi [0.1,0.9]**;
cổ điển + TTM **bọc Negative Binomial**) ⇒ SPL/coverage đo lẫn cả "lớp bọc". Giải pháp:
- Sinh quantile thô theo cách tự nhiên của từng model (native / NB), **rồi áp split-conformal calibration
  đồng nhất trên cửa sổ validation cho TẤT CẢ mô hình**.
- **Báo cáo cả bản raw lẫn bản calibrated.** Bản calibrated dùng cho so sánh công bằng; bản raw để bàn về
  hành vi gốc (vd kẹp đuôi Chronos, thừa phủ của NB).
- 9 mức quantile M5 giữ nguyên `[0.005,0.025,0.165,0.25,0.5,0.75,0.835,0.975,0.995]`.

**Ba mối nối đông cứng (cập nhật):**
1. Schema dữ liệu long.
2. Format forecast: `series_id, date, quantile_level, value` (thêm `d_int` nội bộ để join).
3. **[SỬA]** "Giao thức hiệu chuẩn chung" (không chỉ là cách phát quantile cho model điểm): NB/native →
   **conformal calibration dùng chung**, hàm ở `src/common/`.

**[SỬA] Phần cứng.** **CPU đủ cho pilot** (Chronos-Bolt ~7s, TTM ~1–3s cho vài trăm chuỗi). **GPU chỉ cần
cho:** full 30.490 chuỗi, few-shot, và Moirai-2. FM dùng size small/base + fp16 khi có GPU. Full-data xử lý
bằng parquet + downcast/polars (đã kiểm chứng chạy tốt).

**[MỚI] Version pinning & lưu ý FM:** pin `chronos-forecasting`, `granite-tsfm`, `statsforecast`, `lightgbm`.
Chronos-Bolt gọi **`predict_quantiles(inputs=..., prediction_length=..., quantile_levels=...)`**.
**[SỬA 2026-10-05] Lưu ý rò rỉ pre-training (đã kiểm nguồn):** M5 là **tập zero-shot giữ ngoài training**
của Chronos/Chronos-Bolt (Benchmark II — Ansari et al. 2024, arXiv:2403.07815) và **không nằm trong
Monash+LibCity** của TTM (Ekambaram et al. 2024, arXiv:2401.03955) → **rủi ro rò rỉ trực tiếp thấp**. Vẫn
diễn giải zero-shot thận trọng (corpus Chronos-Bolt không công bố đầy đủ), nhưng **không còn là "cảnh báo
chính"** như giả định ban đầu.

Đồng bộ & seed: `configs/sample_ids.csv` + `configs/config.yaml` (`seed: 42`), sinh một lần bởi P2.

## 6. Phân công chi tiết theo người

### P1 — Dữ liệu & hạ tầng (kiêm điều phối)
Tải M5; repo skeleton + `src/common/` (chốt schema cùng P5). Wide→long; join calendar + sell_prices;
feature nền dùng chung. **[SỬA]** Ghi chú ràng buộc actuals ≤ d_1941 và ngày split ở `schema.py`.
Output: `data/data_long.parquet`, `src/common/schema.py`, README + requirements (kèm **version pin**).

### P2 — EDA & phân nhóm demand
EDA (zero-rate, phân phối, mùa vụ, tác động giá/event/SNAP). Tính ADI & CV², áp ngưỡng SBC (ADI=1.32,
CV²=0.49) → 4 nhóm. **[SỬA]** Sinh mẫu theo quy tắc mới (N≤400/nhóm hoặc lấy toàn bộ nhóm hiếm), **ghi rõ
mất cân bằng**, và **sinh nhãn cho full 30.490** để phục vụ weighting. Output: `data/segment_labels.parquet`
(cho toàn bộ), `configs/sample_ids.csv`, bảng phân bố nhóm (đối chiếu Mục 4).

### P3 — Mô hình machine learning
Feature lag/rolling/days-since-last-sale/calendar/price. **[LƯU Ý leak-free]** dùng lag ≥ horizon để cả
28 ngày test tính được từ dữ liệu ≤ ngày gốc. LightGBM global; 9 quantile bằng quantile regression native.
**[SỬA]** Xuất **bản raw và bản calibrated** (qua giao thức chung với P5). Two-stage là ablation tùy chọn.
Output: `outputs/forecasts/lgbm.parquet` (+ `lgbm_cal.parquet`), feature importance + config.

### P4 — Mô hình cổ điển & foundation model
Cổ điển: Naive, SeasonalNaive(7), Croston, SBA, TSB (statsforecast). **[SỬA]** point → phân phối thô bằng
NB, **rồi qua conformal calibration chung** (đồng sở hữu với P5) — NB không còn là bước cuối.
FM (chạy mẫu): **Chronos-Bolt (base) + TTM** zero-shot (đã kiểm chứng CPU); Moirai-2 là **stretch goal**;
few-shot nếu kịp (cần GPU). **[SỬA]** Ghi cấu hình Chronos (`predict_quantiles(inputs=...)`, kẹp đuôi
[0.1,0.9]), TTM (context 512, PL 96 → cắt 28). Đo runtime/tài nguyên mỗi FM. Output: các `*.parquet` cùng
format (raw + calibrated) + bảng runtime/cấu hình.

### P5 — Giao thức xác suất, đánh giá & tổng hợp
**[SỬA/MỞ RỘNG]** Chốt `src/common/` (`metrics.py`, `forecast_io.py`, **`calibration.py`** — split-conformal
dùng chung). Harness đọc mọi forecast, tính RMSSE, WSPL/SPL, **coverage (kết quả chính)**; join
`segment_labels`. **Thêm:** (i) **kiểm định MCB/Diebold-Mariano** để gắn nhãn thắng/tương đương;
(ii) **hai bảng tổng hợp**: balanced-per-segment & frequency-weighted (hoặc full); (iii) error analysis
over/under-forecast, xử lý chuỗi nhiều 0; (iv) biểu đồ forecast vs actual. Output: `metrics.py`,
`calibration.py`, các bảng model×nhóm (raw & calibrated), bảng "model thắng theo nhóm" **kèm p-value/nhãn
ý nghĩa**, biểu đồ.

## 7. Tài liệu tham khảo

Giữ nguyên các mục gốc (M5 competition; Chronos; Wang–Kang–Petropoulos; Oliveira–Ramos; Two-Stage fashion
retail; bộ M5 Kaggle). **[MỚI] Bổ sung:**
- Conformal prediction cho time series (calibration công bằng đa mô hình).
- Koning/Makridakis MCB & Diebold–Mariano (kiểm định độ chênh dự báo).
- Chronos-Bolt / Moirai-2 (Moirai-MoE) / TTM (IBM Granite) — cập nhật khi triển khai FM 2026, **pin version**.
- **Rủi ro rò rỉ pre-training thấp** (M5 là zero-shot benchmark của Chronos; không có trong corpus TTM) — vẫn diễn giải zero-shot thận trọng.

---

## Phụ lục A — Bằng chứng pilot (full 800 chuỗi, 1 cửa sổ) làm mốc

| Nhóm | Thắng theo SPL | Chênh | Thắng theo RMSSE | Coverage-95 Chronos | Coverage-95 nhóm bọc-NB |
|---|---|---:|---|---:|---:|
| smooth | lgbm | 2.1% (tương đương) | chronos_bolt (0.692) | 0.80 | 0.98 |
| erratic | chronos_bolt | 2.6% (tương đương) | chronos_bolt (0.683) | 0.81 | 0.95–0.99 |
| intermittent | lgbm | 2.8% (tương đương) | ~ (chronos 0.816 ≈ lgbm 0.818) | 0.75 | 0.96–0.99 |
| lumpy | lgbm | 6.4% (thắng rõ) | lgbm (0.749) | 0.77 | 0.95–0.98 |

*Lưu ý: pilot 1 cửa sổ, chưa kiểm định ý nghĩa, quantile chưa hiệu chuẩn đồng nhất → chỉ dùng làm mốc.
WSPL đảo ngôi ở erratic (chronos < lgbm). Các con số này sẽ được tái tạo ở full-scale theo bản v2.*
