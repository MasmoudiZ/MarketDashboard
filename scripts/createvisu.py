# scripts/createvisu.py

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sector_data.csv"
OUTPUT_PATH = ROOT / "output" / "sectors_2panels_legacy_style.png"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def perf_color(x: float) -> str:
    if pd.isna(x):
        return "#CCCCCC"
    return "#008000" if x >= 0 else "#B00020"


def format_pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{x:+.2f}%"


def draw_sector_panel(
    ax: plt.Axes,
    df_univ: pd.DataFrame,
    title: str,
    max_abs: dict[str, float],
) -> None:
    """
    Dessine un panneau secteurs avec jauges horizontales partant de la gauche
    pour Perf 5D, 1M, 3M et Perf YTD.
    """
    ax.set_axis_off()

    perf_cols = ["perf_5d", "perf_1m", "perf_3m", "perf_ytd"]
    col_titles = ["Perf 5D", "1M", "3M", "Perf YTD"]

    n = len(df_univ)
    top = 0.9
    row_h = 0.8 / (n + 1)

    x_label = 0.02
    # zones pour les jauges
    col_width = 0.22
    x_starts = [
        0.32,
        0.32 + col_width,
        0.32 + 2 * col_width,
        0.32 + 3 * col_width,
    ]
    x_bar_right = [x + col_width * 0.9 for x in x_starts]

    # Titre du bloc
    ax.text(
        0.0,
        0.98,
        title,
        fontsize=14,
        fontweight="bold",
        ha="left",
        va="top",
        color="white",
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="#00508A",
            edgecolor="#00508A",
        ),
    )

    # En-têtes colonnes
    y_head = top
    ax.text(x_label, y_head, "Sector", fontsize=9, fontweight="bold", va="bottom")
    for col_title, x0 in zip(col_titles, x_starts):
        ax.text(
            x0 + (x_bar_right[0] - x_starts[0]) / 2,
            y_head,
            col_title,
            fontsize=9,
            fontweight="bold",
            va="bottom",
            ha="center",
        )

    # Lignes
    for i, (_, row) in enumerate(df_univ.iterrows()):
        y = top - (i + 1) * row_h

        ax.text(x_label, y, str(row["sector"]), fontsize=9, va="center")

        for col_name, x_left, x_right in zip(perf_cols, x_starts, x_bar_right):
            val = row.get(col_name, np.nan)
            bar_total = x_right - x_left
            max_abs_val = max_abs[col_name] if max_abs[col_name] > 0 else 1.0

            # fond
            ax.add_patch(
                plt.Rectangle(
                    (x_left, y - row_h * 0.35),
                    bar_total,
                    row_h * 0.7,
                    facecolor="#F2F2F2",
                    edgecolor="none",
                    transform=ax.transAxes,
                    zorder=0,
                )
            )

            if not pd.isna(val):
                frac = min(abs(val) / max_abs_val, 1.0)
                filled = bar_total * frac
                color = perf_color(val)

                # barre remplie : part de la gauche
                ax.add_patch(
                    plt.Rectangle(
                        (x_left, y - row_h * 0.35),
                        filled,
                        row_h * 0.7,
                        facecolor=color,
                        edgecolor="none",
                        transform=ax.transAxes,
                        zorder=1,
                    )
                )

                txt_color = "white" if frac > 0.35 else "black"
                ax.text(
                    x_left + bar_total / 2,
                    y,
                    format_pct(val),
                    fontsize=8,
                    va="center",
                    ha="center",
                    color=txt_color,
                )
            else:
                ax.text(
                    x_left + bar_total / 2,
                    y,
                    "—",
                    fontsize=8,
                    va="center",
                    ha="center",
                    color="#777777",
                )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"{DATA_PATH} introuvable. Lance d'abord : python -m scripts.createdata"
        )

    df = pd.read_csv(DATA_PATH)

    # sécurité : on force les noms de colonnes attendus
    expected = {"universe", "sector", "level", "perf_5d", "perf_1m", "perf_3m", "perf_ytd"}
    missing = expected.difference(df.columns)
    if missing:
        raise KeyError(f"Colonnes manquantes dans {DATA_PATH}: {missing}")

    for col in ["perf_5d", "perf_1m", "perf_3m", "perf_ytd"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # max absolus par colonne pour l’échelle commune
    max_abs = {
        col: float(np.nanmax(np.abs(df[col]))) if df[col].notna().any() else 1.0
        for col in ["perf_5d", "perf_1m", "perf_3m", "perf_ytd"]
    }

    fig, axes = plt.subplots(1, 2, figsize=(13, 7), dpi=150)

    # SP 500
    univ1 = df[df["universe"] == "SP 500"].copy()
    draw_sector_panel(axes[0], univ1, "SP 500", max_abs)

    # Stoxx 600
    univ2 = df[df["universe"] == "Stoxx 600"].copy()
    draw_sector_panel(axes[1], univ2, "Stoxx 600", max_abs)

    plt.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150)
    plt.close(fig)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
