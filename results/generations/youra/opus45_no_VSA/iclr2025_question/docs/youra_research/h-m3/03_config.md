# Config: h-m3 (MECHANISM)

Applied: Standard PyTorch/HF fixed-config dict pattern (no KB match for RCI-specific config; used general experiment config conventions).

## Codebase Analysis (Serena)

**Project Type**: green-field (h-e1/code/ does not exist on disk; no base config classes to verify)
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: hardcoded dict (single fixed config, no dataclass needed — mechanism verification run, no hyperparameter search)

---

## M-1: Setup & config [Complexity: 4, Budget: 0 subtasks]

**Applied**: Standard fixed-config dict (matches architecture's `config.py` spec exactly)

### Configuration (Hardcoded Dict)

```python
# code/config.py
CONFIG = {
    "seed": 42,
    "model_id": "meta-llama/Llama-2-7b-hf",
    "device": "cuda",
    "torch_dtype": "float16",
    "layer_range": (24, 32),      # inclusive, 9 layers (25..32 incl. embedding offset handled in rci.py)
    "batch_size": 1,               # NFR-2: hidden state extraction is single-sample
    "temperature": 0.0,            # greedy decode for hallucination labeling
    "dataset": "truthful_qa",
    "dataset_config": "multiple_choice",  # MC1
    "n_samples": 817,

    # Gate thresholds (success criteria)
    "halluc_rate_threshold": 0.30,   # hallucination_flip_rate >= 0.30
    "correct_rate_threshold": 0.10,  # correct_flip_rate < 0.10
    "separation_threshold": 0.20,    # separation >= 0.20

    "figures_dir": "figures/",
}
```

- All values sourced directly from PRD success criteria and architecture `config.py` — no tuning performed (mechanism verification, not training).
- `layer_range=(24, 32)` and thresholds are fixed per hypothesis spec, not swept.

### Subtasks [0/0 used]

None — complexity 4, single fixed config, no decomposition needed.

---

## Notes

- No YAML needed; single run, no CLI overrides required (NFR-1: reproducibility via fixed seed only).
- No training config (no optimizer/scheduler/epochs) — this is inference-only mechanism analysis.
- `dataclass` format skipped in favor of dict per PoC/mechanism-verification brevity (matches architecture's literal `config.py` module-level constants style).
