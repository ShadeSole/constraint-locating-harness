# Simulated Annealing for Constrained Locating Arrays: Cost Relative to Covering, and One versus Two Faults

*Working title. Full first draft, written 2026-11-05 in a live cloud session for the author to rewrite.*

> **Status of this draft (read first).**
> - Every number comes from `docs/PAPER_RESULTS.md` or a named `docs/PROJECT_NOTES.md` section. None was re-measured
>   for this draft. Every number is a sandbox (cloud) result.
> - **Reproduced locally** (author's machine, 2026-11-08, Windows 11, Python 3.13.1; PROJECT_NOTES item 80): the
>   small-model exact minima and t = 3 searches (RQ1 small models, RQ4), and all of RQ5 except the suite searches.
>   Every row matched. Also re-run there (item 83): the RQ5 simulations (identical), RQ1 on spins and bugzilla (3 of 4
>   equal; spins locating 39 against 38), and RQ3 apache and gcc (73 and 60 against 67 to 69 and 54 to 55: still
>   below the published minima). **Not yet reproduced locally:** RQ2, and RQ3's literature benchmarks and Insurance.
> - Before submission:
>   - Re-run the headline rows locally (`scripts/reproduce.py quick`).
>   - Check every Jin & Tsuchiya Table 1 figure against the journal PDF.
>   - Resolve the remaining **[verify]** marker (origin of the 18 literature models).
> - Citations are limited to sources listed in `docs/LITERATURE_CHECK.md`. Their bibliographic details were confirmed
>   against Crossref and arXiv on 2026-11-05. One [verify] remains: which Segall et al. paper the Zenodo archive cites for the 18
>   literature models.
> - Wording rule: no "first", "novel" or "no prior work". Where a search found nothing, the text says "we did not find".

## Abstract

A locating array is a test suite that both covers every t-way interaction and identifies which interaction caused a
failure. Real systems forbid some parameter combinations. Constrained locating arrays (CLAs; Jin & Tsuchiya 2020)
handle this by exempting interactions that no valid test can tell apart. Simulated annealing (SA) is known to build
small unconstrained locating arrays (Konishi et al. 2020). We study SA for constrained locating arrays, keeping every
test valid with a rule check and an SMT fallback. We ask four questions.

**How much does localization cost over coverage?** On five constrained benchmarks at strength 2, a locating array
needed about 1.6 to 2.1 times as many tests as a covering array built by the same search under the same budget. On
small models where exact minima are known, the ratio at the minimum was 1.33 to 1.80 at strength 2.

**Does the move design matter?** On unconstrained versions of three benchmarks, we raced against SA4LA on the same
machine at equal time. A move that redraws a whole test lost by 8 to 17 tests. A "local" move that edits only the
values of the target interaction matched SA4LA, at most one test worse.

**How does it compare with the published CLA heuristic?** With the local move, apache and gcc reached 67 to 69 and 54
to 55 tests within the published heuristic's average time, below its minima of 85 and 61 (10 seeds). On a second
machine, seed 0 reached 73 and 60: still below, but by much less on gcc. Results at a time cap depend on the machine,
and the hardware differs from the published runs, so this is not a same-machine comparison. On 18 literature benchmarks, at ten times the larger of 5 s and the
heuristic's time, the median over 3 seeds was below the published minimum on 12.

**What does locating two faults cost?** On seven small models with exact minima, locating up to two faults at strength
2 needs roughly twice the tests of locating one. On all seven it needs exactly as many as locating one fault at
strength 3. We show by verified counterexamples that a (1bar, 3)-locating array need not be (2bar, 2)-locating, so that
equality is not a general rule.

**Does localization work when faults break the assumptions?**
- **Simulated violations, 8 models.** A one-fault array met a single faulty 3-way interaction and gave a wrong diagnosis in
  7 to 85% of cases. A two-fault array never did; it flags such failures instead. This follows from a
  known property (Colbourn & McClary's Lemma 7.1), applied to constrained arrays.
- **Real code, two programs.** On two Python standard-library modules with 131 and 258 mutation-injected faults:
  - Single-pair faults, the case the standard construction targets, were 0 of 83 and 1 of 110 configuration-dependent
    faults.
  - The standard one-fault array correctly diagnosed 0 and 1 faults.
  - The two-fault array, at 2.6 to 2.8 times the size, correctly diagnosed 11 and 48: every fault that fit its model.
    It named a wrong cause in 3 and 0 cases.
  - **Equal-budget controls.** We compared 200 random suites of the same size, with the same two-pair decoder.
    - They averaged 10.2 and 43.2 correct diagnoses, against 11 and 48 for each of three two-fault suites.
    - They are not significantly worse on average (empirical p >= 0.16), but 50% and 84% of them fell short of the
      two-fault suites, and about one in six misled on many faults.
    - So most of the gain comes from test budget and decoder; the construction makes the best case dependable.

## 1. Introduction

Combinatorial interaction testing chooses a small set of test configurations so that every combination of t parameter
values appears in some test. A failing test then shows that some interaction failed, but not which one. Locating arrays
(Colbourn & McClary 2008) strengthen covering arrays: every pair of interactions (or of sets of up to d interactions)
must appear in different sets of tests. The set of failing tests then identifies the faulty interaction.

Real configuration spaces have constraints: some combinations of values are invalid. Constraints can make two
interactions impossible to tell apart: no valid test contains one without the other. Jin & Tsuchiya (2020) define
constrained locating arrays (CLAs), which exempt such indistinguishable pairs. They prove that a CLA always exists and
give a heuristic and an SMT-based construction. Separately, Konishi et al. (2020) built unconstrained locating arrays by
simulated annealing in their tool SA4LA. Their cost counts uncovered interactions and colliding interactions, and an
outer loop searches over sizes. They list the constrained case as future work.

This paper applies simulated annealing to constrained locating arrays. Every test is kept valid under the constraints.
We evaluate it against the published CLA heuristic, against SA4LA on unconstrained versions of the same models, and
against exact minima where these can be computed. We did not find a published metaheuristic for constrained locating
arrays (three literature searches, excerpts only; see Section 7). Metaheuristics with constraint handling exist for
constrained **covering** arrays (Garvin, Cohen & Dwyer 2009, 2011). This work combines the two settings,
and we make no claim that it is the first to do so.

**Contributions.**
1. An SA construction for (1bar, t) constrained locating arrays that keeps every test valid. Its "local" move follows
   SA4LA's moves; what we add is that every move stays valid under the constraints, via a rule check with an SMT
   fallback (Section 3).
2. A measurement of the cost of localization over coverage on constrained benchmarks, with the same search and budget
   for both (RQ1). On small models it is anchored by exact minima from MaxSAT.
3. A same-machine, equal-time comparison with SA4LA showing that the move design, not the size schedule, explained an
   initial 8 to 17 test gap (RQ2).
4. Results on the constrained benchmarks used by Jin & Tsuchiya, and on 18 literature models (RQ3).
5. Exact minimum sizes for (2bar, 2) and (2bar, 3) CLAs on small models, using a MaxSAT and SAT formulation with lazily
   added separation constraints. We also give verified counterexamples showing that (1bar, 3)-locating does not imply
   (2bar, 2)-locating (RQ4).
6. A measurement of how locating arrays behave when faults violate their assumptions (RQ5):
   - in simulation, with more faulty pairs than planned, a higher-strength fault, or flaky tests;
   - on two real programs, with automatically generated mutation faults whose exact failing configurations are known.

All suites reported were re-checked by an independent verifier that shares only the model loader with the search.

## 2. Background and definitions

**Model.** A system has k parameters, each with a finite set of values, and a set of forbidden combinations. A
configuration (test) assigns one value to every parameter; it is *valid* if it contains no forbidden combination. A
t-way *interaction* is an assignment of values to t parameters; it is *feasible* if some valid test contains it.

**Covering.** A suite (a list of valid tests) is t-covering if every feasible t-way interaction appears in at least one
test. For an interaction or a set of interactions T, let rho(T) be the set of tests that contain at least one member of
T.

**Locating (constrained).** Following Jin & Tsuchiya (2020), two sets of interactions are *distinguishable* if some
valid test contains an interaction in one set and none in the other. A suite is a (dbar, t)-CLA if it is t-covering,
and if rho(T1) != rho(T2) for every distinguishable pair of sets T1 and T2 of at most d feasible t-way interactions.
Indistinguishable pairs are exempt. With d = 1 this asks that every distinguishable pair of interactions be separated
by some test. We write C(d, t) for the minimum size of a (dbar, t)-CLA of a given model.

**Ceiling.** In earlier versions of this harness, the *ceiling* is the number of interactions distinguishable from
every other interaction. It is the d = 1, t = 2 instance of Jin & Tsuchiya's distinguishability, not a new concept. We
use it only to check that every distinguishable pair has been separated.

**Fault model.** We consider interaction localization only, with deterministic failures: a test fails if and only if it
contains a faulty interaction. Source-code fault localization is out of scope.

## 3. Method

### 3.1 Cost

For a suite S, the cost is

    cost(S) = w * (number of uncovered feasible t-way interactions)
            + (number of avoidable collisions),

where an avoidable collision is a pair of covered interactions with the same test set even though some valid test
would separate them. The weight is w = 1 by default. Pairs that no valid test separates are computed once and excluded
from the cost. A suite with cost 0 is a (1bar, t)-CLA. This is the SA4LA cost, except that indistinguishable pairs are
exempted for the constrained case.

### 3.2 Annealing and the size schedule

For a fixed size n, the search starts from n valid tests and applies one move per step:
- A move that does not raise the cost is always kept.
- A move that raises it by delta is kept with probability exp(-delta / T).
- T falls geometrically from 2.0 to 0.05 over the steps of one run.
- A run stops at cost 0 or when its step budget is spent.

The outer loop solves a start size, then tries one test fewer. Each size gets up to R independent restarts of M moves
each. The search stops at the first size where every restart fails, or when a wall-clock cap is reached. A failed size
is a budget statement, not a proof of impossibility. For the benchmarks we used M = 6,000 and R = 5. The start size was
the published heuristic's maximum or SA4LA's size, as stated per experiment.

### 3.3 Keeping every test valid

On small models the search draws only from the enumerated valid configurations. On the benchmark models validity is
checked by Z3. Three moves are compared:
- **random**: replace a random test with a Z3-drawn valid configuration.
- **targeted**: if an interaction is uncovered, insert a valid configuration that contains it. Otherwise, pick an
  interaction in an avoidable collision and either replace a test that lacks it with one that contains it, or change
  one value of a test that contains it. New tests come from Z3 draws.
- **local**: the same choices as targeted, but each test is edited in place. To insert an interaction, only its t
  values are overwritten in an existing test, as SA4LA does. The edit is kept if it breaks no forbidden rule (a plain
  rule check); otherwise a Z3 draw containing the interaction is used. To break a collision, one value of the colliding
  interaction itself is changed (the first value that breaks no rule). If none works, a one-value neighbour is tried,
  then a Z3 draw.

Under every move, every test in the suite is valid at every step.

### 3.4 Exact minima and lower bounds (small models)

For small models we enumerate all valid configurations and give each a Boolean variable x_c meaning "chosen".
- **Coverage:** each feasible interaction requires one clause, "some chosen test contains it".
- **Separation:** for a pair of distinguishable sets with test sets A and B, at least one chosen test must lie in the
  symmetric difference of A and B.
- **Lazy separation:** separation clauses are added lazily. Solve, find the pairs the current solution fails to
  separate, add their clauses, and repeat.
- **Two solving routes:**
  - Z3's MaxSAT optimiser minimises the number of chosen tests. Each finished round's optimum is a proven lower bound.
  - A SAT route (CaDiCaL through PySAT, with a sequential-counter cardinality constraint) decides "at most K tests?".
    UNSAT at K proves C(d, t) >= K + 1.
- **Symmetry breaking (unconstrained models only):** fix the first configuration, or fix the minimum-weight non-zero
  configuration. We validated it against minima found without symmetry breaking.
- **Cross-check:** the SAT route agreed with all 19 minima the MaxSAT route had found, giving UNSAT at the minimum
  minus one and SAT at the minimum (PROJECT_NOTES, item 70).

### 3.5 Independent verification

Every suite reported was re-checked by a separate verifier. It shares only the model loader with the search and uses
its own Z3 encoding (benchmarks) or enumeration (small models). It checks three things: every test is valid, every
feasible interaction is covered, and no avoidable collision remains. On the CCAG models, the number of inseparable
pairs it reports equals the corresponding column of Jin & Tsuchiya's Table 1 (9, 0, 599, 0 and 46 for spins, bugzilla,
spinv, apache and gcc).

## 4. Experimental setup

**Models.**
- **Five constrained systems** (apache, bugzilla, gcc, spins, spinv) from the CCAG repository. Their parameter and value
  counts match the systems of Cohen, Dwyer & Shi (2008).
- **18 literature benchmarks** (Segall et al. 2011; the archive attributes them to "Segall et al." [verify that its reference is this paper]), taken from the Jia et al. CIT benchmark archive (Zenodo, DOI
  10.5281/zenodo.581657). 18 of 20 match Jin & Tsuchiya's Table 1 interaction counts. ProcessorComm2 and Storage4
  differ and were excluded.
- **Seven small example models** (11 to 144 valid configurations) bundled with the prototype.
- **`model_spins_core`**: 978 valid configurations, derived from spins.
- **Random models** for RQ4 (Section 5.4).

**Implementation.** Python 3, standard library, with Z3 for validity on the benchmarks. Exact work uses Z3 and PySAT
(CaDiCaL 1.9.5).

**Hardware.** All runs used a 4-core cloud container, at most 4 processes at a time. The published CLA heuristic
figures come from a C++ implementation on a 3.2 GHz Xeon. The two are not comparable machine for machine.

**Seeds and budgets.** Three seeds per configuration unless stated (ten for apache, gcc and Insurance). Budgets are
wall-clock caps, stated per table. Most benchmark runs were stopped by the cap while still shrinking, so their sizes
are upper bounds for that budget.

## 5. Results

### 5.1 RQ1: How many more tests does localization cost than coverage?

Same search (local move), same budget, both modes; seeds 0 to 2. Sources: PROJECT_NOTES items 61 and 62.

| model | t | cap | covering | locating | extra tests | locating / covering |
|---|---|---|---|---|---|---|
| spins | 2 | 600 s | 20 / 21 / 21 | 38 / 39 / 39 | 18 | 1.86 to 1.90 |
| bugzilla | 2 | 600 s | 16 / 16 / 16 | 32 / 32 / 32 | 16 | 2.00 |
| spinv | 2 | 600 s | 51 / 50 / 49 | 82 / 82 / 82 | 31 to 33 | 1.61 to 1.67 |
| apache | 2 | 3,263 s | 36 / 37 / 36 | 69 / 69 / 69 | 32 to 33 | 1.86 to 1.92 |
| gcc | 2 | 2,495 s | 26 / 28 / 28 | 54 / 54 / 55 | 26 to 28 | 1.93 to 2.08 |
| spins | 3 | 2,700 s | 107 / 108 / 108 | 195 / 193 / 192 | 84 to 88 | 1.78 to 1.82 |
| seven small models | 3 | 60 s | 9 to 15 | 11 to 28 | 2 to 14 | 1.22 to 2.00 |

At strength 2, a locating array needed about 1.6 to 2.1 times the tests of a covering array at the same budget. At
strength 3 on spins the ratio was about 1.8. Spins and bugzilla finished before the cap at t = 2; the other CCAG runs
were capped.

On the seven small models, exact minima by MaxSAT (item 63) show that the best of three seeds reached the proven
minimum in 27 of 28 (model, strength, mode) cases. The exception is model_8param locating at t = 3: the minimum is 26
and the search found 27 to 28. More budget did not close that gap (item 64). At the minimum, the ratio of locating to
covering size is 1.33 to 1.80 at t = 2 and 1.22 to 1.86 at t = 3.

**Answer.** Localizing one fault costs roughly 1.6 to 2 times the tests needed for coverage on these models, both in
the search results and at the proven minimum where it is known.

### 5.2 RQ2: Does the move design matter?

SA4LA cannot express constraints, so both tools ran on the CCAG models with the constraints removed. Our search was
capped at SA4LA's own run time for the same model and seed, on the same container. Sources: items 52, 54 and 55.

| model (unconstrained) | SA4LA | targeted move, same time | local move, same time |
|---|---|---|---|
| spins | 35 / 35 / 35 | 45 / 44 / 43 | 35 / 36 / 35 |
| bugzilla | 32 / 32 / 32 | 43 / 44 / 43 | 32 / 32 / 32 |
| spinv | 51 / 51 / 52 | 66 / 68 / 67 | 51 / 51 / 52 |

**Diagnosis.** We started the targeted move at SA4LA's own size. It solved that size in none of 18 runs, even with
30,000 moves, whereas SA4LA reached it within single anneals of at most 4,096 moves. The targeted move also made about
4 to 9 times fewer moves per second. The gap therefore came from the move (replacing a whole test with a fresh solver
draw), not from the size schedule. With the local move the search matched SA4LA at equal time; one spins seed was one
test worse. Given more moves from SA4LA's size, the local move reached 50 on spinv (3 seeds) and 34 on spins (1 seed).
Apache was not part of the re-run.

**Answer.** Yes. Editing only the values of the target interaction, as SA4LA does, was the difference. Keeping every
test valid did not prevent it from matching SA4LA on these models.

### 5.3 RQ3: Constrained benchmarks against the published CLA heuristic

The published figures are from Jin & Tsuchiya's Table 1 (10 runs each). Our cap equals their average time, with a
minimum of 5 s. Sources: items 56, 59 and 60. **Different hardware and language, and their tool is not public, so this
is not a same-machine comparison.**

| model | published min to max (avg time) | local move, cap = their time | local move, 10x |
|---|---|---|---|
| apache | 85 to 89 (3,263 s) | 67 to 69, median 68.5 (10 seeds) | not run |
| gcc | 61 to 68 (2,495 s) | 54 to 55, median 54 (10 seeds) | not run |
| spins | 49 to 53 (0.63 s) | 51 / 50 / 51 (5 s) | 42 / 42 / 43 |
| bugzilla | 41 to 48 (9.02 s) | 46 / 46 / 46 | 36 / 35 / 34 |
| spinv | 91 to 97 (58.21 s) | 95 / 96 / 95 | 83 / 83 / 83 |
| Insurance | 789 to 805 (84.34 s) | 803 / 803 / 803 (3 seeds) | 775 to 782, median 778 (10 seeds) |

On the 18 literature benchmarks, at 10 times max(5 s, their time), the median over 3 seeds was below the published
minimum on 12 and inside the published range on 6. On 13 of those models their time is under 1 s, so even the first
cap gives our search 5 to 50 times their time.

**Answer.** On the two largest constrained systems the search found smaller arrays than the published heuristic's best
within the heuristic's average time: apache 67 to 69 against 85, gcc 54 to 55 against 61.

**The margin depends on the machine.** The author re-ran seed 0 on a second machine (Windows, Python 3.13.1, z3 5.1.0,
against Linux and z3 5.3.2; PROJECT_NOTES item 83). It reached 73 on apache and 60 on gcc, both again stopped by the
cap. Both are still below the published minimum, but by 1 test on gcc. Sizes at a time cap depend on how many moves fit
in the budget, so we report the claim as "below the published minimum on both machines", not as a fixed margin.

On small
models it is **not faster**: it reaches smaller arrays given seconds to minutes, against their sub-second times.

### 5.4 RQ4: What does locating two faults cost?

Exact minima by MaxSAT or SAT over all valid configurations, t = 2. Sources: items 65 and 70.

| model | valid configurations | C(1, 2) | C(2, 2) |
|---|---|---|---|
| model.json | 18 | 9 | 17 |
| model_6param.json | 36 | 10 | 22 |
| model_8param.json | 144 | 11 | 26 (search: 28 / 27 / 28) |
| model_high_constraints.json | 11 | 9 | 11 |
| model_low_constraints.json | 32 | 8 | 15 |
| model_multivalue.json | 30 | 11 | 22 |
| my_model.json | 24 | 8 | 17 |
| model_spins_core.json | 978 | search 30 / 30 / 30; proven >= 16 | search 83 / 84 / 82; proven >= 16 |

**Cost.**
- At t = 2 the exact minimum for two faults is roughly double that for one on the small models. The exception is
  model_high_constraints, which has only 11 valid configurations.
- At t = 3, d = 2 needs every valid configuration on four of the seven small models (item 65; model_8param, solved
  later in item 70, needs 50 of its 144).
- On model_8param, C(2, 3) = 50; the d = 2 search capped at 1,800 s reached 55.
- The search reached the exact C(2, 2) on six of the seven small models.

**Bounds on the larger model.** On model_spins_core, the best proven lower bound for both minima is 16, from counting
(items 71 and 72): two parameters have 16 feasible value pairs and each test contains exactly one of them. Z3 MaxSAT
and lazy SAT both failed to prove more within 30 to 60 minutes per question. The t = 2 covering minimum there is
between 16 and 18. Whether the search is near-optimal on this model is open.

**Two faults at t = 2 versus one fault at t = 3.** On all seven small models, C(2, 2) = C(1, 3). This is not a general
rule:
- **Random models** (item 65): 33 solved random models with 3 to 6 parameters. The minima were equal on 27. On the
  other 6, C(2, 2) was smaller.
- **Counterexamples to implication** (item 67): (1bar, 3)-CLAs that are not (2bar, 2)-CLAs exist. One is on 5
  unconstrained three-valued parameters; others are on 13 of 198 random constrained models. Each counterexample was
  verified independently.
- **Sizes on those 15 counterexample models** (item 68): the minimum (2bar, 2) size is smaller than the minimum
  (1bar, 3) size on 12 and unsettled on 3. On no model so far is it larger.
- **Unconstrained binary models** with 3 to 6 parameters (item 69): the two minima are exactly equal (8, 14, 15, 19).

Colbourn & McClary (2008) relate (d, t)-detecting arrays to covering arrays of strength t + d. We did not find a
published statement relating (1bar, t + 1)-locating to (2bar, t)-locating. Colbourn & McClary was read only in
excerpts, so this is "not found", not "new".

**Answer.** Locating two faults roughly doubles the minimum at t = 2 on these small models. The cheaper strategy of
building a (1bar, 3) array does not guarantee two-fault location. On the models tested, a (2bar, 2) array was never
larger than a (1bar, 3) array.

### 5.5 RQ5: What happens when real faults break the assumptions?

A (dbar, t)-CLA guarantees the right answer only for at most d deterministic t-way faults. We measured what the
standard construction and its alternatives report when this does not hold. Sources: PROJECT_NOTES items 73 to 76.

**Suites and decoders.** For each model we compare three suites at t = 2, each decoded with its own decoder:

| suite | what it is | decoder |
|---|---|---|
| C | a minimum covering suite | one-pair |
| L1 | a (1bar, 2) CLA | one-pair |
| L2 | a (2bar, 2) CLA | up-to-two-pairs |

A diagnosis is *misleading* when no candidate is equivalent to the true fault, and some candidate is present in a
valid configuration that passes.

**Simulated violations (8 models, 5 seeds; items 73 and 74).** Range over models and seeds of the share of faults with a
wrong diagnosis:

| real fault | C | L1 | L2 |
|---|---|---|---|
| one faulty pair (as designed) | 0% | 0% | 0% |
| two faulty pairs | 14 to 52% | 3 to 22% | 0% |
| one faulty 3-way interaction | 11 to 60% | 7 to 85% | 0% |
| one pair, 5% of outcomes flipped | 2 to 21% | 9 to 18% | 0 to 8% |

L2's zero for a single higher-strength fault is not chance:
- **Claim.** In a (dbar, t)-CLA with d >= 2, every explanation of the failing tests of a feasible fault T of strength
  greater than t names only interactions whose every valid configuration contains T.
- **Proof.** For a t-subset p of T and a candidate s, rho(s) is contained in rho(T), which is contained in rho(p). So
  {p} and {p, s} produce the same failing tests. The array must therefore treat them as indistinguishable, which means
  every valid configuration containing s contains p.
- **Prior art.** This is the constrained analogue of Colbourn & McClary's Lemma 7.1: a (dbar, t)-locating array is
  (d - 1, t)-detecting. We do not claim it as new.
- **Exhaustive check.** On 7 small models, every 3-way and 4-way fault had 0 violations for L2, and violations on 6 of
  7 models for L1.

**Real programs (items 75 and 76).**
- **Subjects.** Two CPython 3.13 standard-library modules: `textwrap` (10 options, 4,352 valid configurations, with the
  library's own validity rule as the constraint) and `configparser` (10 options, 3,456 configurations, unconstrained).
- **Pass/fail.** A test is a configuration run on a fixed set of inputs. It fails if its output or the exception it
  raises differs from the unmodified module's.
- **Faults.** Every single-point mutant of the main classes under standard mutation operators: 131 and 258 mutants. We
  ran each mutant on every valid configuration, which gives its exact set of failing configurations as ground truth.
- **Faults kept.** Configuration-dependent faults, those failing on some but not all valid configurations: 83 for
  textwrap (61 distinct failure sets) and 110 for configparser (29 distinct).

How the real faults fit the model:

| failure set is exactly the configurations containing | textwrap (83) | configparser (110) |
|---|---|---|
| one pair | 0 | 1 |
| two pairs | 11 | 47 |
| a union of 3 or more pairs | 8 | 59 |
| a union of 3-way interactions | 16 | 2 |
| needs 4-way or wider | 48 | 1 |

Diagnoses (counted per mutant; per distinct failure set in brackets):

| | textwrap correct | textwrap misleading | configparser correct | configparser misleading |
|---|---|---|---|---|
| C (12 / 9 tests) | 0 (0) | 24 (21) | 0 (0) | 56 (6) |
| L1 (21 / 19 tests) | 0 (0) | 5 (4) | 1 (1) | 2 (1) |
| L2 (58 / 49 tests) | 11 (5) | 3 (3) | 48 (11) | 0 (0) |

All remaining faults were flagged (no explanation matched) or missed (no test failed).
- **L2.** On both programs, L2 diagnosed correctly every fault that fit its model. Its 3 misleading cases on textwrap
  are unions of several higher-strength interactions, which the claim above does not cover.
- **L1.** L1 diagnosed one fault correctly in total, because single-pair faults were almost absent.
- **Suite sizes.** L1 and L2 are search results, seed 0. L2 was capped at 900 s, so it is an upper bound. All suites
  pass the independent verifier.

**Equal-budget controls (item 77).** Is L2's advantage just its size? We compared it with two alternatives:
- R: suites of exactly |L2| valid configurations drawn uniformly at random (5 seeds), with the same up-to-two-pairs
  decoder.
- L13: a (1bar, 3) CLA, the other natural way to spend a larger budget (71 and 57 tests, verified).

| suite | textwrap correct / misleading | configparser correct / misleading |
|---|---|---|
| L2 | 11 / 3 | 48 / 0 |
| R, same size, 5 seeds | 5 to 11 / 3 to 6 | 39 to 48 / 0 to 16 |
| L13, one-interaction decoder | 0 / 0 | 1 / 0 |
| L13, up-to-two-pairs decoder | 11 / 4 | 48 / 0 |

- **Budget and decoder explain most of the effect.** Random suites of the same size reach about the same number of
  correct diagnoses in most seeds. So does the (1bar, 3) suite once it is decoded with two-pair explanations.
- **The construction gives the best case consistently, not a significantly better average (item 78).**
  - Setup: 200 random draws per program, compared with 3 independently searched L2 suites per program.
  - Correct diagnoses: every L2 suite reached the maximum that any random draw reached (11 and 48). Random draws fell
    short of it in 100 and 168 of 200 cases.
  - Misleading diagnoses: L2's counts (2 to 4, and 0) sit near the random median, not below it.
  - Significance: with an empirical one-sided test (share of random draws at least as good), no L2 suite is
    significantly better than a typical random suite (all p >= 0.16).
  - The random tail is real: 32 and 37 of 200 draws misled on at least 6 and at least 10 faults.
  - Guaranteed pair coverage does not close the gap. We padded a minimum covering suite with random tests to the same
    size (200 draws, item 81). It averaged 9.97 and 43.98 correct; 114 and 164 of 200 fell short of L2 (p = 0.43 and
    0.18). What the construction adds is the separation of two-pair explanations, not coverage.
  - L2 also carries the guarantee above.

**Answer.**
- On these two programs, configuration-dependent faults rarely have the single-pair form the standard (1bar, 2)
  construction targets.
- That construction rarely misleads (2 to 6% of faults), but it almost never diagnoses either.
- A (2bar, 2) CLA costs 2.6 to 2.8 times as many tests and diagnosed every fault that fit its model (11 and 48).
- Equal-size random suites with the same decoder are not significantly worse on average. So the main lever is a test
  budget large enough, plus a decoder that allows two-pair explanations.
- The (2bar, 2) construction makes the outcome dependable: it reached the best case in all 6 suites built, which half
  or more of random suites did not, and it carries the guarantee for single higher-strength faults.
- For practice: if a test budget allows only a one-fault locating array, its main value on these programs is to signal
  that a failure does not fit the model; it rarely names the cause.

## 6. Threats to validity

- **External.**
  - The CLA heuristic comparison (RQ3) is not same-machine: their tool is not public, and the language and hardware
    differ.
  - RQ4 uses only small models and one derived model; no CCAG benchmark was run at d = 2. The prototype scores all
    pairs of fault sets over enumerated configurations, which does not scale to them.
  - RQ5 uses two programs, both Python standard-library modules, each with one fixed input corpus. The faults are
    mutation faults, not historical bugs. configparser has no constraints, so it does not exercise the constrained
    setting.
  - Six Table 1 rows (8, 9 and 21 to 24) were read by a freeform query of a PDF conversion and must be checked. Rows
    1 to 5 were not available.
- **Internal.**
  - Most benchmark runs were stopped by a time cap while still shrinking, so their sizes are upper bounds for the
    budget, not minima.
  - The exact minima depend on the encoding matching the definition. This was checked by a second verifier and by
    agreement between two solver routes (MaxSAT and SAT) on 19 minima.
- **Conclusion.**
  - Three seeds per configuration (ten for apache, gcc and Insurance) is a small sample.
  - Minimality is proven only on the small models. On the CCAG models no lower bound is known; on model_spins_core
    the proven bound (16) is far below the search size (30).
- **Reproduction.** All numbers come from cloud runs. The author re-ran the following on their own machine (Windows,
  against the Linux cloud):
  - the small-model rows of RQ1 and RQ4, and all of RQ5 except the suite searches: every row matched;
  - RQ1 on spins and bugzilla: 3 of 4 rows equal, spins locating 39 against 38 in a finished run, probably from a
    different z3 version;
  - RQ3 apache and gcc, seed 0: 73 and 60 against 67 to 69 and 54 to 55, both capped.
  RQ2 (the SA4LA race) and RQ3's literature benchmarks and Insurance runs have not been reproduced locally.

## 7. Related work

- **Locating arrays.** Colbourn & McClary (2008) introduced locating and detecting arrays for interaction faults and
  related detecting arrays to covering arrays of higher strength. Other work: optimal locating arrays for at most two
  faults (Shi, Tang & Yin 2012); mixed alphabet sizes (Shi, Jin & Tsuchiya 2020); faster location and d = 2
  constructions in the unconstrained case (Dougherty, Green & Kim 2023, arXiv 2310.07448).
- **Constrained locating arrays.** Jin & Tsuchiya (2020) define CLAs and distinguishability, prove existence, and give
  a heuristic and an SMT construction. Constrained detecting arrays are studied by Jin, Shi & Tsuchiya (arXiv
  2110.06449).
- **Search-based construction.** Konishi et al. find minimum locating arrays with a CSP solver (arXiv 1904.07480) and
  build unconstrained locating arrays by SA in SA4LA (Konishi et al. 2020). Our cost and
  our local move follow theirs. Garvin, Cohen & Dwyer apply meta-heuristic search with constraint handling to
  constrained **covering** arrays (2009, 2011). A survey of constrained combinatorial testing is Wu et al.
  (arXiv 1908.02480).
- **Not found.** In three searches (excerpts only) we did not find a metaheuristic for constrained locating arrays, or
  a minimum-size result for constrained (2bar, t) locating arrays.

## 8. Conclusion

Simulated annealing with moves that keep every test valid builds constrained locating arrays. On the constrained
benchmarks used by Jin & Tsuchiya, it reaches smaller sizes than the published heuristic given comparable or larger
time, though not on the same machine. On the unconstrained versions it matches SA4LA at equal time once the move edits
only the target interaction's values. Localization costs roughly 1.6 to 2 times the tests of coverage. On small models,
locating two faults at strength 2 costs about twice as much as one fault and, on the models tested, never more than
locating one fault at strength 3. A (1bar, 3) array does not guarantee two-fault location.

When faults break the model, the standard one-fault array seldom names a wrong cause, but on two real programs it
almost never named the right one either. A two-fault array, at about 2.6 to 2.8 times the tests, diagnosed every
mutation fault that fit its model, and by a known property it never names a cause unrelated to a single
higher-strength fault. Equal-size random suites with the same decoder were not significantly worse on average, but half
or more fell short of the construction's result. The budget and the decoder drive most of the gain; the construction
makes it dependable.

Open questions:
- Lower bounds that make the search's sizes on mid-sized models such as model_spins_core interpretable.
- d = 2 on real benchmarks, which needs a scoring method that does not enumerate configurations.
- More programs, historical (not mutation) faults, and strength-3 suites for RQ5.
- Local reproduction of all results.

## References

Bibliographic details were confirmed on 2026-11-05 against Crossref records and arXiv abstract pages; only the titles,
authors and venues were checked, not the papers' contents. Each source is also listed in `docs/LITERATURE_CHECK.md`.

1. C. J. Colbourn and D. W. McClary. Locating and detecting arrays for interaction faults. *Journal of Combinatorial
   Optimization* 15(1):17-48, 2008 (online 2007). DOI 10.1007/s10878-007-9082-4. Lemma numbers in RQ5 are from the
   Dagstuhl Seminar Proceedings 09281 version, DOI 10.4230/DagSemProc.09281.3 (check against the journal version).
2. H. Jin and T. Tsuchiya. Constrained locating arrays for combinatorial interaction testing. *Journal of Systems and
   Software* 170:110771, 2020. DOI 10.1016/j.jss.2020.110771. arXiv 1801.06041.
3. T. Konishi, H. Kojima, H. Nakagawa and T. Tsuchiya. Using simulated annealing for locating array construction.
   *Information and Software Technology* 126:106346, 2020. DOI 10.1016/j.infsof.2020.106346. arXiv 1909.13090.
4. T. Konishi, H. Kojima, H. Nakagawa and T. Tsuchiya. Finding minimum locating arrays using a CSP solver. arXiv
   1904.07480, 2019. (Journal version not checked.)
5. H. Jin, C. Shi and T. Tsuchiya. Constrained detecting arrays: mathematical structures for fault identification in
   combinatorial interaction testing. arXiv 2110.06449, 2021. (Summary in ICSTW 2024, pp. 215-216, DOI
   10.1109/ICSTW60967.2024.00049.)
6. B. J. Garvin, M. B. Cohen and M. B. Dwyer. An improved meta-heuristic search for constrained interaction testing.
   In *1st International Symposium on Search Based Software Engineering (SSBSE)*, pp. 13-22, 2009. DOI
   10.1109/SSBSE.2009.25.
7. B. J. Garvin, M. B. Cohen and M. B. Dwyer. Evaluating improvements to a meta-heuristic search for constrained
   interaction testing. *Empirical Software Engineering* 16(1):61-102, 2011 (online 2010). DOI
   10.1007/s10664-010-9135-7.
8. R. E. Dougherty, D. N. Green and G. M. Kim. Faster location in combinatorial interaction testing. arXiv 2310.07448,
   2023.
9. H. Wu, C. Nie, J. Petke, Y. Jia and M. Harman. A survey of constrained combinatorial testing. arXiv 1908.02480, 2019.
10. C. Shi, Y. Tang and J. Yin. Optimal locating arrays for at most two faults. *Science China Mathematics*
    55(1):197-206, 2012 (online 2011). DOI 10.1007/s11425-011-4307-5.
11. C. Shi, H. Jin and T. Tsuchiya. Locating arrays with mixed alphabet sizes. *Mathematics* 8(5):831, 2020. DOI
    10.3390/math8050831. arXiv 2001.11712.
12. M. B. Cohen, M. B. Dwyer and J. Shi. Constructing interaction test suites for highly-configurable systems in the
    presence of constraints: a greedy approach. *IEEE Transactions on Software Engineering* 34(5):633-650, 2008. DOI
    10.1109/TSE.2008.50.
13. I. Segall, R. Tzoref-Brill and E. Farchi. Using binary decision diagrams for combinatorial test design. In *ISSTA
    2011*, pp. 254-264. DOI 10.1145/2001420.2001451. The Jia et al. archive (ref. 14) attributes its 20 real-world models to "a recent benchmark created by Segall et al."; [verify that the archive's reference is this paper]
14. Y. Jia, M. B. Cohen, M. Harman and J. Petke. Combinatorial Interaction Testing (CIT) Benchmarks. Zenodo, DOI
    10.5281/zenodo.581657.
15. SA4LA, github.com/tatsuhirotsuchiya/SA4LA. CCAG, github.com/GIST-NJU/CCAG.

## Author checklist before submission

- [x] Reproduce the small-model and RQ5 rows locally (done 2026-11-08, item 80; all rows matched).
- [ ] Reproduce RQ1 CCAG rows, RQ2 and RQ3 locally (tiers `spins` and `long`; needs the CCAG folder).
- [ ] Check Table 1 numbers against the journal PDF.
- [ ] Confirm the origin of the 18 literature models (the last [verify]).
- [ ] Read Colbourn & McClary (2008) in full before keeping the "not found" sentence in RQ4.
- [ ] Decide the target venue and trim to its page limit. RQ4 could be a separate short paper.
