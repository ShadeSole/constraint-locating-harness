"""Plan item 26: covering-only (or locating) cold shrinking search on model_spins_core.json.
Usage: PYTHONPATH=. python3 scripts/item26_cover.py SEED MODE   (MODE cover | locate)
Start 32, 6000 moves, 5 restarts, targeted, cold, as in items 6 and 7. Prints one JSON line."""
import json, sys, time
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
from cla_harness.solver import Z3CostModel, find_small_suite_z3
seed, mode = int(sys.argv[1]), sys.argv[2]
p, f = load_model("examples/model_spins_core.json")
model = Z3CostModel(p, f, cover_only=(mode == "cover"))
t = time.perf_counter()
r = find_small_suite_z3(model, 32, seed=seed, restarts=5, steps_per_restart=6000, neighbor="targeted")
configs = valid_configurations(p, f); valid = {tuple(sorted(c.items())) for c in configs}
ok = r["suite"] is not None and all(tuple(sorted(c.items())) in valid for c in r["suite"]) and \
     all(any(contains_interaction(c, i) for c in r["suite"]) for i in model.interactions)
print(json.dumps({"seed": seed, "mode": mode, "size": r["size"], "moves": r["total_moves"],
                  "seconds": round(time.perf_counter() - t, 1), "valid_and_covering": ok,
                  "attempts": [(a["n"], a["solved"]) for a in r["attempts"]]}), flush=True)
