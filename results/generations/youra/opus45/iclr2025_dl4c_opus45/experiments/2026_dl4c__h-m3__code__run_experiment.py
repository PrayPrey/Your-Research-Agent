#!/usr/bin/env python3
"""H-M3 Experiment: LlmFix 19-Cause Fine-Grained Error Taxonomy Analysis.

This experiment tests whether DPO preference optimization concentrates
failures in execution errors at fine-grained LlmFix 19-cause taxonomy level
(Cramer's V > 0.03).

Gate: SHOULD_WORK
"""

import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from data_loader import load_he1_results, extract_failures, validate_data_integrity
from classifier import classify_batch
from analyze import run_analysis, save_outputs
from visualize import generate_all_figures


def main() -> None:
    """Orchestrate full H-M3 experiment pipeline.

    Steps:
    1. Load H-E1 execution results
    2. Extract failures and validate counts
    3. Classify at coarse + fine granularity
    4. Run dual-granularity statistical analysis
    5. Generate all figures
    6. Print gate result
    """
    print("=" * 60)
    print("H-M3: LlmFix 19-Cause Fine-Grained Error Taxonomy Analysis")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    # 1. Load H-E1 results
    print("=== Step 1: Loading H-E1 Data ===")
    try:
        rl_results, dpo_results = load_he1_results(CONFIG)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("H-E1 data not found. Please run H-E1 experiment first.")
        sys.exit(1)

    # 2. Extract failures
    print("\n=== Step 2: Extracting Failures ===")
    rl_failures = extract_failures(rl_results)
    dpo_failures = extract_failures(dpo_results)
    print(f"RL failures: {len(rl_failures)}")
    print(f"DPO failures: {len(dpo_failures)}")

    # Validate data integrity
    valid = validate_data_integrity(rl_failures, dpo_failures, CONFIG)
    if not valid:
        print("WARNING: Data integrity check failed, but continuing...")

    # 3. Classify at dual granularity
    print("\n=== Step 3: Classifying Errors ===")
    rl_classified = classify_batch(rl_failures)
    dpo_classified = classify_batch(dpo_failures)
    print(f"Classified {len(rl_classified)} RL failures")
    print(f"Classified {len(dpo_classified)} DPO failures")

    # Show sample classifications
    print("\nSample RL classifications:")
    for r in rl_classified[:3]:
        print(f"  {r['task_id']}: {r['coarse_category']} -> {r['fine_cause']}")

    print("\nSample DPO classifications:")
    for r in dpo_classified[:3]:
        print(f"  {r['task_id']}: {r['coarse_category']} -> {r['fine_cause']}")

    # 4. Run statistical analysis
    print("\n=== Step 4: Running Statistical Analysis ===")
    metrics = run_analysis(rl_classified, dpo_classified, CONFIG)

    # 5. Save outputs
    print("\n=== Step 5: Saving Outputs ===")
    all_classified = rl_classified + dpo_classified
    save_outputs(all_classified, metrics, CONFIG)

    # 6. Generate figures
    print("\n=== Step 6: Generating Figures ===")
    cause_labels = metrics["fine"]["cause_labels"]
    generate_all_figures(rl_classified, dpo_classified, metrics, cause_labels, CONFIG)

    # 7. Print results summary
    print("\n" + "=" * 60)
    print("H-M3 EXPERIMENT RESULTS")
    print("=" * 60)

    print("\n--- Coarse Analysis (3-tier) ---")
    print(f"  Chi-square: {metrics['coarse']['chi2']:.4f}")
    print(f"  p-value: {metrics['coarse']['p_value']:.2e}")
    print(f"  Cramer's V: {metrics['coarse']['cramers_v']:.4f}")

    print("\n--- Fine Analysis (19-cause) ---")
    print(f"  Chi-square: {metrics['fine']['chi2']:.4f}")
    print(f"  p-value: {metrics['fine']['p_value']:.2e}")
    print(f"  Cramer's V: {metrics['fine']['cramers_v']:.4f}")
    print(f"  Active causes: {len(cause_labels)}")

    print("\n--- Direction Check ---")
    print(f"  RL syntax+runtime: {metrics['direction']['rl_syntax_runtime_prop']:.2%}")
    print(f"  DPO syntax+runtime: {metrics['direction']['dpo_syntax_runtime_prop']:.2%}")
    print(f"  Direction satisfied (DPO > RL): {metrics['direction']['direction_satisfied']}")

    print("\n--- GATE EVALUATION (SHOULD_WORK) ---")
    gate = metrics["gate_result"]
    print(f"  Cramer's V threshold: {gate['cramers_v_threshold']}")
    print(f"  Cramer's V actual: {gate['cramers_v_actual']:.4f}")
    print(f"  p-value threshold: {gate['p_value_threshold']}")
    print(f"  p-value actual: {gate['p_value_actual']:.2e}")
    print(f"  Direction satisfied: {gate['direction_satisfied']}")

    gate_pass = gate["gate_pass"]
    print("\n" + "=" * 60)
    if gate_pass:
        print("GATE RESULT: *** PASS ***")
        print("Effect persists at fine-grained 19-cause taxonomy level")
    else:
        print("GATE RESULT: *** FAIL ***")
        print("Effect does NOT persist at fine-grained taxonomy level")
        if gate["cramers_v_actual"] < gate["cramers_v_threshold"]:
            print(f"  - Cramer's V ({gate['cramers_v_actual']:.4f}) < threshold ({gate['cramers_v_threshold']})")
        if gate["p_value_actual"] >= gate["p_value_threshold"]:
            print(f"  - p-value ({gate['p_value_actual']:.2e}) >= threshold ({gate['p_value_threshold']})")
    print("=" * 60)

    print(f"\nCompleted: {datetime.now().isoformat()}")

    # Return exit code based on gate result
    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    main()
