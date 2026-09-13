# Config: H-M3 (MECHANISM, PoC — negative control)

**Applied**: No relevant KB pattern (search returned unrelated diffusion/inductor docs) — used standard PyTorch defaults + H-M1 seed/threshold conventions.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Config classes verified from base code — H-M1 has no config dataclass/constants file (`test_data.py`/`permute.py`/`metrics.py` use inline function-argument defaults, no `@dataclass`). H-M3 follows the same hardcoded-dict style for consistency; no dataclass pattern to inherit.
**Config Files Found**: None — `h-m1/code/` has no `config*.py`
**Pattern Used**: Hardcoded dict (matches H-M1 style: plain function args, no config class)

---

## Q-1..Q-8: Variance Test Pipeline [Complexity: Low, Budget: 0 subtasks]

**Applied**: Standard PyTorch defaults; seeds/thresholds per PRD FR-1/FR-2/FR-3/FR-5, NFR-2.

### Configuration (Hardcoded Dict)

```python
CONFIG = {
    # test data (reused from H-M1 generate_test_mlp)
    "hidden_dims": (32, 32),
    "input_dim": 32,
    "output_dim": 10,
    "test_data_seed": 42,

    # MLPMatched model
    "mlp_hidden_dims": (256, 128),  # input_dim -> 256 -> 128 -> 1
    "mlp_init_seed": 1042,

    # permutations (reused from H-M1 generate_permutations)
    "n_hidden_layers": 2,
    "n_perms": 10,
    "perm_seeds": list(range(10)),  # 0-9

    # gate thresholds (opposite polarity vs H-M1/H-M2 invariance gate)
    "cv_threshold": 0.1,        # coefficient_of_variation > 0.1 -> pass
    "max_deviation_threshold": 0.01,  # max_deviation > 0.01 -> pass
}
```

No subtasks — all tasks Low complexity (budget 0).

---

## Inherited Configuration (Base Hypothesis H-M1)

No config class exists in H-M1 to inherit; H-M1 uses plain function defaults:
- `generate_test_mlp(hidden_dims=(32,32), input_dim=32, output_dim=10, seed=42)` — verified from `h-m1/code/test_data.py`
- `generate_permutations(hidden_dims, base_seed=0)` — verified from `h-m1/code/permute.py`
- `permute_state_dict(state_dict, n_hidden_layers=2, perms=...)` — verified from `h-m1/code/permute.py`

H-M3's `CONFIG` dict values above match these defaults exactly (test_data_seed=42, hidden_dims=(32,32)) so calls can pass `CONFIG["..."]` directly without renaming.

**Verified from**: `h-m1/code/test_data.py`, `h-m1/code/permute.py` (actual implementation, no `03_config.md` existed for H-M1 to cross-check).
