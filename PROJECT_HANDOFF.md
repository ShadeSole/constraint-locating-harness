# Constraint-Aware LA + Fault-Localization Harness
## Project Handoff for Continued Development

**Current development line:** V0.2 experiment framework  
**Last known working release:** V0.1  
**Active Git branch:** `v0.2-experiments`  
**Primary language:** Python  
**Research area:** constrained combinatorial interaction testing (CIT), locating arrays, and fault localization

## 1. Read This First
This project is already under development. **Do not redesign or rebuild it from scratch unless explicitly asked.** Inspect the repository first, preserve the existing architecture where reasonable, determine what is already implemented, and make incremental testable changes. Do not present illustrative numbers as experimental results. Preserve the distinction between established research concepts and this project's implementation/experimental contribution.

## 2. Overarching Research Goal
The project investigates how to test highly configurable software efficiently while also making failures diagnostically useful. Traditional combinatorial testing can reduce the number of configurations by covering important t-way interactions, but coverage alone does not necessarily identify which interaction caused a failure.

Primary research question:

> **How can constraint-aware combinatorial test suites be constructed to efficiently cover feasible configuration interactions while preserving enough distinguishability to localize failure-inducing interactions?**

Experimental question:

> **What additional testing cost is required to gain fault-localization capability beyond ordinary interaction coverage?**

The central tradeoff is **coverage + localization capability vs. test-suite size + computational cost**.

## 3. Research Framing
The project does **not** claim to invent locating arrays or constrained locating arrays. Potential contributions should instead be framed as an implementation, new/modified heuristic, experimental analysis, real-test integration, noisy/multiple-fault extension, alternative constraint solving, or statistical/AI-assisted ranking. Any novelty claim requires literature review and evidence.

## 4. Conceptual Pipeline
```text
Configurable software/model
          |
Parameters + values
          |
Configuration constraints
          |
Valid configurations
          |
Feasible t-way interactions
          |
Test-suite generator
     /           \
covering       locating-oriented
     \           /
          |
Run/simulate tests
          |
PASS/FAIL outcome vector
          |
Fault localizer
          |
Candidate failure-inducing interaction(s)
```

### Terminology
- **Configuration:** complete assignment of a value to every parameter.
- **Valid configuration:** complete configuration satisfying all constraints.
- **Interaction:** partial assignment involving `t` parameters.
- **Feasible interaction:** interaction appearing in at least one valid complete configuration.
- **Covering suite:** valid configurations collectively exercising every feasible interaction of the chosen strength.
- **Fault:** currently, one feasible interaction designated as failure-inducing.
- **Localizer:** identifies feasible interaction(s) consistent with observed PASS/FAIL outcomes.
- **Locating property:** tests provide enough distinguishing information that candidate interactions do not have indistinguishable signatures under the assumed fault model.

## 5. Incidence-Matrix Interpretation
Rows are selected tests and columns are feasible interactions. Define `M[i,j]=1` iff test `i` contains interaction `j`.

Under the deterministic single-fault model, FAIL=1 and PASS=0. If interaction `j` is faulty, the observed outcome vector equals its incidence signature. Identical interaction columns/signatures are indistinguishable.

Core distinction:

> **100% interaction coverage does not automatically imply 100% unique fault localization.**

## 6. V0.1 — Working Prototype
Approximate repository structure:

```text
cla_harness/
    __init__.py
    core.py
    generator.py
    localizer.py
    io.py
    cli.py
examples/
    model.json
tests/
    test_harness.py
docs/
    PROJECT_NOTES.md
README.md
pyproject.toml
requirements.txt
```

### `core.py`
Configuration representation, forbidden assignments, enumeration, constraint filtering, t-way interaction extraction, feasible interaction collection, containment checks, labels.

### `generator.py`
Greedy feasible t-way covering generator, signatures, ambiguous-pair detection, and greedy locating-oriented generator. The locating method is a heuristic, not a claim of optimality.

### `localizer.py`
Deterministic single-interaction fault simulation, exact signature localization, simple noisy Hamming-distance ranking, candidate reporting.

### `io.py`
JSON model loading, command-line interaction parsing, CSV suite output.

### `cli.py`
Commands for building suites and demonstrating fault injection/localization.

## 7. Current Example Model
Five binary parameters:

```text
Auth        = Password | CAC
Network     = WiFi | Ethernet
Encryption  = On | Off
Logging     = On | Off
Database    = Local | Remote
```

Example forbidden assignments:

```text
Auth=CAC AND Encryption=Off
Database=Remote AND Network=WiFi
```

Verified V0.1 example:

```text
Raw configurations:             32
Valid configurations:           18
Feasible pairwise interactions: 38
```

A locating-oriented verification run selected 11 tests with 0 ambiguous interaction pairs. An injected `Auth=CAC AND Database=Remote` fault was uniquely localized. These are example-specific results only.

## 8. Useful Commands
```bash
python -m unittest discover -s tests
python -m cla_harness.cli demo examples/model.json --fault Auth=CAC Database=Remote
python -m cla_harness.cli build examples/model.json --mode locate --strength 2 --output suite.csv
python -m cla_harness.cli build examples/model.json --mode cover --strength 2 --output covering_suite.csv
```

## 9. Environment Notes
The project was initially used on Windows with a Bash-style shell. Git Bash activation is typically:

```bash
source .venv/Scripts/activate
```

Linux/WSL/macOS:

```bash
source .venv/bin/activate
```

V0.1 intentionally used a simple implementation before adding Z3 or other solver dependencies.

## 10. Git/GitHub Workflow
Stable line: `main`. Active development branch: `v0.2-experiments`.

If needed:

```bash
git push -u origin v0.2-experiments
```

Commit after a small feature works and tests pass. Example commits:

```text
Add V0.2 experiment setup
Add covering suite evaluation
Add localization rate metric
Compare covering and locating suites
Add experiment result export
Complete V0.2 experiment framework
```

Before a checkpoint:

```bash
python -m unittest discover -s tests
python -m cla_harness.experiment
git status
git add .
git commit -m "DESCRIPTIVE MESSAGE"
git push
```

## 11. V0.2 — Current Objective
V0.1 asked: **Can the mechanism localize an injected interaction fault?**

V0.2 asks: **How well does a locating-oriented suite localize feasible faults compared with an ordinary covering suite, and what additional test cost does it require?**

Major new file: `cla_harness/experiment.py`.

The core experiment iterates over every feasible interaction, treats it as the hidden fault, simulates the suite, calls the localizer, and counts whether the actual fault is the one and only candidate.

Conceptual function:

```python
def evaluate_suite(suite, interactions):
    total = 0
    correctly_localized = 0

    for fault in interactions:
        outcomes = run_suite(suite, fault)
        candidates = localize_exact(suite, outcomes, interactions)
        total += 1

        if len(candidates) == 1 and candidates[0] == fault:
            correctly_localized += 1

    return correctly_localized, total
```

Localization rate:

```python
localization_rate = correctly_localized / total
```

Evaluate this independently for the covering and locating-oriented suites.

## 12. Desired V0.2 Experiment
1. Load `examples/model.json`.
2. Obtain valid configurations.
3. Obtain feasible pairwise interactions.
4. Generate greedy covering suite.
5. Evaluate every feasible interaction as a possible single fault.
6. Calculate covering-suite unique localization rate.
7. Generate locating-oriented suite.
8. Evaluate every feasible interaction against it.
9. Calculate locating-suite unique localization rate.
10. Compare suite size and localization capability.

Desired terminal structure:

```text
VALID CONFIGURATIONS: ...
FEASIBLE INTERACTIONS: ...

COVERING SUITE
Tests: ...
Localized: ... / ...
Localization rate: ...%

LOCATING SUITE
Tests: ...
Localized: ... / ...
Localization rate: ...%
```

Actual numbers must come from execution.

## 13. V0.2 Metrics To Add/Verify
- Suite size
- Feasible interaction coverage
- Unique localization rate
- Ambiguous interaction pairs
- Generation/evaluation runtime using `time.perf_counter()`
- Reproducible CSV output

Target CSV shape:

```csv
model,method,tests,interactions,ambiguous_pairs,localized,total,localization_rate,runtime
model,cover,...,...,...,...,...,...,...
model,locate,...,...,...,...,...,...,...
```

## 14. Benchmark Expansion
A single toy model is insufficient for general conclusions. Add reproducible models such as:

```text
examples/model.json
examples/model_6param.json
examples/model_8param.json
examples/model_multivalue.json
examples/model_low_constraints.json
examples/model_high_constraints.json
```

Independent variables can include parameter count, values per parameter, interaction strength, constraint density/structure, feasible configuration count, and feasible interaction count.

## 15. Definition of V0.2 Complete
```text
[ ] Automatically inject every feasible single t-way fault
[ ] Evaluate ordinary covering suite
[ ] Evaluate locating-oriented suite
[ ] Calculate unique localization rate
[ ] Verify interaction coverage
[ ] Calculate ambiguous interaction pairs
[ ] Measure runtime
[ ] Save reproducible CSV results
[ ] Run multiple benchmark models
[ ] Add/extend automated tests
[ ] Update README/documentation
[ ] Commit/push completed work
[ ] Merge v0.2-experiments into main after verification
[ ] Tag/release v0.2.0
```

## 16. Planned Roadmap
### V0.3 — stronger evaluation/baselines
Improve benchmarks, compare against established combinatorial-testing approaches/tools where practical, and evaluate/improve the greedy heuristic.

### V0.4 — stronger constraint solving
Introduce SAT/SMT support such as Z3 for richer constraints and larger spaces.

### V0.5 — multiple simultaneous faults
Move beyond exactly one failure-inducing interaction.

### V0.6 — noisy/nondeterministic failures
Use repeated execution, Hamming-distance baseline, likelihood/probabilistic/statistical scoring.

### V0.7 — real software/test-runner integration
Potential pytest/JUnit/CI/configuration-deployment adapters and structured outcome collection.

### V0.8+ — richer/AI-assisted localization
Potentially combine interaction evidence, PASS/FAIL history, logs, stack traces, code coverage, and recent source changes to rank likely causes or source locations. AI is an extension, not the current foundation.

## 17. Interaction vs. Source-Code Localization
**Interaction localization:** Which configuration combination is associated with the failure? Example: `Encryption=TLS AND Authentication=Certificate`.

**Source-code localization:** Which implementation location contains the defect? Example: `auth/certificate.py`.

These are distinct problems even if a future system combines them.

## 18. Current Simplifying Assumptions
Unless the repository has since changed:
- finite discrete parameters;
- simplified forbidden partial-assignment constraints;
- exhaustive enumeration acceptable for small models;
- pairwise (`t=2`) primary example;
- one failure-inducing interaction for exact localization;
- deterministic outcomes under the exact model;
- greedy construction rather than guaranteed minimum-size suites.

## 19. What Not To Do Next
Do not immediately add an LLM and call the system "AI fault detection." First establish correctness, reproducibility, baselines, metrics, scaling behavior, and failure cases. Do not replace working code with a giant framework without demonstrated need.

## 20. Documentation Expectations
Keep `README.md` current with problem, assumptions, install/run/model/experiment instructions and metric definitions. Use `docs/PROJECT_NOTES.md` for design decisions, math, assumptions, research questions, and experiment planning.

For significant experiments preserve model/version, Git commit hash, random seed if applicable, `t`, raw/feasible configuration counts, feasible interaction count, method, suite size, runtime, coverage, ambiguous pairs, localization rate, and fault-model assumptions.

## 21. Recommended Next Action for a New Assistant
1. Read this handoff.
2. Inspect the actual repository; it is the implementation source of truth.
3. Run:

```bash
git status
git branch
python -m unittest discover -s tests
python -m cla_harness.experiment
```

4. Determine which V0.2 checklist items already work.
5. Do not overwrite working code merely to match this handoff.
6. Continue with the next incomplete V0.2 item.
7. Make one small change at a time and test it.
8. Explain how each change contributes to the research question.
9. Commit and push working checkpoints.

If repository behavior conflicts with this document, inspect the current code and Git history. The repository is authoritative about what has actually been implemented.

## 22. One-Paragraph Summary
This research project develops a constraint-aware combinatorial testing and fault-localization harness for configurable software. It models parameters, values, and forbidden configurations; enumerates feasible t-way interactions; constructs small covering and locating-oriented test suites; and uses PASS/FAIL signatures to identify failure-inducing interactions. The immediate research focus is measuring how much additional testing is required to make interactions uniquely distinguishable compared with ordinary interaction coverage. V0.1 established a working deterministic single-fault prototype, while V0.2 adds systematic experiments that inject every feasible interaction as a fault and compare suite size, coverage, ambiguity, localization rate, and runtime. Longer-term work may add Z3 constraints, multiple faults, nondeterministic failures, real test-runner integration, stronger baselines, and statistical or AI-assisted localization.

## 23. Short Explanation for Collaborators
> **It generates small test suites for configurable software that respect invalid configuration constraints and are designed not only to exercise interaction-based bugs, but also to make the responsible configuration interaction identifiable from the resulting pattern of test failures.**
