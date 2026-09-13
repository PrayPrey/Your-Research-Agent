from dataclasses import dataclass


@dataclass
class Config:
    # Inherited from H-E1/H-M2
    K: int = 10
    seed: int = 42
    n_bootstrap: int = 1000
    n_questions: int = 98
    delta_auroc_gate: float = 0.03

    # Paths (relative to code/ dir)
    he1_code_dir: str = "../../h-e1/code"
    hm2_code_dir: str = "../../h-m2/code"
    he1_results_dir: str = "../../h-e1/results"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"

    # H-M3 specific: SCG BERTScore
    rescale_with_baseline: bool = True
