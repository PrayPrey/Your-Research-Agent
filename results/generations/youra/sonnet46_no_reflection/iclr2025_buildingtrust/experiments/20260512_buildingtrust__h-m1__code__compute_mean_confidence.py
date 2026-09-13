"""compute_mean_confidence.py — Compute real mean_confidence per model from leaderboard arc_challenge."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from datasets import load_dataset

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


def get_mean_confidence(model_id: str, repo: str) -> float | None:
    prefix = model_id.replace("/", "__")
    config_name = f"{prefix}__leaderboard_arc_challenge"
    try:
        ds = load_dataset(repo, config_name, split="latest", streaming=True)
        max_probs = []
        for row in ds:
            resps = row["resps"]
            log_liks = []
            for choice_resp in resps:
                if isinstance(choice_resp, (list, tuple)) and len(choice_resp) > 0:
                    inner = choice_resp[0]
                    if isinstance(inner, (list, tuple)) and len(inner) > 0:
                        log_liks.append(float(inner[0]))
                    else:
                        log_liks.append(float(inner))
            if not log_liks:
                continue
            lls = np.array(log_liks)
            lls -= lls.max()
            exp_lls = np.exp(lls)
            probs = exp_lls / exp_lls.sum()
            max_probs.append(float(probs.max()))
        if not max_probs:
            return None
        return float(np.mean(max_probs))
    except Exception as e:
        print(f"  ERROR {model_id}: {e}", flush=True)
        return None


def main():
    records = []
    for i, (model_id, repo) in enumerate(MODEL_TO_REPO.items(), 1):
        print(f"[{i}/30] {model_id}", flush=True)
        mc = get_mean_confidence(model_id, repo)
        if mc is not None:
            print(f"  mean_confidence={mc:.4f}", flush=True)
            records.append({"model_id": model_id, "mean_confidence": mc})
        else:
            print(f"  FAILED", flush=True)

    if records:
        mc_df = pd.DataFrame(records)
        mc_df.to_csv("results/mean_confidence_real.csv", index=False)
        print(f"\nSaved {len(mc_df)} rows to results/mean_confidence_real.csv")

        # Update model_matrix.csv
        BASE = Path("../h-e1/code/outputs")
        matrix = pd.read_csv(BASE / "model_matrix.csv")
        matrix = matrix.drop(columns=["mean_confidence"], errors="ignore")
        matrix = matrix.merge(mc_df, on="model_id", how="left")
        matrix.to_csv(BASE / "model_matrix.csv", index=False)
        print("Updated h-e1/code/outputs/model_matrix.csv with real mean_confidence")
        print(matrix[["model_id", "mean_confidence"]].to_string(index=False))

    return 0 if len(records) >= 25 else 1


if __name__ == "__main__":
    sys.exit(main())
