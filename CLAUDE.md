# CLAUDE.md: constraint-locating-harness

Research prototype for constrained combinatorial interaction testing: build
test suites that cover feasible t-way interactions AND can localize the
failure-inducing one. Python 3.10+, standard library only. Active branch:
`v0.3-development` (simulated annealing for constrained locating arrays).

## Accuracy rules (most important)
1. **Never state a number from memory.** Suite sizes, localization rates,
   ceilings, timings, and test counts come from `docs/PROJECT_NOTES.md` (cite
   the section heading) or from a command you just ran. If neither, say
   "not measured".
2. **Label every result's origin:** "sandbox" (an AI session ran it) or
   "reproduced locally" (the user ran it). One seed = one data point; say so.
3. **Novelty:** locating arrays, constrained LAs, distinguishability (Jin &
   Tsuchiya 2020) and SA for unconstrained LAs (Konishi et al.) are published.
   The `ceiling` metric is NOT new. The possible gap is SA for *constrained*
   LAs evaluated against the ceiling. Check `docs/LITERATURE_CHECK.md` before
   making any claim about prior work, and never invent citations.
4. **Before editing code, read the function you are changing.** Don't guess
   signatures; `grep -n "^def " cla_harness/*.py` lists them.
5. If unsure, say you're unsure and name the file or command that would settle it.

## Code map
- `cla_harness/core.py`: configs, forbidden constraints, t-way interactions, `constrained_core`
- `cla_harness/generator.py`: greedy covering + locating suites, `signature`, `ambiguous_pairs`
- `cla_harness/localizer.py`: fault simulator, exact localization (`rank_noisy` unused)
- `cla_harness/io.py`: JSON + CASA model loading, CSV output
- `cla_harness/experiment.py`: V0.2 runner; `ceiling_of`, `coverage_of`
- `cla_harness/annealing.py` (large): `suite_cost`, `anneal_suite`, `find_small_suite`,
  `exact_minimum_suite_size`, `multi_seed_search`, CLI `main`
- `cla_harness/cli.py`: `cla-harness build|demo`
- `examples/*.json`: 8 models (`model_spins_core.json` is slow; needs `--include-slow`)
- `tests/`: unittest suites (~19 s; exact-search tests are slowest)

## Read only when the task needs it (these files are long)
| Need | Read |
|---|---|
| Current status / next step | `PROJECT_HANDOFF.md` section 0 only |
| A benchmark or SA result | `docs/PROJECT_NOTES.md`, the matching `##` section (grep `^#` first) |
| Prior work / novelty | `docs/LITERATURE_CHECK.md` sections 1 and 3 |
| CCAG/CASA benchmarks | `docs/BENCHMARKS.md` |
| Paper-ready findings | `docs/PROJECT_NOTES.md` "Observations worth carrying into the paper" |

## Do not read
- `.venv/`, `__pycache__/`, `*.egg-info/`
- `../constraint-locating-harness-main/`: an OLD V0.1 copy. Its code differs; never use it.
- `../external/CCAG/`: large third-party benchmark repo; open only specific model files.
- `results/*.csv`: regenerated each run; rerun instead of trusting old output.

## Commands (PowerShell, repo root)
```
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m cla_harness.experiment
.\.venv\Scripts\python.exe -m cla_harness.annealing examples\model.json 9 --neighbor targeted --exact
```

## Working style
- Incremental, tested changes. Don't redesign unless asked.
- After a result is measured, record it in `docs/PROJECT_NOTES.md` (commit hash,
  seed, budget, sandbox/local) and update `PROJECT_HANDOFF.md` section 0.
- Keep this file under ~1 page; put details in docs/, not here.
