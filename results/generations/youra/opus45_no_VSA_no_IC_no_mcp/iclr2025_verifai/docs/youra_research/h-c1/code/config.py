import os
import sys

h_e1_code = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../h-e1/code'))
if h_e1_code not in sys.path:
    sys.path.insert(0, h_e1_code)

CONFIG = {
    "models": [
        "codellama/CodeLlama-7b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
        "gpt-4",
    ],
    "model_keys": {
        "codellama/CodeLlama-7b-Instruct-hf": "7B",
        "codellama/CodeLlama-34b-Instruct-hf": "34B",
        "gpt-4": "gpt4",
    },
    "openai_models": {"gpt-4"},
    "benchmarks": ["humaneval", "mbpp"],
    "benchmark_datasets": {
        "humaneval": "evalplus/humanevalplus",
        "mbpp": "evalplus/mbppplus",
    },
    "prompt_formats": ["structured", "raw"],
    "temperature": 0.0,
    "max_new_tokens": 1024,
    "batch_size": 1,
    "seed": 42,
    "torch_dtype": "float16",
    "device_map": "auto",
    "max_iterations": 3,
    "exec_timeout_sec": 3.0,
    "eval_k": [1],
    "n_workers": 4,
    "openai_max_retries": 5,
    "openai_backoff_base_sec": 2.0,
    "openai_rate_limit_rps": 2.0,
    "stats": {
        "alpha": 0.05,
        "correction_method": "fdr_bh",
        "anova_ss_type": 3,
        "effect_size": "eta_squared",
        "contrast_effect_size": "cohens_d",
        "ci_level": 0.95,
        "planned_contrasts": "monotonic_ordering",
    },
    "cache_dir": "outputs/cache/",
    "cache_enabled": True,
    "results_path": "outputs/results.json",
    "figures_dir": "outputs/figures/",
}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
