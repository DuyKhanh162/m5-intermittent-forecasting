# Hướng dẫn làm slide (Bước 10b) — P2 chủ trì

Khung **khái quát** ~12 slide. Mỗi slide ghi **ý chính + nguồn lấy nội dung**; P2 tự chọn bố cục/hình/độ sâu cho phù hợp thời lượng. Nguồn chung:
- Lý thuyết: `docs/theory/LyThuyet.md`
- Số liệu & kết luận: `docs/report/BaoCao_Tong_Hop.md`
- Hình sẵn: `docs/report/img/` (WSPL, coverage, RMSSE) + biểu đồ trong `P1/P2/P4/P5.ipynb`

| # | Slide | Ý chính (khái quát) | Nguồn |
|---|---|---|---|
| 1 | **Trang bìa / Giới thiệu** | Tên đề tài · nhóm · câu hỏi lõi "nhu cầu nào → model nào" | Báo cáo §1 |
| 2 | **Mục lục** | Liệt kê các phần slide | — |
| 3 | **Đặc trưng bộ dữ liệu** | M5 (30.490 chuỗi × 1.941 ngày) · SNAP/giá · **95% gián đoạn** · 4 nhóm SBC | Báo cáo §2 + biểu đồ P1/P2 |
| 4 | **Lý thuyết — Cổ điển** | Naive/SNaive/Croston/SBA/TSB + bọc NB (tách cỡ bán/khoảng cách) | Lý thuyết §4.1 |
| 5 | **Lý thuyết — Machine Learning** | LightGBM quantile: feature + boosting + 9 phân vị | Lý thuyết §4.2 |
| 6 | **Lý thuyết — Foundation Model** | Chronos/TTM/Moirai: zero-shot, cơ chế quantile, kẹp đuôi, rò rỉ | Lý thuyết §4.3 |
| 7 | **Cách làm + kết quả — Cổ điển** | Rolling-origin + bọc NB; Croston/SBA tốt nhất họ cổ điển | Báo cáo §4.1, §5 + bảng 3 |
| 8 | **Cách làm + kết quả — ML** | Feature leak-free (lag≥28); **LightGBM WSPL thấp nhất tổng thể** | Báo cáo §4.1, §5 + hình WSPL |
| 9 | **Cách làm + kết quả — FM** | Zero-shot + hiệu chuẩn conformal (cov95 **0,75→0,95**); runtime | Báo cáo §4.2–4.3, §5.3 + hình coverage |
| 10 | **Đánh giá** | Metric (WSPL/coverage) · kiểm định DM/MCB · bảng quyết định theo nhóm | Báo cáo §5.4 + bảng 4 |
| 11 | **Kết luận** | smooth→lgbm (thắng rõ); 3 nhóm còn lại **tương đương** → chọn rẻ; FM chưa vượt; **không model thắng tuyệt đối** | Báo cáo §7 |
| 12 | **Lời cảm ơn** | Cảm ơn GVHD, nhóm, nguồn dữ liệu M5 | — |

**Lưu ý trình bày (gợi ý, không bắt buộc):**
- Mỗi slide lý thuyết: nêu **1–2 công thức/ý cốt lõi**, tránh nhồi chữ.
- Mỗi slide kết quả: **1 bảng hoặc 1 hình** làm điểm nhấn (dùng hình có sẵn trong `docs/report/img/`).
- Kết luận nhấn thông điệp: *lựa chọn model phụ thuộc nhóm nhu cầu; phần lớn nằm trong sai số thống kê → tối ưu chi phí vận hành.*
- Nếu có thời lượng: tách "Đánh giá" và "Kết luận" thành 2 slide; nếu ngắn, gộp 1.
