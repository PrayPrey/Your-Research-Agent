# Configuration for h-e1 Experiment
# Semantic Entropy vs Ensemble Baseline

CONFIG = {
    # Data
    "dataset": "natural_questions",
    "split": "validation",
    "num_samples": 100,
    "filter_unanswerable": True,

    # Model
    "model_name": "mistralai/Mistral-7B-v0.1",
    "device": "cuda",
    "dtype": "float16",

    # Generation
    "k_samples": 10,  # K=10 from hypothesis
    "temperature": 0.7,  # Standard for diverse sampling
    "max_new_tokens": 50,  # Short answer format

    # Semantic Entropy
    "embedding_model": "all-MiniLM-L6-v2",  # From Kuhn et al. 2023
    "clustering_threshold": 0.5,  # Cosine similarity threshold

    # Experiment
    "seed": 42,
    "output_dir": "./figures",

    # Gate Thresholds
    "gate_auroc_min": 0.70,  # Absolute AUROC threshold
    "gate_difference_min": 0.07,  # AUROC_semantic - AUROC_ensemble threshold
}
