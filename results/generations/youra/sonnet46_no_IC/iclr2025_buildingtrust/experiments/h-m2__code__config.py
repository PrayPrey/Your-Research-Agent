"""Configuration for H-M2: RLHF Representation Rigidity Reduces Adversarial Robustness."""
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_HM2 = os.path.dirname(_HERE)   # h-m2/
_RESEARCH = os.path.dirname(_HM2)  # youra_research/

HE1_CODE_DIR = os.path.join(_RESEARCH, "h-e1", "code")
HE1_RESULTS_DIR = os.path.join(HE1_CODE_DIR, "TrustLLM", "results")
HE1_JSON = os.path.join(_RESEARCH, "h-e1", "experiment_results_phase3.json")

OUTPUT_DIR = _HM2
FIGURES_DIR = os.path.join(_HM2, "figures")
RESULTS_JSON = os.path.join(_HM2, "experiment_results_h_m2.json")
LOG_PATH = os.path.join(_HM2, "experiment.log")

DIMENSIONS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]
SAFETY_IDX = 1
ROBUSTNESS_IDX = 3
ETHICS_IDX = 5
RHO_THRESHOLD = -0.4   # signed: must be < -0.4
SECONDARY_GATE_MIN = 2  # >=2 of 3 pairs with delta_robustness <= 0
N_PAIRS = 3
BONFERRONI_ALPHA = 0.0033

LLAMA2_SCALES = ["7b", "13b", "70b"]
LLAMA2_BASE_NAMES = ["LLaMA-2-7b-base", "LLaMA-2-13b-base", "LLaMA-2-70b-base"]
LLAMA2_CHAT_NAMES = ["LLaMA-2-7b-chat", "LLaMA-2-13b-chat", "LLaMA-2-70b-chat"]
LLAMA2_PAIRS = list(zip(LLAMA2_BASE_NAMES, LLAMA2_CHAT_NAMES, LLAMA2_SCALES))

PYTHIA_SIZES = ["70m", "160m", "410m", "1b", "1.4b", "2.8b", "6.9b", "12b"]
PYTHIA_CACHE_KEY = "pythia_results"

PRIMARY_COVARIATES = ["log10_params", "is_RLHF"]

ABLATION_MODES = {
    "uncontrolled": {"covariates": []},
    "scale_only":   {"covariates": ["log10_params"]},
    "rlhf_only":    {"covariates": ["is_RLHF"]},
}
