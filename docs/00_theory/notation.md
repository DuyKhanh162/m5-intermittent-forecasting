# Bảng ký hiệu thống nhất — Bước 0 (P1 chủ trì)

> Cả nhóm dùng CHUNG ký hiệu này trong lý thuyết, code và báo cáo. Sửa phải báo P1.

| Ký hiệu | Ý nghĩa |
|---|---|
| $y_{i,t}$ | nhu cầu (sales) của chuỗi $i$ tại ngày $t$ |
| $i$ | chỉ số chuỗi = cặp (sản phẩm × cửa hàng), `series_id` |
| $t$ | chỉ số ngày; `d_int` = 1..1941 |
| $h$ | bước dự báo trong horizon; $H=28$ |
| $\hat{y}_{i,t}$ | dự báo điểm (P50) |
| $q_{i,t}^{(u)}$ | quantile mức $u$ của chuỗi $i$, ngày $t$ |
| $u$ | mức quantile ∈ {0.005, 0.025, 0.165, 0.25, 0.5, 0.75, 0.835, 0.975, 0.995} |
| ADI | Average Demand Interval — khoảng TB giữa 2 lần bán ≠ 0 |
| CV² | bình phương hệ số biến thiên của **cỡ bán** (kỳ ≠ 0) |
| $\alpha$ | tham số làm mượt (Croston/SBA/TSB) |
| RMSSE | Root Mean Squared Scaled Error (điểm, chính) |
| MASE | Mean Absolute Scaled Error (điểm, phụ) |
| SPL | Scaled Pinball Loss (xác suất, phụ) |
| WSPL | Weighted (dollar) SPL (xác suất, **chính**, chuẩn M5) |
| Coverage | tỷ lệ actual rơi trong dải danh nghĩa (hiệu chuẩn, **chính**) |

**Ngưỡng SBC:** ADI = 1.32, CV² = 0.49 → 4 nhóm.

**Split:** train ≤ d_1885 · val d_1886–1913 · test d_1914–1941. Actuals tối đa = **d_1941**.

**Quy ước metric:** mọi metric THẤP = tốt, trừ Coverage (gần mức danh nghĩa = tốt).
