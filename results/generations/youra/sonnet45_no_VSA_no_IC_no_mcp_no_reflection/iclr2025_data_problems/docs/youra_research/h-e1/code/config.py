# Configuration for H-E1 Quality Metrics Correlation Study

CONFIG = {
    # Dataset
    "dataset_name": "allenai/c4",
    "dataset_split": "en",
    "subset_size_gb": 10,
    "num_subsets": 12,

    # Quality dimensions (3 levels per dimension)
    "quality_dimensions": {
        "deduplication": ["low", "medium", "high"],
        "domain_diversity": ["low", "medium", "high"],
        "perplexity": ["low", "medium", "high"],
        "token_efficiency": ["low", "medium", "high"]
    },

    # Quality metrics computation
    "ngram_size": 13,
    "perplexity_model": "gpt2",
    "perplexity_batch_size": 128,

    # Density metrics computation
    "embedder_model": "all-MiniLM-L6-v2",
    "semantic_sample_size": 1000,

    # Statistical analysis
    "correlation_threshold_r": 0.5,
    "significance_threshold_p": 0.01,
    "reproducibility_cv_threshold": 0.10,

    # Reproducibility
    "seed": 42,
    "num_reproducibility_samples": 3,

    # Compute
    "device": "cuda",

    # Output paths
    "output_dir": "results/",
    "data_dir": "data/subsets/",
    "plots_dir": "results/plots/"
}
