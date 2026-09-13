# Logic: H-M2 (Update-Norm Parity Intervention)

**Applied**: Standard PyTorch grad-hook/manual-scaling pattern (KB: no group-robustness-specific match found; using textbook per-parameter-group gradient scaling before `optimizer.step()`)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual H-E1 code (not spec)
**Analyzed Path**: `docs/youra_research/h-e1/code/{config,data,sharpness,model}.py`
**Relevant Symbols**:
- `Config` (dataclass) / `CONFIG` (module singleton) — `h-e1/code/config.py`
- `WaterbirdDataset.__init__(root, split="train")`, `get_group_loader(dataset, group_id, batch_size=32)` — `h-e1/code/data.py`
- `compute_sharpness_ratio(model, dataset)`, `compute_group_sharpness(model, loader, num_iterations)` — `h-e1/code/sharpness.py`
- `create_random_model(seed)` — `h-e1/code/model.py` (reference only; H-M2 needs pretrained variant)

**Critical finding**: `compute_sharpness_ratio` reads `CONFIG.minority_groups`, `CONFIG.majority_groups`, `CONFIG.batch_size`, `CONFIG.num_power_iter` as a **global module import** (`from config import CONFIG`), not as function params. H-M2's `config.py` MUST define a module-level `CONFIG = Config(...)` singleton with these exact field names for `sharpness.py` to work unmodified. Also `compute_loss` in `sharpness.py` casts inputs `.double()` and expects model in double precision — H-M2's pretrained model must also `.double()`.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/data.py (ACTUAL CODE, reuse unmodified)
class WaterbirdDataset(Dataset):
    def __init__(self, root: str, split: str = "train"): ...
    def __getitem__(self, idx: int) -> tuple:  # (img[3,224,224], label:int, group:int)
        ...

def get_group_loader(dataset: WaterbirdDataset, group_id: int, batch_size: int = 32) -> DataLoader: ...

# From: h-e1/code/sharpness.py (ACTUAL CODE, reuse unmodified)
def compute_sharpness_ratio(model: nn.Module, dataset: WaterbirdDataset) -> float:
    # reads CONFIG.minority_groups/majority_groups/batch_size/num_power_iter globally
    ...

# From: h-e1/code/config.py (pattern to follow, not import — H-M2 defines its own CONFIG)
@dataclass
class Config:
    data_root: str; img_size: int; batch_size: int
    imagenet_mean: tuple; imagenet_std: tuple
    minority_groups: tuple; majority_groups: tuple
    num_classes: int; num_power_iter: int; seeds: tuple
CONFIG = Config()  # module singleton
```

**Verified from**: `h-e1/code/data.py`, `h-e1/code/sharpness.py`, `h-e1/code/config.py` (actual implementation).

---

## A-1: Data Pipeline [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch `Dataset`/`DataLoader` reuse pattern

### API Signatures

```python
# data.py — WaterbirdDataset, get_group_loader copied verbatim from h-e1/code/data.py
# imagenet_mean/std/img_size/batch_size read from h-m2 CONFIG (module singleton, same field names)

def get_train_loader(dataset: WaterbirdDataset, batch_size: int) -> DataLoader:
    """Full train split loader, shuffled, for ERM/parity forward-backward."""
    ...

def get_group_batch(dataset: WaterbirdDataset, group_id: int, batch_size: int) -> tuple:
    """Sample one batch from group_id for per-group grad norm computation.
    Returns (x[B,3,H,W], y[B], group[B])"""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Copy WaterbirdDataset | Verbatim from h-e1/code/data.py |
| L-1-2 | Copy get_group_loader | Verbatim from h-e1/code/data.py |
| L-1-3 | Implement get_train_loader | shuffle=True, num_workers configurable |
| L-1-4 | Implement get_group_batch | For A-3/A-5 per-group gradient computation |

---

## A-2: Pretrained Model Builder [Complexity: 4, Budget: 4]

**Applied**: torchvision pretrained-weights loading pattern

### API Signatures

```python
def create_pretrained_model(seed: int) -> nn.Module:
    """ResNet-50 ImageNet-pretrained, fc replaced Linear(2048,2), cast .double()."""
    ...
```

### Pseudo-code

```
1. torch.manual_seed(seed)
2. model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
3. model.fc = nn.Linear(2048, CONFIG.num_classes)  # re-init seeded
4. return model.double()  # match h-e1 sharpness.py double-precision convention
```

### Subtasks [1/1 used — merged into single subtask, complexity 4 covers whole function]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | create_pretrained_model | Load pretrained ResNet-50, replace fc, seed fc init, cast double |

---

## A-3: Parity Intervention Module [Complexity: 14, Budget: 14]

**Applied**: Manual per-parameter-group gradient norm scaling (no autograd hook needed — direct `.grad` manipulation between `backward()` and `step()`)

### API Signatures

```python
class UpdateNormParityTrainer:
    def __init__(self, model: nn.Module, num_groups: int = 4, scale: float = 1.0):
        """scale=1.0 Full Parity, scale=0.5 Partial Parity, scale=0.0 => no-op (baseline)."""
        ...

    def compute_group_grad_norms(
        self, dataset: WaterbirdDataset, group_ids: tuple, batch_size: int, criterion: nn.Module
    ) -> dict:
        """Per group: zero_grad -> forward -> backward -> flat grad L2 norm. Restores grads to zero after.
        Returns {group_id: norm_float}"""
        ...

    def apply_parity_scaling(
        self, model: nn.Module, group_norms: dict, target_group: int
    ) -> dict:
        """Rescale model.grad (already populated from target_group's backward) so its
        norm moves toward mean(group_norms) by self.scale fraction.
        Returns {"group": target_group, "orig_norm": float, "scaled_norm": float, "target_norm": float}"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| flat_grad | [P] | P = total model params, concatenated `.grad.reshape(-1)` |
| group_norms values | scalar float | L2 norm per group |

### Pseudo-code

```
compute_group_grad_norms(dataset, group_ids, batch_size, criterion):
  norms = {}
  for g in group_ids:
      x, y, _ = get_group_batch(dataset, g, batch_size)   # [B,3,H,W], [B]
      model.zero_grad()
      loss = criterion(model(x), y)
      loss.backward()
      flat = cat([p.grad.reshape(-1) for p in model.parameters() if p.grad is not None])
      norms[g] = flat.norm().item()
  model.zero_grad()
  return norms

apply_parity_scaling(model, group_norms, target_group):
  mean_norm = mean(group_norms.values())
  orig = group_norms[target_group]
  target_norm = orig + scale * (mean_norm - orig)   # interpolate toward mean by `scale`
  factor = target_norm / (orig + 1e-12)
  for p in model.parameters():
      if p.grad is not None: p.grad.mul_(factor)
  return {"group": target_group, "orig_norm": orig, "scaled_norm": target_norm, "target_norm": mean_norm}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | UpdateNormParityTrainer.__init__ | Store model ref, num_groups, scale |
| L-3-2 | compute_group_grad_norms | Per-group backward pass, flat L2 norm, zero grads after |
| L-3-3 | apply_parity_scaling | Interpolate target group's grad toward mean norm by `scale` |
| L-3-4 | Integration hook contract | Document call order: backward(target group) -> apply_parity_scaling -> step() |

---

## A-4: Training Loop (ERM Baseline) [Complexity: 10, Budget: 10]

**Applied**: Standard SGD training loop with early stopping

### API Signatures

```python
def train_one_variant(variant: str, seed: int, cfg: Config) -> dict:
    # variant in {"baseline","full_parity","partial_parity"}
    # returns {"sr_by_epoch": list[tuple[int,float]], "wga": float,
    #          "per_group_acc": dict[int,float], "update_norms": list[dict]}
    ...

def evaluate(model: nn.Module, loader: DataLoader) -> tuple:
    """Returns (y_true: list[int], y_pred: list[int], groups: list[int])"""
    ...
```

### Pseudo-code (ERM path, variant="baseline")

```
model = create_pretrained_model(seed)
opt = SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay)
criterion = CrossEntropyLoss()
best_wga, patience_ctr = -inf, 0
for epoch in range(cfg.epochs):
    for x, y, g in train_loader:
        opt.zero_grad(); loss = criterion(model(x.double()), y); loss.backward(); opt.step()
    y_t, y_p, grp = evaluate(model, val_loader)
    wga = worst_group_accuracy(y_t, y_p, grp)
    if epoch == cfg.sr_eval_epoch: sr = compute_sharpness_ratio(model, train_dataset)
    if wga > best_wga: best_wga, patience_ctr = wga, 0
    else: patience_ctr += 1
    if patience_ctr >= cfg.early_stop_patience: break
return {...}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | train_one_variant skeleton | Model/opt/criterion setup, epoch loop, baseline path |
| L-4-2 | Early stopping on WGA | Patience counter, best checkpoint tracking |
| L-4-3 | evaluate() | Full-batch forward, collect (y_true, y_pred, groups) |

---

## A-5: Training Loop Integration (Parity Variants) [Complexity: 12, Budget: 12]

**Applied**: Trainer-hook composition into existing loop

### API Signatures

```python
def train_step_parity(
    model: nn.Module, trainer: UpdateNormParityTrainer, x: Tensor, y: Tensor, g: Tensor,
    dataset: WaterbirdDataset, cfg: Config, opt: torch.optim.Optimizer, criterion: nn.Module
) -> dict:
    """One optimizer step with parity intervention. Returns update_norm log dict."""
    ...
```

### Pseudo-code

```
train_step_parity(...):
  group_norms = trainer.compute_group_grad_norms(dataset, cfg.minority_groups + cfg.majority_groups, cfg.batch_size, criterion)
  opt.zero_grad()
  loss = criterion(model(x.double()), y); loss.backward()
  target_group = mode(g.tolist())  # dominant group in this batch
  log = trainer.apply_parity_scaling(model, group_norms, target_group)
  opt.step()
  return log
```

`train_one_variant` branches: `if variant != "baseline": trainer = UpdateNormParityTrainer(model, scale={"full_parity":1.0,"partial_parity":cfg.partial_scale}[variant]); use train_step_parity per batch else use plain step.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | train_step_parity | Single-step parity-scaled update |
| L-5-2 | Variant branching in train_one_variant | Select trainer/scale by variant string |
| L-5-3 | update_norms logging | Append per-step log dicts to results["update_norms"] |

---

## A-6: SR + Metrics Wiring [Complexity: 9, Budget: 9]

**Applied**: Direct reuse of h-e1 sharpness.py; sklearn-based group accuracy

### API Signatures

```python
# sharpness.py copied unmodified from h-e1/code/sharpness.py
# H-M2's config.py CONFIG must expose minority_groups/majority_groups/batch_size/num_power_iter

def per_group_accuracy(y_true: list, y_pred: list, groups: list) -> dict:
    """Returns {group_id: accuracy_float} for each of 4 groups."""
    ...

def worst_group_accuracy(y_true: list, y_pred: list, groups: list) -> float:
    """min(per_group_accuracy(...).values())"""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Copy sharpness.py + wire CONFIG | Verbatim copy, verify CONFIG field compat |
| L-6-2 | per_group_accuracy / worst_group_accuracy | sklearn accuracy_score per group mask |

---

## A-7: Ablation Orchestration [Complexity: 10, Budget: 10]

**Applied**: Nested loop grid-search pattern with per-run result persistence

### API Signatures

```python
def run_ablation(cfg: Config) -> dict:
    """loop variants x seeds -> train_one_variant -> save results/{variant}_seed{seed}.json
    Returns {variant: [result_dict per seed]}"""
    ...
```

### Pseudo-code

```
all_results = {v: [] for v in cfg.variants}
for variant in cfg.variants:
    for seed in cfg.seeds:
        r = train_one_variant(variant, seed, cfg)
        save_json(f"results/{variant}_seed{seed}.json", r)
        all_results[variant].append(r)
return all_results
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | run_ablation loop | 3 variants x 5 seeds |
| L-7-2 | Per-run JSON persistence | save_json helper, path convention |
| L-7-3 | Result collection dict | Aggregate into {variant: [runs]} for stats |

---

## A-8: Statistical Validation [Complexity: 7, Budget: 7]

**Applied**: scipy.stats independent t-test for group comparison

### API Signatures

```python
def aggregate_across_seeds(results: list[dict]) -> dict:
    """Returns {"sr_mean": float, "sr_std": float, "wga_mean": float, "wga_std": float}"""
    ...

def sr_significance_test(baseline_srs: list[float], parity_srs: list[float]) -> dict:
    """Welch's t-test. Returns {"t_stat": float, "p_value": float, "significant": bool}"""
    ...
```

### Pseudo-code

```
sr_significance_test(baseline_srs, parity_srs):
  t, p = scipy.stats.ttest_ind(baseline_srs, parity_srs, equal_var=False)
  return {"t_stat": t, "p_value": p, "significant": p < 0.05}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | aggregate_across_seeds | numpy mean/std over SR, WGA lists |
| L-8-2 | sr_significance_test | scipy Welch's t-test wrapper |

---

## A-9: Visualization Suite [Complexity: 8, Budget: 8]

**Applied**: Standard matplotlib line/box/bar plot patterns

### API Signatures

```python
def plot_sr_trajectory(results_by_variant: dict, out_path: str) -> None: ...
def plot_group_accuracy_trajectories(results_by_variant: dict, out_path: str) -> None: ...
def plot_update_norm_boxplot(results_by_variant: dict, out_path: str) -> None: ...
def plot_wga_comparison(results_by_variant: dict, out_path: str) -> None: ...
```

### Subtasks [2/2 used, 2 merged pairs]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | plot_sr_trajectory + plot_group_accuracy_trajectories | Line plots over epoch, one line per variant |
| L-9-2 | plot_update_norm_boxplot + plot_wga_comparison | Boxplot per variant, bar chart final WGA |

---

## A-10: End-to-End Orchestration + Success Criteria Check [Complexity: 8, Budget: 8]

**Applied**: Standard main.py orchestrator + gate-check pattern

### API Signatures

```python
def check_success_criteria(agg: dict) -> dict:
    """agg keyed by variant. Returns {"sr_pass": bool, "wga_pass": bool, "p_pass": bool, "overall_pass": bool}"""
    ...

def main() -> None:
    # run_ablation -> aggregate_across_seeds per variant -> sr_significance_test
    # -> check_success_criteria -> 4 figures -> save results/summary.json
    ...
```

### Pseudo-code

```
check_success_criteria(agg):
  sr_pass = agg["full_parity"]["sr_mean"] <= 1.1 and agg["baseline"]["sr_mean"] > 1.2
  wga_pass = agg["full_parity"]["wga_mean"] >= agg["baseline"]["wga_mean"]
  p_pass = sr_significance_test(baseline_srs, parity_srs)["significant"]
  return {"sr_pass":sr_pass, "wga_pass":wga_pass, "p_pass":p_pass, "overall_pass": all([sr_pass,wga_pass,p_pass])}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-10-1 | check_success_criteria | Gate check against PRD thresholds |
| L-10-2 | main() orchestrator | Wire all modules, save summary.json |

---

**Total subtasks**: 26 (within per-task budgets; epic-level task count matches architecture's 4-subtask breakdown targets where budget allowed, merged where complexity was low)
