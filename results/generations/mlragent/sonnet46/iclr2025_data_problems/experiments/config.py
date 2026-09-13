"""Configuration for DynaMix experiments."""
import os

# Experiment settings
SEED = 42
DEVICE = "cuda"

# Data domains (simulated with real text data from HuggingFace)
DOMAINS = ["web", "code", "science", "wiki", "instructions"]
NUM_DOMAINS = len(DOMAINS)

# Model config - small GPT-2 style proxy models
PROXY_MODEL_SIZES = [
    {"n_embd": 128, "n_layer": 4, "n_head": 4, "name": "proxy_small"},
    {"n_embd": 256, "n_layer": 6, "n_head": 8, "name": "proxy_medium"},
]

# Training config
BATCH_SIZE = 32
SEQ_LEN = 128
LEARNING_RATE = 3e-4
WEIGHT_DECAY = 0.01
MAX_STEPS = 2000       # Steps per run
EVAL_INTERVAL = 100    # Evaluate every N steps
WARMUP_STEPS = 100

# DynaMix controller config
RL_UPDATE_INTERVAL = 200   # Update controller every N steps
RL_LEARNING_RATE = 1e-3
RL_GAMMA = 0.99
RL_CLIP_EPS = 0.2
SNR_WINDOW = 20            # Steps to average SNR

# Static baseline mixtures (following Llama-2 inspired proportions)
STATIC_UNIFORM = [0.2, 0.2, 0.2, 0.2, 0.2]
STATIC_TUNED = [0.45, 0.20, 0.10, 0.10, 0.15]  # web-heavy like Llama

# DoReMi-style: upweight lower-loss domains
DOREMI_WARMUP_STEPS = 400

# Scaling law config
NUM_PROXY_SCALES = 2
SCALING_FIT_SAMPLES = 10

# Output directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "outputs")
DATA_CACHE_DIR = os.path.join(BASE_DIR, "data_cache")

# Evaluation tasks
EVAL_TASKS = ["perplexity_web", "perplexity_code", "perplexity_science", "perplexity_wiki"]

# Number of tokens per domain for data loading
TOKENS_PER_DOMAIN = 50000  # small subset for efficiency
