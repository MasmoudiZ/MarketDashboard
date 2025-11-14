from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

OUT = Path("data")
OUT.mkdir(exist_ok=True, parents=True)

# ============================================================
# Univers macro : groupes + tickers Yahoo Finance
# (tu peux ajuster les tickers si besoin)
# ============================================================
MACRO_GROUPS = {
    "Actions Monde": [
        ("MSCI WORLD",      "URTH"),      # proxy MSCI World
        ("MSCI World EUR",  "IQQW.DE"),   # proxy MSCI World EUR
        ("Vix Index",       "^VIX"),
    ],

    "Actions Etats-Unis": [
        ("S&P 500 INDEX",        "^GSPC"),
        ("RUSSELL 2000 INDEX",   "^RUT"),
        ("NASDAQ COMPOSITE",     "^IXIC"),
    ],

    "Actions Europe": [
        ("Euro Stoxx 50 Pr",     "^STOXX50E"),
        ("STXE 600 (EUR) Pr",    "SXXP.DE"),
        ("DAX INDEX",            "^GDAXI"),
        ("CAC 40 INDEX",         "^FCHI"),
        ("CAC Small Index",      "^CACSM"),   # à ajuster si besoin
        ("CAC Mid & Small INDEX","^CACMS"),   # à ajuster si besoin
        ("FTSE MIB INDEX",       "FTSEMIB.MI"),
        ("FTSE 100 INDEX",       "^FTSE"),
    ],

    "Actions Asie / Emergents": [
        ("NIKKEI 225",           "^N225"),
        ("HANG SENG INDEX",      "^HSI"),
        ("CSI 300 INDEX",        "000300.SS"),
        ("BRAZIL IBOVESPA INDEX","^BVSP"),
    ],

    "Obligations": [
        ("US IG",    "LQD"),
        ("US HY",    "HYG"),
        ("EU IG",    "IEAC.L"),
        ("EU HY",    "IHYG.L"),
    ],

    "Taux": [
        ("US 10 Y",   "^TNX"),      # yield 10Y US (x10)
        ("Bund 10",   "FGBL.DE"),   # future bund 10Y
        ("French 10Y","FOAT.PA"),   # future/ETF OAT
        ("Japon 10 Y","JGBL.L"),    # gov. bonds Japan 10+
        ("UK 10Y",    "GILT.L"),    # UK gilts
    ],

    "Changes": [
        ("EUR/USD", "EURUSD=X"),
        ("EUR/CNY", "EURCNY=X"),
        ("EUR/CHF", "EURCHF=X"),
        ("EUR/JPY", "EURJPY=X"),
        ("EUR/GBP", "EURGBP=X"),
    ],

    "Matières 1ères": [
        ("Or",                 "GC=F"),
        ("Vaneck Gold Miners", "GDX"),
        ("Bitcoin",            "BTC-USD"),
        ("Pétrole",            "CL=F"),
        ("Argent",             "SI=F"),
        ("Agriculture",        "DBA"),
    ],
}

# ============================================================
# Fonctions de calcul
# ============================================================
def pct_change_window(s: pd.Series, days: int) -> float:
    if s.empty:
        return float("nan")
    end = s.index[-1]
    ref = s.loc[: end - timedelta(days=days)]
    if ref.empty:
        return float("nan")
    p0 = float(ref.iloc[-1])
    p1 = float(s.iloc[-1])
    if p0 == 0:
        return float("nan")
    return (p1 / p0 - 1.0) * 100.0


def ytd_change(s: pd.Series) -> float:
    if s.empty:
        return float("nan")
    d0 = pd.Timestamp(year=s.index[-1].year, month=1, day=1)
    ref = s.loc[:d0]
    if ref.empty:
        return float("nan")
    p0 = float(ref.iloc[-1])
    p1 = float(s.iloc[-1])
    if p0 == 0:
        return float("nan")
    return (p1 / p0 - 1.0) * 100.0


# ============================================================
# Main
# ============================================================
def main():
    start = (datetime.today() - timedelta(days=370)).strftime("%Y-%m-%d")

    # liste (groupe, nom, ticker)
    items = [
        (grp, name, tick)
        for grp, lst in MACRO_GROUPS.items()
        for (name, tick) in lst
    ]

    tickers = list({t for _, _, t in items})

    px = yf.download(
        tickers,
        start=start,
        progress=False,
        auto_adjust=False,
    )

    # colonne de prix
    if "Adj Close" in px:
        px = px["Adj Close"]
    else:
        px = px["Close"]

    # drop des colonnes totalement vides
    px = px.dropna(how="all", axis=1)

    rows = []
    for grp, name, t in items:
        s = px[t].dropna() if t in px.columns else pd.Series(dtype=float)
        level = float(s.iloc[-1]) if not s.empty else float("nan")
        lastwk = pct_change_window(s, 7)
        ytd = ytd_change(s)
        rows.append((grp, name, level, lastwk, ytd))

    df = pd.DataFrame(
        rows,
        columns=["Groupe", "Libellé", "Niveau", "LastWeek", "PerfYTD"],
    )
    df.to_csv(OUT / "macro_dashboard.csv", index=False, encoding="utf-8-sig")
    print(f"✅ Saved data -> {OUT/'macro_dashboard.csv'}")


if __name__ == "__main__":
    main()
