"""Plan items 19-20: ONE Z3-backed SA run at a fixed size on the original spins model.
Usage: PYTHONPATH=. python3 scripts/item19_run.py BENCH_DIR SIZE STEPS [seed]
Cooling falls from 2.0 to 0.05 over exactly STEPS moves (as in find_small_suite_z3); the run seed is
annealing._restart_seed(seed, SIZE, 0). Prints one JSON line, with independent checks on the returned suite."""
import json, sys, time
from cla_harness.io import load_casa_model
from cla_harness.core import is_valid, contains_interaction
from cla_harness.annealing import _restart_seed
from cla_harness.solver import Z3CostModel, anneal_suite_z3
bench, size, steps = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
params, forb = load_casa_model(f"{bench}/spins.model", f"{bench}/spins.constraints")
model = Z3CostModel(params, forb)
t = time.perf_counter()
r = anneal_suite_z3(model, size, _restart_seed(seed, size, 0), steps, 2.0, (0.05 / 2.0) ** (1.0 / steps),
                    neighbor="targeted")
suite = r["suite"]
print(json.dumps({"size": size, "steps_budget": steps, "seed": seed, "solved": r["solved"], "cost": r["cost"],
                  "moves": r["steps"], "seconds": round(time.perf_counter() - t, 1),
                  "all_tests_valid": all(is_valid(c, forb) for c in suite),
                  "covered_independent": sum(any(contains_interaction(c, i) for c in suite) for i in model.interactions),
                  "feasible": len(model.interactions), "z3_cost_queries": [model.misses, model.hits]}), flush=True)
