"""H-E1 Experiment Configuration."""
from dataclasses import dataclass
import os

# Resolve base project root relative to this file
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_E1_DIR = os.path.dirname(_THIS_DIR)


@dataclass
class ExperimentConfig:
    # Dataset
    dataset_id: str = "mandarjoshi/trivia_qa"
    dataset_config: str = "rc.nocontext"
    dataset_split: str = "validation"
    n_prompts: int = 300  # ponytail: PoC smoke test; restore 2500 for Phase 5 full run
    seed: int = 42

    # Generator (Llama)
    llm_id: str = "meta-llama/Llama-3.1-8B-Instruct"
    n_samples: int = 5
    temperature: float = 0.7
    top_p: float = 0.95
    max_new_tokens: int = 50

    # NLI (for SE clustering)
    nli_id: str = "cross-encoder/nli-deberta-v3-small"
    nli_batch_size: int = 32
    strict_entailment: bool = False

    # LM Judge
    judge_id: str = "Qwen/Qwen2.5-7B-Instruct"
    judge_batch_size: int = 16

    # Statistical thresholds — MUST NOT CHANGE (gate spec)
    pearson_r_threshold: float = 0.7
    partial_r2_threshold: float = 0.02
    circularity_threshold: float = 0.4
    abandon_threshold: float = 0.85

    # Paths (absolute, resolved at runtime)
    checkpoint_path: str = os.path.join(_H_E1_DIR, "results", "signals.pkl")
    results_path: str = os.path.join(_H_E1_DIR, "results", "stats.json")
    figures_dir: str = os.path.join(_H_E1_DIR, "figures")
    code_dir: str = _THIS_DIR


CONFIG = ExperimentConfig()

# Module-level constants for direct import
DATASET_ID = CONFIG.dataset_id
DATASET_CONFIG = CONFIG.dataset_config
DATASET_SPLIT = CONFIG.dataset_split
N_PROMPTS = CONFIG.n_prompts
SEED = CONFIG.seed

LLM_ID = CONFIG.llm_id
N_SAMPLES = CONFIG.n_samples
TEMPERATURE = CONFIG.temperature
TOP_P = CONFIG.top_p
MAX_NEW_TOKENS = CONFIG.max_new_tokens

NLI_ID = CONFIG.nli_id
NLI_BATCH_SIZE = CONFIG.nli_batch_size
STRICT_ENTAILMENT = CONFIG.strict_entailment

JUDGE_ID = CONFIG.judge_id
JUDGE_BATCH_SIZE = CONFIG.judge_batch_size

PEARSON_R_THRESHOLD = CONFIG.pearson_r_threshold
PARTIAL_R2_THRESHOLD = CONFIG.partial_r2_threshold
CIRCULARITY_THRESHOLD = CONFIG.circularity_threshold
ABANDON_THRESHOLD = CONFIG.abandon_threshold

CHECKPOINT_PATH = CONFIG.checkpoint_path
RESULTS_PATH = CONFIG.results_path
FIGURES_DIR = CONFIG.figures_dir

JUDGE_PROMPT: str = (
    "Is the following answer correct for the question? Answer YES or NO.\n"
    "Question: {question}\nAnswer: {answer}\nCorrect?"
)

JUDGE_LOAD_KWARGS = {
    "torch_dtype": "bfloat16",
    "device_map": "auto",
}
