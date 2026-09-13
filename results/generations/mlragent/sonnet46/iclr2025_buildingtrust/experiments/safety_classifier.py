"""Safety classifier with conformal prediction (UQM) for CARE framework."""

import numpy as np
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)
from config import SEED, DEFAULT_ALPHA, ALPHA_VALUES


class TfidfSafetyClassifier:
    """TF-IDF + Logistic Regression safety classifier (fast baseline)."""

    def __init__(self, seed=SEED):
        self.vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
        self.clf = LogisticRegression(max_iter=1000, random_state=seed)
        self.fitted = False

    def fit(self, texts, labels):
        X = self.vectorizer.fit_transform(texts)
        self.clf.fit(X, labels)
        self.fitted = True
        return self

    def predict_proba(self, texts):
        X = self.vectorizer.transform(texts)
        return self.clf.predict_proba(X)[:, 1]

    def predict(self, texts):
        probs = self.predict_proba(texts)
        return (probs > 0.5).astype(int)


class RoBERTaSafetyClassifier:
    """RoBERTa-based hate speech detector using HuggingFace."""

    def __init__(self, device=None):
        if device is None:
            device = 0 if torch.cuda.is_available() else -1
        self.device = device
        self.model_name = "facebook/roberta-hate-speech-dynabench-r4-target"
        self.pipe = None

    def load(self):
        print(f"  Loading RoBERTa classifier on device {self.device}...")
        self.pipe = pipeline(
            "text-classification",
            model=self.model_name,
            device=self.device,
            truncation=True,
            max_length=128,
        )
        print("  RoBERTa loaded.")
        return self

    def predict_proba(self, texts, batch_size=32):
        """Return probability of 'hate'/'unsafe' label."""
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            out = self.pipe(batch, truncation=True, max_length=128)
            for item in out:
                label = item["label"].lower()
                score = item["score"]
                # 'nothate' -> safe, 'hate' -> unsafe
                # 'normal'/'label_0' -> safe
                if label in ["nothate", "not_hate", "normal", "label_0", "0"]:
                    results.append(1.0 - score)
                elif label in ["hate", "label_1", "toxic", "offensive", "1"]:
                    results.append(score)
                else:
                    # Unknown label: use score as-is if > 0.5 means unsafe
                    results.append(score)
        return np.array(results)

    def predict(self, texts):
        probs = self.predict_proba(texts)
        return (probs > 0.5).astype(int)


class ConformaPredictor:
    """
    Conformal Prediction wrapper for uncertainty quantification (UQM).
    Implements CARE's tripartite classification: high-conf safe, high-conf unsafe, ambiguous.
    """

    def __init__(self, base_classifier):
        self.clf = base_classifier
        self.quantile_thresholds = {}  # alpha -> q_hat
        self.calibrated = False

    def calibrate(self, cal_texts, cal_labels, alpha_values=None):
        """
        Compute conformal quantile thresholds on calibration set.
        Uses nonconformity score: s = 1 - f(x)[y_true]
        """
        if alpha_values is None:
            alpha_values = ALPHA_VALUES

        print("  Computing conformal calibration...")
        probs = self.clf.predict_proba(cal_texts)
        cal_labels = np.array(cal_labels)

        nonconf_scores = []
        for prob, label in zip(probs, cal_labels):
            # prob is P(unsafe), label is 0 or 1
            p_true = prob if label == 1 else (1 - prob)
            s = 1 - p_true
            nonconf_scores.append(s)
        nonconf_scores = np.array(nonconf_scores)

        n = len(nonconf_scores)
        for alpha in alpha_values:
            level = np.ceil((n + 1) * (1 - alpha)) / n
            level = min(level, 1.0)
            q_hat = np.quantile(nonconf_scores, level)
            self.quantile_thresholds[alpha] = q_hat

        self.calibrated = True
        print(f"  Calibration complete for alpha values: {alpha_values}")
        print(f"  Quantile thresholds: {self.quantile_thresholds}")
        return nonconf_scores

    def predict_set(self, texts, alpha=DEFAULT_ALPHA):
        """
        Return prediction sets and tripartite classification.
        Returns:
          - decisions: 'safe' | 'unsafe' | 'ambiguous'
          - probs: raw classifier probabilities
          - pred_sets: list of prediction sets {0}, {1}, or {0,1}
        """
        if not self.calibrated:
            raise RuntimeError("Must calibrate before prediction.")

        q_hat = self.quantile_thresholds[alpha]
        probs = self.clf.predict_proba(texts)
        decisions = []
        pred_sets = []

        for prob in probs:
            # s(x, y=1) = 1 - prob
            # s(x, y=0) = 1 - (1 - prob) = prob
            s_unsafe = 1 - prob
            s_safe = prob

            in_unsafe = s_unsafe <= q_hat
            in_safe = s_safe <= q_hat

            if in_unsafe and in_safe:
                decisions.append("ambiguous")
                pred_sets.append({0, 1})
            elif in_unsafe:
                decisions.append("unsafe")
                pred_sets.append({1})
            elif in_safe:
                decisions.append("safe")
                pred_sets.append({0})
            else:
                # Empty prediction set (shouldn't happen at valid alpha)
                decisions.append("ambiguous")
                pred_sets.append(set())

        return decisions, probs, pred_sets

    def evaluate_coverage(self, test_texts, test_labels):
        """Compute empirical coverage rates for each alpha."""
        test_labels = np.array(test_labels)
        probs = self.clf.predict_proba(test_texts)

        coverage_rates = {}
        for alpha, q_hat in self.quantile_thresholds.items():
            covered = 0
            for prob, label in zip(probs, test_labels):
                # Check if true label is in prediction set
                s_true = 1 - prob if label == 1 else prob
                if s_true <= q_hat:
                    covered += 1
            coverage_rates[alpha] = covered / len(test_labels)

        return coverage_rates

    def get_ambiguity_rate(self, texts, alpha=DEFAULT_ALPHA):
        """Compute fraction of ambiguous predictions."""
        decisions, _, _ = self.predict_set(texts, alpha=alpha)
        return sum(1 for d in decisions if d == "ambiguous") / len(decisions)


def evaluate_classifier(clf, test_texts, test_labels, name="Classifier"):
    """Compute standard safety classification metrics."""
    test_labels = np.array(test_labels)

    if hasattr(clf, "predict_proba"):
        probs = clf.predict_proba(test_texts)
        preds = (probs > 0.5).astype(int)
    else:
        preds = clf.predict(test_texts)
        probs = preds.astype(float)

    acc = accuracy_score(test_labels, preds)
    prec = precision_score(test_labels, preds, zero_division=0)
    rec = recall_score(test_labels, preds, zero_division=0)
    f1 = f1_score(test_labels, preds, zero_division=0)

    try:
        auroc = roc_auc_score(test_labels, probs)
    except Exception:
        auroc = float("nan")

    metrics = {
        "name": name,
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "auroc": float(auroc),
    }
    return metrics, probs


def compute_ece(probs, labels, n_bins=10):
    """Compute Expected Calibration Error."""
    probs = np.array(probs)
    labels = np.array(labels)
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
        if mask.sum() == 0:
            continue
        avg_conf = probs[mask].mean()
        avg_acc = labels[mask].mean()
        ece += mask.sum() / len(probs) * abs(avg_conf - avg_acc)
    return float(ece)
