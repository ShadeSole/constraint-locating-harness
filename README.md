# Constraint-Aware Locating Array + Fault Localization Harness

A small research prototype for **constrained combinatorial interaction testing (CIT)**.

The research question: *how can we efficiently generate constraint-aware test
suites that cover feasible configuration interactions **and** keep enough
information to identify which interaction caused a failure?*

The locating idea is operationally important: *coverage tells you a bug-triggering interaction was exercised; localization tries to tell you which interaction caused the failures.*

## What it does

1. Models configurable software as parameters and values.
2. Rejects configurations containing forbidden partial assignments.
3. Enumerates feasible `t`-way interactions (pairwise by default).
4. Generates a greedy covering suite or a greedy locating-oriented suite.
5. Injects a hidden interaction fault (a simulated deterministic fault, not a real program failure).
6. Observes PASS/FAIL signatures.
7. Attempts to identify the failure-inducing interaction.

## Quick start

Requires Python 3.10+. Run everything from the repository root.

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -e .
python -m unittest discover -s tests
cla-harness demo examples/model.json --fault Auth=CAC Database=Remote
```

PowerShell (if activation is blocked, call the venv's Python directly):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m cla_harness.cli demo examples\model.json --fault Auth=CAC Database=Remote
```

## Run the V0.2 experiments

```bash
python -m cla_harness.experiment
```

For each model in `examples/`, this injects **every** feasible 2-way interaction
as the single fault, once per suite, and compares the covering suite against the
locating suite. It prints a per-model report and a summary table, and writes
`results/v0_2_results.csv` (gitignored; regenerated on every run).

Metrics recorded per (model, method):

| column | meaning |
|---|---|
| `valid_configs` | configurations left after constraints |
| `tests` | suite size |
| `interactions`, `covered`, `coverage_rate` | feasible interactions, and how many the suite exercises (checked independently of the generator) |
| `ambiguous_pairs` | interaction pairs with identical PASS/FAIL signatures |
| `localized`, `total`, `localization_rate` | faults whose exact signature matches only the true interaction |
| `ceiling`, `ceiling_gap` | the most interactions *any* suite could localize in this model, and how far this suite falls short of it |
| `generation_seconds`, `evaluation_seconds` | timing, kept separate |

### The achievable ceiling

Constraints can make different interactions logically identical (for example, a
rule chain that forces `Encryption=Off` to imply `Auth=Password` and
`Network=WiFi`). Such interactions have the same signature in every valid
configuration, so no suite of any size can tell them apart. `ceiling` counts the
interactions that are alone in their signature group over all valid
configurations. Read `localized` against `ceiling`, not against `total`, to
separate heuristic quality from model structure.

### Current benchmark results (t = 2, greedy heuristics)

Measured with the commands above; the full record, with commit hashes and
discussion, is in `docs/PROJECT_NOTES.md`.

| model | valid configs | feasible interactions | covering suite: tests, localized | locating suite: tests, localized | ceiling |
|---|---|---|---|---|---|
| `model.json` | 18 | 38 | 6, 10/38 | 11, 38/38 | 38 |
| `my_model.json` | 24 | 39 | 7, 13/39 | 9, 39/39 | 39 |
| `model_6param.json` | 36 | 58 | 7, 15/58 | 11, 58/58 | 58 |
| `model_8param.json` | 144 | 110 | 7, 15/110 | 13, 110/110 | 110 |
| `model_multivalue.json` | 30 | 46 | 9, 24/46 | 12, 46/46 | 46 |
| `model_low_constraints.json` | 32 | 40 | 6, 8/40 | 9, 40/40 | 40 |
| `model_high_constraints.json` | 11 | 35 | 7, 14/35 | 11, 28/35 | 28 |

In every model the covering suite exercises all feasible interactions but
localizes only a fraction of them; the locating suite costs more tests and reaches
the ceiling. These are single runs of a deterministic greedy heuristic on small
hand-built models. They illustrate the coverage-versus-localization tradeoff;
they are not evidence about the heuristic's behavior on real systems.

## Build a suite (single model)

```bash
cla-harness build examples/model.json --mode locate --strength 2 --output suite.csv
cla-harness build examples/model.json --mode cover --strength 2 --output covering_suite.csv
```

The program reports the number of possible configurations, the number remaining
after constraints, the number of feasible interactions, the number of selected
tests, and the number of still-ambiguous pairs of interactions.

## Model format

Models live in `examples/`:

```json
{
  "parameters": {
    "Auth": ["Password", "CAC"],
    "Network": ["WiFi", "Ethernet"]
  },
  "forbidden": [
    {"Auth": "CAC", "Network": "WiFi"}
  ]
}
```

A `forbidden` object means that entire partial assignment is illegal. An empty
`forbidden` list means no constraints.

## Code map

- `cla_harness/core.py`: configuration space, constraints, t-way interactions
- `cla_harness/generator.py`: greedy covering and locating-oriented generation
- `cla_harness/localizer.py`: deterministic simulator, exact localization, noisy ranking (noisy ranking is not yet used by the experiments)
- `cla_harness/io.py`: JSON model loading, suite and results CSV output
- `cla_harness/experiment.py`: V0.2 experiment runner and metrics (including the ceiling)
- `cla_harness/cli.py`: command-line interface (`build`, `demo`)
- `tests/`: regression tests, including hand-derived counts for every shipped model
- `docs/PROJECT_NOTES.md`: benchmark log, findings, and research caveats
- `PROJECT_HANDOFF.md`: current status and next steps

## Research limitations

This is a research prototype, not a claim of a new or optimal locating-array
construction algorithm. Locating arrays, and their constrained variants, are
established in the literature; this project does not claim to have invented them.

Current assumptions:
- finite discrete parameters
- constraints expressed as forbidden partial assignments
- exhaustive enumeration of valid configurations (limits model size)
- deterministic tests
- one failure-inducing `t`-way interaction at a time for exact localization
- greedy, not optimal, suite construction
- localization is of *interactions* in a simulated fault model; this is separate from locating faults in source code

These assumptions should be stated explicitly in any report.

## Next upgrades

1. A metaheuristic (for example simulated annealing) with a locating-aware objective, aimed at smaller suites than the greedy heuristic. Greedy locating generation also gets noticeably slower as models grow, which is a further motivation.
2. Z3/SMT constraints rather than enumerating and filtering all configurations.
3. Multiple simultaneous failure-inducing interactions (`d > 1`).
4. Noisy/nondeterministic outcomes using probabilistic scoring.
5. Real test-runner adapters (pytest/JUnit/CI).
6. Baseline against NIST ACTS or another covering-array generator, and against published constrained locating-array results.
7. A literature check on constrained locating/distinguishing arrays before any novelty claim.
