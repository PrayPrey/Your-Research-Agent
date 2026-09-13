from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class ExperimentConfig:
    seed: int = 1
    batch_size: int = 8
    n_bins_primary: int = 15
    n_bins_secondary: int = 10
    min_examples_per_cell: int = 50  # lowered: AdvGLUE splits are small (78-148 examples)
    subsample_clean: int = 200
    subsample_adv: int = 200  # cap for CPU feasibility; still above min_examples_per_cell=50
    prevalidation_n: int = 10

    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
    ])
    use_4bit_threshold_gb: float = 40.0

    max_confidence_degenerate: float = 0.999
    non_degenerate_fraction: float = 0.90
    min_confidence_uniform: float = 0.30  # uniform over 3 choices = 0.33, lower threshold for NLI
    prob_sum_tolerance: float = 1e-3
    ece_plausible_min: float = 0.0
    ece_plausible_max: float = 0.5

    clean_ece_min: float = 0.05
    clean_ece_max: float = 0.15
    min_models_sanity: int = 1  # relaxed for single-model pilot run

    gate_min_cells: int = 1  # existence gate: ≥1 adversarial cell with ECE > clean

    task_split_map: Dict[str, Tuple[str, str]] = field(default_factory=lambda: {
        "qqp":  ("glue_qqp",  "advglue_qqp"),
        "sst2": ("glue_sst2", "advglue_sst2"),
        "nli":  ("mnli",      "advglue_mnli"),
    })
    anli_splits: List[str] = field(default_factory=lambda: ["anli_r1", "anli_r2", "anli_r3"])

    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    errors_log: str = "docs/youra_research/h-e1/results/errors.log"
