"""Main validation pipeline for H-M2 Bayesian Gate 2 prediction."""

import argparse
import numpy as np
from pathlib import Path

from data_loader import Gate2CorpusLoader
from predictor import Gate1Predictor, Gate2BayesianPredictor
from error_analyzer import ErrorAnalyzer
from evaluator import SuccessEvaluator
from visualizer import Gate2Visualizer
from validator import ValidationWriter


def run_validation(h_m1_path: str, output_dir: str, k: float = 1.000) -> dict:
    """
    Run full H-M2 validation pipeline.

    Args:
        h_m1_path: Path to H-M1 validation data
        output_dir: Output directory for results
        k: Scaling factor from H-M1 (default 1.000)

    Returns:
        dict with validation results
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Step 1: Load and filter data
    print("Loading Gate 2 corpus...")
    loader = Gate2CorpusLoader(h_m1_path)
    df = loader.load()
    df_gate2 = loader.filter_gate2_data(df)

    if not loader.validate_sample_size(df_gate2, min_samples=10):
        raise ValueError(f"Insufficient Gate 2 data: {len(df_gate2)} < 10 hypotheses")

    print(f"Loaded {len(df_gate2)} hypotheses with Gate 2 data")

    # Step 2: Run predictions
    print("Computing Gate 1 prior predictions...")
    gate1 = Gate1Predictor(k=k, prior_variance=0.02)
    pred_g1 = []
    for _, row in df_gate2.iterrows():
        pred_mean, _ = gate1.predict(row['O_10'])
        pred_g1.append(pred_mean)
    pred_g1 = np.array(pred_g1)

    print("Computing Gate 2 posterior predictions...")
    gate2 = Gate2BayesianPredictor(k=k, prior_var=0.02, likelihood_var=0.002)
    pred_g2 = []
    for _, row in df_gate2.iterrows():
        pred_mean, _ = gate2.predict(row['O_10'], row['O_100'])
        pred_g2.append(pred_mean)
    pred_g2 = np.array(pred_g2)

    # Step 3: Compute errors
    print("Computing errors and reduction...")
    analyzer = ErrorAnalyzer()
    O_full = df_gate2['O_full'].values

    errors_g1 = analyzer.compute_errors(pred_g1, O_full)
    errors_g2 = analyzer.compute_errors(pred_g2, O_full)

    reduction_results = analyzer.compute_reduction(errors_g1, errors_g2)
    mean_reduction = reduction_results['mean_reduction']
    per_hypothesis_reduction = reduction_results['per_hypothesis_reduction']

    # Step 4: Statistical test
    print("Running paired t-test...")
    ttest_results = analyzer.paired_ttest(errors_g1, errors_g2)
    t_stat = ttest_results['t_statistic']
    p_value = ttest_results['p_value']
    dof = ttest_results['dof']

    # Step 5: Evaluate success criteria
    print("Evaluating success criteria...")
    evaluator = SuccessEvaluator(reduction_threshold=40.0, p_threshold=0.05)
    eval_result = evaluator.evaluate(mean_reduction, p_value)
    result = eval_result['result']

    # Step 6: Generate visualizations
    print("Generating visualizations...")
    figures_dir = output_path / 'figures'
    visualizer = Gate2Visualizer(str(figures_dir))

    visualizer.plot_error_reduction_histogram(per_hypothesis_reduction)
    visualizer.plot_gate_comparison_scatter(O_full, pred_g1, pred_g2)
    visualizer.plot_paired_errors(errors_g1, errors_g2)
    visualizer.plot_boxplot_comparison(errors_g1, errors_g2, p_value)
    visualizer.plot_metrics_comparison(
        target_reduction=40.0,
        actual_reduction=mean_reduction,
        target_pvalue=0.05,
        actual_pvalue=p_value
    )

    # Step 7: Write validation report
    print("Writing validation report...")
    writer = ValidationWriter(str(output_path / '04_validation.md'))
    writer.write_results(
        sample_size=len(df_gate2),
        mean_reduction=mean_reduction,
        p_value=p_value,
        t_stat=t_stat,
        dof=dof,
        result=result,
        mean_error_g1=float(np.mean(errors_g1)),
        mean_error_g2=float(np.mean(errors_g2))
    )

    print(f"\nValidation complete: {result}")
    print(f"Mean error reduction: {mean_reduction:.2f}%")
    print(f"p-value: {p_value:.4f}")

    return {
        'result': result,
        'mean_reduction': mean_reduction,
        'p_value': p_value,
        't_statistic': t_stat,
        'sample_size': len(df_gate2)
    }


def main():
    parser = argparse.ArgumentParser(description='H-M2 Bayesian Gate 2 validation')
    parser.add_argument('--h-m1-path', type=str, default='../h-m1/04_validation_data.csv',
                        help='Path to H-M1 validation data')
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Output directory for results')
    parser.add_argument('--k', type=float, default=1.000,
                        help='Scaling factor from H-M1')

    args = parser.parse_args()

    results = run_validation(args.h_m1_path, args.output_dir, args.k)
    return results


if __name__ == '__main__':
    main()
