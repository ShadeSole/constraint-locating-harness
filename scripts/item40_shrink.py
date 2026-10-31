"""Plan item 40: Z3-backed shrinking search on original spins at a given strength, FastZ3CostModel.
Usage: PYTHONPATH=. python3 scripts/item40_shrink.py BENCH_DIR STRENGTH MODE(cover|locate) SEED START [steps=6000] [restarts=5] [cap_s=7200] [model_name=spins]
Prints one JSON line per attempted size and a final line."""
import json, sys, time
from cla_harness.io import load_casa_model
from cla_harness.solver import FastZ3CostModel, find_small_suite_z3
bench, tt, mode, seed, start = sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
steps = int(sys.argv[6]) if len(sys.argv) > 6 else 6000
restarts = int(sys.argv[7]) if len(sys.argv) > 7 else 5
cap = float(sys.argv[8]) if len(sys.argv) > 8 else 7200
name = sys.argv[9] if len(sys.argv) > 9 else "spins"
params, forb = load_casa_model(f"{bench}/{name}.model", f"{bench}/{name}.constraints")
model = FastZ3CostModel(params, forb, cover_only=(mode == "cover"), strength=tt)
t0 = time.perf_counter()
def log(a):
    print(json.dumps({"event": "size", "mode": mode, "seed": seed, "elapsed_s": round(time.perf_counter() - t0, 1), **a,
                      "z3_cost_queries": [model.misses, model.hits]}, default=str), flush=True)
r = find_small_suite_z3(model, start, seed=seed, restarts=restarts, steps_per_restart=steps,
                        neighbor="targeted", max_seconds=cap, on_attempt=log)
print(json.dumps({"event": "final", "model": name, "mode": mode, "strength": tt, "seed": seed, "start": start, "size": r["size"],
                  "total_moves": r["total_moves"], "timed_out": r["timed_out"], "elapsed_s": round(time.perf_counter() - t0, 1)}), flush=True)
