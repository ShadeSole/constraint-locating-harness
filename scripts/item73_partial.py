"""Plan item 73 check: are 'wrong' answers partly right? For T1 (faulty triple) and P2 (two faulty pairs), split
'wrong' into 'partial' (every candidate pair is contained in the true triple, or is one of the true pairs) and
'unrelated' (some candidate is not). Same suites and seeds as item73_robust.py.
Usage: PYTHONPATH=. python3 scripts/item73_partial.py MODEL.json [same suite options as item73_robust.py]"""
import sys, runpy, json
sys.argv = ["item73_robust.py"] + sys.argv[1:]
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    ns = runpy.run_path("scripts/item73_robust.py", run_name="item73")
g, build, scen, suites = ns["g"], ns["build"], ns["scen"], ns["suites"]
for name, (suite, d) in suites.items():
    rows, table = build(suite, d)
    for sc in ("P2", "T1"):
        part = unrel = 0
        for fs in scen[sc]:
            r = 0
            for i in fs:
                r |= rows[i]
            cands = table.get(r, [])
            if not r or not cands or any(g(c) == g(fs) for c in cands):
                continue
            inside = lambda c: all((p in fs) if sc == "P2" else (p <= fs[0]) for p in c)
            if all(inside(c) for c in cands):
                part += 1
            else:
                unrel += 1
        print(json.dumps({"model": ns["model"], "suite": name, "scenario": sc, "faults": len(scen[sc]),
                          "wrong_partial": part, "wrong_unrelated": unrel}), flush=True)
