"""Plan item 15: Z3-backed cost versus suite_cost on 200 seeded random suites per model.
Usage: PYTHONPATH=. python3 scripts/item15_check.py"""
import glob, random, time
from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.io import load_model
from cla_harness.annealing import suite_cost, unavoidable_pairs
from cla_harness.solver import Z3CostModel
print("model | suites | identical | suites with avoidable collisions | suite_cost total s | Z3 cost total s | Z3 query s | cache misses / hits")
for path in sorted(glob.glob("examples/*.json")):
    p, f = load_model(path)
    configs = valid_configurations(p, f); ints = feasible_interactions(configs, 2)
    un = unavoidable_pairs(configs, ints)
    rng = random.Random(11)
    suites = [rng.choices(configs, k=rng.randint(1, min(16, 2 * len(configs)))) for _ in range(200)]
    t = time.perf_counter(); want = [suite_cost(s, ints, un) for s in suites]; te = time.perf_counter() - t
    model = Z3CostModel(p, f)
    t = time.perf_counter(); got = [model.suite_cost(s) for s in suites]; tz = time.perf_counter() - t
    print(f"{path.split('/')[-1]} | {len(suites)} | {sum(a == b for a, b in zip(want, got))} | "
          f"{sum(w['avoidable_collisions'] > 0 for w in want)} | {te:.3f} | {tz:.3f} | {model.seconds:.3f} | {model.misses} / {model.hits}")
