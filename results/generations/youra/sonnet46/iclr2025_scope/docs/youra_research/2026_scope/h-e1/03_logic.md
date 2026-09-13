# Logic: H-E1 — Activation Sparsity Existence Check for LLaMA-3-8B

**Hypothesis Type**: EXISTENCE (PoC/measurement-only)
**Applied**: PyTorch register_forward_hook layerwise pattern (torch.nn.Module)
**Applied**: Magnitude-based sparsity thresholding |a| < epsilon (TEAL calibration methodology)

Applied: PyTorch register_forward_hook layerwise pattern (torch.nn.Module)
Applied: Magnitude-based sparsity thresholding |a| < epsilon (TEAL calibration methodology)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## E3: Sparsity Measurement Engine [Complexity: 14, Budget: 3]

### L-E3-1: register_hooks()

```python
def register_hooks(
    model: PreTrainedModel,
    epsilon: float,
    layer_counts: List[List[float]],  # shape: [32, n_batches_so_far]
) -> List[torch.utils.hooks.RemovableHook]:
    """Register gate_proj forward hooks on all 32 MLP layers."""
```

**Tensor shapes:**
- hook input `module_output`: `[B=8, seq_len, intermediate_size=14336]` FloatTensor
- computed per-call sparsity: scalar = `(output.abs() < epsilon).float().mean().item()`
- `layer_counts[i]`: list of scalars, one per batch, accumulated across calls

**Pseudo-code:**

```
hooks = []
for i in range(cfg.n_layers):  # 0..31
    layer_module = model.model.layers[i].mlp.gate_proj

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            # output: [B, seq_len, 14336]
            sparsity_val = (output.abs() < epsilon).float().mean().item()
            layer_counts[layer_idx].append(sparsity_val)
        return hook_fn

    handle = layer_module.register_forward_hook(make_hook(i))
    hooks.append(handle)

return hooks  # List[RemovableHook], len=32
```

**Edge cases:**
- If `model.model.layers[i].mlp.gate_proj` does not exist → `AttributeError` propagates; caller validates in `setup_model_and_tokenizer()` first
- Closure must capture `layer_idx` via `make_hook(i)` pattern (not `i` directly)

---

### L-E3-2: measure_layer_sparsity()

```python
def measure_layer_sparsity(
    model: PreTrainedModel,
    dataloader: DataLoader,
    epsilon: float,
    cfg: ExperimentConfig,
) -> np.ndarray:
    """Run forward passes with hooks; return per-layer mean sparsity. Returns shape (32,)."""
```

**Tensor shapes:**
- `batch["input_ids"]`: `[B=8, seq_len]` LongTensor
- hook captures `gate_proj` output: `[B=8, seq_len, 14336]` FloatTensor
- `layer_counts[i]`: list of scalars (one per batch) → `np.mean(layer_counts[i])` → scalar
- return: `np.ndarray` shape `(32,)`, dtype float64

**Pseudo-code:**

```
layer_counts = [[] for _ in range(cfg.n_layers)]  # 32 empty lists
hooks = register_hooks(model, epsilon, layer_counts)

try:
    model.eval()
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(model.device)  # [8, seq_len]
            model(input_ids)
            # hooks fire automatically; layer_counts[i] appended per layer
finally:
    for h in hooks:
        h.remove()  # guaranteed cleanup

# Aggregate
layer_sparsity = np.array([np.mean(layer_counts[i]) for i in range(cfg.n_layers)])
# shape: (32,)

# Mechanism verification
assert len(layer_sparsity) == cfg.n_layers, "Not all hooks fired"
assert layer_sparsity.mean() > 0.0, "Zero sparsity detected"

return layer_sparsity  # (32,)
```

**Edge cases:**
- Empty dataloader → `layer_counts[i]` stays empty → `np.mean([])` → NaN; guard with `len(dataloader) > 0` check before loop
- Exception during forward pass → `finally` block removes hooks regardless

---

### L-E3-3: run_all_conditions()

```python
def run_all_conditions(
    model: PreTrainedModel,
    alpaca_short: DataLoader,   # max_length=128
    alpaca_long: DataLoader,    # max_length=512
    wikitext_long: DataLoader,  # max_length=512
    cfg: ExperimentConfig,
) -> dict:
    """Sweep 3 datasets × 4 epsilons = 12 measurements. Returns dict keyed by (dataset, epsilon, length)."""
```

**Return type:**
- `dict[(str, float, int), np.ndarray]`
- key: `("alpaca", 0.01, 128)` → value: `np.ndarray` shape `(32,)`

**Pseudo-code:**

```
results = {}

dataset_configs = [
    ("alpaca",   alpaca_short,   cfg.short_length),   # 128
    ("alpaca",   alpaca_long,    cfg.long_length),     # 512
    ("wikitext", wikitext_long,  cfg.long_length),     # 512
]

for eps in cfg.epsilons:  # [0.001, 0.01, 0.05, 0.1]
    for (dataset_name, dataloader, length) in dataset_configs:
        key = (dataset_name, eps, length)
        print(f"Measuring: dataset={dataset_name}, eps={eps}, length={length}")
        layer_sparsity = measure_layer_sparsity(model, dataloader, eps, cfg)
        results[key] = layer_sparsity  # shape (32,)

# Total: 4 epsilons × 3 dataloaders = 12 entries
return results
```

**Edge cases:**
- `("alpaca", eps, 128)` and `("alpaca", eps, 512)` share same dataset name with different length key
- Key collision impossible due to length differentiation in tuple

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1 | register_hooks | Closure-based hook factory for 32 gate_proj layers |
| L-E3-2 | measure_layer_sparsity | Forward pass loop with try/finally hook cleanup |
| L-E3-3 | run_all_conditions | 3×4 condition sweep returning keyed dict |

---

## E5: Visualization [Complexity: 12, Budget: 3]

### L-E5-1: plot_sparsity_profile()

```python
def plot_sparsity_profile(
    alpaca_sparsity: np.ndarray,    # shape (32,)
    wikitext_sparsity: np.ndarray,  # shape (32,)
    epsilon: float,
    cfg: ExperimentConfig,
    save_path: Path,
) -> None:
    """Per-layer sparsity line plot, Alpaca vs WikiText overlaid. Saves to save_path."""
```

**Pseudo-code:**

```
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(cfg.n_layers)  # [0..31]

ax.plot(x, alpaca_sparsity,   label="Alpaca (512-tok)",    marker="o", linewidth=1.5)
ax.plot(x, wikitext_sparsity, label="WikiText-103 (512-tok)", marker="s", linewidth=1.5)

ax.set_xlabel("Layer Index")
ax.set_ylabel(f"Mean Sparsity Fraction (|a| < {epsilon})")
ax.set_title(f"Per-Layer Activation Sparsity (epsilon={epsilon})")
ax.set_xticks(x[::4])  # every 4th layer label
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(save_path, dpi=150, bbox_inches="tight")
plt.close(fig)
```

---

### L-E5-2: plot_gate_metrics_bar()

```python
def plot_gate_metrics_bar(
    cv: float,
    tau: float,
    cfg: ExperimentConfig,
    save_path: Path,
) -> None:
    """Bar chart: CV vs 0.3 threshold, tau vs 0.6 threshold. Saves to save_path."""
```

**Pseudo-code:**

```
fig, ax = plt.subplots(figsize=(6, 5))

metrics   = [cv,  tau]
thresholds = [cfg.cv_threshold, cfg.tau_threshold]  # [0.3, 0.6]
labels    = ["CV (epsilon=0.01)", "Kendall tau\n(Alpaca vs WikiText)"]
colors    = ["steelblue" if v > t else "tomato" for v, t in zip(metrics, thresholds)]

bars = ax.bar(labels, metrics, color=colors, edgecolor="black", width=0.4)

# Threshold lines
ax.axhline(cfg.cv_threshold,  color="steelblue", linestyle="--", alpha=0.7, label=f"CV threshold={cfg.cv_threshold}")
ax.axhline(cfg.tau_threshold, color="darkorange", linestyle="--", alpha=0.7, label=f"tau threshold={cfg.tau_threshold}")

# Value annotations on bars
for bar, val in zip(bars, metrics):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f"{val:.3f}", ha="center", va="bottom", fontsize=11)

ax.set_ylabel("Metric Value")
ax.set_title("Gate Condition Metrics (H-E1)")
ax.set_ylim(0, max(max(metrics), 1.0) * 1.15)
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(save_path, dpi=150, bbox_inches="tight")
plt.close(fig)
```

---

### L-E5-3: plot_rank_correlation_scatter()

```python
def plot_rank_correlation_scatter(
    alpaca_sparsity: np.ndarray,    # shape (32,)
    wikitext_sparsity: np.ndarray,  # shape (32,)
    tau: float,
    p_value: float,
    cfg: ExperimentConfig,
    save_path: Path,
) -> None:
    """Scatter of rank arrays (Alpaca vs WikiText) with Kendall tau annotation."""
```

**Pseudo-code:**

```
alpaca_ranks   = np.argsort(np.argsort(alpaca_sparsity))    # rank [0..31]
wikitext_ranks = np.argsort(np.argsort(wikitext_sparsity))  # rank [0..31]

fig, ax = plt.subplots(figsize=(6, 6))
ax.scatter(alpaca_ranks, wikitext_ranks, s=60, edgecolors="black", alpha=0.8)

# Perfect-correlation diagonal
ax.plot([0, 31], [0, 31], "k--", alpha=0.4, label="Perfect rank agreement")

# Tau annotation
ax.text(0.05, 0.92, f"Kendall tau = {tau:.3f}\np = {p_value:.3e}",
        transform=ax.transAxes, fontsize=11, verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

ax.set_xlabel("Alpaca Layer Rank (by sparsity)")
ax.set_ylabel("WikiText-103 Layer Rank (by sparsity)")
ax.set_title("Rank Correlation: Alpaca vs WikiText-103")
ax.legend()
plt.tight_layout()
plt.savefig(save_path, dpi=150, bbox_inches="tight")
plt.close(fig)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E5-1 | plot_sparsity_profile | 32-layer line plot, two datasets overlaid |
| L-E5-2 | plot_gate_metrics_bar | Bar chart with threshold lines at 0.3 and 0.6 |
| L-E5-3 | plot_rank_correlation_scatter | Rank scatter with tau annotation |

---

## E6: Orchestration [Complexity: 11, Budget: 2]

### L-E6-1: setup_model_and_tokenizer()

```python
def setup_model_and_tokenizer(
    cfg: ExperimentConfig,
) -> tuple[PreTrainedModel, PreTrainedTokenizer]:
    """Load LLaMA-3-8B float16, eval mode, device_map='auto'. Validates 32 layers + gate_proj."""
```

**Pseudo-code:**

```
tokenizer = AutoTokenizer.from_pretrained(cfg.model_name)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    cfg.model_name,
    torch_dtype=torch.float16,
    device_map="auto",
)
model.eval()

# Architecture validation
n_layers = len(model.model.layers)
if n_layers != cfg.n_layers:
    raise RuntimeError(f"Expected {cfg.n_layers} layers, got {n_layers}. Not LLaMA-3-8B.")

for i in range(cfg.n_layers):
    if not hasattr(model.model.layers[i].mlp, "gate_proj"):
        raise RuntimeError(f"Layer {i} MLP has no gate_proj. Architecture mismatch.")

print(f"Model loaded: {cfg.n_layers} layers, gate_proj verified.")
return model, tokenizer
```

**Edge cases:**
- `RuntimeError` on architecture mismatch — explicit failure required (NFR-7)
- Tokenizer without pad token → set to eos_token (LLaMA-3 has no pad by default)

---

### L-E6-2: save_results()

```python
def save_results(
    condition_results: dict,    # {(dataset, epsilon, length): np.ndarray(32,)}
    metrics: dict,              # flat dict of floats
    gate_pass: bool,
    cfg: ExperimentConfig,
) -> None:
    """Save results.json summary and per-condition arrays. Output dir: cfg.results_dir."""
```

**JSON schema for `results.json`:**

```json
{
  "hypothesis": "H-E1",
  "gate_pass": true,
  "primary_metrics": {
    "cv_primary": 0.412,
    "tau_calibration": 0.731,
    "tau_length": 0.698,
    "cv_primary_pass": true,
    "tau_calibration_pass": true
  },
  "all_metrics": {
    "cv_alpaca_long_eps0.001": 0.389,
    "cv_alpaca_long_eps0.01": 0.412,
    "cv_alpaca_long_eps0.05": 0.445,
    "cv_alpaca_long_eps0.1": 0.431,
    "tau_calibration_eps0.001": 0.712,
    "tau_calibration_eps0.01": 0.731,
    "tau_calibration_eps0.05": 0.744,
    "tau_calibration_eps0.1": 0.739,
    "tau_length_eps0.01": 0.698
  },
  "layer_sparsity_conditions": {
    "alpaca_eps0.01_len512": [0.12, 0.08, ...],
    "wikitext_eps0.01_len512": [0.11, 0.09, ...]
  }
}
```

**Pseudo-code:**

```
results_path = Path(cfg.results_dir)
results_path.mkdir(parents=True, exist_ok=True)

# Serialize condition_results (tuple keys → string keys)
layer_arrays = {}
for (dataset, eps, length), arr in condition_results.items():
    key = f"{dataset}_eps{eps}_len{length}"
    layer_arrays[key] = arr.tolist()  # list of 32 floats

summary = {
    "hypothesis": "H-E1",
    "gate_pass": gate_pass,
    "primary_metrics": {
        "cv_primary": metrics["cv_primary"],
        "tau_calibration": metrics["tau_calibration"],
        "tau_length": metrics.get("tau_length"),
        "cv_primary_pass": metrics["cv_primary"] > cfg.cv_threshold,
        "tau_calibration_pass": metrics["tau_calibration"] >= cfg.tau_threshold,
    },
    "all_metrics": {k: v for k, v in metrics.items() if isinstance(v, float)},
    "layer_sparsity_conditions": layer_arrays,
}

with open(results_path / "results.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"Results saved to {results_path / 'results.json'}")
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E6-1 | setup_model_and_tokenizer | Load + validate 32 layers with gate_proj access |
| L-E6-2 | save_results | JSON serialization with schema above |

---

## E4: Metrics Computation [Complexity: 10, Budget: 1]

### L-E4-1: compute_all_metrics()

```python
def compute_all_metrics(
    condition_results: dict,    # {(dataset, epsilon, length): np.ndarray(32,)}
    cfg: ExperimentConfig,
) -> dict:
    """Compute CV and Kendall tau for all epsilon conditions. Returns flat metrics dict."""
```

**Return dict schema:**

```python
{
    # Primary gate metrics (epsilon=0.01, long condition)
    "cv_primary": float,           # CV of alpaca_long at primary_epsilon
    "tau_calibration": float,      # tau(alpaca_long, wikitext_long) at primary_epsilon
    "tau_calibration_pval": float,
    "tau_length": float,           # tau(alpaca_short, alpaca_long) at primary_epsilon
    "tau_length_pval": float,

    # Per-epsilon sweep
    "cv_alpaca_long_eps{e}": float,           # for e in epsilons
    "tau_calibration_eps{e}": float,          # for e in epsilons
    "tau_calibration_pval_eps{e}": float,
    "tau_length_eps{e}": float,               # for e in epsilons
    "tau_length_pval_eps{e}": float,
}
```

**Pseudo-code:**

```
metrics = {}

for eps in cfg.epsilons:  # [0.001, 0.01, 0.05, 0.1]
    eps_key = str(eps)

    alpaca_long   = condition_results[("alpaca",   eps, cfg.long_length)]   # (32,)
    alpaca_short  = condition_results[("alpaca",   eps, cfg.short_length)]  # (32,)
    wikitext_long = condition_results[("wikitext", eps, cfg.long_length)]   # (32,)

    # CV: coefficient of variation across 32 layers
    cv = alpaca_long.std() / alpaca_long.mean()
    metrics[f"cv_alpaca_long_eps{eps_key}"] = float(cv)

    # Kendall tau: calibration stability (Alpaca vs WikiText)
    tau_cal, p_cal = kendalltau(alpaca_long, wikitext_long)
    metrics[f"tau_calibration_eps{eps_key}"]      = float(tau_cal)
    metrics[f"tau_calibration_pval_eps{eps_key}"] = float(p_cal)

    # Kendall tau: length stability (short vs long Alpaca)
    tau_len, p_len = kendalltau(alpaca_short, alpaca_long)
    metrics[f"tau_length_eps{eps_key}"]      = float(tau_len)
    metrics[f"tau_length_pval_eps{eps_key}"] = float(p_len)

# Primary metrics (epsilon = cfg.primary_epsilon = 0.01)
primary = str(cfg.primary_epsilon)
metrics["cv_primary"]             = metrics[f"cv_alpaca_long_eps{primary}"]
metrics["tau_calibration"]        = metrics[f"tau_calibration_eps{primary}"]
metrics["tau_calibration_pval"]   = metrics[f"tau_calibration_pval_eps{primary}"]
metrics["tau_length"]             = metrics[f"tau_length_eps{primary}"]
metrics["tau_length_pval"]        = metrics[f"tau_length_pval_eps{primary}"]

return metrics
```

**Edge cases:**
- `alpaca_long.mean() == 0.0` → division by zero in CV → guard: `if mean == 0: cv = 0.0`
- Missing key in `condition_results` → `KeyError`; caller must ensure all 12 conditions populated

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-1 | compute_all_metrics | CV + tau sweep across 4 epsilons, returns flat dict |

---

## Tensor Shape Summary

| Variable | Shape | Dtype | Notes |
|----------|-------|-------|-------|
| `input_ids` batch | `[8, seq_len]` | LongTensor | seq_len = 128 or 512 |
| `gate_proj` output (hook) | `[8, seq_len, 14336]` | FloatTensor (fp16) | intermediate_size=14336 for LLaMA-3-8B |
| sparsity scalar per batch | scalar | float | `(output.abs() < eps).float().mean().item()` |
| `layer_sparsity` | `(32,)` | float64 | mean across batches per layer |
| `condition_results` value | `(32,)` | float64 | one per (dataset, epsilon, length) |
| alpaca/wikitext ranks | `(32,)` | int64 | `np.argsort(np.argsort(arr))` |

---

*Hypothesis: H-E1 | Type: EXISTENCE | Budget: 9 subtasks used (3+3+2+1)*
