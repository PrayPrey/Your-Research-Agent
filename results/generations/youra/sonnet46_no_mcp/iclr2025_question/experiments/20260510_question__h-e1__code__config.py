from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ExperimentConfig:
    # Dataset
    hf_dataset_id: str = "pminervini/HaluEval"
    dataset_split: str = "qa_samples"
    n_hallucinated: int = 1000
    n_factual: int = 1000
    seed: int = 42

    # LLM Inference
    llm_model_id: str = "meta-llama/Llama-2-7b-hf"
    llm_dtype: str = "bfloat16"
    max_new_tokens: int = 256
    greedy_temperature: float = 0.0
    stochastic_temperature: float = 1.0
    n_stochastic_samples: int = 5

    # NLI Model
    nli_model_id: str = "microsoft/deberta-large-mnli"
    nli_batch_size: int = 16

    # Evaluation
    n_bootstrap: int = 1000
    bonferroni_k: int = 3
    alpha: float = 0.05
    min_auroc_gap: float = 0.05
    min_ci_separation: float = 0.0

    # AUROC direction: True = higher score → more hallucinated
    auroc_higher_is_more_hallucinated: Dict[str, bool] = field(default_factory=lambda: {
        "token_entropy_mean": True,
        "semantic_entropy": True,
        "selfcheckgpt_bertscore_n5": True,
    })

    # Paths (relative to code/ directory)
    data_dir: str = "data"
    outputs_dir: str = "outputs"
    results_dir: str = "results"
    figures_dir: str = "figures"


def get_config() -> ExperimentConfig:
    return ExperimentConfig()
