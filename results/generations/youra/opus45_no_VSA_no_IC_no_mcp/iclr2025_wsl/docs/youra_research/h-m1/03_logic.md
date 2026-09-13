# Logic: h-m1 (MECHANISM)

**Applied**: training-dynamics-tracking-pattern (per-epoch gradient/weight hooks around existing train loop)
**Applied**: distributional-comparison-pattern (Wasserstein distance + CoV over per-layer time series)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code (Serena MCP unavailable in this environment; `Read` used directly on `h-e1/code/*.py` per fallback — files are small and fully readable, equivalent verification).
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Relevant Symbols**: `FlattenedMLP.forward`, `DWSModel.forward`, `DWSModel.get_layer_activations`, `NFTModel.forward`, `NFTModel.get_attention_weights`, `train_model`, `evaluate`, `get_dataloaders`, `get_weight_shapes`, `attention_entropy`, `layer_activation_variance`, `Config` (all read from actual `.py` files, not spec).

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/models.py (ACTUAL CODE)
class FlattenedMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int] = None, num_classes: int = 10, dropout: float = 0.1): ...
    def forward(self, weight_list: List[Tensor]) -> Tensor: ...  # -> [B, num_classes]

class DWSModel(nn.Module):
    def __init__(self, weight_shapes: List[Tuple[int, int]], hidden: int = 128, num_classes: int = 10): ...
    def forward(self, weight_list: List[Tensor]) -> Tensor: ...  # -> [B, num_classes]
    def get_layer_activations(self, weight_list: List[Tensor]) -> List[Tensor]: ...  # per-layer feats, each [B, hidden]

class NFTModel(nn.Module):
    def __init__(self, weight_shapes: List[Tuple[int, int]], d_model: int = 128, nhead: int = 4,
                 num_layers: int = 2, num_classes: int = 10): ...
    def forward(self, weight_list: List[Tensor]) -> Tensor: ...  # -> [B, num_classes]
    def get_attention_weights(self, weight_list: List[Tensor]) -> Tensor: ...
    # -> [B, nhead, num_tokens, num_tokens] (average_attn_weights=False, last encoder layer)

# From: h-e1/code/train.py
def train_model(model: nn.Module, train_loader: DataLoader, cfg: Config) -> nn.Module: ...
def evaluate(model: nn.Module, test_loader: DataLoader, cfg: Config) -> Dict: ...  # {"accuracy": float}

# From: h-e1/code/data.py
def get_dataloaders(cfg: Config) -> Tuple[DataLoader, DataLoader]: ...
def get_weight_shapes(cfg: Config) -> List[Tuple[int, int]]: ...
# batch item: weight_list is List[Tensor], each [B, in_c, out_c] after collate_fn

# From: h-e1/code/metrics.py
def attention_entropy(attn_weights: Tensor) -> float: ...
def layer_activation_variance(layer_outputs: List[Tensor]) -> float: ...

# From: h-e1/code/config.py
@dataclass
class Config:
    data_dir: str = "data/mnist_inrs"
    batch_size: int = 64
    d_model: int = 128; nhead: int = 4; num_layers: int = 2
    dws_hidden: int = 128; mlp_hidden: list; dropout: float = 0.1; num_classes: int = 10
    lr: float = 1e-3; weight_decay: float = 1e-4; epochs: int = 50; cosine_t_max: int = 50
    seed: int = 42; device: str = "cuda"
    results_path: str; fig_dir: str; checkpoint_dir: str
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation).

**Important**: `train_model` has NO hooks — h-m1 must NOT monkeypatch it; write a parallel `train_model_tracked` that duplicates the AdamW/CosineAnnealingLR/CrossEntropyLoss loop and inserts tracker calls (per architecture decision).

---

## M-2+M-3: TrainingDynamicsTracker + Instrumented Training Loop [Complexity: 12+11, Budget: 2 subtasks]

**Applied**: hook-based-metric-collection (accumulate into dict of lists per epoch, no autograd hooks needed — grads read from `.grad` after `backward()`)

### API Signatures

```python
# tracker.py
class TrainingDynamicsTracker:
    def __init__(self, model: nn.Module, model_type: str):
        """model_type: 'mlp' | 'dws' | 'nft'."""
        self.grad_norms: dict[str, list[float]] = {}      # {param_name: [norm_per_epoch]}
        self.weight_updates: dict[str, list[float]] = {}  # {param_name: [delta_norm_per_snapshot]}
        self.attention_entropy: list[float] = []           # nft only

    def track_gradients(self, epoch: int) -> None:
        """Reads model.named_parameters() .grad after backward(), appends L2 norm per param."""
        ...

    def track_weight_updates(self, prev_weights: dict[str, Tensor], epoch: int) -> None:
        """delta = current_param - prev_weights[name]; appends delta.norm() per param."""
        ...

    def track_attention(self, sample_input: List[Tensor]) -> None:
        """NFT only: calls model.get_attention_weights(sample_input) -> attention_entropy()."""
        ...

    def snapshot_weights(self) -> dict[str, Tensor]:
        """Returns {name: param.detach().clone() for name, param in model.named_parameters()}."""
        ...

    def to_dict(self) -> dict:
        return {"grad_norms": self.grad_norms, "weight_updates": self.weight_updates,
                "attention_entropy": self.attention_entropy}
```

```python
# train_tracked.py
def train_model_tracked(
    model: nn.Module,
    model_type: str,
    train_loader: DataLoader,
    cfg: Config,
    sample_input: Optional[List[Tensor]] = None,  # fixed batch for attention tracking (nft)
) -> Tuple[nn.Module, TrainingDynamicsTracker]:
    """Duplicates train_model's AdamW/CosineAnnealingLR loop; adds tracker calls per epoch."""
    ...
```

### Pseudo-code (train_model_tracked)

```
1. optimizer = AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
2. scheduler = CosineAnnealingLR(optimizer, T_max=cfg.cosine_t_max)
3. tracker = TrainingDynamicsTracker(model, model_type)
4. prev_weights = tracker.snapshot_weights()
5. for epoch in range(cfg.epochs):
     for weight_list, labels in train_loader:
         loss = CE(model(weight_list), labels); loss.backward()
         if epoch % cfg.track_every == 0: tracker.track_gradients(epoch)  # before optimizer.step()
         optimizer.step(); optimizer.zero_grad()
     scheduler.step()
     if (epoch + 1) % cfg.snapshot_every == 0:
         tracker.track_weight_updates(prev_weights, epoch)
         prev_weights = tracker.snapshot_weights()
     if model_type == "nft" and sample_input is not None:
         tracker.track_attention(sample_input)
6. return model, tracker
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weight_list[i] | [B, in_c, out_c] | per-layer batched INR weights |
| grad_norms[name] | list[float], len = epochs/track_every | scalar L2 norm per param per epoch |
| attn (via track_attention) | [B, nhead, T, T] | from `get_attention_weights` |

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M1-1 | tracker.py | TrainingDynamicsTracker: track_gradients, track_weight_updates, track_attention, snapshot_weights, to_dict |
| L-M1-2 | train_tracked.py | train_model_tracked: instrumented loop, weight snapshotting every cfg.snapshot_every epochs |

---

## M-4+M-6: Distributional Metrics + Early-Signature Check [Complexity: 8+6, Budget: 1 subtask]

### API Signatures

```python
# metrics.py additions (h-e1 attention_entropy, layer_activation_variance reused unchanged)
from scipy.stats import wasserstein_distance

def wasserstein_grad_distance(dws_norms: List[float], nft_norms: List[float]) -> float:
    """scipy.stats.wasserstein_distance(dws_norms, nft_norms)."""
    ...

def weight_update_cov(layer_updates: dict[str, List[float]]) -> float:
    """CoV = std(final-epoch delta per layer) / mean(...) across layers."""
    ...

def locality_score(layer_updates: dict[str, List[float]], epoch: int) -> float:
    """Same formula as weight_update_cov but restricted to updates <= epoch."""
    ...

def check_success_criteria(dws_stats: dict, nft_stats: dict, cfg: Config) -> dict[str, bool]:
    """Returns {'grad_flow_diff': bool, 'dws_locality': bool,
    'nft_entropy_increases': bool, 'early_signature': bool}."""
    ...
```

### Pseudo-code (check_success_criteria)

```
1. grad_flow_diff = wasserstein_grad_distance(dws_stats['grad_norms_flat'], nft_stats['grad_norms_flat']) > cfg.wasserstein_threshold
2. dws_locality = weight_update_cov(dws_stats['weight_updates']) > weight_update_cov(nft_stats['weight_updates'])
3. nft_entropy_increases = nft_stats['attention_entropy'][-1] > nft_stats['attention_entropy'][0]
4. early_signature = locality_score(dws_stats['weight_updates'], cfg.early_signature_epoch) differs
   from locality_score(nft_stats['weight_updates'], cfg.early_signature_epoch) by > threshold
5. return dict of the 4 booleans
```

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M1-3 | metrics.py additions | wasserstein_grad_distance, weight_update_cov, locality_score, check_success_criteria |

---

## M-1+M-5+M-7+M-8: Port + Multi-seed Runner + Visualization + Orchestration [Budget: 1 subtask]

### API Signatures

```python
# config.py
@dataclass
class Config(BaseConfig):
    epochs: int = 100
    lr: float = 1e-4
    seeds: list = field(default_factory=lambda: [42, 123, 7])
    track_every: int = 1
    snapshot_every: int = 10
    wasserstein_threshold: float = 0.1
    early_signature_epoch: int = 20

# run_seeds.py
def run_single(model_type: str, seed: int, cfg: Config, weight_shapes: List[Tuple[int, int]]) -> dict:
    """Builds model by type, trains via train_model_tracked, evals via evaluate().
    Returns {**tracker.to_dict(), 'accuracy': float, 'seed': int}."""
    ...

def run_all_seeds(cfg: Config) -> dict:
    """Returns {'mlp': [...], 'dws': [...], 'nft': [...]}, one dict per seed per model_type."""
    ...

# visualize.py
def plot_gradient_heatmap(dws_grads: dict, nft_grads: dict, out_path: str) -> None: ...
def plot_locality_evolution(dws_updates: dict, out_path: str) -> None: ...
def plot_attention_entropy_curve(nft_entropy: List[float], out_path: str) -> None: ...
def plot_layerwise_update_boxplot(dws_updates: dict, nft_updates: dict, out_path: str) -> None: ...
def plot_gate_metrics(results: dict, out_path: str) -> None: ...  # required gate figure

# main.py
def main() -> None:
    """cfg -> run_all_seeds -> aggregate stats -> check_success_criteria -> visualize -> save results.json."""
    ...
```

### Subtasks [1/4 used — M-1 (port), M-7 (viz) folded into implementation of this subtask, no separate budget line]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M1-4 | run_seeds.py + visualize.py + main.py + config.py | Port config; multi-seed runner (mlp/dws/nft x 3 seeds); 5 plots; main.py orchestration + results.json |

---

## Total Subtasks: 4/4 used
