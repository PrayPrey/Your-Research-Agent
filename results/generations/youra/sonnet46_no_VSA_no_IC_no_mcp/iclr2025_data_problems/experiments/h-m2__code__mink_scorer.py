"""Min-k% probability scoring per Shi et al. 2023."""
from __future__ import annotations

import gc
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MinKScore:
    item_id: int
    benchmark: str
    model_key: str
    scores: dict  # {k_percent: float}  e.g. {10: -4.2, 20: -3.8, 40: -3.1}


# Type alias
ScoresDict = dict  # {model_key: {benchmark: [per-item k20 scores]}}


def compute_token_logprobs(
    input_ids,  # torch.Tensor shape [1, seq_len]
    model,
    device: str = "cuda",
) -> np.ndarray:
    """
    Compute per-token log-probabilities via next-token prediction.
    Returns np.ndarray shape [seq_len - 1].
    """
    import torch
    import torch.nn.functional as F

    with torch.no_grad():
        logits = model(input_ids).logits  # [1, L, V]

    shift_logits = logits[0, :-1, :].float()  # [L-1, V]
    shift_labels = input_ids[0, 1:]            # [L-1]

    log_probs = F.log_softmax(shift_logits, dim=-1)  # [L-1, V]
    token_log_probs = log_probs[
        torch.arange(len(shift_labels), device=device), shift_labels
    ].cpu().numpy()  # [L-1]

    return token_log_probs


def compute_mink_score(
    token_log_probs: np.ndarray,
    k: int = 20,
) -> float:
    """
    Min-k% probability score per Shi et al. 2023.
    Higher (less negative) = more memorized.
    """
    if len(token_log_probs) == 0:
        return float("-inf")

    sorted_probs = np.sort(token_log_probs)  # ascending: lowest first
    k_count = max(1, int(len(sorted_probs) * k / 100))
    return float(sorted_probs[:k_count].mean())


def score_benchmark_items(
    items,  # list[BenchmarkItem]
    model,
    tokenizer,
    k_values: list[int] | None = None,
    device: str = "cuda",
) -> list[MinKScore]:
    """Score all valid benchmark items for one model."""
    if k_values is None:
        k_values = [10, 20, 40]

    import torch
    from tqdm import tqdm
    from config import MIN_SEQ_LEN, MAX_SEQ_LEN

    scores = []
    valid_items = [it for it in items if it.valid]

    bench_name = valid_items[0].benchmark if valid_items else "unknown"
    for item in tqdm(valid_items, desc=f"Scoring {bench_name}", leave=False):
        inputs = tokenizer(
            item.text,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_SEQ_LEN,
        )
        input_ids = inputs["input_ids"].to(device)

        if input_ids.shape[1] < MIN_SEQ_LEN:
            continue

        try:
            token_log_probs = compute_token_logprobs(input_ids, model, device)
            item_scores = {k: compute_mink_score(token_log_probs, k) for k in k_values}
            scores.append(MinKScore(
                item_id=item.item_id,
                benchmark=item.benchmark,
                model_key="",  # filled by caller
                scores=item_scores,
            ))
        except Exception as e:
            logger.warning(f"Scoring error on item {item.item_id}: {e}")

    return scores


def save_mink_scores(
    scores: list[MinKScore],
    model_key: str,
    benchmark: str,
    checkpoint_dir: Path,
) -> None:
    """Atomic write of min-k% scores for one model-benchmark combination."""
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_key": model_key,
        "benchmark": benchmark,
        "scores": [
            {"item_id": s.item_id, **{f"k{k}": v for k, v in s.scores.items()}}
            for s in scores
        ],
    }
    safe_key = model_key.replace(".", "_")
    path = checkpoint_dir / f"mink_scores_{safe_key}_{benchmark}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload))
    os.replace(tmp, path)
    logger.info(f"Saved {len(scores)} scores: {path.name}")


def load_mink_scores(
    model_key: str,
    benchmark: str,
    checkpoint_dir: Path,
) -> list[MinKScore] | None:
    """Load checkpoint; return None if missing."""
    safe_key = model_key.replace(".", "_")
    path = checkpoint_dir / f"mink_scores_{safe_key}_{benchmark}.json"
    if not path.exists():
        return None

    data = json.loads(path.read_text())
    scores = []
    for d in data["scores"]:
        item_id = d["item_id"]
        k_scores = {int(k[1:]): v for k, v in d.items() if k.startswith("k")}
        scores.append(MinKScore(
            item_id=item_id,
            benchmark=benchmark,
            model_key=model_key,
            scores=k_scores,
        ))
    return scores


def score_all_models(
    model_configs: dict,  # {key: (hf_id, revision)}
    benchmark_items: dict,  # {benchmark: [BenchmarkItem]}
    k_values: list[int] | None = None,
    checkpoint_dir: Path | None = None,
    device: str = "cuda",
) -> ScoresDict:
    """
    Score all models × benchmarks with checkpoint/resume.
    Returns {model_key: {benchmark: [k20_scores_per_item]}}.
    Memory strategy: load one model at a time, del + empty_cache between.
    """
    import torch
    from config import BENCHMARKS, K_VALUES, CHECKPOINT_DIR
    from model_loader import load_model_checkpoint, verify_checkpoint_step, ModelSpec

    if k_values is None:
        k_values = K_VALUES
    if checkpoint_dir is None:
        checkpoint_dir = CHECKPOINT_DIR

    results: ScoresDict = {}

    for model_key, (model_id, revision) in model_configs.items():
        results[model_key] = {}

        # Check if all benchmarks cached
        all_cached = all(
            load_mink_scores(model_key, bench, checkpoint_dir) is not None
            for bench in BENCHMARKS
        )
        if all_cached:
            logger.info(f"All benchmarks cached for {model_key}, loading from checkpoint")
            for bench in BENCHMARKS:
                cached = load_mink_scores(model_key, bench, checkpoint_dir)
                results[model_key][bench] = [s.scores.get(20, float("-inf")) for s in cached]
            continue

        # Load model
        logger.info(f"Loading model: {model_key}")
        model, tokenizer = load_model_checkpoint(model_id, revision, device=device)
        corpus, size = model_key.split("_", 1)
        spec = ModelSpec(model_id=model_id, revision=revision,
                         corpus=corpus, size=size, key=model_key)
        verify_checkpoint_step(model, spec)

        for bench in BENCHMARKS:
            cached = load_mink_scores(model_key, bench, checkpoint_dir)
            if cached is not None:
                logger.info(f"Cached: {model_key}/{bench}")
                results[model_key][bench] = [s.scores.get(20, float("-inf")) for s in cached]
                continue

            items = benchmark_items.get(bench, [])
            # Apply length filter with this model's tokenizer
            from benchmark_loader import filter_by_length
            valid_items = filter_by_length(items, tokenizer)

            scores = score_benchmark_items(valid_items, model, tokenizer,
                                           k_values=k_values, device=device)
            for s in scores:
                s.model_key = model_key

            save_mink_scores(scores, model_key, bench, checkpoint_dir)
            results[model_key][bench] = [s.scores.get(20, float("-inf")) for s in scores]
            logger.info(f"Scored {len(scores)} items for {model_key}/{bench}")

        # Free VRAM
        del model
        gc.collect()
        torch.cuda.empty_cache()

    return results
