"""Plan item 67: decide exactly, for one model, whether EVERY (1bar, 3) constrained locating array is (2bar, 2).
Usage: PYTHONPATH=. python3 scripts/item67_exact_implication.py MODEL [FROM TO]   (MODEL = a JSON path, or "binK" /
"terK" for K unconstrained parameters with 2 / 3 values; FROM and TO are conditions "dD_tT", default d1_t3 d2_t2: the
question becomes "does every FROM array satisfy TO?", so known-false pairs serve as negative controls)
Both conditions are monotone (adding tests never breaks them), and each is "every clause contains a chosen test", where
a clause is the set of valid configurations covering an interaction, or separating two fault sets with different full
signatures. Some (1bar, 3) array fails (2bar, 2) iff for some (2bar, 2) clause M the suite V \\ M is (1bar, 3), i.e.
iff some (2bar, 2) clause contains no (1bar, 3) clause. So the implication holds on the model iff every (2bar, 2)
clause contains at least one (1bar, 3) clause. Checked with bit masks over the valid configurations."""
import json, sys, time
from itertools import combinations
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
from cla_harness.io import load_model
spec = sys.argv[1]
src, dst = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ("d1_t3", "d2_t2")
t0 = time.time()
if spec.startswith(("bin", "ter")):
    v = 2 if spec.startswith("bin") else 3
    params, forb = {f"p{j}": [str(x) for x in range(v)] for j in range(int(spec[3:]))}, []
else:
    params, forb = load_model(spec)
configs = valid_configurations(params, forb)

def masks(t):
    return [sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i))
            for i in sorted(feasible_interactions(configs, t), key=sorted)]

def minimal(clauses):
    kept = []
    for m in sorted(clauses, key=lambda m: bin(m).count("1")):
        if not any(k & m == k for k in kept):
            kept.append(m)
    return kept

def clause_parts(cond):
    d, t = int(cond[1]), int(cond.split("_t")[1])
    cover = masks(t)
    classes = set(cover)
    if d == 2:
        classes |= {a | b for a, b in combinations(cover, 2)}
    return cover, sorted(classes)

cover_s, classes_s = clause_parts(src)
c_src = minimal(set(cover_s) | {a ^ b for a, b in combinations(classes_s, 2)})
cover_d, classes_d = clause_parts(dst)
checked, bad = 0, None
for m in cover_d:  # coverage clauses of the target condition
    checked += 1
    if not any(k & m == k for k in c_src):
        bad = {"kind": "coverage", "mask": m}
        break
if bad is None:
    seen = set()
    for a, b in combinations(classes_d, 2):
        m = a ^ b
        if m in seen:
            continue
        seen.add(m)
        checked += 1
        if not any(k & m == k for k in c_src):
            bad = {"kind": "separation", "mask": m}
            break
out = {"model": spec.replace("\\", "/").split("/")[-1], "configs": len(configs), "from": src, "to": dst,
       "from_minimal_clauses": len(c_src), "to_classes": len(classes_d), "to_clauses_checked": checked, "implication_holds": bad is None,
       "seconds": round(time.time() - t0, 1)}
if bad:
    out["counterexample"] = {"kind": bad["kind"], "suite_is_all_valid_configurations_except": [configs[k] for k in range(len(configs)) if bad["mask"] >> k & 1]}
print(json.dumps(out))
