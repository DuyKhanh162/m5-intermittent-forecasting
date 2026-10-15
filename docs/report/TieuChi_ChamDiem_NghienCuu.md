# Khung tiêu chí chấm điểm bài nghiên cứu (thang 10)

Dùng để chấm **toàn bộ project** ("So sánh mô hình cổ điển, machine learning và time-series
foundation model cho dự báo xác suất nhu cầu gián đoạn trong bán lẻ, có phân nhóm theo đặc
tính nhu cầu") như **một bài nghiên cứu khoa học**. Tổng 10 điểm trên 8 tiêu chí.

> **Khác biệt với `RUBRIC_BaoCao.md`:** file đó chấm *chất lượng trình bày của bản báo cáo*;
> file này chấm *chất lượng của công trình nghiên cứu* (có thêm trục tái lập & đóng góp khoa học).

| # | Tiêu chí | Điểm tối đa | Mô tả mức ĐẠT điểm tối đa |
|---|---|---:|---|
| C1 | **Đặt vấn đề & câu hỏi nghiên cứu** | 1.0 | Vấn đề rõ ràng, có động lực thực tiễn (demand gián đoạn → cần dự báo xác suất); câu hỏi nghiên cứu **cụ thể, kiểm chứng được** ("nhu cầu nào → model nào", "FM có hơn không") và được trả lời trọn vẹn ở kết luận. |
| C2 | **Tổng quan & nền lý thuyết** | 1.5 | Trình bày đủ và chính xác: chuỗi thời gian, SBC, dự báo điểm vs xác suất, **cả 3 họ model**, bọc NB, conformal, metric & kiểm định. Có trích dẫn nguồn gốc (SBC, Croston/TSB, Chronos/TTM/Moirai, conformal, DM/MCB) đặt đúng chỗ. |
| C3 | **Dữ liệu & phương pháp (rigor)** | 2.0 | Mô tả dữ liệu M5 đầy đủ; thiết kế thực nghiệm chặt: **no-leakage** (lag ≥ H, split theo thời gian, scale train-only), rolling-origin ≥ 3 cửa sổ, lấy mẫu phân tầng hợp lý; **hiệu chuẩn split-conformal từ validation** để so sánh công bằng; giao thức **pre-registered**. Trừ điểm nếu có rò rỉ, thiếu mô tả, hoặc so sánh không công bằng. |
| C4 | **Thực nghiệm & kết quả** | 1.5 | Kết quả đầy đủ cho cả 3 họ model × 4 nhóm; có bảng/hình đánh số & tham chiếu; báo cả raw & calibrated, cả balanced & frequency-weighted; số liệu **khớp output thật** (`data/outputs/*`, notebook), không bịa. |
| C5 | **Kiểm định thống kê & tính trung thực** | 1.5 | Có kiểm định phù hợp (**DM panel + Holm**, MCB tham chiếu) với **win-rule khắt khe**; phân biệt rõ "thắng rõ" vs "tương đương"; **không over-claim** (FM chưa đủ bằng chứng → nói đúng như vậy); mọi khẳng định có số/bằng chứng kèm. |
| C6 | **Thảo luận, đóng góp & hạn chế** | 1.0 | Diễn giải có chiều sâu (error analysis, hàm ý vận hành "chọn model rẻ khi tương đương"); nêu **đóng góp** (khung so sánh công bằng + kết luận có điều kiện theo nhóm); nêu **đủ hạn chế** (rò rỉ pre-training FM, bất đối xứng horizon, coverage rời rạc, phạm vi mẫu). |
| C7 | **Trình bày & trích dẫn** | 1.0 | Bố cục chuẩn học thuật (chương/mục, mục lục, danh mục hình/bảng, tài liệu tham khảo); thuật ngữ nhất quán; văn mạch lạc, đọc trôi; hình/bảng rõ, có chú thích; trích dẫn đúng chuẩn. |
| C8 | **Khả năng tái lập (reproducibility)** | 0.5 | Có mã nguồn/notebook chạy lại được, seed cố định, mô tả cấu hình; output & hình truy nguyên được từ dữ liệu; đường dẫn dữ liệu/kết quả rõ ràng. |

**Tổng: 10.0 điểm.**

## Cách chấm
- Mỗi tiêu chí cho điểm theo tỷ lệ đạt (0 → tối đa), có thể lấy 0.25 làm bước.
- Tổng = Σ các tiêu chí. Ghi chú ngắn lý do trừ điểm cho từng tiêu chí.
- **Ưu tiên kiểm C3–C5** (rigor, kết quả, kiểm định) vì đây là lõi của một bài nghiên cứu;
  đối chiếu trực tiếp với `data/outputs/*` và các notebook `P1–P5.ipynb`.
- Thang quy đổi gợi ý: **≥ 9.0** xuất sắc · **8.0–8.9** tốt · **7.0–7.9** khá · **< 7.0** cần sửa.

## Thang mức chất lượng cho từng tiêu chí (tham khảo)
- **Tốt (100% điểm):** đạt đầy đủ như mô tả cột "ĐẠT điểm tối đa".
- **Khá (~70%):** đạt phần lớn, thiếu một vài chi tiết không cốt lõi.
- **Trung bình (~50%):** có làm nhưng thiếu/sai ở điểm quan trọng (vd thiếu một họ model, kiểm định sơ sài).
- **Yếu (≤ 30%):** thiếu hẳn hoặc có lỗi phương pháp nghiêm trọng (rò rỉ dữ liệu, bịa số, over-claim).
