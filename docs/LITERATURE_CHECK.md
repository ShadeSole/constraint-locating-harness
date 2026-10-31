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

## 6. Addendum: targeted search for Garvin et al. and recent work (2026-10-16, live session; search only, nothing read in full)
Web search via a search tool returns excerpts only; absence of a result is not proof of absence.
- **Garvin, Cohen & Dwyer located.** "An improved meta-heuristic search for constrained interaction testing" (1st International Symposium on Search Based Software Engineering, 2009; IEEE Xplore, entry found) and the journal follow-up "Evaluating improvements to a meta-heuristic search for constrained interaction testing", Empirical Software Engineering (Springer, DOI 10.1007/s10664-010-9135-7; volume and year [verify]). They are about constrained COVERING arrays by meta-heuristic search. So a metaheuristic with constraint handling is prior art for covering arrays; it can no longer be listed as "recalled but not found". Not read in full: what constraint-handling they use and whether their search is simulated annealing [verify].
- **Konishi et al. SA for locating arrays** is also published in Information and Software Technology (ScienceDirect, pii S0950584920301130); the venue line in section 2 can be confirmed from that entry [verify volume/year].
- **Found, not read:** "Lower Bounds and Construction of Detecting Arrays" (tabu search, ResearchGate listing); "Complete, Sound, and Scalable Identification of Minimal Failure[-inducing combinations]" (ACM DL 10.1145/3811916, title truncated in the listing); "Fault localization for automatic train operation based on the adaptive error locating array algorithm" (Scientific Reports, 2024); BayesFLo (arXiv 2403.08079). Their relevance to constrained locating arrays is unchecked.
- **Not found in these three searches:** a post-2023 paper constructing constrained locating arrays by simulated annealing or another metaheuristic. This is a weak negative (three queries, excerpts only). Do not write "no prior work"; write "we did not find".
- Consequence for the hypothesis in section 3: "constraint handling inside a metaheuristic" exists for covering arrays (Garvin et al.), and SA exists for unconstrained locating arrays (Konishi et al.). The remaining possible gap is the combination, and the measurement of covering-versus-locating overhead and of the ceiling on constrained benchmarks. Still a hypothesis.

## 7. Addendum: Jin & Tsuchiya Table 1 read in full text (2026-10-17, cloud session; PDF converted to markdown, check against the PDF before quoting)
Experiments use (1bar,2)-CLAs. Table 1 sizes for the heuristic (min to max over 10 runs): Spins 49 to 53, Bugzilla 41 to 48, Spinv 91 to 97, Apache 85 to 89, GCC 61 to 68; SMT timed out on all five. Comparison with this repo's results is in PROJECT_NOTES 'Comparison with published CLA sizes'. Not yet read: the Konishi et al. SA paper's tables (downloaded, not analysed).

## 8. Addendum: tools and benchmark sources (2026-10-27, live session)
- Jin & Tsuchiya 2020 Table 1 checked against the arXiv PDF; see PROJECT_NOTES 'Item 46 resolved in the live session'.
- SA4LA (github.com/tatsuhirotsuchiya/SA4LA; Konishi, Kojima, Nakagawa, Tsuchiya, Inf. Softw. Technol. 126, 2020, 106346): input is strength and value counts only; unconstrained locating arrays. Not run.
- Benchmark archive: Jia, Cohen, Harman, Petke, "Combinatorial Interaction Testing (CIT) Benchmarks", Zenodo, DOI 10.5281/zenodo.581657 (contains the 20 Segall et al. real-world models). Not downloaded (network policy).
- Not found: a public implementation of the Jin & Tsuchiya CLA heuristic; a source for Aircraft, Car, Movie, Medicitries, Medicitries_small.

## 9. Addendum: machine learning / LLM work near covering arrays, locating arrays and failure-inducing interactions (research plan item 50, 2026-10-27, cloud run, not reproduced by the author)
Method: three web searches (excerpts only), then each source below was opened (landing page or abstract page, not the full text). Entries are limited to those pages' contents; venue is given only where the page stated it. Absence of a result is not proof of absence; "we did not find" is the strongest claim available.

| Title | Authors | Year | Venue | One line (from the abstract page) |
|---|---|---|---|---|
| Combinatorial Test Design Model Creation using Large Language Models | Furman, Farchi, Gildein, Hicks, Rawlins | 2025 | IEEE ICST (workshops; DOI 10.1109/ICSTW64639.2025.10962528) | Initial experience using LLMs to generate a base combinatorial test design model (parameters and values); it does not construct arrays. |
| GALP: A hybrid artificial intelligence algorithm for generating covering array | Esfandyari, Rafe | 2021 | Soft Computing 25(11), 7673-7689 | Combines a genetic algorithm with a particle swarm variant to generate covering arrays; this is metaheuristic search, not a learned model. |
| Combinatorial Testing for Deep Learning Systems | Ma, Zhang, Xue, Li, Liu, Zhao, Wang | 2018 | arXiv 1806.07723 (venue not stated on the page) | Applies combinatorial coverage criteria to testing deep-learning systems; combinatorial testing OF ML, not ML used to build arrays. |
| ProphetFuzz: Fully Automated Prediction and Fuzzing of High-Risk Option Combinations with Only Documentation via Large Language Model | Wang, Zhou, Chen, Li, Miao | 2024 | arXiv 2409.00922 (related DOI 10.1145/3658644.3690231) | An LLM predicts which command-line option combinations are likely vulnerable, then fuzzes them; prediction of risky combinations, not localization of a failure-inducing one. |
| Isolating Failure-Inducing Combinations in Combinatorial Testing using Test Augmentation and Classification | Shakya, Xie, Li, Lei, Kacker, Kuhn | 2012 | IEEE ICST 2012 | Classification-tree analysis plus extra generated tests to isolate failure-inducing combinations. Older than 2018 and classical machine learning; listed as the closest "learned classifier" precedent. |

What the searches suggested but I did NOT open (so not claimed): a systematic mapping study (arXiv 2206.10210) whose excerpt says neural networks and reinforcement learning have been used for covering-array generation; a reinforcement-learning-guided simulated annealing attributed to Jia et al. in that excerpt. Both are leads to verify, not citations.

Reading across the table: of the sources opened, none builds locating arrays with a learned model and none uses ML or an LLM to localize failure-inducing interactions in the sense used here. That is "we did not find", from three queries and five opened pages. Interaction localization only; no source-code fault localization is covered.

## 10. Addendum: d = 2 and the (2bar, 2) versus (1bar, 3) observation (research plan item 65, 2026-10-30, live session; search excerpts plus one slide deck read)

Question: is a relation between (2bar, 2)- and (1bar, 3)-locating arrays (constrained or not) known? Observed in item 65 on
the example models (equal minima, arrays of one kind pass the other's check), not general on random models.

Searched (Exa and Tavily; Firecrawl returned HTTP 403): "(2,2) locating array strength 3 relation", "locating array d = 2
t = 2 versus t = 3", Colbourn McClary detecting array. Read in full: Colbourn, "Fault Location and Resolvable Set Systems"
(slides, ACA 2015, pages.mtu.edu/~tonchev/Colbourn.pdf): defines (d, t)-locating and detecting arrays; for d = 2 it lists
the conditions (no two sets equal, no set equal to a union of two others, unions of two distinct pairs differ); no
relation to strength t + 1 is stated there. Excerpts only: Dougherty, Green & Kim 2023 (arXiv 2310.07448) say
constructions are "only well studied for d = 1" and claim the first non-trivial d = 2 arrays (unconstrained); Shi, Tang
& Yin 2012 relate optimal detecting arrays to super-simple orthogonal arrays; Martinez, Moura, Panario & Stevens 2009
(error locating arrays, built from covering arrays).

Result: no source found that states the relation. Colbourn & McClary 2008, the most likely place, is still read only as
an abstract. So: "we did not find it", not "it is new". Also not found: any constrained (2bar, t) locating array
construction or minimum-size result; Jin & Tsuchiya 2020 define the (dbar, t) variants but their Table 1 results are
for d = 1 (section 7 above).

## 11. Addendum: prior results relating strength and number of faults (research plan item 66, 2026-10-31, live session; excerpts only)

- Colbourn & McClary, "Locating and Detecting Arrays for Interaction Faults" (Dagstuhl Seminar Proceedings 09281;
  journal version J. Comb. Optim. 15(1), 2008). Excerpts read: Theorem 8.5, "Every CA(N; t + d, k, v) with d < v is a
  (d, t)-detecting array" (mixed-level version for d < s1 <= ... <= sk); Theorem 8.1, every (d, t)-detecting array with
  all sk = d + 1 is a (t + 1)-covering array; a (1, t-hat)-locating array is a (1, t)-locating array and a t-covering
  array. Unconstrained throughout. The item 66 conjecture ((1bar, 3)-locating implies (2bar, 2)-locating, with
  constraints) is not this theorem: it would follow from strength t + d = 4 coverage, not from (1bar, 3) location.
- Lanus et al. (NSF PAR 10118967, PSCR): summarise that known general methods build (d, t)-locating arrays from covering
  arrays of strength t + d, and that every (d, t)-detecting array is (dbar, t)- and (d, t)-locating.
- Shi, Tang & Yin, "Optimal locating arrays for at most two faults", Science China Mathematics, 2011 (title and venue
  only): unconstrained (2bar, t) results exist and must be cited for any d = 2 claim.
- Konishi et al. 2019 (arXiv 1904.07480), Proposition 2.4: an array is (1bar, t)-locating iff (1, t)-locating and
  t-covering.

Not found: a statement that (1bar, t + 1)-locating implies (2bar, t)-locating, constrained or not. Colbourn & McClary
was read only in excerpts, so this is "not found", not "new".

