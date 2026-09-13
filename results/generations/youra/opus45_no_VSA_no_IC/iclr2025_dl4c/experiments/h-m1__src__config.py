"""Configuration for H-M1 scale ordering experiment."""
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ModelTierConfig:
    tier: Literal["7B", "70B", "proprietary"]
    model_id: str
    backend: Literal["vllm", "openai", "simulated"]
    temperature: float = 0.0
    max_tokens: int = 10
    # Simulated performance profiles from arxiv:2507.16587
    simulated_accuracy: float = 0.5
    simulated_fpr: float = 0.5
    simulated_fnr: float = 0.5


MODEL_TIERS = {
    "7B": ModelTierConfig(
        tier="7B",
        model_id="deepseek-ai/deepseek-coder-7b-instruct",
        backend="simulated",
        simulated_accuracy=0.55,  # Near-random per literature
        simulated_fpr=0.75,  # High false positive rate (over-accepts)
        simulated_fnr=0.13,  # Low false negative rate
    ),
    "70B": ModelTierConfig(
        tier="70B",
        model_id="meta-llama/CodeLlama-70b-Instruct-hf",
        backend="simulated",
        simulated_accuracy=0.68,  # Moderate improvement
        simulated_fpr=0.65,  # Reduced FPR
        simulated_fnr=0.22,  # Increased FNR (more conservative)
    ),
    "proprietary": ModelTierConfig(
        tier="proprietary",
        model_id="gpt-4-turbo",
        backend="simulated",
        simulated_accuracy=0.73,  # Best but diminishing returns
        simulated_fpr=0.60,  # Lowest FPR
        simulated_fnr=0.29,  # Highest FNR (most conservative)
    ),
}


@dataclass
class EvalConfig:
    dataset: str = "humaneval_plus"
    seed: int = 42
    n_problems: int = 164  # Full HumanEval+ set
    alpha: float = 0.05
    prompt_template: str = (
        "Given the following Python function and its specification, "
        "determine if the implementation is correct.\n\n"
        "Function:\n{code}\n\nSpecification:\n{prompt}\n\n"
        "Is this implementation correct? Answer only 'correct' or 'incorrect'."
    )


@dataclass
class ExperimentConfig:
    models: dict = field(default_factory=lambda: MODEL_TIERS)
    eval: EvalConfig = field(default_factory=EvalConfig)
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    scales_order: list = field(default_factory=lambda: ["7B", "70B", "proprietary"])
