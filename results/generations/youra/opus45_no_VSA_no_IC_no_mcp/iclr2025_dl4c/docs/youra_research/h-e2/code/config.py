"""Configuration for h-e2 experiment: AI-critic vs random baseline."""

MODEL_ID = "codellama/CodeLlama-7b-Instruct-hf"
K_ITERS = 3
TEMPERATURE = 0.7
MAX_TOKENS = 512
SEED = 42

DATASETS = {
    "humaneval": {"path": "openai_humaneval", "split": "test"},
    "mbpp": {"path": "mbpp", "split": "test"},
}

FIGURES_DIR = "../figures/"
TIMEOUT_SEC = 10
