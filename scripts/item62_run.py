"""Plan item 62: item61_run.py with a strength argument and JSON-model support; otherwise identical.
Usage: PYTHONPATH=. python3 scripts/item62_run.py BENCH_DIR MODEL_NAME STRENGTH MODE(cover|locate) NEIGHBOR SEED START OUT.json [steps=6000] [restarts=5] [cap_s=7200]
MODEL_NAME ending in .json is loaded with load_model from BENCH_DIR; otherwise the CASA .model/.constraints pair. Prints one JSON line per attempted size and a final line."""
import json, sys, time
from cla_harness.io import load_casa_model, load_model
from cla_harness.solver import FastZ3CostModel, find_small_suite_z3
bench, name, strength, mode, neighbor, seed, start, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5], int(sys.argv[6]), int(sys.argv[7]), sys.argv[8]
steps = int(sys.argv[9]) if len(sys.argv) > 9 else 6000
restarts = int(sys.argv[10]) if len(sys.argv) > 10 else 5
cap = float(sys.argv[11]) if len(sys.argv) > 11 else 7200
params, forb = load_model(f"{bench}/{name}") if name.endswith(".json") else load_casa_model(f"{bench}/{name}.model", f"{bench}/{name}.constraints")
t0 = time.perf_counter()
model = FastZ3CostModel(params, forb, cover_only=(mode == "cover"), strength=strength)
print(json.dumps({"event": "built", "model": name, "strength": strength, "interactions": len(model.interactions), "build_s": round(time.perf_counter() - t0, 1)}), flush=True)
t0 = time.perf_counter()
def log(a):
    print(json.dumps({"event": "size", "mode": mode, "neighbor": neighbor, "seed": seed, "elapsed_s": round(time.perf_counter() - t0, 1), **a}, default=str), flush=True)
r = find_small_suite_z3(model, start, seed=seed, restarts=restarts, steps_per_restart=steps,
                        neighbor=neighbor, max_seconds=cap, on_attempt=log)
json.dump({"model": name, "strength": strength, "mode": mode, "neighbor": neighbor, "seed": seed, "size": r["size"], "suite": r["suite"]}, open(out, "w"))
print(json.dumps({"event": "final", "model": name, "mode": mode, "neighbor": neighbor, "seed": seed, "start": start, "size": r["size"],
                  "total_moves": r["total_moves"], "timed_out": r["timed_out"], "elapsed_s": round(time.perf_counter() - t0, 1)}), flush=True)
