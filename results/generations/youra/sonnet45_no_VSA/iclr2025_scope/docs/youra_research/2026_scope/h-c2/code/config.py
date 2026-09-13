"""
Configuration for H-C2 Cross-Framework Contract Validation System
Hypothesis ID: h-c2
Phase: 4 - Implementation
"""

import torch

CONFIG = {
    # Contract settings
    "dtype_preservation_enabled": True,
    "shape_consistency_enabled": True,
    "numerical_tolerance_enabled": True,
    "operator_semantics_enabled": False,  # Disabled for PoC (too complex)

    # Numerical tolerances
    "default_rtol": 1e-5,
    "default_atol": 1e-7,
    "matmul_rtol": 1e-4,
    "matmul_atol": 1e-6,

    # Dataset (SIMPLIFIED for PoC - using synthetic only)
    "onnx_samples": 0,  # Disabled for PoC
    "crossedwires_sample": 0,  # Disabled for PoC
    "synthetic_samples": 100,  # Reduced for PoC
    "train_test_split": 0.70,
    "test_inputs_per_model": 3,  # Reduced for PoC

    # Frameworks
    "pytorch_version": "1.13.0",
    "tensorflow_version": "2.10.0",

    # Execution
    "timeout_per_contract": 2.0,
    "timeout_per_model": 10.0,
    "parallel_contracts": False,  # Disabled for PoC (simplicity)
    "max_workers": 1,

    # Baselines
    "run_no_validation": True,
    "run_end_to_end": True,

    # Metrics (SHOULD_WORK gate)
    "detection_rate_threshold": 0.70,
    "false_positive_threshold": 0.10,
    "precision_threshold": 0.80,
    "f1_threshold": 0.75,

    # Environment
    "seed": 42,
    "device": "cpu",  # Force CPU for reproducibility
    "log_level": "INFO",

    # Output
    "results_path": "experiment_results.json",
    "figures_dir": "figures/"
}
