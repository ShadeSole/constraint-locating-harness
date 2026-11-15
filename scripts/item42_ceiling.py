"""Plan item 42: indistinguishable feasible interactions (Jin & Tsuchiya Def. 1 / Lemma 1, d = 1) via Z3, t = 2.
Usage: PYTHONPATH=. python3 scripts/item42_ceiling.py BENCH_DIR NAME [pool=400] [cap_s=1800]
Step 1: Z3-sampled valid configurations (a pool). Pairs of interactions that some pool test separates need no query.
Step 2: every remaining pair (identical signature over the pool) gets the exact Z3 query (Z3CostModel.separable).
An interaction is 'distinguishable' if it has no inseparable partner. Prints JSON lines."""
import json, sys, time
from collections import defaultdict
from itertools import combinations
from cla_harness.io import load_casa_model
from cla_harness.core import contains_interaction, is_valid
from cla_harness.solver import FastZ3CostModel, sample_valid_configurations
bench, name = sys.argv[1], sys.argv[2]
pool = int(sys.argv[3]) if len(sys.argv) > 3 else 400
cap = float(sys.argv[4]) if len(sys.argv) > 4 else 1800
params, forb = load_casa_model(f"{bench}/{name}.model", f"{bench}/{name}.constraints")
t0 = time.perf_counter()
model = FastZ3CostModel(params, forb, cover_only=True, strength=2)
n = len(model.interactions)
tests = sample_valid_configurations(params, forb, pool, seed=0)
groups = defaultdict(list)
for it in model.interactions:
    groups[tuple(contains_interaction(c, it) for c in tests)].append(it)
pairs = [(a, b) for g in groups.values() if len(g) > 1 for a, b in combinations(g, 2)]
print(json.dumps({"event": "setup", "model": name, "feasible_2way": n, "all_pairs": n * (n - 1) // 2, "pool": len(tests),
                  "pool_valid": all(is_valid(c, forb) for c in tests), "pairs_needing_query": len(pairs),
                  "setup_s": round(time.perf_counter() - t0, 1)}), flush=True)
t1 = time.perf_counter(); inseparable = []; done = 0; capped = False
for a, b in pairs:
    if time.perf_counter() - t1 > cap:
        capped = True; break
    if not model.separable(a, b):
        inseparable.append((a, b))
    done += 1
bad = {i for p in inseparable for i in p}
print(json.dumps({"event": "result", "model": name, "capped": capped, "pairs_queried": done, "pairs_total_needing_query": len(pairs),
                  "inseparable_pairs": len(inseparable), "interactions_in_an_inseparable_pair": len(bad),
                  "distinguishable_interactions": n - len(bad) if not capped else None,
                  "query_s": round(time.perf_counter() - t1, 1), "z3_queries": model.misses}), flush=True)
