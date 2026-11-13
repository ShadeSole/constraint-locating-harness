"""Plan item 71: a lower bound on the (dbar, t) locating array size from the t-way covering minimum.
Usage: PYTHONPATH=. python3 scripts/item71_cover_bound.py MODEL.json STRENGTH K TIMEOUT_S
Decides "is there a t-way covering array of at most K valid configurations?" with CaDiCaL (PySAT) and a sequential-counter
cardinality constraint. Every locating array covers every feasible t-way interaction, so UNSAT at K proves that any
locating array of that strength needs at least K + 1 tests. Prints one JSON line (sat / unsat / timeout)."""
import json, sys, time, threading
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
path, t, K, timeout = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
start = time.time()
configs = valid_configurations(*load_model(path))
n = len(configs)
inter = feasible_interactions(configs, t)
card = CardEnc.atmost(list(range(1, n + 1)), bound=K, top_id=n, encoding=EncType.seqcounter)
s = Solver(name="cadical195", bootstrap_with=card.clauses)
for i in inter:
    s.add_clause([k + 1 for k, c in enumerate(configs) if contains_interaction(c, i)])
timer = threading.Timer(timeout, s.interrupt)
timer.start()
r = s.solve_limited(expect_interrupt=True)
timer.cancel()
out = {"model": path.split("/")[-1], "strength": t, "K": K, "configs": n, "interactions": len(inter),
       "result": {True: "sat", False: "unsat", None: "timeout"}[r], "seconds": round(time.time() - start, 1)}
if r:
    out["size"] = sum(1 for v in s.get_model()[:n] if v > 0)
print(json.dumps(out), flush=True)
