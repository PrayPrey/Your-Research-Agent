"""H-M2 Configuration: Corpus Entropy → Model Logit Margin Internalization."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

HM1_CODE_DIR: str = str(Path(__file__).parent.parent.parent / "h-m1" / "code")
HE1_DATA_DIR: str = str(Path(__file__).parent.parent.parent / "h-e1" / "data" / "corpora")
HM2_BASE_DIR: str = str(Path(__file__).parent.parent)

ALL_CONFIGS: List[str] = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]

CORPUS_H_ENTROPY: Dict[str, float] = {
    "C0": 3.2662,
    "C1": 3.2702,
    "C2": 3.2528,
    "C3": 3.2275,
    "C4": 3.1106,
    "C5": 2.5374,
    "C6": 3.2209,
    "C7": 3.2275,  # shuffled-demographic, same entropy as C3
}


@dataclass
class HM2Config:
    # Inherited path references
    hm1_code_dir: str = HM1_CODE_DIR
    he1_data_dir: str = HE1_DATA_DIR
    hm2_base_dir: str = HM2_BASE_DIR

    # Derived paths
    tokenized_dir: str = str(Path(HM2_BASE_DIR) / "data" / "tokenized")
    checkpoints_dir: str = str(Path(HM2_BASE_DIR) / "checkpoints")
    configs_dir: str = str(Path(HM2_BASE_DIR) / "configs")
    results_dir: str = str(Path(HM2_BASE_DIR) / "results")
    figures_dir: str = str(Path(HM2_BASE_DIR) / "figures")
    probe_templates_path: str = str(Path(HM2_BASE_DIR) / "data" / "probe_templates.json")
    results_path: str = str(Path(HM2_BASE_DIR) / "results" / "results.json")
    validation_path: str = str(Path(HM2_BASE_DIR) / "04_validation.md")

    # Pythia-1B architecture (fixed, do not tune)
    hidden_size: int = 2048
    num_layers: int = 16
    num_attention_heads: int = 8
    vocab_size: int = 50304
    max_seq_len: int = 2048

    # Training hyperparameters (fixed per H-PCFH-v1)
    global_batch_size: int = 256
    lr: float = 2e-5
    train_iters_full: int = 190735   # 100B tokens
    train_iters_quick: int = 95368   # 50B tokens (PoC gate)
    seed: int = 42

    # AdamW optimizer (fixed)
    adam_beta1: float = 0.9
    adam_beta2: float = 0.95
    adam_eps: float = 1e-8
    weight_decay: float = 0.1
    warmup_fraction: float = 0.01   # 1% warmup for cosine decay

    # Probe configuration
    n_probe_templates: int = 50              # minimum templates per demographic axis
    n_occupation_pairs: int = 20             # WinoBias occupation categories
    logit_margin_sanity_bound: float = 10.0  # |margin| must be < 10.0

    # Statistical gate (tightened from H-M1's 0.05)
    alpha_level: float = 0.01
    negative_control_delta_threshold: float = 0.01  # |C7 - C0| <= 0.01
    n_bootstrap: int = 1000

    # Scale robustness (Pythia-160M check)
    scale_check_configs: List[str] = field(
        default_factory=lambda: ["C1", "C3", "C5"]
    )

    # Visualization (inherited from H-M1)
    dpi: int = 150
    figure_size: tuple = (10, 6)
    figure_size_heatmap: tuple = (14, 10)


def load_config(yaml_path: Optional[str] = None) -> HM2Config:
    """Load config from YAML overrides or return defaults."""
    cfg = HM2Config()
    if yaml_path and Path(yaml_path).exists():
        with open(yaml_path) as f:
            overrides = yaml.safe_load(f) or {}
        for k, v in overrides.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
    return cfg
