"""Stage B statistics (plan item 78): (2bar, 2) suites against equal-size random suites.
Usage: python3 scripts/stageb/stats.py CONTROLS200.json L2_SEED_CONTROLS.json [more...]
CONTROLS200.json holds R0..R199 (random suites of the seed-0 L2 size, same up-to-two-pairs decoder) and L2 seed 0.
Each further file holds one more L2 suite under the key "L2" (controls.py run with --seeds 0).
For each metric (correct and misleading, per mutant and per distinct failure set) it prints the random distribution
(mean, 5th / 50th / 95th percentile, min, max) and, for each L2 suite, an empirical one-sided p-value:
  misleading: p = (1 + #random draws with misleading <= L2's) / (1 + N)
  correct:    p = (1 + #random draws with correct  >= L2's) / (1 + N)
A small p means few random suites of that size do as well as the L2 suite."""
import json, sys
base = json.load(open(sys.argv[1]))
rand = [v for k, v in base["suites"].items() if k.startswith("R")]
l2s = [("L2 seed 0", base["suites"]["L2"])]
for p in sys.argv[2:]:
    l2s.append((p.split("/")[-1].replace(".json", ""), json.load(open(p))["suites"]["L2"]))
N = len(rand)
out = {"model": base["model"], "random_draws": N, "random_size": rand[0]["size"], "metrics": {}}
for unit in ("per_mutant", "per_distinct_set"):
    for metric in ("correct", "misleading"):
        xs = sorted(r[unit][metric] for r in rand)
        q = lambda f: xs[min(N - 1, int(f * N))]
        row = {"mean": round(sum(xs) / N, 2), "p5": q(0.05), "median": q(0.5), "p95": q(0.95), "min": xs[0],
               "max": xs[-1], "l2": []}
        for name, s in l2s:
            v = s[unit][metric]
            better = sum(x <= v for x in xs) if metric == "misleading" else sum(x >= v for x in xs)
            row["l2"].append({"suite": name, "size": s["size"], "value": v, "p": round((1 + better) / (1 + N), 3)})
        out["metrics"][f"{unit}/{metric}"] = row
print(json.dumps(out, indent=1))
