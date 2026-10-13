"""Plan item 12: Z3 feasible 2-way interactions vs enumeration, one timed run each.
Usage: PYTHONPATH=. python3 scripts/item12_timing.py"""
import glob, time
from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.io import load_model
from cla_harness import solver
print("model | feasible (enum) | feasible (Z3) | equal | enumerate s (valid + interactions) | Z3 s")
for path in sorted(glob.glob("examples/*.json")):
    p, f = load_model(path)
    t = time.perf_counter(); e = feasible_interactions(valid_configurations(p, f), 2); te = time.perf_counter() - t
    t = time.perf_counter(); z = solver.feasible_interactions_z3(p, f); tz = time.perf_counter() - t
    print(f"{path} | {len(e)} | {len(z)} | {e == z} | {te:.4f} | {tz:.3f}")
