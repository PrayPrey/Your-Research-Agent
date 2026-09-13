"""H-M2 Configuration - Error Family Statistical Analysis"""
import os
from pathlib import Path

# Benchmark ordering - MUST match H-E1 matrix index order
BENCHMARK_NAMES = [
    "trivia_qa", "natural_questions", "squad",  # Factual Recall family
    "pop_qa", "halueval_qa", "fever",            # Entity/Claim family
]

# Error family definitions
FACTUAL_FAMILY = {"trivia_qa", "natural_questions", "squad"}
ENTITY_FAMILY = {"pop_qa", "halueval_qa", "fever"}

# Paths
YOURA_RESEARCH = Path(__file__).parent.parent.parent  # youra_research/
H_E1_RESULTS = YOURA_RESEARCH / "h-e1" / "results.json"
FIGURES_DIR = Path(__file__).parent.parent / "figures"

# Statistical thresholds (from PRD Success Criteria)
P_VALUE_THRESHOLD = 0.05           # PRIMARY: Mann-Whitney U one-sided
SAME_FAMILY_MEAN_THRESHOLD = 0.15  # SECONDARY: mean same-family JS-div
CLIFFS_DELTA_THRESHOLD = -0.5      # TERTIARY: large effect size

SEED = 42
