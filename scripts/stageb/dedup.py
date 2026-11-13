"""Stage B: diagnosis outcomes counted once per DISTINCT failure set (mutants with identical failure sets give
identical outcomes, so they are counted once). Usage: python3 scripts/stageb/dedup.py MUTANTS.jsonl EVALUATION.json"""
import json, sys
from collections import Counter
mut = {m["id"]: frozenset(m.get("failing", [])) for m in map(json.loads, open(sys.argv[1]))}
ev = json.load(open(sys.argv[2]))
for s in ("C", "L1", "L2"):
    seen = {}
    for p in ev["per_mutant"]:
        if p["suite"] == s:
            seen.setdefault(mut[p["mutant"]], (p["outcome"], p["type"]))
    c = Counter(o for o, _ in seen.values())
    t = Counter(ty for _, ty in seen.values())
    print(json.dumps({"suite": s, "distinct_sets": len(seen), "outcomes": dict(c), "types": dict(t)}))
