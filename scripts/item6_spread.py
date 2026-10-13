"""Plan items 6-8: one seed per process through multi_seed_search, with wall time.
Usage: PYTHONPATH=. python3 scripts/item6_spread.py SEED MODE [restarts]
MODE: cold | extra (warm_extra). Model: examples/model_spins_core.json, start 32, 6000 moves, targeted.
Prints one JSON line.
"""
import json, sys, time
from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.io import load_model
from cla_harness.annealing import unavoidable_pairs, multi_seed_search
seed, mode = int(sys.argv[1]), sys.argv[2]
restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 5
params, forb = load_model("examples/model_spins_core.json")
configs = valid_configurations(params, forb)
ints = feasible_interactions(configs, 2)
un = unavoidable_pairs(configs, ints)
t = time.perf_counter()
r = multi_seed_search(configs, ints, un, 32, [seed], restarts=restarts, steps_per_restart=6000,
                      neighbor="targeted", warm_start=mode == "extra", warm_extra=mode == "extra")
run = r["runs"][0]
print(json.dumps({"seed": seed, "mode": mode, "restarts": restarts, "size": run["size"],
                  "moves": run["total_moves"], "seconds": round(time.perf_counter() - t, 1),
                  "attempts": [(a["n"], a["solved"], a["solved_by"]) for a in run["attempts"]]}), flush=True)
