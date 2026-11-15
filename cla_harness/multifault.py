"""Locating arrays for up to d = 2 faults on models small enough to list every valid test.

A fault set is 1 or 2 distinct feasible t-way interactions. Its signature over some tests is the set of tests that
contain at least one of its interactions (a test fails when any faulty interaction is in it). A suite is a
(2bar, t) constrained locating array when every interaction is covered and any two fault sets whose signatures over
ALL valid configurations differ also differ over the suite. Fault sets with equal full signatures can never be told
apart (Jin & Tsuchiya's distinguishability), so they are exempt.

Everything is a bit mask over the list of valid configurations: bit k is configuration k. Fault sets that share a full
signature behave identically on every suite, so the cost works on the distinct full signatures ("classes").
"""
from collections import Counter
from itertools import combinations
import math
import random
import time
from typing import Dict, List, Optional

from .core import contains_interaction


class MultiFaultModel:
    """Full signatures of every interaction and every fault class, for one model, strength and d (1 or 2)."""

    def __init__(self, configs, interactions, d: int = 2):
        if d not in (1, 2):
            raise ValueError("d must be 1 or 2")
        self.configs = list(configs)
        self.interactions = sorted(interactions, key=sorted)
        self.masks = [sum(1 << k for k, c in enumerate(self.configs) if contains_interaction(c, i))
                      for i in self.interactions]
        classes = set(self.masks)
        if d == 2:
            classes |= {a | b for a, b in combinations(self.masks, 2)}
        self.classes = sorted(classes)
        self.d = d

    def cost(self, chosen: int) -> dict:
        """uncovered: interactions in no chosen test; avoidable_collisions: pairs of classes that the chosen tests
        (a bit mask) do not separate; cost = their sum."""
        uncovered = sum(1 for m in self.masks if not m & chosen)
        seen = Counter(c & chosen for c in self.classes)
        collisions = sum(n * (n - 1) // 2 for n in seen.values())
        return {"uncovered": uncovered, "avoidable_collisions": collisions, "cost": uncovered + collisions}

    def problems(self, chosen: int, rng: random.Random) -> Optional[int]:
        """A mask of configurations that would fix one random problem of the chosen suite, or None if there is none:
        the tests of an uncovered interaction, or the tests that separate one colliding pair of classes."""
        uncovered = [m for m in self.masks if not m & chosen]
        if uncovered:
            return rng.choice(uncovered)
        groups: Dict[int, List[int]] = {}
        for c in self.classes:
            groups.setdefault(c & chosen, []).append(c)
        colliding = [g for g in groups.values() if len(g) > 1]
        if not colliding:
            return None
        a, b = rng.sample(rng.choice(colliding), 2)
        return a ^ b


def _bits(mask: int) -> List[int]:
    return [k for k in range(mask.bit_length()) if mask >> k & 1]


def anneal_multifault(model: MultiFaultModel, n_tests: int, seed: int, max_steps: int = 20000,
                      start_temp: float = 2.0, end_temp: float = 0.05, targeted: bool = True,
                      initial: Optional[List[int]] = None) -> dict:
    """Simulated annealing over suites of n_tests distinct valid configurations (positions in model.configs).

    A move swaps one chosen test for one unchosen configuration. Targeted moves pick the new configuration from a
    mask returned by MultiFaultModel.problems (so it fixes the problem it was drawn for) with probability 0.9;
    otherwise the new configuration is random. The test taken out is random. Acceptance and cooling as in
    annealing.anneal_suite, with the temperature falling geometrically from start_temp to end_temp over max_steps.
    Stops at cost zero. Returns the best suite seen."""
    n = len(model.configs)
    if not 1 <= n_tests <= n:
        raise ValueError("n_tests must be between 1 and the number of valid configurations")
    rng = random.Random(seed)
    current = list(initial) if initial is not None else rng.sample(range(n), n_tests)
    chosen = sum(1 << k for k in current)
    cost = model.cost(chosen)
    best, best_cost = list(current), cost
    temp = start_temp
    cooling = (end_temp / start_temp) ** (1 / max(1, max_steps))
    steps = 0
    full = (1 << n) - 1
    while steps < max_steps and best_cost["cost"] > 0:
        steps += 1
        fix = model.problems(chosen, rng) if targeted and rng.random() < 0.9 else None
        pool = _bits(fix & ~chosen) if fix else []
        if not pool:
            pool = _bits(full & ~chosen)
        if not pool:
            break  # every configuration is already chosen
        new = rng.choice(pool)
        slot = rng.randrange(n_tests)
        trial = chosen & ~(1 << current[slot]) | (1 << new)
        trial_cost = model.cost(trial)
        delta = trial_cost["cost"] - cost["cost"]
        if delta <= 0 or rng.random() < math.exp(-delta / temp):
            current[slot] = new
            chosen, cost = trial, trial_cost
            if cost["cost"] < best_cost["cost"]:
                best, best_cost = list(current), cost
        temp *= cooling
    return {"indices": sorted(best), "cost": best_cost, "steps": steps}


def find_small_multifault(model: MultiFaultModel, start: int, seed: int, steps_per_restart: int = 6000,
                          restarts: int = 5, targeted: bool = True, log=None,
                          max_seconds: Optional[float] = None) -> dict:
    """Shrink one test at a time from `start`: at each size up to `restarts` annealing runs (the first warm-started
    from the last solved suite minus one random test); stop at the first size where all fail, or once max_seconds
    have passed (checked between annealing runs; "timed_out" says which). Returns the smallest solved suite, or
    size None if `start` itself is not solved."""
    began = time.perf_counter()
    timed_out = False
    rng = random.Random(seed)
    solved = None
    n = start
    while n >= 1:
        ok = None
        for r in range(restarts):
            if max_seconds is not None and time.perf_counter() - began > max_seconds:
                timed_out = True
                break
            initial = None
            if r == 0 and solved is not None:
                initial = list(solved)
                initial.pop(rng.randrange(len(initial)))
            result = anneal_multifault(model, n, seed * 1000 + n * 10 + r, steps_per_restart, targeted=targeted,
                                       initial=initial)
            if log:
                log({"n": n, "restart": r, "cost": result["cost"], "steps": result["steps"]})
            if result["cost"]["cost"] == 0:
                ok = result["indices"]
                break
        if ok is None:
            break
        solved = ok
        n -= 1
    return {"size": len(solved) if solved else None, "indices": solved, "timed_out": timed_out}
