"""Khung tiêu chí readiness cho P3/P4 — đo DIAGNOSTIC THÔ trên output test full-scale.

KHÔNG phải metric cuối của P5 (không calibration, không DM/MCB, không 2 bảng balanced/weighted).
Mục đích: trả lời "P3/P4 đã đủ tốt để bàn giao chưa" bằng:
  - D1 hợp đồng lưới (series×cửa sổ×quantile×H, value>=0, monotonic)
  - D4 sanity xác suất thô: coverage các dải danh nghĩa (50/67/95/99%) vs mục tiêu, zero-rate median,
       độ rộng dải 95% — toàn cục và theo nhóm demand.
Chạy: python scripts/eval_readiness.py
"""
import numpy as np
import pandas as pd

import fc_common as fc
from fc_common import H, Q, FORECAST_DIR

MODELS = ["naive", "snaive", "croston", "sba", "tsb", "lgbm", "chronos_bolt", "ttm", "moirai_2"]
# (q_low, q_high, target) — chỉ dùng các cặp quantile có sẵn trong lưới
BANDS = [(0.25, 0.75, 0.50), (0.165, 0.835, 0.67), (0.025, 0.975, 0.95), (0.005, 0.995, 0.99)]


def main():
    data, windows, sample_ids, _ = fc.load_inputs()
    # actuals + segment cho các ngày test
    long = pd.read_parquet(fc.PATH_LONG, columns=["series_id", "d_int", "sales", "segment"])
    long["series_id"] = long["series_id"].astype(str)
    test_dint = set()
    for _, w in windows.iterrows():
        test_dint |= set(range(int(w["test_start"]), int(w["test_end"]) + 1))
    actual = long[long["d_int"].isin(test_dint)].copy()
    actual["sales"] = actual["sales"].astype(np.float32)
    seg_map = long[["series_id", "segment"]].drop_duplicates().set_index("series_id")["segment"]

    rows_global, rows_seg = [], []
    for m in MODELS:
        p = FORECAST_DIR / f"{m}.parquet"
        if not p.exists():
            rows_global.append({"model": m, "note": "THIẾU FILE"}); continue
        df = pd.read_parquet(p)
        df["series_id"] = df["series_id"].astype(str)
        wide = df.pivot_table(index=["series_id", "d_int"], columns="quantile_level",
                              values="value", aggfunc="first")
        wide = wide.merge(actual.set_index(["series_id", "d_int"])["sales"],
                          left_index=True, right_index=True, how="inner").reset_index()
        wide["segment"] = wide["series_id"].map(seg_map)
        a = wide["sales"].to_numpy()

        def cov(ql, qh):
            return float(((wide[ql].to_numpy() <= a) & (a <= wide[qh].to_numpy())).mean())

        rec = {"model": m, "n_points": len(wide)}
        for ql, qh, tgt in BANDS:
            rec[f"cov{int(tgt*100)}"] = round(cov(ql, qh), 3)
        rec["w95"] = round(float((wide[0.975] - wide[0.025]).mean()), 2)  # độ rộng dải 95%
        rec["med_zero%"] = round(float((wide[0.5] == 0).mean() * 100), 1)
        rows_global.append(rec)

        for s, g in wide.groupby("segment"):
            aa = g["sales"].to_numpy()
            rows_seg.append({"model": m, "segment": s,
                             "cov95": round(float(((g[0.025].to_numpy() <= aa) &
                                                   (aa <= g[0.975].to_numpy())).mean()), 3)})

    gdf = pd.DataFrame(rows_global)
    print("=== D1+D4 Diagnostic THÔ (test 3.474×3, CHƯA calibrate) ===")
    print("Mục tiêu coverage: cov50→0.50 cov67→0.67 cov95→0.95 cov99→0.99\n")
    print(gdf.to_string(index=False))

    print("\n=== cov95 theo nhóm demand (pivot) ===")
    sdf = pd.DataFrame(rows_seg).pivot(index="model", columns="segment", values="cov95")
    print(sdf.to_string())

    # cờ readiness thô cho coverage 95: |cov-0.95| <= 0.05 = ổn thô; ngược lại cần conformal (bình thường với FM)
    print("\n=== Cờ sanity cov95 (|cov95-0.95|<=0.05 = OK thô; lệch = chờ conformal của P5) ===")
    for _, r in gdf.iterrows():
        if "cov95" in r and pd.notna(r["cov95"]):
            d = r["cov95"] - 0.95
            flag = "OK" if abs(d) <= 0.05 else ("THIẾU PHỦ" if d < 0 else "THỪA PHỦ")
            print(f"  {r['model']:14s} cov95={r['cov95']:.3f}  [{flag}]")


if __name__ == "__main__":
    main()
