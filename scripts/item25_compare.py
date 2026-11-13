"""Plan item 25: covering-only versus locating search on the 7 non-slow example models.
Both modes: Z3-backed cold shrinking search, targeted moves, 3 restarts x 3000 moves per size,
start size = greedy locating size, base seed SEED. Greedy covering size shown for reference.
Usage: PYTHONPATH=. python3 scripts/item25_compare.py SEED"""
import glob, sys, time
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
from cla_harness.io import load_model
from cla_harness.generator import greedy_covering_suite, greedy_locating_suite
from cla_harness.solver import Z3CostModel, find_small_suite_z3
seed = int(sys.argv[1])
print("model | valid | greedy cover | greedy locate | Z3 SA cover-only size (s) | Z3 SA locating size (s) | difference (locating - covering) | cover suite covers all, tests valid")
for path in sorted(glob.glob("examples/*.json")):
    name = path.split("/")[-1]
    if "spins" in name:
        continue
    p, f = load_model(path)
    configs = valid_configurations(p, f); ints = feasible_interactions(configs, 2)
    gc = len(greedy_covering_suite(configs, ints, 2)); gl = len(greedy_locating_suite(configs, ints, 2))
    key = lambda c: tuple(sorted(c.items())); valid = {key(c) for c in configs}
    out = {}
    for mode in ("cover", "locate"):
        model = Z3CostModel(p, f, cover_only=(mode == "cover"))
        t = time.perf_counter()
        r = find_small_suite_z3(model, gl, seed=seed, restarts=3, steps_per_restart=3000, neighbor="targeted")
        out[mode] = (r, time.perf_counter() - t)
    rc, tc = out["cover"]; rl, tl = out["locate"]
    ok = all(any(contains_interaction(c, i) for c in rc["suite"]) for i in ints) and all(key(c) in valid for c in rc["suite"])
    print(f"{name} | {len(configs)} | {gc} | {gl} | {rc['size']} ({tc:.1f}) | {rl['size']} ({tl:.1f}) | {rl['size'] - rc['size']} | {ok}", flush=True)
