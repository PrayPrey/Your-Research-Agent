"""Configuration for h-m2 experiment."""
from pathlib import Path

class Config:
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_FOLDER = PROJECT_ROOT / "data/mcp_traces"
    OUTPUT_FOLDER = PROJECT_ROOT / "outputs"
    FIGURES_FOLDER = PROJECT_ROOT / "figures"
    ANNOTATIONS_FOLDER = PROJECT_ROOT / "annotations"
    PROMPTS_FOLDER = PROJECT_ROOT / "prompts"
    
    # Dataset
    SAMPLE_SIZE = 50
    N_QUERIES = 25
    N_RESULTS = 25
    MIN_NL_WORDS = 10
    RANDOM_SEED = 42
    
    # LLM
    LLM_MODEL = "claude-sonnet-4-5"
    LLM_TEMPERATURE = 0.0
    MULTI_VOTE_COUNT = 3
    CONSENSUS_THRESHOLD = 2  # ≥2/3 votes
    
    # Gate Thresholds
    PRECISION_THRESHOLD = 0.70
    RECALL_THRESHOLD = 0.80
    KAPPA_THRESHOLD = 0.70
    
    def __init__(self):
        self.OUTPUT_FOLDER.mkdir(exist_ok=True)
        self.FIGURES_FOLDER.mkdir(exist_ok=True)
        self.ANNOTATIONS_FOLDER.mkdir(exist_ok=True)
        self.PROMPTS_FOLDER.mkdir(exist_ok=True)
