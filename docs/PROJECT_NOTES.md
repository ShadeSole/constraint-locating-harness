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

## Simulated annealing, preliminary results (V0.3 step 2, commit ae9fcc1)

Method: `anneal_suite` in `cla_harness/annealing.py`. The search keeps a suite of
exactly N valid configurations; one move replaces a random test with a random
valid configuration; a move that raises the cost by delta is kept with
probability exp(-delta/T), T starting at 2.0 and multiplied by 0.999 per move;
20,000 moves maximum, best suite returned. Cost = weight * (feasible
interactions in no test) + (pairs of covered interactions with identical test
sets that some valid test could separate). Cost 0 means the suite covers every
feasible interaction and localizes as many interactions as any suite could (the
ceiling). Cost form follows Konishi et al. (arXiv 1909.13090); under
constraints the collision term ignores pairs no suite can separate.

Results reproduced exactly on the user's machine (seeds 0-4; steps to reach
cost 0):
- model.json, N = 9 (greedy locating needs 11): solved 5 of 5, steps
  2875, 922, 1153, 1746, 812; every suite covers 38/38 and localizes 38/38
  by the separate evaluator.
- model_high_constraints.json, N = 9 (greedy locating selected all 11 valid
  configurations): solved 5 of 5, steps 140, 145, 215, 266, 351; every suite
  covers 35/35 and localizes 28/35, the ceiling.

Sandbox runs only (not yet reproduced by the user): at the greedy size every
seed solved on model.json, my_model.json, model_6param.json and
model_high_constraints.json; at two tests below the greedy size, model.json and
model_high_constraints.json were still solved (5 of 5); my_model.json and
model_6param.json were not solved within 20,000 moves (0 of 5), as was
anything four tests below greedy.

What this supports: on two of the small models the simplest SA move finds a
suite two tests smaller than the greedy locating heuristic's, which is
consistent with the project's standing statement that greedy is not optimal.
In particular the greedy suite on model_high_constraints.json contained all 11
valid configurations although 9 suffice for the same localization.

What it does not support: any general claim that SA beats greedy. Five seeds,
untuned temperature, small models, one move type. An unsolved run means "not
found in 20,000 moves", not "impossible". Runs also take seconds because the
cost is recomputed from scratch on every move.

## Simulated annealing, targeted moves and exact minima (V0.3 step 3, commit 519a6c8)

Added `neighbor="targeted"` to `anneal_suite`: if some feasible interaction is
uncovered, pick one and swap a test for a valid configuration containing it;
otherwise pick an interaction in an avoidable collision and either swap a test
that lacks it for a valid configuration that contains it, or change one
parameter value of a test that has it (a valid configuration differing in
exactly one parameter). After Konishi et al. (arXiv 1909.13090), adapted so
every test stays a valid configuration. Also added `exact_minimum_suite_size`,
which tries every subset of valid configurations (small models only) to find
the true smallest zero-cost suite, with its own bit-mask cost.

**Exact minima (all three reproduced in the user's local environment through
the test suite; counts are how many suites of that size have cost zero):**

| model | true minimum tests | such suites | greedy locating | SA (either move) |
|-------|--------------------|-------------|-----------------|------------------|
| model.json | 9 | 2 | 11 | reaches 9 |
| my_model.json | 8 | 8 | 9 | reaches 8 |
| model_high_constraints.json | 9 | 1 | 11 | reaches 9 |

Greedy locating is therefore 2, 1 and 2 tests above the optimum on these three
models. The smaller sizes SA failed at earlier are impossible, not search
failures. On model_high_constraints.json exactly one 9-test suite exists out of
55 choices of 9 from the 11 valid configurations, and SA finds it in a few
hundred moves. One caution: "cost zero" here means every feasible interaction
is covered and every separable pair is separated, which a test confirms is the
same as localizing as many interactions as any suite could; it is not the
smallest suite for coverage alone.

**Random versus targeted moves, sandbox runs (5 seeds, steps to solution, medians
over solved runs):** model.json N=9: 1153 random, 324 targeted. my_model.json
N=9: 409 / 92. model_6param.json N=11: 305 / 111. Targeted needed roughly 3 to 5
times fewer moves at sizes both solved, and did not solve any size that random
could not. (my_model.json N=8 was solved by both: 779 / 98.) For model.json with
targeted moves, run in the user's local environment: seeds 0 to 4 solved N=9 in
383, 324, 77, 487 and 76 moves.

**model_spins_core.json, targeted moves, N=32 (the size the greedy locating
heuristic needed), seeds 0 to 2, 6000 moves, reproduced by the user:**
seed 0 solved at 2116 moves (6.94 s); seed 1 not solved, final cost 29,
covered 225/239, localized 189/239 (19.04 s); seed 2 solved at 2033 moves
(6.70 s). Solved 2 of 3.

**Sandbox only (not reproduced by the user; three runs sharing two CPU cores,
so times are inflated; 3 seeds, 20,000 moves):** N=32 solved 2 of 3; N=30
solved 1 of 3 (seed 2, at 5998 moves; seed 0 ended at cost 1, seed 1 at cost
28); N=28 solved 0 of 3 (best cost 6). So SA found a 30-test suite, below the
greedy heuristic's 32, in one of three runs; no 28-test suite was found.

**Observations and limits:**
- Unsolved runs commonly stall near cost 30 with about 14 interactions
  uncovered. With temperature 2.0 multiplied by 0.999 per move, the search is
  effectively frozen after about 5000 moves, so the rest of a 20,000-move run
  is wasted. Slower cooling, restarts or reheating are the obvious next
  experiment; none has been tried, and the schedule has not been tuned at all.
- Time comparison with greedy is only indicative: greedy locating took about
  192 s in one sandbox run (not on the user's machine), SA found 32 tests in
  about 7 s on the user's machine. Different machines, single runs.
- The exact minimum is known only for models small enough to enumerate. For
  model_spins_core.json the true minimum is unknown, so "SA found 30, greedy 32"
  says nothing about how close either is to optimal.
- Small models, few seeds, one real-benchmark-derived model. No ranking of
  methods is justified yet.

## Simulated annealing, suite-size search (V0.3 step 4, commit 0984942)

`find_small_suite` starts at a given size and shrinks by one while the search
succeeds. At each size it makes up to `restarts` independent annealing runs of
`steps_per_restart` moves; "failure at size n" means all of them ended with cost
above zero, i.e. a fixed budget of restarts x moves, not wall-clock time. The
cooling rate is derived so the temperature falls from 2.0 to 0.05 over exactly the
per-run budget (replacing the fixed 0.999 that froze after about 5000 moves).
A failed size is NOT a proof of impossibility; only `exact_minimum_suite_size`
proves a minimum, and only on small models. Runner:
`python -m cla_harness.annealing MODEL START --shrink --neighbor targeted --steps S --restarts R`
(the runner's default is still random moves, so pass `--neighbor targeted`).

**Verified by tests (90 tests pass in the sandbox, 3 gated skips):** on the three
small models, starting two tests above the proven minimum, the search ends at
exactly 9, 9 and 8 tests with localization equal to the ceiling (3 restarts,
2000 moves, targeted). Six deliberate breaks of the shrinking loop were each
caught by the new tests.

**Reproduced by the user (Windows, Git Bash): 90 tests OK, and the spins-core run
below matched the sandbox move for move; only the time differed (180.79 s on the
user's machine versus 225.65 s in the sandbox).** The small-model runs were not
reproduced by the user.
- Small models (sandbox only), random moves, 3 restarts x 3000 moves, start 11: model.json ends
  at 9 (10,372 total moves), model_high_constraints.json at 9 (9,293),
  my_model.json at 8 (10,443). These equal the proven minima.
- model_spins_core.json, targeted moves, 5 restarts x 6000 moves, start 32,
  one run (seed 0, reproduced by the user): size 32 solved on run 1 (2,743 moves); size 31 on run 1
  (3,865); size 30 on run 4 (23,948 moves, so 3 failed runs first); size 29
  failed all 5 runs (30,000 moves). Smallest found: 30 tests, covered 239/239,
  localized 229/239 (the ceiling). Total 60,556 moves, 180.79 s on the user's
  machine (225.65 s on a two-core sandbox). The greedy locating heuristic needed 32 tests on this model.

**Caveats:** one seed, one real-benchmark-derived model, schedule untuned. Whether
29 is impossible is unknown (a larger budget or warm-starting from the 30-test
suite might find it). Greedy and SA times were not measured on one machine.
Do not call SA "better" than greedy from this; it is a single indicative run.

## Simulated annealing, warm start and a larger budget (V0.3 step 5)

Step 5 adds `initial` to `anneal_suite` (start from a given suite instead of a
random one), `drop_least_useful_test`, and `warm_start=True` in `find_small_suite`:
the first run at each size below the start size begins from the previously solved
suite minus the one test whose removal costs least, at a lower temperature
(`warm_start_temp`, default 0.3). It replaces restart 0, so the failure budget at
each size is unchanged. Runner flags: `--warm-start`, `--warm-temp`, `--seed`.
102 tests pass in the sandbox (12 new, 7 deliberate breaks each caught).

**model_spins_core.json, targeted moves, seed 0, 5 restarts per size. Rows marked
"user-reproduced" matched the user's Windows run move for move (102 tests OK);
the warm-start rows are sandbox only:**

| Setting | Sizes tried | Smallest found | Total moves |
|---|---|---|---|
| cold, 6000 moves/run, start 32 (user-reproduced) | 32, 31, 30 solved; 29 failed | 30 | 60,556 |
| warm (T 0.3 or 0.1, same result), 6000 moves/run, start 32 | 32, 31 (warm, 187 moves), 30 solved; 29 failed | 30 | 56,878 |
| warm, 20,000 moves/run, start 31 | 31, 30 solved; 29 failed (100,000 moves) | 30 | 183,875 |
| cold, 20,000 moves/run, start 31 (user-reproduced; 605.92 s on the user's machine, 748.17 s in the sandbox) | 31, 30, 29 solved; 28 failed (100,000 moves) | 29 | 200,251 |

Every suite found covers 239/239 and localizes 229/239 (the ceiling).

**What this shows, and does not:**
- Warm start saved moves on an easy step (size 31: 187 moves instead of 3,865) but
  did not help below that. At size 30 the warm run failed in both budgets and a
  cold run solved it.
- At 20,000 moves/run, the cold search found a 29-test suite in its FIRST run at
  size 29 (16,376 moves). In the warm search that first run was the warm run,
  which failed, and the four cold runs after it (different seeds) also failed.
  So warm start, as built, cost the one lucky restart. One seed, so this may be
  luck rather than a systematic effect.
- A bigger move budget mattered more than warm start: 6000 moves/run reached 30,
  20,000 moves/run reached 29 in one search. No suite of 28 was found in 100,000
  moves. The true minimum is unknown, so none of these sizes is shown optimal.
- Greedy locating needed 32 tests on this model, so SA found a smaller suite
  (29 to 30 vs 32), but only on one derived model with one seed, and the times
  were not compared on one machine. Not a general ranking.
- Warm temperatures 0.3 and 0.1 gave identical move counts here; the temperature
  is untuned and this test could not separate them.

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

## Greedy vs SA sizes on the enumerable example models (research plan item 2)

Origin: cloud run, not reproduced by the author. Base commit fd4ff84 plus
`scripts/item2_sizes.py` (new; calls existing functions only). t = 2, 7 models in
`examples/` (`model_spins_core.json` excluded as slow). SA = `find_small_suite`,
targeted moves, started at the greedy locating size, 3 restarts x 3000 moves per
size, base seeds 0, 1, 2 (three data points per model, not a distribution). Times are
single wall-clock measurements on a cloud container, greedy and SA on the same machine.
Command: `PYTHONPATH=. python3 scripts/item2_sizes.py SEED`.

| model | valid | feasible | ceiling | greedy cover | greedy locate (localized) | SA size, seeds 0/1/2 (localized) | SA time s, seeds 0/1/2 |
|---|---|---|---|---|---|---|---|
| model.json | 18 | 38 | 38 | 6 | 11 (38/38) | 9/9/9 (38/38) | 2.1/2.1/2.4 |
| model_6param.json | 36 | 58 | 58 | 7 | 11 (58/58) | 10/10/10 (58/58) | 4.6/3.9/4.1 |
| model_8param.json | 144 | 110 | 110 | 7 | 13 (110/110) | 11/12/11 (110/110) | 9.8/8.8/15.6 |
| model_high_constraints.json | 11 | 35 | 28 | 7 | 11 (28/35) | 9/9/9 (28/35) | 1.9/2.0/2.1 |
| model_low_constraints.json | 32 | 40 | 40 | 6 | 9 (40/40) | 8/8/8 (40/40) | 2.4/2.0/2.2 |
| model_multivalue.json | 30 | 46 | 46 | 9 | 12 (46/46) | 11/11/11 (46/46) | 3.3/3.2/3.1 |
| my_model.json | 24 | 39 | 39 | 7 | 9 (39/39) | 8/8/8 (39/39) | 2.1/2.2/2.0 |

Greedy times (locating, seed-independent algorithm, three runs): 0.02 to 0.10 s on the
small models, about 2.7 to 2.8 s on model_8param.json; covering greedy at most 0.01 s.

Observations: in every run SA ended with full coverage and localization equal to the
ceiling, one or two tests below greedy locating. On model_8param.json the seeds
disagreed (11, 12, 11), so a single seed would mislead there. Sizes for model.json,
model_high_constraints.json and my_model.json (9, 9, 8) equal the proven minima recorded
above; whether the others are minimal is not known (no exact search was run).
Not supported: any general claim that SA beats greedy (7 tiny models, 3 seeds, untuned
schedule). The CASA benchmark files are not in this container, so only the hand-built
models were run.

## Ceiling on the original spins model (research plan item 42)
Cloud run, not reproduced by the author. `scripts/item42_ceiling.py` (spins from a CCAG clone outside the repo, nothing committed) and `scripts/item42_check.py`; z3-solver 5.3.1 pip-installed. Strength 2, d = 1, interaction localization only (no source-code fault localization). An interaction is counted distinguishable if no other feasible interaction is inseparable from it (Jin & Tsuchiya Def. 1 / Lemma 1 as implemented by `Z3CostModel.separable`; the primary paper's definitions were not re-read in this session).

Method: 400 Z3-sampled valid configurations (all checked valid) give each interaction a signature; pairs whose signatures differ are separated by some pool test and need no query. Every pair with identical signatures gets the exact Z3 query.

Cross-check (same method, pool 100): on all 8 example models the Z3 count equals `experiment.ceiling_of` from full enumeration (38, 58, 110, 28, 40, 46, 229, 39 distinguishable; high_constraints 28 of 35, spins_core 229 of 239, the other six equal to their feasible count).

| quantity | value |
|---|---|
| feasible 2-way interactions | 979 |
| all pairs of interactions | 478,731 |
| pairs needing a Z3 query after the pool | 9 |
| of these, inseparable | 9 |
| interactions in an inseparable pair | 10 |
| distinguishable interactions (ceiling) | 969 |
| setup time / query time | 3.1 s / under 0.05 s (30 min budget not approached) |

Comparison: the locating suites of item 23 (all ten seeds, sizes 42 to 44) left 969 of 979 interactions uniquely identified (see the item 23 section), equal to this exact count. So on this model, at t = 2, d = 1, the best suites separate every interaction that any suite could separate; the 10 left over are inseparable for any suite. Not shown: anything at t = 3 or d > 1, or whether suites of items 27/40 (covering-only) matter here (their count of 457 to 566 is from item 28). One model.

## Open questions
- Low priority, not a blocker: no CASA benchmark file was run for item 2 (the CCAG files are not in
  the cloud container, `../external` absent). The loader is already tested in tests/test_casa.py and
  almost every benchmark is too large to enumerate (docs/BENCHMARKS.md), so this only matters once
  solver-based handling exists (plan item 6).
- Item 3: rows with more than 4 rules rest on fewer orderings (survivors only); see that section.

## Needs your decision
- Item 33 approved in the live session (carried out as items 39 and 40). Still yours: comparison with published sizes (needs the primary papers' definitions read first), multiple faults, nondeterminism, anything AI-based.

## Constraint-structure family: fraction of distinguishable interactions (research plan item 3)

Origin: cloud run, not reproduced by the author. Base commit dbdc4ff plus `scripts/item3_constraint_family.py`
(new; existing functions only). Deterministic: two repeat runs gave identical output.
Command: `PYTHONPATH=. python3 scripts/item3_constraint_family.py 20 10`.

Design: the parameters are fixed (the 5 binary parameters of model.json); only the forbidden rules
change. Candidates are the 40 pair rules (one value of each of two parameters forbidden together).
For each of 20 shuffle seeds (0-19) the candidates are put in random order and the family is the
nested prefixes of 0 to 10 rules, so each set is the previous plus one rule. Metric: fraction
distinguishable = ceiling / feasible 2-way interactions (t = 2, single fault; `ceiling_of`). This is
interaction localization only; no source-code fault localization is involved.

| rules | orderings n | valid (mean) | feasible (mean) | ceiling (mean) | fraction min / median / max | n with fraction < 1 |
|---|---|---|---|---|---|---|
| 0 | 20 | 32.0 | 40.0 | 40.0 | 1.000 / 1.000 / 1.000 | 0 |
| 1 | 20 | 24.0 | 39.0 | 39.0 | 1.000 / 1.000 / 1.000 | 0 |
| 2 | 20 | 18.1 | 37.7 | 35.8 | 0.892 / 0.947 / 1.000 | 13 |
| 3 | 20 | 13.3 | 34.9 | 29.3 | 0.361 / 0.871 / 0.946 | 20 |
| 4 | 20 | 9.4 | 30.8 | 20.2 | 0.273 / 0.655 / 0.871 | 20 |
| 5 | 19 | 6.8 | 27.3 | 12.8 | 0.000 / 0.444 / 0.767 | 19 |
| 6 | 18 | 4.6 | 23.3 | 5.1 | 0.000 / 0.186 / 0.536 | 18 |
| 7 | 17 | 3.8 | 20.9 | 3.6 | 0.000 / 0.120 / 0.536 | 17 |
| 8 | 15 | 2.9 | 17.8 | 1.7 | 0.000 / 0.048 / 0.417 | 15 |
| 9 | 15 | 2.1 | 14.5 | 0.3 | 0.000 / 0.000 / 0.056 | 15 |
| 10 | 14 | 1.6 | 12.5 | 0.1 | 0.000 / 0.000 / 0.056 | 14 |

Observations: with 0 or 1 rules every interaction is distinguishable in all 20 orderings. From 2 rules
on the fraction drops, and from 3 rules on it is below 1 in every ordering that still has a valid
configuration. The spread between orderings at the same rule count is large (for example 0.361 to
0.946 at 3 rules), so rule COUNT alone does not determine the fraction; which rules are chosen matters.
Consistent with the existing high-constraint finding (model_high_constraints.json, 28/35 = 0.800).

Caveats: (1) rows from 5 rules on drop orderings whose rules left no valid configuration, so those
rows are survivors only and not comparable with earlier rows. (2) Mean valid counts at 8+ rules are
under 3 configurations; those rows are degenerate (a tiny valid set separates few interactions) and say
little about realistic models. (3) One parameter set, only pair rules, only t = 2, 20 orderings.
(4) Did not test which rule features (shared parameter, implication chains) drive the loss; that is a
hypothesis only.

## Strength-3 measurements on the small models (research plan item 4)

Origin: cloud run, not reproduced by the author. Base commit 85e808d plus `scripts/item4_strength3.py`
(new; same as item2_sizes.py with t = 3). Command: `PYTHONPATH=. python3 scripts/item4_strength3.py SEED 3`,
seeds 0, 1, 2. SA settings as in the item 2 section (targeted, 3 restarts x 3000 moves per size, started at the
greedy locating size). Here the fault is one feasible 3-way interaction and only 3-way interactions are
considered (2-way interactions are not in the set). Interaction localization only. The strength-2 columns are
from the item 2 section.

| model | valid | feasible 3-way | ceiling | greedy cover | greedy locate (localized) | SA size, seeds 0/1/2 (localized) | t=2 greedy / SA sizes |
|---|---|---|---|---|---|---|---|
| model.json | 18 | 68 | 60 | 12 | 17 (60/68) | 17/17/17 (60/68) | 11 / 9 |
| model_6param.json | 36 | 144 | 136 | 15 | 24 (136/144) | 22/22/22 (136/144) | 11 / 10 |
| model_8param.json | 144 | 424 | 416 | 18 | 30 (416/424) | 28/28/28 (416/424) | 13 / 11-12 |
| model_high_constraints.json | 11 | 55 | 25 | 10 | 11 (25/55) | 11/11/11 (25/55) | 11 / 9 |
| model_low_constraints.json | 32 | 80 | 80 | 12 | 17 (80/80) | 15/15/15 (80/80) | 9 / 8 |
| model_multivalue.json | 30 | 91 | 87 | 17 | 23 (87/91) | 22/22/22 (87/91) | 12 / 11 |
| my_model.json | 24 | 74 | 74 | 13 | 17 (74/74) | 17/17/17 (74/74) | 9 / 8 |

Times (single measurements, seconds, seed 0): greedy locating 0.04 to 0.8 s on the six smaller models and
73.9 s on model_8param.json (2.8 s at t = 2); SA 3.7 to 18.6 s on the six smaller models and 117.0 s on
model_8param.json (9.8 s at t = 2). Seeds 1 and 2 were within about 25 s of these.

Observations: (1) Every suite, greedy and SA, covered all feasible 3-way interactions and reached the ceiling.
(2) Moving from t = 2 to t = 3 lowers the ceiling fraction on several models: model.json 60/68, model_6param
136/144, model_8param 416/424, model_multivalue 87/91 (all 1.0 at t = 2), and model_high_constraints 25/55
(28/35 at t = 2). model_low_constraints and my_model stay at 1.0. So unconstrained-looking gaps appear at
t = 3 from constraints alone; mechanism not investigated. (3) SA is 0 to 2 tests below greedy; it equals greedy on
model.json, my_model.json and model_high_constraints.json. On model_high_constraints.json the 11 tests are all the
valid configurations, so no smaller suite exists to find. SA size did not vary across the three seeds.

Caveats: 3 seeds, small hand-built models, untuned schedule, a failed smaller size means "not found in the
budget", not proof of minimality (no exact search at t = 3 was run). Suite sizes grow faster than the number of
interactions suggests, and runtime at t = 3 is 10 to 12 times that at t = 2 on model_8param.json.

## Warm start as an extra run versus replacing restart 0 (research plan item 5)

Origin: cloud run, not reproduced by the author. Base commit e2243bd plus uncommitted-then-committed changes in
this item: `find_small_suite(..., warm_extra=True)` and CLI flag `--warm-extra` (existing warm-start code
reused; default behavior unchanged), 2 new tests (112 total pass, 3 skipped), and
`scripts/item5_warm_compare.py`. Modes: **cold** = no warm start; **warm** = warm run replaces restart 0
(the existing V0.3 step 5 behavior); **extra** = the warm run goes first and all 5 cold restarts follow with
exactly the seeds of the cold search, so a size below the start has up to 6 runs instead of 5.
Setup: model_spins_core.json, strength 2, targeted moves, 5 restarts, 6000 moves/run, start 32 (greedy
locating size), base seeds 0, 1, 2, one search per cell. Command:
`PYTHONPATH=. python3 scripts/item5_warm_compare.py examples/model_spins_core.json 32 SEED MODE`.

| seed | cold: smallest (total moves) | warm (replaces restart 0) | extra (additional run) |
|---|---|---|---|
| 0 | 30 (60,556) | 30 (56,878) | 30 (69,550) |
| 1 | 31 (36,737) | 30 (35,898) | 31 (40,296) |
| 2 | 32 (33,061) | 32 (33,061) | 30 (46,064) |

All suites found are the ceiling-reaching suites the search returns (cost zero); every size below the smallest
listed failed all of its runs within budget. Seed 0 cold (60,556 moves) and warm (56,878) repeat the figures in
the "warm start and a larger budget" section move for move. Wall times (365 to 537 s per search) are not
comparable: nine searches shared a 4-core container; not used for conclusions.

Observations: the smallest size found was 30 in 1 of 3 seeds for cold, 2 of 3 for warm and 2 of 3 for extra.
Extra was never worse than cold (its cold restarts are the same runs) and beat cold on seed 2 (30 vs 32),
where the warm run solved 31 and then 30 from the carried suite. Replacing restart 0 helped on seed 1 and
was identical to cold on seeds 0 (size) and 2. Extra costs one more run per failed size, visible in total moves
(seed 0: 69,550 vs 60,556).

Caveats: three seeds, one derived model (not the benchmark `spins`), one budget, untuned warm temperature
(0.3). Which warm seed is used differs between modes (warm uses restart index 0, extra uses -1), so some
differences between warm and extra are seed luck; with three data points no ranking is supported. Extra gets one
more run than the others at each size, so it is not a budget-matched comparison. A matched comparison would give
cold 6 restarts; not run.

## Spread on the spins-derived model, part 1: cold search, seeds 0-4 (research plan item 6)

Origin: cloud run, not reproduced by the author. Base commit b1bea6b plus `scripts/item6_spread.py` (new; calls
`multi_seed_search` once per seed so each seed can be timed). Model: examples/model_spins_core.json (a DERIVED
model, not the benchmark `spins`), strength 2, targeted moves, cold search (no warm start), 5 restarts,
6000 moves per run, start size 32 (greedy locating size). Command:
`PYTHONPATH=. python3 scripts/item6_spread.py SEED cold`.

| seed | final size | total moves | seconds | sizes solved | first size that failed all 5 runs |
|---|---|---|---|---|---|
| 0 | 30 | 60,556 | 263.3 | 32, 31, 30 | 29 |
| 1 | 31 | 36,737 | 166.3 | 32, 31 | 30 |
| 2 | 32 | 33,061 | 153.9 | 32 | 31 |
| 3 | 31 | 48,327 | 218.3 | 32, 31 | 30 |
| 4 | 30 | 40,232 | 171.2 | 32, 31, 30 | 29 |

Over the 5 seeds: min 30, median 31, max 32 (sizes 30, 31, 32, 31, 30; histogram 30: 2, 31: 2, 32: 1).
Check required by the plan: seed 0 gave 30 tests, as expected, with 60,556 moves, equal to the earlier
recorded figure. Seeds 1 and 2 also match the item 5 runs (same sizes and moves).
Timing caveat: seeds 0-3 ran at the same time on a 4-core container and seed 4 ran alone afterwards, so
seconds are not strictly comparable between seeds 0-3 and seed 4; treat them as order of magnitude.
Every returned suite has cost zero (covers all 239 feasible interactions and reaches the 229-interaction
ceiling by construction of the search). A "failed" size means not found within 5 x 6000 moves, not proven
impossible. Greedy locating needed 32 tests on this model (see the suite-size search section). Five seeds
on one derived model: no general claim. Items 7 and 8 extend this to seeds 5-9 and a budget-matched
comparison.

## Spread on the spins-derived model, part 2: cold search, seeds 5-9 (research plan item 7)

Origin: cloud run, not reproduced by the author. Same script, model and settings as the item 6 section
(`scripts/item6_spread.py`, base commit 1b41b8d, cold, 5 restarts, 6000 moves per run, targeted, start 32).
Command: `PYTHONPATH=. python3 scripts/item6_spread.py SEED cold` for seeds 5-9.

| seed | final size | total moves | seconds | sizes solved | first size that failed all 5 runs |
|---|---|---|---|---|---|
| 5 | 31 | 50,792 | 238.4 | 32, 31 | 30 |
| 6 | 31 | 50,795 | 236.3 | 32, 31 | 30 |
| 7 | 30 | 68,839 | 313.4 | 32, 31, 30 | 29 |
| 8 | 30 | 67,550 | 311.5 | 32, 31, 30 | 29 |
| 9 | 31 | 35,012 | 159.2 | 32, 31 | 30 |

Seeds 5-9 alone: min 30, median 31, max 31 (histogram 30: 2, 31: 3). Seeds 0-9 together (items 6 and 7): sizes
30, 31, 32, 31, 30, 31, 31, 30, 30, 31, so min 30, median 31, max 32, histogram 30: 4, 31: 5, 32: 1. No seed
reached 29 (every seed that solved 30 failed all 5 runs at 29). Timing caveat as in item 6: seeds 5-8 ran
together on a 4-core container and seed 9 ran alone, so seconds are order of magnitude only. Seeds 5 and 6 differ
in total moves by 3 (50,792 vs 50,795); this is coincidence of two independent runs, not a duplicated seed.
Ten seeds on one derived model: still a small sample.

## Budget-matched warm start comparison, seeds 0-9 (research plan item 8)

Origin: cloud run, not reproduced by the author. Base commit 8d4fefc, `scripts/item6_spread.py` (via
`multi_seed_search`), examples/model_spins_core.json (DERIVED model), strength 2, targeted moves, 6000 moves
per run, start 32. Two modes with an equal number of runs per size below the start: **cold, 6 restarts** versus
**warm_extra, 5 restarts** (1 warm run + 5 cold runs). Commands:
`PYTHONPATH=. python3 scripts/item6_spread.py SEED cold 6` and `... SEED extra 5`. Four searches ran at a time
on a 4-core container, so seconds are order of magnitude only.

| seed | cold, 6 restarts: size (moves) | warm_extra, 5 restarts: size (moves) |
|---|---|---|
| 0 | 30 (66,556) | 30 (69,550) |
| 1 | 31 (42,737) | 31 (40,296) |
| 2 | 32 (39,061) | 30 (46,064) |
| 3 | 31 (54,327) | 30 (53,050) |
| 4 | 30 (46,232) | 30 (47,333) |
| 5 | 31 (56,792) | 31 (55,811) |
| 6 | 31 (56,795) | 30 (46,394) |
| 7 | 30 (74,839) | 30 (71,256) |
| 8 | 30 (73,550) | 30 (55,661) |
| 9 | 31 (41,012) | 30 (46,568) |
| median final size | 31 | 30 |
| count at 30 / 31 / 32 | 4 / 5 / 1 | 8 / 2 / 0 |
| total moves, 10 seeds | 551,901 | 531,983 |

Observations: with equal runs per size, warm_extra ended at a smaller size than cold on 4 seeds, equal on 6 seeds, and larger on none. The
four seeds where it was smaller are 2 (30 vs 32), 3 (30 vs 31), 6 (30 vs 31) and 9 (30 vs 31). Cold with a sixth
restart gave the same final sizes as cold with five (item 6 and 7 tables) on all ten seeds, so the extra cold
restart bought nothing in this sample, while the warm run did. Total moves were similar (531,983 vs 551,901);
wall time was not compared strictly.

Caveats: ten seeds, one derived model (not the benchmark `spins`), one budget, one warm temperature (0.3);
a size counted as failed means not found within budget. The medians differ by one test; with 10 seeds this
is suggestive and not a tested difference (no significance test was run). Only the warm run's seed differs from
the cold runs' seeds, so luck in that single run per size can matter. Not a general statement about warm start.

## Summary of research plan items 6 to 8 (research plan item 9)

Origin: cloud run, not reproduced by the author. All numbers are copied from the three sections above (items 6, 7
and 8), none new. Model: examples/model_spins_core.json (DERIVED from the CCAG `spins` benchmark, not the benchmark),
strength 2, targeted moves, 6000 moves per run, start size 32; greedy locating needs 32 tests on this model.
Final size = smallest size at which some run reached cost zero before a size failed all its runs.

| search mode (runs per size below 32) | seeds | final size 30 / 31 / 32 | median | min / max | total moves | source section |
|---|---|---|---|---|---|---|
| cold, 5 restarts | 0-4 | 2 / 2 / 1 | 31 | 30 / 32 | 218,913 | item 6 |
| cold, 5 restarts | 5-9 | 2 / 3 / 0 | 31 | 30 / 31 | 272,988 | item 7 |
| cold, 5 restarts | 0-9 | 4 / 5 / 1 | 31 | 30 / 32 | 491,901 | items 6 + 7 |
| cold, 6 restarts | 0-9 | 4 / 5 / 1 | 31 | 30 / 32 | 551,901 | item 8 |
| warm_extra, 5 restarts (1 warm + 5 cold = 6 runs) | 0-9 | 8 / 2 / 0 | 30 | 30 / 31 | 531,983 | item 8 |

What the numbers show:
- Final size depends on the seed: the same cold search ended at 30, 31 or 32 tests depending on the seed
  (4, 5 and 1 of ten seeds). A single-seed size should not be quoted alone.
- No search on any of the 10 seeds found a suite smaller than 30.
- Adding a sixth cold restart changed no final size on these 10 seeds, and cost 60,000 more moves in total.
- With the same number of runs per size, warm_extra ended smaller than cold on 4 of 10 seeds, equal on 6, and
  larger on none; the medians are 30 and 31.

What they do not show: that warm_extra is better in general. Ten seeds on one derived model is still a small
sample; the median difference is one test and no significance test was run; one warm temperature (0.3) and one
budget; a size marked failed means not found within budget, not impossible; the model is a projection of
`spins`, so nothing here is a result on the benchmark itself. Timings were not compared (several searches shared
a 4-core container).

## Z3 stage 1, item 10: optional Z3 dependency and `is_valid` cross-check (research plan item 10)

Origin: cloud run, not reproduced by the author. Base commit d77a8eb. Installed `z3-solver` 5.1.0.0 with pip in the
cloud container (version printed by `z3.get_version_string()`: 5.1.0).

What was added (no existing function changed):
- `cla_harness/solver.py`: `build_solver` and `is_valid(parameters, forbidden, config)`. One Z3 integer per
  parameter (value index); each forbidden rule becomes Not(And(...)); a rule naming an unknown parameter or value
  is never violated, as in `Forbidden.violated_by`. A config with a missing parameter or an unlisted value raises
  ValueError (the enumeration-based `core.is_valid` does no such check). The module imports Z3 at the top, so
  importing it without Z3 raises ImportError with an install hint; nothing else imports it.
- `tests/test_solver.py` (6 tests, `unittest.skipUnless` Z3 is installed). With Z3 hidden (a stub `z3.py` that raises
  ImportError) all 6 are skipped and the module imports cleanly.
- CLAUDE.md now says standard library only with Z3 as an optional extra; `pyproject.toml` has an optional
  extra `z3`; `requirements.txt` lists it as a comment.

Cross-check result: on all 8 models in `examples/`, Z3's `is_valid` agreed with membership in
`valid_configurations` for every configuration of the full product (the products are 32, 64, 256, 32, 32, 48,
4096 and 32 configurations; none exceeds the 50,000 limit, so the seeded-random-5,000 branch was not needed on
the examples). The random-sampling branch is implemented in the test helper and exercised separately on a synthetic
20-binary-parameter model (product 1,048,576, 300 seeded samples, two rules; both valid and invalid samples occurred,
and all agreed). A deliberate break (checking with no rules) is caught by a test. Full suite with Z3: 118 tests, OK,
3 skipped (the 3 earlier gated skips); the new file alone took 22.0 s.

Timing note, not a benchmark: `is_valid` rebuilds the solver on every call, so the 6 tests take about 22 s
mostly on that (the largest model is 4096 calls). Item 13 will do the timing comparison properly.
Caveat: agreement on 8 small models and one synthetic model supports that the encoding is right for pair-or-larger
partial-assignment rules of this kind; it does not prove it for the CASA files, whose clauses are larger.

## Z3 stage 1, item 11: listing and sampling valid configurations (research plan item 11)

Origin: cloud run, not reproduced by the author. Base commit eb3bfd6 plus `scripts/item11_timing.py` (new),
z3-solver 5.1.0.0. Added to `cla_harness/solver.py` (no existing function changed):
- `valid_configurations_z3(parameters, forbidden)`: lists every valid configuration with one blocking clause per
  solution; the order is Z3's, not product order.
- `sample_valid_configurations(parameters, forbidden, n, seed)`: seeded draws; per draw the parameters are visited
  in random order and values tried in random order, keeping the first value Z3 can still extend (solver
  assumptions). Every sample is valid by construction. It is reproducible per seed but NOT uniform over valid
  configurations; repeats are possible. Returns [] if the model has no valid configuration.
- 4 new tests (listing equals enumeration, samples valid/seeded/varied, a model with no valid configuration, two
  deliberate breaks caught). Full suite: 122 tests OK, 3 skipped.

Results on all 8 example models (each has at most 978 valid configurations, so all are within the 5,000 limit):
(a) the Z3 list equals the enumeration set exactly on all 8 (same size, no duplicates, same members);
(b) all 1,000 seeded samples (seed 0) were valid on all 8. Single timed run each, seconds, one container
(repeats come in item 13):

| model | valid | enumerate | Z3 list | Z3, 1000 samples |
|---|---|---|---|---|
| model.json | 18 | 0.0001 | 0.141 | 1.697 |
| model_6param.json | 36 | 0.0003 | 0.034 | 2.135 |
| model_8param.json | 144 | 0.0005 | 0.112 | 3.162 |
| model_high_constraints.json | 11 | 0.0002 | 0.019 | 1.807 |
| model_low_constraints.json | 32 | 0.0001 | 0.035 | 1.530 |
| model_multivalue.json | 30 | 0.0001 | 0.024 | 1.758 |
| model_spins_core.json | 978 | 0.0200 | 1.076 | 3.675 |
| my_model.json | 24 | 0.0001 | 0.021 | 1.922 |

What this shows: on these tiny models Z3 listing was slower than plain enumeration in every row (by about 50x to
1,400x on the single runs; the first row also includes Z3's one-time start-up cost, which is not separated). It does
not show what happens on models too large to enumerate; that is the reason for the solver, and was not tested.
Sampling cost is roughly 1.5 to 3.7 ms per sample here. One run per cell, so treat timings as rough.

## Z3 stage 1, item 12: feasible 2-way interactions via Z3 (research plan item 12)

Origin: cloud run, not reproduced by the author. Base commit 8ebd5a0 plus `scripts/item12_timing.py` (new),
z3-solver 5.1.0.0. Added `feasible_interactions_z3(parameters, forbidden, strength=2)` to `cla_harness/solver.py`
(no existing function changed). A pair of values of two parameters is feasible if Z3 finds a valid configuration
containing both (one satisfiability query with assumptions per candidate pair); the result has the same type as
`core.feasible_interactions`. Only strength 2 is implemented (other values raise ValueError). 5 new tests
(equality on all 8 models, the counts 38 / 35 / 239 already recorded in these notes, an indirectly infeasible pair
that no rule names, no-valid-configuration and unsupported strength, one deliberate break). Full suite: 127 tests OK,
3 skipped.

Result: on all 8 example models the Z3 interaction set equals the set from enumeration, exactly. Single timed run
each, seconds (item 13 adds repeats); "enumerate" includes building the valid configurations:

| model | feasible 2-way | enumerate | Z3 |
|---|---|---|---|
| model.json | 38 | 0.0002 | 0.017 |
| model_6param.json | 58 | 0.0003 | 0.011 |
| model_8param.json | 110 | 0.0019 | 0.019 |
| model_high_constraints.json | 35 | 0.0002 | 0.008 |
| model_low_constraints.json | 40 | 0.0002 | 0.008 |
| model_multivalue.json | 46 | 0.0002 | 0.009 |
| model_spins_core.json | 239 | 0.0351 | 0.059 |
| my_model.json | 39 | 0.0003 | 0.014 |

What this shows: Z3 was slower on every model here, though the gap shrinks as the model grows (about 1.7 times on
spins core, tens of times on the smallest; one run each, and the first call may include Z3 start-up). The cost of the
Z3 route depends on the number of candidate value pairs, not on the number of valid configurations, which is the
property that matters for models too large to enumerate; that was NOT tested. Models are tiny.

## Z3 stage 1, item 13: timing table, enumeration versus Z3 (research plan item 13)

Origin: cloud run, not reproduced by the author. Base commit e76550a plus \`scripts/item13_timing.py\` (new),
z3-solver 5.1.0.0, all 8 example models, 3 repeats per cell, run alone on the container, no warm-up (repeat 1
includes any first-call cost). Command: \`PYTHONPATH=. python3 scripts/item13_timing.py\`. Tasks:
- **validity** (item 10): decide validity of every configuration of the full product: \`core.is_valid\` per
  configuration versus \`solver.is_valid\` per configuration (which rebuilds the solver on each call);
- **listing** (item 11): \`valid_configurations\` versus \`valid_configurations_z3\`;
- **pairs** (item 12): \`feasible_interactions(valid_configurations(...))\` versus \`feasible_interactions_z3\`.
Sampling (item 11) has no enumeration counterpart and is not in this table (its timing is in the item 11 section).

Median of 3 repeats, seconds; the Z3 column "range" is the fastest to slowest of its 3 repeats:

| model | task | enumeration median | Z3 median | Z3 range | Z3 / enumeration (medians) |
|---|---|---|---|---|---|
| model | validity | 0.0001 | 0.0794 | 0.0777 to 0.0885 | 1442.6x |
| model | listing | 0.0001 | 0.0216 | 0.0186 to 0.0295 | 386.1x |
| model | pairs | 0.0003 | 0.0088 | 0.0084 to 0.0096 | 27.5x |
| model_6param | validity | 0.0001 | 0.1516 | 0.1388 to 0.1964 | 1975.3x |
| model_6param | listing | 0.0001 | 0.0279 | 0.0274 to 0.0283 | 233.1x |
| model_6param | pairs | 0.0003 | 0.0118 | 0.0118 to 0.0127 | 35.7x |
| model_8param | validity | 0.0003 | 0.6147 | 0.6136 to 0.6879 | 1798.6x |
| model_8param | listing | 0.0005 | 0.1107 | 0.1074 to 0.1563 | 245.4x |
| model_8param | pairs | 0.0017 | 0.0204 | 0.0204 to 0.0206 | 12.0x |
| model_high_constraints | validity | 0.0001 | 0.0664 | 0.0652 to 0.0678 | 1177.6x |
| model_high_constraints | listing | 0.0001 | 0.0117 | 0.0116 to 0.0118 | 167.1x |
| model_high_constraints | pairs | 0.0001 | 0.0085 | 0.0084 to 0.0086 | 64.7x |
| model_low_constraints | validity | 0.0000 | 0.0444 | 0.0434 to 0.0448 | 4515.6x |
| model_low_constraints | listing | 0.0000 | 0.0201 | 0.0198 to 0.0206 | 766.7x |
| model_low_constraints | pairs | 0.0001 | 0.0079 | 0.0078 to 0.0080 | 62.8x |
| model_multivalue | validity | 0.0001 | 0.0826 | 0.0815 to 0.0843 | 1261.0x |
| model_multivalue | listing | 0.0001 | 0.0217 | 0.0211 to 0.0218 | 177.6x |
| model_multivalue | pairs | 0.0002 | 0.0093 | 0.0093 to 0.0099 | 44.8x |
| model_spins_core | validity | 0.0168 | 19.2902 | 19.2612 to 19.4159 | 1145.1x |
| model_spins_core | listing | 0.0209 | 0.9307 | 0.9263 to 0.9581 | 44.6x |
| model_spins_core | pairs | 0.0299 | 0.0525 | 0.0493 to 0.0539 | 1.8x |
| my_model | validity | 0.0000 | 0.0548 | 0.0535 to 0.0813 | 1631.7x |
| my_model | listing | 0.0000 | 0.0189 | 0.0189 to 0.0196 | 474.6x |
| my_model | pairs | 0.0001 | 0.0082 | 0.0080 to 0.0084 | 70.8x |

What the measurements show: in all 24 cells Z3 was slower than enumeration. The gap is largest for per-configuration
validity (about 1,100 to 4,500 times; this reflects rebuilding a solver per call, a property of this
implementation, not of Z3) and for listing (about 45 to 770 times). For feasible pairs it is smallest (about 2 to 71
times) and shrinks as the model grows: 1.8 times on model_spins_core.json (the largest, 978 valid configurations),
the only cell near parity. Z3 repeats were mostly stable (within about 10 percent of the median), except the first
repeat of some validity cells, which ran up to about 50 percent above it (my_model 0.0813 s vs median 0.0548 s); enumeration times below about 0.0001 s are at the timer's printed resolution,
so ratios in rows where the enumeration median prints as 0.0000 or 0.0001 (for example validity on
model_low_constraints, 4,515.6 times) are unreliable and only the direction is meaningful.
What it does not show: how either approach behaves on models too large to enumerate (none was tried), and nothing
here supports "Z3 is faster"; at this model size it is not. Single machine, 8 tiny models.

## Summary of research plan items 10 to 13: Z3 stage 1 (research plan item 14)

Origin: cloud run, not reproduced by the author. Every number is copied from the four sections above; none is new.
z3-solver 5.1.0.0 (optional; the core package stays standard library only). All checks are on the 8 models in
`examples/`, each with at most 978 valid configurations.

| item | Z3 function in `cla_harness/solver.py` | checked against | result on all 8 models | slowest-to-fastest vs enumeration (medians of 3 repeats) |
|---|---|---|---|---|
| 10 | `is_valid(parameters, forbidden, config)` | `valid_configurations`, full product (largest 4,096) | agreed on every configuration | Z3 slower in all 8: about 1,100 to 4,500 times (rebuilds the solver per call) |
| 11 | `valid_configurations_z3`, `sample_valid_configurations` | same set; samples must be valid | list equal on all 8; 1,000 of 1,000 samples valid on all 8 | listing: Z3 slower in all 8, about 45 to 770 times |
| 12 | `feasible_interactions_z3` (t = 2 only) | `feasible_interactions` | equal on all 8 (for example 38, 35 and 239 on three models) | Z3 slower in all 8, about 2 to 71 times; 1.8 times on `model_spins_core.json` |
| 13 | (timing only) | n/a | 24 of 24 cells: Z3 slower | spins core: validity 19.29 s vs 0.0168 s, listing 0.931 s vs 0.0209 s, pairs 0.0525 s vs 0.0299 s |

The suite with Z3 installed has 127 tests, OK, 3 skipped; with Z3 hidden, the Z3 tests skip.

What Z3 does now: it gives a second, independent way to answer three questions (is this configuration valid, which
configurations are valid, which pairs of values can co-occur) and on these 8 models it agrees with the enumeration
every time. That agreement is evidence the constraint encoding is right for rules of this form.

What Z3 does not change yet: the SA search, the greedy generators, the ceiling and the localization evaluator all
still enumerate valid configurations; nothing calls `solver.py` except its tests and timing scripts. No result in
the earlier sections depends on Z3. On these tiny models Z3 is slower than enumeration in every measured cell, so
nothing here shows a speed benefit.

What is not tested: any model too large to enumerate (the reason to use a solver), CASA-format models, strengths other
than 2 for interactions, and the sampler's distribution (reproducible but not uniform). Wiring Z3 into the search and
trying a large benchmark are item 15, which is marked STOP FOR USER.

## Z3 stage 2, item 15: lazy solver-backed cost (research plan item 15)

Origin: cloud run, not reproduced by the author. Base commit 0290c6b plus `scripts/item15_check.py` (new),
z3-solver 5.1.0.0. Added `Z3CostModel` to `cla_harness/solver.py` (`annealing.suite_cost` and all other existing
code unchanged). Construction takes the feasible 2-way interactions from `feasible_interactions_z3`. For each pair of
interactions that a suite covers with exactly the same tests, `separable(a, b)` asks Z3 whether some VALID configuration
contains one but not the other; such a pair is "avoidable". Answers are cached per unordered pair; `hits`,
`misses` and `seconds` record cache use and time inside Z3 queries. `suite_cost(suite, weight, detail)` returns the
same dictionary as `annealing.suite_cost` (uncovered, avoidable_collisions, cost, and with detail the sorted
uncovered and colliding lists). No enumerated list of valid configurations or precomputed `unavoidable` set is used.

Cross-check: on each of the 8 example models, 200 seeded random suites (random.Random(11); 1 to 16 configurations drawn
with repeats from the valid set), compared with `suite_cost` using the enumeration-based `unavoidable_pairs`,
including the detail lists: **identical on 200 of 200 suites on every model (1,600 of 1,600)**. The check was not vacuous:
185 to 200 suites per model had at least one avoidable collision (table). Tests: 3 new (the 8-model cross-check, weight and
caching, a deliberate break that treats every colliding pair as avoidable and is caught). Full suite: 130 tests OK, 3 skipped.

| model | suites identical | suites with avoidable collisions | suite_cost, 200 suites (s) | Z3 cost, 200 suites (s) | of which in Z3 queries (s) | cache misses / hits |
|---|---|---|---|---|---|---|
| model.json | 200 / 200 | 198 | 0.045 | 0.187 | 0.137 | 370 / 4,391 |
| model_6param.json | 200 / 200 | 199 | 0.069 | 0.450 | 0.369 | 1,001 / 9,261 |
| model_8param.json | 200 / 200 | 200 | 0.130 | 1.783 | 1.596 | 4,235 / 30,370 |
| model_high_constraints.json | 200 / 200 | 199 | 0.039 | 0.147 | 0.104 | 284 / 4,774 |
| model_low_constraints.json | 200 / 200 | 185 | 0.045 | 0.217 | 0.164 | 475 / 4,101 |
| model_multivalue.json | 200 / 200 | 199 | 0.053 | 0.265 | 0.202 | 526 / 5,409 |
| model_spins_core.json | 200 / 200 | 200 | 0.304 | 6.979 | 6.469 | 15,968 / 77,181 |
| my_model.json | 200 / 200 | 196 | 0.061 | 0.202 | 0.149 | 424 / 4,437 |

Timings are single runs; the Z3 column is cumulative for the 200 suites, so the cache fills as it goes (later suites
cost less). What it shows: the Z3 cost agrees with the enumeration-based cost exactly, and is slower on these models
(about 3 to 23 times for 200 suites), with almost all of the time in Z3 queries; on spins core about 0.4 ms per query
(15,968 misses in 6.47 s). What it does not show: behaviour on a model too large to enumerate (item 17), where the
number of distinct colliding pairs, and so of Z3 queries, is the thing to watch; or inside an SA loop, where suites
change one test at a time and the cache hit rate may differ from random suites. Random suites are not the suites SA
visits, so agreement is evidence for the classification, not for any search result.

## Z3 stage 2, item 16: solver-backed SA moves and search (research plan item 16)

Origin: cloud run, not reproduced by the author. Base commit 5e5c6f4 plus `scripts/item16_compare.py` (new), z3-solver
5.1.0.0. New functions in `cla_harness/solver.py` (`annealing.anneal_suite` and `find_small_suite` unchanged):
- `anneal_suite_z3(model, n_tests, seed, max_steps, start_temp, cooling, weight, neighbor)`: same acceptance rule,
  schedule and stopping rule as `anneal_suite`; the state is a list of configuration dicts; the cost is
  `Z3CostModel.suite_cost` (item 15); starting tests are Z3-drawn valid configurations. Moves: "random" replaces a
  test with a Z3-drawn valid configuration; "targeted" puts in a Z3-drawn valid configuration containing an uncovered
  interaction, or, for an avoidable collision, replaces a test lacking the chosen interaction with one containing it, or
  a test having it with a valid configuration that differs in exactly one parameter (found by Z3 with the other
  parameters fixed). The draws are random-order extensions, reproducible per seed, not uniform.
- `find_small_suite_z3(model, start_size, seed, restarts, steps_per_restart, ...)`: the cold shrinking search, mirroring
  `find_small_suite` (same cooling derivation and restart seeds; no warm start).
Tests (7 new, full suite 137 OK, 3 skipped): every test in every suite is valid (checked against the enumeration), the
returned cost equals a fresh recomputation, SA reaches the exact minima 9, 8 and 9 with both moves at the SAME budget as
the enumeration-based test (proven-minimum size, seeds 0 and 1, up to 20,000 moves), cannot solve one test below the
minimum, `find_small_suite_z3` started two above ends exactly at the minimum (3 restarts x 2000 moves, as for
`find_small_suite`), reproducibility, the one-change neighbor differs in exactly one parameter and is valid, and a
deliberate break (model with the rules removed produces forbidden tests) is caught.

Comparison on the 7 non-slow example models, seeds 0, 1 and 2, same settings for both searches (targeted moves, 3
restarts x 3000 moves per size, start = greedy locating size), `PYTHONPATH=. python3 scripts/item16_compare.py SEED`:
the final size from the Z3-backed search **equalled the enumeration-based search's size in all 21 of 21 runs**, and all
Z3 suites contained only valid tests.

| model | exact minimum (notes) | final size, enumeration SA / Z3 SA, seeds 0/1/2 | total moves, Z3 SA, seeds 0/1/2 | wall seconds enumeration SA | wall seconds Z3 SA |
|---|---|---|---|---|---|
| model.json | 9 | 9/9/9 and 9/9/9 | 9,367 / 9,572 / 9,294 | 2.0 / 2.0 / 2.1 | 14.3 / 14.7 / 13.7 |
| model_high_constraints.json | 9 | 9/9/9 and 9/9/9 | 9,008 / 9,030 / 9,116 | 1.8 / 1.9 / 1.9 | 14.0 / 14.1 / 14.7 |
| my_model.json | 8 | 8/8/8 and 8/8/8 | 9,139 / 9,681 / 9,652 | 2.0 / 1.9 / 1.8 | 14.6 / 15.3 / 16.0 |
| model_6param.json | not recorded | 10/10/10 and 10/10/10 | 9,730 / 10,964 / 11,448 | 4.7 / 4.0 / 4.5 | 20.3 / 22.4 / 23.1 |
| model_8param.json | not recorded | 11/12/11 and 11/12/11 | 12,853 / 9,694 / 13,645 | 8.8 / 9.0 / 14.6 | 38.3 / 29.3 / 40.5 |
| model_low_constraints.json | not recorded | 8/8/8 and 8/8/8 | 9,341 / 9,270 / 9,316 | 1.9 / 2.0 / 2.0 | 14.6 / 14.8 / 14.4 |
| model_multivalue.json | not recorded | 11/11/11 and 11/11/11 | 9,271 / 9,200 / 9,383 | 3.0 / 2.8 / 3.0 | 16.2 / 16.0 / 16.1 |

Where no exact minimum is recorded (the four lower rows) the sizes are what the searches FOUND, not shown minimal.
The enumeration-based sizes also agree with the earlier item 2 table (same settings). Timings: the three seeds ran
at the same time on a 4-core container, so seconds are approximate. Z3-backed search took about 3 to 9 times as
long as the enumeration-based one on these models. Most of the Z3 time is not in the cost queries: those took 0.1 to
1.2 s per search (item 15's cache answers nearly all of them; Z3 cache misses 139 to 2,957, hits 57,198 to 300,455);
the rest is in generating moves and starting tests, whose Z3 calls are not separately counted here.

What this shows: with Z3 supplying the moves and the cost, SA behaves like the enumeration-based SA on these small
models (same final sizes, valid tests, the proven minima reached). What it does not show: any benefit at this scale
(it is slower), anything on a model too large to enumerate (item 17), or that the two searches visit the same suites
(move counts differ because the random draws differ). Seven models, three seeds.

## Z3 stage 2, item 17: first model too large to enumerate, original spins (research plan item 17)

Origin: cloud run, not reproduced by the author. Base commit f598c4b, `scripts/item17_spins.py`, z3-solver 5.1.0.0.
Benchmark files: CCAG (GIST-NJU/CCAG, public, read access via the session's git proxy), cloned shallow into
`/home/user/gist-nju/ccag` OUTSIDE this repository; no CCAG file is committed. Model: `benchmark/spins.model` and
`spins.constraints`, loaded with `load_casa_model`. Command:
`PYTHONPATH=. python3 scripts/item17_spins.py /home/user/gist-nju/ccag/benchmark 0 40 6000 5 7200`.

Model facts (measured): 18 parameters, 46 values, 13 rules; 2,002,944 valid configurations (computed as 978 valid
configurations of the 9-parameter constrained core times 2,048 combinations of the 9 free parameters, which matches the
figure in docs/BENCHMARKS.md); 979 feasible 2-way interactions (from `feasible_interactions_z3`). The search never listed the valid configurations.

Search (the placeholders written into the plan; chosen without a measurement): Z3-backed targeted SA
(`find_small_suite_z3`), one seed (seed 0), start size 40, 6000 moves per run, 5 restarts per size, cooling from 2.0 to
0.05 over each run, shrinking one test at a time, wall-clock cap 7,200 s.

**Result: cost zero was NOT reached at the start size of 40.** All 5 runs at size 40 (30,000 moves in 960.6 s of wall
time) ended with cost above zero; the best run had 0 uncovered interactions and 3 avoidable collisions (cost 3.0), so
the best 40-test suite covered all 979 feasible interactions but still left 3 pairs of interactions that some valid test
could separate. No final suite size is recorded, because the plan allows recording one only if cost zero was reached.
The cap was not hit (the search stopped because size 40 failed). Per the plan the start size was not raised.

Z3 use in the cost function: 16,941 distinct pair queries (cache misses) and 934,952 cache hits, 9.9 s inside those
queries out of 960.6 s total; so about 32 ms per move overall, almost all of it outside the cost queries (move and
starting-test generation, and the Python cost loop), as in the item 16 comparison.

What this shows: the solver-backed search runs end to end on a model with about 2 million valid configurations that the
enumeration-based code was never run on, with every test a Z3-drawn valid configuration, and in 960 s reached full
coverage but not cost zero at 40 tests. What it does not show: whether 40 is too small for this budget, too small in
principle, or just needs more moves (the 9-parameter derived model needed 30 to 32 tests, which says nothing certain
about the full model); anything about suite sizes in the literature (not compared, by instruction); anything beyond one
seed and one budget. A failed size means not found within 5 x 6000 moves, not impossible.

## Summary of research plan items 15 to 17: Z3 stage 2 (research plan item 18)

Origin: cloud run, not reproduced by the author. Every number is copied from the three sections above; none is new
except the one marked "computed for this summary". z3-solver 5.1.0.0. The suite has 138 tests, OK, 3 skipped.

| item | what was built (`cla_harness/solver.py`) | check | result | cost compared with the enumeration-based code |
|---|---|---|---|---|
| 15 | `Z3CostModel`: lazy, cached, solver-backed `suite_cost` | 200 seeded random suites on each of the 8 example models vs `annealing.suite_cost`, including the detail lists | identical on 1,600 of 1,600 suites (185 to 200 suites per model had avoidable collisions) | Z3 slower: about 3 to 23 times for 200 suites; most time inside Z3 queries |
| 16 | `anneal_suite_z3` (random and targeted Z3 moves) and `find_small_suite_z3` (cold shrinking search) | exact minima 9, 8, 9 at the same budgets as the existing tests; 7 non-slow models x seeds 0 to 2 against `find_small_suite` | minima reached with both moves; final size equal to the enumeration-based search in 21 of 21 runs; all tests valid | Z3 slower: about 3 to 9 times; cost queries 0.1 to 1.2 s per search, the rest in move generation |
| 17 | (no new search code; `deadline`/`max_seconds` cap and progress callback added to the Z3 functions) | original `spins` (2,002,944 valid configurations, 979 feasible 2-way interactions), seed 0, start 40, 6000 moves x 5 restarts | cost zero NOT reached at 40: best run 0 uncovered, 3 avoidable collisions; no size recorded | 30,000 moves in 960.6 s (about 32 ms per move); 9.9 s in cost queries |

What the three items establish: the Z3-backed cost and the Z3-backed search agree with the enumeration-based ones on every
small model checked (same costs, same final sizes, valid tests, the proven minima), and the search can run on a model whose
2 million valid configurations were never listed.

What they do not establish:
- Any speed benefit: Z3 was slower in every comparison, on models small enough to enumerate.
- Any suite size for `spins`: the one run did not reach cost zero at its placeholder start size of 40. That says nothing
  yet about whether 40 is too small in principle, too small for this budget, or what the smallest size is. One seed, one
  budget, one model; not compared with published sizes.
- That the Z3 and enumeration searches visit the same suites (the random draws differ), or any property of the sampler's
  distribution (reproducible, not uniform).
- Strengths other than 2, other CASA models, or multiple faults.

Computed for this summary (not part of items 15 to 17; script-free, from `feasible_interactions_z3` on the loaded
`spins` model): the largest number of feasible value pairs for any single pair of parameters is 16 (P13 with P16), so no
suite of fewer than 16 tests can cover every feasible 2-way interaction. This is a coverage bound only, not a bound on
the size of a locating suite, and says nothing about whether 40 is close to the minimum.

Next steps are not in the plan yet; choosing a new start size should rest on measurements (best cost at several sizes and
budgets), not a guess. Item 19 is marked STOP FOR USER.

## Z3 stage 3, items 19 to 21: choosing the spins start size from measurements (research plan items 19, 20, 21)

Origin: cloud run, not reproduced by the author. Base commit 5d94a8d, scripts `scripts/item19_run.py` (new) and
`scripts/item17_spins.py`, z3-solver 5.1.0.0, original CCAG `spins` model (clone outside the repo; 2,002,944 valid
configurations, 979 feasible 2-way interactions), Z3-backed targeted SA, seed 0 throughout. Items 19 to 22 were added
to the plan by the research session after item 17's start size of 40 turned out to be an unmeasured placeholder.

**Item 19, one run of 6000 moves per size** (cooling 2.0 to 0.05 over the run; the five runs of items 19 and 20 shared a
4-core container, so seconds are approximate). Command: `PYTHONPATH=. python3 scripts/item19_run.py BENCH_DIR SIZE 6000`.

| size | solved (cost 0) | moves used | seconds |
|---|---|---|---|
| 56 | yes | 231 | 12.1 |
| 52 | yes | 856 | 36.3 |
| 48 | yes | 1,755 | 66.7 |
| 44 | yes | 3,286 | 114.8 |
| 40 (item 17: best of 5 runs of 6000 moves) | no, cost 3 | 30,000 | 960.6 |

For each solved run an independent check on the returned suite found all tests valid under the rules and 979 of 979
feasible interactions covered. The number of moves needed rose as the size fell (231, 856, 1,755, 3,286); that is four
points on one seed and does not by itself show a trend for other seeds.

**Item 20, size 40, one run of 30,000 moves** (same total moves as item 17's five runs, one slower cooling schedule):
not solved; final cost 4 (0 uncovered, 4 avoidable collisions), 945.4 s, tests valid, 979 of 979 covered. Item 17's best of
five shorter runs was cost 3. One seed each: this does not show that a long run is worse, only that spending the same moves
in one run did not reach zero at size 40 either, so more moves per run alone is not what separates 40 from 44.

**Item 21, shrinking search from the smallest size solved in item 19 (44)**, 5 restarts of 6000 moves per size, cap 7,200 s
(not reached). Command: `PYTHONPATH=. python3 scripts/item17_spins.py BENCH_DIR 0 44 6000 5 7200`.

| size | result | runs used | moves | best cost if unsolved |
|---|---|---|---|---|
| 44 | solved | 1 of 5 | 3,286 | - |
| 43 | solved | 1 of 5 | 4,134 | - |
| 42 | not solved | 5 of 5 | 30,000 | 1 (0 uncovered, 1 avoidable collision) |

**Smallest size at which cost zero was reached: 43 tests** (seed 0, this budget). Total 37,420 moves, 1,207.2 s, 19,282
distinct Z3 cost queries with 891,891 cache hits (12.2 s inside them). The 43-test suite, checked independently of the
cost code: all tests valid, 979 of 979 interactions covered, and 969 of 979 interactions have a signature (set of tests
containing them) that no other interaction shares. Z3 reports that the other 10 cannot be separated by any valid test
(that is what cost zero means here); I did not compute the ceiling independently for the full model. For information, the
derived 9-parameter model's ceiling gap in these notes is also 10 interactions (239 feasible, 229 localizable); that the two
sets of 10 are the same interactions was not checked.

What the three items show: on this model with this seed the cost at the unsolved sizes falls as the size rises (4 and 3 at 40,
1 at 42), cost zero is reached at 43 and above in the runs made, and the final answer at the placeholder size of 40 in item 17
was a size problem more than a budget problem (a 5x longer single run did no better). What they do not show: that 43 is the
smallest possible (42 failed all 5 runs within budget; more moves or other seeds may solve it), the spread over seeds (one
seed), or anything about published sizes (not compared, by instruction). The sizes found here are not comparable with the
derived model's 30 to 32 tests, which is a different model.

## Summary of research plan items 19 to 21 (research plan item 22)

Origin: cloud run, not reproduced by the author; numbers copied from the section above, none new.
- One seed, original spins, same cooling: cost zero in one 6000-move run at sizes 56, 52, 48 and 44 (231, 856, 1,755 and
  3,286 moves); not at 40 (best cost 3 over five runs, 4 in one run of 30,000 moves).
- The shrinking search from 44 reached cost zero at 44 and 43 and failed all five runs at 42 (best cost 1): smallest size
  found 43, with 979/979 coverage and 969/979 interactions uniquely identified by the suite, tests all valid.
- This gives the start-size question a measured answer for seed 0: 43 was reached, 40 and 42 were not within the budget.
  Whether 42 or fewer is possible, and how much the answer varies by seed, is open; a multi-seed spread like items 6 to 8
  on the derived model is the obvious next step and is not in the plan yet.

## Spread on the original spins model, seeds 0 to 9 (research plan items 23 and 24)

Origin: cloud run, not reproduced by the author. Base commit 57aec1f, `scripts/item17_spins.py`, z3-solver 5.1.0.0, CCAG
`spins` (clone outside the repo; 2,002,944 valid configurations, 979 feasible 2-way interactions). Z3-backed targeted shrinking
search exactly as in item 21: start size 44, 6000 moves per run, 5 restarts per size, cap 7,200 s per seed (never reached).
Seed 0 is the item 21 run (same code, run alone with one other job); seeds 1 to 9 ran up to four at a time on a 4-core
container, so seconds are approximate. Command: `PYTHONPATH=. python3 scripts/item17_spins.py BENCH_DIR SEED 44 6000 5 7200`.
Items 23 and 24 were added to the plan by the research session, because on the derived model the final size varied by seed.

| seed | smallest size with cost zero | sizes solved | first failed size | its best cost | total moves | seconds |
|---|---|---|---|---|---|---|
| 0 | 43 | 44, 43 | 42 | 1 | 37,420 | 1,207.2 |
| 1 | 42 | 44, 43, 42 | 41 | 1 | 62,409 | 2,030.3 |
| 2 | 43 | 44, 43 | 42 | 1 | 44,145 | 1,462.5 |
| 3 | 43 | 44, 43 | 42 | 1 | 51,099 | 1,693.9 |
| 4 | 43 | 44, 43 | 42 | 1 | 43,466 | 1,422.5 |
| 5 | 42 | 44, 43, 42 | 41 | 1 | 98,419 | 3,201.2 |
| 6 | 43 | 44, 43 | 42 | 1 | 63,680 | 2,086.0 |
| 7 | 44 | 44 | 43 | 1 | 34,295 | 1,106.0 |
| 8 | 43 | 44, 43 | 42 | 1 | 51,783 | 1,688.6 |
| 9 | 42 | 44, 43, 42 | 41 | 1 | 48,477 | 1,580.2 |

Over seeds 0 to 9: smallest sizes 42, 43, 44 reached by 3, 6 and 1 seeds (min 42, median 43, max 44); 535,193 moves in
total. No seed failed at the start size of 44. For every seed the returned suite was checked independently of the cost code:
all tests valid under the rules, 979 of 979 interactions covered, and 969 of 979 interactions uniquely identified by the suite
(the same 969 for all ten), and the cost model reports cost zero. In all ten searches the first size to fail had best cost 1 (no
uncovered interaction, one avoidable collision).

**Summary (item 24).** What the numbers show: on the original spins model with this budget, the smallest suite with cost zero
varies with the seed over 42 to 44 tests (median 43), so a single seed would have given 42, 43 or 44 depending on the draw; this
repeats the pattern seen on the derived model (30 to 32). The place where the search stops is consistent in one respect: every
search ended one size below its answer with cost 1, never with a large cost. The count of uniquely identified interactions
(969 of 979) was the same for all ten suites, which is what one would expect if the ten interactions that no test can separate
are the same set; that they are the same set was not checked. What the numbers do not show: that 42 (or 41) is the true minimum
or that 41 is impossible (a failed size means not found within 5 x 6000 moves; seeds 1, 5 and 9 reached 42, so a larger budget or
more seeds might reach lower); anything about a general advantage of the method; any comparison with published sizes (not made,
by instruction). Ten seeds on one model is still a small sample.

## Covering-only baseline versus locating, small models (research plan item 25)

Origin: cloud run, not reproduced by the author. Base commit 56a8da9 plus `scripts/item25_compare.py` (new), z3-solver 5.1.0.0.
Items 25 to 28 were proposed by the research session and approved by the plan author ("go"). Research question
(Research question section above): how much extra suite size makes feasible interactions distinguishable, compared with
ordinary constrained t-way coverage? Interaction localization only.

Code: `Z3CostModel(parameters, forbidden, cover_only=True)` makes the cost the number of uncovered feasible interactions
only (collisions neither counted nor queried); the default is unchanged. 3 new tests (cover-mode cost and uncovered list
equal a direct count on 100 random suites per model on all 8 example models and no Z3 separability query is made; cover-only
cost never exceeds locating cost; the cover-only search returns valid, fully covering suites no larger than the known locating
minimum). Full suite: 141 tests OK, 3 skipped.

Comparison, 7 non-slow models, seeds 0, 1 and 2, identical settings for both modes (Z3-backed cold shrinking search, targeted
moves, 3 restarts x 3000 moves per size, start = greedy locating size). Command:
`PYTHONPATH=. python3 scripts/item25_compare.py SEED`. Final sizes by seed 0/1/2; every cover-only suite was checked
independently to contain only valid tests and to cover all feasible interactions (21 of 21 True):

| model | valid | greedy cover | greedy locate | Z3 SA cover-only | Z3 SA locating | difference (locating - covering) |
|---|---|---|---|---|---|---|
| model.json | 18 | 6 | 11 | 5/5/5 | 9/9/9 | 4/4/4 |
| model_6param.json | 36 | 7 | 11 | 6/6/6 | 10/10/10 | 4/4/4 |
| model_8param.json | 144 | 7 | 13 | 7/7/7 | 11/12/11 | 4/5/4 |
| model_high_constraints.json | 11 | 7 | 11 | 6/6/6 | 9/9/9 | 3/3/3 |
| model_low_constraints.json | 32 | 6 | 9 | 6/6/6 | 8/8/8 | 2/2/2 |
| model_multivalue.json | 30 | 9 | 12 | 7/7/7 | 11/11/11 | 4/4/4 |
| my_model.json | 24 | 7 | 9 | 6/6/6 | 8/8/8 | 2/2/2 |

The locating columns equal the item 16 results for the same models and seeds. What this shows: on these seven small models
the distinguishable-signature requirement cost 2 to 5 extra tests over the smallest covering suite the search found, i.e.
about 1.3 to 1.8 times the covering size (8 vs 6 on low_constraints and my_model, 9 vs 5 on model.json),
and the covering size itself was stable across seeds (the locating size varied only on model_8param). The SA covering size was
at or below the greedy covering size on every model (equal on model_8param and model_low_constraints; one to two tests below
on the rest). What it does not show: that the covering sizes are minimal (search results at a fixed budget; no exact covering
minimum was computed), anything about larger models (items 26 and 27), or anything about strengths other than 2. Seven tiny
hand-built models, three seeds.

## Covering-only baseline versus locating, derived spins model, seeds 0 to 9 (research plan item 26)

Origin: cloud run, not reproduced by the author. Base commit ddd0a23, `scripts/item26_cover.py` (new), z3-solver 5.1.0.0.
Model: `examples/model_spins_core.json` (DERIVED from the CCAG `spins` benchmark, not the benchmark; 978 valid
configurations, 239 feasible 2-way interactions). Z3-backed cold shrinking search in cover-only mode, targeted moves, start 32,
6000 moves, 5 restarts per size, exactly as the locating runs of items 6 and 7 (which used the enumeration-based
`find_small_suite`; the same settings, different code path, so move counts are not comparable). Command:
`PYTHONPATH=. python3 scripts/item26_cover.py SEED cover`. Four seeds ran at a time on a 4-core container, so seconds are
approximate. For every seed the returned suite was checked independently: all tests valid and all 239 feasible interactions
covered (10 of 10 True).

| seed | covering size | locating size (items 6 and 7) | difference | covering moves | covering seconds |
|---|---|---|---|---|---|
| 0 | 18 | 30 | 12 | 40,746 | 290.9 |
| 1 | 18 | 31 | 13 | 39,332 | 286.0 |
| 2 | 18 | 32 | 14 | 39,607 | 284.5 |
| 3 | 18 | 31 | 13 | 39,928 | 286.3 |
| 4 | 18 | 30 | 12 | 40,288 | 241.6 |
| 5 | 18 | 31 | 13 | 38,734 | 231.6 |
| 6 | 18 | 31 | 13 | 39,877 | 235.6 |
| 7 | 18 | 30 | 12 | 37,311 | 221.3 |
| 8 | 18 | 30 | 12 | 39,748 | 237.0 |
| 9 | 18 | 31 | 13 | 40,504 | 242.5 |

Over the ten seeds: covering size 18 for every seed (min = median = max = 18); locating size min 30, median 31, max 32;
difference (locating minus covering) min 12, median 13, max 14; locating about 1.67 to 1.78 times the covering size. In every
covering search the size that failed all five runs was 17.
Computed for this section (not a run of the search): the largest number of feasible value pairs for any single pair of
parameters in this model is 16 (P13/P14, P13/P15, P14/P15), so no suite of fewer than 16 tests can cover every feasible
interaction; the search found 18 for all ten seeds and failed at 17 for all ten. A gap of 2 above that bound is a fact about
these runs; whether 16 or 17 is attainable was not tested.

What this shows: on this derived model, making interactions distinguishable cost about 12 to 14 additional tests over the
smallest covering suite the search found, and the covering size was the same for all ten seeds whereas the locating size varied
by seed. What it does not show: that 18 is the true covering minimum (a failed size means not found within 5 x 6000 moves);
anything about the real `spins` benchmark (item 27); anything beyond one derived model and ten seeds. The two sets of runs used
different code (enumeration-based locating, Z3-backed covering); on the small models of item 25 the two code paths gave the
same locating sizes, so this is not expected to matter, but it was not tested on this model.

## Covering-only baseline versus locating, original spins, seeds 0 to 9 (research plan item 27)

Origin: cloud run, not reproduced by the author. Base commit 781cab5, `scripts/item19_run.py` and `scripts/item17_spins.py` (both
given an optional trailing `cover` argument), z3-solver 5.1.0.0, original CCAG `spins` (clone outside the repo; 2,002,944
valid configurations, 979 feasible 2-way interactions). Z3-backed cold shrinking search in cover-only mode, targeted moves,
6000 moves per run, 5 restarts per size, cap 7,200 s per seed (never reached), four seeds at a time on a 4-core container (seconds
approximate). A first attempt at the ten-seed search was killed when the sandbox restarted (about 430 s in, no results) and was
rerun from the start; only the rerun is reported.

**Start size from a sweep (seed 0, one run of 6000 moves per size, cover mode):** 36, 32 and 28 reached cost zero (76, 495 and
2,667 moves); 24 did not (2 interactions uncovered); 20 did not (16 uncovered). The smallest solved, 28, was the start size.
Each solved suite was checked independently (all tests valid, 979 of 979 covered). Commands:
`scripts/item19_run.py BENCH_DIR SIZE 6000 0 cover` and
`PYTHONPATH=. python3 scripts/item17_spins.py BENCH_DIR SEED 28 6000 5 7200 cover`.

| seed | covering size | locating size (item 23) | difference | first failed size, best cost (uncovered) | covering moves | covering seconds |
|---|---|---|---|---|---|---|
| 0 | 25 | 43 | 18 | 24, 1 | 44,770 | 1,378.3 |
| 1 | 24 | 42 | 18 | 23, 4 | 54,789 | 1,656.9 |
| 2 | 25 | 43 | 18 | 24, 1 | 49,818 | 1,527.6 |
| 3 | 24 | 43 | 19 | 23, 3 | 52,602 | 1,581.8 |
| 4 | 23 | 43 | 20 | 22, 4 | 73,045 | 2,174.9 |
| 5 | 24 | 42 | 18 | 23, 2 | 58,364 | 1,788.7 |
| 6 | 24 | 43 | 19 | 23, 3 | 51,775 | 1,579.5 |
| 7 | 24 | 44 | 20 | 23, 1 | 53,920 | 1,650.0 |
| 8 | 23 | 43 | 20 | 22, 4 | 94,740 | 2,919.9 |
| 9 | 24 | 42 | 18 | 23, 1 | 50,408 | 1,546.5 |

Covering sizes over the ten seeds: 23, 24 and 25 reached by 2, 6 and 2 seeds (min 23, median 24, max 25). Difference
(locating minus covering): min 18, median 18.5, max 20; locating/covering per seed 1.72 to 1.87. Total 584,231 covering moves; no
seed hit the cap. For every seed the covering suite was checked independently: all tests valid and 979 of 979 interactions covered.
As a by-product, the same checks show how much distinguishing the covering suites achieved by accident: only 457 to 566 of 979
interactions had a signature no other interaction shares (against 969 for the locating suites of item 23).

What it shows: on the original spins model, making interactions distinguishable cost about 18 to 20 more tests than the smallest
covering suite the search found (covering 23 to 25, locating 42 to 44), roughly 1.7 to 1.9 times the size, and the covering size
varied by seed only over a range of 2. What it does not show: that the covering sizes are minimal (a failed size means not found within
5 x 6000 moves; the covering suite is above the bound of 16 computed in the item 18 notes, so 16 to 22 were not excluded); anything
about other benchmarks; a comparison with published sizes (not made). Ten seeds on one model.

## Summary of research plan items 25 to 27: extra tests needed to distinguish interactions (research plan item 28)

Origin: cloud run, not reproduced by the author; every number is copied from the items 25, 26, 27 sections above (locating sizes
from items 6, 7, 16 and 23); none is new. Interaction localization only (single deterministic fault, t = 2). Sizes are what the
search found within a fixed budget, not proven minima.

| model or group | seeds | covering size (search) | locating size (search) | extra tests (locating - covering) | locating / covering |
|---|---|---|---|---|---|
| model.json | 3 | 5/5/5 | 9/9/9 | 4/4/4 | 1.8 |
| model_6param.json | 3 | 6/6/6 | 10/10/10 | 4/4/4 | 1.67 |
| model_8param.json | 3 | 7/7/7 | 11/12/11 | 4/5/4 | 1.57 to 1.71 |
| model_high_constraints.json | 3 | 6/6/6 | 9/9/9 | 3/3/3 | 1.5 |
| model_low_constraints.json | 3 | 6/6/6 | 8/8/8 | 2/2/2 | 1.33 |
| model_multivalue.json | 3 | 7/7/7 | 11/11/11 | 4/4/4 | 1.57 |
| my_model.json | 3 | 6/6/6 | 8/8/8 | 2/2/2 | 1.33 |
| model_spins_core.json (derived from spins) | 10 | 18 for all (median 18) | 30 to 32 (median 31) | 12 to 14 (median 13) | 1.67 to 1.78 |
| spins (original, CCAG) | 10 | 23 to 25 (median 24) | 42 to 44 (median 43) | 18 to 20 (median 18.5) | 1.72 to 1.87 |

What the numbers show: in every model and every seed the smallest suite that made interactions distinguishable was larger than the
smallest covering suite the search found, by 2 to 5 tests on the seven small models, 12 to 14 on the derived spins model and 18 to
20 on the original spins model; as a ratio, 1.33 to 1.87 across all rows. The extra count grew with model size across these three
groups, while the ratio stayed in a narrower band (1.33 to 1.87); with three groups of very different models this is an
observation, not a fitted trend. On the two spins models the covering size was nearly constant across seeds (18 for all; 23 to 25)
while the locating size varied by 2 (30 to 32; 42 to 44).
What they do not show: that any covering or locating size is the true minimum; that the ratio is stable on other models or at other
strengths (t = 3, d > 1 were not measured here); anything about how the covering and locating sizes compare with published ones (not
compared, by instruction). Seven tiny hand-built models with 3 seeds, one derived model and one real benchmark with 10 seeds is a
small sample. The covering runs used the Z3-backed search and some locating runs the enumeration-based one; where both were run
on the same model and seed (items 16 and 25) the locating sizes were identical.

## Strength-t support in the Z3 code (research plan item 29)

Origin: cloud run, not reproduced by the author. Base commit 040d152, z3-solver 5.1.0.0. Items 29 to 32 were proposed by the research
session and approved by the plan author ("go"); the reason is that the research question is not limited to pairs and the
covering-versus-locating comparison (items 25 to 28) was strength 2 only.

Changes in `cla_harness/solver.py` (nothing else changed): `feasible_interactions_z3(parameters, forbidden, strength=2)` now
accepts any strength from 1 to the number of parameters (previously strength 2 only; the default and every existing call are
unchanged; other values raise ValueError), and `Z3CostModel(parameters, forbidden, cover_only=False, strength=2)` passes the
strength through. The cost code itself was already generic over interaction size.

Tests (5 new, 1 old test updated: the earlier "strength 3 raises ValueError" check became "strength 0 or one above the number of
parameters raises", because that restriction was deliberately lifted). On all 8 example models the Z3 interaction set equals
`feasible_interactions` from the enumeration at t = 1, 2 and 3; the default strength is 2; at t = 3 the Z3 locating cost
(including the detail lists) equals `annealing.suite_cost` on 200 seeded random suites per model (1,600 of 1,600), with avoidable
collisions present in the comparison for every model, and the Z3 cover-only cost equals a direct count of uncovered 3-way
interactions on the same suites; the cover-only and locating Z3 searches at t = 3 return valid suites covering every feasible
3-way interaction on model.json; a deliberate break is caught. Full suite: 146 tests OK, 3 skipped; it now takes about 393 s
(earlier 170 to 230 s), most of the increase from the t = 3 cost comparison on model_spins_core.json, which the strength-3 tests
exercise with 200 suites and many separability queries.

Not shown: any search result at t = 3 (items 30 and 31), speed at larger models, or the original spins model at t = 3 (which has at
most 13,328 candidate 3-way interactions, against 992 pairs and 1,520 for the derived model; item 33 reserves a faster cost
evaluation for a decision by the plan author).

## Strength 3: covering-only versus locating, small models (research plan item 30)

Origin: cloud run, not reproduced by the author. Base commit aa67773 plus `scripts/item30_compare.py` (new), z3-solver 5.1.0.0.
Strength 3: the hidden fault is one feasible 3-way interaction and only 3-way interactions are counted (interaction localization only).
Same settings as item 25 (Z3-backed cold shrinking search, targeted moves, 3 restarts x 3000 moves per size, start = greedy locating
size at t = 3), seeds 0, 1 and 2; the enumeration-based locating search (`find_small_suite`, same settings and seeds) was also rerun
as a direct consistency check. Three seeds ran at the same time on a 4-core container, seconds approximate. Command:
`PYTHONPATH=. python3 scripts/item30_compare.py SEED 3`. Every covering suite was checked independently (21 of 21: tests valid and
all feasible 3-way interactions covered). Final sizes, seeds 0/1/2:

| model | valid | feasible 3-way | greedy cover | greedy locate | Z3 cover-only | Z3 locating | enumeration locating | extra tests (Z3 locating - covering) | locating / covering | (t = 2: cover, locating) |
|---|---|---|---|---|---|---|---|---|---|---|
| model.json | 18 | 68 | 12 | 17 | 12/12/12 | 17/17/17 | 17/17/17 | 5/5/5 | 1.42 | 5, 9 |
| model_6param.json | 36 | 144 | 15 | 24 | 12/12/12 | 22/22/22 | 22/22/22 | 10/10/10 | 1.83 | 6, 10 |
| model_8param.json | 144 | 424 | 18 | 30 | 14/14/14 | 28/29/28 | 28/28/28 | 14/15/14 | 2.0 to 2.07 | 7, 11 to 12 |
| model_high_constraints.json | 11 | 55 | 10 | 11 | 9/9/9 | 11/11/11 | 11/11/11 | 2/2/2 | 1.22 | 6, 9 |
| model_low_constraints.json | 32 | 80 | 12 | 17 | 10/10/10 | 15/15/15 | 15/15/15 | 5/5/5 | 1.5 | 6, 8 |
| model_multivalue.json | 30 | 91 | 17 | 23 | 15/15/15 | 22/22/22 | 22/22/22 | 7/7/7 | 1.47 | 7, 11 |
| my_model.json | 24 | 74 | 13 | 17 | 10/10/10 | 17/17/17 | 17/17/17 | 7/7/7 | 1.7 | 6, 8 |

(The last column repeats the t = 2 sizes from items 25 and 16 for comparison.) Consistency: the Z3-backed locating size equalled the
enumeration-based size in 20 of 21 runs; the one difference was model_8param.json seed 1 (29 versus 28), where the two searches
draw different random moves, so one size apart on one seed is within the seed variation already seen on that model at t = 2. The
locating sizes also equal the item 4 enumeration-based t = 3 sizes (17, 22, 28, 11, 15, 22, 17) except that same case.
Greedy covering sizes were at or above the SA covering size on every model (equal on model.json: 12 and 12); on
model_high_constraints.json the locating size, 11, equals the number of valid configurations, so no smaller locating suite exists
there (which also caps the difference at 2).

What this shows: at t = 3 on these seven small models, distinguishing 3-way interactions needed 2 to 15 more tests than covering them
(ratio 1.22 to 2.07), against 2 to 5 more (ratio 1.33 to 1.8) at t = 2; the covering size rose roughly 1.5 to 2 times from t = 2 to
t = 3 (for example 5 to 12 on model.json, 7 to 14 on model_8param), and the locating size rose more (9 to 17, 11 to 28). The covering
size was identical across the three seeds on every model; the locating size varied only on model_8param. What it does not show: that
any size is minimal (search results at a fixed budget); anything about larger models or the derived spins model (item 31); a
statement about how the ratio behaves at other strengths. Seven tiny models, three seeds.

## Strength 3 on the derived spins model (research plan item 31)

Origin: cloud run, not reproduced by the author. Base commit 22dbdda plus the existing scripts `scripts/item31_probe.py`,
`item31_run.py` and `item31_search.py` (z3-solver 5.3.0, Python 3.11, 4-core container, up to 4 processes at a time, so timings are
approximate). Model: `examples/model_spins_core.json` (DERIVED from spins; it is not the benchmark), strength 3, 1,313 feasible
3-way interactions (the plan said at most 1,520 candidates). Interaction localization only; no source-code fault localization.

Timing (probe, 1 run each; 60-move targeted runs, 20 random suites): cost evaluation took 0.022 s (size 30) and 0.032 s (size 45) in
covering mode, and 1.0 s (size 30, the first evaluation 1.4 s, includes Z3 queries) and 0.17 s (size 45) in locating mode; a move
took 0.026 to 0.044 s (covering) and 0.057 to 0.114 s (locating) over those 60 moves. A 6000-move run therefore projects to well
under the 15-minute limit; measured full 6000-move runs took 154 to 323 s (covering, sizes 30 to 70) and 329 to 445 s (locating,
sizes 70 to 100), so the item continued.

Size sweep, seed 0, one 6000-move run per size, targeted moves, cooling 2.0 to 0.05 (`item31_run.py`; every returned suite had
valid tests and the independent coverage count matched):

| mode | size | uncovered | avoidable collisions | solved | moves | seconds |
|---|---|---|---|---|---|---|
| cover | 30 / 40 / 50 / 60 / 70 | 149 / 68 / 29 / 11 / 1 | 0 | no | 6000 | 154 / 199 / 238 / 280 / 323 |
| cover | 80 / 100 / 120 | 0 | 0 | yes | 345 / 64 / 37 | 21 / 5 / 4 |
| locate | 70 / 80 / 90 / 100 | 20 / 18 / 1 / 0 | 258 / 149 / 52 / 17 | no | 6000 | 329 / 366 / 407 / 445 |
| locate | 120 / 200 / 300 / 450 | 0 | 0 | yes | 1415 / 61 / 3 / 0 | 124 / 11 / 3 / 3 |

Start sizes chosen from the sweep (smallest size solved): covering 80, locating 120 (sizes between 100 and 120 were not swept).

Shrinking search, seeds 0 to 4, cold, targeted moves, 5 restarts x 6000 moves per size, cap 7,200 s per seed (`item31_search.py`;
every final suite checked: tests valid, all 1,313 interactions covered). "Capped" = the wall-clock cap ended the search; the cost
shown for the first failed size comes from an attempt the cap may have cut short.

| seed | covering size | locating size | difference | ratio | locating run | cost at first failed locating size (uncovered 0 in all) |
|---|---|---|---|---|---|---|
| 0 | 71 | 110 | 39 | 1.549 | capped at 7200 s while trying 109 | 1 |
| 1 | 71 | 112 | 41 | 1.577 | capped at 7200 s while trying 111 | 1 |
| 2 | 71 | 110 | 39 | 1.549 | finished, 6150 s, failed at 109 | 1 |
| 3 | 71 | 111 | 40 | 1.563 | capped at 7200 s while trying 110 | 2 |
| 4 | 71 | 110 | 39 | 1.549 | capped at 7200 s while trying 109 | 1 |

Covering searches finished without the cap (2,681 to 3,073 s, 45,565 to 50,606 moves); each failed at size 70 with 1 uncovered
interaction. Median covering 71, median locating 110, median difference 39 (range 39 to 41). Z3 queries in the locating searches:
12,564 to 14,034 misses and 13.4 to 15.7 million cache hits per seed. The locating sizes of seeds 0, 1, 3 and 4 are upper bounds
from a capped search (a smaller suite might have been found with more time).

What this shows: on this derived model at t = 3, the search found covering suites of 71 tests for all five seeds and locating suites
of 110 to 112, about 39 to 41 more tests (1.55 to 1.58 times). At t = 2 on the same model the found sizes were 18 (covering) and 30 to
32 (locating), so both grew with strength and the extra cost grew from about 13 to about 39 tests (ratio about 1.7 to about 1.55,
from items 26 and 28). The covering size was the same on all five seeds. What it does not show: that any size is minimal (search
results at a fixed budget; four of the five locating runs were capped); anything about the original spins model (item 33 is for
the plan author); a comparison with published sizes. Five seeds, one derived model.

Test suite before this commit (cloud run, not reproduced by the author): 146 tests, OK, 3 skipped, 420 s.

## Summary of research plan items 29 to 31: strength 2 versus strength 3 (research plan item 32)

Origin: cloud run, not reproduced by the author; every number is copied from the items 28, 30 and 31 sections above; none is new.
Interaction localization only (single deterministic fault); no source-code fault localization. Sizes are what a fixed-budget search
found, not proven minima.

| model or group | seeds at t = 3 | t = 2 cover / locate / extra / ratio | t = 3 cover / locate / extra / ratio |
|---|---|---|---|
| model.json | 3 | 5 / 9 / 4 / 1.8 | 12 / 17 / 5 / 1.42 |
| model_6param.json | 3 | 6 / 10 / 4 / 1.67 | 12 / 22 / 10 / 1.83 |
| model_8param.json | 3 | 7 / 11 to 12 / 4 to 5 / 1.57 to 1.71 | 14 / 28 to 29 / 14 to 15 / 2.0 to 2.07 |
| model_high_constraints.json | 3 | 6 / 9 / 3 / 1.5 | 9 / 11 / 2 / 1.22 |
| model_low_constraints.json | 3 | 6 / 8 / 2 / 1.33 | 10 / 15 / 5 / 1.5 |
| model_multivalue.json | 3 | 7 / 11 / 4 / 1.57 | 15 / 22 / 7 / 1.47 |
| my_model.json | 3 | 6 / 8 / 2 / 1.33 | 10 / 17 / 7 / 1.7 |
| model_spins_core.json (derived, not the benchmark) | t = 2: 10; t = 3: 5 | 18 / 30 to 32 (median 31) / 12 to 14 (median 13) / 1.67 to 1.78 | 71 / 110 to 112 (median 110) / 39 to 41 (median 39) / 1.549 to 1.577 |
| spins (original, CCAG) | t = 2: 10; t = 3: not run | 23 to 25 / 42 to 44 / 18 to 20 / 1.72 to 1.87 | not run (item 33, plan author's decision) |

What the numbers show: on the seven small models the covering size went up from t = 2 to t = 3 on every model (for example 5 to 12 on
model.json), the locating size went up on every model, and the extra tests (locating minus covering) went up on every model except
model_high_constraints.json, where the t = 3 locating size, 11, equals the number of valid configurations, which caps the difference
at 2. The ratio went up on four small models and down on three (model.json, model_high_constraints.json, model_multivalue.json), so
no direction of the ratio is shown for the small models. On the derived spins model the extra tests grew from 12 to 14 to 39 to 41
while the ratio fell slightly (1.67 to 1.78 to 1.549 to 1.577). Four of five derived-model locating searches at t = 3 were stopped
by the 7,200 s cap, so those locating sizes are upper bounds from capped searches. On the small models the Z3-backed locating size
equalled the enumeration-based size in 20 of 21 runs (the exception, model_8param.json seed 1, 29 versus 28).
What they do not show: that any size is minimal; ten seeds were not run at t = 3 (3 seeds on the small models, 5 on the derived
model, none on original spins); anything about the original spins model at t = 3; any comparison with published sizes (not made, by
instruction); behaviour at other strengths or with more than one fault.

Test suite before this commit (cloud run, not reproduced by the author): 146 tests, OK, 3 skipped, 393 s (z3-solver 5.3.0).

## FastZ3CostModel (research plan item 34)
Added `FastZ3CostModel` to cla_harness/solver.py (subclass of Z3CostModel; parent unchanged). Tests (tests/test_solver.py, class FastCostModel): its cost and detail lists equal Z3CostModel and, in locating mode, annealing.suite_cost, at t = 2 and t = 3 on all 8 example models (100 random suites per model, 10 on model_spins_core.json to keep the suite time down). Full suite in this session: 149 tests OK, 3 skipped (cloud run, not reproduced by the author). No speed measurement yet: that is item 35. The search functions were not yet run with the fast model beyond a small smoke test.

## Cost-evaluation timing, FastZ3CostModel versus Z3CostModel, strength 3, derived spins (research plan item 35)
Cloud run, not reproduced by the author. model_spins_core.json, t = 3, 1,313 feasible 3-way interactions, 5 random suites of 32 valid tests (seed 0), mean seconds per `suite_cost` call, python 3.13 / z3 5.3.0.0. One model, one suite size, one seed.

| model class | mode | build (s) | first evaluation (s) | repeat evaluation, same suites (s) | Z3 queries (misses) | Z3 time (s) |
|---|---|---|---|---|---|---|
| Z3CostModel | cover | 1.61 | 0.0190 | 0.0184 | 0 | 0 |
| Z3CostModel | locate | 0.57 | 1.5667 | 0.0184 | 12210 | 7.61 |
| FastZ3CostModel | cover | 0.45 | 0.0025 | 0.0005 | 0 | 0 |
| FastZ3CostModel | locate | 0.39 | 1.4168 | 0.0040 | 12210 | 6.99 |

What this shows: the repeat evaluation (collision answers cached) is faster with the fast model (0.0040 s versus 0.0184 s locating; 0.0005 s versus 0.0184 s covering). The first locating evaluation on new suites is dominated by Z3 collision queries, which are the same for both classes (12,210 queries), so the fast model changes little there. Not measured: time per move inside a real search, the cache hit rate over a full run, and anything on the original spins model (the CCAG clone was not used in this step). Whether item 33 (original spins, t = 3) is feasible is therefore not settled by this table; the next step would be to time a short search run and one cost evaluation on the original model.

## Search-level timing, fast versus Z3 cost model, derived spins at t = 3 (research plan item 36)
Cloud run, not reproduced by the author. model_spins_core.json (derived, not the benchmark), t = 3, targeted moves, seed 0, 600 moves, cooling for a 6000-move run, python 3.13 / z3 5.3.0.0. One seed, one run per row.

| mode | size | model class | seconds | seconds per move | final uncovered / avoidable collisions | Z3 cache hits / misses |
|---|---|---|---|---|---|---|
| cover | 71 | Z3CostModel | 29.6 | 0.049 | 15 / 0 | 0 / 0 |
| cover | 71 | FastZ3CostModel | 4.3 | 0.007 | 15 / 0 | 0 / 0 |
| locate | 110 | Z3CostModel | 46.3 | 0.077 | 14 / 85 | 164,597 / 1,399 |
| locate | 110 | FastZ3CostModel | 5.3 | 0.009 | 14 / 85 | 164,597 / 1,399 |

For both modes the two classes returned the identical suite and cost, with the same number of accepted moves (392 and 36). In these 600-move runs the fast class took about one seventh (cover) and one ninth (locate) of the time per move. Not measured: whole 6000-move runs or a shrinking search with the fast class, and anything on the original spins model (plan item 37). The Z3 query time was about 1 s of the 46 s in the locating run, so in a search the cost loop, not Z3, dominated here; item 35's first-evaluation timing was a different situation (new suites, many fresh queries).

## Original spins at t = 3: timing with the fast cost model (research plan item 37)
Cloud run, not reproduced by the author. Model: original CCAG `spins` (clone at depth 1 in a folder outside this repository; nothing from it committed), strength 3, FastZ3CostModel, python 3.13 / z3 5.3.0.0. One size (100 tests), seed 0, targeted moves, cooling for a 6000-move run. The size 100 is a placeholder chosen without a size sweep, so the final costs say nothing about the achievable size. No seed search was started (item 33 stays with the plan author).

- Feasible 3-way interactions: 12,835 (the plan said at most 13,328 candidates). Model build: 4.6 s (covering), 4.5 s (locating).
- Cost evaluation on 3 random valid suites of 100 tests: covering 0.1809 s first, 0.0415 s repeat; locating 8.9042 s first (35,173 Z3 queries, 25.8 s Z3 time over the 3 suites), 0.0529 s repeat.
- 300-move targeted runs: covering 15.2 s (0.051 s per move, 123 accepted, final 150 uncovered); locating 69.6 s (0.232 s per move, 53 accepted, final 242 uncovered and 5,304 avoidable collisions; 101,470 Z3 misses, 1,969,703 cache hits, Z3 time reported as 70.8 s, slightly above the wall time, so treat Z3 time as approximate).
- Full 6000-move targeted runs, started together in two processes (4-core container, so timings are approximate), cap 900 s:

| mode | size | moves | accepted | seconds | final uncovered | final avoidable collisions | Z3 misses / hits |
|---|---|---|---|---|---|---|---|
| cover | 100 | 6000 | 488 | 275.4 | 38 | 0 | 0 / 0 |
| locate | 100 | 6000 | 116 | 544.6 | 197 | 3,857 | 152,136 / 28,347,311 |

Neither run reached the 900 s cap, so a 6000-move run on original spins at t = 3 fits under 15 minutes in both modes at size 100 (measured, one size, two runs running at the same time). Neither reached cost zero at size 100, so size 100 is below what these runs could solve; a size sweep (as in items 19 and 27) is the next step, then a shrinking search. Not measured: larger sizes (cost per move grows with size in the earlier derived-model runs), a shrinking search, other seeds. Interaction localization only.

## Original spins at t = 3: size sweep (research plan item 39)
Cloud run, not reproduced by the author. `scripts/item39_run.py`, original CCAG spins (clone outside the repo), t = 3, FastZ3CostModel, targeted moves, seed 0, ONE run of up to 6000 moves per size (cooling 2.0 to 0.05 over 6000 moves), cap 3,600 s, 4 processes at a time on a 4-core machine (times approximate), 12,835 feasible 3-way interactions. One seed.

| mode | size | solved | moves used | seconds | Z3 cost queries (misses / hits) |
|---|---|---|---|---|---|
| cover | 120 | yes | 5,333 | 157.4 | 0 / 0 |
| cover | 140 | yes | 1,773 | 58.5 | 0 / 0 |
| cover | 160 | yes | 402 | 14.1 | 0 / 0 |
| cover | 200 | yes | 92 | 5.0 | 0 / 0 |
| locate | 200 | yes | 5,492 | 210.6 | 9,103 / 2,188,489 |
| locate | 260 | yes | 737 | 33.6 | 1,483 / 281,229 |
| locate | 320 | yes | 158 | 10.1 | 548 / 60,201 |
| locate | 400 | yes | 41 | 5.5 | 378 / 14,785 |

Every run reached cost zero with all tests valid, so all eight sizes were solved; the sweep did not find where solving stops, and the smallest solved sizes (covering 120, locating 200) are therefore only upper bounds on what this budget can reach. The moves used fall as the size grows, and the two smallest sizes used most of the 6000 moves (5,333 and 5,492). Item 37's size 100 did not reach cost zero (covering: 38 uncovered after 6000 moves), so the covering threshold for this budget lies between 100 and 120 in these two runs (different seeds of the run are not compared; one run each). Not measured: anything between the sizes. Item 40 starts the shrinking search at 120 (covering) and 200 (locating).

## Original spins at t = 3: shrinking search, seeds 0 to 4 (research plan item 40)
Cloud run, not reproduced by the author. `scripts/item40_shrink.py`, original CCAG spins (clone outside the repo), t = 3, FastZ3CostModel, `find_small_suite_z3`, targeted moves, 6000 moves per run, 5 restarts per size, cap 7,200 s per seed (never reached), start 120 (covering) and 200 (locating) from item 39, shrinking one test at a time, 4 processes at a time on 4 cores (times approximate). 12,835 feasible 3-way interactions. Sizes are what the search found, not proven minima.

| seed | covering size | locating size | difference | ratio | covering: best cost at first failed size (uncovered) | locating: best cost at first failed size (avoidable collisions) | covering s | locating s |
|---|---|---|---|---|---|---|---|---|
| 0 | 114 | 199 | 85 | 1.746 | 5 (at 113) | 1 (at 198) | 3,686 | 2,060 |
| 1 | 115 | 197 | 82 | 1.713 | 1 (at 114) | 2 (at 196) | 2,509 | 3,563 |
| 2 | 116 | 199 | 83 | 1.716 | 2 (at 115) | 2 (at 198) | 2,554 | 3,955 |
| 3 | 116 | 198 | 82 | 1.707 | 1 (at 115) | 2 (at 197) | 2,111 | 2,986 |
| 4 | 114 | 200 | 86 | 1.754 | 1 (at 113) | 3 (at 199) | 2,574 | 1,815 |

Min / median / max over seeds 0 to 4: covering 114 / 115 / 116; locating 197 / 199 / 200; difference 82 / 83 / 86; ratio 1.707 to 1.754. Locating-mode failures had 0 uncovered interactions; their remaining cost was all avoidable collisions. No seed was capped. Locating seed 4 failed at the very first shrink step (200 to 199), and locating sizes sit within 3 of the start size 200 for every seed, so these locating sizes lie close to the start size chosen from item 39; the start size, not only the search, may limit what is found, and a restart from a larger or smaller start was not run. Item 39 solved locating size 200 only after 5,492 of 6,000 moves, consistent with 200 being near this budget's limit, but that is one run. Not measured: other seeds beyond 0 to 4, longer budgets, strength 2 for comparison on the same budget (items 23 and 27 are strength 2 with different budgets), anything compared with published sizes. Five seeds on one model is a small sample. Interaction localization only.

## Second large CCAG benchmark: feasibility check (research plan item 41)
Cloud run, not reproduced by the author. `scripts/item41_probe.py` (load + `FastZ3CostModel` build at t = 2), CCAG cloned outside the repo (shallow clone of GIST-NJU/ccag, not committed). Strength 2, interaction localization only. z3-solver 5.3.1 was pip-installed into the container for this run. The clone has 5 named models (apache, bugzilla, gcc, spins, spinv) plus `benchmark_1` to `benchmark_30` (`.model` files only, no `.constraints` files, so not loadable by `load_casa_model` as called here; not tried).

| model | parameters | values | rules | candidate 2-way | feasible 2-way | load s | Z3 build s |
|---|---|---|---|---|---|---|---|
| apache | 172 | 367 | 7 | 66,930 | 66,927 | 0.0 | 11.9 |
| bugzilla | 52 | 109 | 5 | 5,822 | 5,818 | 0.0 | 0.8 |
| gcc | 199 | 408 | 40 | 82,809 | 82,770 | 0.0 | 18.4 |
| spinv | 55 | 134 | 49 | 8,797 | 8,741 | 0.0 | 1.9 |

All four load and build in well under 5 minutes, so the setup condition of the item is met. I chose spinv (most rules per parameter, small build) for a covering-versus-locating run at t = 2.

Size sweep on spinv, seed 0, ONE run of 6000 targeted moves per size (`scripts/item39_run.py ... spinv`, 6 processes on 4 cores so times are inflated; cap 900 s):

| mode | size | solved | uncovered | avoidable collisions | moves | seconds |
|---|---|---|---|---|---|---|
| cover | 15 | no | 768 | 0 | 6,000 | 517 |
| cover | 20 | no | 414 | 0 | 6,000 | 527 |
| cover | 30 | no | 148 | 0 | 6,000 | 545 |
| locate | 30 | no (hit 900 s cap) | 313 | 9,003 | 4,189 | 900 |
| locate | 45 | no | 96 | 1,325 | 6,000 | 651 |
| locate | 60 | no | 17 | 174 | 6,000 | 603 |

No size reached cost zero, so the sizes I guessed were all too small for this budget and no shrinking search or covering-versus-locating comparison was run. Not measured: the size at which spinv is solved. Cost fell with size in every mode, but this is one run each and nothing is extrapolated. Per-move cost is high (about 0.09 s per move in covering at these sizes with oversubscribed cores), which makes a seed search on spinv a long job.

## Open questions (item 41)
- spinv at t = 2: placeholder sizes 15 to 30 (cover) and 30 to 60 (locate) were all unsolved at 6000 moves. A larger sweep is needed before any covering-versus-locating run; not done in this session.
- `benchmark_N.model` files have no `.constraints` file in the clone; whether they carry constraints another way was not checked.

## spinv at t = 2: covering versus locating, seeds 0 to 2 (research plan item 41, continued; supersedes the sweep and the .constraints remark in the item 41 section above)
Cloud run, not reproduced by the author. Written by the live session; an earlier scheduled run wrote the feasibility section above in parallel. Two points in that section disagree with this session's runs: (1) `benchmark_1` ... `benchmark_30` DO have `.constraints` files in the clone used here (`benchmark_1.constraints` etc.), and `benchmark_1` and `benchmark_20` loaded and built (benchmark_1: 97 parameters, 222 values, 24 rules, 24,350 candidate and 23,876 feasible 2-way interactions, Z3 build 4.9 s; benchmark_20: 158 parameters, 370 values, 48 rules, 67,940 candidate and 64,620 feasible, build 17.6 s); (2) its spinv sizes were all too small, while larger sizes are solved here. Scripts: `scripts/item41_probe.py`, `scripts/item39_run.py ... spinv`, `scripts/item40_shrink.py ... spinv`; t = 2, FastZ3CostModel, targeted moves, 8,741 feasible 2-way interactions, 4 cores shared by up to 6 processes (times approximate).

Size sweep, seed 0, one 6000-move run per size: covering unsolved at 20 (414 uncovered), 30 (148) and 40 (30), solved at 50, 60, 70, 80; locating unsolved at 60 (17 uncovered, 174 avoidable collisions) and 80 (0 uncovered, 1 avoidable), solved at 100 (sizes 70 and 90 not run).

Shrinking search (6000 moves, 5 restarts per size, cap 7,200 s per seed), covering from 50 and locating from 100:

| seed | covering size | locating size | difference | ratio | covering: cost at first failed size | locating: cost at first failed size |
|---|---|---|---|---|---|---|
| 0 | 48 | 79 (hit the cap while trying 78) | 31 | 1.646 | 1 uncovered (at 47) | 1 avoidable collision (at 78; cap-truncated) |
| 1 | 49 | 79 | 30 | 1.612 | 1 uncovered (at 48) | 1 avoidable (at 78) |
| 2 | 48 | 78 | 30 | 1.625 | 1 uncovered (at 47) | 3 avoidable (at 77) |

Min / median / max: covering 48 / 48 / 49; locating 78 / 79 / 79; difference 30 to 31; ratio 1.612 to 1.646. In the sweep the single run at size 80 failed (cost 1) while all three shrinking searches got below 80, so one run per size is not a reliable test of a size. Sizes are search results, not proven minima; three seeds, one model, t = 2, interaction localization only; nothing compared with published sizes.

## Distinguishable-interaction ceiling by Z3 on large models (research plan item 42)
Cloud run, not reproduced by the author. `scripts/item42_ceiling.py`, t = 2, d = 1, interaction localization only. Method: 400 seeded Z3-sampled valid configurations; pairs of interactions that some sampled test separates are separable (the test is a valid witness); every remaining pair gets the exact Z3 query "is there a valid configuration containing exactly one of them" (Jin & Tsuchiya Lemma 1). An interaction counts as distinguishable if it has no inseparable partner. This is the same quantity as `experiment.ceiling_of`: the Z3 count equals `ceiling_of` on all 8 example models (`scripts/item42_check.py`; for example model_high_constraints 28 of 35, model_spins_core 229 of 239).

| model | feasible 2-way | pairs needing a query after the pool | inseparable pairs | interactions in an inseparable pair | distinguishable | query time (s) |
|---|---|---|---|---|---|---|
| spins | 979 | 9 | 9 | 10 | 969 | 0.0 |
| spinv | 8,741 | 599 | 599 | 1,084 | 7,657 | 0.3 |
| bugzilla | 5,818 | 0 | 0 | 0 | 5,818 | 0.0 |
| benchmark_1 | 23,876 | 917 | 917 | 1,354 | 22,522 | 0.4 |
| benchmark_20 | 64,620 | 11,039 | 11,037 | 2,931 | 61,689 | 4.8 |

The all-pairs counts (for example 478,731 for spins) were never queried; the pool removed all but a few hundred to ~11,000 pairs per model. The pool is one seeded sample, so a different sample could leave a different number of pairs to query but not change the exact answers. On spins the best locating suites of items 21 to 27 reached cost zero, which by the cost definition means no avoidable collision remains, so what they leave unseparated is exactly these inseparable pairs; this is by construction, not a separate measurement. Not measured: t = 3 ceilings, the other CCAG models, d = 2.

## Summary of research plan items 38 to 42 (research plan item 43)
All numbers below are cloud runs, not reproduced by the author; each is in the section named. Sizes are search results at a fixed budget, not proven minima. Interaction localization only. Nothing is compared with published sizes.

| model, strength | seeds | covering size (min / median / max) | locating size (min / median / max) | difference | ratio | section |
|---|---|---|---|---|---|---|
| original spins, t = 2 | 10 | 23 to 25 (median 24) | 42 to 44 (median 43) | 18 to 20 | 1.72 to 1.87 | item 28 summary |
| original spins, t = 3 | 5 | 114 / 115 / 116 | 197 / 199 / 200 | 82 to 86 | 1.707 to 1.754 | "Original spins at t = 3: shrinking search" (item 40) |
| spinv, t = 2 | 3 | 48 / 48 / 49 | 78 / 79 / 79 | 30 to 31 | 1.612 to 1.646 | "spinv at t = 2" (item 41) |

(The first row is copied from the item 28 summary; rows 2 and 3 are this session's runs.)

Indistinguishable interactions (t = 2, d = 1, Z3), from the item 42 section: spins 10 of 979 interactions in an inseparable pair, spinv 1,084 of 8,741, bugzilla 0 of 5,818, benchmark_1 1,354 of 23,876, benchmark_20 2,931 of 64,620.

What the numbers show: on the two large benchmarks tried, a suite that distinguishes interactions needed about 1.6 to 1.9 times the tests of a suite that only covers them (original spins t = 2: 1.72 to 1.87; t = 3: 1.707 to 1.754; spinv t = 2: 1.612 to 1.646), at the budgets used. What they do not show: whether this holds on other models, at other budgets (the t = 3 locating searches ended within 3 tests of their start size 200), or against published sizes. The literature check (docs/LITERATURE_CHECK.md section 6) found Garvin et al. (constrained covering arrays by meta-heuristic) and Konishi et al. (SA, unconstrained locating arrays) but no constrained-locating-array metaheuristic paper in three excerpt-only searches; that is a weak negative, not a novelty claim.

## Needs your decision (added by item 43)
- Comparison with published sizes: needs the primary papers' definitions read first (Jin & Tsuchiya 2020; Konishi et al.), then a model and strength where definitions match.
- Whether to extend: more seeds on spinv or benchmark_20, a longer or restarted-from-larger t = 3 locating search (sizes were near the start size), d = 2, nondeterminism, anything AI-based.

## Comparison with published CLA sizes (research plan item 44)
Origin: cloud run, not reproduced by the author. Scripts `scripts/item44_run.py` (search, saves the final suite) and `scripts/item44_verify.py` (checks a saved suite); suites in `docs/item44_suites/`. Interaction localization only. t = 2, d = 1.

**Definitions checked (Jin & Tsuchiya 2020, arXiv 1801.06041, text obtained via a PDF-to-markdown fetch; wording and table figures should be checked against the PDF before quoting).** Their experiments generate (1bar,2)-CLAs: every valid 2-way interaction is covered, and every pair of valid interactions that is distinguishable (Definition 1 / Lemma 1) is separated by some test (their SMT section: coverage constraint plus, for each distinguishable pair, a row covering only one of them). That is the same condition as `cost == 0` in `FastZ3CostModel` (0 uncovered, 0 avoidable collisions). Table 1 columns that match this repo's own numbers: valid 2-way interactions Spins 979, Spinv 8,741, Bugzilla 5,818, and indistinguishable pairs Spins 9, Spinv 599, Bugzilla 0 (the verifier below left exactly 9, 599, 0 inseparable pairs).

**Published heuristic (their Table 1, 10 runs each; min to max over runs; C++, CIT-BACH 3-way covering array then row deletion, 3.2 GHz Xeon):** Spins 49 to 53 (1 s), Bugzilla 41 to 48 (about 9 s), Spinv 91 to 97 (about 58 s). Their SMT method timed out on all three.

**This repo's search (Z3-backed targeted SA, start size shown, 6000 moves x 5 restarts per size, shrink by one; times on a 4-core shared container):**

| model | seed | start | final size | verified (item44_verify) | first failed size: best cost | total moves | time (s) |
|---|---|---|---|---|---|---|---|
| spins | 0 | 44 | 43 | yes | not recorded here | 37,420 | 265 |
| spins | 1 | 44 | 42 | yes | not recorded here | 62,409 | 450 |
| spins | 2 | 44 | 43 | yes | not recorded here | 44,145 | 325 |
| bugzilla | 0 | 60 | 37 | yes | 36: 5 avoidable collisions | 74,164 | 2,986 |
| spinv | 0 | 90 | 79 | yes | 78: 1 avoidable collision | 99,012 | 5,893 |
| spinv | 1 | 90 | 79 | yes | 78: 1 avoidable collision | 84,271 | 4,833 |

Verification: `item44_verify.py` rechecks each saved suite with its own Z3 encoding (it shares only the .model/.constraints loader with the search): all tests valid, 0 uncovered, 0 avoidable collisions, so each is a (1bar,2)-CLA by the definition above. Reproducibility: spins seed 0 gave 43 tests and 37,420 moves, identical to the item 21 / 23 record.

**What this shows:** on these three CCAG models, at this budget, this search found valid (1bar,2)-CLAs smaller than the sizes in the published table (spins 42 to 43 against 49 to 53; bugzilla 37 against 41 to 48; spinv 79 against 91 to 97). **What it does not show:** that the method is better. The two use different algorithms and very different compute (published heuristic: seconds; this search: 4 to 98 minutes per run), different hardware, and the published numbers are read from a converted PDF. Seeds: 3, 1 and 2, so bugzilla is one data point. Sizes are search results, not proven minima. Not run: apache, gcc, the CitLab/literature benchmarks 1 to 25, t = 3 against anything published (they evaluated only t = 2, d = 1), and a time-matched comparison.

## Needs your decision (added by item 44)
- Item 44 found sizes below the published heuristic's on spins, bugzilla and spinv. Before this goes in a paper: (a) check Table 1 against the PDF (figures were read from a converted copy); (b) decide whether to run a time-matched comparison (limit our search to their seconds-scale budgets) and whether to add apache, gcc and the CitLab benchmarks; (c) ask whether the authors' CLA tool or SA4LA can be run on the same machine for a like-for-like size comparison.

## Comparison with published CLA sizes, continued (research plan item 45)
Cloud run, not reproduced by the author. Same scripts and definition as item 44; all suites in `docs/item44_suites/`; every suite below was checked by `scripts/item44_verify.py` (valid tests, 0 uncovered, 0 avoidable collisions). t = 2, d = 1, interaction localization only. Runs shared 4 cores with up to 4 other searches, so times are approximate.

**Table 1 cross-check.** A second rendering (arXiv HTML v2, answered by a direct-quote query) gives the same first two numeric columns as the PDF conversion: Apache 89 / 85, Bugzilla 48 / 41, GCC 68 / 61, Spins 53 / 49, Spinv 97 / 91, and the same valid-pair and indistinguishable-pair columns (the HTML table's column headers were garbled, so these are max / min of the heuristic as in the PDF conversion). This is two conversions agreeing, not the printed PDF; the journal version (J. Syst. Softw. 170, 2020) may differ.

**All runs (final size; "cap" = stopped by the 7,200 s wall-clock cap while still shrinking, so the size is where it was, not where it fails):**

| model | published heuristic, 10 runs (min to max) | this search, seed: size | notes |
|---|---|---|---|
| spins | 49 to 53 | 0:43, 1:42, 2:43 | start 44 |
| bugzilla | 41 to 48 | 0:37, 1:36, 2:36, 3:37 | seed 0 start 60, seeds 1 to 3 start 45; size 35 not recorded for seeds 1 to 3, size 36 failed for seed 0 with 5 avoidable collisions |
| spinv | 91 to 97 | 0:79, 1:79, 2:78 | seeds 0, 1 start 90; seed 2 start 85; the next size failed with 1, 1 and 3 avoidable collisions |
| apache | 85 to 89 | 0:82 (cap), 1:82 (cap) | start 100 and 90; size 81 (seed 1) in progress at the cap with 11 avoidable left |
| gcc | 61 to 68 | 0:63 (cap), 1:61 (cap) | start 75 and 70; ends at the cap, sizes 62 and 60 not completed (12 and 9 avoidable left) |

Median over seeds of the final sizes: spins 43, bugzilla 36.5, spinv 79, apache 82, gcc 62. The inseparable-pair counts left by the verifier equal the paper's column: spins 9, spinv 599, bugzilla 0, apache 0, gcc 46.

**Time-capped runs (same search, wall-clock cap on the whole run, model build excluded, seeds 0 to 2, start 60 for bugzilla and 53 for spins):**

| model | cap | sizes reached | published heuristic (size, time) |
|---|---|---|---|
| bugzilla | 60 s | 48, 48, 47 | 41 to 48, about 9 s |
| bugzilla | 600 s | 39, 39, 40 | same |
| spins | 10 s | 52, 53, 52 | 49 to 53, about 0.6 s |

**Time to reach sizes (from the logs of the uncapped runs, seed 0):** bugzilla 48 at 49 s, 41 at 302 s, 37 at 1,685 s.

**What the numbers show:** at wall-clock budgets about 7 to 17 times their reported times (bugzilla 60 s, spins 10 s) this search lands inside the published range, not below it. Below the published minimum appears only with budgets of about 10 to 1,000 times theirs, on spins, bugzilla, spinv and apache; on gcc the best size (61, seed 1) only equals the published minimum (61), and both gcc runs were cut off by the cap. **What they do not show:** equal-hardware timing (their machine, language and generator differ from this container, and CPU shares here varied); that the search would beat their method given their own time; anything about the CitLab and literature benchmarks 1 to 25 (not run) or other strengths. Seeds: 2 to 4 per model, so spread is only indicated.

## Needs your decision (added by item 45)
- Item 46 (STOP FOR USER): to compare at equal time and hardware we would have to run the authors' own tool (the CLA generator, or SA4LA for unconstrained arrays) in this container. That means downloading and executing third-party code; I did not do it. Also the CitLab/literature benchmarks 1 to 25 need their source files.
- Paper framing: the defensible statement from the data is "at 10 to 1,000 times the published run time, a solver-backed SA reaches smaller (1bar,2)-CLAs on five CCAG benchmarks (verified), and at about 10 times their time it matches their range". A speed or quality win is NOT shown.

## Needs your decision (added by item 46)
- Item 46 (STOP FOR USER): a time-matched comparison on the same machine needs the authors' CLA tool or SA4LA (external download and run), and the 25 CitLab/literature benchmarks need a source for the files. Both are decisions about third-party code and data.

## Item 46 resolved in the live session: PDF check, time ratios, tool and benchmark sources (research plan items 46 and 47)
Live session (sandbox), 2026-10-27. Docs only; no code changed, no search run.

**Table 1 checked against the arXiv PDF** (https://arxiv.org/pdf/1801.06041, 29 pages, read by a PDF parser with a direct-quote query; rows 8, 9 and 21 to 24 were not returned). Heuristic (1bar,2)-CLA sizes max / min and average time over 10 runs:

| No. | SUT | max | min | avg time (s) |
|---|---|---|---|---|
| 26 | Apache | 89 | 85 | 3,263.15 |
| 27 | Bugzilla | 48 | 41 | 9.02 |
| 28 | GCC | 68 | 61 | 2,494.59 |
| 29 | Spins | 53 | 49 | 0.63 |
| 30 | Spinv | 97 | 91 | 58.21 |

Sizes agree with the two conversions used in items 44 and 45. Valid-pair and indistinguishable-pair columns also agree (Apache 66,927 / 0, Bugzilla 5,818 / 0, GCC 82,770 / 46, Spins 979 / 9, Spinv 8,741 / 599). Still not checked: the journal version (J. Syst. Softw. 170, 2020).

**Correction to the item 45 framing.** Our run time divided by their average time (our times from items 44 and 45; different hardware and language, so this is a ratio of wall-clock numbers, not of compute):

| model | ratio(s) |
|---|---|
| spins | 421, 714, 516 (seeds 0 to 2) |
| bugzilla | 331 (seed 0) |
| spinv | 101, 83 (seeds 0, 1) |
| apache | 2.2 (7,200 s cap) |
| gcc | 2.9 (7,200 s cap) |

So "10 to 1,000 times the published run time" is wrong for apache: both apache seeds ended at 82 (below the published minimum of 85) within about 2.2 times the published average time. For gcc, 61 (equal to the published minimum) within about 2.9 times. Two seeds each, capped runs, different hardware; this is not a time-matched comparison.

**Tools.** SA4LA (github.com/tatsuhirotsuchiya/SA4LA, Konishi et al., Java) was cloned outside the repo. Its input format is strength, number of parameters and value counts only, and no source file mentions constraints, so it builds unconstrained locating arrays only. It cannot give a like-for-like constrained comparison; it can give a same-machine comparison of the two searches on the CCAG models with constraints removed. Building and running it was blocked by the session's permission check (third-party code); not run. The Jin & Tsuchiya heuristic implementation (C++, CIT-BACH based) was not found in a public repository by web and developer-index searches.

**Literature benchmarks 1 to 25.** 20 of them (Banking1/2, CommProtocol, Concurrency, Healthcare1 to 4, Insurance, NetworkMgmt, ProcessorComm1/2, Services, Storage1 to 5, SystemMgmt, Telecom; Segall et al.) are in the Jia, Cohen, Harman and Petke benchmark archive on Zenodo (DOI 10.5281/zenodo.581657, ICSE15_HHSA_Benchmarks.zip, .model and .constraints files). Download was refused by the container's network policy (zenodo.org not allowed). No source found yet for Aircraft, Car, Movie, Medicitries and Medicitries_small.

## Needs your decision (added by item 47)
- SA4LA run (item 52): needs a permission rule that allows building and running third-party Java code in the session, or a run on your machine.
- Literature benchmarks (item 53): add zenodo.org to the environment's allowed domains, or download the archive yourself and put it outside the repo.

## Multiple faults: how far are d = 1 suites from the (bar2,2) condition? (research plan item 48)
Cloud run, not reproduced by the author. `scripts/item48_sets.py` (new; no library change; z3-solver 5.3.2.0 installed in this session via `python3 -m pip`). Interaction localization only. t = 2, one seed (0).
Suites: the item 25 locating search re-run (Z3-backed cold shrinking, targeted, 3 restarts x 3000 moves, start = greedy locating size, seed 0); the sizes equal item 25's seed-0 locating column (9, 10, 9 for high_constraints, 8, 11, 8), so the same suites were found again. Sets = every single feasible interaction plus every pair of distinct feasible interactions; a set's signature is the tests (or valid configurations) that contain at least one interaction of the set. Counts are by brute force over bit masks. "Unavoidable" = equal signature over all valid configurations (enumerated); avoidable = colliding minus unavoidable. Command: `PYTHONPATH=. python3 scripts/item48_sets.py`.

| model | valid configs | suite size | interactions | sets (size 1 or 2) | set pairs | colliding pairs | unavoidable | avoidable |
|---|---|---|---|---|---|---|---|---|
| model.json | 18 | 9 | 38 | 741 | 274,170 | 1,013 | 406 | 607 |
| model_6param.json | 36 | 10 | 58 | 1,711 | 1,462,905 | 4,912 | 648 | 4,264 |
| model_8param.json | 144 | - | 110 | 6,105 | 18,632,460 | skipped (over 5,000,000 set pairs) | | |
| model_high_constraints.json | 11 | 9 | 35 | 630 | 198,135 | 1,753 | 1,297 | 456 |
| model_low_constraints.json | 32 | 8 | 40 | 820 | 335,790 | 2,280 | 60 | 2,220 |
| model_multivalue.json | 30 | 11 | 46 | 1,081 | 583,740 | 1,393 | 261 | 1,132 |
| my_model.json | 24 | 8 | 39 | 780 | 303,810 | 1,998 | 198 | 1,800 |

Sanity check built into the script: among pairs of single interactions, none were colliding-but-avoidable on any of the six models (all 0), as expected for suites with cost 0.
What this shows: on these six small models, the d = 1 suites leave every set pair of size 1 or 2 mostly unseparated in the avoidable sense (456 to 4,264 avoidable colliding pairs per model), so a d = 1 suite is not a d = 2 suite; the count says how far, nothing about how many extra tests a d = 2 suite needs. What it does not show: sizes of d = 2 suites (no search run), results on model_8param (skipped by the rule), larger models, or any seed other than 0.
Test status before commit: 149 tests OK, 3 skipped (z3 installed; before installing, 40 skipped).

## Flaky failures: how often does exact localization survive? (research plan item 49)
Cloud run, not reproduced by the author. `scripts/item49_flaky.py` (new; library unchanged; `rank_noisy` not used, so I did not need to read it for this item). Interaction localization only. t = 2, one seed (0) for the suite search and for the random failures (`random.Random(0)`, one stream per model).
Suites: the item 25 locating search re-run per model (Z3-backed cold shrinking, targeted, 3 restarts x 3000 moves, start = greedy locating size, seed 0). All 7 non-slow models, including model_8param.json (item 48 skipped it for set-pair count; this item does not need pairs). Fault model: every feasible interaction is the single fault, 20 trials each; a test that contains it fails with probability p in each of r repeats, and is reported failing if it failed in any repeat; tests without it never fail. `localize_exact` is run on the reported outcomes. exact = it returned exactly the true interaction; empty = empty list; wrong = non-empty but not exactly the true one (includes ambiguous lists). Command: `PYTHONPATH=. python3 scripts/item49_flaky.py`.

| model | suite size | interactions | p | r | exact | empty | wrong |
|---|---|---|---|---|---|---|---|
| model.json | 9 | 38 | 1.0 | 1 | 1.0000 | 0.0000 | 0.0000 |
| model.json | 9 | 38 | 1.0 | 2 | 1.0000 | 0.0000 | 0.0000 |
| model.json | 9 | 38 | 1.0 | 3 | 1.0000 | 0.0000 | 0.0000 |
| model.json | 9 | 38 | 0.9 | 1 | 0.7934 | 0.1079 | 0.0987 |
| model.json | 9 | 38 | 0.9 | 2 | 0.9868 | 0.0039 | 0.0092 |
| model.json | 9 | 38 | 0.9 | 3 | 0.9947 | 0.0000 | 0.0053 |
| model.json | 9 | 38 | 0.7 | 1 | 0.4526 | 0.2711 | 0.2763 |
| model.json | 9 | 38 | 0.7 | 2 | 0.8053 | 0.1184 | 0.0763 |
| model.json | 9 | 38 | 0.7 | 3 | 0.9289 | 0.0421 | 0.0289 |
| model.json | 9 | 38 | 0.5 | 1 | 0.2013 | 0.4447 | 0.3539 |
| model.json | 9 | 38 | 0.5 | 2 | 0.5395 | 0.2289 | 0.2316 |
| model.json | 9 | 38 | 0.5 | 3 | 0.7395 | 0.1395 | 0.1211 |
| model_6param.json | 10 | 58 | 1.0 | 1 | 1.0000 | 0.0000 | 0.0000 |
| model_6param.json | 10 | 58 | 1.0 | 2 | 1.0000 | 0.0000 | 0.0000 |
| model_6param.json | 10 | 58 | 1.0 | 3 | 1.0000 | 0.0000 | 0.0000 |
| model_6param.json | 10 | 58 | 0.9 | 1 | 0.7991 | 0.0991 | 0.1017 |
| model_6param.json | 10 | 58 | 0.9 | 2 | 0.9647 | 0.0181 | 0.0172 |
| model_6param.json | 10 | 58 | 0.9 | 3 | 0.9983 | 0.0000 | 0.0017 |
| model_6param.json | 10 | 58 | 0.7 | 1 | 0.4190 | 0.3388 | 0.2422 |
| model_6param.json | 10 | 58 | 0.7 | 2 | 0.7828 | 0.1043 | 0.1129 |
| model_6param.json | 10 | 58 | 0.7 | 3 | 0.9276 | 0.0241 | 0.0483 |
| model_6param.json | 10 | 58 | 0.5 | 1 | 0.1836 | 0.5069 | 0.3095 |
| model_6param.json | 10 | 58 | 0.5 | 2 | 0.5034 | 0.2664 | 0.2302 |
| model_6param.json | 10 | 58 | 0.5 | 3 | 0.7276 | 0.1345 | 0.1379 |
| model_8param.json | 11 | 110 | 1.0 | 1 | 1.0000 | 0.0000 | 0.0000 |
| model_8param.json | 11 | 110 | 1.0 | 2 | 1.0000 | 0.0000 | 0.0000 |
| model_8param.json | 11 | 110 | 1.0 | 3 | 1.0000 | 0.0000 | 0.0000 |
| model_8param.json | 11 | 110 | 0.9 | 1 | 0.7495 | 0.1173 | 0.1332 |
| model_8param.json | 11 | 110 | 0.9 | 2 | 0.9732 | 0.0086 | 0.0182 |
| model_8param.json | 11 | 110 | 0.9 | 3 | 0.9968 | 0.0018 | 0.0014 |
| model_8param.json | 11 | 110 | 0.7 | 1 | 0.3959 | 0.2700 | 0.3341 |
| model_8param.json | 11 | 110 | 0.7 | 2 | 0.7655 | 0.1068 | 0.1277 |
| model_8param.json | 11 | 110 | 0.7 | 3 | 0.9282 | 0.0364 | 0.0355 |
| model_8param.json | 11 | 110 | 0.5 | 1 | 0.1736 | 0.3918 | 0.4345 |
| model_8param.json | 11 | 110 | 0.5 | 2 | 0.4586 | 0.2205 | 0.3209 |
| model_8param.json | 11 | 110 | 0.5 | 3 | 0.6882 | 0.1468 | 0.1650 |
| model_high_constraints.json | 9 | 35 | 1.0 | 1 | 0.8000 | 0.0000 | 0.2000 |
| model_high_constraints.json | 9 | 35 | 1.0 | 2 | 0.8000 | 0.0000 | 0.2000 |
| model_high_constraints.json | 9 | 35 | 1.0 | 3 | 0.8000 | 0.0000 | 0.2000 |
| model_high_constraints.json | 9 | 35 | 0.9 | 1 | 0.6186 | 0.1271 | 0.2543 |
| model_high_constraints.json | 9 | 35 | 0.9 | 2 | 0.7900 | 0.0086 | 0.2014 |
| model_high_constraints.json | 9 | 35 | 0.9 | 3 | 0.7957 | 0.0014 | 0.2029 |
| model_high_constraints.json | 9 | 35 | 0.7 | 1 | 0.3457 | 0.3200 | 0.3343 |
| model_high_constraints.json | 9 | 35 | 0.7 | 2 | 0.6271 | 0.1086 | 0.2643 |
| model_high_constraints.json | 9 | 35 | 0.7 | 3 | 0.7314 | 0.0343 | 0.2343 |
| model_high_constraints.json | 9 | 35 | 0.5 | 1 | 0.1429 | 0.5214 | 0.3357 |
| model_high_constraints.json | 9 | 35 | 0.5 | 2 | 0.4057 | 0.2471 | 0.3471 |
| model_high_constraints.json | 9 | 35 | 0.5 | 3 | 0.5829 | 0.1429 | 0.2743 |
| model_low_constraints.json | 8 | 40 | 1.0 | 1 | 1.0000 | 0.0000 | 0.0000 |
| model_low_constraints.json | 8 | 40 | 1.0 | 2 | 1.0000 | 0.0000 | 0.0000 |
| model_low_constraints.json | 8 | 40 | 1.0 | 3 | 1.0000 | 0.0000 | 0.0000 |
| model_low_constraints.json | 8 | 40 | 0.9 | 1 | 0.8125 | 0.0250 | 0.1625 |
| model_low_constraints.json | 8 | 40 | 0.9 | 2 | 0.9838 | 0.0025 | 0.0138 |
| model_low_constraints.json | 8 | 40 | 0.9 | 3 | 0.9988 | 0.0000 | 0.0013 |
| model_low_constraints.json | 8 | 40 | 0.7 | 1 | 0.5200 | 0.1325 | 0.3475 |
| model_low_constraints.json | 8 | 40 | 0.7 | 2 | 0.8263 | 0.0213 | 0.1525 |
| model_low_constraints.json | 8 | 40 | 0.7 | 3 | 0.9487 | 0.0050 | 0.0462 |
| model_low_constraints.json | 8 | 40 | 0.5 | 1 | 0.2737 | 0.2737 | 0.4525 |
| model_low_constraints.json | 8 | 40 | 0.5 | 2 | 0.5262 | 0.0963 | 0.3775 |
| model_low_constraints.json | 8 | 40 | 0.5 | 3 | 0.7762 | 0.0300 | 0.1938 |
| model_multivalue.json | 11 | 46 | 1.0 | 1 | 1.0000 | 0.0000 | 0.0000 |
| model_multivalue.json | 11 | 46 | 1.0 | 2 | 1.0000 | 0.0000 | 0.0000 |
| model_multivalue.json | 11 | 46 | 1.0 | 3 | 1.0000 | 0.0000 | 0.0000 |
| model_multivalue.json | 11 | 46 | 0.9 | 1 | 0.8011 | 0.1043 | 0.0946 |
| model_multivalue.json | 11 | 46 | 0.9 | 2 | 0.9848 | 0.0076 | 0.0076 |
| model_multivalue.json | 11 | 46 | 0.9 | 3 | 1.0000 | 0.0000 | 0.0000 |
| model_multivalue.json | 11 | 46 | 0.7 | 1 | 0.4380 | 0.2804 | 0.2815 |
| model_multivalue.json | 11 | 46 | 0.7 | 2 | 0.7902 | 0.1185 | 0.0913 |
| model_multivalue.json | 11 | 46 | 0.7 | 3 | 0.9543 | 0.0250 | 0.0207 |
| model_multivalue.json | 11 | 46 | 0.5 | 1 | 0.2326 | 0.4315 | 0.3359 |
| model_multivalue.json | 11 | 46 | 0.5 | 2 | 0.5522 | 0.2359 | 0.2120 |
| model_multivalue.json | 11 | 46 | 0.5 | 3 | 0.7250 | 0.1424 | 0.1326 |
| my_model.json | 8 | 39 | 1.0 | 1 | 1.0000 | 0.0000 | 0.0000 |
| my_model.json | 8 | 39 | 1.0 | 2 | 1.0000 | 0.0000 | 0.0000 |
| my_model.json | 8 | 39 | 1.0 | 3 | 1.0000 | 0.0000 | 0.0000 |
| my_model.json | 8 | 39 | 0.9 | 1 | 0.8077 | 0.0628 | 0.1295 |
| my_model.json | 8 | 39 | 0.9 | 2 | 0.9833 | 0.0064 | 0.0103 |
| my_model.json | 8 | 39 | 0.9 | 3 | 0.9987 | 0.0000 | 0.0013 |
| my_model.json | 8 | 39 | 0.7 | 1 | 0.4974 | 0.1821 | 0.3205 |
| my_model.json | 8 | 39 | 0.7 | 2 | 0.8231 | 0.0577 | 0.1192 |
| my_model.json | 8 | 39 | 0.7 | 3 | 0.9474 | 0.0154 | 0.0372 |
| my_model.json | 8 | 39 | 0.5 | 1 | 0.2615 | 0.3744 | 0.3641 |
| my_model.json | 8 | 39 | 0.5 | 2 | 0.5244 | 0.1462 | 0.3295 |
| my_model.json | 8 | 39 | 0.5 | 3 | 0.7667 | 0.0731 | 0.1603 |

What this shows: at p = 1.0 every model gives exact = 1.0000 except model_high_constraints.json at 0.8000 (wrong 0.2000, all r). I checked separately that 7 of its 35 feasible interactions share their signature over all 11 valid configurations with another interaction, i.e. 7/35 = 0.2, so that 0.2 is the unavoidable ambiguity, not noise. For p < 1, exact localization drops sharply at r = 1 (for p = 0.9 between 0.6186 and 0.8125 across models; for p = 0.5 between 0.1429 and 0.2737) and recovers with repeats (p = 0.9, r = 3: 0.7957 on high_constraints and 0.9947 to 1.0000 on the others; p = 0.5, r = 3: 0.5829 to 0.7762). Failures show up as both empty results (all failing tests missed) and wrong results (a subset of the failing tests looks like another interaction's pattern). What it does not show: any other seed, strength t = 3, larger models, suites built to tolerate flakiness, or how a ranking method (`rank_noisy`) would do; none were run.
Test status before commit: 149 tests OK, 3 skipped (z3 installed).

## Summary of research plan items 47 to 50 (research plan item 51)
Cloud run, not reproduced by the author. Interaction localization only; one seed (0) for items 48 and 49. In this session I re-ran `scripts/item48_sets.py` and `scripts/item49_flaky.py` (z3-solver 5.3.2.0 installed via pip) instead of copying numbers. Item 48: all six table rows (sets, set pairs, colliding, unavoidable, avoidable) are identical to the item 48 section, and model_8param.json is skipped again (18,632,460 set pairs, over the 5,000,000 rule). Item 49: all 84 rows (7 models x 4 values of p x 3 values of r; exact, empty, wrong) are identical to the item 49 table. Items 47 and 50 involved no code; their results (PDF table check, time ratios, tool and benchmark sources, literature search) are in the item 46/47 section above and in docs/LITERATURE_CHECK.md, and were not re-measured here (web and PDF access, not repeated).

| item | what was measured | result (see section) |
|---|---|---|
| 47 | Table 1 vs PDF; time ratios | sizes agree; apache ratio about 2.2, so the "10 to 1,000 times" framing was wrong for apache (item 46/47 section; not re-run) |
| 48 | colliding pairs of fault sets of size 1 or 2 in d = 1 suites | 1,013 to 4,912 colliding pairs on six models, of which 456 to 4,264 avoidable (re-run) |
| 49 | exact localization under flaky failures | p = 1.0: exact 1.0000 on six models, 0.8000 on model_high_constraints.json (unavoidable ambiguity); p = 0.9, r = 1: 0.6186 to 0.8125; p = 0.5, r = 3: 0.5829 to 0.7762 (re-run) |
| 50 | ML/LLM literature | five sources opened; none builds locating arrays or localizes interactions with a learned model, "did not find" from three queries (not re-run) |

Test status before commit: 149 tests OK, 3 skipped (z3 installed).

What this shows: a suite built for single faults leaves many two-interaction fault sets confusable, and the exact localizer needs repeats to cope with flaky failures. What it does not show: sizes of d = 2 suites, other seeds, t = 3, larger models, `rank_noisy`, or any comparison with published sizes beyond what items 44 to 47 recorded.

## Needs your decision (added by item 51)
- Items 52 and 53 stay STOP FOR USER (see the entries added by item 47).

## Literature benchmarks: comparison with Jin & Tsuchiya Table 1 rows 6 to 25 (research plan item 53)
Live session (sandbox), 2026-10-27. Interaction localization only; t = 2, d = 1; seeds 0 to 2 (three data points per model).

**Source and conversion.** Jia, Cohen, Harman and Petke, CIT Benchmarks, Zenodo DOI 10.5281/zenodo.581657, `ICSE15_HHSA_Benchmarks.zip`, folder `segall_issta_11` (20 Segall et al. models; kept outside the repo, not committed). Its `X_yue.cons` files number (parameter, value) pairs from 1 (in every file the largest index equals the number of values and index 0 never occurs), so `scripts/item53_convert.py` shifts every index down by one into the format `load_casa_model` reads; a model with no .cons file gets an empty constraints file (Insurance, Storage2).

**Model check against Table 1.** Feasible 2-way interaction count (FastZ3CostModel, cover mode) equals Table 1's |VI_2| on 18 of 20 models. Two differ and are excluded: ProcessorComm2 (3,081 here, 2,525 in the table) and Storage4 (3,414 here, 3,491). As an independent check, the verifier's inseparable-pair count equals Table 1's * column on all 18 (for example Healthcare3 477, SystemMgmt 130, Services 93). Table 1 rows 1 to 5 (Aircraft, Car, Movie, Medicitries, Medicitries_small) are not in the archive; no source found. Rows 8, 9 and 21 to 24 were read from the arXiv PDF by a freeform (not direct-quote) query; check them against the PDF before quoting.

**Settings.** `scripts/item44_run.py` unchanged: Z3-backed targeted SA, 6000 moves x 5 restarts per size, shrink by one, start = the published maximum size, **wall-clock cap 900 s per run** (item 44 used 7,200 s; reduced to bound the session). Four runs at a time on a 4-core container. Every saved suite (`docs/item53_suites/`, 54 files) passed `scripts/item44_verify.py`: valid tests, 0 uncovered, 0 avoidable collisions.

| No. | model | published min to max | SMT (exact search) | this search, seeds 0/1/2 | median | median vs published min | our time (s), median | published avg time (s) | time ratio |
|---|---|---|---|---|---|---|---|---|---|
| 6 | Banking1 | 25 to 28 | 23 | 22/22/22 | 22 | -3 | 71.9 | 0.14 | 514 |
| 7 | Banking2 | 27 to 30 | T.O. | 23/23/23 | 23 | -4 | 179.5 | 0.17 | 1,056 |
| 8 | Concurrency | 7 to 7 | 7 | 7/7/7 | 7 | +0 | 41.9 | 0.1 | 419 |
| 9 | CommProtocol | 33 to 35 | T.O. | 29/30/29 | 29 | -4 | 331.3 | 0.18 | 1,841 |
| 10 | Healthcare1 | 45 to 50 | 42 | 41/40/41 | 41 | -4 | 226 | 0.2 | 1,130 |
| 11 | Healthcare2 | 33 to 36 | T.O. | 29/30/29 | 29 | -4 | 192.1 | 0.2 | 960 |
| 12 | Healthcare3 | 77 to 101 | T.O. | 69c/68c/70c | 69 | -8 | 900 (cap) | 4.38 | 205 |
| 13 | Healthcare4 | 98 to 105 | T.O. | 94c/94c/94c | 94 | -4 | 900 (cap) | 20.85 | 43 |
| 14 | Insurance | 789 to 805 | T.O. | 789c/789c/790c | 789 | +0 | 900 (cap) | 84.34 | 11 |
| 15 | NetworkMgmt | 202 to 210 | T.O. | 179/181/179c | 179 | -23 | 830.2 (cap) | 1.86 | 446 |
| 16 | ProcessorComm1 | 58 to 63 | T.O. | 50/51/52 | 51 | -7 | 496.8 | 0.59 | 842 |
| 18 | Services | 194 to 200 | T.O. | 174c/174c/175c | 174 | -20 | 900 (cap) | 4.62 | 195 |
| 19 | Storage1 | 22 to 22 | 22 | 22/22/22 | 22 | +0 | 37.2 | 0.11 | 338 |
| 20 | Storage2 | 34 to 37 | 30 | 30/30/30 | 30 | -4 | 78 | 0.12 | 650 |
| 21 | Storage3 | 87 to 89 | T.O. | 74/76/75 | 75 | -12 | 751.4 | 0.77 | 976 |
| 23 | Storage5 | 344 to 361 | T.O. | 350c/350c/350c | 350 | +6 | 900 (cap) | 56.18 | 16 |
| 24 | SystemMgmt | 27 to 31 | T.O. | 25/25/25 | 25 | -2 | 172.1 | 0.16 | 1,076 |
| 25 | Telecom | 49 to 54 | T.O. | 44/44/45 | 44 | -5 | 219.4 | 0.22 | 997 |

median below published min: 14, equal: 3, above: 1

"c" = stopped by the 900 s cap while still shrinking (the size is where it was, not where it fails). Time ratio = our median run time / their average time; different hardware and language, so this compares wall-clock numbers, not compute. SMT column is the size their SMT method reached (it starts from the heuristic's minimum), not a proven minimum.

**What the numbers show.** Median size below the published heuristic minimum on 14 of 18 models, equal on 3 (Concurrency, Storage1, Insurance), above on 1 (Storage5, capped at 350 against 344). Where their SMT method finished, our sizes were equal (Concurrency 7, Storage1 22, Storage2 30) or smaller (Banking1 22 against 23, Healthcare1 40 to 41 against 42). Our runs used about 11 to 1,841 times their average time; on the two models nearest to equal time (Insurance about 11 times, Storage5 about 16 times) the search did not go below their minimum.

**What they do not show.** That this search beats their heuristic at equal time or hardware; minimum sizes (search results at a fixed budget); anything for Table 1 rows 1 to 5, ProcessorComm2 or Storage4. Three seeds per model.

## Same-machine, equal-time comparison with SA4LA, constraints removed (research plan item 52)
Live session (sandbox), 2026-10-27, after the plan author committed `.claude/settings.json` allowing javac/java. Interaction localization only; t = 2, d = 1; seeds 0 to 2.

**What was run.** SA4LA (github.com/tatsuhirotsuchiya/SA4LA, commit 07fdcb0, Konishi et al.) built from source outside the repo (never committed). Its sources mix UTF-8-with-BOM and Shift-JIS (one file, comments only), so a copy was re-encoded to plain UTF-8 before `javac`; no code was changed. The source was checked for network, process and file-write calls (none besides its optional output file). Default settings (temperature 4.0, cooling 0.999, 4,096 iterations, 3 retries), seeds 0 to 2, 3,600 s cap. SA4LA cannot express constraints, so all four CCAG models (spins, bugzilla, spinv, apache) were run with their constraints **removed** (the .model file is SA4LA's input format; spins matched SA4LA's own `spin-s-2` input exactly). Then `scripts/item44_run.py` (Z3-backed targeted SA, unchanged) on the same unconstrained models, same seeds, **wall-clock cap = SA4LA's own run time for that model and seed** (3,600 s for apache), start size = the upper bound SA4LA printed for that model. Both phases ran 4 processes at a time on the same 4-core container. Our model build (0.2 s spins to 8.8 s apache) is outside our cap. `scripts/item52_parse.py` turns SA4LA's printed array into suite JSON; every array below passed `scripts/item44_verify.py` (valid, 0 uncovered, 0 avoidable collisions). Suites in `docs/item52_suites/`.

| model (unconstrained) | SA4LA size, seeds 0/1/2 | SA4LA time (s) | this search, same cap | this search start |
|---|---|---|---|---|
| spins | 35 / 35 / 35 | 31.9 / 30.2 / 40.5 | 45 / 44 / 43 (capped) | 62 |
| bugzilla | 32 / 32 / 32 | 191.2 / 158.2 / 197.4 | 43 / 44 / 43 (capped) | 73 |
| spinv | 51 / 51 / 52 | 408.3 / 421.3 / 380.2 | 66 / 68 / 67 (capped) | 74 |
| apache | cut off at 3,600 s; log shows 63 / 63 / 64 rows reached (not printed, not verified) | 3,600 (cap) | 89 / 90 / 90 (capped) | 147 |

**What the numbers show.** At equal wall-clock time on the same machine, SA4LA's arrays are smaller on every model and seed: by 8 to 10 rows on spins, 11 to 12 on bugzilla, 14 to 17 on spinv, and (unverified for SA4LA) about 26 on apache. Every one of our runs was still shrinking when it hit the cap. A single seed-0 spins run of SA4LA alone took 24.8 s (35 rows), so the parallel load slowed SA4LA too.

**What they do not show.** Anything about constrained models (SA4LA cannot run them); minimum sizes; behaviour at our item 44 budgets. Likely contributors, not tested: SA4LA binary-searches the size between bounds while this search shrinks by one test from the start; Java versus Python; SA4LA's incremental cost evaluation. Implication for the paper: the size results of items 44, 45 and 53 rest on much larger time budgets, and at equal time this search's engine is clearly slower than SA4LA's on unconstrained arrays. Any claim must be about constrained arrays and must state the time budgets.

## Needs your decision (added by the scheduled research run, 2026-10-27)
- Every item in docs/RESEARCH_PLAN.md (1 to 53) is ticked. The scheduled run has nothing left to do until you add new items; the open choices are the ones listed in the earlier "Needs your decision" entries (published-size framing, more seeds, d = 2, AI-based work).
