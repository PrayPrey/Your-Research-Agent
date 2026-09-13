# Config: h-e1 (EXISTENCE PoC)

Applied: single fixed-config PoC pattern (no grid, no ablations, 1 seed)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict

---

## A-9: NLI Model Configuration [Complexity: 1, Budget: 1]

**Applied**: Standard PyTorch/HF defaults for zero-shot NLI scoring (used by both semantic_entropy clustering and SelfCheckNLI)

### Configuration (Hardcoded Dict)

```python
# code/config.py
CONFIG = {
    # Reproducibility
    "seed": 42,

    # Generation model
    "model_id": "meta-llama/Meta-Llama-3-8B-Instruct",
    "dtype": "bfloat16",
    "device_map": "auto",
    "max_new_tokens": 256,

    # Sampling for semantic entropy / SelfCheckGPT
    "num_samples": 10,          # N samples for semantic entropy
    "selfcheck_k_samples": 5,   # K samples for SelfCheckGPT (FR-6)
    "temperature": 0.7,

    # NLI model (shared: semantic entropy clustering + SelfCheckNLI)
    "nli_model_id": "microsoft/deberta-v3-large",
    "nli_dtype": "float32",     # Non-standard: NLI scoring needs full precision for stable entailment probs
    "nli_max_length": 512,

    # Evaluation
    "auroc_threshold": 0.55,

    # Dataset
    "dataset_name": "truthful_qa",
    "dataset_config": "multiple_choice",
    "cache_dir": ".cache",

    # Output
    "results_dir": "docs/youra_research/h-e1/code/results",
    "figures_dir": "docs/youra_research/h-e1/figures",
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-9-1 | NLI model config entry | Add `nli_model_id`, `nli_dtype`, `nli_max_length` to shared CONFIG dict for use in semantic_entropy clustering (A-4) and SelfCheckNLI (A-5) |
