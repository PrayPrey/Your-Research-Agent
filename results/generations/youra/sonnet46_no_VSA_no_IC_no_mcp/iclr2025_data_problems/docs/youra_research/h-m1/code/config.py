from dataclasses import dataclass, field
from pathlib import Path


BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
NGRAM_SIZE = 13
SAMPLE_SIZE = 10_000
RANDOM_SEED = 42
CORRECTED_ALPHA = 0.0125  # Bonferroni 0.05/4
N_WORKERS = 4
# EleutherAI/pile uses an obsolete loading script; monology/pile-uncopyrighted
# is a parquet mirror of the public-license subsets with the same pile_set_name metadata.
PILE_HF_ID = "monology/pile-uncopyrighted"
PILE_DEDUP_HF_ID = "EleutherAI/the_pile_deduplicated"
BASE_DIR = Path(__file__).parent.parent
FIGURES_DIR = BASE_DIR / "figures"
CHECKPOINT_DIR = BASE_DIR / "checkpoints"

PIPELINE_STAGES = [
    "hash_diff",
    "sample",
    "ngrams",
    "overlaps",
    "stats",
    "ablations",
    "figures",
]


@dataclass
class FigureConfig:
    dpi: int = 150
    bar_figsize: tuple = (10, 6)
    violin_figsize: tuple = (12, 6)
    rank_figsize: tuple = (6, 6)
    subset_figsize: tuple = (12, 7)
    color_removed: str = "#d62728"
    color_retained: str = "#1f77b4"
    sig_thresholds: tuple = (0.001, 0.01, 0.05)
    sig_markers: tuple = ("***", "**", "*", "ns")
    output_format: str = "png"
    ci: float = 0.95
    out_bar: str = "fig_overlap_comparison.png"
    out_violin: str = "fig_overlap_distributions.png"
    out_rank: str = "fig_rank_correlation.png"
    out_subset: str = "fig_subset_breakdown.png"


@dataclass
class StyleConfig:
    seaborn_theme: str = "whitegrid"
    seaborn_context: str = "paper"
    font_size_title: int = 13
    font_size_axis: int = 11
    font_size_tick: int = 9
    font_size_annot: int = 10
    axis_labels: dict = field(default_factory=lambda: {
        "mmlu": "MMLU",
        "hellaswag": "HellaSwag",
        "arc_challenge": "ARC-Challenge",
        "winogrande": "WinoGrande",
        "arc_easy": "ARC-Easy",
    })
    title_bar: str = "13-gram Overlap: Removed vs Retained Docs"
    title_violin: str = "Overlap Distribution by Benchmark"
    title_rank: str = "Expected Contamination Rank vs Observed Overlap Diff"
    title_subset: str = "Mean Removed-Doc Overlap by Pile Subset"
    mpl_backend: str = "Agg"


@dataclass
class PipelineConfig:
    stages: list = field(default_factory=lambda: list(PIPELINE_STAGES))
    skip_stages: list = field(default_factory=list)
    checkpoint_dir: Path = CHECKPOINT_DIR
    resume: bool = True
    log_level: str = "INFO"
    checkpoint_files: dict = field(default_factory=lambda: {
        "hash_diff":  "removed_hashes.json",
        "sample":     "sampled_docs.json",
        "ngrams":     "ngram_sets.pkl",
        "overlaps":   "overlap_scores.json",
        "stats":      "statistical_results.json",
        "ablations":  "ablation_results.json",
    })


@dataclass
class ResourceConfig:
    n_workers: int = N_WORKERS
    batch_size: int = 1_000
    memory_limit_gb: float = 14.0
    random_seed: int = RANDOM_SEED
