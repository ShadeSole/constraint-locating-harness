"""Plan item 65: d = 2 (or 1) locating-array search with cla_harness.multifault on a JSON model.
Usage: PYTHONPATH=. python3 scripts/item65_search.py MODEL.json STRENGTH D SEED START OUT.json [steps=6000] [restarts=5] [cap_s=3600]
Prints one JSON line per annealing run and a final line; saves the smallest solved suite."""
import json, sys, time
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.multifault import MultiFaultModel, find_small_multifault
path, t, d, seed, start, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
steps = int(sys.argv[7]) if len(sys.argv) > 7 else 6000
restarts = int(sys.argv[8]) if len(sys.argv) > 8 else 5
cap = float(sys.argv[9]) if len(sys.argv) > 9 else 3600
t0 = time.perf_counter()
params, forb = load_model(path)
configs = valid_configurations(params, forb)
model = MultiFaultModel(configs, feasible_interactions(configs, t), d)
name = path.replace("\\", "/").split("/")[-1]
print(json.dumps({"event": "built", "model": name, "configs": len(configs), "interactions": len(model.interactions),
                  "classes": len(model.classes), "build_s": round(time.perf_counter() - t0, 1)}), flush=True)
t0 = time.perf_counter()
log = lambda e: print(json.dumps({"event": "run", "elapsed_s": round(time.perf_counter() - t0, 1), **e}), flush=True)
r = find_small_multifault(model, start, seed, steps, restarts, log=log, max_seconds=cap)
if r["indices"]:
    json.dump({"model": name, "strength": t, "d": d, "seed": seed, "suite": [configs[k] for k in r["indices"]]},
              open(out, "w"), indent=1)
print(json.dumps({"event": "final", "model": name, "strength": t, "d": d, "seed": seed, "start": start, "size": r["size"],
                  "timed_out": r["timed_out"], "elapsed_s": round(time.perf_counter() - t0, 1)}), flush=True)
