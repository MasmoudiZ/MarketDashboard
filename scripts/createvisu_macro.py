# scripts/createvisu_macro.py

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "macro_dashboard.csv"
OUTPUT_PATH = ROOT / "output" / "macro_dashboard_legacy_style.png"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def perf_color(x: float) -> str:
    if pd.isna(x):
        return "#CCCCCC"
    return "#008000" if x >= 0 else "#B00020"  # vert / rouge


def format_pct(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "—"
    return f"{x:+.2f}%"


def format_level(x: float | None) -> str:
    if x is None or pd.isna(x):
        return "—"
    # nombre avec séparateur de milliers et 2 décimales
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")


def draw_block(
    ax: plt.Axes,
    df_block: pd.DataFrame,
    title: str,
    max_abs_ytd: float,
) -> None:
    """
    Dessine un bloc style tableau :
    Libellé | Niveau | LastWeek | PerfYTD (jauge horizontale partant de la gauche)
    """
    ax.set_axis_off()

    n = len(df_block)
    top = 0.9
    row_h = 0.8 / (n + 1)  # un peu de marge en bas
    x_label = 0.02
    x_level = 0.42
    x_last = 0.60
    x_bar_left = 0.72
    x_bar_right = 0.97

    # Header
    ax.text(
        0.0,
        0.98,
        title,
        fontsize=12,
        fontweight="bold",
        ha="left",
        va="top",
        color="white",
        bbox=dict(
            boxstyle="round,pad=0.25",
            facecolor="#00508A",
            edgecolor="#00508A",
        ),
    )

    # En-têtes de colonnes
    y_head = top
    ax.text(x_label, y_head, "Libellé", fontsize=8, fontweight="bold", va="bottom")
    ax.text(x_level, y_head, "Niveau", fontsize=8, fontweight="bold", va="bottom")
    ax.text(x_last,  y_head, "LastWeek", fontsize=8, fontweight="bold", va="bottom")
    ax.text(
        (x_bar_left + x_bar_right) / 2,
        y_head,
        "PerfYTD",
        fontsize=8,
        fontweight="bold",
        va="bottom",
        ha="center",
    )

    # Lignes
    for i, (_, row) in enumerate(df_block.iterrows()):
        y = top - (i + 1) * row_h

        lvl = row.get("Niveau", np.nan)
        lw = row.get("LastWeek", np.nan)
        ytd = row.get("PerfYTD", np.nan)

        # texte
        ax.text(x_label, y, str(row["Libellé"]), fontsize=8, va="center")
        ax.text(x_level, y, format_level(lvl), fontsize=8, va="center", ha="right")
        ax.text(
            x_last,
            y,
            format_pct(lw),
            fontsize=8,
            va="center",
            ha="right",
            color=perf_color(lw),
        )

        # barre PerfYTD : toujours depuis la gauche
        bar_width_total = x_bar_right - x_bar_left
        if not pd.isna(ytd) and max_abs_ytd > 0:
            frac = min(abs(ytd) / max_abs_ytd, 1.0)
            filled_w = bar_width_total * frac
            color = perf_color(ytd)

            # fond neutre
            ax.add_patch(
                plt.Rectangle(
                    (x_bar_left, y - row_h * 0.35),
                    bar_width_total,
                    row_h * 0.7,
                    facecolor="#F2F2F2",
                    edgecolor="none",
                    transform=ax.transAxes,
                    zorder=0,
                )
            )

            # barre remplie, partant du bord gauche
            ax.add_patch(
                plt.Rectangle(
                    (x_bar_left, y - row_h * 0.35),
                    filled_w,
                    row_h * 0.7,
                    facecolor=color,
                    edgecolor="none",
                    transform=ax.transAxes,
                    zorder=1,
                )
            )

            # valeur en texte au centre
            ax.text(
                x_bar_left + bar_width_total / 2,
                y,
                format_pct(ytd),
                fontsize=8,
                va="center",
                ha="center",
                color="white" if abs(ytd) > max_abs_ytd * 0.25 else "black",
            )
        else:
            ax.text(
                x_bar_left + bar_width_total / 2,
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
            f"{DATA_PATH} introuvable. Lance d'abord : python -m scripts.createdata_macro"
        )

    df = pd.read_csv(DATA_PATH)

    # Harmonise le nom de la colonne de bloc
    if "block" in df.columns:
        block_col = "block"
    elif "Groupe" in df.columns:
        block_col = "Groupe"
    else:
        raise KeyError(
            f"Aucune colonne 'block' ou 'Groupe' trouvée dans {DATA_PATH}.\n"
            f"Colonnes dispo : {list(df.columns)}"
        )

    df = df.rename(columns={block_col: "block"})

    # S’assure que PerfYTD est bien numérique
    df["PerfYTD"] = pd.to_numeric(df["PerfYTD"], errors="coerce")
    max_abs_ytd = float(np.nanmax(np.abs(df["PerfYTD"]))) if df["PerfYTD"].notna().any() else 1.0

    # Ordre des blocs
    order = [
        "Actions Monde",
        "Actions États-Unis",
        "Actions Europe",
        "Actions Asie / Emergents",
        "Obligations",
        "Taux",
        "Changes",
        "Matières 1ères",
    ]

    fig, axes = plt.subplots(4, 2, figsize=(11, 8), dpi=150)
    axes = axes.ravel()

    for i, block_name in enumerate(order):
        ax = axes[i]
        sub = df[df["block"] == block_name].copy()
        if sub.empty:
            ax.set_axis_off()
            ax.text(0.5, 0.5, block_name, ha="center", va="center")
            continue
        draw_block(ax, sub, block_name, max_abs_ytd)

    # Si moins de 8 blocs, on coupe les axes restants
    for j in range(len(order), len(axes)):
        axes[j].set_axis_off()

    plt.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=150)
    plt.close(fig)
    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
