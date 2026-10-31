"""Plan item 55: item44_run.py with a choice of neighbor move (targeted or local); otherwise identical.
Usage: PYTHONPATH=. python3 scripts/item55_run.py BENCH_DIR MODEL_NAME NEIGHBOR SEED START OUT.json [steps=6000] [restarts=5] [cap_s=7200]
t = 2, locating mode. Prints one JSON line per attempted size and a final line."""
import json, sys, time
from cla_harness.io import load_casa_model
from cla_harness.solver import FastZ3CostModel, find_small_suite_z3
bench, name, neighbor, seed, start, out = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
steps = int(sys.argv[7]) if len(sys.argv) > 7 else 6000
restarts = int(sys.argv[8]) if len(sys.argv) > 8 else 5
cap = float(sys.argv[9]) if len(sys.argv) > 9 else 7200
params, forb = load_casa_model(f"{bench}/{name}.model", f"{bench}/{name}.constraints")
t0 = time.perf_counter()
model = FastZ3CostModel(params, forb, strength=2)
print(json.dumps({"event": "built", "model": name, "interactions": len(model.interactions), "build_s": round(time.perf_counter() - t0, 1)}), flush=True)
t0 = time.perf_counter()
def log(a):
    print(json.dumps({"event": "size", "neighbor": neighbor, "seed": seed, "elapsed_s": round(time.perf_counter() - t0, 1), **a}, default=str), flush=True)
r = find_small_suite_z3(model, start, seed=seed, restarts=restarts, steps_per_restart=steps,
                        neighbor=neighbor, max_seconds=cap, on_attempt=log)
json.dump({"model": name, "mode": "locate", "neighbor": neighbor, "seed": seed, "size": r["size"], "suite": r["suite"]}, open(out, "w"))
print(json.dumps({"event": "final", "model": name, "neighbor": neighbor, "seed": seed, "start": start, "size": r["size"],
                  "total_moves": r["total_moves"], "timed_out": r["timed_out"], "elapsed_s": round(time.perf_counter() - t0, 1)}), flush=True)
