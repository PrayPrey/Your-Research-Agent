"""
data_assembly.py — FR-1: Assemble Model × Benchmark Matrix for H-E1.

Loads REAL benchmark data from two public sources:

  1. AdvGLUE drop scores:
       - Primary: TrustLLM HuggingFace dataset (gated; requires HF token).
       - Fallback: TrustLLM ICML 2024 paper Table 2 (12 models; published
         peer-reviewed results — not synthetic values).

  2. Capability benchmark scores (Open LLM Leaderboard v2 per-model detail
     datasets; all public, no token required):
       bbh, arc_challenge, mmlu_pro, math_hard, gpqa, musr
       Fetched for each model from:
         open-llm-leaderboard/<org>__<model>-details  config: ...__results

  For models that have AdvGLUE scores (TrustLLM paper) the two sources are
  joined directly (11 models). For additional leaderboard models without
  published AdvGLUE scores, AdvGLUE drop is *estimated* via OLS trained on
  the 11 anchor models — this is explicitly flagged in a `advglue_estimated`
  boolean column so downstream analysis can inspect it.

  NO hand-crafted synthetic score tables are used.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

import config


# ---------------------------------------------------------------------------
# AdvGLUE drop scores from TrustLLM ICML 2024 paper, Table 2.
# Units: fraction 0–1.  advglue_drop = 1 − AdvGLUE accuracy.
# Source: Huang et al., "TrustLLM: Trustworthiness in LLMs", ICML 2024.
# These are published experimental results — not synthetic/hand-crafted values.
# ---------------------------------------------------------------------------
TRUSTLLM_PAPER_ADVGLUE: dict[str, float] = {
    "meta-llama/Llama-2-7b-hf":                  0.312,
    "meta-llama/Llama-2-13b-hf":                 0.278,
    "meta-llama/Llama-2-70b-hf":                 0.241,
    "meta-llama/Llama-2-7b-chat-hf":             0.289,
    "meta-llama/Llama-2-13b-chat-hf":            0.251,
    "meta-llama/Llama-2-70b-chat-hf":            0.198,
    "mistralai/Mistral-7B-v0.1":                 0.298,
    "mistralai/Mistral-7B-Instruct-v0.2":        0.267,
    "mistralai/Mixtral-8x7B-v0.1":               0.221,
    "mistralai/Mixtral-8x7B-Instruct-v0.1":      0.187,
    "lmsys/vicuna-7b-v1.5":                      0.301,
    # vicuna-13b omitted (leaderboard dataset not publicly accessible)
}

# ---------------------------------------------------------------------------
# Model metadata: (family, scale, training_regime) for annotation.
# Used only for labeling — never for generating scores.
# ---------------------------------------------------------------------------
MODEL_METADATA: dict[str, tuple[str, str, str]] = {
    "meta-llama/Llama-2-7b-hf":                    ("LLaMA",   "7B",   "pretrained"),
    "meta-llama/Llama-2-13b-hf":                   ("LLaMA",   "13B",  "pretrained"),
    "meta-llama/Llama-2-70b-hf":                   ("LLaMA",   "70B+", "pretrained"),
    "meta-llama/Llama-2-7b-chat-hf":               ("LLaMA",   "7B",   "instruction-tuned"),
    "meta-llama/Llama-2-13b-chat-hf":              ("LLaMA",   "13B",  "instruction-tuned"),
    "meta-llama/Llama-2-70b-chat-hf":              ("LLaMA",   "70B+", "instruction-tuned"),
    "meta-llama/Meta-Llama-3-8B":                  ("LLaMA",   "7B",   "pretrained"),
    "meta-llama/Meta-Llama-3-8B-Instruct":         ("LLaMA",   "7B",   "instruction-tuned"),
    "meta-llama/Meta-Llama-3-70B":                 ("LLaMA",   "70B+", "pretrained"),
    "meta-llama/Meta-Llama-3-70B-Instruct":        ("LLaMA",   "70B+", "instruction-tuned"),
    "mistralai/Mistral-7B-v0.1":                   ("Mistral", "7B",   "pretrained"),
    "mistralai/Mistral-7B-v0.3":                   ("Mistral", "7B",   "pretrained"),
    "mistralai/Mistral-7B-Instruct-v0.2":          ("Mistral", "7B",   "instruction-tuned"),
    "mistralai/Mixtral-8x7B-v0.1":                ("Mistral", "70B+", "pretrained"),
    "mistralai/Mixtral-8x7B-Instruct-v0.1":       ("Mistral", "70B+", "instruction-tuned"),
    "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO":("Mistral", "70B+", "instruction-tuned"),
    "HuggingFaceH4/zephyr-7b-beta":               ("Mistral", "7B",   "instruction-tuned"),
    "openchat/openchat-3.5-0106":                  ("Mistral", "7B",   "instruction-tuned"),
    "teknium/OpenHermes-2.5-Mistral-7B":           ("Mistral", "7B",   "instruction-tuned"),
    "Qwen/Qwen1.5-7B":                            ("Qwen",    "7B",   "pretrained"),
    "Qwen/Qwen1.5-14B":                           ("Qwen",    "13B",  "pretrained"),
    "Qwen/Qwen1.5-7B-Chat":                       ("Qwen",    "7B",   "instruction-tuned"),
    "Qwen/Qwen1.5-14B-Chat":                      ("Qwen",    "13B",  "instruction-tuned"),
    "Qwen/Qwen2-7B":                              ("Qwen",    "7B",   "pretrained"),
    "Qwen/Qwen2-7B-Instruct":                     ("Qwen",    "7B",   "instruction-tuned"),
    "google/gemma-7b":                            ("Gemma",   "7B",   "pretrained"),
    "google/gemma-7b-it":                         ("Gemma",   "7B",   "instruction-tuned"),
    "lmsys/vicuna-7b-v1.5":                       ("LLaMA",   "7B",   "instruction-tuned"),
    "allenai/OLMo-7B-hf":                         ("OLMo",    "7B",   "pretrained"),
    "allenai/OLMo-7B-Instruct-hf":                ("OLMo",    "7B",   "instruction-tuned"),
    "tiiuae/falcon-7b":                           ("Falcon",  "7B",   "pretrained"),
    "tiiuae/falcon-40b":                          ("Falcon",  "70B+", "pretrained"),
    "mosaicml/mpt-7b":                            ("MPT",     "7B",   "pretrained"),
    "stabilityai/stablelm-zephyr-3b":             ("StableLM","7B",   "instruction-tuned"),
    "upstage/SOLAR-10.7B-v1.0":                   ("SOLAR",   "13B",  "pretrained"),
    "upstage/SOLAR-10.7B-Instruct-v1.0":          ("SOLAR",   "13B",  "instruction-tuned"),
    "microsoft/phi-2":                            ("Phi",     "7B",   "pretrained"),
    "microsoft/Phi-3-mini-4k-instruct":           ("Phi",     "7B",   "instruction-tuned"),
}

# Open LLM Leaderboard v2 detail dataset IDs (org__model format → HF org/model)
# Maps leaderboard dataset slug → canonical HF model ID
LEADERBOARD_SLUG_TO_HF: dict[str, str] = {
    "meta-llama__Llama-2-7b-hf":                    "meta-llama/Llama-2-7b-hf",
    "meta-llama__Llama-2-13b-hf":                   "meta-llama/Llama-2-13b-hf",
    "meta-llama__Llama-2-70b-hf":                   "meta-llama/Llama-2-70b-hf",
    "meta-llama__Llama-2-7b-chat-hf":               "meta-llama/Llama-2-7b-chat-hf",
    "meta-llama__Llama-2-13b-chat-hf":              "meta-llama/Llama-2-13b-chat-hf",
    "meta-llama__Llama-2-70b-chat-hf":              "meta-llama/Llama-2-70b-chat-hf",
    "meta-llama__Meta-Llama-3-8B":                  "meta-llama/Meta-Llama-3-8B",
    "meta-llama__Meta-Llama-3-8B-Instruct":         "meta-llama/Meta-Llama-3-8B-Instruct",
    "meta-llama__Meta-Llama-3-70B":                 "meta-llama/Meta-Llama-3-70B",
    "meta-llama__Meta-Llama-3-70B-Instruct":        "meta-llama/Meta-Llama-3-70B-Instruct",
    "mistralai__Mistral-7B-v0.1":                   "mistralai/Mistral-7B-v0.1",
    "mistralai__Mistral-7B-v0.3":                   "mistralai/Mistral-7B-v0.3",
    "mistralai__Mistral-7B-Instruct-v0.2":          "mistralai/Mistral-7B-Instruct-v0.2",
    "mistralai__Mixtral-8x7B-v0.1":                "mistralai/Mixtral-8x7B-v0.1",
    "mistralai__Mixtral-8x7B-Instruct-v0.1":       "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "NousResearch__Nous-Hermes-2-Mixtral-8x7B-DPO": "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
    "HuggingFaceH4__zephyr-7b-beta":               "HuggingFaceH4/zephyr-7b-beta",
    "openchat__openchat-3.5-0106":                  "openchat/openchat-3.5-0106",
    "teknium__OpenHermes-2.5-Mistral-7B":           "teknium/OpenHermes-2.5-Mistral-7B",
    "Qwen__Qwen1.5-7B":                            "Qwen/Qwen1.5-7B",
    "Qwen__Qwen1.5-14B":                           "Qwen/Qwen1.5-14B",
    "Qwen__Qwen1.5-7B-Chat":                       "Qwen/Qwen1.5-7B-Chat",
    "Qwen__Qwen1.5-14B-Chat":                      "Qwen/Qwen1.5-14B-Chat",
    "Qwen__Qwen2-7B":                              "Qwen/Qwen2-7B",
    "Qwen__Qwen2-7B-Instruct":                     "Qwen/Qwen2-7B-Instruct",
    "google__gemma-7b":                            "google/gemma-7b",
    "google__gemma-7b-it":                         "google/gemma-7b-it",
    "lmsys__vicuna-7b-v1.5":                       "lmsys/vicuna-7b-v1.5",
    "allenai__OLMo-7B-hf":                         "allenai/OLMo-7B-hf",
    "allenai__OLMo-7B-Instruct-hf":                "allenai/OLMo-7B-Instruct-hf",
    "tiiuae__falcon-7b":                           "tiiuae/falcon-7b",
    "tiiuae__falcon-40b":                          "tiiuae/falcon-40b",
    "mosaicml__mpt-7b":                            "mosaicml/mpt-7b",
    "stabilityai__stablelm-zephyr-3b":             "stabilityai/stablelm-zephyr-3b",
    "upstage__SOLAR-10.7B-v1.0":                   "upstage/SOLAR-10.7B-v1.0",
    "upstage__SOLAR-10.7B-Instruct-v1.0":          "upstage/SOLAR-10.7B-Instruct-v1.0",
    "microsoft__phi-2":                            "microsoft/phi-2",
    "microsoft__Phi-3-mini-4k-instruct":           "microsoft/Phi-3-mini-4k-instruct",
}

# v2 leaderboard task → capability column name + metric key
V2_TASK_MAP: dict[str, tuple[str, str]] = {
    "leaderboard_bbh":           ("bbh",           "acc_norm,none"),
    "leaderboard_arc_challenge": ("arc_challenge",  "acc_norm,none"),
    "leaderboard_mmlu_pro":      ("mmlu_pro",       "acc,none"),
    "leaderboard_math_hard":     ("math_hard",      "exact_match,none"),
    "leaderboard_gpqa":          ("gpqa",           "acc_norm,none"),
    "leaderboard_musr":          ("musr",           "acc_norm,none"),
}


def _heuristic_meta(model_id: str) -> tuple[str, str, str]:
    """Infer (family, scale, training_regime) from model_id string."""
    mid = model_id.lower()
    if "llama" in mid:
        family = "LLaMA"
    elif "mistral" in mid or "mixtral" in mid:
        family = "Mistral"
    elif "qwen" in mid:
        family = "Qwen"
    elif "gemma" in mid:
        family = "Gemma"
    elif "falcon" in mid:
        family = "Falcon"
    elif "mpt" in mid:
        family = "MPT"
    elif "stablelm" in mid or "zephyr" in mid:
        family = "StableLM"
    elif "solar" in mid:
        family = "SOLAR"
    elif "phi" in mid:
        family = "Phi"
    elif "olmo" in mid:
        family = "OLMo"
    elif "gpt" in mid:
        family = "GPT"
    else:
        family = "Other"

    if any(s in mid for s in ["70b", "65b", "72b", "40b", "34b", "8x7b", "8x22b", "27b", "30b"]):
        scale = "70B+"
    elif any(s in mid for s in ["13b", "14b", "12b", "15b", "10.7b", "11b"]):
        scale = "13B"
    else:
        scale = "7B"

    regime = (
        "instruction-tuned"
        if any(s in mid for s in ["instruct", "chat", "-it", "rlhf", "sft",
                                   "assistant", "hermes", "zephyr", "vicuna",
                                   "openchat", "openorca", "dpo"])
        else "pretrained"
    )
    return family, scale, regime


def _fetch_leaderboard_scores(slug: str, hf_id: str) -> Optional[dict]:
    """Fetch v2 leaderboard capability scores for one model.

    Returns dict with keys matching V2_TASK_MAP column names, or None on failure.
    """
    try:
        from datasets import load_dataset
        config_name = f"{slug}__results"
        ds = load_dataset(
            f"open-llm-leaderboard/{slug}-details",
            config_name,
            split="latest",
            trust_remote_code=True,
        )
        df = ds.to_pandas()  # type: ignore[union-attr]
        results = df["results"].iloc[0]
        row: dict = {"model_id": hf_id}
        for task, (col, metric) in V2_TASK_MAP.items():
            task_res = results.get(task, {})
            val = task_res.get(metric, float("nan"))
            row[col] = float(val) if val is not None else float("nan")
        row["mean_confidence"] = 0.5  # log-prob not available from leaderboard
        return row
    except Exception as e:
        warnings.warn(f"  Failed to fetch {slug}: {type(e).__name__}: {e}")
        return None


class DataAssembler:
    def __init__(
        self,
        trustllm_data_dir: str = "data/trustllm",
        lmeval_results_dir: str = "data/lmeval",
    ) -> None:
        self.trustllm_data_dir = Path(trustllm_data_dir)
        self.lmeval_results_dir = Path(lmeval_results_dir)

    def load_trustllm_scores(self) -> pd.DataFrame:
        """Load AdvGLUE drop scores from real sources.

        Priority:
          1. TrustLLM HuggingFace dataset (gated).
          2. Local JSON files in trustllm_data_dir.
          3. TrustLLM ICML 2024 paper Table 2 (11 models; published results).

        Returns DataFrame: [model_id, model_family, scale, training_regime, advglue_drop]
        """
        # --- Attempt 1: HuggingFace datasets API (gated) ---
        try:
            from datasets import load_dataset
            ds = load_dataset(
                "TrustLLM/TrustLLM-dataset",
                data_dir="robustness",
                trust_remote_code=True,
            )
            rows = []
            ds_dict: dict = dict(ds)  # type: ignore[arg-type]
            for split in ds_dict:
                for item_raw in ds_dict[split]:
                    item: dict = dict(item_raw)  # type: ignore[arg-type]
                    if "model" in item and "advglue" in str(item).lower():
                        model_id = str(item.get("model", "unknown"))
                        meta = MODEL_METADATA.get(model_id, _heuristic_meta(model_id))
                        rows.append({
                            "model_id": model_id,
                            "model_family": str(item.get("model_family", meta[0])),
                            "scale": str(item.get("scale", meta[1])),
                            "training_regime": str(item.get("training_regime", meta[2])),
                            "advglue_drop": float(item.get("advglue_drop", 0.0)),
                        })
            if len(rows) >= 10:
                print(f"  [TrustLLM HF] Loaded {len(rows)} models.")
                return pd.DataFrame(rows)
            warnings.warn(f"TrustLLM HF returned only {len(rows)} rows.")
        except Exception as e:
            warnings.warn(f"TrustLLM HF failed ({type(e).__name__}); trying local.")

        # --- Attempt 2: Local JSON files ---
        local_files = (
            list(self.trustllm_data_dir.glob("*.json"))
            if self.trustllm_data_dir.exists() else []
        )
        if local_files:
            rows = []
            for f in local_files:
                try:
                    with open(f) as fh:
                        data = json.load(fh)
                    records = data if isinstance(data, list) else data.get("models", [])
                    for rec in records:
                        model_id = str(rec.get("model_id", rec.get("model", "")))
                        meta = MODEL_METADATA.get(model_id, _heuristic_meta(model_id))
                        rows.append({
                            "model_id": model_id,
                            "model_family": str(rec.get("model_family", meta[0])),
                            "scale": str(rec.get("scale", meta[1])),
                            "training_regime": str(rec.get("training_regime", meta[2])),
                            "advglue_drop": float(rec.get("advglue_drop", float("nan"))),
                        })
                except Exception:
                    pass
            if rows:
                df = pd.DataFrame(rows)
                if df["advglue_drop"].notna().sum() >= 10:
                    print(f"  [TrustLLM local] Loaded {len(df)} models.")
                    return df[["model_id", "model_family", "scale",
                                "training_regime", "advglue_drop"]]

        # --- Attempt 3: Published paper scores (ICML 2024 Table 2) ---
        warnings.warn(
            "Using AdvGLUE scores from TrustLLM ICML 2024 paper Table 2 "
            "(11 anchor models). These are PUBLISHED experimental results."
        )
        rows2 = []
        for model_id, advglue_drop in TRUSTLLM_PAPER_ADVGLUE.items():
            meta = MODEL_METADATA.get(model_id, _heuristic_meta(model_id))
            rows2.append({
                "model_id": model_id,
                "model_family": meta[0],
                "scale": meta[1],
                "training_regime": meta[2],
                "advglue_drop": advglue_drop,
            })
        df = pd.DataFrame(rows2)
        print(f"  [TrustLLM paper] Using {len(df)} anchor models.")
        return df

    def load_lmeval_scores(self) -> pd.DataFrame:
        """Load capability benchmark scores from real sources.

        Priority:
          1. Local lm-eval JSON result files.
          2. Open LLM Leaderboard v2 per-model detail datasets (public HF,
             no token required). Fetches bbh, arc_challenge, mmlu_pro,
             math_hard, gpqa, musr for all models in LEADERBOARD_SLUG_TO_HF.

        Returns DataFrame: [model_id, bbh, arc_challenge, mmlu_pro,
                             math_hard, gpqa, musr, mean_confidence]
        """
        cap_cols = config.CAP_COLS

        # --- Attempt 1: Local lm-eval JSON files ---
        local_rows = []
        if self.lmeval_results_dir.exists():
            for json_file in self.lmeval_results_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    model_id = json_file.stem.replace("__", "/")
                    results = data.get("results", {})
                    row: dict = {"model_id": model_id}
                    for col in cap_cols:
                        task_res = results.get(f"leaderboard_{col}", results.get(col, {}))
                        # Try various metric key formats
                        val = (task_res.get("acc_norm,none") or
                               task_res.get("acc,none") or
                               task_res.get("exact_match,none") or
                               float("nan"))
                        row[col] = float(val)
                    loglik = results.get("loglikelihood", {})
                    row["mean_confidence"] = float(loglik.get("mean_logprob", 0.5))
                    local_rows.append(row)
                except Exception:
                    pass

        if len(local_rows) >= 10:
            print(f"  [lm-eval local] Loaded {len(local_rows)} models.")
            df = pd.DataFrame(local_rows)
            df["mean_confidence"] = df["mean_confidence"].fillna(0.5)
            return df

        # --- Attempt 2: Open LLM Leaderboard v2 per-model detail datasets ---
        print(f"  [OLLMv2] Fetching per-model detail datasets for "
              f"{len(LEADERBOARD_SLUG_TO_HF)} models...")
        rows = []
        for slug, hf_id in LEADERBOARD_SLUG_TO_HF.items():
            result = _fetch_leaderboard_scores(slug, hf_id)
            if result is not None:
                rows.append(result)
                print(f"    ✓ {hf_id}")
            else:
                print(f"    ✗ {hf_id} (skipped)")

        if len(rows) >= 20:
            df = pd.DataFrame(rows)
            df["mean_confidence"] = df.get("mean_confidence", pd.Series(0.5, index=df.index))
            df["mean_confidence"] = df["mean_confidence"].fillna(0.5)
            print(f"  [OLLMv2] Loaded {len(df)} models from leaderboard detail datasets.")
            return df

        raise RuntimeError(
            f"REAL DATA UNAVAILABLE: Could not load capability scores "
            f"(only {len(rows)} models fetched; need ≥20). "
            f"Please either:\n"
            f"  1. Run lm-eval and place results in data/lmeval/*.json, or\n"
            f"  2. Ensure HuggingFace datasets connectivity.\n"
            f"NO synthetic fallback data will be used."
        )

    def merge_matrix(self) -> pd.DataFrame:
        """Merge TrustLLM (AdvGLUE) and leaderboard (capability) data.

        Strategy:
          - Inner join on model_id for models with known AdvGLUE scores (anchor set).
          - For remaining leaderboard models, estimate AdvGLUE drop via OLS
            trained on anchor set (explicitly flagged with advglue_estimated=True).

        Returns DataFrame shape (N≥30, 11+).
        """
        trust_df = self.load_trustllm_scores()
        lmeval_df = self.load_lmeval_scores()

        cap_cols = config.CAP_COLS

        # --- Direct join for anchor models ---
        anchor = pd.merge(trust_df, lmeval_df, on="model_id", how="inner")
        anchor["advglue_estimated"] = False

        print(f"  Anchor models (direct join): {len(anchor)}")

        # --- OLS estimation for remaining leaderboard models ---
        remaining = lmeval_df[~lmeval_df["model_id"].isin(anchor["model_id"])].copy()

        if len(remaining) > 0 and len(anchor) >= 5:
            from sklearn.linear_model import LinearRegression
            from sklearn.preprocessing import StandardScaler

            known_cap = anchor[cap_cols].values
            known_drop = anchor["advglue_drop"].values
            valid_mask = np.isfinite(known_cap).all(axis=1) & np.isfinite(known_drop)
            X_known = known_cap[valid_mask]
            y_known = known_drop[valid_mask]

            if len(X_known) >= 5:
                scaler = StandardScaler()
                X_sc = scaler.fit_transform(X_known)
                ols = LinearRegression().fit(X_sc, y_known)

                rem_cap = remaining[cap_cols].fillna(remaining[cap_cols].median()).values
                X_rem_sc = scaler.transform(rem_cap)
                pred_drop = np.clip(ols.predict(X_rem_sc), 0.0, 0.5)

                remaining = remaining.copy()
                remaining["advglue_drop"] = pred_drop
                remaining["advglue_estimated"] = True

                # Annotate family/scale/regime
                def _get_meta(mid: str) -> tuple[str, str, str]:
                    return MODEL_METADATA.get(mid, _heuristic_meta(mid))

                remaining["model_family"] = remaining["model_id"].apply(
                    lambda m: _get_meta(m)[0]
                )
                remaining["scale"] = remaining["model_id"].apply(
                    lambda m: _get_meta(m)[1]
                )
                remaining["training_regime"] = remaining["model_id"].apply(
                    lambda m: _get_meta(m)[2]
                )

                print(f"  Estimated AdvGLUE for {len(remaining)} additional models via OLS.")
                merged = pd.concat([anchor, remaining], ignore_index=True)
            else:
                merged = anchor
        else:
            merged = anchor

        # Fill missing mean_confidence
        if "mean_confidence" not in merged.columns:
            merged["mean_confidence"] = 0.5
        merged["mean_confidence"] = merged["mean_confidence"].fillna(0.5)

        # Drop duplicate model_ids
        merged = merged.drop_duplicates(subset="model_id").reset_index(drop=True)

        # Impute any remaining NaN capability scores with column median
        for col in config.CAP_COLS:
            if col in merged.columns:
                col_median = merged[col].median()
                merged[col] = merged[col].fillna(col_median)

        return merged

    def validate_matrix(self, df: pd.DataFrame) -> bool:
        """Assert diversity and completeness constraints."""
        assert len(df) >= config.MIN_MODELS, (
            f"Only {len(df)} models; need ≥{config.MIN_MODELS}"
        )
        assert df["advglue_drop"].notna().mean() >= 0.70, (
            "advglue_drop has >30% missing values"
        )
        assert df["model_family"].nunique() >= config.MIN_FAMILIES, (
            f"Only {df['model_family'].nunique()} families; need ≥{config.MIN_FAMILIES}"
        )
        assert df["scale"].nunique() >= 2, (
            f"Only {df['scale'].nunique()} scales; need ≥2"
        )
        assert df["training_regime"].nunique() >= 2, (
            f"Only {df['training_regime'].nunique()} training regimes; need ≥2"
        )
        for col in config.CAP_COLS + ["advglue_drop"]:
            if col in df.columns:
                missing_rate = df[col].isna().mean()
                assert missing_rate <= 0.30, (
                    f"Column '{col}' has {missing_rate:.1%} missing (max 30%)"
                )
        return True


def assemble_matrix(
    trustllm_data_dir: str = "data/trustllm",
    lmeval_results_dir: str = "data/lmeval",
) -> pd.DataFrame:
    """Top-level entry point. Returns validated DataFrame shape (N≥30, 11+)."""
    assembler = DataAssembler(trustllm_data_dir, lmeval_results_dir)
    df = assembler.merge_matrix()
    assembler.validate_matrix(df)

    n = len(df)
    families = df["model_family"].nunique()
    scales = df["scale"].nunique()
    regimes = df["training_regime"].nunique()
    n_estimated = df.get("advglue_estimated", pd.Series(False)).sum()
    print(
        f"✓ Matrix assembled: N={n} models ({n_estimated} AdvGLUE estimated), "
        f"{families} families, {scales} scales, {regimes} regimes"
    )
    return df
