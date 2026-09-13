"""
Main experiment runner for H-E1 Base-Rate Validation Study.
"""
import yaml
import json
import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from data.loader import load_hh_rlhf_dataset
from data.sampler import stratified_sample
from annotation.storage import load_annotations, save_annotations
from annotation.interface import collect_annotations_batch
from analysis.agreement import compute_cohens_kappa
from analysis.metrics import majority_vote, calculate_base_rate
from analysis.hypothesis_test import binomial_test
from visualization.plots import (
    plot_base_rate_comparison,
    plot_agreement_heatmap,
    plot_violation_distribution,
    plot_length_bias
)


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def log(message: str, level: str = "INFO"):
    """Simple print-based logging for LIGHT tier."""
    print(f"[{level}] {message}")


def run_experiment(config_path: str = "config.yaml", annotations_file: str = None) -> Dict[str, Any]:
    """
    Orchestrate full annotation study pipeline.

    Args:
        config_path: Path to configuration YAML
        annotations_file: Optional path to pre-existing annotations CSV

    Returns:
        Dict with results
    """
    log("="*80)
    log("H-E1 Base-Rate Validation Study")
    log("="*80)

    # Step 1: Load config
    log("Loading configuration...")
    config = load_config(config_path)

    # Set random seed
    seed = config["experiment"]["seed"]
    np.random.seed(seed)
    log(f"Random seed set to {seed}")

    # Create output directories
    Path(config["outputs"]["data_dir"]).mkdir(parents=True, exist_ok=True)
    Path(config["outputs"]["figures_dir"]).mkdir(parents=True, exist_ok=True)
    Path("outputs").mkdir(exist_ok=True)

    # Step 2: Data sampling
    log("\n" + "="*80)
    log("STEP 1: Data Sampling")
    log("="*80)

    samples_file = Path(config["outputs"]["data_dir"]) / config["outputs"]["samples_file"]

    if samples_file.exists():
        log(f"Loading existing samples from {samples_file}")
        samples = pd.read_csv(samples_file)
    else:
        log(f"Loading HH-RLHF dataset: {config['dataset']['name']}")
        dataset = load_hh_rlhf_dataset(
            dataset_name=config["dataset"]["name"],
            subset=config["dataset"]["subset"],
            split=config["dataset"]["split"],
            cache_dir=config["dataset"].get("cache_dir")
        )
        log(f"Dataset loaded: {len(dataset)} samples")

        log(f"Performing stratified sampling (n={config['sampling']['sample_size']})")
        samples = stratified_sample(
            dataset,
            sample_size=config["sampling"]["sample_size"],
            seed=seed
        )
        samples.to_csv(samples_file, index=False)
        log(f"✓ Samples saved to {samples_file}")

    log(f"Sample size: {len(samples)}")
    log(f"Quartile distribution:\n{samples['length_quartile'].value_counts().sort_index()}")

    # Step 3: Annotation collection or loading
    log("\n" + "="*80)
    log("STEP 2: Annotation Collection")
    log("="*80)

    if annotations_file and Path(annotations_file).exists():
        log(f"Loading existing annotations from {annotations_file}")
        annotations = load_annotations(annotations_file)
    else:
        annotations_path = Path(config["outputs"]["data_dir"]) / config["outputs"]["annotations_file"]
        if annotations_path.exists():
            log(f"Loading existing annotations from {annotations_path}")
            annotations = load_annotations(str(annotations_path))
        else:
            log("ERROR: No annotations file found!", level="ERROR")
            log("This experiment requires REAL human annotations.", level="ERROR")
            log("", level="ERROR")
            log("To collect annotations, run:", level="ERROR")
            log("  python -m annotation.interface --samples <samples_file> --annotator <1|2|3>", level="ERROR")
            log("", level="ERROR")
            log(f"Expected annotation file: {annotations_path}", level="ERROR")
            raise FileNotFoundError(
                f"Annotation file not found: {annotations_path}. "
                "This experiment requires real human annotations. "
                "Please run the annotation interface to collect annotations from 3 independent annotators."
            )

    log(f"Total annotations: {len(annotations)}")
    log(f"Annotators: {sorted(annotations['annotator_id'].unique())}")
    log(f"Samples annotated: {annotations['sample_id'].nunique()}")

    # Step 4: Inter-annotator agreement
    log("\n" + "="*80)
    log("STEP 3: Inter-Annotator Agreement Analysis")
    log("="*80)

    kappa, pairwise_kappas = compute_cohens_kappa(annotations)
    log(f"Overall Cohen's kappa: {kappa:.3f}")
    log(f"\nPairwise kappa matrix:")
    log(str(pairwise_kappas))

    # Interpret kappa
    kappa_interp = interpret_kappa(kappa, config)
    log(f"Interpretation: {kappa_interp}")

    # Step 5: Majority vote
    log("\n" + "="*80)
    log("STEP 4: Majority Vote Labeling")
    log("="*80)

    final_labels = majority_vote(annotations)
    log(f"Final labels determined: {len(final_labels)} samples")

    # Save final labels
    final_labels_file = Path(config["outputs"]["data_dir"]) / config["outputs"]["final_labels_file"]
    final_labels_df = pd.DataFrame({
        'sample_id': sorted(annotations['sample_id'].unique()),
        'final_label': final_labels
    })
    final_labels_df.to_csv(final_labels_file, index=False)
    log(f"✓ Final labels saved to {final_labels_file}")

    # Step 6: Base-rate calculation
    log("\n" + "="*80)
    log("STEP 5: Base-Rate Calculation")
    log("="*80)

    base_rate, ci = calculate_base_rate(final_labels)
    log(f"Base-rate (p): {base_rate:.3f}")
    log(f"95% Confidence Interval: ({ci[0]:.3f}, {ci[1]:.3f})")
    log(f"Number of violations: {np.sum(final_labels)} / {len(final_labels)}")

    # Step 7: Binomial test (MUST_WORK gate)
    log("\n" + "="*80)
    log("STEP 6: Binomial Hypothesis Test (MUST_WORK Gate)")
    log("="*80)

    n_violations = np.sum(final_labels)
    p_value, decision = binomial_test(
        n_successes=n_violations,
        n_trials=len(final_labels),
        p_null=config["hypothesis_test"]["null_hypothesis_threshold"],
        alpha=config["hypothesis_test"]["alpha"],
        alternative=config["hypothesis_test"]["alternative"]
    )

    log(f"H0: p < {config['hypothesis_test']['null_hypothesis_threshold']}")
    log(f"H1: p ≥ {config['hypothesis_test']['null_hypothesis_threshold']}")
    log(f"Binomial test p-value: {p_value:.4f}")
    log(f"Significance level (α): {config['hypothesis_test']['alpha']}")
    log(f"\n{'='*80}")
    log(f"GATE DECISION: {'PASS ✓' if decision else 'FAIL ✗'}")
    log(f"{'='*80}")

    # Step 8: Visualizations
    log("\n" + "="*80)
    log("STEP 7: Visualization Generation")
    log("="*80)

    plot_base_rate_comparison(
        base_rate=base_rate,
        threshold=config["hypothesis_test"]["null_hypothesis_threshold"],
        p_value=p_value,
        output_path=str(Path(config["outputs"]["figures_dir"]) / "base_rate.png")
    )

    plot_agreement_heatmap(
        pairwise_kappas=pairwise_kappas,
        output_path=str(Path(config["outputs"]["figures_dir"]) / "agreement_heatmap.png")
    )

    plot_violation_distribution(
        annotations=annotations,
        output_path=str(Path(config["outputs"]["figures_dir"]) / "violation_types.png")
    )

    plot_length_bias(
        samples=samples,
        final_labels=final_labels,
        output_path=str(Path(config["outputs"]["figures_dir"]) / "length_bias.png")
    )

    # Step 9: Save results
    log("\n" + "="*80)
    log("STEP 8: Saving Results")
    log("="*80)

    results = {
        "experiment": config["experiment"]["name"],
        "hypothesis_id": config["experiment"]["hypothesis_id"],
        "sample_size": len(final_labels),
        "base_rate": float(base_rate),
        "confidence_interval": {
            "lower": float(ci[0]),
            "upper": float(ci[1])
        },
        "cohens_kappa": float(kappa),
        "kappa_interpretation": kappa_interp,
        "binomial_test": {
            "n_violations": int(n_violations),
            "n_trials": len(final_labels),
            "p_null": config["hypothesis_test"]["null_hypothesis_threshold"],
            "p_value": float(p_value),
            "alpha": config["hypothesis_test"]["alpha"],
            "decision": "PASS" if decision else "FAIL"
        },
        "gate_passed": decision
    }

    results_file = config["outputs"]["results_file"]
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    log(f"✓ Results saved to {results_file}")

    # Step 10: Write report
    write_report(results, config)

    log("\n" + "="*80)
    log("EXPERIMENT COMPLETE")
    log("="*80)

    return results


def interpret_kappa(kappa: float, config: Dict) -> str:
    """Return kappa interpretation label."""
    interp = config["statistical_analysis"]["kappa_interpretation"]

    if kappa < interp["poor"][1]:
        return "poor"
    elif kappa < interp["slight"][1]:
        return "slight"
    elif kappa < interp["fair"][1]:
        return "fair"
    elif kappa < interp["moderate"][1]:
        return "moderate"
    else:
        return "substantial"


def write_report(results: Dict[str, Any], config: Dict) -> None:
    """Write summary report to markdown."""
    report_file = config["outputs"]["report_file"]

    report = f"""# H-E1 Base-Rate Validation Study - Results

**Experiment:** {results['experiment']}
**Hypothesis ID:** {results['hypothesis_id']}
**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

This study validated the base-rate of genuine safety policy violations in HH-RLHF dataset's rejected responses through blinded human annotation.

---

## Results

### Primary Metrics

**Base-Rate:**
- Observed proportion: **{results['base_rate']:.3f}**
- 95% Confidence Interval: ({results['confidence_interval']['lower']:.3f}, {results['confidence_interval']['upper']:.3f})
- Violations: {results['binomial_test']['n_violations']} / {results['binomial_test']['n_trials']}

**MUST_WORK Gate Test:**
- H0: p < {results['binomial_test']['p_null']}
- H1: p ≥ {results['binomial_test']['p_null']}
- Binomial test p-value: **{results['binomial_test']['p_value']:.4f}**
- Significance level (α): {results['binomial_test']['alpha']}
- **Decision: {results['binomial_test']['decision']}**

### Secondary Metrics

**Inter-Annotator Agreement:**
- Cohen's κ: **{results['cohens_kappa']:.3f}**
- Interpretation: **{results['kappa_interpretation']}**

---

## Gate Decision

**MUST_WORK Gate:** {'✓ PASSED' if results['gate_passed'] else '✗ FAILED'}

{'The base-rate of genuine safety violations meets the threshold requirement (p ≥ 0.40). Proceeding to dependent hypotheses (H-M1, H-M2, H-M3, H-M4).' if results['gate_passed'] else 'The base-rate does not meet the threshold requirement. STOP: Reassess hypothesis framing or pivot research direction.'}

---

## Figures

Generated visualizations are saved in `{config['outputs']['figures_dir']}/`:
1. `base_rate.png` - Base-rate vs threshold comparison
2. `agreement_heatmap.png` - Inter-annotator agreement matrix
3. `violation_types.png` - Distribution of annotation judgments
4. `length_bias.png` - Violation rate by response length quartile

---

## Data Files

- Samples: `{config['outputs']['data_dir']}/{config['outputs']['samples_file']}`
- Annotations: `{config['outputs']['data_dir']}/{config['outputs']['annotations_file']}`
- Final Labels: `{config['outputs']['data_dir']}/{config['outputs']['final_labels_file']}`
- Results: `{config['outputs']['results_file']}`

---

*Generated by H-E1 experiment runner*
"""

    with open(report_file, 'w') as f:
        f.write(report)

    log(f"✓ Report written to {report_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="H-E1 Base-Rate Validation Study")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    parser.add_argument("--annotations", default=None, help="Path to annotations CSV")
    args = parser.parse_args()

    results = run_experiment(config_path=args.config, annotations_file=args.annotations)

    # Exit with appropriate code
    sys.exit(0 if results['gate_passed'] else 1)
