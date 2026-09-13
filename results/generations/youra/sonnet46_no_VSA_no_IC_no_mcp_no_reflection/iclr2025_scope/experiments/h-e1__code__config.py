from dataclasses import dataclass, field
import torch


@dataclass
class ExperimentConfig:
    model_name: str = "state-spaces/mamba-130m-hf"
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: tuple = ("in_proj", "out_proj", "x_proj")
    max_length: int = 128
    batch_size: int = 32
    epochs: int = 3
    lr: float = 3e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.06
    seed: int = 42
    tasks: tuple = ("sst2", "mnli", "qnli", "qqp")
    results_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"
    device: str = field(
        default_factory=lambda: "cuda" if torch.cuda.is_available() else "cpu"
    )

    def __post_init__(self):
        assert "conv1d" not in self.target_modules, \
            "conv1d cannot be a LoRA target on Mamba"
