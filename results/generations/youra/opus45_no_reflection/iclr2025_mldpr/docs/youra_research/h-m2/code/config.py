"""Configuration for H-M2 Emergent-Capability Benchmark Analysis."""
from dataclasses import dataclass

POST_2020_THRESHOLD: float = 0.80
GPT3_RELEASE_DATE: str = "2020-06-01"
GPT3_RELEASE_YEAR: int = 2020

PWC_DATASET_ID: str = "pwc-archive/datasets"
PWC_SPLIT: str = "train"

EMERGENT_KEYWORDS: list[str] = [
    "reasoning", "emergent", "capability", "understanding",
    "commonsense", "multi-task", "chain-of-thought", "few-shot",
    "language model", "code generation", "multitask", "multilingual",
    "truthful", "factual", "math reasoning",
]

EMERGENT_BENCHMARK_NAMES: set[str] = {
    "mmlu", "big-bench", "bigbench", "humaneval", "truthfulqa", "gsm8k",
    "math", "arc", "hellaswag", "winogrande", "lambada", "squad",
    "natural-questions", "triviaqa", "codex", "apps", "mbpp",
}

EMERGENT_TASK_TYPES: set[str] = {
    "question-answering", "code-generation", "math-word-problems",
    "reading-comprehension",
}

MIN_EMERGENT_BENCHMARKS: int = 50


@dataclass
class SemanticScholarConfig:
    base_url: str = "https://api.semanticscholar.org/graph/v1"
    rate_limit_per_min: int = 100
    timeout_sec: int = 10
    max_retries: int = 3
    retry_backoff_sec: float = 2.0


@dataclass
class RunConfig:
    max_runtime_min: int = 20
    seed: int = 42
    results_path: str = "results/results.json"
    figures_dir: str = "figures/"


@dataclass
class VizConfig:
    emergent_color: str = "#d62728"
    traditional_color: str = "#1f77b4"
    threshold_line_color: str = "#2ca02c"
    gpt3_marker_color: str = "#7f7f7f"
    figsize: tuple = (10, 6)
    dpi: int = 150
    font_size: int = 11
