"""Re-run headline results on your own machine and compare them with the cloud (sandbox) numbers.

Usage (PowerShell, repo root):
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py quick            # about 20 to 30 minutes, examples/ only
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py spins            # about 45 minutes, needs ..\\external\\CCAG
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py long             # about 1.6 hours (apache + gcc locating, seed 0)
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py rq5              # RQ5, about 30 to 60 minutes, needs python-sat
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py sim              # RQ5 simulations (items 73, 74), needs python-sat
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py speed            # 5 minutes: search throughput (moves per second), gcc
  .\\.venv\\Scripts\\python.exe scripts\\reproduce.py realbug          # item 85: two real CPython bugs, a few minutes
  add  --ccag PATH  if the CCAG benchmark folder is not ..\\external\\CCAG\\benchmark

Needs z3-solver (pip install z3-solver); tier rq5 also needs python-sat (pip install python-sat).

Tier rq5 (items 75 to 78) re-runs every mutant of the two programs (textwrap and configparser, copied in docs/item75 and
docs/item76) on every valid configuration, re-verifies the committed suites, and re-runs the diagnosis evaluation and the
200-draw random control on the new mutant results. It does NOT re-search the suites (capped searches depend on machine
speed); it compares every number with the committed cloud files. A different Python version can change library
behaviour, so mismatching mutants are counted and reported, not hidden. Mutants that loop forever are stopped after
STAGEB_TIMEOUT seconds (environment variable, default 180).
 Runs the same scripts the cloud runs used, one at a time, verifies every suite
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
D2_T2 = [17, 22, None, 11, 15, 22, 17]  # item 65 exact (2bar, 2) minima; model_8param (26, item 70 by SAT) skipped: Z3 does not finish
T3_SEED0 = {"cover": [12, 12, 14, 9, 10, 15, 10], "locate": [17, 22, 27, 11, 15, 22, 17]}  # item 62, seed 0


SPEED_CLOUD = "66 (sandbox 2026-11-09: 400 moves in 300 s, 1.3 moves/s)"  # PROJECT_NOTES item 84


def run(args, env):
    p = subprocess.run([sys.executable] + args, cwd=ROOT, env=env, capture_output=True, text=True)
    lines = [l for l in p.stdout.splitlines() if l.startswith("{")]
    if p.returncode != 0 or not lines:
        raise RuntimeError(f"{' '.join(args)} failed:\n{p.stdout[-2000:]}\n{p.stderr[-2000:]}")
    return [json.loads(l) for l in lines]


RQ5 = [  # name, committed folder, model file, mutant runner, covering-SAT start size
    ("textwrap", "docs/item75", "docs/item75/textwrap_model.json", "scripts/stageb/tw_mutants.py", 12),
    ("configparser", "docs/item76", "docs/item76/configparser_model.json", "scripts/stageb/cp_mutants.py", 9)]


def run_to_file(args, env, out):
    """Run a script whose stdout is one (possibly multi-line) JSON document; save it to out and return it."""
    p = subprocess.run([sys.executable] + args, cwd=ROOT, env=env, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed:\n{p.stderr[-2000:]}")
    with open(out, "w", encoding="utf-8") as f:
        f.write(p.stdout)
    return json.loads(p.stdout)


def rq5(env, note):
    d = os.path.join(ROOT, "results", "reproduce_rq5")
    os.makedirs(d, exist_ok=True)
    for name, folder, model, runner, cover_k in RQ5:
        src = lambda f: os.path.join(ROOT, folder, f)
        mut = os.path.join(d, f"{name}_mutants.jsonl")
        if os.path.exists(mut):
            os.remove(mut)
        p = subprocess.run([sys.executable, "-I", runner, mut, "--isolated"], cwd=ROOT, env=env, capture_output=True,
                           text=True)
        if p.returncode != 0:
            raise RuntimeError(f"{runner} failed:\n{p.stderr[-2000:]}")
        load = lambda f: {r["id"]: r for r in map(json.loads, open(f, encoding="utf-8"))}
        new, old = load(mut), load(src("mutants.jsonl"))
        cls = lambda r: ("ok", tuple(r["failing"])) if r["status"] == "ok" else ("excluded",)
        same = sum(i in new and cls(new[i]) == cls(old[i]) for i in old)
        sec = f"Stage B, {name} (item {folder[-2:]})"
        note(f"{name}: mutants with the same failing configurations as the cloud run", f"{same} of {len(old)}",
             f"{len(old)} of {len(old)}", sec, None)
        for suite in ("suite_L1.json", "suite_L2.json", "suite_L2_s1.json", "suite_L2_s2.json", "suite_L13.json"):
            v = run(["scripts/item65_verify.py", model, os.path.join(folder, suite)], env)[-1]
            note(f"{name}: {suite} size", v["size"], json.load(open(src(suite)))["suite"].__len__(), sec, v["ok"])
        ev = run_to_file(["scripts/stageb/tw_evaluate.py", mut, os.path.join(folder, "suite_L1.json"),
                          os.path.join(folder, "suite_L2.json"), "--cover-k", str(cover_k), "--model", model], env,
                         os.path.join(d, f"{name}_evaluation.json"))
        ev0 = json.load(open(src("evaluation.json")))
        note(f"{name}: configuration-dependent mutants", ev["config_dependent"], ev0["config_dependent"], sec, None)
        for k in ("C/all", "L1/all", "L2/all"):
            for o in ("correct", "misleading", "flagged"):
                note(f"{name}: {k} {o}", ev["summary"][k][o], ev0["summary"][k][o], sec, None)
        c200 = os.path.join(d, f"{name}_controls200.json")
        run_to_file(["scripts/stageb/controls.py", "--model", model, "--mutants", mut, "--l2",
                     os.path.join(folder, "suite_L2.json"), "--l13", os.path.join(folder, "suite_L13.json"),
                     "--seeds", "200"], env, c200)
        seeds = []
        for s_ in (1, 2):
            out = os.path.join(d, f"{name}_controls_L2_s{s_}.json")
            run_to_file(["scripts/stageb/controls.py", "--model", model, "--mutants", mut, "--l2",
                         os.path.join(folder, f"suite_L2_s{s_}.json"), "--l13", os.path.join(folder, "suite_L13.json"),
                         "--seeds", "0"], env, out)
            seeds.append(out)
        st = run_to_file(["scripts/stageb/stats.py", c200] + seeds, env, os.path.join(d, f"{name}_stats.json"))
        st0 = json.load(open(src("stats.json")))
        sec78 = "RQ5 controls with 200 random draws (item 78)"
        for m in ("per_mutant/correct", "per_mutant/misleading"):
            note(f"{name}: random suites, mean {m}", st["metrics"][m]["mean"], st0["metrics"][m]["mean"], sec78, None)
            note(f"{name}: L2 seeds 0/1/2 {m}", "/".join(str(x["value"]) for x in st["metrics"][m]["l2"]),
                 "/".join(str(x["value"]) for x in st0["metrics"][m]["l2"]), sec78, None)


def d2_suite(m):
    return "docs/item70/model_8param_t2_d2_size26.json" if m == "model_8param" else f"docs/item65_suites/{m}_t2_d2.json"


REALBUG = [  # name, subject, buggy source, fixed source, committed run file, model, committed suites folder, cover start
    ("configparser gh-130941, original inputs", "cp", "docs/item85/configparser_gh130941_buggy.py",
     "docs/item85/configparser_gh130941_fixed.py", "cp_corpus", "docs/item76/configparser_model.json", "docs/item76", 9),
    ("configparser gh-130941, + regression-test input", "cp", "docs/item85/configparser_gh130941_buggy.py",
     "docs/item85/configparser_gh130941_fixed.py", "cp_regression", "docs/item76/configparser_model.json", "docs/item76", 9),
    ("textwrap gh-139065, original inputs", "tw", "docs/item85/textwrap_gh139065_buggy_py313.py",
     "docs/item85/textwrap_gh139065_fixed_py313.py", "tw_corpus", "docs/item75/textwrap_model.json", "docs/item75", 12),
    ("textwrap gh-139065, + regression-test input", "tw", "docs/item85/textwrap_gh139065_buggy_py313.py",
     "docs/item85/textwrap_gh139065_fixed_py313.py", "tw_regression", "docs/item75/textwrap_model.json", "docs/item75", 12)]


def realbug(env, note):
    """Item 85: re-run the two real CPython bugs (buggy source = parent of the fix commit, reference = the fix commit)
    with the committed suites, and compare the failing configurations, each suite's outcome, and the pair the one-fault
    suite names for the configparser bug with the committed files in docs/item85."""
    d = os.path.join(ROOT, "results", "reproduce_realbug")
    os.makedirs(d, exist_ok=True)
    sec = "Two real historical CPython bugs (item 85)"
    for label, subject, buggy, fixed, run_name, model, folder, cover_k in REALBUG:
        committed = json.loads(open(os.path.join(ROOT, "docs", "item85", f"{run_name}.jsonl"), encoding="utf-8").readline())
        out = os.path.join(d, f"{run_name}.jsonl")
        args = ["-I", "scripts/stageb/realbug.py", "--subject", subject, "--buggy", buggy, "--fixed", fixed, "--out", out]
        for text in committed.get("extra_texts", []):  # the same inputs as the committed run
            args += ["--extra-text", text]
        run(args, env)
        new = json.loads(open(out, encoding="utf-8").readline())
        note(f"{label}: failing configurations", new["n_fail"], committed["n_fail"], sec, None)
        note(f"{label}: same failing configurations as the cloud run", new["failing"] == committed["failing"], True, sec,
             None)
        if not new["n_fail"]:
            continue
        ev = run_to_file(["scripts/stageb/tw_evaluate.py", out, os.path.join(folder, "suite_L1.json"),
                          os.path.join(folder, "suite_L2.json"), "--cover-k", str(cover_k), "--model", model], env,
                         os.path.join(d, f"{run_name}_evaluation.json"))
        ev0 = json.load(open(os.path.join(ROOT, "docs", "item85", f"{run_name}_evaluation.json"), encoding="utf-8"))
        got = {p["suite"]: p["outcome"] for p in ev["per_mutant"]}
        want = {p["suite"]: p["outcome"] for p in ev0["per_mutant"]}
        for suite in ("C", "L1", "L2"):
            note(f"{label}: suite {suite} outcome", got[suite], want[suite], sec, None)
        if run_name == "cp_regression":
            note(f"{label}: pair named by the one-fault suite", named_pair(model, folder, set(new["failing"])),
                 "allow_no_value=T + interpolation=extended", sec, None)


def named_pair(model, folder, failing):
    """The pair(s) whose tests in the one-fault suite are exactly the failing tests (the one-pair decoder)."""
    sys.path.insert(0, ROOT)
    from cla_harness.io import load_model
    from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
    configs = valid_configurations(*load_model(os.path.join(ROOT, model)))
    key = lambda c: tuple(sorted(c.items()))
    index = {key(c): k for k, c in enumerate(configs)}
    suite = [index[key(c)] for c in json.load(open(os.path.join(ROOT, folder, "suite_L1.json")))["suite"]]
    failing_rows = [r for r, k in enumerate(suite) if k in failing]
    names = []
    for p in feasible_interactions(configs, 2):
        if [r for r, k in enumerate(suite) if contains_interaction(configs[k], p)] == failing_rows:
            names.append(" + ".join(f"{a}={v}" for a, v in sorted(p)))
    return "; ".join(sorted(names)) or "none"


def sim(env, note):
    """Items 73 and 74: re-run the robustness simulation (seed 0, 2000 samples) and the exhaustive claim check, and
    compare every output line with the committed one (fixed seeds, so they should be identical)."""
    d = os.path.join(ROOT, "results", "reproduce_sim")
    os.makedirs(d, exist_ok=True)
    key = lambda r: (r["model"], r["suite"], r.get("scenario", r.get("fault_strength")))
    for m in SMALL + ["model_spins_core"]:
        if m == "model_spins_core":
            extra = ["--d1", "docs/item65_suites/search_spins_core_t2_d1_s0.json",
                     "--d2", "docs/item65_suites/search_spins_core_t2_d2_s0.json", "--cover-k", "18"]
        else:
            extra = ["--d2", d2_suite(m)]
        new = run(["scripts/item73_robust.py", f"examples/{m}.json"] + extra, env)
        old = [json.loads(l) for l in open(os.path.join(ROOT, "docs", "item73", f"{m}.jsonl"), encoding="utf-8")]
        oldk = {key(r): r for r in old}
        same = sum(oldk.get(key(r)) == r for r in new)
        note(f"item 73 simulation, {m}: identical output rows", f"{same} of {len(new)}", f"{len(old)} of {len(old)}",
             "When faults break the assumptions (item 73)", None)
    old = {key(r): r for r in map(json.loads, open(os.path.join(ROOT, "docs", "item74", "claim_small.jsonl"),
                                                   encoding="utf-8"))}
    for m in SMALL:
        new = run(["scripts/item74_check_claim.py", f"examples/{m}.json", f"docs/item74/{m}_L1.json", d2_suite(m)], env)
        for r in new:
            o = old[key(r)]
            note(f"item 74 claim check, {m}, {r['suite']}, fault strength {r['fault_strength']}: violations",
                 r["violations"], o["violations"], "The item 73 guarantee (item 74)", None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tier", choices=["quick", "spins", "long", "rq5", "sim", "speed", "realbug"])
    ap.add_argument("--ccag", default=os.path.join(ROOT, "..", "external", "CCAG", "benchmark"))
    a = ap.parse_args()
    # PYTHONHASHSEED=0 makes searches repeatable run to run: without it, Python's per-process string-hash randomization
    # changes set iteration order and so the search path, even with the same seed (item 84). Cloud runs before item 84
    # used random hash seeds, so a finished search can legitimately differ from its cloud value by run-to-run variation.
    env = dict(os.environ, PYTHONPATH=ROOT, PYTHONHASHSEED="0")
    os.makedirs(OUT, exist_ok=True)
    rows = []  # (what, measured, cloud, source, verified)

    def note(*row):
        rows.append(row)
        print(" | ".join(str(x) for x in row), flush=True)

    if a.tier == "rq5":
        rq5(env, note)
    elif a.tier == "sim":
        sim(env, note)
    elif a.tier == "realbug":
        realbug(env, note)
    elif a.tier == "quick":
        for (t, mode), sizes in EXACT.items():
            for name, cloud in zip(SMALL, sizes):
                r = run(["scripts/item63_exact.py", f"examples/{name}.json", str(t), mode, "1800"], env)[-1]
                got = r.get("size", f"z3 {r['z3']}")
                note(f"exact minimum, {name}, t={t}, {mode}", got, cloud, "Exact minimum sizes on the small models (item 63)",
                     r.get("check_ok"))
        for name, cloud in zip(SMALL, D2_T2):
            if cloud is None:
                continue
            out = os.path.join(OUT, f"d2_t2_{name}.json")
            r = run(["scripts/item65_exact.py", f"examples/{name}.json", "2", "2", "1800", out], env)[-1]
            v = run(["scripts/item65_verify.py", f"examples/{name}.json", out], env)[-1] if "size" in r else {"ok": None}
            note(f"exact minimum, {name}, t=2, d=2 (two faults)", r.get("size", f"z3 {r['z3']}"), cloud,
                 "Two faults (d = 2): exact minima and a search (item 65)", v["ok"])
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
                         ("gcc", "locate", 68, 2495, "54 to 55", "Ten seeds on apache, gcc and Insurance (item 60)")],
                # item 84: same search as the long tier, gcc seed 0, but capped at 300 s; compare total moves (and moves
                # per second) with the cloud value to tell machine throughput apart from search behaviour
                "speed": [("gcc", "locate", 68, 300, SPEED_CLOUD, "Search throughput on two machines (item 84)")]}[a.tier]
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
            moves = r.get("total_moves")
            rate = f", {moves} moves, {moves / max(r['elapsed_s'], 1e-9):.1f} moves/s" if moves is not None else ""
            note(f"search t=2, {name}, {mode}, seed 0, cap {cap} s ({status}, {r['elapsed_s']} s{rate})", r["size"], cloud,
                 source, ok)

    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    try:
        import z3
        z3v = z3.get_version_string()
    except ImportError:
        z3v = "not installed"
    path = os.path.join(ROOT, "results", f"reproduce_{a.tier}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Re-run of tier {a.tier} on this machine (label it \"reproduced locally\" only if this is the author's "
                f"machine)\n\n{datetime.datetime.now():%Y-%m-%d %H:%M}, commit {git}, "
                f"{platform.platform()}, {platform.processor() or 'cpu unknown'}, {os.cpu_count()} logical cores, "
                f"Python {platform.python_version()}, z3 {z3v}. One seed per row.\n\n"
                "| what | this run | cloud (sandbox) | PROJECT_NOTES section | suite verified |\n|---|---|---|---|---|\n")
        for row in rows:
            f.write("| " + " | ".join(str(x) for x in row) + " |\n")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
