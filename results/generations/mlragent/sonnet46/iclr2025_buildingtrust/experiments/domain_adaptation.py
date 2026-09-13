"""Domain-Adaptive Policy Layer (DAPL) for CARE framework."""

import numpy as np
from config import DOMAINS, LAMBDA, DEFAULT_ALPHA


# Regulatory knowledge base: domain-specific threshold adjustments
# Delta_Theta: positive values lower thresholds (more conservative)
REGULATORY_KNOWLEDGE_BASE = {
    "healthcare": {
        "base_alpha_adjust": -0.05,  # More conservative (lower false negative rate)
        "category_weights": {
            "hate_speech": 0.8,
            "violence_incitement": 1.2,
            "self_harm": 1.5,      # Higher weight for healthcare
            "misinformation": 1.3,  # Medical misinformation is very serious
            "harassment": 0.9,
        },
        "lambda": 1.0,
        "regulation": "HIPAA",
    },
    "finance": {
        "base_alpha_adjust": -0.03,
        "category_weights": {
            "hate_speech": 0.7,
            "violence_incitement": 0.8,
            "self_harm": 0.9,
            "misinformation": 1.4,  # Financial misinformation is critical
            "harassment": 1.1,
        },
        "lambda": 0.8,
        "regulation": "MiFID II",
    },
    "general": {
        "base_alpha_adjust": 0.0,
        "category_weights": {
            "hate_speech": 1.0,
            "violence_incitement": 1.0,
            "self_harm": 1.0,
            "misinformation": 1.0,
            "harassment": 1.0,
        },
        "lambda": 0.0,
        "regulation": "General",
    },
}


class DomainAdaptivePolicyLayer:
    """
    DAPL: dynamically adjusts decision thresholds based on deployment context.
    Implements: Theta_eff(d) = Theta_base + lambda * Delta_Theta(d)
    """

    def __init__(self, base_alpha=DEFAULT_ALPHA, base_lambda=LAMBDA):
        self.base_alpha = base_alpha
        self.base_lambda = base_lambda
        self.rkb = REGULATORY_KNOWLEDGE_BASE

    def get_effective_alpha(self, domain):
        """Compute effective coverage level for a domain."""
        if domain not in self.rkb:
            domain = "general"
        reg = self.rkb[domain]
        lam = reg["lambda"]
        delta_alpha = reg["base_alpha_adjust"]
        # More lambda -> more conservative -> lower alpha -> higher coverage
        effective_alpha = self.base_alpha + lam * delta_alpha
        effective_alpha = np.clip(effective_alpha, 0.01, 0.49)
        return effective_alpha

    def adjust_category_thresholds(self, base_thresholds, domain):
        """Adjust per-category thresholds based on domain regulation."""
        if domain not in self.rkb:
            domain = "general"
        reg = self.rkb[domain]
        lam = reg["lambda"]
        weights = reg["category_weights"]

        effective_thresholds = {}
        for cat, base_thresh in base_thresholds.items():
            weight = weights.get(cat, 1.0)
            # Higher weight -> lower threshold (more sensitive)
            delta = lam * (1.0 / weight - 1.0) * 0.1
            effective_thresholds[cat] = np.clip(base_thresh + delta, 0.1, 0.9)
        return effective_thresholds

    def apply_domain_adaptation(self, probs, domain, conformal_predictor):
        """
        Apply domain-adapted conformal prediction.
        Returns decisions with domain-adjusted thresholds.
        """
        effective_alpha = self.get_effective_alpha(domain)
        # Find closest calibrated alpha
        available_alphas = list(conformal_predictor.quantile_thresholds.keys())
        closest_alpha = min(available_alphas, key=lambda a: abs(a - effective_alpha))
        decisions, _, pred_sets = conformal_predictor.predict_set(
            probs_only=probs, alpha=closest_alpha
        )
        return decisions, effective_alpha, closest_alpha


def evaluate_domain_adaptation(
    conformal_pred, dapl, domain_test_sets, base_alpha=DEFAULT_ALPHA
):
    """
    Compare CARE performance with and without DAPL for each domain.
    Returns F1 delta (DAPL-enabled vs disabled).
    """
    results = {}
    for domain, (texts, labels) in domain_test_sets.items():
        labels_arr = np.array(labels)

        # Without DAPL (use base alpha)
        decisions_base, probs, _ = conformal_pred.predict_set(texts, alpha=base_alpha)
        preds_base = np.array([1 if d == "unsafe" else 0 for d in decisions_base])

        # With DAPL (use domain-adjusted alpha)
        eff_alpha = dapl.get_effective_alpha(domain)
        available_alphas = list(conformal_pred.quantile_thresholds.keys())
        closest_alpha = min(available_alphas, key=lambda a: abs(a - eff_alpha))
        decisions_dapl, _, _ = conformal_pred.predict_set(texts, alpha=closest_alpha)
        preds_dapl = np.array([1 if d == "unsafe" else 0 for d in decisions_dapl])

        from sklearn.metrics import f1_score, precision_score, recall_score
        f1_base = f1_score(labels_arr, preds_base, zero_division=0)
        f1_dapl = f1_score(labels_arr, preds_dapl, zero_division=0)
        prec_base = precision_score(labels_arr, preds_base, zero_division=0)
        rec_base = recall_score(labels_arr, preds_base, zero_division=0)
        prec_dapl = precision_score(labels_arr, preds_dapl, zero_division=0)
        rec_dapl = recall_score(labels_arr, preds_dapl, zero_division=0)

        results[domain] = {
            "f1_base": float(f1_base),
            "f1_dapl": float(f1_dapl),
            "f1_delta": float(f1_dapl - f1_base),
            "precision_base": float(prec_base),
            "precision_dapl": float(prec_dapl),
            "recall_base": float(rec_base),
            "recall_dapl": float(rec_dapl),
            "effective_alpha": float(eff_alpha),
            "base_alpha": float(base_alpha),
            "regulation": REGULATORY_KNOWLEDGE_BASE.get(domain, {}).get("regulation", "N/A"),
        }
        print(f"  Domain {domain}: F1 {f1_base:.3f} -> {f1_dapl:.3f} (delta={f1_dapl-f1_base:+.3f})")

    return results
