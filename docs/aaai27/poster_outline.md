# AAAI-27 Undergraduate Consortium poster: outline

**Status.** Draft outline, 2026-11-11; real-bug case study added 2026-11-12.
- **Poster session.** Thursday 2027-02-18 (tentative).
- **Still to come.** Size, orientation and template arrive with AAAI's poster guidance in the first week of December.
  This outline assumes a landscape poster in three columns and must be adjusted to that guidance.
- **Mentor check.** Confirm with the mentor that the poster may show results obtained after acceptance.

**Rules for every number on the poster.**
- It comes from `docs/PROJECT_NOTES.md` (item named).
- It is labelled *reproduced locally* (re-run on the author's machine) or *cloud run* (not yet re-run locally).
- Novelty wording stays "we did not find", never "first" or "novel".

---

## Header (full width)

- **Title:** Constraint-Aware Test Suites That Locate Faults: Simulated Annealing for Configurable Software
  (the accepted title; or a shorter poster title such as "Which settings broke it? Test suites that locate faults").
- Author, affiliation, logos: as in the camera-ready.
- **Take-home banner, one or two lines:**
  > A 19-test suite pinpointed the two settings behind a real, fixed Python bug, out of 3,456 configurations. Across
  > hundreds of generated bugs, localization worked whenever a bug fit its model and safely said "doesn't fit"
  > otherwise. How often real bugs fit is the open question.

---

## Column 1: Problem and question

**1. The problem** (3 short bullets and one picture)
- Configurable software fails when certain *combinations* of settings meet.
- A covering test suite exposes the failure but does not say which combination caused it.
- Some combinations are forbidden. Constraints can make two combinations impossible to tell apart, however many valid
  tests are run (Jin & Tsuchiya 2020).

**Figure 1: toy example.** Four tests over 3 options, with fail/pass marks.
- Show how the pattern of failing tests points to one pair (locating) or to several (ambiguous).
- Hand-drawn, with no measured numbers in it.

**2. Research question** (from the statement)
> How can we efficiently generate small, constraint-aware test suites that cover every feasible interaction and also
> distinguish every interaction that can be distinguished?

**3. Why this is AI**
- Search and optimization (simulated annealing) combined with constraint reasoning (SAT/SMT).
- The targets include machine-learning pipelines with many interacting settings.

**4. What is known** (one line each)
- Locating arrays: Colbourn & McClary 2008.
- Constrained locating arrays and distinguishability: Jin & Tsuchiya 2020.
- Annealing for *unconstrained* locating arrays: Konishi et al. 2020.
- What remains: in our searches we did not find annealing applied to *constrained* locating arrays.

---

## Column 2: Approach and benchmark results

**5. Method** (Figure 2: a diagram with 4 boxes)
- **Model:** options plus forbidden combinations.
- **Search:** simulated annealing over suites of *valid* tests only, with validity kept by a rule check and an SMT
  (Z3) fallback.
- **Cost:** uncovered combinations plus avoidable collisions. Zero means every combination that can be told apart is
  told apart.
- **Shrink loop:** remove one test at a time.
- **Checks:** an independent verifier on every suite, and exact minima by MaxSAT/SAT on small models.

**6. What locating costs.** RQ1, item 61 (cloud run).
- A locating suite needed about **1.6 to 2.1 times** the tests of a covering suite on five constrained benchmark
  systems, with the same search and budget.
- Possible figure: paired bars of covering against locating size per system.

**7. Against the published method.** RQ3, items 60 and 83.

| system | published heuristic, best | our search, cloud run (10 seeds) | our search, reproduced locally (seed 0) |
|---|---|---|---|
| apache | 85 | 67 to 69 | 73 |
| gcc | 61 | 54 to 55 | 60 |

- One line under the table: "Same time budget as the published average, different hardware. The search stops at a
  time cap, so the margin depends on the machine."

**8. Exact answers on small models.** Items 63 and 65 (reproduced locally).
- The search reached the proven minimum in 27 of 28 small-model cases.
- Locating two faults roughly doubles the minimum test count on these models.

---

## Column 3: Real programs (the headline) and next steps

**9. Case study: two real, fixed CPython bugs.** Item 85 (cloud run; not yet re-run locally). Put this at the top of
the column: it is the demo.

*How it was tested:*
- For each bug we took the module source just before and just after the CPython developers' fix (a one- or two-line
  change).
- The fixed version is the reference; the buggy version is the program under test.
- Ground truth is every configuration where the two behave differently.

**Figure 5 (demo figure): configparser gh-130941**, "Fix configparser parsing values with `allow_no_value` and
`interpolation` set" (fixed April 2025).
- 384 of 3,456 configurations fail, using the input from the fix's own regression test.

| suite | result |
|---|---|
| covering only (9 tests) | missed: no test failed |
| one-fault locating (19 tests) | **caught it and named `allow_no_value = True` + `interpolation = extended`, the two settings in the official bug report** |
| two-fault locating (49 tests) | caught it; "no single explanation fits" |

- Small print: "Our original inputs never triggered this bug: a suite only finds bugs its inputs exercise. In our test
  the failure also needs '=' as a separator, because of how the regression input is written."

**textwrap gh-139065**, "Fix trailing space before long word" (fixed October 2025): the honest limit, as one line or
a small inset.
- Our original inputs triggered it: 224 of 4,352 configurations fail.
- The covering (12 tests) and one-fault (21 tests) suites missed it.
- The two-fault suite (58 tests) detected it but could not name a settings-only cause. None exists: the bug also
  depends on where line lengths land in the text.

**Message:** when a bug is a combination of settings, a small locating suite can name it. When it also depends on the
input, larger suites detect it but cannot name it.

**10. Generated bugs in two real programs.** RQ5, items 75 and 76 (reproduced locally).
- **Programs:** two Python standard-library modules, textwrap and configparser.
- **Bugs:** every small automatic code mutation of their main classes, 131 and 258 in all. 83 and 110 of them fail
  only in some configurations.
- **Ground truth:** each mutant was run on every valid configuration, so the exact set of failing settings is known.

**Figure 3: shape of the generated faults** (stacked bar per program; item 75 and 76 shape tables)

| fault is exactly... | textwrap (83) | configparser (110) |
|---|---|---|
| one faulty pair | 0 | 1 |
| two faulty pairs | 11 | 47 |
| needs more than two pairs, or wider combinations | 72 | 62 |

- **Message:** these generated faults rarely match the "one faulty pair" model. They come from mutating core code,
  so they may be wider than typical real configuration bugs. How often real bugs match is the open question.

**Figure 4 (main figure): correct diagnoses and wrong causes named**

| suite (tests: textwrap / configparser) | textwrap correct / wrong cause | configparser correct / wrong cause |
|---|---|---|
| covering only (12 / 9) | 0 / 24 | 0 / 56 |
| one-fault locating (21 / 19) | 0 / 5 | 1 / 2 |
| two-fault locating (58 / 49) | **11 / 3** | **48 / 0** |
| random suites of the same size, mean of 200 (item 78) | 10.2 / 3.9 | 43.2 / 3.9 |

- The rest were reported as "no single explanation fits", or no test failed.
- Present this as a grouped bar chart.

**11. What it means** (three bullets)
- Localization worked whenever a bug fit the suite's model. For the bugs that did not fit, the suites mostly said
  "no single explanation fits", the safe answer, and the one-fault suite rarely named a wrong cause.
- Most of the gain comes from more tests plus a decoder that allows two faulty pairs. Random suites of the same size
  come close on average; there is no significant difference (items 78 and 81).
- The two-fault construction reached the best result on every one of the 6 suites built, while 50% and 84% of the
  random suites fell short. It also has a guarantee: for a single wider fault it never names an unrelated cause, the
  constrained version of Colbourn & McClary's Lemma 7.1 (items 73 and 74).

**12. Long-term plan** (the statement's four stages, with status)

| stage | status |
|---|---|
| 1. Scale with a SAT/SMT solver | done: runs on the standard benchmarks |
| 2. Three-way and multiple faults | started: exact minima, real-program study |
| 3. Noisy (flaky) outcomes | started: simulation |
| 4. Learning to rank suspects | planned |

**13. Honest limits** (small font)
- Two programs, with mutation faults. The two historical bugs are anecdotes, not a rate, and were picked because
  their titles suggested setting interactions.
- One seed per benchmark row.
- The minimum is unknown on mid-sized models: on the spins-derived model it lies between 16 and 29 (items 71, 72).

**14. Reproducibility** (one line, plus a link or QR code if the repository is made public)
- Re-run on the author's machine with every exact and RQ5 row matching: `quick` 48 of 48, `rq5` 40 of 40, `sim`
  all rows (items 80 and 83).

**15. References** (4 to 6, small font)
- Colbourn & McClary 2008; Jin & Tsuchiya 2020; Konishi et al. 2020; Garvin, Cohen & Dwyer 2011.
- CPython issues gh-130941 and gh-139065 (python/cpython on GitHub; fix commits c35c7353eb and 1c598e0436).

---

## Notes for building it

- **Visual priority:** banner, then Figure 5 (the real-bug case study), then Figure 4, then Figure 3. A visitor should
  get the message from those alone.
- **Figure 5** comes from `docs/item85/cp_regression_evaluation.json` and `docs/item85/cp_regression.jsonl`. The named
  pair is recorded in PROJECT_NOTES item 85.
- **Before printing:** re-run `reproduce.py realbug` (item 86) on the author's machine, so the case study can
  carry the "reproduced locally" label too.
- **Text:** keep it under about 500 words. The tables above are the content, not the final layout; charts replace most
  of them.
- **Figures 3 and 4** can be generated from `docs/item75/evaluation.json`, `docs/item76/evaluation.json`,
  `docs/item75/shapes.txt`, `docs/item76/shapes.txt` and `docs/item7{5,6}/stats.json`.
- **Talk (5 to 6 minutes, Wed 2027-02-17):** a title slide, then one slide each for sections 1, 2, 9 (the case
  study, the strongest slide), 10 with 11, and 12.
