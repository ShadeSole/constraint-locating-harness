# Standard benchmark instances (found 2026-10-04)

Purpose: the seven hand-built models in `examples/` are too small to support a
paper. The constrained locating array literature evaluates on 27-35 standard
instances (Jin & Tsuchiya, J. Systems and Software 2020: 30 benchmarks;
Konishi et al., arXiv 1909.13090: 35 instances). This note records where
comparable instances can be obtained and what they mean for the harness.

## Source

The CCAG repository (GIST-NJU/CCAG on GitHub, MIT license) ships a `benchmark/`
folder with 35 constrained models in the CASA file format:

- five named systems: `apache`, `bugzilla`, `gcc`, `spins`, `spinv`
- thirty numbered instances: `benchmark_1` ... `benchmark_30`

Each model has `NAME.model` and `NAME.constraints` (and a `NAME.corpus` of
random failure-inducing combinations used by that project, not needed here).

The five named systems match the real-world systems of Cohen, Dwyer & Shi
(IEEE TSE 34, 2008): Apache (172 parameters), Bugzilla (52), GCC (199), SPIN
simulator (18), SPIN verifier (55); their parameter counts and value counts
agree with the files. NOT confirmed: where `benchmark_1`...`benchmark_30` come
from (the IBM models of Segall, Tzoref-Brill & Farchi, ISSTA 2011, are a
plausible origin, and the total of 35 matches Konishi et al.), and whether
their numbering matches the numbering in the CLA paper. Do not state either as
fact in a paper without checking. The separate IBM artifact of Tzoref-Brill &
Maoz (FSE 2018, 48 obfuscated models, XML, "academic research purposes only",
citation required) is a different collection and is not the same files.

Keep the benchmark files OUTSIDE this repository (they belong to other
authors). The working copy used here is in a sibling folder `external/CCAG/`
beside the repository.

## File format (CASA), as observed

`NAME.model`:
- line 1: strength t (2 in every file)
- line 2: number of parameters p
- line 3: p integers, the number of values of each parameter

`NAME.constraints`:
- first token: number of constraints c
- then for each constraint: a literal count k, then k pairs `sign index`
- every sign in all 35 files is `-`, and indices run from 0 to
  (total number of values - 1)

Inferred reading (validate before relying on it): values are numbered 0,1,2,...
consecutively across parameters in order, so index i identifies one
(parameter, value) pair; a clause with literals `- a - b` means NOT(a AND b),
that is, a forbidden partial assignment. This is the same constraint form the
harness already uses (`forbidden`: list of partial assignments), but clauses
have 2 to 5 literals, so they forbid combinations larger than pairs. A clause
that names two values of the same parameter can never be violated and should
be handled explicitly by a loader.

All 35 files parse completely with this reading. Evidence that the reading is
right, from `spins` only: the loader's rules give 2,002,944 valid
configurations out of 8,388,608 raw, matching a count made directly from the
raw files by two independent methods (pruned depth-first search and
inclusion-exclusion over the 13 clauses). One file is good support, not proof
for all 35; the same check should be repeated on `bugzilla` or a numbered
instance with a solver once Z3 is in place.

## Sizes (computed from the files)

| instance | parameters | total values | constraints | clause sizes |
|---|---|---|---|---|
| apache | 172 | 367 | 7 | 2-5 |
| bugzilla | 52 | 109 | 5 | 2-3 |
| gcc | 199 | 408 | 40 | 2-3 (37 of size 2, 3 of size 3 in the file) |
| spins | 18 | 46 | 13 | 2 |
| spinv | 55 | 134 | 49 | 2-3 |
| benchmark_1..30 | 27-197 | 59-446 | 10-48 | 2-4 |

One secondary source described GCC's constraints with the 2-way and 3-way
counts the other way round; the file counts above are what the loader will see.

## What this means for the harness

The harness enumerates every valid configuration. Raw configuration counts:

| instance | raw configurations (before constraints) |
|---|---|
| spins | 8.4 million |
| benchmark_23 | 6.0e8 |
| benchmark_7 | 1.6e9 |
| benchmark_3 | 2.1e9 |
| bugzilla | 2.7e16 |
| gcc | 4.6e61 |

Only `spins` is anywhere near enumerable, and it is still out of reach for the
current pipeline: it has 2,002,944 valid configurations, and the harness
stores every valid configuration as a Python dictionary (about two million
dictionaries of 18 entries), then repeatedly scans them in the greedy
heuristic and in the `ceiling` computation. Every other instance is far out of
reach. Running on these
benchmarks therefore requires replacing enumeration with a constraint solver:

- feasibility of a t-way interaction: is there a valid configuration
  containing it (one satisfiability query each);
- distinguishability, straight from Jin & Tsuchiya Lemma 1: two interaction
  sets are distinguishable iff some valid test covers an interaction in one
  and none in the other (one satisfiability query per pair, so the number of
  pairs must be managed);
- generating or sampling valid configurations for a search.

Z3 (`pip install z3-solver`) is available and is the natural first choice. It
is not installed in the project's environment yet.

This also matches the project's stated plan to introduce Z3 deliberately, and
it makes the ceiling computation a solver query instead of a table lookup.
