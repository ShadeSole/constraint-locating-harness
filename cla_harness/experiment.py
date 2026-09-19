from .core import (
    valid_configurations,
    feasible_interactions,
    contains_interaction
)

from .generator import (
    greedy_covering_suite,
    greedy_locating_suite,
    ambiguous_pairs
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
def coverage_of(suite, interactions):
    """Count feasible interactions appearing in at least one test of the suite."""
    covered = 0
    for interaction in interactions:
        if any(contains_interaction(test, interaction) for test in suite):
            covered += 1
    return covered, len(interactions)

def evaluate_method(method, suite, interactions):
    """Collect all V0.2 metrics for one suite into a single record."""
    covered, feasible = coverage_of(suite, interactions)
    localized, total = evaluate_suite(suite, interactions)
    return {
        "method": method,
        "tests": len(suite),
        "interactions": feasible,
        "covered": covered,
        "coverage_rate": covered / feasible,
        "ambiguous_pairs": len(ambiguous_pairs(suite, interactions)),
        "localized": localized,
        "total": total,
        "localization_rate": localized / total,
    }

def print_report(title, result):
    print()
    print(title)
    print("Tests:", result["tests"])
    print(
        "Coverage:",
        result["covered"], "/", result["interactions"],
        f"({result['coverage_rate']:.2%})"
    )
    print("Ambiguous pairs:", result["ambiguous_pairs"])
    print("Localized:", result["localized"], "/", result["total"])
    print("Localization rate:", f"{result['localization_rate']:.2%}")

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
    cover_result = evaluate_method("cover", cover_suite, interactions)
    print_report("COVERING SUITE", cover_result)

    locate_suite = greedy_locating_suite(
        configs,
        interactions,
        strength=2
    )
    locate_result = evaluate_method("locate", locate_suite, interactions)
    print_report("LOCATING SUITE", locate_result)

if __name__ == "__main__":
    main()
