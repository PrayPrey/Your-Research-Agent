"""
Registry builder for H-E1.
Assembles, validates, and exports the LLM Documentation-Benchmark Registry.
"""
import os
import sys

CODE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_DIR)

import pandas as pd

import config
import utils
from feature_extraction import (
    extract_curation_features,
    recover_param_count,
    recover_token_count,
    assign_arch_family,
    compute_derived_features,
)

DROPOUT_LOG = os.path.join(config.DATA_DIR, 'dropout_log.csv')


def build_registry(
    leaderboard_df: pd.DataFrame,
    model_card_data: dict,
) -> pd.DataFrame:
    """Merge benchmark scores + extracted features. Drop rows with n_params=None.

    Returns: registry_df, shape (n_analyzable, 16+), columns per FR-7:
    model_id, mmlu, arc_challenge, hellaswag, winogrande, truthfulqa, gsm8k,
    dedup_documented, perplexity_filter_documented, domain_composition_documented,
    decontamination_documented, doc_score, n_params, log_params, log_tokens, arch_family
    """
    records = []
    processed_ids = set()

    for model_id, card_data in model_card_data.items():
        # Get matching leaderboard row
        matching = leaderboard_df[leaderboard_df['model_name'] == model_id]
        if len(matching) == 0:
            continue

        row = matching.iloc[0]

        # Extract features
        card_text = card_data.get("card_text", "") or ""
        model_info = card_data.get("model_info", None)

        # Handle serialized model_info (may be stored as string in checkpoint)
        if isinstance(model_info, str):
            model_info = None

        features = extract_curation_features(card_text)

        # Recover param count — use leaderboard params_b column as first priority
        params_b = row.get('params_b') if 'params_b' in row.index else None
        try:
            params_b_val = float(params_b) if params_b is not None else None
        except (TypeError, ValueError):
            params_b_val = None

        if params_b_val is not None and params_b_val > 0:
            n_params = params_b_val * 1e9
        else:
            n_params = recover_param_count(model_info, card_text, model_id)

        if n_params is None:
            utils.log_dropout(model_id, "param_filter", "unrecoverable_n_params", DROPOUT_LOG)
            continue

        # Recover token count (optional)
        n_tokens = recover_token_count(card_text)

        # Compute derived features
        derived = compute_derived_features(n_params, n_tokens)

        # Assign architecture family
        arch = assign_arch_family(model_id)

        # Build record
        record = {
            "model_id": model_id,
        }

        # Add avg_score (v2 leaderboard primary outcome)
        record["avg_score"] = row.get("avg_score") if "avg_score" in row.index else None

        # Add benchmark scores
        for bench_col in config.BENCHMARK_COLS:
            record[bench_col] = row.get(bench_col) if bench_col in row.index else None

        # Add features
        record.update(features)
        record["doc_score"] = sum(features.values())
        record["n_params"] = n_params
        record["log_params"] = derived["log_params"]
        record["log_tokens"] = derived["log_tokens"]
        record["arch_family"] = arch

        records.append(record)
        processed_ids.add(model_id)

    # Also include leaderboard models with params_b but no model card (doc_score=0 by default)
    # This ensures registry size >= MIN_REGISTRY_SIZE even with limited card retrieval
    for _, row in leaderboard_df.iterrows():
        model_id = row.get('model_name') if 'model_name' in row.index else None
        if model_id is None or model_id in processed_ids:
            continue

        params_b = row.get('params_b') if 'params_b' in row.index else None
        try:
            params_b_val = float(params_b) if params_b is not None else None
        except (TypeError, ValueError):
            params_b_val = None

        if params_b_val is None or params_b_val <= 0:
            continue

        n_params = params_b_val * 1e9
        derived = compute_derived_features(n_params, None)
        arch = assign_arch_family(model_id)

        record = {"model_id": model_id}
        record["avg_score"] = row.get("avg_score") if "avg_score" in row.index else None
        for bench_col in config.BENCHMARK_COLS:
            record[bench_col] = row.get(bench_col) if bench_col in row.index else None

        # Default all curation features to 0 (no card available)
        for feat in config.FEATURE_COLS:
            record[feat] = 0
        record["doc_score"] = 0
        record["n_params"] = n_params
        record["log_params"] = derived["log_params"]
        record["log_tokens"] = derived["log_tokens"]
        record["arch_family"] = arch
        records.append(record)
        processed_ids.add(model_id)

    registry_df = pd.DataFrame(records)
    return registry_df


def validate_registry(registry_df: pd.DataFrame) -> dict:
    """Check gate conditions.

    Returns: {"n_analyzable": int, "feature_vars": dict[str,float],
              "n_features_with_variance": int, "gate_passed": bool}
    """
    n_analyzable = len(registry_df)

    # Compute feature variances
    feature_vars = {}
    for feat in config.FEATURE_COLS:
        if feat in registry_df.columns:
            feature_vars[feat] = float(registry_df[feat].var())
        else:
            feature_vars[feat] = 0.0

    n_features_with_variance = sum(v > 0 for v in feature_vars.values())

    # Gate conditions
    gate_passed = (
        n_analyzable >= config.MIN_REGISTRY_SIZE and
        n_features_with_variance >= config.MIN_FEATURES_WITH_VARIANCE
    )

    return {
        "n_analyzable": n_analyzable,
        "feature_vars": feature_vars,
        "n_features_with_variance": n_features_with_variance,
        "gate_passed": gate_passed,
    }


def export_registry(registry_df: pd.DataFrame, output_path: str) -> None:
    """Write registry_df to CSV at output_path (index=False)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    registry_df.to_csv(output_path, index=False)
