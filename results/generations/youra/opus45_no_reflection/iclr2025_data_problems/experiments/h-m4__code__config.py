"""H-M4 Config: Pareto Curve Analysis - Architecture-Approximation Interaction"""
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ExperimentConfig:
    dataset_name: str = "glue"
    dataset_config: str = "sst2"
    max_length: int = 128
    train_batch_size: int = 32
    epochs: int = 3
    lr: float = 2e-5
    bert_model_id: str = "bert-base-uncased"
    gpt2_model_id: str = "gpt2"
    device: str = "cuda"
    output_dir: str = "."
    figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"
    results_path: str = "results.yaml"
    mislabel_fraction: float = 0.05

    # Multi-seed for statistical testing (reduced for PoC)
    seeds: List[int] = field(default_factory=lambda: [42, 123])

    # Compute budget sweep (proj_dim for EK-FAC/TRAK, checkpoint count for TracIn)
    compute_budgets: List[int] = field(default_factory=lambda: [64, 256, 1024])
    tracin_checkpoint_counts: Dict[int, int] = field(default_factory=lambda: {
        64: 1, 256: 2, 1024: 3
    })

    methods: List[str] = field(default_factory=lambda: ["ekfac", "tracin", "trak"])
    architectures: List[str] = field(default_factory=lambda: ["bert", "gpt2"])

    # Statistical threshold
    alpha: float = 0.05
    trak_invariance_threshold: float = 0.05

    # Sample sizes for attribution computation (PoC-level)
    n_train_sample: int = 500
    n_query_sample: int = 100

    mislabeled_indices_path: str = "mislabeled_indices_seed{seed}.json"

GATE_CONFIG = {
    "type": "SHOULD_WORK",
    "predictions": {
        "P1": "EK-FAC GPT-2 > BERT at matched compute",
        "P2": "TracIn BERT > GPT-2 at matched compute",
        "P3": "TRAK |BERT - GPT-2| < 5%"
    },
    "alpha": 0.05
}

FIGURE_FILES = {
    "pareto_frontier_grid": "pareto_frontier_grid.png",
    "arch_comparison_ekfac": "arch_comparison_ekfac.png",
    "arch_comparison_tracin": "arch_comparison_tracin.png",
    "arch_comparison_trak": "arch_comparison_trak.png",
    "dominance_heatmap": "dominance_heatmap.png",
    "auc_vs_projdim": "auc_vs_projdim.png",
    "auc_bar_fixed_budget": "auc_bar_fixed_budget.png",
}

PLOT_CONFIG = {
    "pareto_grid_shape": (2, 3),
    "figsize": (15, 8),
    "dpi": 150,
    "x_scale": "log",
    "colors": {"bert": "#1f77b4", "gpt2": "#ff7f0e"},
    "fixed_budget_for_bar_chart": 256,
}
