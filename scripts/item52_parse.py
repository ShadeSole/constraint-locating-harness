"""Plan item 52: turn SA4LA's printed output into this repo's suite JSON so scripts/item44_verify.py can check it.
SA4LA (github.com/tatsuhirotsuchiya/SA4LA) ends with '__END <rows> <ms>' followed by the array, one row per line,
values as integers; parameters are P0.. and values "0".. as in load_casa_model.
Usage: python3 scripts/item52_parse.py SA4LA_LOG MODEL_NAME SEED OUT.json   (prints one JSON summary line)"""
import json, sys
log, name, seed, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
upper = next((l for l in lines if l.startswith("Suspect that the optimum")), "")
end = [i for i, l in enumerate(lines) if l.startswith("__END ")]
if not end:
    print(json.dumps({"model": name, "seed": seed, "error": "no __END line (run cut off or failed)", "upper_line": upper}))
    sys.exit(0)
_, rows, ms = lines[end[-1]].split()
suite = []
for l in lines[end[-1] + 1:]:
    vals = l.split()
    if not vals:
        if suite: break
        continue
    suite.append({f"P{j}": v for j, v in enumerate(vals)})
assert len(suite) == int(rows), (len(suite), rows)
json.dump({"model": name, "mode": "locate", "seed": seed, "size": len(suite), "suite": suite}, open(out, "w"))
bounds = upper[upper.find("[") + 1:upper.find("]")].split("..") if "[" in upper else ["", ""]
print(json.dumps({"model": name, "seed": seed, "size": len(suite), "time_s": int(ms) / 1000,
                  "lower": int(bounds[0]) if bounds[0] else None, "upper": int(bounds[1]) if bounds[1] else None}))
