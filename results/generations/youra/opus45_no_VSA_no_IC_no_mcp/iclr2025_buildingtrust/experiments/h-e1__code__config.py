"""Configuration for h-e1 EXISTENCE hypothesis experiment."""

MODELS = [
    # Pythia family
    {"id": "EleutherAI/pythia-70m", "family": "pythia", "params": 70_000_000},
    {"id": "EleutherAI/pythia-160m", "family": "pythia", "params": 160_000_000},
    {"id": "EleutherAI/pythia-410m", "family": "pythia", "params": 410_000_000},
    {"id": "EleutherAI/pythia-1b", "family": "pythia", "params": 1_000_000_000},
    {"id": "EleutherAI/pythia-1.4b", "family": "pythia", "params": 1_400_000_000},
    {"id": "EleutherAI/pythia-2.8b", "family": "pythia", "params": 2_800_000_000},
    {"id": "EleutherAI/pythia-6.9b", "family": "pythia", "params": 6_900_000_000},
    {"id": "EleutherAI/pythia-12b", "family": "pythia", "params": 12_000_000_000},
    # Llama-2 family
    {"id": "meta-llama/Llama-2-7b-hf", "family": "llama2", "params": 7_000_000_000},
    {"id": "meta-llama/Llama-2-13b-hf", "family": "llama2", "params": 13_000_000_000},
    {"id": "meta-llama/Llama-2-70b-hf", "family": "llama2", "params": 70_000_000_000},
    # Mistral
    {"id": "mistralai/Mistral-7B-v0.1", "family": "mistral", "params": 7_000_000_000},
    # Falcon
    {"id": "tiiuae/falcon-7b", "family": "falcon", "params": 7_000_000_000},
    {"id": "tiiuae/falcon-40b", "family": "falcon", "params": 40_000_000_000},
]

TASKS = ["truthfulqa_mc1", "glue"]

RESULTS_DIR = "results/"
FIGURES_DIR = "figures/"
SCORES_CSV = "results/scores.csv"

SEED = 42
N_BOOTSTRAP = 1000
CI_LEVEL = 0.95

R_THRESHOLD = 0.3
P_THRESHOLD = 0.05
CI_LOWER_THRESHOLD = 0.0
