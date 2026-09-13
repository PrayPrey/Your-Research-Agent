# Logic: H-E1 — Checkpoint Linear Probe Battery (EXISTENCE)

Applied: checkpoint-linear-probe-erm pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Probe Battery [Complexity: 14 High, Budget: 4 subtasks]

Applied: frozen-backbone-avgpool-hook pattern

### API Signatures

```python
# probe.py

def extract_features(
    model: nn.Module,
    loader: DataLoader,
    device: str,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract avgpool features from frozen model.
    Returns (features [N,2048], core_labels [N], spurious_labels [N])
    """
    # Register forward hook on model.avgpool
    # model.eval() + torch.no_grad()
    # Accumulate hook outputs per batch, then stack
    # Waterbirds: N=1199; CelebA: N=19867
    ...


def fit_probe(
    features: np.ndarray,   # [N, 2048]
    labels: np.ndarray,     # [N]
    cfg: "ProbeConfig",
) -> float:
    """Fit L2 logistic regression probe, return accuracy on same split."""
    # LogisticRegression(C=cfg.C, max_iter=cfg.max_iter,
    #                    solver=cfg.solver, random_state=cfg.random_state)
    # Returns clf.score(features, labels)
    ...


def run_probe_battery(
    cfg: "ExperimentConfig",
    seed: int,
    device: str,
) -> pd.DataFrame:
    """Per-checkpoint loop: load -> extract -> probe x2 -> delta -> discard.
    Returns DataFrame columns=[epoch, spurious_acc, core_acc, delta]
    """
    # checkpoint_epochs = range(2, cfg.train.epochs+1, cfg.train.checkpoint_interval)
    # For each epoch t:
    #   ckpt_path = f"{cfg.train.checkpoint_dir}/seed_{seed}/epoch_{t:03d}.pt"
    #   model.load_state_dict(torch.load(ckpt_path, map_location=device))
    #   feats, core_lbls, spur_lbls = extract_features(model, val_loader, device)
    #   spur_acc = fit_probe(feats, spur_lbls, cfg.probe)
    #   core_acc = fit_probe(feats, core_lbls, cfg.probe)
    #   delta = spur_acc - core_acc
    #   del feats  # discard immediately — memory safety
    # Return pd.DataFrame(records)
    ...


def run_all_seeds(
    cfg: "ExperimentConfig",
    device: str,
) -> pd.DataFrame:
    """Multi-seed orchestration. Returns combined DataFrame with seed column."""
    # For seed in cfg.train.seeds:
    #   df_seed = run_probe_battery(cfg, seed, device)
    #   df_seed["seed"] = seed
    #   results.append(df_seed)
    # Return pd.concat(results, ignore_index=True)
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features (Waterbirds) | (1199, 2048) | avgpool output, val set |
| features (CelebA) | (19867, 2048) | avgpool output, val set |
| hook buffer per batch | (B, 2048) | B=128 default |
| core_labels / spurious_labels | (N,) | int64 |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | extract_features | avgpool hook registration, batch loop, (N,2048) output |
| L-3-2 | fit_probe | LogisticRegression(C=1.0, lbfgs), spurious/core label handling |
| L-3-3 | run_probe_battery | per-checkpoint loop with memory-safe feature discard |
| L-3-4 | run_all_seeds | multi-seed orchestration, DataFrame with seed column |

---

## A-2: ERM Training [Complexity: 13 Medium, Budget: 2 subtasks]

Applied: resnet50-erm-sgd-checkpoint pattern

### API Signatures

```python
# train.py

def build_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """ResNet-50 with replaced FC head. Returns model (not moved to device)."""
    # model = torchvision.models.resnet50(pretrained=pretrained)
    # model.fc = nn.Linear(2048, num_classes)
    # Returns model — caller moves to device
    ...


def get_transforms(augment: bool) -> transforms.Compose:
    """Return train (augment=True) or val transforms."""
    # augment=True:  RandomResizedCrop(224), RandomHorizontalFlip, ToTensor, Normalize
    # augment=False: Resize(256), CenterCrop(224), ToTensor, Normalize
    # Normalize: mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]
    ...


def train_one_seed(cfg: "TrainConfig", seed: int, device: str) -> None:
    """ERM training for one seed. Saves checkpoints to disk every 2 epochs."""
    # 1. Set seeds: torch.manual_seed(seed), np.random.seed(seed), random.seed(seed)
    # 2. model = build_model().to(device)
    # 3. optimizer = SGD(model.parameters(), lr=cfg.lr,
    #                    momentum=cfg.momentum, weight_decay=cfg.weight_decay)
    # 4. criterion = nn.CrossEntropyLoss()
    # 5. For epoch in range(1, cfg.epochs+1):
    #      train one epoch (standard forward/backward/step)
    #      if epoch % cfg.checkpoint_interval == 0:
    #        path = f"{cfg.checkpoint_dir}/seed_{seed}/epoch_{epoch:03d}.pt"
    #        torch.save(model.state_dict(), path)
    ...


def main(cfg: "TrainConfig", device: str) -> None:
    """Iterate over cfg.seeds, call train_one_seed per seed."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input batch | (128, 3, 224, 224) | standard ImageNet size |
| avgpool output (per sample) | (2048,) | after flatten |
| logits | (128, 2) | 2-class head |

### Checkpoint Save Protocol

```
{checkpoint_dir}/seed_{seed}/epoch_{t:03d}.pt   <- model.state_dict() only
Waterbirds: t in {2, 4, ..., 300} → 150 files per seed
CelebA:     t in {2, 4, ..., 50}  →  25 files per seed
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | train_one_seed | SGD setup, epoch loop, checkpoint save every 2 epochs |
| L-2-2 | build_model | ResNet-50 pretrained, FC replacement for 2-class output |
