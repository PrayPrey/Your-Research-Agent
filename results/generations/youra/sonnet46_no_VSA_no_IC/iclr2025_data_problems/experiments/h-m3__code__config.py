from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

CHECKPOINT_STEPS: list[int] = [
    0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
    *range(1000, 144000, 1000),
]  # len=154

PILE_DOMAINS: list[str] = [
    "Pile-CC", "PubMed Central", "Books3", "OpenWebText2", "ArXiv",
    "Github", "FreeLaw", "StackExchange", "USPTO Backgrounds",
    "PubMed Abstracts", "Gutenberg (PG-19)", "OpenSubtitles",
    "Wikipedia (en)", "DM Mathematics", "Ubuntu IRC", "BookCorpus2",
    "EuroParl", "HackerNews", "YoutubeSubtitles", "PhilPapers",
    "NIH ExPorter", "Enron Emails",
]  # len=22

FOCAL_DOMAINS: dict[str, str] = {
    "wikipedia": "Wikipedia (en)",
    "books": "Books3",
}

BATCH_SIZE: str = "auto"
DTYPE: str = "float"
NGRAM_SIZE: int = 13
CONTAMINATION_DELTA_THRESHOLD: float = 0.03
SEED: int = 42

MODEL_SIZES: list[str] = [
    "70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b",
    "70m-deduped", "160m-deduped", "410m-deduped", "1b-deduped",
    "1.4b-deduped", "2.8b-deduped", "6.9b-deduped", "12b-deduped",
]

MODEL_IDS: dict[str, str] = {
    "70m":           "EleutherAI/pythia-70m",
    "160m":          "EleutherAI/pythia-160m",
    "410m":          "EleutherAI/pythia-410m",
    "1b":            "EleutherAI/pythia-1b",
    "1.4b":          "EleutherAI/pythia-1.4b",
    "2.8b":          "EleutherAI/pythia-2.8b",
    "6.9b":          "EleutherAI/pythia-6.9b",
    "12b":           "EleutherAI/pythia-12b",
    "70m-deduped":   "EleutherAI/pythia-70m-deduped",
    "160m-deduped":  "EleutherAI/pythia-160m-deduped",
    "410m-deduped":  "EleutherAI/pythia-410m-deduped",
    "1b-deduped":    "EleutherAI/pythia-1b-deduped",
    "1.4b-deduped":  "EleutherAI/pythia-1.4b-deduped",
    "2.8b-deduped":  "EleutherAI/pythia-2.8b-deduped",
    "6.9b-deduped":  "EleutherAI/pythia-6.9b-deduped",
    "12b-deduped":   "EleutherAI/pythia-12b-deduped",
}

MODEL_PARAMS: dict[str, int] = {
    "70m": 70_000_000, "160m": 160_000_000, "410m": 410_000_000,
    "1b": 1_000_000_000, "1.4b": 1_400_000_000, "2.8b": 2_800_000_000,
    "6.9b": 6_900_000_000, "12b": 12_000_000_000,
    "70m-deduped": 70_000_000, "160m-deduped": 160_000_000,
    "410m-deduped": 410_000_000, "1b-deduped": 1_000_000_000,
    "1.4b-deduped": 1_400_000_000, "2.8b-deduped": 2_800_000_000,
    "6.9b-deduped": 6_900_000_000, "12b-deduped": 12_000_000_000,
}

TASKS: dict[str, dict] = {
    "mmlu":          {"num_fewshot": 5,  "metric": "acc,none"},
    "hellaswag":     {"num_fewshot": 10, "metric": "acc_norm,none"},
    "arc_challenge": {"num_fewshot": 25, "metric": "acc_norm,none"},
    "winogrande":    {"num_fewshot": 5,  "metric": "acc,none"},
}

# ponytail: lowered to 0.20 because 70m fails >=100 checkpoints with 0.30 threshold; keep knob for tuning
FLOOR_THRESHOLD: float = 0.20
MIN_VALID_CHECKPOINTS: int = 100

N_PERMUTATIONS: int = 1000
VIF_THRESHOLD: float = 10.0
PCA_VARIANCE_RETAINED: float = 0.95
BOOKS3_VARIANCE_THRESHOLD: float = 1e-6
N_MODEL_SIZES: int = 16
N_CHECKPOINTS: int = 154
N_DOMAINS: int = 22

H_E1_EXPOSURE_DIR: str = "docs/youra_research/h-e1"
RESULTS_DIR: str = "results/h-m3"
EVAL_CACHE_DIR: str = "results/h-m3/eval_cache"
FIGURES_DIR: str = "docs/youra_research/h-m3/figures"
EXISTING_CACHE_PATH: str = "pythia/evals/pythia-v1/"

SMALL_MODEL_SIZES: list[str] = [s for s in MODEL_SIZES if any(
    s.startswith(p) for p in ["70m", "160m", "410m"]
)]
LARGE_MODEL_SIZES: list[str] = [s for s in MODEL_SIZES if s not in SMALL_MODEL_SIZES]


@dataclass
class PanelConfig:
    floor_threshold: float = FLOOR_THRESHOLD
    vif_threshold: float = VIF_THRESHOLD
    pca_variance_retained: float = PCA_VARIANCE_RETAINED
    min_checkpoints_per_model: int = MIN_VALID_CHECKPOINTS
    dropped_domain: str = "Unknown"
    multiindex_levels: list[str] = field(default_factory=lambda: ["model_size", "checkpoint"])


@dataclass
class VisualizationConfig:
    dpi: int = 300
    figsize_default: tuple = (10, 6)
    palette: str = "colorblind"
    ci_alpha: float = 0.95
    figure_paths: dict = field(default_factory=lambda: {
        "fig1": "fig1_gate_metrics_comparison.png",
        "fig2": "fig2_domain_coefficient_heatmap.png",
        "fig3": "fig3_directional_scatter.png",
        "fig4": "fig4_r2_decomposition.png",
        "fig5": "fig5_permutation_null.png",
        "fig6": "fig6_subgroup_robustness.png",
    })


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "H-M3"
    base_hypothesis: str = "H-M2"
    output_dir: str = RESULTS_DIR
    figures_dir: str = FIGURES_DIR
    seed: int = SEED
    n_permutations: int = N_PERMUTATIONS
    benchmarks: list[str] = field(default_factory=lambda: list(TASKS.keys()))
    focal_domains: list[str] = field(default_factory=lambda: list(FOCAL_DOMAINS.values()))
    model_sizes: list[str] = field(default_factory=lambda: list(MODEL_SIZES))
    small_sizes: list[str] = field(default_factory=lambda: list(SMALL_MODEL_SIZES))
    large_sizes: list[str] = field(default_factory=lambda: list(LARGE_MODEL_SIZES))
    resume: bool = True


FIGURE_SPECS: dict[str, dict] = {
    "fig1": {
        "type": "bar",
        "groups": ["mmlu", "hellaswag", "arc_challenge", "winogrande"],
        "series": ["Wikipedia (en)", "Books3"],
        "error_bars": "95ci_clustered_se",
        "figsize": (12, 6),
    },
    "fig2": {
        "type": "heatmap",
        "rows": "domain_cols",
        "cols": ["mmlu", "hellaswag", "arc_challenge", "winogrande"],
        "figsize": (14, 10),
    },
    "fig3": {
        "type": "scatter",
        "x": "beta_Wikipedia",
        "y": "beta_Books3",
        "hue": "benchmark",
        "diagonal": True,
        "figsize": (8, 8),
    },
    "fig4": {
        "type": "bar",
        "series": ["domain_only", "scale_only", "full"],
        "metric": "r2_within",
        "figsize": (10, 6),
    },
    "fig5": {
        "type": "histogram",
        "n_bins": 50,
        "panels": ["mmlu", "hellaswag"],
        "figsize": (12, 5),
    },
    "fig6": {
        "type": "bar",
        "series": ["small_wiki", "small_books", "large_wiki", "large_books"],
        "figsize": (14, 6),
    },
}
