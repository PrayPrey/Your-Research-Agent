# Config: h-e1 (EXISTENCE PoC)

**Hypothesis**: NTI (layers 24-32) achieves AUROC > 0.55 on TruthfulQA MC1

**Applied**: No close KB pattern match (searched "DL config patterns" — top hits were latent-diffusion/pytorch-inductor/JAX, not applicable to this PoC). Using standard hardcoded-dict config per EXISTENCE rules.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (confirmed by architecture doc)
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict (single fixed config, no dataclass — EXISTENCE PoC, no variation needed)

---

## A-1: Setup & Config [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch/HF reproducibility defaults (fixed seed, single config, no grid).

### Configuration (Hardcoded Dict)

```python
# code/config.py
CONFIG = {
    "seed": 42,
    "model_id": "meta-llama/Llama-2-7b-hf",
    "device": "cuda",
    "dtype": "float16",
    "target_layers": (24, 32),   # inclusive layer range for NTI
    "n_folds": 5,
    "auroc_threshold": 0.55,      # gate: mean AUROC must exceed
    "min_fold_threshold": 0.52,   # gate: falsification boundary per fold
    "min_pass_rate": 0.8,         # gate: >=4/5 folds
    "dataset": "truthful_qa",
    "dataset_config": "multiple_choice",
    "figures_dir": "figures/",
    "batch_size": 8,              # inference batching, perf budget: 817 samples / 2hr
}
```

No hyperparameter search, no ablation configs, no alternate model IDs — single fixed run per EXISTENCE rules.

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | config.py | Define CONFIG dict above |
| C-1-2 | deps | requirements.txt (transformer_lens>=2.0, torch>=2.1, scikit-learn>=1.4, datasets, transformers) |
| C-1-3 | seeding | `torch.manual_seed`, `np.random.seed`, `random.seed` from CONFIG["seed"] at run.py entry |
| C-1-4 | dirs | Create `CONFIG["figures_dir"]` if not exists |

---

## Notes

- Single global CONFIG dict imported by all modules (data.py, model.py, evaluate.py, visualize.py, run.py) — matches architecture's `config.py` module-level constants approach.
- No dataclass used: EXISTENCE PoC has zero config variation, a dict is simpler and sufficient (per ladder: don't build a class for a value that never changes).
- No second subtask group added — A-1 (Setup & config) is the only task in this budget allocation (2 subtasks budget note in header refers to total document scope; all 4 A-1 subtasks are within its own complexity/budget=4).
