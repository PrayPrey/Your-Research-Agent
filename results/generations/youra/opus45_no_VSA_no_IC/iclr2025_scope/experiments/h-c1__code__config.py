"""Configuration for h-c1: Cross-task scaling law comparison (HotpotQA)."""
from dataclasses import dataclass, field

MODELS: dict[str, float] = {
    "pythia-1b": 1.0e9,
    "pythia-2.8b": 2.8e9,
    "pythia-6.9b": 6.9e9,
    "pythia-12b": 1.2e10,
}

MODEL_HF_IDS: dict[str, str] = {
    "pythia-1b": "EleutherAI/pythia-1b",
    "pythia-2.8b": "EleutherAI/pythia-2.8b",
    "pythia-6.9b": "EleutherAI/pythia-6.9b",
    "pythia-12b": "EleutherAI/pythia-12b",
}

RANKS: list[int] = [4, 8, 16, 32, 64, 128]
SEEDS: list[int] = [42, 1337, 2024]
TARGET_MODULES: list[str] = ["query_key_value"]


@dataclass
class TrainConfig:
    epochs: int = 3
    lr: float = 1e-4
    batch_size: int = 8
    grad_accum: int = 4
    warmup_steps: int = 100
    max_length: int = 512  # HotpotQA multi-doc context (higher than h-e1's 384)
    lr_scheduler: str = "linear"
    grad_clip: float = 1.0
    gradient_checkpointing: bool = True


@dataclass
class LoRAConfig:
    rank: int = 16
    alpha_multiplier: int = 2
    dropout: float = 0.05
    target_modules: list[str] = field(default_factory=lambda: TARGET_MODULES)


@dataclass
class Paths:
    results_dir: str = "results"
    figures_dir: str = "figures"
    checkpoint_dir: str = "checkpoints"
    rank_sweep_csv: str = "results/h-c1_rank_sweep.csv"
    optimal_ranks_csv: str = "results/h-c1_optimal_ranks.csv"
    scaling_fit_json: str = "results/h-c1_scaling_fit.json"
    comparison_json: str = "results/h-c1_cross_task_comparison.json"
    dual_plot_png: str = "figures/h-c1_dual_scaling_plot.png"
    h_e1_scaling_fit_json: str = "../../h-e1/code/results/h-e1_scaling_fit.json"
    h_e1_optimal_ranks_csv: str = "../../h-e1/code/results/h-e1_optimal_ranks.csv"


@dataclass
class HotpotDataConfig:
    dataset_name: str = "hotpotqa/hotpot_qa"
    dataset_config: str = "distractor"
    max_length: int = 512


@dataclass
class AnalysisConfig:
    n_bootstrap: int = 1000
    alpha_ci: float = 0.95


@dataclass
class ComparisonConfig:
    alpha_diff_threshold: float = 0.15
    require_ci_overlap: bool = True
