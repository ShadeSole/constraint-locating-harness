"""Plan item 66: stress test on near-minimal suites. For random models, search (cla_harness.multifault) for a small
(1bar, 3) array and check it against (2bar, 2); and for a small (2bar, 2) array and check it against (1bar, 3).
Usage: PYTHONPATH=. python3 scripts/item66_stress.py N_MODELS SEED MAX_VALUES MAX_PARAMS [MAX_CONFIGS]
Random models: 3 to MAX_PARAMS parameters, 2 to MAX_VALUES values, 0 to 6 forbidden value pairs, at most 250 valid
configurations (MAX_CONFIGS, default 250). Search: start = all valid configurations, 1500 moves x 2 restarts per size. Prints one line per model."""
import json, random, sys
from cla_harness.core import Forbidden, valid_configurations, feasible_interactions
from cla_harness.multifault import MultiFaultModel, find_small_multifault
n_models, seed, maxv, maxp = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
max_configs = int(sys.argv[5]) if len(sys.argv) > 5 else 250
summary = {"models": 0, "d1t3_arrays_failing_d2t2": 0, "d2t2_arrays_failing_d1t3": 0}
for k in range(n_models):
    rng = random.Random(seed * 100000 + k)
    params = {f"p{j}": [f"v{v}" for v in range(rng.randint(2, maxv))] for j in range(rng.randint(3, maxp))}
    forbidden = []
    for _ in range(rng.randint(0, 6)):
        a, b = rng.sample(sorted(params), 2)
        forbidden.append(Forbidden.from_dict({a: rng.choice(params[a]), b: rng.choice(params[b])}))
    configs = valid_configurations(params, forbidden)
    if not 4 <= len(configs) <= max_configs:
        continue
    summary["models"] += 1
    m22 = MultiFaultModel(configs, feasible_interactions(configs, 2), 2)
    m13 = MultiFaultModel(configs, feasible_interactions(configs, 3), 1)
    row = {"k": k, "levels": [len(v) for v in params.values()], "forbidden": len(forbidden), "configs": len(configs)}
    for name, search, other, key in (("d1t3", m13, m22, "d1t3_arrays_failing_d2t2"), ("d2t2", m22, m13, "d2t2_arrays_failing_d1t3")):
        r = find_small_multifault(search, len(configs), seed=k, steps_per_restart=1500, restarts=2)
        chosen = sum(1 << c for c in r["indices"])
        holds = other.cost(chosen)["cost"] == 0
        row[name] = {"size": r["size"], "passes_other": holds}
        if not holds:
            summary[key] += 1
            row[name]["suite"] = r["indices"]
    print(json.dumps(row), flush=True)
print(json.dumps({"summary": summary, "seed": seed, "max_values": maxv, "max_params": maxp}), flush=True)
