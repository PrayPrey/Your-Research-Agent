from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Config:
    # Models
    model_id_base: str = "meta-llama/Llama-2-7b-hf"
    model_id_chat: str = "meta-llama/Llama-2-7b-chat-hf"
    nli_model_id: str = "cross-encoder/nli-deberta-v3-small"

    # Generation
    K: int = 10
    temperature_sample: float = 0.7
    temperature_greedy: float = 0.0
    max_new_tokens_gen: int = 50
    max_new_tokens_vc: int = 80
    do_sample_vc: bool = False

    # Data
    n_questions: int = 141  # all yes/no-anchored TruthfulQA examples
    dataset_id: str = "truthful_qa"
    dataset_config: str = "generation"
    seed: int = 42

    # Evaluation
    n_bootstrap: int = 1000
    parse_rate_gate: float = 0.70
    batch_size: int = 8

    # Paths
    hm2_code_dir: str = "../../h-m2/code"
    hm4_code_dir: str = "../../h-m4/code"
    hm4_results_path: str = "../../h-m4/results.json"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"

    # Figure settings
    figure_dpi: int = 150
    fig_size_bar: Tuple[int, int] = (8, 5)
    fig_size_cross: Tuple[int, int] = (9, 5)
    fig_size_rank: Tuple[int, int] = (7, 4)
    fig_size_dist: Tuple[int, int] = (8, 4)
    fig_size_violin: Tuple[int, int] = (9, 5)

    # Color palette
    color_se: str = "#55A868"
    color_scg: str = "#8172B2"
    color_te: str = "#DD8452"
    color_vc: str = "#4C72B0"

    # Output filenames
    fname_bar: str = "auroc_comparison.png"
    fname_cross: str = "cross_benchmark_comparison.png"
    fname_rank: str = "rank_ordering.png"
    fname_dist: str = "vc_confidence_distribution.png"
    fname_violin: str = "bootstrap_distributions.png"
