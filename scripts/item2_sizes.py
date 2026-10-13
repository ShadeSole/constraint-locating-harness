"""Plan item 2: greedy vs SA suite sizes and times on the enumerable example models.

Usage: python scripts/item2_sizes.py [seed]
Uses existing functions only; strength 2; SA = find_small_suite, targeted moves,
3 restarts x 3000 moves per size, started at the greedy locating size.
"""
import glob, sys, time
from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.io import load_model
from cla_harness.generator import greedy_covering_suite, greedy_locating_suite
from cla_harness.annealing import unavoidable_pairs, find_small_suite
from cla_harness.experiment import evaluate_method, ceiling_of

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
print("model | valid | feasible | ceiling | cover tests (s) | greedy-locate tests, localized (s) | SA tests, localized, moves (s)")
for path in sorted(glob.glob("examples/*.json")):
    if "spins" in path:
        continue
    params, forb = load_model(path)
    configs = valid_configurations(params, forb)
    ints = feasible_interactions(configs, strength=2)
    ceil = ceiling_of(configs, ints)
    t = time.perf_counter(); cov = greedy_covering_suite(configs, ints, 2); tc = time.perf_counter() - t
    t = time.perf_counter(); loc = greedy_locating_suite(configs, ints, 2); tl = time.perf_counter() - t
    rl = evaluate_method("locate", loc, ints)
    un = unavoidable_pairs(configs, ints)
    t = time.perf_counter()
    r = find_small_suite(configs, ints, un, len(loc), seed=seed, restarts=3,
                         steps_per_restart=3000, neighbor="targeted")
    ts = time.perf_counter() - t
    rs = evaluate_method("sa", r["suite"], ints)
    print(f"{path} | {len(configs)} | {len(ints)} | {ceil} | {len(cov)} ({tc:.3f}) | "
          f"{len(loc)}, {rl['localized']}/{rl['total']} ({tl:.3f}) | "
          f"{r['size']}, {rs['localized']}/{rs['total']}, {r['total_moves']} ({ts:.1f})")
