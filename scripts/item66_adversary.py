"""Plan item 66: adversarial search for a suite that is (1bar, 3)-locating but NOT (2bar, 2)-locating.
Usage: PYTHONPATH=. python3 scripts/item66_adversary.py MODEL(K binary unconstrained as "binK", or a JSON path) START SEED STEPS
Starts from a small (1bar, 3) array found by cla_harness.multifault (start START, 1500 x 2 per size), then makes random
moves (swap one test for an unchosen valid configuration, drop a test, or add one) and keeps a move when it does not
worsen (cost13, -min(cost22, 50)) lexicographically, plus an occasional random accept. Stops when cost13 = 0 and
cost22 > 0 (a counterexample), printing it, or after STEPS moves."""
import json, random, sys
from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.io import load_model
from cla_harness.multifault import MultiFaultModel, find_small_multifault
spec, start, seed, steps = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
if spec.startswith("bin"):
    params, forb = {f"p{j}": ["0", "1"] for j in range(int(spec[3:]))}, []
else:
    params, forb = load_model(spec)
configs = valid_configurations(params, forb)
m13 = MultiFaultModel(configs, feasible_interactions(configs, 3), 1)
m22 = MultiFaultModel(configs, feasible_interactions(configs, 2), 2)
r = find_small_multifault(m13, min(start, len(configs)), seed, 1500, 2)
chosen = set(r["indices"])
rng = random.Random(seed)
def energy(s):
    mask = sum(1 << c for c in s)
    return (m13.cost(mask)["cost"], -min(m22.cost(mask)["cost"], 50))
e = energy(chosen)
found = None
for step in range(steps):
    trial = set(chosen)
    move = rng.random()
    outside = [c for c in range(len(configs)) if c not in trial]
    if move < 0.6 and outside and trial:
        trial.remove(rng.choice(sorted(trial))); trial.add(rng.choice(outside))
    elif move < 0.8 and len(trial) > 1:
        trial.remove(rng.choice(sorted(trial)))
    elif outside:
        trial.add(rng.choice(outside))
    et = energy(trial)
    if et <= e or rng.random() < 0.02:
        chosen, e = trial, et
    if e[0] == 0 and e[1] < 0:
        found = sorted(chosen)
        break
out = {"model": spec, "seed": seed, "start_size": r["size"], "steps": step + 1, "final_cost13": e[0], "final_cost22": -e[1],
       "counterexample": found is not None}
if found:
    out["suite"] = [configs[c] for c in found]
print(json.dumps(out))
