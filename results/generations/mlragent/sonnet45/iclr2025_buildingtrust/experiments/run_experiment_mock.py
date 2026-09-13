"""
Main Experiment Script with Mock Models
Runs the complete experimental pipeline using simulated model responses
"""
import os
import sys
import json
import time
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# Import modules
from config import (EXPERIMENT_CONFIG, MODEL_CONFIG, DATASET_CONFIG,
                    CALIBRATION_CONFIG, OUTPUT_DIR, RESULTS_DIR, FIGURES_DIR)
from data_processing import DataProcessor
from mock_models import MockModelSystem  # Use mock instead of real models
from disagreement_analysis import DisagreementAnalyzer
from confidence_calibration import ConfidenceCalibrator
from evaluation import CalibrationMetrics, check_answer_correctness, get_consensus_answer
from baselines import BaselineEvaluator
from visualization import (plot_calibration_curve, plot_method_comparison,
                            plot_selective_prediction, plot_confidence_distribution_by_correctness,
                            create_results_summary_table)


class ExperimentRunner:
    """Main experiment runner with mock models"""

    def __init__(self, config: Dict):
        self.config = config
        self.results = {}
        self.log_file = None

    def log(self, message: str):
        """Log message to console and file"""
        print(message)
        if self.log_file:
            self.log_file.write(message + '\n')
            self.log_file.flush()

    def setup_directories(self):
        """Create output directories"""
        os.makedirs(RESULTS_DIR, exist_ok=True)
        os.makedirs(FIGURES_DIR, exist_ok=True)
        self.log("Created output directories")

    def step1_load_data(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Step 1: Load and prepare datasets"""
        self.log("\n" + "=" * 80)
        self.log("STEP 1: LOADING DATA")
        self.log("=" * 80)

        processor = DataProcessor(DATASET_CONFIG)

        # Load datasets
        all_samples = processor.load_all_datasets()

        # Limit number of samples for efficiency
        max_samples = self.config.get('n_samples', 200)
        all_samples = all_samples[:max_samples]
        self.log(f"\nUsing {len(all_samples)} samples total")

        # Split data
        train_samples, val_samples, test_samples = processor.split_data(
            all_samples,
            CALIBRATION_CONFIG['train_ratio'],
            CALIBRATION_CONFIG['val_ratio'],
            CALIBRATION_CONFIG['test_ratio']
        )

        return train_samples, val_samples, test_samples

    def step2_query_models(self, samples: List[Dict], split_name: str) -> Dict:
        """Step 2: Query ensemble of mock models"""
        self.log("\n" + "=" * 80)
        self.log(f"STEP 2: QUERYING MOCK MODELS ({split_name} split)")
        self.log("=" * 80)

        # Use mock model system
        mock_system = MockModelSystem(MODEL_CONFIG['models'], seed=42)

        # Prepare questions and answers
        questions = [s['question'] for s in samples]
        answers = [s['answer'] for s in samples]

        n_samples_per_model = self.config.get('n_response_samples', 2)

        self.log(f"Querying {len(questions)} questions...")

        # Query mock models
        all_responses = mock_system.batch_query_ensemble(
            questions,
            correct_answers=answers,
            n_samples=n_samples_per_model
        )

        self.log(f"Collected mock responses for {len(all_responses)} questions")

        return all_responses

    def step3_analyze_disagreement(self, response_dict: Dict) -> Dict:
        """Step 3: Analyze disagreement patterns"""
        self.log("\n" + "=" * 80)
        self.log("STEP 3: ANALYZING DISAGREEMENT")
        self.log("=" * 80)

        analyzer = DisagreementAnalyzer()
        analysis_results = analyzer.batch_analyze(response_dict)

        self.log(f"\nAnalyzed {len(analysis_results)} questions")

        # Print sample analysis
        sample_question = list(analysis_results.keys())[0]
        sample_analysis = analysis_results[sample_question]
        self.log(f"\nSample analysis for: '{sample_question[:50]}...'")
        self.log(f"  Semantic Dispersion: {sample_analysis['semantic_dispersion']:.4f}")
        self.log(f"  Cluster Diversity: {sample_analysis['cluster_diversity']:.4f}")
        self.log(f"  Length Variance: {sample_analysis['length_variance']:.4f}")
        self.log(f"  Composite Uncertainty: {sample_analysis['composite_uncertainty']:.4f}")

        return analysis_results

    def step4_prepare_labels(self, samples: List[Dict], response_dict: Dict) -> Dict:
        """Step 4: Prepare ground truth labels"""
        self.log("\n" + "=" * 80)
        self.log("STEP 4: PREPARING GROUND TRUTH LABELS")
        self.log("=" * 80)

        labels = {}

        for sample in samples:
            question = sample['question']
            if question not in response_dict:
                continue

            responses = response_dict[question]
            ground_truth = sample['answer']
            aliases = sample.get('aliases', [ground_truth])

            # Get consensus answer from models
            consensus_answer, _ = get_consensus_answer(responses)

            # Check if consensus is correct
            is_correct = check_answer_correctness(consensus_answer, ground_truth, aliases)

            labels[question] = 1.0 if is_correct else 0.0

        correct_count = sum(labels.values())
        total_count = len(labels)
        self.log(f"\nLabeled {total_count} questions")
        self.log(f"Correct predictions: {correct_count}/{total_count} ({correct_count / total_count * 100:.1f}%)")

        return labels

    def step5_train_calibrator(self, train_samples: List[Dict],
                                train_responses: Dict,
                                train_analysis: Dict,
                                train_labels: Dict,
                                val_samples: List[Dict],
                                val_responses: Dict,
                                val_analysis: Dict,
                                val_labels: Dict) -> ConfidenceCalibrator:
        """Step 5: Train confidence calibrator"""
        self.log("\n" + "=" * 80)
        self.log("STEP 5: TRAINING CONFIDENCE CALIBRATOR")
        self.log("=" * 80)

        # Prepare training data
        train_data = []
        for sample in train_samples:
            question = sample['question']
            if question in train_analysis and question in train_labels:
                train_data.append((train_analysis[question], train_labels[question]))

        # Prepare validation data
        val_data = []
        for sample in val_samples:
            question = sample['question']
            if question in val_analysis and question in val_labels:
                val_data.append((val_analysis[question], val_labels[question]))

        self.log(f"Training samples: {len(train_data)}")
        self.log(f"Validation samples: {len(val_data)}")

        # Train calibrator
        calibrator = ConfidenceCalibrator(CALIBRATION_CONFIG)
        calibrator.train(train_data, val_data)

        # Save model
        model_path = os.path.join(OUTPUT_DIR, 'calibration_model.pt')
        calibrator.save_model(model_path)

        return calibrator

    def step6_evaluate(self, samples: List[Dict],
                       responses: Dict,
                       analysis: Dict,
                       labels: Dict,
                       calibrator: ConfidenceCalibrator,
                       split_name: str) -> Dict:
        """Step 6: Evaluate methods"""
        self.log("\n" + "=" * 80)
        self.log(f"STEP 6: EVALUATION ({split_name} split)")
        self.log("=" * 80)

        # Evaluate proposed method
        self.log("\n--- Proposed Method (Multi-Model Disagreement) ---")
        proposed_confidences = []
        questions_order = []

        for sample in samples:
            question = sample['question']
            if question in analysis:
                confidence = calibrator.predict(analysis[question])
                proposed_confidences.append(confidence)
                questions_order.append(question)

        proposed_confidences = np.array(proposed_confidences)
        correctness = np.array([labels[q] for q in questions_order])

        proposed_metrics = CalibrationMetrics.compute_all_metrics(
            proposed_confidences, correctness, CALIBRATION_CONFIG['n_bins']
        )
        CalibrationMetrics.print_metrics(proposed_metrics, "Proposed Method")

        # Evaluate baselines
        self.log("\n--- Baseline Methods ---")
        baseline_evaluator = BaselineEvaluator()
        baseline_confidences_dict = baseline_evaluator.evaluate_all_baselines(
            responses, analysis, labels
        )

        baseline_metrics = {}
        for baseline_name, conf_dict in baseline_confidences_dict.items():
            confs = np.array([conf_dict[q] for q in questions_order])
            metrics = CalibrationMetrics.compute_all_metrics(
                confs, correctness, CALIBRATION_CONFIG['n_bins']
            )
            baseline_metrics[baseline_name] = metrics
            CalibrationMetrics.print_metrics(metrics, f"Baseline: {baseline_name}")

        # Combine all results
        all_results = {
            'proposed': proposed_metrics,
            **baseline_metrics
        }

        # Store confidences for visualization
        all_confidences = {
            'proposed': proposed_confidences,
            **{name: np.array([conf_dict[q] for q in questions_order])
               for name, conf_dict in baseline_confidences_dict.items()}
        }

        return {
            'metrics': all_results,
            'confidences': all_confidences,
            'correctness': correctness,
            'questions': questions_order
        }

    def step7_visualize(self, test_results: Dict):
        """Step 7: Generate visualizations"""
        self.log("\n" + "=" * 80)
        self.log("STEP 7: GENERATING VISUALIZATIONS")
        self.log("=" * 80)

        # Plot calibration curves for all methods
        for method_name, confidences in test_results['confidences'].items():
            save_path = os.path.join(FIGURES_DIR, f'calibration_{method_name}.png')
            plot_calibration_curve(
                confidences,
                test_results['correctness'],
                title=f"Calibration Curve - {method_name.replace('_', ' ').title()}",
                save_path=save_path
            )

        # Plot method comparison
        save_path = os.path.join(FIGURES_DIR, 'method_comparison.png')
        plot_method_comparison(test_results['metrics'], save_path)

        # Plot selective prediction for proposed method
        save_path = os.path.join(FIGURES_DIR, 'selective_prediction_proposed.png')
        plot_selective_prediction(
            test_results['confidences']['proposed'],
            test_results['correctness'],
            title="Selective Prediction - Proposed Method",
            save_path=save_path
        )

        # Plot confidence distribution
        save_path = os.path.join(FIGURES_DIR, 'confidence_distribution_proposed.png')
        plot_confidence_distribution_by_correctness(
            test_results['confidences']['proposed'],
            test_results['correctness'],
            title="Confidence Distribution - Proposed Method",
            save_path=save_path
        )

        self.log("Generated all visualizations")

    def save_final_results(self, test_results: Dict):
        """Save final results"""
        self.log("\n" + "=" * 80)
        self.log("SAVING FINAL RESULTS")
        self.log("=" * 80)

        # Save metrics
        metrics_file = os.path.join(RESULTS_DIR, 'metrics.json')
        with open(metrics_file, 'w') as f:
            json.dump(test_results['metrics'], f, indent=2)
        self.log(f"Saved metrics to {metrics_file}")

        # Create summary table
        summary_table = create_results_summary_table(test_results['metrics'])
        summary_file = os.path.join(RESULTS_DIR, 'summary_table.md')
        with open(summary_file, 'w') as f:
            f.write(summary_table)
        self.log(f"Saved summary table to {summary_file}")

    def run(self):
        """Run complete experiment pipeline"""
        # Open log file
        log_file_path = os.path.join(OUTPUT_DIR, 'log.txt')
        self.log_file = open(log_file_path, 'w')

        start_time = time.time()

        try:
            self.log("=" * 80)
            self.log("ADAPTIVE CONFIDENCE CALIBRATION EXPERIMENT (MOCK MODELS)")
            self.log("=" * 80)
            self.log(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Setup
            self.setup_directories()

            # Step 1: Load data
            train_samples, val_samples, test_samples = self.step1_load_data()

            # Step 2: Query models for all splits
            train_responses = self.step2_query_models(train_samples, 'train')
            val_responses = self.step2_query_models(val_samples, 'val')
            test_responses = self.step2_query_models(test_samples, 'test')

            # Step 3: Analyze disagreement
            train_analysis = self.step3_analyze_disagreement(train_responses)
            val_analysis = self.step3_analyze_disagreement(val_responses)
            test_analysis = self.step3_analyze_disagreement(test_responses)

            # Step 4: Prepare labels
            train_labels = self.step4_prepare_labels(train_samples, train_responses)
            val_labels = self.step4_prepare_labels(val_samples, val_responses)
            test_labels = self.step4_prepare_labels(test_samples, test_responses)

            # Step 5: Train calibrator
            calibrator = self.step5_train_calibrator(
                train_samples, train_responses, train_analysis, train_labels,
                val_samples, val_responses, val_analysis, val_labels
            )

            # Step 6: Evaluate
            test_results = self.step6_evaluate(
                test_samples, test_responses, test_analysis, test_labels,
                calibrator, 'test'
            )

            # Step 7: Visualize
            self.step7_visualize(test_results)

            # Save final results
            self.save_final_results(test_results)

            # Print summary
            elapsed_time = time.time() - start_time
            self.log("\n" + "=" * 80)
            self.log("EXPERIMENT COMPLETED SUCCESSFULLY")
            self.log("=" * 80)
            self.log(f"Total time: {elapsed_time / 60:.1f} minutes")
            self.log(f"Results saved to: {RESULTS_DIR}")

        except Exception as e:
            self.log(f"\n\nERROR: {str(e)}")
            import traceback
            self.log(traceback.format_exc())
            raise

        finally:
            if self.log_file:
                self.log_file.close()


if __name__ == '__main__':
    # Run experiment
    runner = ExperimentRunner(EXPERIMENT_CONFIG)
    runner.run()
