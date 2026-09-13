"""Pairwise cosine similarity matrix + gate evaluation for H-E1."""
import numpy as np
import torch

SOURCES = ["humaneval_train", "mbpp_train", "leetcode", "equal_mix"]
BENCHMARKS = ["humaneval_plus", "mbpp_plus"]
GATE_THRESHOLD = 0.95


def mean_pairwise_cosine(src: torch.Tensor, tgt: torch.Tensor) -> float:
    """dot(src, tgt.T).mean() — valid because both are L2-normalized."""
    return (src.cpu() @ tgt.cpu().T).mean().item()


def compute_similarity_matrix(embeddings: dict) -> dict:
    """Returns {"codebert": ndarray(4,2), "minilm": ndarray(4,2)}.
    Rows: SOURCES order, cols: BENCHMARKS order.
    """
    result = {}
    for encoder in ["codebert", "minilm"]:
        mat = np.zeros((len(SOURCES), len(BENCHMARKS)))
        for i, src_name in enumerate(SOURCES):
            for j, bm_name in enumerate(BENCHMARKS):
                mat[i, j] = mean_pairwise_cosine(
                    embeddings[src_name][encoder],
                    embeddings[bm_name][encoder],
                )
        result[encoder] = mat
    return result


def evaluate_gate(sim_matrices: dict) -> dict:
    """Returns gate evaluation dict with all 16 similarity values.
    Gate SATISFIED if any value < GATE_THRESHOLD (0.95).
    """
    all_values = []
    for mat in sim_matrices.values():
        all_values.extend(mat.flatten().tolist())

    return {
        "gate_satisfied": min(all_values) < GATE_THRESHOLD,
        "min_sim": float(min(all_values)),
        "max_sim": float(max(all_values)),
        "mean_sim": float(np.mean(all_values)),
        "std_sim": float(np.std(all_values)),
        "all_values": all_values,
        "threshold": GATE_THRESHOLD,
    }


def verify_embeddings(embeddings: dict, sim_matrices: dict) -> tuple:
    """Shape checks + gate check. Returns (all_pass, checks_dict)."""
    checks = {}
    all_pass = True

    for name, enc_dict in embeddings.items():
        cb = enc_dict.get("codebert")
        ml = enc_dict.get("minilm")
        if cb is not None and cb.ndim == 2 and cb.shape[1] == 768:
            checks[f"{name}_codebert_shape"] = True
        else:
            checks[f"{name}_codebert_shape"] = False
            all_pass = False
        if ml is not None and ml.ndim == 2 and ml.shape[1] == 384:
            checks[f"{name}_minilm_shape"] = True
        else:
            checks[f"{name}_minilm_shape"] = False
            all_pass = False

    for encoder, mat in sim_matrices.items():
        std_ok = float(np.std(mat)) > 0.001
        checks[f"{encoder}_matrix_std"] = std_ok
        if not std_ok:
            all_pass = False

    gate_result = evaluate_gate(sim_matrices)
    checks["gate_satisfied"] = gate_result["gate_satisfied"]

    return all_pass, checks
