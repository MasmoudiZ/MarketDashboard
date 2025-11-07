from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
import yaml


# ---------- Helpers ----------
def last_business_day(dt: datetime) -> datetime:
    while dt.weekday() >= 5:  # 5=Saturday, 6=Sunday
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
def _pct(a: float, b: float) -> float:
    if pd.isna(a) or pd.isna(b) or b == 0:
        return np.nan
    return (a / b - 1.0) * 100.0


def _coerce_to_series(x, label: str) -> pd.Series:
    """
    Convertit x en Series 1D horodatée, de façon robuste :
    - DataFrame 1 colonne -> colonne unique
    - DataFrame multi-colonnes -> 'Adj Close' si dispo, sinon 1ère colonne
    - ndarray/list -> Series
    - Series -> inchangée
    Nettoie aussi l'index (to_datetime, drop tz).
    """
    # DataFrame
    if isinstance(x, pd.DataFrame):
        if x.shape[1] == 1:
            s = x.iloc[:, 0]
        else:
            if "Adj Close" in x.columns:
                s = x["Adj Close"]
            else:
                s = x.iloc[:, 0]
    # Series
    elif isinstance(x, pd.Series):
        s = x
    # Numpy / list-like
    else:
        try:
            arr = np.asarray(x)
            # squeeze pour éliminer (n,1)
            arr = np.squeeze(arr)
            s = pd.Series(arr)
        except Exception as e:
            raise ValueError(f"[{label}] Impossible de convertir en Series: {type(x)} - {e}")

    # Assainir index temporel
    if not isinstance(s.index, pd.DatetimeIndex):
        idx = pd.to_datetime(s.index, errors="coerce", utc=True)
    else:
        idx = s.index

    # drop NA d’index
    mask_valid = ~pd.isna(idx)
    s = pd.Series(s.values[mask_valid], index=idx[mask_valid])

    # retirer timezone si présente
    try:
        if getattr(s.index, "tz", None) is not None:
            s.index = s.index.tz_convert(None)
    except Exception:
        # si tz_localize/convert plante, on tente tz_localize(None)
        try:
            s.index = s.index.tz_localize(None)
        except Exception:
            pass

    # tri + dropna valeurs
    s = s.sort_index().astype(float).dropna()
    return s


def compute_perf_table(series_map: dict[str, pd.Series | pd.DataFrame | np.ndarray | list],
                       universe_name: str) -> pd.DataFrame:
    """
    Input: dict {label -> Series(prices) OU DataFrame(1 col) OU array}.
    Output: DataFrame colonnes:
      universe, sector, level, perf_5d, perf_1m, perf_3m, perf_ytd
    """
    today = last_business_day(datetime.now())
    rows = []

    for label, obj in series_map.items():
        try:
            s = _coerce_to_series(obj, label)
        except Exception:
            # on logge une ligne vide pour garder la table complète
            rows.append([universe_name, label, np.nan, np.nan, np.nan, np.nan, np.nan])
            continue

        if s.empty:
            rows.append([universe_name, label, np.nan, np.nan, np.nan, np.nan, np.nan])
            continue

        # Fréquence business + ffill
        s = s.asfreq("B").ffill()

        level = float(s.iloc[-1])

        # Jours ouvrés relatifs
        d5  = s.index[-1] - pd.tseries.offsets.BDay(5)
        d21 = s.index[-1] - pd.tseries.offsets.BDay(21)
        d63 = s.index[-1] - pd.tseries.offsets.BDay(63)
        # close Y-1 (au plus proche <= 31/12)
        y0  = pd.Timestamp(year=today.year - 1, month=12, day=31)

        def val_at(idx_like):
            try:
                # prend la dernière valeur <= idx_like
                return float(s.loc[:idx_like].iloc[-1])
            except Exception:
                return np.nan

        p5  = val_at(d5)
        p21 = val_at(d21)
        p63 = val_at(d63)
        py0 = val_at(y0)

        perf_5d  = _pct(level, p5)
        perf_1m  = _pct(level, p21)
        perf_3m  = _pct(level, p63)
        perf_ytd = _pct(level, py0)

        rows.append([universe_name, label, level, perf_5d, perf_1m, perf_3m, perf_ytd])

    df = pd.DataFrame(
        rows,
        columns=["universe", "sector", "level", "perf_5d", "perf_1m", "perf_3m", "perf_ytd"]
    )
    return df
