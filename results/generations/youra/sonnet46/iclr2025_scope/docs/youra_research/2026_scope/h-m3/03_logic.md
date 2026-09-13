# Logic: H-M3 Sparsity-Rank Sensitivity Correlation

**Generated:** 2026-05-08
**Hypothesis:** H-M3 (MECHANISM) — Incremental from h-m2

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental from h-m2)
**Status**: API signatures verified from actual h-m2 code (Serena MCP had no active project; files read directly)
**Analyzed Path**: `/home/anonymous/YouRA_results_new_4/TEST_scope_4/docs/youra_research/20260508_scope/h-m2/code/`
**Relevant Symbols**:
- `measure_layer_sparsity(model, dataloader: DataLoader, epsilon: float, cfg: ExperimentConfig) -> np.ndarray` — shape (32,)
- `register_hooks(model, epsilon: float, layer_counts: List[List[float]]) -> List`
- `ExperimentConfig` — h-m2 config (NOT reused; h-m3 defines own)
- `load_alpaca_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int) -> DataLoader`
- `load_wikitext_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int) -> DataLoader`
- h-m2 `data_utils.py` has NO GLUE loading — h-m3 must implement its own

---

## External Dependencies API

Applied: LoRA rank_pattern budget-neutral perturbation pattern (HF PEFT conceptual guide)
Applied: Covariance-based SVD via eigvalsh (spectral efficiency pattern)
Applied: Semipartial r² via sklearn LinearRegression + statsmodels OLS

### API Signatures (From Actual h-m2 Code)

```python
# From: h-m2/code/measure_sparsity.py (ACTUAL CODE)
def measure_layer_sparsity(
    model,
    dataloader: DataLoader,
    epsilon: float,
    cfg: ExperimentConfig,   # h-m2 ExperimentConfig — NOT reused in h-m3
) -> np.ndarray:
    """Returns per-layer mean sparsity. shape: (32,)"""
    ...

# From: h-m2/code/data_utils.py (ACTUAL CODE)
# NOTE: Only Alpaca + WikiText loaders exist — NO GLUE loading
def load_alpaca_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int) -> DataLoader: ...
def load_wikitext_dataloader(tokenizer, cfg: ExperimentConfig, max_length: int) -> DataLoader: ...

# From: h-m2/code/config.py (ACTUAL CODE — for reference only, NOT imported)
# h-m2 ExperimentConfig fields: model_name, n_layers=32, epsilons, primary_epsilon=0.01
# h-m3 uses its OWN ExperimentConfig (different fields)
```

**h-m3 reads sparsity from**: `h-m2/experiment_results.json["sparsity_profiles"]["0.01"]` — no import needed.

---

## A-3: Joint Rank Sensitivity Sweep [Complexity: 18, Budget: 5 subtasks]

### L-A3-1: `build_joint_rank_pattern`

```python
def build_joint_rank_pattern(
    perturbed_layer_idx: int,
    delta_r: int,
    r_base: int,
    n_layers: int,
    target_modules: List[str],
) -> Dict[str, int]:
    """Build budget-neutral rank_pattern for LoraConfig.
    Reduces layer perturbed_layer_idx by delta_r; distributes freed budget
    proportionally to remaining layers. Minimum rank = 1.
    Returns: dict mapping 'base_model.model.layers.{l}.{proj}' -> rank
             Total entries: n_layers * len(target_modules) = 32 * 7 = 224
    """
```

**Pseudo-code:**
```
freed_budget = len(target_modules) * delta_r  # 7 * delta_r per perturbed layer
remaining_layers = [i for i in range(n_layers) if i != perturbed_layer_idx]  # 31 layers
bonus_per_layer = freed_budget / len(remaining_layers)  # float

rank_pattern = {}
for l in range(n_layers):
    for proj in target_modules:
        key = f"base_model.model.layers.{l}.self_attn.{proj}" if "proj" in ["q","k","v","o"] else
              f"base_model.model.layers.{l}.mlp.{proj}"
        if l == perturbed_layer_idx:
            rank = max(1, r_base - delta_r)
        else:
            # floor allocation + top-up for integer budget
            rank = r_base + int(bonus_per_layer)
rank_pattern[key] = rank

# Top-up: distribute leftover integers to first (freed_budget % 31) remaining layers
leftover = freed_budget - sum of integer bonuses already distributed
for first leftover remaining layers: rank_pattern[key] += 1

return rank_pattern
```

### L-A3-2: `run_single_perturbation`

```python
def run_single_perturbation(
    task: str,
    seed: int,
    layer_idx: int,
    delta_r: int,
    baseline_acc: float,
    cfg: "ExperimentConfig",
) -> float:
    """Fine-tune with perturbed rank_pattern; return accuracy_drop.
    accuracy_drop = baseline_acc - perturbed_acc  (positive = worse)
    Logits: [B, num_labels]; labels: [B,] where num_labels=2 (sst2) or 3 (mnli)
    """
```

**Pseudo-code:**
```
set_seed(seed)
rank_pattern = build_joint_rank_pattern(layer_idx, delta_r, cfg.lora_r, cfg.n_layers, cfg.target_modules)
lora_cfg = LoraConfig(
    r=cfg.lora_r, lora_alpha=cfg.lora_r,
    rank_pattern=rank_pattern,
    target_modules=cfg.target_modules,
)
model = load_base_model(cfg, num_labels=get_num_labels(task))
model = get_peft_model(model, lora_cfg)
train_model(model, task, seed, cfg)  # 3 epochs, AdamW
perturbed_acc = evaluate_model(model, val_dl, task, cfg)
return baseline_acc - perturbed_acc
```

### L-A3-3: `run_sensitivity_sweep`

```python
def run_sensitivity_sweep(
    task: str,
    cfg: "ExperimentConfig",
    baseline_accs: Dict[int, float],  # seed -> baseline accuracy
) -> np.ndarray:
    """Run 32 * 5 = 160 perturbed runs for one task.
    Returns: accuracy_drops shape (32,) float32 — mean over seeds
    """
```

**Pseudo-code:**
```
drops = np.zeros((cfg.n_layers, len(cfg.seeds)), dtype=np.float32)
for l in range(cfg.n_layers):
    for s_idx, seed in enumerate(cfg.seeds):
        drops[l, s_idx] = run_single_perturbation(task, seed, l, cfg.delta_r,
                                                    baseline_accs[seed], cfg)
return drops.mean(axis=1)  # shape (32,)
```

### L-A3-4: `identify_sensitive_layers`

```python
def identify_sensitive_layers(
    accuracy_drops: np.ndarray,  # shape (32,)
    threshold: float = 0.005,
) -> np.ndarray:
    """Returns boolean mask shape (32,). True = drop >= threshold."""
```

**Pseudo-code:**
```
mask = accuracy_drops >= threshold
for l in range(len(accuracy_drops)):
    print(f"[SENSITIVITY] Layer {l}: accuracy_drop={accuracy_drops[l]:.4f}, sensitive={mask[l]}")
return mask
```

### L-A3-5: `check_delta_r_fallback`

```python
def check_delta_r_fallback(
    accuracy_drops: np.ndarray,  # shape (32,)
    threshold: float,
    cfg: "ExperimentConfig",
) -> int:
    """If no sensitive layers: log warning, return 4. Else return cfg.delta_r."""
```

**Pseudo-code:**
```
mask = accuracy_drops >= threshold
if mask.sum() == 0:
    print("[FALLBACK] No sensitive layers found, increasing delta_r to 4")
    return 4
return cfg.delta_r
```

---

## A-5: ΔW Spectral Analysis [Complexity: 17, Budget: 4 subtasks]

### L-A5-1: `compute_spectral_decay_ratio`

```python
def compute_spectral_decay_ratio(
    delta_w: torch.Tensor,  # shape (d_out, d_in), e.g., (4096, 4096) or (4096, 14336)
    top_k: int = 4,
) -> float:
    """Covariance-based SVD via eigvalsh.
    Returns: sum(top-k SVs) / frobenius_norm — scalar float
    """
```

**Pseudo-code:**
```
delta_w = delta_w.float()  # ensure float32
d_out, d_in = delta_w.shape
if d_out >= d_in:
    W = delta_w.T @ delta_w  # shape (d_in, d_in)
else:
    W = delta_w @ delta_w.T  # shape (d_out, d_out)
eigenvalues = torch.linalg.eigvalsh(W)  # shape (min(d_out, d_in),), ascending
singular_values = eigenvalues.clamp(min=0).sqrt()  # shape (min(d_out, d_in),)
sv_sorted = singular_values.flip(0)  # descending
top_k_sum = sv_sorted[:top_k].sum().item()
frob_norm = torch.norm(delta_w, 'fro').item()
return top_k_sum / (frob_norm + 1e-12)
```

### L-A5-2: `compute_all_spectral_decays`

```python
def compute_all_spectral_decays(
    delta_w_dict: Dict[str, torch.Tensor],  # layer_name -> ΔW
    cfg: "ExperimentConfig",
) -> np.ndarray:
    """Compute spectral_decay_ratio per MLP gate_proj layer.
    Key format: 'model.layers.{l}.mlp.gate_proj'
    Returns: np.ndarray shape (32,)
    """
```

**Pseudo-code:**
```
result = np.zeros(cfg.n_layers, dtype=np.float32)
for l in range(cfg.n_layers):
    key = f"model.layers.{l}.mlp.gate_proj"
    if key in delta_w_dict:
        result[l] = compute_spectral_decay_ratio(delta_w_dict[key], cfg.top_k_svs)
return result
```

### L-A5-3: `run_multiple_regression`

```python
def run_multiple_regression(
    sparsity: np.ndarray,      # shape (32,)
    grad_norms: np.ndarray,    # shape (32,)
    spectral_decay: np.ndarray,  # shape (32,)
) -> Dict:
    """Full and reduced OLS regression; compute semipartial r² for sparsity.
    Returns: {
        "r2_full": float,
        "r2_reduced": float,
        "unique_var_sparsity": float,      # r2_full - r2_reduced
        "p_value_sparsity_beta": float,
        "coef_sparsity": float,
        "coef_grad_norm": float,
    }
    """
```

**Pseudo-code:**
```
import statsmodels.api as sm

n = len(sparsity)
X_full = sm.add_constant(np.column_stack([sparsity, grad_norms]))  # (32, 3)
X_reduced = sm.add_constant(grad_norms.reshape(-1, 1))             # (32, 2)
y = spectral_decay

ols_full = sm.OLS(y, X_full).fit()
ols_reduced = sm.OLS(y, X_reduced).fit()

r2_full = ols_full.rsquared
r2_reduced = ols_reduced.rsquared
unique_var_sparsity = r2_full - r2_reduced

# p-value for sparsity coefficient (index 1 in full model, after intercept)
p_value_sparsity_beta = ols_full.pvalues[1]
coef_sparsity = ols_full.params[1]
coef_grad_norm = ols_full.params[2]

return {...}
```

### L-A5-4: `compute_semipartial_r2`

```python
def compute_semipartial_r2(
    sparsity: np.ndarray,       # shape (32,)
    grad_norms: np.ndarray,     # shape (32,)
    spectral_decay: np.ndarray, # shape (32,)
) -> Tuple[float, float]:
    """Convenience wrapper. Returns (unique_var_sparsity, p_value_sparsity_beta)."""
```

**Pseudo-code:**
```
results = run_multiple_regression(sparsity, grad_norms, spectral_decay)
return results["unique_var_sparsity"], results["p_value_sparsity_beta"]
```

---

## A-2: Uniform LoRA Trainer [Complexity: 16, Budget: 3 subtasks]

### L-A2-1: `train_uniform_lora`

```python
def train_uniform_lora(
    task: str,
    seed: int,
    cfg: "ExperimentConfig",
    return_delta_w: bool = True,
    return_grad_norms: bool = True,
) -> Dict:
    """Full training loop with gradient norm hooks.
    LoRA A: shape (r, d_in); LoRA B: shape (d_out, r); ΔW = B@A: (d_out, d_in)
    Returns: {
        "accuracy": float,
        "delta_w": Dict[str, torch.Tensor],   # layer_name -> ΔW, CPU
        "grad_norms": Dict[str, float],        # layer_name -> Frobenius norm
    }
    """
```

**Pseudo-code:**
```
set_seed(seed)
tokenizer = load_tokenizer(cfg)
model = load_base_model(cfg, num_labels=get_num_labels(task))
lora_cfg = LoraConfig(r=cfg.lora_r, lora_alpha=cfg.lora_r, target_modules=cfg.target_modules)
model = get_peft_model(model, lora_cfg)

train_dl = load_glue_dataloader(task, "train", tokenizer, cfg)
val_dl = load_glue_dataloader(task, "validation", tokenizer, cfg)

# Register backward hooks on gate_proj lora_A/lora_B for grad norm tracking
stored_grads = {}
hooks = []
for name, module in model.named_modules():
    if "gate_proj" in name and hasattr(module, "lora_A"):
        handle = module.lora_A.default.weight.register_hook(
            lambda grad, n=name: stored_grads.update({n + ".lora_A": grad.detach()})
        )
        hooks.append(handle)

optimizer = AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
scheduler = get_cosine_schedule_with_warmup(optimizer, warmup_ratio=cfg.warmup_ratio, ...)

for epoch in range(cfg.num_epochs):
    for batch in train_dl:
        logits = model(**batch).logits    # [B, num_labels]
        loss = cross_entropy(logits, batch["labels"])  # labels: [B,]
        loss.backward()
        optimizer.step(); scheduler.step(); optimizer.zero_grad()

for h in hooks: h.remove()

accuracy = evaluate_model(model, val_dl, task, cfg)
delta_w = compute_delta_w(model) if return_delta_w else {}
grad_norms = compute_grad_norms(stored_grads) if return_grad_norms else {}
return {"accuracy": accuracy, "delta_w": delta_w, "grad_norms": grad_norms}
```

### L-A2-2: `compute_delta_w`

```python
def compute_delta_w(model) -> Dict[str, torch.Tensor]:
    """Extract ΔW = lora_B.weight @ lora_A.weight for each LoRA layer.
    Key: 'model.layers.{l}.mlp.gate_proj' (and other projections)
    A shape: (r, d_in); B shape: (d_out, r); ΔW: (d_out, d_in)
    gate_proj ΔW: (4096, 14336); up_proj ΔW: (4096, 14336);
    down_proj ΔW: (14336, 4096); q/k/v/o_proj ΔW: (4096, 4096)
    Returns tensors detached and moved to CPU.
    """
```

**Pseudo-code:**
```
delta_w = {}
for name, module in model.named_modules():
    if hasattr(module, "lora_A") and hasattr(module, "lora_B"):
        A = module.lora_A.default.weight  # (r, d_in)
        B = module.lora_B.default.weight  # (d_out, r)
        dw = (B @ A).detach().cpu()       # (d_out, d_in)
        # Extract clean key: strip "base_model.model." prefix if present
        clean_key = name.replace("base_model.model.", "model.")
        delta_w[clean_key] = dw
return delta_w
```

### L-A2-3: `compute_grad_norms`

```python
def compute_grad_norms(
    stored_grads: Dict[str, torch.Tensor],  # hook-captured gradients
) -> Dict[str, float]:
    """Compute Frobenius norm of captured gradients per layer.
    Returns: Dict[layer_name -> float]
    """
```

**Pseudo-code:**
```
grad_norms = {}
for name, grad_tensor in stored_grads.items():
    norm = torch.norm(grad_tensor.float(), 'fro').item()
    # Normalize key to 'model.layers.{l}.mlp.gate_proj' format
    clean_key = name.replace(".lora_A", "").replace("base_model.model.", "model.")
    grad_norms[clean_key] = norm
return grad_norms
```

---

## A-4: AdaLoRA Runner [Complexity: 15, Budget: 2 subtasks]

### L-A4-1: `run_adalora`

```python
def run_adalora(
    task: str,
    seed: int,
    cfg: "ExperimentConfig",
) -> Dict[str, int]:
    """Train AdaLoRA at 60% budget (target_r=9 vs r_base=16).
    Returns: rank_pattern dict from model.base_model.rank_pattern
    """
```

**Pseudo-code:**
```
set_seed(seed)
tokenizer = load_tokenizer(cfg)
model = load_base_model(cfg, num_labels=get_num_labels(task))

adalora_cfg = AdaLoraConfig(
    target_r=cfg.adalora_target_r,          # 9
    init_r=cfg.adalora_init_r,              # 16
    tinit=cfg.adalora_tinit,                # 100
    tfinal=cfg.adalora_tfinal,              # 1500
    deltaT=cfg.adalora_deltaT,              # 10
    beta1=cfg.adalora_beta1,                # 0.85
    beta2=cfg.adalora_beta2,                # 0.85
    orth_reg_weight=cfg.adalora_orth_reg_weight,  # 0.5
    target_modules=cfg.target_modules,
)
model = get_peft_model(model, adalora_cfg)

from peft.tuners.adalora import RankAllocator
rankallocator = RankAllocator(model, peft_config=adalora_cfg, adapter_name="default")

train_dl = load_glue_dataloader(task, "train", tokenizer, cfg)
optimizer = AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
global_step = 0

for epoch in range(cfg.num_epochs):
    for batch in train_dl:
        logits = model(**batch).logits  # [B, num_labels]
        loss = cross_entropy(logits, batch["labels"])
        loss.backward()
        optimizer.step(); optimizer.zero_grad()
        rankallocator.update_and_mask(model, global_step)
        global_step += 1

return extract_rank_pattern(model)
```

### L-A4-2: `rank_pattern_to_array`

```python
def rank_pattern_to_array(
    rank_pattern: Dict[str, int],
    n_layers: int = 32,
) -> np.ndarray:
    """Convert rank_pattern keys to ordered (32,) array.
    Aggregation: max rank across 7 projection types per layer.
    Key format: 'base_model.model.layers.{l}.mlp.gate_proj' -> extract l
    Returns: np.ndarray shape (32,)
    """
```

**Pseudo-code:**
```
import re
layer_ranks = {l: [] for l in range(n_layers)}
for key, rank in rank_pattern.items():
    match = re.search(r'layers\.(\d+)\.', key)
    if match:
        l = int(match.group(1))
        if 0 <= l < n_layers:
            layer_ranks[l].append(rank)

result = np.zeros(n_layers, dtype=np.float32)
for l in range(n_layers):
    result[l] = max(layer_ranks[l]) if layer_ranks[l] else 0.0
return result
```

---

## A-6: Correlation Analysis [Complexity: 13, Budget: 2 subtasks]

### L-A6-1: `compute_pearson_r`

```python
def compute_pearson_r(
    sparsity: np.ndarray,        # shape (32,)
    accuracy_drops: np.ndarray,  # shape (32,)
    sensitive_mask: np.ndarray,  # shape (32,) boolean
) -> Tuple[float, float]:
    """Pearson r on sensitive layers only.
    Returns: (r, p_value). If n_sensitive < 3: returns (np.nan, np.nan).
    """
```

**Pseudo-code:**
```
n_sensitive = sensitive_mask.sum()
if n_sensitive < 3:
    print(f"[WARNING] Only {n_sensitive} sensitive layers — skipping Pearson r")
    return (np.nan, np.nan)
from scipy.stats import pearsonr
r, p = pearsonr(sparsity[sensitive_mask], accuracy_drops[sensitive_mask])
return (r, p)
```

### L-A6-2: `evaluate_gate`

```python
def evaluate_gate(
    pearson_r_sst2: float,
    pearson_r_mnli: float,
    kendall_tau_sst2: float,
    kendall_tau_mnli: float,
    unique_var_sparsity: float,
    p_value_sparsity_beta: float,
    n_sensitive_sst2: int,
    cfg: "ExperimentConfig",
) -> Dict:
    """Evaluate all three gate conditions with R6 fallback.
    Returns: {
        "gate_pearson": bool,
        "gate_tau": bool,
        "gate_spectral": bool,
        "gate_pass": bool,
        "r6_fallback": bool,
        "all_metrics": dict,
    }
    """
```

**Pseudo-code:**
```
r6_fallback = (n_sensitive_sst2 < cfg.r6_min_sensitive_layers)  # < 5

if r6_fallback:
    gate_pearson = (pearson_r_mnli <= cfg.pearson_r_threshold)        # -0.4
    gate_tau = (kendall_tau_mnli >= cfg.kendall_tau_threshold)         # 0.4
else:
    gate_pearson = (pearson_r_sst2 <= cfg.pearson_r_threshold and
                    pearson_r_mnli <= cfg.pearson_r_threshold)
    gate_tau = (kendall_tau_sst2 >= cfg.kendall_tau_threshold and
                kendall_tau_mnli >= cfg.kendall_tau_threshold)

gate_spectral = (unique_var_sparsity >= cfg.unique_var_threshold and
                 p_value_sparsity_beta < cfg.p_value_threshold)

gate_pass = gate_pearson and gate_tau and gate_spectral

print(f"[GATE] MUST_WORK: {'PASS' if gate_pass else 'FAIL'}")
print(f"  gate_pearson={gate_pearson}, gate_tau={gate_tau}, gate_spectral={gate_spectral}")
print(f"  r6_fallback={r6_fallback}, n_sensitive_sst2={n_sensitive_sst2}")

return {
    "gate_pearson": gate_pearson,
    "gate_tau": gate_tau,
    "gate_spectral": gate_spectral,
    "gate_pass": gate_pass,
    "r6_fallback": r6_fallback,
    "all_metrics": {
        "pearson_r_sst2": pearson_r_sst2,
        "pearson_r_mnli": pearson_r_mnli,
        "kendall_tau_sst2": kendall_tau_sst2,
        "kendall_tau_mnli": kendall_tau_mnli,
        "unique_var_sparsity": unique_var_sparsity,
        "p_value_sparsity_beta": p_value_sparsity_beta,
        "n_sensitive_sst2": n_sensitive_sst2,
    }
}
```

---

## Subtask Summary [14/14 used]

| ID | Subtask | Module | Description |
|----|---------|--------|-------------|
| L-A3-1 | build_joint_rank_pattern | sensitivity_sweep.py | Budget-neutral rank_pattern, 224 entries |
| L-A3-2 | run_single_perturbation | sensitivity_sweep.py | Single (task, seed, layer, delta_r) run |
| L-A3-3 | run_sensitivity_sweep | sensitivity_sweep.py | 160 runs per task, returns (32,) mean drops |
| L-A3-4 | identify_sensitive_layers | sensitivity_sweep.py | Boolean mask (32,) with logging |
| L-A3-5 | check_delta_r_fallback | sensitivity_sweep.py | delta_r=4 if no sensitive layers |
| L-A5-1 | compute_spectral_decay_ratio | spectral_analysis.py | Covariance SVD, top-k / frobenius |
| L-A5-2 | compute_all_spectral_decays | spectral_analysis.py | gate_proj only, (32,) array |
| L-A5-3 | run_multiple_regression | spectral_analysis.py | OLS full+reduced, semipartial r² |
| L-A5-4 | compute_semipartial_r2 | spectral_analysis.py | Wrapper returning (unique_var, p_value) |
| L-A2-1 | train_uniform_lora | lora_trainer.py | Training loop + grad hooks + delta_w |
| L-A2-2 | compute_delta_w | lora_trainer.py | B@A per LoRA layer, CPU tensors |
| L-A2-3 | compute_grad_norms | lora_trainer.py | Frobenius norm from hook-captured grads |
| L-A4-1 | run_adalora | adalora_runner.py | AdaLoRA training + rank_pattern extraction |
| L-A4-2 | rank_pattern_to_array | adalora_runner.py | Dict -> (32,) via regex layer index |

---

## Key Tensor Shapes

| Variable | Shape | Location |
|----------|-------|----------|
| sparsity | (32,) | from h-m2 JSON |
| accuracy_drops | (32,) | sensitivity_sweep output |
| sensitive_mask | (32,) bool | identify_sensitive_layers |
| ΔW gate_proj | (4096, 14336) | LLaMA MLP gate/up |
| ΔW down_proj | (14336, 4096) | LLaMA MLP down |
| ΔW attention | (4096, 4096) | q/k/v/o proj |
| LoRA A | (r, d_in) | lora_A.default.weight |
| LoRA B | (d_out, r) | lora_B.default.weight |
| spectral_decay | (32,) | spectral_analysis output |
| grad_norms | (32,) | compute_grad_norms output |
| adalora_ranks | (32,) | rank_pattern_to_array output |
