"""H-M2 configuration constants."""
import os
from pathlib import Path

_PROJECT_ROOT = os.environ.get(
    "YOURA_PROJECT_ROOT",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
)

H_E1_RESULTS_DIR = Path(_PROJECT_ROOT) / "docs/youra_research/h-e1/docs/youra_research/h-e1/results"
H_M2_RESULTS_DIR = Path(_PROJECT_ROOT) / "docs/youra_research/h-m2/results"
H_M2_FIGURES_DIR = Path(_PROJECT_ROOT) / "docs/youra_research/h-m2/figures"
H_E1_CODE_DIR    = Path(_PROJECT_ROOT) / "docs/youra_research/h-e1/code"

# Available model (single model from H-E1)
MODEL = "Llama-2-7b-hf"

# Available task splits with their clean counterparts
# Format: task_id -> (adversarial_file, clean_file)
TASK_FILE_MAP = {
    "advglue_mnli": (
        "Llama-2-7b-hf_nli_adversarial_examples.jsonl",
        "Llama-2-7b-hf_nli_clean_examples.jsonl",
    ),
    "advglue_qqp": (
        "Llama-2-7b-hf_qqp_adversarial_examples.jsonl",
        "Llama-2-7b-hf_qqp_clean_examples.jsonl",
    ),
    "anli_r1": (
        "Llama-2-7b-hf_nli_anli_r1_examples.jsonl",
        "Llama-2-7b-hf_nli_clean_examples.jsonl",   # clean baseline shared with MNLI
    ),
    "anli_r2": (
        "Llama-2-7b-hf_nli_anli_r2_examples.jsonl",
        "Llama-2-7b-hf_nli_clean_examples.jsonl",
    ),
    "anli_r3": (
        "Llama-2-7b-hf_nli_anli_r3_examples.jsonl",
        "Llama-2-7b-hf_nli_clean_examples.jsonl",
    ),
}

TASKS = list(TASK_FILE_MAP.keys())

# Gate thresholds (H-M2 hypothesis)
DELTA_ACC_GATE   = -0.10   # accuracy must DROP by >= 10pp
CONF_WRONG_GATE  =  0.70   # mean confidence on wrong adv predictions >= 0.70
GATE_RATE        =  0.60   # fraction of cells that must pass both conditions
TOTAL_CELLS      = len(TASKS)  # 5 cells (1 model x 5 tasks)

# Task subsets for ablation B
NLI_TASKS     = ["advglue_mnli", "anli_r1", "anli_r2", "anli_r3"]
NON_NLI_TASKS = ["advglue_qqp"]
ANLI_TASKS    = ["anli_r1", "anli_r2", "anli_r3"]
