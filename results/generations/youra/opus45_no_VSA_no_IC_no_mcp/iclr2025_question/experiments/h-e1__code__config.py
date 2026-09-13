"""Configuration for H-E1 EXISTENCE experiment."""

CONFIG = {
    # Models
    "MODEL_ID": "meta-llama/Llama-2-7b-hf",
    "EMBED_MODEL_ID": "sentence-transformers/all-MiniLM-L6-v2",
    "MODEL_DTYPE": "float16",
    "DEVICE_MAP": "auto",

    # Dataset
    "DATASET_ID": "truthfulqa/truthful_qa",
    "DATASET_SPLIT": "validation",
    "DATASET_CONFIG": "generation",
    "CACHE_DIR": "data/h-e1_cache",

    # Generation / sampling
    "N_SAMPLES": 5,
    "TEMPERATURE": 1.0,
    "MAX_NEW_TOKENS": 128,

    # Labeling (BERTScore)
    "BERTSCORE_MODEL": "microsoft/deberta-xlarge-mnli",
    "BERTSCORE_RESCALE": True,
    "LABEL_MIN_BEST_SCORE": 0.5,

    # Evaluation
    "N_BOOTSTRAP": 1000,
    "SEED": 42,

    # Output
    "OUTPUT_DIR": "outputs",
    "SCORES_CSV": "outputs/scores.csv",
    "METRICS_JSON": "outputs/metrics.json",
    "ROC_PLOT_PNG": "outputs/roc_curves.png",
}
