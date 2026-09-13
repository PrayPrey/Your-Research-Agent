"""Configuration for h-e1 attention entropy experiment."""

CONFIG = {
    # Model Configuration
    "model": {
        "name": "gpt2",  # Fallback to GPT-2 for CPU (Llama-2 too slow)
        "output_attentions": True,
        "torch_dtype": "float32",  # CPU requires float32
        "device_map": None,  # CPU only
        "attention_layer": -1,  # Last layer
        "aggregate_heads": True  # Average across attention heads
    },

    # NER Configuration (inherited from h-c1)
    "ner": {
        "model_name": "en_core_web_lg",  # Validated F1=0.96 in h-c1
        "entity_types": ["PERSON", "ORG", "GPE", "PRODUCT"]
    },

    # Data Configuration
    "data": {
        "entity_errors_path": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_buildingtrust/docs/youra_research/h-c1/code/data/truthfulqa_entity_subset/entity_errors.json",
        "non_entity_errors_path": "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_buildingtrust/docs/youra_research/h-c1/code/data/truthfulqa_entity_subset/non_entity_errors.json",
        "entity_error_samples": 50,
        "non_entity_error_samples": 50,
        "total_samples": 100
    },

    # Entropy Configuration
    "entropy": {
        "epsilon": 1e-10,  # Smoothing for log(0)
        "span_aggregation": "mean"  # Average entropy across entity tokens
    },

    # Statistical Testing
    "statistics": {
        "alpha": 0.05,  # Significance threshold
        "test_type": "one_tailed",  # entity < non-entity
        "effect_size": "cohens_d"
    },

    # Output Configuration
    "output": {
        "figures_dir": "./figures/",
        "results_file": "./results/entropy_results.json",
        "scores_file": "./results/entropy_scores.csv",
        "validation_report": "../04_validation.md",
        "figure_dpi": 300,
        "figure_format": "png"
    },

    # Reproducibility
    "seed": 42
}
