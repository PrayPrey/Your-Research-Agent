import os

RAFF_CSV_PATH: str = "data/raff_corpus.csv"

HF_FIELDS: list[str] = [
    "intended_use",
    "out_of_scope_use",
    "limitations",
    "license",
    "task_categories",
    "dataset_info",
    "provenance",
]

THRESHOLDS: dict = {
    "hf_coverage_rate": 0.50,
    "openml_temporal_filter_success_rate": 0.70,
}

HF_RATE_LIMIT_SEC: float = 1.0
RESULTS_DIR: str = "results"
HF_TOKEN: str | None = os.environ.get("HF_TOKEN", None)

VIZ_CONFIG = {
    "gate_metrics_bar": {
        "figsize": (7, 4),
        "colors": {"pass": "#2ecc71", "fail": "#e74c3c"},
        "threshold_linestyle": "--",
        "threshold_color": "black",
        "threshold_linewidth": 1.5,
        "ylabel": "Rate",
        "title": "Gate Metrics vs Thresholds",
    },
    "hf_field_heatmap": {
        "figsize": (12, 8),
        "cmap": "YlGn",
        "xticklabel_rotation": 45,
        "yticklabel_fontsize": 8,
        "title": "HF Field Presence per Dataset",
    },
    "openml_run_histogram": {
        "figsize": (8, 4),
        "bins": 20,
        "xlabel": "Pre-publication OpenML run count",
        "ylabel": "Number of datasets",
        "title": "OpenML Pre-publication Run Distribution",
    },
    "dataset_freq_bar": {
        "figsize": (12, 5),
        "top_n": 30,
        "xlabel_rotation": 45,
        "ylabel": "Paper count",
        "title": "Dataset Frequency in Raff Corpus (Top 30)",
    },
}
