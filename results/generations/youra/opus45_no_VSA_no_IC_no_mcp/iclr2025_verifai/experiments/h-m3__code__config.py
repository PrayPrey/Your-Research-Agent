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
    # H-M3 additions
    "fix_levels": [0, 1, 2, 3],
    "n_repetitions": 3,
    "level_order_seed": 42,
    "target_error_instances": 500,
    "repairable_error_types": ["syntax", "type", "runtime", "semantic"],
    "max_repair_attempts_leveled": 3,
    "quadratic_formula": "success ~ level + I(level**2)",
    "quad_pval_threshold": 0.05,
    "results_path_hm3": "outputs/h-m3_results.json",
    "figures_dir_hm3": "outputs/h-m3_figures/",
    "raw_instances_path": "outputs/error_instances.json",
    "log_level": "INFO",
    "log_path": "outputs/h-m3_run.log",
}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
