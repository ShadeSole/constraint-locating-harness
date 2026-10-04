import unittest
from pathlib import Path

import random
from unittest import mock

from cla_harness import annealing
from cla_harness.annealing import (
    _TargetedHelper,
    _restart_seed,
    anneal_suite,
    drop_least_useful_test,
    exact_minimum_suite_size,
    find_small_suite,
    suite_cost,
    unavoidable_pairs,
)
from cla_harness.core import Forbidden, feasible_interactions, valid_configurations
from cla_harness.experiment import coverage_of, evaluate_suite, ceiling_of
from cla_harness.generator import greedy_covering_suite, greedy_locating_suite
from cla_harness.io import load_model

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def two_binary(forbidden_rules=()):
    parameters = {"A": ["0", "1"], "B": ["0", "1"]}
    forbidden = [Forbidden.from_dict(r) for r in forbidden_rules]
    configs = valid_configurations(parameters, forbidden)
    interactions = feasible_interactions(configs, 1)  # A0, A1, B0, B1
    return configs, interactions


def config(a, b):
    return {"A": a, "B": b}


class CostByHand(unittest.TestCase):
    """Two binary parameters, strength 1: interactions A0, A1, B0, B1."""

    def setUp(self):
        self.configs, self.interactions = two_binary()
        self.unavoidable = unavoidable_pairs(self.configs, self.interactions)

    def test_nothing_is_unavoidable_without_constraints(self):
        self.assertEqual(self.unavoidable, set())

    def test_empty_suite_leaves_everything_uncovered(self):
        r = suite_cost([], self.interactions, self.unavoidable)
        self.assertEqual((r["uncovered"], r["avoidable_collisions"], r["cost"]), (4, 0, 4))

    def test_one_test_covers_two_and_collides_them(self):
        # (0,0) covers A0 and B0, which then appear in exactly the same tests.
        r = suite_cost([config("0", "0")], self.interactions, self.unavoidable)
        self.assertEqual((r["uncovered"], r["avoidable_collisions"]), (2, 1))
        self.assertEqual(r["cost"], 3)

    def test_weight_scales_only_the_uncovered_part(self):
        r = suite_cost([config("0", "0")], self.interactions, self.unavoidable, weight=10)
        self.assertEqual(r["cost"], 10 * 2 + 1)

    def test_two_diagonal_tests_cover_all_but_collide_in_pairs(self):
        # (0,0),(1,1): A0 and B0 share signature (1,0); A1 and B1 share (0,1).
        suite = [config("0", "0"), config("1", "1")]
        r = suite_cost(suite, self.interactions, self.unavoidable)
        self.assertEqual((r["uncovered"], r["avoidable_collisions"], r["cost"]), (0, 2, 2))

    def test_three_tests_separate_everything(self):
        suite = [config("0", "0"), config("1", "1"), config("0", "1")]
        r = suite_cost(suite, self.interactions, self.unavoidable)
        self.assertEqual(r["cost"], 0)


class CostIgnoresUnavoidablePairs(unittest.TestCase):
    def test_forced_equivalences_cost_nothing(self):
        # Forbid A0&B1 and A1&B0: only (0,0) and (1,1) remain valid, so
        # A0~B0 and A1~B1 can never be separated by any suite.
        configs, interactions = two_binary(
            [{"A": "0", "B": "1"}, {"A": "1", "B": "0"}]
        )
        unavoidable = unavoidable_pairs(configs, interactions)
        self.assertEqual(len(unavoidable), 2)
        r = suite_cost(configs, interactions, unavoidable)  # the whole valid space
        self.assertEqual((r["uncovered"], r["avoidable_collisions"], r["cost"]), (0, 0, 0))


class CostOnHighConstraintsModel(unittest.TestCase):
    """Ties the cost to results already recorded in PROJECT_NOTES.md."""

    def setUp(self):
        parameters, forbidden = load_model(str(EXAMPLES / "model_high_constraints.json"))
        self.configs = valid_configurations(parameters, forbidden)
        self.interactions = feasible_interactions(self.configs, 2)
        self.unavoidable = unavoidable_pairs(self.configs, self.interactions)

    def test_five_unavoidable_pairs(self):
        # The 5 ambiguous pairs left at the ceiling (28 of 35 localizable).
        self.assertEqual(len(self.unavoidable), 5)

    def test_whole_valid_space_costs_zero(self):
        r = suite_cost(self.configs, self.interactions, self.unavoidable)
        self.assertEqual(r["cost"], 0)

    def test_locating_suite_costs_zero_and_reaches_the_ceiling(self):
        suite = greedy_locating_suite(self.configs, self.interactions, strength=2)
        r = suite_cost(suite, self.interactions, self.unavoidable)
        self.assertEqual(r["cost"], 0)
        localized, _ = evaluate_suite(suite, self.interactions)
        self.assertEqual(localized, ceiling_of(self.configs, self.interactions))

    def test_covering_suite_has_covering_but_not_separation(self):
        # Recorded: the covering suite has 21 ambiguous pairs, 5 of them
        # unavoidable, so 16 are avoidable.
        suite = greedy_covering_suite(self.configs, self.interactions, strength=2)
        r = suite_cost(suite, self.interactions, self.unavoidable)
        self.assertEqual(r["uncovered"], 0)
        self.assertEqual(r["avoidable_collisions"], 16)

    def test_zero_cost_means_ceiling_reached(self):
        # The cost is zero exactly when the suite localizes as many
        # interactions as any suite could.
        ceiling = ceiling_of(self.configs, self.interactions)
        for generator in (greedy_covering_suite, greedy_locating_suite):
            suite = generator(self.configs, self.interactions, strength=2)
            r = suite_cost(suite, self.interactions, self.unavoidable)
            localized, _ = evaluate_suite(suite, self.interactions)
            self.assertEqual(r["cost"] == 0, localized == ceiling)


class CostOnSpinsCore(unittest.TestCase):
    """The derived real-benchmark model; fast checks only (no locating suite)."""

    def setUp(self):
        parameters, forbidden = load_model(str(EXAMPLES / "model_spins_core.json"))
        self.configs = valid_configurations(parameters, forbidden)
        self.interactions = feasible_interactions(self.configs, 2)
        self.unavoidable = unavoidable_pairs(self.configs, self.interactions)

    def test_nine_unavoidable_pairs(self):
        # Groups of 2, 2, 2 and 4 identical interactions: 1 + 1 + 1 + 6 pairs.
        self.assertEqual(len(self.unavoidable), 9)

    def test_whole_valid_space_costs_zero(self):
        r = suite_cost(self.configs, self.interactions, self.unavoidable)
        self.assertEqual(r["cost"], 0)

    def test_covering_suite_avoidable_collisions(self):
        # Recorded: the covering suite has 369 ambiguous pairs; 9 of them are
        # unavoidable, so 360 are avoidable. The locating suite's 9 recorded
        # ambiguous pairs are exactly the unavoidable ones.
        suite = greedy_covering_suite(self.configs, self.interactions, strength=2)
        r = suite_cost(suite, self.interactions, self.unavoidable)
        self.assertEqual((r["uncovered"], r["avoidable_collisions"]), (0, 360))


class AnnealByHand(unittest.TestCase):
    """Two binary parameters, strength 1: four interactions, four valid tests."""

    def setUp(self):
        self.configs, self.interactions = two_binary()
        self.unavoidable = unavoidable_pairs(self.configs, self.interactions)

    def run_sa(self, n_tests, seed=0, steps=500):
        return anneal_suite(self.configs, self.interactions, self.unavoidable,
                            n_tests, seed=seed, max_steps=steps)

    def test_three_tests_are_enough(self):
        # Verified by hand: any three of the four configurations separate all
        # four interactions, so annealing must find a zero-cost suite.
        for seed in range(5):
            result = self.run_sa(3, seed)
            self.assertTrue(result["solved"])
            self.assertEqual(len(result["suite"]), 3)

    def test_two_tests_can_never_be_enough(self):
        # Four interactions need four different non-empty signatures, but two
        # tests allow only three (01, 10, 11). No search can reach zero.
        result = self.run_sa(2, steps=300)
        self.assertFalse(result["solved"])
        self.assertEqual(result["steps"], 300)
        self.assertGreater(result["cost"]["cost"], 0)

    def test_same_seed_gives_the_same_run(self):
        a, b = self.run_sa(2, seed=7, steps=200), self.run_sa(2, seed=7, steps=200)
        self.assertEqual(a["suite"], b["suite"])
        self.assertEqual((a["steps"], a["accepted"]), (b["steps"], b["accepted"]))

    def test_suite_uses_only_valid_configurations_and_reported_cost_is_real(self):
        for n in (2, 3):
            result = self.run_sa(n, steps=200)
            self.assertEqual(len(result["suite"]), n)
            for test in result["suite"]:
                self.assertIn(test, self.configs)
            recomputed = suite_cost(result["suite"], self.interactions, self.unavoidable)
            self.assertEqual(result["cost"], recomputed)

    def test_bad_sizes_are_rejected(self):
        for n in (0, 5):
            with self.assertRaises(ValueError):
                self.run_sa(n)

    def test_returns_the_best_suite_seen_not_the_last_one(self):
        # With an enormous temperature and no cooling every move is accepted, so
        # the search is a random walk whose final state is rarely its best. The
        # returned suite must still be the best one, and its reported cost must
        # match the suite actually returned.
        parameters, forbidden = load_model(str(EXAMPLES / "model.json"))
        configs = valid_configurations(parameters, forbidden)
        interactions = feasible_interactions(configs, 2)
        unavoidable = unavoidable_pairs(configs, interactions)
        for seed in range(5):
            result = anneal_suite(configs, interactions, unavoidable, 4, seed=seed,
                                  max_steps=200, start_temp=1e9, cooling=1.0)
            recomputed = suite_cost(result["suite"], interactions, unavoidable)
            self.assertEqual(result["cost"], recomputed)
            self.assertEqual(result["accepted"], 200)  # nothing was rejected


class AnnealMatchesIndependentEvaluator(unittest.TestCase):
    def test_zero_cost_suite_covers_everything_and_reaches_the_ceiling(self):
        # model.json: the greedy locating suite needs 11 tests. Annealing finds
        # a 9-test suite with cost 0; the project's separate evaluator must
        # agree that it covers all 38 interactions and localizes 38 of 38.
        parameters, forbidden = load_model(str(EXAMPLES / "model.json"))
        configs = valid_configurations(parameters, forbidden)
        interactions = feasible_interactions(configs, 2)
        unavoidable = unavoidable_pairs(configs, interactions)
        result = anneal_suite(configs, interactions, unavoidable, 9, seed=0, max_steps=20000)
        self.assertTrue(result["solved"])
        covered, total = coverage_of(result["suite"], interactions)
        localized, _ = evaluate_suite(result["suite"], interactions)
        self.assertEqual((covered, total), (38, 38))
        self.assertEqual(localized, ceiling_of(configs, interactions))
        self.assertEqual(localized, 38)


class ExactMinimumByHand(unittest.TestCase):
    def test_unconstrained_two_binary_needs_three_tests(self):
        # Hand-derived earlier: any 3 of the 4 configurations separate all four
        # interactions, and 2 tests cannot (only 3 non-empty signatures exist).
        configs, interactions = two_binary()
        unavoidable = unavoidable_pairs(configs, interactions)
        found = exact_minimum_suite_size(configs, interactions, unavoidable, max_n=4)
        self.assertEqual((found["n"], found["count"]), (3, 4))

    def test_forced_equivalences_need_both_valid_tests(self):
        # Only (0,0) and (1,1) are valid: one test leaves two interactions
        # uncovered, both tests give cost zero.
        configs, interactions = two_binary([{"A": "0", "B": "1"}, {"A": "1", "B": "0"}])
        unavoidable = unavoidable_pairs(configs, interactions)
        found = exact_minimum_suite_size(configs, interactions, unavoidable, max_n=2)
        self.assertEqual((found["n"], found["count"]), (2, 1))

    def test_returns_none_when_max_n_is_too_small(self):
        configs, interactions = two_binary()
        unavoidable = unavoidable_pairs(configs, interactions)
        self.assertIsNone(exact_minimum_suite_size(configs, interactions, unavoidable, max_n=2))

    def test_refuses_to_run_for_hours(self):
        configs, interactions = two_binary()
        unavoidable = unavoidable_pairs(configs, interactions)
        with self.assertRaises(ValueError):
            exact_minimum_suite_size(configs, interactions, unavoidable, max_n=4, max_subsets=5)

    def test_example_really_has_cost_zero(self):
        configs, interactions = two_binary()
        unavoidable = unavoidable_pairs(configs, interactions)
        found = exact_minimum_suite_size(configs, interactions, unavoidable, max_n=4)
        self.assertEqual(suite_cost(found["example"], interactions, unavoidable)["cost"], 0)


# Smallest zero-cost suite sizes found by trying every subset, and how many suites
# of that size exist. Regression snapshots from exact_minimum_suite_size, which
# uses its own bit-mask cost; the greedy locating heuristic needs 11, 11 and 9.
EXACT_MINIMA = {
    "model.json": (9, 2),
    "model_high_constraints.json": (9, 1),
    "my_model.json": (8, 8),
}


class SearchAgainstExactMinimum(unittest.TestCase):
    def setUp(self):
        self.models = {}
        for name in EXACT_MINIMA:
            parameters, forbidden = load_model(str(EXAMPLES / name))
            configs = valid_configurations(parameters, forbidden)
            interactions = feasible_interactions(configs, 2)
            self.models[name] = (configs, interactions, unavoidable_pairs(configs, interactions))

    def test_exact_minima(self):
        for name, (n, count) in EXACT_MINIMA.items():
            configs, interactions, unavoidable = self.models[name]
            found = exact_minimum_suite_size(configs, interactions, unavoidable, max_n=n)
            self.assertEqual((found["n"], found["count"]), (n, count), name)

    def test_annealing_reaches_the_exact_minimum_with_both_moves(self):
        for name, (n, _) in EXACT_MINIMA.items():
            configs, interactions, unavoidable = self.models[name]
            for neighbor in ("random", "targeted"):
                for seed in range(2):
                    result = anneal_suite(configs, interactions, unavoidable, n,
                                          seed=seed, max_steps=20000, neighbor=neighbor)
                    self.assertTrue(result["solved"], (name, neighbor, seed))

    def test_annealing_cannot_beat_the_exact_minimum(self):
        # One test below the proven minimum is impossible, so no search can solve it.
        for name, (n, _) in EXACT_MINIMA.items():
            configs, interactions, unavoidable = self.models[name]
            result = anneal_suite(configs, interactions, unavoidable, n - 1,
                                  seed=0, max_steps=1500, neighbor="targeted")
            self.assertFalse(result["solved"], name)


class TargetedMoveBehaviour(unittest.TestCase):
    def setUp(self):
        self.configs, self.interactions = two_binary()
        self.unavoidable = unavoidable_pairs(self.configs, self.interactions)
        self.helper = _TargetedHelper(self.configs, sorted(self.interactions, key=sorted))

    def index_of(self, a, b):
        return self.configs.index(config(a, b))

    def test_detail_lists_name_the_problem_interactions(self):
        r = suite_cost([config("0", "0")], self.interactions, self.unavoidable, detail=True)
        names = lambda items: sorted(sorted(i)[0][0] + sorted(i)[0][1] for i in items)
        self.assertEqual(names(r["uncovered_list"]), ["A1", "B1"])
        self.assertEqual(names(r["colliding_list"]), ["A0", "B0"])

    def test_default_cost_has_no_detail_keys(self):
        r = suite_cost([config("0", "0")], self.interactions, self.unavoidable)
        self.assertEqual(set(r), {"uncovered", "avoidable_collisions", "cost"})

    def test_uncovered_interaction_gets_a_test_that_contains_one(self):
        current = [self.index_of("0", "0")]  # leaves A1 and B1 uncovered
        cost = suite_cost([self.configs[k] for k in current], self.interactions,
                          self.unavoidable, detail=True)
        for seed in range(20):
            position, replacement = self.helper.move(random.Random(seed), current, cost)
            self.assertEqual(position, 0)
            new_test = self.configs[replacement]
            self.assertTrue(new_test["A"] == "1" or new_test["B"] == "1")  # holds A1 or B1

    def test_collision_move_changes_the_suite_and_stays_valid(self):
        current = [self.index_of("0", "0"), self.index_of("1", "1")]  # all covered, 2 collisions
        cost = suite_cost([self.configs[k] for k in current], self.interactions,
                          self.unavoidable, detail=True)
        self.assertEqual(cost["uncovered_list"], [])
        for seed in range(50):
            position, replacement = self.helper.move(random.Random(seed), current, cost)
            self.assertIn(position, (0, 1))
            self.assertNotEqual(replacement, current[position])
            self.assertTrue(0 <= replacement < len(self.configs))

    def test_one_change_neighbors_differ_in_exactly_one_parameter(self):
        for k, base in enumerate(self.configs):
            for j in self.helper.one_change_neighbors(k):
                self.assertEqual(sum(base[n] != self.configs[j][n] for n in base), 1)

    def test_targeted_search_is_reproducible_and_valid(self):
        parameters, forbidden = load_model(str(EXAMPLES / "model.json"))
        configs = valid_configurations(parameters, forbidden)
        interactions = feasible_interactions(configs, 2)
        unavoidable = unavoidable_pairs(configs, interactions)
        kwargs = dict(seed=3, max_steps=2000, neighbor="targeted")
        a = anneal_suite(configs, interactions, unavoidable, 9, **kwargs)
        b = anneal_suite(configs, interactions, unavoidable, 9, **kwargs)
        self.assertEqual((a["suite"], a["steps"], a["accepted"]), (b["suite"], b["steps"], b["accepted"]))
        for test in a["suite"]:
            self.assertIn(test, configs)
        self.assertEqual(a["cost"], suite_cost(a["suite"], interactions, unavoidable))

    def test_unknown_neighbor_is_rejected(self):
        with self.assertRaises(ValueError):
            anneal_suite(self.configs, self.interactions, self.unavoidable, 2,
                         seed=0, neighbor="magic")


if __name__ == "__main__":
    unittest.main()


class FindSmallSuiteByHand(unittest.TestCase):
    """Two binary parameters, strength 1: the hand-verified minimum is 3 tests."""

    def setUp(self):
        self.configs, self.interactions = two_binary()
        self.unavoidable = unavoidable_pairs(self.configs, self.interactions)

    def search(self, start=4, **kwargs):
        kwargs.setdefault("restarts", 3)
        kwargs.setdefault("steps_per_restart", 200)
        return find_small_suite(self.configs, self.interactions, self.unavoidable,
                                start, **kwargs)

    def test_shrinks_to_the_minimum_and_stops(self):
        found = self.search()
        self.assertEqual(found["size"], 3)
        self.assertEqual([(a["n"], a["solved"]) for a in found["attempts"]],
                         [(4, True), (3, True), (2, False)])

    def test_returned_suite_is_valid_and_has_cost_zero(self):
        found = self.search()
        self.assertEqual(len(found["suite"]), 3)
        for test in found["suite"]:
            self.assertIn(test, self.configs)
        self.assertEqual(suite_cost(found["suite"], self.interactions, self.unavoidable)["cost"], 0)

    def test_failure_costs_exactly_the_fixed_budget(self):
        # Size 2 can never be solved, so every restart must use every move.
        found = self.search(restarts=3, steps_per_restart=200)
        failed = found["attempts"][-1]
        self.assertEqual(failed["restarts_used"], 3)
        self.assertEqual(failed["moves"], 3 * 200)

    def test_total_moves_adds_up_over_all_sizes(self):
        found = self.search()
        self.assertEqual(found["total_moves"], sum(a["moves"] for a in found["attempts"]))

    def test_same_arguments_give_the_same_result(self):
        a, b = self.search(seed=4), self.search(seed=4)
        self.assertEqual(a["suite"], b["suite"])
        self.assertEqual(a["attempts"], b["attempts"])

    def test_nothing_found_when_the_start_size_is_too_small(self):
        found = self.search(start=2)
        self.assertIsNone(found["suite"])
        self.assertIsNone(found["size"])
        self.assertEqual(len(found["attempts"]), 1)

    def test_min_size_stops_the_shrinking_early(self):
        found = self.search(min_size=3)
        self.assertEqual([a["n"] for a in found["attempts"]], [4, 3])
        self.assertEqual(found["size"], 3)

    def test_bad_arguments_are_rejected(self):
        for kwargs in ({"start": 0}, {"start": 5}, {"restarts": 0},
                       {"steps_per_restart": 0}, {"end_temp": 0},
                       {"end_temp": 3.0}, {"min_size": 0}):
            with self.assertRaises(ValueError, msg=str(kwargs)):
                self.search(**kwargs)

    def test_cooling_runs_from_start_temp_down_to_end_temp_over_the_budget(self):
        calls = []
        real = annealing.anneal_suite

        def spy(*args, **kwargs):
            calls.append(kwargs)
            return real(*args, **kwargs)

        with mock.patch.object(annealing, "anneal_suite", spy):
            self.search(start=3, steps_per_restart=400, start_temp=2.0, end_temp=0.05)
        self.assertTrue(calls)
        for kwargs in calls:
            self.assertEqual(kwargs["max_steps"], 400)
            final = kwargs["start_temp"] * kwargs["cooling"] ** 400
            self.assertAlmostEqual(final, 0.05, places=9)

    def test_restart_seeds_are_stable_and_differ_by_size_and_restart(self):
        self.assertEqual(_restart_seed(1, 5, 0), _restart_seed(1, 5, 0))
        seeds = {_restart_seed(1, n, r) for n in (4, 5, 6) for r in range(4)}
        self.assertEqual(len(seeds), 12)
        self.assertNotEqual(_restart_seed(1, 5, 0), _restart_seed(2, 5, 0))


class FindSmallSuiteAgainstExactMinimum(unittest.TestCase):
    def test_search_ends_exactly_at_the_proven_minimum(self):
        # Starting two tests above the proven minimum, the search must come down to
        # the minimum and cannot go below it, because no smaller suite exists.
        for name, (n, _) in EXACT_MINIMA.items():
            parameters, forbidden = load_model(str(EXAMPLES / name))
            configs = valid_configurations(parameters, forbidden)
            interactions = feasible_interactions(configs, 2)
            unavoidable = unavoidable_pairs(configs, interactions)
            found = find_small_suite(configs, interactions, unavoidable, n + 2,
                                     seed=0, restarts=3, steps_per_restart=2000)
            self.assertEqual(found["size"], n, name)
            localized, _ = evaluate_suite(found["suite"], interactions)
            self.assertEqual(localized, ceiling_of(configs, interactions), name)


class WarmStartByHand(unittest.TestCase):
    """Two binary parameters, strength 1: any three of the four tests give cost zero."""

    def setUp(self):
        self.configs, self.interactions = two_binary()
        self.unavoidable = unavoidable_pairs(self.configs, self.interactions)

    def cost(self, indices):
        suite = [self.configs[i] for i in indices]
        return suite_cost(suite, self.interactions, self.unavoidable)["cost"]

    def test_run_starts_from_the_given_suite(self):
        # Zero moves allowed, so the result is exactly the starting suite.
        result = anneal_suite(self.configs, self.interactions, self.unavoidable,
                              2, seed=0, max_steps=0, initial=[0, 0])
        self.assertEqual(result["indices"], [0, 0])
        self.assertEqual(result["suite"], [self.configs[0]] * 2)
        self.assertEqual(result["steps"], 0)

    def test_a_good_starting_suite_is_solved_without_any_move(self):
        result = anneal_suite(self.configs, self.interactions, self.unavoidable,
                              3, seed=0, max_steps=100, initial=[0, 1, 2])
        self.assertTrue(result["solved"])
        self.assertEqual(result["steps"], 0)

    def test_indices_match_the_returned_suite(self):
        result = anneal_suite(self.configs, self.interactions, self.unavoidable,
                              3, seed=2, max_steps=200)
        self.assertEqual([self.configs[i] for i in result["indices"]], result["suite"])

    def test_bad_initial_suites_are_rejected(self):
        for initial in ([0, 1], [0, 1, 2, 3], [0, 1, 9], [0, 1, -1]):
            with self.assertRaises(ValueError, msg=str(initial)):
                anneal_suite(self.configs, self.interactions, self.unavoidable,
                             3, seed=0, initial=initial)

    def test_drop_keeps_all_but_one_test_and_picks_the_cheapest_drop(self):
        indices = [0, 1, 2]
        costs = [self.cost(indices[:k] + indices[k + 1:]) for k in range(3)]
        self.assertGreater(len(set(costs)), 1)  # the choice really matters here
        rest = drop_least_useful_test(self.configs, self.interactions,
                                      self.unavoidable, indices)
        self.assertEqual(len(rest), 2)
        self.assertEqual(self.cost(rest), min(costs))
        self.assertEqual(rest, indices[:costs.index(min(costs))] + indices[costs.index(min(costs)) + 1:])

    def test_drop_from_a_redundant_suite_stays_at_cost_zero(self):
        rest = drop_least_useful_test(self.configs, self.interactions,
                                      self.unavoidable, [0, 1, 2, 3])
        self.assertEqual(len(rest), 3)
        self.assertEqual(self.cost(rest), 0)

    def search(self, **kwargs):
        kwargs.setdefault("restarts", 3)
        kwargs.setdefault("steps_per_restart", 200)
        return find_small_suite(self.configs, self.interactions, self.unavoidable,
                                4, warm_start=True, **kwargs)

    def test_warm_start_solves_the_next_size_from_the_previous_suite(self):
        found = self.search()
        self.assertEqual(found["size"], 3)
        by_size = {a["n"]: a for a in found["attempts"]}
        self.assertEqual(by_size[4]["solved_by"], "cold")  # nothing to warm start from
        self.assertEqual(by_size[3]["solved_by"], "warm")
        self.assertEqual((by_size[3]["restarts_used"], by_size[3]["moves"]), (1, 0))
        self.assertIsNone(by_size[2]["solved_by"])

    def test_without_warm_start_every_run_is_cold(self):
        found = find_small_suite(self.configs, self.interactions, self.unavoidable, 4,
                                 restarts=3, steps_per_restart=200)
        self.assertEqual(found["size"], 3)
        self.assertEqual({a["solved_by"] for a in found["attempts"]}, {"cold", None})

    def test_warm_run_is_one_of_the_restarts_so_the_failure_budget_is_unchanged(self):
        found = self.search(restarts=3, steps_per_restart=200)
        failed = found["attempts"][-1]
        self.assertEqual((failed["restarts_used"], failed["moves"]), (3, 3 * 200))

    def test_only_the_first_run_at_a_size_is_warm_and_it_is_cooler(self):
        calls = []
        real = annealing.anneal_suite

        def spy(*args, **kwargs):
            calls.append((args[3], kwargs))
            return real(*args, **kwargs)

        with mock.patch.object(annealing, "anneal_suite", spy):
            self.search(restarts=3, steps_per_restart=400, start_temp=2.0,
                        end_temp=0.05, warm_start_temp=0.3)
        size_two = [kw for n, kw in calls if n == 2]
        self.assertEqual(len(size_two), 3)
        self.assertIsNotNone(size_two[0]["initial"])
        self.assertEqual(len(size_two[0]["initial"]), 2)
        self.assertEqual(size_two[0]["start_temp"], 0.3)
        self.assertAlmostEqual(0.3 * size_two[0]["cooling"] ** 400, 0.05, places=9)
        for kw in size_two[1:]:
            self.assertIsNone(kw["initial"])
            self.assertEqual(kw["start_temp"], 2.0)
        # The very first size has nothing to warm start from.
        self.assertTrue(all(kw["initial"] is None for n, kw in calls if n == 4))

    def test_warm_temperature_is_only_checked_when_warm_start_is_on(self):
        for temp in (0.01, 3.0):
            with self.assertRaises(ValueError):
                self.search(warm_start_temp=temp)
            found = find_small_suite(self.configs, self.interactions, self.unavoidable, 4,
                                     restarts=2, steps_per_restart=100, warm_start_temp=temp)
            self.assertEqual(found["size"], 3)


class WarmStartAgainstExactMinimum(unittest.TestCase):
    def test_warm_search_also_ends_exactly_at_the_proven_minimum(self):
        for name, (n, _) in EXACT_MINIMA.items():
            parameters, forbidden = load_model(str(EXAMPLES / name))
            configs = valid_configurations(parameters, forbidden)
            interactions = feasible_interactions(configs, 2)
            unavoidable = unavoidable_pairs(configs, interactions)
            found = find_small_suite(configs, interactions, unavoidable, n + 2, seed=0,
                                     restarts=3, steps_per_restart=2000, warm_start=True)
            self.assertEqual(found["size"], n, name)
            self.assertEqual(suite_cost(found["suite"], interactions, unavoidable)["cost"], 0, name)
