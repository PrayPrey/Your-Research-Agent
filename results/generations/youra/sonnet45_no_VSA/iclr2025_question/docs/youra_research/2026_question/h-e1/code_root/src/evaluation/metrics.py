"""Evaluation metrics for uncertainty quantification."""

import numpy as np
from sklearn.metrics import roc_auc_score
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def check_answer_correctness(predicted: str, ground_truth: str) -> bool:
    """Simple exact match for answer correctness."""
    pred = predicted.lower().strip()
    gt = ground_truth.lower().strip() if isinstance(ground_truth, str) else ground_truth[0].lower().strip()
    return gt in pred or pred in gt


class AUROCComputer:
    """Compute AUROC with bootstrap confidence intervals."""
    
    def compute_auroc(self, y_true: np.ndarray, y_scores: np.ndarray) -> float:
        """Compute AUROC point estimate."""
        try:
            return roc_auc_score(y_true, y_scores)
        except ValueError as e:
            logger.warning(f"AUROC computation failed: {e}")
            return 0.5
    
    def compute_with_ci(
        self,
        y_true: np.ndarray,
        y_scores: np.ndarray,
        n_bootstrap: int = 1000,
        random_state: int = 42
    ) -> Dict[str, float]:
        """Compute AUROC with 95% bootstrap confidence intervals."""
        np.random.seed(random_state)
        
        # Point estimate
        auroc = self.compute_auroc(y_true, y_scores)
        
        # Bootstrap
        bootstrap_aurocs = []
        n = len(y_true)
        
        for _ in range(n_bootstrap):
            indices = np.random.choice(n, size=n, replace=True)
            try:
                boot_auroc = roc_auc_score(y_true[indices], y_scores[indices])
                bootstrap_aurocs.append(boot_auroc)
            except ValueError:
                continue
        
        if bootstrap_aurocs:
            ci_lower = np.percentile(bootstrap_aurocs, 2.5)
            ci_upper = np.percentile(bootstrap_aurocs, 97.5)
        else:
            ci_lower = auroc
            ci_upper = auroc
        
        return {
            'auroc': auroc,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper
        }


class RiskCoverageComputer:
    """Compute risk-coverage curves."""
    
    def compute_curve(
        self,
        y_true: np.ndarray,
        y_scores: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute error rate at each coverage threshold."""
        # Sort by uncertainty (descending)
        sorted_indices = np.argsort(-y_scores)
        sorted_labels = y_true[sorted_indices]
        
        coverages = np.linspace(0, 1, 101)
        error_rates = []
        
        for cov in coverages:
            n_retained = int(len(sorted_labels) * cov)
            if n_retained == 0:
                error_rates.append(0.0)
            else:
                error_rates.append(1.0 - np.mean(sorted_labels[:n_retained]))
        
        return coverages, np.array(error_rates)
    
    def compute_error_reduction(
        self,
        y_true: np.ndarray,
        baseline_scores: np.ndarray,
        method_scores: np.ndarray,
        coverage: float = 0.8
    ) -> float:
        """Compute error reduction at specific coverage."""
        _, baseline_errors = self.compute_curve(y_true, baseline_scores)
        _, method_errors = self.compute_curve(y_true, method_scores)
        
        cov_idx = int(coverage * 100)
        baseline_error = baseline_errors[cov_idx]
        method_error = method_errors[cov_idx]
        
        if baseline_error == 0:
            return 0.0
        
        reduction = (baseline_error - method_error) / baseline_error
        return reduction


class EvaluationRunner:
    """Run full evaluation pipeline."""
    
    def __init__(self):
        self.auroc_computer = AUROCComputer()
        self.risk_coverage = RiskCoverageComputer()
    
    def evaluate_all_methods(
        self,
        samples: List[Dict],
        generations: Dict[int, List],
        baseline_scores: Dict[str, Dict[int, float]],
        semantic_entropy_scores: Dict[int, float]
    ) -> Dict:
        """Evaluate all methods and compute metrics."""
        logger.info("Running evaluation")
        
        # Compute labels (1 = correct, 0 = incorrect)
        labels = []
        msp_scores = []
        entropy_scores = []
        se_scores = []
        
        for sample in samples:
            example_id = sample['example_id']
            if example_id not in generations or example_id not in semantic_entropy_scores:
                continue
            
            # Check correctness of first generated answer
            first_answer = generations[example_id][0].text
            is_correct = check_answer_correctness(first_answer, sample['ground_truth'])
            
            labels.append(1 if is_correct else 0)
            msp_scores.append(baseline_scores['msp'][example_id])
            entropy_scores.append(baseline_scores['token_entropy'][example_id])
            se_scores.append(semantic_entropy_scores[example_id])
        
        labels = np.array(labels)
        msp_scores = np.array(msp_scores)
        entropy_scores = np.array(entropy_scores)
        se_scores = np.array(se_scores)
        
        # Invert labels for AUROC (1 = incorrect, 0 = correct)
        y_true = 1 - labels
        
        logger.info(f"Evaluation on {len(labels)} examples")
        logger.info(f"Accuracy: {np.mean(labels):.3f}")
        
        # Compute AUROC with CI
        results = {
            'msp': self.auroc_computer.compute_with_ci(y_true, msp_scores),
            'token_entropy': self.auroc_computer.compute_with_ci(y_true, entropy_scores),
            'semantic_entropy': self.auroc_computer.compute_with_ci(y_true, se_scores)
        }
        
        # Compute error reduction
        error_reduction = self.risk_coverage.compute_error_reduction(
            labels, msp_scores, se_scores, coverage=0.8
        )
        results['error_reduction_80'] = error_reduction
        
        # Log results
        logger.info("\n=== AUROC Results ===")
        for method, scores in results.items():
            if isinstance(scores, dict):
                logger.info(f"{method}: {scores['auroc']:.4f} ({scores['ci_lower']:.4f}, {scores['ci_upper']:.4f})")
        logger.info(f"Error reduction @ 80%: {error_reduction:.2%}")
        
        return results
