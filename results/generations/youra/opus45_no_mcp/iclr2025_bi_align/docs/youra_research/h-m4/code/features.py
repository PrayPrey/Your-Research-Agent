"""Bidirectional feature scoring for H-M4."""

from config import H_M4_Config

cfg = H_M4_Config()


def score_bidirectional_features(task_text: str) -> dict:
    """Score task on 3 bidirectional features. Returns dict with scores 0-3."""
    t = task_text.lower()
    features = {
        "user_belief_reference": int(any(m in t for m in cfg.belief_markers)),
        "context_dependent": int(any(m in t for m in cfg.context_markers)),
        "hedged_answer": int(any(m in t for m in cfg.hedge_markers)),
    }
    features["total"] = sum([
        features["user_belief_reference"],
        features["context_dependent"],
        features["hedged_answer"]
    ])
    return features


def score_all(records: list) -> list:
    """Add bidirectional feature scores to each record."""
    for r in records:
        features = score_bidirectional_features(r["question"])
        r.update(features)
        r["bidirectional_score"] = features["total"]
    return records
