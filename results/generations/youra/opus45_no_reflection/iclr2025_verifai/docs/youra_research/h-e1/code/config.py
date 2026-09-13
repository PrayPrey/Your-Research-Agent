"""H-E1 Configuration: AS Components Measurability PoC"""

CONFIG = {
    # Datasets
    "dataset_humaneval": "openai/openai_humaneval",
    "dataset_mbpp": "mbpp",

    # Sampling
    "sample_size": 100,
    "random_seed": 42,

    # Signal generation
    "conditions": ["C1", "C2", "C3", "C4", "C5", "C6"],
    "llm_temp": 0.7,
    "max_truncate_frames": 3,

    # Extraction gate
    "extraction_rate_target": 0.95,
    "correlation_threshold": 0.5,

    # Output
    "output_dir": "outputs",
    "figures_dir": "../figures",
}
