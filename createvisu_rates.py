from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

US_COLOR = "#d79b00"
DE_COLOR = "#003f6f"

START_PLOT = pd.Timestamp("2020-10-01")

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_rates_df() -> pd.DataFrame:
    csv_path = DATA_DIR / "rates_fred.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} introuvable. Lance d'abord : python -m scripts.createdata_rates"
        )

    df = pd.read_csv(csv_path, parse_dates=["date"], index_col="date")
    # filtre sur la période voulue
    df = df.loc[df.index >= START_PLOT]
    # 🔁 on passe en hebdo : un point par semaine (vendredi)
    df_w = df.resample("W-FRI").last().dropna(how="all")
    return df_w



def save_fig(fig: plt.Figure, filename: str) -> None:
    out_path = OUTPUT_DIR / filename
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


def plot_yield_curve(ax: plt.Axes, last_row: pd.Series) -> None:
    tenor_cols = [
        ("US_1M", "1M"), ("US_3M", "3M"), ("US_6M", "6M"),
        ("US_1Y", "1Y"), ("US_2Y", "2Y"), ("US_3Y", "3Y"),
        ("US_5Y", "5Y"), ("US_7Y", "7Y"), ("US_10Y", "10Y"),
        ("US_20Y", "20Y"), ("US_30Y", "30Y")
    ]

    xs, us_y = [], []
    for col, label in tenor_cols:
        if col in last_row.index and pd.notna(last_row[col]):
            xs.append(label)
            us_y.append(last_row[col])

    ax.plot(xs, us_y, marker="s", linewidth=2, color=US_COLOR, label="Taux US")

    if "Bund_10Y" in last_row.index and pd.notna(last_row["Bund_10Y"]):
        de_y = [last_row["Bund_10Y"]] * len(xs)
        ax.plot(xs, de_y, marker="s", linewidth=2, color=DE_COLOR, label="Taux Allemands")

    ax.set_ylabel("%")
    ax.set_title("Courbe des taux")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)


def plot_10y(ax: plt.Axes, df: pd.DataFrame) -> None:
    ax.plot(df.index, df["US_10Y"], color=US_COLOR, linewidth=2, label="Taux US 10 ans")
    ax.plot(df.index, df["Bund_10Y"], color=DE_COLOR, linewidth=2, label="Taux Allemand 10 ans")
    ax.set_ylabel("%")
    ax.set_title("Taux 10 ans")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.6)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False)


def plot_spread_de(ax: plt.Axes, df: pd.DataFrame) -> None:
    spread = (df["OAT_10Y"] - df["Bund_10Y"]) * 100.0
    ax.plot(spread.index, spread, color=DE_COLOR, linewidth=2)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("bps")
    ax.set_title("Taux 2-10Y ALLEMAND")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.6)


def plot_spread_us(ax: plt.Axes, df: pd.DataFrame) -> None:
    spread = (df["US_10Y"] - df["US_2Y"]) * 100.0
    ax.plot(spread.index, spread, color=US_COLOR, linewidth=2)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("bps")
    ax.set_title("Taux 2-10Y US")
    ax.grid(True, axis="y", linewidth=0.5, alpha=0.6)


def main() -> None:
    df_m = load_rates_df()
    last_row = df_m.iloc[-1]

    # 1) Courbe
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    plot_yield_curve(ax1, last_row)
    save_fig(fig1, "rates_curve.png")

    # 2) 10 ans
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    plot_10y(ax2, df_m)
    save_fig(fig2, "rates_10y.png")

    # 3) Spread allemand
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    plot_spread_de(ax3, df_m)
    save_fig(fig3, "rates_spread_de_2_10.png")

    # 4) Spread US
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    plot_spread_us(ax4, df_m)
    save_fig(fig4, "rates_spread_us_2_10.png")

    # 5) Dashboard global
    fig, axes = plt.subplots(2, 2, figsize=(12, 7))
    ax_curve, ax_de = axes[0]
    ax_10y, ax_us = axes[1]

    plot_yield_curve(ax_curve, last_row)
    plot_spread_de(ax_de, df_m)
    plot_10y(ax_10y, df_m)
    plot_spread_us(ax_us, df_m)

    fig.tight_layout()
    save_fig(fig, "rates_dashboard_fred.png")


if __name__ == "__main__":
    main()
