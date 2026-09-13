"""Configuration for h-c1: Mode 3 subjective vs objective comparison."""

import os

H_E1_DIR = os.path.join(os.path.dirname(__file__), "../../h-e1/code/")
H_E1_RESULTS_CSV = os.path.join(H_E1_DIR, "outputs/results.csv")
DATASET_ID = "lmsys/lmsys-arena-human-preference-55k"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs/")

MIN_PER_CATEGORY = 500

SUBJECTIVE_CATEGORIES = {"creative_writing", "general"}
OBJECTIVE_CATEGORIES = {"coding", "math", "hard_prompts"}

OBJECTIVE_KEYWORDS = [
    "code", "function", "algorithm", "debug", "compile",
    "solve", "equation", "calculate", "proof", "theorem",
    "def ", "class ", "import ", "bug", "programming",
]
SUBJECTIVE_KEYWORDS = [
    "write", "story", "poem", "creative", "imagine",
    "opinion", "feel", "describe", "essay", "narrative",
]

ALPHA = 0.05
RATIO_SUCCESS_THRESHOLD = 1.5
RATIO_FALSIFY_THRESHOLD = 1.0

CATEGORY_DIST_PATH = os.path.join(OUTPUT_DIR, "category_mode_distribution.json")
RATIO_ANALYSIS_PATH = os.path.join(OUTPUT_DIR, "ratio_analysis.json")
PROMPT_CATEGORIES_PATH = os.path.join(OUTPUT_DIR, "prompt_categories.parquet")
