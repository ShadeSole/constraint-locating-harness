
from __future__ import annotations
from dataclasses import dataclass
from itertools import product, combinations
from typing import Dict, List, Tuple, Iterable, FrozenSet, Any

Config = Dict[str, str]
Term = Tuple[str, str]
Interaction = FrozenSet[Term]

@dataclass(frozen=True)
class Forbidden:
    """A partial assignment that may not appear in a valid configuration."""
    terms: Interaction

    @staticmethod
    def from_dict(d: Dict[str, str]) -> "Forbidden":
        return Forbidden(frozenset(d.items()))

    def violated_by(self, config: Config) -> bool:
        return all(config.get(k) == v for k, v in self.terms)

def all_configurations(parameters: Dict[str, List[str]]) -> List[Config]:
    names = list(parameters)
    return [
        dict(zip(names, values))
        for values in product(*(parameters[name] for name in names))
    ]

def is_valid(config: Config, forbidden: Iterable[Forbidden]) -> bool:
    return not any(rule.violated_by(config) for rule in forbidden)

def valid_configurations(parameters: Dict[str, List[str]], forbidden: Iterable[Forbidden]) -> List[Config]:
    rules = list(forbidden)
    return [c for c in all_configurations(parameters) if is_valid(c, rules)]

def interactions_of(config: Config, strength: int = 2) -> FrozenSet[Interaction]:
    if strength < 1 or strength > len(config):
        raise ValueError("strength must be between 1 and the number of parameters")
    return frozenset(
        frozenset(combo)
        for combo in combinations(config.items(), strength)
    )

def feasible_interactions(configs: Iterable[Config], strength: int = 2) -> FrozenSet[Interaction]:
    out = set()
    for config in configs:
        out.update(interactions_of(config, strength))
    return frozenset(out)

def contains_interaction(config: Config, interaction: Interaction) -> bool:
    return all(config.get(k) == v for k, v in interaction)

def interaction_label(interaction: Interaction) -> str:
    return " AND ".join(f"{k}={v}" for k, v in sorted(interaction))
