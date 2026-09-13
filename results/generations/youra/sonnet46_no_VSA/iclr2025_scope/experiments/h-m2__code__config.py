"""H-M2 configuration: paths, thresholds, domain filter constants."""
import os
from pathlib import Path

# Project root (3 levels up from this file: code/ -> h-m2/ -> youra_research/ -> docs/ -> TEST_scope/)
CODE_DIR = Path(__file__).parent
H_M2_DIR = CODE_DIR.parent
RESEARCH_DIR = H_M2_DIR.parent
PROJECT_ROOT = RESEARCH_DIR.parent.parent  # TEST_scope/

# H-E1 output paths (verified from actual h-e1/code/evaluate.py)
H_E1_RESULTS_DIR = str(PROJECT_ROOT / "docs/youra_research/h-e1/results")
MOHAWK_RESULTS_JSON = f"{H_E1_RESULTS_DIR}/mohawk_longbench.json"
LAWCAT_RESULTS_JSON = f"{H_E1_RESULTS_DIR}/lawcat_longbench.json"

# Alternative paths to probe if primary missing
H_E1_ALT_PATHS = [
    str(PROJECT_ROOT / "docs/youra_research/h-e1/results"),
    str(PROJECT_ROOT / "docs/youra_research/h-e1/code/results"),
    str(PROJECT_ROOT / "docs/youra_research/h-e1/outputs"),
]

# LongBench v2 category map (copied from H-E1 evaluate.py)
CATEGORY_MAP = {
    "single-document QA": "single_doc_qa",
    "multi-document QA": "multi_doc_qa",
    "long in-context learning": "long_in_context_learning",
    "long-dialogue history understanding": "long_dialogue",
    "code repository understanding": "code_repo",
    "long structured data understanding": "long_structured_data",
    "single_doc_qa": "single_doc_qa",
    "multi_doc_qa": "multi_doc_qa",
    "long_in_context_learning": "long_in_context_learning",
    "long_dialogue": "long_dialogue",
    "code_repo": "code_repo",
    "long_structured_data": "long_structured_data",
}

# Domain filter (H-E1 canonical category names)
RETRIEVAL_CATEGORIES = {"multi_doc_qa", "long_structured_data"}

# LongBench v2 HuggingFace source
LONGBENCH_HF_ID = "THUDM/LongBench"
LONGBENCH_HF_CONFIG = "v2"

# Statistical thresholds
GATE_RATIO_THRESHOLD = 2.0
MIN_SAMPLES_PER_MODEL = 100
DEPTH_FALLBACK_VALUE = 0.5
HOLM_N_TESTS = 2

# Output paths
OUTPUT_DIR = str(H_M2_DIR)
FIGURES_DIR = f"{OUTPUT_DIR}/figures"
RESULTS_JSON = f"{OUTPUT_DIR}/h_m2_results.json"
SUMMARY_MD = f"{OUTPUT_DIR}/h_m2_summary.md"

os.makedirs(FIGURES_DIR, exist_ok=True)
