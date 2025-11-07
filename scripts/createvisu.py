from __future__ import annotations
from pathlib import Path
from marketdash.config import load_config
from marketdash.visuals import plot_sector_panels

def main():
    cfg = load_config()
    data_file = Path(cfg["cache_dir"]) / "sector_data.csv"
    out_file  = Path(cfg["output_dir"]) / "sectors_2panels_legacy_style.png"
    plot_sector_panels(str(data_file), output=str(out_file))

if __name__ == "__main__":
    main()

