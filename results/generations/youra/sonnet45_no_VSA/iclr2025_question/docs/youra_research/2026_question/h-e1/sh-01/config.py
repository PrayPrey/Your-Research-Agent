"""Configuration for sh-01 experiment."""

import os

class Config:
    # Data
    TRUTHFULQA_SAMPLE_SIZE = 200
    WRITINGPROMPTS_SAMPLE_SIZE = 200
    RANDOM_SEED = 42

    # Generation
    LLM_MODEL = "gpt-3.5-turbo"
    TEMPERATURE = 0.7
    MAX_TOKENS = 200
    API_RATE_LIMIT = 60  # requests/min

    # CCP Evaluation
    NLI_MODEL = "microsoft/deberta-large-mnli"
    K_ALTERNATIVES = 10
    BATCH_SIZE = 32

    # Statistical
    ALPHA = 0.05  # significance level
    TARGET_DELTA_RHO = 0.15
    TARGET_R_SQUARED = 0.6

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "results")
    FIGURES_DIR = os.path.join(BASE_DIR, "figures")
    CHECKPOINT_DIR = os.path.join(BASE_DIR, "checkpoints")
    CHECKPOINT_INTERVAL = 50

    # Ensure directories exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
