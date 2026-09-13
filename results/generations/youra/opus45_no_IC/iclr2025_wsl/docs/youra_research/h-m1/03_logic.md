# Logic: H-M1 (MECHANISM)

**Hypothesis:** NFN equivariant layers produce permutation-invariant outputs (correlation > 0.99)

Applied: PyTorch eval-mode inference pattern (no NFN-specific KB entries; Archon KB search "permutation invariance test PyTorch" returned only low-similarity general PyTorch/diffusers results — not used)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: API signatures verified from actual H-E1 code (differ from 03_prd.md/experiment brief assumptions)
**Analyzed Path**: `docs/youra_research/h-e1/code/{model.py, data.py, zoo_generator.py, config.py}`
**Relevant Symbols**: `NFNRegressor` (model.py:5-23), `get_network_spec_from_sample` (data.py:110-120), `make_collate_fn` (data.py:93-107), `SimpleCNN`/`convert_state_dict_to_nfn_format` (zoo_generator.py)

**Critical finding**: `zoo_generator.py::convert_state_dict_to_nfn_format` renames `SimpleCNN`'s `nn.Sequential` state_dict keys from `net.0.weight/net.0.bias, net.2.*, net.4.*` to `layer0.weight/layer0.bias, layer1.*, layer2.*` before saving to the zoo / training the checkpoint. **The H-E1 checkpoint was trained on `layer{i}.weight/bias` keys, NOT `net.{2i}.*` keys.** H-M1's `test_data.py` and `permute.py` MUST generate/permute state_dicts using `layer0/layer1/layer2` keys to match `network_spec` derived from the checkpoint's training data, or `state_dict_to_tensors` will fail / produce shape-incompatible wsfeat.

## External Dependencies API

```python
# From: h-e1/code/model.py (ACTUAL CODE)
class NFNRegressor(nn.Module):
    def __init__(self, network_spec: Any, nfn_channels: int = 32): ...
    def forward(self, wsfeat: Any) -> torch.Tensor: ...  # wsfeat -> [B, 1]

# From: h-e1/code/data.py (ACTUAL CODE)
def get_network_spec_from_sample(models: List[Dict]) -> Any:
    # models[0]['state_dict'] must use layer{i}.weight/bias keys
    # returns nfn.common.NetworkSpec via state_dict_to_tensors + network_spec_from_wsfeat

def make_collate_fn(network_spec: Any) -> Callable:
    # returns collate_fn(batch: List[Tuple[Dict, float]]) -> Tuple[WeightSpaceFeatures, Tensor]
    # internally: state_dict_to_tensors(sd) per sample -> default_collate -> WeightSpaceFeatures(*wts_and_bs)

# From: h-e1/code/zoo_generator.py (ACTUAL CODE)
class SimpleCNN(nn.Module):
    def __init__(self, input_dim: int = 3072, hidden_dims: Tuple[int, ...] = (64, 64)): ...
    # self.net = Sequential(Linear(3072,64), ReLU, Linear(64,64), ReLU, Linear(64,10))

def convert_state_dict_to_nfn_format(state_dict: Dict) -> Dict:
    # net.0.weight/bias -> layer0.weight/bias
    # net.2.weight/bias -> layer1.weight/bias
    # net.4.weight/bias -> layer2.weight/bias

# From: h-e1/code/config.py (ACTUAL CODE)
Config.nfn_channels = 32
Config().checkpoint_dir  # h-e1/checkpoints/
```

**Verified from**: `h-e1/code/` (actual implementation, not 03_architecture.md/PRD/brief).

**Correction vs architecture doc**: `03_architecture.md` correctly flagged `input_dim=3072` but did NOT flag the `layer{i}` key renaming — this logic spec adds that correction.

---

## M-1: Test MLP Generator [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch weight init (matches H-E1 checkpoint's `layer{i}` key convention)

### API

```python
def generate_test_mlp(
    hidden_dims: Tuple[int, ...] = (64, 64),
    input_dim: int = 3072,
    output_dim: int = 10,
    seed: int = 42,
) -> Dict[str, torch.Tensor]:
    """Random MLP state_dict, layer{i}.weight/bias keys, matches SimpleCNN shape."""
    ...
```

### Tensor Shapes

| Key | Shape |
|-----|-------|
| layer0.weight / bias | [64, 3072] / [64] |
| layer1.weight / bias | [64, 64] / [64] |
| layer2.weight / bias | [10, 64] / [10] |

### Pseudo-code

```
1. torch.manual_seed(seed)
2. dims = [input_dim] + list(hidden_dims) + [output_dim]
3. for i in range(len(dims)-1):
     W = randn(dims[i+1], dims[i]) * 0.1
     b = zeros(dims[i+1])
     sd[f"layer{i}.weight"] = W; sd[f"layer{i}.bias"] = b
4. return sd
```

---

## M-2: Permutation Generator [Complexity: 4, Budget: 4]

**Applied**: torch.randperm standard pattern

### API

```python
def generate_permutations(hidden_dims: Tuple[int, ...] = (64, 64), base_seed: int = 0) -> List[torch.Tensor]:
    """One randperm(h) per hidden layer, seeded base_seed for reproducibility. -> [perm_0, perm_1]"""
    ...
```

### Pseudo-code

```
1. torch.manual_seed(base_seed)
2. return [torch.randperm(h) for h in hidden_dims]
```

---

## M-3: Permutation Application [Complexity: 8, Budget: 8]

**Applied**: Manual weight-row/col permutation (no KB pattern; correctness-critical, unit-testable)

### API

```python
def permute_state_dict(
    state_dict: Dict[str, torch.Tensor],
    n_hidden_layers: int = 2,
    perms: List[torch.Tensor] = None,
) -> Dict[str, torch.Tensor]:
    """Apply neuron perms[i] to layer{i} outputs, propagate to layer{i+1} inputs.
    layer{n_hidden_layers} (final output layer) gets input-col perm only, no output perm."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| perms[i] | [hidden_dims[i]] | index permutation |
| layer{i}.weight | [out_i, in_i] | rows=out neurons, cols=in neurons |

### Pseudo-code

```
1. new_sd = deepcopy(state_dict)
2. for i in range(n_hidden_layers):          # hidden layers: 0, 1
     W, b = new_sd[f"layer{i}.weight"], new_sd[f"layer{i}.bias"]
     W = W[perms[i], :]                      # permute output rows
     b = b[perms[i]]                         # permute output bias
     if i > 0:
         W = W[:, perms[i-1]]                # permute input cols from prev perm
     new_sd[f"layer{i}.weight"], new_sd[f"layer{i}.bias"] = W, b
3. # final output layer (index = n_hidden_layers), input-col perm only:
   W_out = new_sd[f"layer{n_hidden_layers}.weight"]
   new_sd[f"layer{n_hidden_layers}.weight"] = W_out[:, perms[-1]]
   # bias unchanged (no output permutation on final layer)
4. return new_sd
```

---

## M-4: Load H-E1 NFN + network_spec [Complexity: 7, Budget: 7]

**Applied**: PyTorch checkpoint load + eval() pattern

### API

```python
def load_nfn_model(
    checkpoint_path: str,
    network_spec: Any,
    nfn_channels: int = 32,
) -> "NFNRegressor":
    """Instantiate NFNRegressor(network_spec, nfn_channels), load_state_dict, .eval()."""
    ...
```

### Pseudo-code

```
1. sys.path.insert(0, str(h_e1_code_dir))
2. from model import NFNRegressor
3. from data import get_network_spec_from_sample
4. network_spec = get_network_spec_from_sample([{"state_dict": base_state_dict}])
5. model = NFNRegressor(network_spec, nfn_channels=32)
6. model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
7. model.eval()
8. return model
```

---

## M-5: wsfeat Conversion [Complexity: 6, Budget: 6]

**Applied**: Reuse H-E1's `make_collate_fn` batching pattern (single-sample batch)

### API

```python
def state_dict_to_wsfeat(state_dict: Dict[str, torch.Tensor], network_spec: Any) -> Any:
    """Single state_dict -> batched WeightSpaceFeatures [B=1, ...] via nfn.common.state_dict_to_tensors."""
    ...
```

### Pseudo-code

```
1. from nfn.common import state_dict_to_tensors, WeightSpaceFeatures
2. wts, bs = state_dict_to_tensors(state_dict)
3. wts_b = [w.unsqueeze(0) for w in wts]   # [1, ...]
4. bs_b = [b.unsqueeze(0) for b in bs]     # [1, ...]
5. return WeightSpaceFeatures(wts_b, bs_b)
```

---

## M-6: Inference Loop [Complexity: 5, Budget: 5]

**Applied**: torch.no_grad() eval loop

### API

```python
def run_predictions(
    nfn_model: nn.Module,
    base_state_dict: Dict[str, torch.Tensor],
    hidden_dims: Tuple[int, ...],
    network_spec: Any,
    n_perms: int = 10,
) -> List[float]:
    """[pred_original] + [pred_perm_i for i in 0..n_perms-1], len = n_perms + 1."""
    ...
```

### Pseudo-code

```
1. preds = []
2. wsfeat = state_dict_to_wsfeat(base_state_dict, network_spec)
3. with torch.no_grad(): preds.append(nfn_model(wsfeat).item())
4. for seed in range(n_perms):
     perms = generate_permutations(hidden_dims, base_seed=seed)
     perm_sd = permute_state_dict(base_state_dict, len(hidden_dims), perms)
     wsfeat_p = state_dict_to_wsfeat(perm_sd, network_spec)
     with torch.no_grad(): preds.append(nfn_model(wsfeat_p).item())
5. return preds
```

---

## M-7: Invariance Metrics [Complexity: 4, Budget: 4]

**Applied**: torch.std/mean built-ins

### API

```python
def compute_invariance_metrics(predictions: List[float]) -> Dict[str, float]:
    """{mean, std, max_deviation, invariance_score, invariance_correlation}"""
    ...

def gate_passed(metrics: Dict[str, float], dev_threshold: float = 1e-5, corr_threshold: float = 0.99) -> bool:
    """(max_deviation < dev_threshold) or (invariance_correlation > corr_threshold)"""
    ...
```

### Pseudo-code

```
1. preds = torch.tensor(predictions)
2. mean_pred = preds.mean(); std_pred = preds.std()
3. max_dev = (preds - mean_pred).abs().max()
4. invariance_score = 1.0 if max_dev < 1e-5 else 0.0
5. invariance_correlation = 1.0 - min(max_dev.item() / (mean_pred.abs().item() + 1e-12), 1.0)
6. return {mean, std, max_deviation, invariance_score, invariance_correlation}
```

---

## M-8: Visualization [Complexity: 5, Budget: 5]

**Applied**: matplotlib standard bar/heatmap/hist

### API

```python
def plot_predictions_bar(predictions: List[float], out_path: str) -> None: ...
def plot_deviation_heatmap(predictions: List[float], out_path: str) -> None: ...  # pairwise |p_i - p_j|, [11,11]
def plot_prediction_histogram(predictions: List[float], out_path: str) -> None: ...
```

Bar chart is required (FR-7); heatmap/histogram are additional (LLM-autonomous). Labels: index 0 = "original", 1-10 = "perm_{seed}".

---

## M-9: Gate Evaluation + Results Orchestration [Complexity: 6, Budget: 6]

**Applied**: Standard main() orchestration + json.dump

### API

```python
def main() -> None:
    """load checkpoint -> generate test MLP -> run_predictions -> metrics -> gate -> save results.json + figures."""
    ...
```

### Pseudo-code

```
1. base_sd = generate_test_mlp(seed=42)
2. network_spec = get_network_spec_from_sample([{"state_dict": base_sd}])
3. nfn_model = load_nfn_model(h_e1_checkpoint_path, network_spec, nfn_channels=32)
4. predictions = run_predictions(nfn_model, base_sd, hidden_dims=(64,64), network_spec=network_spec, n_perms=10)
5. metrics = compute_invariance_metrics(predictions)
6. passed = gate_passed(metrics)
7. plot_predictions_bar(predictions, "h-m1/figures/permutation_invariance.png")
8. plot_deviation_heatmap(predictions, "h-m1/figures/deviation_heatmap.png")
9. plot_prediction_histogram(predictions, "h-m1/figures/prediction_histogram.png")
10. json.dump({"predictions": predictions, "metrics": metrics, "gate_passed": passed}, "h-m1/results.json")
```

---

## Subtasks

No subtasks — all tasks are Low complexity (4-8), directly implementable per PRD Epic Tasks table in `03_architecture.md`.
