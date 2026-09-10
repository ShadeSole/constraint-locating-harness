
from __future__ import annotations
import json, csv
from pathlib import Path
from typing import Dict, List, Tuple
from .core import Forbidden, Interaction, Config

def load_model(path: str):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    parameters = data["parameters"]
    forbidden = [Forbidden.from_dict(x) for x in data.get("forbidden", [])]
    return parameters, forbidden

def interaction_from_text(items: List[str]) -> Interaction:
    pairs = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"Expected PARAM=VALUE, got {item!r}")
        k, v = item.split("=", 1)
        pairs.append((k, v))
    return frozenset(pairs)

def write_suite_csv(path: str, suite: List[Config]) -> None:
    if not suite:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(suite[0].keys()))
        w.writeheader()
        w.writerows(suite)
