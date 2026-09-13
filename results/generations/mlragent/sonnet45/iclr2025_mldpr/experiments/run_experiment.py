"""
Main Experiment Runner for Temporal Dataset Cards
Executes all experiments and generates comprehensive results
"""

import sys
import json
import os
from datetime import datetime
from evaluation import ExperimentRunner, compute_summary_metrics
from create_visualizations import generate_all_visualizations


class Logger:
    """Simple logger to write to both console and file"""

    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log = open(log_file, 'w', encoding='utf-8')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


def format_results_for_display(results: dict, indent: int = 0) -> str:
    """Format results dictionary for readable display"""
    output = []
    prefix = "  " * indent

    for key, value in results.items():
        if isinstance(value, dict):
            output.append(f"{prefix}{key}:")
            output.append(format_results_for_display(value, indent + 1))
        elif isinstance(value, list):
            if len(value) > 5:
                output.append(f"{prefix}{key}: [{len(value)} items]")
            else:
                output.append(f"{prefix}{key}: {value}")
        elif isinstance(value, float):
            output.append(f"{prefix}{key}: {value:.6f}")
        else:
            output.append(f"{prefix}{key}: {value}")

    return "\n".join(output)


def main():
    """Main execution function"""

    print("="*80)
    print("TEMPORAL DATASET CARDS - EXPERIMENTAL EVALUATION")
    print("="*80)
    print()

    # Setup logging
    log_file = "log.txt"
    logger = Logger(log_file)
    sys.stdout = logger

    try:
        print(f"Experiment started at: {datetime.now().isoformat()}")
        print()

        # Initialize experiment runner
        print("Initializing experiment runner...")
        runner = ExperimentRunner(seed=42)
        print("✓ Experiment runner initialized")
        print()

        # Run all experiments
        print("="*80)
        print("EXECUTING EXPERIMENTS")
        print("="*80)
        print()

        results = runner.run_all_experiments()

        print()
        print("="*80)
        print("COMPUTING SUMMARY METRICS")
        print("="*80)
        print()

        summary = compute_summary_metrics(results)

        print("Summary Metrics:")
        print(format_results_for_display(summary))
        print()

        # Save results to JSON
        print("="*80)
        print("SAVING RESULTS")
        print("="*80)
        print()

        results_file = "experiment_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Results saved to: {results_file}")

        summary_file = "summary_metrics.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Summary saved to: {summary_file}")

        # Generate visualizations
        print()
        print("="*80)
        print("GENERATING VISUALIZATIONS")
        print("="*80)
        print()

        generate_all_visualizations(results, summary, ".")

        # Generate tables for results.md
        print()
        print("="*80)
        print("GENERATING RESULT TABLES")
        print("="*80)
        print()

        tables = generate_result_tables(results, summary)

        tables_file = "result_tables.json"
        with open(tables_file, 'w') as f:
            json.dump(tables, f, indent=2)
        print(f"✓ Tables saved to: {tables_file}")

        print()
        print("="*80)
        print("EXPERIMENT COMPLETED SUCCESSFULLY")
        print("="*80)
        print()
        print(f"Experiment ended at: {datetime.now().isoformat()}")

        # Print key findings
        print()
        print("="*80)
        print("KEY FINDINGS")
        print("="*80)
        print()
        print(f"1. Reproducibility Variance Reduction: {summary['reproducibility']['variance_reduction']:.1f}%")
        print(f"2. Reproduction Success Rate Improvement: {summary['reproducibility']['success_rate_improvement']:.1f}%")
        print(f"3. Impact Tracing F1 Score: {summary['impact_tracing']['automated_f1']:.3f}")
        print(f"4. Annotation Propagation Rate: {summary['annotation_propagation']['temporal_system_rate']*100:.1f}%")
        print(f"5. Notification Time Reduction: {summary['annotation_propagation']['notification_time_reduction']:.1f} days")
        print()

    except Exception as e:
        print()
        print("="*80)
        print("ERROR OCCURRED")
        print("="*80)
        print()
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # Close logger
        sys.stdout = logger.terminal
        logger.close()

    return 0


def generate_result_tables(results: dict, summary: dict) -> dict:
    """Generate formatted tables for results.md"""

    tables = {}

    # Table 1: Reproducibility Comparison
    tables['reproducibility'] = {
        'headers': ['Method', 'Mean Accuracy', 'Variance', 'Std Dev', 'Success Rate (%)'],
        'rows': [
            [
                'Without Temporal Cards',
                f"{results['experiment_1_reproducibility']['without_temporal_cards']['mean_accuracy']:.4f}",
                f"{results['experiment_1_reproducibility']['without_temporal_cards']['variance']:.6f}",
                f"{results['experiment_1_reproducibility']['without_temporal_cards']['std_accuracy']:.4f}",
                f"{results['experiment_1_reproducibility']['without_temporal_cards']['reproduction_success_rate']*100:.1f}"
            ],
            [
                'With Temporal Cards',
                f"{results['experiment_1_reproducibility']['with_temporal_cards']['mean_accuracy']:.4f}",
                f"{results['experiment_1_reproducibility']['with_temporal_cards']['variance']:.6f}",
                f"{results['experiment_1_reproducibility']['with_temporal_cards']['std_accuracy']:.4f}",
                f"{results['experiment_1_reproducibility']['with_temporal_cards']['reproduction_success_rate']*100:.1f}"
            ]
        ]
    }

    # Table 2: Impact Tracing Performance
    tables['impact_tracing'] = {
        'headers': ['Method', 'Precision', 'Recall', 'F1 Score', 'True Positives', 'False Positives'],
        'rows': [
            [
                'Manual Review',
                f"{results['experiment_2_impact_tracing']['manual_review']['precision']:.3f}",
                f"{results['experiment_2_impact_tracing']['manual_review']['recall']:.3f}",
                f"{results['experiment_2_impact_tracing']['manual_review']['f1_score']:.3f}",
                f"{results['experiment_2_impact_tracing']['manual_review']['true_positives']}",
                f"{results['experiment_2_impact_tracing']['manual_review']['false_positives']}"
            ],
            [
                'Automated Tracing',
                f"{results['experiment_2_impact_tracing']['automated_tracing']['precision']:.3f}",
                f"{results['experiment_2_impact_tracing']['automated_tracing']['recall']:.3f}",
                f"{results['experiment_2_impact_tracing']['automated_tracing']['f1_score']:.3f}",
                f"{results['experiment_2_impact_tracing']['automated_tracing']['true_positives']}",
                f"{results['experiment_2_impact_tracing']['automated_tracing']['false_positives']}"
            ]
        ]
    }

    # Table 3: Annotation Propagation
    tables['annotation_propagation'] = {
        'headers': ['System', 'Propagation Rate (%)', 'Avg Notification Time (days)', 'User Acknowledgment (%)'],
        'rows': [
            [
                'Manual Propagation',
                f"{results['experiment_3_annotation_propagation']['without_temporal_system']['propagation_rate']*100:.1f}",
                f"{results['experiment_3_annotation_propagation']['without_temporal_system']['avg_notification_time_days']:.1f}",
                f"{results['experiment_3_annotation_propagation']['without_temporal_system']['user_acknowledgment_rate']*100:.1f}"
            ],
            [
                'Temporal Card System',
                f"{results['experiment_3_annotation_propagation']['with_temporal_system']['propagation_rate']*100:.1f}",
                f"{results['experiment_3_annotation_propagation']['with_temporal_system']['avg_notification_time_days']:.1f}",
                f"{results['experiment_3_annotation_propagation']['with_temporal_system']['user_acknowledgment_rate']*100:.1f}"
            ]
        ]
    }

    # Table 4: Summary of Improvements
    tables['improvements'] = {
        'headers': ['Metric', 'Improvement'],
        'rows': [
            ['Variance Reduction', f"{summary['reproducibility']['variance_reduction']:.1f}%"],
            ['Success Rate Improvement', f"{summary['reproducibility']['success_rate_improvement']:.1f}%"],
            ['F1 Score Improvement', f"{summary['impact_tracing']['f1_improvement']:.3f}"],
            ['Notification Time Reduction', f"{summary['annotation_propagation']['notification_time_reduction']:.1f} days"]
        ]
    }

    return tables


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
