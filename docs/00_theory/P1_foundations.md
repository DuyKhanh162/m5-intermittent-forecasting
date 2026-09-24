# Bước 0 — Nền lý thuyết chung (P1)

> Phần lý thuyết P1 chủ trì: nền tảng xuyên suốt (không thuộc model cụ thể nào) + vai trò
> biên tập (phát template, thống nhất ký hiệu, gộp tài liệu — tiền đề cho 10a).

## 1. Chuỗi thời gian cơ bản
- **Chuỗi thời gian**: quan sát theo trục thời gian, có thứ tự; không được xáo trộn.
- **Lag**: giá trị quá khứ $y_{t-k}$ dùng làm đặc trưng dự báo.
- **Tính mùa vụ**: chu kỳ lặp (tuần: wday; năm: tháng). M5 có mùa vụ tuần rõ.
- **Rolling window**: thống kê trượt (mean/std) trên cửa sổ gần nhất.

## 2. Vì sao cấm shuffle & split theo thời gian
Thực tế chỉ có **quá khứ** để dự báo **tương lai**. Nếu test lọt vào train (shuffle ngẫu nhiên)
= "nhìn trộm" tương lai → điểm đẹp giả, không dùng được thật. Vì vậy:
- Chia theo **mốc thời gian**, không ngẫu nhiên.
- Mọi thao tác (feature, hiệu chuẩn) chỉ dùng dữ liệu ≤ ngày gốc.
- **Rolling-origin evaluation** (nền bước 8): trượt điểm gốc lùi ≥3 lần, mỗi lần dự báo 1 cửa sổ
  28 ngày mới → đo model nào ỔN ĐỊNH qua thời gian, không bị may rủi 1 cửa sổ.

## 3. Cấu trúc dữ liệu M5
- **Wide vs long**: wide = mỗi chuỗi 1 hàng, mỗi ngày 1 cột (M5 gốc); long = mỗi (chuỗi, ngày)
  1 hàng. Chỉ long mới join được calendar/giá và là định dạng model xử lý tự nhiên.
- **calendar**: ngày lễ (event), **SNAP** (ngày phát trợ cấp thực phẩm Mỹ — nhu cầu Foods tăng vọt,
  dùng làm biến ngoại sinh), wday/month/year.
- **sell_prices**: giá theo tuần (wm_yr_wk).
- **Ràng buộc quan trọng**: `sales_train_evaluation.csv` chỉ có actuals tới **d_1941**;
  actuals d_1942–1969 KHÔNG có → split test = d_1914–1941.

## 4. Intermittent demand & ADI/CV²
- **Intermittent demand**: chuỗi nhiều ngày = 0, nhu cầu không xuất hiện đều → phá vỡ ARIMA/ETS.
- Đo trên 2 chiều: **ADI** (độ gián đoạn) và **CV²** (độ loạn của cỡ bán) → 4 nhóm SBC
  (smooth / erratic / intermittent / lumpy). M5: ~95% là intermittent + lumpy (nền cho P2 nói sâu).

## 5. Dự báo điểm vs xác suất & bộ metric
- **Điểm**: 1 giá trị $\hat{y}$. **Xác suất**: dải/quantile (P10/P50/P90) — cần vì sai số bất đối xứng
  (thiếu hàng ≠ thừa hàng).
- Bộ metric (chi tiết ký hiệu trong `notation.md`): **RMSSE** (điểm, chính), **WSPL** (xác suất, chính,
  dollar-weighted), **Coverage** (hiệu chuẩn, chính); MASE & SPL phụ.
- Không dùng MAE/RMSE thường: không scale, không cộng gộp giữa chuỗi khác quy mô, không phạt bất đối xứng.

## Vai trò điều phối của P1 ở bước 0
1. Phát `TEMPLATE_model_theory.md` cho P2–P5 (mỗi model 4 ý).
2. Thống nhất `notation.md`.
3. Gộp 5 phần thành 1 tài liệu lý thuyết, kiểm ký hiệu nhất quán (đầu vào cho báo cáo 10a).
