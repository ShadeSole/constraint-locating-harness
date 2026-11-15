"""Plan item 66: does a small (1bar, 3) array on an unconstrained binary model with many parameters also satisfy
(2bar, 2)? Usage: PYTHONPATH=. python3 scripts/item66_sparse.py K START SEED
Model: K binary parameters, no constraints (2^K configurations). Search with cla_harness.multifault for a (1bar, 3)
array from START tests (1500 moves x 2 restarts per size), then score it against (2bar, 2) and print one colliding
pair of fault sets if it fails."""
import json, random, sys
from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.multifault import MultiFaultModel, find_small_multifault
k, start, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
params = {f"p{j}": ["0", "1"] for j in range(k)}
configs = valid_configurations(params, [])
m13 = MultiFaultModel(configs, feasible_interactions(configs, 3), 1)
m22 = MultiFaultModel(configs, feasible_interactions(configs, 2), 2)
r = find_small_multifault(m13, start, seed, 1500, 2)
out = {"k": k, "seed": seed, "start": start, "d1t3_size": r["size"]}
if r["indices"]:
    chosen = sum(1 << c for c in r["indices"])
    cost = m22.cost(chosen)
    out["d2t2_cost_of_that_array"] = cost
    if cost["cost"]:
        out["example_problem_mask"] = bin(m22.problems(chosen, random.Random(0)))
        out["suite"] = [configs[c] for c in r["indices"]]
print(json.dumps(out))
