"""Configuration for H-M4: Bidirectional Tasks Show Miscalibrated Confidence."""

from dataclasses import dataclass


@dataclass
class H_M4_Config:
    # Paths
    e1_results_path: str = "../../h-e1/code/outputs/results.json"
    output_dir: str = "outputs"
    results_path: str = "outputs/results.json"
    figures_dir: str = "../figures"

    # Feature keyword lists (FR-2)
    belief_markers: tuple = (
        "you think", "you believe", "your view", "your opinion",
        "you feel", "you assume", "you expect"
    )
    context_markers: tuple = (
        "in this context", "given that", "assuming",
        "depending on", "it depends", "situation"
    )
    hedge_markers: tuple = (
        "might be", "could be", "possibly", "sometimes",
        "it varies", "not always", "generally"
    )

    # Gate thresholds
    r_threshold: float = 0.4
    d_threshold: float = 0.3
    partial_r_threshold: float = 0.3

    seed: int = 42
