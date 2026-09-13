import os

MODELS = {
    "llama2": "meta-llama/Llama-2-7b-hf",
    "mistral": "mistralai/Mistral-7B-v0.1",
}
DATASETS = ["trivia_qa", "nq", "truthful_qa"]
AGGREGATIONS = ["min", "mean", "sum"]
SEED = 42
MAX_NEW_TOKENS = 30  # Factual answers are short; reduces inference time
BOOTSTRAP_N = 1000

# Subsample for single-GPU tractability (full sets are 17K/3.6K samples)
# 2000 TriviaQA + 2000 NQ + 817 TruthfulQA (full) ~ 4817 total per model
# At ~0.9s/sample: ~4300s per model, ~8600s (2.4h) total for 2 models
MAX_SAMPLES_PER_DATASET = {
    "trivia_qa": 2000,
    "nq": 2000,
    "truthful_qa": None,  # full (817)
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
FARQUHAR_DATA_DIR = "/home/PrayPrey/data/semantic_uncertainty"
