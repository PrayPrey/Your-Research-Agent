"""Main orchestration pipeline for H-M-Integrated mechanism validation.

This script conducts paired statistical comparison of linguistic markers
between RLHF chosen and rejected responses.
"""

import sys
import os
import json
import numpy as np
from datetime import datetime

# Add current directory to path first
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add h-e1 code path
h_e1_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../h-e1/code')
)
if h_e1_path not in sys.path:
    sys.path.insert(1, h_e1_path)

# Import h-m-integrated modules (from current directory)
from config import MechanismConfig
from paired_data_loader import PairedDataLoader
from paired_comparator import PairedComparator
from consistency_analyzer import InternalConsistencyAnalyzer
from cross_split_validator import CrossSplitValidator
from visualizer import MechanismVisualizer

# Import h-e1 modules
from data_loader import HHRLHFDataLoader
from extractor import LinguisticMarkerExtractor


def verify_h_e1_integration():
    """Verify h-e1 module integration.

    Returns:
        Tuple of (extractor, base_loader, config)
    """
    print("=== Verifying H-E1 Integration ===")

    # Load h-e1 configuration - import from h-e1 path
    import importlib.util
    h_e1_config_path = os.path.join(h_e1_path, 'config.py')
    spec = importlib.util.spec_from_file_location("h_e1_config", h_e1_config_path)
    h_e1_config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h_e1_config_module)
    h_e1_config = h_e1_config_module.Config()
    print("✓ H-E1 Config loaded")

    # Initialize data loader
    base_loader = HHRLHFDataLoader(cache_dir=None)
    print("✓ HHRLHFDataLoader initialized")

    # Initialize extractor
    extractor = LinguisticMarkerExtractor(
        spacy_model=h_e1_config.spacy_model,
        hedging_markers=h_e1_config.hedging_markers,
        alternative_patterns=h_e1_config.alternative_patterns
    )
    print("✓ LinguisticMarkerExtractor initialized")

    # Test extraction on sample text
    sample_text = "I think you could perhaps try this approach."
    features = extractor.extract_all_features(sample_text)
    assert 'modal_freq' in features
    assert 'hedging_freq' in features
    assert 'alt_freq' in features
    print("✓ Extraction test passed")

    print("\n✓ H-E1 integration verified successfully\n")

    return extractor, base_loader, h_e1_config


def main():
    """Main orchestration pipeline."""

    print("\n" + "="*60)
    print("H-M-INTEGRATED: Linguistic Mechanism Validation")
    print("="*60 + "\n")

    start_time = datetime.now()

    # === 1. Setup ===
    print("=== 1. Setup ===")
    config = MechanismConfig()
    print(f"Configuration loaded:")
    print(f"  - Cohen's d threshold: {config.cohens_d_threshold}")
    print(f"  - p-value threshold: {config.p_value_threshold}")
    print(f"  - Cronbach's α threshold: {config.cronbach_alpha_threshold}")
    print(f"  - Min passing splits: {config.min_passing_splits}")

    # Verify h-e1 integration
    extractor, base_loader, h_e1_config = verify_h_e1_integration()

    # === 2. Load Paired Data ===
    print("\n=== 2. Load Paired Data ===")
    paired_loader = PairedDataLoader(base_loader)
    all_pairs = paired_loader.load_paired_dataset()

    print(f"\nDataset summary:")
    print(f"  Total pairs: {len(all_pairs)}")
    for split_name in paired_loader.get_split_names():
        split_pairs = paired_loader.get_split_pairs(split_name)
        print(f"  - {split_name}: {len(split_pairs)} pairs")

    # === 3. Extract Features ===
    print("\n=== 3. Extract Features (Full Dataset) ===")
    comparator = PairedComparator(extractor)
    chosen_features, rejected_features = comparator.extract_paired_features(all_pairs)

    print(f"\nFeature statistics:")
    print(f"  Chosen - Mean modal freq: {np.mean(chosen_features[:, 0]):.3f}")
    print(f"  Rejected - Mean modal freq: {np.mean(rejected_features[:, 0]):.3f}")

    # === 4. Primary Gate: Paired t-test + Cohen's d ===
    print("\n=== 4. Primary Gate: Paired t-test + Cohen's d ===")
    ttest_result = comparator.paired_ttest(chosen_features, rejected_features)
    cohens_d = comparator.cohens_d_paired(chosen_features, rejected_features)
    primary_pass = comparator.check_primary_gate(
        cohens_d, ttest_result['p_value'],
        config.cohens_d_threshold, config.p_value_threshold
    )

    print(f"Results:")
    print(f"  t-statistic: {ttest_result['t_stat']:.4f}")
    print(f"  p-value: {ttest_result['p_value']:.6f}")
    print(f"  Cohen's d: {cohens_d:.4f}")
    print(f"  |Cohen's d|: {abs(cohens_d):.4f}")
    print(f"  Direction: {'chosen < rejected' if cohens_d < 0 else 'chosen > rejected'}")
    print(f"  Primary Gate: {'PASS ✓' if primary_pass else 'FAIL ✗'}")

    # === 5. Secondary Gate: Cronbach's Alpha ===
    print("\n=== 5. Secondary Gate: Cronbach's Alpha ===")
    consistency_analyzer = InternalConsistencyAnalyzer()
    difference_matrix = chosen_features - rejected_features
    consistency_stats = consistency_analyzer.compute_statistics(difference_matrix)
    alpha = consistency_stats['cronbach_alpha']
    secondary_pass = consistency_analyzer.check_secondary_gate(
        alpha, config.cronbach_alpha_threshold
    )

    print(f"Results:")
    print(f"  Cronbach's α: {alpha:.4f}")
    print(f"  Mean correlation: {consistency_stats['mean_correlation']:.4f}")
    print(f"  Secondary Gate: {'PASS ✓' if secondary_pass else 'FAIL ✗'}")

    # === 6. Tertiary Gate: Cross-Split Validation ===
    print("\n=== 6. Tertiary Gate: Cross-Split Validation ===")
    split_pairs_dict = {}
    for split_name in paired_loader.get_split_names():
        split_pairs_dict[split_name] = paired_loader.get_split_pairs(split_name)

    validator = CrossSplitValidator(comparator)
    split_results = validator.validate_per_split(split_pairs_dict)
    passing_count = validator.count_passing_splits(split_results)
    tertiary_pass = validator.check_tertiary_gate(
        passing_count, len(split_results), config.min_passing_splits
    )

    print(f"\nSummary:")
    print(f"  Total splits tested: {len(split_results)}")
    print(f"  Passing splits: {passing_count}")
    print(f"  Tertiary Gate: {'PASS ✓' if tertiary_pass else 'FAIL ✗'}")

    # === 7. Visualizations ===
    print("\n=== 7. Generate Visualizations ===")
    visualizer = MechanismVisualizer(config)

    # Gate metrics (MANDATORY)
    visualizer.plot_gate_metrics(
        cohens_d, alpha, ttest_result['p_value'],
        os.path.join(config.figures_dir, 'gate_metrics.png')
    )

    # Forest plot
    visualizer.plot_forest_plot(
        split_results,
        os.path.join(config.figures_dir, 'forest_plot.png')
    )

    # Density comparison
    visualizer.plot_density_comparison(
        chosen_features[:, 0], rejected_features[:, 0],
        os.path.join(config.figures_dir, 'density_plots.png')
    )

    # Paired differences
    differences = chosen_features[:, 0] - rejected_features[:, 0]
    visualizer.plot_paired_differences(
        differences,
        os.path.join(config.figures_dir, 'paired_differences.png')
    )

    # Correlation heatmap
    corr_matrix = np.array(consistency_stats['correlation_matrix'])
    visualizer.plot_correlation_heatmap(
        corr_matrix,
        os.path.join(config.figures_dir, 'marker_correlations.png')
    )

    # === 8. Save Results ===
    print("\n=== 8. Save Results ===")

    # Compile all statistics
    results = {
        'timestamp': datetime.now().isoformat(),
        'hypothesis_id': 'h-m-integrated',
        'dataset': {
            'name': h_e1_config.dataset_name,
            'total_pairs': len(all_pairs),
            'splits': {name: len(paired_loader.get_split_pairs(name))
                      for name in paired_loader.get_split_names()}
        },
        'primary_gate': {
            'cohens_d': float(cohens_d),
            't_statistic': float(ttest_result['t_stat']),
            'p_value': float(ttest_result['p_value']),
            'threshold_d': config.cohens_d_threshold,
            'threshold_p': config.p_value_threshold,
            'passed': primary_pass
        },
        'secondary_gate': {
            'cronbach_alpha': float(alpha),
            'mean_correlation': float(consistency_stats['mean_correlation']),
            'threshold': config.cronbach_alpha_threshold,
            'passed': secondary_pass
        },
        'tertiary_gate': {
            'split_results': {
                name: {
                    'cohens_d': float(result['cohens_d']),
                    'p_value': float(result['p_value']),
                    't_stat': float(result['t_stat']),
                    'n_pairs': result['n_pairs'],
                    'passed': result['pass']
                }
                for name, result in split_results.items()
            },
            'passing_count': passing_count,
            'total_splits': len(split_results),
            'min_passing': config.min_passing_splits,
            'passed': tertiary_pass
        },
        'overall_gate_result': 'PASS' if (primary_pass and secondary_pass and tertiary_pass) else 'FAIL',
        'descriptive_stats': {
            'chosen_mean_modal': float(np.mean(chosen_features[:, 0])),
            'rejected_mean_modal': float(np.mean(rejected_features[:, 0])),
            'chosen_std_modal': float(np.std(chosen_features[:, 0])),
            'rejected_std_modal': float(np.std(rejected_features[:, 0])),
            'difference_mean': float(np.mean(differences)),
            'difference_std': float(np.std(differences))
        },
        'runtime_seconds': (datetime.now() - start_time).total_seconds()
    }

    # Save to JSON
    os.makedirs(config.results_dir, exist_ok=True)
    results_path = os.path.join(config.results_dir, 'statistics.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✓ Results saved to: {results_path}")

    # === 9. Generate Validation Report ===
    print("\n=== 9. Generate Validation Report ===")
    generate_validation_report(results, config)

    # === Final Summary ===
    print("\n" + "="*60)
    print("FINAL GATE RESULTS")
    print("="*60)
    print(f"Primary Gate (Effect Size):   {'PASS ✓' if primary_pass else 'FAIL ✗'}")
    print(f"Secondary Gate (Consistency): {'PASS ✓' if secondary_pass else 'FAIL ✗'}")
    print(f"Tertiary Gate (Replication):  {'PASS ✓' if tertiary_pass else 'FAIL ✗'}")
    print("="*60)
    print(f"OVERALL: {results['overall_gate_result']}")
    print("="*60)

    elapsed_time = datetime.now() - start_time
    print(f"\nTotal runtime: {elapsed_time}")

    return results


def generate_validation_report(results: dict, config: MechanismConfig):
    """Generate 04_validation.md report.

    Args:
        results: Results dictionary
        config: Configuration object
    """
    report_path = config.validation_report

    with open(report_path, 'w') as f:
        f.write("# Phase 4 Validation Report: H-M-Integrated\n\n")
        f.write(f"**Date:** {results['timestamp']}\n")
        f.write(f"**Hypothesis ID:** {results['hypothesis_id']}\n")
        f.write(f"**Hypothesis Type:** MECHANISM\n\n")

        f.write("---\n\n")

        f.write("## Executive Summary\n\n")
        f.write(f"**Overall Gate Result:** {results['overall_gate_result']}\n\n")

        f.write("| Gate | Criterion | Result | Status |\n")
        f.write("|------|-----------|--------|--------|\n")

        primary = results['primary_gate']
        f.write(f"| Primary | Cohen's d ≥ {primary['threshold_d']}, p < {primary['threshold_p']} | ")
        f.write(f"d={primary['cohens_d']:.4f}, p={primary['p_value']:.6f} | ")
        f.write(f"{'PASS ✓' if primary['passed'] else 'FAIL ✗'} |\n")

        secondary = results['secondary_gate']
        f.write(f"| Secondary | α > {secondary['threshold']} | ")
        f.write(f"α={secondary['cronbach_alpha']:.4f} | ")
        f.write(f"{'PASS ✓' if secondary['passed'] else 'FAIL ✗'} |\n")

        tertiary = results['tertiary_gate']
        f.write(f"| Tertiary | ≥{tertiary['min_passing']}/{tertiary['total_splits']} splits pass | ")
        f.write(f"{tertiary['passing_count']}/{tertiary['total_splits']} passed | ")
        f.write(f"{'PASS ✓' if tertiary['passed'] else 'FAIL ✗'} |\n\n")

        f.write("---\n\n")

        f.write("## Dataset\n\n")
        f.write(f"**Dataset:** {results['dataset']['name']}\n")
        f.write(f"**Total Pairs:** {results['dataset']['total_pairs']:,}\n\n")
        f.write("**Splits:**\n")
        for split_name, count in results['dataset']['splits'].items():
            f.write(f"- {split_name}: {count:,} pairs\n")
        f.write("\n")

        f.write("---\n\n")

        f.write("## Primary Gate: Effect Size Analysis\n\n")
        f.write("**Criterion:** Cohen's d ≥ 0.15, p < 0.05, chosen < rejected\n\n")
        f.write("**Results:**\n")
        f.write(f"- t-statistic: {primary['t_statistic']:.4f}\n")
        f.write(f"- p-value: {primary['p_value']:.6f}\n")
        f.write(f"- Cohen's d: {primary['cohens_d']:.4f}\n")
        f.write(f"- Direction: {'chosen < rejected ✓' if primary['cohens_d'] < 0 else 'chosen > rejected ✗'}\n\n")

        f.write("**Interpretation:**\n")
        if primary['passed']:
            f.write(f"✓ The effect size (|d| = {abs(primary['cohens_d']):.4f}) meets the threshold of {primary['threshold_d']}, ")
            f.write(f"and is statistically significant (p = {primary['p_value']:.6f} < {primary['threshold_p']}). ")
            f.write("The direction is correct (chosen < rejected), indicating chosen responses have fewer modal verbs.\n\n")
        else:
            f.write(f"✗ Primary gate FAILED. ")
            if abs(primary['cohens_d']) < primary['threshold_d']:
                f.write(f"Effect size (|d| = {abs(primary['cohens_d']):.4f}) below threshold ({primary['threshold_d']}). ")
            if primary['p_value'] >= primary['threshold_p']:
                f.write(f"Not statistically significant (p = {primary['p_value']:.6f} ≥ {primary['threshold_p']}). ")
            if primary['cohens_d'] > 0:
                f.write("Wrong direction (chosen > rejected).")
            f.write("\n\n")

        f.write("**Descriptive Statistics:**\n")
        stats = results['descriptive_stats']
        f.write(f"- Chosen mean modal freq: {stats['chosen_mean_modal']:.3f} ± {stats['chosen_std_modal']:.3f}\n")
        f.write(f"- Rejected mean modal freq: {stats['rejected_mean_modal']:.3f} ± {stats['rejected_std_modal']:.3f}\n")
        f.write(f"- Mean difference: {stats['difference_mean']:.3f} ± {stats['difference_std']:.3f}\n\n")

        f.write("---\n\n")

        f.write("## Secondary Gate: Internal Consistency\n\n")
        f.write(f"**Criterion:** Cronbach's α > {secondary['threshold']}\n\n")
        f.write("**Results:**\n")
        f.write(f"- Cronbach's α: {secondary['cronbach_alpha']:.4f}\n")
        f.write(f"- Mean inter-item correlation: {secondary['mean_correlation']:.4f}\n\n")

        f.write("**Interpretation:**\n")
        if secondary['passed']:
            f.write(f"✓ Internal consistency (α = {secondary['cronbach_alpha']:.4f}) exceeds threshold ({secondary['threshold']}), ")
            f.write("indicating the three marker types (modal verbs, hedging, alternatives) measure a consistent underlying construct.\n\n")
        else:
            f.write(f"✗ Secondary gate FAILED. Internal consistency (α = {secondary['cronbach_alpha']:.4f}) ")
            f.write(f"below threshold ({secondary['threshold']}), suggesting markers may not measure a unified construct.\n\n")

        f.write("---\n\n")

        f.write("## Tertiary Gate: Cross-Split Replication\n\n")
        f.write(f"**Criterion:** At least {tertiary['min_passing']} of {tertiary['total_splits']} splits pass primary criteria\n\n")
        f.write("**Per-Split Results:**\n\n")
        f.write("| Split | N Pairs | Cohen's d | p-value | Status |\n")
        f.write("|-------|---------|-----------|---------|--------|\n")

        for split_name, split_result in tertiary['split_results'].items():
            f.write(f"| {split_name} | {split_result['n_pairs']:,} | ")
            f.write(f"{split_result['cohens_d']:.4f} | {split_result['p_value']:.6f} | ")
            f.write(f"{'PASS ✓' if split_result['passed'] else 'FAIL ✗'} |\n")

        f.write("\n**Interpretation:**\n")
        if tertiary['passed']:
            f.write(f"✓ Replication achieved: {tertiary['passing_count']} of {tertiary['total_splits']} splits passed ")
            f.write(f"(≥ {tertiary['min_passing']} required), demonstrating the mechanism generalizes across dataset conditions.\n\n")
        else:
            f.write(f"✗ Tertiary gate FAILED. Only {tertiary['passing_count']} of {tertiary['total_splits']} splits passed ")
            f.write(f"(< {tertiary['min_passing']} required), indicating lack of replication.\n\n")

        f.write("---\n\n")

        f.write("## Visualizations\n\n")
        f.write("All figures saved to `figures/`:\n\n")
        f.write("1. **gate_metrics.png** - Gate criteria comparison (MANDATORY)\n")
        f.write("2. **forest_plot.png** - Effect sizes by split with 95% CI\n")
        f.write("3. **density_plots.png** - Distribution comparison (chosen vs rejected)\n")
        f.write("4. **paired_differences.png** - Histogram of paired differences\n")
        f.write("5. **marker_correlations.png** - Correlation heatmap\n\n")

        f.write("---\n\n")

        f.write("## Conclusion\n\n")
        if results['overall_gate_result'] == 'PASS':
            f.write("✓ **All gates PASSED.** The hypothesis is supported: chosen RLHF responses exhibit ")
            f.write("systematically lower linguistic agency markers compared to rejected responses, with ")
            f.write("small-to-medium effect size, internal consistency, and cross-split replication.\n\n")
            f.write("**Next Steps:** Proceed to Phase 5 baseline comparison (if enabled) or Phase 6 paper writing.\n\n")
        else:
            f.write("✗ **Gate FAILURE.** The hypothesis is not supported. ")
            failed_gates = []
            if not primary['passed']:
                failed_gates.append('primary (effect size)')
            if not secondary['passed']:
                failed_gates.append('secondary (consistency)')
            if not tertiary['passed']:
                failed_gates.append('tertiary (replication)')
            f.write(f"Failed gates: {', '.join(failed_gates)}.\n\n")
            f.write("**Recommended Actions:**\n")
            f.write("- PIVOT to alternative linguistic markers or measurement approaches\n")
            f.write("- EXPLORE direct user studies for agency perception\n")
            f.write("- ABANDON computational proxy approach if no viable alternatives\n\n")

        f.write("---\n\n")
        f.write(f"**Runtime:** {results['runtime_seconds']:.1f} seconds\n")
        f.write(f"**Generated:** {results['timestamp']}\n")

    print(f"✓ Validation report saved to: {report_path}")


if __name__ == "__main__":
    results = main()
