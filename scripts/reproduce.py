"""Re-run headline results on your own machine and compare them with the cloud (sandbox) numbers.

Usage (PowerShell, repo root):
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py quick            # about 10 to 20 minutes, examples/ only
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py spins            # about 45 minutes, needs ..\\external\\CCAG
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py long             # about 1.6 hours (apache + gcc locating, seed 0)
  add  --ccag PATH  if the CCAG benchmark folder is not ..\\external\\CCAG\\benchmark

Needs z3-solver (pip install z3-solver). Runs the same scripts the cloud runs used, one at a time, verifies every suite
with the independent checker, and writes results/reproduce_<tier>.md with each measured value next to the cloud value
and the PROJECT_NOTES section it came from. Search sizes depend on machine speed when a time cap is hit, so a capped
row that differs by a test or two is expected; exact minima (item 63) and finished searches should match.
"""
import argparse, datetime, json, os, platform, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "reproduce_suites")
SMALL = ["model", "model_6param", "model_8param", "model_high_constraints", "model_low_constraints",
         "model_multivalue", "my_model"]
# Cloud values, copied from docs/PROJECT_NOTES.md (section named in each row).
EXACT = {  # item 63, "Exact minimum sizes on the small models": (t, mode) -> size per model, in SMALL order
    (2, "cover"): [5, 6, 7, 6, 6, 7, 6], (2, "locate"): [9, 10, 11, 9, 8, 11, 8],
    (3, "cover"): [12, 12, 14, 9, 10, 15, 10], (3, "locate"): [17, 22, 26, 11, 15, 22, 17]}
T3_START = [17, 22, 29, 11, 15, 22, 17]  # item 62 start sizes
T3_SEED0 = {"cover": [12, 12, 14, 9, 10, 15, 10], "locate": [17, 22, 27, 11, 15, 22, 17]}  # item 62, seed 0


def run(args, env):
    p = subprocess.run([sys.executable] + args, cwd=ROOT, env=env, capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith("{")]
    if p.returncode != 0 or not lines:
        raise RuntimeError(f"{' '.join(args)} failed:\n{p.stdout[-2000:]}\n{p.stderr[-2000:]}")
    return [json.loads(l) for l in lines]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tier", choices=["quick", "spins", "long"])
    ap.add_argument("--ccag", default=os.path.join(ROOT, "..", "external", "CCAG", "benchmark"))
    a = ap.parse_args()
    env = dict(os.environ, PYTHONPATH=ROOT)
    os.makedirs(OUT, exist_ok=True)
    rows = []  # (what, measured, cloud, source, verified)

    def note(*row):
        rows.append(row)
        print(" | ".join(str(x) for x in row), flush=True)

    if a.tier == "quick":
        for (t, mode), sizes in EXACT.items():
            for name, cloud in zip(SMALL, sizes):
                r = run(["scripts/item63_exact.py", f"examples/{name}.json", str(t), mode, "1800"], env)[-1]
                got = r.get("size", f"z3 {r['z3']}")
                note(f"exact minimum, {name}, t={t}, {mode}", got, cloud, "Exact minimum sizes on the small models (item 63)",
                     r.get("check_ok"))
        for mode in ("cover", "locate"):
            for name, start, cloud in zip(SMALL, T3_START, T3_SEED0[mode]):
                out = os.path.join(OUT, f"t3_{mode}_{name}_s0.json")
                r = run(["scripts/item62_run.py", "examples", f"{name}.json", "3", mode, "local", "0", str(start), out,
                         "6000", "5", "60"], env)[-1]
                v = run(["scripts/item62_verify.py", "examples", out, "3"], env)[-1]
                note(f"search t=3, {name}, {mode}, seed 0, cap 60 s", r["size"], cloud,
                     "RQ1 at t = 3 with the local move (item 62)", v["ok"])
    else:
        jobs = {"spins": [("spins", "cover", 53, 600, 20, "Covering versus locating with the local move (item 61)"),
                          ("spins", "locate", 53, 600, 38, "Covering versus locating with the local move (item 61)"),
                          ("bugzilla", "cover", 48, 600, 16, "Covering versus locating with the local move (item 61)"),
                          ("bugzilla", "locate", 48, 600, 32, "Covering versus locating with the local move (item 61)")],
                "long": [("apache", "locate", 89, 3263, "67 to 69", "Ten seeds on apache, gcc and Insurance (item 60)"),
                         ("gcc", "locate", 68, 2495, "54 to 55", "Ten seeds on apache, gcc and Insurance (item 60)")]}[a.tier]
        if not os.path.exists(os.path.join(a.ccag, "spins.model")):
            sys.exit(f"CCAG benchmark folder not found at {a.ccag}; pass --ccag PATH")
        for name, mode, start, cap, cloud, source in jobs:
            out = os.path.join(OUT, f"t2_{mode}_{name}_s0.json")
            r = run(["scripts/item61_run.py", a.ccag, name, mode, "local", "0", str(start), out, "6000", "5", str(cap)],
                    env)[-1]
            if mode == "locate":
                ok = run(["scripts/item44_verify.py", a.ccag, out], env)[-1]["is_CLA_1bar_2"]
            else:
                ok = run(["scripts/item62_verify.py", a.ccag, out, "2"], env)[-1]["ok"]
            status = "capped" if r.get("timed_out") else "finished"
            note(f"search t=2, {name}, {mode}, seed 0, cap {cap} s ({status}, {r['elapsed_s']} s)", r["size"], cloud,
                 source, ok)

    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    try:
        import z3
        z3v = z3.get_version_string()
    except ImportError:
        z3v = "not installed"
    path = os.path.join(ROOT, "results", f"reproduce_{a.tier}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Reproduced locally: tier {a.tier}\n\n{datetime.datetime.now():%Y-%m-%d %H:%M}, commit {git}, "
                f"{platform.platform()}, {platform.processor() or 'cpu unknown'}, {os.cpu_count()} logical cores, "
                f"Python {platform.python_version()}, z3 {z3v}. One seed per row.\n\n"
                "| what | reproduced locally | cloud (sandbox) | PROJECT_NOTES section | suite verified |\n|---|---|---|---|---|\n")
        for row in rows:
            f.write("| " + " | ".join(str(x) for x in row) + " |\n")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
