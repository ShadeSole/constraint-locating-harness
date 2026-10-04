"""Building blocks for a simulated-annealing search for constrained locating suites.

Step 1 (this file so far): the cost function only. The search loop comes later.

The cost follows the two-part form used for unconstrained locating arrays by
Konishi, Kojima, Nakagawa & Tsuchiya (arXiv 1909.13090): a suite is good when
(1) every feasible interaction appears in some test, and (2) different
interactions appear in different sets of tests. Under constraints, part (2) must
ignore pairs that NO suite can separate (Jin & Tsuchiya, J. Systems and
Software 170, 2020), otherwise the cost could never reach zero.
"""
from __future__ import annotations
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
