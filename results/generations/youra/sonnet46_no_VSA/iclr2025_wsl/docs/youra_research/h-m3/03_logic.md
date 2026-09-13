# Logic: H-M3 — DeepSets Mechanism Closure Validation

**Date:** 2026-08-03
**Applied**: PyTorch flat-module pattern (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental from H-M2 + H-E1)
**Status**: API signatures verified from actual code
**Analyzed Path**: `h-e1/code/encoder_c2.py`, `h-m2/code/lgbm_trainer.py`, `h-m2/code/permutation.py`
**Relevant Symbols**:
- `DeepSetsChannelEncoder.forward(state_dict: dict) -> Tensor` → `(embed_dim,)` [line 50]
- `run_cv_lgbm(X, y, n_splits, random_state, params) -> (fold_preds, full_model)` [line 20]
- `compute_orbit_preds(full_model, permuted_X) -> np.ndarray` — `permuted_X`: `(N, K, embed_dim)` → `(N, K)` [line 51]
- `decompose_mse(y, fold_preds, orbit_preds) -> dict` [line 67]
- `sample_functional_permutations(channels_per_layer, K, seed) -> list` [line 7]
- `apply_permutation(state_dict, perm_spec, conv_weight_keys, bias_keys) -> dict` [line 27]

---

## External Dependencies API

### Verified from actual code

```python
# h-e1/code/encoder_c2.py
class DeepSetsChannelEncoder(nn.Module):
    def __init__(self, kernel_dims: list = None, hidden_dim: int = 64, embed_dim: int = 128): ...
    def forward(self, state_dict: dict) -> torch.Tensor: ...
    # state_dict -> (embed_dim,)  i.e. (128,) by default

def build_c2_encoder(embed_dim: int = 128, hidden_dim: int = 64) -> DeepSetsChannelEncoder:
    # kernel_dims=[25, 25, 4] hardcoded (conv1=5x5, conv2=5x5, conv3=2x2)
    ...

# h-m2/code/lgbm_trainer.py
def run_cv_lgbm(
    X: np.ndarray,          # (N, F)
    y: np.ndarray,          # (N,)
    n_splits: int = 5,
    random_state: int = 42,
    params: dict = None,
) -> tuple:                  # (fold_preds: (N,), full_model: LGBMRegressor)
    ...

def compute_orbit_preds(
    full_model,
    permuted_X: np.ndarray,  # (N, K, embed_dim)
) -> np.ndarray:             # (N, K)
    ...

def decompose_mse(
    y: np.ndarray,
    fold_preds: np.ndarray,
    orbit_preds: np.ndarray,  # (N, K)
) -> dict:                    # keys: mse_total, mse_perm, mse_res, ratio, r2_c1, tau_c1, ...
    ...

# h-m2/code/permutation.py
def sample_functional_permutations(
    channels_per_layer: list,  # [C_out_0, C_out_1, C_out_2] e.g. [16, 16, 16]
    K: int,
    seed: int = 1,
) -> list:  # K specs; each spec = list of LongTensors [perm_0, perm_1, perm_2]
    ...

def apply_permutation(
    state_dict: dict,
    perm_spec: list,
    conv_weight_keys: list = None,
    bias_keys: list = None,
) -> dict:  # permuted deep-copy of state_dict
    ...
```

---

## A-5: C3 NFN Encoder [Complexity: 14, Budget: 4 subtasks]

Applied: NFN WeightSpaceFeatures pipeline pattern

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | build_nfn_encoder | NPLinear → HNPPool → Flatten sequential |
| L-5-2 | state_dict_to_nfn_features | state_dict → WeightSpaceFeatures |
| L-5-3 | extract_c3_embeddings_with_fallback | NFN path with C2 fallback |
| L-5-4 | verify_c3_compatibility | Quick compatibility probe |

### L-5-1: build_nfn_encoder

```python
def build_nfn_encoder(
    network_spec,          # from network_spec_from_wsfeat(wsfeat)
    nfn_channels: int = 32,
) -> torch.nn.Sequential:
    """Build NPLinear→HNPPool→Flatten encoder. Output: (nfn_channels * n_pool_outs,)"""
    ...
```

**Pseudo-code:**
```
from nfn import layers as nfn_layers
from nfn.common import network_spec_from_wsfeat

1. encoder = nn.Sequential(
       nfn_layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
       nn.ReLU(),
       nfn_layers.NPLinear(network_spec, nfn_channels, nfn_channels, io_embed=True),
       nn.ReLU(),
       nfn_layers.HNPPool(network_spec),
       nn.Flatten(),
   )
2. return encoder
```

**Tensor shapes:**
| Variable | Shape | Note |
|----------|-------|------|
| wsfeat input | WeightSpaceFeatures | NFN's typed container |
| after NPLinear | WeightSpaceFeatures w/ nfn_channels | in-place channel transform |
| after HNPPool | (nfn_channels * n_pool_outs,) | n_pool_outs from HNPPool.get_num_outs(network_spec) |
| output | (nfn_channels * n_pool_outs,) | typically ~(32 * n,) |

---

### L-5-2: state_dict_to_nfn_features

```python
def state_dict_to_nfn_features(
    state_dict: dict,
) -> Optional["WeightSpaceFeatures"]:
    """Convert state_dict to NFN WeightSpaceFeatures. Returns None on failure (triggers fallback)."""
    ...
```

**Pseudo-code:**
```
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat

1. try:
       tensors = state_dict_to_tensors(state_dict)
       # tensors: list of weight Tensors per layer
       # conv: (C_out, C_in, kH, kW) — NFN may expect (C_out, C_in, kH*kW) or flat
       wsfeat = WeightSpaceFeatures(tensors, network_spec)
       return wsfeat
   except RuntimeError as e:
       logging.warning(f"[state_dict_to_nfn_features] NFN conversion failed: {e}")
       return None
```

---

### L-5-3: extract_c3_embeddings_with_fallback

```python
def extract_c3_embeddings_with_fallback(
    state_dicts: list,          # N dicts
    nfn_channels: int = 32,
    embed_dim: int = 128,       # fallback C2 embed_dim
    hidden_dim: int = 64,       # fallback C2 hidden_dim
) -> np.ndarray:                # (N, embed_c3) or (N, embed_dim) on fallback
    """NFN encode all models; fall back to C2 on RuntimeError."""
    ...
```

**Pseudo-code:**
```
1. wsfeat_0 = state_dict_to_nfn_features(state_dicts[0])
2. if wsfeat_0 is None:
       logging.warning("[C3] Using C2 fallback for all models")
       return extract_c2_embeddings(state_dicts, embed_dim, hidden_dim)
3. network_spec = network_spec_from_wsfeat(wsfeat_0)
4. encoder = build_nfn_encoder(network_spec, nfn_channels).eval()
5. embeddings = []
6. for sd in state_dicts:
       wsfeat = state_dict_to_nfn_features(sd)
       if wsfeat is None:
           logging.warning("[C3] Single model NFN failed; skipping (will cause shape mismatch)")
           raise RuntimeError("Partial NFN failure — re-run with fallback")
       with torch.no_grad():
           emb = encoder(wsfeat)  # (embed_c3,)
       embeddings.append(emb.cpu().numpy())
7. X_c3 = np.stack(embeddings)   # (N, embed_c3)
8. assert X_c3.shape[0] == len(state_dicts)
9. logging.info(f"[C3] NFN embeddings shape: {X_c3.shape}")
10. return X_c3
```

---

### L-5-4: verify_c3_compatibility

```python
def verify_c3_compatibility(state_dicts: list) -> bool:
    """Test NFN conversion on first model. Returns True if NFN path is usable."""
    ...
```

**Pseudo-code:**
```
1. wsfeat = state_dict_to_nfn_features(state_dicts[0])
2. ok = wsfeat is not None
3. logging.info(f"[C3 compat] NFN path {'OK' if ok else 'FAILED — will use C2 fallback'}")
4. return ok
```

---

## A-3: C2 DeepSets Encoder [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch eval-loop pattern

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | extract_c2_embeddings | Encode N models; assert orbitvar < 1e-4 |
| L-3-2 | compute_c2_orbitvar | Mean embedding variance over K orbit permutations |

### L-3-1: extract_c2_embeddings

```python
def extract_c2_embeddings(
    state_dicts: list,       # N state dicts
    embed_dim: int = 128,
    hidden_dim: int = 64,
) -> np.ndarray:             # (N, 128)
    """Encode all models; assert OrbitVar(C2) < 1e-4 before returning."""
    ...
```

**Pseudo-code:**
```
1. encoder = build_c2_encoder(embed_dim=embed_dim, hidden_dim=hidden_dim).eval()
2. embeddings = []
3. with torch.no_grad():
       for sd in state_dicts:
           emb = encoder.forward(sd)   # (embed_dim,) = (128,)
           embeddings.append(emb.cpu().numpy())
4. X_c2 = np.stack(embeddings)         # (N, 128)
5. assert X_c2.shape == (len(state_dicts), embed_dim)
6. # OrbitVar check: K=10 quick orbits on first 5 models
7. perm_fn = sample_functional_permutations
8. orbitvar = compute_c2_orbitvar(encoder, state_dicts[:5], perm_fn, K=10, seed=0)
9. assert orbitvar < 1e-4, f"OrbitVar={orbitvar:.2e} >= 1e-4 — C2 invariance FAILED"
10. logging.info(f"[C2] X_c2.shape={X_c2.shape}, orbitvar={orbitvar:.2e}")
11. return X_c2
```

**Tensor shapes:** `X_c2`: `(N, 128)` where N=100

---

### L-3-2: compute_c2_orbitvar

```python
def compute_c2_orbitvar(
    encoder: "DeepSetsChannelEncoder",
    state_dicts: list,       # subset or full N models
    perm_fn,                 # sample_functional_permutations
    K: int = 50,
    seed: int = 1,
) -> float:
    """Mean variance of C2 embeddings over K orbit permutations. Should be ~0."""
    ...
```

**Pseudo-code:**
```
# channels_per_layer for CIFAR10-GS: 3 conv layers, C_out=[8,6,4] per _CIFAR10GS_CNN
# NOTE: actual dataset uses C=16 per PRD; verify from state_dicts[0]
1. C_outs = [state_dicts[0][k].shape[0] for k in CONV_WEIGHT_KEYS]  # e.g. [16,16,16]
2. perm_specs = perm_fn(channels_per_layer=C_outs, K=K, seed=seed)
   # Returns list[list[LongTensor]] length K; each inner list has len(CONV_WEIGHT_KEYS) tensors
3. per_model_vars = []
4. encoder.eval()
5. with torch.no_grad():
       for sd in state_dicts:
           orbit_embs = []
           for spec in perm_specs:
               perm_sd = apply_permutation(sd, spec)
               emb = encoder.forward(perm_sd)  # (embed_dim,)
               orbit_embs.append(emb.cpu().numpy())
           orbit_embs = np.stack(orbit_embs)   # (K, embed_dim)
           var = float(np.var(orbit_embs, axis=0).mean())  # scalar
           per_model_vars.append(var)
6. orbitvar = float(np.mean(per_model_vars))
7. return orbitvar
```

---

## A-7: MSE Permutation Test (C2) [Complexity: 11, Budget: 1 subtask]

Applied: Standard PyTorch eval-loop pattern

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | compute_mse_perm_c2 | K=50 orbit predictions → MSE_perm(C2) |

### L-7-1: compute_mse_perm_c2

```python
def compute_mse_perm_c2(
    lgbm_model,               # LGBMRegressor trained on X_c2 (full_model from run_cv_lgbm)
    encoder: "DeepSetsChannelEncoder",
    state_dicts: list,        # N dicts
    y: np.ndarray,            # (N,) — unused here but kept for decompose_mse
    K: int = 50,
    seed: int = 1,
) -> float:
    """MSE_perm(C2) = mean per-model orbit prediction variance over K permutations."""
    ...
```

**Pseudo-code:**
```
1. C_outs = [state_dicts[0][k].shape[0] for k in CONV_WEIGHT_KEYS]
2. perm_specs = sample_functional_permutations(channels_per_layer=C_outs, K=K, seed=seed)
   # list of K specs
3. N = len(state_dicts)
4. embed_dim = encoder.proj.out_features  # 128
5. permuted_X = np.zeros((N, K, embed_dim), dtype=np.float32)
6. encoder.eval()
7. with torch.no_grad():
       for n, sd in enumerate(state_dicts):
           for k, spec in enumerate(perm_specs):
               perm_sd = apply_permutation(sd, spec)
               emb = encoder.forward(perm_sd)   # (embed_dim,)
               permuted_X[n, k, :] = emb.cpu().numpy()
8. orbit_preds = compute_orbit_preds(lgbm_model, permuted_X)  # (N, K)
9. per_model_orbit_var = np.var(orbit_preds, axis=1, ddof=0)   # (N,)
10. mse_perm_c2 = float(np.mean(per_model_orbit_var))
11. logging.info(f"[MSE_perm C2] K={K}, mse_perm={mse_perm_c2:.6f}")
12. return mse_perm_c2
```

**Tensor shapes:**

| Variable | Shape | Note |
|----------|-------|------|
| permuted_X | (100, 50, 128) | N=100, K=50, embed_dim=128 |
| orbit_preds | (100, 50) | from compute_orbit_preds |
| per_model_orbit_var | (100,) | variance over K dim |
| mse_perm_c2 | scalar | mean of per_model_orbit_var |

---

## Key Tensor Shape Summary

| Symbol | Shape | Source |
|--------|-------|--------|
| conv1 weights | (16, 3, 5, 5) | C_out=16, C_in=3 (grayscale 3-ch), kH=kW=5 |
| conv2 weights | (16, 16, 5, 5) | C_out=16, C_in=16 |
| conv3 weights | (16, 16, 2, 2) | C_out=16, C_in=16, kH=kW=2 (from PRD N=100 dataset) |
| C2 per-model emb | (128,) | DeepSetsChannelEncoder.forward output |
| X_c2 | (100, 128) | N=100 models |
| X_c3 | (100, nfn_channels * n_pool_outs) | n_pool_outs from HNPPool.get_num_outs |
| permuted_X | (100, 50, 128) | for compute_orbit_preds |
| orbit_preds | (100, 50) | from compute_orbit_preds |

**Note on conv3:** PRD states C=16 channels for N=100 dataset (vs. _CIFAR10GS_CNN's C_out=4). Actual channel sizes must be read from `state_dicts[0]` keys at runtime. `C_outs = [sd[k].shape[0] for k in CONV_WEIGHT_KEYS]`.
