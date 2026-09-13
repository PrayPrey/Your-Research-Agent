"""Configuration for H-E1 benchmark correlation experiment."""

MODEL_ID = "meta-llama/Llama-2-7b-hf"
SEED = 42
CORR_THRESHOLD = 0.5

DATASETS = {
    "truthfulqa": {
        "path": "truthful_qa",
        "subset": "multiple_choice",
        "split": "validation",
        "max_samples": 817,  # full set
    },
    "hhh_helpful": {
        "path": "Anthropic/hh-rlhf",
        "subset": None,
        "split": "test",
        "filter_key": "helpful",
        "max_samples": 1000,  # subsample for PoC
    },
    "hhh_harmless": {
        "path": "Anthropic/hh-rlhf",
        "subset": None,
        "split": "test",
        "filter_key": "harmless",
        "max_samples": 1000,  # subsample for PoC
    },
}

FIGURES_DIR = "../figures"
RESULTS_PATH = "../results/results.json"
