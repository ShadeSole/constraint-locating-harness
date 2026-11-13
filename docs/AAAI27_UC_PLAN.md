# AAAI-27 Undergraduate Consortium: camera-ready plan

Accepted to the AAAI-27 Undergraduate Consortium (author's message, 2026-11-09). This file tracks what the
camera-ready research statement needs. Travel and personal details are deliberately not kept in the repository.

## Dates (from the acceptance email)

| date | item |
|---|---|
| "coming days" after 2026-11-09 | mentor assigned |
| first week of December 2026 | poster guidance from AAAI |
| **Mon 2026-12-14** | **camera-ready (CRC) due**, on the AAAI CRC site (not EasyChair) |
| Wed 2027-02-17 | 5 to 6 minute talk at the Undergraduate Consortium |
| Thu 2027-02-18 (tentative) | poster at the main conference |

Not yet known: the CRC page limit and template. Get them from the mentor or the CRC instructions before cutting text;
they could not be fetched from this environment (web tools blocked, HTTP 403).

## The accepted research statement, checked against PROJECT_NOTES (2026-11-09)

Title: "Constraint-Aware Test Suites That Locate Faults: Simulated Annealing for Configurable Software". Every number
in it matches PROJECT_NOTES:
- 9 / 9 / 8 minima: item 63 and the V0.2 runs.
- spins-derived model: 978 valid configurations, 239 interactions, ceiling 229.
- 32 greedy; 30 tests at 6,000 moves; 29 at 20,000 moves, user-reproduced; no 28 in 100,000 moves (PROJECT_NOTES
  lines near "cold, 20,000 moves/run").
- Original spins: about 2 million valid configurations (2,002,944).

**Outdated by later work** (the statement was written before items 17 to 84):

| statement says | current state (PROJECT_NOTES item) |
|---|---|
| enumeration "cannot reach standard benchmarks"; Stage 1 = add a SAT/SMT solver | Done. A Z3-backed search runs on the CCAG benchmarks and 18 literature models, and is compared with published CLA sizes (items 17, 56, 59, 60). |
| "A first, immediate step is to run multiple seeds to see whether the 29-test result repeats" | Partly done. Later searches on the spins-derived model found 30 / 30 / 30 (item 65, 6,000 moves per run). The best proven lower bound is only 16 (items 71, 72), so the minimum is between 16 and 29. |
| Stage 2: three-way interactions and several faults | Done in part. t = 3 searches and exact minima (items 62, 63); two faults, with exact minima and counterexamples (items 65 to 70). |
| Stage 3: noisy outcomes | Started. Flaky-test simulation (item 73). |
| "Published annealing work reports difficulty beyond pairwise strength" | The source is not identified in LITERATURE_CHECK (it says only "reportedly"). Replace with our own t = 3 measurements (items 62, 63) or cite a verified source. |
| Not in the statement | Real-program study (RQ5, items 75 to 82): the standard one-fault array almost never diagnoses mutation faults in textwrap and configparser. Reproduced locally (item 80). |

**Citation fixes** (verified 2026-11-05, LITERATURE_CHECK section 12):
- Konishi et al. 2019a (SA): now published, *Information and Software Technology* 126:106346, 2020.
- Konishi et al. 2019b (CSP): the arXiv author order is Konishi, Kojima, Nakagawa, Tsuchiya. The statement has Nakagawa
  before Kojima.
- Jin, Shi & Tsuchiya: the full title is "Constrained Detecting Arrays: Mathematical Structures for Fault
  Identification in Combinatorial Interaction Testing".
- Colbourn & McClary 2008: add pages 17-48.
- Garvin, Cohen & Dwyer 2011: *Empirical Software Engineering* 16(1):61-102.
- Torres-Jimenez & Rodriguez-Tello 2012: title not verified here (LITERATURE_CHECK lists it only by topic). Check
  before the CRC.

**Claims to keep exactly as careful as they are.** The statement already says "I did not find prior work" and "This
is a hypothesis, not a claim". Keep that wording. Item 74 found that the two-fault guarantee is Colbourn & McClary's
Lemma 7.1 in the constrained setting, so do not present it as new.

## Open questions for the mentor

1. May the CRC add results obtained after acceptance, such as RQ5? Or should changes be limited to corrections and
   mentor feedback?
2. Page limit and template for the CRC.
3. Is the personal statement part of the proceedings, or only the research statement?

## Proposed order of work

1. Now: fix the citations above, and replace the unsourced "difficulty beyond pairwise strength" sentence. Both are
   safe under any CRC rule.
2. After the mentor answers question 1: add a short "Progress since submission" paragraph (Stage 1 done; first
   Stage 2 and 3 results; the real-program finding), with numbers from PROJECT_NOTES and their reproduction labels.
3. December: poster and a 5 to 6 minute talk built around one message (outline: `docs/aaai27/poster_outline.md`). Candidate: "on real programs the standard
   one-fault design almost never names the cause; more tests plus a two-pair decoder do".
