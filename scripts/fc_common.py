"""Tiện ích dùng chung cho các script sinh forecast bổ sung (P3 cổ điển + P4 val).

Giữ ĐÚNG hợp đồng lưới P5: 3.474 chuỗi × 3 cửa sổ × 9 quantile × 28 ngày, giá trị đếm >= 0.
Spec bung point -> 9 quantile dùng Negative Binomial (NB) giống P4/M5_reference §3.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import yaml
from scipy import stats


def find_root() -> Path:
    cwd = Path.cwd()
    for cand in (cwd, cwd.parent, *cwd.parents):
        if (cand / "common" / "config.yaml").exists():
            return cand
    raise RuntimeError(f"Không tìm được project root từ {cwd}")


ROOT = find_root()
CFG = yaml.safe_load(open(ROOT / "common/config.yaml", encoding="utf-8"))
SEED = int(CFG["seed"])
H = int(CFG["horizon"])
Q = sorted(float(q) for q in CFG["quantiles"])

PATH_LONG = ROOT / "data/processed/data_long.parquet"
PATH_WINDOWS = ROOT / "common/rolling_windows.csv"
PATH_SAMPLE = ROOT / "common/sample_ids.csv"
FORECAST_DIR = ROOT / "data/outputs/forecasts"
VAL_DIR = FORECAST_DIR / "val"

TEST_COLS = ["series_id", "date", "d_int", "quantile_level", "value", "model"]
VAL_COLS = TEST_COLS + ["window"]


def load_inputs():
    """Trả về (data_long đã sort, windows, sample_ids list, day_to_date dict)."""
    windows = pd.read_csv(PATH_WINDOWS)
    sample_ids = pd.read_csv(PATH_SAMPLE)["series_id"].astype(str).tolist()
    data = pd.read_parquet(PATH_LONG, columns=["series_id", "date", "d_int", "sales"])
    data["series_id"] = data["series_id"].astype(str)
    data["date"] = pd.to_datetime(data["date"])
    data["d_int"] = pd.to_numeric(data["d_int"]).astype(int)
    data["sales"] = pd.to_numeric(data["sales"]).astype(np.float32)
    data = data.sort_values(["series_id", "d_int"]).reset_index(drop=True)

    assert set(data["series_id"].unique()) == set(sample_ids), \
        "data_long không khớp common/sample_ids.csv"
    assert data.groupby("d_int")["date"].nunique().max() == 1
    day_to_date = (data[["d_int", "date"]].drop_duplicates()
                   .set_index("d_int")["date"].to_dict())
    return data, windows, sample_ids, day_to_date


def get_dispersion(data: pd.DataFrame, origin: int) -> dict:
    """NB dispersion r theo chuỗi từ insample (d_int <= origin): r = m^2/(v-m) nếu v>m, else inf (Poisson)."""
    mv = (data.loc[data["d_int"] <= origin]
          .groupby("series_id")["sales"].agg(["mean", "var"]))
    mean, var = mv["mean"].to_numpy(), mv["var"].to_numpy()
    r = np.full(len(mv), np.inf, dtype=np.float64)
    use_nb = (mean > 0) & (var > mean)
    r[use_nb] = mean[use_nb] ** 2 / (var[use_nb] - mean[use_nb])
    return dict(zip(mv.index.astype(str), r))


def point_to_quantiles(point_df: pd.DataFrame, model_name: str, disp_r: dict) -> pd.DataFrame:
    """point_df: [series_id, date, d_int, value(mean)] -> long 9 quantile theo NB/Poisson."""
    pf = point_df.copy()
    pf["value"] = pf["value"].clip(lower=0).astype(float)
    pf["r"] = pf["series_id"].map(disp_r).fillna(np.inf)
    mu, r = pf["value"].to_numpy(), pf["r"].to_numpy()
    finite = np.isfinite(r) & (r > 0)
    outputs = []
    for q in Q:
        qv = np.empty_like(mu, dtype=float)
        if finite.any():
            rr, mm = r[finite], mu[finite]
            p = rr / (rr + np.where(mm > 0, mm, 1e-9))
            qv[finite] = stats.nbinom.ppf(q, rr, p)
        if (~finite).any():
            qv[~finite] = stats.poisson.ppf(q, mu[~finite])
        block = pf[["series_id", "date", "d_int"]].copy()
        block["quantile_level"] = float(q)
        block["value"] = np.nan_to_num(qv, nan=0.0, posinf=0.0, neginf=0.0)
        block["model"] = model_name
        outputs.append(block)
    return pd.concat(outputs, ignore_index=True)[TEST_COLS]


def validate_grid(df: pd.DataFrame, model_name: str, n_series: int, exp_dint: set, is_val: bool):
    cols = VAL_COLS if is_val else TEST_COLS
    assert list(df.columns) == cols, f"{model_name}: sai schema {list(df.columns)}"
    assert df["series_id"].nunique() == n_series, \
        f"{model_name}: {df['series_id'].nunique()} series (cần {n_series})"
    assert set(df["d_int"].unique()) == exp_dint, f"{model_name}: sai tập ngày"
    assert sorted(np.round(df["quantile_level"].unique(), 6)) == sorted(np.round(Q, 6))
    assert df["value"].notna().all() and np.isfinite(df["value"]).all() and (df["value"] >= 0).all()
    assert set(df["model"].unique()) == {model_name}
    key = (["window"] if is_val else []) + ["series_id", "d_int", "quantile_level"]
    assert df.duplicated(key).sum() == 0, f"{model_name}: trùng key"
    idx = (["window"] if is_val else []) + ["series_id", "d_int"]
    wide = df.pivot(index=idx, columns="quantile_level", values="value")[Q]
    n_cross = int((np.diff(wide.to_numpy(), axis=1) < -1e-8).any(axis=1).sum())
    assert n_cross == 0, f"{model_name}: còn {n_cross} quantile crossing"
    print(f"  [OK] {model_name:14s} {len(df):>9,} dòng | {df['series_id'].nunique():,} chuỗi "
          f"| {df['d_int'].nunique()} ngày | không crossing")
