import random
import unittest
from itertools import combinations
from pathlib import Path

from cla_harness.core import contains_interaction, feasible_interactions, valid_configurations
from cla_harness.io import load_model
from cla_harness.multifault import MultiFaultModel, anneal_multifault, find_small_multifault

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def load(name, t=2):
    params, forbidden = load_model(str(EXAMPLES / name))
    configs = valid_configurations(params, forbidden)
    return configs, feasible_interactions(configs, t)


def brute_force_cost(configs, interactions, suite_positions, d):
    """The definition, written out with sets of interactions instead of bit masks."""
    suite = [configs[k] for k in suite_positions]
    interactions = list(interactions)
    fault_sets = [frozenset([i]) for i in interactions]
    if d == 2:
        fault_sets += [frozenset(p) for p in combinations(interactions, 2)]

    def signature(tests, fault_set):
        return tuple(any(contains_interaction(c, i) for i in fault_set) for c in tests)

    uncovered = sum(1 for i in interactions if not any(contains_interaction(c, i) for c in suite))
    # one representative per full signature, as in the module's docstring
    classes = {}
    for s in fault_sets:
        classes.setdefault(signature(configs, s), s)
    reps = list(classes.values())
    collisions = sum(1 for a, b in combinations(reps, 2) if signature(suite, a) == signature(suite, b))
    return uncovered, collisions


class MultiFaultCost(unittest.TestCase):
    def test_cost_matches_the_definition_on_random_suites(self):
        for name in ("model.json", "model_high_constraints.json", "my_model.json"):
            configs, interactions = load(name)
            for d in (1, 2):
                model = MultiFaultModel(configs, interactions, d)
                rng = random.Random(0)
                for _ in range(5):
                    positions = rng.sample(range(len(configs)), rng.randint(1, len(configs)))
                    got = model.cost(sum(1 << k for k in positions))
                    self.assertEqual((got["uncovered"], got["avoidable_collisions"]),
                                     brute_force_cost(configs, interactions, positions, d), (name, d, positions))

    def test_all_valid_configurations_have_cost_zero(self):
        configs, interactions = load("model_6param.json")
        model = MultiFaultModel(configs, interactions, 2)
        self.assertEqual(model.cost((1 << len(configs)) - 1)["cost"], 0)

    def test_d_must_be_1_or_2(self):
        configs, interactions = load("model.json")
        with self.assertRaises(ValueError):
            MultiFaultModel(configs, interactions, 3)


class MultiFaultSearch(unittest.TestCase):
    def test_search_reaches_the_exact_minima(self):
        # Exact minima from scripts/item65_exact.py (MaxSAT), recorded in docs/PROJECT_NOTES.md (item 65).
        for name, d, minimum in (("model.json", 1, 9), ("model.json", 2, 17),
                                 ("model_high_constraints.json", 2, 11), ("my_model.json", 2, 17)):
            configs, interactions = load(name)
            model = MultiFaultModel(configs, interactions, d)
            result = find_small_multifault(model, len(configs), seed=0, steps_per_restart=2000, restarts=3)
            self.assertEqual(result["size"], minimum, (name, d))
            chosen = sum(1 << k for k in result["indices"])
            self.assertEqual(model.cost(chosen)["cost"], 0)

    def test_annealing_is_reproducible(self):
        configs, interactions = load("my_model.json")
        model = MultiFaultModel(configs, interactions, 2)
        a = anneal_multifault(model, 18, seed=3, max_steps=300)
        b = anneal_multifault(model, 18, seed=3, max_steps=300)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
