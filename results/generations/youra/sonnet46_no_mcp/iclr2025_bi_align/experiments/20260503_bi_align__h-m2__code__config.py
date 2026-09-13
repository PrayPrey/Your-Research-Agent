"""H-M2 Configuration: Round-Stratified Label-Distribution Coefficient Shift."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

# ---------------------------------------------------------------------------
# Inherited from H-E1 / H-M1
# ---------------------------------------------------------------------------

HH_RLHF_DATASET: str = "Anthropic/hh-rlhf"
WEBGPT_DATASET: str = "openai/webgpt_comparisons"
N_ROUNDS: int = 3
RANDOM_SEED: int = 42
BOOTSTRAP_ITERS: int = 2000
ALPHA: float = 0.05
BONFERRONI_K: int = 3
ALPHA_CORRECTED: float = 0.0167
BRIER_GATE_THRESHOLD: float = 0.02
LR_PARAMS: Dict[str, Any] = {
    "C": 1.0,
    "solver": "lbfgs",
    "max_iter": 1000,
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
# New for H-M2: Data
# ---------------------------------------------------------------------------

TEST_SIZE: float = 0.25
ROUND_SIZE_MIN: int = 500
EARLY_ROUND: int = 1
LATE_ROUND: int = 3
CI_ALPHA: float = 0.05

# ---------------------------------------------------------------------------
# New for H-M2: Gate
# ---------------------------------------------------------------------------

N_DIRECTIONAL_GATE: int = 2
BETA_Q_STABILITY_THRESHOLD: float = 0.2
TOPIC_BALANCE_ALPHA: float = 0.05

# ---------------------------------------------------------------------------
# New for H-M2: Ambiguity (A-7)
# ---------------------------------------------------------------------------

AMBIGUITY_THRESHOLD: float = 0.1     # |q_score - 0.5| < 0.1 → high ambiguity for HH-RLHF
HIGH_AMBIGUITY_PREF_RATE_TARGET: float = 0.60
AUC_HELD_OUT_MIN: float = 0.55
AUC_HELD_OUT_TARGET: float = 0.60

# ---------------------------------------------------------------------------
# New for H-M2: Figures (A-8)
# ---------------------------------------------------------------------------

FIGURES_DPI: int = 150
FIGURE_SIZE_COEF: tuple = (10, 6)
FIGURE_SIZE_BOOT: tuple = (12, 4)
FIGURE_SIZE_STABILITY: tuple = (8, 5)
FIGURE_SIZE_SCATTER: tuple = (8, 8)
FIGURE_SIZE_TOPIC: tuple = (10, 5)
FIGURE_SIZE_GATE: tuple = (10, 6)

COLOR_EARLY: str = "#2196F3"
COLOR_LATE: str = "#FF9800"
CI_BAR_CAPSIZE: int = 5
CI_BAR_LINEWIDTH: float = 1.5
NON_OVERLAP_COLOR: str = "#4CAF50"

COLOR_PALETTE: Dict[str, str] = {
    "early_round": COLOR_EARLY,
    "late_round": COLOR_LATE,
    "neutral": "#95A7AA",
    "ci_fill": "#BDC3C7",
    "significant": NON_OVERLAP_COLOR,
    "high_ambiguity": "#E74C3C",
    "low_ambiguity": "#3498DB",
}

FIGURE_FILENAMES: Dict[str, str] = {
    "coef_comparison":     "fig1_coefficient_comparison.png",
    "bootstrap_dist":      "fig2_bootstrap_distributions.png",
    "feature_stability":   "fig3_feature_stability_rounds.png",
    "cross_round_scatter": "fig4_cross_round_scatter.png",
    "topic_balance":       "fig5_topic_balance.png",
    "gate_metrics":        "fig6_gate_metrics.png",
}

# ---------------------------------------------------------------------------
# New for H-M2: Output / Logging (A-9)
# ---------------------------------------------------------------------------

FIGURES_DIR: str = "../figures"
RESULTS_PATH: str = "../results/results.yaml"
LOG_LEVEL: str = "INFO"

# ---------------------------------------------------------------------------
# Smoke test overrides
# ---------------------------------------------------------------------------

SMOKE_OVERRIDES: Dict[str, Any] = {
    "bootstrap_iters": 20,
    "hh_rlhf_subsample": 500,
    "round_size_min": 100,
}


@dataclass
class Paths:
    base_dir: Path
    h_e1_code_dir: Path
    h_m1_code_dir: Path
    hypothesis_dir: Path
    figures_dir: Path
    results_dir: Path
    code_dir: Path
    tests_dir: Path

    @classmethod
    def from_base(cls, base_dir: Path) -> "Paths":
        base_dir = Path(base_dir)
        bi_align_dir = base_dir / "docs" / "youra_research" / "20260503_bi_align"
        hypothesis_dir = bi_align_dir / "h-m2"
        return cls(
            base_dir=base_dir,
            h_e1_code_dir=bi_align_dir / "h-e1" / "code",
            h_m1_code_dir=bi_align_dir / "h-m1" / "code",
            hypothesis_dir=hypothesis_dir,
            figures_dir=hypothesis_dir / "figures",
            results_dir=hypothesis_dir / "results",
            code_dir=hypothesis_dir / "code",
            tests_dir=hypothesis_dir / "tests",
        )


@dataclass
class ExperimentConfig:
    hh_rlhf_dataset: str = HH_RLHF_DATASET
    n_rounds: int = N_ROUNDS
    round_size_min: int = ROUND_SIZE_MIN
    early_round: int = EARLY_ROUND
    late_round: int = LATE_ROUND
    test_size: float = TEST_SIZE
    random_seed: int = RANDOM_SEED
    lr_params: Dict[str, Any] = field(default_factory=lambda: LR_PARAMS.copy())
    bootstrap_iters: int = BOOTSTRAP_ITERS
    ci_alpha: float = CI_ALPHA
    n_directional_gate: int = N_DIRECTIONAL_GATE
    beta_q_stability_threshold: float = BETA_Q_STABILITY_THRESHOLD
    topic_balance_alpha: float = TOPIC_BALANCE_ALPHA
    ambiguity_threshold: float = AMBIGUITY_THRESHOLD
    high_ambiguity_pref_rate_target: float = HIGH_AMBIGUITY_PREF_RATE_TARGET
    auc_held_out_min: float = AUC_HELD_OUT_MIN
    auc_held_out_target: float = AUC_HELD_OUT_TARGET
    figures_dir: str = FIGURES_DIR
    results_path: str = RESULTS_PATH
    log_level: str = LOG_LEVEL
    hh_rlhf_subsample: Optional[int] = None


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
