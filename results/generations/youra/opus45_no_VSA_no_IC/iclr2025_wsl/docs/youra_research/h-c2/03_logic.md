# Logic Design: H-C2

**Hypothesis:** Crossing point N* where NFN matches Statistics R² at N* < 2500
**Type:** CONDITION

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: API signatures verified from actual H-M2 code (NOT `pip install nfn`, NOT spec pseudocode in 02c)
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Relevant Symbols**: `NFNAccuracyPredictor`, `EquivariantLayer`, `PerNeuronMLP`, `extract_weight_tensors`, `collate_weights`, `ResNet20`, `generate_model_zoo`, `download_model_zoo`, `load_checkpoints`, `split_test_set`, `train_model`, `evaluate_model`, `set_seed`, `paired_ttest`

**Critical deviation from spec**: 02c_experiment_brief.md shows `pip install nfn` library usage (`WeightSpaceFeatures`, `layers.NPLinear`). Actual H-M2 code implements a **custom DeepSets-style equivariant NFN** — no external `nfn` package dependency. H-C2 reuses this actual implementation for consistency with the base hypothesis. Statistics baseline (`stats.py` in H-M2) only contains significance-testing utilities, not a feature extractor — H-C2 must implement `StatisticsExtractor`/`StatisticsPredictor` fresh (not present in H-M2).

---

## 1. Model Zoo Loading & Weight Extraction

**Applied**: Reuse `data.py` from H-M2 verbatim (ResNet20 synthetic zoo generator + loader).

```python
# Reused from h-m2/code/data.py — import directly or copy unmodified
from data import ResNet20, download_model_zoo, load_checkpoints, split_test_set

# items: List[Tuple[state_dict, float]]  where state_dict values are param tensors
zoo_path = download_model_zoo(dest_dir="data/model_zoo")   # generates/loads 6000 synthetic CIFAR CNN checkpoints
items = load_checkpoints(zoo_path)
train_pool, test_set = split_test_set(items, test_size=500, seed=42)
# train_pool: 5500 items available for subsampling N in {100,250,500,1000,2500}
# test_set: fixed 500 items, identical across all N/seed combos
```

## 2. NFNAccuracyPredictor (reused from H-M2, unmodified)

**Applied**: DeepSets-style permutation-equivariant weight encoder (custom, not `pip install nfn`).

```python
class NFNAccuracyPredictor(nn.Module):
    def __init__(self, hidden_dim: int = 128, num_layers: int = 3):
        ...
    def forward(self, weight_tensors: List[Tensor]) -> Tensor:
        """weight_tensors: list of [B, out_ch, in_ch] per layer -> [B] predicted accuracy."""
        ...

def extract_weight_tensors(state_dict: dict) -> List[Tensor]:
    """Per-layer weight tensors, each [1, out_ch, in_ch] (batch dim added)."""

def collate_weights(items: List[Tuple[dict, float]]) -> Tuple[List[Tensor], Tensor]:
    """-> (batched: list of [B, out_ch, in_ch] per layer, accs: [B])"""
```

| Variable | Shape | Note |
|----------|-------|------|
| weight (per layer) | [B, out_ch, in_ch] | conv weights reshaped via `w.reshape(B, out_ch, -1)` if dim>3 |
| row_stats/col_stats | [B, out_ch, 7] | 7 handcrafted per-row/col stats |
| pooled feature | [B, hidden_dim] | after mean-pool over rows/cols |
| output | [B] | predicted accuracy (squeeze(-1)) |

## 3. StatisticsExtractor (new — per Unterthiner et al.)

**Applied**: Standard PyTorch tensor stats, no KB pattern needed.

```python
def extract_statistics(state_dict: dict) -> torch.Tensor:
    """Per-layer [mean, std, L2 norm, spectral norm] concatenated -> [F]"""
    features = []
    for name, param in state_dict.items():
        if 'weight' in name.lower() and param.dim() >= 2:
            w2d = param.reshape(param.size(0), -1)  # [out_ch, in_ch*k*k]
            features.extend([
                param.mean().item(),
                param.std().item(),
                param.norm(2).item(),
                torch.linalg.svdvals(w2d)[0].item(),  # spectral norm
            ])
    features.append(sum(p.numel() for p in state_dict.values()))  # total params
    features.append(sum(1 for n in state_dict if 'weight' in n.lower()))  # layer count
    return torch.tensor(features, dtype=torch.float32)  # [F], F ~ 20-50


def collate_statistics(items: List[Tuple[dict, float]]) -> Tuple[Tensor, Tensor]:
    """-> (X: [B, F], y: [B])"""
    feats = torch.stack([extract_statistics(sd) for sd, _ in items])  # [B, F]
    accs = torch.tensor([acc for _, acc in items], dtype=torch.float32)  # [B]
    return feats, accs
```

## 4. StatisticsPredictor (linear regressor)

```python
class StatisticsPredictor(nn.Module):
    def __init__(self, in_dim: int):
        super().__init__()
        self.linear = nn.Linear(in_dim, 1)

    def forward(self, x: Tensor) -> Tensor:
        """x: [B, F] -> [B]"""
        return self.linear(x).squeeze(-1)
```

Note: feature dim `F` must be normalized (StandardScaler) before fitting — fit scaler on train split only, per seed.

```python
from sklearn.preprocessing import StandardScaler

def fit_scaler(X_train: torch.Tensor) -> StandardScaler:
    scaler = StandardScaler().fit(X_train.numpy())
    return scaler

def apply_scaler(X: torch.Tensor, scaler: StandardScaler) -> torch.Tensor:
    return torch.tensor(scaler.transform(X.numpy()), dtype=torch.float32)
```

## 5. Training Loop with Early Stopping

**Applied**: Extend H-M2's `train_model` (which has no val split) with early stopping using an internal val carve-out — required per PRD (patience=10).

```python
def train_model_early_stop(
    model: nn.Module,
    train_items: list,
    collate_fn: Callable,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    batch_size: int = 32,
    max_epochs: int = 100,
    patience: int = 10,
    val_frac: float = 0.15,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> Dict[str, List[float]]:
    """Adam + MSE, early stop on val loss plateau. Returns history dict."""
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.MSELoss()

    n_val = max(1, int(len(train_items) * val_frac))
    val_items, fit_items = train_items[:n_val], train_items[n_val:]

    best_val_loss, patience_ctr, best_state = float("inf"), 0, None
    history = {"train_loss": [], "val_loss": []}

    for epoch in range(max_epochs):
        model.train()
        indices = torch.randperm(len(fit_items)).tolist()
        train_losses = []
        for start in range(0, len(indices), batch_size):
            batch = [fit_items[i] for i in indices[start:start + batch_size]]
            inputs, targets = collate_fn(batch)
            inputs = [w.to(device) for w in inputs] if isinstance(inputs, list) else inputs.to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            pred = model(inputs)
            loss = criterion(pred, targets)
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())

        val_loss = _eval_loss(model, val_items, collate_fn, criterion, device)
        history["train_loss"].append(np.mean(train_losses))
        history["val_loss"].append(val_loss)

        if val_loss < best_val_loss - 1e-5:
            best_val_loss, patience_ctr = val_loss, 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            patience_ctr += 1
            if patience_ctr >= patience:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    return history


def _eval_loss(model, items, collate_fn, criterion, device) -> float:
    model.eval()
    with torch.no_grad():
        inputs, targets = collate_fn(items)
        inputs = [w.to(device) for w in inputs] if isinstance(inputs, list) else inputs.to(device)
        targets = targets.to(device)
        return criterion(model(inputs), targets).item()
```

For N=100, `val_frac=0.15` gives only ~15 val models — acceptable per PRD (uses paper defaults, no HPO).

## 6. Evaluation & Metrics

**Applied**: Reuse `evaluate_model` pattern from H-M2, extend with Kendall's τ.

```python
from sklearn.metrics import r2_score, mean_squared_error
from scipy.stats import kendalltau

def evaluate_model(
    model: nn.Module, test_items: list, collate_fn: Callable,
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
) -> Dict[str, Any]:
    """-> {r2, mse, kendall_tau, kendall_p, y_true: [N_test], y_pred: [N_test]}"""
    model = model.to(device).eval()
    preds, targets_list = [], []
    with torch.no_grad():
        for start in range(0, len(test_items), 32):
            batch = test_items[start:start + 32]
            inputs, targets = collate_fn(batch)
            inputs = [w.to(device) for w in inputs] if isinstance(inputs, list) else inputs.to(device)
            pred = model(inputs)
            preds.extend(pred.cpu().numpy())
            targets_list.extend(targets.numpy())

    y_true, y_pred = np.array(targets_list), np.array(preds)  # [500] each
    tau, tau_p = kendalltau(y_true, y_pred)
    return {
        "r2": r2_score(y_true, y_pred),
        "mse": mean_squared_error(y_true, y_pred),
        "kendall_tau": float(tau),
        "kendall_p": float(tau_p),
        "y_true": y_true, "y_pred": y_pred,
    }
```

## 7. Crossing Point Detection Algorithm

**Applied**: Standard PyTorch/numpy scan, per PRD verification protocol.

```python
def compute_ci95(scores: List[float]) -> Tuple[float, float]:
    """Mean +/- 1.96*sem -> (lower, upper)."""
    arr = np.array(scores)
    mean, sem = arr.mean(), arr.std(ddof=1) / np.sqrt(len(arr))
    return mean - 1.96 * sem, mean + 1.96 * sem


def find_crossing_point(
    nfn_r2_by_n: Dict[int, List[float]],   # {N: [r2_seed0, ..., r2_seed9]}
    stats_r2_by_n: Dict[int, List[float]],
    threshold: float = 0.03,
) -> Optional[Dict[str, Any]]:
    """First N (ascending) where |mean NFN R2 - mean Stats R2| < threshold
    AND 95% CIs overlap. Returns None if no crossing found."""
    for n in sorted(nfn_r2_by_n.keys()):
        nfn_mean = np.mean(nfn_r2_by_n[n])
        stats_mean = np.mean(stats_r2_by_n[n])
        delta = abs(nfn_mean - stats_mean)

        nfn_lo, nfn_hi = compute_ci95(nfn_r2_by_n[n])
        stats_lo, stats_hi = compute_ci95(stats_r2_by_n[n])
        ci_overlap = nfn_lo <= stats_hi and stats_lo <= nfn_hi

        if delta < threshold and ci_overlap:
            return {"n_star": n, "delta": delta, "nfn_r2": nfn_mean,
                    "stats_r2": stats_mean, "ci_overlap": ci_overlap}
    return None
```

## 8. Main Experiment Orchestration

```python
N_VALUES = [100, 250, 500, 1000, 2500]
SEEDS = list(range(10))

def run_experiment():
    zoo_path = download_model_zoo()
    items = load_checkpoints(zoo_path)
    train_pool, test_set = split_test_set(items, test_size=500, seed=42)

    results = []  # rows: {n, seed, method, r2, mse, kendall_tau}

    for n in N_VALUES:
        for seed in SEEDS:
            set_seed(seed)
            rng = random.Random(seed)
            train_subset = rng.sample(train_pool, n)

            # NFN
            nfn = NFNAccuracyPredictor(hidden_dim=128)
            train_model_early_stop(nfn, train_subset, collate_weights)
            nfn_metrics = evaluate_model(nfn, test_set, collate_weights)
            results.append({"n": n, "seed": seed, "method": "nfn", **_strip_arrays(nfn_metrics)})

            # Statistics
            X_train, y_train = collate_statistics(train_subset)
            scaler = fit_scaler(X_train)
            X_train_s = apply_scaler(X_train, scaler)
            stats_model = StatisticsPredictor(in_dim=X_train_s.shape[1])
            train_model_early_stop(
                stats_model,
                list(zip(X_train_s, y_train)),
                collate_fn=lambda b: (torch.stack([x for x, _ in b]), torch.stack([y for _, y in b])),
            )
            X_test, y_test = collate_statistics(test_set)
            X_test_s = apply_scaler(X_test, scaler)
            stats_metrics = _eval_stats(stats_model, X_test_s, y_test)
            results.append({"n": n, "seed": seed, "method": "stats", **stats_metrics})

    nfn_r2_by_n = {n: [r["r2"] for r in results if r["n"] == n and r["method"] == "nfn"] for n in N_VALUES}
    stats_r2_by_n = {n: [r["r2"] for r in results if r["n"] == n and r["method"] == "stats"] for n in N_VALUES}

    crossing = find_crossing_point(nfn_r2_by_n, stats_r2_by_n, threshold=0.03)
    gate_pass = crossing is not None and crossing["n_star"] < 2500

    save_results(results, crossing, gate_pass, "results.json")
    plot_crossing_point(nfn_r2_by_n, stats_r2_by_n, crossing, "figures/crossing_point.png")
    return results, crossing, gate_pass


def _eval_stats(model, X_test, y_test) -> Dict[str, Any]:
    model.eval()
    with torch.no_grad():
        pred = model(X_test).numpy()
    y_true = y_test.numpy()
    tau, tau_p = kendalltau(y_true, pred)
    return {"r2": r2_score(y_true, pred), "mse": mean_squared_error(y_true, pred),
            "kendall_tau": float(tau), "kendall_p": float(tau_p)}
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C2-1 | Data reuse | Import `data.py` from H-M2 unmodified |
| L-C2-2 | NFN reuse | Import `nfn_model.py` from H-M2 unmodified |
| L-C2-3 | StatisticsExtractor | New: per-layer mean/std/L2/spectral norm |
| L-C2-4 | StatisticsPredictor | New: linear regressor + scaler |
| L-C2-5 | Early-stop training | Extend H-M2 `train_model` with val split + patience |
| L-C2-6 | Evaluation | Extend H-M2 `evaluate_model` with Kendall's τ |
| L-C2-7 | Crossing detection | `find_crossing_point` with CI overlap check |
| L-C2-8 | Orchestration | `run_experiment` loop, results.json, figure |

---

*Phase 3 Logic Document — designed by Logic Agent*
</content>
