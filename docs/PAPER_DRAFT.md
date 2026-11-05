# Simulated Annealing for Constrained Locating Arrays: Cost Relative to Covering, and One versus Two Faults

*Working title. Full first draft, written 2026-11-05 in a live cloud session for the author to rewrite.*

> **Status of this draft (read first).**
> - Every number comes from `docs/PAPER_RESULTS.md` or a named `docs/PROJECT_NOTES.md` section. None was re-measured
>   for this draft. Every number is a **sandbox (cloud) result that the author has not reproduced locally**.
> - Before submission:
>   - Re-run the headline rows locally (`scripts/reproduce.py quick`).
>   - Check every Jin & Tsuchiya Table 1 figure against the journal PDF.
>   - Resolve each **[verify]** and **[cite]** marker.
> - Citations are limited to sources listed in `docs/LITERATURE_CHECK.md`. Volume, page and year details marked
>   [verify] were not confirmed: the citation database could not be reached from this session (HTTP 403).
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
to 55 tests within the published heuristic's average time, below its minima of 85 and 61 (10 seeds). The hardware
differs, so this is not a same-machine comparison. On 18 literature benchmarks, at ten times the larger of 5 s and the
heuristic's time, the median over 3 seeds was below the published minimum on 12.

**What does locating two faults cost?** On seven small models with exact minima, locating up to two faults at strength
2 needs roughly twice the tests of locating one. On all seven it needs exactly as many as locating one fault at
strength 3. We show by verified counterexamples that a (1bar, 3)-locating array need not be (2bar, 2)-locating, so that
equality is not a general rule.

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
constrained **covering** arrays (Garvin, Cohen & Dwyer [verify venue and year]). This work combines the two settings,
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
- **Five constrained systems** (apache, bugzilla, gcc, spins, spinv) from the CCAG repository [cite repository]. Their
  parameter and value counts match the systems of Cohen, Dwyer & Shi (2008) [verify].
- **18 literature benchmarks** (Segall et al. [verify]), taken from the Jia et al. CIT benchmark archive (Zenodo, DOI
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
within the heuristic's average time: apache 67 to 69 against 85, gcc 54 to 55 against 61. On small
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

## 6. Threats to validity

- **External.**
  - The CLA heuristic comparison (RQ3) is not same-machine: their tool is not public, and the language and hardware
    differ.
  - RQ4 uses only small models and one derived model; no CCAG benchmark was run at d = 2. The prototype scores all
    pairs of fault sets over enumerated configurations, which does not scale to them.
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
- **Reproduction.** All numbers come from cloud runs that the author has not yet reproduced locally.

## 7. Related work

- **Locating arrays.** Colbourn & McClary (2008) introduced locating and detecting arrays for interaction faults and
  related detecting arrays to covering arrays of higher strength. Other work: optimal locating arrays for at most two
  faults (Shi, Tang & Yin 2011 [verify]); mixed alphabets [cite arXiv 2001.11712]; faster location and d = 2
  constructions in the unconstrained case (Dougherty, Green & Kim 2023, arXiv 2310.07448).
- **Constrained locating arrays.** Jin & Tsuchiya (2020) define CLAs and distinguishability, prove existence, and give
  a heuristic and an SMT construction. Constrained detecting arrays are studied by Jin, Shi & Tsuchiya (arXiv
  2110.06449).
- **Search-based construction.** Konishi et al. find minimum locating arrays with a CSP solver (arXiv 1904.07480) and
  build unconstrained locating arrays by SA in SA4LA (Inf. Softw. Technol. 126, 2020, 106346 [verify]). Our cost and
  our local move follow theirs. Garvin, Cohen & Dwyer apply meta-heuristic search with constraint handling to
  constrained **covering** arrays [verify venue and year]. A survey of constrained combinatorial testing is Wu et al.
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

Open questions:
- Lower bounds that make the search's sizes on mid-sized models such as model_spins_core interpretable.
- d = 2 on real benchmarks, which needs a scoring method that does not enumerate configurations.
- Local reproduction of all results.

## References

Only sources listed in `docs/LITERATURE_CHECK.md`. Fields marked [verify] were not confirmed against the publisher.

1. C. J. Colbourn and D. W. McClary. Locating and detecting arrays for interaction faults. *J. Comb. Optim.* 15(1),
   2008. (Also Dagstuhl Seminar Proceedings 09281.)
2. H. Jin and T. Tsuchiya. Constrained locating arrays for combinatorial interaction testing. *J. Syst. Softw.* 170,
   2020. arXiv 1801.06041. [verify title and pages]
3. T. Konishi, H. Kojima, H. Nakagawa and T. Tsuchiya. Using simulated annealing for locating array construction.
   *Inf. Softw. Technol.* 126, 2020, 106346. arXiv 1909.13090. [verify title]
4. T. Konishi et al. Finding minimum locating arrays using a CSP solver. arXiv 1904.07480. [verify authors and venue]
5. H. Jin, C. Shi and T. Tsuchiya. Constrained detecting arrays. arXiv 2110.06449. [verify title and venue]
6. B. J. Garvin, M. B. Cohen and M. B. Dwyer. An improved meta-heuristic search for constrained interaction testing.
   SSBSE 2009; and Evaluating improvements to a meta-heuristic search for constrained interaction testing, *Empirical
   Softw. Eng.*, DOI 10.1007/s10664-010-9135-7. [verify volume and year]
7. R. Dougherty, D. Green and H. Kim. Faster location in combinatorial interaction testing. arXiv 2310.07448.
   [verify authors]
8. H. Wu et al. A survey of constrained combinatorial testing. arXiv 1908.02480. [verify authors]
9. C. Shi, Y. Tang and J. Yin. Optimal locating arrays for at most two faults. *Sci. China Math.*, 2011. [verify]
10. M. B. Cohen, M. B. Dwyer and J. Shi. (Constrained covering array benchmarks.) *IEEE TSE* 34, 2008. [verify title]
11. Y. Jia, M. B. Cohen, M. Harman and J. Petke. Combinatorial Interaction Testing (CIT) Benchmarks. Zenodo, DOI
    10.5281/zenodo.581657.
12. I. Segall, R. Tzoref-Brill and E. Farchi. (Real-world models.) ISSTA 2011. [verify; origin of the 18 models]
13. SA4LA repository, github.com/tatsuhirotsuchiya/SA4LA. CCAG repository, GIST-NJU/CCAG on GitHub.
14. Locating arrays with mixed alphabet sizes. arXiv 2001.11712. [verify authors]

## Author checklist before submission

- [ ] Reproduce headline rows locally and relabel them "reproduced locally".
- [ ] Check Table 1 numbers against the journal PDF.
- [ ] Resolve every [verify] and [cite].
- [ ] Read Colbourn & McClary (2008) in full before keeping the "not found" sentence in RQ4.
- [ ] Decide the target venue and trim to its page limit. RQ4 could be a separate short paper.
