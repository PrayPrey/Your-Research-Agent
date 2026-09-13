import os

CONFIG = {
    "models": [
        "codellama/CodeLlama-7b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
        "gpt-4",
    ],
    "openai_models": {"gpt-4"},
    "benchmarks": ["humaneval", "mbpp"],
    "benchmark_datasets": {
        "humaneval": "evalplus/humanevalplus",
        "mbpp": "evalplus/mbppplus",
    },
    "temperature": 0.0,
    "max_new_tokens": 512,
    "batch_size": 1,
    "seed": 42,
    "torch_dtype": "float16",
    "device_map": "auto",
    "max_repair_attempts": 5,
    "prompt_formats": ["structured", "raw"],
    "exec_timeout_sec": 3.0,
    "eval_k": [1],
    "n_workers": 4,
    "openai_max_retries": 5,
    "openai_backoff_base_sec": 2.0,
    "results_path": "outputs/results.json",
    "figures_dir": "outputs/figures/",
}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
