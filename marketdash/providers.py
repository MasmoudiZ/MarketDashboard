from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path
import os, time, json, requests
import pandas as pd
import yfinance as yf

# ---------- Yahoo Finance ----------
def yf_history(ticker: str, start: datetime, end: datetime) -> pd.Series:
    """
    Série de prix (Adj Close/Close) sur [start, end], index datetime naive.
    Renvoie une Series vide si rien.
    """
    df = yf.download(
        ticker,
        start=start.strftime("%Y-%m-%d"),
        end=(end + timedelta(days=1)).strftime("%Y-%m-%d"),
        progress=False,
        auto_adjust=False,
    )
    if df is None or df.empty:
        return pd.Series(dtype=float)
    s = df["Adj Close"] if "Adj Close" in df.columns else df["Close"]
    s.index = pd.to_datetime(s.index).tz_localize(None)
    return s.dropna()

# ---------- TradingEconomics ----------
_TE_BASE = "https://api.tradingeconomics.com"

def _te_key() -> str:
    k = os.getenv("TE_API_KEY", "").strip()
    if k:
        return k
    return ""  # on tolère vide => appel public très limité

def te_get(path: str, **params) -> list[dict]:
    """
    GET basique TE. Gère la clé, les erreurs simples et retourne du JSON (list/dict).
    """
    params = {k: v for k, v in params.items() if v is not None}
    key = _te_key()
    if key:
        params["c"] = key
    url = f"{_TE_BASE.rstrip('/')}/{path.lstrip('/')}"
    r = requests.get(url, params=params, timeout=20)
    if r.status_code == 429:
        time.sleep(1.0)  # petit cool-down
        r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    try:
        return r.json()
    except json.JSONDecodeError:
        return []

def te_history(symbol: str, start: datetime | None = None, end: datetime | None = None) -> pd.Series:
    """
    Historique d'un symbole TE (ex: 'Germany Government Bond 10Y').
    Retourne une Series (Date -> valeur) ou vide si indisponible.
    """
    params = {}
    if start: params["d1"] = start.strftime("%Y-%m-%d")
    if end:   params["d2"] = end.strftime("%Y-%m-%d")
    data = te_get(f"historical/series/{symbol}", **params)
    if not data:
        return pd.Series(dtype=float)
    # TE renvoie [{'Date': '2024-01-02T00:00:00', 'Value': 2.34}, ...]
    df = pd.DataFrame(data)
    if df.empty or "Date" not in df or "Value" not in df:
        return pd.Series(dtype=float)
    s = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    out = pd.Series(df["Value"].astype(float).values, index=s).sort_index().dropna()
    return out
