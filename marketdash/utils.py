from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import yaml, os

# ---------- Helpers ----------
def last_business_day(dt: datetime) -> datetime:
    while dt.weekday() >= 5:
        dt -= timedelta(days=1)
    return dt

def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def load_yaml(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

# ---------- Perf calculations ----------
def _pct(a: float, b: float) -> float | float("nan"):
    if pd.isna(a) or pd.isna(b) or b == 0:
        return np.nan
    return (a / b - 1.0) * 100.0

def compute_perf_table(series_map: dict[str, pd.Series],
                       universe_name: str) -> pd.DataFrame:
    """
    Input: dict {label -> Series(prices)}.
    Output: DataFrame avec colonnes: universe, sector, level, perf_5d, perf_1m, perf_3m, perf_ytd
    """
    today = last_business_day(datetime.now())
    rows = []
    for label, s in series_map.items():
        s = s.dropna()
        if s.empty:
            rows.append([universe_name, label, np.nan, np.nan, np.nan, np.nan, np.nan])
            continue

        s = s.asfreq("B").ffill()  # régularise Jours Ouvrés
        level = float(s.iloc[-1])

        # points de comparaison
        d5 = s.index[-1] - pd.tseries.offsets.BDay(5)
        d21 = s.index[-1] - pd.tseries.offsets.BDay(21)  # ~1M
        d63 = s.index[-1] - pd.tseries.offsets.BDay(63)  # ~3M
        y0 = pd.Timestamp(year=today.year-1, month=12, day=31)

        def val_at(idx_like):
            try:
                return float(s.loc[:idx_like].iloc[-1])
            except Exception:
                return np.nan

        p5  = val_at(d5)
        p21 = val_at(d21)
        p63 = val_at(d63)
        py0 = val_at(y0)

        perf_5d = _pct(level, p5)
        perf_1m = _pct(level, p21)
        perf_3m = _pct(level, p63)
        perf_ytd = _pct(level, py0)

        rows.append([universe_name, label, level, perf_5d, perf_1m, perf_3m, perf_ytd])

    df = pd.DataFrame(rows, columns=["universe","sector","level","perf_5d","perf_1m","perf_3m","perf_ytd"])
    return df
