"""Plan item 65: on random small models, compare the exact minimum (2bar, 2) and (1bar, 3) constrained locating array
sizes (scripts/item65_exact.py for both), to look for a model where they differ.
Usage: PYTHONPATH=. python3 scripts/item65_random.py N_MODELS SEED WORKDIR
Model k: 3 to 6 parameters with 2 to 3 values each, 0 to 4 forbidden pairs of values, from random.Random(SEED * 100000 + k);
models with more than 100 configurations before constraints are skipped (reported as skipped)."""
import json, os, random, subprocess, sys
n_models, seed, work = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
os.makedirs(work, exist_ok=True)
env = dict(os.environ, PYTHONPATH=os.getcwd())
for k in range(n_models):
    rng = random.Random(seed * 100000 + k)
    params = {f"p{j}": [f"v{v}" for v in range(rng.randint(2, 3))] for j in range(rng.randint(3, 6))}
    forbidden = []
    for _ in range(rng.randint(0, 4)):
        a, b = rng.sample(sorted(params), 2)
        forbidden.append({a: rng.choice(params[a]), b: rng.choice(params[b])})
    total = 1
    for v in params.values():
        total *= len(v)
    if total > 100:
        print(json.dumps({"k": k, "skipped": total}), flush=True)
        continue
    path = os.path.join(work, f"random_{seed}_{k}.json")
    json.dump({"parameters": params, "forbidden": forbidden}, open(path, "w"))
    res = {}
    for t, d in ((2, 2), (3, 1)):
        p = subprocess.run([sys.executable, "scripts/item65_exact.py", path, str(t), str(d), "600"], env=env,
                           capture_output=True, text=True)
        lines = [l for l in p.stdout.splitlines() if l.startswith("{")]
        res[f"t{t}d{d}"] = json.loads(lines[-1]) if lines else {"error": p.stderr[-300:]}
    a, b = res["t2d2"], res["t3d1"]
    print(json.dumps({"k": k, "params": [len(v) for v in params.values()], "forbidden": len(forbidden),
                      "configs": a.get("configs"), "t2d2": a.get("size", a.get("z3", a.get("error"))),
                      "t3d1": b.get("size", b.get("z3", b.get("error"))),
                      "equal": a.get("size") is not None and a.get("size") == b.get("size")}), flush=True)
