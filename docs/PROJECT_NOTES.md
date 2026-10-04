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

### examples/model_low_constraints.json (model.json's parameters, 0 forbidden rules) -- commit 3e18b06
- Change relative to model.json: identical 5 binary parameters, forbidden
  list emptied out entirely (0 rules instead of 2). model.json itself now
  serves as the "medium" density point in this comparison; a high-density
  model is still planned to complete the three-point curve.
- Valid configurations: 32 / 32 (trivial with no constraints; test-verified)
- Feasible pairwise interactions: 40 (all possible term-pairs, trivial with
  no constraints; test-verified)
- Covering suite: 6 tests, coverage 40/40 (100%), 46 ambiguous pairs,
  localized 8/40 (20.00%)
- Locating suite: 9 tests, coverage 40/40 (100%), 0 ambiguous pairs,
  localized 40/40 (100%)
- Observed generation time: covering ~0.0008s, locating ~0.0852s
- Note: compared to model.json (2 rules, 11 locating tests, 38 feasible),
  removing all constraints actually *lowered* the locating suite size (9
  vs 11) despite having slightly more feasible interactions to distinguish
  (40 vs 38). More valid configurations (32 vs 18) apparently gives the
  locating heuristic a richer pool of naturally-distinguishing tests to
  pick from. Only two points on this curve so far; the high-density model
  is needed before drawing any conclusion about direction.

### examples/model_high_constraints.json (model.json's parameters, 4 forbidden rules) -- commit f2ca363
- Change relative to model.json: identical 5 binary parameters; forbidden
  list grows from 2 rules to 4 (model.json's original two, plus
  Auth=CAC & Logging=Off, plus Network=Ethernet & Encryption=Off).
- Valid configurations: 11 / 32 (hand-derived by inclusion-exclusion and
  test-verified)
- Feasible pairwise interactions: 35 (test-verified). 5 of the 40 possible
  term-pairs are infeasible: the 4 forbidden rules themselves, plus one
  *indirect* case (Database=Remote AND Encryption=Off) that no rule names
  but that cannot occur because Database=Remote forces Network=Ethernet
  (rule 2), which forces Encryption=On (rule 4).
- Covering suite: 7 tests, coverage 35/35 (100%), 21 ambiguous pairs,
  localized 14/35 (40.00%)
- Locating suite: 11 tests (every valid configuration), coverage 35/35
  (100%), **5 ambiguous pairs, localized 28/35 (80.00%)** -- the first model
  where full localization was not reached. See "Finding: a structural
  ceiling on localization" below: this is not a heuristic shortfall.
- Observed generation time (verification run, not averaged): covering
  ~0.0005s, locating ~0.015s

#### Constraint-density comparison (same 5 binary parameters throughout)
| Rules | Model                        | Valid | Feasible | Cover tests / localized | Locate tests / localized |
|-------|------------------------------|-------|----------|-------------------------|--------------------------|
| 0     | model_low_constraints.json   | 32    | 40       | 6 / 8 of 40 (20.00%)    | 9 / 40 of 40 (100%)      |
| 2     | model.json                   | 18    | 38       | 6 / 10 of 38 (26.32%)   | 11 / 38 of 38 (100%)     |
| 4     | model_high_constraints.json  | 11    | 35       | 7 / 14 of 35 (40.00%)   | 11 / 28 of 35 (80.00%)   |

### examples/model_spins_core.json (DERIVED from the CCAG `spins` benchmark) -- commit bad0946
- What it is: the SPIN simulator benchmark projected onto the 9 parameters
  that appear in its 13 constraints (6 binary, 3 four-valued). It is a
  derived model, not the benchmark: the 9 omitted unconstrained parameters
  are not represented. Source and attribution in `docs/BENCHMARKS.md`.
  First model in the set that comes from a published benchmark's rules.
- Valid configurations: 978 of 4,096 raw (978 * 2,048 = 2,002,944, the full
  benchmark's independently counted valid configurations).
- Feasible pairwise interactions: 239 (hand-derived as 252 value pairs
  across parameters minus 13 forbidden pairs; test-verified).
- Achievable ceiling: 229 / 239. The 10 interactions no suite can separate
  fall into four groups from chains of forced values: P0=1 forces P1=0,
  P2=0, P14=0 and P15=0 (four identical interactions); any non-zero P15
  forces P0=0 and P12=0 (three identical pairs). The same mechanism as in
  model_high_constraints.json, here arising from a published benchmark.
- Covering suite: 22 tests, coverage 239/239 (100%), 369 ambiguous pairs,
  localized 71/239 (29.71%), ceiling gap 158.
- Locating suite: 32 tests, coverage 239/239 (100%), 9 ambiguous pairs
  (3 + the 6 pairs inside the group of four), localized 229/239 (95.82%),
  ceiling gap 0. The greedy heuristic reached the ceiling.
- Test counts, coverage, ambiguous pairs, localized counts and ceiling were
  reproduced exactly on the user's machine and in the sandbox.
- Generation time (one sandbox run, not averaged, NOT confirmed on the
  user's machine): covering about 0.18 s, locating about 192 s, roughly
  1,000 times slower. Timing on the user's machine was not captured; compare
  only after repeating runs on one machine.
- Runs only with `python -m cla_harness.experiment --include-slow`.

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

**Greedy locating generation cost grows steeply with the number of valid
configurations (added with the spins core).** Generation took about 2 s for
model_8param.json (144 valid configurations, 110 interactions) and about 192 s
for model_spins_core.json (978 valid configurations, 239 interactions) in
sandbox runs, while greedy covering stayed under 0.2 s. Two models do not
establish a growth law, and the runs were not averaged. It does show that the
greedy locating heuristic's cost is the practical limit on this model, which
motivates a cheaper search; the likely cause is that every candidate is scored
by recomputing ambiguous pairs each round, not yet profiled.

**The ceiling mechanism appears in a published benchmark's constraints.** In
model_spins_core.json the unreachable 10 interactions come from the same
forced-value chains as in model_high_constraints.json, so the effect is not an
artifact of hand-built rules. Still one benchmark, pairwise only, and known
theory (Jin & Tsuchiya, see docs/LITERATURE_CHECK.md), not a new result.

## Finding: a structural ceiling on localization (model_high_constraints.json)

**Claim (for this model, `t=2`, deterministic single-fault model):** the
maximum achievable unique-localization rate is 28/35 = 80%, for *any* test
suite, of any size, built from this model's valid configurations. The greedy
locating generator's 80% is not a near-miss.

**Evidence.** Using all 11 valid configurations as the suite -- the largest
suite that exists under this model -- still leaves exactly 5 ambiguous
interaction pairs, the same 5 the greedy suite leaves (the greedy suite in
fact selected all 11 configurations). Adding tests cannot help once every
valid configuration is already included.

**Why.** Each ambiguous pair traces to one parameter value that forces a
chain of other values through the forbidden rules, so several differently
named interactions are logically the same event and have identical
PASS/FAIL signatures in every possible suite:
- `Encryption=Off` forces `Auth=Password` (rule 1) and `Network=WiFi`
  (rule 4), and `Network=WiFi` forces `Database=Local` (rule 2). So
  `Encryption=Off AND Auth=Password`, `Encryption=Off AND Network=WiFi`, and
  `Encryption=Off AND Database=Local` all hold in exactly the same valid
  configurations. Three interactions, 3 ambiguous pairs.
- `Auth=CAC` forces `Encryption=On` (rule 1) and `Logging=On` (rule 3), so
  `Auth=CAC AND Encryption=On` and `Auth=CAC AND Logging=On` are identical.
  1 pair.
- `Database=Remote` forces `Network=Ethernet` (rule 2), which forces
  `Encryption=On` (rule 4), so `Database=Remote AND Network=Ethernet` and
  `Database=Remote AND Encryption=On` are identical. 1 pair.

**Why it matters for the research question.** The project's framing so far is
a cost tradeoff: coverage is cheap, localization costs extra tests. This
model shows a second, different limit: in some constrained spaces no number
of extra tests buys full localization, because the constraints themselves
erase the distinguishing information. It also means the six earlier
"locating suite reached 100%" results should not be read as evidence that
the greedy heuristic always reaches full localization; they may reflect
milder constraint structure, which these experiments have not separated
from heuristic quality.

**Implications for the framework:**
1. *Achievable ceiling -- implemented (commit 9996811).* `ceiling_of` in
   `experiment.py` groups interactions by their signature over the full set
   of valid configurations (no suite generation needed); the ceiling is the
   number of interactions alone in their group. Adding tests only splits
   signature groups, never merges them, so no suite can localize more. Each
   result row now carries `ceiling` and `ceiling_gap` (ceiling minus
   localized), so "localized / ceiling" separates heuristic quality from
   model structure. Tests check it against hand-derived tiny cases and
   against `evaluate_suite` run with every valid configuration as the suite.
2. Constraint structure, not just rule count, is what matters: the 4-rule
   model's ceiling comes from rules sharing parameters and chaining. Worth
   characterizing which constraint graphs produce collapse (not yet done).

**Measured ceiling results (t=2, from running the harness):** the ceiling
equals the number of feasible interactions on six of the seven models
(model.json 38, my_model.json 39, model_6param.json 58, model_8param.json
110, model_multivalue.json 46, model_low_constraints.json 40), and the
locating suite reaches it on all six (gap 0). On model_high_constraints.json
the ceiling is 28 of 35; the locating suite reaches it (gap 0) and the
covering suite is 14 below it (14/35 localized). Covering-suite gaps on the
others are large (for example 95 of 110 on model_8param.json), which
restates the original coverage-versus-localization tradeoff relative to what
was achievable.

**Caveats.** One model. Pairwise only. Deterministic single-fault outcomes
only; richer fault models (multiple faults, noise) change what is
distinguishable. The ceiling is for 2-way interactions as the candidate set;
a different candidate definition would give a different ceiling. Literature status (checked 2026-10-04, see `docs/LITERATURE_CHECK.md`): this
is NOT a new phenomenon. Jin & Tsuchiya (J. Systems and Software 170, 2020)
define distinguishability for constrained systems (Definition 1 and Lemma 1:
two sets of valid interactions are distinguishable iff some valid test covers
an interaction in one and none in the other), define constrained locating
arrays (CLAs) that only require separating distinguishable pairs, and prove a
CLA always exists. The `ceiling` metric here is the single-fault (d=1), t=2
instance of that concept, and the ambiguous pairs left at the ceiling are
their indistinguishable pairs. What this project adds is measurement: reporting
localized-versus-achievable as a metric, and (so far only on seven small
models) how it responds to constraint density.

## Future work: metaheuristic locating-aware objective (candidate V0.3 direction)

The uploaded reference (Torres-Jimenez & Rodriguez-Tello, "An improved
simulated annealing algorithm for constructing strength-three covering
arrays," Information Sciences, 2012) constructs small covering arrays with
simulated annealing, optimizing purely for size/coverage. It and the broader
metaheuristic covering-array literature it surveys (simulated annealing,
genetic algorithms, memetic algorithms, tabu search) do not treat
distinguishability/localization as an objective at all.

Literature update (2026-10-04, `docs/LITERATURE_CHECK.md`): the paragraph that
stood here claimed that metaheuristics do not treat distinguishability as an
objective. That is wrong for locating arrays. Konishi, Kojima, Nakagawa &
Tsuchiya ("Using simulated annealing for locating array construction", arXiv
1909.13090; reported as Information and Software Technology 2020) already use
SA with cost = weight * (uncovered t-way interactions) + (interactions whose
covering-row set equals another interaction's), a targeted neighborhood and a
binary search over array size. It is for unconstrained arrays and lists
constrained locating arrays as future work, as does the 2023 LocAG paper
(Dougherty, Green & Kim). The Torres-Jimenez & Rodriguez-Tello paper is
covering-array SA only.

What may remain open (hypothesis, pending a deeper search): a metaheuristic for
constrained locating arrays, where candidate rows must be valid, scored
against the distinguishability ceiling and compared with the published CLA
heuristic. Candidate V0.3 order:
1. Locate the standard benchmarks (CitLab and the sources cited in the CLA
   paper) and add a loader; the seven hand-built models are too small to
   support a paper.
2. Run a targeted search for post-2023 constrained locating array work.
3. Implement a constrained SA that searches over valid configurations only,
   starting from the Konishi cost function and neighborhood, with the cost
   counting only avoidable ambiguity (distinguishable pairs left unseparated).
4. Compare with the greedy heuristic on the same models; compare with published
   CLA sizes only where the same benchmark is used.

This does not belong in V0.2. It is recorded here so it is not lost.
