"""Configuration for H-M1: RLHF Co-Optimization of Safety and Ethics."""
import os

# Base paths (relative to this file's directory: h-m1/code/)
_HERE = os.path.dirname(os.path.abspath(__file__))
_HM1 = os.path.dirname(_HERE)  # h-m1/
_RESEARCH = os.path.dirname(_HM1)  # youra_research/

HE1_CODE_DIR = os.path.join(_RESEARCH, "h-e1", "code")
HE1_RESULTS_DIR = os.path.join(HE1_CODE_DIR, "TrustLLM", "results")
HE1_JSON = os.path.join(_RESEARCH, "h-e1", "experiment_results_phase3.json")

OUTPUT_DIR = _HM1
FIGURES_DIR = os.path.join(_HM1, "figures")
RESULTS_JSON = os.path.join(_HM1, "experiment_results_phase3.json")
LOG_PATH = os.path.join(_HM1, "experiment.log")

# Analysis constants
DIMENSIONS = ["truthfulness", "safety", "fairness", "robustness", "privacy", "machine_ethics"]
SAFETY_IDX = 1
ETHICS_IDX = 5
RHO_THRESHOLD = 0.5
SECONDARY_GATE_MIN = 2  # >=2 of 3 pairs
N_PAIRS = 3
BONFERRONI_ALPHA = 0.0033

# LLaMA-2 pair definitions
LLAMA2_SCALES = ["7b", "13b", "70b"]
LLAMA2_BASE_NAMES = ["LLaMA-2-7b-base", "LLaMA-2-13b-base", "LLaMA-2-70b-base"]
LLAMA2_CHAT_NAMES = ["LLaMA-2-7b-chat", "LLaMA-2-13b-chat", "LLaMA-2-70b-chat"]

LLAMA2_PAIRS = list(zip(LLAMA2_BASE_NAMES, LLAMA2_CHAT_NAMES, LLAMA2_SCALES))
