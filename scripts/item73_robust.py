"""Plan item 73 (Stage A of the real-use study): how do locating arrays behave when faults break their assumptions?
Usage: PYTHONPATH=. python3 scripts/item73_robust.py MODEL.json [--samples N] [--seed S] [--d1 SUITE.json] [--d2 SUITE.json]
       [--cover-k K] > out.jsonl

Suites (t = 2). Unless a file is given, each minimum is found here by SAT, ascending K until SAT:
  C  minimum 2-way covering suite;
  L1 minimum (1bar, 2) constrained locating array (via scripts/item69_decide.py);
  L2 (2bar, 2) array from --d2 (default: none).
Each suite is decoded with the decoder it was built for: C and L1 with a one-pair decoder, L2 with an up-to-two-pairs
decoder. Fault scenarios (deterministic unless stated): P1 one faulty pair (all pairs), P2 two pairs, P3 three pairs,
T1 one faulty 3-way interaction, N05 / N10 one faulty pair with each test outcome flipped with probability 0.05 / 0.10
(nearest-signature decoding). Outcome per fault:
  correct   every candidate explanation is equivalent to the true fault set over ALL valid configurations
  ambiguous candidates include an equivalent explanation and at least one that is not
  wrong     at least one candidate, none equivalent: the decoder confidently points at the wrong cause
  flagged   no explanation matches: the decoder can tell the result is outside its model
  missed    no test failed
"""
import json, random, subprocess, sys, os, tempfile
from itertools import combinations
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction

args = sys.argv[1:]
def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default
path = args[0]
samples, seed = int(opt("--samples", 2000)), int(opt("--seed", 0))
rng = random.Random(seed)
params, forb = load_model(path)
configs = valid_configurations(params, forb)
n = len(configs)
pairs = sorted(feasible_interactions(configs, 2), key=sorted)
triples = sorted(feasible_interactions(configs, 3), key=sorted)
gmask = {}
for i in pairs + triples:
    gmask[i] = sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i))
key = lambda c: tuple(sorted(c.items()))
index = {key(c): k for k, c in enumerate(configs)}

def min_cover(start_k):
    k = start_k
    while True:
        card = CardEnc.atmost(list(range(1, n + 1)), bound=k, top_id=n, encoding=EncType.seqcounter)
        s = Solver(name="cadical195", bootstrap_with=card.clauses)
        for i in pairs:
            s.add_clause([b + 1 for b in range(n) if gmask[i] >> b & 1])
        if s.solve():
            return [configs[b] for b in range(n) if s.get_model()[b] > 0]
        k += 1

def min_locate():
    k = 1
    while True:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            out = f.name
        r = subprocess.run([sys.executable, "scripts/item69_decide.py", path, "2", "1", str(k), out],
                           capture_output=True, text=True, env=dict(os.environ, PYTHONPATH="."))
        last = json.loads(r.stdout.strip().splitlines()[-1])
        if last["result"] == "sat":
            return json.load(open(out))["suite"]
        k += 1

def load_suite(p):
    return json.load(open(p))["suite"]

suites = {}
suites["C"] = (min_cover(int(opt("--cover-k", 1))), 1)
suites["L1"] = (load_suite(opt("--d1")) if opt("--d1") else min_locate(), 1)
if opt("--d2"):
    suites["L2"] = (load_suite(opt("--d2")), 2)

def build(suite, d):
    rows = {i: sum(1 << r for r, c in enumerate(suite) if contains_interaction(c, i)) for i in pairs + triples}
    table = {}
    for i in pairs:
        table.setdefault(rows[i], []).append((i,))
    if d == 2:
        for a, b in combinations(pairs, 2):
            table.setdefault(rows[a] | rows[b], []).append((a, b))
    return rows, table

def g(fs):
    m = 0
    for i in fs:
        m |= gmask[i]
    return m

def classify(cands, truth_g, failed):
    if not failed:
        return "missed"
    if not cands:
        return "flagged"
    eq = [g(c) == truth_g for c in cands]
    return "correct" if all(eq) else ("ambiguous" if any(eq) else "wrong")

scen = {"P1": [(p,) for p in pairs],
        "P2": [tuple(rng.sample(pairs, 2)) for _ in range(samples)],
        "P3": [tuple(rng.sample(pairs, 3)) for _ in range(samples)],
        "T1": [(t,) for t in (triples if len(triples) <= samples else rng.sample(triples, samples))]}
model = os.path.basename(path)
for name, (suite, d) in suites.items():
    for c in suite:
        assert key(c) in index, "suite has an invalid test"
    rows, table = build(suite, d)
    N = len(suite)
    for sc, faults in scen.items():
        counts = dict.fromkeys(["correct", "ambiguous", "wrong", "flagged", "missed"], 0)
        for fs in faults:
            r = 0
            for i in fs:
                r |= rows[i]
            counts[classify(table.get(r, []), g(fs), r != 0)] += 1
        print(json.dumps({"model": model, "suite": name, "decoder_d": d, "size": N, "scenario": sc,
                          "faults": len(faults), **counts}), flush=True)
    for p_flip, sc in ((0.05, "N05"), (0.10, "N10")):
        counts = dict.fromkeys(["correct", "ambiguous", "wrong", "flagged", "missed"], 0)
        for _ in range(samples):
            f = rng.choice(pairs)
            r = rows[f] ^ sum(1 << b for b in range(N) if rng.random() < p_flip)
            if r == 0:
                counts["missed"] += 1
                continue
            dist = {i: bin(rows[i] ^ r).count("1") for i in pairs}
            best = min(dist.values())
            cands = [(i,) for i, v in dist.items() if v == best]
            counts[classify(cands, gmask[f], True)] += 1
        print(json.dumps({"model": model, "suite": name, "decoder_d": 1, "size": N, "scenario": sc,
                          "faults": samples, **counts}), flush=True)
