import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from config import ExperimentConfig


class ResultVisualizer:
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.figures_dir = config.get_figures_dir()
        os.makedirs(self.figures_dir, exist_ok=True)

    def bar_chart(self, mean_rho: float, threshold: float = 0.7) -> str:
        fig, ax = plt.subplots(figsize=(6, 4))
        color = "green" if mean_rho < threshold else "red"
        ax.bar(["Mean Spearman ρ"], [mean_rho], color=color, alpha=0.7, label="Measured")
        ax.axhline(y=threshold, color="red", linestyle="--", label=f"Threshold ({threshold})")
        verdict = "PASS (misalignment confirmed)" if mean_rho < threshold else "FAIL (no misalignment)"
        ax.set_title(f"H-E1: LoRA-Locret Correlation\n{verdict}")
        ax.set_ylabel("Spearman ρ")
        ax.set_ylim(0, 1)
        ax.legend()
        path = os.path.join(self.figures_dir, "mean_rho_bar.png")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def layer_head_heatmap(self, per_layer_per_head: np.ndarray) -> str:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(
            per_layer_per_head,
            ax=ax,
            cmap="coolwarm",
            center=0.7,
            vmin=0,
            vmax=1,
            xticklabels=4,
            yticklabels=4,
        )
        ax.set_title("H-E1: Spearman ρ by Layer × Head")
        ax.set_xlabel("Head Index")
        ax.set_ylabel("Layer Index")
        path = os.path.join(self.figures_dir, "layer_head_heatmap.png")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def token_scatter(
        self,
        lora_scores: np.ndarray,
        cis_scores: np.ndarray,
        tokens: list,
        example_idx: int,
    ) -> str:
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.scatter(lora_scores, cis_scores, alpha=0.6, s=20)
        ax.set_xlabel("LoRA Attention Score")
        ax.set_ylabel("Locret CIS Score")
        ax.set_title(f"H-E1: Token-Level Scores (Example {example_idx})")
        path = os.path.join(self.figures_dir, "token_scatter.png")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def rho_histogram(self, per_example_rho: list) -> str:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(per_example_rho, bins=20, color="steelblue", alpha=0.7, edgecolor="black")
        ax.axvline(x=0.7, color="red", linestyle="--", label="Threshold 0.7")
        ax.set_xlabel("Mean Spearman ρ")
        ax.set_ylabel("Count")
        ax.set_title("H-E1: Per-Example ρ Distribution")
        ax.legend()
        path = os.path.join(self.figures_dir, "rho_histogram.png")
        plt.tight_layout()
        plt.savefig(path, dpi=150)
        plt.close()
        return path

    def save_all(
        self,
        results: dict,
        lora_scores_sample: list,
        cis_scores_sample: list,
        tokens_sample: list,
    ) -> dict:
        paths = {}
        paths["bar"] = self.bar_chart(results["mean_rho"])
        per_layer_mean = np.array(results.get("per_layer_mean", np.zeros((32, 32))))
        paths["heatmap"] = self.layer_head_heatmap(per_layer_mean)
        if lora_scores_sample and cis_scores_sample:
            lora_arr = np.array(lora_scores_sample[0]).mean(axis=0) if len(lora_scores_sample) > 0 else np.array([])
            cis_arr = np.array(cis_scores_sample[0]).mean(axis=0) if len(cis_scores_sample) > 0 else np.array([])
            if len(lora_arr) > 0 and len(cis_arr) > 0:
                paths["scatter"] = self.token_scatter(lora_arr, cis_arr, tokens_sample, 0)
            else:
                paths["scatter"] = None
        else:
            paths["scatter"] = None
        paths["histogram"] = self.rho_histogram(results.get("all_example_rhos", []))
        return paths
