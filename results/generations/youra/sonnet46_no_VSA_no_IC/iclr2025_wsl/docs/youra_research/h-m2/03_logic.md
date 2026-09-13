---
hypothesis_id: h-m2
hypothesis_type: MECHANISM
generated_at: "2026-08-21T15:30:00+00:00"
budget: 12 subtasks
---

# Logic Design: H-M2 — Sample Efficiency via Permutation Equivariance

Applied: continuation-first pattern (load H-E1 results → fallback training if missing)
Applied: bootstrap percentile CI over 5 seeds for robust efficiency ratio estimation

---

## Codebase Analysis (Serena)

**Base hypotheses:** H-E1 + H-M1
**Analyzed:** `docs/youra_research/h-e1/code/encoders.py`, `train.py`, `data.py`; `docs/youra_research/h-m1/code/permute.py`
**Key findings from actual code:**

- `FlatMLP.__init__(input_dim, hidden_dim=256, num_layers=3)` — note: default hidden_dim=256 (NOT 512 as PRD draft stated)
- `FlatMLP.forward(x: Tensor) -> Tensor` — x shape (B, D), returns (B,) squeezed
- `FlatMLPPermAug.__init__(input_dim, hidden_dim=256, num_layers=3, perm_prob=0.5, weight_shapes=[])` — subclass of FlatMLP
- `FlatMLPPermAug.forward(x, training=False)` — applies `_permute_flat_weights` only when `training=True`
- `GNNNFNEncoder.__init__(hidden_dim=64, num_layers=4, in_channels=1, out_channels=128)` — confirmed hidden_dim=64 from H-M1
- `train_one(encoder, train_loader, val_loader, encoder_name, epochs=100, lr=1e-3, weight_decay=1e-4, seed=42, device="cuda") -> dict` — returns `{"train_loss": [...], "val_loss": [...]}`
- `load_zoo(zoo_name: str) -> tuple` — returns `(train_ds, val_ds, test_ds)` as ZooDataset objects; uses `config.ZOO_PATHS[zoo_name]`
- `subsample(dataset: ZooDataset, n, seed: int = 42) -> ZooDataset` — n='full' returns unchanged; wraps Subset with `.targets` attr
- H-E1 `ENCODER_NAMES = ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]` — DWSNets NOT in H-E1 actual run list
- H-E1 config has hardcoded absolute paths — H-M2 must NOT import H-E1 config; use sys.path to import H-E1 code modules only

---

## External Dependencies API

### From `h-e1/code/encoders.py`

```python
class FlatMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, num_layers: int = 3): ...
    def forward(self, x: Tensor) -> Tensor:
        # x: (B, D) flat weight vector
        # returns: (B,) scalar predictions

class FlatMLPPermAug(FlatMLP):
    def __init__(self, input_dim: int, hidden_dim: int = 256, num_layers: int = 3,
                 perm_prob: float = 0.5, weight_shapes: list = None): ...
    def forward(self, x: Tensor, training: bool = False) -> Tensor:
        # training=True applies random neuron permutation augmentation

class GNNNFNEncoder(nn.Module):
    def __init__(self, hidden_dim: int = 64, num_layers: int = 4,
                 in_channels: int = 1, out_channels: int = 128): ...
    # forward: accepts PyG Batch from state_dict_to_graph
```

### From `h-e1/code/train.py`

```python
def train_one(
    encoder: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    encoder_name: str,         # "flat_mlp" | "flat_mlp_perm_aug" | "gnn_nfn"
    epochs: int = 100,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    seed: int = 42,
    device: str = "cuda",
) -> dict:
    # Returns {"train_loss": [float, ...], "val_loss": [float, ...]}
    # NOTE: train_one does NOT return R² — must call get_predictions separately
```

### From `h-e1/code/data.py`

```python
def load_zoo(zoo_name: str) -> tuple[ZooDataset, ZooDataset, ZooDataset]:
    # Returns (train_ds, val_ds, test_ds)
    # zoo_name must be key in config.ZOO_PATHS

def subsample(dataset: ZooDataset, n, seed: int = 42) -> ZooDataset:
    # n: int or "full"; uses numpy rng (NOT torch manual_seed)
    # Returns Subset with .targets and .zoo_arch attrs

class FlatCollator:
    def __call__(self, batch) -> tuple[Tensor, Tensor]:
        # Returns (X, y) where X: (B, D), y: (B,)

class ZooDataset(Dataset):
    def __getitem__(self, idx) -> tuple[dict, Tensor]:
        # Returns (state_dict: OrderedDict, target: float tensor)
```

### From `h-m1/code/permute.py`

```python
def permute_weights(weight_dict: dict, layer_key: str, perm: Tensor) -> dict:
    # Apply neuron permutation to one hidden layer (rows of W_l, cols of W_{l+1})

def get_perm(size: int, device: torch.device = torch.device("cpu")) -> Tensor:
    # torch.randperm(size, device=device)
```

---

## Subtask Specifications

### A-4: Training Fallback (4 subtasks)

#### L-4-1: `run_training_cell`

```python
def run_training_cell(
    encoder_name: str,      # "flat_mlp" | "flat_mlp_perm_aug" | "gnn_nfn"
    zoo_name: str,          # "mnist" | "cifar10"
    n_train: int | str,     # int or "full"
    seed: int,
    device: str,
    h_e1_code_path: str,
    zoo_paths: dict,        # {"mnist": "...", "cifar10": "..."}
    epochs: int = 100,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
) -> float:
    """
    Train one (encoder, zoo, n_train, seed) cell. Returns R² on fixed test set.

    Pseudo-code:
    1. sys.path.insert(0, h_e1_code_path)
    2. from data import load_zoo, subsample, FlatCollator, GNNCollator
    3. from train import train_one, get_predictions  [see NOTE below]
    4. from encoders import build_encoder  [verify build_encoder signature]
    5. train_ds, val_ds, test_ds = load_zoo(zoo_name)  [uses injected zoo_paths]
    6. sub_train = subsample(train_ds, n_train, seed)
    7. batch_size = 16 if (n_train != "full" and n_train <= 250) else 32
    8. collator = FlatCollator() if encoder_name in ["flat_mlp", "flat_mlp_perm_aug"]
                  else GNNCollator()
    9. train_loader = DataLoader(sub_train, batch_size, shuffle=True, collate_fn=collator)
       val_loader   = DataLoader(val_ds, batch_size=64, shuffle=False, collate_fn=collator)
       test_loader  = DataLoader(test_ds, batch_size=64, shuffle=False, collate_fn=collator)
    10. encoder = build_encoder(encoder_name, input_dim=flat_dim)
    11. train_one(encoder, train_loader, val_loader, encoder_name, epochs, lr, weight_decay, seed, device)
    12. preds, targets = get_predictions(encoder, test_loader, encoder_name, device)
    13. from sklearn.metrics import r2_score
        return float(r2_score(targets, preds))

    NOTE: train_one returns loss history dict; R² computed separately via get_predictions.
    NOTE: load_zoo uses config.ZOO_PATHS — H-M2 must monkey-patch config.ZOO_PATHS before import.
    """
```

#### L-4-2: `make_dataloader`

```python
def make_dataloader(
    dataset,               # ZooDataset or Subset
    encoder_name: str,
    batch_size: int,
    shuffle: bool = False,
) -> DataLoader:
    """
    Dispatch between FlatCollator and GNNCollator based on encoder_name.

    Pseudo-code:
    flat_encoders = {"flat_mlp", "flat_mlp_perm_aug"}
    if encoder_name in flat_encoders:
        collate_fn = FlatCollator()
    else:  # gnn_nfn, dwsnets (both use graph representation)
        collate_fn = GNNCollator()
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle,
                      collate_fn=collate_fn, num_workers=0)

    NOTE: GNNCollator verified from H-E1 data.py — wraps state_dict_to_graph + Batch.from_data_list
    """
```

#### L-4-3: `run_training_fallback`

```python
def run_training_fallback(
    encoder_names: list[str],
    zoo_names: list[str],
    training_sizes: list,
    seeds: list[int],
    device: str,
    existing_results: dict | None = None,
) -> dict:
    """
    Run training for all (encoder, zoo, size, seed) cells missing from existing_results.
    Returns merged results dict.

    Pseudo-code:
    results = copy(existing_results) if existing_results else {}
    for enc in encoder_names:
        for zoo in zoo_names:
            for n in training_sizes:
                seed_r2s = []
                for seed in seeds:
                    # skip if already in existing_results
                    if enc in results and zoo in results[enc] \
                       and str(n) in results[enc][zoo]:
                        seed_r2s = results[enc][zoo][str(n)]["seed_r2s"]
                        break
                    r2 = run_training_cell(enc, zoo, n, seed, device, ...)
                    seed_r2s.append(r2)
                mean_r2, ci_lo, ci_hi = bootstrap_ci(seed_r2s)
                results.setdefault(enc, {}).setdefault(zoo, {})[str(n)] = {
                    "mean_r2": mean_r2, "ci_lo": ci_lo, "ci_hi": ci_hi,
                    "seed_r2s": seed_r2s
                }
    return results
    """
```

#### L-4-4: `check_and_merge`

```python
def check_and_merge(
    h_e1_results: dict | None,
    required_encoders: list[str],
    required_zoos: list[str],
    required_sizes: list,
) -> tuple[dict, list]:
    """
    Check h_e1_results completeness. Returns (partial_results, missing_cells).
    missing_cells: list of (encoder, zoo, size) tuples needing training.

    Pseudo-code:
    partial = h_e1_results or {}
    missing = []
    for enc in required_encoders:
        for zoo in required_zoos:
            for n in required_sizes:
                if not (enc in partial and zoo in partial[enc]
                        and str(n) in partial[enc][zoo]):
                    missing.append((enc, zoo, n))
    return partial, missing
    """
```

---

### A-10: Integration (2 subtasks)

#### L-10-1: `main()` pseudo-code

```python
def main():
    """Full execution sequence with explicit error handling."""
    # 1. DWSNets compatibility check
    dwsnets_ok = check_dwsnets_compatibility("cifar10")
    encoder_names = list(config.ENCODER_NAMES)  # ["flat_mlp", "flat_mlp_perm_aug", "gnn_nfn"]
    if dwsnets_ok:
        encoder_names.append("dwsnets")
        print("✓ DWSNets compatible — added to encoder list")
    else:
        print("⚠ DWSNets incompatible with CNN-s zoo (≤2 FC layers) — excluded")

    # 2. Load or compute results
    h_e1_results = load_h_e1_results(config.H_E1_RESULTS_JSON)
    if h_e1_results is not None:
        print(f"✓ Loaded H-E1 results from {config.H_E1_RESULTS_JSON}")
        partial, missing = check_and_merge(h_e1_results, encoder_names,
                                           config.ZOO_NAMES, config.TRAINING_SIZES)
    else:
        print("⚠ H-E1 results not found — running training fallback")
        partial, missing = {}, [(e, z, n) for e in encoder_names
                                for z in config.ZOO_NAMES for n in config.TRAINING_SIZES]

    if missing:
        print(f"  Running training for {len(missing)} missing cells...")
        results = run_training_fallback(encoder_names, config.ZOO_NAMES,
                                        config.TRAINING_SIZES, config.SEEDS,
                                        config.DEVICE, existing_results=partial)
    else:
        results = partial

    # 3. Analysis
    efficiency_ratios = compute_all_efficiency_ratios(results)

    # 4. Mechanism verification
    for enc in [e for e in encoder_names if e in ("gnn_nfn", "dwsnets")]:
        indicators = verify_mechanism_activated_batch(enc, results, config.DEVICE)
        print(f"  {enc} mechanism check: {indicators}")

    # 5. Gate check
    gate_passed, details = check_gate(efficiency_ratios)
    print(f"\n{'✅' if gate_passed else '❌'} Gate: efficiency_ratio >= 2.0: {details}")

    # 6. Visualize
    os.makedirs(config.FIGURES_DIR, exist_ok=True)
    for zoo in config.ZOO_NAMES:
        plot_learning_curves(results, zoo,
                             os.path.join(config.FIGURES_DIR, f"learning_curves_{zoo}.png"))
    plot_efficiency_bar(efficiency_ratios,
                        os.path.join(config.FIGURES_DIR, "efficiency_ratio_bar.png"))

    # 7. Save + print summary
    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(config.RESULTS_DIR, "learning_curve_results.json")
    save_results_json(results, efficiency_ratios, gate_passed, out_path)
    print_summary_table(efficiency_ratios, gate_passed)
```

#### L-10-2: `end_to_end_smoke_test`

```python
def end_to_end_smoke_test():
    """
    Minimal smoke test: single cell (gnn_nfn, cifar10, size=100, seed=0).
    Verifies no import errors, shape errors, or division-by-zero in ratio computation.

    Steps:
    1. run_training_cell("gnn_nfn", "cifar10", 100, 0, "cpu", ...)
       → assert r2 is float and not NaN
    2. dummy_results = {"gnn_nfn": {"cifar10": {"100": {"mean_r2": r2, "ci_lo": r2, "ci_hi": r2,
                                                         "seed_r2s": [r2]}}},
                        "flat_mlp": {"cifar10": {"100": {"mean_r2": r2-0.1, ...}}}}
    3. ratios = compute_all_efficiency_ratios(dummy_results)
       → assert "gnn_nfn" in ratios
    4. gate_passed, _ = check_gate(ratios)
       → assert isinstance(gate_passed, bool)
    print("✓ Smoke test passed")
```

---

### A-6: Bootstrap CI & Efficiency Ratio (2 subtasks)

#### L-6-1: `bootstrap_ci`

```python
def bootstrap_ci(
    seed_r2s: list[float],
    n_boot: int = 1000,
    ci: float = 0.95,
) -> tuple[float, float, float]:
    """
    Percentile bootstrap CI over 5-seed R² values.

    Pseudo-code:
    if len(seed_r2s) < 2:
        mean = seed_r2s[0] if seed_r2s else 0.0
        return mean, mean, mean   # degenerate CI

    arr = np.array(seed_r2s)
    mean = float(np.mean(arr))
    boot_means = [np.mean(np.random.choice(arr, len(arr), replace=True))
                  for _ in range(n_boot)]
    alpha = (1 - ci) / 2
    lo = float(np.percentile(boot_means, alpha * 100))
    hi = float(np.percentile(boot_means, (1 - alpha) * 100))
    return mean, lo, hi

    NOTE: Uses np.random — seed separately if needed (don't mix with torch seeds)
    """
```

#### L-6-2: `compute_efficiency_ratio`

```python
def compute_efficiency_ratio(
    plain_curve: dict,      # {str(size) -> float} mean_r2 per size
    equiv_curve: dict,      # same schema
    training_sizes: list,   # [100, 250, 500, 1000, "full"] — ordered
    peak_fraction: float = 0.90,
) -> float:
    """
    N_plain(90% peak R²) / N_equiv(90% peak R²).

    Pseudo-code:
    # Convert size keys to int (map "full" to len of training split)
    # Use ordered training_sizes list to determine numeric size for "full"
    def get_r2_list(curve):
        return [(n, curve[str(n)]) for n in training_sizes if str(n) in curve]

    plain_list = get_r2_list(plain_curve)  # [(100, r2), (250, r2), ...]
    equiv_list = get_r2_list(equiv_curve)

    plain_peak = max(r2 for _, r2 in plain_list)
    equiv_peak = max(r2 for _, r2 in equiv_list)

    plain_threshold = peak_fraction * plain_peak
    equiv_threshold = peak_fraction * equiv_peak

    # Find minimum N where threshold met
    plain_90 = next((n for n, r2 in plain_list if r2 >= plain_threshold), None)
    equiv_90 = next((n for n, r2 in equiv_list if r2 >= equiv_threshold), None)

    if plain_90 is None or equiv_90 is None:
        return float('inf')  # never reached threshold

    # Map "full" to a concrete number for ratio computation
    size_map = {100: 100, 250: 250, 500: 500, 1000: 1000, "full": 3402}  # MNIST default
    plain_n = size_map.get(plain_90, plain_90)
    equiv_n = size_map.get(equiv_90, equiv_90)

    if equiv_n == 0:
        return float('inf')
    return plain_n / equiv_n
    """
```

---

### A-8: Visualization (2 subtasks)

#### L-8-1: `plot_learning_curves`

```python
def plot_learning_curves(
    results: dict,     # {encoder: {zoo: {size: {mean_r2, ci_lo, ci_hi}}}}
    zoo_name: str,
    out_path: str,
) -> None:
    """
    Matplotlib spec:
    - fig size: (8, 5)
    - x-axis: training sizes [100, 250, 500, 1000, full_size] — log scale
    - y-axis: R² (0 to 1)
    - Line per encoder: color map {"flat_mlp": "gray", "flat_mlp_perm_aug": "orange",
                                    "gnn_nfn": "steelblue", "dwsnets": "green"}
    - CI band: ax.fill_between(x, ci_lo, ci_hi, alpha=0.2, color=encoder_color)
    - Legend top-left
    - Title: f"Learning Curves — {zoo_name.upper()} Zoo"
    - x-tick labels: ["100", "250", "500", "1K", "Full"]
    - plt.tight_layout(); plt.savefig(out_path, dpi=150, bbox_inches='tight')
    """
```

#### L-8-2: `plot_efficiency_bar`

```python
def plot_efficiency_bar(
    efficiency_ratios: dict,   # {encoder: {zoo: float}}
    out_path: str,
) -> None:
    """
    Grouped bar chart: x-axis = equivariant encoders × zoos, y-axis = efficiency ratio.
    - Bar groups: one per equivariant encoder, two bars per group (mnist, cifar10)
    - Dashed red horizontal line at y=2.0 with label "Gate threshold (2.0×)"
    - Bar labels: show ratio value above each bar (format: f"{ratio:.2f}×")
    - fig size: (7, 4)
    - Title: "Sample Efficiency Ratio (N_plain(90%peak) / N_equiv(90%peak))"
    - plt.tight_layout(); plt.savefig(out_path, dpi=150, bbox_inches='tight')
    """
```

---

### A-7: Gate & Mechanism Verification (2 subtasks)

#### L-7-1: `check_gate`

```python
def check_gate(
    efficiency_ratios: dict,   # {encoder: {zoo: float}}
    gate: float = 2.0,
) -> tuple[bool, dict]:
    """
    Gate: ratio >= 2.0 for >= 1 equivariant encoder (gnn_nfn or dwsnets) on BOTH zoos.

    Pseudo-code:
    equivariant_encoders = [e for e in efficiency_ratios if e in ("gnn_nfn", "dwsnets")]
    details = {}
    for enc in equivariant_encoders:
        per_zoo = efficiency_ratios[enc]
        meets_both = all(per_zoo.get(zoo, 0) >= gate for zoo in ["mnist", "cifar10"])
        details[enc] = {
            "ratios": per_zoo,
            "meets_gate": meets_both,
        }

    gate_passed = any(d["meets_gate"] for d in details.values())
    # SHOULD_WORK gate: failure logs as limitation, does not stop pipeline
    return gate_passed, details
    """
```

#### L-7-2: `verify_mechanism_activated_batch`

```python
def verify_mechanism_activated_batch(
    encoder_name: str,
    results: dict,        # full results dict (for loading encoder)
    device: str,
    zoo_name: str = "cifar10",
    n_check: int = 1,    # number of test-set models to check
) -> dict:
    """
    Sanity check: equivariance still holds after training (max_diff < 1e-4 on one batch).
    Inherited from H-M1 verify_mechanism_activated() pattern.

    Pseudo-code:
    # Load encoder (from checkpoint or rebuild)
    encoder = load_trained_encoder(encoder_name, zoo_name, device)
    # Load one zoo model
    train_ds, val_ds, test_ds = load_zoo(zoo_name)
    state_dict, _ = test_ds[0]
    # Apply permutation
    from permute import permute_weights, get_perm
    perm = get_perm(get_hidden_size(state_dict))
    sd_perm = permute_weights(state_dict, hidden_layer_key, perm)
    # Forward pass
    with torch.no_grad():
        out_orig = encoder_forward(encoder, encoder_name, state_dict, device)
        out_perm = encoder_forward(encoder, encoder_name, sd_perm, device)
    max_diff = (out_orig - out_perm).abs().max().item()
    return {
        "equivariance_holds": max_diff < 1e-4,
        "max_diff": max_diff,
        "encoder": encoder_name,
    }
    """
```
