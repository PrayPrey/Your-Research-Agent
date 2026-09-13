"""compute_real_ece.py — Compute real ECE from Open LLM Leaderboard v2 details.

Extracts per-sample (max-choice confidence, correctness) from arc_challenge
leaderboard details, then computes ECE via uncertainty-calibration.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import calibration as cal
from datasets import load_dataset

# Map model_id -> leaderboard dataset repo name
MODEL_TO_REPO = {
    "meta-llama/Llama-2-7b-hf": "open-llm-leaderboard/meta-llama__Llama-2-7b-hf-details",
    "meta-llama/Llama-2-13b-hf": "open-llm-leaderboard/meta-llama__Llama-2-13b-hf-details",
    "meta-llama/Llama-2-70b-hf": "open-llm-leaderboard/meta-llama__Llama-2-70b-hf-details",
    "meta-llama/Llama-2-13b-chat-hf": "open-llm-leaderboard/meta-llama__Llama-2-13b-chat-hf-details",
    "meta-llama/Llama-2-70b-chat-hf": "open-llm-leaderboard/meta-llama__Llama-2-70b-chat-hf-details",
    "mistralai/Mistral-7B-v0.1": "open-llm-leaderboard/mistralai__Mistral-7B-v0.1-details",
    "mistralai/Mistral-7B-Instruct-v0.2": "open-llm-leaderboard/mistralai__Mistral-7B-Instruct-v0.2-details",
    "lmsys/vicuna-7b-v1.5": "open-llm-leaderboard/lmsys__vicuna-7b-v1.5-details",
    "meta-llama/Meta-Llama-3-8B": "open-llm-leaderboard/meta-llama__Meta-Llama-3-8B-details",
    "meta-llama/Meta-Llama-3-70B": "open-llm-leaderboard/meta-llama__Meta-Llama-3-70B-details",
    "meta-llama/Meta-Llama-3-70B-Instruct": "open-llm-leaderboard/meta-llama__Meta-Llama-3-70B-Instruct-details",
    "mistralai/Mistral-7B-v0.3": "open-llm-leaderboard/mistralai__Mistral-7B-v0.3-details",
    "HuggingFaceH4/zephyr-7b-beta": "open-llm-leaderboard/HuggingFaceH4__zephyr-7b-beta-details",
    "openchat/openchat-3.5-0106": "open-llm-leaderboard/openchat__openchat-3.5-0106-details",
    "teknium/OpenHermes-2.5-Mistral-7B": "open-llm-leaderboard/teknium__OpenHermes-2.5-Mistral-7B-details",
    "Qwen/Qwen1.5-7B": "open-llm-leaderboard/Qwen__Qwen1.5-7B-details",
    "Qwen/Qwen1.5-14B": "open-llm-leaderboard/Qwen__Qwen1.5-14B-details",
    "Qwen/Qwen1.5-7B-Chat": "open-llm-leaderboard/Qwen__Qwen1.5-7B-Chat-details",
    "Qwen/Qwen1.5-14B-Chat": "open-llm-leaderboard/Qwen__Qwen1.5-14B-Chat-details",
    "Qwen/Qwen2-7B": "open-llm-leaderboard/Qwen__Qwen2-7B-details",
    "Qwen/Qwen2-7B-Instruct": "open-llm-leaderboard/Qwen__Qwen2-7B-Instruct-details",
    "google/gemma-7b": "open-llm-leaderboard/google__gemma-7b-details",
    "google/gemma-7b-it": "open-llm-leaderboard/google__gemma-7b-it-details",
    "tiiuae/falcon-7b": "open-llm-leaderboard/tiiuae__falcon-7b-details",
    "tiiuae/falcon-40b": "open-llm-leaderboard/tiiuae__falcon-40b-details",
    "mosaicml/mpt-7b": "open-llm-leaderboard/mosaicml__mpt-7b-details",
    "stabilityai/stablelm-zephyr-3b": "open-llm-leaderboard/stabilityai__stablelm-zephyr-3b-details",
    "upstage/SOLAR-10.7B-v1.0": "open-llm-leaderboard/upstage__SOLAR-10.7B-v1.0-details",
    "upstage/SOLAR-10.7B-Instruct-v1.0": "open-llm-leaderboard/upstage__SOLAR-10.7B-Instruct-v1.0-details",
    "microsoft/phi-2": "open-llm-leaderboard/microsoft__phi-2-details",
}


def model_id_to_config_prefix(model_id: str) -> str:
    """Convert model_id to the config name prefix used in leaderboard details."""
    return model_id.replace("/", "__")


def extract_probs_labels_from_arc(model_id: str, repo: str) -> tuple[np.ndarray, np.ndarray] | None:
    """Load arc_challenge details and extract (max_choice_prob, correct) pairs."""
    prefix = model_id_to_config_prefix(model_id)
    config_name = f"{prefix}__leaderboard_arc_challenge"
    try:
        ds = load_dataset(repo, config_name, split="latest", streaming=True)
        probs_list, labels_list = [], []
        for row in ds:
            # resps is a list: [[[loglik_str, is_greedy_str]], ...] — one entry per choice
            resps = row["resps"]
            log_liks = []
            for choice_resp in resps:
                # choice_resp: [[loglik_str, is_greedy_str]]
                if isinstance(choice_resp, (list, tuple)) and len(choice_resp) > 0:
                    inner = choice_resp[0]
                    if isinstance(inner, (list, tuple)) and len(inner) > 0:
                        log_liks.append(float(inner[0]))
                    else:
                        log_liks.append(float(inner))
            if not log_liks:
                continue
            # Convert log-likelihoods to softmax probabilities
            log_liks_arr = np.array(log_liks)
            log_liks_arr -= log_liks_arr.max()  # numerical stability
            exp_liks = np.exp(log_liks_arr)
            probs_softmax = exp_liks / exp_liks.sum()
            # Max confidence = probability assigned to the chosen (argmax) answer
            max_prob = float(probs_softmax.max())
            # Correctness: acc_norm preferred, fallback to acc
            correct = float(row["acc_norm"] if row["acc_norm"] is not None else row["acc"])
            probs_list.append(max_prob)
            labels_list.append(int(correct))
        if len(probs_list) < 10:
            print(f"  WARNING: only {len(probs_list)} samples for {model_id}", flush=True)
            return None
        return np.array(probs_list, dtype=float), np.array(labels_list, dtype=int)
    except Exception as e:
        print(f"  ERROR loading {model_id}: {e}", flush=True)
        return None


def compute_ece_from_arrays(probs: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> float:
    return float(cal.get_ece(probs, labels, num_bins=n_bins))


def bootstrap_ece_ci(probs: np.ndarray, labels: np.ndarray, n_bootstrap: int = 10000, seed: int = 42, n_bins: int = 15) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(labels)
    samples = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        samples.append(cal.get_ece(probs[idx], labels[idx], num_bins=n_bins))
    return float(np.percentile(samples, 2.5)), float(np.percentile(samples, 97.5))


def main():
    model_ids = list(MODEL_TO_REPO.keys())
    records = []
    failed = []

    for model_id in model_ids:
        repo = MODEL_TO_REPO[model_id]
        print(f"[{len(records)+len(failed)+1}/30] {model_id}", flush=True)
        result = extract_probs_labels_from_arc(model_id, repo)
        if result is None:
            failed.append(model_id)
            continue
        probs, labels = result
        ece = compute_ece_from_arrays(probs, labels)
        ci_low, ci_high = bootstrap_ece_ci(probs, labels)
        mean_conf = float(probs.mean())
        print(f"  ECE={ece:.4f} CI=[{ci_low:.4f},{ci_high:.4f}] mean_conf={mean_conf:.4f} n={len(probs)}", flush=True)
        records.append({"model_id": model_id, "ECE": ece, "ECE_ci_lower": ci_low, "ECE_ci_upper": ci_high, "mean_confidence": mean_conf, "n_samples": len(probs)})

    if records:
        out_df = pd.DataFrame(records)
        out_path = Path("results/ece_scores_real.csv")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(out_path, index=False)
        print(f"\nSaved {len(out_df)} real ECE scores to {out_path}", flush=True)
        print(out_df[["model_id", "ECE"]].to_string(index=False))

    if failed:
        print(f"\nFailed models ({len(failed)}): {failed}", flush=True)
        # Also update mean_confidence from the arc data if possible
        print("\nPartially successful. Check results/ece_scores_real.csv", flush=True)

    return 0 if len(records) >= 25 else 1


if __name__ == "__main__":
    sys.exit(main())
