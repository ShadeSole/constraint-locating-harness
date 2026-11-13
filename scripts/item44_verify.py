"""Plan item 44: check a saved suite against Jin & Tsuchiya's (1bar,2)-CLA condition (d = 1, t = 2), separately from the search code.
Usage: PYTHONPATH=. python3 scripts/item44_verify.py BENCH_DIR SUITE.json
Checks, using only the .model/.constraints loader and a fresh Z3 encoding written here (not FastZ3CostModel):
 1. every test gives each parameter a listed value and violates no forbidden rule (plain Python check);
 2. every feasible 2-way interaction is covered (feasibility decided here, one Z3 query per candidate pair);
 3. every pair of feasible interactions that the suite does not separate is inseparable for ANY valid test (one Z3 query per such pair)."""
import json, sys, itertools, collections
import z3
from cla_harness.io import load_casa_model
bench, path = sys.argv[1], sys.argv[2]
d = json.load(open(path)); name = d["model"]; suite = d["suite"]
params, forb = load_casa_model(f"{bench}/{name}.model", f"{bench}/{name}.constraints")
names = list(params)
ok_domain = all(all(t[p] in params[p] for p in names) and set(t) == set(names) for t in suite)
ok_rules = all(not all(t.get(p) == v for p, v in r.terms) for t in suite for r in forb)
v = {p: z3.Int(f"x_{i}") for i, p in enumerate(names)}
s = z3.Solver()
for p in names: s.add(v[p] >= 0, v[p] < len(params[p]))
for r in forb:
    lits = [v[p] == params[p].index(x) for p, x in r.terms if p in params and x in params[p]]
    if len(lits) == len(r.terms): s.add(z3.Not(z3.And(*lits)))
eq = lambda i: v[i[0]] == params[i[0]].index(i[1])
feas = []
for a, b in itertools.combinations(names, 2):
    for x in params[a]:
        for y in params[b]:
            if s.check(eq((a, x)), eq((b, y))) == z3.sat: feas.append(((a, x), (b, y)))
groups = collections.defaultdict(list); uncovered = 0
for it in feas:
    sig = tuple(all(t[p] == x for p, x in it) for t in suite)
    if any(sig): groups[sig].append(it)
    else: uncovered += 1
avoidable = inseparable = 0
for g in groups.values():
    for i, j in itertools.combinations(g, 2):
        ci = z3.And(eq(i[0]), eq(i[1])); cj = z3.And(eq(j[0]), eq(j[1]))
        if s.check(ci, z3.Not(cj)) == z3.sat or s.check(cj, z3.Not(ci)) == z3.sat: avoidable += 1
        else: inseparable += 1
print(json.dumps({"model": name, "mode": d["mode"], "seed": d["seed"], "size": len(suite), "tests_domain_ok": ok_domain, "tests_rules_ok": ok_rules,
                  "feasible_pairs": len(feas), "uncovered": uncovered, "avoidable_collisions": avoidable, "inseparable_pairs_left": inseparable,
                  "is_CLA_1bar_2": ok_domain and ok_rules and uncovered == 0 and avoidable == 0}))
