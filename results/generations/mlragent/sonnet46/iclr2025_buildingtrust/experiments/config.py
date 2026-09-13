"""Configuration for CARE framework experiments."""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Dataset settings
DATASET_SIZE = 2000        # Total samples from ToxiGen
CALIBRATION_SIZE = 400     # Samples for conformal calibration
TEST_SIZE = 600            # Test set size
DOMAIN_TEST_SIZE = 200     # Samples per domain test set

# Conformal prediction settings
ALPHA_VALUES = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]  # Coverage targets 1-alpha
DEFAULT_ALPHA = 0.10  # Default: 90% coverage

# Model settings
SAFETY_CLASSIFIER_MODEL = "facebook/roberta-hate-speech-dynabench-r4-target"
EXPLANATION_MODEL = "claude-sonnet-4-6"  # via Anthropic API

# Domain adaptation settings
LAMBDA = 0.5  # Regulatory sensitivity scaling

# Training settings
BATCH_SIZE = 32
MAX_LENGTH = 128

# Experiment seeds
SEED = 42

# API settings
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Risk categories for multi-label classification
RISK_CATEGORIES = [
    "hate_speech",
    "violence_incitement",
    "self_harm",
    "misinformation",
    "harassment",
]

# Domain contexts
DOMAINS = {
    "general": {"lambda": 0.0, "description": "General-purpose context"},
    "healthcare": {"lambda": 1.0, "description": "Healthcare/medical context (HIPAA)"},
    "finance": {"lambda": 0.8, "description": "Financial advisory context (MiFID II)"},
}
