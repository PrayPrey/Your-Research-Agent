# Config: H-E1 (EXISTENCE)

Applied: fixed-single-config-poc (single hardcoded config, no grid/variants — EXISTENCE gate)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: hardcoded dict (module-level constants), per architecture.md

---

## Config (`code/h-e1/config.py`)

```python
CONFIG = {
    # Models
    "MODEL_ID": "meta-llama/Llama-2-7b-hf",
    "EMBED_MODEL_ID": "sentence-transformers/all-MiniLM-L6-v2",
    "MODEL_DTYPE": "float16",
    "DEVICE_MAP": "auto",

    # Dataset
    "DATASET_ID": "truthfulqa/truthful_qa",
    "DATASET_SPLIT": "validation",   # generation config only has 'validation' split (817 rows)
    "DATASET_CONFIG": "generation",
    "CACHE_DIR": "data/h-e1_cache",

    # Generation / sampling
    "N_SAMPLES": 5,
    "TEMPERATURE": 1.0,
    "MAX_NEW_TOKENS": 128,

    # Labeling (BERTScore)
    "BERTSCORE_MODEL": "microsoft/deberta-xlarge-mnli",  # bert-score default
    "BERTSCORE_RESCALE": True,        # NFR: speed/stability per PRD risk mitigation
    "LABEL_MIN_BEST_SCORE": 0.5,      # FR-5.3 threshold

    # Evaluation
    "N_BOOTSTRAP": 1000,
    "SEED": 42,

    # Output
    "OUTPUT_DIR": "results/h-e1",
    "SCORES_CSV": "results/h-e1/scores.csv",
    "METRICS_JSON": "results/h-e1/metrics.json",
    "ROC_PLOT_PNG": "results/h-e1/roc_curves.png",
}
```

No hyperparameter sweep, no ablations, single seed — EXISTENCE gate tests signal presence only (PRD success criteria: entropy_AUROC > 0.55, consistency_AUROC > 0.55, CI lower > 0.50).

### Subtasks

0/0 used — task budget is constants-only, no subtask decomposition for config.
