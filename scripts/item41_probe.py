"""Plan item 41: load a CCAG model and report size and Z3 setup time at t = 2.
Usage: PYTHONPATH=. python3 scripts/item41_probe.py BENCH_DIR NAME"""
import json, sys, time
from itertools import combinations
from cla_harness.io import load_casa_model
from cla_harness.solver import FastZ3CostModel
bench, name = sys.argv[1], sys.argv[2]
t = time.perf_counter()
params, forb = load_casa_model(f"{bench}/{name}.model", f"{bench}/{name}.constraints")
load_s = time.perf_counter() - t
sizes = [len(v) for v in params.values()]
cands = sum(a * b for a, b in combinations(sizes, 2))
t = time.perf_counter()
model = FastZ3CostModel(params, forb, cover_only=True, strength=2)
print(json.dumps({"model": name, "parameters": len(params), "values": sum(sizes), "rules": len(forb),
                  "candidate_2way": cands, "feasible_2way": len(model.interactions),
                  "load_s": round(load_s, 2), "z3_build_s": round(time.perf_counter() - t, 1)}), flush=True)
