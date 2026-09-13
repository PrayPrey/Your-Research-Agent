"""Configuration for H-E1 Benchmark Clustering Experiment."""

import os

SEED = 42

BENCHMARKS = [
    "trivia_qa",
    "natural_questions",
    "squad",
    "pop_qa",
    "halueval_qa",
    "fever",
]

N_SAMPLES = 1000
GEN_MODEL = "meta-llama/Llama-2-7b-hf"
NLI_MODEL = "microsoft/deberta-v3-large-mnli"
N_GENERATIONS = 10
TEMPERATURE = 0.7
MAX_NEW_TOKENS = 64

KDE_BANDWIDTH = "scott"
ENTROPY_SUPPORT_RANGE = (0, 3)
ENTROPY_SUPPORT_POINTS = 1000
CLUSTER_K_RANGE = (2, 4)
LINKAGE_METHOD = "ward"
SILHOUETTE_THRESHOLD = 0.5

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(os.path.dirname(BASE_DIR), "cache")
FIGURES_DIR = os.path.join(os.path.dirname(BASE_DIR), "figures")
RESULTS_PATH = os.path.join(os.path.dirname(BASE_DIR), "results.json")

CONFIG = {
    "seed": SEED,
    "benchmarks": BENCHMARKS,
    "n_samples": N_SAMPLES,
    "gen_model": GEN_MODEL,
    "n_generations": N_GENERATIONS,
    "temperature": TEMPERATURE,
    "max_new_tokens": MAX_NEW_TOKENS,
    "nli_model": NLI_MODEL,
    "kde_bandwidth": KDE_BANDWIDTH,
    "entropy_support_range": ENTROPY_SUPPORT_RANGE,
    "entropy_support_points": ENTROPY_SUPPORT_POINTS,
    "cluster_k_range": CLUSTER_K_RANGE,
    "linkage_method": LINKAGE_METHOD,
    "silhouette_threshold": SILHOUETTE_THRESHOLD,
}

PATHS = {
    "cache_dir": CACHE_DIR,
    "figures_dir": FIGURES_DIR,
    "results_path": RESULTS_PATH,
}
