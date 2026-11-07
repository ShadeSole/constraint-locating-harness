"""Stage B (plan item 75): diagnose each textwrap mutant with three suites and compare with ground truth.
Usage: PYTHONPATH=. python3 scripts/stageb/tw_evaluate.py MUTANTS.jsonl L1.json L2.json [--cover-k K] > out.json

Ground truth for a mutant is F, the exact set of valid configurations on which it fails (from tw_mutants.py).
Only configuration-dependent mutants are used: 0 < |F| < number of valid configurations, status ok.
Type of F: "pair" if F equals the configurations containing some single option pair; "two_pairs" if it equals the
union for two pairs; "triple" if it equals those containing some 3-way interaction; "other" otherwise.
Suites: C = minimum 2-way covering suite (SAT, ascending from --cover-k), L1 and L2 from files.
C and L1 use the one-pair decoder, L2 the up-to-two-pairs decoder. For a candidate explanation S, G(S) is the set of
valid configurations containing a member of S. Outcome per (mutant, suite):
  correct     every candidate has G(S) == F
  ambiguous   some candidate has G(S) == F, some not
  safe        no candidate equals F, but every candidate has G(S) inside F (every config with the named cause fails)
  misleading  no candidate equals F and some candidate has configurations outside F (names a cause that passes
              elsewhere)
  flagged     no candidate matches the failing tests
  missed      no test in the suite fails
"""
import json, sys
from itertools import combinations
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction

mpath, l1, l2 = sys.argv[1:4]
cover_k = int(sys.argv[sys.argv.index("--cover-k") + 1]) if "--cover-k" in sys.argv else 1
params, forb = load_model("docs/item75/textwrap_model.json")
configs = valid_configurations(params, forb)
n = len(configs)
key = lambda c: tuple(sorted(c.items()))
index = {key(c): k for k, c in enumerate(configs)}
pairs = sorted(feasible_interactions(configs, 2), key=sorted)
triples = feasible_interactions(configs, 3)
G = {i: sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i)) for i in pairs}
pair_masks = set(G.values())
two_masks = {a | b for a, b in combinations(pair_masks, 2)}
triple_masks = {sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, t)) for t in triples}

def min_cover(k):
    while True:
        card = CardEnc.atmost(list(range(1, n + 1)), bound=k, top_id=n, encoding=EncType.seqcounter)
        s = Solver(name="cadical195", bootstrap_with=card.clauses)
        for i in pairs:
            s.add_clause([b + 1 for b in range(n) if G[i] >> b & 1])
        if s.solve():
            return [b for b in range(n) if s.get_model()[b] > 0]
        k += 1

suites = {"C": (min_cover(cover_k), 1),
          "L1": ([index[key(c)] for c in json.load(open(l1))["suite"]], 1),
          "L2": ([index[key(c)] for c in json.load(open(l2))["suite"]], 2)}

def table_for(rows_idx, d):
    rows = {i: sum(1 << r for r, k in enumerate(rows_idx) if G[i] >> k & 1) for i in pairs}
    tab = {}
    for i in pairs:
        tab.setdefault(rows[i], []).append((i,))
    if d == 2:
        for a, b in combinations(pairs, 2):
            tab.setdefault(rows[a] | rows[b], []).append((a, b))
    return tab

def gtype(F):
    if F in pair_masks:
        return "pair"
    if F in two_masks:
        return "two_pairs"
    if F in triple_masks:
        return "triple"
    return "other"

mutants = [json.loads(l) for l in open(mpath)]
use = [m for m in mutants if m["status"] == "ok" and 0 < m["n_fail"] < n]
outcomes = ["correct", "ambiguous", "safe", "misleading", "flagged", "missed"]
result = {"valid_configs": n, "mutants_total": len(mutants),
          "status": {s: sum(m["status"] == s for m in mutants) for s in ("ok", "timeout", "compile_error")},
          "never_fail": sum(m["status"] == "ok" and m["n_fail"] == 0 for m in mutants),
          "always_fail": sum(m["status"] == "ok" and m["n_fail"] == n for m in mutants),
          "config_dependent": len(use), "suite_sizes": {k: len(v[0]) for k, v in suites.items()}}
F_of = {m["id"]: sum(1 << k for k in m["failing"]) for m in use}
result["distinct_failure_sets"] = len(set(F_of.values()))
result["ground_truth_types"] = {}
for m in use:
    t = gtype(F_of[m["id"]])
    result["ground_truth_types"][t] = result["ground_truth_types"].get(t, 0) + 1
per = []
for name, (idx, d) in suites.items():
    tab = table_for(idx, d)
    for m in use:
        F = F_of[m["id"]]
        R = sum(1 << r for r, k in enumerate(idx) if F >> k & 1)
        if not R:
            o = "missed"
        else:
            cands = tab.get(R, [])
            if not cands:
                o = "flagged"
            else:
                gs = []
                for S in cands:
                    g = 0
                    for p in S:
                        g |= G[p]
                    gs.append(g)
                eq = [g == F for g in gs]
                if all(eq):
                    o = "correct"
                elif any(eq):
                    o = "ambiguous"
                elif all(g & ~F == 0 for g in gs):
                    o = "safe"
                else:
                    o = "misleading"
        per.append({"suite": name, "mutant": m["id"], "type": gtype(F), "outcome": o})
summary = {}
for name in suites:
    for t in ["all", "pair", "two_pairs", "triple", "other"]:
        sel = [p for p in per if p["suite"] == name and (t == "all" or p["type"] == t)]
        if sel:
            summary[f"{name}/{t}"] = {o: sum(p["outcome"] == o for p in sel) for o in outcomes} | {"n": len(sel)}
result["summary"] = summary
result["per_mutant"] = per
print(json.dumps(result, indent=1))
