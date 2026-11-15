"""Plan item 48: (bar2,2) condition checked on d = 1 locating suites. Measure only.
For each of the 7 non-slow example models at t = 2: rebuild the item 25 locating suite (seed 0, Z3-backed cold
shrinking search, targeted, 3 restarts x 3000 moves, start = greedy locating size). Sets = every single feasible
interaction and every pair of distinct feasible interactions. A set's signature = tests (or valid configurations)
containing ANY interaction in it. Colliding pair = two distinct sets with equal suite signature; unavoidable =
equal signature over ALL valid configurations; avoidable = colliding - unavoidable.
Usage: PYTHONPATH=. python3 scripts/item48_sets.py"""
import glob
from collections import Counter
from itertools import combinations
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
from cla_harness.io import load_model
from cla_harness.generator import greedy_locating_suite
from cla_harness.solver import Z3CostModel, find_small_suite_z3
LIMIT = 5_000_000

def masks(configs, ints):
    m = {}
    for i in ints:
        v = 0
        for k, c in enumerate(configs):
            if contains_interaction(c, i):
                v |= 1 << k
        m[i] = v
    return m

def groups(ints, mk):
    cnt = Counter()
    for i in ints:
        cnt[mk[i]] += 1
    for a, b in combinations(ints, 2):
        cnt[mk[a] | mk[b]] += 1
    return cnt

def pairs(cnt):
    return sum(v * (v - 1) // 2 for v in cnt.values())

print("model | valid | suite size | interactions | sets (1 or 2) | set pairs | colliding pairs | unavoidable | avoidable | avoidable single-vs-single (d=1 check)")
for path in sorted(glob.glob("examples/*.json")):
    name = path.split("/")[-1]
    if "spins" in name:
        continue
    p, f = load_model(path)
    configs = valid_configurations(p, f)
    ints = sorted(feasible_interactions(configs, 2), key=lambda i: sorted(i))
    n = len(ints); m = n + n * (n - 1) // 2; sp = m * (m - 1) // 2
    if sp > LIMIT:
        print(f"{name} | {len(configs)} | - | {n} | {m} | {sp} | skipped (over {LIMIT} set pairs)")
        continue
    gl = len(greedy_locating_suite(configs, feasible_interactions(configs, 2), 2))
    r = find_small_suite_z3(Z3CostModel(p, f), gl, seed=0, restarts=3, steps_per_restart=3000, neighbor="targeted")
    suite = r["suite"]
    sm = masks(suite, ints); cm = masks(configs, ints)
    coll = pairs(groups(ints, sm)); unav = pairs(groups(ints, cm))
    s1 = sum(1 for a, b in combinations(ints, 2) if sm[a] == sm[b] and cm[a] != cm[b])
    print(f"{name} | {len(configs)} | {len(suite)} | {n} | {m} | {sp} | {coll} | {unav} | {coll - unav} | {s1}", flush=True)
