"""Configuration for H-M2: Proof Depth Filtering Analysis."""

RANDOM_SEED = 42

# Prover configuration
PROVER_CONFIG = {
    "pass_k": 16,
    "timeout_seconds": 60,
    "max_tokens": 1024,
    "temperature": 0.0,  # Greedy for reproducibility
}

# Dataset configuration
DATASET_CONFIG = {
    "name": "miniF2F",
    "split": "test",
    "total_theorems": 244,
    "source_url": "https://github.com/google-deepmind/miniF2F",
    "lean_version": "v4.14.0",
    "mathlib_compatible": True,
}

# Depth threshold configuration
DEPTH_CONFIG = {
    "shallow_max": 3,
    "medium_max": 10,
    "min_solved_required": 30,
}

# Statistical analysis configuration
STATISTICAL_CONFIG = {
    "bootstrap_samples": 10000,
    "confidence_level": 0.95,
    "mcnemar_alpha": 0.05,
}

# Logging configuration
LOGGING_CONFIG = {
    "verbosity": "INFO",
    "output_dir": "./results",
    "proof_log": "proofs.json",
    "tactic_counts": "tactic_counts.csv",
    "results_file": "results.json",
    "histogram_file": "depth_histogram.png",
    "progress_interval": 10,
}

# Validation configuration
VALIDATION_CONFIG = {
    "spot_check_fraction": 0.1,
    "min_accuracy": 0.8,
}

# Gate criteria (SHOULD_WORK)
GATE_CRITERIA = {
    "delta_min": 0.05,
    "delta_max": 0.30,
    "target_delta": 0.15,
}


def validate_config():
    """Validate configuration constraints."""
    assert PROVER_CONFIG["pass_k"] >= 1, "pass_k must be >= 1"
    assert PROVER_CONFIG["timeout_seconds"] > 0, "timeout must be positive"
    assert PROVER_CONFIG["max_tokens"] > 0, "max_tokens must be positive"
    assert 0.0 <= PROVER_CONFIG["temperature"] <= 1.0, "temperature in [0, 1]"

    assert DATASET_CONFIG["total_theorems"] == 244, "miniF2F test has 244 theorems"

    assert DEPTH_CONFIG["shallow_max"] > 0, "shallow_max must be positive"
    assert DEPTH_CONFIG["medium_max"] > DEPTH_CONFIG["shallow_max"], "medium > shallow"
    assert DEPTH_CONFIG["min_solved_required"] >= 30, "Need >=30 for statistical power"

    assert STATISTICAL_CONFIG["bootstrap_samples"] >= 1000, "Need >=1000 bootstrap samples"
    assert 0.0 < STATISTICAL_CONFIG["confidence_level"] < 1.0, "CI in (0, 1)"
    assert 0.0 < STATISTICAL_CONFIG["mcnemar_alpha"] < 1.0, "alpha in (0, 1)"

    assert 0.0 < VALIDATION_CONFIG["spot_check_fraction"] <= 1.0, "fraction in (0, 1]"
    assert 0.0 < VALIDATION_CONFIG["min_accuracy"] <= 1.0, "accuracy in (0, 1]"

    assert GATE_CRITERIA["delta_min"] < GATE_CRITERIA["delta_max"], "min < max"
    assert GATE_CRITERIA["delta_min"] <= GATE_CRITERIA["target_delta"] <= GATE_CRITERIA["delta_max"], "target in range"
