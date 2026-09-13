"""
Configuration file for Semantic Consistency Graph experiments.
"""

import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Dataset settings
NUM_SYNTHETIC_CONVERSATIONS = 100  # Reduced for computational efficiency
NUM_TURNS_RANGE = (5, 15)  # Range of conversation turns
CONTRADICTION_DISTANCE_RANGE = (2, 8)  # Temporal distance between contradictions

# Model settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
NLI_MODEL = "cross-encoder/nli-deberta-v3-base"  # For NLI inference
LLM_MODEL = "gpt-4o-mini"  # Using API-based model

# SCG parameters
ALPHA = 0.4  # Balance between semantic similarity and NLI
CONTRADICTION_THRESHOLD = 0.3
TEMPORAL_DECAY_LAMBDA = 5.0
BETA_WEIGHTS = [0.4, 0.3, 0.3]  # Weights for claim-level uncertainty
GAMMA = 0.5  # Weight for max uncertainty in turn-level
DELTA = 0.4  # Weight for contradiction clusters in conversation-level

# Training settings
BATCH_SIZE = 16
LEARNING_RATE = 5e-5
NUM_EPOCHS = 3
MAX_SEQ_LENGTH = 128

# Evaluation settings
RANDOM_SEED = 42
TRAIN_SPLIT = 0.7
VAL_SPLIT = 0.15
TEST_SPLIT = 0.15

# API settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Device settings
import torch
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
