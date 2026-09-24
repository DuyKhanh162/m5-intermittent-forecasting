# -*- coding: utf-8 -*-
"""run_pilot.py — Chạy TOÀN BỘ pipeline pilot từ notebook (cấu hình gốc, KHÔNG thu nhỏ).

Regenerate outputs/ (forecast + metric + decision_table pilot) ở quy mô thật của pilot
(SAMPLE_PER_SEGMENT gốc, có FM). Khác `tests/smoke_test.py` (thu nhỏ 40/nhóm để chạy nhanh).

Chạy từ gốc repo:  python scripts/run_pilot.py
Cần: raw-data/ (hoặc data/raw/) + packages trong requirements.txt. CPU đủ (~vài phút).
"""
import os
import sys
import io
import traceback
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import matplotlib
matplotlib.use("Agg")
import nbformat

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)                       # notebook dùng đường dẫn tương đối gốc repo
# notebook đọc raw từ "raw-data/"; nếu chỉ có data/raw/ thì tạo symlink tạm hiểu được
if not (ROOT / "raw-data").exists() and (ROOT / "data" / "raw").exists():
    print("Lưu ý: notebook đọc 'raw-data/'. Bạn đang có 'data/raw/'. "
          "Tạo junction/symlink 'raw-data' -> 'data/raw' hoặc copy trước khi chạy.")

NB = ROOT / "notebooks" / "M5_demand_forecasting_study.ipynb"
nb = nbformat.read(str(NB), as_version=4)
ns = {"display": print}

code_cells = [c for c in nb.cells if c.cell_type == "code"]
print(f"Chạy pilot đầy đủ: {len(code_cells)} code cells (cấu hình gốc)\n")

import subprocess, importlib, time, warnings, json, math, random  # noqa: E402
warnings.filterwarnings("ignore")

for i, c in enumerate(code_cells):
    src = c.source
    if "PKGS =" in src and "pip_install" in src:
        print(f"[{i:02d}] SKIP pip-install cell (giả định đã cài sẵn)")
        ns.update(dict(sys=sys, subprocess=subprocess, importlib=importlib, time=time,
                       warnings=warnings, os=os, json=json, math=math, random=random,
                       INSTALL_LOG={"(run_pilot)": "skipped pip install"}))
        continue
    try:
        exec(compile(src, f"<cell {i}>", "exec"), ns)
        head = src.strip().splitlines()[0][:60]
        print(f"[{i:02d}] OK   {head}")
    except Exception:
        print(f"[{i:02d}] FAIL {src.strip().splitlines()[0][:60]}")
        traceback.print_exc()
        raise SystemExit(1)

print("\n=== PILOT CHẠY XONG — outputs/ đã được tái tạo ở quy mô gốc ===")
