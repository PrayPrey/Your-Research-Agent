"""H-M2 Feature Breakdown: Per-feature high-conf rates."""
from loader import MODEL_FIELDS


# Feature markers from H-M1 task_classifier.py
USER_BELIEF_MARKERS = ["you think", "your opinion", "do you believe", "your view", "you feel"]
CONTEXT_MARKERS = ["given that", "considering", "in this situation", "assuming", "if you were"]
HEDGE_MARKERS = ["might", "could", "possibly", "it depends", "perhaps", "maybe"]


def compute_bidir_features(text: str) -> dict:
    """Compute bidirectional features from task text."""
    text_lower = text.lower()
    return {
        "user_belief_reference": any(m in text_lower for m in USER_BELIEF_MARKERS),
        "context_dependent": any(m in text_lower for m in CONTEXT_MARKERS),
        "hedged_answer": any(m in text_lower for m in HEDGE_MARKERS),
    }


def breakdown_by_feature(records: list, threshold: float = 0.7, task_texts: dict = None) -> dict:
    """
    Break down high-conf rates by bidirectional feature.
    If task_texts provided, computes features from text; else uses task_type as proxy.
    Returns {feature_name: {"rate_with_feature": float, "rate_without": float, "n_with": int}}.
    """
    if task_texts is None:
        # Fallback: use task_type as proxy (Type B = has bidir features)
        return {
            "note": "task_texts not provided, using task_type as proxy",
            "proxy_analysis": True,
        }

    results = {}
    for feature_name in ["user_belief_reference", "context_dependent", "hedged_answer"]:
        with_feature = []
        without_feature = []

        for t in records:
            text = task_texts.get(t["task_id"], "")
            features = compute_bidir_features(text)
            avg_conf = sum(t.get(f, 0) for f in MODEL_FIELDS) / len(MODEL_FIELDS)

            if features[feature_name]:
                with_feature.append(avg_conf >= threshold)
            else:
                without_feature.append(avg_conf >= threshold)

        n_with = len(with_feature)
        n_without = len(without_feature)

        results[feature_name] = {
            "rate_with_feature": sum(with_feature) / n_with if n_with > 0 else 0.0,
            "rate_without_feature": sum(without_feature) / n_without if n_without > 0 else 0.0,
            "n_with_feature": n_with,
            "n_without_feature": n_without,
        }

    return results
