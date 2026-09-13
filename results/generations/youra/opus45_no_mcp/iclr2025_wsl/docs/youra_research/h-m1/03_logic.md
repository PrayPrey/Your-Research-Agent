# Logic Design: H-M1 (Layer-wise Structure Advantage)

**Applied**: Encoder-Regressor pattern (StatNN flatten baseline vs Hyper-Representations layer-wise stats encoding), standard PyTorch train/eval loop

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Flatten+MLP Encoder [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch (flatten + 2-layer MLP)

### API Signatures

```python
def flatten_weights(weights_dict: dict[str, torch.Tensor]) -> torch.Tensor:
    """Flatten all layer tensors (sorted key order) into single 1D vector."""
    ...

class FlattenMLPEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, embed_dim: int = 128):
        ...
    def forward(self, weights_flat: torch.Tensor) -> torch.Tensor:
        """weights_flat: [B, input_dim] -> [B, embed_dim]"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weights_flat | [B, input_dim] | input_dim = total params, padded/truncated per batch (see A-2 collate) |
| embedding | [B, 128] | fc2 output |

### Pseudo-code

```
flatten_weights(weights_dict):
  1. parts = [weights_dict[k].flatten() for k in sorted(weights_dict.keys())]
  2. return torch.cat(parts, dim=0)  # [input_dim]

FlattenMLPEncoder.forward(x):
  1. h = relu(fc1(x))   # [B, hidden_dim]
  2. return fc2(h)      # [B, embed_dim]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | flatten_weights | sorted-key concat of flattened tensors |
| L-3-2 | FlattenMLPEncoder.__init__ | 2 linear layers |
| L-3-3 | FlattenMLPEncoder.forward | relu(fc1) -> fc2 |
| L-3-4 | input_dim resolution | compute max input_dim across dataset once, pad shorter vectors with zeros in collate_fn |

---

## A-4: Layer-wise Encoder [Complexity: 10, Budget: 10]

**Applied**: Hyper-Representations per-layer statistics pattern (mean/std/min/max, sorted-key aggregation)

### API Signatures

```python
def layer_wise_stats(
    weights_dict: dict[str, torch.Tensor],
    stats: list[str] = ["mean", "std", "min", "max"],
) -> torch.Tensor:
    """Per-layer stats (sorted keys) concatenated. Returns [num_layers * len(stats)]."""
    ...

class LayerWiseEncoder(nn.Module):
    def __init__(self, num_layers: int, stats_per_layer: int = 4,
                 hidden_dim: int = 256, embed_dim: int = 128):
        ...
    def compute_layer_stats(self, param: torch.Tensor) -> torch.Tensor:
        """param: [*] any shape -> [4] (mean,std,min,max)"""
        ...
    def forward(self, weights_dict: dict[str, torch.Tensor]) -> torch.Tensor:
        """weights_dict: layer_name -> tensor -> [embed_dim]"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| layer_stats (per layer) | [4] | mean, std, min, max |
| x (concatenated) | [num_layers * 4] | fixed num_layers across dataset (same architecture family) |
| embedding | [embed_dim] | per-sample; batched externally -> [B, embed_dim] |

### Pseudo-code

```
layer_wise_stats(weights_dict, stats):
  1. all_stats = []
  2. for name in sorted(weights_dict.keys()):
       flat = weights_dict[name].flatten().float()
       s = []
       if 'mean' in stats: s.append(flat.mean())
       if 'std'  in stats: s.append(flat.std())
       if 'min'  in stats: s.append(flat.min())
       if 'max'  in stats: s.append(flat.max())
       all_stats.extend(s)
  3. return torch.tensor(all_stats)  # [num_layers*4]

LayerWiseEncoder.forward(weights_dict):
  1. layer_stats = [compute_layer_stats(weights_dict[name])
                     for name in sorted(weights_dict.keys())]
  2. x = torch.cat(layer_stats, dim=-1)     # [num_layers*4]
  3. h = relu(fc1(x))                        # [hidden_dim]
  4. return fc2(h)                           # [embed_dim]
```

**Note**: `forward` operates per-sample (variable-shape weight dicts prevent stacking); batch loop wraps this in `FullModel` (A-5), stacking outputs via `torch.stack`.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | layer_wise_stats fn | standalone module-level function, sorted-key loop |
| L-4-2 | compute_layer_stats method | mean/std/min/max on flattened float tensor |
| L-4-3 | LayerWiseEncoder.__init__/forward | fc1/fc2, sorted-key concat, per-sample forward |
| L-4-4 | num_layers determination | fixed from first sample's weights_dict len(keys()); assert consistent across dataset |

---

## A-5: Regressor Head + FullModel Wrapper [Complexity: 5, Budget: 5]

### API Signatures

```python
class AccuracyPredictor(nn.Module):
    def __init__(self, embed_dim: int = 128, hidden_dim: int = 64):
        ...
    def forward(self, embedding: torch.Tensor) -> torch.Tensor:
        """embedding: [B, embed_dim] -> [B] (scalar accuracy pred)"""
        ...

class FullModel(nn.Module):
    """Wraps encoder + AccuracyPredictor; dispatches per-sample vs batched encoder."""
    def __init__(self, encoder: nn.Module, predictor: AccuracyPredictor, method: str):
        # method: "flatten" | "layerwise"
        ...
    def forward(self, weights_input) -> torch.Tensor:
        """
        flatten: weights_input [B, input_dim] tensor -> [B]
        layerwise: weights_input list[dict] (len B) -> [B]
        """
        ...
```

### Pseudo-code

```
FullModel.forward(weights_input):
  1. if method == "flatten":
       emb = encoder(weights_input)          # [B, embed_dim]
     else:  # layerwise
       emb = torch.stack([encoder(wd) for wd in weights_input])  # [B, embed_dim]
  2. return predictor(emb)                    # [B]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | AccuracyPredictor.__init__ | 2 linear layers (embed_dim->hidden->1) |
| L-5-2 | AccuracyPredictor.forward | relu(fc1) -> fc2 -> squeeze(-1) |
| L-5-3 | FullModel dispatch | method-conditional forward per above |
| L-5-4 | device placement | ensure per-sample loop tensors moved to device before encoder call |

---

## A-6: Training Loop [Complexity: 11, Budget: 11]

**Applied**: Standard PyTorch train/val loop, ReduceLROnPlateau, manual early stopping

### API Signatures

```python
def set_seed(seed: int) -> None: ...

def train_one_epoch(model: nn.Module, loader: DataLoader,
                     optimizer: torch.optim.Optimizer, device: str) -> float:
    """Returns mean train MSE loss for epoch."""
    ...

def validate(model: nn.Module, loader: DataLoader, device: str) -> float:
    """Returns mean val MSE loss (no_grad)."""
    ...

def train_model(
    model: nn.Module, train_loader: DataLoader, val_loader: DataLoader,
    lr: float = 1e-3, weight_decay: float = 1e-4, max_epochs: int = 50,
    early_stop_patience: int = 10, device: str = "cuda",
) -> tuple[nn.Module, dict]:
    """Returns (best_model_state_loaded, history={'train_loss':[...],'val_loss':[...]})"""
    ...

def save_checkpoint(model: nn.Module, path: str) -> None: ...
```

### Pseudo-code

```
train_model(model, train_loader, val_loader, ...):
  1. optimizer = AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
  2. scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
  3. best_val_loss = inf; patience_ctr = 0; best_state = None
  4. history = {'train_loss': [], 'val_loss': []}
  5. for epoch in range(max_epochs):
       train_loss = train_one_epoch(model, train_loader, optimizer, device)
       val_loss = validate(model, val_loader, device)
       scheduler.step(val_loss)
       history['train_loss'].append(train_loss); history['val_loss'].append(val_loss)
       if val_loss < best_val_loss:
         best_val_loss = val_loss; best_state = deepcopy(model.state_dict()); patience_ctr = 0
       else:
         patience_ctr += 1
         if patience_ctr >= early_stop_patience: break
  6. model.load_state_dict(best_state)
  7. return model, history

train_one_epoch(model, loader, optimizer, device):
  1. model.train(); total_loss = 0
  2. for weights_input, targets in loader:
       targets = targets.to(device).float()          # [B]
       preds = model(weights_input)                    # [B]
       loss = F.mse_loss(preds, targets)
       optimizer.zero_grad(); loss.backward(); optimizer.step()
       total_loss += loss.item() * len(targets)
  3. return total_loss / len(loader.dataset)

validate: same as train_one_epoch but model.eval(), torch.no_grad(), no backward
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| targets | [B] | ground-truth accuracy, float |
| preds | [B] | model output |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | set_seed | torch/np/random seed + cudnn deterministic flags |
| L-6-2 | train_one_epoch/validate | MSE loss loop over DataLoader |
| L-6-3 | train_model orchestration | AdamW + scheduler + early stopping + best-state restore |
| L-6-4 | save_checkpoint | torch.save(model.state_dict(), path) |

---

## A-7: Evaluation Metrics [Complexity: 6, Budget: 6]

**Applied**: scipy.stats.pearsonr / ttest_rel

### API Signatures

```python
def predict(model: nn.Module, loader: DataLoader, device: str) -> tuple[np.ndarray, np.ndarray]:
    """Returns (preds [N], targets [N])"""
    ...

def compute_pearson(preds: np.ndarray, targets: np.ndarray) -> dict:
    """Returns {'pearson_r': float, 'p_value': float}"""
    ...

def compare_methods(flatten_results: list[float], layerwise_results: list[float]) -> dict:
    """Paired t-test across seeds. Returns {'delta_r','t_stat','p_value'}"""
    ...
```

### Pseudo-code

```
predict(model, loader, device):
  1. model.eval(); all_preds=[]; all_targets=[]
  2. with torch.no_grad():
       for weights_input, targets in loader:
         preds = model(weights_input)
         all_preds.append(preds.cpu().numpy()); all_targets.append(targets.numpy())
  3. return np.concatenate(all_preds), np.concatenate(all_targets)

compute_pearson(preds, targets):
  1. r, p = scipy.stats.pearsonr(preds, targets)
  2. return {'pearson_r': r, 'p_value': p}

compare_methods(flatten_results, layerwise_results):
  1. t_stat, p_val = scipy.stats.ttest_rel(layerwise_results, flatten_results)
  2. delta_r = np.mean(layerwise_results) - np.mean(flatten_results)
  3. return {'delta_r': delta_r, 't_stat': t_stat, 'p_value': p_val}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | predict | eval-mode inference loop, numpy concat |
| L-7-2 | compute_pearson | scipy.stats.pearsonr wrapper |
| L-7-3 | compare_methods | scipy.stats.ttest_rel + delta_r |
| L-7-4 | 5/5 seed-improve check | `all(l > f for l,f in zip(layerwise_results, flatten_results))` in run_experiment.py gate logic |

---

## A-9: Multi-seed Orchestration (relevant logic only) [Complexity: 12, Budget: 12]

### API Signatures

```python
def run_seed(method: str, seed: int, train_loader: DataLoader, val_loader: DataLoader,
             test_loader: DataLoader, cfg: "Config") -> dict:
    """method: 'flatten'|'layerwise'. Returns {'pearson_r': float, 'history': dict}"""
    ...
```

### Pseudo-code

```
run_seed(method, seed, train_loader, val_loader, test_loader, cfg):
  1. set_seed(seed)
  2. if method == 'flatten':
       encoder = FlattenMLPEncoder(input_dim, cfg.hidden_dim, cfg.embed_dim)
     else:
       encoder = LayerWiseEncoder(num_layers, 4, cfg.hidden_dim, cfg.embed_dim)
  3. predictor = AccuracyPredictor(cfg.embed_dim, cfg.predictor_hidden)
  4. model = FullModel(encoder, predictor, method).to(cfg.device)
  5. model, history = train_model(model, train_loader, val_loader,
                                    cfg.lr, cfg.weight_decay, cfg.max_epochs,
                                    cfg.early_stop_patience, cfg.device)
  6. preds, targets = predict(model, test_loader, cfg.device)
  7. metrics = compute_pearson(preds, targets)
  8. return {'pearson_r': metrics['pearson_r'], 'history': history}

main():
  1. for method in ['flatten', 'layerwise']:
       for seed in cfg.seeds:
         result = run_seed(method, seed, ...); collect r-value
  2. gate = compare_methods(flatten_rs, layerwise_rs)
  3. PASS if gate['delta_r'] > 0.1 and gate['p_value'] < 0.05
  4. generate figures, write results.json
```

### Subtasks (owned by A-9, logic-relevant only) [3/12 used here — remaining in architecture]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | run_seed | seed-set, model build, train, test predict, pearson r |
| L-9-2 | main aggregation | loop 2 methods x 5 seeds, collect r lists |
| L-9-3 | gate decision | compare_methods + threshold check per PRD FR-5.4/Success Criteria |
