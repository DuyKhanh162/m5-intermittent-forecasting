# Nền lý thuyết (Bước 0) — Dự báo xác suất nhu cầu gián đoạn

Tài liệu thống nhất cho cả nhóm: khái niệm nền · cách xử lý dữ liệu · lý thuyết từng mô hình (4 ý) · hiệu chuẩn · cách đánh giá · ký hiệu chung. Viết gọn, đủ ý để tra cứu khi làm P1–P5 và viết báo cáo.

---

## 0. Ký hiệu thống nhất

| Ký hiệu | Nghĩa |
|---|---|
| $y_{i,t}$ | nhu cầu (sales) của chuỗi $i$ tại ngày $t$ |
| $\hat q_{\tau}$ | dự báo **phân vị** mức $\tau$ |
| $\mathcal{Q}$ | tập 9 mức phân vị $\{0.005, 0.025, 0.165, 0.25, 0.5, 0.75, 0.835, 0.975, 0.995\}$ |
| $H$ | độ dài dự báo (horizon) = **28 ngày** |
| $\tau$ | một mức phân vị; $\hat q_{0.5}$ = median (dự báo điểm) |
| train / val / test | tập huấn luyện / hiệu chuẩn / kiểm tra (chia **theo thời gian**) |
| $s_1, s_2$ | hệ số chuẩn hoá MASE / RMSSE (naive, tính **trên train**) |

---

## 1. Dữ liệu & bài toán

**Chuỗi thời gian (time series).** Dữ liệu có **trục thời gian**: giá trị hôm nay phụ thuộc quá khứ. Ba thành phần khai thác: **lag** (trễ $k$ ngày), **mùa vụ** (chu kỳ tuần/năm), **rolling** (thống kê trượt: trung bình/độ lệch $n$ ngày gần nhất).

**M5 (Walmart).** 30.490 chuỗi (3.049 SP × 10 cửa hàng, 3 ngành) × ~1.941 ngày + `calendar` (lễ/sự kiện, **SNAP** = ngày phát trợ cấp thực phẩm → tăng cầu Foods) + `sell_prices`. Các biến này làm **feature ngoại sinh** giải thích biến động không theo mùa vụ.

**Nhu cầu gián đoạn (intermittent demand).** Nhiều ngày = 0, xen kẽ vài ngày có bán → trung bình không đại diện, dự báo điểm kém ý nghĩa. Đây là đặc tính của ~95% SKU bán lẻ.

**Phân nhóm SBC (Syntetos–Boylan–Croston).** Hai chỉ số (tính **trên train**):
- **ADI** (Average Demand Interval) = $\dfrac{\text{số ngày}}{\text{số ngày có bán}>0}$ — đo *độ thưa* (càng lớn càng gián đoạn).
- **CV²** = $\left(\dfrac{\sigma}{\mu}\right)^2$ của nhu cầu các ngày > 0 — đo *biến động cỡ nhu cầu*.

Ngưỡng **ADI = 1,32**, **CV² = 0,49** → 4 nhóm: `smooth` (đều, ổn định), `erratic` (đều, biến động mạnh), `intermittent` (thưa, ổn định), `lumpy` (thưa, biến động mạnh).

---

## 2. Cách xử lý dữ liệu (vì sao làm vậy)

**Cấm shuffle — tôn trọng trục thời gian.** Mọi thao tác (chia dữ liệu, tạo feature, hiệu chuẩn) **chỉ dùng quá khứ**. Trộn ngẫu nhiên = **rò rỉ tương lai** (leakage) → đánh giá ảo.

**Chia theo thời gian + rolling-origin.** Thay vì một lần chia, dùng **≥3 cửa sổ trượt lùi 28 ngày**: mỗi cửa sổ có train (quá khứ) → val → test (28 ngày kế), **mọi test ≤ ngày cuối có actuals (d_1941)**. Lý do: (i) ước lượng độ chính xác **ổn định** qua nhiều gốc thời gian; (ii) tránh may rủi của một cửa sổ đơn.

**Leak-free khi tạo feature (ML).** Để dự báo đủ 28 ngày test chỉ từ dữ liệu ≤ gốc, mọi lag/rolling phải **lag ≥ horizon (≥28)** — nếu dùng lag-1 sẽ cần biết ngày hôm trước của test (chưa có).

**Chuẩn hoá wide→long.** Bảng rộng (chuỗi × ngày) → dạng dài (mỗi dòng = chuỗi×ngày) + ghép calendar/giá + feature nền (wday, month, is_event, SNAP, sell_price) để model dùng chung.

---

## 3. Dự báo điểm vs dự báo xác suất

- **Dự báo điểm:** một con số (vd median). Với chuỗi nhiều 0, điểm thường = 0 → vô dụng cho quyết định tồn kho.
- **Dự báo xác suất:** cả **phân phối** qua **9 phân vị** → trả lời "80% khả năng nhu cầu ≤ bao nhiêu?". Cần cho **đặt mức tồn kho an toàn**. Đây là **trục chính** của nghiên cứu.

---

## 4. Lý thuyết các mô hình

Mỗi mô hình trình bày theo **4 ý tách dòng**: **(1) Khái niệm · (2) Cơ chế & công thức (đầu vào → tính toán → đầu ra, vì sao ra kết quả đó) · (3) Điểm mạnh – yếu & khi nào dùng · (4) Hợp / không hợp chuỗi gián đoạn.** Đầu ra chung của mọi mô hình là **9 phân vị** cho 28 ngày test; mô hình chỉ ra *điểm* thì được **bọc Negative Binomial** (mục 4.1.6) để thành phân vị.

### 4.1 Họ cổ điển (thống kê)

#### 4.1.1 Naive
**(1) Khái niệm.**
Giả định "ngày mai giống hôm nay": dự báo luôn bằng giá trị quan sát **gần nhất**.

**(2) Cơ chế & công thức — đầu vào → tính toán → đầu ra.**
Đầu vào: chuỗi lịch sử đến ngày gốc $t$. Tính toán: lấy giá trị cuối $y_t$ và lặp cho mọi bước: $\hat y_{t+h}=y_t$. Đầu ra: một đường **phẳng** = $y_t$ cho 28 ngày → bọc NB để ra 9 phân vị.
*Vì sao ra kết quả đó:* dự báo **chỉ dựa trên 1 điểm cuối cùng**, không dùng gì khác → nếu $y_t=0$ thì toàn bộ dự báo = 0.

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: rẻ nhất, là **mốc tham chiếu** bắt buộc. Yếu: bỏ qua mùa vụ, xu hướng, nhiễu. Dùng: làm baseline để đo "giá trị gia tăng" của model phức tạp.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Không hợp:** chuỗi nhiều 0 → $y_t$ thường = 0 (dự báo 0) hoặc đúng ngày có spike (dự báo spike kéo dài sai). Kém nhất họ cổ điển trong kết quả project.

#### 4.1.2 SeasonalNaive(7)
**(1) Khái niệm.**
Lặp lại giá trị của **cùng ngày trong tuần trước** (chu kỳ 7).

**(2) Cơ chế & công thức.**
Đầu vào: ≥7 ngày gần nhất. Tính toán: $\hat y_{t+h}=y_{t+h-7}$ (chiếu lại mẫu tuần gần nhất). Đầu ra: lặp mẫu 7 ngày → bọc NB.
*Vì sao:* dự báo dựa trên **giả định mùa vụ tuần ổn định** — nhu cầu thứ Bảy tuần này ≈ thứ Bảy tuần trước.

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: bắt **mùa vụ tuần** (bán lẻ cuối tuần +31%). Yếu: nhạy với nhiễu của đúng 1 tuần mẫu. Dùng: baseline khi dữ liệu có chu kỳ tuần rõ.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Trung tính:** tốt nếu mẫu tuần đều; với chuỗi thưa/ngẫu nhiên thì mẫu tuần không ổn → kém.

#### 4.1.3 Croston
**(1) Khái niệm.**
Phương pháp **chuẩn mực cho nhu cầu gián đoạn**: tách nhu cầu thành **cỡ bán** (khi có bán) và **khoảng cách giữa 2 lần bán**, làm mượt **riêng** từng thành phần.

**(2) Cơ chế & công thức.**
Đầu vào: chuỗi; chỉ cập nhật tại **kỳ có bán** ($y>0$). Tính toán (làm mượt mũ SES, hệ số $\alpha$): cỡ bán $\hat z_t=\alpha y_t+(1-\alpha)\hat z_{t-1}$; khoảng cách $\hat p_t=\alpha q+(1-\alpha)\hat p_{t-1}$ (với $q$ = số kỳ kể từ lần bán trước). Đầu ra: **nhu cầu suất mỗi kỳ** $\hat y=\hat z/\hat p$ (= cỡ trung bình chia cho tần suất) → bọc NB ra 9 phân vị.
*Vì sao:* thay vì để các ngày 0 "kéo" trung bình xuống, Croston **ước lượng riêng** "mỗi lần bán bao nhiêu" và "bao lâu bán một lần" → cho **mức kỳ vọng ổn định** phản ánh đúng nhịp bán thưa.

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: ổn định, chuẩn vàng gián đoạn. Yếu: **thiên lệch dương** nhẹ, **không giảm** khi hàng ngừng bán (vì chỉ cập nhật lúc có bán), giả định khoảng cách hình học. Dùng: SKU thưa nhưng còn hoạt động.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Rất hợp** — được **thiết kế riêng** cho intermittent (nhóm `intermittent`/`lumpy`).

#### 4.1.4 SBA (Syntetos–Boylan Approximation)
**(1) Khái niệm.**
Bản **khử thiên lệch** của Croston.

**(2) Cơ chế & công thức.**
Đầu vào/tính toán giống Croston, nhưng **nhân hệ số hiệu chỉnh** $\left(1-\frac{\alpha}{2}\right)$: $\hat y_{\text{SBA}}=\left(1-\frac{\alpha}{2}\right)\hat z/\hat p$. Đầu ra: điểm (đã bớt thiên lệch) → bọc NB.
*Vì sao:* kỳ vọng của tỷ số $\hat z/\hat p$ **lệch dương** ~$\alpha/2$; nhân hệ số này kéo về gần kỳ vọng thật → ước lượng **chính xác hơn** khi chuỗi rất thưa.

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: chính xác hơn Croston ở chuỗi rất thưa. Yếu: vẫn giả định interval hình học. Dùng: lumpy/intermittent rất thưa.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Rất hợp** — thường **tốt nhất họ cổ điển** (project: SBA/Croston ngang nhau, dẫn nhóm cổ điển).

#### 4.1.5 TSB (Teunter–Syntetos–Babai)
**(1) Khái niệm.**
Cập nhật **xác suất có bán** và **cỡ bán** ở **mọi kỳ** (kể cả kỳ = 0) — khác Croston chỉ cập nhật khi có bán.

**(2) Cơ chế & công thức.**
Đầu vào: chuỗi. Tính toán: xác suất có bán $\hat d_t=\beta\,\mathbb{1}(y_t>0)+(1-\beta)\hat d_{t-1}$ (cập nhật mỗi kỳ); cỡ bán $\hat z_t$ cập nhật (SES) khi có bán. Đầu ra: $\hat y=\hat d\cdot\hat z$ → bọc NB.
*Vì sao:* vì xác suất $\hat d$ **giảm dần về 0** qua các kỳ không bán → dự báo **tự hạ** khi hàng có dấu hiệu ngừng bán (Croston không làm được).

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: xử lý **vòng đời / hàng ngừng bán**, tránh thiên lệch obsolescence. Yếu: thêm tham số $\beta$ phải chọn. Dùng: SKU có nguy cơ ngừng bán.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Hợp**, đặc biệt chuỗi gián đoạn có **xu hướng tắt dần**.

#### 4.1.6 Bọc Negative Binomial (NB) — biến điểm → phân phối
**(1) Khái niệm.**
Lớp "bọc" chung để mô hình **chỉ ra điểm** (cổ điển, TTM) có được **phân phối** 9 phân vị.

**(2) Cơ chế & công thức.**
Đầu vào: dự báo điểm (xem như trung bình $\mu$) + phương sai $\sigma^2$ ước từ lịch sử. Tính toán tham số NB: $r=\dfrac{\mu^2}{\sigma^2-\mu}$, $p=\dfrac{r}{r+\mu}$ (khi $\sigma^2>\mu$; nếu $\sigma^2\le\mu$ dùng **Poisson**); rồi lấy $\hat q_\tau=\text{NB}^{-1}(\tau;\,r,p)$. Đầu ra: 9 phân vị.
*Vì sao:* NB là phân phối **đếm, phương sai > trung bình** (overdispersion) → đuôi dày hợp nhu cầu bán lẻ biến động; từ một điểm + độ biến động lịch sử suy ra **toàn bộ dải khả dĩ**.

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: đơn giản, hợp dữ liệu đếm. Yếu: **giả định dạng NB** (có thể thừa/thiếu phủ nếu sai dạng) → cần conformal chỉnh lại. Dùng: mọi model ra điểm.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Hợp** bản chất đếm-gián đoạn; nhưng coverage cuối cùng vẫn phải **hiệu chuẩn** (Mục 5).

### 4.2 Họ Machine Learning

#### 4.2.1 LightGBM (Gradient Boosting — quantile)
**(1) Khái niệm.**
Tập hợp **cây quyết định** cộng dồn (gradient boosting), học quan hệ **phi tuyến** giữa nhiều feature và nhu cầu; dùng ở chế độ **quantile regression** để ra trực tiếp từng phân vị.

**(2) Cơ chế & công thức — đầu vào → tính toán → đầu ra.**
Đầu vào: với mỗi (chuỗi, ngày) một **vector feature**: lag ≥ 28 (`lag_28/35/56`), rolling (`rmean_28`, `rstd_28`, `rmean_7`), days-since-last-sale, lịch (wday/month), giá, SNAP. Tính toán: xây **tuần tự** nhiều cây — mỗi cây mới học **phần dư** (gradient của hàm mất mát) của tổ hợp cây trước; với phân vị $\tau$ dùng **pinball loss** làm mục tiêu nên cây tối ưu đúng mức $\tau$. Huấn luyện **9 mô hình riêng** (mỗi $\tau$ một model). Đầu ra: $\hat q_\tau(x)=\sum_k \text{tree}_k(x)$.
*Vì sao ra kết quả đó / dựa trên gì:* dự báo = **tổng đóng góp của các cây** theo giá trị feature hiện tại; thực nghiệm cho thấy **`rmean_28` (~67%)** và **`rstd_28` (~17%)** chi phối → nghĩa là model dự đoán chủ yếu dựa trên **mức nhu cầu trung bình & độ biến động gần đây**, điều chỉnh thêm theo lịch/giá/SNAP. Học **global** (một model cho mọi chuỗi) nên "mượn sức" từ toàn tập.

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: khai thác **feature ngoại sinh**, phi tuyến, phân vị native; **baseline mạnh nhất** (M5 & project đều xác nhận). Yếu: cần **feature engineering leak-free** (lag ≥ H), không ngoại suy ngoài dải train. Dùng: khi có nhiều feature + đủ dữ liệu huấn luyện.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Hợp** nếu có feature "cảm biến độ thưa" (days-since-last-sale, rolling) — khi đó model học được nhịp gián đoạn; trong project **thắng rõ ở `smooth`** và tốt nhất tổng thể.

### 4.3 Họ Foundation Model (đào sâu nhất)

**Khái niệm chung.**
Mô hình lớn được **pretrain** trên kho chuỗi thời gian khổng lồ (hàng tỷ điểm, đa lĩnh vực) → dùng **zero-shot**: đưa chuỗi M5 vào là **dự báo ngay, không huấn luyện lại** — như "GPT cho time-series" (dự báo bằng **nhận dạng mẫu** đã học). **Few-shot** = fine-tune nhẹ trên một lát train (tùy chọn, project chưa làm). Điểm chung về cơ chế: **không dùng feature ngoại sinh**, chỉ nhìn **context** (chuỗi quá khứ ≤ train_end).

#### 4.3.1 Chronos-Bolt
**(1) Khái niệm.**
"Ngôn ngữ hoá" chuỗi: coi giá trị như **token** và dự báo như mô hình ngôn ngữ.

**(2) Cơ chế & công thức.**
Đầu vào: context ≤ 512 điểm. Tính toán: **scale** chuỗi → **lượng tử hoá** giá trị thành token trong một từ vựng → kiến trúc **T5 encoder–decoder** (Bolt: cắt context thành *patch* rồi sinh **đa bước trực tiếp**) → model trả về **phân phối phân vị** cho 28 ngày → giải lượng tử về thang gốc. Đầu ra: 9 phân vị **native**, nhưng head huấn luyện trên dải **[0.1, 0.9]** nên **kẹp đuôi** (q.005≈q.025, q.975≈q.995).
*Vì sao:* dự báo dựa trên **mẫu hình thống kê đã học từ pretrain** (không từ M5) — model chọn phân phối tương lai **khả dĩ nhất** given context; vì chưa "thấy" M5 nên là **zero-shot** thực sự.

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: zero-shot, không cần train, patch → nhanh. Yếu: **thiếu phủ đuôi** (phải hiệu chuẩn), **không dùng ngoại sinh** (SNAP/giá). Dùng: thiếu dữ liệu/thời gian để train riêng.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Cạnh tranh** nhưng **chưa vượt** LightGBM đã tune; đuôi phân vị cực **phải hiệu chuẩn** mới dùng được cho tồn kho.

#### 4.3.2 TTM (TinyTimeMixer)
**(1) Khái niệm.**
Mô hình **MLP-Mixer nhẹ** của IBM (ít tham số, rất nhanh).

**(2) Cơ chế & công thức.**
Đầu vào: context 512, **chuẩn hoá z-score** theo thống kê context. Tính toán: các khối **mixer** trộn thông tin **theo thời gian** và **theo kênh** (thay cho attention) → sinh **điểm** đa bước → **đảo z-score** về thang gốc. Đầu ra: điểm → **bọc NB** (Mục 4.1.6) ra 9 phân vị.
*Vì sao:* điểm dự báo là **mẫu hình đã học khi pretrain**; còn **dải** không do model sinh mà do **lớp NB** (dựa mean/var lịch sử) → chất lượng dải phụ thuộc giả định bọc.

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: **cực nhanh** (~giây cho vài nghìn chuỗi), nhẹ. Yếu: chỉ ra điểm → **dải phụ thuộc NB**. Dùng: cần tốc độ/triển khai nhẹ.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Khá** — điểm hợp lý, nhưng phủ dải phụ thuộc lớp bọc; không nổi trội theo WSPL.

#### 4.3.3 Moirai-2
**(1) Khái niệm.**
Transformer **universal forecasting** (Salesforce) cho đa tần suất/đa biến.

**(2) Cơ chế & công thức.**
Đầu vào: context. Tính toán: encoder có **masking**, **any-variate attention** → sinh **phân vị native** trên lưới (≈ 0.1–0.9) → **nội suy** về 9 mức yêu cầu + **sắp xếp** (sort) khử crossing. Đầu ra: 9 phân vị.
*Vì sao:* model học **phân phối tiên nghiệm** từ kho đa lĩnh vực → với context M5 cho ra phân phối dự đoán; các mức ngoài lưới train bị **kẹp/nội suy** nên đuôi hẹp.

**(3) Điểm mạnh – yếu & khi nào dùng.**
Mạnh: linh hoạt, phân vị native. Yếu: **kẹp đuôi** → thiếu phủ; nặng hơn TTM. Dùng: zero-shot đa domain.

**(4) Hợp / không hợp chuỗi gián đoạn.**
**Tốt ở `erratic`** (WSPL thấp nhất nhóm này) nhưng **không áp đảo**; vẫn cần hiệu chuẩn đuôi.

> **Cảnh báo rò rỉ pre-training (đã kiểm nguồn).** M5 là **tập zero-shot giữ ngoài training** của Chronos/Chronos-Bolt (Benchmark II) và **không nằm trong Monash+LibCity** của TTM → **rủi ro rò rỉ trực tiếp thấp**; vẫn diễn giải zero-shot thận trọng vì corpus FM không công bố đầy đủ.

---

## 5. Hiệu chuẩn dự báo xác suất (calibration / conformal)

**Vấn đề.** Ba họ sinh dải bằng **3 cơ chế khác nhau** (native kẹp đuôi · bọc-NB · nội suy) → đo coverage trực tiếp là đo lẫn **"lớp bọc"**, không phải năng lực thật.

**Split-conformal (phân phối tự do).** Trên **validation**: tính **sai số phân vị** (residual) của mỗi mô hình, lấy **offset** = order-statistic của residual theo **từng (nhóm × mức $\tau$)** (nguyên tắc Mondrian) → **cộng offset vào dự báo test**, rồi **sắp xếp** giữ đơn điệu, kẹp ≥ 0. Kết quả: mọi mô hình được **đưa về cùng một cây thước** → so sánh công bằng. Báo **cả bản raw lẫn calibrated**.

**Vì sao conformal:** (i) không giả định phân phối; (ii) đảm bảo coverage hợp lệ nếu dữ liệu đổi chỗ được (exchangeable); (iii) tách **năng lực mô hình** khỏi cách vẽ dải.

---

## 6. Cách đánh giá (metric + kiểm định)

### 6.1 Metric
| Metric | Công thức (ý chính) | Đo gì |
|---|---|---|
| **MASE** | $\dfrac{\overline{\|y-\hat y\|}}{s_1}$, $s_1$ = MAE naive in-sample | độ chính xác điểm, **chuẩn hoá** để so giữa chuỗi |
| **RMSSE** | $\sqrt{\dfrac{\overline{(y-\hat y)^2}}{s_2}}$, $s_2$ = MSE naive in-sample | như MASE nhưng phạt lỗi lớn |
| **SPL** (pinball) | $\overline{\max\big(\tau(y-\hat q_\tau),\,(\tau-1)(y-\hat q_\tau)\big)}/s_1$ | **chất lượng dải** (trung bình mọi $\tau$) |
| **WSPL** | SPL **trọng số theo doanh thu** (giá × sản lượng) | chất lượng dải **có ý nghĩa tiền tệ** (tiêu chí chính) |
| **coverage** $c_{\text{nom}}$ | $P\big(y\in[\hat q_{lo},\hat q_{hi}]\big)$ | **độ tin cậy dải** (kết quả chính); mục tiêu danh nghĩa 50/67/95/99 |

Chuẩn hoá bằng scale naive **tính trên train** (leak-free) để so sánh được giữa các nhóm/chuỗi. Tổng hợp **hai cách**: *balanced* (đều 4 nhóm) và *frequency-weighted* (theo tỷ trọng 30.490 chuỗi).

### 6.2 Rolling-origin
Chấm trên **3 cửa sổ** rồi tổng hợp → kết luận không phụ thuộc một gốc thời gian.

### 6.3 Kiểm định thống kê (vì sao: chênh nhỏ có thể do may rủi)
- **Diebold–Mariano (DM):** so **chênh lệch hàm mất mát** $d_t = L^{(A)}_t - L^{(B)}_t$ giữa 2 model; thống kê $z = \bar d / \widehat{\text{SE}}(\bar d)$. Dùng **SE gom cụm theo chuỗi** (residual nhiều cửa sổ của cùng chuỗi phụ thuộc nhau) và **hiệu chỉnh đa so sánh Holm** (kiểm nhiều cặp).
- **MCB (Multiple Comparison with the Best):** so **hạng trung bình** của mỗi model với best; khoảng tin cậy Nemenyi (critical distance). Dùng **tham chiếu**.
- **Win rule (luật tuyên bố thắng):** một model "thua rõ" best khi **p (Holm) < 0,05 VÀ thua ở cả 3 cửa sổ**. "**Thắng rõ**" ⇔ chỉ best sống sót; ngược lại "**tương đương**" → chọn model **đơn giản/rẻ** trong nhóm tương đương.

---

## 7. Lưu ý diễn giải (giới hạn lý thuyết)
1. **Coverage rời rạc:** dữ liệu đếm có sàn 0 → khi $\hat q_{0.025}=0$ không thể "miss dưới" → coverage-95 hội tụ ~0,975.
2. **Bất đối xứng horizon FM:** cổ điển dự báo test ở $h=1\text{–}28$; FM dự báo test ở $h=29\text{–}56$ (dùng $h=1\text{–}28$ làm validation để hiệu chuẩn).
3. **Rò rỉ pre-training FM:** rủi ro thấp (M5 là zero-shot benchmark) nhưng corpus FM không công bố đủ → thận trọng.

---

## 8. Tài liệu tham khảo (chính)
- Makridakis, Spiliotis & Assimakopoulos (2022). *The M5 Accuracy competition.* IJF.
- Syntetos & Boylan (2005). *Accuracy of intermittent demand estimates* (SBC, SBA).
- Croston (1972); Teunter, Syntetos & Babai (2011) — Croston / TSB.
- Ke et al. (2017). *LightGBM.*
- Ansari et al. (2024). *Chronos.* TMLR — arXiv:2403.07815.
- Ekambaram et al. (2024). *Tiny Time Mixers (TTM).* arXiv:2401.03955.
- Woo et al. (2024). *Moirai / unified training for universal forecasting* (Salesforce).
- Vovk et al.; Gibbs & Candès — *Conformal prediction.*
- Diebold & Mariano (1995); Harvey–Leybourne–Newbold (1997); Koning/Makridakis — DM & MCB.
- Wang, Kang & Petropoulos (2024). *Combining probabilistic forecasts of intermittent demand.* EJOR.

---

*Tài liệu nền Bước 0 — dùng chung P1–P5. Phần model do chủ model chủ trì (P3: cổ điển+ML · P4: FM · P5: hiệu chuẩn+đánh giá · P2: SBC · P1: nền + gộp + ký hiệu).*
