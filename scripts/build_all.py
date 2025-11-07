import sys
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = [
    "scripts/createdata.py",
    "scripts/createdata_macro.py",
    "scripts/createvisu.py",
    "scripts/createvisu_macro.py",
]

def run(cmd):
    print(f"▶ {cmd}")
    res = subprocess.run([sys.executable, "-m", cmd.replace("/", ".").replace(".py","")])
    if res.returncode != 0:
        sys.exit(res.returncode)

if __name__ == "__main__":
    # crée les dossiers si absents
    (ROOT/"data").mkdir(exist_ok=True)
    (ROOT/"output").mkdir(exist_ok=True)
    for s in SCRIPTS:
        run(s)
    print("✅ Build complet : CSV dans data/, images dans output/")
