"""Configuration for H-E1 Mode 3 Existence Experiment."""

CONFIG = {
    "dataset_id": "lmsys/lmsys-arena-human-preference-55k",
    "rm_models": {
        "openassistant": "OpenAssistant/reward-model-deberta-v3-large-v2",
        "pairrm": "llm-blender/PairRM",
        "armorm": "RLHFlow/ArmoRM-Llama3-8B-v0.1",
    },
    "use_armorm": True,
    "batch_size": 8,
    "output_dir": "outputs/",
    "scores_cache_path": "outputs/rm_scores.parquet",
    "mode_dist_path": "outputs/mode_distribution.json",
    "stats_path": "outputs/statistical_results.json",
    "valid_winners": ["model_a", "model_b", "tie", "tie (bothbad)"],
    "binomial_p0": 0.10,
    "sensitivity_thresholds": [0.05, 0.08, 0.10],
    "use_cluster_entropy_fallback": False,
    "seed": 42,
}
