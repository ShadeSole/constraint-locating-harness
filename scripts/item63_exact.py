"""Plan item 63: exact minimum covering / locating array size on a small JSON model, by MaxSAT over the valid configurations.
Usage: PYTHONPATH=. python3 scripts/item63_exact.py MODEL.json STRENGTH MODE [TIMEOUT_S] [OUT.json]
Each valid configuration is a Boolean "chosen". Every feasible t-way interaction needs a chosen test containing it; in
locate mode every pair of interactions whose signatures over ALL valid configurations differ needs a chosen test that
contains exactly one of them (inseparable pairs are exempt). Z3's Optimize minimizes the number chosen; "optimal" means
Z3 finished, so that size is a proven minimum. The returned suite is re-checked with annealing.suite_cost (cover: 0 uncovered;
locate: cost 0)."""
import json, sys, time
import z3
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
from cla_harness.annealing import suite_cost, unavoidable_pairs
path, t, mode = sys.argv[1], int(sys.argv[2]), sys.argv[3]
timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 600
start = time.time()
params, forb = load_model(path)
configs = valid_configurations(params, forb)
inter = sorted(feasible_interactions(configs, t), key=sorted)
masks = [sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i)) for i in inter]
clauses = set(masks)
if mode == "locate":
    for a in range(len(masks)):
        for b in range(a + 1, len(masks)):
            if masks[a] != masks[b]:
                clauses.add(masks[a] ^ masks[b])
x = [z3.Bool(f"c{k}") for k in range(len(configs))]
opt = z3.Optimize()
opt.set("timeout", int(timeout * 1000))
for m in clauses:
    opt.add(z3.Or([x[k] for k in range(len(configs)) if m >> k & 1]))
for v in x:
    opt.add_soft(z3.Not(v))
result = opt.check()
out = {"model": path.split("/")[-1], "strength": t, "mode": mode, "configs": len(configs), "interactions": len(inter),
       "clauses": len(clauses), "z3": str(result), "seconds": round(time.time() - start, 1)}
if result == z3.sat:
    model = opt.model()
    suite = [c for k, c in enumerate(configs) if z3.is_true(model.eval(x[k], model_completion=True))]
    cost = suite_cost(suite, set(inter), set() if mode == "cover" else unavoidable_pairs(configs, set(inter)))
    check = cost["uncovered"] if mode == "cover" else cost["cost"]
    out.update({"size": len(suite), "check_ok": check == 0})
    if len(sys.argv) > 5:
        json.dump({"model": out["model"], "strength": t, "mode": mode, "seed": None, "suite": suite},
                  open(sys.argv[5], "w"), indent=1)
print(json.dumps(out))
