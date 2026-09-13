# h-c3 Configuration
# Composition Contract Validation

DATASET_CONFIG = {
    "corpus_path": "../../h-e1/data/defect_corpus.csv",
    "category_filter": "composition",
    "expected_count": 68,
    "checksum": "6572aa34c06ecf13",
    "validate_on_load": True,
    "random_seed": 1
}

CONTRACT_CONFIG = {
    "types": [
        "device_placement",
        "tensor_layout",
        "cross_library_binding"
    ],
    "timeout_seconds": 10,
    "timeout_grace_period": 1,
    "version_tolerance": {
        "pytorch_minor": 2,
        "transformers_minor": 2,
        "cuda_compatible": True
    },
    "bidirectional_propagation": True,
    "propagation_modes": ["forward", "backward"],
    "pipeline_stages": [
        "dataset",
        "preprocess",
        "model",
        "output"
    ]
}

EVALUATION_CONFIG = {
    "target_detection_rate": 0.60,
    "baseline_detection_rate": 0.0,
    "confidence_level": 0.95,
    "ci_method": "wilson",
    "max_execution_time": 10,
    "false_positive_threshold": 0.05,
    "version_stability_target": 0.80,
    "gate_pass_threshold": 0.60,
    "gate_warning_threshold": 0.40
}

VERSION_CONFIG = {
    "test_mode": "version_stability",
    "version_deltas": [-2, -1, 0, 1, 2],
    "enforce_compatibility": True,
    "per_version_timeout": 10,
    "total_stability_timeout": 3600
}

VISUALIZATION_CONFIG = {
    "output_dir": "../figures",
    "format": "png",
    "dpi": 300,
    "figure_sizes": {
        "gate_metrics": (10, 6),
        "detection_by_type": (10, 6),
        "execution_time_dist": (10, 6),
        "version_stability_heatmap": (12, 8),
        "failure_propagation": (10, 10)
    },
    "colors": {
        "device_placement": "#3498db",
        "tensor_layout": "#f39c12",
        "cross_library_binding": "#9b59b6",
        "pass_threshold": "#2ecc71",
        "fail_threshold": "#e74c3c"
    },
    "gate_threshold": 0.60,
    "show_baseline": True,
    "show_ci_bars": True,
    "filenames": {
        "gate_metrics": "gate_metrics.png",
        "detection_by_type": "detection_by_type.png",
        "execution_time_dist": "execution_time_dist.png",
        "version_stability_heatmap": "version_stability_heatmap.png",
        "failure_propagation": "failure_propagation.png"
    }
}

OUTPUT_CONFIG = {
    "base_dir": "..",
    "results_dir": "../results",
    "figures_dir": "../figures",
    "logs_dir": "../logs",
    "result_files": {
        "composition_results": "../results/composition_results.csv",
        "version_stability": "../results/version_stability.csv",
        "false_positives": "../results/false_positives.csv",
        "metrics_summary": "../results/metrics_summary.json"
    },
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "save_logs": True
}

GLOBAL_CONFIG = {
    "hypothesis_id": "h-c3",
    "experiment_name": "composition_contract_validation",
    "experiment_type": "MECHANISM",
    "gate_type": "SHOULD_WORK",
    "random_seed": 1,
    "deterministic": True,
    "baseline_corpus": "../../h-e1/data/defect_corpus.csv",
    "baseline_contractability": 0.0,
    "max_execution_time": 10,
    "max_total_runtime": 900,
    "version_stability_window": 2,
    "poc_pass": {
        "detection_rate_improvement": True,
        "all_defects_processed": True,
        "execution_time_met": True
    },
    "gate_pass": {
        "detection_rate": 0.60,
        "version_stability": 0.80,
        "false_positive_rate": 0.05
    }
}
