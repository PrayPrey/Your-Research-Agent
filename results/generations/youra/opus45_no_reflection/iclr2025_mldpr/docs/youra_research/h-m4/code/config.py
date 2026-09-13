# H-M4 Configuration: Traditional Benchmark Persistence with Reduced Dominance

TRADITIONAL_BENCHMARKS: list[str] = ["imagenet", "imagenet-1k", "cifar-10", "cifar-100"]

SPLIT_DATE: str = "2020-01"
DATE_RANGE: tuple[str, str] = ("2018-01", "2024-12")

# Gate thresholds
COUNT_RATIO_BOUNDS: tuple[float, float] = (0.8, 1.2)
PER_BENCHMARK_STABILITY_BOUND: float = 0.30
SIGNIFICANCE_ALPHA: float = 0.05

SEED: int = 42

HF_DATASETS = {
    "eval_tables": "pwc-archive/evaluation-tables",
    "datasets_meta": "pwc-archive/datasets",
}

OUTPUT_DIR: str = "../figures/"
RESULTS_PATH: str = "results.yaml"

# Visualization config
FIGURE_SIZE: tuple[int, int] = (10, 6)
DPI: int = 150

COLORS = {
    "traditional": "#d62728",
    "emergent": "#1f77b4",
    "pre_2020": "#7f7f7f",
    "post_2020": "#2ca02c",
    "split_line": "#000000",
}

PER_BENCHMARK_COLORS = {
    "imagenet": "#1f77b4",
    "imagenet-1k": "#ff7f0e",
    "cifar-10": "#2ca02c",
    "cifar-100": "#d62728",
}

FIGURE_FILES = {
    "gate_metrics": "gate_metrics.png",
    "share_timeseries": "share_timeseries.png",
    "stacked_area": "stacked_area.png",
    "per_benchmark": "per_benchmark.png",
}
