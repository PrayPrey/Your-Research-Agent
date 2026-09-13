# Configuration: H-E1 (Benchmark Independence Verification)

**Type**: EXISTENCE (PoC) — single fixed config, no hyperparameter search.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: Hardcoded dict

**Applied**: Standard PyTorch/HuggingFace defaults (fp16 inference config)

---

## Configuration

```python
CONFIG = {
    # Model
    "model_name": "meta-llama/Llama-2-7b-hf",
    "device": "cuda",
    "dtype": "float16",          # bf16 also fine; fp16 chosen for widest GPU support

    # Datasets
    "datasets": {
        "truthfulqa": {
            "path": "truthful_qa",
            "subset": "multiple_choice",
            "split": "validation",
            "n_samples": 817,     # full set
        },
        "hhh_helpful": {
            "path": "Anthropic/hh-rlhf",
            "subset": "helpful-base",
            "split": "test",
            "n_samples": None,    # None = full eval split
        },
        "hhh_harmless": {
            "path": "Anthropic/hh-rlhf",
            "subset": "harmless-base",
            "split": "test",
            "n_samples": None,    # None = full eval split
        },
    },

    # Evaluation
    "batch_size": 8,
    "max_new_tokens": 128,        # only used if generation needed for preference scoring
    "seed": 42,

    # Analysis
    "correlation_method": "pearson",
    "correlation_threshold": 0.5,   # gate: all pairwise |r| < 0.5

    # Output
    "figures_dir": "h-e1/figures/",
    "results_file": "h-e1/results/correlation_results.json",
}
```

### Subtasks

PoC — no subtask decomposition (single script: load model → eval 3 benchmarks → compute correlations → plot).

---

## Environment Requirements

- **GPU**: ~14GB VRAM (fp16 Llama-2-7B inference)
- **Packages**: `torch`, `transformers`, `datasets`, `accelerate`, `scipy` (pearsonr), `pandas`, `matplotlib`, `seaborn` (heatmap)
- **HF auth**: `huggingface-cli login` required (gated Llama-2 weights)
