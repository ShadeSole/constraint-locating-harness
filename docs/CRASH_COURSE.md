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
| Multi-seed spread on that model | not measured yet | n/a |

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
