"""Plan item 74: exhaustive check of the item 73 claim. For a (dbar, 2) suite with d = 2, decoded with the up-to-two-pairs
decoder, and any feasible fault interaction T of strength 3 or 4 that some test contains: every candidate set S of at
most 2 pairs with rows(S) = rows(T) must satisfy G(S) subset of G(T), where G is the set of valid configurations
containing a member of S (resp. T). The same check is run on the d = 1 suite with the one-pair decoder, where the
claim is NOT expected to hold. Prints one JSON line per (model, suite, fault strength).
Usage: PYTHONPATH=. python3 scripts/item74_check_claim.py MODEL.json D1_SUITE.json D2_SUITE.json"""
import json, sys
from itertools import combinations
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
path, s1, s2 = sys.argv[1:4]
configs = valid_configurations(*load_model(path))
pairs = sorted(feasible_interactions(configs, 2), key=sorted)
G = lambda i: sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i))
gp = {p: G(p) for p in pairs}
for label, sp, d in (("L1", s1, 1), ("L2", s2, 2)):
    suite = json.load(open(sp))["suite"]
    R = lambda i: sum(1 << r for r, c in enumerate(suite) if contains_interaction(c, i))
    rp = {p: R(p) for p in pairs}
    table = {}
    for p in pairs:
        table.setdefault(rp[p], []).append((p,))
    if d == 2:
        for a, b in combinations(pairs, 2):
            table.setdefault(rp[a] | rp[b], []).append((a, b))
    for t in (3, 4):
        faults = feasible_interactions(configs, t)
        checked = viol = cand_total = 0
        example = None
        for T in faults:
            r = R(T)
            if not r:
                continue
            gT = G(T)
            for S in table.get(r, []):
                cand_total += 1
                gS = 0
                for p in S:
                    gS |= gp[p]
                if gS & ~gT:
                    viol += 1
                    if example is None:
                        example = {"fault": sorted(T), "candidate": [sorted(p) for p in S]}
            checked += 1
        print(json.dumps({"model": path.split("/")[-1], "suite": label, "size": len(suite), "fault_strength": t,
                          "faults_checked": checked, "candidates": cand_total, "violations": viol,
                          "example": example}), flush=True)
