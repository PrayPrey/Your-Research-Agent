"""config.py — h-m4 constants and dataclasses for difficulty-stratified ECE analysis."""
from __future__ import annotations
from dataclasses import dataclass, field

MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6
SEED: int = 42

N_BOOT: int = 1000
M_PRIMARY: int = 15
M_SENSITIVITY: list[int] = [10, 15, 20]
DELTA_ECE_THRESHOLD: float = 0.03
MIN_TIER_SIZE: int = 20
HOLDOUT_FRAC: float = 0.2
T_BOUNDS: tuple[float, float] = (0.01, 10.0)

P1_MIN_PASSING: int = 2
P1_REQUIRE_CI_EXCLUDES_ZERO: bool = True
P2_MIN_PASSING: int = 2
P2_BOOTSTRAP_P_THRESHOLD: float = 0.05

CONFIDENCE_SCORES_FILENAME: str = "ptrue_confidence_scores.json"
TIER_ASSIGNMENTS_FILENAME: str = "tier_assignments.csv"

DEFAULT_HM3_RESULTS: str = "../h-m3/results"
DEFAULT_HM2_RESULTS: str = "../h-m2/results"
DEFAULT_HE1_RESULTS: str = "../h-e1/results"
DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"

RESULTS_FILENAME: str = "delta_ece_results.json"
RESULTS_SCHEMA_VERSION: str = "FR-8.1"


@dataclass
class ExperimentConfig:
    hm3_results: str = DEFAULT_HM3_RESULTS
    hm2_results: str = DEFAULT_HM2_RESULTS
    he1_results: str = DEFAULT_HE1_RESULTS
    output_dir: str = DEFAULT_OUTPUT_DIR
    figures_dir: str = DEFAULT_FIGURES_DIR
    seed: int = SEED
    n_boot: int = N_BOOT
    m_primary: int = M_PRIMARY


@dataclass
class FigureConfig:
    figures_dir: str = DEFAULT_FIGURES_DIR
    dpi: int = 150
    fig1_filename: str = "fig1_delta_ece_gate.png"
    fig2_filename: str = "fig2_reliability_diagrams.png"
    fig3_filename: str = "fig3_temperature_scaling.png"
    fig4_filename: str = "fig4_null_baseline.png"
    fig5_filename: str = "fig5_m_sensitivity.png"
    fig6_filename: str = "fig6_bootstrap_distribution.png"
    reliability_bins: int = 15
    bootstrap_hist_bins: int = 30
