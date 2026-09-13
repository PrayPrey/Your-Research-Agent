import numpy as np
import pandas as pd


def compute_formality_delta(human_formality: float, ai_formality: float) -> float:
    return abs(human_formality - ai_formality)


def label_continuation(turn_pairs: list[dict]) -> np.ndarray:
    return np.array([1 if p["has_next_turn"] else 0 for p in turn_pairs])


def build_analysis_frame(
    turn_pairs: list[dict],
    human_scores: list[float],
    ai_scores: list[float]
) -> pd.DataFrame:
    data = []
    for i, pair in enumerate(turn_pairs):
        delta = compute_formality_delta(human_scores[i], ai_scores[i])
        continuation = 1 if pair["has_next_turn"] else 0
        data.append({
            "conversation_id": pair["conversation_id"],
            "turn_idx": pair["turn_idx"],
            "human_formality": human_scores[i],
            "ai_formality": ai_scores[i],
            "delta": delta,
            "continuation": continuation
        })
    return pd.DataFrame(data)
