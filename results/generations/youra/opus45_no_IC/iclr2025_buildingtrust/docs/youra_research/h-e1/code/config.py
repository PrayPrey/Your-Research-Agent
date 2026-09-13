"""H-E1 Configuration: Category-dependent calibration variation in LLMs on TruthfulQA."""

import torch

SEED = 42

# Model
MODEL_ID = "meta-llama/Llama-2-7b-hf"
DTYPE = torch.float16
DEVICE_MAP = "auto"

# Dataset
DATASET_ID = "truthfulqa/truthful_qa"
DATASET_CONFIG = "multiple_choice"
DATASET_SPLIT = "validation"
MIN_CLUSTER_SIZE = 50

# Inference
BATCH_SIZE = 8

# Metrics
N_BINS = 15
N_BOOTSTRAP = 100
CI = 0.95
ALPHA = 0.05
ECE_RANGE_TARGET = 0.05

# Output paths
RESULTS_JSON = "04_results.json"
VALIDATION_MD = "04_validation.md"
FIGURES_DIR = "figures/"

CLUSTER_NAMES = {
    1: "Health/Nutrition/Psychology",
    2: "Law/Politics/Government",
    3: "Finance/Economics",
    4: "Science/Technology/Math",
    5: "History/Geography/Culture",
    6: "Religion/Philosophy/Ethics",
    7: "Misconceptions/Myths/Superstitions",
}

CATEGORY_TO_CLUSTER = {
    "Health": 1, "Nutrition": 1, "Psychology": 1,
    "Law": 2, "Politics": 2, "Government": 2,
    "Finance": 3, "Economics": 3, "Statistics": 3,
    "Science": 4, "Technology": 4, "Math": 4, "Physics": 4, "Biology": 4,
    "History": 5, "Geography": 5, "Culture": 5, "Weather": 5,
    "Language": 5, "Education": 5, "Confusion: Places": 5,
    "Religion": 6, "Philosophy": 6, "Ethics": 6, "Sociology": 6,
    "Misconceptions": 7, "Misconceptions: Topical": 7, "Myths and Fairytales": 7,
    "Myths": 7, "Superstitions": 7, "Conspiracies": 7,
    "Paranormal": 7, "Indexical Error: Identity": 7, "Indexical Error: Time": 7,
    "Indexical Error: Location": 7, "Indexical Error: Other": 7,
    "Indexical Error: All": 7, "Subjective": 7, "Logical Falsehood": 7,
    "Stereotypes": 7, "Fiction": 7, "Advertising": 7, "Misquotations": 7,
    "Proverbs": 7, "Mandela Effect": 7, "Confusion: People": 7,
    "Confusion: Other": 7, "Distraction": 7, "Misinformation": 7,
}
