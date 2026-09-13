import os
import sys
import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

# Ensure h-m1/code is in path for local imports
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import config as cfg
from peakedness import analyze_group_peakedness, test_peakedness_difference
from visualization import save_all_figures


def load_or_run_inference(
    dataset_name: str,
    model_key: str,
    h_e1_results_dir: str,
    h_e1_code_dir: str,
    results_dir: str,
    max_samples: Optional[int] = 2000,
    seed: int = 42,
) -> List[Dict]:
    """
    Returns list of dicts each with 'logprobs' (List[float]) and 'label' (int).

    Path A: load from h-m1/results/{model}_{dataset}_records.npz
    Path B: load from h-e1/results/{model}_{dataset}_records.npz (if has logprobs)
    Path C: re-run inference via H-E1 pipeline
    """
    # Path A: h-m1 own cache
    cache_path = os.path.join(results_dir, f"{model_key}_{dataset_name}_records.npz")
    if os.path.exists(cache_path):
        print(f"  Loading from h-m1 cache: {cache_path}")
        data = np.load(cache_path, allow_pickle=True)
        if "records" in data:
            records = data["records"].tolist()
            print(f"  Loaded {len(records)} records from cache.")
            return records

    # Path B: h-e1 raw records cache
    h_e1_cache = os.path.join(h_e1_results_dir, f"{model_key}_{dataset_name}_records.npz")
    if os.path.exists(h_e1_cache):
        print(f"  Checking h-e1 cache: {h_e1_cache}")
        data = np.load(h_e1_cache, allow_pickle=True)
        if "records" in data:
            recs = data["records"].tolist()
            if recs and isinstance(recs[0], dict) and "logprobs" in recs[0]:
                print(f"  Found {len(recs)} raw records in h-e1 cache.")
                os.makedirs(results_dir, exist_ok=True)
                np.savez(cache_path, records=np.array(recs, dtype=object))
                return recs

    # Path C: re-run inference
    print(f"  No cache found — running inference for {model_key}/{dataset_name}")
    if h_e1_code_dir not in sys.path:
        sys.path.insert(0, h_e1_code_dir)

    from inference import load_model, run_inference
    from data_loader import get_dataset
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("_h_e1_cfg_rt", os.path.join(h_e1_code_dir, "config.py"))
    _h_e1_cfg_rt = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_h_e1_cfg_rt)
    FARQUHAR_DATA_DIR = _h_e1_cfg_rt.FARQUHAR_DATA_DIR
    MAX_NEW_TOKENS = _h_e1_cfg_rt.MAX_NEW_TOKENS

    print(f"  Loading dataset {dataset_name}...")
    samples = get_dataset(dataset_name, farquhar_data_dir=FARQUHAR_DATA_DIR)
    print(f"  Dataset size: {len(samples)}")

    if max_samples and len(samples) > max_samples:
        random.seed(seed)
        samples = random.sample(samples, max_samples)
        print(f"  Subsampled to {len(samples)}")

    print(f"  Loading model {model_key}...")
    model, tokenizer = load_model(model_key)

    print(f"  Running inference ({len(samples)} samples)...")
    records = run_inference(samples, model, tokenizer, max_new_tokens=MAX_NEW_TOKENS)
    print(f"  Inference done: {len(records)} records with logprobs")

    # Free GPU memory
    import torch
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    os.makedirs(results_dir, exist_ok=True)
    np.savez(cache_path, records=np.array(records, dtype=object))
    print(f"  Cached raw records to {cache_path}")
    return records


def run_dataset(
    dataset_name: str,
    model_key: str,
) -> Dict:
    """Full peakedness analysis for one (dataset, model) pair."""
    records = load_or_run_inference(
        dataset_name,
        model_key,
        cfg.H_E1_RESULTS_DIR,
        cfg.H_E1_CODE_DIR,
        cfg.RESULTS_DIR,
        cfg.MAX_SAMPLES[dataset_name],
        cfg.SEED,
    )

    print(f"  Computing peakedness for {len(records)} records...")
    groups = analyze_group_peakedness(records)
    print(f"  Groups: hallucinated={len(groups['hallucinated'])}, correct={len(groups['correct'])}")

    stats = test_peakedness_difference(groups["hallucinated"], groups["correct"])

    # Cache peakedness arrays
    os.makedirs(cfg.RESULTS_DIR, exist_ok=True)
    np.savez(
        os.path.join(cfg.RESULTS_DIR, f"peakedness_{model_key}_{dataset_name}.npz"),
        hallucinated=np.array(groups["hallucinated"]),
        correct=np.array(groups["correct"]),
        labels=np.array([r["label"] for r in records]),
    )

    return {
        "dataset": dataset_name,
        "model": model_key,
        "stats": stats,
        "hallucinated": groups["hallucinated"],
        "correct": groups["correct"],
        "n_samples": len(records),
    }


def save_results(all_results: Dict, results_dir: str) -> None:
    summary = {}
    for k, v in all_results.items():
        summary[k] = {
            "p_value": v["stats"]["p_value"],
            "direction": v["stats"]["direction"],
            "mean_hallucinated": v["stats"]["mean_hallucinated"],
            "mean_correct": v["stats"]["mean_correct"],
            "n_hallucinated": v["stats"]["n_hallucinated"],
            "n_correct": v["stats"]["n_correct"],
        }
    out = os.path.join(results_dir, "results_summary.json")
    with open(out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Summary saved to {out}")


def main() -> None:
    os.makedirs(cfg.RESULTS_DIR, exist_ok=True)
    os.makedirs(cfg.FIGURES_DIR, exist_ok=True)

    all_results = {}

    for model_key in cfg.MODELS_TO_RUN:
        for dataset_name in cfg.DATASETS:
            key = f"{model_key}_{dataset_name}"
            print(f"\n--- Running {key} ---")

            if model_key == "mistral":
                try:
                    result = run_dataset(dataset_name, model_key)
                except Exception as e:
                    print(f"  Mistral failed: {e} — skipping")
                    continue
            else:
                result = run_dataset(dataset_name, model_key)

            all_results[key] = result
            p = result["stats"]["p_value"]
            direction = result["stats"]["direction"]
            mean_h = result["stats"]["mean_hallucinated"]
            mean_c = result["stats"]["mean_correct"]
            print(f"  p={p:.4f}, direction={direction}, mean_h={mean_h:.4f}, mean_c={mean_c:.4f}")

    save_results(all_results, cfg.RESULTS_DIR)

    gate_pass = any(
        v["stats"]["p_value"] < cfg.P_VALUE_THRESHOLD
        for v in all_results.values()
    )

    print("\nGenerating figures...")
    save_all_figures(all_results, cfg.FIGURES_DIR)
    print(f"Figures saved to {cfg.FIGURES_DIR}")

    print("\n" + "=" * 60)
    print(f"GATE RESULT: {'PASS' if gate_pass else 'FAIL'}")
    for k, v in all_results.items():
        s = v["stats"]
        sig = "PASS p<0.05" if s["p_value"] < cfg.P_VALUE_THRESHOLD else "FAIL p>=0.05"
        print(f"  {k}: {sig}, p={s['p_value']:.6f}, direction={s['direction']}, "
              f"n_h={s['n_hallucinated']}, n_c={s['n_correct']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
