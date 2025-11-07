from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from marketdash.data.macro_map import MACRO_GROUPS

OUT = Path("data"); OUT.mkdir(exist_ok=True, parents=True)

def pct_change_window(s: pd.Series, days: int) -> float:
    if s.empty: return float("nan")
    end = s.index[-1]
    ref = s.loc[: end - timedelta(days=days)]
    if ref.empty: return float("nan")
    p0 = float(ref.iloc[-1]); p1 = float(s.iloc[-1])
    if p0 == 0: return float("nan")
    return (p1/p0 - 1.0)*100.0

def ytd_change(s: pd.Series) -> float:
    if s.empty: return float("nan")
    d0 = pd.Timestamp(year=s.index[-1].year, month=1, day=1)
    ref = s.loc[:d0]
    if ref.empty: return float("nan")
    p0 = float(ref.iloc[-1]); p1 = float(s.iloc[-1])
    if p0 == 0: return float("nan")
    return (p1/p0 - 1.0)*100.0

def main():
    start = (datetime.today() - timedelta(days=370)).strftime("%Y-%m-%d")
    items = [(grp, name, tick) for grp, lst in MACRO_GROUPS.items() for (name, tick) in lst]
    tickers = list({t for _, _, t in items})
    px = yf.download(tickers, start=start, progress=False, auto_adjust=False)   
    if ("Adj Close" in px):
        px = px["Adj Close"]
    else:
    # fallback si Yahoo renvoie 'Close' (rare si auto_adjust=False, mais safe)
        px = px["Close"]

    # drop des colonnes vides
    px = px.dropna(how="all", axis=1)

    rows = []
    for grp, name, t in items:
        s = px[t].dropna() if t in px.columns else pd.Series(dtype=float)
        level = float(s.iloc[-1]) if not s.empty else float("nan")
        lastwk = pct_change_window(s, 7)
        ytd = ytd_change(s)
        rows.append((grp, name, level, lastwk, ytd))

    df = pd.DataFrame(rows, columns=["Groupe", "Libellé", "Niveau", "LastWeek", "PerfYTD"])
    df.to_csv(OUT / "macro_dashboard.csv", index=False, encoding="utf-8-sig")
    print(f"✅ Saved data -> {OUT/'macro_dashboard.csv'}")

if __name__ == "__main__":
    main()
