"""Plan item 66: do the (2bar, 2) and (1bar, 3) constrained locating conditions agree on arbitrary suites?
Usage: PYTHONPATH=. python3 scripts/item66_equiv.py N_MODELS SUITES_PER_MODEL SEED MAX_VALUES
Random models: 3 to 6 parameters, 2 to MAX_VALUES values each, 0 to 4 forbidden value pairs (at most 200 valid
configurations). For each model, random subsets of the valid configurations (size uniform in 1..all) are scored with
cla_harness.multifault: d = 2 at t = 2 and d = 1 at t = 3. Counts suites where exactly one condition holds."""
import json, random, sys
from cla_harness.core import Forbidden, valid_configurations, feasible_interactions
from cla_harness.multifault import MultiFaultModel
n_models, per, seed, maxv = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
totals = {"models": 0, "suites": 0, "both": 0, "neither": 0, "only_d2t2": 0, "only_d1t3": 0}
examples = []
for k in range(n_models):
    rng = random.Random(seed * 100000 + k)
    params = {f"p{j}": [f"v{v}" for v in range(rng.randint(2, maxv))] for j in range(rng.randint(3, 6))}
    forbidden = []
    for _ in range(rng.randint(0, 4)):
        a, b = rng.sample(sorted(params), 2)
        forbidden.append(Forbidden.from_dict({a: rng.choice(params[a]), b: rng.choice(params[b])}))
    configs = valid_configurations(params, forbidden)
    if not 1 <= len(configs) <= 200:
        continue
    totals["models"] += 1
    m22 = MultiFaultModel(configs, feasible_interactions(configs, 2), 2)
    m13 = MultiFaultModel(configs, feasible_interactions(configs, 3), 1)
    for _ in range(per):
        chosen = sum(1 << c for c in rng.sample(range(len(configs)), rng.randint(1, len(configs))))
        a = m22.cost(chosen)["cost"] == 0
        b = m13.cost(chosen)["cost"] == 0
        totals["suites"] += 1
        key = "both" if a and b else "neither" if not (a or b) else "only_d2t2" if a else "only_d1t3"
        totals[key] += 1
        if key.startswith("only") and len(examples) < 5:
            examples.append({"k": k, "levels": [len(v) for v in params.values()], "forbidden": len(forbidden), "which": key})
print(json.dumps({"seed": seed, "max_values": maxv, **totals, "examples": examples}))
