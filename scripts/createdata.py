from __future__ import annotations
from datetime import datetime
from pathlib import Path
import pandas as pd

from marketdash.config import load_config
from marketdash.providers import yf_history  # TE dispo aussi si besoin
from marketdash.utils import compute_perf_table, ensure_dir

# === Univers (modifiable sans toucher au moteur) ===
SP500_SECTORS = {
    "Information Technology": "XLK",
    "Communication Services": "XLC",
    "Industrials": "XLI",
    "Utilities": "XLU",
    "Financials": "XLF",
    "Consumer Discretionary": "XLY",
    "Health Care": "XLV",
    "Energy": "XLE",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Cons. Staples": "XLP",
}

# Stoxx 600 — proxies iShares/ETF (adapte si besoin; manquants => "—")
STOXX600_SECTORS = {
    "Banks": "EXV1.DE",
    "Utilities": "EXH7.DE",
    "Financial Services": "EXX6.DE",
    "Energy": "EXH1.DE",
    "Insurance": "EXH4.DE",
    "Basic resources": "EXH2.DE",
    "Technology": "EXV3.DE",
    "Construction": "EXV6.DE",
    "Real Estate": "EXI5.DE",
    "Automobiles": "EXV4.DE",
    "Consumer Discretionary": "EXH3.DE",
    "Media": "EXV5.DE",
    "Retail": "EXI1.DE",
    "Healthcare": "EXH5.DE",
    "Travel & Leisure": "EXV2.DE",
    "Chemicals": "EXH6.DE",
}

def _collect_block(universe_name: str, mapping: dict[str,str], start: datetime, end: datetime) -> pd.DataFrame:
    series_map = {}
    for sector, ticker in mapping.items():
        s = yf_history(ticker, start, end)
        series_map[sector] = s
    df = compute_perf_table(series_map, universe_name)
    return df

def main():
    cfg = load_config()
    cache_dir = ensure_dir(cfg["cache_dir"])

    end = datetime.now()
    start = end.replace(year=end.year-2)

    df_spx   = _collect_block("SP 500",    SP500_SECTORS,   start, end)
    df_stoxx = _collect_block("Stoxx 600", STOXX600_SECTORS, start, end)

    df = pd.concat([df_spx, df_stoxx], ignore_index=True)
    out = Path(cache_dir) / "sector_data.csv"
    df.to_csv(out, index=False)
    print(f"✅ Saved data -> {out}")

if __name__ == "__main__":
    main()
