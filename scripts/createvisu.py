from __future__ import annotations
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import yfinance as yf

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ================== STYLE — IDENTIQUE À L'ANCIEN ==================
FIG_PX_W, FIG_PX_H, DPI = 1030, 465, 100
FIG_W, FIG_H = FIG_PX_W / DPI, FIG_PX_H / DPI

COLOR_HEADER = "#0A3D6E"
COLOR_HDRROW = "#0A3D6E"
COLOR_CELL_A = "#EEF1F5"
COLOR_CELL_B = "#FFFFFF"
COLOR_BAR_BG = "#E6E6E6"
COLOR_BAR_POS = "#00B050"
COLOR_BAR_NEG = "#C00000"
COLOR_TEXT = (0.12, 0.12, 0.12)

TITLE_H = 28
HEADER_H = 28
ROW_H = 24
GUTTER_X = 24
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 20, 20, 14, 14

CAP_5D = 5.0
CAP_1M = 6.0
CAP_3M = 15.0
CAP_YTD = 50.0

try:
    plt.rcParams["font.family"] = "Roboto"
except Exception:
    plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

# ================== UNIVERS — SECTEURS (proxies) ==================
SP500_SECTORS: Dict[str, str] = {
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

STOXX600_SECTORS: Dict[str, str] = {
    "Banks": "EXV1.DE",
    "Utilities": "EXH7.DE",
    "Indus Gd&Srv": "EXH1.DE",
    "Energy": "EXV9.DE",
    "Insurance": "EXH9.DE",
    "Constru": "EXI1.DE",
    "Basic ressources": "EXH5.DE",
    "Telco": "EXV3.DE",
    "Technology": "EXV2.DE",
    "Retail": "EXH3.DE",
    "Finanserv": "EXH9.DE",
    "F&B": "EXH4.DE",
    "Personal Care and goods": "EXH6.DE",
    "Immo": "IQQR.DE",
    "Healthcare": "EXV4.DE",
    "Travel & Leisure": "EXV5.DE",
    "Consumer Discretionary": "EXH2.DE",
    "Chimie": "EXH7.DE",
    "Auto": "EXV6.DE",
    "Media": "EXH8.DE",
}

# ================== AIDES ==================
def last_business_day(dt: datetime) -> datetime:
    while dt.weekday() >= 5:
        dt -= timedelta(days=1)
    return dt

def _load_price_series(ticker: str, start: datetime, end: datetime) -> pd.Series:
    """Télécharge une série quotidienne robuste (gère Adj Close / Close)."""
    df = yf.download(
        ticker,
        start=start.strftime("%Y-%m-%d"),
        end=(end + timedelta(days=1)).strftime("%Y-%m-%d"),
        progress=False,
        auto_adjust=False,
        group_by="column",
        interval="1d",
    )
    if df is None or df.empty:
        return pd.Series(dtype=float)

    if "Adj Close" in df:
        s = df["Adj Close"].dropna()
    elif "Close" in df:
        s = df["Close"].dropna()
    else:
        # dernier recours : 1ère colonne numérique
        s = None
        for c in df.columns:
            ser = pd.to_numeric(df[c], errors="coerce").dropna()
            if not ser.empty:
                s = ser
                break
        if s is None:
            return pd.Series(dtype=float)

    s.index = pd.to_datetime(s.index).tz_localize(None)
    return s.astype(float)

def _perf_pct(series: pd.Series, ref_date: datetime) -> float:
    """Perf % vs dernier point <= ref_date."""
    s = series.dropna()
    if s.empty:
        return np.nan
    s_ref = s.loc[:ref_date]
    if s_ref.empty:
        return np.nan
    p0 = float(s_ref.iloc[-1])
    p1 = float(s.iloc[-1])
    if p0 == 0:
        return np.nan
    return (p1 / p0 - 1.0) * 100.0

def compute_rows(universe: Dict[str, str], keep_order: bool = True) -> List[Tuple[str, float, float, float, float]]:
    today = last_business_day(datetime.now())
    d_5d = today - timedelta(days=7)
    d_1m = today - relativedelta(months=1)
    d_3m = today - relativedelta(months=3)
    y0 = last_business_day(datetime(today.year - 1, 12, 31))
    start = min(d_3m, y0) - timedelta(days=10)

    out = []
    for name, ticker in universe.items():
        s = _load_price_series(ticker, start, today)
        if s.empty:
            out.append((name, np.nan, np.nan, np.nan, np.nan))
            continue
        p5d = _perf_pct(s, d_5d)
        p1m = _perf_pct(s, d_1m)
        p3m = _perf_pct(s, d_3m)
        pytd = _perf_pct(s, y0)
        out.append((name, p5d, p1m, p3m, pytd))

    return out

# ================== RENDU (COPIE VISUELLE) ==================
def _draw_gauge(ax, x, y, w, h, value, cap):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=COLOR_BAR_BG, edgecolor='white', lw=0.5))
    if value is not None and not np.isnan(value) and cap > 0:
        fill = min(abs(value) / cap, 1.0) * w
        if fill > 0:
            ax.add_patch(Rectangle(
                (x, y), fill, h,
                facecolor=(COLOR_BAR_POS if value >= 0 else COLOR_BAR_NEG),
                edgecolor='none'
            ))
        ax.text(x + w - 2, y + h / 2, f"{value:+.2f}%", ha="right", va="center", fontsize=8, color=COLOR_TEXT)
    else:
        ax.text(x + w / 2, y + h / 2, "—", ha="center", va="center", fontsize=8, color=COLOR_TEXT)

def draw_panel_legacy(ax, x, y, w, title: str, rows: List[Tuple[str, float, float, float, float]]):
    ax.add_patch(Rectangle((x, y), w, TITLE_H, facecolor=COLOR_HEADER, edgecolor='none'))
    ax.text(x + 10, y + TITLE_H / 2, title, va="center", ha="left", color="white", fontsize=11, weight="bold")
    
    col_w = [int(0.46 * w), int(0.18 * w), int(0.18 * w), int(0.18 * w), w - int(0.46 * w) - 3 * int(0.18 * w)]
    headers = ["Secteur", "Perf 5D", "1M", "3M", "Perf YTD"]
    
    ax.add_patch(Rectangle((x, y + TITLE_H), w, HEADER_H, facecolor=COLOR_HDRROW, edgecolor='none'))
    tx = x
    for i, cw in enumerate(col_w):
        ax.text(tx + 6, y + TITLE_H + HEADER_H / 2, headers[i], va="center", ha="left", color="white", fontsize=9, weight="bold")
        tx += cw

    ry = y + TITLE_H + HEADER_H
    for i, (name, p5d, p1m, p3m, pytd) in enumerate(rows):
        bg = COLOR_CELL_A if (i % 2 == 0) else COLOR_CELL_B
        ax.add_patch(Rectangle((x, ry), w, ROW_H, facecolor=bg, edgecolor='white', lw=0.5))
        ax.text(x + 6, ry + ROW_H / 2, name, va="center", ha="left", color=COLOR_TEXT, fontsize=9)

        gx = x + col_w[0]
        bar_h = ROW_H - 8
        _draw_gauge(ax, gx + 6, ry + 4, col_w[1] - 12, bar_h, p5d, CAP_5D)
        gx += col_w[1]
        _draw_gauge(ax, gx + 6, ry + 4, col_w[2] - 12, bar_h, p1m, CAP_1M)
        gx += col_w[2]
        _draw_gauge(ax, gx + 6, ry + 4, col_w[3] - 12, bar_h, p3m, CAP_3M)
        gx += col_w[3]
        _draw_gauge(ax, gx + 6, ry + 4, col_w[4] - 12, bar_h, pytd, CAP_YTD)
        
        ry += ROW_H

    return TITLE_H + HEADER_H + len(rows) * ROW_H

def build_legacy_two_panels(
    left_title: str = "SP 500",
    left_universe: Dict[str, str] = SP500_SECTORS,
    right_title: str = "Stoxx 600",
    right_universe: Dict[str, str] = STOXX600_SECTORS,
    outfile: str = "sectors_2panels_legacy_style.png"
):
    left_rows = compute_rows(left_universe, keep_order=True)
    right_rows = compute_rows(right_universe, keep_order=True)

    fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
    ax = plt.axes([0, 0, 1, 1]); ax.axis("off")
    ax.set_xlim(0, FIG_PX_W); ax.set_ylim(0, FIG_PX_H); ax.invert_yaxis()

    panel_w = (FIG_PX_W - MARGIN_L - MARGIN_R - GUTTER_X) / 2
    xL = MARGIN_L
    xR = MARGIN_L + panel_w + GUTTER_X
    y = MARGIN_T

    _ = draw_panel_legacy(ax, xL, y, panel_w, left_title, left_rows)
    _ = draw_panel_legacy(ax, xR, y, panel_w, right_title, right_rows)

    out_path = OUTPUT_DIR / outfile
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


# ================== MAIN ==================
if __name__ == "__main__":
    build_legacy_two_panels()
