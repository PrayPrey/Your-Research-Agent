"""H-M1 Configuration - TruthfulQA vs MMLU distinctness analysis."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
H_E1_RESULTS_PATH = os.path.join(os.path.dirname(BASE_DIR), "..", "h-e1", "experiment_results.json")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
DATA_CACHE_DIR = os.path.join(BASE_DIR, "data_cache")

Z_HIGH_MMLU = 1.0
Z_LOW_TRUTHFULQA = 0.0
MIN_MODELS = 30
N_TARGET_MODELS = 50
CORRELATION_METHOD = "spearman"
ALPHA = 0.05

MMLU_SUBJECTS = [
    "abstract_algebra", "anatomy", "astronomy", "business_ethics", "clinical_knowledge",
    "college_biology", "college_chemistry", "college_computer_science", "college_mathematics",
    "college_medicine", "college_physics", "computer_security", "conceptual_physics",
    "econometrics", "electrical_engineering", "elementary_mathematics", "formal_logic",
    "global_facts", "high_school_biology", "high_school_chemistry", "high_school_computer_science",
    "high_school_european_history", "high_school_geography", "high_school_government_and_politics",
    "high_school_macroeconomics", "high_school_mathematics", "high_school_microeconomics",
    "high_school_physics", "high_school_psychology", "high_school_statistics",
    "high_school_us_history", "high_school_world_history", "human_aging", "human_sexuality",
    "international_law", "jurisprudence", "logical_fallacies", "machine_learning", "management",
    "marketing", "medical_genetics", "miscellaneous", "moral_disputes", "moral_scenarios",
    "nutrition", "philosophy", "prehistory", "professional_accounting", "professional_law",
    "professional_medicine", "professional_psychology", "public_relations", "security_studies",
    "sociology", "us_foreign_policy", "virology", "world_religions"
]
