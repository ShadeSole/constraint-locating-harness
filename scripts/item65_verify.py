"""Plan item 65: check a saved suite against the (dbar, t) condition, d = 1 or 2, sharing no code with
cla_harness.multifault (no bit masks; signatures are tuples of booleans and sets of test positions).
Usage: PYTHONPATH=. python3 scripts/item65_verify.py MODEL.json SUITE.json
Checks: every test assigns each parameter a listed value and breaks no forbidden rule; every feasible t-way
interaction is in some test; any two fault sets (1 to d distinct interactions) with the same suite signature have the
same signature over all valid configurations."""
import json, sys
from itertools import combinations
from cla_harness.io import load_model
from cla_harness.core import is_valid, valid_configurations, feasible_interactions
model_path, suite_path = sys.argv[1], sys.argv[2]
params, forb = load_model(model_path)
d_ = json.load(open(suite_path))
t, d, suite = d_["strength"], d_["d"], d_["suite"]
valid = all(set(c) == set(params) and all(c[p] in params[p] for p in params) and is_valid(c, forb) for c in suite)
configs = valid_configurations(params, forb)
inter = sorted(feasible_interactions(configs, t), key=sorted)
has = lambda c, i: all(c.get(p) == v for p, v in i)
full = {i: tuple(has(c, i) for c in configs) for i in inter}
mine = {i: frozenset(k for k, c in enumerate(suite) if has(c, i)) for i in inter}
uncovered = sum(1 for i in inter if not mine[i])
sets = [(i,) for i in inter] + (list(combinations(inter, 2)) if d == 2 else [])
by_suite = {}
for s in sets:
    sig = frozenset().union(*(mine[i] for i in s))
    fsig = tuple(any(col) for col in zip(*(full[i] for i in s)))
    by_suite.setdefault(sig, set()).add(fsig)
avoidable = sum(len(v) * (len(v) - 1) // 2 for v in by_suite.values())
print(json.dumps({"model": model_path.split("/")[-1], "strength": t, "d": d, "size": len(suite), "valid": valid,
                  "uncovered": uncovered, "unseparated_distinguishable_class_pairs": avoidable,
                  "ok": valid and uncovered == 0 and avoidable == 0}))
