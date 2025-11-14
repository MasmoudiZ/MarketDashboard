from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
to_remove = list((ROOT/"data").glob("*.csv")) + list((ROOT/"output").glob("*.png"))

for f in to_remove:
    try:
        f.unlink()
        print(f"🧹 removed {f}")
    except Exception as e:
        print(f"skip {f}: {e}")

print("🧹 Clean done.")
