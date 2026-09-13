from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m2"
    name: str = "Min-k% Memorization Signal — Pile vs Dedup-Pile"

    model_configs: dict = field(default_factory=lambda: {
        "pile_1b":      ("EleutherAI/pythia-1b",            "step98000"),
        "deduped_1b":   ("EleutherAI/pythia-1b-deduped",   "step143000"),
        "pile_6.9b":    ("EleutherAI/pythia-6.9b",          "step98000"),
        "deduped_6.9b": ("EleutherAI/pythia-6.9b-deduped", "step143000"),
    })
    model_sizes: list = field(default_factory=lambda: ["1b", "6.9b"])
    cache_dir: str = "./model_cache"
    torch_dtype: str = "float16"
    device: str = "cuda"

    tokens_per_step: int = 2_097_152
    pile_matched_step: int = 98_000
    dedup_final_step: int = 143_000

    benchmarks: list = field(default_factory=lambda: ["mmlu", "hellaswag", "arc_challenge", "winogrande"])

    k_primary: int = 20
    k_values: list = field(default_factory=lambda: [10, 20, 40])
    k_sensitivity: list = field(default_factory=lambda: [5, 10, 20, 40, 60])
    min_seq_len: int = 32
    max_seq_len: int = 512

    alpha: float = 0.05
    n_benchmarks: int = 4
    corrected_alpha: float = 0.0125
    wilcoxon_alternative: str = "greater"
    ttest_alternative: str = "greater"

    scoring_batch_size: int = 1
    n_workers: int = 1

    base_dir: Path = Path("docs/youra_research/h-m2")
    checkpoint_dir: Path = Path("docs/youra_research/h-m2/checkpoints")
    figures_dir: Path = Path("docs/youra_research/h-m2/figures")
    hm1_results_path: Path = Path("docs/youra_research/h-m1/dry_run_result.json")

    pipeline_stages: list = field(default_factory=lambda: [
        "load_benchmarks",
        "score_models",
        "run_stats",
        "run_ablations",
        "generate_figures",
    ])
    skip_stages: list = field(default_factory=list)
    resume: bool = True

    log_level: str = "INFO"
    random_seed: int = 1


# Module-level constants for import convenience
BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_CONFIGS = {
    "pile_1b":      ("EleutherAI/pythia-1b",            "step98000"),
    "deduped_1b":   ("EleutherAI/pythia-1b-deduped",   "step143000"),
    "pile_6.9b":    ("EleutherAI/pythia-6.9b",          "step98000"),
    "deduped_6.9b": ("EleutherAI/pythia-6.9b-deduped", "step143000"),
}
K_VALUES = [10, 20, 40]
CORRECTED_ALPHA = 0.0125
MIN_SEQ_LEN = 32
MAX_SEQ_LEN = 512
CHECKPOINT_DIR = Path("docs/youra_research/h-m2/checkpoints")
FIGURES_DIR = Path("docs/youra_research/h-m2/figures")
