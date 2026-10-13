"""Plan item 5: cold vs warm (replaces restart 0) vs warm-extra (one extra run) on one model.
Usage: PYTHONPATH=. python3 scripts/item5_warm_compare.py MODEL START SEED MODE [steps] [restarts]
MODE is cold | warm | extra. Prints one line. SA settings: targeted moves.
"""
import sys, time
from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.io import load_model
from cla_harness.annealing import unavoidable_pairs, find_small_suite
model, start, seed, mode = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
steps = int(sys.argv[5]) if len(sys.argv) > 5 else 6000
restarts = int(sys.argv[6]) if len(sys.argv) > 6 else 5
params, forb = load_model(model)
configs = valid_configurations(params, forb)
ints = feasible_interactions(configs, 2)
un = unavoidable_pairs(configs, ints)
t = time.perf_counter()
r = find_small_suite(configs, ints, un, start, seed=seed, restarts=restarts, steps_per_restart=steps,
                     neighbor="targeted", warm_start=mode != "cold", warm_extra=mode == "extra")
sizes = ",".join(f"{a['n']}{'ok' if a['solved'] else 'FAIL'}{'/'+a['solved_by'] if a['solved_by'] else ''}" for a in r["attempts"])
print(f"{model} seed={seed} mode={mode} steps={steps} restarts={restarts} -> size {r['size']}, moves {r['total_moves']}, "
      f"{time.perf_counter()-t:.1f}s, attempts {sizes}", flush=True)
