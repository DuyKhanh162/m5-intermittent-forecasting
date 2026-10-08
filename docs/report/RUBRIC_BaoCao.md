# Tiêu chí đánh giá chất lượng báo cáo tổng hợp (thang 10)

Dùng để chấm `BaoCao_Tong_Hop.md` trước khi bàn giao. **Ngưỡng đạt: ≥ 9.0/10.**

| # | Tiêu chí | Trọng số | ĐẠT (điểm tối đa) khi |
|---|---|---|---|
| C1 | **Hoàn chỉnh cấu trúc & nội dung** | 2.0 | Có đủ: tóm tắt · câu hỏi nghiên cứu · dữ liệu · phương pháp (cả 3 họ model + hiệu chuẩn + kiểm định) · kết quả · thảo luận · giới hạn · kết luận · tài liệu. Tích hợp đủ **cả 5 phần P1–P5**. |
| C2 | **Chính xác & trung thực số liệu** | 2.0 | Mọi con số khớp output thật (metrics, decision_table, EDA); không bịa; mỗi khẳng định có số/bằng chứng kèm; phân biệt rõ "thắng rõ" vs "tương đương". |
| C3 | **Chặt chẽ phương pháp (rigor)** | 2.0 | Nêu rõ no-leakage (lag≥H, split, scale train-only), hiệu chuẩn conformal từ val, DM+Holm+MCB, win-rule. Nêu **đủ các giới hạn** (rò rỉ pre-training FM, bất đối xứng horizon, coverage rời rạc). |
| C4 | **Mạch lạc & trình bày** | 1.5 | Bố cục logic, có bảng/hình đánh số & được tham chiếu, thuật ngữ nhất quán, đọc trôi. |
| C5 | **Chiều sâu diễn giải & kết luận** | 1.5 | Trả lời rõ "nhu cầu nào → model nào" có điều kiện; hàm ý vận hành (chọn model rẻ khi tương đương); error analysis được diễn giải; không over-claim. |
| C6 | **Trích dẫn & tài liệu** | 1.0 | Trích nguồn chính (M5, SBC Syntetos–Boylan, Chronos, TTM, conformal, DM/MCB) đúng chỗ. |

## Cách chấm
- Mỗi tiêu chí cho điểm theo tỷ lệ đạt (0 → max).
- Tổng = Σ. Nếu < 9.0 → ghi rõ tiêu chí thiếu + sửa, chấm lại. Lặp đến khi ≥ 9.0.
- Ưu tiên kiểm C2 (số liệu) bằng cách đối chiếu trực tiếp với `data/outputs/*`.
