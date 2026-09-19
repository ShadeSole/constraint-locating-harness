import time

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

from .io import load_model, write_results_csv

MODEL_PATH = "examples/model.json"
RESULTS_PATH = "results/v0_2_results.csv"
STRENGTH = 2

RESULT_COLUMNS = [
    "model",
    "strength",
    "method",
    "tests",
    "interactions",
    "covered",
    "coverage_rate",
    "ambiguous_pairs",
    "localized",
    "total",
    "localization_rate",
    "generation_seconds",
    "evaluation_seconds",
]

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
    start = time.perf_counter()
    covered, feasible = coverage_of(suite, interactions)
    localized, total = evaluate_suite(suite, interactions)
    evaluation_seconds = time.perf_counter() - start
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
        "evaluation_seconds": evaluation_seconds,
    }

def run_method(model, method, generator, configs, interactions, strength):
    """Generate a suite (timed), then evaluate it (timed inside evaluate_method)."""
    start = time.perf_counter()
    suite = generator(configs, interactions, strength=strength)
    generation_seconds = time.perf_counter() - start

    result = evaluate_method(method, suite, interactions)
    result["generation_seconds"] = generation_seconds
    result["model"] = model
    result["strength"] = strength
    return result

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
    print("Generation time:", f"{result['generation_seconds']:.4f} s")
    print("Evaluation time:", f"{result['evaluation_seconds']:.4f} s")

def main():

    parameters, forbidden = load_model(
        MODEL_PATH
    )

    configs = valid_configurations(
        parameters,
        forbidden
    )

    interactions = feasible_interactions(
        configs,
        strength=STRENGTH
    )

    print("Valid configurations:", len(configs))
    print("Feasible interactions:", len(interactions))

    cover_result = run_method(
        MODEL_PATH,
        "cover",
        greedy_covering_suite,
        configs,
        interactions,
        strength=STRENGTH
    )
    print_report("COVERING SUITE", cover_result)

    locate_result = run_method(
        MODEL_PATH,
        "locate",
        greedy_locating_suite,
        configs,
        interactions,
        strength=STRENGTH
    )
    print_report("LOCATING SUITE", locate_result)

    write_results_csv(
        RESULTS_PATH,
        [cover_result, locate_result],
        RESULT_COLUMNS
    )
    print()
    print("Wrote results:", RESULTS_PATH)

if __name__ == "__main__":
    main()