"""Configuration for H-M3: Researcher Attention Shift experiment."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class BenchmarkConfig:
    emergent: list[str] = field(default_factory=lambda: [
        "MMLU", "BIG-Bench", "HumanEval", "GSM8K", "MATH",
        "ARC", "HellaSwag", "WinoGrande", "TruthfulQA", "LAMBADA",
    ])
    traditional: list[str] = field(default_factory=lambda: [
        "ImageNet", "CIFAR-10", "CIFAR-100", "MNIST",
        "SQuAD", "GLUE", "CoNLL", "Penn Treebank",
    ])
    time_range: tuple[str, str] = ("2018-01", "2024-12")
    split_date: str = "2021-01"
    ablation_splits: list[str] = field(default_factory=lambda: ["2020-01", "2021-01", "2022-01"])

    def __post_init__(self):
        overlap = set(self.emergent) & set(self.traditional)
        if overlap:
            raise ValueError(f"Benchmark(s) in both categories: {overlap}")


@dataclass
class DataConfig:
    retries: int = 3
    backoff_base_seconds: float = 2.0
    pwc_api_base_url: str = "https://paperswithcode.com/api/v1/"
    hf_fallback_dataset: str = "pwc-archive/datasets"
    seed: int = 42


@dataclass
class AnalysisConfig:
    chi_square_alpha: float = 0.05
    period_labels: tuple[str, str] = ("pre_2021", "post_2021")


@dataclass
class VisualizationConfig:
    figsize_default: tuple[int, int] = (10, 6)
    figsize_heatmap: tuple[int, int] = (14, 8)
    dpi: int = 150
    style: str = "seaborn-v0_8-whitegrid"
    palette_emergent: str = "#d62728"
    palette_traditional: str = "#1f77b4"
    heatmap_top_n: int = 20
    output_dir: str = "figures/"
    file_format: Literal["png", "pdf", "svg"] = "png"


@dataclass
class ExperimentConfig:
    benchmarks: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    data: DataConfig = field(default_factory=DataConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    viz: VisualizationConfig = field(default_factory=VisualizationConfig)
    results_path: str = "results.json"


EMERGENT_BENCHMARKS = BenchmarkConfig().emergent
TRADITIONAL_BENCHMARKS = BenchmarkConfig().traditional
TIME_RANGE = ("2018-01", "2024-12")
SPLIT_DATE = "2021-01"
PRE_POST_SPLITS = ["2020-01", "2021-01", "2022-01"]
