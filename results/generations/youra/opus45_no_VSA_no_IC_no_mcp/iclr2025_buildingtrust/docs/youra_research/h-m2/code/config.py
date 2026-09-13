"""Configuration for h-m2 Pareto-Optimal ECE Analysis."""
from pathlib import Path

SEED = 42
N_BINS = 15

H_E1_SCORES = Path(__file__).parent / "../../h-e1/code/results/scores.csv"
OUTPUT_PATH = Path(__file__).parent / "results"
FIGURES_PATH = Path(__file__).parent / "../figures"

P_THRESHOLD = 0.05
D_THRESHOLD = 0.5

MODEL_PARAMS = {
    "EleutherAI/pythia-70m": 70_000_000,
    "EleutherAI/pythia-160m": 160_000_000,
    "EleutherAI/pythia-410m": 410_000_000,
    "EleutherAI/pythia-1b": 1_000_000_000,
    "EleutherAI/pythia-1.4b": 1_400_000_000,
    "EleutherAI/pythia-2.8b": 2_800_000_000,
    "EleutherAI/pythia-6.9b": 6_900_000_000,
    "EleutherAI/pythia-12b": 12_000_000_000,
    "meta-llama/Llama-2-7b-hf": 7_000_000_000,
    "meta-llama/Llama-2-13b-hf": 13_000_000_000,
    "meta-llama/Llama-2-70b-hf": 70_000_000_000,
    "mistralai/Mistral-7B-v0.1": 7_000_000_000,
    "tiiuae/falcon-7b": 7_000_000_000,
    "tiiuae/falcon-40b": 40_000_000_000,
}
