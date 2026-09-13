"""Configuration for H-C1: Feedback Diversity CONDITION Test."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    # Model
    model_id: str = "Salesforce/codet5p-220m"
    lora_r: int = 16
    lora_alpha: int = 32
    lora_target_modules: list = field(default_factory=lambda: ["q", "v"])
    lora_dropout: float = 0.1

    # CE training
    lr: float = 5e-5  # CodeRL default (differs from H-E1's 2e-5)
    weight_decay: float = 0.05
    warmup_steps: int = 200
    batch_size: int = 8
    ce_epochs: int = 10

    # RL training
    rl_epochs: int = 5
    rl_lr: float = 1e-5

    # Self-refine inference
    refine_k: int = 3
    max_new_tokens: int = 512
    temperature: float = 0.8

    # Diversity thresholds (bits)
    diversity_high_threshold: float = 2.5
    diversity_low_threshold: float = 1.5
    error_types: int = 4  # CompileError, RuntimeError, FailedTest, PassedTest

    # Conditions
    diversity_modes: list = field(default_factory=lambda: ["high", "low"])
    refine_modes: list = field(default_factory=lambda: ["refine", "single"])

    # Reproducibility
    seed: int = 42

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    @property
    def cache_dir(self) -> Path:
        # Share cache with H-E1
        h_e1_cache = self.base_dir.parent / "h-e1" / "data_cache"
        if h_e1_cache.exists():
            return h_e1_cache
        return self.base_dir / "data_cache"

    @property
    def checkpoint_dir(self) -> Path:
        return self.base_dir / "checkpoints"

    @property
    def figures_dir(self) -> Path:
        return self.base_dir / "figures"

    @property
    def outputs_dir(self) -> Path:
        return self.base_dir / "code" / "outputs"

    def __post_init__(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
