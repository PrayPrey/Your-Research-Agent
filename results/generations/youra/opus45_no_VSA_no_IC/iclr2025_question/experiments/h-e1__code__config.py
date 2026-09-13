"""Configuration for h-e1 EXISTENCE PoC experiment."""

import os

SEED = 42

MODELS = {
    "llama3-8b": {
        "id": "meta-llama/Meta-Llama-3-8B-Instruct",
        "n_layers": 32,
        "hidden_dim": 4096,
    },
    "mistral-7b": {
        "id": "mistralai/Mistral-7B-Instruct-v0.2",
        "n_layers": 32,
        "hidden_dim": 4096,
    },
    "qwen2-7b": {
        "id": "Qwen/Qwen2-7B-Instruct",
        "n_layers": 28,
        "hidden_dim": 3584,
    },
}

NLI_MODEL_ID = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"

N_SAMPLES = 5
TEMPERATURE = 0.7
TRAIN_SPLIT = 0.8
LAYER_FRACTION = 2 / 3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")

TORCH_DTYPE = "float16"
DEVICE_MAP = "auto"
