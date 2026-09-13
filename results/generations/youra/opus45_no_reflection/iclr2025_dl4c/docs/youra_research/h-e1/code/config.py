"""Configuration for EVAF H-E1 experiment."""

CONFIG = {
    # Models
    "baseline_model_id": "Salesforce/codet5-large",
    "feedback_model_id": "codellama/CodeLlama-7b-Instruct-hf",
    "precision": "float16",
    "device": "cuda",

    # Generation
    "temperature": 0.2,
    "max_tokens": 512,
    "seed": 42,

    # Evaluation / gating
    "test_timeout_s": 3.0,

    # Data
    "dataset_name": "openai_humaneval",
    "dataset_split": "test",

    # Output paths
    "results_dir": "outputs/",
    "figures_dir": "outputs/figures/",
    "results_json": "outputs/results.json",
    "metrics_json": "outputs/metrics.json",
}
