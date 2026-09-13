"""
Configuration module for H-E1 Structural Enumeration Preference experiment.

Defines dataclass configs for stimulus generation, inference, and experiment orchestration.
"""

from dataclasses import dataclass, field
from typing import List
from pathlib import Path


MODEL_IDS = {
    "armo": "RLHFlow/ArmoRM-Llama3-8B-v0.1",
    "ultra": "openbmb/UltraRM-13b",
    "starling": "berkeley-nest/Starling-RM-7B-alpha",
    "pairrm": "llm-blender/PairRM",
}


@dataclass
class StimulusConfig:
    """Configuration for stimulus generation."""
    n_prompts: int = 75
    factors: List[str] = field(default_factory=lambda: ["structure", "correctness", "completeness"])
    length_tolerance: float = 0.02  # ±2% length match across structure conditions
    seed: int = 42


@dataclass
class InferenceConfig:
    """Configuration for reward model inference."""
    batch_size: int = 16
    device: str = "cuda"
    dtype: str = "bfloat16"
    use_4bit: bool = False  # Set True if VRAM < 16GB (UltraRM-13b fallback)


@dataclass
class GateConfig:
    """Configuration for gate condition checking."""
    d_threshold: float = 0.3  # Minimum Cohen's d for gate pass
    min_models: int = 2  # Minimum RMs that must exceed threshold
    alpha: float = 0.05  # Significance level for paired t-test
    ci_coverage: float = 0.95  # CI coverage for effect size intervals


@dataclass
class ExperimentConfig:
    """Main experiment configuration."""
    stimulus: StimulusConfig = field(default_factory=StimulusConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    rm_ids: List[str] = field(default_factory=lambda: ["armo", "ultra", "starling", "pairrm"])
    resume: bool = True  # Resume from checkpoint if intermediate files exist

    def validate(self) -> None:
        """Validate configuration and create output directories."""
        assert self.stimulus.n_prompts > 0, "n_prompts must be positive"
        assert 0.0 < self.stimulus.length_tolerance < 0.1, "length_tolerance must be in (0, 0.1)"
        assert self.inference.batch_size > 0, "batch_size must be positive"
        for rm in self.rm_ids:
            assert rm in MODEL_IDS, f"Unknown RM key: {rm}. Must be one of {list(MODEL_IDS.keys())}"

        # Create output directories
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.figures_dir).mkdir(parents=True, exist_ok=True)


def get_default_config() -> ExperimentConfig:
    """Return default experiment configuration."""
    cfg = ExperimentConfig()
    cfg.validate()
    return cfg
