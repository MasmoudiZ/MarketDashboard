from __future__ import annotations
from pathlib import Path
import os, yaml

_DEFAULTS = {
    "cache_dir": "data",
    "output_dir": "output",
    "te_api_key": os.getenv("TE_API_KEY", ""),  # optionnel, peut rester vide
}

def load_config(path: str | Path = "config.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        return dict(_DEFAULTS)
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return {**_DEFAULTS, **cfg}
