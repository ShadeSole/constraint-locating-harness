import csv
import tempfile
import unittest
from pathlib import Path

from cla_harness.core import valid_configurations, feasible_interactions
from cla_harness.generator import greedy_covering_suite, greedy_locating_suite
from cla_harness.io import load_model, write_results_csv
from cla_harness.experiment import (
    RESULT_COLUMNS,
    evaluate_suite,
    run_method,
)

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
MODEL_FILES = ["model.json", "my_model.json", "model_6param.json", "model_8param.json", "model_multivalue.json"]

def run_both_methods(model_file, strength=2):
    """Build the model and return (num_valid_configs, num_interactions, [cover, locate])."""
    parameters, forbidden = load_model(str(EXAMPLES / model_file))
    configs = valid_configurations(parameters, forbidden)
    interactions = feasible_interactions(configs, strength)
    records = [
        run_method(model_file, "cover", greedy_covering_suite, configs, interactions, strength),
        run_method(model_file, "locate", greedy_locating_suite, configs, interactions, strength),
    ]
    return len(configs), len(interactions), records


class EvaluateSuiteByHand(unittest.TestCase):
    """Tiny model where the correct answer can be worked out on paper."""

    def setUp(self):
        parameters = {"A": ["0", "1"], "B": ["0", "1"]}
        self.configs = valid_configurations(parameters, [])
        # Strength 1: the interactions are A=0, A=1, B=0, B=1.
        self.interactions = feasible_interactions(self.configs, 1)

    def test_two_tests_leave_every_interaction_ambiguous(self):
        # Tests: (A0,B0) and (A1,B1).
        # A=0 and B=0 both have signature (1,0); A=1 and B=1 both have (0,1).
        suite = [
            {"A": "0", "B": "0"},
            {"A": "1", "B": "1"},
        ]
        localized, total = evaluate_suite(suite, self.interactions)
        self.assertEqual((localized, total), (0, 4))

    def test_all_four_tests_localize_every_interaction(self):
        # With all four configurations the four signatures are all different.
        localized, total = evaluate_suite(self.configs, self.interactions)
        self.assertEqual((localized, total), (4, 4))


class ExperimentInvariants(unittest.TestCase):
    """Properties that must hold on every benchmark model."""

    def test_model_level_counts_for_example_model(self):
        # These depend only on the model and constraints, not on any heuristic.
        valid, feasible, _ = run_both_methods("model.json")
        self.assertEqual(valid, 18)
        self.assertEqual(feasible, 38)

    def test_model_level_counts_for_6param_model(self):
        # model_6param.json = model.json plus one unconstrained binary parameter.
        # Valid configurations double: 18 * 2 = 36.
        # Pairs involving the new parameter: 5 other parameters * (2 * 2 values) = 20,
        # all feasible, so 38 + 20 = 58.
        valid, feasible, _ = run_both_methods("model_6param.json")
        self.assertEqual(valid, 36)
        self.assertEqual(feasible, 58)

    def test_model_level_counts_for_8param_model(self):
        # model_8param.json = model.json's 5 constrained parameters plus 3 more
        # unconstrained binary parameters (Compression, Caching, Backup), none of
        # which appear in any forbidden rule.
        #
        # Valid configurations: the 5 constrained parameters still allow 18 valid
        # combinations (as in model.json); each is extended freely by the 3 new
        # parameters: 18 * 2^3 = 144.
        #
        # Feasible pairwise interactions, by category of parameter pair:
        #   - among the 5 original parameters: 38 (as in model.json)
        #   - one original parameter x one new parameter: 5 * 3 pairs * 4 values = 60
        #     (always feasible, since the new parameters are unconstrained)
        #   - among the 3 new parameters: 3 pairs * 4 values = 12
        # Total: 38 + 60 + 12 = 110.
        valid, feasible, _ = run_both_methods("model_8param.json")
        self.assertEqual(valid, 144)
        self.assertEqual(feasible, 110)
    def test_model_level_counts_for_multivalue_model(self):
        # model_multivalue.json = model.json with Network expanded from 2 values
        # (WiFi, Ethernet) to 3 (WiFi, Ethernet, Cellular). Everything else,
        # including both forbidden rules, is unchanged.
        #
        # Valid configurations, by inclusion-exclusion on the 2 forbidden rules
        # over the raw 2*3*2*2*2=48 configurations:
        #   rule1 (Auth=CAC, Encryption=Off) violated by: 1*3*1*2*2 = 12
        #   rule2 (Database=Remote, Network=WiFi) violated by: 2*1*2*2*1 = 8
        #   both violated (overlap): 1*1*1*2*1 = 2
        #   invalid = 12 + 8 - 2 = 18; valid = 48 - 18 = 30
        #
        # Feasible pairwise interactions: of the 10 parameter pairs, only two
        # contain an infeasible term-combination (exactly the two forbidden
        # rules themselves, since every other parameter pair can always be
        # extended to a valid configuration independently). Total possible
        # term-pairs = 48 (sum of values(A)*values(B) over the 10 pairs);
        # subtract the 2 infeasible ones (the forbidden rules) = 46.
        valid, feasible, _ = run_both_methods("model_multivalue.json")
        self.assertEqual(valid, 30)
        self.assertEqual(feasible, 46)
        
    def test_both_methods_cover_every_feasible_interaction(self):
        for model_file in MODEL_FILES:
            _, _, records = run_both_methods(model_file)
            for r in records:
                with self.subTest(model=model_file, method=r["method"]):
                    self.assertEqual(r["covered"], r["interactions"])
                    self.assertEqual(r["coverage_rate"], 1.0)

    def test_zero_ambiguity_if_and_only_if_full_localization(self):
        # Under the single-fault deterministic model, an interaction is uniquely
        # localized exactly when no other interaction shares its signature.
        for model_file in MODEL_FILES:
            _, _, records = run_both_methods(model_file)
            for r in records:
                with self.subTest(model=model_file, method=r["method"]):
                    no_ambiguity = r["ambiguous_pairs"] == 0
                    fully_localized = r["localized"] == r["total"]
                    self.assertEqual(no_ambiguity, fully_localized)

    def test_records_have_exactly_the_csv_columns(self):
        _, _, records = run_both_methods("model.json")
        for r in records:
            self.assertEqual(set(r), set(RESULT_COLUMNS))

    def test_snapshot_example_model(self):
        # REGRESSION SNAPSHOT of current greedy-heuristic behavior on model.json.
        # If you deliberately improve the heuristics this test is EXPECTED to
        # change; update the numbers after checking the new results are correct.
        _, _, (cover, locate) = run_both_methods("model.json")
        self.assertEqual((cover["tests"], cover["localized"]), (6, 10))
        self.assertEqual((locate["tests"], locate["localized"]), (11, 38))


class CsvOutput(unittest.TestCase):
    def test_csv_has_expected_header_and_rows(self):
        _, _, records = run_both_methods("model.json")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "results.csv"  # parent folder does not exist yet
            write_results_csv(str(path), records, RESULT_COLUMNS)

            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.assertEqual(reader.fieldnames, RESULT_COLUMNS)
                rows = list(reader)

        self.assertEqual(len(rows), 2)
        self.assertEqual([r["method"] for r in rows], ["cover", "locate"])
        self.assertEqual(int(rows[0]["tests"]), records[0]["tests"])
        self.assertEqual(int(rows[1]["localized"]), records[1]["localized"])


if __name__ == "__main__":
    unittest.main()
