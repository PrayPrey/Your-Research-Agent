# Logic: H-M2
## Group-Balanced Gradient Propagates Through All Backbone Layers — Proxy Verification

**Generated:** 2026-08-05
**Applied:** sequential-checkpoint-load pattern (standard PyTorch)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from h-m1 actual code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**:
- `load_group_distribution()` — WILDS loading via `get_dataset(download=False, root_dir=config.WILDS_CACHE)`
- `_eval_checkpoint_worker()` — checkpoint loading pattern: `ckpt['model_state_dict']`, `model.fc = Linear(2048, 2)`
- `save_results(gate_checks)` — `json.dump(gate_checks, f, indent=2)`
- `generate_validation_report(gate_checks, group_counts)` — writes markdown to `config.VALIDATION_REPORT`
- `save_figures(group_counts, gate_checks)` — `Path(config.FIGURES_DIR).mkdir(parents=True, exist_ok=True)`
- `config.py` — `BASE_DIR`, `FIGURES_DIR`, `RESULTS_JSON`, `VALIDATION_REPORT`, `WILDS_CACHE`, `WILDS_DATASET`, `CHECKPOINT_ARCHIVE`

**Critical finding**: h-m1 checkpoints use key `model_state_dict` (not `model` or `state_dict`). PRD spec's `load_resnet50` uses `'model'`/`'state_dict'` keys — VERIFY against actual files at runtime with strict=False fallback.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual h-m1 Code)

```python
# From: docs/youra_research/h-m1/code/run_experiment.py (ACTUAL CODE)

# WILDS loading pattern
from wilds import get_dataset
dataset = get_dataset(dataset='waterbirds', download=False, root_dir='/home/PrayPrey/.wilds_cache')
train_data = dataset.get_subset('train', transform=transform)
test_data  = dataset.get_subset('test',  transform=transform)
# metadata: train_data.metadata_array.numpy()[:, 0] → group_array (0-3)
# background_label = group_array % 2

# Checkpoint structure (from _eval_checkpoint_worker — ACTUAL):
ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)
ckpt['model_state_dict']   # actual key in h-e1 checkpoints
ckpt.get('method', '')     # stored method label, e.g. 'groupdro'

# Model construction (ACTUAL):
model = tv_models.resnet50(weights=None)
model.fc = torch.nn.Linear(2048, 2)   # 2-class output, not default 1000
model.load_state_dict(ckpt['model_state_dict'])

# Config constants (from h-m1/code/config.py ACTUAL):
# WILDS_CACHE, WILDS_DATASET, CHECKPOINT_ARCHIVE — replicated in h-m2/code/config.py
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# FIGURES_DIR, RESULTS_JSON, VALIDATION_REPORT derived from BASE_DIR
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

---

## A-4: Weight Difference Analysis [Complexity: 9, Budget: 2 subtasks]

**Applied**: Standard PyTorch parameter iteration

### API Signatures

```python
def verify_gradient_propagation(erm_ckpt: str, gdro_ckpt: str, seed: int) -> dict:
    """Per-block L2 weight diff (GroupDRO - ERM) for layer4[0,1,2] + head."""
    # Returns keys: layer4_block{0,1,2}_diff, head_weight_diff,
    #               backbone_to_head_ratio, gradient_reached_layer4
    ...

def compare_all_methods(checkpoint_dir: str, methods: list[str], seeds: list[int]) -> dict:
    """Weight diff analysis for all method pairs vs ERM, all seeds."""
    # Returns: {method: {seed: {block0_diff, block1_diff, block2_diff,
    #                           head_weight_diff, backbone_to_head_ratio,
    #                           gradient_reached_layer4}}}
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| layer4[b].conv1.weight | (256, 1024, 1, 1) or (512, 256, 1, 1) | varies by block position |
| layer4[b].conv2.weight | (64, 256, 3, 3) block 0 | per block structure |
| diff tensor | scalar | `torch.norm(gdro_p - erm_p)` |

### Pseudo-code

```
verify_gradient_propagation(erm_ckpt, gdro_ckpt, seed):
  erm = load_resnet50(erm_ckpt)   # model.fc = Linear(2048, 2)
  gdro = load_resnet50(gdro_ckpt)
  block_diffs = []
  for b in [0, 1, 2]:
    param_diffs = [norm(gp - ep) for gp, ep in zip(gdro.layer4[b].parameters(),
                                                     erm.layer4[b].parameters())]
    block_diffs.append(mean(param_diffs))
  head_diff = norm(gdro.fc.weight - erm.fc.weight)
  ratio = mean(block_diffs) / max(head_diff, 1e-10)
  return {layer4_block{b}_diff: block_diffs[b],
          head_weight_diff: head_diff,
          backbone_to_head_ratio: ratio,
          gradient_reached_layer4: any(d > 1e-6 for d in block_diffs)}

compare_all_methods(checkpoint_dir, methods, seeds):
  results = {}
  for method in methods:
    results[method] = {}
    for seed in seeds:
      erm_ckpt = f"{checkpoint_dir}/erm_seed{seed}.pt"
      m_ckpt   = f"{checkpoint_dir}/{method}_seed{seed}.pt"
      results[method][seed] = verify_gradient_propagation(erm_ckpt, m_ckpt, seed)
  return results
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L4.1 | verify_gradient_propagation | Per-seed ERM vs method weight diff at layer4[0,1,2] + head |
| L4.2 | compare_all_methods | Loop over all methods × seeds, aggregate results dict |

---

## A-5: Gradient Norm Analysis [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard PyTorch backward pass, zero_grad pattern

### API Signatures

```python
def compute_layer4_gradient_norm(
    model: torch.nn.Module,
    dataloader: DataLoader,
    loss_type: str,        # 'erm' | 'groupdro'
    device: str = 'cpu',
    n_batches: int = 50
) -> tuple[float, float]:
    """Mean and std of layer4 grad norms over n_batches.
    model must be in train() mode. No optimizer step performed."""
    # Returns: (mean_float, std_float)
    # Input batch: (x [B,3,224,224], y [B], metadata [B, M])
    # layer4 grad norm per batch: mean([p.grad.norm() for p in model.layer4.parameters()])
    ...

def run_gradient_analysis(
    checkpoint_dir: str,
    train_loader: DataLoader,
    device: str
) -> dict:
    """Load ERM + GroupDRO seed-1 checkpoints, compute gradient norms for both loss types."""
    # Returns: {'erm': (mean, std), 'groupdro': (mean, std)}
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | (B, 3, 224, 224) | Input batch, B=32 |
| logits | (B, 2) | 2-class output |
| p.grad | same as p | layer4 parameter gradient |
| group mask | (B,) | metadata[:, 0] == g |

### Pseudo-code

```
compute_layer4_gradient_norm(model, dataloader, loss_type, device, n_batches):
  model.train()
  batch_norms = []
  for i, (x, y, metadata) in enumerate(dataloader):
    if i >= n_batches: break
    x, y = x.to(device), y.to(device)
    logits = model(x)
    if loss_type == 'erm':
      loss = F.cross_entropy(logits, y)
    else:  # groupdro
      group = metadata[:, 0].to(device)
      g_losses = [cross_entropy(logits[group==g], y[group==g]) for g in 0..3 if any(group==g)]
      loss = stack(g_losses).max()
    model.zero_grad()
    loss.backward()
    norms = [p.grad.norm().item() for p in model.layer4.parameters() if p.grad is not None]
    if norms: batch_norms.append(mean(norms))
  return mean(batch_norms), std(batch_norms)

run_gradient_analysis(checkpoint_dir, train_loader, device):
  # Use seed-1 checkpoints as representative
  erm_model  = load_resnet50(f"{checkpoint_dir}/erm_seed1.pt", device)
  gdro_model = load_resnet50(f"{checkpoint_dir}/groupdro_seed1.pt", device)
  erm_stats  = compute_layer4_gradient_norm(erm_model,  train_loader, 'erm',      device)
  gdro_stats = compute_layer4_gradient_norm(gdro_model, train_loader, 'groupdro', device)
  return {'erm': erm_stats, 'groupdro': gdro_stats}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L5.1 | compute_layer4_gradient_norm | Single model + loss_type → (mean, std) over 50 batches |
| L5.2 | run_gradient_analysis | Load seed-1 ERM+GroupDRO, call L5.1 for both, return dict |

---

## A-6: Feature Extraction + Linear Probe [Complexity: 11, Budget: 2 subtasks]

**Applied**: H-P0 proven extraction protocol (layer4 → adaptive_avg_pool2d → flatten)

### API Signatures

```python
def extract_layer4_features(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: str
) -> tuple[np.ndarray, np.ndarray]:
    """Extract layer4 features for all samples in dataloader.
    Returns: (features [N, 2048], background_labels [N])
    background_label = group_array % 2 (0=land, 1=water)
    model must be in eval() mode. Uses torch.no_grad()."""
    # x [B,3,224,224] -> layer4 [B,2048,7,7] -> pool [B,2048,1,1] -> flatten [B,2048]
    ...

def run_linear_probe_all_checkpoints(
    checkpoint_dir: str,
    train_loader: DataLoader,
    test_loader: DataLoader,
    device: str = 'cpu'
) -> dict:
    """Run linear probe for all 12 checkpoints sequentially.
    Returns: {ckpt_name: accuracy_float}
    e.g. {'erm_seed1': 0.923, 'groupdro_seed1': 0.871, ...}
    Fits on train features, evaluates on full test set (5794 samples)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x (input) | (B, 3, 224, 224) | ImageNet-normalized |
| after layer4 | (B, 2048, 7, 7) | ResNet-50 layer4 output |
| after adaptive_avg_pool2d(1,1) | (B, 2048, 1, 1) | spatial collapse |
| after flatten | (B, 2048) | feature vector |
| features [N] | (N, 2048) | full split, N=4795 train / 5794 test |
| background_labels [N] | (N,) | int64, 0 or 1 |

### Pseudo-code

```
extract_layer4_features(model, dataloader, device):
  model.eval()
  all_feats, all_labels = [], []
  with torch.no_grad():
    for x, y, metadata in dataloader:
      x = x.to(device)
      # H-P0 proven protocol:
      h = model.conv1(x); h = model.bn1(h); h = model.relu(h); h = model.maxpool(h)
      h = model.layer1(h); h = model.layer2(h); h = model.layer3(h)
      h = model.layer4(h)                         # [B, 2048, 7, 7]
      h = F.adaptive_avg_pool2d(h, (1, 1))         # [B, 2048, 1, 1]
      h = h.flatten(1)                             # [B, 2048]
      group = metadata[:, 0].numpy()
      bg_label = group % 2                         # background_label
      all_feats.append(h.cpu().numpy())
      all_labels.append(bg_label)
  return np.concatenate(all_feats), np.concatenate(all_labels)

run_linear_probe_all_checkpoints(checkpoint_dir, train_loader, test_loader, device):
  methods = ['erm', 'groupdro', 'sam', 'dfr']
  seeds   = [1, 2, 3]
  results = {}
  # Extract train features once per checkpoint (sequential, del model between)
  for method in methods:
    for seed in seeds:
      ckpt_name = f"{method}_seed{seed}"
      model = load_resnet50(f"{checkpoint_dir}/{ckpt_name}.pt", device)
      train_feats, train_labels = extract_layer4_features(model, train_loader, device)
      test_feats,  test_labels  = extract_layer4_features(model, test_loader,  device)
      del model; gc.collect()  # OOM-safe: <4GB
      acc = linear_probe(train_feats, train_labels, test_feats, test_labels)
      results[ckpt_name] = acc
  return results

linear_probe(train_feats, train_labels, test_feats, test_labels):
  # sklearn LogisticRegression — exact params from PRD
  clf = LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42)
  clf.fit(train_feats, train_labels)       # train_feats [N_train, 2048]
  return clf.score(test_feats, test_labels) # test_feats [5794, 2048]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L6.1 | extract_layer4_features | H-P0 protocol → (features [N,2048], bg_labels [N]) |
| L6.2 | run_linear_probe_all_checkpoints | Sequential load × 12 ckpts, extract train+test, probe, gc |

---

## Implementation Notes for Coder (Phase 4)

- `load_resnet50` must set `model.fc = torch.nn.Linear(2048, 2)` before `load_state_dict` (h-m1 actual code uses 2-class head, not torchvision default 1000)
- Checkpoint key is `model_state_dict` (verified from h-m1 actual code) — try `['model_state_dict']` first, then fall back to `['model']`, `['state_dict']`, else use raw dict
- `model.train()` only in `compute_layer4_gradient_norm`; `model.eval()` + `torch.no_grad()` everywhere else
- `del model; gc.collect()` between each checkpoint in A-6 to stay under 4 GB
- Train DataLoader: `shuffle=False, batch_size=32` for reproducible gradient analysis
- Test DataLoader: `shuffle=False, batch_size=128` for full 5794 samples
- `group_array = metadata[:, 0].numpy().astype(int)` (h-m1 actual pattern)
- `background_label = group_array % 2` (probe target)
- `matplotlib.use('Agg')` before pyplot import (h-m1 pattern, headless server)
