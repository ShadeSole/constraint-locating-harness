"""Stage B (plan item 75): shape of each configuration-dependent mutant's failure set F, and detail of misleading
diagnoses. 'union of pairs' / 'union of triples' = F equals the union of all pair (triple) masks it contains; the
minimal number of such interactions is found greedily (an upper bound on the true minimum).
Usage: PYTHONPATH=. python3 scripts/stageb/tw_shapes.py docs/item75/mutants.jsonl docs/item75/evaluation.json"""
import json, sys
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
params, forb = load_model("docs/item75/textwrap_model.json")
configs = valid_configurations(params, forb)
n = len(configs)
def masks(t):
    return {i: sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i)) for i in feasible_interactions(configs, t)}
P, T = masks(2), masks(3)
def union_of(F, M):
    inside = [m for m in M.values() if m & ~F == 0]
    u = 0
    for m in inside: u |= m
    if u != F:
        return None
    left, k = F, 0
    while left:
        best = max(inside, key=lambda m: bin(m & left).count("1")); left &= ~best; k += 1
    return k
mut = {m["id"]: m for m in map(json.loads, open(sys.argv[1]))}
ev = json.load(open(sys.argv[2]))
seen = {}
for p in ev["per_mutant"]:
    if p["suite"] != "L1": continue
    m = mut[p["mutant"]]; F = sum(1 << k for k in m["failing"])
    seen[m["id"]] = {"id": m["id"], "op": m["operator"], "line": m["line"], "n_fail": m["n_fail"],
                     "pairs_needed": union_of(F, P), "triples_needed": union_of(F, T)}
rows = list(seen.values())
cat = lambda r: ("<=2 pairs" if r["pairs_needed"] and r["pairs_needed"] <= 2 else
                 "union of 3+ pairs" if r["pairs_needed"] else
                 "union of triples" if r["triples_needed"] else "needs 4+ way")
from collections import Counter
print("shape of 83 failure sets:", dict(Counter(cat(r) for r in rows)))
print("failing configs per mutant: min", min(r["n_fail"] for r in rows), "median", sorted(r["n_fail"] for r in rows)[len(rows)//2], "max", max(r["n_fail"] for r in rows), "of", n)
for p in ev["per_mutant"]:
    if p["outcome"] == "misleading":
        r = seen[p["mutant"]]
        print("misleading:", p["suite"], "mutant", r["id"], r["op"], "line", r["line"], "fails on", r["n_fail"], "configs; shape:", cat(r))
