from dataclasses import dataclass

@dataclass(frozen=True)
class ExperimentConfig:
    seed: int = 42
    generator_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    n_samples: int = 10
    temperature: float = 0.7
    max_tokens: int = 256
    nli_model: str = "microsoft/deberta-large-mnli"
    entailment_threshold: float = 0.5
    bertscore_lang: str = "en"
    gate_threshold: float = 0.55
    n_bootstrap: int = 1000
    figures_dir: str = "figures"
    results_path: str = "results.json"

CONFIG = ExperimentConfig()
