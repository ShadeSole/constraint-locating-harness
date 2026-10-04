# Project documentation plan

## Problem
Configurable software may have many legal configurations and forbidden option combinations. Pairwise/t-way coverage can expose failures, but a failed test does not automatically identify the responsible interaction.

## Research question
How much additional test-suite size is required to make feasible interactions distinguishable by their PASS/FAIL signatures, compared with ordinary constrained t-way coverage?

## Core representation
For a selected suite, define an incidence matrix `M`:
- row = test configuration
- column = feasible t-way interaction
- `M[i,j]=1` iff test `i` contains interaction `j`.

Under the deterministic single-fault model, if interaction `j` causes every containing test to fail and all other tests pass, the observed failure vector equals column `j`. Identical columns are therefore indistinguishable.

## What to save for every experiment
- model JSON
- Git commit hash
- random seed (when randomness is added)
- interaction strength `t`
- number of raw configurations
- number of feasible configurations
- number of feasible interactions
- suite-generation method
- suite size
- generation runtime
- coverage percentage
- number of ambiguous interaction pairs
- unique localization rate
- injected fault(s)
- observed PASS/FAIL vector

## Recommended repository structure
- README.md: setup and usage
- docs/: design, math, assumptions, experiments
- examples/: reproducible models
- tests/: automated correctness checks
- results/: generated CSV/JSON experiment results (add later)
- src/package: implementation

## Claims to avoid
Do not claim that the project invented constrained locating arrays. They already exist in the research literature. Frame the contribution as an implementation, experimental extension, alternative heuristic, integration, or new evaluation unless you establish a genuinely novel result.

## Good report outline
1. Motivation
2. Background: CIT, covering arrays, locating arrays, constraints
3. Problem definition and assumptions
4. System design
5. Algorithms
6. Incidence-matrix interpretation
7. Experimental methodology
8. Results
9. Threats to validity
10. Related tools/work
11. Future work

## Logging convention (added 2026-09-28)
Every time a new benchmark model is added and pushed, record its results in the
"Benchmark results" section below before moving on to the next checklist item.
Include the commit hash the numbers came from, since the greedy heuristics and
metrics can change behavior across commits.

## Benchmark results

All runs below use `t=2` (pairwise interactions), the greedy covering and greedy
locating generators as implemented in `cla_harness/generator.py`, and the
deterministic single-fault model. Timings are from a single run each (not
averaged/repeated) and will vary by machine and by run; they are included as
order-of-magnitude evidence, not precise benchmarks. Repeat-and-median timing
is still future work (see V0.2 checklist).

### examples/model.json (5 binary parameters, 2 forbidden rules) — commit 323817f
- Valid configurations: 18 / 32
- Feasible pairwise interactions: 38
- Covering suite: 6 tests, coverage 38/38 (100%), 54 ambiguous pairs,
  localized 10/38 (26.32%)
- Locating suite: 11 tests, coverage 38/38 (100%), 0 ambiguous pairs,
  localized 38/38 (100%)
- Observed generation time: covering ~0.0004s, locating ~0.03-0.045s (varied
  across runs on the same machine)

### examples/my_model.json (5 binary parameters, 1 forbidden rule) — commit 323817f
- Valid configurations: 24 / 32
- Feasible pairwise interactions: 39
- Covering suite: 7 tests, coverage 39/39 (100%), 40 ambiguous pairs,
  localized 13/39 (33.33%)
- Locating suite: 9 tests, coverage 39/39 (100%), 0 ambiguous pairs,
  localized 39/39 (100%)
- Observed generation time: covering ~0.0003-0.001s, locating ~0.04-0.054s

### examples/model_6param.json (model.json + 1 free binary parameter) — commit 81b999c
- Valid configurations: 36 / 64 (18 * 2, hand-derived and test-verified)
- Feasible pairwise interactions: 58 (38 + 20, hand-derived and test-verified)
- Covering suite: 7 tests, coverage 58/58 (100%), 88 ambiguous pairs,
  localized 15/58 (25.86%)
- Locating suite: 11 tests, coverage 58/58 (100%), 0 ambiguous pairs,
  localized 58/58 (100%)
- Observed generation time (live run on Shade's machine): covering 0.0015s,
  locating 0.1603s

### examples/model_8param.json (model.json + 3 free binary parameters) — commit 215da32
- Valid configurations: 144 / 256 (18 * 2^3, hand-derived and test-verified)
- Feasible pairwise interactions: 110 (38 + 60 + 12, hand-derived and test-verified)
- Covering suite: 7 tests, coverage 110/110 (100%), 212 ambiguous pairs,
  localized 15/110 (13.64%)
- Locating suite: 13 tests, coverage 110/110 (100%), 0 ambiguous pairs,
  localized 110/110 (100%)
- Observed generation time (live run on Shade's machine): covering 0.0081s,
  locating 2.0917s

### examples/model_multivalue.json (model.json with Network expanded to 3 values) -- commit 65c2fb6
- Change relative to model.json: Network grows from 2 values (WiFi, Ethernet)
  to 3 (WiFi, Ethernet, Cellular). Both forbidden rules and every other
  parameter are unchanged.
- Valid configurations: 30 / 48 (hand-derived via inclusion-exclusion and
  test-verified)
- Feasible pairwise interactions: 46 (hand-derived and test-verified)
- Covering suite: 9 tests, coverage 46/46 (100%), 26 ambiguous pairs,
  localized 24/46 (52.17%)
- Locating suite: 12 tests, coverage 46/46 (100%), 0 ambiguous pairs,
  localized 46/46 (100%)
- Observed generation time: covering ~0.0006s, locating ~0.1045s

## Observations worth carrying into the paper

**Localization cost in tests stays small, but the covering-suite localization
rate depends on more than just size.** Across all five models the locating
suite needed only 2-5 more tests than the covering suite to go from partial
to full localization -- that part looks robust. The covering suite's
localization rate, however, is not simply a function of model size:
26.32% -> 33.33% -> 25.86% -> 13.64% for the four binary models (roughly
getting worse as the configuration space grows), but then 52.17%, nearly
double the previous best, for model_multivalue.json, the one model with a
3-valued parameter. The leading hypothesis is that parameter pairs touching a
3-valued parameter contribute 6 distinct term-combinations instead of 4,
giving the covering suite more naturally distinct signatures to land on even
before any locating-specific effort -- but this is one model with one
parameter changed, not yet a confirmed effect. A second multi-value model
(a different parameter expanded, or more than one) would help confirm or
rule this out before it's treated as a real finding rather than a
coincidence.

**The greedy locating heuristic's computational cost looks superlinear.**
Going from model_6param.json to model_8param.json, feasible interactions grew
about 1.9x (58 -> 110) and valid configurations grew 4x (36 -> 144), but
locating-suite generation time grew roughly 13x (0.16s -> 2.09s) on the same
machine. This is consistent with the structure of `greedy_locating_suite` in
`generator.py`: `score()` calls `ambiguous_pairs()` for every candidate
configuration in every round, and `ambiguous_pairs()` itself rescans every
feasible interaction's full signature. The test-suite-size cost of locating
has stayed cheap so far; the search cost to find that suite has not. This is
a concrete, measured motivation for exploring a smarter search method (see
Future work below) rather than a vague appeal to "greedy might not scale."

## Future work: metaheuristic locating-aware objective (candidate V0.3 direction)

The uploaded reference (Torres-Jimenez & Rodriguez-Tello, "An improved
simulated annealing algorithm for constructing strength-three covering
arrays," Information Sciences, 2012) constructs small covering arrays with
simulated annealing, optimizing purely for size/coverage. It and the broader
metaheuristic covering-array literature it surveys (simulated annealing,
genetic algorithms, memetic algorithms, tabu search) do not treat
distinguishability/localization as an objective at all.

That is a real gap this project already sits in. A concrete, specific
direction for V0.3, sharper than "also try SA": give a metaheuristic (SA or
a GA) a locating-aware fitness function, one that penalizes ambiguous
interaction pairs directly rather than only rewarding coverage, and test
whether it can reach full localization with a smaller suite than the greedy
locating heuristic, and/or reach it faster than the greedy heuristic's
super-linear search cost documented above.

Suggested order, once the remaining V0.2 benchmarks are in:
1. Do a quick literature check on locating arrays / distinguishing arrays
   specifically (not just covering arrays) so any novelty claim is checked
   against prior work rather than assumed.
2. As a cheap first experiment, run a plain size/coverage-optimizing SA
   (as in the uploaded paper) through the existing `evaluate_method`
   pipeline unmodified, and see where it lands on ambiguous pairs and
   localization rate, before designing a locating-aware fitness function.
3. Only then design and implement the locating-aware objective itself.

This does not belong in V0.2. It is recorded here so it is not lost.
