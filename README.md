# Constraint-Aware Locating Array + Fault Localization Harness

A small research prototype for **constrained combinatorial interaction testing (CIT)**.

## What it does

1. Models configurable software as parameters and values.
2. Rejects configurations containing forbidden partial assignments.
3. Enumerates feasible `t`-way interactions (pairwise by default).
4. Generates a small greedy covering suite or a locating-oriented suite.
5. Injects a hidden interaction fault.
6. Observes PASS/FAIL signatures.
7. Attempts to identify the failure-inducing interaction.

The locating idea is operationally important: *coverage tells you a bug-triggering interaction was exercised; localization tries to tell you which interaction caused the failures.*

## Quick start (Windows PowerShell)

Install Python 3.10+ from python.org and ensure **Add Python to PATH** is checked.

```powershell
cd path\to\constraint_locating_harness
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -e .
python -m unittest discover -s tests
cla-harness demo examples\model.json --fault Auth=CAC Database=Remote
```

If PowerShell blocks activation, you can avoid activation and run:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m cla_harness.cli demo examples\model.json --fault Auth=CAC Database=Remote
```

## Build a suite

```powershell
cla-harness build examples\model.json --mode locate --strength 2 --output suite.csv
```

Compare against ordinary coverage:

```powershell
cla-harness build examples\model.json --mode cover --strength 2 --output covering_suite.csv
```

The program reports:
- number of possible configurations
- number remaining after constraints
- number of feasible interactions
- number of selected tests
- number of still-ambiguous pairs of interactions

## Model format

Edit `examples/model.json`:

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

A `forbidden` object means that entire partial assignment is illegal.

## Code map

- `core.py`: configuration space, constraints, t-way interactions
- `generator.py`: greedy covering and locating-oriented generation
- `localizer.py`: deterministic simulator, exact localization, noisy ranking
- `io.py`: JSON model and CSV output
- `cli.py`: command-line interface
- `tests/`: regression tests

## Research limitations

This is intentionally a **V1 research prototype**, not a claim of a new optimal CLA construction algorithm.

Current assumptions:
- finite discrete parameters
- constraints expressed as forbidden partial assignments
- exhaustive enumeration of valid configurations
- deterministic tests
- one failure-inducing `t`-way interaction at a time for exact localization
- greedy, not optimal, suite construction

These assumptions should be stated explicitly in any report.

## Suggested experiment

For several models:

1. Generate a normal greedy covering suite.
2. Generate the locating-oriented suite.
3. For every feasible 2-way interaction, inject it as the fault.
4. Record whether the localizer returns exactly one candidate.
5. Compare:
   - suite size
   - 2-way coverage
   - ambiguous interaction pairs
   - unique localization rate
   - generation time

This directly tests the research question: **How much extra testing is required to gain localization capability beyond coverage?**

## Next upgrades

1. Z3/SMT constraints rather than enumerating and filtering all configurations.
2. Multiple simultaneous failure-inducing interactions (`d > 1`).
3. Noisy/nondeterministic outcomes using probabilistic scoring.
4. Real test-runner adapters (pytest/JUnit/CI).
5. SAT/MaxSAT or integer-programming optimization.
6. Baseline against NIST ACTS or another covering-array generator.
7. Reproduce constrained locating-array definitions from the literature exactly and benchmark against published instances.
