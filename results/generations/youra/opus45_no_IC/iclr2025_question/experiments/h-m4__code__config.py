"""Configuration for H-M4: Cross-cluster threshold transfer experiment."""

import os
import sys
import importlib.util

# Import H-M3 config using importlib to avoid naming conflicts
H_M3_CODE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "h-m3", "code")
h_m3_config_path = os.path.join(H_M3_CODE_PATH, "config.py")

spec = importlib.util.spec_from_file_location("h_m3_config", h_m3_config_path)
h_m3_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h_m3_config)

# Inherited from H-M3
SEED = h_m3_config.SEED
CALIB_SPLIT = h_m3_config.CALIB_SPLIT
TARGET_FPR = h_m3_config.TARGET_FPR

# Re-export TARGET_FPR at module level for import
__all__ = ['SEED', 'CALIB_SPLIT', 'TARGET_FPR', 'GEN_MODEL', 'NLI_MODEL', 'N_GENERATIONS',
           'TEMPERATURE', 'MAX_NEW_TOKENS', 'NLI_BATCH_SIZE', 'ENTAILMENT_THRESHOLD',
           'F1_THRESHOLD', 'N_BOOTSTRAP', 'CROSS_CLUSTER_PAIRS', 'JS_DIVERGENCE',
           'DEGRADATION_THRESHOLD', 'H_M3_RESULTS_PATH', 'H_M3_BASELINE_DEGRADATION',
           'SAMPLE_SIZE', 'OUTPUTS_DIR', 'FIGURES_DIR']
GEN_MODEL = h_m3_config.GEN_MODEL
NLI_MODEL = h_m3_config.NLI_MODEL
N_GENERATIONS = h_m3_config.N_GENERATIONS
TEMPERATURE = h_m3_config.TEMPERATURE
MAX_NEW_TOKENS = h_m3_config.MAX_NEW_TOKENS
NLI_BATCH_SIZE = h_m3_config.NLI_BATCH_SIZE
ENTAILMENT_THRESHOLD = h_m3_config.ENTAILMENT_THRESHOLD
F1_THRESHOLD = h_m3_config.F1_THRESHOLD
N_BOOTSTRAP = h_m3_config.N_BOOTSTRAP

# Cross-cluster pairs (source from Cluster 1, target from Cluster 2)
CROSS_CLUSTER_PAIRS = [
    ("trivia_qa", "pop_qa"),
    ("trivia_qa", "halueval_qa"),
]

# JS-divergence values from H-E1
JS_DIVERGENCE = {
    ("trivia_qa", "pop_qa"): 0.422,
    ("trivia_qa", "halueval_qa"): 0.526,
}

# H-M4 gate threshold (inverted from H-M3's <= 0.08)
DEGRADATION_THRESHOLD = 0.15

# H-M3 baseline for Mann-Whitney comparison
H_M3_RESULTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "h-m3", "outputs", "experiment_results.json"
)
H_M3_BASELINE_DEGRADATION = 0.032

# Sample size per benchmark (150 for mock fix validation, scale up for final run)
SAMPLE_SIZE = 150

# Output directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
