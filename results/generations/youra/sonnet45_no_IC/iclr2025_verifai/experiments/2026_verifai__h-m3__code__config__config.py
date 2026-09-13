"""Configuration for h-m3 semantic similarity-based constraint detection."""

from pathlib import Path

class Config:
    """Configuration constants for h-m3 experiment."""

    # === Paths ===
    PROJECT_ROOT = Path(__file__).parent.parent
    H_M2_OUTPUT_FOLDER = PROJECT_ROOT / "../../h-m2/code/outputs"
    OUTPUT_FOLDER = PROJECT_ROOT / "outputs"
    FIGURES_FOLDER = PROJECT_ROOT / "figures"
    GROUND_TRUTH_FOLDER = PROJECT_ROOT / "ground_truth"

    # Output files
    DETECTED_CONTRADICTIONS_FILE = OUTPUT_FOLDER / "detected_contradictions.json"
    RESULTS_FILE = OUTPUT_FOLDER / "h_m3_results.json"

    # Input files (from h-m2)
    ASSUMPTIONS_FILE = "llm_extraction_results.json"
    CLAIMS_FILE = "llm_extraction_results.json"

    # Ground truth
    KNOWN_FAILURES_FILE = "known_failures.json"

    # === Inherited from h-m2 ===
    RANDOM_SEED = 42
    FIGURE_DPI = 300
    FIGURE_SIZE = (10, 6)

    # === Data Loading (M3-2) ===
    EARLY_PHASES = [1, 2, 3]
    LATER_PHASES = [4, 5, 6]

    # === Semantic Encoder (M3-3) ===
    SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"
    EMBEDDING_BATCH_SIZE = 32
    DEVICE = "cpu"

    # === Contradiction Detection (M3-4) ===
    SIMILARITY_THRESHOLD = 0.3
    FUZZY_MATCH_THRESHOLD = 0.7

    # === Gate Evaluator (M3-6) ===
    RECALL_TARGET = 0.70
    RECALL_ACCEPTABLE = 0.60
    FP_RATE_LIMIT = 0.30

    # === Threshold Tuning (M3-7) ===
    ENABLE_THRESHOLD_TUNING = True
    TUNING_THRESHOLDS = [0.2, 0.25, 0.3, 0.35, 0.4]

    def __init__(self):
        """Initialize configuration and create directories."""
        self.OUTPUT_FOLDER.mkdir(exist_ok=True, parents=True)
        self.FIGURES_FOLDER.mkdir(exist_ok=True, parents=True)
        self.GROUND_TRUTH_FOLDER.mkdir(exist_ok=True, parents=True)
