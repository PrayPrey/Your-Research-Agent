"""
H-M1 Experiment Configuration — Conditional Log-Odds Analysis
"""
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

HE1_CODE_DIR: str = str(Path(__file__).parent.parent.parent / "h-e1" / "code")
HE1_DATA_DIR: str = str(Path(__file__).parent.parent.parent / "h-e1" / "data")
HM1_BASE_DIR: str = str(Path(__file__).parent.parent)

CORPUS_CONFIG_IDS = ["C1", "C2", "C3", "C4", "C5", "C6"]


@dataclass
class HM1Config:
    # H-E1 paths (verified from actual code)
    he1_code_dir: str = HE1_CODE_DIR
    he1_data_dir: str = HE1_DATA_DIR
    fasttext_model_path: str = str(Path(HE1_DATA_DIR) / "models" / "openhermes_reddit_eli5_vs_rw_v2_bigram_200k_train.bin")

    # H-M1 specific
    window_size: int = 10          # matches h-e1 actual value
    alpha: float = 0.5             # Laplace smoothing
    n_bootstrap: int = 1000
    seed: int = 42
    alpha_level: float = 0.05
    filtering_intensities: List[int] = field(default_factory=lambda: [10, 30, 50, 70, 90])
    fasttext_configs: List[str] = field(default_factory=lambda: ["C1", "C2", "C3", "C4", "C5"])
    all_configs: List[str] = field(default_factory=lambda: ["C1", "C2", "C3", "C4", "C5", "C6"])

    # Paths
    data_dir: str = str(Path(HM1_BASE_DIR) / "data")
    figures_dir: str = str(Path(HM1_BASE_DIR) / "figures")
    results_path: str = str(Path(HM1_BASE_DIR) / "results.json")
    validation_path: str = str(Path(HM1_BASE_DIR) / "04_validation.md")
    log_odds_matrix_path: str = str(Path(HM1_BASE_DIR) / "data" / "log_odds_matrix.csv")

    # Visualization
    figure_size: tuple = (10, 6)
    figure_size_heatmap: tuple = (14, 10)
    dpi: int = 150
    bar_color: str = "#4C72B0"
    highlight_color: str = "#DD8452"


def load_config(yaml_path: Optional[str] = None) -> HM1Config:
    """Load config from YAML or return defaults."""
    cfg = HM1Config()
    if yaml_path and Path(yaml_path).exists():
        with open(yaml_path) as f:
            overrides = yaml.safe_load(f) or {}
        for k, v in overrides.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
    return cfg


def get_he1_lexicons() -> Dict[str, List[str]]:
    """Import and return H-E1 occupation_lexicon and demographic_lexicon."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "he1_config", str(Path(HE1_CODE_DIR) / "config.py")
    )
    he1_module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(he1_module)  # type: ignore
    CONFIG = he1_module.CONFIG
    return {
        "occupation_lexicon": CONFIG["occupation_lexicon"],
        "demographic_lexicon": CONFIG["demographic_lexicon"],
    }
