"""Experiment configuration for H-E1 (Feedback Ordering Effect)."""
from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    # LLM
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 2048

    # Feedback
    feedback_token_budget: int = 500

    # Repair loop
    n_iterations: int = 3

    # Sandbox
    exec_timeout_s: int = 10
    exec_retries: int = 3

    # Reproducibility
    seed: int = 42

    # Metrics
    bootstrap_resamples: int = 10000
    alpha: float = 0.05
