# Config: H-M2 (MECHANISM — prediction-level invariance, no training)

**Applied**: Archon KB search ("DL config patterns") returned only unrelated PyTorch inductor config (low relevance) — reused H-M1's hardcoded-dict pattern for property/inference-only tests.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: No H-M2 config file exists yet (new file). H-M1's actual code inspected via architecture doc's Serena findings — confirms `generate_test_mlp` defaults (input_dim=3072, hidden=[64,64], not PRD's stale "32-32-32-10").
**Config Files Found**: None for H-M2 (green-field file) — reusing `h-m1/code/` modules directly, no local config.py in h-m1/code either (H-M1 uses inline CONFIG dict in its script, not a separate config.py)
**Pattern Used**: dict (matches H-M1)

---

## Configuration (Hardcoded Dict)

Single fixed config — no hyperparameter tuning, pure property test extending H-M1 to prediction level.

```python
CONFIG = {
    # Test MLP generation (P-3) — reuse H-M1 defaults unchanged
    "test_seed": 42,
    "input_dim": 3072,        # CIFAR-10 flattened; PRD's "32-32-32-10" is stale, trust H-M1 code
    "hidden_sizes": [64, 64],
    "output_dim": 10,

    # Permutations (P-4)
    "n_perms": 10,

    # NFN model loading (P-2) — inherited from H-E1 via H-M1
    "nfn_channels": 32,
    "checkpoint_path": "../../h-e1/checkpoints/nfn_model.pt",

    # Gate threshold (P-5) — same as H-M1's dev_threshold
    "dev_threshold": 1e-5,

    # sys.path injection (P-1)
    "h_m1_code_dir": "../../h-m1/code",
    "h_e1_code_dir": "../../h-e1/code",

    # Output paths
    "results_path": "../results.json",
    "figure_dir": "../figures",
}
```

### Subtasks
None — budget is 0 subtasks (all Epics Low complexity, per task allocation).

---

## Inherited Configuration (Base Hypothesis: H-M1)

H-M2 has no separate config.py in H-M1's code — H-M1 uses an inline `CONFIG` dict (verified: no `config*.py` file found under `h-m1/code/`, per Serena Glob). Relevant fields reused directly above (`test_seed`, `input_dim`, `hidden_sizes`, `output_dim`, `n_perms`, `nfn_channels`, `checkpoint_path`, `dev_threshold`).

Transitively inherited from H-E1 (`h-e1/code/config.py`, actual `@dataclass Config`):

```python
@dataclass
class Config:
    nfn_channels: int = 32      # <- reused for NFN reconstruction/checkpoint loading
    # other fields (lr, epochs, batch_size, etc.) irrelevant — no training in H-M2
```

**Verified from**: `docs/youra_research/h-m1/code/` (no config.py — inline dict pattern) and `docs/youra_research/h-e1/code/config.py` (actual implementation, transitively via H-M1's 03_config.md).
