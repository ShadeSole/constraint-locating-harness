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


def feasible_interactions_z3(parameters: Dict[str, List[str]], forbidden: Iterable[Forbidden],
                             strength: int = 2):
    """Feasible t-way interactions: value combinations of `strength` parameters that some valid configuration contains.

    Returns a frozenset of frozensets of (parameter, value) terms, the same type as
    `core.feasible_interactions(configs, strength)`. One satisfiability query (solver assumptions)
    per candidate combination, so the cost is the number of candidates (the sum over parameter
    subsets of the product of their value counts), not the number of valid configurations.
    `strength` must be between 1 and the number of parameters (ValueError otherwise); the default,
    2, is the original behavior.
    """
    from itertools import combinations, product
    if not 1 <= strength <= len(parameters):
        raise ValueError("strength must be between 1 and the number of parameters")
    solver, variables = build_solver(parameters, forbidden)
    feasible = set()
    names = list(parameters)
    for subset in combinations(names, strength):
        for indices in product(*(range(len(parameters[n])) for n in subset)):
            assumptions = [variables[n] == i for n, i in zip(subset, indices)]
            if solver.check(*assumptions) == z3.sat:
                feasible.add(frozenset((n, parameters[n][i]) for n, i in zip(subset, indices)))
    return frozenset(feasible)


class Z3CostModel:
    """Lazy, solver-backed version of `annealing.suite_cost` for one model.

    The feasible 2-way interactions come from `feasible_interactions_z3`. For a pair of
    interactions that a suite covers with exactly the same tests, Z3 is asked whether some
    VALID configuration contains one but not the other (the pair is then "avoidable": a better
    suite could separate it). Answers are cached per unordered pair, so a pair costs at most
    one decision however many suites are scored. `hits`, `misses` and `seconds` count cache
    use and the time spent in Z3 queries, so a slow run is visible.

    With cover_only=True the cost is only the number of uncovered feasible interactions (ordinary
    t-way coverage): collisions are neither counted nor queried, so no Z3 separability query is made.
    The default (False) is unchanged. `strength` (default 2) is the interaction strength t.
    """

    def __init__(self, parameters: Dict[str, List[str]], forbidden: Iterable[Forbidden],
                 cover_only: bool = False, strength: int = 2):
        self.cover_only = cover_only
        self.strength = strength
        self.parameters = parameters
        self.solver, self.variables = build_solver(parameters, forbidden)
        self.interactions = sorted(feasible_interactions_z3(parameters, forbidden, strength), key=sorted)
        self._separable: Dict[frozenset, bool] = {}
        self.hits = 0
        self.misses = 0
        self.seconds = 0.0

    def _contains(self, interaction):
        return z3.And(*[self.variables[name] == self.parameters[name].index(value)
                        for name, value in interaction])

    def separable(self, a, b) -> bool:
        """True if some valid configuration contains exactly one of the interactions a, b."""
        import time
        pair = frozenset((a, b))
        if pair in self._separable:
            self.hits += 1
            return self._separable[pair]
        self.misses += 1
        start = time.perf_counter()
        in_a, in_b = self._contains(a), self._contains(b)
        answer = (self.solver.check(in_a, z3.Not(in_b)) == z3.sat
                  or self.solver.check(in_b, z3.Not(in_a)) == z3.sat)
        self.seconds += time.perf_counter() - start
        self._separable[pair] = answer
        return answer

    def suite_cost(self, suite: List[Config], weight: float = 1.0, detail: bool = False) -> dict:
        """Same result as `annealing.suite_cost(suite, interactions, unavoidable, weight, detail)`."""
        from collections import defaultdict
        from itertools import combinations
        from .core import contains_interaction
        groups = defaultdict(list)
        uncovered_list = []
        for interaction in self.interactions:
            signature = tuple(contains_interaction(c, interaction) for c in suite)
            if any(signature):
                groups[signature].append(interaction)
            else:
                uncovered_list.append(interaction)
        avoidable = [] if self.cover_only else [
            (a, b) for group in groups.values() if len(group) > 1
            for a, b in combinations(group, 2) if self.separable(a, b)]
        result = {
            "uncovered": len(uncovered_list),
            "avoidable_collisions": len(avoidable),
            "cost": weight * len(uncovered_list) + len(avoidable),
        }
        if detail:
            result["uncovered_list"] = sorted(uncovered_list, key=sorted)
            result["colliding_list"] = sorted({i for pair in avoidable for i in pair}, key=sorted)
        return result


class FastZ3CostModel(Z3CostModel):
    """Z3CostModel with a faster `suite_cost` (research plan item 33 prerequisite). Same results.

    Instead of testing every interaction against every test, each configuration is mapped once
    (memoized) to the ids of the interactions it contains: a configuration contains exactly one
    value combination per parameter subset of size t, so that is C(n, t) dictionary lookups.
    A suite's cost then groups interaction ids by the set of tests covering them. Collision
    classification still goes through `separable` (Z3, cached). The cost, the uncovered count and
    the detail lists are identical to `Z3CostModel.suite_cost`; the parent class is unchanged.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from itertools import combinations
        self._names = list(self.parameters)
        self._subsets = list(combinations(range(len(self._names)), self.strength))
        self._ids = {}
        for k, interaction in enumerate(self.interactions):
            terms = {n: v for n, v in interaction}
            idx = tuple(sorted(self._names.index(n) for n in terms))
            self._ids[(idx, tuple(terms[self._names[i]] for i in idx))] = k
        self._covered: Dict[tuple, tuple] = {}

    def _covered_ids(self, config: Config) -> tuple:
        key = tuple(config[n] for n in self._names)
        found = self._covered.get(key)
        if found is None:
            ids = self._ids
            found = tuple(k for k in (ids.get((sub, tuple(key[i] for i in sub))) for sub in self._subsets)
                          if k is not None)
            self._covered[key] = found
        return found

    def suite_cost(self, suite: List[Config], weight: float = 1.0, detail: bool = False) -> dict:
        from itertools import combinations
        covering: Dict[int, list] = {}
        for t, config in enumerate(suite):
            for k in self._covered_ids(config):
                covering.setdefault(k, []).append(t)
        groups: Dict[tuple, list] = {}
        for k, tests in covering.items():
            groups.setdefault(tuple(tests), []).append(self.interactions[k])
        uncovered_list = [self.interactions[k] for k in range(len(self.interactions)) if k not in covering]
        avoidable = [] if self.cover_only else [
            (a, b) for group in groups.values() if len(group) > 1
            for a, b in combinations(group, 2) if self.separable(a, b)]
        result = {
            "uncovered": len(uncovered_list),
            "avoidable_collisions": len(avoidable),
            "cost": weight * len(uncovered_list) + len(avoidable),
        }
        if detail:
            result["uncovered_list"] = sorted(uncovered_list, key=sorted)
            result["colliding_list"] = sorted({i for pair in avoidable for i in pair}, key=sorted)
        return result


# ---------------------------------------------------------------------------
# Solver-backed simulated annealing. These are NEW functions; annealing.anneal_suite and
# find_small_suite are unchanged. The search state is a list of configuration dicts (not
# indices into an enumerated list), so nothing here needs the valid configurations listed.
# ---------------------------------------------------------------------------

def _draw(model: "Z3CostModel", rng, fixed: Dict[str, int] = None):
    """One valid configuration drawn with `rng`, extending the value indices in `fixed`.

    Parameters are visited in random order and values tried in random order, keeping the
    first value Z3 can still extend. Not uniform. Returns None if `fixed` is unsatisfiable.
    """
    names = list(model.parameters)
    chosen = [model.variables[n] == i for n, i in (fixed or {}).items()]
    if model.solver.check(*chosen) != z3.sat:
        return None
    for name in rng.sample([n for n in names if n not in (fixed or {})], len(names) - len(fixed or {})):
        order = list(range(len(model.parameters[name])))
        rng.shuffle(order)
        for index in order:
            if model.solver.check(*chosen, model.variables[name] == index) == z3.sat:
                chosen.append(model.variables[name] == index)
                break
    model.solver.check(*chosen)
    return _decode(model.solver.model(), model.parameters, model.variables)


def _one_change_neighbor(model: "Z3CostModel", rng, base: Config):
    """A valid configuration differing from `base` in exactly one parameter, or None."""
    names = list(model.parameters)
    for name in rng.sample(names, len(names)):
        others = {n: model.parameters[n].index(base[n]) for n in names if n != name}
        alternatives = [i for i, v in enumerate(model.parameters[name]) if v != base[name]]
        rng.shuffle(alternatives)
        for index in alternatives:
            config = _draw(model, rng, {**others, name: index})
            if config is not None:
                return config
    return None


def _z3_move(model: "Z3CostModel", rng, current: List[Config], cost: dict, targeted: bool):
    """Return (position in the suite to change, the valid configuration to put there)."""
    from .core import contains_interaction
    if not targeted:
        return rng.randrange(len(current)), _draw(model, rng)
    def containing(target):
        return _draw(model, rng, {n: model.parameters[n].index(v) for n, v in target})
    if cost["uncovered_list"]:
        target = rng.choice(cost["uncovered_list"])
        return rng.randrange(len(current)), containing(target)
    target = rng.choice(cost["colliding_list"])
    having = [p for p, c in enumerate(current) if contains_interaction(c, target)]
    lacking = [p for p in range(len(current)) if p not in having]
    if lacking and (not having or rng.random() < 0.5):
        return rng.choice(lacking), containing(target)
    position = rng.choice(having)
    neighbor = _one_change_neighbor(model, rng, current[position])
    return position, neighbor if neighbor is not None else containing(target)


def anneal_suite_z3(model: "Z3CostModel", n_tests: int, seed: int, max_steps: int = 20000,
                    start_temp: float = 2.0, cooling: float = 0.999, weight: float = 1.0,
                    neighbor: str = "random", deadline: float = None) -> dict:
    """Simulated annealing for a suite of n_tests valid configurations, with Z3 doing the validity work.

    Same acceptance rule, temperature schedule and stopping rule as `annealing.anneal_suite`:
    a move that raises the cost by delta is kept with probability exp(-delta/T); T starts at
    start_temp and is multiplied by `cooling` per move; the search stops at cost zero or after
    max_steps moves and returns the best suite seen. Differences: the cost is `model.suite_cost`
    (lazy, cached Z3 queries), the starting tests are Z3-drawn valid configurations (distinct if
    found within 50 tries each), and the moves are:
      "random":   replace a random test with a Z3-drawn valid configuration;
      "targeted": if an interaction is uncovered, put in a Z3-drawn valid configuration containing it;
                  otherwise pick an interaction in an avoidable collision and either replace a test
                  that lacks it with a valid configuration containing it, or replace a test that has
                  it with a valid configuration differing in exactly one parameter (Z3 decides).
    Every test in every suite is valid by construction. Reproducible for a given seed unless
    `deadline` (a time.perf_counter() value) is given: the run then stops early, with
    "timed_out": True, when the clock passes it, and where it stops depends on machine speed.
    Returns {"suite", "cost", "steps", "accepted", "solved", "timed_out"}.
    """
    import math
    import random
    import time
    if neighbor not in ("random", "targeted"):
        raise ValueError("neighbor must be 'random' or 'targeted'")
    if n_tests < 1:
        raise ValueError("n_tests must be at least 1")
    rng = random.Random(seed)
    targeted = neighbor == "targeted"
    current: List[Config] = []
    for _ in range(n_tests):
        for _try in range(50):
            candidate = _draw(model, rng)
            if candidate is None:
                raise ValueError("the model has no valid configuration")
            if candidate not in current:
                break
        current.append(candidate)
    current_cost = model.suite_cost(current, weight, detail=targeted)
    best, best_cost = list(current), current_cost
    temperature = start_temp
    steps = accepted = 0
    timed_out = False
    while steps < max_steps and best_cost["cost"] > 0:
        if deadline is not None and time.perf_counter() > deadline:
            timed_out = True
            break
        steps += 1
        position, replacement = _z3_move(model, rng, current, current_cost, targeted)
        proposal = list(current)
        proposal[position] = replacement
        proposal_cost = model.suite_cost(proposal, weight, detail=targeted)
        delta = proposal_cost["cost"] - current_cost["cost"]
        if delta <= 0 or rng.random() < math.exp(-delta / temperature):
            current, current_cost = proposal, proposal_cost
            accepted += 1
            if current_cost["cost"] < best_cost["cost"]:
                best, best_cost = list(current), current_cost
        temperature *= cooling
    return {"suite": best, "cost": {k: best_cost[k] for k in ("uncovered", "avoidable_collisions", "cost")},
            "steps": steps, "accepted": accepted, "solved": best_cost["cost"] == 0,
            "timed_out": timed_out}


def find_small_suite_z3(model: "Z3CostModel", start_size: int, seed: int = 0, restarts: int = 5,
                        steps_per_restart: int = 20000, start_temp: float = 2.0, end_temp: float = 0.05,
                        neighbor: str = "targeted", min_size: int = 1, max_seconds: float = None,
                        on_attempt=None) -> dict:
    """Cold shrinking search with `anneal_suite_z3`, mirroring `annealing.find_small_suite` (no warm start).

    Solve at start_size, then try one test fewer, until a size fails all `restarts` runs of
    `steps_per_restart` moves (not proof of impossibility). Cooling falls from start_temp to
    end_temp over exactly steps_per_restart moves. Restart seeds come from
    `annealing._restart_seed`. With `max_seconds`, the whole search stops when that much wall-clock
    time has passed (the run in progress ends early); the result then has "timed_out": True and the
    attempt in progress is recorded as unsolved. `on_attempt(record)` is called after each size.
    Returns {"suite", "size", "attempts", "total_moves",
    "timed_out"}.
    """
    import time
    from .annealing import _restart_seed
    if restarts < 1 or steps_per_restart < 1 or start_size < 1 or min_size < 1 or not 0 < end_temp <= start_temp:
        raise ValueError("invalid search settings")
    cooling = (end_temp / start_temp) ** (1.0 / steps_per_restart)
    deadline = None if max_seconds is None else time.perf_counter() + max_seconds
    best_suite, attempts, total_moves, n, timed_out = None, [], 0, start_size, False
    while n >= min_size and not timed_out:
        solved, moves, used, best_cost = None, 0, 0, None
        for restart in range(restarts):
            used += 1
            result = anneal_suite_z3(model, n, _restart_seed(seed, n, restart), steps_per_restart,
                                     start_temp, cooling, neighbor=neighbor, deadline=deadline)
            moves += result["steps"]
            if best_cost is None or result["cost"]["cost"] < best_cost["cost"]:
                best_cost = result["cost"]
            if result["solved"]:
                solved = result["suite"]
                break
            if result["timed_out"]:
                timed_out = True
                break
        total_moves += moves
        attempts.append({"n": n, "solved": solved is not None, "restarts_used": used, "moves": moves,
                         "best_cost": best_cost})
        if on_attempt is not None:
            on_attempt(attempts[-1])
        if solved is None:
            break
        best_suite = solved
        n -= 1
    return {"suite": best_suite, "size": len(best_suite) if best_suite is not None else None,
            "attempts": attempts, "total_moves": total_moves, "timed_out": timed_out}
