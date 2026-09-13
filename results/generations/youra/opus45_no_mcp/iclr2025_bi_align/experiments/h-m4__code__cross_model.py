"""Cross-model consistency for H-M4."""


def per_model_consistency(records: list, models: list) -> dict:
    """Report cross-model info (aggregate-only, no per-model cluster data in H-E1)."""
    return {
        "note": "aggregate-only: per-model cluster labels unavailable in H-E1 results",
        "models_evaluated": models
    }
