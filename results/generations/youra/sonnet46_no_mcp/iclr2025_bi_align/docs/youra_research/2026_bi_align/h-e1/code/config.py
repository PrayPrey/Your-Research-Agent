from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import yaml


@dataclass
class DataConfig:
    hh_rlhf_dataset: str = "Anthropic/hh-rlhf"
    webgpt_dataset: str = "openai/webgpt_comparisons"
    cache_dir: str = "./data/cache"
    n_rounds: int = 3
    min_round1_size: int = 10000
    coverage_threshold: float = 0.80


@dataclass
class FeatureConfig:
    hedging_phrases: List[str] = field(default_factory=lambda: [
        "i think", "i believe", "perhaps", "possibly", "might", "may",
        "could", "probably", "seems", "appears", "arguably", "likely",
        "uncertain", "not sure", "unclear", "i'm not certain",
    ])
    structure_markers: List[str] = field(default_factory=lambda: [
        "\n-", "\n*", "1.", "2.", "3.", "##", "**",
        "first,", "second,", "third,", "finally,",
        "in conclusion,", "to summarize,", "in summary,",
    ])
    vif_threshold: float = 10.0
    vif_warn_threshold: float = 5.0
    scaler_type: str = "standard"


@dataclass
class QEarlyConfig:
    lr_params: Dict[str, Any] = field(default_factory=lambda: {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
        "class_weight": "balanced",
        "random_state": 42,
    })
    calibration_method: str = "sigmoid"
    brier_gate_threshold: float = 0.02


@dataclass
class AnalysisConfig:
    bootstrap_iters: int = 1000
    permutation_iters: int = 1000
    alpha: float = 0.05
    bonferroni_k: int = 3
    alpha_corrected: float = 0.0167
    fleiss_kappa_threshold: float = 0.4
    min_high_ambiguity_samples: int = 500
    random_seed: int = 42


@dataclass
class OutputConfig:
    figures_dir: str = "../figures"
    results_file: str = "../experiment_results.json"
    log_level: str = "INFO"


@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    q_early: QEarlyConfig = field(default_factory=QEarlyConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    random_seed: int = 42
    n_rounds: int = 3


# Module-level constants (for import convenience)
HH_RLHF_DATASET = "Anthropic/hh-rlhf"
WEBGPT_DATASET = "openai/webgpt_comparisons"
N_ROUNDS = 3
BOOTSTRAP_ITERS = 200
PERMUTATION_ITERS = 200
ALPHA = 0.05
BONFERRONI_K = 3
ALPHA_CORRECTED = 0.0167
BRIER_GATE_THRESHOLD = 0.02
FIGURES_DIR = "../figures"
RANDOM_SEED = 42
LR_PARAMS = {
    "C": 1.0,
    "max_iter": 1000,
    "solver": "lbfgs",
    "class_weight": "balanced",
    "random_state": 42,
}
HEDGE_WORDS = [
    "i think", "i believe", "perhaps", "possibly", "might", "may",
    "could", "probably", "seems", "appears", "arguably", "likely",
    "uncertain", "not sure", "unclear", "i'm not certain",
]
STRUCT_MARKERS = [
    "\n-", "\n*", "1.", "2.", "3.", "##", "**",
    "first,", "second,", "third,", "finally,",
    "in conclusion,", "to summarize,", "in summary,",
]


def load_config(config_path: Optional[str] = None) -> ExperimentConfig:
    if config_path is None:
        return ExperimentConfig()
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)
    cfg = ExperimentConfig()
    if "random_seed" in raw:
        cfg.random_seed = raw["random_seed"]
    if "n_rounds" in raw:
        cfg.n_rounds = raw["n_rounds"]
    if "data" in raw:
        cfg.data = DataConfig(**{k: v for k, v in raw["data"].items()
                                 if k in DataConfig.__dataclass_fields__})
    if "features" in raw:
        cfg.features = FeatureConfig(**{k: v for k, v in raw["features"].items()
                                        if k in FeatureConfig.__dataclass_fields__})
    if "q_early" in raw:
        cfg.q_early = QEarlyConfig(**{k: v for k, v in raw["q_early"].items()
                                      if k in QEarlyConfig.__dataclass_fields__})
    if "analysis" in raw:
        cfg.analysis = AnalysisConfig(**{k: v for k, v in raw["analysis"].items()
                                         if k in AnalysisConfig.__dataclass_fields__})
    if "output" in raw:
        cfg.output = OutputConfig(**{k: v for k, v in raw["output"].items()
                                     if k in OutputConfig.__dataclass_fields__})
    return cfg
