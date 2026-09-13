"""Gate verification for H-M3"""
from metrics import compute_relative_arch_diff

def verify_gate(results: dict, threshold: float = 0.10) -> dict:
    """Check if any method shows >threshold relative AUC difference across architectures.

    results: {method: {"bert": auc, "gpt2": auc}}
    Returns: {"pass": bool, "per_method_diff": {method: diff}, "max_diff": float, "max_method": str}
    """
    per_method_diff = {}
    max_diff = 0.0
    max_method = None

    for method, aucs in results.items():
        bert_auc = aucs.get("bert", 0.5)
        gpt2_auc = aucs.get("gpt2", 0.5)
        diff = compute_relative_arch_diff(bert_auc, gpt2_auc)
        per_method_diff[method] = diff

        if diff > max_diff:
            max_diff = diff
            max_method = method

    gate_pass = any(d > threshold for d in per_method_diff.values())

    return {
        "pass": gate_pass,
        "per_method_diff": per_method_diff,
        "max_diff": max_diff,
        "max_method": max_method,
        "threshold": threshold,
    }
