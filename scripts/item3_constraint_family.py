"""Plan item 3: vary ONLY the constraints on a fixed parameter set; measure the
fraction of feasible 2-way interactions that are distinguishable (ceiling / feasible).

Parameters: the 5 binary parameters of examples/model.json. Candidate rules: all 40
pair-forbidden rules (one value of each of two parameters). For each ordering seed the
candidates are shuffled; the family is the nested prefixes k = 0..K of that order, so
rule set k+1 is rule set k plus one rule. A prefix with no valid configuration ends the
sequence. Usage: PYTHONPATH=. python3 scripts/item3_constraint_family.py [n_orders] [max_k]
"""
import random, statistics, sys
from itertools import combinations, product
from cla_harness.core import Forbidden, valid_configurations, feasible_interactions
from cla_harness.io import load_model
from cla_harness.experiment import ceiling_of

n_orders = int(sys.argv[1]) if len(sys.argv) > 1 else 20
max_k = int(sys.argv[2]) if len(sys.argv) > 2 else 10
params, _ = load_model("examples/model.json")
names = list(params)
cands = [{a: va, b: vb} for a, b in combinations(names, 2)
         for va, vb in product(params[a], params[b])]
rows = {k: [] for k in range(max_k + 1)}   # k -> list of (valid, feasible, ceiling)
for seed in range(n_orders):
    order = cands[:]
    random.Random(seed).shuffle(order)
    for k in range(max_k + 1):
        forb = [Forbidden.from_dict(d) for d in order[:k]]
        cfgs = valid_configurations(params, forb)
        if not cfgs:
            break
        ints = feasible_interactions(cfgs, strength=2)
        rows[k].append((len(cfgs), len(ints), ceiling_of(cfgs, ints)))
print(f"candidates={len(cands)} orderings={n_orders}")
print("rules | n | valid mean | feasible mean | ceiling mean | fraction distinguishable: min / median / max | n with fraction<1")
for k, r in rows.items():
    if not r:
        continue
    fr = [c / f for _, f, c in r]
    print(f"{k} | {len(r)} | {statistics.mean(v for v,_,_ in r):.1f} | "
          f"{statistics.mean(f for _,f,_ in r):.1f} | {statistics.mean(c for _,_,c in r):.1f} | "
          f"{min(fr):.3f} / {statistics.median(fr):.3f} / {max(fr):.3f} | {sum(x<1 for x in fr)}")
