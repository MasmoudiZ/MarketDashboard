from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DATA = Path("data") / "macro_dashboard.csv"
OUT  = Path("output"); OUT.mkdir(exist_ok=True, parents=True)

def cell_bg(fig, x, y, w, h, color):
    ax = fig.add_axes([x, y, w, h]); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=color, transform=ax.transAxes, zorder=-1))
    return ax

def pct_box(fig, x, y, w, h, v):
    ax = fig.add_axes([x, y, w, h]); ax.axis("off")
    col = "#2ca02c" if (pd.notna(v) and v >= 0) else "#d62728"
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, color=col, transform=ax.transAxes))
    ax.text(0.5, 0.5, f"{v:+.2f}%" if pd.notna(v) else "—", va="center", ha="center", color="white", fontsize=8)
    return ax

def draw_panel(fig, df, groups, x0):
    y = 0.88
    for g in groups:
        cell_bg(fig, x0, y, 0.44, 0.05, "#123a5a").text(0.01, 0.5, g, va="center", ha="left",
                                                       color="white", fontsize=10, fontweight="bold")
        cell_bg(fig, x0, y-0.04, 0.44, 0.04, "#e9edf5")
        cell_bg(fig, x0+0.01, y-0.04, 0.22, 0.04, "none").text(0, 0.5, "Libellé", va="center")
        cell_bg(fig, x0+0.23, y-0.04, 0.07, 0.04, "none").text(0.5, 0.5, "Niveau", va="center", ha="center")
        cell_bg(fig, x0+0.30, y-0.04, 0.07, 0.04, "none").text(0.5, 0.5, "LastWeek", va="center", ha="center")
        cell_bg(fig, x0+0.37, y-0.04, 0.07, 0.04, "none").text(0.5, 0.5, "PerfYtd", va="center", ha="center")

        y -= 0.08
        grp = df[df["Groupe"] == g].reset_index(drop=True)
        for i, r in grp.iterrows():
            bg = "#f7f9fc" if i % 2 == 0 else "#eef2f7"
            cell_bg(fig, x0, y, 0.44, 0.045, bg)
            cell_bg(fig, x0+0.01, y, 0.22, 0.045, "none").text(0, 0.5, r["Libellé"], va="center")
            lvl = f"{r['Niveau']:.0f}" if pd.notna(r["Niveau"]) else "—"
            cell_bg(fig, x0+0.23, y, 0.07, 0.045, "none").text(0.5, 0.5, lvl, va="center", ha="center", fontsize=8)
            pct_box(fig, x0+0.30, y, 0.07, 0.045, r["LastWeek"])
            pct_box(fig, x0+0.37, y, 0.07, 0.045, r["PerfYTD"])
            y -= 0.05
        y -= 0.02

def main():
    df = pd.read_csv(DATA)
    left_groups  = ["Actions Monde", "Actions États-Unis", "Actions Europe", "Actions Asie / Emergents"]
    right_groups = ["Obligations", "Taux", "Changes", "Matières 1ères"]

    fig = plt.figure(figsize=(12, 6)); fig.patch.set_facecolor("white")
    draw_panel(fig, df, left_groups, 0.05)
    draw_panel(fig, df, right_groups, 0.51)

    out = OUT / "macro_dashboard_legacy_style.png"
    fig.savefig(out, dpi=150, bbox_inches="tight"); plt.close(fig)
    print(f"Saved {out}")

if __name__ == "__main__":
    main()
