from __future__ import annotations

from pathlib import Path
from typing import Tuple, List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ======================================================================
#  Chemins
# ======================================================================

def get_paths() -> Tuple[Path, Path]:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    output_dir = root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return data_dir, output_dir


# ======================================================================
#  STYLE EXACT LEGACY
# ======================================================================

DPI = 100

COLOR_BLUE   = "#213A63"
COLOR_HDR    = "#213A63"
COLOR_ROW_A  = "#EFF2F7"     # couleur legacy
COLOR_ROW_B  = "#FFFFFF"
COLOR_BAR_BG = "#E6E6E6"
COLOR_POS    = "#00B050"
COLOR_NEG    = "#C00000"
COLOR_TEXT   = "#1E1E1E"

MARGIN_L, MARGIN_R = 25, 15
MARGIN_T, MARGIN_B = 10, 12
GUTTER_COL = 40
BLOCK_V_SPACING = 6

CAT_W = 120
HDR_H = 24
ROW_H = 18

COL_W = 410

# Police
try:
    plt.rcParams["font.family"] = "Roboto"
except:
    plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9
plt.rcParams["axes.unicode_minus"] = False


# ======================================================================
#  Formatage
# ======================================================================

def fmt_level(x: float) -> str:
    if pd.isna(x):
        return ""
    return f"{x:,.0f}".replace(",", " ")


def fmt_pct(x: float) -> str:
    if pd.isna(x):
        return ""
    return f"{x:+.2f}%"


def block_height(n_rows: int) -> int:
    return HDR_H + ROW_H * n_rows + BLOCK_V_SPACING


# ======================================================================
#   Bloc
# ======================================================================

def draw_macro_block(
    ax,
    x0, y0,
    width,
    group_name,
    df_block,
    max_abs_ytd
):

    df_block = df_block.reset_index(drop=True)
    n_rows = len(df_block) or 2

    table_w = width - CAT_W
    x_table = x0 + CAT_W

    # -------- Catégorie --------
    cat_h = HDR_H + ROW_H * n_rows
    ax.add_patch(Rectangle((x0, y0), CAT_W, cat_h, facecolor=COLOR_BLUE))

    ax.text(
        x0 + 12,
        y0 + cat_h / 2,   # ajustement vertical fin
        group_name,
        ha="left",
        va="center",
        color="white",
        weight="bold",
        wrap=True,
    )

    # -------- Header --------
    ax.add_patch(Rectangle((x_table, y0), table_w, HDR_H, facecolor=COLOR_HDR))

    col_label_w = 0.46 * table_w
    col_level_w = 0.20 * table_w
    col_last_w  = 0.16 * table_w
    col_ytd_w   = table_w - col_label_w - col_level_w - col_last_w

    x_label = x_table
    x_level = x_label + col_label_w
    x_last  = x_level + col_level_w
    x_ytd   = x_last + col_last_w

    # Header text (remonté de 2 px)
    header_y = y0 + HDR_H / 2 + 2

    ax.text(x_label + 4, header_y, "Indice",
            ha="left", va="center", color="white", weight="bold")
    ax.text(x_level + col_level_w/2, header_y, "Niveau",
            ha="center", va="center", color="white", weight="bold")
    ax.text(x_last + col_last_w/2, header_y, "Last Week",
            ha="center", va="center", color="white", weight="bold")
    ax.text(x_ytd + col_ytd_w/2, header_y, "Perf Ytd",
            ha="center", va="center", color="white", weight="bold")

    # -------- Lignes --------
    for i, row in df_block.iterrows():
        y_row = y0 + HDR_H + i * ROW_H + 2   # micro-ajustement bas

        bg = COLOR_ROW_A if i % 2 == 0 else COLOR_ROW_B
        ax.add_patch(Rectangle((x_table, y_row), table_w, ROW_H, facecolor=bg))

        label = str(row["Libellé"])
        level = row["Niveau"]
        lastw = row["LastWeek"]
        ytd = row["PerfYTD"]

        # Libellé
        ax.text(x_label + 4, y_row + ROW_H/2,
                label, ha="left", va="center", color=COLOR_TEXT)

        # Niveau
        ax.text(x_level + col_level_w - 4, y_row + ROW_H/2,
                fmt_level(level), ha="right", va="center", color=COLOR_TEXT)

        # LastWeek (barre fine + offset)
        bar_w = 6
        bar_h = ROW_H - 10
        bar_x = x_last + 6
        bar_y = y_row + (ROW_H - bar_h)/2

        if not pd.isna(lastw):
            col = COLOR_POS if lastw >= 0 else COLOR_NEG
            ax.add_patch(Rectangle((bar_x, bar_y), bar_w, bar_h, facecolor=col))
            ax.text(x_last + col_last_w - 6, y_row + ROW_H/2,   # -6 px
                    fmt_pct(lastw), ha="right", va="center", color=col)

        # Perf YTD (jauge fine)
        gauge_margin = 5
        gauge_h = ROW_H - 9
        gx = x_ytd + gauge_margin
        gy = y_row + (ROW_H - gauge_h)/2
        gauge_w = col_ytd_w - gauge_margin*2 - 38

        ax.add_patch(Rectangle((gx, gy), gauge_w, gauge_h, facecolor=COLOR_BAR_BG))

        if not pd.isna(ytd) and max_abs_ytd > 0:
            frac = min(abs(ytd) / max_abs_ytd, 1.0)
            fill_w = gauge_w * frac
            col = COLOR_POS if ytd >= 0 else COLOR_NEG
            ax.add_patch(Rectangle((gx, gy), fill_w, gauge_h, facecolor=col))

        ax.text(x_ytd + col_ytd_w - 4, y_row + ROW_H/2,
                fmt_pct(ytd), ha="right", va="center", color=COLOR_TEXT)

    return block_height(n_rows)


# ======================================================================
# MAIN
# ======================================================================

def main():
    data_dir, output_dir = get_paths()
    df = pd.read_csv(data_dir / "macro_dashboard.csv")

    for col in ("Niveau", "LastWeek", "PerfYTD"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    max_abs_ytd = df["PerfYTD"].abs().max()

    left = ["Actions Monde","Actions Etats-Unis",
            "Actions Europe","Actions Asie / Emergents"]
    right = ["Obligations","Taux","Changes","Matières 1ères"]

    def col_height(groups):
        h = 0
        for g in groups:
            n = len(df[df["Groupe"] == g]) or 2
            h += block_height(n)
        return h

    total_h = max(col_height(left), col_height(right)) + MARGIN_T + MARGIN_B
    total_w = MARGIN_L + COL_W + GUTTER_COL + COL_W + MARGIN_R

    fig = plt.figure(figsize=(total_w/DPI, total_h/DPI), dpi=DPI)
    ax = fig.add_axes([0,0,1,1])
    ax.set_xlim(0, total_w)
    ax.set_ylim(0, total_h)
    ax.invert_yaxis()
    ax.axis("off")

    # Gauche
    y = MARGIN_T
    for g in left:
        block_df = df[df["Groupe"] == g].copy()
        h = draw_macro_block(ax, MARGIN_L, y, COL_W, g, block_df, max_abs_ytd)
        y += h

    # Droite
    x_right = MARGIN_L + COL_W + GUTTER_COL
    y = MARGIN_T
    for g in right:
        block_df = df[df["Groupe"] == g].copy()
        h = draw_macro_block(ax, x_right, y, COL_W, g, block_df, max_abs_ytd)
        y += h

    out = output_dir / "macro_dashboard_legacy_strategy.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
