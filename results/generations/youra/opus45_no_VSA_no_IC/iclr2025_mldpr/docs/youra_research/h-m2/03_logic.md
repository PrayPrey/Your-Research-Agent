# Logic: H-M2 Training Regime vs Cross-Dataset Gap

**Scope**: High-complexity modules only — M-4, M-5, M-6 (budget: 6 subtasks)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (confirmed in 03_architecture.md)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

## Applied Patterns

Applied: Standard PyTorch SGD+cosine fine-tuning loop (torchvision ResNet-50)
Applied: sklearn KNeighborsClassifier for cosine k-NN eval (feature caching to .npy)

---

## M-4: Single-Benchmark Training [Complexity: 11, Budget: 3+2+3+3]

**Applied**: Standard PyTorch fine-tuning loop

### API Signatures

```python
def finetune_single(
    benchmark: str,          # in {cub, dogs, cars, aircraft, flowers}
    seed: int,
    cfg: Config,
) -> str:
    """Fine-tune ResNet-50 on single benchmark. Returns ckpt path."""
    ...

def train_one_epoch(
    model: FeatureResNet50,
    loader: DataLoader,
    optimizer: torch.optim.SGD,
    scheduler: torch.optim.lr_scheduler.CosineAnnealingLR,
    criterion: nn.CrossEntropyLoss,
    device: torch.device,
) -> float:  # avg loss
    ...

def run_all_single(cfg: Config) -> list[str]:
    """5 benchmarks x 3 seeds -> 15 ckpt paths."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x (batch img) | [B, 3, 224, 224] | B=cfg.batch_size |
| logits | [B, num_classes] | per-benchmark class count |
| loss | scalar | CrossEntropyLoss |

### Pseudo-code (training loop)

```
def finetune_single(benchmark, seed, cfg):
    set_seed(seed)
    train_loader = build_dataloader(benchmark, cfg.data_root, train=True, cfg.batch_size)
    model = FeatureResNet50(num_classes=NUM_CLASSES[benchmark], pretrained=True).to(device)
    optimizer = SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.epochs)
    criterion = CrossEntropyLoss()

    for epoch in range(cfg.epochs):
        avg_loss = train_one_epoch(model, train_loader, optimizer, scheduler, criterion, device)
        scheduler.step()

    ckpt_path = f"{cfg.ckpt_dir_single}/{benchmark}_seed{seed}.pt"
    torch.save(model.state_dict(), ckpt_path)
    return ckpt_path

def run_all_single(cfg):
    return [finetune_single(b, s, cfg) for b in cfg.single_benchmarks for s in cfg.seeds]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M4-1 | train_one_epoch | Forward/backward/step, return avg loss |
| L-M4-2 | finetune_single | Full loop: model init, optimizer, scheduler, save ckpt |
| L-M4-3 | run_all_single | Loop over 5 benchmarks x 3 seeds, collect ckpt paths |
| L-M4-4 | set_seed util | torch/numpy/random seeding for reproducibility (NFR-3) |

---

## M-5: Multi-Benchmark Training [Complexity: 12, Budget: 3+3+3+3]

**Applied**: Standard PyTorch fine-tuning loop + WeightedRandomSampler balancing

### API Signatures

```python
def finetune_multi(
    benchmark_names: list[str],   # e.g. ["cub","dogs","cars"]
    seed: int,
    cfg: Config,
) -> str:
    """Fine-tune ResNet-50 on ConcatDataset w/ balanced sampler. Returns ckpt path."""
    ...

def run_all_multi(cfg: Config) -> list[str]:
    """3 mixes x 3 seeds -> 9 ckpt paths."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x (batch img) | [B, 3, 224, 224] | mixed-dataset batch |
| labels | [B] | unified label space (offset-applied) |
| logits | [B, total_classes] | total_classes = sum of per-dataset classes in mix |

### Pseudo-code (training loop)

```
def finetune_multi(benchmark_names, seed, cfg):
    set_seed(seed)
    loader = build_multi_dataloader(benchmark_names, cfg.data_root, cfg.batch_size)
    # loader internally uses ConcatDataset + WeightedRandomSampler (from M-2)

    total_classes = sum(NUM_CLASSES[b] for b in benchmark_names)
    model = FeatureResNet50(num_classes=total_classes, pretrained=True).to(device)
    optimizer = SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=cfg.epochs)
    criterion = CrossEntropyLoss()

    for epoch in range(cfg.epochs):
        avg_loss = train_one_epoch(model, loader, optimizer, scheduler, criterion, device)  # reuse M-4
        scheduler.step()

    mix_id = "_".join(benchmark_names)
    ckpt_path = f"{cfg.ckpt_dir_multi}/{mix_id}_seed{seed}.pt"
    torch.save(model.state_dict(), ckpt_path)
    return ckpt_path

def run_all_multi(cfg):
    return [finetune_multi(mix, s, cfg) for mix in cfg.multi_configs for s in cfg.seeds]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M5-1 | finetune_multi | Full loop: multi-loader, total_classes model init, save ckpt (reuses train_one_epoch from L-M4-1) |
| L-M5-2 | run_all_multi | Loop over 3 mixes x 3 seeds, collect ckpt paths |
| L-M5-3 | class-offset label validation | Assert unified label range matches total_classes before training starts |

---

## M-6: k-NN Cross-Dataset Eval [Complexity: 13, Budget: 3+3+3+4]

**Applied**: sklearn KNeighborsClassifier (cosine metric) on cached 2048-d features

### API Signatures

```python
def extract_features(
    model: FeatureResNet50,
    loader: DataLoader,
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (features [N,2048], labels [N])."""
    ...

def cache_features(
    features: np.ndarray, labels: np.ndarray, cache_path: str,
) -> None:
    """Save to .npz (NFR-2: cache to disk)."""
    ...

def load_cached_features(cache_path: str) -> tuple[np.ndarray, np.ndarray]:
    ...

def knn_accuracy(
    support_features: np.ndarray,  # [S, 2048]
    support_labels: np.ndarray,    # [S]
    query_features: np.ndarray,    # [Q, 2048]
    query_labels: np.ndarray,      # [Q]
    k: int = 5,
) -> float:
    """cosine-metric k-NN accuracy on query set."""
    ...

def sample_support_set(
    features: np.ndarray, labels: np.ndarray, n_per_class: int = 5, seed: int = 0,
) -> tuple[np.ndarray, np.ndarray]:
    ...

def evaluate_in_distribution(model: FeatureResNet50, benchmark: str, cfg: Config) -> float: ...
def evaluate_ood(model: FeatureResNet50, target_benchmark: str, cfg: Config) -> float: ...

def evaluate_all_targets(
    model: FeatureResNet50,
    train_domains: list[str],
    eval_domains: list[str],   # in-dist domains + cfg.held_out_eval
    cfg: Config,
) -> dict[str, float]:
    """{domain_name: accuracy} for each eval domain, incl. NABirds OOD."""
    ...

def run_all_knn_eval(ckpt_paths: list[str], train_domains_map: dict[str, list[str]], cfg: Config) -> dict[str, dict[str, float]]:
    """{ckpt_path: {domain: acc}} for all 24 models."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features | [N, 2048] | avgpool output, N=dataset size |
| support_features | [S, 2048] | S = n_classes * knn_support_per_class(=5) |
| query_features | [Q, 2048] | Q = full target test split |
| pred_labels | [Q] | k-NN majority vote |

### Pseudo-code (feature extraction + k-NN)

```
def extract_features(model, loader):
    model.eval()
    feats, labels = [], []
    with torch.no_grad():
        for x, y in loader:
            f = model.extract_features(x.to(device))  # [B, 2048]
            feats.append(f.cpu().numpy()); labels.append(y.numpy())
    return np.concatenate(feats), np.concatenate(labels)

def knn_accuracy(support_features, support_labels, query_features, query_labels, k=5):
    clf = KNeighborsClassifier(n_neighbors=k, metric="cosine")
    clf.fit(support_features, support_labels)
    preds = clf.predict(query_features)
    return accuracy_score(query_labels, preds)

def evaluate_all_targets(model, train_domains, eval_domains, cfg):
    results = {}
    for domain in eval_domains:
        cache_path = f"{cfg.feature_dir}/{domain}_test.npz"
        if exists(cache_path):
            q_feat, q_lab = load_cached_features(cache_path)
        else:
            q_loader = build_dataloader(domain, cfg.data_root, train=False, cfg.batch_size)
            q_feat, q_lab = extract_features(model, q_loader)
            cache_features(q_feat, q_lab, cache_path)

        s_loader = build_dataloader(domain, cfg.data_root, train=True, cfg.batch_size)
        s_feat_all, s_lab_all = extract_features(model, s_loader)
        s_feat, s_lab = sample_support_set(s_feat_all, s_lab_all, cfg.knn_support_per_class)

        results[domain] = knn_accuracy(s_feat, s_lab, q_feat, q_lab, cfg.knn_k)
    return results

def run_all_knn_eval(ckpt_paths, train_domains_map, cfg):
    out = {}
    for path in ckpt_paths:
        model = load_model_from_ckpt(path, cfg)
        train_domains = train_domains_map[path]
        eval_domains = train_domains + [cfg.held_out_eval]
        out[path] = evaluate_all_targets(model, train_domains, eval_domains, cfg)
    return out
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M6-1 | extract_features + cache/load | Feature extraction loop + .npz disk cache (NFR-2) |
| L-M6-2 | sample_support_set + knn_accuracy | Stratified support sampling, sklearn cosine k-NN |
| L-M6-3 | evaluate_in_distribution / evaluate_ood / evaluate_all_targets | Domain-level accuracy dict incl. NABirds OOD |
| L-M6-4 | run_all_knn_eval | Loop over 24 ckpts x eval domains, aggregate results |

---

## Shared Utilities (cross-module)

```python
NUM_CLASSES: dict[str, int] = {
    "cub": 200, "dogs": 120, "flowers": 102, "cars": 196, "aircraft": 100, "nabirds": 555,
}

def set_seed(seed: int) -> None: ...  # torch.manual_seed, np.random.seed, random.seed

def load_model_from_ckpt(ckpt_path: str, cfg: Config) -> FeatureResNet50: ...
```
