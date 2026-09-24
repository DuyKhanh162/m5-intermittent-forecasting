# -*- coding: utf-8 -*-
"""download_data.py — Chuẩn bị dữ liệu M5 thô vào data/raw/.

Thứ tự thử:
  1. Nếu data/raw/ (hoặc raw-data/) đã có sales_train_evaluation.csv -> xong.
  2. Nếu có file zip M5 (m5-forecasting-accuracy.zip) ở gốc repo hoặc data/ -> giải nén vào data/raw/.
  3. Ngược lại -> in hướng dẫn tải từ Kaggle rồi thoát.

Dữ liệu M5 KHÔNG commit lên git (quá lớn). Mỗi thành viên tự chạy script này 1 lần.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REQUIRED = [
    "calendar.csv", "sell_prices.csv",
    "sales_train_evaluation.csv", "sample_submission.csv",
]
KAGGLE_HINT = """
Không tìm thấy dữ liệu M5. Hãy lấy bằng MỘT trong hai cách:

  (A) Kaggle CLI (cần `pip install kaggle` + API token ~/.kaggle/kaggle.json):
        kaggle competitions download -c m5-forecasting-accuracy -p data/raw
      rồi chạy lại: python scripts/download_data.py

  (B) Tải thủ công zip từ https://www.kaggle.com/competitions/m5-forecasting-accuracy/data
      đặt file 'm5-forecasting-accuracy.zip' ở gốc repo, rồi chạy lại script này.
""".strip()


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here] + list(here.parents):
        if (p / "configs" / "config.yaml").exists():
            return p
    return here.parents[1]


def _has_all(d: Path) -> bool:
    return d.exists() and all((d / f).exists() for f in REQUIRED)


def main() -> int:
    root = repo_root()
    target = root / "data" / "raw"
    target.mkdir(parents=True, exist_ok=True)

    if _has_all(target):
        print(f"✓ Dữ liệu đã sẵn ở {target}")
        return 0
    legacy = root / "raw-data"
    if _has_all(legacy):
        print(f"✓ Dữ liệu đã sẵn ở {legacy} (build_long tự nhận). Không cần làm gì thêm.")
        return 0

    # tìm zip để giải nén
    candidates = list(root.glob("*.zip")) + list((root / "data").glob("*.zip"))
    zip_path = next((z for z in candidates if "m5" in z.name.lower()), None)
    if zip_path is None and candidates:
        zip_path = candidates[0]

    if zip_path and zip_path.exists():
        print(f"Giải nén {zip_path.name} -> {target} ...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(target)
        # một số bản M5 lồng thêm zip con — giải nén nốt
        for inner in target.glob("*.zip"):
            with zipfile.ZipFile(inner) as zf:
                zf.extractall(target)
        if _has_all(target):
            print(f"✓ Xong. Dữ liệu ở {target}")
            return 0
        print("⚠ Giải nén xong nhưng thiếu file. Kiểm tra nội dung zip.")

    print(KAGGLE_HINT)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
