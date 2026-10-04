# Literature check: locating arrays, constraints, and metaheuristics (2026-10-04)

Status: second pass. The core papers below were read in full text via a web
fetch tool, which returns a model-processed rendering of the text, so quoted
wording must be checked against the PDF before it is quoted in a paper.
Items still marked [verify] have not been confirmed. Web search is not
exhaustive; absence of a result here is not proof that no work exists.

## 1. Bottom line

1. **The structural ceiling is established theory.** Jin & Tsuchiya define
   distinguishability for constrained systems (Definition 1: two sets of valid
   interactions are distinguishable iff some array of valid tests gives them
   different covering-test sets; Lemma 1: iff a valid test covers some
   interaction in one set and none in the other). Their constrained locating
   arrays (CLAs) exempt indistinguishable pairs, and they prove a CLA always
   exists with or without constraints (Theorem 3), whereas an ordinary locating
   array may not. Their experiments also report which interaction pairs are
   indistinguishable per benchmark.
2. **This project's `ceiling` is the single-fault (d=1), t=2 instance of that
   concept.** It counts interactions that are distinguishable from every other
   valid interaction. The "5 ambiguous pairs" left at the ceiling in
   `model_high_constraints.json` are indistinguishable pairs in their sense.
   The project's value is as a reported metric (localized versus achievable)
   and as a controlled experiment, not as a new phenomenon.
3. **The SA objective is also prior art, for the unconstrained case.** Konishi
   et al. use SA with cost = weight * (uncovered t-way interactions) +
   (interactions with a covering-row set identical to another's), a targeted
   neighborhood, and a binary-search wrapper over array size. They list
   constrained locating arrays as future work.
4. **Still apparently open (hypothesis, needs a deeper search):** a
   metaheuristic (SA/GA) for constrained locating arrays with constraint
   handling inside the search. The 2023 LocAG paper also defers the
   constrained case.

## 2. What each source establishes

| Work | Established | Not established / [verify] |
|---|---|---|
| Colbourn & McClary, "Locating and detecting arrays for interaction faults," J. Comb. Optim. 15(1), 2008 | Defines locating and detecting arrays; existence conditions; asymptotic size bounds | Abstract only |
| Jin & Tsuchiya, "Constrained locating arrays for combinatorial interaction testing," J. Systems and Software 170 (2020); arXiv 1801.06041 | Valid tests via constraint predicate; t-CCA; Definition 1 and Lemma 1 (distinguishability); four CLA variants ((d,t), (d-bar,t), (d,t-bar), (d-bar,t-bar); bars mean "at most"), all requiring separation only of distinguishable pairs; Theorem 2 (CLAs reduce to ordinary locating arrays without constraints); Theorem 3 (CLA always exists). Algorithm 1 builds a (t+1)-way constrained covering array (CIT-BACH tool) then removes redundant rows while preserving the CLA conditions; an SMT algorithm (Yices) shrinks N until it fails or times out at one hour. 30 benchmarks (CitLab synthetic 1-5; literature 6-25; real-world Apache, Bugzilla, GCC, Spins, Spinv 26-30); 3-199 factors; 36 to 82,770 valid 2-way interactions; only t=2 and d=1 evaluated; arrays of 5-361 tests; heuristic mostly under a second, up to about 3,350 s on the largest; SMT often times out. They list indistinguishable pairs per benchmark. Stated limits: deletion order affects size; no optimality guarantee; a 3-way CCA may not contain any optimal CLA | No explicit upper bound on the locatable fraction (the paper gives the existence result instead); exact figures should be checked in the PDF tables |
| Jin, Shi & Tsuchiya, "Constrained detecting arrays" (SAC 2020; arXiv 2110.06449) | Detecting-array analogue with a masking concept; satisfiability-based and two-step heuristic algorithms; 27 benchmarks | Journal venue of the extended version [verify] |
| Konishi et al., "Finding minimum locating arrays using a CSP solver," arXiv 1904.07480 (2019) | Exact CSP formulation for minimum (1-bar,t)-locating arrays; new minimum arrays and minimality proofs | Unconstrained-array scope; confirm there is no forbidden-combination handling [verify] |
| Konishi, Kojima, Nakagawa & Tsuchiya, "Using simulated annealing for locating array construction," arXiv 1909.13090 (authors' repository reports Information and Software Technology 2020 [verify venue]) | Random initial array; targeted neighborhood (overwrite a random row with a chosen uncovered interaction, or alter one factor value in a row covering an indistinct interaction, or overwrite a row not covering it); multiplicative cooling r = 0.999; always accept non-worsening moves, otherwise accept with probability exp(-delta/T); binary search plus a decrementing phase over array size; 35 instances from the CIT literature (2^3 up to 2^189 3^10); matched or beat known sizes on small cases, 333 vs 421 rows on one real-world case (about 21% smaller; the paper text also gives 293 vs 421, treat as [verify]); t=3 succeeded on only 11 of 35 instances; stated limits: t>2 and memory. Conclusion lists constrained locating arrays as future work. Code: SA4LA (Java) | Parameter tuning left open |
| Dougherty, Green & Kim, "Faster Location in Combinatorial Interaction Testing," arXiv 2310.07448 (2023) | LocAG: covering array first, then partitioning plus a genetic algorithm; first non-trivial d=2, t>=2 results; explicitly unconstrained | Preprint status [verify] |
| Wu, Nie, Petke, Jia & Harman, "A Survey of Constrained Combinatorial Testing," arXiv 1908.02480 | Constraint-handling taxonomy for covering arrays (remodel, avoid, post-process, transfer); most generators lacked constraint support | Little on locating arrays under constraints |
| Torres-Jimenez & Rodriguez-Tello, SA for strength-three covering arrays, Information Sciences 2012 | In the project files; SA for covering arrays | Covering only |

Found but not read: Yilmaz, Cohen & Porter on covering arrays for fault
characterization (IEEE TSE); a Lanus (ASU) dissertation on interaction testing
and fault location; "Locating arrays with mixed alphabet sizes" (arXiv
2001.11712). Recalled from memory and NOT found by the searches: Garvin, Cohen
& Dwyer on meta-heuristic search for constrained interaction testing. Do not
cite until located.

## 3. What this means for the claims the paper can make

Safe to say, with citation:
- Locating arrays and constrained locating arrays are established, with a
  formal distinguishability concept and an existence guarantee.
- Constraints can make some interactions indistinguishable; the ceiling in
  this project's experiments is an instance of that concept.
- SA has been applied to unconstrained locating array construction.

Not safe:
- Any claim that the ceiling, the "ambiguous pairs at the ceiling," or a
  locating-aware SA objective is new.
- Any claim about suite-size quality of the greedy locating heuristic. It has
  not been compared with the CLA heuristic, the SMT approach, or SA4LA on
  shared benchmarks.

Where a contribution could still be (hypotheses to test, not claims):
- A metaheuristic for constrained locating arrays with constraint handling in
  the search (repair, penalty, or sampling only valid configurations), measured
  against the distinguishability ceiling and against the CLA heuristic.
- A controlled study of how constraint structure (count of rules, and chaining
  of forbidden rules) determines the fraction of interactions that are
  distinguishable, and how suite size and generation cost respond. Their
  benchmarks vary many things at once; a family that varies only the
  constraints would isolate the effect. Check first whether this is already
  reported in their per-benchmark counts.
- Models beyond the deterministic single-fault, t=2 setting: t=3 (where SA
  reportedly struggles), d=2, nondeterministic outcomes, and statistical or
  AI-assisted ranking.

## 4. Gaps in this project exposed by the literature

- Seven small hand-built models versus 30-35 standard instances (up to about
  200 factors). Standard instances are needed; CitLab is the named source for
  the first five of the CLA benchmarks, and the larger ones are cited from the
  literature. Availability and format are not yet checked.
- The project's greedy builds a suite forward from nothing; the published CLA
  heuristic starts from a (t+1)-way covering array and deletes rows. These are
  different strategies; their relative size quality is unmeasured.
- The project enumerates all valid configurations, which does not scale to
  199-factor instances. A solver or sampling-based approach would be required
  to run on the large benchmarks.
- No t=3 measurements yet.

## 5. Recommended next steps, in order

1. Fix the project's documents so they state the correct novelty status (done
   in the repository notes alongside this note).
2. Locate the benchmark instances and their file format (CitLab and the
   literature sources) and add a loader.
3. Run a targeted search for post-2023 work on constrained locating arrays and
   for the Garvin et al. work.
4. Decide V0.3: a constrained SA over valid configurations, using the
   Konishi neighborhood adapted so that every candidate row is valid, compared
   with the greedy heuristic and, where possible, with the published CLA sizes.
5. Consider renaming the `ceiling` column or documenting it as "distinguishable
   interactions (Jin & Tsuchiya Def. 1, d=1)" so readers recognize it.

## Sources

- [Colbourn & McClary 2008, J. Comb. Optim.](https://link.springer.com/article/10.1007/s10878-007-9082-4)
- [Jin & Tsuchiya 2020, J. Syst. Softw. 170](https://www.sciencedirect.com/science/article/pii/S0164121220301874) / [arXiv 1801.06041](https://arxiv.org/abs/1801.06041)
- [Jin, Shi & Tsuchiya, Constrained Detecting Arrays, arXiv 2110.06449](https://arxiv.org/abs/2110.06449)
- [Konishi et al., Finding minimum locating arrays using a CSP solver, arXiv 1904.07480](https://arxiv.org/abs/1904.07480)
- [Konishi et al., Using simulated annealing for locating array construction, arXiv 1909.13090](https://arxiv.org/abs/1909.13090)
- [SA4LA repository](https://github.com/tatsuhirotsuchiya/SA4LA)
- [Dougherty, Green & Kim, Faster Location in Combinatorial Interaction Testing, arXiv 2310.07448](https://arxiv.org/abs/2310.07448)
- [Wu et al., A Survey of Constrained Combinatorial Testing, arXiv 1908.02480](https://arxiv.org/abs/1908.02480)
- [Locating arrays with mixed alphabet sizes, arXiv 2001.11712](https://arxiv.org/pdf/2001.11712)
- [Yilmaz, Cohen & Porter, fault characterization (IEEE TSE), found not read](https://www.cs.umd.edu/~aporter/Docs/tse-0198-0705-2c.pdf)
