from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

MODEL_CONFIGS: dict[str, dict] = {
    "bert-base-uncased": {
        "task": "mnli",
        "num_labels": 3,
        "target_modules": ["query", "key", "value", "dense"],
    },
    "microsoft/deberta-v3-base": {
        "task": "mnli",
        "num_labels": 3,
        "target_modules": ["query_proj", "key_proj", "value_proj", "pos_proj"],
    },
    "google/vit-base-patch16-224": {
        "task": "cifar10",
        "num_labels": 10,
        "target_modules": ["query", "key", "value", "dense"],
    },
}

ORACLE_RANKS: list[int] = [4, 8, 16, 32, 64]
BASELINE_RANK: int = 8
SEEDS: list[int] = [42, 137]


@dataclass
class ExperimentConfig:
    model_name: str = "bert-base-uncased"

    output_dir: Path = Path("docs/youra_research/h-e1")
    results_dir: Path = Path("docs/youra_research/h-e1/results")
    figures_dir: Path = Path("docs/youra_research/h-e1/figures")
    checkpoint_dir: Path = Path("docs/youra_research/h-e1/checkpoints")

    epochs_nlp: int = 1
    batch_size_nlp: int = 32
    lr_nlp: float = 2e-5

    epochs_vit: int = 2
    batch_size_vit: int = 128
    lr_vit: float = 1e-4

    # ponytail: PoC layer sampling — sweep subset of layers (every N-th) to demonstrate correlation
    # Full sweep (layer_sample_step=1) takes ~200+ hours on shared H100.
    # With step=4, ~18 layers/model gives statistically valid N for Pearson r test.
    layer_sample_step: int = 4

    # ponytail: PoC dataset subsampling — full MNLI (393K) takes ~90min/run under GPU contention.
    # 2000 train + 1000 val gives stable rank ordering at fraction of the cost.
    max_train_samples: int = 2000
    max_val_samples: int = 1000

    weight_decay: float = 0.01
    warmup_ratio: float = 0.06
    max_length: int = 128

    oracle_ranks: list = field(default_factory=lambda: list(ORACLE_RANKS))
    baseline_rank: int = BASELINE_RANK
    seeds: list = field(default_factory=lambda: list(SEEDS))

    fp32_models: tuple = ("microsoft/deberta-v3-base",)

    svd_threshold: float = 1e-10
    pearson_threshold: float = 0.65
    p_threshold: float = 0.05
    n_bootstrap: int = 1000
    bootstrap_seed: int = 42
    pr_enabled: bool = True
    success_families_required: int = 2

    @classmethod
    def from_model(cls, model_name: str, base_dir: Path) -> "ExperimentConfig":
        base_dir = Path(base_dir)
        return cls(
            model_name=model_name,
            output_dir=base_dir,
            results_dir=base_dir / "results",
            figures_dir=base_dir / "figures",
            checkpoint_dir=base_dir / "checkpoints",
        )
