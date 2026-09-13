#!/usr/bin/env python3
"""
Main pipeline for h-e1: Policy-Layer Capability Decoupling Validation
Evaluates capability invariance across compliance levels (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0})
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG
from data.loader import MMLULoader, HumanEvalLoader
from models.api_client import APIModelClient, PolicyLayer
from evaluation.evaluator import MMLUEvaluator, HumanEvalEvaluator
from analysis.statistics import GateAnalyzer
from visualization.plotter import ResultsVisualizer


def setup_environment():
    """Setup output directories and verify API keys."""
    print("="*60)
    print("SETUP: Environment Initialization")
    print("="*60)

    # Create output directories
    os.makedirs(CONFIG["results_dir"], exist_ok=True)
    os.makedirs(CONFIG["figures_dir"], exist_ok=True)
    print(f"✓ Output directories created")

    # Verify API key
    if CONFIG["api_provider"] == "anthropic":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        print(f"✓ Anthropic API key found")
    elif CONFIG["api_provider"] == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
        print(f"✓ OpenAI API key found")

    print(f"✓ Model: {CONFIG['model_name']}")
    print(f"✓ Lambda values: {CONFIG['lambda_values']}")
    print()

    return CONFIG


def load_datasets():
    """Load MMLU and HumanEval datasets."""
    print("="*60)
    print("DATA: Loading Datasets")
    print("="*60)

    # Load MMLU
    mmlu_loader = MMLULoader(
        dataset_name=CONFIG["mmlu_dataset"],
        split=CONFIG["mmlu_split"],
        few_shot_n=CONFIG["mmlu_few_shot_n"]
    )
    mmlu_loader.load_dataset()

    # Try to load HumanEval (optional)
    humaneval_loader = None
    try:
        humaneval_loader = HumanEvalLoader()
        humaneval_loader.load_dataset()
    except Exception as e:
        print(f"⚠ HumanEval not available: {e}")
        print("⚠ Continuing with MMLU only")

    print()
    return mmlu_loader, humaneval_loader


def run_experiment(config, mmlu_loader, humaneval_loader):
    """Run full evaluation across all lambda values."""
    print("="*60)
    print("EXPERIMENT: Running Evaluations")
    print("="*60)

    # Initialize API client
    model_client = APIModelClient(
        model_name=config["model_name"],
        api_provider=config["api_provider"]
    )

    # Initialize evaluators
    mmlu_eval = MMLUEvaluator(model_client, mmlu_loader)
    he_eval = HumanEvalEvaluator(model_client, humaneval_loader) if humaneval_loader else None

    all_results = []

    for lambda_val in config["lambda_values"]:
        print(f"\n{'='*60}")
        print(f"Lambda = {lambda_val}")
        print(f"{'='*60}")

        # MMLU evaluation
        print(f"\n[1/{'2' if he_eval else '1'}] Running MMLU evaluation...")
        mmlu_results = mmlu_eval.evaluate(lambda_val)
        mmlu_results["dataset"] = "MMLU"
        mmlu_accuracy = mmlu_eval.compute_accuracy(mmlu_results)
        print(f"MMLU Accuracy: {mmlu_accuracy:.4f}")

        combined_results = [mmlu_results]

        # HumanEval evaluation (if available)
        if he_eval:
            print(f"\n[2/2] Running HumanEval evaluation...")
            he_results = he_eval.evaluate(lambda_val)
            he_results["dataset"] = "HumanEval"
            # Add 'subject' column with NaN for consistency with MMLU
            he_results["subject"] = None
            # Rename 'passed' to 'correct' for consistency
            he_results["correct"] = he_results["passed"]
            he_pass_rate = he_eval.compute_pass_at_k(he_results, k=1)
            print(f"HumanEval pass@1: {he_pass_rate:.4f}")
            combined_results.append(he_results)

        # Combine results
        combined = pd.concat(combined_results, ignore_index=True)
        all_results.append(combined)

        # Save checkpoint
        checkpoint_path = os.path.join(config["results_dir"], f"checkpoint_lambda_{lambda_val}.csv")
        combined.to_csv(checkpoint_path, index=False)
        print(f"✓ Checkpoint saved: {checkpoint_path}")

    # Combine all results
    final_results = pd.concat(all_results, ignore_index=True)

    # Save final results
    results_path = os.path.join(config["results_dir"], "all_results.csv")
    final_results.to_csv(results_path, index=False)
    print(f"\n✓ Final results saved: {results_path}")

    return final_results


def analyze_results(results_df, config):
    """Perform statistical analysis and gate validation."""
    print("\n" + "="*60)
    print("ANALYSIS: Statistical Validation")
    print("="*60)

    # Run gate analysis
    analyzer = GateAnalyzer(results_df)
    gate_metrics = analyzer.validate_gate()

    # Save metrics
    metrics_path = os.path.join(config["results_dir"], "gate_metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(gate_metrics, f, indent=2)
    print(f"✓ Metrics saved: {metrics_path}")

    return gate_metrics


def generate_visualizations(results_df, gate_metrics, config):
    """Generate all required figures."""
    print("\n" + "="*60)
    print("VISUALIZATION: Generating Figures")
    print("="*60)

    visualizer = ResultsVisualizer(config["figures_dir"])

    # 1. Gate metrics (MANDATORY)
    visualizer.plot_gate_metrics(gate_metrics)

    # 2. Capability consistency
    visualizer.plot_capability_consistency(results_df)

    # 3. Subject heatmap (MMLU only)
    visualizer.plot_subject_heatmap(results_df)

    # 4. Accuracy distributions
    visualizer.plot_distributions(results_df)

    print()


def generate_report(gate_metrics, results_df, config):
    """Generate 04_validation.md report."""
    print("="*60)
    print("REPORT: Generating Validation Document")
    print("="*60)

    report_path = os.path.join("..", "04_validation.md")

    # Build report content
    report = f"""---
hypothesis_id: h-e1
validation_date: {datetime.now().strftime('%Y-%m-%d')}
gate_type: MUST_WORK
gate_result: {'PASS' if gate_metrics['overall_pass'] else 'FAIL'}
---

# Validation Report: h-e1

**Hypothesis Statement:** Under conditions where Constitutional AI or system-prompted LLMs are evaluated across multiple compliance strength levels (λ ∈ {{0.2, 0.4, 0.6, 0.8, 1.0}}), if base model capability is held frozen while policy-layer rules are varied, then base capability metrics (MMLU, HumanEval) will remain invariant (ICC > 0.95, ANOVA p > 0.05), because the architectural separation between base weights and policy layer allows compliance modulation without capability degradation.

**Gate Type:** MUST_WORK
**Gate Condition:** (ICC > 0.95) AND (ANOVA p > 0.05) AND (Cohen's f < 0.10)

---

## Gate Results

### 1. ICC (Intraclass Correlation Coefficient)
- **Value:** {gate_metrics['icc']['value']:.4f}
- **95% CI Lower:** {gate_metrics['icc']['ci_lower']:.4f}
- **Threshold:** > {gate_metrics['icc']['threshold']}
- **Status:** {'✓ PASS' if gate_metrics['icc']['passed'] else '✗ FAIL'}

### 2. ANOVA p-value
- **F-statistic:** {gate_metrics['anova_p']['f_stat']:.4f} (df1={gate_metrics['anova_p']['df1']}, df2={gate_metrics['anova_p']['df2']})
- **p-value:** {gate_metrics['anova_p']['value']:.4f}
- **Threshold:** > {gate_metrics['anova_p']['threshold']}
- **Status:** {'✓ PASS' if gate_metrics['anova_p']['passed'] else '✗ FAIL'}

### 3. Cohen's f (Effect Size)
- **Value:** {gate_metrics['cohens_f']['value']:.4f}
- **Threshold:** < {gate_metrics['cohens_f']['threshold']}
- **Status:** {'✓ PASS' if gate_metrics['cohens_f']['passed'] else '✗ FAIL'}

---

## Overall Gate Decision

**Result:** {'✓✓✓ PASS ✓✓✓' if gate_metrics['overall_pass'] else '✗✗✗ FAIL ✗✗✗'}

{'The hypothesis is validated. Base capability metrics remain invariant across compliance levels, confirming architectural separation between policy-layer and capability-layer.' if gate_metrics['overall_pass'] else 'The hypothesis is NOT validated. Base capability shows significant variation across compliance levels, suggesting lack of architectural separation.'}

---

## Experimental Results

### Dataset Statistics
- **MMLU:** {len(results_df[results_df['dataset'] == 'MMLU'])} questions across 57 subjects
- **HumanEval:** {len(results_df[results_df['dataset'] == 'HumanEval'])} coding problems
- **Compliance Levels:** {len(results_df['lambda'].unique())} conditions (λ = {', '.join(map(str, sorted(results_df['lambda'].unique())))})

### Accuracy by Compliance Level
"""

    # Add accuracy table
    for lam in sorted(results_df["lambda"].unique()):
        lam_data = results_df[results_df["lambda"] == lam]
        mmlu_acc = lam_data[lam_data["dataset"] == "MMLU"]["correct"].mean()
        he_acc = lam_data[lam_data["dataset"] == "HumanEval"]["correct"].mean()
        report += f"\n**λ = {lam}:**\n"
        report += f"- MMLU: {mmlu_acc:.4f}\n"
        report += f"- HumanEval: {he_acc:.4f}\n"

    report += f"""

---

## Figures

All figures saved to `figures/` directory:

1. **gate_metrics.png** - Gate validation metrics comparison (MANDATORY)
2. **capability_consistency.png** - Accuracy vs λ with error bars
3. **subject_heatmap.png** - MMLU subject × λ heatmap
4. **accuracy_distributions.png** - Violin plots per λ condition

---

## Raw Data

- **Results:** `results/all_results.csv`
- **Checkpoints:** `results/checkpoint_lambda_*.csv`
- **Gate Metrics:** `results/gate_metrics.json`

---

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    with open(report_path, 'w') as f:
        f.write(report)

    print(f"✓ Validation report saved: {report_path}")
    print()


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("h-e1: Policy-Layer Capability Decoupling Validation")
    print("="*60 + "\n")

    # Setup
    config = setup_environment()

    # Load data
    mmlu_loader, humaneval_loader = load_datasets()

    # Run experiment
    results = run_experiment(config, mmlu_loader, humaneval_loader)

    # Analyze
    gate_metrics = analyze_results(results, config)

    # Visualize
    generate_visualizations(results, gate_metrics, config)

    # Generate report
    generate_report(gate_metrics, results, config)

    # Final status
    print("="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Gate Result: {'PASS ✓' if gate_metrics['overall_pass'] else 'FAIL ✗'}")
    print("="*60 + "\n")

    # Signal completion (for Step 5 detection)
    with open("EXPERIMENT_COMPLETE", "w") as f:
        f.write(f"Gate: {'PASS' if gate_metrics['overall_pass'] else 'FAIL'}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")


if __name__ == "__main__":
    main()
