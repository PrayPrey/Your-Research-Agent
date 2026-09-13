"""Configuration for H-M1 Semantic Entropy Experiment."""

import os
from dataclasses import dataclass, field

SEED = 42

# Data
DATASET_NAME = "trivia_qa"
DATASET_SUBSET = "rc.nocontext"
SPLIT = "validation"
SAMPLE_SIZE = 1000
F1_THRESHOLD = 0.5

# Models
GEN_MODEL = "meta-llama/Llama-2-7b-chat-hf"
NLI_MODEL = "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli"

# Generation
N_GENERATIONS = 10
TEMPERATURE = 0.7
MAX_NEW_TOKENS = 50
TOP_P = 1.0

# Entailment clustering
ENTAILMENT_THRESHOLD = 0.5
NLI_BATCH_SIZE = 32

# Evaluation thresholds (MUST_WORK gate)
P_VALUE_THRESHOLD = 0.05
COHENS_D_THRESHOLD = 0.3
AUROC_SECONDARY = 0.65

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
CACHE_DIR = os.path.join(PARENT_DIR, "cache")
FIGURES_DIR = os.path.join(PARENT_DIR, "figures")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
RESULTS_PATH = os.path.join(PARENT_DIR, "experiment_results.json")

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

@dataclass
class DataConfig:
    dataset_name: str = DATASET_NAME
    dataset_subset: str = DATASET_SUBSET
    split: str = SPLIT
    sample_size: int = SAMPLE_SIZE
    seed: int = SEED
    f1_threshold: float = F1_THRESHOLD

@dataclass
class ModelConfig:
    model_name: str = GEN_MODEL
    dtype: str = "float16"
    device_map: str = "auto"

@dataclass
class GenerationConfig:
    temperature: float = TEMPERATURE
    n_samples: int = N_GENERATIONS
    max_new_tokens: int = MAX_NEW_TOKENS
    do_sample: bool = True
    top_p: float = TOP_P

@dataclass
class NLIConfig:
    model_name: str = NLI_MODEL
    entailment_threshold: float = ENTAILMENT_THRESHOLD
    batch_size: int = NLI_BATCH_SIZE

@dataclass
class EvaluationConfig:
    p_value_threshold: float = P_VALUE_THRESHOLD
    cohens_d_threshold: float = COHENS_D_THRESHOLD
    auroc_secondary: float = AUROC_SECONDARY

@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    nli: NLIConfig = field(default_factory=NLIConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    seed: int = SEED
    output_dir: str = OUTPUTS_DIR
    figures_dir: str = FIGURES_DIR
    results_path: str = RESULTS_PATH
