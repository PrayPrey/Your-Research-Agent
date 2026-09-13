from dataclasses import dataclass, field
from typing import List


@dataclass
class StatTestConfig:
    n_resamples: int = 10000
    random_state: int = 42
    significance_threshold: float = 0.05
    alternative: str = "greater"
    bootstrap_n: int = 1000
    min_rank_variation: int = 2
    ci_percentiles: List[float] = field(default_factory=lambda: [2.5, 97.5])


@dataclass
class PathConfig:
    h_e1_results: str = "docs/youra_research/h-e1/experiment_results.json"
    h_e2_csv: str = "docs/youra_research/h-e2/results/all_results.csv"
    h_c1_json: str = "docs/youra_research/h-c1/results/pass_at_1_7b.json"
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    null_dist_dir: str = "docs/youra_research/h-m2/results/null_distributions"


@dataclass
class VizConfig:
    dpi: int = 150
    fig1_size: tuple = (10, 5)
    fig2_size: tuple = (14, 8)
    fig3_size: tuple = (8, 5)
    fig4_size: tuple = (8, 6)
    fig5_size: tuple = (6, 6)
    condition_colors: List[str] = field(default_factory=lambda: [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    ])
    significance_marker: str = "*"
    significance_fontsize: int = 14


@dataclass
class ExperimentConfig:
    source_conditions: List[str] = field(default_factory=lambda: [
        "humaneval_only", "mbpp_only", "leetcode_only", "equal_mix",
    ])
    h_e1_source_keys: List[str] = field(default_factory=lambda: [
        "humaneval_train", "mbpp_train", "leetcode", "equal_mix",
    ])
    benchmarks: List[str] = field(default_factory=lambda: [
        "humaneval_plus", "mbpp_plus",
    ])
    h_e2_benchmark_keys: List[str] = field(default_factory=lambda: [
        "humaneval", "mbpp_plus",
    ])
    encoders: List[str] = field(default_factory=lambda: ["codebert", "minilm"])
    model_sizes: List[str] = field(default_factory=lambda: ["1b"])
    stat: StatTestConfig = field(default_factory=StatTestConfig)
    viz: VizConfig = field(default_factory=VizConfig)
    paths: PathConfig = field(default_factory=PathConfig)


CFG = ExperimentConfig()
