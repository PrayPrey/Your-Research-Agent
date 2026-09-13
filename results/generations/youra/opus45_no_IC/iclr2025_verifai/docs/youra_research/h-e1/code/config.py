"""Configuration for H-E1: Error Class Independence Verification."""

import os
from pathlib import Path

SEED = 42
TEMPERATURE = 0.2
N_SAMPLES = 10
MODELS = ["codellama/CodeLlama-7b-hf", "gpt-4"]
JACCARD_THRESHOLD = 0.30
MEAN_JACCARD_THRESHOLD = 0.25

HUMANEVAL_SIZE = 164

VERUS_TASK_IDS = {
    "HumanEval/0", "HumanEval/1", "HumanEval/2", "HumanEval/3", "HumanEval/4",
    "HumanEval/5", "HumanEval/6", "HumanEval/7", "HumanEval/8", "HumanEval/9",
    "HumanEval/10", "HumanEval/11", "HumanEval/12", "HumanEval/13", "HumanEval/14",
    "HumanEval/15", "HumanEval/16", "HumanEval/17", "HumanEval/18", "HumanEval/19",
    "HumanEval/20", "HumanEval/21", "HumanEval/22",
}

HYPOTHESIS_FOLDER = Path(__file__).parent.parent
FIGURES_DIR = HYPOTHESIS_FOLDER / "figures"
RESULTS_DIR = HYPOTHESIS_FOLDER / "results"
CODE_DIR = HYPOTHESIS_FOLDER / "code"
OUTPUTS_DIR = CODE_DIR / "outputs"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
