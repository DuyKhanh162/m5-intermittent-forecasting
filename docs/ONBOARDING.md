# Hướng dẫn onboarding cho thành viên (từ số 0)

> Dành cho **người mới**: chưa quen Git/PR cũng làm theo được. Đọc từ trên xuống, làm đúng thứ tự.
> Ai bí ở đâu nhắn **P1 (điều phối)**. Repo: `DuyKhanh162/m5-intermittent-forecasting` (private).

---

## 0. Bức tranh tổng thể (đọc 2 phút)

Nhóm so sánh **3 họ mô hình** (Cổ điển · ML · Foundation Model) cho **dự báo xác suất nhu cầu
gián đoạn** trên dữ liệu **M5 Walmart**, chia theo **4 nhóm demand** (SBC). Câu hỏi lõi:
**"nhu cầu nào → dùng model nào"** (không phải "model nào mạnh nhất").

Quy trình 10 bước, mỗi người sở hữu vài bước. **Nguyên tắc bất di bất dịch:** mọi người làm việc
trên **cùng một định dạng dữ liệu, cùng split, cùng bộ đo** → so sánh mới công bằng. Vì vậy có vài
file "mối nối đông cứng" (frozen) không được tự sửa (xem §6).

### Trạng thái hiện tại (P1 đã dựng xong nền)

| Bước | Nội dung | Người | Trạng thái |
|:---:|---|:---:|---|
| 0 | Lý thuyết | cả nhóm | 🟡 Khung + phần P1 xong; **P2–P5 viết phần model của mình** (`docs/00_theory/`) |
| 1 | Chuẩn hóa long | P1 | ✅ **Xong** — `src/data/build_long.py`, đã sinh `data_long` |
| 2–3 | Phân nhóm SBC + lấy mẫu | P2 | 🟡 Baseline chạy được (`src/segmentation/sbc.py`) + đã sinh nhãn/mẫu; **P2 làm EDA + 2 góc báo cáo** |
| 4 | Split + rolling-origin | P1 | ✅ **Xong** — `src/data/splits.py` (3 cửa sổ, no-leakage) |
| 5 | 3 họ model → forecast | P3·P4 | 🔴 **Stub** — có interface + code tham chiếu trong notebook, chờ triển khai |
| 6–7 | Hiệu chuẩn + metric | P5 | 🟡 Baseline metric + NB xong; **split-conformal + coverage là việc P5** |
| 8 | Rolling ≥3 + DM/MCB | P1·P5 | 🟡 **Công cụ xong** (`significance.py`); chạy ra nhãn thắng cần forecast của bước 5 |
| 9 | Bảng khuyến nghị | P2 | 🔴 Chờ bước 6–8 |
| 10 | Báo cáo + slide | P1·P2 | 🔴 Chờ kết quả |

**Đã có sẵn để dùng ngay:**
- `configs/sample_ids.csv` — 3.474 chuỗi mẫu (dùng CHUNG cho mọi model).
- `configs/segment_labels.parquet` — nhãn 4 nhóm cho toàn bộ 30.490 chuỗi.
- `notebooks/M5_..._study.ipynb` — **pilot chạy full P1→P5 trong 1 file**: là "bản mẫu" để mỗi người
  copy code phần mình ra module. `outputs/` chứa kết quả pilot 800 chuỗi (tham chiếu).

---

## 1. Cài đặt lần đầu (một lần duy nhất)

### 1.1 Cài công cụ
1. **Python 3.11** — https://www.python.org/downloads/ (khi cài **tick "Add Python to PATH"**).
2. **Git** — https://git-scm.com/download/win
3. (khuyến nghị) **VS Code** — https://code.visualstudio.com/ + extension *Python*, *Jupyter*.
4. (tuỳ chọn) **GitHub CLI** `gh` — https://cli.github.com/ (đăng nhập: `gh auth login`).

### 1.2 Nhận lời mời & clone repo
- Mở email/thông báo GitHub → **Accept invitation** vào repo.
- Mở **PowerShell**, chạy:
```powershell
cd D:\   # hoặc thư mục bạn muốn
git clone https://github.com/DuyKhanh162/m5-intermittent-forecasting
cd m5-intermittent-forecasting
```

### 1.3 Tạo môi trường Python riêng & cài thư viện
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # kích hoạt (đầu dòng lệnh có "(.venv)")
python -m pip install --upgrade pip
pip install -r requirements.txt      # cài đúng version cả nhóm dùng chung
```
> Nếu `Activate.ps1` báo lỗi execution policy, chạy 1 lần:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` rồi thử lại.

### 1.4 Tải dữ liệu M5 (KHÔNG có sẵn trong repo vì quá lớn ~500MB)
```powershell
python scripts\download_data.py
```
- Nếu bạn đã có file `m5-forecasting-accuracy.zip`, đặt nó ở gốc repo rồi chạy lại → tự giải nén.
- Nếu chưa: script sẽ in hướng dẫn tải từ Kaggle
  (https://www.kaggle.com/competitions/m5-forecasting-accuracy/data).

### 1.5 Sinh dữ liệu & kiểm tra mọi thứ chạy
```powershell
$env:PYTHONUTF8=1                    # để in tiếng Việt trên Windows
python -m src.data.build_long --scope sample   # ~30s, tạo data/processed/data_long.parquet
python -m pytest tests\ -q           # phải thấy "13 passed"
```
✅ Thấy `13 passed` là môi trường của bạn đã ĐỒNG BỘ với cả nhóm. Bắt đầu làm được.

> **Vì sao ai cũng ra kết quả giống nhau?** Mọi hằng số nằm trong `configs/config.yaml`
> (seed=42, split, quantile…), mẫu cố định trong `configs/sample_ids.csv`. Chạy lại `build_long`
> luôn cho **data_long y hệt**.

---

## 2. Quy trình làm việc ĐỒNG BỘ (Git flow) — phần quan trọng nhất

**Ý tưởng:** không ai sửa thẳng vào `main`. Mỗi việc = 1 **branch** riêng → làm xong mở **Pull
Request (PR)** → **1 người khác review** → **merge** vào `main`. Nhờ vậy `main` luôn chạy được và
không ai đạp lên code của nhau.

### Vòng lặp chuẩn cho MỖI đầu việc

```powershell
# 1) Luôn bắt đầu từ main mới nhất
git checkout main
git pull origin main

# 2) Tạo branch cho việc của mình (quy ước: p<số>/buoc<k>-<mô-tả-ngắn>)
git checkout -b p3/buoc5-lightgbm-quantile

# 3) ... viết code, chạy thử ...
$env:PYTHONUTF8=1
python -m pytest tests\ -q          # đảm bảo không làm hỏng gì

# 4) Lưu thay đổi (commit)
git add -A
git commit -m "P3: lightgbm 9 quantile, xuat forecast lgbm.parquet"

# 5) Đẩy branch lên GitHub
git push -u origin p3/buoc5-lightgbm-quantile

# 6) Mở PR: link GitHub in ra ở bước 5, bấm vào -> "Create pull request"
#    (điền template, gán 1 người review). Hoặc dùng: gh pr create --fill
```

### Sau khi mở PR
- **CI tự chạy** `pytest` — chờ dấu ✓ xanh.
- Nhờ **1 thành viên** bấm **Review → Approve**.
- Đủ approve + CI xanh → bấm **Merge** (chọn *Squash and merge*) → **Delete branch**.
- Về máy: `git checkout main` rồi `git pull origin main` để cập nhật.

> ⚠️ Hiện repo là **Free + private** nên GitHub **chưa ép buộc** được luật này ở phía server
> (đang chờ P1 duyệt GitHub Student Pack). Trong lúc đó **tự giác tuân thủ**: vẫn mở PR, vẫn nhờ
> review, **không push thẳng vào `main`**.

### Quy ước tên branch & commit
- Branch: `p2/buoc2-eda-segmentation`, `p5/buoc6-conformal`, `p1/buoc8-mcb`…
- Commit: ngắn, rõ, bắt đầu bằng `Pn:` — ví dụ `P4: chronos-bolt zero-shot + runtime`.

---

## 3. Mỗi người bắt đầu từ đâu

Mở notebook pilot `notebooks/M5_demand_forecasting_study.ipynb` để xem **code mẫu phần của mình**
đã chạy được thế nào, rồi bê ra module tương ứng (đừng viết lại từ đầu).

| Bạn | Bước | Bắt đầu từ | Đích đến (output) |
|:---:|---|---|---|
| **P2** | 2–3 | `src/segmentation/sbc.py` (baseline) + notebook §2 | EDA + `sample_ids`/`segment_labels` (đã có) + 2 góc báo cáo |
| **P3** | 5 | `src/models/ml_lightgbm.py` (stub) + notebook §4 | `outputs/forecasts/lgbm.parquet` (raw + calibrated) |
| **P4** | 5 | `src/models/classical.py`, `foundation.py` (stub) + notebook §5–6 | `{naive,snaive,croston,sba,tsb,chronos_bolt,ttm}.parquet` |
| **P5** | 6–7–8 | `src/common/metrics.py`, `calibration.py`, `src/evaluation/harness.py` + notebook §7 | bảng metric + bảng thắng theo nhóm |
| **P1** | 0·1·4·8·10a | ✅ xong 1·4·8-công cụ | điều phối + gộp báo cáo |

**Xuất forecast phải đúng "khuôn" chung** — luôn dùng:
```python
from src.common.forecast_io import write_forecast
write_forecast(df, "outputs/forecasts/<model>.parquet")   # tự kiểm tra đủ cột
```
Cột bắt buộc: `series_id, date, d_int, quantile_level, value, model`.

---

## 4. Cách dùng các module đã có (ví dụ code)

```python
from src.common import schema
from src.data import splits, build_long
import pandas as pd

cfg = schema.load_config()                     # đọc configs/config.yaml
long = pd.read_parquet("data/processed/data_long.parquet")

# Lấy 3 cửa sổ rolling-origin (bước 4)
for w in splits.rolling_windows(cfg):
    train, val, test = splits.split_long(long, w)
    print(w.name, "train<=", w.train_end, "test", w.test_start, "->", w.test_end)

# Kiểm định (bước 8) — khi đã có loss của các model
from src.evaluation import significance
dm, p = significance.diebold_mariano(loss_model_a, loss_model_b)
res = significance.mcb(loss_matrix, ["lgbm","chronos_bolt","sba"])
```

---

## 5. QUY TẮC VÀNG (vi phạm là hỏng so sánh)

1. **Không sửa "mối nối đông cứng"** nếu chưa báo P1: `src/common/schema.py`, `forecast_io.py`,
   `configs/config.yaml`, `configs/sample_ids.csv`, `configs/segment_labels.parquet`.
2. **Không shuffle. Tôn trọng trục thời gian.** Chỉ dùng dữ liệu ≤ ngày gốc.
3. **ML: lag ≥ horizon (28)** — nếu không sẽ "nhìn trộm" tương lai → điểm đẹp giả.
4. **Chỉ tune/hiệu chuẩn trên `validation`**, không đụng `test` sớm.
5. **Mọi model chạy trên cùng `sample_ids` + cùng split** → mới so được.
6. **Đừng commit dữ liệu lớn** (`raw-data/`, `data/`, `*.zip` đã bị `.gitignore`).

---

## 6. Sự cố thường gặp

| Triệu chứng | Cách xử lý |
|---|---|
| `UnicodeEncodeError` / tiếng Việt lỗi | `$env:PYTHONUTF8=1` trước khi chạy |
| `ModuleNotFoundError: src` | Chạy từ **gốc repo** và dùng `python -m src.data.build_long` (có `-m`) |
| `FileNotFoundError: sales_train_evaluation.csv` | Chạy `python scripts\download_data.py` |
| `Activate.ps1` bị chặn | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Quên bật venv (`(.venv)` không hiện) | `.\.venv\Scripts\Activate.ps1` |
| **Merge conflict** khi PR | `git checkout main && git pull`, rồi `git checkout <branch>` và `git merge main`, sửa chỗ `<<<<`, `git add`, `git commit` |
| Lỡ commit vào `main` | Báo P1; tạm thời: `git branch p x-fix && git reset --hard origin/main` (cẩn thận, hỏi trước) |

---

## 7. Nhịp làm việc & mốc thời gian
- Nền lý thuyết (mỗi người phần mình): **26/9**
- Xong toàn bộ, kể cả slide: **trước 7/10**
- Nộp chính thức: **15/10**

Chi tiết kế hoạch: [`docs/plan/PLAN_REVISED.md`](plan/PLAN_REVISED.md). Phân công đầy đủ:
[`../CONTRIBUTING.md`](../CONTRIBUTING.md).
