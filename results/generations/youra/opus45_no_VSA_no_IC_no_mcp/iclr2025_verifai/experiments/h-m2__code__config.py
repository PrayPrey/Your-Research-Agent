import os

CONFIG = {
    "base_model_id": "codellama/CodeLlama-7b-Instruct-hf",
    "temperature": 0.8,
    "top_p": 0.95,
    "max_new_tokens": 512,
    "min_samples": 500,
    "bootstrap_replicas": 10000,
    "significance_alpha": 0.05,
    "sections": ["PROBLEM", "LOCATION", "CONTEXT", "ROOT_CAUSE"],
    "exec_timeout_sec": 5,
    "failed_samples_path": "data/failed_samples.json",
    "results_path": "data/paired_results.json",
    "figures_dir": "outputs/figures/",
}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
