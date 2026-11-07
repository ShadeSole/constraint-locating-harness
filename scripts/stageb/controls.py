"""Stage B equal-budget controls (plan item 77). Same outcome definitions as tw_evaluate.py.
Usage: PYTHONPATH=. python3 scripts/stageb/controls.py --model MODEL.json --mutants MUTANTS.jsonl --l2 L2.json
       --l13 L13.json [--seeds 5] > out.json
Suites and decoders:
  L2          the (2bar, 2) suite again, decoder: up to two pairs (must reproduce tw_evaluate.py; consistency check)
  R<s>        |L2| valid configurations drawn uniformly at random (seed s, without replacement), decoder: up to two pairs
  L13         a (1bar, 3) suite, decoder: one interaction of strength 2 or 3
  L13/2pairs  the same L13 suite, decoder: up to two pairs
For each suite: counts of correct / ambiguous / safe / misleading / flagged / missed over configuration-dependent
mutants, and the same counted once per distinct failure set."""
import json, sys, random
from itertools import combinations
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction

arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
params, forb = load_model(arg("--model"))
configs = valid_configurations(params, forb)
n = len(configs)
key = lambda c: tuple(sorted(c.items()))
index = {key(c): k for k, c in enumerate(configs)}
pairs = sorted(feasible_interactions(configs, 2), key=sorted)
triples = sorted(feasible_interactions(configs, 3), key=sorted)
G = {i: sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i)) for i in pairs + triples}
load_idx = lambda p: [index[key(c)] for c in json.load(open(p))["suite"]]
l2, l13 = load_idx(arg("--l2")), load_idx(arg("--l13"))
suites = {"L2": (l2, pairs, 2)}
for s in range(int(arg("--seeds", 5))):
    suites[f"R{s}"] = (random.Random(s).sample(range(n), len(l2)), pairs, 2)
suites["L13"] = (l13, pairs + triples, 1)
suites["L13/2pairs"] = (l13, pairs, 2)

mut = [json.loads(l) for l in open(arg("--mutants"))]
use = [m for m in mut if m["status"] == "ok" and 0 < m["n_fail"] < n]
F_of = {m["id"]: sum(1 << k for k in m["failing"]) for m in use}
outs = ["correct", "ambiguous", "safe", "misleading", "flagged", "missed"]
res = {"model": arg("--model"), "config_dependent": len(use), "suites": {}}
for name, (idx, pool, d) in suites.items():
    rows = {i: sum(1 << r for r, k in enumerate(idx) if G[i] >> k & 1) for i in pool}
    tab = {}
    for i in pool:
        tab.setdefault(rows[i], []).append((i,))
    if d == 2:
        for a, b in combinations(pool, 2):
            tab.setdefault(rows[a] | rows[b], []).append((a, b))
    per, per_set = {o: 0 for o in outs}, {}
    for m in use:
        F = F_of[m["id"]]
        R = sum(1 << r for r, k in enumerate(idx) if F >> k & 1)
        if not R:
            o = "missed"
        elif not tab.get(R):
            o = "flagged"
        else:
            gs = []
            for S in tab[R]:
                g = 0
                for p in S:
                    g |= G[p]
                gs.append(g)
            eq = [g == F for g in gs]
            o = ("correct" if all(eq) else "ambiguous" if any(eq) else
                 "safe" if all(g & ~F == 0 for g in gs) else "misleading")
        per[o] += 1
        per_set.setdefault(F, o)
    res["suites"][name] = {"size": len(idx), "per_mutant": per,
                           "per_distinct_set": {o: sum(v == o for v in per_set.values()) for o in outs}}
print(json.dumps(res, indent=1))
