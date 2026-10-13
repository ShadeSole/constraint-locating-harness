"""Plan item 11: Z3 listing and sampling versus enumeration, one timed run each.
Usage: PYTHONPATH=. python3 scripts/item11_timing.py"""
import glob, time
from cla_harness.core import valid_configurations
from cla_harness.io import load_model
from cla_harness import solver
key = lambda c: tuple(sorted(c.items()))
print("model | valid | enumerate s | Z3 list s | same set | Z3 1000 samples s | all samples valid")
for path in sorted(glob.glob("examples/*.json")):
    p, f = load_model(path)
    t = time.perf_counter(); enum = valid_configurations(p, f); te = time.perf_counter() - t
    t = time.perf_counter(); listed = solver.valid_configurations_z3(p, f); tz = time.perf_counter() - t
    t = time.perf_counter(); samples = solver.sample_valid_configurations(p, f, 1000, seed=0); ts = time.perf_counter() - t
    S = {key(c) for c in enum}
    print(f"{path} | {len(enum)} | {te:.4f} | {tz:.3f} | {({key(c) for c in listed} == S) and len(listed) == len(S)} | {ts:.3f} | {all(key(c) in S for c in samples)}")
