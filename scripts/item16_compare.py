"""Plan item 16: Z3-backed SA (find_small_suite_z3) versus enumeration-based find_small_suite.
Same settings for both: targeted moves, 3 restarts x 3000 moves per size, base seed SEED,
start size = greedy locating size. The other four models have no recorded exact minimum.
Usage: PYTHONPATH=. python3 scripts/item16_compare.py SEED"""
import glob, sys, time
from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.io import load_model
from cla_harness.generator import greedy_locating_suite
from cla_harness.annealing import unavoidable_pairs, find_small_suite
from cla_harness.solver import Z3CostModel, find_small_suite_z3
seed = int(sys.argv[1])
KNOWN = {"model.json": 9, "model_high_constraints.json": 9, "my_model.json": 8}
key = lambda c: tuple(sorted(c.items()))
print("model | valid | greedy | exact minimum | enum SA size, moves, s | Z3 SA size, moves, s | Z3 queries (misses/hits), Z3 query s | all Z3 tests valid")
for path in sorted(glob.glob("examples/*.json")):
    name = path.split("/")[-1]
    if "spins" in name:
        continue
    p, f = load_model(path)
    configs = valid_configurations(p, f); ints = feasible_interactions(configs, 2)
    un = unavoidable_pairs(configs, ints); start = len(greedy_locating_suite(configs, ints, 2))
    t = time.perf_counter()
    e = find_small_suite(configs, ints, un, start, seed=seed, restarts=3, steps_per_restart=3000, neighbor="targeted")
    te = time.perf_counter() - t
    model = Z3CostModel(p, f)
    t = time.perf_counter()
    z = find_small_suite_z3(model, start, seed=seed, restarts=3, steps_per_restart=3000, neighbor="targeted")
    tz = time.perf_counter() - t
    valid = {key(c) for c in configs}
    print(f"{name} | {len(configs)} | {start} | {KNOWN.get(name, 'not recorded')} | {e['size']}, {e['total_moves']}, {te:.1f} | "
          f"{z['size']}, {z['total_moves']}, {tz:.1f} | {model.misses}/{model.hits}, {model.seconds:.1f} | "
          f"{all(key(c) in valid for c in z['suite'])}", flush=True)
