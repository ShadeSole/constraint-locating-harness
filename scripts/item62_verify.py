"""Plan item 62: check a saved suite at strength t (cover: valid and 0 uncovered; locate: also 0 avoidable collisions).
Usage: PYTHONPATH=. python3 scripts/item62_verify.py BENCH_DIR SUITE.json STRENGTH
JSON models are checked by full enumeration (core.valid_configurations, annealing.suite_cost), sharing no code with the
Z3 search. CASA models are too large to enumerate and are checked with solver.Z3CostModel (the per-interaction loop
cost), a different code path from the FastZ3CostModel used by the search; validity is a plain rule check."""
import json, sys
from cla_harness.io import load_casa_model, load_model
from cla_harness.core import is_valid, valid_configurations, feasible_interactions
bench, path, t = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = json.load(open(path)); name, suite, mode = d["model"], d["suite"], d["mode"]
if name.endswith(".json"):
    params, forb = load_model(f"{bench}/{name}")
    from cla_harness.annealing import suite_cost, unavoidable_pairs
    configs = valid_configurations(params, forb)
    inter = feasible_interactions(configs, t)
    cost = suite_cost(suite, inter, set() if mode == "cover" else unavoidable_pairs(configs, inter))
    method = "enumeration"
else:
    params, forb = load_casa_model(f"{bench}/{name}.model", f"{bench}/{name}.constraints")
    from cla_harness.solver import Z3CostModel
    cost = Z3CostModel(params, forb, cover_only=(mode == "cover"), strength=t).suite_cost(suite)
    method = "Z3CostModel"
valid = all(set(c) == set(params) and all(c[p] in params[p] for p in params) and is_valid(c, forb) for c in suite)
uncovered = cost["uncovered"]
avoid = 0 if mode == "cover" else cost["avoidable_collisions"]
print(json.dumps({"model": name, "mode": mode, "seed": d["seed"], "strength": t, "size": len(suite), "method": method,
                  "valid": valid, "uncovered": uncovered, "avoidable_collisions": avoid,
                  "ok": valid and uncovered == 0 and avoid == 0}))
