"""Evaluation metrics and gate verification."""
from sklearn.metrics import f1_score, accuracy_score, classification_report
from config import GATE_MACRO_F1, EMBEDDING_DIM


def compute_metrics(y_true: list, y_pred: list) -> dict:
    """Compute macro-F1, accuracy, and classification report."""
    return {
        "macro_f1": f1_score(y_true, y_pred, average="macro"),
        "accuracy": accuracy_score(y_true, y_pred),
        "report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
    }


def verify_mechanism(model, X_sample: list, y_sample: list) -> bool:
    """Verify MiniLM+LogReg mechanism works correctly."""
    emb = model.encode(X_sample[:10])
    assert emb.shape == (10, EMBEDDING_DIM), f"Wrong embedding shape: {emb.shape}"
    assert hasattr(model.clf, "classes_"), "Classifier not fitted"
    preds = model.predict(X_sample[:10])
    assert set(preds).issubset(set(model.clf.classes_)), "Invalid predictions"
    print("Mechanism verification passed")
    return True


def gate_check(proposed_f1: float, baseline_f1: float, threshold: float = GATE_MACRO_F1) -> dict:
    """Check if proposed model passes MUST_WORK gate."""
    passed = proposed_f1 >= threshold and proposed_f1 > baseline_f1
    reasons = []
    if proposed_f1 < threshold:
        reasons.append(f"macro_f1 {proposed_f1:.4f} < threshold {threshold}")
    if proposed_f1 <= baseline_f1:
        reasons.append(f"proposed {proposed_f1:.4f} not > baseline {baseline_f1:.4f}")
    return {
        "pass": passed,
        "proposed_f1": proposed_f1,
        "baseline_f1": baseline_f1,
        "threshold": threshold,
        "reasons": reasons,
    }
