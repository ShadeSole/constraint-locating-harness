"""Plan item 30: covering-only versus locating at strength T on the 7 non-slow example models.
Z3-backed cold shrinking search, targeted moves, 3 restarts x 3000 moves per size, start = greedy
locating size at strength T, base seed SEED. Also reruns the enumeration-based locating search
(find_small_suite, same settings) for a direct consistency check. Greedy covering size for reference.
Usage: PYTHONPATH=. python3 scripts/item30_compare.py SEED [T]   (T defaults to 3)"""
import glob, sys, time
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
from cla_harness.io import load_model
from cla_harness.generator import greedy_covering_suite, greedy_locating_suite
from cla_harness.annealing import unavoidable_pairs, find_small_suite
from cla_harness.solver import Z3CostModel, find_small_suite_z3
seed = int(sys.argv[1]); T = int(sys.argv[2]) if len(sys.argv) > 2 else 3
print(f"strength {T}, seed {seed}")
print("model | valid | feasible | greedy cover | greedy locate | Z3 cover size (s) | Z3 locating size (s) | enumeration locating size (s) | difference (Z3 locating - covering) | cover suite valid and covers all")
for path in sorted(glob.glob("examples/*.json")):
    name = path.split("/")[-1]
    if "spins" in name:
        continue
    p, f = load_model(path)
    configs = valid_configurations(p, f); ints = feasible_interactions(configs, T)
    gc = len(greedy_covering_suite(configs, ints, T)); gl = len(greedy_locating_suite(configs, ints, T))
    key = lambda c: tuple(sorted(c.items())); valid = {key(c) for c in configs}
    res = {}
    for mode in ("cover", "locate"):
        model = Z3CostModel(p, f, cover_only=(mode == "cover"), strength=T)
        t = time.perf_counter()
        r = find_small_suite_z3(model, gl, seed=seed, restarts=3, steps_per_restart=3000, neighbor="targeted")
        res[mode] = (r, time.perf_counter() - t, model)
    t = time.perf_counter()
    e = find_small_suite(configs, ints, unavoidable_pairs(configs, ints), gl, seed=seed, restarts=3,
                         steps_per_restart=3000, neighbor="targeted")
    te = time.perf_counter() - t
    rc, tc, mc = res["cover"]; rl, tl, _ = res["locate"]
    ok = all(any(contains_interaction(c, i) for c in rc["suite"]) for i in ints) and all(key(c) in valid for c in rc["suite"])
    print(f"{name} | {len(configs)} | {len(ints)} | {gc} | {gl} | {rc['size']} ({tc:.1f}) | {rl['size']} ({tl:.1f}) | "
          f"{e['size']} ({te:.1f}) | {rl['size'] - rc['size']} | {ok}", flush=True)
