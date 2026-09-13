"""Configuration for h-m4 meta-research validation."""

import os

# Seeds
SEED = 42

# Pool sizes
N_HYPOTHESIS_POOL = 100
N_SAMPLE_SIZE = 20

# Thresholds
GATE_THRESHOLD = 0.65  # MUST_WORK gate
BASELINE_THRESHOLD = 0.50  # PoC baseline
ALPHA = 0.05  # Statistical significance level

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H_M1_KB_PATH = os.path.join(os.path.dirname(BASE_DIR), "h-m1/data/pwc_cache/kb.yaml")
OUTPUT_DIR = os.path.join(BASE_DIR, "data")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")

# Hypothesis Generation
DOMAINS = ["nlp", "vision", "training", "multimodal"]
COMPLEXITY_LEVELS = ["simple", "moderate", "complex"]
LLM_MODEL = "claude-sonnet-4-5"

# Confound patterns (from h-m3)
CONFOUND_PATTERNS = {
    "nlp": [
        {"keywords": ["tokenizer", "vocab", "BLEU"], "description": "tokenizer-BLEU confound"},
        {"keywords": ["sequence length", "accuracy"], "description": "length-metric confound"},
        {"keywords": ["vocabulary size", "perplexity"], "description": "vocab-perplexity confound"},
        {"keywords": ["subword", "tokenization", "F1"], "description": "tokenization-F1 confound"},
        {"keywords": ["max length", "truncation", "score"], "description": "truncation-score confound"},
    ],
    "vision": [
        {"keywords": ["resolution", "architecture"], "description": "resolution-architecture confound"},
        {"keywords": ["augmentation", "model capacity"], "description": "augmentation-capacity confound"},
        {"keywords": ["image size", "depth"], "description": "size-depth confound"},
        {"keywords": ["color depth", "network size"], "description": "color-network confound"},
        {"keywords": ["crop size", "model complexity"], "description": "crop-complexity confound"},
    ],
    "training": [
        {"keywords": ["batch size", "learning rate"], "description": "batch-LR confound"},
        {"keywords": ["optimizer", "weight decay"], "description": "optimizer-regularization confound"},
        {"keywords": ["epochs", "dataset size"], "description": "epochs-data confound"},
        {"keywords": ["batch", "LR"], "description": "batch-LR confound (abbrev)"},
        {"keywords": ["momentum", "learning rate schedule"], "description": "momentum-schedule confound"},
    ],
}
