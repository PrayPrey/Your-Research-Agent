import logging
import os
from typing import Dict, List, Optional

import numpy as np

from config import ExperimentConfig

logger = logging.getLogger(__name__)


class Visualizer:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg
        self.figures_dir = cfg.paths.figures_dir
        os.makedirs(self.figures_dir, exist_ok=True)

    def plot_gate_metrics(
        self,
        std_t_star: float,
        t_star_per_seed: Dict[int, Optional[float]],
        gate_threshold: float = 10.0,
    ) -> str:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(["std(t*)"], [std_t_star], color="#4C72B0", alpha=0.85, label=f"std(t*)={std_t_star:.2f}")
        ax.axhline(gate_threshold, color="red", linestyle="--", linewidth=1.5, label=f"Gate threshold ({gate_threshold} epochs)")

        valid_t = [(s, v) for s, v in t_star_per_seed.items() if v is not None]
        if valid_t:
            xs = [0] * len(valid_t)
            ys = [v for _, v in valid_t]
            ax.scatter(xs, ys, color="orange", s=80, zorder=5, label="Per-seed t* values")
            for s, v in valid_t:
                ax.annotate(f"seed {s}: {v}", xy=(0, v), xytext=(0.08, v), fontsize=8, color="darkorange")

        ax.set_ylabel("Epochs")
        ax.set_title("H-M3: std(t*) vs. MUST_WORK Gate Threshold")
        ax.legend()
        ax.set_ylim(0, max(gate_threshold * 1.5, std_t_star * 1.5 + 1))

        path = os.path.join(self.figures_dir, "gate_metrics.png")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info(f"Saved gate metrics figure: {path}")
        return path

    def plot_delta_timeline(
        self,
        delta_curves: Dict[int, np.ndarray],
        t_star_per_seed: Dict[int, Optional[int]],
        checkpoint_interval: int = 2,
    ) -> str:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(9, 5))
        colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

        for i, (seed, curve) in enumerate(sorted(delta_curves.items())):
            epochs = [j * checkpoint_interval for j in range(len(curve))]
            color = colors[i % len(colors)]
            ax.plot(epochs, curve, marker="o", markersize=4, color=color, label=f"Seed {seed}", linewidth=1.5)
            t = t_star_per_seed.get(seed)
            if t is not None:
                ax.axvline(t, color=color, linestyle="--", alpha=0.7, linewidth=1.2)
                ax.annotate(f"t*={t}", xy=(t, 0), xytext=(t + 0.2, ax.get_ylim()[0] + 0.005),
                            fontsize=8, color=color, rotation=90, va="bottom")

        ax.axhline(0.02, color="gray", linestyle=":", linewidth=1.2, label="Threshold (0.02)")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("delta(t) = spurious_acc - core_acc")
        ax.set_title("H-M3: delta(t) Curves with t* per Seed")
        ax.legend()

        path = os.path.join(self.figures_dir, "delta_timeline.png")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info(f"Saved delta timeline figure: {path}")
        return path

    def plot_gap_area_boxplot(
        self,
        gap_areas: List[float],
        ci_low: float,
        ci_high: float,
    ) -> str:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 5))
        ax.boxplot(gap_areas, positions=[1], widths=0.5, patch_artist=True,
                   boxprops=dict(facecolor="#4C72B0", alpha=0.6))
        ax.scatter([1] * len(gap_areas), gap_areas, color="orange", zorder=5, s=60, label="Per-seed gap area")
        ax.axhspan(ci_low, ci_high, alpha=0.2, color="green", label=f"95% CI [{ci_low:.4f}, {ci_high:.4f}]")

        ax.set_xticks([1])
        ax.set_xticklabels(["Gap Area A"])
        ax.set_ylabel("Gap Area A = sum(max(delta(t), 0))")
        ax.set_title("H-M3: Gap Area Distribution with Bootstrap CI")
        ax.legend()

        path = os.path.join(self.figures_dir, "gap_area_boxplot.png")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info(f"Saved gap area boxplot: {path}")
        return path

    def plot_cross_dataset(self, waterbirds_std: float, celeba_std: float) -> str:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(7, 5))
        ax.bar(["Waterbirds", "CelebA"], [waterbirds_std, celeba_std],
               color=["#4C72B0", "#DD8452"], alpha=0.85)
        ax.axhline(10.0, color="red", linestyle="--", linewidth=1.5, label="Gate threshold (10 epochs)")
        ax.set_ylabel("std(t*) [epochs]")
        ax.set_title("H-M3: std(t*) Cross-Dataset Consistency")
        ax.legend()

        path = os.path.join(self.figures_dir, "cross_dataset.png")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        logger.info(f"Saved cross-dataset figure: {path}")
        return path

    def save_all(
        self,
        delta_curves: Dict[int, np.ndarray],
        analysis_results: dict,
        validation_results: dict,
    ) -> List[str]:
        saved = []
        std_t = analysis_results.get("std_t_star", 0.0)
        t_star_per_seed = analysis_results.get("t_star_per_seed", {})
        gap_areas = list(analysis_results.get("gap_areas", {}).values())
        ci = validation_results.get("gap_area_ci_95")

        try:
            saved.append(self.plot_gate_metrics(std_t, t_star_per_seed))
        except Exception as e:
            logger.warning(f"gate_metrics plot failed: {e}")

        try:
            saved.append(self.plot_delta_timeline(
                delta_curves, t_star_per_seed,
                self.cfg.analysis.checkpoint_interval
            ))
        except Exception as e:
            logger.warning(f"delta_timeline plot failed: {e}")

        if ci and gap_areas:
            try:
                saved.append(self.plot_gap_area_boxplot(gap_areas, ci[0], ci[1]))
            except Exception as e:
                logger.warning(f"gap_area_boxplot failed: {e}")

        logger.info(f"All figures saved: {saved}")
        return saved
