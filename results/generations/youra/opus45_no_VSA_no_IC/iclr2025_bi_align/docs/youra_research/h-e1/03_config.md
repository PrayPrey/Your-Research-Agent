# Config: H-E1 (EXISTENCE)

Applied: Hardcoded dict pattern (PoC minimal config, no tuning)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict

---

## A-1..A-7: Single Fixed Pipeline Config [Budget: 0 subtasks]

**Applied**: Hardcoded dict pattern (PoC minimal config)

### Configuration (Hardcoded Dict)

```python
# config.py
CONFIG = {
    "dataset_id": "lmsys/chatbot_arena_conversations",
    "rm_models": {
        "openassistant": "OpenAssistant/reward-model-deberta-v3-large-v2",
        "pairrm": "llm-blender/PairRM",
        "armorm": "RLHFlow/ArmoRM-Llama3-8B-v0.1",
    },
    "use_armorm": True,       # FR-6: set False for 2-model fallback if VRAM insufficient
    "batch_size": 8,
    "output_dir": "outputs/",
    "scores_cache_path": "outputs/rm_scores.parquet",
    "mode_dist_path": "outputs/mode_distribution.json",
    "stats_path": "outputs/statistical_results.json",
    "valid_winners": ["model_a", "model_b", "tie", "tie (bothbad)"],
    "binomial_p0": 0.10,      # FR-5: H0 threshold
    "sensitivity_thresholds": [0.05, 0.08, 0.10],  # Risk mitigation: low Mode 3 count
    "use_cluster_entropy_fallback": False,  # FR-7: set True if model-pair IDs unavailable
    "seed": 42,
}
```

No hyperparameter tuning — this is a data analysis / statistical-test pipeline (EXISTENCE PoC), not a trainable model. Single fixed run, no grid, no ablation configs beyond the two documented fallbacks (FR-6, FR-7) which are boolean toggles in the same dict.

### Subtasks [0/0 used]

No subtask breakdown — budget is 0 (all tasks Low/High complexity handled directly by Coder per architecture's own breakdown column).
