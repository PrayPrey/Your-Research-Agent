"""Configuration for H-M2 Hedging Marker Detection experiment."""
import os

CONFIG = {
    "model": {
        "name": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 500,
    },
    "dataset": {
        "name": "truthful_qa",
        "config": "generation",
        "split": "validation",
        "n_items": 817,
    },
    "hedging": {
        "markers": [
            "might", "may", "could", "possibly", "perhaps", "uncertain",
            "unsure", "alternatively", "however", "although", "probably",
            "likely", "unlikely", "but", "not sure", "hard to say",
            "difficult to determine",
        ],
        "extended_markers": [
            "seem", "appears", "tends", "generally", "typically",
            "in some cases", "it depends", "not always", "sometimes",
            "often", "rarely", "approximately", "roughly", "around",
            "i think", "i believe", "in my opinion", "arguably",
        ],
        "confidence_split_markers": ["confidence:", "my confidence", "i am confident"],
        "presence_rate_threshold": 0.30,
    },
    "api": {
        "max_retries": 3,
        "backoff_base": 2,
        "timeout": 60,
    },
    "paths": {
        "cache_path": ".cache/responses.jsonl",
        "results_path": "results/h-m2_results.json",
        "summary_path": "results/summary.yaml",
        "figures_dir": "../figures",
    },
    "seed": 42,
}

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
