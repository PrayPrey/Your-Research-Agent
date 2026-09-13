"""Main experiment pipeline orchestrator"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import TIMMDataLoader
from assumption_validator import AssumptionValidator
from classifier_trainer import LogisticClassifierTrainer
from evaluator import ValidationEvaluator
from report_generator import ResultsReporter
from config import FEATURE_NAMES, THRESHOLDS


class ExperimentPipeline:
    """End-to-end experiment pipeline for H-E1"""

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(__file__)
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.models_dir = os.path.join(self.base_dir, 'models')
        self.results_dir = os.path.join(self.base_dir, 'results')
        self.logs_dir = os.path.join(self.base_dir, 'logs')

        # Setup logging
        self._setup_logging()

        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 80)
        self.logger.info("H-E1 Experiment Pipeline Started")
        self.logger.info("=" * 80)

    def _setup_logging(self):
        """Configure logging to file and console"""
        os.makedirs(self.logs_dir, exist_ok=True)

        log_file = os.path.join(self.logs_dir, 'experiment_log.txt')

        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def run_data_preparation(self):
        """Phase 1: Download models and extract features"""
        self.logger.info("=" * 80)
        self.logger.info("PHASE 1: Data Preparation")
        self.logger.info("=" * 80)

        loader = TIMMDataLoader()

        # Download and extract
        self.logger.info("Downloading TIMM models and extracting features...")
        data = loader.download_models()

        if not data:
            raise RuntimeError("No models successfully downloaded")

        # Create splits
        self.logger.info("Creating train/val splits...")
        train_df, val_df = loader.create_splits(data)

        # Save
        os.makedirs(self.data_dir, exist_ok=True)
        loader.save_features(train_df, val_df, self.data_dir)

        self.logger.info(f"Data preparation complete: {len(train_df)} train, {len(val_df)} val")
        return train_df, val_df

    def run_assumption_validation(self, train_df):
        """Phase 2: Validate A1, A2, A3 assumptions"""
        self.logger.info("=" * 80)
        self.logger.info("PHASE 2: Assumption Validation")
        self.logger.info("=" * 80)

        validator = AssumptionValidator(train_df)

        # Run tests
        a1_result = validator.validate_a1_naming_alignment()
        a2_result = validator.validate_a2_normalization_convention()
        a3_result = validator.validate_a3_scale_invariance()

        # Save results
        output_path = os.path.join(self.data_dir, 'assumption_validation.json')
        validator.save_validation_results(output_path)

        # Check for failures
        all_passed = all([a1_result['passed'], a2_result['passed'], a3_result['passed']])

        if not all_passed:
            self.logger.warning("Some assumptions failed - proceed with caution")
        else:
            self.logger.info("All assumptions passed")

        return validator.validation_results

    def run_training(self, train_df):
        """Phase 3: Train LogisticRegression classifier"""
        self.logger.info("=" * 80)
        self.logger.info("PHASE 3: Classifier Training")
        self.logger.info("=" * 80)

        trainer = LogisticClassifierTrainer()

        X_train = train_df[FEATURE_NAMES]
        y_train = train_df['family']

        # Train
        classifier, scaler = trainer.train(X_train, y_train)

        # Save artifacts
        os.makedirs(self.models_dir, exist_ok=True)
        trainer.save_artifacts(classifier, scaler, self.models_dir)

        self.logger.info("Training complete")
        return classifier, scaler

    def run_evaluation(self, classifier, scaler, val_df):
        """Phase 4: Evaluate on validation set"""
        self.logger.info("=" * 80)
        self.logger.info("PHASE 4: Validation Evaluation")
        self.logger.info("=" * 80)

        evaluator = ValidationEvaluator(classifier, scaler)

        X_val = val_df[FEATURE_NAMES]
        y_val = val_df['family']

        # Evaluate
        results = evaluator.evaluate(X_val, y_val)

        # Generate visualizations
        os.makedirs(self.results_dir, exist_ok=True)

        evaluator.generate_confusion_matrix(
            y_val, results['y_pred'],
            os.path.join(self.results_dir, 'confusion_matrix.png')
        )

        evaluator.generate_feature_importance(
            FEATURE_NAMES,
            os.path.join(self.results_dir, 'feature_importance.png')
        )

        evaluator.generate_r_distribution(
            val_df,
            os.path.join(self.results_dir, 'r_distribution.png')
        )

        # Get misclassified models
        misclassified = evaluator.get_misclassified_models(val_df, results['y_pred'])
        results['misclassified'] = misclassified

        # Store classifier coefficients for report
        results['classifier_coef'] = classifier.coef_

        self.logger.info("Evaluation complete")
        return results

    def run_reporting(self, results, assumptions, val_df):
        """Phase 5: Generate results report"""
        self.logger.info("=" * 80)
        self.logger.info("PHASE 5: Report Generation")
        self.logger.info("=" * 80)

        reporter = ResultsReporter(results, assumptions, val_df)

        output_path = os.path.join(self.results_dir, 'h_e1_results.md')
        reporter.generate_markdown_report(output_path, threshold=THRESHOLDS['macro_accuracy'])

        self.logger.info("Report generation complete")

        # Final decision
        decision = "PASSED" if results['macro_accuracy'] > THRESHOLDS['macro_accuracy'] else "FAILED"
        self.logger.info("=" * 80)
        self.logger.info(f"FINAL DECISION: {decision}")
        self.logger.info(f"Validation Accuracy: {results['macro_accuracy']:.2%}")
        self.logger.info(f"Threshold: {THRESHOLDS['macro_accuracy']:.0%}")
        self.logger.info("=" * 80)

        return decision

    def execute_full_pipeline(self):
        """Execute all phases sequentially"""
        start_time = datetime.now()

        try:
            # Phase 1: Data Preparation
            train_df, val_df = self.run_data_preparation()

            # Phase 2: Assumption Validation
            assumptions = self.run_assumption_validation(train_df)

            # Phase 3: Training
            classifier, scaler = self.run_training(train_df)

            # Phase 4: Evaluation
            results = self.run_evaluation(classifier, scaler, val_df)

            # Phase 5: Reporting
            decision = self.run_reporting(results, assumptions, val_df)

            end_time = datetime.now()
            duration = end_time - start_time

            self.logger.info("=" * 80)
            self.logger.info(f"Pipeline completed in {duration}")
            self.logger.info("=" * 80)

            return decision, results

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    pipeline = ExperimentPipeline()
    decision, results = pipeline.execute_full_pipeline()

    # Exit code based on decision
    sys.exit(0 if decision == "PASSED" else 1)
