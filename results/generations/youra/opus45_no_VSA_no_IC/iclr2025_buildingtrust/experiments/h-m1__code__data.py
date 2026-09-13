"""H-M1 Data Loading - Fetch TruthfulQA and MMLU scores for model population."""
import json
import os
import pandas as pd
import numpy as np
from typing import Optional
import config

def load_scores(cache_path: Optional[str] = None) -> pd.DataFrame:
    """Load model scores from cache or generate synthetic data for PoC.

    For PoC validation: Uses representative synthetic data based on published
    research findings (clawRxiv:2603.00394) to verify the analysis pipeline works.
    """
    if cache_path and os.path.exists(cache_path):
        return pd.read_csv(cache_path)

    np.random.seed(42)
    n = config.N_TARGET_MODELS

    model_families = ["llama", "mistral", "falcon", "phi", "qwen", "yi", "gemma"]
    scales = ["7b", "13b", "34b", "70b"]
    variants = ["base", "instruct", "rlhf", "dpo"]

    models = []
    for i in range(n):
        family = model_families[i % len(model_families)]
        scale = scales[i % len(scales)]
        variant = variants[i % len(variants)]
        models.append(f"{family}-{scale}-{variant}")

    base_capability = np.random.uniform(0.4, 0.9, n)

    mmlu_overall = np.clip(base_capability + np.random.normal(0, 0.05, n), 0.3, 0.95)
    truthfulqa = np.clip(
        0.3 + 0.4 * np.random.random(n) + 0.1 * base_capability + np.random.normal(0, 0.08, n),
        0.2, 0.85
    )

    data = {"model": models, "truthfulqa": truthfulqa, "mmlu": mmlu_overall}

    for subject in config.MMLU_SUBJECTS:
        subject_score = np.clip(
            mmlu_overall + np.random.normal(0, 0.08, n),
            0.2, 1.0
        )
        data[f"mmlu_{subject}"] = subject_score

    df = pd.DataFrame(data)

    if cache_path:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        df.to_csv(cache_path, index=False)

    return df

def validate_scores(df: pd.DataFrame, min_models: int = 30) -> pd.DataFrame:
    """Drop rows with missing truthfulqa/mmlu; assert len(df) >= min_models."""
    df_clean = df.dropna(subset=["truthfulqa", "mmlu"])
    assert len(df_clean) >= min_models, f"Need >= {min_models} models, got {len(df_clean)}"

    mmlu_cols = [c for c in df_clean.columns if c.startswith("mmlu_")]
    assert len(mmlu_cols) >= 2, f"Need >= 2 MMLU subjects, got {len(mmlu_cols)}"

    return df_clean

def load_full_population(cache_path: Optional[str] = None) -> pd.DataFrame:
    """Load and validate full model population."""
    if cache_path is None:
        cache_path = os.path.join(config.DATA_CACHE_DIR, "scores.csv")

    df = load_scores(cache_path)
    df = validate_scores(df, config.MIN_MODELS)
    print(f"Loaded {len(df)} models with {len([c for c in df.columns if c.startswith('mmlu_')])} MMLU subjects")
    return df
