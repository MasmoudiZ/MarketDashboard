from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

COLOR_HEADER = "#0A3D6E"
COLOR_HDRROW = "#0A3D6E"
COLOR_CELL_A = "#EEF1F5"
COLOR_CELL_B = "#FFFFFF"
COLOR_BAR_BG = "#E6E6E6"
COLOR_BAR_POS = "#00B050"
COLOR_BAR_NEG = "#C00000"
COLOR_TEXT   = (0.12, 0.12, 0.12)

FIG_PX_W, FIG_PX_H = 1082, 560
DPI = 100
FIG_W, FIG_H = FIG_PX_W / DPI, FIG_PX_H / DPI
TITLE_W   = 140
HEADER_H  = 28
ROW_H     = 28
LEFT_MARGIN, RIGHT_MARGIN = 18, 28
TOP_MARGIN,  BOTTOM_MARGIN = 14, 12
GUTTER = 34
COL_W = (FIG_PX_W - LEFT_MARGIN - RIGHT_MARGIN - GUTTER) // 2
LEFT_X  = LEFT_MARGIN
RIGHT_X = LEFT_MARGIN + COL_W + GUTTER

def _draw_panel(ax, title, rows, x, y, sec_w):
    sec_h = HEADER_H + len(rows)*ROW_H + 10
    # bande bleu titre
    ax.add_patch(Rectangle((x, y), sec_w, HEADER_H, facecolor=COLOR_HEADER, edgecolor='none'))
    ax.text(x+8, y+HEADER_H/2, title, color="white", weight="bold", va="center", fontsize=12)

    # en-têtes colonnes
    cx, cw = x, sec_w
    hdr_y = y + HEADER_H
    ax.add_patch(Rectangle((cx, hdr_y), cw, HEADER_H, facecolor=COLOR_HDRROW, edgecolor='none'))
    headers = ["Secteur", "Perf 5D", "1M", "3M", "Perf YTD"]
    col_w = [int(0.44*cw), int(0.14*cw), int(0.14*cw), int(0.14*cw), cw - int(0.44*cw) - 3*int(0.14*cw)]
    tx = cx
    for i, w in enumerate(headers):
        ax.text(tx+6, hdr_y + HEADER_H/2, w, va="center", ha="left", color="white", fontsize=9, weight="bold")
        tx += col_w[i]

    # lignes
    ry = hdr_y + HEADER_H
    for i, r in rows.iterrows():
        bg = COLOR_CELL_A if (i % 2 == 0) else COLOR_CELL_B
        ax.add_patch(Rectangle((cx, ry), cw, ROW_H, facecolor=bg, edgecolor='white', lw=0.5))
        # libellé
        ax.text(cx+6, ry + ROW_H/2, r["sector"], va="center", ha="left", color=COLOR_TEXT, fontsize=9)
        # valeurs + jauges
        vals = [r["perf_5d"], r["perf_1m"], r["perf_3m"]]
        gw = [col_w[1], col_w[2], col_w[3]]
        gx = [cx + col_w[0], cx + col_w[0] + col_w[1], cx + col_w[0] + col_w[1] + col_w[2]]
        cap = 8.0  # cap visuel ±8%
        for k,v in enumerate(vals):
            ax.add_patch(Rectangle((gx[k]+4, ry+4), gw[k]-8, ROW_H-8, facecolor=COLOR_BAR_BG, edgecolor='white', lw=0.5))
            if pd.notna(v):
                fill = min(abs(v)/cap, 1.0) * (gw[k]-8)
                if fill>0:
                    ax.add_patch(Rectangle((gx[k]+4, ry+4), fill, ROW_H-8,
                                           facecolor=(COLOR_BAR_POS if v>=0 else COLOR_BAR_NEG), edgecolor='none'))
                ax.text(gx[k]+gw[k]-6, ry+ROW_H/2, f"{v:+.2f}%", ha="right", va="center", fontsize=8, color=COLOR_TEXT)
            else:
                ax.text(gx[k]+gw[k]/2, ry+ROW_H/2, "—", ha="center", va="center", fontsize=8, color=COLOR_TEXT)
        # YTD texte
        ytd_txt = "—" if pd.isna(r["perf_ytd"]) else f"{r['perf_ytd']:+.2f}%"
        ax.text(cx + col_w[0] + col_w[1] + col_w[2] + col_w[3] + 6, ry+ROW_H/2, ytd_txt,
                va="center", ha="left", color=COLOR_TEXT, fontsize=9)
        ry += ROW_H

    return sec_h + 10

def plot_sector_panels(df_or_path, output="output/sectors_2panels_legacy_style.png"):
    df = pd.read_csv(df_or_path) if isinstance(df_or_path, (str, Path)) else df_or_path.copy()
    df = df.fillna(np.nan)

    left = df[df["universe"]=="SP 500"].reset_index(drop=True)
    right = df[df["universe"]=="Stoxx 600"].reset_index(drop=True)

    fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
    ax = plt.axes([0,0,1,1]); ax.axis("off")
    ax.set_xlim(0, FIG_PX_W); ax.set_ylim(0, FIG_PX_H); ax.invert_yaxis()

    yL = TOP_MARGIN
    _ = _draw_panel(ax, "SP 500", left,  LEFT_X, yL,  COL_W)
    yR = TOP_MARGIN
    _ = _draw_panel(ax, "Stoxx 600", right, RIGHT_X, yR, COL_W)

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {output}")
