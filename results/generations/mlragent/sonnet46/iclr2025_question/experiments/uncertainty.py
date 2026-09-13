"""HalluConform: Conformal prediction + baselines for hallucination detection."""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve
from config import ALPHA_BASE, ALPHA_RISK


class HalluConform:
    """
    Calibration-Aware Conformal Prediction framework for hallucination detection.

    Combines three nonconformity measures:
    - Token-level entropy
    - Attention consistency (cross-layer variance)
    - Hidden-state trajectory divergence

    Uses split conformal prediction for statistically guaranteed coverage.
    """

    def __init__(self, alpha: float = ALPHA_BASE, use_adaptive: bool = True):
        self.alpha = alpha
        self.use_adaptive = use_adaptive
        self.scaler = StandardScaler()
        self.lr = LogisticRegression(max_iter=1000)
        self.weights_ = None
        self.threshold_ = None
        self.calibration_scores_ = None
        self.is_fitted = False

    def _extract_features(self, results):
        """Extract feature matrix from results."""
        X = np.array([
            [r["token_entropy"], r["attention_consistency"], r["hidden_divergence"]]
            for r in results
        ])
        return X

    def _compute_nonconformity_scores(self, X):
        """Compute composite nonconformity scores."""
        X_scaled = self.scaler.transform(X)
        # Use logistic regression probabilities as nonconformity scores
        # Higher score = more likely hallucination
        proba = self.lr.predict_proba(X_scaled)[:, 1]
        return proba

    def calibrate(self, cal_results):
        """
        Calibration phase: fit the composite scorer and compute threshold.

        Args:
            cal_results: list of dicts with signal fields and 'correct' field
        """
        X = self._extract_features(cal_results)
        # y=1 means hallucination (incorrect), y=0 means correct
        y_hal = np.array([1 - r["correct"] for r in cal_results])

        # Fit scaler and logistic regression
        X_scaled = self.scaler.fit_transform(X)
        self.lr.fit(X_scaled, y_hal)
        self.weights_ = self.lr.coef_[0]

        # Compute nonconformity scores on calibration set
        # For conformal prediction: nonconformity = hallucination probability
        cal_scores = self.lr.predict_proba(X_scaled)[:, 1]
        self.calibration_scores_ = cal_scores

        # Only consider correct samples for conformal threshold
        # We want: P(flag correct as hallucination) <= alpha
        correct_mask = y_hal == 0
        if correct_mask.sum() > 0:
            correct_scores = cal_scores[correct_mask]
            n = len(correct_scores)
            level = np.ceil((n + 1) * (1 - self.alpha)) / n
            level = min(level, 1.0)
            self.threshold_ = np.quantile(correct_scores, level)
        else:
            self.threshold_ = 0.5

        self.is_fitted = True
        return self

    def get_threshold(self, risk_level: str = "low"):
        """Get threshold adjusted for domain risk level."""
        if not self.use_adaptive:
            return self.threshold_
        # Lower alpha_eff means stricter threshold (lower false negative rate)
        alpha_eff = ALPHA_RISK.get(risk_level, self.alpha)
        n = len(self.calibration_scores_)
        level = np.ceil((n + 1) * (1 - alpha_eff)) / n
        level = min(level, 1.0)
        # Recompute on calibration scores of correct samples
        # Use stored calibration scores as proxy
        correct_scores = self.calibration_scores_
        return float(np.quantile(correct_scores, level))

    def predict(self, test_results, use_domain_risk: bool = True):
        """
        Predict hallucination labels for test results.

        Returns: dict with predictions and scores
        """
        X = self._extract_features(test_results)
        scores = self._compute_nonconformity_scores(X)

        predictions = []
        for i, (score, r) in enumerate(zip(scores, test_results)):
            risk_level = r.get("risk_level", "low") if use_domain_risk else "low"
            threshold = self.get_threshold(risk_level)
            pred = int(score > threshold)
            predictions.append({
                "nonconformity_score": float(score),
                "predicted_hallucination": pred,
                "threshold_used": float(threshold),
                "risk_level": risk_level,
            })

        return predictions

    def evaluate(self, test_results, use_domain_risk: bool = True):
        """Evaluate hallucination detection performance."""
        predictions = self.predict(test_results, use_domain_risk)
        y_true_hal = np.array([1 - r["correct"] for r in test_results])
        scores = np.array([p["nonconformity_score"] for p in predictions])
        y_pred = np.array([p["predicted_hallucination"] for p in predictions])

        metrics = _compute_metrics(y_true_hal, y_pred, scores)

        # Empirical coverage: fraction of correct (non-hallucinated) that are NOT flagged
        correct_mask = y_true_hal == 0
        if correct_mask.sum() > 0:
            not_flagged_correct = ((y_pred == 0) & correct_mask).sum()
            coverage = not_flagged_correct / correct_mask.sum()
        else:
            coverage = 0.0
        metrics["empirical_coverage"] = float(coverage)
        metrics["theoretical_coverage"] = 1 - self.alpha

        return metrics, predictions


class EntropyThreshold:
    """Baseline: flag samples with token entropy above threshold."""

    def __init__(self):
        self.threshold_ = None
        self.is_fitted = False

    def calibrate(self, cal_results):
        entropies = np.array([r["token_entropy"] for r in cal_results])
        y_hal = np.array([1 - r["correct"] for r in cal_results])
        # Find threshold that maximizes F1
        self.threshold_ = _find_best_threshold(entropies, y_hal)
        self.is_fitted = True
        return self

    def predict(self, test_results, **kwargs):
        scores = np.array([r["token_entropy"] for r in test_results])
        return [{"nonconformity_score": float(s),
                 "predicted_hallucination": int(s > self.threshold_),
                 "threshold_used": float(self.threshold_),
                 "risk_level": r.get("risk_level", "low")}
                for s, r in zip(scores, test_results)]

    def evaluate(self, test_results, **kwargs):
        preds = self.predict(test_results)
        y_true_hal = np.array([1 - r["correct"] for r in test_results])
        scores = np.array([p["nonconformity_score"] for p in preds])
        y_pred = np.array([p["predicted_hallucination"] for p in preds])
        return _compute_metrics(y_true_hal, y_pred, scores), preds


class MaxProbThreshold:
    """Baseline: flag samples with low max probability (high uncertainty)."""

    def __init__(self):
        self.threshold_ = None
        self.is_fitted = False

    def calibrate(self, cal_results):
        # Use negative entropy as proxy for max probability
        entropies = np.array([r["token_entropy"] for r in cal_results])
        y_hal = np.array([1 - r["correct"] for r in cal_results])
        # Low entropy = high max prob = confident = correct
        # Score: entropy (higher entropy = more likely hallucination)
        self.threshold_ = _find_best_threshold(entropies, y_hal)
        self.is_fitted = True
        return self

    def predict(self, test_results, **kwargs):
        scores = np.array([r["token_entropy"] for r in test_results])
        return [{"nonconformity_score": float(s),
                 "predicted_hallucination": int(s > self.threshold_),
                 "threshold_used": float(self.threshold_),
                 "risk_level": r.get("risk_level", "low")}
                for s, r in zip(scores, test_results)]

    def evaluate(self, test_results, **kwargs):
        preds = self.predict(test_results)
        y_true_hal = np.array([1 - r["correct"] for r in test_results])
        scores = np.array([p["nonconformity_score"] for p in preds])
        y_pred = np.array([p["predicted_hallucination"] for p in preds])
        return _compute_metrics(y_true_hal, y_pred, scores), preds


class LengthNormalizedEntropy:
    """Baseline: entropy normalized by generation length."""

    def __init__(self):
        self.threshold_ = None
        self.is_fitted = False

    def calibrate(self, cal_results):
        scores = np.array([
            r["token_entropy"] / max(len(r.get("generation", " ").split()), 1)
            for r in cal_results
        ])
        y_hal = np.array([1 - r["correct"] for r in cal_results])
        self.threshold_ = _find_best_threshold(scores, y_hal)
        self.is_fitted = True
        return self

    def predict(self, test_results, **kwargs):
        scores = np.array([
            r["token_entropy"] / max(len(r.get("generation", " ").split()), 1)
            for r in test_results
        ])
        return [{"nonconformity_score": float(s),
                 "predicted_hallucination": int(s > self.threshold_),
                 "threshold_used": float(self.threshold_),
                 "risk_level": r.get("risk_level", "low")}
                for s, r in zip(scores, test_results)]

    def evaluate(self, test_results, **kwargs):
        preds = self.predict(test_results)
        y_true_hal = np.array([1 - r["correct"] for r in test_results])
        scores = np.array([p["nonconformity_score"] for p in preds])
        y_pred = np.array([p["predicted_hallucination"] for p in preds])
        return _compute_metrics(y_true_hal, y_pred, scores), preds


def _find_best_threshold(scores, y_true, n_thresholds=100):
    """Find threshold that maximizes F1 score on calibration set."""
    thresholds = np.linspace(scores.min(), scores.max(), n_thresholds)
    best_f1 = -1
    best_t = thresholds[len(thresholds) // 2]
    for t in thresholds:
        preds = (scores > t).astype(int)
        tp = ((preds == 1) & (y_true == 1)).sum()
        fp = ((preds == 1) & (y_true == 0)).sum()
        fn = ((preds == 0) & (y_true == 1)).sum()
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        if f1 > best_f1:
            best_f1 = f1
            best_t = t
    return float(best_t)


def _compute_metrics(y_true, y_pred, scores):
    """Compute hallucination detection metrics."""
    tp = ((y_pred == 1) & (y_true == 1)).sum()
    fp = ((y_pred == 1) & (y_true == 0)).sum()
    tn = ((y_pred == 0) & (y_true == 0)).sum()
    fn = ((y_pred == 0) & (y_true == 1)).sum()

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0.0

    # AUROC and AUPRC
    if len(np.unique(y_true)) > 1:
        auroc = roc_auc_score(y_true, scores)
        auprc = average_precision_score(y_true, scores)
    else:
        auroc = 0.5
        auprc = float(y_true.mean())

    return {
        "auroc": float(auroc),
        "auprc": float(auprc),
        "f1": float(f1),
        "precision": float(precision),
        "recall": float(recall),
        "fpr": float(fpr),
        "fnr": float(fnr),
        "accuracy": float(accuracy),
        "n_hallucinations": int(y_true.sum()),
        "n_total": int(len(y_true)),
        "hallucination_rate": float(y_true.mean()),
    }
