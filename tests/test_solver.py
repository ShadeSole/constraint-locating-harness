import glob
import random
import unittest
from itertools import product
from math import prod
from pathlib import Path

from cla_harness.core import Forbidden, all_configurations, feasible_interactions, valid_configurations
from cla_harness.io import load_model
from cla_harness.annealing import suite_cost, unavoidable_pairs

try:
    from cla_harness import solver
except ImportError:  # Z3 not installed: the tests below are skipped
    solver = None

EXAMPLES = sorted(glob.glob(str(Path(__file__).resolve().parent.parent / "examples" / "*.json")))
PRODUCT_LIMIT = 50_000
SAMPLE_SIZE = 5_000


def configs_to_check(parameters, product_limit=PRODUCT_LIMIT, sample_size=SAMPLE_SIZE, seed=0):
    """The full product when it is small, else `sample_size` seeded random configurations."""
    if prod(len(v) for v in parameters.values()) <= product_limit:
        return all_configurations(parameters)
    rng = random.Random(seed)
    return [{n: rng.choice(v) for n, v in parameters.items()} for _ in range(sample_size)]


def key(config):
    return tuple(sorted(config.items()))


@unittest.skipUnless(solver is not None, "z3-solver is not installed")
class SolverIsValid(unittest.TestCase):
    def test_example_models_found(self):
        self.assertEqual(len(EXAMPLES), 8)

    def test_agrees_with_enumeration_on_every_example_model(self):
        for path in EXAMPLES:
            parameters, forbidden = load_model(path)
            valid = {key(c) for c in valid_configurations(parameters, forbidden)}
            for config in configs_to_check(parameters):
                self.assertEqual(solver.is_valid(parameters, forbidden, config),
                                 key(config) in valid, (path, config))

    def test_sampling_branch_for_a_product_over_the_limit(self):
        parameters = {f"P{i}": ["0", "1"] for i in range(20)}   # 1,048,576 > limit
        forbidden = [Forbidden.from_dict({"P0": "1", "P1": "1"}),
                     Forbidden.from_dict({"P2": "0", "P3": "1", "P4": "1"})]
        sample = configs_to_check(parameters, product_limit=1000, sample_size=300, seed=1)
        self.assertEqual(len(sample), 300)
        from cla_harness.core import is_valid as enumerated_is_valid
        results = [solver.is_valid(parameters, forbidden, c) for c in sample]
        self.assertEqual(results, [enumerated_is_valid(c, forbidden) for c in sample])
        self.assertIn(True, results)
        self.assertIn(False, results)

    def test_rule_naming_unknown_parameter_or_value_is_never_violated(self):
        parameters = {"A": ["x", "y"], "B": ["u", "v"]}
        forbidden = [Forbidden.from_dict({"A": "x", "Z": "q"}), Forbidden.from_dict({"B": "nope"})]
        for config in all_configurations(parameters):
            self.assertTrue(solver.is_valid(parameters, forbidden, config))

    def test_config_with_unlisted_value_or_missing_parameter_raises(self):
        parameters = {"A": ["x", "y"], "B": ["u", "v"]}
        with self.assertRaises(ValueError):
            solver.is_valid(parameters, [], {"A": "x", "B": "w"})
        with self.assertRaises(ValueError):
            solver.is_valid(parameters, [], {"A": "x"})

    def test_deliberate_break_is_caught(self):
        # A checker that ignores the rules must disagree with the enumeration on model.json.
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model.json")])
        valid = {key(c) for c in valid_configurations(parameters, forbidden)}
        wrong = [c for c in all_configurations(parameters) if solver.is_valid(parameters, [], c) != (key(c) in valid)]
        self.assertGreater(len(wrong), 0)


@unittest.skipUnless(solver is not None, "z3-solver is not installed")
class SolverEnumerationAndSampling(unittest.TestCase):
    def test_listing_equals_enumeration_on_every_example_model(self):
        for path in EXAMPLES:
            parameters, forbidden = load_model(path)
            expected = {key(c) for c in valid_configurations(parameters, forbidden)}
            self.assertLessEqual(len(expected), 5000, path)
            listed = solver.valid_configurations_z3(parameters, forbidden)
            self.assertEqual(len(listed), len(expected), path)            # no duplicates
            self.assertEqual({key(c) for c in listed}, expected, path)

    def test_samples_are_valid_seeded_and_varied(self):
        for path in EXAMPLES:
            parameters, forbidden = load_model(path)
            expected = {key(c) for c in valid_configurations(parameters, forbidden)}
            a = solver.sample_valid_configurations(parameters, forbidden, 200, seed=3)
            b = solver.sample_valid_configurations(parameters, forbidden, 200, seed=3)
            c = solver.sample_valid_configurations(parameters, forbidden, 200, seed=4)
            self.assertEqual(len(a), 200)
            self.assertTrue(all(key(x) in expected for x in a + c), path)
            self.assertEqual(a, b, path)                                    # same seed, same draw
            if len(expected) > 1:
                self.assertGreater(len({key(x) for x in a}), 1, path)
                self.assertNotEqual(a, c, path)                             # different seed differs

    def test_model_with_no_valid_configuration(self):
        parameters = {"A": ["x"], "B": ["u"]}
        forbidden = [Forbidden.from_dict({"A": "x"})]
        self.assertEqual(solver.valid_configurations_z3(parameters, forbidden), [])
        self.assertEqual(solver.sample_valid_configurations(parameters, forbidden, 5), [])

    def test_deliberate_breaks_are_caught(self):
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model.json")])
        expected = {key(c) for c in valid_configurations(parameters, forbidden)}
        self.assertNotEqual({key(c) for c in solver.valid_configurations_z3(parameters, [])}, expected)
        unconstrained = solver.sample_valid_configurations(parameters, [], 300, seed=0)
        self.assertTrue(any(key(x) not in expected for x in unconstrained))


@unittest.skipUnless(solver is not None, "z3-solver is not installed")
class SolverFeasibleInteractions(unittest.TestCase):
    def test_equals_enumeration_on_every_example_model(self):
        for path in EXAMPLES:
            parameters, forbidden = load_model(path)
            expected = feasible_interactions(valid_configurations(parameters, forbidden), 2)
            self.assertGreater(len(expected), 0, path)
            self.assertEqual(solver.feasible_interactions_z3(parameters, forbidden), expected, path)

    def test_known_counts_from_the_notes(self):
        # PROJECT_NOTES: model.json 38, model_high_constraints.json 35 (28 distinguishable), spins core 239.
        counts = {Path(p).name: len(solver.feasible_interactions_z3(*load_model(p))) for p in EXAMPLES}
        self.assertEqual((counts["model.json"], counts["model_high_constraints.json"],
                          counts["model_spins_core.json"]), (38, 35, 239))

    def test_indirectly_infeasible_pair_is_excluded(self):
        # B=1 forces A=0 (rule A=1&B=1), C=1 forces A=1 (rule A=0&C=1): B=1 and C=1 can never co-occur
        # although no rule names that pair.
        parameters = {"A": ["0", "1"], "B": ["0", "1"], "C": ["0", "1"]}
        forbidden = [Forbidden.from_dict({"A": "1", "B": "1"}), Forbidden.from_dict({"A": "0", "C": "1"})]
        found = solver.feasible_interactions_z3(parameters, forbidden)
        self.assertNotIn(frozenset({("B", "1"), ("C", "1")}), found)
        self.assertEqual(found, feasible_interactions(valid_configurations(parameters, forbidden), 2))

    def test_no_valid_configuration_and_invalid_strength(self):
        parameters = {"A": ["x"], "B": ["u"]}
        self.assertEqual(solver.feasible_interactions_z3(parameters, [Forbidden.from_dict({"A": "x"})]), frozenset())
        for bad in (0, 3):                                   # strength must be 1 .. number of parameters
            with self.assertRaises(ValueError):
                solver.feasible_interactions_z3(parameters, [], strength=bad)

    def test_deliberate_break_is_caught(self):
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model.json")])
        expected = feasible_interactions(valid_configurations(parameters, forbidden), 2)
        self.assertNotEqual(solver.feasible_interactions_z3(parameters, []), expected)


def random_suites(configs, count, seed):
    rng = random.Random(seed)
    return [rng.choices(configs, k=rng.randint(1, min(16, 2 * len(configs)))) for _ in range(count)]


@unittest.skipUnless(solver is not None, "z3-solver is not installed")
class SolverCost(unittest.TestCase):
    SUITES_PER_MODEL = 200

    def test_cost_identical_to_suite_cost_on_random_suites_for_every_model(self):
        for path in EXAMPLES:
            parameters, forbidden = load_model(path)
            configs = valid_configurations(parameters, forbidden)
            interactions = feasible_interactions(configs, 2)
            unavoidable = unavoidable_pairs(configs, interactions)
            model = solver.Z3CostModel(parameters, forbidden)
            self.assertEqual(set(model.interactions), set(interactions), path)
            mixed = 0
            for suite in random_suites(configs, self.SUITES_PER_MODEL, seed=11):
                want = suite_cost(suite, interactions, unavoidable, detail=True)
                got = model.suite_cost(suite, detail=True)
                self.assertEqual(got, want, path)
                mixed += want["avoidable_collisions"] > 0
            self.assertGreater(mixed, 0, path)       # the comparison included avoidable collisions

    def test_weight_is_applied_and_cache_is_used(self):
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model.json")])
        configs = valid_configurations(parameters, forbidden)
        interactions = feasible_interactions(configs, 2)
        unavoidable = unavoidable_pairs(configs, interactions)
        model = solver.Z3CostModel(parameters, forbidden)
        suite = configs[:3]
        self.assertEqual(model.suite_cost(suite, weight=5.0)["cost"],
                         suite_cost(suite, interactions, unavoidable, weight=5.0)["cost"])
        misses = model.misses
        self.assertGreater(misses, 0)
        model.suite_cost(suite)                       # the same suite again: no new Z3 queries
        self.assertEqual(model.misses, misses)
        self.assertGreater(model.hits, 0)

    def test_cover_only_cost_is_the_count_of_uncovered_interactions(self):
        from cla_harness.core import contains_interaction
        for path in EXAMPLES:
            parameters, forbidden = load_model(path)
            configs = valid_configurations(parameters, forbidden)
            model = solver.Z3CostModel(parameters, forbidden, cover_only=True)
            for suite in random_suites(configs, 100, seed=21):
                uncovered = [i for i in model.interactions
                             if not any(contains_interaction(c, i) for c in suite)]
                got = model.suite_cost(suite, detail=True)
                self.assertEqual(got["cost"], len(uncovered), path)
                self.assertEqual((got["uncovered"], got["avoidable_collisions"]), (len(uncovered), 0), path)
                self.assertEqual(got["uncovered_list"], sorted(uncovered, key=sorted), path)
            self.assertEqual(model.misses, 0, path)          # no separability query was needed
        # the default model is unchanged by the new option
        parameters, forbidden = load_model(EXAMPLES[0])
        self.assertFalse(solver.Z3CostModel(parameters, forbidden).cover_only)

    def test_cover_only_never_costs_more_than_locating(self):
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model.json")])
        configs = valid_configurations(parameters, forbidden)
        cover = solver.Z3CostModel(parameters, forbidden, cover_only=True)
        locate = solver.Z3CostModel(parameters, forbidden)
        for suite in random_suites(configs, 100, seed=5):
            self.assertLessEqual(cover.suite_cost(suite)["cost"], locate.suite_cost(suite)["cost"])

    def test_deliberate_break_is_caught(self):
        # Treating every colliding pair as avoidable overcounts on high_constraints, which has
        # indistinguishable interactions (28 of 35 localizable).
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model_high_constraints.json")])
        configs = valid_configurations(parameters, forbidden)
        interactions = feasible_interactions(configs, 2)
        unavoidable = unavoidable_pairs(configs, interactions)
        self.assertGreater(len(unavoidable), 0)
        model = solver.Z3CostModel(parameters, forbidden)
        model.separable = lambda a, b: True
        wrong = [s for s in random_suites(configs, 50, seed=1)
                 if model.suite_cost(s)["cost"] != suite_cost(s, interactions, unavoidable)["cost"]]
        self.assertGreater(len(wrong), 0)


Z3_MINIMA = {"model.json": 9, "model_high_constraints.json": 9, "my_model.json": 8}


@unittest.skipUnless(solver is not None, "z3-solver is not installed")
class SolverAnnealing(unittest.TestCase):
    def model_for(self, name, cover_only=False):
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index(name)])
        valid = {key(c) for c in valid_configurations(parameters, forbidden)}
        return solver.Z3CostModel(parameters, forbidden, cover_only=cover_only), valid

    def test_cover_only_search_solves_with_valid_tests_and_needs_no_more_tests_than_locating(self):
        from cla_harness.core import contains_interaction
        for name, n in Z3_MINIMA.items():
            model, valid = self.model_for(name, cover_only=True)
            found = solver.find_small_suite_z3(model, n, seed=0, restarts=3, steps_per_restart=2000)
            self.assertIsNotNone(found["size"], name)
            self.assertLessEqual(found["size"], n, name)       # a locating suite of size n also covers
            self.assertTrue(all(key(c) in valid for c in found["suite"]))
            self.assertTrue(all(any(contains_interaction(c, i) for c in found["suite"])
                                for i in model.interactions), name)

    def test_every_test_in_every_suite_is_valid_and_cost_is_consistent(self):
        for name in ("model.json", "model_spins_core.json"):
            model, valid = self.model_for(name)
            for neighbor in ("random", "targeted"):
                result = solver.anneal_suite_z3(model, 12, seed=2, max_steps=60, neighbor=neighbor)
                self.assertEqual(len(result["suite"]), 12)
                self.assertTrue(all(key(c) in valid for c in result["suite"]), (name, neighbor))
                self.assertEqual(model.suite_cost(result["suite"])["cost"], result["cost"]["cost"])

    def test_reaches_the_exact_minimum_with_both_moves(self):
        # Same budget as the enumeration-based test: size = proven minimum, 2 seeds, 20,000 moves.
        for name, n in Z3_MINIMA.items():
            model, valid = self.model_for(name)
            for neighbor in ("random", "targeted"):
                for seed in range(2):
                    result = solver.anneal_suite_z3(model, n, seed=seed, max_steps=20000, neighbor=neighbor)
                    self.assertTrue(result["solved"], (name, neighbor, seed))
                    self.assertTrue(all(key(c) in valid for c in result["suite"]))

    def test_cannot_beat_the_exact_minimum(self):
        for name, n in Z3_MINIMA.items():
            model, _ = self.model_for(name)
            result = solver.anneal_suite_z3(model, n - 1, seed=0, max_steps=1500, neighbor="targeted")
            self.assertFalse(result["solved"], name)

    def test_search_ends_exactly_at_the_proven_minimum(self):
        for name, n in Z3_MINIMA.items():
            model, valid = self.model_for(name)
            found = solver.find_small_suite_z3(model, n + 2, seed=0, restarts=3, steps_per_restart=2000)
            self.assertEqual(found["size"], n, name)
            self.assertTrue(all(key(c) in valid for c in found["suite"]))

    def test_reproducible_and_seed_sensitive(self):
        model, _ = self.model_for("model.json")
        a = solver.anneal_suite_z3(model, 10, seed=5, max_steps=80, neighbor="targeted")
        b = solver.anneal_suite_z3(model, 10, seed=5, max_steps=80, neighbor="targeted")
        c = solver.anneal_suite_z3(model, 10, seed=6, max_steps=80, neighbor="targeted")
        self.assertEqual(a, b)
        self.assertNotEqual(a["suite"], c["suite"])

    def test_one_change_neighbor_differs_in_exactly_one_parameter_and_is_valid(self):
        import random
        model, valid = self.model_for("model.json")
        rng = random.Random(0)
        for _ in range(30):
            base = solver._draw(model, rng)
            other = solver._one_change_neighbor(model, rng, base)
            self.assertIsNotNone(other)
            self.assertIn(key(other), valid)
            self.assertEqual(sum(base[n] != other[n] for n in base), 1)

    def test_deadline_stops_a_run_early_and_is_reported(self):
        import time
        model, _ = self.model_for("model_spins_core.json")
        past = time.perf_counter() - 1.0
        result = solver.anneal_suite_z3(model, 5, seed=0, max_steps=10000, deadline=past)
        self.assertTrue(result["timed_out"])
        self.assertEqual(result["steps"], 0)
        found = solver.find_small_suite_z3(model, 6, seed=0, restarts=2, steps_per_restart=5000, max_seconds=0.0)
        self.assertTrue(found["timed_out"])
        self.assertIsNone(found["size"])
        free = solver.anneal_suite_z3(model, 5, seed=0, max_steps=3)
        self.assertFalse(free["timed_out"])

    def test_deliberate_break_is_caught(self):
        # With the model's rules ignored the "valid" check below would fail: sampling from an
        # unconstrained model must produce tests the real model forbids.
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model.json")])
        valid = {key(c) for c in valid_configurations(parameters, forbidden)}
        loose = solver.Z3CostModel(parameters, [])
        result = solver.anneal_suite_z3(loose, 12, seed=0, max_steps=5, neighbor="random")
        self.assertTrue(any(key(c) not in valid for c in result["suite"]))


@unittest.skipUnless(solver is not None, "z3-solver is not installed")
class SolverStrengthT(unittest.TestCase):
    def test_interaction_sets_equal_enumeration_at_t1_t2_t3_on_every_example_model(self):
        for path in EXAMPLES:
            parameters, forbidden = load_model(path)
            configs = valid_configurations(parameters, forbidden)
            for t in (1, 2, 3):
                self.assertEqual(solver.feasible_interactions_z3(parameters, forbidden, t),
                                 feasible_interactions(configs, t), (path, t))

    def test_default_strength_is_two(self):
        parameters, forbidden = load_model(EXAMPLES[0])
        self.assertEqual(solver.feasible_interactions_z3(parameters, forbidden),
                         solver.feasible_interactions_z3(parameters, forbidden, 2))
        self.assertEqual(solver.Z3CostModel(parameters, forbidden).strength, 2)

    def test_t3_cost_identical_to_suite_cost_and_cover_cost_to_a_direct_count(self):
        from cla_harness.core import contains_interaction
        for path in EXAMPLES:
            parameters, forbidden = load_model(path)
            configs = valid_configurations(parameters, forbidden)
            interactions = feasible_interactions(configs, 3)
            unavoidable = unavoidable_pairs(configs, interactions)
            locate = solver.Z3CostModel(parameters, forbidden, strength=3)
            cover = solver.Z3CostModel(parameters, forbidden, cover_only=True, strength=3)
            self.assertEqual(set(locate.interactions), set(interactions), path)
            with_collisions = 0
            for suite in random_suites(configs, 200, seed=31):
                want = suite_cost(suite, interactions, unavoidable, detail=True)
                self.assertEqual(locate.suite_cost(suite, detail=True), want, path)
                uncovered = [i for i in interactions if not any(contains_interaction(c, i) for c in suite)]
                self.assertEqual(cover.suite_cost(suite)["cost"], len(uncovered), path)
                with_collisions += want["avoidable_collisions"] > 0
            self.assertGreater(with_collisions, 0, path)

    def test_t3_search_returns_valid_suites_that_cover_all_3way_interactions(self):
        from cla_harness.core import contains_interaction
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model.json")])
        valid = {key(c) for c in valid_configurations(parameters, forbidden)}
        for cover_only in (True, False):
            model = solver.Z3CostModel(parameters, forbidden, cover_only=cover_only, strength=3)
            found = solver.find_small_suite_z3(model, 17, seed=0, restarts=3, steps_per_restart=2000)
            self.assertIsNotNone(found["size"])
            self.assertTrue(all(key(c) in valid for c in found["suite"]))
            self.assertTrue(all(any(contains_interaction(c, i) for c in found["suite"]) for i in model.interactions))

    def test_deliberate_break_is_caught(self):
        # Computing 2-way interactions where 3-way ones are required must differ from the enumeration.
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model.json")])
        configs = valid_configurations(parameters, forbidden)
        self.assertNotEqual(solver.feasible_interactions_z3(parameters, forbidden, 2),
                            feasible_interactions(configs, 3))


if __name__ == "__main__":
    unittest.main()
