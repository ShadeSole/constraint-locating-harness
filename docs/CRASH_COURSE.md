# Crash course: what this project is and what has been done

Read this top to bottom once, then read only the newest entries in the Run log.
Numbers here come from `docs/PROJECT_NOTES.md` or from a command that was run;
anything not measured says "not measured". Every result is labeled with where it
came from: "reproduced locally" (the author ran it) or "cloud run" (an AI session
ran it and the author has not repeated it yet).

## 1. The problem in plain words

Software with many settings can fail only when a particular combination of
settings occurs together, for example "encryption = on" together with
"cache = off". A single option is rarely the culprit.

- **Interaction:** a specific pair (or triple) of option values, such as A=1 and B=0.
- **t-way coverage (covering array):** a test suite in which every t-way interaction
  appears in at least one test. This finds failures but does not say which
  interaction caused one.
- **Locating array:** a suite designed so that the *pattern* of passing and failing
  tests identifies the faulty interaction. Each interaction has a different set of
  tests that contain it, so one fault leaves a distinct fingerprint.
- **Constraints:** real systems forbid some combinations. A test must be valid, so
  the suite can only use valid configurations.
- **Distinguishable interactions:** with constraints, some interactions occur in
  exactly the same valid tests, so no valid suite can tell them apart. Jin and
  Tsuchiya (2020) define this precisely.
- **The ceiling (this project's metric):** the number of interactions that *can* be
  told apart from every other one. It is the best any suite can do. It is known
  theory (the d=1, t=2 case of Jin and Tsuchiya's distinguishability), not a new
  idea.

## 2. What has been built

1. **Model and enumeration:** parameters plus forbidden partial assignments; the
   code lists every valid configuration and every feasible interaction.
2. **Greedy suites:** a covering heuristic and a locating heuristic. Greedy is a
   baseline, not optimal.
3. **Fault injection:** inject one interaction as the fault, run the suite, and check
   whether the pass/fail pattern points to it uniquely. This is a simulation of
   *interaction* localization; it is separate from finding a bug in source code.
4. **Simulated annealing (SA), step by step:**
   - *State:* a list of N valid configurations, so every test is valid by construction.
   - *Cost:* uncovered interactions plus avoidable collisions (two covered interactions
     with identical covering tests, when some valid test could separate them).
     Cost zero means full coverage and the ceiling reached.
   - *Move:* replace one test, randomly or with a targeted choice that fixes an
     uncovered or colliding interaction.
   - *Acceptance:* worse moves are accepted with probability exp(-delta/T); the
     temperature T falls over the run, so early moves explore and late moves settle.
   - *Shrinking:* find a solution at size N, then try N-1, and so on. A size "fails"
     only after a fixed budget of restarts and moves, so results repeat on any
     machine. A failure is not a proof that the size is impossible.
   - *Warm start:* start the next smaller size from the previous solution minus its
     least useful test.
   - *Multi-seed:* repeat the whole search with different seeds to see the spread,
     because one seed is one data point.
5. **Exact minima on small models:** brute-force search proves the true smallest suite.
   The three small hand-built models have minimum sizes 9, 9 and 8 tests.

## 3. Results so far (see docs/PROJECT_NOTES.md for the full tables)

| Result | Value | Origin |
|---|---|---|
| Automated tests | 110 pass | reproduced locally |
| Spins-derived model | 9 parameters, 13 rules, 978 valid configurations, 239 feasible interactions, ceiling 229 | PROJECT_NOTES |
| Greedy locating suite on that model | 32 tests | PROJECT_NOTES |
| SA, seed 0, 6,000 moves per run | 30 tests, 60,556 moves | reproduced locally |
| SA, seed 0, 20,000 moves per run | 29 tests; 28 not found within 100,000 moves | reproduced locally |
| Multi-seed spread on that model, cold search, 10 seeds | final sizes 30 (4 seeds), 31 (5), 32 (1); median 31 | cloud run, not reproduced by the author |
| Same, warm_extra with equal runs per size, 10 seeds | final sizes 30 (8 seeds), 31 (2); median 30 | cloud run, not reproduced by the author |

How to read this: SA found a smaller suite than greedy on this one model with one seed.
That is encouraging but is not yet evidence of a general advantage.

## 4. What is established and what might be new

- **Published (do not claim):** locating arrays (Colbourn and McClary 2008);
  constrained locating arrays and distinguishability (Jin and Tsuchiya 2020; Jin's
  2022 dissertation); SA for unconstrained locating arrays (Konishi et al. 2019).
- **Possibly open (a hypothesis, not a claim):** SA for *constrained* locating arrays
  that searches only valid configurations and is scored against the ceiling. The
  literature searches so far were not exhaustive.
- **Not yet done:** comparison with published sizes on shared benchmarks, a
  solver-based approach for large models, multiple faults, noisy outcomes.

## 5. Be skeptical of

- One seed or one model is an anecdote. Ask for the spread.
- "Failed at size N" means "failed within this budget", not "impossible".
- The derived spins model is a projection of the real benchmark, not the benchmark.
- Cloud-run numbers are unverified until the author repeats them.

## 6. Self-check questions (answer these before writing about the work)

1. Why does a covering array not tell you which interaction failed?
2. Why can two interactions be impossible to tell apart under constraints?
3. What does cost zero mean in the SA, and why is it a clean stopping rule?
4. Why is a failure at size N not a proof that N is too small?
5. What would you need to show before calling SA for constrained locating arrays new?

## 7. Run log (the automated routine appends below; newest last)

Format for each entry: date, plan item, what was done, command run, key numbers with
their origin label, what to be skeptical of, anything left under "Open questions" or
"Needs your decision" in docs/PROJECT_NOTES.md.


- 2026-10-13, plan item 2: ran greedy and SA (targeted, 3x3000 moves, seeds 0-2) on the
  seven small example models with `scripts/item2_sizes.py`. Cloud run, not reproduced by
  the author. SA ended 1 to 2 tests below greedy locating on all seven, always at the
  ceiling; model_8param.json varied by seed (11, 12, 11). Be skeptical: tiny hand-built
  models, three seeds, no CASA models run. Logged in PROJECT_NOTES "Open questions".

- 2026-10-13, plan item 3: kept the 5 binary parameters fixed, added 0 to 10 random pair-forbidden
  rules in nested order over 20 shuffle seeds (`scripts/item3_constraint_family.py`), and measured
  ceiling / feasible. Cloud run, not reproduced by the author. All interactions are distinguishable at
  0 and 1 rules; at 3 rules the median fraction is 0.871 with a range of 0.361 to 0.946, so which
  rules you add matters, not just how many. Be skeptical: later rows keep only orderings that still
  have a valid configuration, and the 8+ rule rows have under 3 valid configurations on average.

- 2026-10-13, plan item 4: repeated the greedy-vs-SA comparison at strength 3 on the seven small models
  (`scripts/item4_strength3.py`, seeds 0-2). Cloud run, not reproduced by the author. All suites reached the
  ceiling; SA was 0 to 2 tests below greedy and identical across seeds. The ceiling fraction drops at t = 3 on
  five models (for example model.json 60/68). Be skeptical: no exact minimum at t = 3, SA equal to greedy on
  three models, tiny hand-built models only.

- 2026-10-13, plan item 5: added `warm_extra` (warm run as an additional run, cold restarts untouched) and
  compared cold, warm-replaces-restart-0 and warm-extra on the spins-derived model, seeds 0-2
  (`scripts/item5_warm_compare.py`). Cloud run, not reproduced by the author. Smallest sizes: cold 30/31/32,
  warm 30/30/32, extra 30/31/30. Be skeptical: three seeds, one derived model, and extra gets one more run
  per size, so it is not a budget-matched comparison (cold with 6 restarts was not run).

- 2026-10-13, plan item 6: repeated the cold shrinking search on the spins-derived model for seeds 0-4
  (`scripts/item6_spread.py`, via `multi_seed_search`). Cloud run, not reproduced by the author. Final sizes
  30, 31, 32, 31, 30 (min 30, median 31, max 32); seed 0 gave 30 as the plan required. So the smallest suite
  found depends noticeably on the seed, which is why single-seed sizes should not be quoted alone. Be
  skeptical: five seeds, one derived model, "failed" means not found within budget. Seeds 5-9 are item 7.

- 2026-10-13, plan item 7: same cold search, seeds 5-9. Cloud run, not reproduced by the author. Final sizes
  31, 31, 30, 30, 31. Across seeds 0-9: 30 tests for 4 seeds, 31 for 5, 32 for 1 (median 31); none reached 29.
  Be skeptical: ten seeds on one derived model is a small sample, and "not reached" means not found within
  5 x 6000 moves per size.

- 2026-10-13, plan item 8: budget-matched warm start comparison on the spins-derived model, seeds 0-9: cold with
  6 restarts versus warm_extra with 5 (same number of runs per size). Cloud run, not reproduced by the author.
  Median final size 31 for cold and 30 for warm_extra; warm_extra was smaller on 4 seeds, equal on 6, larger on
  none. Cold with 6 restarts gave the same sizes as cold with 5, so the extra restart added nothing here.
  Be skeptical: ten seeds, one derived model, a one-test median difference with no significance test.

- 2026-10-13, plan item 9 (summary of items 6-8, plain language): The same search run with ten different random
  seeds does not always stop at the same suite size. On the spins-derived model the cold search ended at 30
  tests for four seeds, 31 for five and 32 for one, so quoting one seed's size would mislead. Giving the
  search a sixth restart changed nothing. Giving it one extra "warm" run (start from the previous solution with
  one test removed) (without removing any cold restart) ended at 30 for eight seeds and 31 for two, with about the same total
  number of moves. That points toward warm_extra helping, but it is a one-test median difference over ten seeds on
  one derived model with no significance test, so treat it as a lead to check, not a result. Cloud run, not
  reproduced by the author. Full table: PROJECT_NOTES, "Summary of research plan items 6 to 8".

- 2026-10-13, plan item 10: Z3 is a solver that can answer "is this combination allowed?" from the rules directly,
  instead of listing every combination first. Added it as an optional extra (the core stays standard library only)
  in `cla_harness/solver.py`. Cloud run, not reproduced by the author. On all 8 example models, Z3's yes/no for
  every possible configuration matched the existing enumeration; the new tests skip if Z3 is not installed.
  Nothing in the search uses Z3 yet. Be skeptical: the models are tiny, and this one-at-a-time check rebuilds the
  solver each call, so it is slow. Speed is item 13's job.

- 2026-10-13, plan item 11: Z3 can now list every valid configuration (it asks for one, forbids it, asks again) and
  draw seeded random valid ones. Cloud run, not reproduced by the author. On all 8 example models the list matched
  the existing enumeration exactly and every sample was valid. On these tiny models Z3 was slower than plain
  enumeration (single runs: for example 0.141 s versus 0.0001 s on model.json). Be skeptical: the point of Z3 is
  models too big to enumerate, which has not been tested yet, and the sampler is reproducible but not uniform.

- 2026-10-13, plan item 12: Z3 can now decide which pairs of settings can ever occur together by asking, for each
  pair, "does any allowed configuration contain both?" Cloud run, not reproduced by the author. On all 8 example
  models the result equals the existing enumeration exactly (for example 38 for model.json, 239 for the spins-
  derived model). Z3 was slower on these tiny models, though the gap narrowed on the largest. Be skeptical: the
  reason to use Z3 is models too big to enumerate, and none was tried yet.

- 2026-10-13, plan item 13: timed plain enumeration against Z3 for the three jobs from items 10 to 12 (check every
  configuration, list the valid ones, find the feasible pairs) on all 8 example models, 3 repeats each. Cloud run, not
  reproduced by the author. Z3 was slower in all 24 cells. The gap was smallest for finding feasible pairs, and on the
  largest example (the spins-derived model, 978 valid configurations) Z3 took 0.0525 s against 0.0299 s, about 1.8
  times slower. Be skeptical: all models are tiny, so this says nothing yet about models too big to enumerate; and
  the very large ratios in the one-at-a-time validity check come from rebuilding the solver on each call.

- 2026-10-13, plan item 14 (summary of items 10-13, plain language): Z3 is a program that can answer questions about
  the rules directly, without first writing down every allowed configuration. I added an optional Z3 module that
  answers three questions: is this configuration allowed, which configurations are allowed, and which pairs of settings
  can ever occur together. On all 8 example models its answers matched the old way exactly every time, which suggests
  the rules are translated correctly. It was slower than the old way on every model tried, because these models are
  tiny. Nothing in the search uses it yet: the search still lists all configurations first. The real test is a model
  too big to list, which has not been tried and is the next decision for you (item 15). Cloud run, not reproduced by
  the author. Full table: PROJECT_NOTES, "Summary of research plan items 10 to 13".

- 2026-10-13, plan item 15: the search scores a suite by counting interactions it misses and pairs of interactions it
  cannot tell apart although some allowed test could. That second part used a table built by listing every allowed
  configuration. I wrote a version that asks Z3 instead, one pair at a time, and remembers the answers. On all 8
  example models and 200 random suites each, it gave exactly the same score as the old way every time (1,600 of 1,600).
  It is slower on these small models, almost all the time spent in Z3 queries. Cloud run, not reproduced by the author.
  Be skeptical: the suites were random, not the ones the search visits, and the models are tiny. The search itself does
  not use this yet (item 16).

- 2026-10-13, plan item 16: the search can now run without a list of every allowed configuration. Each time it needs
  a new test it asks Z3 for an allowed configuration, optionally one containing a specific interaction that is not yet
  covered, or one that differs from an existing test in exactly one setting. On the three small models with a known
  best size (9, 9 and 8) it reached that size with the same effort as the old search, using only allowed tests. Over
  7 models and 3 seeds it ended at the same size as the old search every time (21 of 21). It was slower here (about 3
  to 9 times). Cloud run, not reproduced by the author. Be skeptical: the models are tiny, so this shows the new
  search is correct, not that it is useful; that needs a model too big to list (item 17).

- 2026-10-13, plan item 17: first run on a model too big to list. The full SPIN simulator benchmark (spins) has
  18 settings with 2,002,944 allowed configurations, and the code never listed them; Z3 supplied every test and decided
  every question about allowed combinations. With the starting size I picked (40 tests), one seed and 30,000 moves
  (16 minutes), the search did not reach a perfect suite: it covered every pair of settings that can occur together
  (979) but still left 3 pairs of interactions that some allowed test could tell apart. So no suite size is
  reported for this model. Cloud run, not reproduced by the author. Be skeptical: the start size and budget were
  placeholders, not measured, so this does not say 40 is too small in principle; it says it was not found within this
  effort. Nothing here is compared with published sizes.

- 2026-10-13, plan item 18 (summary of items 15-17, plain language): The search now has a version that never needs a list
  of all allowed configurations. Z3 scores a suite, proposes new tests, and says which pairs of interactions an allowed
  test could still separate. On the small example models it matched the old search exactly: the same scores on 1,600 of
  1,600 random suites, and the same final suite size in 21 of 21 runs, including the three known best sizes (9, 8
  and 9). It was 3 to 23 times slower there, because those models are small enough to list. On the full SPIN simulator
  model (about 2 million allowed configurations, never listed) one 16-minute run starting at 40 tests did not reach a
  perfect suite: it covered every possible pair but 3 pairs of interactions were still not separated. So no suite size is
  reported for that model, and the start size of 40 was a placeholder, not a measured choice. A simple counting argument
  says at least 16 tests are needed just to cover every pair, which is a floor for coverage only. Cloud run, not
  reproduced by the author. Be skeptical: one seed, one model, one effort level.

- 2026-10-13, plan items 19-22 (plain language): My earlier start size of 40 for the full SPIN simulator model was a guess, so I
  measured instead. With seed 0 and about 3,000 moves, a perfect suite (every pair covered, every separable pair separated)
  was found at 44, 48, 52 and 56 tests; at 40 it was not found, and five times as many moves in one long run did not fix that,
  so the size, not the effort, was the problem. Then I shrank from 44: 44 and 43 worked, 42 failed all five tries (one pair
  still not separated). The smallest suite found is therefore 43 tests, all valid, covering all 979 possible pairs, and
  identifying 969 of them uniquely (the other 10 cannot be told apart by any allowed test). Cloud run, not reproduced by the
  author. Be skeptical: one seed; 42 failing means "not found with this effort", not impossible; and these 43 tests are for
  the full model, so they are not comparable with the 30 to 32 for the smaller derived model. Not compared with any published
  size. The natural next step, several seeds as for the derived model, is not in the plan yet.

- 2026-10-14, plan items 23-24 (plain language): I repeated the full-SPIN-model search with ten different random seeds, all
  starting from 44 tests. The smallest perfect suite found was 42 tests for three seeds, 43 for six and 44 for one (median 43), so the
  answer depends on the seed, as it did for the smaller derived model. Every one of the ten suites used only allowed
  configurations, covered all 979 possible pairs, and identified 969 of them uniquely; the search always stopped one size below
  its answer with a single pair left unseparated. Cloud run, not reproduced by the author. Be skeptical: "failed at 41 or 42" means
  not found with this effort, not impossible; ten seeds on one model is a small sample; no comparison with published sizes was made.

- 2026-10-14, plan item 25 (the research question measured directly): the question is how many more tests it takes to be able to tell
  interactions apart than to merely cover them all. On the seven small models I ran the same search twice, once scoring only coverage
  and once scoring coverage plus separation. Locating needed 2 to 5 more tests (for example 9 versus 5 on model.json, 8 versus 6 on
  low_constraints), the same on every seed apart from one model. Cloud run, not reproduced by the author. Be skeptical: tiny models,
  three seeds, and neither size is proven smallest. Larger models are items 26 and 27.

- 2026-10-14, plan item 26: on the smaller SPIN-derived model the smallest covering suite the search found had 18 tests for every one
  of ten seeds, while the locating suite needed 30 to 32 (median 31). So being able to tell interactions apart cost about 13 extra
  tests (12 to 14) over merely covering them, roughly 1.7 times the size. A simple counting argument says at least 16 tests are
  needed to cover this model, so 18 is close to that floor. Cloud run, not reproduced by the author. Be skeptical: one derived
  model, 18 is a found size not a proven smallest, and the two sets of runs used different code paths.

- 2026-10-14, plan items 27-28 (summary of the covering-versus-locating comparison): The research question asks how many more tests it takes
  to be able to tell interactions apart than just to cover them. Across the three kinds of model the answer was always "more, but
  within a factor of about 1.3 to 1.9". Small hand-built models: 2 to 5 more tests. The SPIN-derived model: about 13 more (18 to cover,
  30 to 32 to distinguish). The full SPIN model: about 18 to 20 more (23 to 25 to cover, 42 to 44 to distinguish). The covering suites
  by themselves told apart only about half of the interactions (457 to 566 of 979 on the full model, against 969 for the locating
  suites). Cloud run, not reproduced by the author. Be skeptical: every size is what a fixed-effort search found, not a proven smallest;
  one real benchmark; no comparison with published sizes; strengths above 2 were not tried here.

- 2026-10-15, plan item 29 (plain language): Everything measured so far was about pairs of settings. I extended the Z3 part of the code so it
  can handle triples (and any size): which triples of settings can occur together, and how to score a suite. It matched the old
  way of listing everything on all 8 example models for sizes 1, 2 and 3, and it scored 1,600 random suites at triples exactly like
  the old scorer. No search has been run on triples yet (items 30 and 31). Cloud run, not reproduced by the author. The test suite
  now takes about 6.5 minutes, mostly because of these triple checks.

- 2026-10-15, plan item 30: repeated the covering-versus-locating comparison for triples of settings on the seven small models. Cloud run, not
  reproduced by the author. Telling triples apart needed 2 to 15 more tests than merely covering them (a factor of 1.2 to 2.1), against 2 to 5
  more (1.3 to 1.8) for pairs, and both sizes grew a lot going from pairs to triples (for example 5 to 12 to cover and 9 to 17 to locate on
  model.json). The new Z3-based search agreed with the old one in 20 of 21 runs. Be skeptical: tiny models, three seeds, sizes are
  found-not-proven, and the biggest ratio comes from a model where one seed differs.

- 2026-10-15, plan item 31 (plain language): I repeated the covering-versus-telling-apart comparison for triples of settings on the
  smaller SPIN-derived model. Cloud run, not reproduced by the author. Covering all possible triples took 71 tests on every one of five
  seeds; making the triples distinguishable took 110 to 112, about 39 to 41 more (1.55 to 1.58 times). For pairs the same model needed
  18 and 30 to 32. Four of the five locating searches stopped because of the 2-hour time cap, so those sizes could probably be pushed
  a little lower with more time. Be skeptical: five seeds, one derived model (not the real benchmark), found sizes are not proven smallest.

- 2026-10-15, plan item 32 (summary of pairs versus triples): Going from pairs to triples of settings made every suite bigger. On the seven
  small models, covering took 9 to 15 tests instead of 5 to 7, and telling triples apart took 11 to 29 instead of 8 to 12. On the
  SPIN-derived model covering took 71 tests (18 for pairs) and telling apart took 110 to 112 (30 to 32 for pairs), so the extra
  tests grew from about 13 to about 39 while the ratio stayed near 1.5 to 1.8. On the small models the ratio went up for some and
  down for others, so no trend is shown. The real SPIN model was not run at triples (that needs a code change you must approve, item 33).
  Cloud run, not reproduced by the author. Be skeptical: few seeds (3 and 5), found sizes are not proven smallest, four of five
  derived-model locating runs were stopped by the time cap.

## Faster cost evaluation (plan items 34 and 35)
The search repeatedly scores a suite by checking which tests contain which interactions. The new FastZ3CostModel remembers, for each test, which interactions it contains, so scoring a suite no longer rescans every interaction. It gives the same scores as the old code (checked on all 8 example models at pairs and triples). On the derived spins model at triples, a repeat scoring took 0.0040 s instead of 0.0184 s in locating mode (one suite size, one seed). Scoring a suite for the first time is still dominated by Z3 questions about whether two interactions can be told apart, and the new class does not change that. Nothing yet says whether the original spins model at triples is feasible.

## Does the faster scoring help a real search? (plan item 36)
Yes, on the one case measured. In a 600-move search on the derived spins model at triples, the faster scoring took 0.007 to 0.009 seconds per move against 0.049 to 0.077 with the old code, and both found exactly the same suite. Most of the old time was the scoring loop, not Z3. This is one seed and 600 moves, and it says nothing yet about the original spins model.

## Can we run triples on the real spins model? (plan item 37)
Timing says yes, if you accept slow runs. With the faster scoring, one 6000-move search at 100 tests took 275 s checking only coverage and 545 s checking coverage plus distinguishability, both under the 15-minute limit we set. The model has 12,835 feasible 3-way interactions. At 100 tests neither search got to a perfect suite (38 interactions still uncovered, and 197 uncovered plus 3,857 indistinguishable pairs), so 100 is too small and we don't know the right size yet. The next step would be a size sweep, then a shrinking search, which is item 33 and still needs your go-ahead.

## Original SPIN at triples: how big a suite is enough? (plan item 39)
I tried eight suite sizes with one 6000-move search each. All of them worked: covering every triple at 120, 140, 160 and 200 tests, and also telling every triple apart at 200, 260, 320 and 400 tests. So these sizes are comfortably large for this search; the smallest working ones, 120 and 200, are only upper bounds. The earlier size-100 try did not finish covering. Cloud run, not reproduced by the author. Be skeptical: one seed, one run per size, and the sizes were my guesses. The next step (item 40) shrinks from 120 and 200 to find the real limit.

## Original SPIN at triples: how many tests? (plan item 40)
I shrank the suite one test at a time, five times with different random seeds. Covering every triple of settings ended at 114 to 116 tests (median 115). Telling every triple apart ended at 197 to 200 tests (median 199), which is 82 to 86 more tests, about 1.7 times as many. For pairs on the same model the earlier numbers were far smaller (see items 23 and 27), so triples cost much more. Cloud run, not reproduced by the author. Be skeptical: five seeds, one model, sizes are what the search found (not proven smallest), and the telling-apart searches started at 200 and barely moved from it, so those sizes may be limited by where I started.

## A second big benchmark (plan item 41)
The CCAG collection has four more named models besides SPIN (apache, bugzilla, gcc, spinv). I loaded all four and built the Z3 setup for pairs; each took under 20 seconds, so loading is not the obstacle. I then tried spinv, the one with many rules, at suite sizes 15 to 60 with one search each, and none reached a perfect suite: the guessed sizes were too small. So there is no covering-versus-locating result for a second model yet; the next step is a bigger size sweep. Cloud run, not reproduced by the author. One seed, one run per size.

## How many pairs of settings can never be told apart? (plan item 42)
Some pairs of settings in SPIN cannot be separated by any test suite, because the rules force them to appear together. I asked Z3 to count them directly instead of relying on a search. Of 979 possible pairs of settings, 10 are stuck in nine inseparable couples, so at most 969 can be told apart. The suites from the earlier ten-seed runs (42 to 44 tests) already told apart exactly 969, so for single faults on pairs they leave nothing on the table. The method also matched a brute-force count on all 8 small example models. This is one model, pairs only, one fault at a time.

## A second big model, and how many interactions can never be told apart (plan items 41 and 42)
On a second real benchmark (spinv, pairs), covering took 48 to 49 tests and telling pairs apart took 78 to 79 (about 1.6 times, 30 to 31 more). That matches the direction seen on the first benchmark. Separately I counted, using Z3, how many pairs of settings no test can ever tell apart because of the constraints: 10 of 979 on spins, 1,084 of 8,741 on spinv, none on bugzilla, 1,354 of 23,876 on benchmark_1 and 2,931 of 64,620 on benchmark_20. The count matches the old method on all 8 small models. Cloud run, not reproduced by the author. Be skeptical: three seeds, search sizes are not proven smallest, and the earlier scheduled note about missing constraint files was wrong for this clone.

## Do our suites beat the published sizes? (plan item 44)
The Jin and Tsuchiya paper reports how many tests their heuristic needed on three of the same benchmarks: Spins 49 to 53, Bugzilla 41 to 48, Spinv 91 to 97. First I checked that we are solving the same problem: the counts of interactions and of un-separable pairs in their table match ours exactly, and their "every pair covered and every separable pair told apart" condition is what our cost measures. Then I re-ran our search and saved the suites, and checked each one with a separate script. We reached 42 to 43 on Spins, 37 on Bugzilla and 79 on Spinv, all passing the check. So on these three models our suites are smaller. That does not mean our method is better: ours ran for minutes to about an hour and a half per run, theirs for seconds, and the machines differ. The fair next step is a run with matched time, and checking their numbers against the PDF itself.

## More seeds, bigger models, and the time question (plan item 45)
I checked the published table a second way (the web version) and the numbers agree. I then ran Bugzilla on four seeds (36 or 37 tests, against the published 41 to 48), Spinv on three (78 or 79, against 91 to 97), and the two biggest models, Apache (82, against 85 to 89) and GCC (61 or 63, against 61 to 68; these two stopped at the 2-hour limit while still shrinking). Every suite passed the separate check. The honest catch is time: when I limited our search to about ten times what the authors report (60 s on Bugzilla, 10 s on Spins) it landed inside their range, not below it. So the fair summary is: given far more time than their heuristic uses, our search finds smaller suites; given similar time, it ties. A real speed comparison needs their tool run on the same machine.

## Checking the paper's table, and what "faster" really means (plan items 46 and 47)
We read the published table straight from the PDF. The sizes match what we had. The new part is the times: the published method took about 3,263 seconds on apache and 2,495 on gcc, so our two-hour runs were only about 2 to 3 times longer there, not hundreds of times longer as on the small models. On apache that is close to a fair fight, and our search still ended below their smallest size, but on different hardware and with only two runs, so it is a hint, not a result. We also found SA4LA, the other group's annealing tool, but it cannot handle constraints, and we found where 20 of the 25 benchmarks used in the paper live; both need your OK before we use them.

## What if two interactions fail at once? (plan item 48)
Our suites are built so that any single failing pair of settings can be told apart from any other single one. I asked how far that is from handling two failures at the same time. On six small example models I took the suite the search found (seed 0) and counted every group of one or two pairs of settings, then checked which groups of this kind give exactly the same pass/fail pattern across the suite. Between 1,013 and 4,912 couples of groups collide per model (one model was too big and was skipped under the 5-million rule). Some of those collisions can never be fixed, because no valid test separates the two groups (60 to 1,297 per model); the rest, 456 to 4,264 per model, could be fixed by a better suite. So a suite built for one failure is clearly not enough for two. This does not say how many extra tests two failures need; nobody searched for such a suite yet. Cloud run, not reproduced by the author. One seed, six small models.

## What if tests fail only some of the time? (plan item 49)
Real failures are sometimes flaky: a test that should fail passes now and then. I simulated this on the seven small example models: for every possible failing pair of settings, a test containing it fails only with some chance p (1.0, 0.9, 0.7 or 0.5), and I allowed 1, 2 or 3 reruns per test (counted as failing if any run failed). Then I asked the exact-match localizer to name the culprit. With p = 1.0 it is always right, except on one model where 20% of the pairs can never be told apart anyway. With p = 0.9 and one run it is right only about 62% to 81% of the time; with three runs about 80% on that same hard model and 99% to 100% on the others. At p = 0.5 even three runs leave it right only 58% to 78% of the time. The exact-match localizer has no tolerance for noise, so reruns help a lot. One seed (20 random trials per pair), small models, suite sizes from the earlier search; the noise-ranking function in the code was not used. Cloud run, not reproduced by the author.
