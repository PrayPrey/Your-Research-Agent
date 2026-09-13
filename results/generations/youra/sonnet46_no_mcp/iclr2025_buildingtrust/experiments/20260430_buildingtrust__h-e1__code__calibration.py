from __future__ import annotations

import glob
import json
import logging
from pathlib import Path

import numpy as np
from netcal.metrics import ECE

from config import ECE_BINS, STOCHASTIC_SEEDS

logger = logging.getLogger(__name__)


def load_mmlu_samples(model_results_path: Path) -> list[dict]:
    pattern = str(model_results_path / "samples_mmlu*.jsonl")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError(f"No MMLU sample files found matching: {pattern}")
    samples = []
    for fpath in sorted(files):
        with open(fpath) as f:
            for line in f:
                line = line.strip()
                if line:
                    samples.append(json.loads(line))
    return samples


def compute_ece_brier(samples: list[dict], n_bins: int = ECE_BINS) -> tuple[float, float]:
    confidences = []
    correctness = []

    for sample in samples:
        filtered_resps = sample.get("filtered_resps", [])
        if not filtered_resps:
            continue
        log_probs = np.array([r[0] for r in filtered_resps], dtype=np.float64)
        # softmax
        log_probs -= log_probs.max()
        probs = np.exp(log_probs)
        probs /= probs.sum()

        pred = int(np.argmax(probs))
        target = sample.get("target", sample.get("doc", {}).get("answer", -1))
        if isinstance(target, str):
            # some tasks store letter, convert
            target = ord(target.upper()) - ord("A")

        conf = float(probs[pred])
        correct = int(pred == int(target))
        confidences.append(conf)
        correctness.append(correct)

    if not confidences:
        return float("nan"), float("nan")

    confidences = np.array(confidences, dtype=np.float64)
    correctness = np.array(correctness, dtype=np.float64)

    ece_metric = ECE(n_bins)
    ece_val = float(ece_metric.measure(confidences, correctness))
    brier_val = float(np.mean((confidences - correctness) ** 2))

    return ece_val, brier_val


def extract_calibration_for_model(model_id: str, results_dir: Path) -> dict[str, float]:
    results_dir = Path(results_dir)
    greedy_path = results_dir / model_id / "greedy"
    samples_greedy = load_mmlu_samples(greedy_path)
    ece_g, brier_g = compute_ece_brier(samples_greedy)

    ece_stoch_vals, brier_stoch_vals = [], []
    for seed in STOCHASTIC_SEEDS:
        stoch_path = results_dir / model_id / f"stochastic_seed{seed}"
        try:
            samples_s = load_mmlu_samples(stoch_path)
            e, b = compute_ece_brier(samples_s)
            if not np.isnan(e):
                ece_stoch_vals.append(e)
                brier_stoch_vals.append(b)
        except FileNotFoundError:
            logger.warning(f"Missing stochastic samples for {model_id} seed={seed}")

    ece_s = float(np.mean(ece_stoch_vals)) if ece_stoch_vals else float("nan")
    brier_s = float(np.mean(brier_stoch_vals)) if brier_stoch_vals else float("nan")

    return {
        "ece_greedy": ece_g,
        "brier_greedy": brier_g,
        "ece_stochastic": ece_s,
        "brier_stochastic": brier_s,
    }
