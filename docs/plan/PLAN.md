# Khung nghiên cứu

**So sánh mô hình cổ điển, machine learning và time-series foundation model cho dự báo xác suất nhu cầu gián đoạn trong bán lẻ, có phân nhóm theo đặc tính nhu cầu**

**1\. Giới thiệu bài toán**  
Trong bán lẻ, nhu cầu theo từng sản phẩm và cửa hàng thường không ổn định, có sản phẩm bán đều mỗi ngày, có sản phẩm nhiều ngày không bán được, có sản phẩm thỉnh thoảng tăng đột biến do khuyến mãi, mùa vụ hoặc sự kiện. Nếu dự báo sai, doanh nghiệp có thể gặp hai vấn đề lớn: tồn kho dư thừa hoặc thiếu hàng.

Bài toán nghiên cứu là: **làm thế nào dự báo nhu cầu bán lẻ tốt hơn khi dữ liệu có nhiều chuỗi gián đoạn, nhiều giá trị 0 và đặc tính khác nhau giữa các nhóm sản phẩm?**

**2\. Câu hỏi nghiên cứu chính**  
Không có một mô hình nào tốt nhất cho mọi loại nhu cầu; vậy mô hình cổ điển, machine learning và time-series foundation model hoạt động khác nhau như thế nào trên từng nhóm demand pattern?

**3\. Kiến thức cơ sở cần trình bày**

* **Time series forecasting**: chuỗi thời gian, lag, mùa vụ, rolling window, train/validation/test theo thời gian.  
* **Retail demand forecasting**: nhu cầu bán lẻ, ảnh hưởng của giá, khuyến mãi, ngày lễ, mùa vụ.  
* **Intermittent demand**: chuỗi có nhiều ngày bằng 0, nhu cầu không xuất hiện đều.  
* **Phân nhóm demand**: dùng ADI và CV² để chia chuỗi thành smooth, erratic, intermittent, lumpy.  
* **Dự báo xác suất**: không chỉ dự báo một giá trị, mà dự báo khoảng/quantile như P10, P50, P90.  
* **Đánh giá mô hình**: MASE, RMSSE, WQL, calibration, có thể thêm MAE/RMSE

**4\. Quy trình thực hiện**

1. **Tiền xử lý dữ liệu**  
   Chuyển dữ liệu sales từ dạng wide sang long, nối với calendar và sell prices, tạo biến ngày trong tuần, tháng, event, SNAP, giá bán.  
2. **Khám phá dữ liệu**  
   Thống kê tỷ lệ zero-sales, phân phối sales, nhóm sản phẩm/cửa hàng, mùa vụ, tác động của giá và ngày lễ.  
3. **Phân nhóm demand**  
   Tính ADI và CV² cho từng chuỗi, sau đó chia thành 4 nhóm: smooth, erratic, intermittent, lumpy.  
4. **Xây dựng mô hình so sánh**  
   Nhóm cổ điển: Naive, Seasonal Naive, Croston/SBA/TSB.  
   Nhóm machine learning: LightGBM hoặc XGBoost với lag/rolling/calendar/price features.  
   Nhóm foundation model: Chronos, TimesFM hoặc Moirai ở chế độ zero-shot/few-shot nếu triển khai được.  
5. **Dự báo xác suất**  
   Với mỗi mô hình, cố gắng tạo P10/P50/P90 hoặc ít nhất là median forecast và khoảng dự báo. Nếu mô hình không hỗ trợ xác suất trực tiếp, có thể dùng residual/bootstrap/quantile regression.  
6. **Đánh giá kết quả**  
   Đánh giá chung và đánh giá riêng theo từng nhóm demand. Output cuối cùng là model nào phù hợp với demand nào không phải là model nào mạnh nhất.

**6\. Mô tả và đánh giá thực nghiệm**

* Bảng tổng quan số lượng chuỗi theo từng nhóm demand.  
* Tỷ lệ zero-sales theo nhóm.  
* Bảng so sánh MASE/RMSSE/WQL của từng mô hình.  
* Bảng “mô hình thắng” theo từng nhóm demand.  
* Biểu đồ forecast vs actual cho vài chuỗi đại diện.  
* Phân tích lỗi: mô hình nào hay dự báo quá cao/quá thấp, mô hình nào xử lý tốt chuỗi nhiều số 0\.

**7\. Bộ dữ liệu và các nghiên cứu trước đó**

* Bộ dữ liệu: [Dữ liệu M5 của Walmart](https://www.kaggle.com/competitions/m5-forecasting-accuracy/data)   
* Các nghiên cứu trước đó:   
  * Wang, Kang & Petropoulos, **“Combining probabilistic forecasts of intermittent demand”**, *European Journal of Operational Research*, 2024\.[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0377221724000511), [EJOR Q1](https://www.scimagojr.com/journalsearch.php/press.jhu.edu/journals/journalsearch.php?q=22489&tip=sid)  
  * Oliveira & Ramos, **“Evaluating the Effectiveness of Time Series Transformers for Demand Forecasting in Retail”**, *Mathematics*, 2024\. [Paper](https://www.mdpi.com/2227-7390/12/17/2728), [journal Q1/Q2 metrics](https://www.iit.comillas.edu/publicacion/info_revista/en/486/Mathematics)  
  * **“Forecasting Intermittent Sales in Fashion Retail: A Two-Stage Machine Learning Approach”**, 2026\.[Paper](https://www.mdpi.com/2571-9394/8/4/56)  
  * Ansari et al., **“Chronos: Learning the Language of Time Series”**, *Transactions on Machine Learning Research*, 2024\. [TMLR](https://mlanthology.org/tmlr/2024/ansari2024tmlr-chronos/)  
  * Makridakis, Spiliotis & Assimakopoulos, **“The M5 accuracy competition: Results, findings and conclusions”**, *International Journal of Forecasting*, 2022\. [Paper](https://doi.org/10.1016/j.ijforecast.2021.11.013), [IJF Q1](https://www.iit.comillas.edu/publicacion/info_revista/en/168/International_Journal_of_Forecasting)

# **Phân công & deadline**

## **Phân công & deadline**

| Người | Bước | Đầu mục công việc |
| :---- | :---- | :---- |
| **P1** — Dữ liệu & điều phối | 0 · 1 · 4 · 8 · 10a | Chuẩn hóa dữ liệu long \+ định dạng output; split thời gian \+ cửa sổ rolling; chạy rolling ≥3; **gộp báo cáo (10a)**; điều phối |
| **P2** — Phân nhóm & tổng hợp | 0 · 2 · 3 · 9 · 10b | Phân nhóm SBC \+ gán nhãn 30.490 chuỗi; lấy mẫu phân tầng; bảng khuyến nghị \+ error analysis; **chủ slide (10b)** |
| **P3** — ML & Cổ điển | 0 · 5 | LightGBM global quantile; Croston/SBA/TSB \+ bọc NB |
| **P4** — Foundation Models | 0 · 5 | Chronos/TTM/Moirai zero-shot \+ **few-shot ablation**; rò rỉ pre-training; runtime |
| **P5** — Đánh giá | 0 · 6 · 7 · 8 | Hiệu chuẩn chung \+ bộ metric RMSSE/WSPL/coverage; kiểm định DM/MCB |

**Lịch chạy nối tiếp theo quy trình** — thông báo 23/9 · **toàn bộ (kể cả slide) xong trước 7/10** · nộp chính thức 15/10:

| Bước | Việc | Người | Hạn |
| :---: | :---- | :---: | :---: |
| 0 | Nền lý thuyết (mỗi người phần mình) | cả nhóm | 26/9 |
| 1 | Chuẩn hóa dữ liệu long \+ chốt định dạng output | P1 | 26/9 |
| 2–3 | Phân nhóm SBC \+ gán nhãn \+ lấy mẫu phân tầng | P2 | 29/9 |
| 4 | Split thời gian \+ cửa sổ rolling-origin | P1 | 29/9 |
| 5 | Chạy 3 họ model → xuất forecast (raw) | P3 · P4 | 2/10 |
| 6–7 | Hiệu chuẩn chung \+ chấm metric (raw & calibrated) | P5 | 3/10 |
| 8 | Rolling ≥3 cửa sổ \+ kiểm định DM/MCB → gắn nhãn thắng/tương đương | P1 · P5 | 5/10 |
| 9 | Tổng hợp 2 bảng \+ bảng thắng theo nhóm \+ error analysis | P2 | 6/10 |
| 10 | Báo cáo (10a) \+ slide (10b) | P1 · P2 | 7/10 |
| — | **Nộp chính thức** (bản đã hoàn tất) | — | 15/10 |

# **Tổng hợp và quy trình**

**So sánh mô hình cổ điển, machine learning và time-series foundation model cho dự báo xác suất nhu cầu gián đoạn trong bán lẻ, có phân nhóm theo đặc tính nhu cầu**

## **Bản chất bài toán**

Dự báo nhu cầu theo cặp (sản phẩm × cửa hàng), theo ngày. Ba đặc điểm chi phối mọi lựa chọn:

* Nhiều ngày \= 0 (gián đoạn), phá vỡ ARIMA/ETS → cần model chuyên trị chuỗi gián đoạn.  
* Các chuỗi khác "tính cách" nhau → phân nhóm, không gộp trung bình.  
* Sai số bất đối xứng, thiếu hàng ≠ thừa hàng → dự báo xác suất (dải), không dự báo điểm.

→ **Câu hỏi cuối không phải "model nào mạnh nhất" mà "nhu cầu nào → dùng model nào".** Đầu ra là một bảng khuyến nghị.

## **Dữ liệu M5**

30.490 chuỗi (3.049 SP × 10 cửa hàng, 3 ngành), \~1.941 ngày, kèm calendar \+ sell\_prices. **SNAP** (trong calendar) \= ngày phát trợ cấp thực phẩm của Mỹ; vào ngày này nhu cầu ngành Foods tăng vọt → dùng làm biến ngoại sinh giúp model giải thích các đợt tăng cầu không theo mùa vụ.

Là dữ liệu time-series nên dễ rò rỉ thông tin tương lai → **cấm shuffle, mọi thao tác (chia dữ liệu, tạo feature, hiệu chuẩn) phải tôn trọng trục thời gian.**

## **Quy trình** 

### **Bước 0 — Lý thuyết**

Mỗi mô hình (cổ điển · ML · FM) trình bày theo **4 ý**: (1) khái niệm, (2) cơ chế/công thức, (3) điểm mạnh–yếu & khi nào áp dụng, (4) vì sao hợp/không hợp chuỗi gián đoạn. FM đào sâu nhất (zero-shot vs few-shot, cơ chế ra quantile, rò rỉ pre-training). Kèm vài khái niệm nền: intermittent demand, dự báo điểm vs xác suất, ADI/CV², calibration, metric.

→ Ai build phần nào chủ trì lý thuyết phần đó; P1 gộp thành 1 tài liệu, thống nhất ký hiệu.

### 

### **Bước 1 — Chuẩn hóa dữ liệu**

**Wide** \= mỗi chuỗi 1 hàng, mỗi ngày 1 cột (M5 gốc). **Long** \= mỗi (chuỗi, ngày) 1 hàng. Chỉ long mới join được calendar/giá và mới là định dạng model xử lý tự nhiên → xoay wide sang long (series\_id, date, sales), join calendar \+ giá. Mỗi người tự triển khai, chỉ cần cùng làm việc trên một **định dạng dữ liệu long** thống nhất.

### **Bước 2 — Phân nhóm demand (SBC)**

Bài toán khó ở 2 chiều: **độ gián đoạn** và **độ loạn của cỡ bán** → đo bằng **ADI** (khoảng cách trung bình giữa 2 lần bán ≠0) và **CV²** (dao động cỡ bán), cắt tại ADI=1.32, CV²=0.49 thành 4 nhóm.

|  | cỡ đều (CV² thấp) | cỡ loạn (CV² cao) |
| ----- | :---: | :---: |
| **bán đều (ADI thấp)** | smooth | erratic |
| **nhiều số 0 (ADI cao)** | intermittent | lumpy |

Đây đúng 2 chiều mà các họ model mạnh/yếu khác nhau → chia theo đây so sánh mới có nghĩa (chia theo 3 ngành chỉ là lát cắt phụ). Thực tế M5: smooth 3.2% · erratic 1.6% · intermittent 75.7% · lumpy 19.4%, tức **95% là intermittent \+ lumpy** → P2 gán nhãn cho cả 30.490 chuỗi (Bước 9 cần).

### **Bước 3 — Lấy mẫu phân tầng \+ 2 góc báo cáo**

Bốc ngẫu nhiên thì gần như toàn intermittent, smooth/erratic biến mất → lấy mẫu **theo từng nhóm**: **lấy toàn bộ erratic \+ smooth, cap intermittent \+ lumpy về cùng cỡ** — vì hai nhóm hiếm chính là chỗ ít dữ liệu và bấp bênh nhất, lấy hết chúng cho lực thống kê tối đa để kết luận đáng tin. (Pilot dùng 200/nhóm làm mốc.)

**Báo cáo bắt buộc CẢ 2 bảng** vì trả lời 2 câu hỏi khác nhau — đây là **cách tổng hợp qua các nhóm**, không phải chọn metric:

* **Balanced** (mỗi nhóm số chuỗi bằng nhau) → "loại chuỗi X hợp model nào" — trục khoa học.  
* **Frequency-weighted / full** (theo tần suất thật) → "triển khai thật lời/lỗ ra sao" — trục vận hành.

*Ví dụ: chỉ dùng balanced rồi lấy trung bình 4 nhóm sẽ thổi phồng smooth/erratic (thực tế 5%) lên \~30× so tần suất thật.*

### **Bước 4 — Chia train / validation / test theo thời gian**

Thực tế chỉ có quá khứ để dự báo tương lai; test lọt vào train là "nhìn trộm", điểm đẹp giả → cắt theo mốc thời gian, không shuffle.

| train | validation | test |
| :---: | :---: | :---: |
| d\_1 … d\_1885 | d\_1886 … d\_1913 (tune \+ hiệu chuẩn) | d\_1914 … d\_1941 (28 ngày) |

Horizon 28 ngày theo chuẩn M5; validation còn giữ vai trò tập hiệu chuẩn conformal (Bước 6\) → đừng đụng test sớm.

### **Bước 5 — Ba họ mô hình**

Đề tài là so sánh 3 triết lý dự báo → chạy song song 3 họ trên cùng split / horizon / mẫu / bộ đo.

**Hiểu Croston trước (nền của cả họ cổ điển):** chuỗi bán gián đoạn đầy số 0 rất khó dự trực tiếp. Croston tách nó thành **hai chuỗi con** rồi làm mượt riêng: (1) **cỡ bán** — mỗi lần bán ≠0 thì bán bao nhiêu; (2) **khoảng cách** — bao nhiêu ngày giữa 2 lần bán. Dự báo cuối \= cỡ ước lượng ÷ khoảng cách ước lượng. Ý tưởng "tách cỡ và tần suất" này là nền của toàn bộ mảng intermittent forecasting.

**A. Cổ điển / thống kê:** Baseline: Naive, SeasonalNaive(7); Họ Croston: Croston, SBA, TSB.

* **SBA** \= Croston sửa thiên lệch (Croston lệch lên có hệ thống; nhân hệ số 1−α/2 để bớt lệch).  
* **TSB** \= thay vì cập nhật khoảng cách, cập nhật **xác suất có bán** mỗi ngày kể cả ngày \= 0 → bắt được hàng đang "chết dần".  
* Rẻ, nhanh, hợp intermittent/lumpy. Yếu: chỉ ra **giá trị điểm** → phải bọc phân phối Negative Binomial (NB) để tạo dải.

**B. Machine Learning — LightGBM global quantile:** **Global** \= 1 model học chung mọi chuỗi, phân biệt chuỗi qua feature (lag, rolling, days-since-last-sale, lịch, giá). **Quantile regression** (pinball loss) tự nhả từng mức quantile → sinh xác suất tự nhiên, không cần bọc.

* **Bẫy leak:** lag-1 cần biết ngày test hôm trước (chưa được biết) → **bắt buộc lag ≥ horizon (≥28)** để mọi ngày test tính được chỉ từ dữ liệu ≤ ngày gốc.

**C. Foundation Model — chạy trên mẫu:** pretrained sẵn như "GPT cho time-series" → chạy **zero-shot** (không train lại trên M5).

* **Chronos-Bolt:** ra quantile native nhưng **kẹp đuôi \[0.1, 0.9\]** — đây là hạn chế (không cho đuôi cực 0.005/0.995 tốt), phải nhờ conformal sửa; là gốc rễ coverage kém ở pilot.  
* **TTM (IBM Granite):** nhỏ, nhanh, ra **điểm** → bọc phân phối giống họ cổ điển.  
* **Moirai-2:** cũng ra quantile native → dùng chính thức trong nghiên cứu, chạy như một FM đầy đủ.  
* **Cảnh báo rò rỉ pre-training (chính, không phải phụ):** Chronos/TTM nhiều khả năng đã "thấy" M5 khi pretrain → điểm zero-shot có thể bị thổi lên vì học thuộc chứ không phải dự báo thật; mọi kết luận về FM phải kèm cảnh báo này.  
* **Few-shot (tùy chọn, nếu kịp) — vì sao thêm:** fine-tune nhẹ trên một lát nhỏ của **train** M5 (vẫn theo mốc thời gian, không đụng test). Không phải để "cho FM thắng" mà là **3 mục đích so sánh**:   
  * (1) **đo giá trị của thích nghi** — delta zero-shot→few-shot cho biết chỉ thêm chút dữ liệu M5 thì FM khá lên bao nhiêu  
  * (2) **so công bằng hơn với ML** — LightGBM được train đầy đủ trên M5, few-shot cho FM cùng một lượng giám sát (nhỏ) nên bớt khập khiễng  
  * (3) **soi rò rỉ pre-training** — nếu few-shot gần như không cải thiện, càng nghi model đã học thuộc M5 lúc pretrain.   
  * Zero-shot vẫn là **kết quả FM chính**, few-shot chỉ là **ablation phụ**; ưu tiên TTM (thiết kế sẵn cho few-shot) rồi Moirai.

### **Bước 6 — Giao thức xác suất công bằng (calibration)**

**Calibration (hiệu chuẩn)** \= chỉnh dải sao cho mức danh nghĩa khớp thực tế: dải "90%" thì actual phải nằm trong \~90% số lần, không phải 80% (quá hẹp, tự tin thừa) hay 99% (quá rộng, vô dụng).

3 họ vẽ dải bằng 3 cơ chế khác nhau (native / kẹp đuôi / bọc-NB), đo thẳng là đo lẫn "lớp bọc" chứ không phải năng lực → áp cùng một **split-conformal calibration** (distribution-free) trên validation cho tất cả model, **báo cả bản raw lẫn calibrated**.

*Ví dụ: pilot cho Chronos coverage-95 \~0.80 (đuôi mỏng do kẹp), nhóm bọc-NB \~0.95–0.99 (đuôi dày) — chênh này do cách vẽ dải, không phải model giỏi hơn.*

→ bản **calibrated** để so công bằng; bản **raw** để bàn hành vi gốc. Câu chốt: **"bắt tất cả vẽ dải bằng cùng cây thước rồi mới chấm".**

### **Bước 7 — Metric & vì sao chọn**

Chốt **trước khi xem kết quả** (pre-registration) để không chọn metric "cho ra kết quả đẹp". **Quan trọng:** balanced và frequency-weighted là **cách tổng hợp qua các nhóm**; cả **5 metric dưới đây đều được tính trong CẢ HAI bảng**. Cái phân biệt là **loại** metric đo cái gì:

* **Đo độ chính xác điểm — RMSSE** (chính; sai số bình phương chia cho naive nên mọi chuỗi về cùng thang, so được giữa chuỗi khác quy mô, chuẩn M5) và **MASE** (phụ; bản trị tuyệt đối, ít nhạy outlier).  
* **Đo chất lượng dải xác suất — WSPL** (chính; pinball loss phạt bất đối xứng "thiếu ≠ thừa", dollar-weighted nên sai ở hàng doanh thu cao đắt hơn, mang màu vận hành, chuẩn M5) và **SPL** (phụ; vì pilot thấy WSPL/SPL **đảo ngôi ở erratic** → phải điều tra).  
* **Đo hiệu chuẩn — Coverage** (nâng thành **kết quả chính**): tỷ lệ thật actual rơi vào dải.

RMSSE đẹp mà dải "95%" chỉ chứa actual 80% nghĩa là dự báo **điểm trúng nhưng dải dối**, model tự tin sai → nguy hiểm cho tồn kho (đặt hàng theo mức 95% sẽ thiếu hàng thường xuyên hơn tưởng). Vì dải mới là thứ ra quyết định, **coverage được đề lên hàng kết quả chính, ngang RMSSE/WSPL.**

*(Không dùng MAE/RMSE thường vì không scale, không cộng gộp được giữa chuỗi khác quy mô, không phạt bất đối xứng.)*

### **Bước 8 — Rolling-origin \+ win rule (kiểm định)**

**Pilot** \= bản chạy thử nhỏ (800 chuỗi, 1 cửa sổ) để kiểm tra pipeline chạy được và lấy trực giác — chưa phải kết luận. **Rolling-origin** \= trượt điểm gốc về trước ≥3 lần, mỗi lần dự báo 1 cửa sổ 28 ngày mới, xem model nào **ổn định qua thời gian**.

Pilot 1 cửa sổ chênh 2–3% nằm trong nhiễu, không phân biệt được ai hơn → **bắt buộc ≥3 cửa sổ \+ kiểm định**: **Diebold-Mariano** (so 1 cặp model) hoặc **MCB** (Multiple Comparison with the Best — so nhiều model qua thứ hạng trung bình, biết model nào khác biệt có ý nghĩa so với model tốt nhất).

**Win rule:** chỉ được nói một model "win" một nhóm khi chênh lệch **sống sót qua ≥3 cửa sổ rolling-origin VÀ qua một kiểm định (MCB/DM)**. Mặc định là **"tương đương"**. Chênh vài % \= tương đương, không phải thắng.

Đây là hàng rào chống tự lừa dối, không phải để dễ dãi tuyên bố thắng. Phần lớn kết luận sẽ là "tương đương" — đó là trung thực, không phải thất bại. **Chi phí tách riêng:** kiểm định chỉ lo về chỉ số dự báo; khi hai model **tương đương về chỉ số** thì mới lấy **chi phí vận hành** phân định (cổ điển ngang LightGBM ở intermittent → chọn cổ điển vì rẻ hơn).

### **Bước 9 — Tổng hợp thành bảng khuyến nghị**

Ghép tất cả lại thành đầu ra cuối:

* 2 bảng model × nhóm: **balanced** và **frequency-weighted/full**, mỗi bảng có **cả raw lẫn calibrated**.  
* Bảng **"model thắng theo nhóm"** kèm p-value / nhãn ý nghĩa (thắng rõ / tương đương).  
* Error analysis (over/under-forecast, hành vi trên chuỗi nhiều số 0\) \+ biểu đồ forecast vs actual.

→ **Kết quả cuối \= "nhu cầu nào → dùng model nào", có cân nhắc chi phí vận hành.**

### **Bước 10 — Báo cáo & slide**

**10a · Tổng hợp báo cáo (P1 chủ trì):** gộp lý thuyết Bước 0 \+ phương pháp Bước 1–8 \+ kết quả Bước 9 thành báo cáo hoàn chỉnh; kèm code có giải thích để tái lập kết quả; thống nhất ký hiệu. Mỗi người nộp phần mình.

**10b · Slide (P2 chủ deck):** \~18–22 slide bám câu hỏi lõi *"nhu cầu nào → model nào"*, tóm tắt theo bước:

* **Bài toán (Bước 0):** demand gián đoạn; vì sao dự báo xác suất; 3 họ model.  
* **Dữ liệu & thiết kế (Bước 1–4):** M5 \+ 4 nhóm SBC; lấy mẫu phân tầng; split theo thời gian.  
* **Model & giao thức (Bước 5–8):** cơ chế 3 họ; calibration "cùng một cây thước"; metric (coverage là chính); rolling ≥3 \+ luật tuyên bố thắng.  
* **Kết quả (Bước 9):** 2 bảng \+ bảng thắng theo nhóm → bảng "nhu cầu nào → model nào" \+ chi phí; kết luận & hạn chế.

