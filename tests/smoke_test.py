# -*- coding: utf-8 -*-
"""Smoke-test the custom pipeline (skips pip install + guarded model cells).
Runs the notebook's own code cells so the test can't drift from the notebook.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import matplotlib
matplotlib.use("Agg")
import nbformat, traceback
import subprocess, importlib, time, warnings, os, json, math, random

warnings.filterwarnings("ignore")

from pathlib import Path
_NB = Path(__file__).resolve().parents[1] / "notebooks" / "M5_demand_forecasting_study.ipynb"
nb = nbformat.read(str(_NB), as_version=4)
ns = {"display": print}   # display() -> print outside Jupyter

code_cells = [c for c in nb.cells if c.cell_type == "code"]
print(f"Tong so code cells: {len(code_cells)}\n")

for i, c in enumerate(code_cells):
    src = c.source
    if "PKGS =" in src and "pip_install" in src:
        print(f"[{i:02d}] SKIP pip-install cell")
        # Seed objects normally created by the setup cell so later notebook
        # cells are tested without reinstalling packages on every smoke run.
        ns.update({
            "sys": sys,
            "subprocess": subprocess,
            "importlib": importlib,
            "time": time,
            "warnings": warnings,
            "os": os,
            "json": json,
            "math": math,
            "random": random,
            "INSTALL_LOG": {"(smoke)": "skipped pip install"},
        })
        continue
    try:
        exec(compile(src, f"<cell {i}>", "exec"), ns)
        # shrink sample right after CONFIG is defined
        if "CONFIG = dict(" in src:
            ns["CONFIG"]["SAMPLE_PER_SEGMENT"] = 40
            print("       (patched SAMPLE_PER_SEGMENT=40 for smoke test)")
        head = src.strip().splitlines()[0][:60]
        print(f"[{i:02d}] OK   {head}")
    except Exception as e:
        head = src.strip().splitlines()[0][:60]
        print(f"[{i:02d}] FAIL {head}")
        traceback.print_exc()
        break
else:
    print("\n=== SMOKE TEST PASSED (moi cell chay het) ===")
