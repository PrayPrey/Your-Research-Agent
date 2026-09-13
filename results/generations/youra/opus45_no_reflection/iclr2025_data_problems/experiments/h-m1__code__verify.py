"""Gate verification for H-M1."""
from config import GATE_CONFIG


def verify_attention_structure(bert_metrics: dict, gpt2_metrics: dict) -> dict:
    """
    Verify that BERT has low upper-triangle sparsity (bidirectional)
    and GPT-2 has high upper-triangle sparsity (causal).

    Returns dict with gate pass/fail status.
    """
    bert_sparsity = bert_metrics["upper_sparsity"]
    gpt2_sparsity = gpt2_metrics["upper_sparsity"]

    bert_pass = bert_sparsity < GATE_CONFIG["bert_max_sparsity"]
    gpt2_pass = gpt2_sparsity > GATE_CONFIG["gpt2_min_sparsity"]

    diff = gpt2_sparsity - bert_sparsity
    gate_pass = bert_pass and gpt2_pass

    return {
        "sparsity_difference": float(diff),
        "bert_upper_sparsity": float(bert_sparsity),
        "gpt2_upper_sparsity": float(gpt2_sparsity),
        "bert_is_causal": bert_metrics["is_causal"],
        "gpt2_is_causal": gpt2_metrics["is_causal"],
        "bert_pass": bert_pass,
        "gpt2_pass": gpt2_pass,
        "gate_pass": gate_pass,
        "thresholds": {
            "bert_max": GATE_CONFIG["bert_max_sparsity"],
            "gpt2_min": GATE_CONFIG["gpt2_min_sparsity"],
        },
    }
