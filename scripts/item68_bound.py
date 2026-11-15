"""Plan item 68: lower bounds on the minimum (dbar, t) locating array size from the lazy MaxSAT of item65_exact.py.
Usage: PYTHONPATH=. python3 scripts/item68_bound.py MODEL.json STRENGTH D TIMEOUT_S
Same clauses as scripts/item65_exact.py. Every finished round's optimum satisfies a subset of the conditions, so it is
a proven lower bound on the true minimum; prints one JSON line per round and a final line with the best bound (and the
exact size if the last round separated every pair)."""
import json, sys, time
from itertools import combinations
import z3
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
path, t, d, timeout = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
start = time.time()
configs = valid_configurations(*load_model(path))
inter = sorted(feasible_interactions(configs, t), key=sorted)
masks = [sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i)) for i in inter]
sets = set(masks) | ({a | b for a, b in combinations(masks, 2)} if d == 2 else set())
distinct = sorted(sets)
x = [z3.Bool(f"c{k}") for k in range(len(configs))]
opt = z3.Optimize()
added = set(masks)
for m in added:
    opt.add(z3.Or([x[k] for k in range(len(configs)) if m >> k & 1]))
for v in x:
    opt.add_soft(z3.Not(v))
bound, exact, rounds = None, None, 0
while True:
    left = timeout - (time.time() - start)
    if left <= 1:
        break
    opt.set("timeout", int(left * 1000))
    if opt.check() != z3.sat:
        break
    rounds += 1
    m = opt.model()
    chosen = sum(1 << k for k in range(len(configs)) if z3.is_true(m.eval(x[k], model_completion=True)))
    bound = bin(chosen).count("1")
    print(json.dumps({"round": rounds, "lower_bound": bound, "seconds": round(time.time() - start, 1)}), flush=True)
    groups = {}
    for c in distinct:
        groups.setdefault(c & chosen, []).append(c)
    new = {a ^ b for g in groups.values() if len(g) > 1 for a, b in combinations(g, 2)} - added
    if not new:
        exact = bound
        break
    for mm in new:
        opt.add(z3.Or([x[k] for k in range(len(configs)) if mm >> k & 1]))
    added |= new
print(json.dumps({"model": path.replace("\\", "/").split("/")[-1], "strength": t, "d": d, "rounds": rounds,
                  "lower_bound": bound, "exact": exact, "seconds": round(time.time() - start, 1)}))
