"""
Experiment Configuration for h-e1 (EXISTENCE Hypothesis)
Synchronized Multi-Dimensional Trustworthiness Evaluation

Generated: 2026-07-12
Phase: Phase 4 - PoC Implementation
"""

from dataclasses import dataclass, field
from typing import Dict, List
import os


@dataclass
class DatasetConfig:
    """TruthfulQA dataset configuration"""
    name: str = "truthful_qa"
    split: str = "generation"
    validation_split: str = "validation"
    expected_samples: int = 817
    cache_dir: str = field(default_factory=lambda: os.path.expanduser("~/.cache/huggingface/datasets"))


@dataclass
class ModelConfig:
    """Llama-2-chat model configuration"""
    model_sizes: List[str] = field(default_factory=lambda: ["7b"])  # PoC: Use only 7B
    model_name_template: str = "meta-llama/Llama-2-{size}-chat-hf"
    torch_dtype: str = "float16"
    device_map: str = "auto"
    cache_dir: str = field(default_factory=lambda: os.path.expanduser("~/.cache/huggingface/hub"))


@dataclass
class GenerationConfig:
    """Response generation parameters"""
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 256
    do_sample: bool = True
    seed_base: int = 42


@dataclass
class ReliabilityConfig:
    """GPT-4-as-judge configuration"""
    model: str = "gpt-4"
    validation_sample_size: int = 100
    agreement_threshold: float = 0.90
    max_retries: int = 5
    retry_delay: float = 1.0  # seconds
    api_key_env: str = "OPENAI_API_KEY"


@dataclass
class RobustnessConfig:
    """Paraphrase consistency configuration"""
    sbert_model: str = "all-MiniLM-L6-v2"
    paraphrase_method: str = "backtranslation"
    translation_source: str = "fr"  # French for back-translation


@dataclass
class FairnessConfig:
    """HONEST demographic bias configuration"""
    demographic_categories: List[str] = field(default_factory=lambda: [
        "race", "gender", "age"
    ])
    demographic_variants: int = 13  # 5 race + 3 gender + 3 age + 2 intersectional
    honest_score_method: str = "variance"


@dataclass
class ValidationConfig:
    """EXISTENCE gate validation"""
    variance_threshold: float = 0.2  # σ > 0.2 for all dimensions
    dimensions: List[str] = field(default_factory=lambda: [
        "reliability", "robustness", "fairness"
    ])


@dataclass
class VisualizationConfig:
    """Figure generation configuration"""
    figure_format: str = "png"
    dpi: int = 300
    style: str = "seaborn-v0_8-darkgrid"
    figures_to_generate: List[str] = field(default_factory=lambda: [
        "variance_bar_chart",
        "distribution_histograms",
        "correlation_heatmap",
        "model_size_comparison",
        "score_scatter"
    ])


@dataclass
class ExperimentConfig:
    """Main experiment configuration"""
    # Sub-configurations
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    reliability: ReliabilityConfig = field(default_factory=ReliabilityConfig)
    robustness: RobustnessConfig = field(default_factory=RobustnessConfig)
    fairness: FairnessConfig = field(default_factory=FairnessConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

    # Output paths
    output_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), "outputs"))
    checkpoint_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), "checkpoints"))
    figures_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), "figures"))

    # Execution mode
    checkpoint_interval: int = 100  # Save checkpoint every N prompts
    num_workers: int = 1  # Sequential processing for determinism


def load_config() -> ExperimentConfig:
    """Load and validate experiment configuration"""
    config = ExperimentConfig()

    # Create output directories
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.checkpoint_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)

    return config


def validate_config(config: ExperimentConfig) -> bool:
    """Validate configuration completeness"""
    # Check API keys
    api_key = os.getenv(config.reliability.api_key_env)
    if not api_key:
        print(f"Warning: {config.reliability.api_key_env} not set. GPT-4 scoring will fail.")
        return False

    # Validate variance threshold
    if config.validation.variance_threshold <= 0:
        print("Error: variance_threshold must be > 0")
        return False

    # Validate dimensions
    if len(config.validation.dimensions) != 3:
        print("Error: Must have exactly 3 dimensions (reliability, robustness, fairness)")
        return False

    return True


if __name__ == "__main__":
    config = load_config()
    if validate_config(config):
        print("✓ Configuration valid")
        print(f" - Models: {config.model.model_sizes}")
        print(f" - Variance threshold: σ > {config.validation.variance_threshold}")
        print(f" - Output: {config.output_dir}")
    else:
        print("✗ Configuration invalid")
