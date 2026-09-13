import logging
from typing import Dict, Optional

import numpy as np

from config import ExperimentConfig

logger = logging.getLogger(__name__)


class TransitionEpochAnalyzer:
    def __init__(self, cfg: ExperimentConfig):
        self.threshold: float = cfg.analysis.threshold
        self.n_consecutive: int = cfg.analysis.n_consecutive
        self.checkpoint_interval: int = cfg.analysis.checkpoint_interval

    def find_t_star(
        self,
        delta_curve: np.ndarray,
        threshold: Optional[float] = None,
        n_consecutive: Optional[int] = None,
    ) -> Optional[int]:
        thr = threshold if threshold is not None else self.threshold
        n_consec = n_consecutive if n_consecutive is not None else self.n_consecutive
        count = 0
        for i, d in enumerate(delta_curve):
            if d < thr:
                count += 1
                if count >= n_consec:
                    start_idx = i - n_consec + 1
                    return start_idx * self.checkpoint_interval
            else:
                count = 0
        return None

    def find_t_star_adaptive(self, delta_curve: np.ndarray) -> Optional[int]:
        t = self.find_t_star(delta_curve)
        if t is not None:
            return t
        # Adaptive fallback: threshold = 0.5 * min(delta_curve)
        adaptive_thr = 0.5 * float(np.min(delta_curve))
        if adaptive_thr <= 0:
            return None
        t_adaptive = self.find_t_star(delta_curve, threshold=adaptive_thr)
        if t_adaptive is not None:
            logger.info(f"Adaptive threshold used: {adaptive_thr:.4f} -> t*={t_adaptive}")
        return t_adaptive

    def compute_gap_area(self, delta_curve: np.ndarray) -> float:
        return float(np.sum(np.maximum(np.array(delta_curve, dtype=np.float32), 0.0)))

    def analyze_across_seeds(self, delta_curves: Dict[int, np.ndarray]) -> dict:
        t_star_per_seed: Dict[int, Optional[int]] = {}
        gap_areas: Dict[int, float] = {}
        used_adaptive: Dict[int, bool] = {}

        for seed, curve in delta_curves.items():
            # Track whether primary threshold works
            t_primary = self.find_t_star(curve)
            t_star = self.find_t_star_adaptive(curve)
            t_star_per_seed[seed] = t_star
            gap_areas[seed] = self.compute_gap_area(curve)
            used_adaptive[seed] = (t_primary is None and t_star is not None)
            logger.info(
                f"[Seed {seed}] t*={t_star} epochs, gap_area={gap_areas[seed]:.4f}, "
                f"adaptive={used_adaptive[seed]}"
            )

        valid = [v for v in t_star_per_seed.values() if v is not None]
        mean_t = float(np.mean(valid)) if valid else None
        std_t = float(np.std(valid, ddof=1)) if len(valid) > 1 else 0.0

        if valid:
            logger.info(
                f"Cross-seed summary: mean_t*={mean_t:.2f}, std_t*={std_t:.2f} epochs, "
                f"valid_seeds={len(valid)}/{len(delta_curves)}"
            )

        return {
            "t_star_per_seed": t_star_per_seed,
            "mean_t_star": mean_t,
            "std_t_star": std_t,
            "gap_areas": gap_areas,
            "mean_gap_area": float(np.mean(list(gap_areas.values()))) if gap_areas else 0.0,
            "valid_seed_count": len(valid),
            "used_adaptive_threshold": used_adaptive,
            "delta_curves_loaded": list(delta_curves.keys()),
        }
