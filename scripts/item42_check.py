"""Plan item 42 cross-check: Z3 pool-plus-query count of distinguishable interactions equals experiment.ceiling_of
(enumeration over all valid configurations) on the 8 example models at t = 2. Usage: PYTHONPATH=. python3 scripts/item42_check.py"""
import glob, json
from collections import defaultdict
from itertools import combinations
from cla_harness.io import load_model
from cla_harness.core import valid_configurations, feasible_interactions, contains_interaction
from cla_harness.experiment import ceiling_of
from cla_harness.solver import FastZ3CostModel, sample_valid_configurations
for path in sorted(glob.glob("examples/*.json")):
    p, f = load_model(path)
    configs = valid_configurations(p, f)
    ints = sorted(feasible_interactions(configs, 2), key=sorted)
    model = FastZ3CostModel(p, f, cover_only=True, strength=2)
    assert set(model.interactions) == set(ints)
    tests = sample_valid_configurations(p, f, 100, seed=0)
    groups = defaultdict(list)
    for it in model.interactions: groups[tuple(contains_interaction(c, it) for c in tests)].append(it)
    bad = {i for g in groups.values() for a, b in combinations(g, 2) if not model.separable(a, b) for i in (a, b)}
    print(json.dumps({"model": path, "enumerated_ceiling": ceiling_of(configs, ints), "z3_distinguishable": len(ints) - len(bad), "feasible": len(ints)}), flush=True)
