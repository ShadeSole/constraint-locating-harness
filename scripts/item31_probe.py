"""Plan item 31, first step: time per cost evaluation and per move at strength 3 on model_spins_core.json.
Usage: PYTHONPATH=. python3 scripts/item31_probe.py"""
import random, time
from cla_harness.io import load_model
from cla_harness.core import valid_configurations
from cla_harness.solver import Z3CostModel, anneal_suite_z3
p, f = load_model("examples/model_spins_core.json")
configs = valid_configurations(p, f)
for mode in ("cover", "locate"):
    t = time.perf_counter(); model = Z3CostModel(p, f, cover_only=(mode == "cover"), strength=3); ti = time.perf_counter() - t
    print(f"{mode}: model setup {ti:.1f} s, {len(model.interactions)} feasible 3-way interactions", flush=True)
    for size in (30, 45):
        rng = random.Random(1); suite = rng.sample(configs, size)
        t = time.perf_counter(); model.suite_cost(suite, detail=True); first = time.perf_counter() - t
        t = time.perf_counter()
        for _ in range(20): model.suite_cost(rng.sample(configs, size), detail=True)
        per = (time.perf_counter() - t) / 20
        t = time.perf_counter(); r = anneal_suite_z3(model, size, 0, 60, neighbor="targeted"); pm = (time.perf_counter() - t) / max(r["steps"], 1)
        print(f"  size {size}: first cost eval {first:.3f} s, mean cost eval over 20 random suites {per:.3f} s, "
              f"60-move targeted run {pm:.3f} s per move (final cost {r['cost']['cost']})", flush=True)
