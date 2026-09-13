from dataclasses import dataclass


@dataclass
class Config:
    # Inherited from H-E1/H-M1
    K: int = 10
    seed: int = 42
    n_bootstrap: int = 1000
    entailment_threshold: float = 0.5
    nli_model_name: str = "cross-encoder/nli-deberta-v3-large"
    n_questions: int = 98

    # Paths
    he1_code_dir: str = "../../h-e1/code"
    hm1_code_dir: str = "../../h-m1/code"
    he1_results_dir: str = "../../h-e1/results"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"

    # Ablation-specific
    paraphrase_subset_size: int = 20
    delta_auroc_gate: float = 0.03
