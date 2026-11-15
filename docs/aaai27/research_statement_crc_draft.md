# Research statement, camera-ready draft (corrections only)

Transcribed from the accepted PDF (`AAAI-27_UC_ResearchStatement__87.pdf`, uploaded 2026-11-09).
- **What changed.** Only the changes listed at the end. Everything else is the accepted text, word for word.
- **Not covered.** New results since acceptance are not added; that waits for the mentor's answer
  (`docs/AAAI27_UC_PLAN.md`, question 1).
- **Author block.** Name, affiliation and email stay as in the accepted PDF. They are left out here so the email is
  not stored in the repository.

---

**Constraint-Aware Test Suites That Locate Faults: Simulated Annealing for Configurable Software**

*(author block unchanged)*

## Introduction

Highly configurable software fails when particular combinations of options interact. Combinatorial interaction testing
(CIT) builds small test suites that cover every t-way combination of option values, but a suite that exposes a failure
does not say *which* combination caused it. Locating arrays (Colbourn and McClary 2008) are designed so that the pattern
of passing and failing tests identifies the failure-inducing interaction. Real systems also forbid some combinations,
and constraints can make some interactions impossible to tell apart however many tests are run (Jin and Tsuchiya 2020).
The problem is relevant to AI in two ways. The methods come from AI: search and optimization (simulated annealing)
combined with constraint reasoning. And the targets include machine-learning systems, whose training pipelines and
frameworks also have many settings that can interact and fail together.

My research question is: *how can we efficiently generate small, constraint-aware test suites that cover every feasible
interaction and also distinguish every interaction that can be distinguished?* I study the tradeoff among suite size,
coverage, localization ability, and computational cost. This statement describes a long-term project I would pursue in
graduate school, and the early prototype that shows the first stage is feasible.

## Background

Jin and Tsuchiya define constrained locating arrays (CLAs): two sets of valid interactions are *distinguishable* if some
valid test covers an interaction in one set and none in the other, and CLAs only need to separate distinguishable pairs
(Jin and Tsuchiya 2020). Their construction builds a covering array and then deletes redundant tests. Konishi et al.
use simulated annealing (SA) for locating arrays without constraints, with a cost that counts uncovered interactions
plus interactions that share the same covering tests, and they list the constrained case as future work (Konishi et al.
2020) **[C1]**. SA is also established for covering arrays (Torres-Jimenez and Rodriguez-Tello 2012), and recent work on
faster location treats only the unconstrained case (Dougherty, Green, and Kim 2023). Related work includes exact
constraint-solver construction of minimum locating arrays (Konishi et al. 2019) **[C2]**, constrained detecting arrays
(Jin, Shi, and Tsuchiya 2021), and metaheuristic search for constrained interaction testing (Garvin, Cohen, and Dwyer
2011).

I did not find prior work that applies SA to constrained locating arrays, with the search restricted to valid
configurations and the result judged against the distinguishability limit. This is a hypothesis, not a claim: my search
is not exhaustive and I will extend it. I do not claim to have invented locating arrays, constrained locating arrays, or
the distinguishability concept. I have not yet surveyed machine-learning approaches to fault localization, and I would
do that review before starting Stage 4.

## Approach

I developed a Python prototype that models parameters and forbidden partial assignments, enumerates valid
configurations and feasible pairwise interactions, injects a single deterministic interaction fault, and checks whether
the pass/fail pattern identifies it uniquely. The *ceiling* is the number of interactions whose set of covering
configurations (over all valid configurations) differs from every other interaction's. It is the single-fault, pairwise
case of distinguishability (Jin and Tsuchiya 2020) and serves as the achievable target.

The SA state is a list of N valid configurations, so every test is valid by construction. The cost is the number of
uncovered interactions plus the number of *avoidable* collisions, meaning covered interactions that share identical
covering tests although no suite is forced to give them identical tests. A cost of zero therefore means full coverage
with the ceiling reached, which I verified with tests. A move replaces one test, either with a random valid
configuration or, in the targeted variant, with one chosen to fix an uncovered or colliding interaction. Moves are
accepted with probability exp(−∆/T) under geometric cooling. An outer loop shrinks N one test at a time. A size *fails*
only after a fixed budget of restarts and moves, so runs are reproducible across machines; a failure is not a proof that
the size is impossible. I compare against a greedy locating heuristic (not optimal) and, on small models, against exact
brute-force minima.

## Evaluation

I measure suite size, covered interactions, interactions localized under exhaustive single-fault injection, the gap to
the ceiling, and the moves used. All results below were reproduced on my own machine. On three small hand-built models,
SA reaches the proven minimum suite sizes of 9, 9, and 8 tests, with localization equal to the ceiling, while the greedy
heuristic needs one to two more tests.

For a more realistic test I derived a nine-parameter model from the 13 forbidden rules of the `spins` benchmark in the
CCAG repository (978 valid configurations, 239 feasible interactions, ceiling 229). This is a derived projection, not
the original benchmark. Greedy locating needs 32 tests. With a single seed, SA found 30 tests at 6,000 moves per run and
29 tests at 20,000 moves per run, covering 239 of 239 interactions and localizing 229, which equals the ceiling. No
28-test suite was found within 100,000 moves, and the true minimum is unknown.

## Long-Term Plan

The prototype covers only the simplest fault model: one deterministic fault, a pairwise interaction, and models small
enough to enumerate. A graduate project would extend it in stages, and I would keep each stage separate so that every
result has a clear baseline.

*Stage 1: scale.* Replace enumeration of valid configurations with a SAT or SMT solver, so that validity checks and
distinguishability checks become queries. This is what is needed to run on the standard benchmarks, which have up to
about 200 parameters, and to compare directly with published CLA sizes.

*Stage 2: stronger faults.* Study three-way interactions and several simultaneous faults. The number of interactions to
cover and separate grows quickly with the strength, so I expect the cost function and the moves to need new ideas here.
**[C3]**

*Stage 3: noisy outcomes.* Real failures are sometimes nondeterministic. I would model flaky tests and treat
localization as probabilistic inference: given noisy pass/fail outcomes, which interaction is most likely responsible,
and how many repeated runs are needed to keep that ranking reliable?

*Stage 4: richer evidence.* Only after the earlier stages have deterministic baselines would I test statistical or
machine-learning ranking of suspect interactions, using test outcomes together with logs, stack traces, and source-code
information. The simulated faults supply labeled data for free, because I know which interaction I injected. I would
train a ranker on some models and fault sets and test it on others, and compare it with the deterministic baseline to
see whether learning adds anything beyond the pass/fail pattern. I would keep interaction localization separate from
source-code fault localization throughout. A related idea is to learn which annealing moves tend to help, to guide the
search, and I would try it only if the baseline search stalls. Finally, I would apply the method to configuration
spaces of machine-learning pipelines as a real-world case study.

*How I would evaluate each stage.* Every stage would use the same measurements: suite size compared with my greedy
baseline and with published CLA sizes; the number of feasible interactions localized compared with the ceiling, using
exhaustive injection of each feasible interaction as a single fault; moves and running time; and the median and range
over many seeds instead of one run. For the larger stages I would use the shared benchmark models from the CCAG
repository so that results can be compared with other work.

The central questions are how much of the achievable localization a search can recover as models grow, what each stage
costs in suite size and computation, and which constraint structures make localization hardest. The prototype already
produces the measurements these questions need: suite size, coverage, localized interactions, gap to the ceiling, and
moves used.

## Discussion

These results are early. They use one seed on one derived model, and the SA schedule is untuned. The original `spins`
model has about two million valid configurations, so enumeration cannot reach standard benchmarks, and the next step is
a SAT or SMT solver for validity and distinguishability. The ceiling itself is known theory, so the contribution I aim
for is empirical: a metaheuristic for constrained locating arrays, scored against the ceiling and against published CLA
sizes on shared benchmarks.

The main risks are scale and fairness of comparison. Annealing may stall on large models, as my unsolved runs froze
early on the derived model, and published sizes come from different tools and time limits. I would report spreads over
many seeds, fix a move budget so that runs are reproducible, and compare on shared benchmarks rather than my own
models. A first, immediate step is to run multiple seeds to see whether the 29-test result repeats.

Two lessons from the prototype shape the plan. First, a clear, checkable objective helps: because a cost of zero
provably means the ceiling is reached, I can test the search against exact minima on small models. Second, I should
check the literature early, not late. A review of recent papers showed that the ceiling and the locating-aware cost
were already known, and I rewrote my notes to say so. I would repeat that check before every claim of novelty.

Keeping the work reproducible, with fixed budgets, seeded runs, and automated tests, is part of the contribution,
because a localization method is only useful if others can repeat its results.

## Conclusion

A constraint-aware simulated annealing search can produce locating-oriented test suites that reach the distinguishability
ceiling and are smaller than a greedy baseline on the models tested. I propose to make this rigorous through
solver-based constraint handling, multi-seed statistics, and comparison with published constructions, and to extend it
toward harder fault models.

## References

Colbourn, C. J.; and McClary, D. W. 2008. Locating and Detecting Arrays for Interaction Faults. *Journal of
Combinatorial Optimization*, 15(1): 17–48. **[C4]**

Dougherty, R. E.; Green, D. N.; and Kim, G. M. 2023. Faster Location in Combinatorial Interaction Testing.
ArXiv:2310.07448.

Garvin, B. J.; Cohen, M. B.; and Dwyer, M. B. 2011. Evaluating Improvements to a Meta-Heuristic Search for Constrained
Interaction Testing. *Empirical Software Engineering*, 16(1): 61–102. Doi:10.1007/s10664-010-9135-7. **[C5]**

Jin, H.; Shi, C.; and Tsuchiya, T. 2021. Constrained Detecting Arrays: Mathematical Structures for Fault Identification
in Combinatorial Interaction Testing. ArXiv:2110.06449. **[C6]**

Jin, H.; and Tsuchiya, T. 2020. Constrained Locating Arrays for Combinatorial Interaction Testing. *Journal of Systems
and Software*, 170: 110771. **[C7]**

Konishi, T.; Kojima, H.; Nakagawa, H.; and Tsuchiya, T. 2019. Finding Minimum Locating Arrays Using a CSP Solver.
ArXiv:1904.07480. **[C2, C8]**

Konishi, T.; Kojima, H.; Nakagawa, H.; and Tsuchiya, T. 2020. Using Simulated Annealing for Locating Array
Construction. *Information and Software Technology*, 126: 106346. **[C1]**

Torres-Jimenez, J.; and Rodriguez-Tello, E. 2012. New Bounds for Binary Covering Arrays Using Simulated Annealing.
*Information Sciences*, 185: 137–152. **[verify: title, volume and pages not checked; the lookup was blocked from the
cloud environment]**

---

## Changes from the accepted version

Every change below corrects a citation or removes an unsourced statement. Sources: `docs/LITERATURE_CHECK.md`
section 12, checked against Crossref and arXiv on 2026-11-05.

| id | where | accepted text | corrected text | why |
|---|---|---|---|---|
| C1 | Background; references | "Konishi et al. 2019a"; reference: ArXiv:1909.13090 | "Konishi et al. 2020"; *Information and Software Technology* 126: 106346 | Published journal version (DOI 10.1016/j.infsof.2020.106346). |
| C2 | Background; references | "Konishi et al. 2019b" | "Konishi et al. 2019" | With the SA paper now dated 2020, the "a/b" suffixes are no longer needed. |
| C3 | Stage 2 | "Published annealing work reports difficulty beyond pairwise strength, so I expect the cost function and the moves to need new ideas here." | "The number of interactions to cover and separate grows quickly with the strength, so I expect the cost function and the moves to need new ideas here." | No source for "published annealing work reports difficulty" could be found in the literature notes. The new sentence is a reason, not a claim about the literature. |
| C4 | References | Colbourn & McClary: "15(1)." | "15(1): 17–48." | Page numbers (Crossref). |
| C5 | References | Garvin et al.: no volume or pages | "16(1): 61–102" | Crossref. |
| C6 | References | "Constrained Detecting Arrays." | Full title | arXiv page. |
| C7 | References | Jin & Tsuchiya: "170." | "170: 110771." | Article number (Crossref). |
| C8 | References | Konishi CSP paper: "Konishi, T.; Nakagawa, H.; Kojima, H.; and Tsuchiya, T." | "Konishi, T.; Kojima, H.; Nakagawa, H.; and Tsuchiya, T." | Author order on the arXiv page. |

**Not changed, and worth deciding with the mentor** (these would add results obtained after acceptance):
- Discussion: "A first, immediate step is to run multiple seeds to see whether the 29-test result repeats." This has
  since been done: later searches found 30, 30 and 30 (PROJECT_NOTES item 65), and the proven lower bound is 16
  (items 71, 72).
- Discussion: "enumeration cannot reach standard benchmarks, and the next step is a SAT or SMT solver". Stage 1 has
  since been done (items 17, 56, 59, 60).
- "I have not yet surveyed machine-learning approaches to fault localization". A small search was done (item 50,
  LITERATURE_CHECK section 9). It is still not a survey, so the sentence remains true.
- The real-program finding (RQ5, items 75 to 82) is not mentioned.
