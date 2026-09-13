"""Configuration schema for h-e1 proxy metric validation experiment."""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class DatasetConfig:
    """HumanEval dataset loading and problem selection."""
    name: str = "HumanEval"
    source: str = "openai/openai_humaneval"
    problem_count: int = 50
    problem_selection_seed: int = 42
    cache_dir: Optional[str] = "./data/humaneval/"
    stratify: bool = True


@dataclass
class ModelConfig:
    """CodeLlama-7B-Instruct inference settings."""
    name: str = "meta-llama/CodeLlama-7b-Instruct-hf"
    dtype: str = "float16"
    device_map: str = "auto"
    cache_dir: Optional[str] = "./models/codellama-7b-instruct/"


@dataclass
class GenerationConfig:
    """Solution generation parameters."""
    temperature: float = 0.8
    top_p: float = 0.95
    max_new_tokens: int = 512
    num_solutions_per_problem: int = 10
    do_sample: bool = True
    seed: int = 42


@dataclass
class CodeBLEUConfig:
    """CodeBLEU metric settings."""
    lang: str = "python"
    weights: Tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25)


@dataclass
class RuntimeConfig:
    """Runtime efficiency measurement."""
    tool: str = "perf"
    event: str = "instructions"
    repetitions: int = 5
    timeout: int = 3


@dataclass
class PRStyleConfig:
    """PR-style placeholder metric."""
    implementation: str = "placeholder"
    seed: int = 42


@dataclass
class ThresholdConfig:
    """Gate validation thresholds."""
    cv_max: float = 5.0
    cohens_d_min: float = 0.8
    spearman_rho_min: float = 0.8


@dataclass
class ControlledTaskConfig:
    """Synthetic complexity class dataset."""
    num_problems: int = 50
    complexity_classes: Tuple[str, str, str] = ("O(n)", "O(n log n)", "O(n²)")
    problems_per_class: int = 17
    test_input_size: int = 1000


@dataclass
class VisualizationConfig:
    """Figure generation settings."""
    output_dir: str = "./figures/"
    dpi: int = 300
    format: str = "png"
    style: str = "seaborn-v0_8-darkgrid"
    figsize: Tuple[int, int] = (10, 6)


@dataclass
class ExperimentConfig:
    """Master configuration for h-e1."""
    hypothesis_id: str = "h-e1"
    experiment_name: str = "proxy_metric_validation"
    seed: int = 42

    dataset: DatasetConfig = None
    model: ModelConfig = None
    generation: GenerationConfig = None
    codebleu: CodeBLEUConfig = None
    runtime: RuntimeConfig = None
    pr_style: PRStyleConfig = None
    thresholds: ThresholdConfig = None
    controlled_tasks: ControlledTaskConfig = None
    visualization: VisualizationConfig = None

    verbose: bool = True
    checkpoint_interval: int = 10

    def __post_init__(self):
        if self.dataset is None:
            self.dataset = DatasetConfig()
        if self.model is None:
            self.model = ModelConfig()
        if self.generation is None:
            self.generation = GenerationConfig()
        if self.codebleu is None:
            self.codebleu = CodeBLEUConfig()
        if self.runtime is None:
            self.runtime = RuntimeConfig()
        if self.pr_style is None:
            self.pr_style = PRStyleConfig()
        if self.thresholds is None:
            self.thresholds = ThresholdConfig()
        if self.controlled_tasks is None:
            self.controlled_tasks = ControlledTaskConfig()
        if self.visualization is None:
            self.visualization = VisualizationConfig()


def validate_config(config: ExperimentConfig) -> None:
    """Validate configuration constraints."""
    assert config.dataset.problem_count > 0
    assert config.dataset.problem_selection_seed >= 0
    assert 0 < config.generation.temperature <= 2.0
    assert 0 < config.generation.top_p <= 1.0
    assert config.generation.max_new_tokens > 0
    assert config.generation.num_solutions_per_problem > 0
    assert len(config.codebleu.weights) == 4
    assert abs(sum(config.codebleu.weights) - 1.0) < 1e-6
    assert config.runtime.repetitions > 0
    assert config.runtime.timeout > 0
    assert config.thresholds.cv_max > 0
    assert config.thresholds.cohens_d_min > 0
    assert 0 <= config.thresholds.spearman_rho_min <= 1.0
    assert config.controlled_tasks.num_problems > 0
    assert config.visualization.dpi > 0
    print("Configuration validation passed.")


# Default configuration instance
CONFIG = ExperimentConfig()
