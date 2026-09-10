
from __future__ import annotations
import argparse
from pathlib import Path
from .core import valid_configurations, feasible_interactions, interaction_label
from .generator import greedy_covering_suite, greedy_locating_suite, ambiguous_pairs
from .localizer import run_suite, localize_exact, rank_noisy, report_candidates
from .io import load_model, interaction_from_text, write_suite_csv

def build(model_path: str, mode: str, strength: int, output: str):
    parameters, forbidden = load_model(model_path)
    configs = valid_configurations(parameters, forbidden)
    interactions = feasible_interactions(configs, strength)
    if mode == "cover":
        suite = greedy_covering_suite(configs, interactions, strength)
    else:
        suite = greedy_locating_suite(configs, interactions, strength)
    write_suite_csv(output, suite)
    amb = ambiguous_pairs(suite, interactions)
    print(f"All configurations: {__import__('math').prod(len(v) for v in parameters.values())}")
    print(f"Valid configurations: {len(configs)}")
    print(f"Feasible {strength}-way interactions: {len(interactions)}")
    print(f"Selected tests: {len(suite)}")
    print(f"Ambiguous interaction pairs: {len(amb)}")
    print(f"Wrote suite: {output}")
    return suite, interactions

def main():
    p = argparse.ArgumentParser(description="Constraint-aware locating-array / fault-localization harness")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Generate a covering or locating test suite")
    b.add_argument("model")
    b.add_argument("--mode", choices=["cover", "locate"], default="locate")
    b.add_argument("--strength", type=int, default=2)
    b.add_argument("--output", default="suite.csv")

    d = sub.add_parser("demo", help="Build suite, inject a fault, and localize it")
    d.add_argument("model")
    d.add_argument("--fault", nargs="+", required=True, help='e.g. Auth=CAC Database=Remote')
    d.add_argument("--mode", choices=["cover", "locate"], default="locate")
    d.add_argument("--strength", type=int, default=2)

    args = p.parse_args()
    if args.cmd == "build":
        build(args.model, args.mode, args.strength, args.output)
    elif args.cmd == "demo":
        suite, interactions = build(args.model, args.mode, args.strength, "suite.csv")
        fault = interaction_from_text(args.fault)
        if fault not in interactions:
            raise SystemExit("Fault is not a feasible interaction in this model.")
        outcomes = run_suite(suite, fault)
        print("Outcomes (1=FAIL, 0=PASS):", "".join(map(str, outcomes)))
        candidates = localize_exact(suite, outcomes, interactions)
        print(report_candidates(candidates))
        if len(candidates) != 1:
            print("Closest candidates:")
            for interaction, distance in rank_noisy(suite, outcomes, interactions)[:5]:
                print(f"  distance={distance}: {interaction_label(interaction)}")

if __name__ == "__main__":
    main()
