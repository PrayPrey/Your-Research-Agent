# h-m1/code/config.py
# H-M1: Automation-Bias-Mediated Ambiguity-Modulated AI-Norm Internalization
# Extends H-E1 config — field names verified from h-e1/code/config.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

# ---------------------------------------------------------------------------
# Inherited from H-E1 (verified from h-e1/code/config.py)
# ---------------------------------------------------------------------------

HH_RLHF_DATASET: str = "Anthropic/hh-rlhf"
WEBGPT_DATASET: str = "openai/webgpt_comparisons"
N_ROUNDS: int = 3
BOOTSTRAP_ITERS: int = 1000
PERMUTATION_ITERS: int = 1000
RANDOM_SEED: int = 42
BONFERRONI_K: int = 3
ALPHA_CORRECTED: float = 0.0167
BRIER_GATE_THRESHOLD: float = 0.02
LR_PARAMS: Dict[str, Any] = {
    "C": 1.0,
    "max_iter": 1000,
    "solver": "lbfgs",
    "class_weight": "balanced",
    "random_state": 42,
}
HEDGE_WORDS: List[str] = [
    "i think", "i believe", "perhaps", "possibly", "might", "may",
    "could", "probably", "seems", "appears", "arguably", "likely",
    "uncertain", "not sure", "unclear", "i'm not certain",
]
STRUCT_MARKERS: List[str] = [
    "\n-", "\n*", "1.", "2.", "3.", "##", "**",
    "first,", "second,", "third,", "finally,",
    "in conclusion,", "to summarize,", "in summary,",
]

# ---------------------------------------------------------------------------
# New for H-M1
# ---------------------------------------------------------------------------

ENCODER_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
ENCODER_BATCH_SIZE: int = 256
EMBED_DIM: int = 384
CUMULATIVE_TOKENS_SCALE: float = 1000.0
AMBIGUITY_KAPPA_THRESHOLD: float = 0.4
EFFECT_SIZE_THRESHOLD: float = 0.1
FIGURES_DIR: str = "../figures"
RESULTS_JSON: str = "../results/results.yaml"
MIN_SESSIONS_PER_WORKER: int = 3
MIN_WORKERS: int = 100
PANEL_COV_TYPE: str = "clustered"
BETA_EXPOSURE_MIN: float = 0.0
AMBIGUITY_SCORE_THRESHOLD: float = 0.4
HH_RLHF_AMBIGUITY_KAPPA: float = 0.4
PANEL_POWER_WARN_ONLY: bool = True

WEBGPT_COLUMN_MAP: Dict[str, List[str]] = {
    "score": ["score_0", "score_1"],
    "answer": ["answer_0", "answer_1"],
    "worker": ["worker_id", "worker", "annotator_id"],
    "timestamp": ["created_at", "timestamp", "date"],
}
WEBGPT_PREFERRED_COL: str = "worker_id"

FIGURE_DPI: int = 150
FIGURE_SIZES: Dict[str, tuple] = {
    "dose_response": (10, 6),
    "ambiguity_modulation": (12, 5),
    "placebo_histogram": (8, 5),
    "worker_fe_dist": (8, 5),
    "discriminant_validity": (8, 6),
    "gate_metrics": (8, 5),
}
COLOR_PALETTE: Dict[str, str] = {
    "high_ambiguity": "#E74C3C",
    "low_ambiguity": "#3498DB",
    "observed": "#2ECC71",
    "null": "#95A7AA",
    "stylistic": "#8E44AD",
    "topic": "#F39C12",
}
FIGURE_FILENAMES: Dict[str, str] = {
    "dose_response": "dose_response.png",
    "ambiguity_modulation": "ambiguity_modulation.png",
    "placebo_histogram": "placebo_permutation.png",
    "worker_fe_dist": "worker_fe_distribution.png",
    "discriminant_validity": "discriminant_validity.png",
    "gate_metrics": "gate_metrics_hm1.png",
}

SMOKE_OVERRIDES: Dict[str, Any] = {
    "bootstrap_iters": 10,
    "permutation_iters": 10,
    "hh_rlhf_subsample": 500,
    "webgpt_subsample": 200,
    "encoder_batch_size": 64,
}


@dataclass
class Paths:
    base_dir: Path
    h_e1_code_dir: Path
    hypothesis_dir: Path
    figures_dir: Path
    results_dir: Path
    code_dir: Path
    tests_dir: Path

    @classmethod
    def from_base(cls, base_dir: Path) -> "Paths":
        base_dir = Path(base_dir)
        hypothesis_dir = base_dir / "docs" / "youra_research" / "20260503_bi_align" / "h-m1"
        return cls(
            base_dir=base_dir,
            h_e1_code_dir=base_dir / "docs" / "youra_research" / "20260503_bi_align" / "h-e1" / "code",
            hypothesis_dir=hypothesis_dir,
            figures_dir=hypothesis_dir / "figures",
            results_dir=hypothesis_dir / "results",
            code_dir=hypothesis_dir / "code",
            tests_dir=hypothesis_dir / "tests",
        )


@dataclass
class ExperimentConfig:
    hh_rlhf_dataset: str = HH_RLHF_DATASET
    webgpt_dataset: str = WEBGPT_DATASET
    n_rounds: int = N_ROUNDS
    encoder_model: str = ENCODER_MODEL
    encoder_batch_size: int = ENCODER_BATCH_SIZE
    embed_dim: int = EMBED_DIM
    cumulative_tokens_scale: float = CUMULATIVE_TOKENS_SCALE
    min_sessions_per_worker: int = MIN_SESSIONS_PER_WORKER
    min_workers: int = MIN_WORKERS
    panel_cov_type: str = PANEL_COV_TYPE
    ambiguity_kappa_threshold: float = AMBIGUITY_KAPPA_THRESHOLD
    ambiguity_score_threshold: float = AMBIGUITY_SCORE_THRESHOLD
    effect_size_threshold: float = EFFECT_SIZE_THRESHOLD
    bootstrap_iters: int = BOOTSTRAP_ITERS
    permutation_iters: int = PERMUTATION_ITERS
    random_seed: int = RANDOM_SEED
    beta_exposure_min: float = BETA_EXPOSURE_MIN
    alpha_significance: float = ALPHA_CORRECTED
    brier_gate_threshold: float = BRIER_GATE_THRESHOLD
    bonferroni_k: int = BONFERRONI_K
    figures_dir: str = FIGURES_DIR
    results_file: str = RESULTS_JSON
    hh_rlhf_subsample: Optional[int] = None
    webgpt_subsample: Optional[int] = None


def load_config(config_path: Optional[str] = None) -> ExperimentConfig:
    if config_path is None:
        return ExperimentConfig()
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)
    cfg = ExperimentConfig()
    for key, val in raw.items():
        if key in ExperimentConfig.__dataclass_fields__:
            setattr(cfg, key, val)
    return cfg
