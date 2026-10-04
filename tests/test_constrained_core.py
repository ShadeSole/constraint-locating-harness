import math
import os
import unittest
from pathlib import Path

from cla_harness.core import (
    Forbidden,
    constrained_core,
    feasible_interactions,
    valid_configurations,
)
from cla_harness.experiment import ceiling_of, selected_model_paths, MODEL_PATHS, SLOW_MODEL_PATHS
from cla_harness.io import load_casa_model, load_model

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK_DIR = Path(
    os.environ.get("CCAG_BENCHMARK_DIR", ROOT.parent / "external" / "CCAG" / "benchmark")
)


class ConstrainedCoreByHand(unittest.TestCase):
    """A 4-parameter model worked out on paper.

    A:2 values, B:2, C:3, D:2. One rule forbids A=1 with B=1. C and D are
    never mentioned, so they are free.
    """

    def setUp(self):
        self.parameters = {
            "A": ["0", "1"],
            "B": ["0", "1"],
            "C": ["0", "1", "2"],
            "D": ["0", "1"],
        }
        self.forbidden = [Forbidden.from_dict({"A": "1", "B": "1"})]

    def test_core_keeps_exactly_the_parameters_in_rules(self):
        core, rules, free = constrained_core(self.parameters, self.forbidden)
        self.assertEqual(list(core), ["A", "B"])
        self.assertEqual(free, ["C", "D"])
        self.assertEqual(rules, self.forbidden)

    def test_valid_counts_multiply_by_free_parameters(self):
        # Core: 2*2 = 4 raw, minus (A=1,B=1) = 3 valid.
        # Full: 3 core * 3 values of C * 2 values of D = 18 valid.
        core, rules, free = constrained_core(self.parameters, self.forbidden)
        core_valid = len(valid_configurations(core, rules))
        full_valid = len(valid_configurations(self.parameters, self.forbidden))
        self.assertEqual(core_valid, 3)
        self.assertEqual(full_valid, 18)
        free_product = math.prod(len(self.parameters[n]) for n in free)
        self.assertEqual(full_valid, core_valid * free_product)

    def test_no_rules_means_empty_core(self):
        core, rules, free = constrained_core(self.parameters, [])
        self.assertEqual(core, {})
        self.assertEqual(free, list(self.parameters))

    def test_every_parameter_in_a_rule_means_nothing_is_free(self):
        rules = [
            Forbidden.from_dict({"A": "1", "B": "1"}),
            Forbidden.from_dict({"C": "2", "D": "0"}),
        ]
        core, _, free = constrained_core(self.parameters, rules)
        self.assertEqual(list(core), list(self.parameters))
        self.assertEqual(free, [])


class SpinsCoreModel(unittest.TestCase):
    """examples/model_spins_core.json: the SPIN simulator benchmark projected
    onto the 9 parameters that appear in its 13 constraints (a DERIVED model)."""

    def setUp(self):
        parameters, forbidden = load_model(str(ROOT / "examples" / "model_spins_core.json"))
        self.parameters = parameters
        self.forbidden = forbidden
        self.configs = valid_configurations(parameters, forbidden)

    def test_shape(self):
        # 6 binary parameters and 3 four-valued ones: 2^6 * 4^3 = 4096 raw.
        counts = sorted(len(v) for v in self.parameters.values())
        self.assertEqual(counts, [2] * 6 + [4] * 3)
        self.assertEqual(len(self.forbidden), 13)

    def test_valid_count_scales_to_the_full_benchmark(self):
        # 978 here; the 9 omitted parameters (7 binary, 2 four-valued) are
        # unconstrained, so the full benchmark has 978 * 2^7 * 4^2 valid
        # configurations, equal to the independently counted 2,002,944.
        self.assertEqual(len(self.configs), 978)
        self.assertEqual(978 * 2**7 * 4**2, 2002944)

    def test_feasible_pair_count_by_hand(self):
        # 24 values in total: sum of squares = 6*4 + 3*16 = 72, so the number
        # of value pairs across different parameters is (24^2 - 72) / 2 = 252.
        # All 13 forbidden pairs are distinct and every other pair has a valid
        # completion, so 252 - 13 = 239 are feasible.
        self.assertEqual(len(feasible_interactions(self.configs, 2)), 239)

    def test_ceiling_regression_snapshot(self):
        # 229 of 239, from an independently written inverted-index script
        # (not ceiling_of). The 10 other interactions sit in four groups with
        # identical signatures, caused by chains of forced values: P0=1 forces
        # P1=0, P2=0, P14=0 and P15=0 (4 interactions identical), and any
        # non-zero P15 forces both P0=0 and P12=0 (three identical pairs).
        interactions = feasible_interactions(self.configs, 2)
        self.assertEqual(ceiling_of(self.configs, interactions), 229)

    @unittest.skipUnless(
        (BENCHMARK_DIR / "spins.model").exists(),
        "CCAG benchmark files not found (set CCAG_BENCHMARK_DIR)",
    )
    def test_file_matches_projection_of_the_real_benchmark(self):
        full_parameters, full_forbidden = load_casa_model(str(BENCHMARK_DIR / "spins.model"))
        core, rules, free = constrained_core(full_parameters, full_forbidden)
        self.assertEqual(self.parameters, core)
        self.assertEqual({frozenset(r.terms) for r in self.forbidden},
                         {frozenset(r.terms) for r in rules})
        self.assertEqual(len(free), 9)


class SelectedModelPaths(unittest.TestCase):
    def test_slow_models_only_on_request(self):
        self.assertEqual(selected_model_paths([]), MODEL_PATHS)
        self.assertEqual(
            selected_model_paths(["--include-slow"]), MODEL_PATHS + SLOW_MODEL_PATHS
        )
        for path in SLOW_MODEL_PATHS:
            self.assertNotIn(path, MODEL_PATHS)


if __name__ == "__main__":
    unittest.main()
