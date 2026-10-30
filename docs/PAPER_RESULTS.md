# Draft results section (for the plan author to edit)

Drafted 2026-10-29 in a live cloud session. **Every number below was produced by cloud (sandbox) runs and has not been
reproduced by the author.** Each table names the `docs/PROJECT_NOTES.md` section it is copied from; nothing here is new
measurement. Before submission: re-run the headline rows locally, check every Table 1 figure against the journal version
(J. Syst. Softw. 170, 2020), and settle the claims in "Positioning" with the literature check.

## Setting and terms

- Interaction localization only: one deterministic faulty interaction (d = 1), strength t = 2 unless stated. No
  source-code fault localization.
- A suite is a (1bar,2)-constrained locating array (CLA) in the sense of Jin & Tsuchiya (2020): every valid test, every
  feasible 2-way interaction covered, and every pair of distinguishable interactions separated by some test.
  Inseparable pairs (no valid test separates them) are exempt.
- Every suite reported was re-checked by `scripts/item44_verify.py`, which shares only the model loader with the search
  and uses its own Z3 encoding.
- Sizes are what a search found within a stated budget, not proven minima. Seeds are listed per row; three seeds is a
  small sample.

## Positioning (claims to keep, claims to avoid)

Prior work (see `docs/LITERATURE_CHECK.md` sections 1, 3 and 6): constrained locating arrays and distinguishability
(Jin & Tsuchiya 2020); simulated annealing for **unconstrained** locating arrays, with a targeted neighbourhood and a
binary search over sizes (Konishi et al. 2020, SA4LA); metaheuristics with constraint handling for constrained
**covering** arrays (Garvin, Cohen & Dwyer). The ceiling metric is an instance of Jin & Tsuchiya's distinguishability.

- Safe: this work applies simulated annealing, with every test kept valid by a solver, to constrained locating arrays,
  and measures it against the published CLA heuristic and against SA4LA.
- Must credit: the "local" move (write an interaction's t values into an existing test; leave a collision by changing
  one of the interaction's own values) follows SA4LA's moves; what is added is keeping every test valid under the
  constraints (rule check, Z3 fallback).
- Avoid: "first", "novel", "no prior work". Three excerpt-only literature searches found no constrained-locating-array
  metaheuristic; that is "we did not find", not "there is none".

## RQ1. How many more tests does localization cost than coverage?

Local move, same budget for both modes. t = 2: PROJECT_NOTES "Covering versus locating with the local move" (item 61);
t = 3: "RQ1 at t = 3 with the local move" (item 62). Seeds 0 to 2.

| model | t | cap | covering | locating | extra tests | locating / covering |
|---|---|---|---|---|---|---|
| spins | 2 | 600 s | 20 / 21 / 21 | 38 / 39 / 39 | 18 | 1.86 to 1.90 |
| bugzilla | 2 | 600 s | 16 / 16 / 16 | 32 / 32 / 32 | 16 | 2.00 |
| spinv | 2 | 600 s | 51 / 50 / 49 | 82 / 82 / 82 | 31 to 33 | 1.61 to 1.67 |
| apache | 2 | 3,263 s | 36 / 37 / 36 | 69 / 69 / 69 | 32 to 33 | 1.86 to 1.92 |
| gcc | 2 | 2,495 s | 26 / 28 / 28 | 54 / 54 / 55 | 26 to 28 | 1.93 to 2.08 |
| spins | 3 | 2,700 s | 107 / 108 / 108 | 195 / 193 / 192 | 84 to 88 | 1.78 to 1.82 |
| seven small example models | 3 | 60 s | 9 to 15 | 11 to 28 | 2 to 14 | 1.22 to 2.00 |

On the five constrained benchmarks at t = 2 a locating array needed about 1.6 to 2.1 times the tests of a covering
array at the same budget; at t = 3 on spins about 1.8 times. Spins and bugzilla runs at t = 2 finished before the
cap; all others on the CCAG models were capped, so their sizes are upper bounds for the budget. On the small models
at t = 3 the local move reproduced the earlier targeted-move sizes (item 32) except one model, and its locating
searches never went below their start size. Item 63 (exact minimum by MaxSAT over all valid configurations) shows
the best small-model sizes are the proven minima in 27 of 28 (model, t, mode) cases; the exception is model_8param.json
locating at t = 3 (minimum 26, search 27 to 28). At the minimum the small-model ratio is 1.33 to 1.80 at t = 2 and
1.22 to 1.86 at t = 3. The earlier
targeted-move measurements (items 28, 32, 40 and 43) are kept in the notes but not used here.

## RQ2. Does the move design matter? A same-machine race with SA4LA

PROJECT_NOTES "Same-machine, equal-time comparison with SA4LA" (item 52), "Why SA4LA won" (item 54) and "A local move,
and the race re-run" (item 55). SA4LA cannot express constraints, so both ran on the CCAG models with constraints
removed; this search was capped at SA4LA's own run time for the same model and seed, on the same 4-core container.

| model (unconstrained) | SA4LA | targeted move, same time | local move, same time |
|---|---|---|---|
| spins | 35 / 35 / 35 | 45 / 44 / 43 | 35 / 36 / 35 |
| bugzilla | 32 / 32 / 32 | 43 / 44 / 43 | 32 / 32 / 32 |
| spinv | 51 / 51 / 52 | 66 / 68 / 67 | 51 / 51 / 52 |

Diagnosis (item 54): started at SA4LA's own size, the targeted move solved it in none of 18 runs, even with 30,000
moves, while SA4LA reached it within single anneals of at most 4,096 moves; the targeted move also made about 4 to 9
times fewer moves per second. The gap was the move (replacing a whole test with a fresh solver draw), not the size
schedule. Given more moves from SA4LA's size, the local move went to 50 on spinv (3 seeds) and 34 on spins (1 seed).
Apache was not part of the re-run.

## RQ3. Constrained benchmarks against the published CLA heuristic

PROJECT_NOTES "Constrained CCAG models with the local move" (item 56), "Literature benchmarks with the local move"
(item 59) and "Ten seeds on apache, gcc and Insurance with the local move" (item 60). Published figures: Jin & Tsuchiya Table 1 (10 runs each, C++,
3.2 GHz Xeon). This search: Python, 4-core cloud container, cap = their average time (minimum 5 s). **Different
hardware and language, and their tool is not public, so this is not a same-machine comparison.**

| model | published min to max (avg time) | local move, cap = their time | local move, 10x |
|---|---|---|---|
| apache | 85 to 89 (3,263 s) | 67 to 69, median 68.5 (10 seeds) | not run |
| gcc | 61 to 68 (2,495 s) | 54 to 55, median 54 (10 seeds) | not run |
| spins | 49 to 53 (0.63 s) | 51 / 50 / 51 (5 s) | 42 / 42 / 43 |
| bugzilla | 41 to 48 (9.02 s) | 46 / 46 / 46 | 36 / 35 / 34 |
| spinv | 91 to 97 (58.21 s) | 95 / 96 / 95 | 83 / 83 / 83 |
| Insurance | 789 to 805 (84.34 s) | 803 / 803 / 803 (3 seeds) | 775 to 782, median 778 (10 seeds) |

On the 18 literature benchmarks (Segall et al., from the Jia et al. Zenodo archive; 18 of 20 match Table 1's
interaction counts), at 10 times max(5 s, their time) the median over 3 seeds was below the published minimum on 12
and inside the published range on 6. For 13 of those models their time is under 1 s, so even the first cap gives this
search 5 to 50 times their time: **the search is not faster on small models**; it reaches smaller arrays given seconds
to minutes.

## Threats to validity (to expand)

- Hardware, language and tool availability: the CLA heuristic comparison is not same-machine.
- Seeds: three per model except apache, gcc and Insurance (ten).
- Budgets: most runs were stopped by their time cap while still shrinking; sizes are upper bounds for that budget.
- Data provenance: Table 1 rows 8, 9 and 21 to 24 were read by a freeform query of a PDF conversion; ProcessorComm2
  and Storage4 differ from Table 1 and were excluded; rows 1 to 5 were not available.
- RQ1 at t = 3 rests on one CCAG model (spins, capped) and seven small hand-made models. Minimality is proven only on
  the small models (item 63); on the CCAG models no lower bound is known.
