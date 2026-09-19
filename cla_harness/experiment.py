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

MODEL_PATHS = [
    "examples/model.json",
    "examples/my_model.json",
]
RESULTS_PATH = "results/v0_2_results.csv"
STRENGTH = 2

RESULT_COLUMNS = [
    "model",
    "strength",
    "valid_configs",
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

def run_model(model_path, strength):
    """Run both methods on one model and return their two result records."""
    parameters, forbidden = load_model(model_path)
    configs = valid_configurations(parameters, forbidden)
    interactions = feasible_interactions(configs, strength=strength)

    print()
    print("=" * 60)
    print("MODEL:", model_path)
    print("Valid configurations:", len(configs))
    print("Feasible interactions:", len(interactions))

    results = []
    methods = [
        ("cover", "COVERING SUITE", greedy_covering_suite),
        ("locate", "LOCATING SUITE", greedy_locating_suite),
    ]
    for method, title, generator in methods:
        result = run_method(
            model_path,
            method,
            generator,
            configs,
            interactions,
            strength=strength
        )
        result["valid_configs"] = len(configs)
        print_report(title, result)
        results.append(result)

    return results

def print_summary(rows):
    print()
    print("=" * 60)
    print("SUMMARY")
    print(f"{'model':<28}{'method':<8}{'tests':>6}{'amb.pairs':>11}{'localized':>12}")
    for r in rows:
        localized = f"{r['localized']}/{r['total']}"
        print(
            f"{r['model']:<28}{r['method']:<8}{r['tests']:>6}"
            f"{r['ambiguous_pairs']:>11}{localized:>12}"
        )

def main():

    rows = []
    for model_path in MODEL_PATHS:
        rows.extend(run_model(model_path, STRENGTH))

    print_summary(rows)

    write_results_csv(
        RESULTS_PATH,
        rows,
        RESULT_COLUMNS
    )
    print()
    print("Wrote results:", RESULTS_PATH)

if __name__ == "__main__":
    main()
