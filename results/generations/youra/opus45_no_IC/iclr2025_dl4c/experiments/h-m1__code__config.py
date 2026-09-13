"""Configuration for H-M1 experiment: Execution Trace -> Token Classification."""

DATA_CONFIG = {
    "humaneval_dataset": "openai/openai_humaneval",
    "mbpp_dataset": "google-research-datasets/mbpp",
    "mbpp_split": "test",
    "total_problems": 664,
    "model_name": "meta-llama/CodeLlama-7b-Instruct-hf",
    "max_new_tokens": 512,
    "generation_temperature": 0.2,
    "generation_top_p": 0.95,
    "device": "cuda",
    "dtype": "bfloat16",
}

PIPELINE_CONFIG = {
    "seed": 42,
    "trace_timeout_sec": 5.0,
    "overhead_bench_samples": 100,
    "batch_size": 1,
    "output_dir": "./outputs",
    "log_every": 50,
}

GATE_THRESHOLDS = {
    "accuracy_min": 0.95,
    "overhead_max": 20.0,
}
