---
hypothesis_id: h-m1
hypothesis_type: MECHANISM
generated_at: "2026-08-21T13:00:00+00:00"
budget: 12 subtasks
---

# Logic Design: H-M1 — Permutation Equivariance Verification

Applied: inference-only dispatch pattern (encoder-type-specific forward pass)
Applied: statistics aggregation pattern (max/mean/median/p95 over 10,000 checks)

---

## Codebase Analysis (Serena)

**Base hypothesis:** H-E1  
**Analyzed:** `docs/youra_research/h-e1/code/encoders.py`, `data.py`, `config.py`  
**Key findings:**
- `GNNNFNEncoder.__init__(hidden_dim=64, num_layers=4, ...)` — confirmed hidden_dim=64 (not 128 as PRD stated)
- `FlatMLP.__init__(input_dim, hidden=512, output_dim=128)` — takes flat tensor `(B, D)`
- `state_dict_to_graph(state_dict) -> Data` — returns PyG `Data` object; batch via `Batch.from_data_list([g])`
- `ZooDataset.__getitem__` returns `(OrderedDict, float)` — keys like `"layers.0.weight"`, `"layers.0.bias"`
- CIFAR-10 zoo file: single `.pt` with dict `{"trainset": [...], "valset": [...], "testset": [...]}`

---

## External Dependencies API

### From `h-e1/code/encoders.py`

```python
class GNNNFNEncoder(nn.Module):
    def __init__(self, hidden_dim: int = 64, num_layers: int = 4,
                 in_channels: int = 1, out_channels: int = 128): ...
    def forward(self, data: Batch) -> Tensor:
        # data: PyG Batch with .x (node features), .edge_index, .edge_attr, .batch
        # returns: (B, 128) — graph-level embedding
        ...

class FlatMLP(nn.Module):
    def __init__(self, input_dim: int, hidden: int = 512, output_dim: int = 128): ...
    def forward(self, x: Tensor) -> Tensor:
        # x: (B, input_dim)
        # returns: (B, 128)
        ...
```

### From `h-e1/code/data.py`

```python
def state_dict_to_graph(state_dict: OrderedDict) -> Data:
    # Converts weight OrderedDict → PyG Data with node/edge features
    # returns: Data(x=..., edge_index=..., edge_attr=...)

def load_zoo(zoo_pt_path: str, split: str = "testset") -> list[tuple[OrderedDict, float]]:
    # Loads zoo .pt file, returns list of (state_dict, accuracy) tuples
    ...
```

---

## Subtask Specifications

### A-6: Verify Loop (4 subtasks)

#### L-6-1: encoder_dispatch

```python
def encoder_dispatch(
    encoder_name: str,
    encoder: nn.Module,
    state_dict: OrderedDict,
    h_e1_data_module,  # imported h-e1 data.py
) -> Tensor:
    """Forward pass for one state_dict through named encoder.
    
    Returns:
        out: Tensor shape (128,) — embedding vector (squeeze batch dim)
    """
    if encoder_name == "flat_mlp":
        # Flatten all weights into 1D tensor
        flat = torch.cat([v.flatten() for v in state_dict.values()])  # (D,)
        x = flat.unsqueeze(0)  # (1, D)
        out = encoder(x)       # (1, 128)
        return out.squeeze(0)  # (128,)
    
    elif encoder_name == "gnn_nfn":
        from torch_geometric.data import Batch
        graph = h_e1_data_module.state_dict_to_graph(state_dict)  # Data
        batch = Batch.from_data_list([graph])  # Batch (B=1)
        out = encoder(batch)   # (1, 128)
        return out.squeeze(0)  # (128,)
    
    elif encoder_name == "dwsnet":
        # DWSNets expects list of (weight, bias) tuples per layer
        # Build from state_dict matching network_spec order
        weights = _build_dwsnet_input(state_dict)  # list of Tensor tuples
        out = encoder(weights)  # (128,) or (1, 128)
        return out.flatten()[:128]  # (128,)
    
    else:
        raise ValueError(f"Unknown encoder: {encoder_name}")
```

#### L-6-2: run_single_model_check

```python
def run_single_model_check(
    encoder_name: str,
    encoder: nn.Module,
    state_dict: OrderedDict,
    hidden_keys: list[str],
    num_perms: int,
    h_e1_data_module,
) -> list[float]:
    """Run num_perms permutation checks on one model.
    
    Returns:
        diffs: list[float] of length num_perms — max abs diff per perm
    """
    out_orig = encoder_dispatch(encoder_name, encoder, state_dict, h_e1_data_module)
    diffs = []
    for _ in range(num_perms):
        # Pick hidden layer to permute (first hidden layer for consistency)
        layer_key = hidden_keys[0] if hidden_keys else None
        if layer_key is None:
            diffs.append(0.0)
            continue
        hidden_size = state_dict[layer_key].shape[0]
        perm = torch.randperm(hidden_size)
        sd_perm = permute_weights(state_dict, layer_key, perm)
        out_perm = encoder_dispatch(encoder_name, encoder, sd_perm, h_e1_data_module)
        diff = (out_orig - out_perm).abs().max().item()
        diffs.append(diff)
    return diffs
```

#### L-6-3: verify_equivariance (outer loop)

```python
def verify_equivariance(
    encoder_name: str,
    encoder: nn.Module,
    weight_samples: list[OrderedDict],
    hidden_keys_per_model: list[list[str]],
    num_perms: int = 50,
    h_e1_data_module = None,
) -> dict:
    """Run full 200×50 verification. Returns stats dict.
    
    Args:
        weight_samples: list of N OrderedDicts from zoo
        hidden_keys_per_model: list[list[str]] — hidden layer keys per model
        
    Returns:
        {
          "max_diff": float,
          "mean_diff": float,
          "median_diff": float,
          "p95_diff": float,
          "all_diffs": list[float],  # length N * num_perms
          "pass": bool,
          "n_checks": int,
        }
    """
    encoder.eval()
    all_diffs = []
    with torch.no_grad():
        for sd, hidden_keys in zip(weight_samples, hidden_keys_per_model):
            diffs = run_single_model_check(
                encoder_name, encoder, sd, hidden_keys, num_perms, h_e1_data_module
            )
            all_diffs.extend(diffs)
    return compute_stats(all_diffs, tol=1e-5 if encoder_name != "flat_mlp" else None)
```

#### L-6-4: compute_stats

```python
def compute_stats(diffs: list[float], tol: float | None = 1e-5) -> dict:
    """Aggregate statistics over all diffs.
    
    Args:
        diffs: list[float] of max abs diffs
        tol: pass threshold (None = don't check)
        
    Returns dict with: max_diff, mean_diff, median_diff, p95_diff, all_diffs, pass, n_checks
    """
    arr = np.array(diffs, dtype=np.float64)
    result = {
        "max_diff": float(arr.max()),
        "mean_diff": float(arr.mean()),
        "median_diff": float(np.median(arr)),
        "p95_diff": float(np.percentile(arr, 95)),
        "all_diffs": diffs,
        "n_checks": len(diffs),
        "pass": bool(arr.max() < tol) if tol is not None else None,
    }
    return result
```

---

### A-4: Encoder Loader (4 subtasks)

#### L-4-1: load_gnn_nfn

```python
def load_gnn_nfn(
    ckpt_path: str,
    hidden_dim: int = 64,    # VERIFIED from H-E1 actual code
    num_layers: int = 4,
) -> GNNNFNEncoder:
    """Load GNNNFNEncoder. Falls back to random init if checkpoint missing.
    
    Returns:
        encoder: GNNNFNEncoder in eval() mode
    """
    # Import from H-E1 code directory
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
    from encoders import GNNNFNEncoder
    
    encoder = GNNNFNEncoder(hidden_dim=hidden_dim, num_layers=num_layers)
    if Path(ckpt_path).exists():
        state = torch.load(ckpt_path, map_location="cpu")
        # H-E1 may save full training state or just model state
        sd = state.get("model_state_dict", state.get("state_dict", state))
        encoder.load_state_dict(sd, strict=False)
        print(f"✓ GNN-NFN loaded from {ckpt_path}")
    else:
        print(f"⚠ GNN-NFN checkpoint not found at {ckpt_path} — using random init")
    return encoder.eval()
```

#### L-4-2: load_flat_mlp

```python
def load_flat_mlp(
    input_dim: int,
    ckpt_path: str,
    hidden: int = 512,
    output_dim: int = 128,
) -> FlatMLP:
    """Load FlatMLP. Falls back to random init if checkpoint missing.
    
    Args:
        input_dim: flattened weight dimension (computed from zoo model)
        
    Returns:
        encoder: FlatMLP(input_dim, hidden=512, output_dim=128) in eval() mode
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
    from encoders import FlatMLP
    
    encoder = FlatMLP(input_dim=input_dim, hidden=hidden, output_dim=output_dim)
    if Path(ckpt_path).exists():
        state = torch.load(ckpt_path, map_location="cpu")
        sd = state.get("model_state_dict", state.get("state_dict", state))
        encoder.load_state_dict(sd, strict=False)
        print(f"✓ FlatMLP loaded from {ckpt_path}")
    else:
        print(f"⚠ FlatMLP checkpoint not found — using random init")
    return encoder.eval()
```

#### L-4-3: build_dwsnet_spec

```python
def build_dwsnet_spec(sample_state_dict: OrderedDict) -> object:
    """Build DWSNets NetworkSpec from a zoo model state_dict.
    
    Handles:
    - FC layers: weight shape (out, in) → LinearSpec(in, out)
    - Conv layers: weight shape (out, in, kH, kW) → treat as FC with dim out*kH*kW? 
      OR skip conv layers and use FC-only spec (safer for DWSNets compatibility)
    
    Strategy: Extract ONLY nn.Linear-style layers (2D weights).
    Conv layers (4D) are flattened per-channel if DWSNets MLP-spec required.
    
    Returns:
        network_spec: DWSNets NetworkSpec or compatible structure
        OR None if CNN spec incompatible (triggers fallback to random MLP spec)
    """
    try:
        from dwsnets import NetworkSpec, LayerSpec
        layer_specs = []
        weight_keys = [k for k in sample_state_dict if k.endswith(".weight")]
        for k in weight_keys:
            w = sample_state_dict[k]
            if w.dim() == 2:  # Linear layer
                in_dim, out_dim = w.shape[1], w.shape[0]
                layer_specs.append(LayerSpec(in_features=in_dim, out_features=out_dim))
            # Skip conv layers (4D) — DWSNets MLP-spec only
        if not layer_specs:
            return None
        return NetworkSpec(layer_specs)
    except Exception as e:
        print(f"⚠ DWSNets spec build failed: {e} — will use fallback MLP spec")
        return None
```

#### L-4-4: load_dwsnet

```python
def load_dwsnet(network_spec, channels: int = 32) -> nn.Module:
    """Load DWSNet from AvivNavon/DWSNets with given spec.
    
    Random init is valid — equivariance is structural (not learned).
    
    Args:
        network_spec: from build_dwsnet_spec() or None for fallback
        channels: DWSNets hidden channels
        
    Returns:
        encoder: DWSNet in eval() mode, or FallbackEquivariantMLP if import fails
    """
    try:
        from dwsnets import DWSNet
        if network_spec is None:
            # Fallback: 3-layer MLP spec matching CIFAR-10 zoo FC layers
            from dwsnets import NetworkSpec, LayerSpec
            network_spec = NetworkSpec([
                LayerSpec(in_features=32*32*3, out_features=256),
                LayerSpec(in_features=256, out_features=10),
            ])
        encoder = DWSNet(network_spec=network_spec, channels=channels)
        print("✓ DWSNet loaded (random init — structural equivariance)")
        return encoder.eval()
    except ImportError:
        print("⚠ DWSNets not installed — install with: git clone https://github.com/AvivNavon/DWSNets && pip install -e .")
        raise
```

---

### A-5: Permute Function (2 subtasks)

#### L-5-1: permute_weights

```python
def permute_weights(
    weight_dict: OrderedDict,
    layer_key: str,
    perm: Tensor,
) -> OrderedDict:
    """Apply neuron permutation to one hidden layer.
    
    Mathematical operation:
      W_in (layer_key):     shape (out, in)   → W_in[perm, :]    (permute rows)
      W_out (next layer):   shape (out, in)   → W_out[:, perm]   (permute cols)
      bias_in (layer_key):  shape (out,)      → bias_in[perm]    (reorder)
    
    For conv weights:
      W_in: shape (out, in, kH, kW) → W_in[perm, :, :, :]
      W_out: shape (out, in, kH, kW) → W_out[:, perm, :, :]
    
    Args:
        weight_dict: OrderedDict of weight tensors
        layer_key: key of incoming weight matrix (e.g., "layers.1.weight")
        perm: Tensor of shape (hidden_size,) — permutation indices
        
    Returns:
        new OrderedDict with permuted weights (original unchanged)
    """
    result = OrderedDict((k, v.clone()) for k, v in weight_dict.items())
    
    # Find bias key for this layer
    bias_key = layer_key.replace(".weight", ".bias")
    
    # Find outgoing weight key (next layer weight)
    all_weight_keys = [k for k in weight_dict if k.endswith(".weight")]
    try:
        idx = all_weight_keys.index(layer_key)
        next_weight_key = all_weight_keys[idx + 1] if idx + 1 < len(all_weight_keys) else None
    except ValueError:
        next_weight_key = None
    
    # Permute incoming weight rows
    w_in = result[layer_key]
    if w_in.dim() == 2:
        result[layer_key] = w_in[perm, :]
    elif w_in.dim() == 4:
        result[layer_key] = w_in[perm, :, :, :]
    
    # Permute incoming bias
    if bias_key in result:
        result[bias_key] = result[bias_key][perm]
    
    # Permute outgoing weight cols
    if next_weight_key is not None:
        w_out = result[next_weight_key]
        if w_out.dim() == 2:
            result[next_weight_key] = w_out[:, perm]
        elif w_out.dim() == 4:
            result[next_weight_key] = w_out[:, perm, :, :]
    
    return result
```

#### L-5-2: permute_all_hidden_layers

```python
def permute_all_hidden_layers(
    weight_dict: OrderedDict,
    hidden_keys: list[str],
    perm: Tensor,
) -> OrderedDict:
    """Apply same permutation to all hidden layers sequentially.
    
    Note: perm size must match hidden layer width; generate separate
    perm per layer if hidden sizes differ.
    
    Args:
        hidden_keys: list of weight keys for hidden layers (not input/output)
        perm: shared permutation (if all hidden dims equal) OR generate per layer
        
    Returns:
        permuted weight_dict
    """
    result = weight_dict
    for layer_key in hidden_keys:
        hidden_size = weight_dict[layer_key].shape[0]
        if perm.shape[0] != hidden_size:
            # Different hidden dim — generate new perm for this layer
            layer_perm = torch.randperm(hidden_size)
        else:
            layer_perm = perm
        result = permute_weights(result, layer_key, layer_perm)
    return result
```

---

### A-10: Main Runner (2 subtasks)

#### L-10-1: main() orchestration

```python
def main() -> None:
    """End-to-end permutation equivariance verification for H-M1."""
    import sys, os
    from pathlib import Path
    
    # 0. Setup
    torch.manual_seed(config.SEED)
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    
    # Add H-E1 code to path
    h_e1_code = Path(__file__).parent.parent.parent / "h-e1" / "code"
    sys.path.insert(0, str(h_e1_code))
    import data as h_e1_data
    
    print("=== H-M1: Permutation Equivariance Verification ===")
    
    # 1. Load data
    print(f"Loading {config.N_MODELS} zoo models...")
    weight_samples = load_zoo_models(n=config.N_MODELS, seed=config.SEED)
    weight_dim = get_weight_dim(weight_samples)
    hidden_keys_per_model = [detect_hidden_layers(sd) for sd in weight_samples]
    print(f"  weight_dim={weight_dim}, sample hidden_keys={hidden_keys_per_model[0]}")
    
    # 2. Load encoders
    print("Loading encoders...")
    encoders = get_all_encoders(weight_dim, weight_samples[0])
    # encoders: {"gnn_nfn": ..., "flat_mlp": ..., "dwsnet": ...}
    
    # 3. Verify each encoder
    results = {}
    for name, enc in encoders.items():
        print(f"Verifying {name} ({config.N_MODELS} models × {config.N_PERMS} perms)...")
        results[name] = verify_equivariance(
            encoder_name=name,
            encoder=enc,
            weight_samples=weight_samples,
            hidden_keys_per_model=hidden_keys_per_model,
            num_perms=config.N_PERMS,
            h_e1_data_module=h_e1_data,
        )
        print(f"  {name}: max_diff={results[name]['max_diff']:.2e}")
    
    # 4. Gate check
    activated, indicators = verify_mechanism_activated(results)
    
    # 5. Report
    print_summary_table(results, activated, indicators)
    save_json(results, activated, indicators)
    save_all_figures(results)
    
    # 6. Assert gate conditions
    assert results["dwsnet"]["max_diff"] < config.TOL_EQUIV, \
        f"DWSNets NOT equivariant: max_diff={results['dwsnet']['max_diff']:.2e}"
    assert results["gnn_nfn"]["max_diff"] < config.TOL_EQUIV, \
        f"GNN-NFN NOT equivariant: max_diff={results['gnn_nfn']['max_diff']:.2e}"
    assert results["flat_mlp"]["max_diff"] > config.TOL_NON_EQUIV, \
        f"Flat-MLP appears equivariant (unexpected): max_diff={results['flat_mlp']['max_diff']:.2e}"
    
    print("\n✅ H-M1 GATE: ALL CONDITIONS PASSED")
    print(f"  DWSNets max_diff={results['dwsnet']['max_diff']:.2e} < {config.TOL_EQUIV}")
    print(f"  GNN-NFN max_diff={results['gnn_nfn']['max_diff']:.2e} < {config.TOL_EQUIV}")
    print(f"  Flat-MLP max_diff={results['flat_mlp']['max_diff']:.2e} > {config.TOL_NON_EQUIV}")
```

#### L-10-2: smoke test

```python
def smoke_test() -> None:
    """Minimal end-to-end test: 1 model, 2 perms, assert output shapes.
    Run before full experiment to catch import/format errors early.
    """
    torch.manual_seed(0)
    samples = load_zoo_models(n=1, seed=0)
    weight_dim = get_weight_dim(samples)
    hidden_keys = [detect_hidden_layers(samples[0])]
    encoders = get_all_encoders(weight_dim, samples[0])
    
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
    import data as h_e1_data
    
    for name, enc in encoders.items():
        result = verify_equivariance(name, enc, samples, hidden_keys,
                                     num_perms=2, h_e1_data_module=h_e1_data)
        assert result["n_checks"] == 2, f"{name}: expected 2 checks, got {result['n_checks']}"
        assert isinstance(result["max_diff"], float), f"{name}: max_diff not float"
        print(f"  smoke test {name}: max_diff={result['max_diff']:.2e} ✓")
    print("✓ Smoke test passed")

if __name__ == "__main__":
    smoke_test()
    main()
```

---

## Tensor Shape Summary

| Operation | Input Shape | Output Shape | Notes |
|-----------|-------------|--------------|-------|
| FlatMLP forward | `(1, D)` | `(1, 128)` | D = flattened zoo model weight dim |
| GNN-NFN forward | PyG Batch (B=1) | `(1, 128)` | graph from state_dict_to_graph |
| DWSNets forward | list of (W,b) tuples | `(128,)` or `(1,128)` | per DWSNets API |
| permute_weights | `(out, in)` or `(out, in, kH, kW)` | same shape | rows/cols permuted |
| compute_stats | `list[float]` len N×K | dict | N=200, K=50, total=10000 |
| out_diff | `(128,)` - `(128,)` | scalar | `.abs().max().item()` |
