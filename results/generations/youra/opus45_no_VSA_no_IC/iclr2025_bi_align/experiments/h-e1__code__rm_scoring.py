"""Reward model scoring with multi-model support."""

import os
import numpy as np
import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from config import CONFIG


class RewardModel:
    """Unified reward model interface for classifier/pairwise/moe types."""

    def __init__(self, model_id: str, model_type: str, device: str = "cuda"):
        self.model_id = model_id
        self.model_type = model_type
        self.device = device

        if model_type == "classifier":
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_id)
            self.model.to(device).eval()

        elif model_type == "pairwise":
            from llm_blender import Blender
            self.blender = Blender()
            self.blender.loadranker("llm-blender/PairRM")

        elif model_type == "moe":
            self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_id, trust_remote_code=True, torch_dtype=torch.bfloat16
            )
            self.model.to(device).eval()

    @torch.no_grad()
    def score(self, prompt: str, response: str) -> float:
        """Return scalar reward score."""
        if self.model_type == "classifier":
            text = prompt + " " + response
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            logits = self.model(**inputs).logits
            return logits[0, 0].item()

        elif self.model_type == "pairwise":
            ranks = self.blender.rank([prompt], [[response, ""]])
            return 1.0 if ranks[0][0] < ranks[0][1] else 0.0

        elif self.model_type == "moe":
            messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": response}]
            text = self.tokenizer.apply_chat_template(messages, tokenize=False)
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=4096)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            output = self.model(**inputs)
            return output.score.item()


def zscore_sigmoid(scores: np.ndarray) -> np.ndarray:
    """Normalize via z-score then sigmoid to [0,1]."""
    mean, std = scores.mean(), scores.std()
    if std < 1e-8:
        return np.full_like(scores, 0.5)
    z = (scores - mean) / std
    return 1 / (1 + np.exp(-z))


def score_all_battles(df: pd.DataFrame, models: dict) -> pd.DataFrame:
    """Score all battles with all models. Supports resume from cache."""
    cache_path = CONFIG["scores_cache_path"]

    cached = load_cached_scores(cache_path)
    if cached is not None and "battle_id" in df.columns and "battle_id" in cached.columns:
        df = df.merge(cached, on="battle_id", how="left", suffixes=("", "_cached"))
        for col in cached.columns:
            if col != "battle_id" and col in df.columns:
                df[col] = df[col].fillna(df.get(f"{col}_cached"))
        df = df[[c for c in df.columns if not c.endswith("_cached")]]

    if "battle_id" not in df.columns:
        df["battle_id"] = range(len(df))

    for name, rm in models.items():
        col_a = f"{name}_score_a"
        col_b = f"{name}_score_b"

        if col_a not in df.columns:
            df[col_a] = np.nan
            df[col_b] = np.nan

        to_score = df[df[col_a].isna()].index.tolist()
        if not to_score:
            print(f"  {name}: all scored (cached)")
            continue

        print(f"  Scoring {name}: {len(to_score)} battles")
        batch_size = CONFIG["batch_size"]

        for i in tqdm(range(0, len(to_score), batch_size), desc=name):
            batch_idx = to_score[i : i + batch_size]
            for idx in batch_idx:
                row = df.loc[idx]
                try:
                    df.loc[idx, col_a] = rm.score(row["prompt"], row["resp_a"])
                    df.loc[idx, col_b] = rm.score(row["prompt"], row["resp_b"])
                except Exception as e:
                    print(f"    Error scoring row {idx}: {e}")
                    df.loc[idx, col_a] = 0.0
                    df.loc[idx, col_b] = 0.0

            if i % (batch_size * 10) == 0:
                cache_scores(df, cache_path)

        cache_scores(df, cache_path)

    return df


def cache_scores(df: pd.DataFrame, path: str) -> None:
    """Save scores to parquet."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    score_cols = ["battle_id"] + [c for c in df.columns if "_score_" in c]
    df[score_cols].to_parquet(path, index=False)


def load_cached_scores(path: str):
    """Load cached scores from parquet."""
    if os.path.exists(path):
        return pd.read_parquet(path)
    return None


def compute_rm_variance(row: dict, model_names: list) -> float:
    """Compute variance of normalized RM preference signals."""
    prefs = []
    for name in model_names:
        norm_a = row.get(f"{name}_norm_a", 0.5)
        norm_b = row.get(f"{name}_norm_b", 0.5)
        prefs.append(norm_a - norm_b)
    return np.var(prefs)
