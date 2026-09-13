# Logic: H-M2
# NFN Equivariant Encoder Permutation Sensitivity Probing

Applied: PyTorch equivariant weight-space pattern (Navon et al. 2023, arXiv:2301.12780)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1 code
**Analyzed Path**: `docs/youra_research/20260505_wsl/h-m1/code/`
**Relevant Symbols**:
- `WeightDataset.__getitem__` → returns `(flat_w: Tensor, acc: Tensor)` — h-m2 must extend to also yield weight_list
- `train_encoder(model, train_loader, val_loader, cfg, device)` → inner loop unpacks `(x, y)` with `_, pred = model(x)`; h-m2 must adapt batch unpacking for `(weight_list, flat_w, acc)`
- `_embed_state_dict(encoder, state_dict, mean, std, device)` → flattens and normalizes; h-m2 needs `_embed_nfn` that extracts ordered weight list instead
- `compute_permutation_sensitivity(encoder, checkpoints, mean, std, cfg, device)` → takes `mean/std` for normalization; h-m2 version omits mean/std (NFN takes structured list, not flat vector)
- `run_gate_check(sensitivity_score, spearman_rho, param_count, n_pairs, cfg)` → uses `cfg.sensitivity_gate` (single scalar); h-m2 uses `cfg.sensitivity_gate_absolute` + `cfg.sensitivity_gate_relative`
- `generate_permuted_weights(state_dict, layer_order, seed)` → reused unchanged
- `get_mnist_cnn_layer_order()` → returns actual hyp_rand keys `module_list.{0,3,6,9,11}` with Conv(8)-Conv(6)-Conv(4)-FC(20)-FC(10); `_extract_weight_list` must discover actual keys at runtime
- `_load_raw_splits(cfg)` → reused unchanged for NFNWeightDataset
- `compute_spearman(model, loader, device)` → unpacks `(x, y)` then `_, pred = model(x)`; h-m2 must adapt for `(weight_list, flat_w, acc)` batch format

---

## A-3: NPLinear Layer [Complexity: 14, Budget: 4 subtasks]

Applied: PyTorch equivariant weight-space pattern (Navon et al. 2023)

### API Signatures

```python
class NPLinear(nn.Module):
    """Permutation-equivariant linear layer operating on structured weight list."""

    def __init__(
        self,
        in_ch: int,
        out_ch: int,
        weight_shapes: List[tuple],
    ):
        """Initialize diag and bias_terms paths for each layer shape."""
        # Per layer i with n_elements_i = prod(shape_i):
        #   diag:       Linear(in_ch, out_ch, bias=False)   — per-element transform
        #   bias_terms: Linear(in_ch, out_ch, bias=True)    — pooled invariant context
        # Separate diag/bias_terms ModuleLists, one entry per shape in weight_shapes
        ...

    def _n_elements(self, shape: tuple) -> int:
        """Return total number of elements for a weight tensor shape."""
        # Conv (C_out, C_in, kH, kW) → C_out * C_in * kH * kW
        # Bias (C,) → C
        # FC   (N_out, N_in) → N_out * N_in
        ...

    def forward(self, Ws: List[torch.Tensor]) -> List[torch.Tensor]:
        """Apply equivariant transform to each layer's channel representation.

        Args:
            Ws: list of L tensors, each [B, n_elements_i, in_ch]
        Returns:
            list of L tensors, each [B, n_elements_i, out_ch]
        """
        # For each layer i:
        #   mean_i = Ws[i].mean(dim=1, keepdim=True)  # [B, 1, in_ch] — pooled context
        #   out_i  = diag[i](Ws[i]) + bias_terms[i](mean_i.expand_as(Ws[i]))
        # Returns list of same length
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| Ws[i] | [B, n_elements_i, in_ch] | Input channel repr per layer |
| mean_i | [B, 1, in_ch] | Global pooled context (invariant) |
| out[i] | [B, n_elements_i, out_ch] | Output channel repr |

**n_elements per layer** (MNIST-CNN canonical shapes):
- conv1.weight (32,1,3,3) → 288; conv1.bias (32,) → 32
- conv2.weight (64,32,3,3) → 18432; conv2.bias (64,) → 64
- fc1.weight (128,1024) → 131072; fc1.bias (128,) → 128
- fc2.weight (10,128) → 1280; fc2.bias (10,) → 10

### Pseudo-code

```
NPLinear.forward(Ws):
  outputs = []
  for i, w in enumerate(Ws):          # w: [B, n_i, in_ch]
    ctx = w.mean(dim=1, keepdim=True)  # [B, 1, in_ch]
    out = diag[i](w) + bias_terms[i](ctx).expand_as(w)
    outputs.append(out)                # [B, n_i, out_ch]
  return outputs
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Shape flattening | `_n_elements(shape)` and weight reshaping to `[B, n_i, ch]` in forward |
| L-3-2 | diag path | `ModuleList` of `Linear(in_ch, out_ch, bias=False)` per layer |
| L-3-3 | bias_terms path | `ModuleList` of `Linear(in_ch, out_ch, bias=True)` + mean pool context |
| L-3-4 | equivariance test | Unit test: permute input neurons, verify output permutes consistently |

---

## A-4: NFNEncoder + NFNWithHead [Complexity: 13, Budget: 2 subtasks]

Applied: Standard PyTorch module composition

### API Signatures

```python
class NFNEncoder(nn.Module):
    """Equivariant encoder: structured weight list → (B, embed_dim) embedding."""

    def __init__(
        self,
        weight_shapes: List[tuple],
        channel_dim: int,
        embed_dim: int = 128,
        n_layers: int = 3,
    ):
        """in_proj: NPLinear(1, channel_dim); layers: n_layers-1 x NPLinear(ch,ch); readout: Linear(ch, embed_dim)."""
        # self.in_proj = NPLinear(1, channel_dim, weight_shapes)
        # self.layers  = nn.ModuleList([NPLinear(channel_dim, channel_dim, weight_shapes)
        #                               for _ in range(n_layers - 1)])
        # self.readout = nn.Linear(channel_dim, embed_dim)
        # self.act     = nn.ReLU()
        ...

    def _prepare_inputs(self, weights: List[torch.Tensor]) -> List[torch.Tensor]:
        """Reshape each raw weight tensor to [B, n_elements_i, 1] channel repr."""
        # weights[i]: [B, *shape_i] → flatten spatial → [B, n_elements_i] → unsqueeze(-1)
        ...

    def forward(self, weights: List[torch.Tensor]) -> torch.Tensor:
        """Forward pass through NFN encoder.

        Args:
            weights: list of 8 tensors, each [B, *layer_shape]
        Returns:
            embedding: [B, embed_dim]
        """
        # 1. Ws = _prepare_inputs(weights)        # list of [B, n_i, 1]
        # 2. Ws = act(in_proj(Ws))               # list of [B, n_i, ch]
        # 3. for layer in self.layers:
        #      Ws = act(layer(Ws))               # list of [B, n_i, ch]
        # 4. pooled = mean over each [B, n_i, ch] → [B, ch], then mean over layers → [B, ch]
        # 5. return readout(pooled)              # [B, embed_dim]
        ...


class NFNWithHead(nn.Module):
    """NFNEncoder + Linear(embed_dim, 1) accuracy prediction head."""

    def __init__(self, encoder: NFNEncoder, embed_dim: int = 128):
        """Wrap encoder with prediction head."""
        # self.encoder = encoder
        # self.head    = nn.Linear(embed_dim, 1)
        ...

    def forward(
        self, weights: List[torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass returning embedding and prediction.

        Args:
            weights: list of 8 tensors, each [B, *layer_shape]
        Returns:
            embedding:  [B, embed_dim]
            prediction: [B, 1]
        """
        # embedding = self.encoder(weights)   # [B, embed_dim]
        # prediction = self.head(embedding)   # [B, 1]
        # return embedding, prediction
        ...


def count_params(model: nn.Module) -> int:
    """Return total trainable parameter count."""
    ...


def grid_search_nfn(
    weight_shapes: List[tuple],
    channel_dim_candidates: List[int],
    n_layers_candidates: List[int],
    embed_dim: int,
    target_min: int,
    target_max: int,
) -> Tuple[NFNEncoder, int, int, int]:
    """Grid search channel_dim x n_layers to hit [target_min, target_max] params.

    Returns: (encoder, channel_dim, n_layers, param_count)
    Raises RuntimeError if no config hits target range.
    """
    # Iterate channel_dim_candidates x n_layers_candidates
    # For each: build NFNWithHead(NFNEncoder(...)), count params
    # Return first hit; log all attempts
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weights[i] | [B, *shape_i] | Raw per-layer tensors from collate |
| Ws[i] after _prepare_inputs | [B, n_elements_i, 1] | Channel dim = 1 initially |
| Ws[i] after in_proj | [B, n_elements_i, ch] | ch = channel_dim |
| pooled | [B, ch] | Global mean over all n_i elements across all layers |
| embedding | [B, 128] | Final encoder output |
| prediction | [B, 1] | Head output for MSE regression |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | NFNEncoder + NFNWithHead | Stack NPLinear layers, global mean pool, two-tuple forward |
| L-4-2 | grid_search_nfn | Iterate channel_dim x n_layers grid, count_params, return first in [475K, 525K] |

---

## A-6: NFN Probing [Complexity: 12, Budget: 2 subtasks]

Applied: Standard PyTorch equivariant weight-space pattern (Navon et al. 2023)

### API Signatures

```python
def _embed_nfn(
    encoder,                        # NFNEncoder in eval mode
    state_dict: Dict[str, torch.Tensor],
    weight_key_order: List[str],    # ordered list of 8 actual state_dict keys
    device: torch.device,
) -> torch.Tensor:
    """Extract ordered weight list from state_dict and encode with NFNEncoder.

    Returns: [embed_dim] on CPU
    """
    # 1. Extract: weight_list = [state_dict[k].float().cpu() for k in weight_key_order]
    # 2. Add batch dim: [w.unsqueeze(0).to(device) for w in weight_list]
    # 3. encoder.eval(); with torch.no_grad(): emb = encoder(batched_list)  # [1, embed_dim]
    # 4. return emb.squeeze(0).cpu()
    ...


def compute_permutation_sensitivity_nfn(
    encoder,                        # NFNEncoder (eval mode set internally)
    checkpoints: List[Dict],
    weight_key_order: List[str],    # ordered keys, discovered at runtime from first checkpoint
    cfg,
    device: torch.device,
) -> Dict:
    """Compute NFN permutation sensitivity score.

    Reuses generate_permuted_weights + get_mnist_cnn_layer_order from h-m1/code/probe.py.
    Reuses stratified_pair_sample from h-e1/code/weight_analysis.py.

    sensitivity_score = mean(L2(enc(w), enc(perm(w)))) / mean(L2(enc(w_i), enc(w_j)))

    Returns:
        {sensitivity_score, mean_equiv_L2, mean_random_L2, n_pairs,
         equiv_dists, random_dists, decile_scores}
    """
    # Import reused functions:
    #   from probe import generate_permuted_weights, get_mnist_cnn_layer_order  (h-m1)
    #   from weight_analysis import stratified_pair_sample                       (h-e1)
    #
    # layer_order = get_mnist_cnn_layer_order()
    # n_per_decile = max(cfg.n_pairs // 10, 5)
    # pairs = stratified_pair_sample(checkpoints, n_per_decile, cfg.acc_threshold, cfg.seed)
    #
    # for (ckpt_i, ckpt_j, decile) in pairs:
    #   e_orig = _embed_nfn(encoder, ckpt_i["state_dict"], weight_key_order, device)
    #   perm_sd = generate_permuted_weights(ckpt_i["state_dict"], layer_order, seed=cfg.seed)
    #   e_perm = _embed_nfn(encoder, perm_sd, weight_key_order, device)
    #   d_equiv = norm(e_orig - e_perm)
    #   e_j = _embed_nfn(encoder, ckpt_j["state_dict"], weight_key_order, device)
    #   d_random = norm(e_orig - e_j)
    #
    # sensitivity_score = mean(equiv_dists) / (mean(random_dists) + 1e-8)
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | _embed_nfn | Extract ordered weight list from state_dict, batch-dim add, NFNEncoder forward, return [embed_dim] CPU |
| L-6-2 | compute_permutation_sensitivity_nfn | Reuse stratified_pair_sample + generate_permuted_weights; compute equiv/random L2 dists + decile breakdown |

---

## External Dependencies (Base Hypothesis)

**Verified from**: `docs/youra_research/20260505_wsl/h-m1/code/` (actual implementation)

```python
# From: h-m1/code/probe.py (ACTUAL CODE)
def generate_permuted_weights(
    state_dict: Dict[str, torch.Tensor],
    layer_order: List[Tuple[str, str, int]],  # (out_key, in_key, n_neurons)
    seed: Optional[int] = None,
) -> Dict[str, torch.Tensor]:
    """Returns new state_dict with permuted weights preserving functional equivalence."""
    ...

def get_mnist_cnn_layer_order() -> List[Tuple[str, str, int]]:
    """Returns actual hyp_rand keys: module_list.{0,3,6,9,11}, Conv(8)-Conv(6)-Conv(4)-FC(20)-FC(10)."""
    # NOTE: NOT canonical Conv(32)-Conv(64)-FC(128)-FC(10) — actual zoo architecture differs!
    ...

def _embed_state_dict(
    encoder,
    state_dict: Dict[str, torch.Tensor],
    mean: torch.Tensor,   # ← h-m2 does NOT use this; NFNEncoder takes structured list
    std: torch.Tensor,    # ← h-m2 does NOT use this
    device: torch.device,
) -> torch.Tensor:
    """h-m1 version — NOT reused in h-m2. h-m2 uses _embed_nfn instead."""
    ...

def compute_permutation_sensitivity(
    encoder,
    checkpoints: List[Dict],
    mean: torch.Tensor,   # ← h-m2 does NOT pass this
    std: torch.Tensor,    # ← h-m2 does NOT pass this
    cfg,
    device: torch.device,
) -> Dict:
    """h-m1 version — NOT reused. h-m2 reimplements as compute_permutation_sensitivity_nfn."""
    ...

# From: h-m1/code/data_loader.py (ACTUAL CODE)
def _load_raw_splits(cfg) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Reused unchanged. Returns (train_ckpts, val_ckpts, test_ckpts)."""
    ...

class WeightDataset(Dataset):
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Returns (flat_w_normalized: Tensor[input_dim], acc: Tensor[])."""
        # h-m2 NFNWeightDataset extends this to also return weight_list
        ...

# From: h-m1/code/train.py (ACTUAL CODE)
def train_encoder(
    model,              # expects model(x) → (embedding, pred) two-tuple
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg,
    device: torch.device,
) -> Tuple[object, TrainHistory]:
    """Inner loop: for x, y in loader — h-m2 must adapt to for weight_list, flat_w, acc in loader."""
    # h-m2 reimplements train loop with weight_list batch unpacking
    ...

# From: h-m1/code/evaluate.py (ACTUAL CODE)
def compute_spearman(model, loader: DataLoader, device: torch.device) -> float:
    """Inner loop: for x, y in loader; _, pred = model(x).
    h-m2 must adapt: for weight_list, flat_w, acc in loader; _, pred = model(weight_list)."""
    ...

def run_gate_check(
    sensitivity_score: float,
    spearman_rho: float,
    param_count: int,
    n_pairs: int,
    cfg,  # uses cfg.sensitivity_gate (single scalar) — h-m2 uses dual thresholds instead
) -> Dict:
    """h-m1 version. h-m2 reimplements as run_gate_check_nfn with dual-threshold logic."""
    ...
```

**Critical differences h-m1 → h-m2:**
- `_embed_state_dict` takes `mean, std` and flattens; `_embed_nfn` takes `weight_key_order` and extracts structured list
- `compute_permutation_sensitivity` takes `mean, std`; `compute_permutation_sensitivity_nfn` does not (NFN normalizes internally via training)
- `run_gate_check` uses `cfg.sensitivity_gate` (>0.3 PASS for h-m1); `run_gate_check_nfn` uses `cfg.sensitivity_gate_absolute` (<0.1) AND `cfg.sensitivity_gate_relative` (<0.3245) with BOTH required
- `train_encoder` inner loop unpacks `(x, y)` → h-m2 unpacks `(weight_list, flat_w, acc)` and passes `weight_list` to `model.forward`
- `get_mnist_cnn_layer_order` returns actual zoo keys (`module_list.*`), not canonical names — `_extract_weight_list` in NFNWeightDataset must auto-discover actual keys from first checkpoint state_dict
