"""Configuration for h-c1 domain boundary detection."""

import os

# Paths relative to h-c1/ directory (one level up from src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = {
    # Paths (External Dependencies)
    "kb_path": os.path.join(BASE_DIR, "../h-m1/data/pwc_cache/kb.yaml"),
    "boundary_test_path": os.path.join(BASE_DIR, "data/boundary_hypotheses.json"),
    "kb_domains_path": os.path.join(BASE_DIR, "data/kb_domain_taxonomy.json"),
    "output_dir": os.path.join(BASE_DIR, "data/"),
    "figures_dir": os.path.join(BASE_DIR, "figures/"),

    # Random Seeds
    "seed": 42,

    # Domain Boundary Detector
    "similarity_threshold": 0.7,
    "max_keywords": 5,

    # Gate Thresholds
    "gate_threshold": 0.80,
    "precision_threshold": 0.75,
    "recall_threshold": 0.80,

    # Visualization
    "format": "png",
    "dpi": 300,

    # Evaluation Metrics
    "metrics": ["accuracy", "precision", "recall", "f1"],
    "primary_metric": "accuracy",
}
