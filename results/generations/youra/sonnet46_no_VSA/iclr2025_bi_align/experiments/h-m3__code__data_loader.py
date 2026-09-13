import json
import os
import numpy as np
import pandas as pd
from rapidfuzz import fuzz, process

from config import ExperimentConfig


def load_h_m2_results(cfg: ExperimentConfig) -> dict:
    """Load and validate h_m2_results.json."""
    path = os.path.join(os.path.dirname(__file__), cfg.h_m2_results_path)
    path = os.path.normpath(path)
    if not os.path.exists(path):
        raise RuntimeError(f"H-M2 results not found: {path}. H-M2 must complete before H-M3.")
    with open(path) as f:
        data = json.load(f)
    required = ["partial_rho", "ci_partial", "raw_rho", "ci_raw", "N"]
    missing = [k for k in required if k not in data]
    if missing:
        raise RuntimeError(f"H-M2 results malformed — missing keys: {missing}")
    ci = data["ci_partial"]
    if not (isinstance(ci, (list, tuple)) and len(ci) == 2 and ci[0] < ci[1]):
        raise RuntimeError(f"H-M2 ci_partial malformed: {ci}")
    return data


def load_harmbench_data() -> dict:
    """Hardcoded HarmBench Table 2 from arXiv:2402.04249 (33 models, attack success rate)."""
    return {
        "gpt-3.5-turbo-1106": 0.826,
        "gpt-4-0613": 0.222,
        "claude-2": 0.020,
        "claude-instant-1": 0.388,
        "llama-2-7b-chat-hf": 0.020,
        "llama-2-13b-chat-hf": 0.020,
        "llama-2-70b-chat-hf": 0.020,
        "vicuna-7b-v1.5": 0.980,
        "vicuna-13b-v1.5": 0.960,
        "baichuan-2-7b-chat": 0.020,
        "baichuan-2-13b-chat": 0.020,
        "qwen-7b-chat": 0.694,
        "qwen-14b-chat": 0.510,
        "mistral-7b-instruct-v0.1": 0.694,
        "mistral-7b-instruct-v0.2": 0.592,
        "mixtral-8x7b-instruct-v0.1": 0.592,
        "openchat-3.5-1210": 0.918,
        "starling-lm-7b-alpha": 0.918,
        "zephyr-7b-beta": 0.959,
        "tulu-2-dpo-7b": 0.918,
        "tulu-2-dpo-13b": 0.776,
        "tulu-2-dpo-70b": 0.673,
        "openhermes-2.5-mistral-7b": 0.918,
        "llama-2-7b-hf": 0.980,
        "llama-2-13b-hf": 0.918,
        "llama-2-70b-hf": 0.939,
        "falcon-7b-instruct": 0.980,
        "mpt-7b-chat": 0.898,
        "dolphin-2.2.1-mistral-7b": 0.980,
        "nous-hermes-2-yi-34b": 0.939,
        "solar-10.7b-instruct-v1.0": 0.837,
        "gemma-7b-it": 0.490,
        "gemma-2b-it": 0.551,
    }


def load_tier1_dataframe(cfg: ExperimentConfig) -> pd.DataFrame:
    """Load and join LLM CSV with BBQ scores for Tier 2 DataFrame (replicates H-M2 load_data)."""
    llm_path = os.path.join(os.path.dirname(__file__), cfg.h_m1_pairs_csv)
    llm_path = os.path.normpath(llm_path)
    if not os.path.exists(llm_path):
        raise RuntimeError(f"LLM CSV not found: {llm_path}")
    df_llm = pd.read_csv(llm_path)  # cols: model_name, TruthfulQA_MC2, MMLU

    # Load BBQ scores
    bbq_path = os.path.join(os.path.dirname(__file__), cfg.bbq_csv)
    bbq_path = os.path.normpath(bbq_path)
    if not os.path.exists(bbq_path):
        raise RuntimeError(f"BBQ CSV not found: {bbq_path}")
    df_bbq = pd.read_csv(bbq_path)  # cols: model_name, bbq_accuracy

    # Inner join on model_name
    df = df_llm.merge(df_bbq, on="model_name", how="inner")
    df = df.dropna(subset=["TruthfulQA_MC2", "bbq_accuracy", "MMLU"])

    # Normalize bbq_accuracy to [0,1] if percentage
    if df["bbq_accuracy"].median() > 1.5:
        df["bbq_accuracy"] = df["bbq_accuracy"] / 100.0

    return df


def load_tier3_delta_bbq(cfg: ExperimentConfig) -> np.ndarray:
    """Load BBQ scores and compute ΔBBQ as deviations from median (proxy for base/chat pairs)."""
    bbq_path = os.path.join(os.path.dirname(__file__), cfg.bbq_csv)
    bbq_path = os.path.normpath(bbq_path)
    if not os.path.exists(bbq_path):
        raise RuntimeError(f"BBQ CSV not found: {bbq_path}")
    df = pd.read_csv(bbq_path)

    bbq = pd.to_numeric(df["bbq_accuracy"], errors="coerce").dropna().values
    if bbq.max() > 1.5:
        bbq = bbq / 100.0

    # ΔBBQ as deviations from median (approximation for available data)
    delta = bbq - np.median(bbq)
    return delta


def fuzzy_join(df: pd.DataFrame, harmbench_df: pd.DataFrame,
               threshold: int = 75) -> pd.DataFrame:
    """Inner join df with harmbench_df on model_name using rapidfuzz."""
    if "model_name" not in df.columns or "model_name" not in harmbench_df.columns:
        raise RuntimeError("Both DataFrames must have 'model_name' column")

    harm_names = harmbench_df["model_name"].tolist()
    matched_rows = []
    for _, row in df.iterrows():
        result = process.extractOne(
            row["model_name"], harm_names,
            scorer=fuzz.token_sort_ratio
        )
        if result is not None and result[1] >= threshold:
            matched_name = result[0]
            harm_row = harmbench_df[harmbench_df["model_name"] == matched_name].iloc[0]
            new_row = row.to_dict()
            new_row["harm_rate"] = harm_row["harm_rate"]
            matched_rows.append(new_row)

    if not matched_rows:
        return pd.DataFrame()
    return pd.DataFrame(matched_rows).reset_index(drop=True)
