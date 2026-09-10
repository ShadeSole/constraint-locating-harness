
from __future__ import annotations
from typing import List, Iterable, Set, Tuple
from .core import Config, Interaction, interactions_of

def greedy_covering_suite(configs: List[Config], interactions: Iterable[Interaction], strength: int = 2) -> List[Config]:
    """Greedy feasible t-way covering suite."""
    uncovered: Set[Interaction] = set(interactions)
    selected: List[Config] = []
    remaining = list(configs)

    while uncovered:
        best = None
        best_gain = -1
        for c in remaining:
            gain = len(set(interactions_of(c, strength)) & uncovered)
            if gain > best_gain:
                best, best_gain = c, gain
        if best is None or best_gain <= 0:
            raise RuntimeError("Could not cover all feasible interactions.")
        selected.append(best)
        uncovered -= set(interactions_of(best, strength))
        remaining.remove(best)
    return selected

def signature(suite: List[Config], interaction: Interaction) -> Tuple[int, ...]:
    from .core import contains_interaction
    return tuple(1 if contains_interaction(c, interaction) else 0 for c in suite)

def ambiguous_pairs(suite: List[Config], interactions: Iterable[Interaction]) -> Set[frozenset]:
    buckets = {}
    for i in interactions:
        buckets.setdefault(signature(suite, i), []).append(i)
    pairs = set()
    for group in buckets.values():
        if len(group) > 1:
            for a in range(len(group)):
                for b in range(a + 1, len(group)):
                    pairs.add(frozenset((group[a], group[b])))
    return pairs

def greedy_locating_suite(
    configs: List[Config],
    interactions: Iterable[Interaction],
    strength: int = 2,
    coverage_weight: float = 1.0,
    locating_weight: float = 1.0,
) -> List[Config]:
    """
    Heuristic single-fault locating suite.
    Adds tests that gain coverage and/or split currently identical interaction signatures.
    """
    interactions = list(interactions)
    selected: List[Config] = []
    remaining = list(configs)
    uncovered = set(interactions)

    def score(candidate: Config) -> float:
        coverage_gain = len(set(interactions_of(candidate, strength)) & uncovered)
        if not selected:
            split_gain = 0
        else:
            before = len(ambiguous_pairs(selected, interactions))
            after = len(ambiguous_pairs(selected + [candidate], interactions))
            split_gain = before - after
        return coverage_weight * coverage_gain + locating_weight * split_gain

    # First guarantee coverage.
    while uncovered:
        best = max(remaining, key=score)
        selected.append(best)
        uncovered -= set(interactions_of(best, strength))
        remaining.remove(best)

    # Then keep adding tests until every interaction has a unique signature, if possible.
    while True:
        current = ambiguous_pairs(selected, interactions)
        if not current:
            break
        if not remaining:
            break
        best = min(
            remaining,
            key=lambda c: len(ambiguous_pairs(selected + [c], interactions))
        )
        new_amb = ambiguous_pairs(selected + [best], interactions)
        if len(new_amb) >= len(current):
            break
        selected.append(best)
        remaining.remove(best)

    return selected
