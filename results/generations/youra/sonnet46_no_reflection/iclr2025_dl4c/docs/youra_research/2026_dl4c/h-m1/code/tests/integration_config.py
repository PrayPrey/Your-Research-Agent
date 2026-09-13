"""Integration test configuration for H-M1 smoke test."""

INTEGRATION_TEST_CONFIG = {
    "smoke_test_problems": 10,
    "smoke_test_pairs": 3,
    "max_runtime_seconds": 300,
    "required_sep_keys": ["sep_grpo", "sep_dpo", "pairs", "condition", "n_pairs"],
    "required_output_keys": ["sep_results", "stat_results", "gate", "config"],
    "sep_value_range": [0.0, 1.0],
    "required_gate_keys": ["satisfied", "detail", "effect_size", "type"],
    "required_stat_keys": ["mann_whitney", "spearman", "summary"],
}
