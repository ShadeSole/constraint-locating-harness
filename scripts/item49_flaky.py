"""Plan item 49: flaky failures vs localize_exact. Script only, library unchanged; rank_noisy is not used.
Suites: same as item 48 (item 25 locating search, seed 0, t = 2). A test containing the fault fails with
probability p per repeat; a test is reported failing if it failed in any of r repeats; tests without the fault never fail.
Every feasible interaction is the single fault, 20 trials each (random.Random(0)). Categories per trial:
exact = localize_exact returned exactly [true]; empty = []; wrong = non-empty and not exactly [true]
(includes ambiguous lists, with or without the true interaction).
Usage: PYTHONPATH=. python3 scripts/item49_flaky.py"""
import glob, random
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
from cla_harness.io import load_model
from cla_harness.generator import greedy_locating_suite
from cla_harness.localizer import localize_exact
from cla_harness.solver import Z3CostModel, find_small_suite_z3
TRIALS = 20
print("model | suite size | interactions | p | r | trials | exact | empty | wrong")
for path in sorted(glob.glob("examples/*.json")):
    name = path.split("/")[-1]
    if "spins" in name:
        continue
    p_, f = load_model(path)
    configs = valid_configurations(p_, f)
    ints = sorted(feasible_interactions(configs, 2), key=lambda i: sorted(i))
    gl = len(greedy_locating_suite(configs, feasible_interactions(configs, 2), 2))
    suite = find_small_suite_z3(Z3CostModel(p_, f), gl, seed=0, restarts=3, steps_per_restart=3000, neighbor="targeted")["suite"]
    contains = {i: [contains_interaction(c, i) for c in suite] for i in ints}
    rng = random.Random(0)
    for p in (1.0, 0.9, 0.7, 0.5):
        for r in (1, 2, 3):
            ex = em = wr = tot = 0
            for fault in ints:
                for _ in range(TRIALS):
                    out = tuple(1 if contains[fault][k] and any(rng.random() < p for _ in range(r)) else 0
                                for k in range(len(suite)))
                    got = localize_exact(suite, out, ints)
                    tot += 1
                    if got == [fault]: ex += 1
                    elif not got: em += 1
                    else: wr += 1
            print(f"{name} | {len(suite)} | {len(ints)} | {p} | {r} | {tot} | {ex/tot:.4f} | {em/tot:.4f} | {wr/tot:.4f}", flush=True)
