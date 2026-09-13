"""
truthfulqa_analysis.py — H-M3 Mechanism Discrimination
TruthfulQA MC1 lm-eval runner and ECE computation.
"""
import glob
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.special import softmax

# Add h-e1/code to path for calibration_analysis
_CODE_DIR = Path(__file__).parent.resolve()
_H_E1_CODE_DIR = str(_CODE_DIR.parent.parent / "h-e1" / "code")
if _H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, _H_E1_CODE_DIR)

from calibration_analysis import compute_ece  # noqa: E402

logger = logging.getLogger(__name__)


def run_lmeval_truthfulqa(
    model_key: str,
    hf_id: str,
    output_dir: str,
    device: str = "cuda",
    timeout: int = 7200,
    limit: int = None,
) -> str:
    """Run lm_eval --tasks truthfulqa_mc1 --num_fewshot 0 --log_samples.

    OOM retry with --batch_size 4.
    Returns: output directory path
    Raises: RuntimeError after 2 failed attempts.
    """
    model_out = os.path.join(output_dir, model_key)
    os.makedirs(model_out, exist_ok=True)

    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={hf_id},dtype=float32",
        "--tasks", "truthfulqa_mc1",
        "--num_fewshot", "0",
        "--output_path", model_out + "/",
        "--log_samples",
        "--device", device,
    ]
    if limit is not None:
        cmd += ["--limit", str(limit)]

    logger.info("Running lm_eval TruthfulQA for %s (hf_id=%s)", model_key, hf_id)
    try:
        subprocess.run(cmd, check=True, timeout=timeout, capture_output=True, text=True)
        logger.info("lm_eval TruthfulQA succeeded for %s", model_key)
        return model_out
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        if "CUDA out of memory" in stderr or "OOM" in stderr:
            logger.warning("OOM for %s, retrying with batch_size=4", model_key)
            cmd_retry = cmd + ["--batch_size", "4"]
            try:
                subprocess.run(cmd_retry, check=True, timeout=timeout, capture_output=True, text=True)
                logger.info("lm_eval TruthfulQA retry succeeded for %s", model_key)
                return model_out
            except subprocess.CalledProcessError as e2:
                raise RuntimeError(
                    f"lm_eval TruthfulQA failed for {model_key} after OOM retry: {e2.stderr}"
                ) from e2
        else:
            raise RuntimeError(
                f"lm_eval TruthfulQA failed for {model_key}: {stderr[:500]}"
            ) from e
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"lm_eval TruthfulQA timed out for {model_key} after {timeout}s")


def load_truthfulqa_logprobs(
    model_key: str,
    results_dir: str,
) -> tuple:
    """Load per-item TruthfulQA MC1 log-probs (variable options).

    Glob: results_dir/{model_key}/**/samples_truthfulqa_mc1*.jsonl
    Returns:
        logprobs_list: list of (K_i,) float64 arrays  # variable K per item
        y_true: (N,) int64
    """
    pattern = os.path.join(results_dir, model_key, "**", "samples_truthfulqa_mc1*.jsonl")
    files = glob.glob(pattern, recursive=True)
    if not files:
        raise FileNotFoundError(
            f"No TruthfulQA samples found for {model_key} in {results_dir}"
        )

    logprobs_list = []
    y_true_list = []

    for fpath in sorted(files):
        with open(fpath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                doc = json.loads(line)
                # Extract log-probs from filtered_resps
                # lm-eval format: [[logprob_str, is_greedy_str], ...] per choice
                lp = [float(resp[0]) for resp in doc["filtered_resps"]]
                # Find correct answer index: mc1_targets.labels has 1 for correct
                mc1_labels = doc["doc"]["mc1_targets"]["labels"]
                gold = int(mc1_labels.index(1))
                logprobs_list.append(np.array(lp, dtype=np.float64))
                y_true_list.append(gold)

    return logprobs_list, np.array(y_true_list, dtype=np.int64)


def _tqa_item_to_softmax_prob(logprobs_i: np.ndarray) -> np.ndarray:
    """Softmax over variable-K log-probs -> probs (K_i,) float64."""
    return softmax(logprobs_i).astype(np.float64)


def _compute_ece_from_conf_correct(
    confidences: np.ndarray,
    correct: np.ndarray,
    n_bins: int = 15,
) -> float:
    """Compute ECE from max-confidence and correctness arrays."""
    # Simple binned ECE computation
    confidences = np.array(confidences, dtype=np.float64)
    correct = np.array(correct, dtype=np.float64)

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(confidences)
    if n == 0:
        return 0.0

    for b in range(n_bins):
        lo, hi = bins[b], bins[b + 1]
        mask = (confidences >= lo) & (confidences < hi)
        if b == n_bins - 1:
            mask = (confidences >= lo) & (confidences <= hi)
        if mask.sum() == 0:
            continue
        avg_conf = confidences[mask].mean()
        avg_acc = correct[mask].mean()
        ece += (mask.sum() / n) * abs(avg_conf - avg_acc)

    return float(ece)


def compute_truthfulqa_ece_all_models(
    tqa_results_dir: str,
    h_e1_results_dir: str,
    sizes: list,
    alignments: list,
    hf_model_ids: dict,
    device: str = "cuda",
    n_bins: int = 15,
    limit: int = None,
) -> dict:
    """Run or load TruthfulQA MC1 for all 12 models; compute ECE.

    Cache check: skip run_lmeval_truthfulqa if JSONL already present.
    Returns:
        {'pythia-{size}-{alignment}': {'ece': float, 'n_items': int}}
    """
    results = {}
    all_keys = []
    for size in sizes:
        all_keys.append((size, "base"))
    for size in sizes:
        for alignment in alignments:
            all_keys.append((size, alignment))

    for size, alignment in all_keys:
        model_key = f"pythia-{size}-{alignment}"
        hf_id = hf_model_ids[size][alignment]

        # Cache check
        pattern = os.path.join(tqa_results_dir, model_key, "**", "samples_truthfulqa_mc1*.jsonl")
        existing = glob.glob(pattern, recursive=True)
        if not existing:
            logger.info("TruthfulQA cache miss for %s, running lm-eval...", model_key)
            run_lmeval_truthfulqa(model_key, hf_id, tqa_results_dir, device, limit=limit)
        else:
            logger.info("TruthfulQA cache hit for %s", model_key)

        try:
            logprobs_list, y_true = load_truthfulqa_logprobs(model_key, tqa_results_dir)
        except FileNotFoundError as e:
            logger.error("Failed to load TruthfulQA for %s: %s", model_key, e)
            results[model_key] = {"ece": float("nan"), "n_items": 0}
            continue

        # Build confidence and correctness arrays
        confs = []
        correct = []
        for lp, y in zip(logprobs_list, y_true):
            probs_i = _tqa_item_to_softmax_prob(lp)
            conf_i = float(np.max(probs_i))
            pred_i = int(np.argmax(probs_i))
            confs.append(conf_i)
            correct.append(int(pred_i == y))

        ece = _compute_ece_from_conf_correct(np.array(confs), np.array(correct), n_bins)
        results[model_key] = {"ece": ece, "n_items": len(y_true)}
        logger.info("TruthfulQA ECE for %s: %.4f (n=%d)", model_key, ece, len(y_true))

    return results


def assess_h3_diagnostic(
    tqa_ece_results: dict,
    mmlu_ece_results: dict,
    sizes: list,
    alignments: list,
) -> dict:
    """H3 diagnostic: TruthfulQA ECE increase >> MMLU ECE increase.

    delta_tqa[alignment] = mean(tqa_ece[aligned]) - mean(tqa_ece[base])
    delta_mmlu[alignment] = mean(mmlu_ece[aligned]) - mean(mmlu_ece[base])
    h3_flag = any(delta_tqa[alignment] > 2 * delta_mmlu[alignment])

    Returns:
        {'h3_flag': bool, 'per_alignment': dict}
    """
    per_alignment = {}
    h3_flag = False

    for alignment in alignments:
        tqa_base_vals = []
        tqa_aligned_vals = []
        mmlu_base_vals = []
        mmlu_aligned_vals = []

        for size in sizes:
            base_key = f"pythia-{size}-base"
            aligned_key = f"pythia-{size}-{alignment}"

            if base_key in tqa_ece_results:
                tqa_base_vals.append(tqa_ece_results[base_key]["ece"])
            if aligned_key in tqa_ece_results:
                tqa_aligned_vals.append(tqa_ece_results[aligned_key]["ece"])
            if base_key in mmlu_ece_results:
                mmlu_base_vals.append(mmlu_ece_results[base_key])
            if aligned_key in mmlu_ece_results:
                mmlu_aligned_vals.append(mmlu_ece_results[aligned_key])

        if not tqa_base_vals or not tqa_aligned_vals:
            per_alignment[alignment] = {
                "delta_tqa": float("nan"),
                "delta_mmlu": float("nan"),
                "ratio": float("nan"),
                "h3_signal": False,
            }
            continue

        delta_tqa = float(np.mean(tqa_aligned_vals) - np.mean(tqa_base_vals))
        delta_mmlu = float(np.mean(mmlu_aligned_vals) - np.mean(mmlu_base_vals)) if mmlu_base_vals else 0.0
        ratio = delta_tqa / max(abs(delta_mmlu), 1e-6)
        h3_signal = delta_tqa > 2 * delta_mmlu

        per_alignment[alignment] = {
            "delta_tqa": delta_tqa,
            "delta_mmlu": delta_mmlu,
            "ratio": ratio,
            "h3_signal": h3_signal,
        }
        if h3_signal:
            h3_flag = True

    logger.info("H3 diagnostic: h3_flag=%s", h3_flag)
    return {"h3_flag": h3_flag, "per_alignment": per_alignment}
