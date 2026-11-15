"""Plan item 69: decide whether a (dbar, t) constrained locating array with at most K tests exists, d = 1 or 2, on a small
JSON model, with a SAT solver (PySAT, pip install python-sat; scripts only, not a library dependency).
Usage: PYTHONPATH=. python3 scripts/item69_decide.py MODEL.json STRENGTH D K [--fix-first] [OUT.json]
Same conditions and lazy clauses as scripts/item65_exact.py: a variable per valid configuration, "at most K chosen" as a
cardinality encoding, a clause per interaction (covered), and separation clauses added only when a solution fails to
separate two fault-set classes whose full signatures differ. UNSAT means no array of size <= K exists (a proven lower
bound K + 1); SAT with every pair separated gives an array of size <= K, saved to OUT.json.
--fix-first adds "configuration 0 is chosen". Only valid for unconstrained models: there, renaming the values of each
parameter maps arrays to arrays (both conditions are preserved) and acts transitively on configurations, so any array can
be mapped to one containing configuration 0.
--fix-two (implies --fix-first; unconstrained models whose parameters all share one value list): also "some chosen
configuration a_w is chosen and no chosen configuration has weight 1 to w - 1", where weight = number of parameters not at
the first value and a_w = the second value on the first w parameters, the first value elsewhere. Sound because renaming
values while keeping the first value fixed, and permuting parameters, both fix configuration 0 and weights; the chosen
configuration of least positive weight can be mapped to a_w."""
import json, sys, time
from itertools import combinations
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
args = [a for a in sys.argv[1:] if not a.startswith("--")]
fix_two = "--fix-two" in sys.argv
fix_first = "--fix-first" in sys.argv or fix_two
path, t, d, K = args[0], int(args[1]), int(args[2]), int(args[3])
out_path = args[4] if len(args) > 4 else None
start = time.time()
params, forb = load_model(path)
if fix_first and forb:
    raise SystemExit("--fix-first is only valid for models without forbidden combinations")
configs = valid_configurations(params, forb)
n = len(configs)
inter = sorted(feasible_interactions(configs, t), key=sorted)
masks = [sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i)) for i in inter]
classes = set(masks) | ({a | b for a, b in combinations(masks, 2)} if d == 2 else set())
if d not in (1, 2):
    raise SystemExit("d must be 1 or 2")
distinct = sorted(classes)
var = lambda k: k + 1  # configuration k is variable k + 1
card = CardEnc.atmost([var(k) for k in range(n)], bound=K, top_id=n, encoding=EncType.seqcounter)
s = Solver(name="cadical195", bootstrap_with=card.clauses)
clause = lambda m: [var(k) for k in range(n) if m >> k & 1]
added = set(masks)
for m in added:
    s.add_clause(clause(m))
if fix_first:
    if configs[0] != {p: vals[0] for p, vals in params.items()}:
        raise SystemExit("configuration 0 is not the all-first-values configuration")
    s.add_clause([var(0)])
if fix_two:
    names = list(params)
    if len({tuple(v) for v in params.values()}) != 1:
        raise SystemExit("--fix-two needs every parameter to share one value list")
    first, second = params[names[0]][0], params[names[0]][1]
    weight = [sum(c[p] != first for p in names) for c in configs]
    top = card.nv
    ys = []
    for w in range(1, len(names) + 1):
        top += 1
        ys.append(top)
        a_w = configs.index({p: (second if i < w else first) for i, p in enumerate(names)})
        s.add_clause([-top, var(a_w)])
        for k in range(n):
            if 1 <= weight[k] < w:
                s.add_clause([-top, -var(k)])
    s.add_clause(ys)
rounds = 0
while True:
    rounds += 1
    if not s.solve():
        result = "unsat"
        break
    model = s.get_model()
    chosen = sum(1 << k for k in range(n) if model[k] > 0)
    groups = {}
    for c in distinct:
        groups.setdefault(c & chosen, []).append(c)
    new = {a ^ b for g in groups.values() if len(g) > 1 for a, b in combinations(g, 2)} - added
    if not new:
        result = "sat"
        break
    for m in new:
        s.add_clause(clause(m))
    added |= new
    print(json.dumps({"round": rounds, "clauses_added": len(added), "seconds": round(time.time() - start, 1)}), flush=True)
out = {"model": path.replace("\\", "/").split("/")[-1], "strength": t, "d": d, "K": K, "fix_first": fix_first, "fix_two": fix_two,
       "configs": n, "result": result, "rounds": rounds, "clauses_added": len(added),
       "seconds": round(time.time() - start, 1)}
if result == "sat":
    idx = [k for k in range(n) if chosen >> k & 1]
    out["size"] = len(idx)
    if out_path:
        json.dump({"model": out["model"], "strength": t, "d": d, "suite": [configs[k] for k in idx]}, open(out_path, "w"),
                  indent=1)
print(json.dumps(out))
