"""Kiểm tra toàn bộ đầu vào P5: TEST (forecasts/*.parquet) + VAL (forecasts/val/*.parquet)
theo đúng hợp đồng lưới mà P5 áp dụng (3.474 chuỗi × 3 cửa sổ × 9 quantile × 28 ngày).
"""
import numpy as np
import pandas as pd

import fc_common as fc
from fc_common import H, Q, FORECAST_DIR, VAL_DIR

EXPECT_MODELS = ["naive", "snaive", "croston", "sba", "tsb", "lgbm", "chronos_bolt", "ttm", "moirai_2"]


def main():
    data, windows, sample_ids, _ = fc.load_inputs()
    exp_series = set(sample_ids)
    exp_test_dint, exp_val_dint = set(), set()
    for _, w in windows.iterrows():
        exp_test_dint |= set(range(int(w["test_start"]), int(w["test_end"]) + 1))
        exp_val_dint |= set(range(int(w["train_end"]) + 1, int(w["val_end"]) + 1))
    exp_rows = len(windows) * len(exp_series) * H * len(Q)

    def check(path, exp_dint):
        if not path.exists():
            return {"rows": 0, "series": 0, "ngày": 0, "trạng thái": "THIẾU FILE"}
        df = pd.read_parquet(path)
        df["series_id"] = df["series_id"].astype(str)
        iss = []
        if set(df["series_id"].unique()) != exp_series:
            iss.append(f"{df['series_id'].nunique()} series")
        if set(df["d_int"].unique()) != exp_dint:
            iss.append(f"{df['d_int'].nunique()} ngày")
        if sorted(np.round(df["quantile_level"].unique(), 6)) != sorted(np.round(Q, 6)):
            iss.append("sai quantile")
        if len(df) != exp_rows:
            iss.append(f"{len(df):,} dòng≠{exp_rows:,}")
        if not ((df["value"] >= 0).all() and np.isfinite(df["value"]).all()):
            iss.append("value lỗi")
        return {"rows": len(df), "series": df["series_id"].nunique(),
                "ngày": df["d_int"].nunique(),
                "trạng thái": "đúng lưới" if not iss else "LỆCH: " + "; ".join(iss)}

    print(f"Lưới chuẩn: {len(exp_series):,} series × {len(windows)} cửa sổ × {len(Q)} q × {H} ngày "
          f"= {exp_rows:,} dòng/model\n")
    rows = []
    for m in EXPECT_MODELS:
        t = check(FORECAST_DIR / f"{m}.parquet", exp_test_dint)
        v = check(VAL_DIR / f"{m}.parquet", exp_val_dint)
        rows.append({"model": m, "TEST": t["trạng thái"], "VAL": v["trạng thái"]})
    rep = pd.DataFrame(rows)
    print(rep.to_string(index=False))

    test_ok = all(r["TEST"] == "đúng lưới" for r in rows)
    val_ok = all(r["VAL"] == "đúng lưới" for r in rows)
    print(f"\nTEST đủ 9 model đúng lưới: {'CÓ' if test_ok else 'CHƯA'}")
    print(f"VAL  đủ 9 model đúng lưới: {'CÓ' if val_ok else 'CHƯA'}")
    print("=> P5 " + ("ĐỦ ĐIỀU KIỆN chạy đầy đủ (test + conformal val)."
                       if test_ok and val_ok else "còn thiếu — xem cột LỆCH/THIẾU ở trên."))


if __name__ == "__main__":
    main()
