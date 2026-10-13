"""Optional Z3 backend for constraint handling.

Z3 (`pip install z3-solver`) is an OPTIONAL dependency: the rest of the package is
standard library only, and nothing outside this module imports it. Importing this
module without Z3 installed raises ImportError with an install hint.

Encoding: one integer variable per parameter, ranging over the index of its value
(0 .. number of values - 1). A forbidden rule (a partial assignment) becomes
Not(And(var == index, ...)). A rule that names a parameter or value the model does
not have can never be violated, matching `Forbidden.violated_by`, so it is dropped.
"""
from __future__ import annotations

from typing import Dict, Iterable, List

try:
    import z3
except ImportError as exc:  # pragma: no cover - exercised only when Z3 is missing
    raise ImportError("cla_harness.solver needs the optional dependency: pip install z3-solver") from exc

from .core import Config, Forbidden


def build_solver(parameters: Dict[str, List[str]], forbidden: Iterable[Forbidden]):
    """Return (solver, variables): one Int per parameter, domain bounds and one clause per rule."""
    variables = {name: z3.Int(f"p{i}") for i, name in enumerate(parameters)}
    solver = z3.Solver()
    for name, values in parameters.items():
        solver.add(variables[name] >= 0, variables[name] < len(values))
    for rule in forbidden:
        literals = []
        for name, value in rule.terms:
            if name not in parameters or value not in parameters[name]:
                literals = None  # this rule can never be violated
                break
            literals.append(variables[name] == parameters[name].index(value))
        if literals is not None:
            solver.add(z3.Not(z3.And(*literals)) if literals else z3.BoolVal(False))
    return solver, variables


def is_valid(parameters: Dict[str, List[str]], forbidden: Iterable[Forbidden], config: Config) -> bool:
    """True if `config` violates no forbidden rule, decided by Z3.

    `config` must give every parameter one of its listed values (ValueError otherwise).
    Note: `cla_harness.core.is_valid` has a different signature (config, forbidden) and
    does not check domains; this function is a separate, solver-backed check.
    """
    solver, variables = build_solver(parameters, forbidden)
    assumptions = []
    for name, values in parameters.items():
        if name not in config or config[name] not in values:
            raise ValueError(f"config needs a listed value for parameter {name!r}")
        assumptions.append(variables[name] == values.index(config[name]))
    return solver.check(*assumptions) == z3.sat


def _decode(model, parameters, variables) -> Config:
    return {name: parameters[name][model.eval(variables[name], model_completion=True).as_long()]
            for name in parameters}


def valid_configurations_z3(parameters: Dict[str, List[str]], forbidden: Iterable[Forbidden]) -> List[Config]:
    """Every valid configuration, found by Z3 with one blocking clause per solution.

    Same set as `core.valid_configurations`; the ORDER is whatever Z3 finds, not product order.
    Cost grows with the number of valid configurations (one solver call each), so this is
    meant for models small enough to enumerate; it is the cross-check for item 12 onward.
    """
    solver, variables = build_solver(parameters, forbidden)
    found: List[Config] = []
    while solver.check() == z3.sat:
        model = solver.model()
        found.append(_decode(model, parameters, variables))
        solver.add(z3.Or(*[variables[name] != model.eval(variables[name], model_completion=True)
                           for name in parameters]))
    return found


def sample_valid_configurations(parameters: Dict[str, List[str]], forbidden: Iterable[Forbidden],
                                n: int, seed: int = 0) -> List[Config]:
    """`n` valid configurations drawn with a seeded random generator (repeats are possible).

    Each draw visits the parameters in a random order and, for each, tries the values in a
    random order, keeping the first value Z3 can still extend to a valid configuration
    (checked with solver assumptions). Every result is valid by construction. The draw is NOT
    uniform over valid configurations; it is only reproducible for a given seed. Returns []
    if the model has no valid configuration.
    """
    import random
    solver, variables = build_solver(parameters, forbidden)
    if solver.check() != z3.sat:
        return []
    rng = random.Random(seed)
    names = list(parameters)
    samples: List[Config] = []
    for _ in range(n):
        chosen = []
        for name in rng.sample(names, len(names)):
            order = list(range(len(parameters[name])))
            rng.shuffle(order)
            for index in order:
                if solver.check(*chosen, variables[name] == index) == z3.sat:
                    chosen.append(variables[name] == index)
                    break
        solver.check(*chosen)
        samples.append(_decode(solver.model(), parameters, variables))
    return samples
