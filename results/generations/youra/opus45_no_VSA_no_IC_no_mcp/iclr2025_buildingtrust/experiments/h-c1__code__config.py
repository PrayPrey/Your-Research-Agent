"""Configuration for h-c1 CONDITION hypothesis: stratified correlation analysis."""

import os
import sys
import importlib.util

H_E1_CODE_DIR = os.path.join(os.path.dirname(__file__), "../../h-e1/code")

# Load h-e1 config without name collision
spec = importlib.util.spec_from_file_location("h_e1_config", os.path.join(H_E1_CODE_DIR, "config.py"))
h_e1_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h_e1_config)

BASE_MODELS = h_e1_config.MODELS
SEED = h_e1_config.SEED
N_BOOTSTRAP = h_e1_config.N_BOOTSTRAP
CI_LEVEL = h_e1_config.CI_LEVEL

# Base models from h-e1 (14 models)
BASE_MODELS_TYPED = [
    {**m, "model_type": "base"} for m in BASE_MODELS
]

# Instruction-tuned models (6 models)
INSTRUCTION_TUNED_MODELS = [
    {"id": "meta-llama/Llama-2-7b-chat-hf", "family": "llama2", "params": 7_000_000_000, "model_type": "instruction-tuned"},
    {"id": "meta-llama/Llama-2-13b-chat-hf", "family": "llama2", "params": 13_000_000_000, "model_type": "instruction-tuned"},
    {"id": "meta-llama/Llama-2-70b-chat-hf", "family": "llama2", "params": 70_000_000_000, "model_type": "instruction-tuned"},
    {"id": "mistralai/Mistral-7B-Instruct-v0.1", "family": "mistral", "params": 7_000_000_000, "model_type": "instruction-tuned"},
    {"id": "tiiuae/falcon-7b-instruct", "family": "falcon", "params": 7_000_000_000, "model_type": "instruction-tuned"},
    {"id": "tiiuae/falcon-40b-instruct", "family": "falcon", "params": 40_000_000_000, "model_type": "instruction-tuned"},
]

ALL_MODELS = BASE_MODELS_TYPED + INSTRUCTION_TUNED_MODELS

TASKS = ["truthfulqa_mc1", "glue"]

H_E1_RESULTS_DIR = os.path.join(H_E1_CODE_DIR, "results")
RESULTS_DIR = "results/"
FIGURES_DIR = "figures/"
SCORES_CSV = "results/scores.csv"

R_THRESHOLD = 0.2  # Per-group threshold (lower than h-e1's 0.3)
P_THRESHOLD = 0.05
