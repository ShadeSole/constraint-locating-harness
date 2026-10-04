import os
import tempfile
import unittest
from pathlib import Path

from cla_harness.core import valid_configurations
from cla_harness.io import load_casa_model

# Real benchmark file, kept OUTSIDE this repository (it belongs to other authors).
# Override with the CCAG_BENCHMARK_DIR environment variable.
BENCHMARK_DIR = Path(
    os.environ.get(
        "CCAG_BENCHMARK_DIR",
        Path(__file__).resolve().parent.parent.parent / "external" / "CCAG" / "benchmark",
    )
)


def write_casa(directory, model_text, constraints_text):
    model = Path(directory) / "m.model"
    model.write_text(model_text, encoding="utf-8")
    (Path(directory) / "m.constraints").write_text(constraints_text, encoding="utf-8")
    return str(model)


# Three parameters with 2, 2 and 3 values. Value indices:
#   P0: 0,1   P1: 2,3   P2: 4,5,6
TINY_MODEL = "2\n3\n2 2 3\n"


class LoadCasaByHand(unittest.TestCase):
    def load(self, constraints_text, model_text=TINY_MODEL):
        with tempfile.TemporaryDirectory() as d:
            return load_casa_model(write_casa(d, model_text, constraints_text))

    def test_parameters_are_named_and_numbered(self):
        parameters, forbidden = self.load("0\n")
        self.assertEqual(
            parameters,
            {"P0": ["0", "1"], "P1": ["0", "1"], "P2": ["0", "1", "2"]},
        )
        self.assertEqual(forbidden, [])

    def test_two_literal_clause_forbids_that_pair(self):
        # "- 1 - 3" forbids P0=1 together with P1=1.
        parameters, forbidden = self.load("1\n2\n- 1 - 3\n")
        self.assertEqual(len(forbidden), 1)
        self.assertEqual(
            dict(forbidden[0].terms), {"P0": "1", "P1": "1"}
        )
        # 2*2*3 = 12 raw; the 3 configurations with P0=1,P1=1 are removed.
        self.assertEqual(len(valid_configurations(parameters, forbidden)), 9)

    def test_three_literal_clause(self):
        # "- 0 - 2 - 6" forbids P0=0, P1=0, P2=2: exactly one configuration.
        parameters, forbidden = self.load("1\n3\n- 0 - 2 - 6\n")
        self.assertEqual(
            dict(forbidden[0].terms), {"P0": "0", "P1": "0", "P2": "2"}
        )
        self.assertEqual(len(valid_configurations(parameters, forbidden)), 11)

    def test_clause_on_one_parameter_is_never_violated_and_is_skipped(self):
        # "- 0 - 1" names P0=0 and P0=1: no configuration can contain both.
        parameters, forbidden = self.load("1\n2\n- 0 - 1\n")
        self.assertEqual(forbidden, [])
        self.assertEqual(len(valid_configurations(parameters, forbidden)), 12)

    def test_two_clauses_overlap_by_inclusion_exclusion(self):
        # Forbid (P0=1,P1=1) -> 3 configs and (P1=1,P2=0) -> 2 configs;
        # both hold in exactly 1 config (P0=1,P1=1,P2=0): 12 - 3 - 2 + 1 = 8.
        parameters, forbidden = self.load("2\n2\n- 1 - 3\n2\n- 3 - 4\n")
        self.assertEqual(len(valid_configurations(parameters, forbidden)), 8)

    def test_positive_literal_is_rejected(self):
        with self.assertRaises(ValueError):
            self.load("1\n2\n+ 1 - 3\n")

    def test_index_out_of_range_is_rejected(self):
        with self.assertRaises(ValueError):
            self.load("1\n2\n- 1 - 7\n")  # only indices 0..6 exist

    def test_value_count_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            self.load("0\n", model_text="2\n3\n2 2\n")

    def test_extra_content_is_rejected(self):
        with self.assertRaises(ValueError):
            self.load("1\n2\n- 1 - 3\n2\n- 0\n")


@unittest.skipUnless(
    (BENCHMARK_DIR / "spins.model").exists(),
    "CCAG benchmark files not found (set CCAG_BENCHMARK_DIR)",
)
class LoadRealSpinsBenchmark(unittest.TestCase):
    def setUp(self):
        self.parameters, self.forbidden = load_casa_model(
            str(BENCHMARK_DIR / "spins.model")
        )

    def test_structure_matches_the_file(self):
        counts = [len(v) for v in self.parameters.values()]
        self.assertEqual(counts, [2] * 13 + [4] * 5)
        self.assertEqual(len(self.forbidden), 13)
        self.assertTrue(all(len(r.terms) == 2 for r in self.forbidden))

    def test_valid_configuration_count_matches_independent_calculation(self):
        # 2,002,944 valid configurations out of 8,388,608 raw. Obtained from
        # the raw files by two independent methods (a pruned depth-first count
        # and inclusion-exclusion over the 13 clauses), neither using this
        # loader. Counting here uses its own depth-first search so the 2
        # million configurations are never stored.
        names = list(self.parameters)
        sizes = [len(self.parameters[n]) for n in names]
        position = {n: i for i, n in enumerate(names)}
        rules_by_last = {}
        for rule in self.forbidden:
            terms = [(position[n], int(v)) for n, v in rule.terms]
            rules_by_last.setdefault(max(i for i, _ in terms), []).append(terms)

        assign = [None] * len(names)

        def count(i):
            if i == len(names):
                return 1
            total = 0
            for v in range(sizes[i]):
                assign[i] = v
                if any(all(assign[a] == b for a, b in r) for r in rules_by_last.get(i, [])):
                    continue
                total += count(i + 1)
            return total

        self.assertEqual(count(0), 2002944)


if __name__ == "__main__":
    unittest.main()
