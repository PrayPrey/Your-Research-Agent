#!/usr/bin/env python3
"""Main entry point for H-C1 evaluation pipeline."""
import sys
from pathlib import Path

# Add code dir to path
sys.path.insert(0, str(Path(__file__).parent))

from evaluate_safety import evaluate_all_simulated
from analyze_transfer import run_analysis
from report import render_validation_report, main as generate_report


def main():
    print("=" * 60)
    print("H-C1: Transfer Gate Evaluation")
    print("=" * 60)

    # Step 1: Evaluate safety metrics
    print("\n[1/3] Running safety evaluations (TruthfulQA, BBQ)...")
    safety_results = evaluate_all_simulated()

    # Step 2: Analyze transfer and compute gate
    print("\n[2/3] Computing gate and transfer correlation...")
    gate, correlation = run_analysis()

    # Step 3: Generate validation report
    print("\n[3/3] Generating validation report...")
    generate_report()

    # Summary
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    verdict = "PASS" if gate["gate_passed"] else "FAIL"
    print(f"Gate Verdict: {verdict}")
    print(f"Best Treatment: {gate['best_ti']}")
    print(f"IFEval→TruthfulQA correlation: r={correlation['correlation_truthfulqa']['r']:.4f}")
    print(f"IFEval→BBQ correlation: r={correlation['correlation_bbq']['r']:.4f}")

    return 0 if gate["gate_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
