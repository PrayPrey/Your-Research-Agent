"""ece_computer.py — ECE computation per model via uncertainty-calibration."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

import calibration as cal
import config


class ECEComputer:
    def __init__(
        self,
        n_bins: int = 15,
        n_bootstrap: int = config.N_BOOTSTRAP,
        seed: int = config.SEED,
        cache_dir: Optional[Path] = None,
    ) -> None:
        self.n_bins = n_bins
        self.n_bootstrap = n_bootstrap
        self.seed = seed
        self.cache_dir = Path(cache_dir) if cache_dir else None

    def compute_ece(self, probs: np.ndarray, labels: np.ndarray) -> float:
        """Compute ECE scalar via cal.get_ece(probs, labels)."""
        probs = np.asarray(probs, dtype=float)
        labels = np.asarray(labels, dtype=float)
        assert probs.shape == labels.shape, "probs and labels must have same shape"
        assert (probs >= 0).all() and (probs <= 1).all(), "probs must be in [0,1]"
        return float(cal.get_ece(probs, labels.astype(int), num_bins=self.n_bins))

    def compute_ece_ci(
        self, probs: np.ndarray, labels: np.ndarray
    ) -> Tuple[float, float]:
        """Bootstrap 95% CI on ECE (10K resamples)."""
        probs = np.asarray(probs, dtype=float)
        labels = np.asarray(labels, dtype=float)
        rng = np.random.default_rng(self.seed)
        ece_samples = []
        n = len(labels)
        for _ in range(self.n_bootstrap):
            idx = rng.integers(0, n, size=n)
            ece_b = cal.get_ece(probs[idx], labels[idx].astype(int), num_bins=self.n_bins)
            ece_samples.append(ece_b)
        return (float(np.percentile(ece_samples, 2.5)), float(np.percentile(ece_samples, 97.5)))

    def compute_per_model(
        self,
        model_logit_paths: dict[str, Path],
    ) -> pd.DataFrame:
        """Compute ECE + CI for all models from logit files."""
        records = []
        for model_id, path in model_logit_paths.items():
            probs, labels = self._load_logits(Path(path))
            ece = self.compute_ece(probs, labels)
            ci_low, ci_high = self.compute_ece_ci(probs, labels)
            records.append({"model_id": model_id, "ECE": ece, "ECE_ci_lower": ci_low, "ECE_ci_upper": ci_high})
        return pd.DataFrame(records)

    def load_or_compute(
        self,
        model_ids: list[str],
        model_logit_paths: Optional[dict[str, Path]] = None,
        force_recompute: bool = False,
    ) -> pd.DataFrame:
        """Load cached ECE CSV or compute. Fallback: Gaussian mock."""
        if self.cache_dir is not None:
            cache_path = self.cache_dir / "ece_scores.csv"
            if cache_path.exists() and not force_recompute:
                df = pd.read_csv(cache_path)
                if len(df) == len(model_ids):
                    return df

        if model_logit_paths:
            df = self.compute_per_model(model_logit_paths)
            if self.cache_dir is not None:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                df.to_csv(self.cache_dir / "ece_scores.csv", index=False)
            return df

        raise RuntimeError(
            "No cached ECE scores found and no logit paths provided. "
            "Run compute_real_ece.py first to generate results/ece_scores.csv."
        )

    def _load_logits(self, path: Path) -> Tuple[np.ndarray, np.ndarray]:
        """Load lm-eval logit file. Returns (probs [N], labels [N])."""
        import json
        with open(path) as f:
            data = json.load(f)
        probs = np.array(data["probs"], dtype=float)
        labels = np.array(data["labels"], dtype=float)
        return probs, labels

    def _mock_ece(self, n_models: int, model_ids: list[str]) -> pd.DataFrame:
        """Gaussian mock fallback. ECE ~ N(0.12, 0.04) clipped [0.05, 0.25]."""
        rng = np.random.default_rng(self.seed)
        ece_vals = rng.normal(0.12, 0.04, size=n_models)
        ece_vals = np.clip(ece_vals, 0.05, 0.25)
        ci_half = rng.uniform(0.01, 0.03, size=n_models)
        return pd.DataFrame({
            "model_id": model_ids,
            "ECE": ece_vals,
            "ECE_ci_lower": np.clip(ece_vals - ci_half, 0.0, 1.0),
            "ECE_ci_upper": np.clip(ece_vals + ci_half, 0.0, 1.0),
        })


def compute_ece_scores(
    model_ids: list[str],
    cache_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """Top-level entry point."""
    computer = ECEComputer(cache_dir=cache_dir)
    return computer.load_or_compute(model_ids)
