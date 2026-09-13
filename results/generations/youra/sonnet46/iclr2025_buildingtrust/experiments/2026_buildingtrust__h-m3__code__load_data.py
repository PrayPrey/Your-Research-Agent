"""
load_data.py — H-M3 Mechanism Discrimination
Data loading: Path A (reuse h-e1 lm-eval outputs) with Path B fallback.
"""
import logging
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

# Add h-e1/code to path for importing calibration_analysis
_CODE_DIR = Path(__file__).parent.resolve()
_H_E1_CODE_DIR = str(_CODE_DIR.parent.parent / "h-e1" / "code")
if _H_E1_CODE_DIR not in sys.path:
    sys.path.insert(0, _H_E1_CODE_DIR)

from calibration_analysis import load_lmeval_samples  # noqa: E402

logger = logging.getLogger(__name__)


def load_logprob_matrices(
    h_e1_results_dir: str,
    h_m3_results_dir: str,
    sizes: list,
    alignments: list,
    device: str = "cuda",
) -> tuple:
    """Dispatcher: try Path A (h-e1 cached results), fallback to Path B (re-run lm-eval).

    Returns:
        ({model_key: (N,4) float64}, "Path A" | "Path B")
        model_key format: 'pythia-{size}-{alignment}'
    """
    logger.info("Attempting Path A: load from h-e1 cached results (%s)", h_e1_results_dir)
    try:
        result = _load_path_a(h_e1_results_dir, sizes, alignments)
        logger.info("Path A succeeded.")
        return result
    except (RuntimeError, FileNotFoundError) as e:
        logger.warning("Path A failed: %s. Falling back to Path B.", e)

    logger.info("Executing Path B: re-run lm-eval with --log_samples")
    return _load_path_b(h_m3_results_dir, sizes, alignments, device=device)


def _load_path_a(results_dir: str, sizes: list, alignments: list) -> tuple:
    """Load from h-e1 JSONL via load_lmeval_samples(model_id, results_dir).

    Returns:
        ({model_key: (N,4) float64}, "Path A")
    Raises:
        RuntimeError if any model returns 0 samples.
    """
    logprob_matrices = {}
    all_keys = []

    for size in sizes:
        all_keys.append(f"pythia-{size}-base")
    for size in sizes:
        for alignment in alignments:
            all_keys.append(f"pythia-{size}-{alignment}")

    logger.info("Loading logprob matrices from Path A: %s", results_dir)
    for model_key in all_keys:
        logprobs, y_true = load_lmeval_samples(model_key, results_dir)
        n = logprobs.shape[0]
        if n == 0:
            raise RuntimeError(
                f"Path A: model '{model_key}' returned 0 samples from {results_dir}."
            )
        logger.info("  %s: %d samples, shape %s", model_key, n, logprobs.shape)
        logprob_matrices[model_key] = logprobs

    # Align to min sample count
    min_n = min(v.shape[0] for v in logprob_matrices.values())
    max_n = max(v.shape[0] for v in logprob_matrices.values())
    if min_n != max_n:
        logger.info(
            "Sample count mismatch (min=%d, max=%d). Truncating all to min=%d.",
            min_n, max_n, min_n,
        )
        logprob_matrices = {k: v[:min_n] for k, v in logprob_matrices.items()}

    logger.info("Path A: loaded %d models, %d samples each", len(logprob_matrices), min_n)
    return logprob_matrices, "Path A"


def _run_lmeval_for_model(
    model_key: str,
    hf_id: str,
    output_dir: str,
    device: str = "cuda",
    num_fewshot: int = 4,
    timeout: int = 7200,
) -> str:
    """Subprocess lm_eval CLI with --log_samples. OOM retry with --batch_size 4."""
    model_out = os.path.join(output_dir, model_key)
    os.makedirs(model_out, exist_ok=True)

    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={hf_id},dtype=float32",
        "--tasks", "mmlu",
        "--num_fewshot", str(num_fewshot),
        "--output_path", model_out + "/",
        "--log_samples",
        "--device", device,
    ]

    logger.info("Running lm_eval for %s (hf_id=%s)", model_key, hf_id)
    try:
        subprocess.run(cmd, check=True, timeout=timeout, capture_output=True, text=True)
        logger.info("lm_eval succeeded for %s", model_key)
        return model_out
    except subprocess.CalledProcessError as e:
        stderr = e.stderr or ""
        if "CUDA out of memory" in stderr or "OOM" in stderr:
            logger.warning("OOM for %s, retrying with batch_size=4", model_key)
            cmd_retry = cmd + ["--batch_size", "4"]
            try:
                subprocess.run(cmd_retry, check=True, timeout=timeout, capture_output=True, text=True)
                logger.info("lm_eval retry succeeded for %s", model_key)
                return model_out
            except subprocess.CalledProcessError as e2:
                raise RuntimeError(
                    f"lm_eval failed for {model_key} after OOM retry: {e2.stderr}"
                ) from e2
        else:
            raise RuntimeError(f"lm_eval failed for {model_key}: {stderr[:500]}") from e
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"lm_eval timed out for {model_key} after {timeout}s")


def _load_path_b(
    output_dir: str,
    sizes: list,
    alignments: list,
    device: str = "cuda",
) -> tuple:
    """Re-run lm-eval for all 12 models then load via load_lmeval_samples().

    Returns:
        ({model_key: (N,4) float64}, "Path B")
    """
    from config import HF_MODEL_IDS, N_ITEMS_EXPECTED

    logprob_matrices = {}
    os.makedirs(output_dir, exist_ok=True)

    keys_to_run = []
    for size in sizes:
        keys_to_run.append((size, "base"))
    for size in sizes:
        for alignment in alignments:
            keys_to_run.append((size, alignment))

    for size, alignment in keys_to_run:
        model_key = f"pythia-{size}-{alignment}"
        hf_id = HF_MODEL_IDS[size][alignment]

        _run_lmeval_for_model(
            model_key=model_key,
            hf_id=hf_id,
            output_dir=output_dir,
            device=device,
            num_fewshot=4,
        )

        logprobs, y_true = load_lmeval_samples(model_key, output_dir)
        n = logprobs.shape[0]
        if n == 0:
            raise RuntimeError(f"Path B: model '{model_key}' returned 0 samples after lm_eval run.")
        if n != N_ITEMS_EXPECTED:
            logger.warning("Path B: %s has %d samples, expected %d", model_key, n, N_ITEMS_EXPECTED)

        logprob_matrices[model_key] = logprobs
        logger.info("Path B loaded %s: %d samples", model_key, n)

    logger.info("Path B: loaded %d models", len(logprob_matrices))
    return logprob_matrices, "Path B"


def load_labels(
    h_e1_results_dir: str,
    sizes: list,
) -> dict:
    """Load y_true (N,) int64 per base model_key from h-e1 JSONL.

    Returns:
        {'pythia-{size}-base': y_true (N,) int64}
    """
    labels = {}
    for size in sizes:
        model_id = f"pythia-{size}-base"
        logprobs, y_true = load_lmeval_samples(model_id, h_e1_results_dir)
        labels[model_id] = y_true
        logger.info("Loaded labels for %s: %d items", model_id, len(y_true))
    return labels

# Public alias for test access
load_logprob_matrices_path_a = _load_path_a
