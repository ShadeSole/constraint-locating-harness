"""Plan item 17: Z3-backed SA on the ORIGINAL spins model (about 2 million valid configurations).
CCAG is cloned OUTSIDE this repository; pass the directory holding spins.model / spins.constraints.
Usage: PYTHONPATH=. python3 scripts/item17_spins.py BENCH_DIR [seed] [start] [steps] [restarts] [max_seconds] [cover]
A trailing "cover" selects the covering-only cost (plan item 27).
Defaults: seed 0, start 40, 6000 moves per run, 5 restarts, 7200 s. Prints JSON lines."""
import json, sys, time
from collections import Counter
from math import prod
from cla_harness.io import load_casa_model
from cla_harness.core import constrained_core, valid_configurations, is_valid, contains_interaction
from cla_harness.solver import Z3CostModel, find_small_suite_z3
bench = sys.argv[1]
seed, start, steps, restarts, cap = (int(sys.argv[i]) if len(sys.argv) > i else d
                                     for i, d in ((2, 0), (3, 40), (4, 6000), (5, 5), (6, 7200)))
cover = len(sys.argv) > 7 and sys.argv[7] == "cover"
params, forb = load_casa_model(f"{bench}/spins.model", f"{bench}/spins.constraints")
core, rules, free = constrained_core(params, forb)
valid_total = len(valid_configurations(core, rules)) * prod(len(params[n]) for n in free)
t0 = time.perf_counter()
model = Z3CostModel(params, forb, cover_only=cover)
print(json.dumps({"event": "setup", "parameters": len(params), "values": sum(len(v) for v in params.values()),
                  "rules": len(forb), "valid_configurations": valid_total, "feasible_2way": len(model.interactions),
                  "mode": "cover" if cover else "locate", "seed": seed, "start": start, "steps_per_restart": steps, "restarts": restarts, "cap_s": cap}), flush=True)
def log(a):
    print(json.dumps({"event": "size", "elapsed_s": round(time.perf_counter() - t0, 1), **a,
                      "z3_cost_queries": [model.misses, model.hits], "z3_cost_query_s": round(model.seconds, 1)}), flush=True)
r = find_small_suite_z3(model, start, seed=seed, restarts=restarts, steps_per_restart=steps,
                        neighbor="targeted", max_seconds=cap, on_attempt=log)
out = {"event": "final", "elapsed_s": round(time.perf_counter() - t0, 1), "size": r["size"], "total_moves": r["total_moves"],
       "timed_out": r["timed_out"], "z3_cost_queries": [model.misses, model.hits], "z3_cost_query_s": round(model.seconds, 1)}
if r["suite"] is not None:
    suite = r["suite"]
    sigs = Counter(tuple(contains_interaction(c, i) for c in suite) for i in model.interactions)
    out.update({"all_tests_valid": all(is_valid(c, forb) for c in suite),
                "covered": sum(any(contains_interaction(c, i) for c in suite) for i in model.interactions),
                "unique_signature": sum(1 for i in model.interactions
                                        if sigs[tuple(contains_interaction(c, i) for c in suite)] == 1),
                "cost": model.suite_cost(suite)})
print(json.dumps(out), flush=True)
