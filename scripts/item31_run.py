"""Plan item 31: ONE Z3-backed SA run at a fixed size on an example model at strength T.
Usage: PYTHONPATH=. python3 scripts/item31_run.py MODEL_JSON T SIZE STEPS SEED MODE   (MODE cover | locate)
Cooling falls from 2.0 to 0.05 over STEPS moves; run seed = annealing._restart_seed(SEED, SIZE, 0). One JSON line,
with independent validity and coverage checks on the returned suite."""
import json, sys, time
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, contains_interaction
from cla_harness.annealing import _restart_seed
from cla_harness.solver import Z3CostModel, anneal_suite_z3
path, T, size, steps, seed, mode = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
p, f = load_model(path)
model = Z3CostModel(p, f, cover_only=(mode == "cover"), strength=T)
t = time.perf_counter()
r = anneal_suite_z3(model, size, _restart_seed(seed, size, 0), steps, 2.0, (0.05 / 2.0) ** (1.0 / steps), neighbor="targeted")
valid = {tuple(sorted(c.items())) for c in valid_configurations(p, f)}
print(json.dumps({"model": path.split("/")[-1], "strength": T, "mode": mode, "size": size, "steps_budget": steps, "seed": seed,
                  "solved": r["solved"], "cost": r["cost"], "moves": r["steps"], "seconds": round(time.perf_counter() - t, 1),
                  "all_tests_valid": all(tuple(sorted(c.items())) in valid for c in r["suite"]),
                  "covered_independent": sum(any(contains_interaction(c, i) for c in r["suite"]) for i in model.interactions),
                  "feasible": len(model.interactions), "z3_cost_queries": [model.misses, model.hits]}), flush=True)
