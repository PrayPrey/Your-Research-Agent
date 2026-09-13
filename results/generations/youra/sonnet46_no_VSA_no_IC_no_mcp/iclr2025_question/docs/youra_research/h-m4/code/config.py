from dataclasses import dataclass


@dataclass
class Config:
    model_id: str = "meta-llama/Llama-2-7b-chat-hf"
    max_new_tokens: int = 80
    seed: int = 42
    n_bootstrap: int = 1000
    n_questions: int = 98
    parse_rate_gate: float = 0.80
    auroc_te_baseline: float = 0.4381270903010034
    auroc_se_baseline: float = 0.28595317725752506
    hm2_code_dir: str = "../../h-m2/code"
    hm3_results_path: str = "../../h-m3/results.json"
    he1_code_dir: str = "../../h-e1/code"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"
