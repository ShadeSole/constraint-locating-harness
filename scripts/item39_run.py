"""Plan item 39: ONE FastZ3CostModel targeted SA run on original spins at a given strength.
Usage: PYTHONPATH=. python3 scripts/item39_run.py BENCH_DIR SIZE STEPS STRENGTH MODE(cover|locate) [seed] [cap_s] [model_name=spins]
Cooling falls from 2.0 to 0.05 over exactly STEPS moves; run seed = annealing._restart_seed(seed, SIZE, 0). Prints JSON lines."""
import json, sys, time
from cla_harness.io import load_casa_model
from cla_harness.core import is_valid, contains_interaction
from cla_harness.annealing import _restart_seed
from cla_harness.solver import FastZ3CostModel, anneal_suite_z3
bench, size, steps, t_str, mode = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
seed = int(sys.argv[6]) if len(sys.argv) > 6 else 0
cap = float(sys.argv[7]) if len(sys.argv) > 7 else 3600
name = sys.argv[8] if len(sys.argv) > 8 else "spins"
params, forb = load_casa_model(f"{bench}/{name}.model", f"{bench}/{name}.constraints")
model = FastZ3CostModel(params, forb, cover_only=(mode == "cover"), strength=t_str)
t = time.perf_counter()
r = anneal_suite_z3(model, size, _restart_seed(seed, size, 0), steps, 2.0, (0.05 / 2.0) ** (1.0 / steps),
                    neighbor="targeted", deadline=t + cap)
suite = r["suite"]
print(json.dumps({"model": name, "mode": mode, "strength": t_str, "size": size, "steps_budget": steps, "seed": seed, "solved": r["solved"], "timed_out": r["timed_out"],
                  "cost": r["cost"], "moves": r["steps"], "seconds": round(time.perf_counter() - t, 1),
                  "all_tests_valid": all(is_valid(c, forb) for c in suite),
                  "feasible": len(model.interactions), "z3_cost_queries_misses_hits": [model.misses, model.hits]}), flush=True)
