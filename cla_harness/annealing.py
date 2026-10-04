"""Building blocks for a simulated-annealing search for constrained locating suites.

Step 1: the cost function.
Step 2: a plain annealing loop for a FIXED suite size, with the simplest possible
neighbor move (replace one test by a random valid configuration).
Later steps: a smarter neighbor, then a search over the suite size.

The cost follows the two-part form used for unconstrained locating arrays by
Konishi, Kojima, Nakagawa & Tsuchiya (arXiv 1909.13090): a suite is good when
(1) every feasible interaction appears in some test, and (2) different
interactions appear in different sets of tests. Under constraints, part (2) must
ignore pairs that NO suite can separate (Jin & Tsuchiya, J. Systems and
Software 170, 2020), otherwise the cost could never reach zero.
"""
from __future__ import annotations
import math
import random
from collections import defaultdict
from itertools import combinations
from typing import Dict, FrozenSet, Iterable, List, Set

from .core import Config, Interaction, contains_interaction

Pair = FrozenSet[Interaction]


def _pairs_in_groups(groups: Iterable[List[Interaction]]) -> Set[Pair]:
    pairs: Set[Pair] = set()
    for group in groups:
        if len(group) > 1:
            for a, b in combinations(group, 2):
                pairs.add(frozenset((a, b)))
    return pairs


def unavoidable_pairs(configs: List[Config], interactions: Iterable[Interaction]) -> Set[Pair]:
    """Pairs of interactions with identical signatures over ALL valid configurations.

    No suite built from valid configurations can tell these apart. Computed once
    per model, before the search starts.
    """
    groups: Dict[tuple, List[Interaction]] = defaultdict(list)
    for interaction in interactions:
        key = tuple(contains_interaction(c, interaction) for c in configs)
        groups[key].append(interaction)
    return _pairs_in_groups(groups.values())


def suite_cost(
    suite: List[Config],
    interactions: Iterable[Interaction],
    unavoidable: Set[Pair],
    weight: float = 1.0,
) -> dict:
    """Score a suite; zero means covered and as well separated as is possible.

    uncovered            feasible interactions that appear in no test
    avoidable_collisions pairs of COVERED interactions that appear in exactly the
                         same tests although some valid test could separate them
    cost                 weight * uncovered + avoidable_collisions
    """
    interactions = list(interactions)
    groups: Dict[tuple, List[Interaction]] = defaultdict(list)
    uncovered = 0
    for interaction in interactions:
        key = tuple(contains_interaction(c, interaction) for c in suite)
        if any(key):
            groups[key].append(interaction)
        else:
            uncovered += 1
    collisions = _pairs_in_groups(groups.values())
    avoidable = len(collisions - unavoidable)
    return {
        "uncovered": uncovered,
        "avoidable_collisions": avoidable,
        "cost": weight * uncovered + avoidable,
    }


def anneal_suite(
    configs: List[Config],
    interactions: Iterable[Interaction],
    unavoidable: Set[Pair],
    n_tests: int,
    seed: int,
    max_steps: int = 20000,
    start_temp: float = 2.0,
    cooling: float = 0.999,
    weight: float = 1.0,
) -> dict:
    """Simulated annealing for a suite of exactly n_tests valid configurations.

    The search state is a list of n_tests positions in `configs`, so every test
    in the suite is a valid configuration by construction. One move replaces one
    randomly chosen test with a randomly chosen valid configuration. A move that
    does not raise the cost is always kept; a move that raises it by delta is
    kept with probability exp(-delta / temperature). The temperature starts at
    start_temp and is multiplied by `cooling` after every proposed move.

    The search stops as soon as the cost reaches zero, or after max_steps moves.
    The best suite seen is returned, which can differ from the final state.
    Results are reproducible: the same seed gives the same run.
    """
    interactions = list(interactions)
    rng = random.Random(seed)
    if not 1 <= n_tests <= len(configs):
        raise ValueError("n_tests must be between 1 and the number of valid configurations")

    current = rng.sample(range(len(configs)), n_tests)  # distinct starting tests

    def cost_of(indices):
        return suite_cost([configs[i] for i in indices], interactions, unavoidable, weight)

    current_cost = cost_of(current)
    best, best_cost = list(current), current_cost
    temperature = start_temp
    steps = 0
    accepted = 0

    while steps < max_steps and best_cost["cost"] > 0:
        steps += 1
        position = rng.randrange(n_tests)
        replacement = rng.randrange(len(configs))
        proposal = list(current)
        proposal[position] = replacement
        proposal_cost = cost_of(proposal)

        delta = proposal_cost["cost"] - current_cost["cost"]
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            current, current_cost = proposal, proposal_cost
            accepted += 1
            if current_cost["cost"] < best_cost["cost"]:
                best, best_cost = list(current), current_cost
        temperature *= cooling

    return {
        "suite": [configs[i] for i in best],
        "cost": best_cost,
        "steps": steps,
        "accepted": accepted,
        "solved": best_cost["cost"] == 0,
    }


def main(argv=None):
    """Try annealing at one suite size on one model: python -m cla_harness.annealing MODEL N"""
    import argparse
    import time
    from .core import valid_configurations, feasible_interactions
    from .experiment import ceiling_of, coverage_of, evaluate_suite
    from .io import load_model

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("model", help="path to a JSON model, e.g. examples/model.json")
    parser.add_argument("n_tests", type=int, help="suite size to search for")
    parser.add_argument("--seeds", type=int, default=5, help="number of independent runs")
    parser.add_argument("--steps", type=int, default=20000, help="moves per run")
    parser.add_argument("--strength", type=int, default=2)
    args = parser.parse_args(argv)

    parameters, forbidden = load_model(args.model)
    configs = valid_configurations(parameters, forbidden)
    interactions = feasible_interactions(configs, args.strength)
    unavoidable = unavoidable_pairs(configs, interactions)
    ceiling = ceiling_of(configs, interactions)
    print(f"{args.model}: {len(configs)} valid configurations, "
          f"{len(interactions)} feasible interactions, ceiling {ceiling}")
    print(f"Searching for a suite of {args.n_tests} tests, {args.steps} moves per run")

    solved = 0
    for seed in range(args.seeds):
        start = time.perf_counter()
        result = anneal_suite(configs, interactions, unavoidable, args.n_tests,
                              seed=seed, max_steps=args.steps)
        seconds = time.perf_counter() - start
        covered, total = coverage_of(result["suite"], interactions)
        localized, _ = evaluate_suite(result["suite"], interactions)
        solved += result["solved"]
        print(f"  seed {seed}: solved={result['solved']} cost={result['cost']['cost']:g} "
              f"steps={result['steps']} covered={covered}/{total} "
              f"localized={localized}/{total} time={seconds:.2f}s")
    print(f"Solved {solved} of {args.seeds} runs")


if __name__ == "__main__":
    main()
