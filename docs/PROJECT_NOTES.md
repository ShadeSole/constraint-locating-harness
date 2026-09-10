# Project documentation plan

## Problem
Configurable software may have many legal configurations and forbidden option combinations. Pairwise/t-way coverage can expose failures, but a failed test does not automatically identify the responsible interaction.

## Research question
How much additional test-suite size is required to make feasible interactions distinguishable by their PASS/FAIL signatures, compared with ordinary constrained t-way coverage?

## Core representation
For a selected suite, define an incidence matrix `M`:
- row = test configuration
- column = feasible t-way interaction
- `M[i,j]=1` iff test `i` contains interaction `j`.

Under the deterministic single-fault model, if interaction `j` causes every containing test to fail and all other tests pass, the observed failure vector equals column `j`. Identical columns are therefore indistinguishable.

## What to save for every experiment
- model JSON
- Git commit hash
- random seed (when randomness is added)
- interaction strength `t`
- number of raw configurations
- number of feasible configurations
- number of feasible interactions
- suite-generation method
- suite size
- generation runtime
- coverage percentage
- number of ambiguous interaction pairs
- unique localization rate
- injected fault(s)
- observed PASS/FAIL vector

## Recommended repository structure
- README.md: setup and usage
- docs/: design, math, assumptions, experiments
- examples/: reproducible models
- tests/: automated correctness checks
- results/: generated CSV/JSON experiment results (add later)
- src/package: implementation

## Claims to avoid
Do not claim that the project invented constrained locating arrays. They already exist in the research literature. Frame the contribution as an implementation, experimental extension, alternative heuristic, integration, or new evaluation unless you establish a genuinely novel result.

## Good report outline
1. Motivation
2. Background: CIT, covering arrays, locating arrays, constraints
3. Problem definition and assumptions
4. System design
5. Algorithms
6. Incidence-matrix interpretation
7. Experimental methodology
8. Results
9. Threats to validity
10. Related tools/work
11. Future work
