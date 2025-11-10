"""
Collecte des taux souverains via FRED et construction d'un CSV unique.

- Courbe US : 1M, 3M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y
- Bund 10Y  : Allemagne
- OAT 10Y   : France

Sortie : data/rates_fred.csv
"""

from __future__ import annotations

from datetime import datetime
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

# ---------- mapping des séries FRED ----------

FRED_SERIES: Dict[str, str] = {
    # Courbe US (constant maturity Treasury)
    "US_1M": "DGS1MO",
    "US_3M": "DGS3MO",
    "US_6M": "DGS6MO",
    "US_1Y": "DGS1",
    "US_2Y": "DGS2",
    "US_3Y": "DGS3",
    "US_5Y": "DGS5",
    "US_7Y": "DGS7",
    "US_10Y": "DGS10",
    "US_20Y": "DGS20",
    "US_30Y": "DGS30",
    # Europe
    "Bund_10Y": "IRLTLT01DEM156N",  # Allemagne 10 ans
    "OAT_10Y": "IRLTLT01FRM156N",   # France 10 ans
}


def fetch_fred_series(series_id: str, start: str, api_key: str) -> pd.Series:
    """
    Télécharge une série FRED et renvoie un Series(date -> valeur float).
    """
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
    s = pd.to_numeric(s, errors="coerce")  # "." -> NaN
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

    all_series = {}
    print(f"📥 Download rates from FRED since {start} ...")

    for label, fred_id in FRED_SERIES.items():
        try:
            s = fetch_fred_series(fred_id, start=start, api_key=api_key)
        except Exception as e:  # pragma: no cover
            print(f"  - {label} ({fred_id}) ... ERROR: {e}")
            continue

        if s.empty:
            print(f"  - {label} ({fred_id}) ... no data")
            continue

        all_series[label] = s
        print(f"  - {label} ({fred_id}) ... ok ({len(s)} points)")

    if not all_series:
        print("⚠️ Aucune donnée taux récupérée depuis FRED.")
        sys.exit(0)

    df = pd.DataFrame(all_series)
    df.sort_index(inplace=True)
    df.index.name = "date"

    out_path = DATA_DIR / "rates_fred.csv"
    df.to_csv(out_path)
    print(f"✅ Saved rates -> {out_path}")


if __name__ == "__main__":
    main()
