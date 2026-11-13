# AAAI-27 Undergraduate Consortium talk: slide outline (5 to 6 minutes)

**Status.** Draft, 2026-11-13. The talk is on Wednesday 2027-02-17.
- **Length.** 7 slides. The spoken script is 541 words: about 3.6 minutes at 150 words per minute, about 4.2 minutes
  at a slower 130. Pauses and pointing at figures fill the rest of the 5 to 6 minute slot. The per-slide times below
  include those pauses.
- **Template.** Use the poster's look once AAAI's guidance arrives.
- **Rule.** Every number comes from `docs/PROJECT_NOTES.md` (item named). Novelty wording stays "we did not find".
- **Before the talk.** Rehearse with a timer; cut slide 3 first if over time.

---

## Slide 0: Title (10 s)

**On the slide:** title, name, West Point. A one-line subtitle: "Which settings broke it? Test suites that locate
faults."

**Say:** "Hi, I'm Alejo. My project is about finding which *combination of settings* makes software fail."

---

## Slide 1: The problem (45 s)

**On the slide**
- Top: "It only breaks when option A is on **and** option B is set to X."
- The toy example (poster Figure 1): 4 tests, 3 options, pass/fail marks. One version where the failing tests point
  to one pair; one where they don't.
- Bottom line: "Some combinations are forbidden, so some causes can never be told apart (Jin & Tsuchiya 2020)."

**Say:** "Configurable software, compilers, web servers, ML training pipelines, often fails only when particular
settings meet. Standard combinatorial testing makes sure every pair of settings gets tested, so you'll see the failure.
But a failing test doesn't tell you *which* combination caused it. Locating arrays are test suites designed so that the
pattern of passing and failing tests points to the cause. Real systems also forbid some combinations, and that can make
two causes impossible to tell apart."

---

## Slide 2: Question and approach (60 s)

**On the slide**
- The research question, in one line: "Can we build small test suites, using only valid configurations, that locate
  every cause that *can* be located?"
- A diagram with 4 boxes (poster Figure 2): options plus rules → simulated annealing over valid tests → cost =
  uncovered + avoidable collisions → shrink one test at a time.
- Small: "Every suite checked by an independent verifier. Exact minimum sizes by SAT/MaxSAT on small models."

**Say:** "The method is AI search: simulated annealing, kept inside the valid configurations by constraint reasoning
with an SMT solver. The cost counts what isn't covered yet plus pairs of causes that still look identical, and zero
means done. Then I shrink the suite one test at a time. Locating arrays, the constrained version, and annealing for
the *unconstrained* case all exist already. What I didn't find in my searches is annealing for the constrained case,
so that's where I started."

---

## Slide 3: Does the search work? (30 s; cut this slide first if over time)

**On the slide:** one small table (item 60 cloud, item 83 local)

| system | published method's best | my search |
|---|---|---|
| apache | 85 tests | 67 to 69 (cloud, 10 seeds); 73 (my laptop) |
| gcc | 61 tests | 54 to 55 (cloud); 60 (my laptop) |

**Say:** "On the two largest standard benchmarks, my search found smaller suites than the published method's best,
within its average running time. The margin depends on the machine: on my laptop it was still smaller, but only by one
test on gcc. So I report it as 'smaller on both machines', not as a fixed number."

---

## Slide 4: A real bug (75 s), the key slide

**On the slide:** poster Figure 5 (`docs/aaai27/figures/fig5_real_bug.pdf`), full width. Source: item 85.

**Say:** "Does this find real bugs? Here's one from Python itself, fixed in April 2025. The bug report's title says it
all: configparser broke when `allow_no_value` and `interpolation` were set together. I took the code from just before
the fix and from just after, and tested every one of 3,456 configurations: 384 fail. A covering suite of 9 tests
missed it completely. My one-fault locating suite, 19 tests, caught it *and* named exactly those two settings, the
same two the Python developers named. One honest detail: my original test inputs never triggered this bug. I used
the input from the fix's own regression test. A test suite can only find bugs its inputs exercise."

---

## Slide 5: But do most bugs look like that? (60 s)

**On the slide:** poster Figure 3 on top (fault shapes) and Figure 4 below (diagnoses), or just Figure 4 with the
headline numbers circled. Items 75 to 78.

**Say:** "To test the assumption more broadly I generated hundreds of small bugs automatically in two Python modules.
Of the 193 that fail only in some configurations, almost none were a single faulty pair: 0 in one program, 1 in the
other. When a bug did fit the model, the suites diagnosed it. When it didn't, they mostly said 'no simple explanation
fits', which is the safe answer, instead of blaming the wrong settings. A two-fault design diagnosed 11 and 48 bugs.
Random suites of the same size came close on average, but half or more fell short. So what helps most is a bigger
budget and allowing for two culprits, and the construction makes that reliable. These generated bugs may be 'wider'
than typical real ones. How often real bugs fit is the open question."

---

## Slide 6: What I learned and what's next (40 s)

**On the slide**
- Three bullets:
  1. It works when bugs fit the model, and safely says so when they don't.
  2. Inputs matter as much as settings.
  3. Next: a set of real historical configuration bugs; noisy (flaky) tests; ML pipeline configurations.
- Small: "Every result above re-run on my own machine and matching, except the real-bug study (cloud run, to be
  re-run)." **Update this line** after `reproduce.py realbug` is run locally.
- "Thank you. Questions?"

**Say:** "Three takeaways. When a bug is a combination of settings, a small locating suite can name it. When it isn't,
the suite tells you that rather than misleading you. And the inputs matter as much as the settings. Next I want to
build a benchmark of real historical configuration bugs, handle flaky tests, and apply this to machine-learning
pipelines. Thank you, and I'd love your feedback."

---

## Likely questions, with honest short answers

- **"Isn't the guarantee for the two-fault design already known?"** Yes. It follows from Colbourn & McClary's
  Lemma 7.1; I measured how often it matters in practice and applied it to the constrained setting. (Item 74.)
- **"Two real bugs is anecdotal."** Agreed. They are a demonstration, not a rate, and I picked them because their
  titles suggested setting interactions. A real-bug benchmark is my next step.
- **"Why generated bugs?"** Because I can run every configuration and know the exact ground truth. The trade-off is
  that they may not look like real configuration bugs.
- **"How big can models get?"** The search runs on benchmarks with about 200 options (gcc). Exact minimum sizes are
  only known for small models; on a mid-sized model the minimum is somewhere between 16 and 29 tests. (Items 71, 72.)
- **"What does 'two-fault' cost?"** About 2.6 to 2.8 times the tests of the one-fault design on these two programs.
  (Items 75, 76.)
