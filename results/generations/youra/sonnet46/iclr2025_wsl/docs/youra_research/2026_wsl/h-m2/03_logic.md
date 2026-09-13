# Logic: H-M2

**hypothesis_id:** h-m2
**hypothesis_type:** MECHANISM
**gate:** SHOULD_WORK
**generated_at:** 2026-03-16

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified via direct Read (Serena project not active — fallback used)
**Analyzed Path**: `docs/youra_research/20260316_wsl/h-m1/code/src/`
**Relevant Symbols**:
- `evaluate_all_encoders(training_results, cfg, flat_test_loader, nft_test_loader, flat_input_dim, layer_fan_ins)` → `pd.DataFrame`
- `evaluate_gate_condition_v2(eval_df, delta_r2, cfg, gate_cfg, results_dir)` → `dict`
- `apply_holm_correction(p_values: list)` → `list` (already exists in h-m1)
- `build_encoder(encoder_name, flat_input_dim, layer_fan_ins, hidden_dim, d_model, n_heads)` → `nn.Module`
- `load_checkpoint(model, path, device)` → `nn.Module`
- `NFTEquivariantEncoder.forward(weight_matrices: list)` → `Tensor`  input: `list[(B, n_units_l, fan_in_l)]`
- `FlatMLPEncoder.forward(x: Tensor)` input: `(B, D)`

---

## External Dependencies API

**Verified from**: `h-m1/code/src/` actual code (NOT spec)

```python
# h-m1/code/src/evaluate.py
def evaluate_all_encoders(
    training_results: list,       # list[dict] with keys: encoder, seed, checkpoint_path
    cfg: ExperimentConfig,        # cfg.encoder_names must be filtered to 4 encoders
    flat_test_loader,
    nft_test_loader,
    flat_input_dim: int,
    layer_fan_ins: list,
) -> pd.DataFrame:
    """Returns DataFrame columns: [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value]
    48 rows when cfg.encoder_names has 4 encoders × 3 seeds × 4 severities."""

def apply_holm_correction(p_values: list) -> list:
    """Apply Holm-Bonferroni step-down. Returns corrected p-values in same order."""

# h-m1/code/src/models.py
def build_encoder(
    encoder_name: str,          # "flat-MLP", "flat-MLP+aug", "flat-MLP+canon", "NFT-base"
    flat_input_dim: int,
    layer_fan_ins: list,
    hidden_dim: int = 512,
    d_model: int = 128,
    n_heads: int = 4,
) -> nn.Module: ...

# h-m1/code/src/train.py
def load_checkpoint(model: nn.Module, path: str, device) -> nn.Module:
    """Loads 'model_state_dict' key from checkpoint dict."""
```

**sys.path setup** (required before any h-m1 import):
```python
import sys, os
HM1_CODE = os.path.abspath("docs/youra_research/20260316_wsl/h-m1/code")
sys.path.insert(0, HM1_CODE)
```

---

## A-5: Bootstrap Statistical Tests [Complexity: 14, Budget: 4 subtasks]

Applied: Standard PyTorch evaluation patterns with scipy bootstrap

### API Signatures

```python
# h-m2/code/src/gate_evaluator.py

def run_paired_bootstrap(
    y_pred_a: np.ndarray,      # (N,) predictions from encoder A (e.g. flat-MLP+aug)
    y_pred_b: np.ndarray,      # (N,) predictions from encoder B (e.g. NFT-base)
    y_true: np.ndarray,        # (N,) ground-truth labels
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> dict:
    """Paired bootstrap test: H0: rho(A) == rho(B).
    Returns: {p_value, ci_lower, ci_upper, delta_rho_obs, delta_rho_mean}
    """
    ...

def apply_holm_correction(p_values: list[float], alpha: float = 0.05) -> list[float]:
    """Holm-Bonferroni step-down correction.
    Returns corrected p-values in same order as input.
    Note: h-m1 already implements this; h-m2 wraps it for local import convenience.
    """
    ...

def compute_cohens_d(
    delta_rho_a: np.ndarray,   # (n_bootstrap,) bootstrap Δρ samples for encoder A
    delta_rho_b: np.ndarray,   # (n_bootstrap,) bootstrap Δρ samples for encoder B
) -> float:
    """Cohen's d = (mean_a - mean_b) / pooled_std."""
    ...

def format_p_value_report(
    bootstrap_results: dict,
    corrected_p_values: list[float],
    encoder_pairs: list[tuple],
) -> str:
    """Format bootstrap results as human-readable string for stdout."""
    ...
```

### Pseudo-code (bootstrap loop)

```
run_paired_bootstrap(y_pred_a, y_pred_b, y_true, n_bootstrap, seed):
    rng = np.random.default_rng(seed)
    N = len(y_true)
    obs_delta = spearmanr(y_pred_a, y_true).correlation - spearmanr(y_pred_b, y_true).correlation
    boot_deltas = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integers(0, N, size=N)
        rho_a = spearmanr(y_pred_a[idx], y_true[idx]).correlation
        rho_b = spearmanr(y_pred_b[idx], y_true[idx]).correlation
        boot_deltas[i] = rho_a - rho_b
    p_value = float(np.mean(boot_deltas <= 0))  # one-sided: P(Δρ_a > Δρ_b)
    ci_lower = float(np.percentile(boot_deltas, 2.5))
    ci_upper = float(np.percentile(boot_deltas, 97.5))
    return {p_value, ci_lower, ci_upper, delta_rho_obs, delta_rho_mean, boot_deltas}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | bootstrap_fn | `run_paired_bootstrap()` implementation |
| L-5-2 | holm_correction | `apply_holm_correction()` wrapper (delegates to h-m1 or re-implements) |
| L-5-3 | cohens_d | `compute_cohens_d()` from bootstrap sample arrays |
| L-5-4 | p_value_report | `format_p_value_report()` for stdout gate summary |

---

## A-6: H-M2 Gate Evaluator [Complexity: 12, Budget: 4 subtasks]

Applied: Standard PyTorch evaluation patterns with scipy bootstrap

### API Signatures

```python
# h-m2/code/src/gate_evaluator.py

AUG_THRESHOLD   = 0.05
CANON_THRESHOLD = 0.03
NFT_THRESHOLD   = 0.02
ENCODERS_HM2    = ["flat-MLP", "flat-MLP+aug", "flat-MLP+canon", "NFT-base"]

# H-M1 known values for consistency check
HM1_KNOWN = {
    "NFT-base":      {"delta_rho": 4.71e-7},
    "flat-MLP+aug":  {"delta_rho": 0.2239},
}

def evaluate_gate_hm2(eval_df: pd.DataFrame) -> dict:
    """SHOULD_WORK gate: three-way ranking at s=1.0.

    Input:  DataFrame with cols [encoder, seed, severity, rho, delta_rho, ...]
    Output: {aug_partial, canon_partial, nft_superior, ranking, passed,
             mean_dr_by_encoder, gate_summary, gate_type}
    """
    ...

def check_checkpoint_consistency(
    eval_df: pd.DataFrame,
    expected: dict = HM1_KNOWN,
    tolerance: float = 0.01,
) -> dict:
    """Verify loaded checkpoint Δρ within ±tolerance of H-M1 known values.
    Returns: {nft_consistent, aug_consistent, passed, details}
    """
    ...

def _validate_ranking(mean_dr: dict) -> bool:
    """Check strict ranking: NFT-base < flat-MLP+canon < flat-MLP+aug < flat-MLP."""
    ...

def _build_gate_summary(
    mean_dr: dict,
    aug_partial: bool,
    canon_partial: bool,
    nft_superior: bool,
    ranking: bool,
    passed: bool,
) -> str:
    """Format multi-line gate summary string for stdout."""
    ...
```

### Pseudo-code (gate logic)

```
evaluate_gate_hm2(eval_df):
    s1_df = eval_df[eval_df.severity == 1.0]
    mean_dr = {enc: s1_df[s1_df.encoder==enc].delta_rho.mean() for enc in ENCODERS_HM2}
    aug_partial   = mean_dr["flat-MLP+aug"]  > AUG_THRESHOLD     # > 0.05
    canon_partial = mean_dr["flat-MLP+canon"] > CANON_THRESHOLD   # > 0.03
    nft_superior  = mean_dr["NFT-base"]       < NFT_THRESHOLD     # < 0.02
    ranking       = _validate_ranking(mean_dr)
    passed        = aug_partial and canon_partial and nft_superior and ranking
    return {aug_partial, canon_partial, nft_superior, ranking, passed,
            mean_dr_by_encoder: mean_dr, gate_summary: _build_gate_summary(...), gate_type: "SHOULD_WORK"}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | gate_fn | `evaluate_gate_hm2()` main logic |
| L-6-2 | consistency_check | `check_checkpoint_consistency()` vs H-M1 known values |
| L-6-3 | gate_summary | `_build_gate_summary()` formatted stdout string |
| L-6-4 | ranking_validation | `_validate_ranking()` strict four-way rank check |

---

## A-4: Multi-Severity Evaluation [Complexity: 11, Budget: 3 subtasks]

Applied: Standard PyTorch evaluation patterns with scipy bootstrap

### API Signatures

```python
# h-m2/code/run_experiment_hm2.py

HM1_CKPT_ROOT  = "docs/youra_research/20260316_wsl/h-m1/code/checkpoints"
ENCODERS_HM2   = ["flat-MLP", "flat-MLP+aug", "flat-MLP+canon", "NFT-base"]
SEEDS          = [42, 123, 456]
SEVERITIES     = [0.0, 0.25, 0.5, 1.0]
SPLIT_SEED     = 42

def run_hm2_evaluation(
    encoders: list[str],       # ENCODERS_HM2
    checkpoints: dict,         # {(encoder_name, seed): ckpt_path}
    zoo_data: dict,            # loaded zoo_enriched.pkl dict
    flat_test_loader,
    nft_test_loader,
    flat_input_dim: int,
    layer_fan_ins: list[int],
    cfg: "ExperimentConfig",   # encoder_names filtered to ENCODERS_HM2
    device: torch.device,
) -> pd.DataFrame:
    """Evaluate 4 encoders × 4 severities × 3 seeds = 48 rows.
    Delegates to evaluate_all_encoders() from h-m1.
    Returns DataFrame: [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value]
    """
    ...

def build_training_results_from_checkpoints(
    ckpt_root: str,
    encoders: list[str],
    seeds: list[int],
) -> list[dict]:
    """Build training_results list from pre-existing checkpoints (no training).
    Each dict: {encoder, seed, checkpoint_path, final_val_loss: nan}
    Checkpoint naming: {enc.replace('+','plus')}_seed{seed}.pt
    """
    ...

def load_encoder_from_checkpoint(
    encoder_name: str,
    seed: int,
    ckpt_root: str,
    flat_input_dim: int,
    layer_fan_ins: list[int],
    device: torch.device,
) -> nn.Module:
    """Load single encoder from h-m1 checkpoint. Returns model in eval mode."""
    ...
```

### Tensor Shapes

| Variable | Shape | Context |
|----------|-------|---------|
| flat input x | (B, D) | D = flattened weight dim (~7850 for MNIST zoo) |
| NFT input per layer | (B, n_units_l, fan_in_l) | list length = num layers |
| preds | (B,) after squeeze(-1) | output of model.forward() |
| y_true | (B,) | generalization gap labels |

NFT example for 2-layer MNIST model (784→64→10):
- Layer 0: `(B, 64, 784)` — weight matrix rows as tokens
- Layer 1: `(B, 10, 64)`

### Pseudo-code

```
run_hm2_evaluation(...):
    training_results = build_training_results_from_checkpoints(ckpt_root, encoders, seeds)
    cfg.encoder_names = encoders  # restrict to 4 HM2 encoders
    eval_df = evaluate_all_encoders(
        training_results, cfg,
        flat_test_loader, nft_test_loader,
        flat_input_dim, layer_fan_ins
    )
    assert len(eval_df) == 48, f"Expected 48 rows, got {len(eval_df)}"
    return eval_df
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | run_eval_fn | `run_hm2_evaluation()` delegating to h-m1 `evaluate_all_encoders()` |
| L-4-2 | tensor_specs | `load_encoder_from_checkpoint()` with correct path mapping |
| L-4-3 | checkpoint_loader | `build_training_results_from_checkpoints()` path construction |

---

## Budget Summary

| Task | Subtasks Used | Budget |
|------|--------------|--------|
| A-5  | 4 | 4 |
| A-6  | 4 | 4 |
| A-4  | 3 | 3 |
| **Total** | **11** | **11** |

*Hypothesis type: MECHANISM | Gate: SHOULD_WORK | H-M1 reuse via sys.path*
