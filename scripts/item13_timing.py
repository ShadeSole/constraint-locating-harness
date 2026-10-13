"""Plan item 13: enumeration versus Z3 for items 10-12 on all example models, 3 repeats each.
Tasks (per model):
  validity: decide validity of every configuration in the full product
            (enumeration: core.is_valid per config; Z3: solver.is_valid per config)
  listing:  all valid configurations (valid_configurations vs valid_configurations_z3)
  pairs:    feasible 2-way interactions from the model
            (feasible_interactions(valid_configurations) vs feasible_interactions_z3)
No warm-up run: repeat 1 includes any first-call cost. Run alone on the machine.
Usage: PYTHONPATH=. python3 scripts/item13_timing.py"""
import glob, statistics, time
from cla_harness.core import all_configurations, is_valid, valid_configurations, feasible_interactions
from cla_harness.io import load_model
from cla_harness import solver
REPEATS = 3

def timed(fn):
    t = time.perf_counter(); fn(); return time.perf_counter() - t

def fmt(xs):
    return "/".join(f"{x:.4f}" for x in xs) + f" (median {statistics.median(xs):.4f})"

print("model | task | enumeration s, repeats 1/2/3 | Z3 s, repeats 1/2/3 | Z3 median / enumeration median")
for path in sorted(glob.glob("examples/*.json")):
    p, f = load_model(path)
    cfgs = all_configurations(p)
    tasks = {
        "validity": (lambda: [is_valid(c, f) for c in cfgs], lambda: [solver.is_valid(p, f, c) for c in cfgs]),
        "listing": (lambda: valid_configurations(p, f), lambda: solver.valid_configurations_z3(p, f)),
        "pairs": (lambda: feasible_interactions(valid_configurations(p, f), 2), lambda: solver.feasible_interactions_z3(p, f)),
    }
    for name, (enum_fn, z3_fn) in tasks.items():
        e = [timed(enum_fn) for _ in range(REPEATS)]
        z = [timed(z3_fn) for _ in range(REPEATS)]
        print(f"{path.split('/')[-1]} | {name} | {fmt(e)} | {fmt(z)} | {statistics.median(z)/statistics.median(e):.1f}x", flush=True)
