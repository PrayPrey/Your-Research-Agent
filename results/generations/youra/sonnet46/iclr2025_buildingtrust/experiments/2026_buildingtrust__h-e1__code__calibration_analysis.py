"""
calibration_analysis.py — H-E1: Alignment-Induced Brier Reliability Overconfidence
Implements: Brier decomposition (Murphy 1973), ECE (Guo 2017), bootstrap CI, run_analysis
"""

import argparse
import csv
import glob
import json
import logging
import os
from pathlib import Path

import numpy as np
from scipy.special import softmax

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

CALIBRATION_CONFIG = {
    "n_bins": 15,
    "n_bootstrap": 1000,
    "seed": 42,
    "results_dir": "./results",
    "calibration_results_file": "calibration_results.json",
}

EVAL_CONFIG = {
    "batch_size": 8,
    "batch_size_fallback": 4,
    "num_fewshot": 0,
    "task": "mmlu",
    "dtype": "float16",
    "output_base": "./results",
}

GATE_CONFIG = {
    "methods": ["ppo", "dpo"],
    "min_sizes_passing": 2,
    "sizes": ["1.4b", "2.8b", "6.9b"],
    "alignments": ["sft", "dpo", "ppo"],
}

REPORT_CONFIG = {
    "output_path": "04_validation.md",
    "gate_result_path": "./results/gate_result.json",
    "sections": [
        "gate_result",
        "per_model_metrics_table",
        "key_findings",
        "failure_analysis",
        "mechanism_activation_indicators",
    ],
}

# ── Model Registry ────────────────────────────────────────────────────────────

MODEL_REGISTRY = {
    # Base models (confirmed public)
    "1.4b-base": "EleutherAI/pythia-1.4b",
    "2.8b-base": "EleutherAI/pythia-2.8b",
    "6.9b-base": "EleutherAI/pythia-6.9b",
    # Aligned models — public fallback ladder (Risk R1: RLHFlow requires auth)
    # SFT: lomahony helpful-sft (HH training, same Pythia base)
    # DPO: Leogrin/lomahony HH-DPO
    # PPO: usvsnsp/lomahony PPO
    "1.4b-sft": "lomahony/pythia-1.4b-helpful-sft",
    "1.4b-dpo": "Leogrin/eleuther-pythia1.4b-hh-dpo",
    "1.4b-ppo": "lomahony/pythia-1.4b-helpful-sfted1-ppo-3epochs-old",
    "2.8b-sft": "lomahony/pythia-2.8b-helpful-sft",
    "2.8b-dpo": "lomahony/eleuther-pythia2.8b-hh-dpo",
    "2.8b-ppo": "usvsnsp/pythia-2.8b-ppo",
    "6.9b-sft": "lomahony/eleuther-pythia6.9b-hh-sft",
    "6.9b-dpo": "lomahony/eleuther-pythia6.9b-hh-dpo",
    "6.9b-ppo": "usvsnsp/pythia-6.9b-ppo",
}

MODEL_IDS = list(MODEL_REGISTRY.values())

# Flat model list for analysis (model_key format: "pythia-{size}-{alignment}")
MODELS = [
    "pythia-1.4b-base", "pythia-1.4b-sft", "pythia-1.4b-dpo", "pythia-1.4b-ppo",
    "pythia-2.8b-base", "pythia-2.8b-sft", "pythia-2.8b-dpo", "pythia-2.8b-ppo",
    "pythia-6.9b-base", "pythia-6.9b-sft", "pythia-6.9b-dpo", "pythia-6.9b-ppo",
]

N_BINS: int = CALIBRATION_CONFIG["n_bins"]
N_BOOTSTRAP: int = CALIBRATION_CONFIG["n_bootstrap"]
SEED: int = CALIBRATION_CONFIG["seed"]
RESULTS_DIR: str = CALIBRATION_CONFIG["results_dir"]

# ── Base / Aligned ID maps ────────────────────────────────────────────────────

BASE_MODEL_IDS: dict = {
    "1.4b": "EleutherAI/pythia-1.4b",
    "2.8b": "EleutherAI/pythia-2.8b",
    "6.9b": "EleutherAI/pythia-6.9b",
}

ALIGNED_MODEL_IDS: dict = {
    "1.4b": {"sft": "lomahony/pythia-1.4b-helpful-sft", "dpo": "Leogrin/eleuther-pythia1.4b-hh-dpo", "ppo": "lomahony/pythia-1.4b-helpful-sfted1-ppo-3epochs-old"},
    "2.8b": {"sft": "lomahony/pythia-2.8b-helpful-sft", "dpo": "lomahony/eleuther-pythia2.8b-hh-dpo", "ppo": "usvsnsp/pythia-2.8b-ppo"},
    "6.9b": {"sft": "lomahony/eleuther-pythia6.9b-hh-sft", "dpo": "lomahony/eleuther-pythia6.9b-hh-dpo", "ppo": "usvsnsp/pythia-6.9b-ppo"},
}

FALLBACK_MODEL_IDS: dict = {
    "sft": "meta-llama/Llama-2-7b-hf",
    "dpo": "meta-llama/Llama-2-7b-chat-hf",
    "ppo": "meta-llama/Llama-2-7b-chat-hf",
}

# deviation log for Risk R1 fallbacks
DEVIATION_LOG: list = []


# ── A-1: Model ID Resolution ──────────────────────────────────────────────────

def parse_model_ids(fallback_sizes: list | None = None) -> list[tuple[str, str]]:
    """Return list of (model_key, hf_id) for all 9 models (3 base + 6 aligned).

    model_key format: "pythia-{size}-{alignment}"
    fallback_sizes: list of sizes to substitute with FALLBACK_MODEL_IDS (Risk R1)
    Returns: 9 (key, hf_id) tuples in fixed order
    """
    fallback_sizes = fallback_sizes or []
    result = []
    for size in ["1.4b", "2.8b", "6.9b"]:
        # Base model (always confirmed public)
        result.append((f"pythia-{size}-base", BASE_MODEL_IDS[size]))
        # Aligned models
        for alignment in ["sft", "dpo", "ppo"]:
            if size in fallback_sizes:
                hf_id = FALLBACK_MODEL_IDS[alignment]
                DEVIATION_LOG.append({
                    "size": size,
                    "alignment": alignment,
                    "original": ALIGNED_MODEL_IDS[size][alignment],
                    "fallback": hf_id,
                    "reason": "Risk R1: RLHFlow ID unavailable on HuggingFace Hub",
                })
                logger.warning("Risk R1 fallback: pythia-%s-%s -> %s", size, alignment, hf_id)
            else:
                hf_id = ALIGNED_MODEL_IDS[size][alignment]
            result.append((f"pythia-{size}-{alignment}", hf_id))
    return result


def resolve_fallback_model_ids(unavailable: list[str]) -> dict[str, str]:
    """Risk R1 fallback for unavailable aligned model IDs.

    Args:
        unavailable: list of model_key strings (e.g., ["pythia-1.4b-sft"])

    Returns:
        dict mapping model_key -> fallback HuggingFace ID with deviation_note
    """
    result = {}
    for model_key in unavailable:
        parts = model_key.split("-")
        if len(parts) < 3:
            continue
        alignment = parts[-1]  # last part: sft/dpo/ppo
        fallback_id = FALLBACK_MODEL_IDS.get(alignment, "meta-llama/Llama-2-7b-hf")
        result[model_key] = {
            "hf_id": fallback_id,
            "deviation_note": (
                f"Risk R1: {model_key} unavailable on HuggingFace Hub. "
                f"Using LLaMA-2 proxy ({fallback_id}). "
                "Document in 04_validation.md."
            ),
        }
    return result


# ── A-2: Data Loading ─────────────────────────────────────────────────────────

def load_lmeval_samples(
    model_id: str,
    results_dir: str = RESULTS_DIR,
) -> tuple[np.ndarray, np.ndarray]:
    """Parse lm-eval --log_samples JSONL for one model.

    Glob: results_dir/{model_id}/**/samples_mmlu*.jsonl
    Returns: (logprobs, y_true)
      logprobs: (N, 4) float64 — raw log-probs before softmax
      y_true:   (N,)   int64  — gold labels 0-3
    """
    pattern = os.path.join(results_dir, model_id, "**", "samples_mmlu*.jsonl")
    files = glob.glob(pattern, recursive=True)

    if not files:
        logger.warning("No JSONL files found for model '%s' at pattern: %s", model_id, pattern)
        return np.empty((0, 4), dtype=np.float64), np.empty((0,), dtype=np.int64)

    logprobs_list = []
    y_true_list = []

    for fpath in sorted(files):
        with open(fpath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    doc = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # lm-eval v0.4.x --log_samples format:
                # doc["filtered_resps"] contains list of [(log_prob, is_greedy), ...]
                # or doc["resps"] / doc["logprobs"]
                # Gold label: doc["doc"]["answer"] or doc["target"] or doc["gold"]
                lp = _extract_logprobs(doc)
                gold = _extract_gold(doc)

                if lp is None or gold is None:
                    continue
                if len(lp) != 4:
                    continue

                logprobs_list.append(lp)
                y_true_list.append(gold)

    if not logprobs_list:
        logger.warning("No valid samples parsed for model '%s'", model_id)
        return np.empty((0, 4), dtype=np.float64), np.empty((0,), dtype=np.int64)

    logprobs = np.array(logprobs_list, dtype=np.float64)  # (N, 4)
    y_true = np.array(y_true_list, dtype=np.int64)         # (N,)
    logger.info("Loaded %d samples for model '%s'", len(y_true), model_id)
    return logprobs, y_true


def _extract_logprobs(doc: dict) -> list | None:
    """Extract 4 log-probs from lm-eval sample dict (handles v0.4.x format)."""
    # lm-eval v0.4.x: filtered_resps is list of [(score, is_greedy)]
    if "filtered_resps" in doc:
        resps = doc["filtered_resps"]
        if isinstance(resps, list) and len(resps) == 4:
            lps = []
            for r in resps:
                if isinstance(r, (list, tuple)) and len(r) >= 1:
                    lps.append(float(r[0]))
                elif isinstance(r, (int, float)):
                    lps.append(float(r))
                else:
                    return None
            return lps

    # Alternative: resps field
    if "resps" in doc:
        resps = doc["resps"]
        if isinstance(resps, list) and len(resps) == 4:
            lps = []
            for r in resps:
                if isinstance(r, (list, tuple)) and len(r) >= 1:
                    lps.append(float(r[0]))
                elif isinstance(r, (int, float)):
                    lps.append(float(r))
                else:
                    return None
            return lps

    # Try direct logprobs field
    if "logprobs" in doc:
        lp = doc["logprobs"]
        if isinstance(lp, list) and len(lp) == 4:
            return [float(x) for x in lp]

    return None


def _extract_gold(doc: dict) -> int | None:
    """Extract gold label (0-3) from lm-eval sample dict."""
    # lm-eval v0.4.x: "doc" sub-dict contains answer
    if "doc" in doc and isinstance(doc["doc"], dict):
        d = doc["doc"]
        # MMLU: answer field is A/B/C/D or 0/1/2/3
        if "answer" in d:
            val = d["answer"]
            if isinstance(val, int) and 0 <= val <= 3:
                return val
            if isinstance(val, str):
                mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
                if val in mapping:
                    return mapping[val]
                try:
                    return int(val)
                except ValueError:
                    pass

    # Direct gold field
    for field in ["gold", "target", "label"]:
        if field in doc:
            val = doc[field]
            if isinstance(val, int) and 0 <= val <= 3:
                return val
            if isinstance(val, str):
                mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
                if val in mapping:
                    return mapping[val]
                try:
                    v = int(val)
                    if 0 <= v <= 3:
                        return v
                except ValueError:
                    pass

    return None


# ── A-2: Calibration Metrics ──────────────────────────────────────────────────

def compute_brier_decomposition(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = N_BINS,
) -> tuple[float, float, float]:
    """Murphy (1973) 3-component Brier decomposition.

    Args:
        y_true: (N,) int64 labels in {0,1,2,3}
        y_prob: (N, 4) float64 softmax probabilities
        n_bins: number of equal-width bins (default 15)

    Returns:
        (reliability, resolution, uncertainty) all float
        reliability = Σ_k Σ_j (n_kj/N)(f_kj - o_kj)^2
        resolution  = Σ_k Σ_j (n_kj/N)(o_kj - o_bar_j)^2
        uncertainty = Σ_j o_bar_j * (1 - o_bar_j)
    """
    N = len(y_true)
    if N == 0:
        return 0.0, 0.0, 0.0

    n_classes = y_prob.shape[1]
    one_hot = (y_true[:, None] == np.arange(n_classes)).astype(float)  # (N, 4)
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)

    REL = 0.0
    RES = 0.0
    UNC = 0.0

    for j in range(n_classes):
        o_bar_j = one_hot[:, j].mean()
        UNC += o_bar_j * (1.0 - o_bar_j)

        bin_idx = np.digitize(y_prob[:, j], bin_edges) - 1
        bin_idx = np.clip(bin_idx, 0, n_bins - 1)

        for b in range(n_bins):
            mask = bin_idx == b
            n_b = mask.sum()
            if n_b == 0:
                continue
            f_bj = y_prob[mask, j].mean()
            o_bj = one_hot[mask, j].mean()
            REL += (n_b / N) * (f_bj - o_bj) ** 2
            RES += (n_b / N) * (o_bj - o_bar_j) ** 2

    return float(REL), float(RES), float(UNC)


def compute_ece(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = N_BINS,
) -> float:
    """Guo et al. (2017) top-1 confidence ECE.

    Args:
        y_true: (N,) int64 labels in {0,1,2,3}
        y_prob: (N, 4) float64 softmax probabilities
        n_bins: number of equal-width bins (default 15)

    Returns:
        ECE scalar float in [0, 1]
    """
    N = len(y_true)
    if N == 0:
        return 0.0

    conf = y_prob.max(axis=1)           # (N,)
    pred = y_prob.argmax(axis=1)        # (N,)
    correct = (pred == y_true).astype(float)  # (N,)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ECE = 0.0

    for b in range(n_bins):
        mask = (conf >= bin_edges[b]) & (conf < bin_edges[b + 1])
        if b == n_bins - 1:
            mask = (conf >= bin_edges[b]) & (conf <= bin_edges[b + 1])
        n_b = mask.sum()
        if n_b == 0:
            continue
        ECE += (n_b / N) * abs(correct[mask].mean() - conf[mask].mean())

    return float(ECE)


# ── A-3: Bootstrap CI ─────────────────────────────────────────────────────────

def compute_delta_reliability(
    base_logprobs: np.ndarray,
    aligned_logprobs: np.ndarray,
    y_true: np.ndarray,
    n_bins: int = N_BINS,
    n_bootstrap: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> tuple[float, float, float]:
    """Bootstrap 95% CI for delta Brier reliability (aligned - base).

    Args:
        base_logprobs:    (N, 4) float64 raw log-probs
        aligned_logprobs: (N, 4) float64 raw log-probs
        y_true:           (N,)   int64
        n_bins, n_bootstrap, seed: calibration parameters

    Returns:
        (delta_reliability, ci_lower, ci_upper)
    """
    N = len(y_true)
    if N == 0:
        return 0.0, 0.0, 0.0

    base_prob = softmax(base_logprobs, axis=-1)      # (N, 4)
    aligned_prob = softmax(aligned_logprobs, axis=-1) # (N, 4)

    # Point estimate
    rel_base = compute_brier_decomposition(y_true, base_prob, n_bins)[0]
    rel_aligned = compute_brier_decomposition(y_true, aligned_prob, n_bins)[0]
    delta = rel_aligned - rel_base

    # Bootstrap
    rng = np.random.default_rng(seed)
    boot_deltas = np.empty(n_bootstrap)

    for b in range(n_bootstrap):
        idx = rng.integers(0, N, size=N)
        rel_b = compute_brier_decomposition(y_true[idx], base_prob[idx], n_bins)[0]
        rel_a = compute_brier_decomposition(y_true[idx], aligned_prob[idx], n_bins)[0]
        boot_deltas[b] = rel_a - rel_b

    ci_lower = float(np.percentile(boot_deltas, 2.5))
    ci_upper = float(np.percentile(boot_deltas, 97.5))

    return float(delta), ci_lower, ci_upper


# ── A-3: Full Analysis ────────────────────────────────────────────────────────

def run_analysis(results_dir: str = RESULTS_DIR, smoke_test: bool = False) -> dict:
    """Load all models, compute all metrics, save calibration_results.json.

    Args:
        results_dir: path to lm-eval output directory
        smoke_test: if True, only process first model with first 10 samples

    Returns:
        results_dict keyed by model_key:
          base:    {"ece": float, "brier_rel": float, "brier_res": float, "brier_unc": float}
          aligned: {..., "delta_rel": float, "ci_lower": float, "ci_upper": float}
    """
    os.makedirs(results_dir, exist_ok=True)

    # Load all logprobs
    all_logprobs: dict = {}
    all_ytrue: dict = {}

    model_list = MODELS[:1] if smoke_test else MODELS

    for model_key in model_list:
        logprobs, y_true = load_lmeval_samples(model_key, results_dir)
        if smoke_test and len(y_true) > 10:
            logprobs = logprobs[:10]
            y_true = y_true[:10]
        all_logprobs[model_key] = logprobs
        all_ytrue[model_key] = y_true
        logger.info("Loaded %s: %d samples", model_key, len(y_true))

    results: dict = {}

    # Compute per-model metrics
    for model_key in model_list:
        logprobs = all_logprobs[model_key]
        y_true = all_ytrue[model_key]

        if len(y_true) == 0:
            logger.warning("Skipping %s — no samples loaded", model_key)
            results[model_key] = {
                "ece": None, "brier_rel": None, "brier_res": None, "brier_unc": None,
                "n_samples": 0, "status": "no_data",
            }
            continue

        y_prob = softmax(logprobs, axis=-1)
        rel, res, unc = compute_brier_decomposition(y_true, y_prob)
        ece = compute_ece(y_true, y_prob)

        results[model_key] = {
            "ece": ece,
            "brier_rel": rel,
            "brier_res": res,
            "brier_unc": unc,
            "n_samples": int(len(y_true)),
            "status": "ok",
        }

    # Compute delta_reliability for aligned vs base
    for size in ["1.4b", "2.8b", "6.9b"]:
        base_key = f"pythia-{size}-base"
        if base_key not in all_logprobs or len(all_ytrue.get(base_key, [])) == 0:
            continue

        for alignment in ["sft", "dpo", "ppo"]:
            aligned_key = f"pythia-{size}-{alignment}"
            if aligned_key not in model_list:
                continue
            if aligned_key not in all_logprobs or len(all_ytrue.get(aligned_key, [])) == 0:
                if aligned_key in results:
                    results[aligned_key].update(delta_rel=None, ci_lower=None, ci_upper=None)
                continue

            # Use base y_true (same MMLU items)
            base_logprobs = all_logprobs[base_key]
            aligned_logprobs = all_logprobs[aligned_key]
            y_true_base = all_ytrue[base_key]

            # Align lengths (take min if different)
            n = min(len(y_true_base), len(all_ytrue[aligned_key]))
            delta, ci_lo, ci_hi = compute_delta_reliability(
                base_logprobs[:n], aligned_logprobs[:n], y_true_base[:n]
            )
            if aligned_key in results:
                results[aligned_key].update(
                    delta_rel=delta, ci_lower=ci_lo, ci_upper=ci_hi
                )

    # Save calibration_results.json
    json_path = os.path.join(results_dir, CALIBRATION_CONFIG["calibration_results_file"])
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info("Saved calibration results: %s", json_path)

    # Save CSV summary
    csv_path = os.path.join(results_dir, "results_summary.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["model_id", "ece", "brier_rel", "delta_rel", "ci_lower", "ci_upper"])
        for model_key, metrics in results.items():
            writer.writerow([
                model_key,
                metrics.get("ece"),
                metrics.get("brier_rel"),
                metrics.get("delta_rel"),
                metrics.get("ci_lower"),
                metrics.get("ci_upper"),
            ])
    logger.info("Saved CSV summary: %s", csv_path)

    return results


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="H-E1 Calibration Analysis")
    parser.add_argument("--results-dir", default=RESULTS_DIR, help="lm-eval output directory")
    parser.add_argument("--smoke-test", action="store_true", help="Run on 1 model, 10 samples")
    args = parser.parse_args()

    results = run_analysis(results_dir=args.results_dir, smoke_test=args.smoke_test)
    print(f"\nAnalysis complete. {len(results)} models processed.")
    for k, v in results.items():
        if v.get("status") == "ok":
            print(f"  {k}: ECE={v['ece']:.4f}, Brier-REL={v['brier_rel']:.4f}")
