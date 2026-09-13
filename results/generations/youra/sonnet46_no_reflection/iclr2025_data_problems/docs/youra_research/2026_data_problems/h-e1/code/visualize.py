from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from config import ExperimentConfig


class ResultVisualizer:
    """Generate all figures to h-e1/figures/."""

    def __init__(self, cfg: ExperimentConfig):
        self.figures_dir = Path(cfg.figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def gate_metrics_bar(self, metrics: dict) -> None:
        """Bar chart: actual vs target for gate metrics. Saves gate_metrics.png."""
        fig, ax = plt.subplots(figsize=(8, 5))
        labels = ["N-gram Recall\n(Lexical, target≥0.80)", "N-gram Recall\n(Semantic, target≤0.40)", "Min-K%++ F1\nVariance (target≥0.15)"]
        targets = [0.80, 0.40, 0.15]
        actuals = [
            metrics.get("ngram_lexical_recall", 0.0),
            metrics.get("ngram_semantic_recall", 0.0),
            metrics.get("minkpp_f1_variance", 0.0),
        ]
        x = np.arange(len(labels))
        w = 0.35
        ax.bar(x - w/2, targets, w, label="Target", color="steelblue", alpha=0.7)
        ax.bar(x + w/2, actuals, w, label="Actual", color="coral", alpha=0.9)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_ylabel("Value")
        ax.set_title("Gate Metrics: Target vs Actual (h-e1)")
        ax.legend()
        plt.tight_layout()
        out = self.figures_dir / "gate_metrics.png"
        plt.savefig(out, dpi=150)
        plt.close(fig)
        print(f"  ✓ Saved {out}")

    def phase_diagram_scatter(
        self,
        ngram_counts: np.ndarray,
        cosines: np.ndarray,
        dominant_detector: np.ndarray,
        strata: np.ndarray,
    ) -> None:
        """2D scatter: (max_13gram × max_SBERT_cosine) colored by stratum. Saves phase_diagram.png."""
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = {"lexical": "blue", "semantic": "green", "indeterminate": "grey"}
        for s, c in colors.items():
            mask = strata == s
            ax.scatter(ngram_counts[mask], cosines[mask], c=c, alpha=0.3, s=5, label=s)
        ax.set_xlabel("Max 13-gram Overlap Count")
        ax.set_ylabel("Max SBERT Cosine Similarity")
        ax.set_title("2D Contamination Phase Diagram (h-e1)")
        ax.legend(markerscale=3)
        plt.tight_layout()
        out = self.figures_dir / "phase_diagram.png"
        plt.savefig(out, dpi=150)
        plt.close(fig)
        print(f"  ✓ Saved {out}")

    def stratum_f1_heatmap(
        self,
        f1_matrix: np.ndarray,
        detector_names: list[str],
    ) -> None:
        """5 detectors × 3 strata × 3 corpora heatmap. Saves stratum_f1_heatmap.png."""
        strata_names = ["lexical", "semantic", "indeterminate"]
        corpus_names = ["pile", "c4", "redpajama"]
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        for ci, corpus in enumerate(corpus_names):
            data = f1_matrix[:, :, ci] if f1_matrix.ndim == 3 else f1_matrix
            sns.heatmap(
                data, ax=axes[ci],
                xticklabels=strata_names,
                yticklabels=detector_names[:data.shape[0]],
                vmin=0, vmax=1, annot=True, fmt=".2f", cmap="YlOrRd",
            )
            axes[ci].set_title(f"F1 Heatmap: {corpus}")
        plt.suptitle("Per-Stratum F1: 5 Detectors × 3 Strata × 3 Corpora (h-e1)")
        plt.tight_layout()
        out = self.figures_dir / "stratum_f1_heatmap.png"
        plt.savefig(out, dpi=150)
        plt.close(fig)
        print(f"  ✓ Saved {out}")

    def minkpp_variance_bar(self, f1_by_corpus: dict) -> None:
        """Min-K%++ F1 per corpus bar chart. Saves minkpp_variance.png."""
        fig, ax = plt.subplots(figsize=(6, 4))
        corpora = list(f1_by_corpus.keys())
        vals = [f1_by_corpus[c] for c in corpora]
        ax.bar(corpora, vals, color="teal", alpha=0.8)
        ax.axhline(y=0.15, color="red", linestyle="--", label="Target variance ≥ 0.15")
        ax.set_ylabel("F1 Score")
        ax.set_title("Min-K%++ F1 per Corpus (h-e1)")
        ax.legend()
        plt.tight_layout()
        out = self.figures_dir / "minkpp_variance.png"
        plt.savefig(out, dpi=150)
        plt.close(fig)
        print(f"  ✓ Saved {out}")

    def indeterminacy_pie(self, stratum_counts: dict) -> None:
        """Pie chart of stratum sizes. Saves indeterminacy_pie.png."""
        fig, ax = plt.subplots(figsize=(6, 5))
        labels = list(stratum_counts.keys())
        sizes = [stratum_counts[k] for k in labels]
        colors = ["#4C9ED9", "#56B356", "#AAAAAA"]
        ax.pie(sizes, labels=labels, colors=colors[:len(labels)], autopct="%1.1f%%", startangle=90)
        ax.set_title("Benchmark Item Stratum Distribution (h-e1)")
        plt.tight_layout()
        out = self.figures_dir / "indeterminacy_pie.png"
        plt.savefig(out, dpi=150)
        plt.close(fig)
        print(f"  ✓ Saved {out}")
