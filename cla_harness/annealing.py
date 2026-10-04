"""Building blocks for a simulated-annealing search for constrained locating suites.

Step 1: the cost function.
Step 2: a plain annealing loop for a FIXED suite size, with the simplest possible
neighbor move (replace one test by a random valid configuration).
Step 3: a targeted neighbor move (after Konishi et al.), chosen with neighbor="targeted".
Step 4: a search over the suite size (find_small_suite): start from a size known to
work and keep shrinking by one until a fixed budget of restarts all fail.
Later steps: speed.

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
    detail: bool = False,
) -> dict:
    """Score a suite; zero means covered and as well separated as is possible.

    uncovered            feasible interactions that appear in no test
    avoidable_collisions pairs of COVERED interactions that appear in exactly the
                         same tests although some valid test could separate them
    cost                 weight * uncovered + avoidable_collisions

    With detail=True the result also lists WHICH interactions are involved
    (uncovered_list, colliding_list), which the targeted neighbor move needs.
    Both lists are sorted so that runs are reproducible.
    """
    interactions = list(interactions)
    groups: Dict[tuple, List[Interaction]] = defaultdict(list)
    uncovered_list: List[Interaction] = []
    for interaction in interactions:
        key = tuple(contains_interaction(c, interaction) for c in suite)
        if any(key):
            groups[key].append(interaction)
        else:
            uncovered_list.append(interaction)
    avoidable_pairs = _pairs_in_groups(groups.values()) - unavoidable
    result = {
        "uncovered": len(uncovered_list),
        "avoidable_collisions": len(avoidable_pairs),
        "cost": weight * len(uncovered_list) + len(avoidable_pairs),
    }
    if detail:
        colliding = {i for pair in avoidable_pairs for i in pair}
        result["uncovered_list"] = sorted(uncovered_list, key=sorted)
        result["colliding_list"] = sorted(colliding, key=sorted)
    return result


def exact_minimum_suite_size(
    configs: List[Config],
    interactions: Iterable[Interaction],
    unavoidable: Set[Pair],
    max_n: int,
    max_subsets: int = 5_000_000,
) -> dict | None:
    """Smallest N for which SOME suite of N valid tests has cost zero, by trying all.

    Exact ground truth for small models, to check what the heuristics find.
    The cost here is the same one as in suite_cost (everything covered, and
    every pair that can be separated is separated), computed independently with
    bit masks. Raises ValueError rather than run for hours: the number of
    subsets tried is the sum of C(len(configs), n) for n = 1..max_n.

    Returns {"n": smallest size, "count": how many suites of that size have cost
    zero, "example": one of them} or None if no size up to max_n works.
    """
    interactions = sorted(interactions, key=sorted)
    total = sum(math.comb(len(configs), n) for n in range(1, max_n + 1))
    if total > max_subsets:
        raise ValueError(f"{total} subsets to try is more than max_subsets={max_subsets}")

    position = {interaction: k for k, interaction in enumerate(interactions)}
    allowed = {
        frozenset(position[i] for i in pair) for pair in unavoidable
    }
    # Bit k of masks[j] is set when test k contains interaction j.
    masks = [
        sum(1 << k for k, c in enumerate(configs) if contains_interaction(c, i))
        for i in interactions
    ]

    def zero_cost(chosen_mask):
        groups: Dict[int, List[int]] = defaultdict(list)
        for j, mask in enumerate(masks):
            signature = mask & chosen_mask
            if signature == 0:
                return False  # an interaction is not covered
            groups[signature].append(j)
        for group in groups.values():
            for a, b in combinations(group, 2):
                if frozenset((a, b)) not in allowed:
                    return False  # a separable pair is not separated
        return True

    for n in range(1, max_n + 1):
        count, example = 0, None
        for chosen in combinations(range(len(configs)), n):
            chosen_mask = 0
            for k in chosen:
                chosen_mask |= 1 << k
            if zero_cost(chosen_mask):
                count += 1
                if example is None:
                    example = [configs[k] for k in chosen]
        if count:
            return {"n": n, "count": count, "example": example}
    return None


class _TargetedHelper:
    """Chooses the targeted neighbor move (after Konishi et al., arXiv 1909.13090).

    Konishi et al. work with unconstrained arrays where a row can be overwritten
    freely. Here every row must stay a valid configuration, so instead of writing
    an interaction into a row we swap in a VALID configuration that contains it
    (a lookup built once), and "change one factor value" becomes "swap in a valid
    configuration that differs in exactly one parameter".
    """

    def __init__(self, configs, interactions):
        self.configs = configs
        self.containing = {
            i: [k for k, c in enumerate(configs) if contains_interaction(c, i)]
            for i in interactions
        }
        self._one_change: Dict[int, List[int]] = {}

    def one_change_neighbors(self, index):
        if index not in self._one_change:
            base = self.configs[index]
            self._one_change[index] = [
                k for k, c in enumerate(self.configs)
                if sum(1 for name in base if base[name] != c[name]) == 1
            ]
        return self._one_change[index]

    def move(self, rng, current, cost):
        """Return (position in the suite to change, index of the valid configuration to put there)."""
        uncovered = cost["uncovered_list"]
        if uncovered:
            target = rng.choice(uncovered)
            return rng.randrange(len(current)), rng.choice(self.containing[target])

        target = rng.choice(cost["colliding_list"])
        having = [p for p, k in enumerate(current) if contains_interaction(self.configs[k], target)]
        lacking = [p for p in range(len(current)) if p not in having]
        if lacking and (not having or rng.random() < 0.5):
            return rng.choice(lacking), rng.choice(self.containing[target])
        position = rng.choice(having)
        options = self.one_change_neighbors(current[position])
        if options:
            return position, rng.choice(options)
        return position, rng.choice(self.containing[target])


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
    neighbor: str = "random",
) -> dict:
    """Simulated annealing for a suite of exactly n_tests valid configurations.

    The search state is a list of n_tests positions in `configs`, so every test
    in the suite is a valid configuration by construction. One move replaces one
    randomly chosen test with a randomly chosen valid configuration. A move that
    does not raise the cost is always kept; a move that raises it by delta is
    kept with probability exp(-delta / temperature). The temperature starts at
    start_temp and is multiplied by `cooling` after every proposed move.

    neighbor="random" is the move above. neighbor="targeted" picks the move using
    the current suite's problems (see _targeted_move): if some interaction is
    uncovered it puts a test containing that interaction in; otherwise it picks an
    interaction in an avoidable collision and either puts a test containing it in
    place of a test that lacks it, or changes one parameter value of a test that
    has it.

    The search stops as soon as the cost reaches zero, or after max_steps moves.
    The best suite seen is returned, which can differ from the final state.
    Results are reproducible: the same seed gives the same run.
    """
    if neighbor not in ("random", "targeted"):
        raise ValueError("neighbor must be 'random' or 'targeted'")
    # A fixed order, so that "random" choices depend only on the seed.
    interactions = sorted(interactions, key=sorted)
    rng = random.Random(seed)
    if not 1 <= n_tests <= len(configs):
        raise ValueError("n_tests must be between 1 and the number of valid configurations")

    targeted = neighbor == "targeted"
    helper = _TargetedHelper(configs, interactions) if targeted else None

    current = rng.sample(range(len(configs)), n_tests)  # distinct starting tests

    def cost_of(indices):
        return suite_cost(
            [configs[i] for i in indices], interactions, unavoidable, weight, detail=targeted
        )

    current_cost = cost_of(current)
    best, best_cost = list(current), current_cost
    temperature = start_temp
    steps = 0
    accepted = 0

    while steps < max_steps and best_cost["cost"] > 0:
        steps += 1
        if targeted:
            position, replacement = helper.move(rng, current, current_cost)
        else:
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
        "cost": {k: best_cost[k] for k in ("uncovered", "avoidable_collisions", "cost")},
        "steps": steps,
        "accepted": accepted,
        "solved": best_cost["cost"] == 0,
    }


def _restart_seed(seed: int, n_tests: int, restart: int) -> int:
    """A seed for one restart that depends only on (seed, size, restart number).

    A string is used on purpose: Random(str) is reproducible across machines and
    Python versions, unlike hash() of a tuple, which changes between runs.
    """
    return random.Random(f"{seed}/{n_tests}/{restart}").randrange(2 ** 31)


def find_small_suite(
    configs: List[Config],
    interactions: Iterable[Interaction],
    unavoidable: Set[Pair],
    start_size: int,
    seed: int = 0,
    restarts: int = 5,
    steps_per_restart: int = 20000,
    start_temp: float = 2.0,
    end_temp: float = 0.05,
    neighbor: str = "targeted",
    min_size: int = 1,
) -> dict:
    """Look for the smallest suite that reaches cost zero, by shrinking one test at a time.

    1. Try to solve at start_size. This should be a size known (or hoped) to work,
       for example the size of the greedy locating suite.
    2. At each size, make up to `restarts` independent annealing runs, each with a
       budget of `steps_per_restart` moves. The first run that reaches cost zero
       solves the size.
    3. After a solved size n, try n - 1 from scratch. Stop at the first size where
       every restart fails (or when n would go below min_size).

    "Failure at size n" is therefore a fixed budget: restarts * steps_per_restart
    moves. It is NOT wall-clock time, so the outcome does not depend on how fast
    the machine is. It is also NOT a proof that n is impossible: a failed size may
    simply need more moves. Only exact_minimum_suite_size proves a minimum, and
    only for small models.

    The cooling rate is chosen so that the temperature falls from start_temp to
    end_temp over exactly steps_per_restart moves. Every run therefore uses its whole
    budget as a slow cooling schedule, instead of freezing after a few thousand moves.

    Returns {"suite": smallest suite solved or None, "size": its size or None,
    "attempts": one record per size tried, "total_moves": all moves over all runs}.
    Each attempt record has n, solved, restarts_used and moves.
    Results are reproducible: the same arguments give the same result.
    """
    interactions = list(interactions)
    if not 1 <= start_size <= len(configs):
        raise ValueError("start_size must be between 1 and the number of valid configurations")
    if restarts < 1 or steps_per_restart < 1:
        raise ValueError("restarts and steps_per_restart must be at least 1")
    if not 0 < end_temp <= start_temp:
        raise ValueError("need 0 < end_temp <= start_temp")
    if min_size < 1:
        raise ValueError("min_size must be at least 1")

    cooling = (end_temp / start_temp) ** (1.0 / steps_per_restart)
    best_suite = None
    attempts = []
    total_moves = 0
    n = start_size

    while n >= min_size:
        solved_suite = None
        moves = 0
        used = 0
        for restart in range(restarts):
            used += 1
            result = anneal_suite(
                configs, interactions, unavoidable, n,
                seed=_restart_seed(seed, n, restart),
                max_steps=steps_per_restart, start_temp=start_temp,
                cooling=cooling, neighbor=neighbor,
            )
            moves += result["steps"]
            if result["solved"]:
                solved_suite = result["suite"]
                break
        total_moves += moves
        attempts.append({"n": n, "solved": solved_suite is not None,
                         "restarts_used": used, "moves": moves})
        if solved_suite is None:
            break
        best_suite = solved_suite
        n -= 1

    return {
        "suite": best_suite,
        "size": len(best_suite) if best_suite is not None else None,
        "attempts": attempts,
        "total_moves": total_moves,
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
    parser.add_argument("--neighbor", choices=["random", "targeted"], default="random")
    parser.add_argument("--shrink", action="store_true",
                        help="treat N as a START size and keep shrinking the suite while the search succeeds")
    parser.add_argument("--restarts", type=int, default=5,
                        help="with --shrink: independent runs allowed at each size")
    parser.add_argument("--exact", action="store_true",
                        help="also find the true minimum suite size by trying every subset (small models only)")
    args = parser.parse_args(argv)

    parameters, forbidden = load_model(args.model)
    configs = valid_configurations(parameters, forbidden)
    interactions = feasible_interactions(configs, args.strength)
    unavoidable = unavoidable_pairs(configs, interactions)
    ceiling = ceiling_of(configs, interactions)
    print(f"{args.model}: {len(configs)} valid configurations, "
          f"{len(interactions)} feasible interactions, ceiling {ceiling}")
    if args.exact:
        exact = exact_minimum_suite_size(configs, interactions, unavoidable, args.n_tests)
        if exact is None:
            print(f"Exact search: no suite of up to {args.n_tests} tests reaches cost zero")
        else:
            print(f"Exact search: smallest possible suite has {exact['n']} tests "
                  f"({exact['count']} such suites exist)")
    if args.shrink:
        start = time.perf_counter()
        found = find_small_suite(configs, interactions, unavoidable, args.n_tests,
                                 seed=0, restarts=args.restarts,
                                 steps_per_restart=args.steps, neighbor=args.neighbor)
        seconds = time.perf_counter() - start
        print(f"Shrinking from {args.n_tests} tests: up to {args.restarts} runs of "
              f"{args.steps} moves per size, {args.neighbor} moves")
        for a in found["attempts"]:
            print(f"  size {a['n']}: solved={a['solved']} runs_used={a['restarts_used']} "
                  f"moves={a['moves']}")
        if found["suite"] is None:
            print(f"No suite found even at the start size; total moves {found['total_moves']}, "
                  f"time {seconds:.2f}s")
        else:
            covered, total = coverage_of(found["suite"], interactions)
            localized, _ = evaluate_suite(found["suite"], interactions)
            print(f"Smallest suite found: {found['size']} tests, covered={covered}/{total} "
                  f"localized={localized}/{total} (ceiling {ceiling}); "
                  f"total moves {found['total_moves']}, time {seconds:.2f}s")
        return
    print(f"Searching for a suite of {args.n_tests} tests, {args.steps} moves per run, "
          f"{args.neighbor} moves")

    solved = 0
    for seed in range(args.seeds):
        start = time.perf_counter()
        result = anneal_suite(configs, interactions, unavoidable, args.n_tests,
                              seed=seed, max_steps=args.steps, neighbor=args.neighbor)
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
