import unittest
from pathlib import Path

from cla_harness.annealing import suite_cost, unavoidable_pairs
from cla_harness.core import Forbidden, feasible_interactions, valid_configurations
from cla_harness.experiment import evaluate_suite, ceiling_of
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


if __name__ == "__main__":
    unittest.main()
