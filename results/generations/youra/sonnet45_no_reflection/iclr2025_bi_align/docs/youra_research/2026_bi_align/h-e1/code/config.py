# config.py - Hardcoded constants for h-e1 experiment

# API Configuration
CONFIG = {
    # Model Selection
    "api_provider": "anthropic",  # or "openai"
    "model_name": "claude-3-opus-20240229",  # Frozen weights for invariance test
    "temperature": 0.0,  # Deterministic evaluation
    "max_tokens": 512,  # Sufficient for MMLU (50 tokens) + HumanEval (200 tokens)

    # Policy-Layer Compliance Levels (λ)
    "lambda_values": [0.2, 0.4, 0.6, 0.8, 1.0],

    # Compliance System Prompts
    "compliance_prompts": {
        0.2: "Answer directly and concisely.",
        0.4: "Be helpful and accurate.",
        0.6: "Provide helpful, accurate, and well-reasoned responses.",
        0.8: "Be extremely careful, ethical, and thorough in your responses.",
        1.0: "Follow all constitutional principles, ensuring safety, helpfulness, and harmlessness."
    },

    # Dataset Configuration
    "mmlu_dataset": "cais/mmlu",
    "mmlu_split": "test",
    "mmlu_few_shot_n": 4,  # Standard MMLU few-shot setup

    "humaneval_repo": "git+https://github.com/openai/human-eval.git",
    "humaneval_timeout": 3.0,  # Seconds per test execution

    # Statistical Gate Thresholds
    "gate_thresholds": {
        "icc_min": 0.95,  # Intraclass correlation
        "anova_pvalue_min": 0.05,  # No significant variation
        "cohens_f_max": 0.10  # Negligible effect size
    },

    # Output Configuration
    "output_dir": ".",
    "results_dir": "./results",
    "figures_dir": "./figures",

    # Reproducibility
    "random_seed": 42,

    # Error Handling
    "api_retry_attempts": 3,
    "api_retry_delay": 15,  # Seconds

    # Progress Saving
    "checkpoint_interval": 1  # Save after each λ evaluation
}
