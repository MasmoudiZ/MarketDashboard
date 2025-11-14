from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

START_PLOT = pd.Timestamp("2020-10-01")
CREDIT_COLOR = "#d79b00"

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_credit_df() -> pd.DataFrame:
    csv_path = DATA_DIR / "credit_dashboard.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} introuvable. Lance d'abord : python -m scripts.createdata_credit"
        )

    df = pd.read_csv(csv_path, parse_dates=["date"], index_col="date")
    df = df.loc[df.index >= START_PLOT]
    # 🔁 hebdo : un point par semaine (vendredi)
    df_w = df.resample("W-FRI").last().dropna(how="all")
    return df_w


def save_fig(fig: plt.Figure, filename: str) -> None:
    out_path = OUTPUT_DIR / filename
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


# --- Graphiques ---
def plot_eur_hy(ax: plt.Axes, df: pd.DataFrame) -> None:
    ax.plot(df.index, df["EU_HY_OAS"], color=CREDIT_COLOR, linewidth=2)
    ax.set_ylabel("bps")
    ax.set_title("iTraxx Europe HY")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.6)


def plot_us_hy(ax: plt.Axes, df: pd.DataFrame) -> None:
    ax.plot(df.index, df["US_HY_OAS"], color=CREDIT_COLOR, linewidth=2)
    ax.set_ylabel("bps")
    ax.set_title("CDX US High Yield")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.6)


def plot_us_ig(ax: plt.Axes, df: pd.DataFrame) -> None:
    ax.plot(df.index, df["US_IG_OAS"], color=CREDIT_COLOR, linewidth=2)
    ax.set_ylabel("bps")
    ax.set_title("CDX US Investment Grade")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.6)


def plot_em_hy(ax: plt.Axes, df: pd.DataFrame) -> None:
    ax.plot(df.index, df["EM_HY_OAS"], color=CREDIT_COLOR, linewidth=2)
    ax.set_ylabel("bps")
    ax.set_title("EM HY OAS")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.6)


def main() -> None:
    df_m = load_credit_df()

    # 1) iTraxx Europe HY
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    plot_eur_hy(ax1, df_m)
    save_fig(fig1, "credit_eur_hy.png")

    # 2) CDX US HY
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    plot_us_hy(ax2, df_m)
    save_fig(fig2, "credit_us_hy.png")

    # 3) CDX US IG
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    plot_us_ig(ax3, df_m)
    save_fig(fig3, "credit_us_ig.png")

    # 4) EM HY OAS
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    plot_em_hy(ax4, df_m)
    save_fig(fig4, "credit_em_hy.png")

    # 5) Dashboard 2x2
    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    ax_tl, ax_tr = axes[0]
    ax_bl, ax_br = axes[1]

    plot_eur_hy(ax_tl, df_m)
    plot_us_hy(ax_tr, df_m)
    plot_us_ig(ax_bl, df_m)
    plot_em_hy(ax_br, df_m)

    fig.tight_layout()
    save_fig(fig, "credit_dashboard_fred.png")


if __name__ == "__main__":
    main()
