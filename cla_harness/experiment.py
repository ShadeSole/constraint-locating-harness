from .core import (
    valid_configurations,
    feasible_interactions
)

from .generator import (
    greedy_covering_suite,
    greedy_locating_suite
)

from .localizer import (
    run_suite,
    localize_exact
)

from .io import load_model

def evaluate_suite(suite, interactions):

    total = 0
    correctly_localized = 0

    for fault in interactions:

        outcomes = run_suite(suite, fault)

        candidates = localize_exact(
            suite,
            outcomes,
            interactions
        )

        total += 1

        if len(candidates) == 1 and candidates[0] == fault:
            correctly_localized += 1

    return correctly_localized, total

def main():

    parameters, forbidden = load_model(
        "examples/model.json"
    )

    configs = valid_configurations(
    parameters,
    forbidden
    )

    interactions = feasible_interactions(
        configs,
        strength=2
    )

    print("Valid configurations:", len(configs))
    print("Feasible interactions:", len(interactions))

    cover_suite = greedy_covering_suite(
            configs,
            interactions,
            strength=2
    )

    print("Covering suite tests:", len(cover_suite))

    cover_correct, total = evaluate_suite(
        cover_suite,
        interactions
    )

    print(
        "Covering suite localized:",
        cover_correct,
        "/",
        total
    )

    cover_rate = cover_correct / total
    print("Covering localization rate:",f"{cover_rate:.2%}")

    
if __name__ == "__main__":
    main()