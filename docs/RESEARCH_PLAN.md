1. CASA-format loader (.model and .constraints) with tests, so CCAG benchmark models can be loaded.
2. Run greedy and SA on the loadable models small enough to enumerate. Record sizes and times.
3. A constraint-structure experiment: a family of models that varies only the constraints, measuring the fraction of distinguishable interactions.
4. Strength-3 measurements on small models.
5. Warm start as an extra run instead of replacing restart 0, then compare.
6. Stops here for you: solver-based constraint handling (Z3/SAT), multiple faults, nondeterminism, anything AI-based.