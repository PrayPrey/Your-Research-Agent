"""Analysis functions for H-M1: LLaMA-2 within-family RLHF effect on safety+ethics."""
import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import binomtest

from config import (
    DIMENSIONS, ETHICS_IDX, HE1_CODE_DIR, HE1_JSON, HE1_RESULTS_DIR,
    LLAMA2_PAIRS, RHO_THRESHOLD, SAFETY_IDX, SECONDARY_GATE_MIN,
)


def load_he1_data(
    he1_code_dir: str = HE1_CODE_DIR,
    he1_results_dir: str = HE1_RESULTS_DIR,
    he1_json: str = HE1_JSON,
) -> tuple:
    """Load H-E1 scores and rho_partial matrix.

    Returns: (scores_df [16,6], annotated_df [16,8], rho_partial [6,6 ndarray])
    Raw scores NOT in h-e1 JSON — loaded via h-e1 data_loader.
    """
    if he1_code_dir not in sys.path:
        sys.path.insert(0, he1_code_dir)

    from data_loader import load_trustllm_scores, add_annotations

    scores_df = load_trustllm_scores(he1_results_dir)
    annotated_df = add_annotations(scores_df)

    with open(he1_json) as f:
        he1_data = json.load(f)
    # Key is "rho_partial" (list-of-lists), NOT "rho_partial_matrix"
    rho_partial = np.array(he1_data["rho_partial"])

    return scores_df, annotated_df, rho_partial


def extract_llama2_pairs(scores_df: pd.DataFrame) -> list:
    """Extract 3 LLaMA-2 base/chat pairs from scores_df.

    Returns list of 3 dicts: {"scale", "base_scores", "chat_scores"}.
    Raises ValueError if any of the 6 models is missing.
    """
    pairs = []
    for base_name, chat_name, scale in LLAMA2_PAIRS:
        if base_name not in scores_df.index:
            raise ValueError(f"Missing base model '{base_name}' in scores_df")
        if chat_name not in scores_df.index:
            raise ValueError(f"Missing chat model '{chat_name}' in scores_df")
        pairs.append({
            "scale": scale,
            "base_scores": scores_df.loc[base_name].values,
            "chat_scores": scores_df.loc[chat_name].values,
        })
    return pairs


def compute_deltas(pairs: list) -> list:
    """Compute per-dimension deltas (chat - base) for each LLaMA-2 pair.

    Returns list of 3 dicts with delta_safety, delta_ethics, both_positive.
    """
    deltas = []
    for p in pairs:
        all_deltas = p["chat_scores"] - p["base_scores"]
        deltas.append({
            "scale": p["scale"],
            "all_deltas": all_deltas,
            "delta_safety": float(all_deltas[SAFETY_IDX]),
            "delta_ethics": float(all_deltas[ETHICS_IDX]),
            "both_positive": bool(all_deltas[SAFETY_IDX] > 0 and all_deltas[ETHICS_IDX] > 0),
        })
    return deltas


def run_sign_test(deltas: list) -> dict:
    """Binomial sign test: P(X >= n_both | n=3, p=0.5), one-sided greater.

    Uses scipy.stats.binomtest (not deprecated binom_test).
    """
    n_both_positive = sum(d["both_positive"] for d in deltas)
    result = binomtest(n_both_positive, n=3, p=0.5, alternative="greater")
    return {
        "n_both_positive": n_both_positive,
        "secondary_gate_pass": n_both_positive >= SECONDARY_GATE_MIN,
        "binom_pvalue": float(result.pvalue),
    }


def verify_primary_gate(rho_partial: np.ndarray) -> dict:
    """Read rho_partial[SAFETY_IDX][ETHICS_IDX] and compare vs RHO_THRESHOLD."""
    rho_safety_ethics = float(rho_partial[SAFETY_IDX][ETHICS_IDX])
    return {
        "rho_safety_ethics": rho_safety_ethics,
        "primary_gate_pass": abs(rho_safety_ethics) > RHO_THRESHOLD,
    }


def run_analysis(
    he1_code_dir: str = HE1_CODE_DIR,
    he1_results_dir: str = HE1_RESULTS_DIR,
    he1_json: str = HE1_JSON,
) -> dict:
    """Top-level analysis: load → extract → compute → test → gate check."""
    scores_df, annotated_df, rho_partial = load_he1_data(
        he1_code_dir, he1_results_dir, he1_json
    )
    pairs = extract_llama2_pairs(scores_df)
    deltas = compute_deltas(pairs)
    sign_test = run_sign_test(deltas)
    primary = verify_primary_gate(rho_partial)

    return {
        "scores_df": scores_df,
        "annotated_df": annotated_df,
        "rho_partial": rho_partial,
        "pairs": pairs,
        "deltas": deltas,
        "sign_test": sign_test,
        "primary": primary,
        "gate_pass": primary["primary_gate_pass"] and sign_test["secondary_gate_pass"],
    }
