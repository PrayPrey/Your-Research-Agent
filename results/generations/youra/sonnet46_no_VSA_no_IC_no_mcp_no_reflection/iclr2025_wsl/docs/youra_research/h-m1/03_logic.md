# Logic: h-m1

Applied: checkpoint-reuse pattern (H-E1 run_experiment.py build_encoder / compute_split)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual H-E1 code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**:
- `FlatMLP.__init__(input_dim, hidden_dim=256)` / `forward(weights_flat: [B,D]) -> [B]`
- `DWSNet.__init__(weight_shapes, hidden_dim=256, **kwargs)`
- `NFT.__init__(weight_shapes, d_model=128, n_heads=4, n_layers=2, max_tokens=512, **kwargs)`
- `GNN.__init__(node_dim=16, edge_dim=1, hidden_dim=128, n_layers=3, max_edges=512, **kwargs)`
- `load_zoo(path, idx_train, idx_val, idx_test, seed=42) -> ZooData`
- `make_loader(zoo, split, batch_size, shuffle, encoder_type="flat", num_workers=0) -> DataLoader`
- `predict_all(model, loader, device) -> (list, list)`
- `eval_spearman(model, zoo, split, batch_size, device) -> (r, p)`
- `compute_split(N, seed, ratios) -> (idx_train, idx_val, idx_test)` — from data.audit
- `train_encoder(encoder, zoo, lr, batch_size, epochs, seed, lr_schedule, device, verbose) -> (model, best_r, curve)`

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/encoders/flat_mlp.py
class FlatMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256): ...
    def forward(self, weights_flat: Tensor) -> Tensor: ...  # [B,D] -> [B]

# From: h-e1/code/encoders/dwsnet.py
class DWSNet(nn.Module):
    def __init__(self, weight_shapes: list, hidden_dim: int = 256, **kwargs): ...
    def forward(self, weights_flat: Tensor) -> Tensor: ...  # [B,D] -> [B]

# From: h-e1/code/encoders/nft.py
class NFT(nn.Module):
    def __init__(self, weight_shapes: list, d_model: int = 128, n_heads: int = 4,
                 n_layers: int = 2, max_tokens: int = 512, **kwargs): ...
    def forward(self, weights_flat: Tensor) -> Tensor: ...  # [B,D] -> [B]

# From: h-e1/code/encoders/gnn.py
class GNN(nn.Module):
    def __init__(self, node_dim: int = 16, edge_dim: int = 1, hidden_dim: int = 128,
                 n_layers: int = 3, max_edges: int = 512, **kwargs): ...
    def forward(self, weights_flat: Tensor) -> Tensor: ...  # [B,D] -> [B]

# From: h-e1/code/data/loader.py
def load_zoo(path: str, idx_train=None, idx_val=None, idx_test=None, seed=42) -> ZooData: ...
def make_loader(zoo: ZooData, split: str, batch_size: int, shuffle: bool = True,
                encoder_type: str = "flat", num_workers: int = 0) -> DataLoader: ...

# From: h-e1/code/training/train.py
def predict_all(model: nn.Module, loader, device: str) -> tuple: ...  # (list, list)
def train_encoder(encoder, zoo, lr, batch_size, epochs, seed=42,
                  lr_schedule="none", device="cuda:0", verbose=False) -> tuple: ...  # (model, best_r, curve)

# From: h-e1/code/data/audit.py (used in run_experiment.py)
def compute_split(N: int, seed: int, ratios: list) -> tuple: ...  # (idx_train, idx_val, idx_test)
```

**Verified from**: `h-e1/code/` (actual implementation)

---

## L-3-1: load_encoder() [Complexity: 9, Budget: 2]

Applied: checkpoint-reuse pattern

### API Signatures

```python
# h-m1/analysis.py

ENCODER_CLS = {
    "flat_mlp": FlatMLP,
    "dws_net": DWSNet,
    "nft": NFT,
    "gnn": GNN,
}

ARCH_KWARGS = {
    # Populated at runtime from zoo.weight_shapes and H-E1 EncoderConfig defaults
    "flat_mlp": lambda zoo: {"input_dim": zoo.weights.shape[1], "hidden_dim": 256},
    "dws_net":  lambda zoo: {"weight_shapes": _get_weight_shapes_2d(zoo), "hidden_dim": 256},
    "nft":      lambda zoo: {"weight_shapes": _get_weight_shapes_2d(zoo), "d_model": 128, "n_heads": 4, "n_layers": 2},
    "gnn":      lambda zoo: {},  # GNN uses defaults
}

def _get_weight_shapes_2d(zoo: "ZooData") -> list:
    """Mirrors h-e1/run_experiment.py get_weight_shapes_2d."""
    if zoo.weight_shapes:
        return zoo.weight_shapes
    return [(27, 4), (36, 8), (512, 64), (64, 10)]

def load_encoder(
    name: str,              # one of ENCODER_NAMES
    checkpoint_path: str,
    zoo: "ZooData",
    device: str,
) -> "nn.Module":
    """Instantiate encoder, load checkpoint state_dict, set eval mode."""
    # name -> encoder key mapping: "flat_mlp"/"dws_net"/"nft"/"gnn"
    ...
```

### Pseudo-code

```
1. cls = ENCODER_CLS[name]
2. kwargs = ARCH_KWARGS[name](zoo)
3. model = cls(**kwargs).to(device)
4. ckpt = torch.load(checkpoint_path, map_location=device)
5. state = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
6. model.load_state_dict(state)
7. model.eval()
8. return model
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1a | _get_weight_shapes_2d | Mirror H-E1 logic for shape inference fallback |
| L-3-1b | load_encoder | Instantiate + load state_dict + eval mode |

---

## L-4-1: check_missing_checkpoints() + retrain_encoder() [Complexity: 13, Budget: 3]

Applied: checkpoint-reuse pattern (H-E1 random_search / train_encoder)

### API Signatures

```python
# h-m1/retrain.py

CHECKPOINT_FILES = {
    "flat_mlp": "flat_mlp_best.pt",
    "dws_net":  "dws_net_best.pt",
    "nft":      "nft_best.pt",
    "gnn":      "gnn_best.pt",
}

def check_missing_checkpoints(
    checkpoint_dir: str,
    encoder_names: list,   # e.g. ["flat_mlp","dws_net","nft","gnn"]
) -> list[str]:
    """Returns names whose checkpoint files do not exist."""
    ...

def retrain_encoder(
    name: str,
    zoo: "ZooData",
    checkpoint_dir: str,
    device: str,
) -> str:
    """Re-train encoder with H-E1 protocol. Returns saved checkpoint path."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1a | check_missing_checkpoints | os.path.exists per checkpoint file |
| L-4-1b | retrain_encoder orchestration | Build encoder, call H-E1 train_encoder, save |
| L-4-1c | checkpoint save | torch.save state_dict to checkpoint_dir/{name}_best.pt |

---

## L-4-2: retrain_encoder pseudo-code [Complexity: 13, Budget: 3]

Applied: H-E1 train_encoder protocol (verified from actual training/train.py)

### Pseudo-code

```
retrain_encoder(name, zoo, checkpoint_dir, device):
  cfg = ENCODER_CONFIGS[ENCODER_NAME_MAP[name]]  # e.g. "nft" -> "NFT"
  kwargs = ARCH_KWARGS[name](zoo)
  encoder = ENCODER_CLS[name](**kwargs)

  # H-E1 protocol: AdamW not Adam — NOTE: H-E1 uses Adam, but PRD says AdamW
  # Use Adam (seed=42) to match H-E1 train_encoder exactly
  model, best_r, curve = train_encoder(
      encoder, zoo,
      lr=cfg.lr_candidates[0],   # pick first candidate (best from H-E1 search)
      batch_size=cfg.batch_size,
      epochs=cfg.epochs,         # NFT=100, GNN=50
      seed=42,
      lr_schedule=cfg.lr_schedule,
      device=device,
      verbose=True,
  )
  # ponytail: uses first lr_candidate, not full random_search; add search if val_r < 0.4

  save_path = os.path.join(checkpoint_dir, f"{name}_best.pt")
  torch.save({"model_state_dict": model.state_dict(), "val_r": best_r}, save_path)
  print(f"[H-M1] Retrained {name}: val_r={best_r:.4f} -> {save_path}")
  return save_path
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-2a | ENCODER_NAME_MAP | Maps "nft"->"NFT" etc. for H-E1 ENCODER_CONFIGS lookup |
| L-4-2b | train_encoder call | Reuse H-E1 exactly; single lr for speed |
| L-4-2c | Save + log | torch.save dict with state_dict and val_r |

---

## L-5-1: bootstrap_ci() [Complexity: 10, Budget: 2]

Applied: Standard numpy bootstrap

### API Signatures

```python
# h-m1/analysis.py

def bootstrap_ci(
    preds: np.ndarray,    # [N]
    targets: np.ndarray,  # [N]
    n: int = 1000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Resample with replacement, compute Spearman per sample.
    Returns (r_point, ci_low, ci_high) at 95% CI."""
    ...
```

### Pseudo-code

```
1. rng = np.random.RandomState(seed)
2. rs = []
3. for _ in range(n):
     idx = rng.randint(0, len(preds), size=len(preds))
     r, _ = spearmanr(preds[idx], targets[idx])
     rs.append(r if r == r else 0.0)  # nan guard
4. r_point, _ = spearmanr(preds, targets)
5. return float(r_point), float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1a | resample loop | numpy randint bootstrap |
| L-5-1b | percentile CI | np.percentile at 2.5/97.5 |

---

## L-5-2: run_analysis() orchestration [Complexity: 10, Budget: 3]

Applied: Standard analysis pipeline

### API Signatures

```python
# h-m1/analysis.py

def run_inference(
    model: "nn.Module",
    zoo: "ZooData",
    device: str,
    batch_size: int = 256,
) -> tuple[np.ndarray, np.ndarray]:
    """Run predict_all on test split. Returns (preds, true_gap) as np arrays."""
    # [N_test], [N_test]
    ...

def run_analysis(
    zoo: "ZooData",
    checkpoint_dir: str,
    device: str,
) -> tuple[dict, dict]:
    """Load all 4 encoders, run inference, compute Spearman+CI.
    Returns (results, preds_dict).
    results: {name: {"r": float, "ci_low": float, "ci_high": float}}
    preds_dict: {name: np.ndarray [N_test]}
    """
    ...

def gate_check(results: dict, baseline_r: float = 0.5567) -> bool:
    """True if any equivariant encoder (non flat_mlp) r > baseline_r."""
    ...

def compute_delta_gap(results: dict, baseline_r: float = 0.5567) -> float:
    """mean(r for equivariant encoders) - baseline_r."""
    ...
```

### Pseudo-code

```
run_analysis(zoo, checkpoint_dir, device):
  results = {}
  preds_dict = {}
  true_gap = zoo.gap[zoo.idx_test]  # [N_test]

  for name in ENCODER_NAMES:  # ["flat_mlp","dws_net","nft","gnn"]
    ckpt_path = os.path.join(checkpoint_dir, CHECKPOINT_FILES[name])
    model = load_encoder(name, ckpt_path, zoo, device)
    preds, _ = run_inference(model, zoo, device)
    r, lo, hi = bootstrap_ci(preds, true_gap)
    results[name] = {"r": r, "ci_low": lo, "ci_high": hi}
    preds_dict[name] = preds
    print(f"[H-M1] {name}: Spearman(gap)={r:.4f} [{lo:.4f},{hi:.4f}] vs FlatMLP=0.5567")

  assert results["flat_mlp"]["r"] > 0.4, "H-E1 consistency check failed"
  return results, preds_dict

gate_check(results, baseline_r=0.5567):
  equivariant = ["dws_net", "nft", "gnn"]
  return any(results[n]["r"] > baseline_r for n in equivariant if n in results)

compute_delta_gap(results, baseline_r=0.5567):
  equivariant = ["dws_net", "nft", "gnn"]
  rs = [results[n]["r"] for n in equivariant if n in results]
  return float(np.mean(rs)) - baseline_r
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-2a | run_inference | Wrap predict_all, return np arrays for test split |
| L-5-2b | run_analysis loop | Load each encoder, infer, bootstrap CI, log |
| L-5-2c | gate_check + compute_delta_gap | Filter equivariant names, compare to baseline |
