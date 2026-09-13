def verify_hessian_gate(bert_metrics, gpt2_metrics, threshold=0.10):
    """Check if BERT and GPT-2 show measurable Hessian spectrum difference."""
    metrics_to_compare = ["top_eigenvalue", "eigenvalue_ratio", "trace"]
    diffs = {}

    for m in metrics_to_compare:
        bert_val = bert_metrics.get(m, 0)
        gpt2_val = gpt2_metrics.get(m, 0)
        denom = max(abs(bert_val), abs(gpt2_val), 1e-12)
        diffs[m] = abs(bert_val - gpt2_val) / denom

    gate_pass = any(v > threshold for v in diffs.values())
    max_diff = max(diffs.values())
    max_metric = max(diffs, key=diffs.get)

    return {
        "diffs": diffs,
        "gate_pass": gate_pass,
        "max_diff": max_diff,
        "max_metric": max_metric,
        "threshold": threshold,
    }
