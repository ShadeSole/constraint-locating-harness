"""Plan item 31: Z3-backed cold shrinking search at strength T on an example model, with a wall-clock cap.
Usage: PYTHONPATH=. python3 scripts/item31_search.py MODEL_JSON T SEED MODE START [STEPS] [RESTARTS] [CAP_S]
MODE cover | locate. Defaults: 6000 moves, 5 restarts, cap 7200 s. Prints JSON lines (one per size, then final)."""
import json, sys, time
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, contains_interaction
from cla_harness.solver import Z3CostModel, find_small_suite_z3
path, T, seed, mode, start = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
steps = int(sys.argv[6]) if len(sys.argv) > 6 else 6000
restarts = int(sys.argv[7]) if len(sys.argv) > 7 else 5
cap = float(sys.argv[8]) if len(sys.argv) > 8 else 7200
p, f = load_model(path)
model = Z3CostModel(p, f, cover_only=(mode == "cover"), strength=T)
t0 = time.perf_counter()
log = lambda a: print(json.dumps({"event": "size", "elapsed_s": round(time.perf_counter() - t0, 1), **a}), flush=True)
r = find_small_suite_z3(model, start, seed=seed, restarts=restarts, steps_per_restart=steps, neighbor="targeted",
                        max_seconds=cap, on_attempt=log)
out = {"event": "final", "model": path.split("/")[-1], "strength": T, "mode": mode, "seed": seed, "start": start,
       "size": r["size"], "total_moves": r["total_moves"], "timed_out": r["timed_out"],
       "elapsed_s": round(time.perf_counter() - t0, 1), "z3_cost_queries": [model.misses, model.hits]}
if r["suite"] is not None:
    valid = {tuple(sorted(c.items())) for c in valid_configurations(p, f)}
    out["all_tests_valid"] = all(tuple(sorted(c.items())) in valid for c in r["suite"])
    out["covered"] = sum(any(contains_interaction(c, i) for c in r["suite"]) for i in model.interactions)
    out["feasible"] = len(model.interactions)
print(json.dumps(out), flush=True)
