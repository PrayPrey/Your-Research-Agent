import os

CONFIG = {
    "judge_model": "gpt-4",
    "judge_provider": "openai",
    "temperature": 0.0,
    "max_tokens": 500,
    "fields": ["line_number", "error_type", "error_message", "code_context"],
    "min_samples": 500,
    "accuracy_threshold": 0.95,
    "pass_rate_threshold": 0.90,
    "max_retries": 5,
    "backoff_base_sec": 2.0,
    "error_pairs_path": "data/error_pairs.json",
    "results_path": "outputs/results.json",
    "figures_dir": "outputs/figures/",
}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
