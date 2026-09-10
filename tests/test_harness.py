
import unittest
from cla_harness.core import Forbidden, valid_configurations, feasible_interactions, interactions_of
from cla_harness.generator import greedy_locating_suite
from cla_harness.localizer import run_suite, localize_exact

class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.parameters = {
            "Auth": ["Password", "CAC"],
            "Network": ["WiFi", "Ethernet"],
            "Encryption": ["On", "Off"],
            "Logging": ["On", "Off"],
            "Database": ["Local", "Remote"],
        }
        self.rules = [
            Forbidden.from_dict({"Auth": "CAC", "Encryption": "Off"}),
            Forbidden.from_dict({"Database": "Remote", "Network": "WiFi"}),
        ]

    def test_interaction_count(self):
        c = {"A":"0", "B":"0", "C":"0", "D":"0", "E":"0"}
        self.assertEqual(len(interactions_of(c, 2)), 10)

    def test_constraints(self):
        configs = valid_configurations(self.parameters, self.rules)
        self.assertTrue(all(not (c["Auth"]=="CAC" and c["Encryption"]=="Off") for c in configs))
        self.assertTrue(all(not (c["Database"]=="Remote" and c["Network"]=="WiFi") for c in configs))

    def test_localization(self):
        configs = valid_configurations(self.parameters, self.rules)
        interactions = feasible_interactions(configs, 2)
        suite = greedy_locating_suite(configs, interactions, 2)
        fault = frozenset({("Auth","CAC"), ("Database","Remote")})
        outcomes = run_suite(suite, fault)
        candidates = localize_exact(suite, outcomes, interactions)
        self.assertIn(fault, candidates)

if __name__ == "__main__":
    unittest.main()
