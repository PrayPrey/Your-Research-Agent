"""config.py — h-m3 constants and dataclasses for P(True) logprob elicitation."""
from __future__ import annotations
from dataclasses import dataclass

# ── Inherited from h-m2 (verified from actual stratify.py) ───────────────────

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

# ── h-m3 specific constants ───────────────────────────────────────────────────

STD_GATE_THRESHOLD: float = 0.05
MAX_NEW_TOKENS: int = 1
SEED: int = 42
CHECKPOINT_INTERVAL: int = 100

PTRUE_PROMPT_TEMPLATE: str = (
    "{problem_description}\n\n```python\n{solution_code}\n```\n\n"
    "Is this solution correct? Answer True or False.\nAnswer:"
)

PTRUE_PROMPT_FALLBACK: str = (
    "{problem_description}\n\n```python\n{solution_code}\n```\n\n"
    "Does this solution pass all tests? Answer True or False.\nAnswer:"
)

CONFIDENCE_SCORES_FILENAME: str = "ptrue_confidence_scores.json"
VERIFIED_RESULTS_FILENAME: str = "ptrue_hm3_verified.json"
VERIFIED_RESULTS_SCHEMA_VERSION: str = "FR-10.1"

DEFAULT_HM1_RESULTS: str = "../../h-e1/results"
DEFAULT_HM2_RESULTS: str = "../../h-m2/results"
DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class ModelLoadConfig:
    torch_dtype: str = "float16"
    device_map: str = "auto"
    max_new_tokens: int = 1
    do_sample: bool = False
    seed: int = 42
    true_token: str = " True"   # leading space for tokenizer
    false_token: str = " False"  # leading space for tokenizer


@dataclass
class MetricsConfig:
    histogram_bins: int = 20
    expected_mean_c_low: float = 0.57
    expected_mean_c_high: float = 0.91
    expected_c_range_min: float = 0.2
    expected_c_range_max: float = 0.9


@dataclass
class FigureConfig:
    figures_dir: str = "figures"
    fig1_filename: str = "fig1_gate_check.png"
    fig2_filename: str = "fig2_c_histograms.png"
    fig3_filename: str = "fig3_c_vs_pass_at_1.png"
    fig4_filename: str = "fig4_c_by_tier.png"
    fig5_filename: str = "fig5_c_cdf.png"
    dpi: int = 150
    histogram_bins: int = 20
