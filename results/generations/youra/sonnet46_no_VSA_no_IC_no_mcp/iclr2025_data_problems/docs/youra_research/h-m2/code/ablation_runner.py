"""k-sensitivity ablation for min-k% score robustness analysis."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


def run_k_sensitivity(
    benchmark_items: dict,
    device: str = "cuda",
    model_id: str = "EleutherAI/pythia-1b",
    revision: str = "step98000",
    benchmark: str = "mmlu",
    k_values: list[int] | None = None,
    checkpoint_dir: Path | None = None,
    max_items: int = 500,
) -> dict:
    """
    Compute mean min-k% differential (Pile - deduped) across k values for one benchmark.
    Uses Pythia-1B for speed (ablation, not primary result).

    Returns: {k: {"pile_mean": float, "dedup_mean": float, "differential": float}}
    """
    from config import K_VALUES, CHECKPOINT_DIR, CORRECTED_ALPHA
    from model_loader import load_model_checkpoint
    from mink_scorer import score_benchmark_items, compute_mink_score, load_mink_scores, save_mink_scores
    from benchmark_loader import filter_by_length
    import torch, gc

    if k_values is None:
        k_values = [5, 10, 20, 40, 60]
    if checkpoint_dir is None:
        checkpoint_dir = CHECKPOINT_DIR

    ablation_cache = checkpoint_dir / f"ablation_k_sensitivity_{benchmark}.json"
    if ablation_cache.exists():
        logger.info("Loading k-sensitivity from cache")
        return json.loads(ablation_cache.read_text())

    dedup_id = "EleutherAI/pythia-1b-deduped"
    dedup_revision = "step143000"

    items = benchmark_items.get(benchmark, [])
    if max_items and len(items) > max_items:
        items = items[:max_items]

    results = {}
    for (mid, rev, corpus_key) in [
        (model_id, revision, "pile"),
        (dedup_id, dedup_revision, "deduped"),
    ]:
        cache_key = f"ablation_{corpus_key}_1b"
        cache_path = checkpoint_dir / f"ablation_scores_{corpus_key}.json"

        if cache_path.exists():
            raw = json.loads(cache_path.read_text())
            results[corpus_key] = {int(k): v for k, v in raw.items()}
            continue

        logger.info(f"Loading {corpus_key} model for ablation")
        model, tokenizer = load_model_checkpoint(mid, rev, device=device)

        valid_items = filter_by_length(items, tokenizer)
        corpus_results = {}
        for k in k_values:
            scores_list = score_benchmark_items(valid_items, model, tokenizer,
                                                k_values=[k], device=device)
            k_scores = [s.scores.get(k, float("-inf")) for s in scores_list]
            corpus_results[k] = float(np.mean(k_scores)) if k_scores else float("nan")

        # Atomic save
        tmp = cache_path.with_suffix(".tmp")
        tmp.write_text(json.dumps({str(k): v for k, v in corpus_results.items()}))
        os.replace(tmp, cache_path)

        results[corpus_key] = corpus_results
        del model
        gc.collect()
        torch.cuda.empty_cache()

    # Compute differentials
    output = {}
    for k in k_values:
        pile_mean = results.get("pile", {}).get(k, float("nan"))
        dedup_mean = results.get("deduped", {}).get(k, float("nan"))
        output[k] = {
            "pile_mean": pile_mean,
            "dedup_mean": dedup_mean,
            "differential": pile_mean - dedup_mean if not (
                np.isnan(pile_mean) or np.isnan(dedup_mean)
            ) else float("nan"),
        }

    # Cache final result
    tmp = ablation_cache.with_suffix(".tmp")
    tmp.write_text(json.dumps({str(k): v for k, v in output.items()}))
    os.replace(tmp, ablation_cache)

    return output
