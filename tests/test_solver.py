import glob
import random
import unittest
from itertools import product
from math import prod
from pathlib import Path

from cla_harness.core import Forbidden, all_configurations, feasible_interactions, valid_configurations
from cla_harness.io import load_model

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

    def test_no_valid_configuration_and_unsupported_strength(self):
        parameters = {"A": ["x"], "B": ["u"]}
        self.assertEqual(solver.feasible_interactions_z3(parameters, [Forbidden.from_dict({"A": "x"})]), frozenset())
        with self.assertRaises(ValueError):
            solver.feasible_interactions_z3(parameters, [], strength=3)

    def test_deliberate_break_is_caught(self):
        parameters, forbidden = load_model(EXAMPLES[[Path(p).name for p in EXAMPLES].index("model.json")])
        expected = feasible_interactions(valid_configurations(parameters, forbidden), 2)
        self.assertNotEqual(solver.feasible_interactions_z3(parameters, []), expected)


if __name__ == "__main__":
    unittest.main()
