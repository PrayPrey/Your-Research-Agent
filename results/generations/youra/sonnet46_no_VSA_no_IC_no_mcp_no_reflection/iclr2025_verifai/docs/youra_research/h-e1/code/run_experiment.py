#!/usr/bin/env python3
"""H-E1: Multi-Verifier Activation Measurement. Main entry point."""
import json
import os
import sys
import argparse

# Run from code/ directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, ExperimentConfig
from data_loader import load_problems
from generate_completions import generate_completions
import verifiers.smt_solver as smt_solver
from measure_activation import run_all_verifiers, compute_stats, gate_check
import visualize


def main():
    parser = argparse.ArgumentParser(description="H-E1 Multi-Verifier Activation Experiment")
    parser.add_argument("--config", default="config/experiment.yaml")
    parser.add_argument("--skip-generation", action="store_true", help="Skip LLM generation, load from cache only")
    parser.add_argument("--skip-smt", action="store_true", help="Skip SMT verifier entirely")
    args = parser.parse_args()

    cfg = load_config(args.config)

    os.makedirs(cfg.paths.results_dir, exist_ok=True)
    os.makedirs(cfg.paths.figures_dir, exist_ok=True)

    # Step 1: Load dataset
    print("\n=== Step 1: Load Dataset ===")
    problems = load_problems()
    assert len(problems) > 0, "No problems loaded!"
    print(f"Total: {len(problems)} problems")

    # Step 2: Generate completions
    print("\n=== Step 2: Generate Completions ===")
    if args.skip_generation:
        completions = {}
        if os.path.exists(cfg.paths.completions_checkpoint):
            with open(cfg.paths.completions_checkpoint) as f:
                for line in f:
                    if line.strip():
                        obj = json.loads(line)
                        completions[obj["problem_id"]] = obj["completion"]
        print(f"Loaded {len(completions)} completions from cache")
    else:
        completions = generate_completions(
            problems,
            checkpoint_path=cfg.paths.completions_checkpoint,
            model=cfg.generation.model,
            temperature=cfg.generation.temperature,
            max_tokens=cfg.generation.max_tokens,
        )

    # Step 3: SMT pilot
    smt_enabled = not args.skip_smt
    pilot_stats = None

    if smt_enabled:
        print("\n=== Step 3: SMT Pilot (20 problems) ===")
        pilot_path = cfg.paths.smt_pilot_results
        if os.path.exists(pilot_path):
            with open(pilot_path) as f:
                pilot_stats = json.load(f)
            print(f"✓ Loaded cached pilot: sat_rate={pilot_stats['sat_rate']:.1%}, passed={pilot_stats['passed_gate']}")
        else:
            pilot_stats = smt_solver.run_pilot(
                problems, completions,
                n=cfg.smt_pilot.n_problems,
                seed=cfg.smt_pilot.seed,
            )
            with open(pilot_path, "w") as f:
                json.dump(pilot_stats, f, indent=2)
            print(f"SMT pilot: sat_rate={pilot_stats['sat_rate']:.1%}, passed_gate={pilot_stats['passed_gate']}")

        if not pilot_stats["passed_gate"]:
            print(f"⚠ SMT pilot failed gate ({pilot_stats['sat_rate']:.1%} < {cfg.smt_pilot.gate_threshold:.0%}). Scoping to 3-category run.")
            smt_enabled = False
    else:
        print("\n=== Step 3: SMT Pilot SKIPPED (--skip-smt) ===")

    # Step 4: Run all verifiers
    print("\n=== Step 4: Run All Verifiers ===")
    results = run_all_verifiers(
        problems,
        completions,
        smt_enabled=smt_enabled,
        out_path=cfg.paths.verifier_results,
    )

    # Step 5: Compute stats
    print("\n=== Step 5: Compute Activation Stats ===")
    stats = compute_stats(results, problems)
    with open(cfg.paths.activation_stats, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"✓ Saved {cfg.paths.activation_stats}")

    # Step 6: Gate check
    print("\n=== Step 6: Gate Check ===")
    passed = gate_check(stats)

    # Step 7: Visualize
    print("\n=== Step 7: Visualize ===")
    visualize.plot_activation_rates(stats, out=os.path.join(cfg.paths.figures_dir, "activation_rates.png"))
    visualize.plot_overlap_matrix(stats, out=os.path.join(cfg.paths.figures_dir, "overlap_matrix.png"))
    visualize.plot_by_source(stats, out=os.path.join(cfg.paths.figures_dir, "activation_by_source.png"))
    visualize.plot_signal_length(results, out=os.path.join(cfg.paths.figures_dir, "signal_length_dist.png"))
    if pilot_stats:
        visualize.plot_smt_pilot(pilot_stats, out=os.path.join(cfg.paths.figures_dir, "smt_pilot.png"))

    # Summary
    print("\n=== SUMMARY ===")
    rates = stats["activation_rates"]
    for cat, rate in rates.items():
        print(f"  {cat}: {rate:.1%}")
    print(f"\nProblems processed: {stats['n_total']}")
    print(f"Gate result: {'PASS' if passed else 'FAIL'}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
