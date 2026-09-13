from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class FeatureProbeConfig:
    batch_size: int = 128
    seed: int = 42
    epochs_waterbirds: int = 100
    data_root: str = "/home/PrayPrey/.wilds_cache"

    h_m1_checkpoint_dir: str = "../../h-m1/code/checkpoints"
    checkpoint_pattern: str = "waterbirds_epoch{epoch}.pt"

    crystallization_epoch: int = 5
    final_epoch: int = 13
    checkpoint_stride: int = 1

    feature_layer: str = "avgpool"
    feature_dim: int = 2048

    probe_lr: float = 0.01
    probe_iterations: int = 100

    noise_margin: float = 0.02
    core_suppression_threshold: float = 0.85

    output_dir: str = "./outputs"
    figures_dir: str = "../figures"
    results_file: str = "probe_results.yaml"

    def get_checkpoint_path(self, epoch: int) -> str:
        return str(Path(self.h_m1_checkpoint_dir) / self.checkpoint_pattern.format(epoch=epoch))

    def get_analysis_epochs(self) -> list:
        return list(range(self.crystallization_epoch, self.final_epoch + 1, self.checkpoint_stride))

CONFIG = FeatureProbeConfig()
