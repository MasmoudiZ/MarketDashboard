"""
Collecte des spreads de crédit (OAS) via FRED.

Séries utilisées (BofA Merrill Lynch / ICE indices) :

- US_IG_OAS  : BAMLC0A0CM
- US_HY_OAS  : BAMLH0A0HYM2
- EU_HY_OAS  : BAMLHE00EHYIOAS
- EM_HY_OAS  : BAMLEMHBHYCRPIOAS

Sortie : data/credit_dashboard.csv
"""

from __future__ import annotations

from pathlib import Path
import os
import sys
from typing import Dict

import pandas as pd
import requests

from marketdash.utils import ensure_dir

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ensure_dir(ROOT / "data")

FRED_CREDIT_SERIES: Dict[str, str] = {
    "US_IG_OAS": "BAMLC0A0CM",
    "US_HY_OAS": "BAMLH0A0HYM2",
    "EU_HY_OAS": "BAMLHE00EHYIOAS",
    "EM_HY_OAS": "BAMLEMHBHYCRPIOAS",
}


def fetch_fred_series(series_id: str, start: str, api_key: str) -> pd.Series:
    params = {
        "series_id": series_id,
        "observation_start": start,
        "api_key": api_key,
        "file_type": "json",
    }

    r = requests.get(FRED_URL, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    obs = data.get("observations", [])
    if not obs:
        return pd.Series(dtype="float64")

    dates = [o["date"] for o in obs]
    values = [o["value"] for o in obs]

    s = pd.Series(values, index=pd.to_datetime(dates))
    s = pd.to_numeric(s, errors="coerce")
    s.name = series_id
    return s.dropna()


def main() -> None:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        print(
            "❌ FRED_API_KEY n'est pas défini. "
            "Ajoute la variable d'environnement FRED_API_KEY avec ta clé FRED."
        )
        sys.exit(1)

    start = "2010-01-01"
    print(f"📥 Download credit OAS from FRED since {start} ...")

    all_series = {}

    for label, fred_id in FRED_CREDIT_SERIES.items():
        try:
            s = fetch_fred_series(fred_id, start=start, api_key=api_key)
        except Exception as e:
            print(f"⚠️ FRED error for {label} ({fred_id}): {e}")
            continue

        if s.empty:
            print(f"⚠️ aucune donnée pour {label} ({fred_id})")
            continue

        all_series[label] = s
        print(f"  - {label} ({fred_id}) ... ok ({len(s)} points)")

    if not all_series:
        print("⚠️ Aucune donnée crédit récupérée depuis FRED.")
        sys.exit(0)

    df = pd.DataFrame(all_series)
    df.sort_index(inplace=True)
    df.index.name = "date"

    out_path = DATA_DIR / "credit_dashboard.csv"
    df.to_csv(out_path)
    print(f"✅ Saved credit -> {out_path}")


if __name__ == "__main__":
    main()
