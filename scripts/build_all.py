from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def run_step(module: str) -> None:
    print(f"▶ {module}")
    ret = subprocess.call(
        [sys.executable, "-m", module],
        cwd=ROOT,
    )
    if ret != 0:
        sys.exit(ret)


def main() -> None:
    steps = [
        "scripts.createdata",         # secteurs actions
        "scripts.createdata_macro",   # macro dashboard
        "scripts.createdata_rates",   # taux
        "scripts.createdata_credit",  # crédit
        "scripts.createvisu",         # visuel secteurs
        "scripts.createvisu_macro",   # visuel macro
        "scripts.createvisu_rates",   # visuel taux
        "scripts.createvisu_credit",  # visuel crédit
    ]

    for mod in steps:
        run_step(mod)

    print("✅ Build complet : CSV dans data/, images dans output/")


if __name__ == "__main__":
    main()
