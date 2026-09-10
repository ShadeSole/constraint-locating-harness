
from __future__ import annotations
from typing import List, Iterable, Tuple, Dict, Any
from .core import Config, Interaction, contains_interaction, interaction_label

def run_suite(suite: List[Config], fault: Interaction) -> Tuple[int, ...]:
    """Deterministic single interaction fault model: 1=FAIL, 0=PASS."""
    return tuple(1 if contains_interaction(c, fault) else 0 for c in suite)

def localize_exact(suite: List[Config], outcomes: Tuple[int, ...], interactions: Iterable[Interaction]) -> List[Interaction]:
    candidates = []
    for interaction in interactions:
        expected = tuple(1 if contains_interaction(c, interaction) else 0 for c in suite)
        if expected == outcomes:
            candidates.append(interaction)
    return candidates

def rank_noisy(
    suite: List[Config],
    outcomes: Tuple[int, ...],
    interactions: Iterable[Interaction]
) -> List[Tuple[Interaction, int]]:
    """Rank candidates by Hamming distance for noisy/non-deterministic outcomes."""
    ranked = []
    for interaction in interactions:
        expected = tuple(1 if contains_interaction(c, interaction) else 0 for c in suite)
        distance = sum(a != b for a, b in zip(expected, outcomes))
        ranked.append((interaction, distance))
    return sorted(ranked, key=lambda x: x[1])

def report_candidates(candidates: List[Interaction]) -> str:
    if not candidates:
        return "No exact candidate interaction matched the observed failure signature."
    if len(candidates) == 1:
        return "FAULT LOCALIZED: " + interaction_label(candidates[0])
    return "AMBIGUOUS: " + ", ".join(interaction_label(x) for x in candidates)
