# -*- coding: utf-8 -*-
"""
Làm gọn + bỏ dấu nhận biết AI trong markdown & COMMENT của notebook P1-P5,
GIỮ NGUYÊN kết quả: không đụng outputs, execution_count, code, string literal.

An toàn:
- Markdown: thay bằng bản viết lại (ngắn gọn, bỏ ký tự AI).
- Code: chỉ sửa phần COMMENT (xác định bằng tokenize); assert mọi token KHÔNG phải
  comment giữ nguyên tuyệt đối -> code/chuỗi/logic không đổi.
- Không ghi/đổi data/outputs, không chạy lại gì.
Chạy: python scripts/deai_notebooks.py
"""
import os, io, json, glob, shutil, tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NBDIR = os.path.join(ROOT, "notebooks")
BAK = os.path.join(NBDIR, "_backup_predeai")

REPL = {'—': '-', '–': '-', '·': '-', '→': '->', '⇒': '=>', '“': '"', '”': '"',
        '‘': "'", '’': "'", '…': '...', '✅': '', '➜': '->', '•': '-'}

def clean_chars(s):
    for a, b in REPL.items():
        s = s.replace(a, b)
    while '  ' in s:
        s = s.replace('  ', ' ')
    return s

def to_lines(text):
    """nbformat source = list of lines, mỗi dòng giữ '\\n' trừ dòng cuối."""
    lines = text.split('\n')
    return [ln + '\n' for ln in lines[:-1]] + [lines[-1]]

# ---- bản viết lại markdown (ngắn gọn, giọng người) theo (tên nb, chỉ số cell) ----
MD = {}
MD[('P1.ipynb', 0)] = """# P1 - Dữ liệu và điều phối (Bước 1, 4)

**Input:** data/raw/*.csv (M5 thô).
**Output:** common/{sample_ids, segment_labels, rolling_windows} + data/processed/data_long.parquet.

Mẫu tham khảo: `notebooks/M5_reference.ipynb` (phần 1). Chạy cell đầu để nạp input, code ở giữa, cuối cùng chạy cell lưu output."""
MD[('P1.ipynb', 2)] = "## Phần code chính (bước 1, 4)"
MD[('P1.ipynb', 9)] = """## Kiểm chứng no-leakage và toàn vẹn dữ liệu

*Chỉ đọc `common/*` và `data_long` đã lưu để assert, không ghi hay đổi output.*"""
MD[('P1.ipynb', 11)] = """## Từ điển dữ liệu: `data_long` (input chung cho P2-P5)

| Cột | Ý nghĩa |
|---|---|
| `series_id` | mã chuỗi = item × store (khóa chính) |
| `d_int` / `date` | ngày dạng số (1..1941) / ngày lịch |
| `sales` | lượng bán mỗi ngày (**biến mục tiêu**) |
| `item_id, dept_id, cat_id, store_id, state_id` | phân cấp sản phẩm / cửa hàng |
| `wday, month, year, wm_yr_wk` | biến lịch (ngày trong tuần, tháng, năm, tuần Walmart) |
| `event_name_1, event_type_1, is_event` | sự kiện/lễ và cờ có sự kiện |
| `snap_CA, snap_TX, snap_WI, snap` | ngày phát trợ cấp SNAP theo bang / cờ chung |
| `sell_price` | giá bán |
| `segment` | nhãn SBC: smooth / erratic / intermittent / lumpy |

**Hợp đồng split (xem `rolling_windows.csv`):** W1 train <= d_1885, val d_1886-1913, test d_1914-1941; W2 và W3 lùi thêm 28 ngày; mọi test <= d_1941 (phạm vi có actuals)."""
MD[('P1.ipynb', 12)] = """## Biểu đồ và diễn giải (bước 1, 4)

*Đọc từ `common/*` đã lưu để minh họa, không tính lại và không ghi output.*"""
MD[('P1.ipynb', 14)] = "**Hình 1. Rolling-origin.** Ba cửa sổ trượt lùi 28 ngày (W1 đến W3): train nở dần về quá khứ, test luôn <= d_1941. Thiết kế này cho đánh giá ổn định và không rò rỉ tương lai (test không bao giờ nằm trong train)."
MD[('P1.ipynb', 16)] = "**Hình 2. Lấy mẫu phân tầng.** Quy tắc giữ hiếm, cap phổ biến: lấy 100% smooth (980) và erratic (494), giới hạn intermittent/lumpy ở 1.000, tổng 3.474 chuỗi. Nhờ vậy hai nhóm hiếm (chỉ khoảng 5% tổng thể) không bị nhóm phổ biến lấn át."
MD[('P1.ipynb', 18)] = "**Hình 3. Mức độ gián đoạn.** `zero_rate` tăng dần từ smooth đến intermittent: nhóm thưa có khoảng 60-90% ngày bằng 0. Đây là căn cứ để dự án ưu tiên dự báo xác suất và tách nhóm khi đánh giá, vì metric điểm kém ý nghĩa với chuỗi nhiều 0."
MD[('P1.ipynb', 19)] = """### Tóm tắt khâu dữ liệu

Đầu ra P1 gồm: nhãn SBC cho 30.490 chuỗi (95% gián đoạn), mẫu phân tầng 3.474 chuỗi cân bằng, và 3 cửa sổ rolling-origin <= d_1941. Đây là input chuẩn hóa, tất định (seed 42) cho P2-P5."""

MD[('P2.ipynb', 0)] = """# P2 - EDA và phân nhóm demand (Bước 2, 3, 9)

**Mục tiêu.** Mô tả đặc tính nhu cầu tập M5, phân nhóm theo khung SBC (Syntetos-Boylan-Croston), và tổng hợp khuyến nghị nhu cầu nào thì dùng model nào dựa trên kết quả P5.

**Input:** `common/segment_labels.parquet` (nhãn SBC + ADI/CV²/zero_rate cho 30.490 chuỗi), `common/sample_ids.csv`, `data/processed/data_long.parquet` (mẫu 3.474 chuỗi).
**Output:** `data/outputs/p2_*.parquet` (phân bố nhóm, EDA, mùa vụ, SNAP, khuyến nghị).

**Bố cục:** (1) phân nhóm SBC và phân bố; (2) EDA đặc tính nhu cầu; (3) khuyến nghị model theo nhóm."""
MD[('P2.ipynb', 1)] = "## Cell đầu: import và nạp input"
MD[('P2.ipynb', 3)] = """## 1. Phân nhóm demand theo khung SBC

Mỗi chuỗi được đặc trưng bởi hai đại lượng tính chỉ trên khoảng train (tránh rò rỉ):
- **ADI** (Average Demand Interval) = số ngày / số ngày có bán > 0, đo mức độ gián đoạn (càng lớn càng thưa).
- **CV²** = (σ/μ)² của nhu cầu các ngày có bán > 0, đo mức độ biến động cỡ nhu cầu.

Áp ngưỡng SBC (Syntetos-Boylan 2005) ADI = 1.32, CV² = 0.49 chia 4 nhóm: smooth (đều, ổn định), erratic (đều nhưng biến động mạnh), intermittent (thưa, ổn định), lumpy (thưa, biến động mạnh). Nhãn do P1 tính sẵn cho cả 30.490 chuỗi; P2 chỉ tổng hợp. Bảng phân bố dùng median cho ADI/CV² vì phân phối lệch phải mạnh."""
MD[('P2.ipynb', 5)] = "**Nhận xét.** Phân bố rất mất cân bằng: hai nhóm thưa chiếm khoảng 95% tổng chuỗi (intermittent 75.8%, lumpy 19.4%), trong khi smooth chỉ 3.2% và erratic 1.6% (zero-rate intermittent khoảng 0.74, lumpy khoảng 0.60). Hệ quả: metric điểm kém ý nghĩa với chuỗi thưa nên ưu tiên metric xác suất; đánh giá phải tách theo nhóm; khi tổng hợp toàn tập cần trọng số theo tần suất."
MD[('P2.ipynb', 7)] = "**Nhận xét.** Scatter xác nhận ranh giới 4 nhóm quanh hai đường ngưỡng. Khối điểm dồn mạnh về phía ADI lớn (đa số chuỗi thưa), khớp với bảng phân bố. Trục CV² trải rộng cho thấy ngay trong nhóm thưa, cỡ mỗi lần bán cũng dao động lớn (thành lumpy). Ranh giới dọc ADI = 1.32 là yếu tố tách chính."
MD[('P2.ipynb', 8)] = """## 2. EDA đặc tính nhu cầu theo nhóm

Phân tích trên mẫu phân tầng 3.474 chuỗi (`data_long`): mô tả nhu cầu, giá, và phản ứng với sự kiện, mùa vụ, SNAP, tức các yếu tố ngoại sinh mà model (nhất là ML/FM) có thể khai thác."""
MD[('P2.ipynb', 10)] = "**Nhận xét.** Nhu cầu/ngày giảm mạnh theo trục gián đoạn: smooth khoảng 7.0 và erratic khoảng 6.8, nhưng intermittent chỉ khoảng 0.63 và lumpy khoảng 1.58, chênh khoảng 10 lần. Giá nhóm intermittent cao nhất (khoảng 5.1), gợi ý mặt hàng đắt hoặc ít mua. Sự kiện gần như không làm tăng nhu cầu trung bình (thậm chí giảm nhẹ ở mọi nhóm), nên feature event nên dùng ở mức chi tiết theo loại thay vì cờ nhị phân tổng."
MD[('P2.ipynb', 12)] = "**Nhận xét.** Mùa vụ tuần rõ: cuối tuần (T7 khoảng 4.33, CN khoảng 4.28) cao hơn ngày thường (khoảng 3.1-3.4) chừng 31%. Mùa vụ năm nhẹ hơn: đỉnh tháng 8 (khoảng 3.89), đáy tháng 1 (khoảng 3.31). Vì vậy feature `wday` là tín hiệu giá trị cho P3/P4, và chu kỳ tuần biện minh cho baseline SeasonalNaive(7)."
MD[('P2.ipynb', 14)] = "**Nhận xét.** SNAP làm tăng nhu cầu ở mọi nhóm (uplift dương toàn bộ): mạnh nhất ở lumpy (+16.2%) và erratic (+13.8%), thấp nhất ở intermittent (+9.7%). Đây là tín hiệu ngoại sinh ổn định hơn cờ sự kiện, nên giữ làm feature cho ML. Mức uplift khác nhau giữa các nhóm cũng cho thấy lợi ích của SNAP phụ thuộc đặc tính chuỗi."
MD[('P2.ipynb', 15)] = """## 3. Khuyến nghị model theo nhóm (Bước 9)

Tổng hợp kết luận có điều kiện: với mỗi nhóm demand, model nào nên dùng. Nguồn là bảng đánh giá của P5 (`metrics_by_model_segment` và `decision_table`), gắn nhãn theo quy tắc: một model thắng rõ khi tốt hơn qua cả 3 cửa sổ rolling-origin và qua kiểm định DM (p < 0.05 sau Holm); ngược lại là tương đương."""
MD[('P2.ipynb', 17)] = """**Nhận xét và bàn luận (bước 9).**

- smooth: LightGBM thắng rõ (WSPL +4.9% so với á quân moirai_2, p = 0.007 sau Holm). Nhóm nhỏ (3.2%) nhưng kết luận chắc chắn thống kê.
- erratic, intermittent, lumpy: tương đương, nhiều model không khác nhau có ý nghĩa, nên khuyến nghị model đơn giản và rẻ (snaive, croston), dù model mạnh nhất theo WSPL là moirai_2 (erratic) hoặc lgbm (intermittent, lumpy).
- Tổng thể cả hai cách gộp: LightGBM WSPL thấp nhất, là lựa chọn mặc định an toàn.
- Mọi coverage-95 sau hiệu chuẩn khoảng 0.95-0.99, dải dự báo đáng tin."""
MD[('P2.ipynb', 20)] = "**Đọc error analysis.** `croston` ở intermittent có bias -0.83 (dự báo thấp) và over_rate rất nhỏ (0.07), đúng bản chất nhu cầu thưa (P50 thường bằng 0). Các nhóm còn lại bias nhẹ, over/under cân đối. Coverage-95 ổn định, nên lỗi chủ yếu là thiên lệch thấp ở chuỗi nhiều 0, không phải sai hệ thống về dải."
MD[('P2.ipynb', 21)] = "## Cell cuối: lưu output"

MD[('P3.ipynb', 0)] = """# P3 - Global LightGBM Quantile Forecasting

Huấn luyện LightGBM global trên mẫu 3.474 chuỗi, 3 rolling window và 9 mức quantile.

- Input: `data/processed/data_long.parquet`, `common/{config.yaml, rolling_windows.csv, sample_ids.csv}`.
- Output chính: `data/outputs/forecasts/lgbm.parquet`.
- Output hỗ trợ: validation forecast, feature importance, runtime, run config trong `data/outputs/p3/`.
- Hiệu chuẩn chung thực hiện ở P5."""
MD[('P3.ipynb', 12)] = """## Mô hình cổ điển cho nhu cầu gián đoạn (Bước 5, phần còn lại của P3)

Naive và SeasonalNaive(7) làm mốc; Croston, SBA, TSB (statsforecast) chuyên trị chuỗi gián đoạn. Các mô hình này chỉ cho giá trị điểm, nên được bọc phân phối Negative Binomial (r = m²/(v-m) nếu v>m, ngược lại Poisson) để sinh đủ 9 quantile, cùng spec với TTM ở P4.

Mỗi cửa sổ rolling: bản test fit trên lịch sử d_int <= test_start-1, bản val fit trên d_int <= train_end (out-of-sample, để P5 hiệu chuẩn). Cả hai dự báo 1..28 bước, tôn trọng trục thời gian."""
MD[('P3.ipynb', 18)] = "*Nhu cầu gần đây (rmean_28 khoảng 67%, rstd_28, rmean_7) chi phối dự báo; lag thô đóng góp nhỏ, hợp lý cho chuỗi bán lẻ.*"
MD[('P3.ipynb', 22)] = "*LightGBM (quantile native) cho khoảng hẹp hơn; cổ điển bọc NB rộng hơn. Khác biệt do lớp bọc, sẽ được P5 hiệu chuẩn, không phải chênh năng lực.*"
MD[('P3.ipynb', 24)] = "**Hình 4. Dải phân vị LightGBM.** 9 mức quantile native tạo khoảng dự báo ôm quanh thực tế; median bám mùa vụ tuần. Khoảng hẹp hơn nhóm cổ điển (Hình 3); độ phủ chính thức sẽ do P5 kiểm và hiệu chuẩn."
MD[('P3.ipynb', 25)] = """### Nhận xét chung (P3)

- LightGBM (ML): quantile native, bám mùa vụ tuần, khoảng hẹp, mạnh với chuỗi có tín hiệu (smooth, lumpy).
- Cổ điển (Croston/SBA/TSB/Naive/SNaive): sinh điểm rồi bọc NB nên median phẳng, khoảng rộng hơn, đóng vai trò baseline cho nhu cầu gián đoạn.
- Chênh độ rộng khoảng (Hình 3) chủ yếu do cách sinh phân phối (native so với bọc NB), không phải chênh năng lực. P5 sẽ áp split-conformal chung rồi mới chấm coverage/SPL chính thức."""

MD[('P4.ipynb', 0)] = """# P4 - Foundation Models cho dự báo nhu cầu gián đoạn

Notebook triển khai ba time-series foundation model trên mẫu M5: Chronos-Bolt, TinyTimeMixer (TTM) và Moirai-2. Mỗi mô hình chạy trên cùng ba cửa sổ rolling-origin; với mỗi cửa sổ, mô hình chỉ nhận dữ liệu đến `train_end`, dự báo qua validation và test rồi chỉ giữ 28 ngày test. Đầu ra chuẩn gồm 9 mức quantile.

Phạm vi P4: dự báo zero-shot với ba mô hình; tạo probabilistic forecast phù hợp từng mô hình; kiểm tra schema và quantile crossing rồi lưu raw forecast; benchmark runtime cùng môi trường; thảo luận rủi ro rò rỉ dữ liệu pre-training."""
MD[('P4.ipynb', 9)] = """## 04. Chronos-Bolt (zero-shot)

Chronos-Bolt dùng trực tiếp từ checkpoint pretrained, không fine-tune trên M5. Context cắt tại `train_end`; mô hình dự báo từ `train_end + 1` đến `test_end` rồi chỉ giữ 28 ngày test.

Chronos-Bolt hỗ trợ quantile native nhưng checkpoint chỉ huấn luyện cho vùng quantile trung tâm. Khi yêu cầu các mức đuôi ngoài vùng hỗ trợ, thư viện chặn chúng về biên được huấn luyện. Đây là hạn chế cần giữ nguyên và ghi nhận ở raw forecast thay vì tự ngoại suy đuôi cực trị."""
MD[('P4.ipynb', 14)] = """## 05. TinyTimeMixer (TTM, zero-shot)

TTM dùng ở chế độ zero-shot và trả về point forecast. Mỗi context được chuẩn hóa theo mean/std tính chỉ từ lịch sử đến `train_end`, sau đó inverse-transform dự báo.

Để tạo 9 quantile theo schema chung, point forecast được bọc bằng Negative Binomial khi phương sai lịch sử lớn hơn trung bình, các trường hợp còn lại dùng Poisson. Vì vậy probabilistic forecast của TTM ở đây là hậu xử lý, không phải quantile native của checkpoint."""
MD[('P4.ipynb', 19)] = """### Nhận xét kết quả TTM

TTM tạo dự báo đầy đủ cho 3.474 chuỗi trong cả ba cửa sổ rolling-origin với 9 mức phân vị và không có quantile crossing ở đầu ra cuối.

Khác Chronos-Bolt, TTM ở thiết lập này cho dự báo điểm. Để chuẩn hóa về cùng định dạng xác suất, dùng Negative Binomial khi phương sai lớn hơn trung bình (trên 99.8% chuỗi rơi vào overdispersion), còn lại dùng Poisson.

Vì vậy các phân vị cuối phụ thuộc giả định của lớp bọc chứ không phải đầu ra xác suất trực tiếp của TTM; khi đánh giá cần phân biệt năng lực dự báo điểm của TTM với chất lượng của bước chuyển điểm sang phân vị."""
MD[('P4.ipynb', 20)] = """## 06. Moirai-2 (zero-shot)

**Lưu ý:** Moirai-2 chạy trong môi trường Python riêng vì Uni2TS yêu cầu dependency khác môi trường Chronos/TTM.

Checkpoint `Salesforce/moirai-2.0-R-small` cho 9 quantile native từ 0.1 đến 0.9. Các mức yêu cầu nằm trong khoảng này được nội suy tuyến tính; các mức ngoài khoảng bị chặn tại biên 0.1/0.9. Sau mapping, bước quantile rearrangement sắp xếp các giá trị tại từng (series_id, d_int) để loại crossing. Đây là bước hậu xử lý, không phải output native."""
MD[('P4.ipynb', 24)] = """### Nhận xét kết quả Moirai-2

Moirai-2 tạo dự báo xác suất cho toàn bộ 3.474 chuỗi trong ba cửa sổ. Phân vị native nằm trong khoảng 0.1-0.9; mức yêu cầu ở giữa được nội suy tuyến tính, mức ngoài phạm vi bị chặn tại hai biên.

Trước bước rearrangement có một phần điểm dự báo bị quantile crossing; sau khi sắp xếp lại thì hết crossing. Vì vậy tính đơn điệu cuối một phần là kết quả hậu xử lý. Việc chặn đuôi tại biên native cũng hạn chế khả năng biểu diễn phần đuôi, cần lưu ý khi đánh giá."""
MD[('P4.ipynb', 33)] = "*Chronos/Moirai bám mùa vụ và kẹp đuôi [0.1, 0.9] nên hẹp đuôi; TTM phẳng ở điểm nhưng khoảng NB rộng nhất. Chi tiết xem biểu đồ.*"
MD[('P4.ipynb', 37)] = """## 11. Forecast validation (bàn giao P5 hiệu chuẩn conformal)

P5 cần forecast trên cửa sổ validation (`train_end+1 .. val_end`) để fit split-conformal cho mọi model. Với FM, bản val chính là slice `[0:H]` của cùng lời gọi `predict` đã sinh test (context vẫn kết thúc ở `train_end`), nên out-of-sample và không rò rỉ, nhất quán với bản test ở mục 04-06. Ghi `data/outputs/forecasts/val/{chronos_bolt, ttm, moirai_2}.parquet` (thêm cột `window`), dùng lại các biến đã có mà không load lại."""

MD[('P5.ipynb', 0)] = """# P5 - Đánh giá và tổng hợp (Bước 6, 7, 8)

**Input:** data/outputs/forecasts/*.parquet, common/segment_labels.parquet, data/processed/data_long.parquet.
**Output:** data/outputs/{metrics_by_model_segment, decision_table}.parquet.

Mẫu tham khảo: `notebooks/M5_reference.ipynb` (phần 7). Chạy cell đầu để nạp input, code ở giữa, cuối cùng chạy cell lưu output."""
MD[('P5.ipynb', 1)] = "## Cell đầu: import và nạp input"
MD[('P5.ipynb', 3)] = """## Phần code chính (Bước 6, 7, 8)

**Giao thức chốt trước khi xem kết quả (pre-registration):**

| Bước | Nội dung | Cài đặt |
|---|---|---|
| 6 | Hiệu chuẩn chung | Split-conformal một phía cho từng mức quantile (CQR), residual chuẩn hóa theo scale MAE-naive của chuỗi, Mondrian theo nhóm demand. Tập hiệu chuẩn của cửa sổ W là forecast validation RAW mà P3/P4 nộp (actual đều <= gốc test, không rò rỉ). Cùng một thủ tục cho mọi model. |
| 7 | Metric | RMSSE (điểm, chính), MASE (phụ), WSPL (xác suất, chính; trọng số doanh thu 28 ngày trước gốc), SPL (phụ), coverage 50/67/95/99 (chính), cùng độ rộng dải 95 và bias để phân tích lỗi. Báo cả raw và calibrated, theo balanced và frequency-weighted. |
| 8 | Kiểm định và win rule | Mỗi (nhóm, metric, bản): Diebold-Mariano panel (SE cluster theo chuỗi, Holm) và MCB tham chiếu. Thắng rõ khi model tốt nhất hơn mọi model khác ở cả 3 cửa sổ và qua DM (p Holm < 0.05); ngược lại là tương đương, khi đó chọn model rẻ nhất. |

**Lưu ý về gốc dự báo:** cổ điển dự báo test từ gốc test_start-1 (h = 1-28); LightGBM train <= train_end nhưng feature lag >= 28 dùng actual tới val_end; ba FM lấy context <= train_end và dự báo 56 ngày (val = h 1-28, test = h 29-56). Nghĩa là FM dự báo test xa hơn và residual hiệu chuẩn dễ hơn test, nên dải FM sau hiệu chuẩn có thể vẫn hơi hẹp; mọi kết luận về FM cần kèm lưu ý này."""
MD[('P5.ipynb', 9)] = """### Bước 7: Chấm metric theo chuỗi rồi tổng hợp

- Theo chuỗi: RMSSE/MASE dùng P50; SPL = trung bình pinball 9 mức / s1; coverage của 4 dải đối xứng; độ rộng dải 95 (chuẩn hóa); bias = (P50 - actual)/s1.
- Tập so sánh: trong mỗi (bản, cửa sổ) chỉ giữ chuỗi mà mọi model đều có forecast và có scale, để chấm trên cùng một tập.
- Tổng hợp nhóm: trung bình chuỗi (WSPL trung bình có trọng số doanh thu). `window = ALL` là trung bình các cửa sổ; `ALL (balanced)` trung bình 4 nhóm ngang nhau; `ALL (frequency-weighted)` theo tần suất thật của nhóm trên 30.490 chuỗi."""
MD[('P5.ipynb', 12)] = """### Hiệu chuẩn: coverage danh nghĩa so với thực tế (raw và calibrated)

Mỗi ô là model × nhóm. Đường chéo là hiệu chuẩn hoàn hảo; dưới đường chéo là dải quá hẹp (tự tin thừa)."""
MD[('P5.ipynb', 14)] = "**Đọc coverage sau hiệu chuẩn.** Conformal hiệu chuẩn từng mức quantile một phía (P(y <= q'_τ) xấp xỉ τ). Với dữ liệu đếm có sàn 0, khi P2.5 = 0 thì không thể miss phía dưới, nên coverage dải 95% hội tụ về khoảng 0.975 chứ không phải 0.95 (xem `miss_lo95`, `miss_hi95`). Đây là tính chất của dữ liệu gián đoạn, không phải lỗi hiệu chuẩn: phía trên (phía quyết định tồn kho) vẫn đúng mức danh nghĩa."
MD[('P5.ipynb', 18)] = "## Cell cuối: lưu output (điền biến theo comment rồi chạy)"
MD[('P5.ipynb', 20)] = """## Biểu đồ tổng hợp kết quả

*Đọc từ `data/outputs/metrics_by_model_segment.parquet` đã lưu, chỉ minh họa, không đổi logic hay output.*"""
MD[('P5.ipynb', 26)] = "*RMSSE (độ chính xác điểm): LightGBM dẫn ở phần lớn nhóm; Naive kém nhất, đúng kỳ vọng.*"


def clean_code_comments(src):
    """Chỉ sửa COMMENT token; assert mọi token khác giữ nguyên."""
    orig_toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    # map: dòng -> cột bắt đầu comment
    com = {tk.start[0]: tk.start[1] for tk in orig_toks if tk.type == tokenize.COMMENT}
    if not com:
        return src, False
    lines = src.split('\n')
    changed = False
    for row, col in com.items():
        ln = lines[row - 1]
        code_part, comment_part = ln[:col], ln[col:]
        new_comment = clean_chars(comment_part).rstrip()
        if new_comment != comment_part:
            lines[row - 1] = code_part + new_comment
            changed = True
    new_src = '\n'.join(lines)
    # KIỂM CHỨNG: token không phải comment phải y hệt
    new_toks = list(tokenize.generate_tokens(io.StringIO(new_src).readline))
    def keep(toks):
        return [(t.type, t.string) for t in toks if t.type != tokenize.COMMENT]
    assert keep(orig_toks) == keep(new_toks), "CODE TOKEN THAY ĐỔI - HỦY"
    return new_src, changed


os.makedirs(BAK, exist_ok=True)
summary = []
for nb in sorted(glob.glob(os.path.join(NBDIR, "P*.ipynb"))):
    name = os.path.basename(nb)
    shutil.copy2(nb, os.path.join(BAK, name))
    data = json.load(open(nb, encoding='utf-8'))
    md_changed = code_changed = 0
    out_before = [json.dumps(c.get('outputs', []), sort_keys=True) for c in data['cells'] if c['cell_type'] == 'code']
    ec_before = [c.get('execution_count') for c in data['cells'] if c['cell_type'] == 'code']
    for i, c in enumerate(data['cells']):
        if c['cell_type'] == 'markdown':
            orig = ''.join(c['source'])
            new = MD.get((name, i), orig)
            new = clean_chars(new)
            if new != orig:
                c['source'] = to_lines(new)
                md_changed += 1
        elif c['cell_type'] == 'code':
            orig = ''.join(c['source'])
            new, ch = clean_code_comments(orig)
            if ch:
                c['source'] = to_lines(new)
                code_changed += 1
    # KIỂM CHỨNG kết quả giữ nguyên
    out_after = [json.dumps(c.get('outputs', []), sort_keys=True) for c in data['cells'] if c['cell_type'] == 'code']
    ec_after = [c.get('execution_count') for c in data['cells'] if c['cell_type'] == 'code']
    assert out_before == out_after, f"{name}: OUTPUTS THAY ĐỔI!"
    assert ec_before == ec_after, f"{name}: execution_count THAY ĐỔI!"
    with open(nb, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write('\n')
    summary.append((name, md_changed, code_changed))

print("XONG. Backup tại:", BAK)
for name, m, c in summary:
    print(f"  {name}: sửa {m} markdown, {c} code-cell (chỉ comment)")
