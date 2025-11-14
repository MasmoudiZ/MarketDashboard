import subprocess
import sys

def run(cmd):
    print(f">>> {cmd}")
    ret = subprocess.call(cmd, shell=True)
    if ret != 0:
        sys.exit(ret)

if __name__ == "__main__":
    run("python -m scripts.clean")
    run("python -m scripts.build_all")
    print("✅ Done. CSV dans data/, PNG dans output/")
