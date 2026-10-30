"""Plan item 65: exact minimum size of a (dbar, t) constrained locating array, d = 1 or 2, on a small JSON model, by
MaxSAT over the valid configurations (item63_exact.py generalised to sets of up to d interactions).
Usage: PYTHONPATH=. python3 scripts/item65_exact.py MODEL.json STRENGTH D [TIMEOUT_S] [OUT.json]
Sets = every set of 1 to D distinct feasible t-way interactions. A set's signature over some tests = the tests that
contain at least one of its interactions. Conditions: every interaction is in a chosen test (separates each set from
the empty set), and any two sets whose signatures over ALL valid configurations differ have different signatures over
the chosen tests; sets with equal full signatures are exempt (inseparable, Jin & Tsuchiya's distinguishability).
Z3 Optimize minimizes the number chosen; "sat" means it finished, so the size is a proven minimum."""
import json, sys, time
from itertools import combinations
import z3
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
path, t, d = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 600
start = time.time()
params, forb = load_model(path)
configs = valid_configurations(params, forb)
inter = sorted(feasible_interactions(configs, t), key=sorted)
masks = [sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i)) for i in inter]
sets = set(masks)
if d >= 2:
    sets |= {a | b for a, b in combinations(masks, 2)}
if d >= 3:
    raise SystemExit("d > 2 not implemented")
distinct = sorted(sets)  # distinct full signatures; sets sharing one are inseparable
clauses = set(masks) | {a ^ b for a, b in combinations(distinct, 2)}
# drop clauses that contain another clause (implied)
by_size = sorted(clauses, key=lambda m: bin(m).count("1"))
kept = []
for m in by_size:
    if not any(k & m == k for k in kept):
        kept.append(m)
x = [z3.Bool(f"c{k}") for k in range(len(configs))]
opt = z3.Optimize()
opt.set("timeout", int(timeout * 1000))
for m in kept:
    opt.add(z3.Or([x[k] for k in range(len(configs)) if m >> k & 1]))
for v in x:
    opt.add_soft(z3.Not(v))
result = opt.check()
out = {"model": path.split("/")[-1], "strength": t, "d": d, "configs": len(configs), "interactions": len(inter),
       "distinct_set_signatures": len(distinct), "clauses": len(clauses), "clauses_kept": len(kept), "z3": str(result),
       "seconds": round(time.time() - start, 1)}
if result == z3.sat:
    model = opt.model()
    chosen = [k for k in range(len(configs)) if z3.is_true(model.eval(x[k], model_completion=True))]
    out["size"] = len(chosen)
    if len(sys.argv) > 5:
        json.dump({"model": out["model"], "strength": t, "d": d, "suite": [configs[k] for k in chosen]},
                  open(sys.argv[5], "w"), indent=1)
print(json.dumps(out))
