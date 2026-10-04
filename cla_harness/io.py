
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

def load_casa_model(model_path: str, constraints_path: str | None = None):
    """Load a model in the CASA file format used by the CCAG benchmark set.

    Returns (parameters, forbidden) in the same shape as load_model, so the
    rest of the harness is unchanged. Parameters are named P0, P1, ... and
    their values "0", "1", ... because the format carries no names.

    Model file:       strength t, number of parameters p, then p value counts.
    Constraints file: number of constraints c; then per constraint a literal
                      count k followed by k pairs "sign index". The index
                      numbers every (parameter, value) pair 0, 1, 2, ... in
                      parameter order. A clause "- a - b" means NOT(a AND b),
                      i.e. a forbidden partial assignment. Only "-" literals
                      are supported (all 35 CCAG benchmark files use only "-").

    A clause that names two different values of the same parameter can never
    be violated, so it adds no restriction and is skipped. The strength line
    is read for validation but not returned.
    """
    model_tokens = Path(model_path).read_text(encoding="utf-8").split()
    if len(model_tokens) < 2:
        raise ValueError("Model file is too short")
    num_params = int(model_tokens[1])
    counts = [int(x) for x in model_tokens[2:]]
    if len(counts) != num_params:
        raise ValueError(
            f"Model file declares {num_params} parameters but lists {len(counts)} value counts"
        )
    if any(c < 1 for c in counts):
        raise ValueError("Every parameter needs at least one value")

    names = [f"P{i}" for i in range(num_params)]
    parameters = {name: [str(v) for v in range(c)] for name, c in zip(names, counts)}

    # index -> (parameter name, value text)
    owner = []
    for name, c in zip(names, counts):
        owner.extend((name, str(v)) for v in range(c))

    if constraints_path is None:
        constraints_path = str(Path(model_path).with_suffix(".constraints"))
    tokens = Path(constraints_path).read_text(encoding="utf-8").split()
    forbidden: List[Forbidden] = []
    if not tokens:
        return parameters, forbidden

    num_constraints = int(tokens[0])
    pos = 1
    for _ in range(num_constraints):
        k = int(tokens[pos]); pos += 1
        terms = {}
        never_violated = False
        for _ in range(k):
            sign, index = tokens[pos], int(tokens[pos + 1]); pos += 2
            if sign != "-":
                raise ValueError(f"Unsupported literal sign {sign!r}; only '-' is supported")
            if not 0 <= index < len(owner):
                raise ValueError(f"Constraint index {index} is out of range 0..{len(owner) - 1}")
            name, value = owner[index]
            if terms.get(name, value) != value:
                never_violated = True
            terms[name] = value
        if not never_violated:
            forbidden.append(Forbidden.from_dict(terms))
    if pos != len(tokens):
        raise ValueError("Constraints file has unexpected extra content")
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
        
def write_results_csv(path: str, rows: List[dict], fieldnames: List[str]) -> None:
    """Write one row per experiment result. Creates the parent folder if needed."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)