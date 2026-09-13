"""Configuration for h-e1 SEDP Existence Validation experiment."""

from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Experiment configuration with hyperparameters from SEP paper."""

    # Data
    dataset_name: str = "truthfulqa/truthful_qa"
    dataset_config: str = "generation"
    test_size: float = 0.2
    seed: int = 42

    # Generation
    llm_name: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    n_responses: int = 20
    temperature: float = 0.7
    max_new_tokens: int = 100
    layer_idx: int = 25  # Middle-to-late layer per SEP paper

    # SE labels
    nli_model_name: str = "cross-encoder/nli-deberta-v3-large"
    entailment_threshold: float = 0.5

    # Similarity features
    embedder_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Probe
    probe_C: float = 1.0
    probe_max_iter: int = 1000

    # Evaluation
    rho_threshold: float = 0.3  # Gate threshold: SEDP rho >= 0.3 to pass

    # Paths
    cache_dir: str = "h-e1/cache"
    figures_dir: str = "h-e1/figures"
    results_path: str = "h-e1/04_validation.md"
