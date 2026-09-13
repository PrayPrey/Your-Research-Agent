#!/usr/bin/env python3
"""
Main Experiment Runner - h-e1
Execute full contractability analysis pipeline.
"""
import sys
import os

# Add code directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data.corpus_loader import DefectCorpusLoader
from contracts.generator import ContractGenerator
from contracts.validator import ContractValidator
from analysis.retrospective_coder import RetrospectiveCoder
from analysis.metrics import MetricsCalculator
from visualization.plots import Visualizer
import pandas as pd
import json
from datetime import datetime


# Configuration from 03_config.md
CONFIG = {
    "random_seed": 42,
    "validation_timeout": 10,
    "pytorch_versions": ["1.11", "1.12", "1.13"],
    "confidence_level": 0.95,
    "gate_conditions": {
        "min_contractability_rate": 40.0,
        "min_kappa": 0.7,
        "max_execution_time": 10
    }
}


def main():
    """Execute full experiment pipeline."""
    print("=" * 80)
    print("API Contract Validation Framework - h-e1")
    print("Hypothesis: ≥40% of environment-stage API defects are contractable")
    print("=" * 80)

    # Create output directories
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
    figures_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    # 1. Load defect corpus (T-01)
    print("\n[1/7] Loading defect corpus...")
    loader = DefectCorpusLoader()
    defects = loader.load_corpus()
    filtered = loader.filter_environment_api_defects(defects)
    categorized = loader.categorize_defects(filtered)

    # 2. Generate contracts (T-02)
    print("\n[2/7] Generating contracts...")
    generator = ContractGenerator()
    contracts = []
    contract_map = {}  # defect_id -> contract

    for idx, defect in categorized.iterrows():
        contract = generator.generate_from_defect(defect)
        contracts.append(contract)
        if contract:
            contract_map[defect['defect_id']] = contract

    expressible_count = sum(1 for c in contracts if c is not None)
    print(f"Generated {expressible_count}/{len(contracts)} expressible contracts")

    # 3. Validate contracts (T-03)
    print("\n[3/7] Validating contracts...")
    validator = ContractValidator(timeout=CONFIG["validation_timeout"])

    validation_results = []
    for contract in contracts:
        if contract:
            result = validator.validate_contract(contract)
            validation_results.append(result)
        else:
            validation_results.append(None)

    pass_count = sum(1 for r in validation_results if r and r.status == "PASS")
    fail_count = sum(1 for r in validation_results if r and r.status == "FAIL")
    timeout_count = sum(1 for r in validation_results if r and r.status == "TIMEOUT")

    print(f"Validation: PASS={pass_count}, FAIL={fail_count}, TIMEOUT={timeout_count}")

    # 4. Version stability testing (T-03)
    print("\n[4/7] Testing version stability...")
    stability_results = []
    stability_map = {}

    for contract in contracts:
        if contract:
            stability = validator.check_version_stability(
                contract,
                versions=CONFIG["pytorch_versions"]
            )
            stability_results.append(stability)
            stability_map[contract.defect_id] = stability
        else:
            stability_results.append({})

    # 5. Retrospective coding (T-04)
    print("\n[5/7] Applying retrospective coding protocol...")

    # Filter to only valid contracts with results
    valid_indices = [
        i for i, (c, r) in enumerate(zip(contracts, validation_results))
        if c is not None and r is not None
    ]

    valid_contracts = [contracts[i] for i in valid_indices]
    valid_results = [validation_results[i] for i in valid_indices]
    valid_stability = [stability_results[i] for i in valid_indices]
    valid_defects = categorized.iloc[valid_indices].reset_index(drop=True)
    valid_types = valid_defects['type'].tolist()

    coder = RetrospectiveCoder(valid_defects, random_seed=CONFIG["random_seed"])
    coder1_labels, coder2_labels = coder.code_corpus(
        valid_contracts,
        valid_results,
        valid_stability
    )

    print(f"Coder 1 contractable: {sum(coder1_labels)}/{len(coder1_labels)}")
    print(f"Coder 2 contractable: {sum(coder2_labels)}/{len(coder2_labels)}")

    # 6. Calculate metrics (T-05)
    print("\n[6/7] Calculating contractability metrics...")
    calc = MetricsCalculator()
    metrics = calc.calculate_contractability_rate(
        coder1_labels,
        coder2_labels,
        valid_types
    )

    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(f"Overall Contractability: {metrics.overall_rate:.1f}%")
    print(f"  95% CI: [{metrics.ci_lower:.1f}%, {metrics.ci_upper:.1f}%]")
    print(f"\nStratified by Type:")
    print(f"  Structural:   {metrics.structural_rate:.1f}%")
    print(f"  Metamorphic:  {metrics.metamorphic_rate:.1f}%")
    print(f"  Composition:  {metrics.composition_rate:.1f}%")
    print(f"\nInter-Rater Reliability:")
    print(f"  Cohen's Kappa: {metrics.kappa:.3f}")
    print(f"\nGate Evaluation:")
    print(f"  Status: {metrics.gate_status}")
    print(f"  Threshold: ≥40% (CI lower >35%)")
    print(f"  Kappa Threshold: ≥0.7")

    baselines = calc.compare_to_baselines(metrics.overall_rate)
    print(f"\nBaseline Comparison:")
    print(f"  No-CI Baseline:    {baselines['no_ci_baseline']:.1f}%")
    print(f"  CI-Only Baseline:  {baselines['ci_only_baseline']:.1f}%")
    print(f"  Proposed:          {baselines['proposed']:.1f}%")
    print(f"  Improvement:       +{baselines['improvement_over_ci']:.1f}%")
    print(f"{'='*60}\n")

    # 7. Generate visualizations (T-06)
    print("[7/7] Generating visualizations...")
    viz = Visualizer(output_dir=figures_dir)

    viz.plot_gate_metrics(metrics)
    viz.plot_defect_distribution(categorized)
    viz.plot_execution_times([r for r in validation_results if r])
    viz.plot_version_stability(stability_map)
    viz.plot_kappa_heatmap(coder1_labels, coder2_labels)

    # Save results
    results = {
        "hypothesis_id": "h-e1",
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "overall_rate": float(metrics.overall_rate),
            "ci_lower": float(metrics.ci_lower),
            "ci_upper": float(metrics.ci_upper),
            "structural_rate": float(metrics.structural_rate),
            "metamorphic_rate": float(metrics.metamorphic_rate),
            "composition_rate": float(metrics.composition_rate),
            "kappa": float(metrics.kappa),
            "gate_status": metrics.gate_status
        },
        "corpus_stats": {
            "total_defects": len(categorized),
            "expressible_contracts": expressible_count,
            "validated_contracts": len(valid_results)
        },
        "validation_stats": {
            "pass": pass_count,
            "fail": fail_count,
            "timeout": timeout_count
        },
        "baselines": baselines
    }

    results_path = os.path.join(output_dir, 'results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {results_path}")
    print(f"Figures saved to: {figures_dir}")

    # Gate verdict
    print("\n" + "=" * 80)
    if metrics.gate_status == "PASS":
        print("✓ HYPOTHESIS h-e1 VALIDATED")
        print(f"  Contractability rate {metrics.overall_rate:.1f}% exceeds 40% threshold")
        print(f"  Cohen's kappa {metrics.kappa:.3f} exceeds 0.7 threshold")
    else:
        print("✗ HYPOTHESIS h-e1 FAILED")
        print("  Recommend: Pivot to structural-only contracts with reduced scope")
    print("=" * 80)

    return metrics.gate_status == "PASS"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
