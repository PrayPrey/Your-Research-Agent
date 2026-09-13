# Logic Design: H-M3
# SymCanon-WSL — NFT with Weight Symmetry Canonicalization

**Hypothesis:** H-M3
**Generated:** 2026-08-27
**Source:** 03_architecture.md, 03_prd.md, h-m2/code (actual code analysis)

---

## Codebase Analysis (Serena)

**[NO-MCP MODE — Serena unavailable. Analysis via direct file read of h-m2/code/.]**

From `h-m2/code/data_prep.py` (actual implementation):
- `apply_condition_d(X)`: steps are scale-per-layer then sign-flip; W1 shape (N, 784, 64); W2 shape (N, 64, 10)
- Weight dim confirmed: `EXPECTED_DIM = 51850` (SPLITS=[50176, 64, 640, 10])
- `train_test_split_fixed(X, Y, test_size=50, seed=42)` — generic utility, reusable

From `h-m2/code/main.py`:
- No NFT trainer present in h-m2; training loop must come from h-m1 or be re-implemented
- Results stored as nested dict `results_a[label_name][k]`; H-M3 uses `results[condition][label_name]`

Applied: condition-registry pattern (dict mapping condition str → preprocessing fn)
Applied: seed-loop pattern (outer loop over seeds, inner loop over conditions)
Applied: BCa-bootstrap CI from scipy (standard for ρ evaluation)

---

## External Dependencies API

### From h-m2/code/data_prep.py (verified signatures)

```python
def apply_condition_d(X: np.ndarray) -> np.ndarray:
    """
    Args: X (N, 51850) float32 — raw weight vectors
    Returns: X_c (N, 51850) float32 — scaled + sign-flip canonicalized
    """

def train_test_split_fixed(
    X: np.ndarray,
    Y: np.ndarray,
    test_size: int = 50,
    seed: int = 42
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Returns: X_tr, X_te, Y_tr, Y_te"""

def load_and_flatten() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Returns: X (N, 51850), Y (N, 3), label_names"""
```

### From h-m1/code/data_loader.py (verified via h-m2 import)

```python
def load_zoo() -> list[dict]:
    """Returns list of dicts with keys: weights_flat (Tensor[51850]), test_accuracy, generalization_gap, learning_rate"""

SPLITS: list[int] = [50176, 64, 640, 10]  # W1_flat, b1, W2_flat, b2
EXPECTED_DIM: int = 51850
```

---

## Subtask L1: data_prep.py — apply_condition_b, apply_condition_c, apply_condition_e

**Parent Epic:** E1 (complexity 10)

```python
def apply_condition_b(X: np.ndarray) -> np.ndarray:
    """
    Condition B: scaling only — per-layer Frobenius norm normalization.
    Args: X (N, 51850) float32
    Returns: X_c (N, 51850) float32
    Tensor shapes intermediate:
        W1_flat: (N, 50176); norms_W1: (N, 1)
        W2_flat: (N, 640);   norms_W2: (N, 1)
    """
    X_c = X.copy()
    # W1 + b1
    norms_W1 = np.linalg.norm(X_c[:, :50176], axis=1, keepdims=True) + 1e-8
    X_c[:, :50176] /= norms_W1
    X_c[:, 50176:50240] /= norms_W1
    # W2 + b2
    norms_W2 = np.linalg.norm(X_c[:, 50240:50880], axis=1, keepdims=True) + 1e-8
    X_c[:, 50240:50880] /= norms_W2
    X_c[:, 50880:51850] /= norms_W2
    return X_c

def apply_condition_c(X: np.ndarray) -> np.ndarray:
    """
    Condition C: sign-flip only — majority-sign M=2.
    Args: X (N, 51850) float32
    Returns: X_c (N, 51850) float32
    Tensor shapes intermediate:
        W1: (N, 784, 64); col_sums: (N, 64); signs: (N, 64)
        W2: (N, 64, 10)
    """
    N = len(X)
    X_c = X.copy()
    W1 = X_c[:, :50176].reshape(N, 784, 64)
    W2 = X_c[:, 50240:50880].reshape(N, 64, 10)
    col_sums = W1.sum(axis=1)       # (N, 64)
    signs = np.sign(col_sums)       # (N, 64)
    signs[signs == 0] = 1.0
    W1 *= signs[:, np.newaxis, :]   # broadcast (N, 1, 64)
    W2 *= signs[:, :, np.newaxis]   # broadcast (N, 64, 1)
    X_c[:, :50176] = W1.reshape(N, 50176)
    X_c[:, 50240:50880] = W2.reshape(N, 640)
    return X_c

def apply_condition_e(X: np.ndarray, seed: int = 42) -> np.ndarray:
    """
    Condition E: random norm control.
    Same scale as Condition B but random unit-direction.
    Purpose: verify improvement is symmetry-specific, not just normalization.
    Args: X (N, 51850) float32; seed: int
    Returns: X_e (N, 51850) float32
    """
    rng = np.random.default_rng(seed)
    X_b = apply_condition_b(X)
    norms = np.linalg.norm(X_b, axis=1, keepdims=True) + 1e-8  # (N, 1)
    rand_dir = rng.standard_normal(X.shape).astype(np.float32)  # (N, 51850)
    rand_norms = np.linalg.norm(rand_dir, axis=1, keepdims=True) + 1e-8
    rand_unit = rand_dir / rand_norms
    return rand_unit * norms  # same norm as B, random direction

CONDITION_FNS: dict[str, Callable] = {
    'A': lambda X: X.copy(),
    'B': apply_condition_b,
    'C': apply_condition_c,
    'D': apply_condition_d,   # from h-m2
    'E': apply_condition_e,
    'F': apply_condition_d,   # same preprocessing as D; no NFT (handled in main)
}
```

---

## Subtask L2: data_prep.py — verify_canonicalization_activated

**Parent Epic:** E1 (complexity 10)

```python
def verify_canonicalization_activated(
    condition: str,
    X_before: np.ndarray,
    X_after: np.ndarray
) -> tuple[bool, dict[str, bool]]:
    """
    Args:
        condition: str in 'A'|'B'|'C'|'D'|'E'
        X_before: (N, 51850) raw weights
        X_after:  (N, 51850) preprocessed weights
    Returns:
        (all_pass: bool, indicators: dict[str, bool])
    Tensor shapes intermediate:
        W1_after: (N, 784, 64); norms: (N,); majority_positive: scalar
    """
    indicators: dict[str, bool] = {}
    N = len(X_after)

    if condition == 'A':
        indicators["no_change"] = np.allclose(X_before, X_after)

    if condition in ('B', 'D', 'F'):
        W1_after = X_after[:, :50176].reshape(N, 784, 64)
        norms = np.linalg.norm(W1_after, axis=(1, 2))  # Frobenius per sample
        indicators["norms_unit"] = float(np.abs(norms - 1.0).mean()) < 0.01

    if condition in ('C', 'D', 'F'):
        W1_after = X_after[:, :50176].reshape(N, 784, 64)
        col_sums = W1_after.sum(axis=1)          # (N, 64)
        majority_pos = (col_sums > 0).mean()      # fraction of neuron×sample pairs
        indicators["majority_positive"] = float(majority_pos) > 0.95

    if condition == 'E':
        # Directions should differ from Condition B
        X_b = apply_condition_b(X_before)
        indicators["differs_from_B"] = not np.allclose(X_after, X_b, atol=1e-3)

    all_pass = all(indicators.values()) if indicators else True
    return all_pass, indicators
```

---

## Subtask L3: model.py — CanonicalWeightEncoder

**Parent Epic:** E2 (complexity 16)

```python
class CanonicalWeightEncoder(nn.Module):
    """
    Preprocessing wrapper: apply canonicalization then NFT encoding.
    NFT architecture unchanged; only input distribution changes.

    Args:
        nft_encoder: NFTEncoder — from h-e1/h-m1 implementation
        condition: str — 'A'|'B'|'C'|'D'|'E'|'F'
        weight_dim: int — 51850 (EXPECTED_DIM)

    Forward input shapes:
        weights_flat: (batch, 51850) float32 — raw flattened weight vectors
    Forward output shapes:
        predictions: (batch, 3) float32 — [test_acc, gen_gap, lr]
    """
    def __init__(
        self,
        nft_encoder: nn.Module,
        condition: str = 'D',
        weight_dim: int = 51850,
    ) -> None: ...

    def forward(self, weights_flat: Tensor) -> Tensor:
        """
        Steps:
        1. Apply condition preprocessing (numpy → preprocess → back to tensor)
        2. Pass through self.nft_encoder
        3. Pass through self.regressor (MLP head: embed_dim → 128 → 3)
        Returns: predictions (batch, 3)
        """

    def freeze_encoder(self) -> None:
        """Freeze NFT encoder weights; only regressor trainable."""
        for p in self.nft_encoder.parameters():
            p.requires_grad_(False)

    def unfreeze_encoder(self) -> None:
        for p in self.nft_encoder.parameters():
            p.requires_grad_(True)
```

---

## Subtask L4: model.py — NFT Architecture (Minimal Implementation)

**Parent Epic:** E2 (complexity 16)

```python
class NFTEncoder(nn.Module):
    """
    Minimal NFT encoder for weight property prediction.
    Based on Zhou 2023; adapted from h-e1/h-m1 implementation.
    Input: weight_flat (batch, 51850)
    Output: embedding (batch, embed_dim)

    Architecture:
    - Linear projection: 51850 → embed_dim (default 256)
    - N_layers Transformer encoder layers (d_model=embed_dim, nhead=8, dim_ff=512)
    - Mean pool over token dimension
    - Output: (batch, embed_dim)
    """
    def __init__(
        self,
        weight_dim: int = 51850,
        embed_dim: int = 256,
        n_layers: int = 4,
        nhead: int = 8,
        dim_ff: int = 512,
        dropout: float = 0.1,
    ) -> None: ...

    def forward(self, weights_flat: Tensor) -> Tensor:
        """
        Input:  (batch, weight_dim)
        Steps:
            x = self.proj(weights_flat)              # (batch, embed_dim)
            x = x.unsqueeze(1)                       # (batch, 1, embed_dim) — treat as 1-token seq
            x = self.transformer_encoder(x)          # (batch, 1, embed_dim)
            x = x.squeeze(1)                         # (batch, embed_dim)
        Output: (batch, embed_dim)
        """

# Regressor head (used in CanonicalWeightEncoder)
class PropertyRegressor(nn.Module):
    """
    MLP: embed_dim → 128 → 3
    Output: (batch, 3) — [test_acc, gen_gap, lr]
    """
```

---

## Subtask L5: train.py — train_condition

**Parent Epic:** E3 (complexity 13)

```python
def train_condition(
    encoder: CanonicalWeightEncoder,
    loader_train: DataLoader,
    loader_val: DataLoader,
    config: ExperimentConfig,
    seed: int = 42,
) -> dict[str, Any]:
    """
    Train encoder for one condition × one seed.

    Args:
        encoder: CanonicalWeightEncoder (condition already set)
        loader_train: DataLoader — (weights_flat, labels) batches; weights (batch, 51850)
        loader_val: DataLoader — same format
        config: ExperimentConfig — lr, weight_decay, max_epochs, patience, ...
        seed: int — for reproducibility

    Returns:
        {
          'best_val_rho': float,        # best val Spearman ρ (mean over 3 tasks)
          'best_epoch': int,
          'checkpoint_path': str,       # path to saved best checkpoint
          'train_history': list[dict],  # per-epoch {train_loss, val_rho}
        }

    Algorithm:
        optimizer = Adam(encoder.parameters(), lr=config.lr, weight_decay=config.wd)
        scheduler = ReduceLROnPlateau(optimizer, patience=config.lr_patience, factor=0.5)
        best_val_rho = -inf; patience_counter = 0
        for epoch in range(config.max_epochs):
            train_loss = _train_epoch(encoder, loader_train, optimizer, criterion=MSELoss)
            val_rho = _val_epoch(encoder, loader_val)  # mean Spearman ρ over 3 tasks
            scheduler.step(-val_rho)  # ReduceLROnPlateau minimizes; negate ρ
            if val_rho > best_val_rho:
                best_val_rho = val_rho; save_checkpoint(encoder, epoch)
                patience_counter = 0
            else:
                patience_counter += 1
            if patience_counter >= config.es_patience: break
        return results_dict
    """

def train_frozen_regressor(
    encoder: CanonicalWeightEncoder,
    loader_train: DataLoader,
    loader_val: DataLoader,
    config: ExperimentConfig,
) -> dict[str, Any]:
    """
    Frozen-encoder sub-experiment.
    Precondition: encoder.freeze_encoder() has been called.
    Only trains regressor head (PropertyRegressor parameters).
    Same training loop as train_condition but optimizer only wraps regressor params.
    """
```

---

## Subtask L6: train.py — DataLoader construction

**Parent Epic:** E3 (complexity 13)

```python
def make_dataloaders(
    X_train: np.ndarray,
    Y_train: np.ndarray,
    X_val: np.ndarray,
    Y_val: np.ndarray,
    batch_size: int = 64,
    seed: int = 42,
) -> tuple[DataLoader, DataLoader]:
    """
    Wrap numpy arrays into DataLoaders.
    Input shapes:
        X_train: (N_train, 51850), Y_train: (N_train, 3)
        X_val:   (N_val,   51850), Y_val:   (N_val,   3)
    Returns: loader_train, loader_val
    Uses: WeightZooDataset(X, Y) — TensorDataset wrapper
    """

class WeightZooDataset(Dataset):
    """
    TensorDataset wrapper for weight vectors + labels.
    __getitem__(i) -> (weights_flat: Tensor[51850], labels: Tensor[3])
    __len__() -> int
    """
```

---

## Subtask L7: evaluate.py — bootstrap_spearman

**Parent Epic:** E4 (complexity 12)

```python
def bootstrap_spearman(
    y_pred: np.ndarray,
    y_true: np.ndarray,
    n_boot: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """
    Args:
        y_pred: (N,) float — model predictions
        y_true: (N,) float — ground truth labels
        n_boot: int — bootstrap resamples
        seed: int — RNG seed
    Returns:
        (rho_obs, ci_lo, ci_hi) — observed ρ, 2.5th and 97.5th percentiles
    Algorithm:
        rng = np.random.default_rng(seed)
        rho_obs = spearmanr(y_pred, y_true).statistic
        boot_rhos = [spearmanr(y_pred[idx], y_true[idx]).statistic
                     for idx in rng.integers(0, N, (n_boot, N))]
        return rho_obs, np.percentile(boot_rhos, 2.5), np.percentile(boot_rhos, 97.5)
    """

def aggregate_seeds(
    per_seed_rhos: list[dict],
) -> dict[str, dict[str, float]]:
    """
    Aggregate Spearman ρ across 3 seeds.
    Args:
        per_seed_rhos: list of dicts {condition: {label: (rho, ci_lo, ci_hi)}}
    Returns:
        {condition: {label: {'rho_mean': float, 'ci_lo': float, 'ci_hi': float}}}
    Algorithm: mean of rho; mean of CI bounds across seeds
    """
```

---

## Subtask L8: evaluate.py — gate checks P1 and P2

**Parent Epic:** E4 (complexity 12)

```python
def check_p1(
    rho_D: float, ci_D: tuple[float, float],
    rho_A: float, ci_A: tuple[float, float],
    delta_threshold: float = 0.05,
) -> dict[str, Any]:
    """
    P1: Δρ ≥ 0.05 AND CI of Δρ excludes 0.
    Returns:
        {
          'pass': bool,
          'delta_rho': float,
          'ci_excludes_zero': bool,
          'delta_ge_threshold': bool,
        }
    CI of Δρ approximated as: (ci_D_lo - ci_A_hi, ci_D_hi - ci_A_lo)
    """

def check_p2(
    rho_table: dict[str, dict[str, float]],
) -> dict[str, Any]:
    """
    P2: ρ_D > ρ_E on ≥2/3 tasks.
    Args:
        rho_table: {condition: {label: rho_mean}}
    Returns:
        {
          'pass': bool,
          'n_pass': int,
          'n_required': int,   # 2
          'per_task': {label: bool}
        }
    """
```

---

## Subtask L9: train.py — frozen-encoder protocol detail

**Parent Epic:** E5 (complexity 11)

```python
def run_frozen_encoder_experiment(
    condition_A_checkpoint: str,
    X_train: np.ndarray,
    Y_train: np.ndarray,
    X_val: np.ndarray,
    Y_val: np.ndarray,
    X_test: np.ndarray,
    Y_test: np.ndarray,
    config: ExperimentConfig,
) -> dict[str, Any]:
    """
    Steps:
    1. Load Condition A NFT from checkpoint_path
    2. Wrap in CanonicalWeightEncoder(condition='B'|'C'|'D')
    3. encoder.freeze_encoder()
    4. For each condition in ('B', 'C', 'D'):
        a. Apply preprocessing to X_train, X_val
        b. train_frozen_regressor(encoder_frozen, ...)
        c. Evaluate on X_test → rho_frozen
    Returns:
        {condition: {'rho_frozen': float, 'rho_full': float}}
        (rho_full loaded from main results for comparison)
    """
```

---

## Subtask L10: main.py — full experiment loop pseudo-code

**Parent Epic:** E7 (complexity 10)

```
Algorithm: run_full_experiment(config)

LOAD zoo → X (N, 51850), Y (N, 3)
SPLIT → X_tr, X_val, X_te (standard zoo splits)

results = {}
for condition in ['A', 'B', 'C', 'D', 'E', 'F']:
    results[condition] = {}
    for seed in config.seeds:            # [42, 123, 456]
        SET_SEED(seed)
        X_tr_c = CONDITION_FNS[condition](X_tr)
        X_val_c = CONDITION_FNS[condition](X_val)
        X_te_c  = CONDITION_FNS[condition](X_te)

        if condition == 'F':
            # Linear regressor, no NFT
            regressor = LinearRegression().fit(X_tr_c, Y_tr)
            y_pred = regressor.predict(X_te_c)
        else:
            encoder = CanonicalWeightEncoder(NFTEncoder(), condition)
            train_result = train_condition(encoder, make_dataloaders(X_tr_c, Y_tr, X_val_c, Y_val_c), config, seed)
            y_pred = encoder(X_te_c).detach().numpy()

        for i, label in enumerate(LABELS):
            rho, ci_lo, ci_hi = bootstrap_spearman(y_pred[:, i], Y_te[:, i])
            results[condition][label] = (rho, ci_lo, ci_hi)

    verify_canonicalization_activated(condition, X_tr[:8], CONDITION_FNS[condition](X_tr[:8]))

# Frozen encoder sub-experiment
run_frozen_encoder_experiment(...)

# Gate checks
p1 = check_p1(results['D']['test_accuracy'], results['A']['test_accuracy'])
p2 = check_p2({c: {l: results[c][l][0] for l in LABELS} for c in results})

SAVE results.json
generate_all_figures(results, p1, p2)
```
