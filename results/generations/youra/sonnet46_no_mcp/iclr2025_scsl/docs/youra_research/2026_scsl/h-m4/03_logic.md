# Logic Design: H-M4
# DFR Efficacy Correlation with Backbone Training Depth

**Hypothesis ID:** H-M4
**Type:** MECHANISM (INCREMENTAL, extending H-E1 + H-M3)
**Date:** 2026-05-04

Applied: flat-module-layout
Applied: dataclass-config
Applied: checkpoint-at-specific-epochs
Applied: sklearn-logreg-dfr

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Analyzed directly (Serena MCP unavailable — read files directly)
**Analyzed Path**: `h-e1/code/` and `h-m3/code/`
**Relevant Symbols**:
- `h-e1/code/train.py`: `build_model(num_classes, pretrained)`, `get_transforms(augment)`, `train_one_seed(cfg, seed, device)` — uses `cfg.checkpoint_interval` (every N epochs, not specific epochs)
- `h-e1/code/data/waterbirds.py`: `WaterbirdsDataset.__getitem__` returns `{image, core_label, spurious_label}` — NO `group_id` field; must add `group_id = 2 * spurious_label + core_label`
- `h-e1/code/train.py`: batch key is `batch["core_label"]` (not `batch["label"]`)
- `h-m3/code/config.py`: `load_config(config_path)` → `ExperimentConfig` pattern confirmed

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/train.py (ACTUAL CODE)
def build_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    # ResNet-50; model.fc = nn.Linear(2048, num_classes)
    ...

def get_transforms(augment: bool) -> transforms.Compose:
    # augment=True: RandomResizedCrop(224) + RandomHorizontalFlip
    # augment=False: Resize(256) + CenterCrop(224)
    ...

def train_one_seed(cfg: TrainConfig, seed: int, device: str) -> None:
    # saves checkpoint when epoch % cfg.checkpoint_interval == 0
    # path: checkpoints/seed_{seed}/epoch_{epoch:03d}.pt
    # batch keys: batch["image"], batch["core_label"]
    ...

# From: h-e1/code/data/waterbirds.py (ACTUAL CODE)
class WaterbirdsDataset(Dataset):
    def __getitem__(self, idx: int) -> dict:
        # Returns: {image, core_label, spurious_label}
        # NO group_id — must compute: group_id = 2 * spurious_label + core_label
        ...

def get_waterbirds_loader(
    root: str, split: str, batch_size: int, num_workers: int, augment: bool = False
) -> DataLoader: ...
```

**Verified from**: `h-e1/code/` (actual implementation, NOT spec)

**Critical adaptation**: H-M4 `WaterbirdsDataset.__getitem__` must add `"group_id": 2 * int(row["place"]) + int(row["y"])` to the returned dict.

**Critical difference**: H-E1 `train_one_seed` saves checkpoints at `epoch % checkpoint_interval == 0`. H-M4 `BackboneTrainer.train_seed` must save at specific epochs `{1, 2, 10, 20, 30}`, not via interval.

---

## E-3: BackboneTrainer [Complexity: 14, High, Budget: 3]

Applied: checkpoint-at-specific-epochs

### API Signatures

```python
class BackboneTrainer:
    def __init__(self, cfg: ExperimentConfig, device: str):
        """Initialize trainer with config and device."""
        ...

    def train_seed(self, seed: int) -> Dict[int, str]:
        """Train ResNet-50 ERM, save checkpoints at cfg.train.checkpoint_epochs.
        Returns: {epoch: ckpt_path} for each checkpoint epoch.
        """
        ...

    def _save_checkpoint(self, model: nn.Module, epoch: int,
                         seed: int, ckpt_dir: str) -> str:
        """Save state_dict; return absolute path."""
        ...

    def _checkpoint_exists(self, epoch: int, seed: int) -> bool:
        """True if checkpoints/seed_{seed}/epoch_{epoch:03d}.pt exists."""
        ...
```

### Pseudo-code (train_seed)

```
1. set seeds: torch.manual_seed(seed), np.random.seed(seed), random.seed(seed)
2. ckpt_dir = cfg.paths.checkpoint_dir / seed_{seed}; makedirs
3. if all checkpoint_epochs exist → return {epoch: path} early
4. model = build_model().to(device)
5. optimizer = SGD(lr, momentum, weight_decay)
6. criterion = CrossEntropyLoss()
7. train_loader = get_waterbirds_loader(augment=True)
8. for epoch in 1..max_epochs:
   a. model.train(); iterate batches → loss.backward(); optimizer.step()
      (use batch["core_label"] as labels)
   b. if epoch in cfg.train.checkpoint_epochs:
      path = _save_checkpoint(model, epoch, seed, ckpt_dir)
      result[epoch] = path
      log: f"Checkpoint saved: epoch {epoch} → {path}"
9. return result
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Training loop | ERM train loop with SGD, CrossEntropyLoss, seed setup, batch["core_label"] key |
| L-3-2 | Checkpoint saving | Save at specific epochs set {1,2,10,20,30}; verify file exists; skip-if-exists logic |
| L-3-3 | ERM WGA logging | Load fc from checkpoint, evaluate WGA on test split at each checkpoint epoch |

---

## E-6: 5-Condition Pipeline [Complexity: 14, High, Budget: 3]

Applied: flat-module-layout

### API Signatures

```python
def run(config_path: str, device: str) -> Dict:
    """Main orchestrator. Returns full results dict."""
    ...
```

### Pseudo-code (run)

```
1. cfg = load_config(config_path)
2. trainer = BackboneTrainer(cfg, device)
3. extractor_cache = {}  # (seed, epoch) → (val_feats, val_labels, val_groups, test_feats, test_labels, test_groups)
4. dfr = DFRModule(cfg)
5. results_per_seed = {}  # {seed: {epoch: {erm_wga, dfr_wga, wga_improvement, feature_dim}}}

6. Phase A — Training:
   for seed in cfg.train.seeds:
       ckpt_map = trainer.train_seed(seed)  # {epoch: path}
       results_per_seed[seed] = {}

7. Phase B — Feature extraction + DFR (nested loop):
   for seed in cfg.train.seeds:
       extractor = FeatureExtractor(device=device)
       for epoch in cfg.analysis.conditions:
           ckpt_path = checkpoints/seed_{seed}/epoch_{epoch:03d}.pt
           key = (seed, epoch)
           if key not in extractor_cache:
               val_feats, val_labels, val_groups = extractor.extract_split(
                   cfg.train.data_root, "val", cfg, ckpt_path)
               test_feats, test_labels, test_groups = extractor.extract_split(
                   cfg.train.data_root, "test", cfg, ckpt_path)
               extractor_cache[key] = (val_feats, val_labels, val_groups,
                                       test_feats, test_labels, test_groups)
           metrics = dfr.evaluate_checkpoint(
               ckpt_path,
               val_feats, val_labels,
               test_feats, test_labels, test_groups,
               device)
           results_per_seed[seed][epoch] = metrics

8. Phase C — Analysis:
   analyzer = CorrelationAnalyzer(cfg)
   aggregated = analyzer.aggregate_across_seeds(results_per_seed)
   corr = analyzer.compute_pearson(aggregated, cfg.analysis.t_star_mean)
   gate = analyzer.evaluate_gate(corr["pearson_r"])
   monotonicity = analyzer.verify_monotonicity(corr["improvements"])

9. Phase D — Visualize + Export:
   viz = Visualizer(cfg)
   fig_paths = viz.save_all(results_per_seed, aggregated, corr, cfg.analysis.t_star_mean)
   exporter = ResultsExporter(cfg)
   json_path = exporter.save_json(results_per_seed, aggregated, corr, gate, fig_paths)
   exporter.print_summary(corr, gate)

10. return {results_per_seed, aggregated, correlation=corr, gate, figure_paths=fig_paths}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Training phase | Loop seeds → trainer.train_seed; build ckpt_map |
| L-6-2 | Feature+DFR loop | Nested seed×epoch loop; feature cache dict; dfr.evaluate_checkpoint per condition |
| L-6-3 | Analysis+export | aggregate, compute_pearson, gate, visualize, save JSON |

---

## E-5: DFRModule [Complexity: 13, Medium, Budget: 2]

Applied: sklearn-logreg-dfr

### API Signatures

```python
def worst_group_accuracy(
    predictions: np.ndarray,   # [N] int predictions
    labels: np.ndarray,        # [N] int true labels
    group_ids: np.ndarray,     # [N] int in {0,1,2,3}
) -> float:
    """min accuracy over groups 0..3."""
    ...

class DFRModule:
    def __init__(self, cfg: ExperimentConfig): ...

    def evaluate_checkpoint(
        self,
        checkpoint_path: str,
        val_feats: np.ndarray,   # [N_val, 2048]
        val_labels: np.ndarray,  # [N_val]
        test_feats: np.ndarray,  # [N_test, 2048]
        test_labels: np.ndarray, # [N_test]
        test_groups: np.ndarray, # [N_test]
        device: str,
    ) -> Dict[str, float]:
        """Returns: {erm_wga, dfr_wga, wga_improvement, feature_dim}"""
        ...

    def _erm_wga(
        self,
        checkpoint_path: str,
        test_feats: np.ndarray,   # [N_test, 2048]
        test_labels: np.ndarray,  # [N_test]
        test_groups: np.ndarray,  # [N_test]
        device: str,
    ) -> float: ...

    def _fit_dfr(
        self,
        val_feats: np.ndarray,   # [N_val, 2048]
        val_labels: np.ndarray,  # [N_val]
    ) -> LogisticRegression:
        """LogisticRegression(C=1.0, class_weight='balanced', solver='lbfgs', max_iter=1000, random_state=42)"""
        ...
```

### Pseudo-code (_erm_wga)

```
1. model = build_model().to(device); load state_dict(checkpoint_path)
2. model.eval()
3. fc_weights = model.fc.weight.detach().cpu().numpy()  # [2, 2048]
4. fc_bias = model.fc.bias.detach().cpu().numpy()       # [2]
5. logits = test_feats @ fc_weights.T + fc_bias         # [N_test, 2]
6. preds = logits.argmax(axis=1)                        # [N_test]
7. return worst_group_accuracy(preds, test_labels, test_groups)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| val_feats | [N_val, 2048] | Frozen ResNet-50 layer4 pool output |
| test_feats | [N_test, 2048] | Same extraction |
| fc_weights | [2, 2048] | ERM classifier weights |
| logits | [N_test, 2] | ERM scores via numpy matmul |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | worst_group_accuracy + _fit_dfr | WGA helper; LogReg fit with fixed seed=42 |
| L-5-2 | evaluate_checkpoint + _erm_wga | ERM fc-layer WGA; DFR predict WGA; log improvement |

---

## E-7: CorrelationAnalyzer [Complexity: 12, Medium, Budget: 2]

Applied: Standard scipy.stats pearsonr

### API Signatures

```python
class CorrelationAnalyzer:
    def __init__(self, cfg: ExperimentConfig): ...

    def aggregate_across_seeds(
        self,
        results_per_seed: Dict[int, Dict[int, Dict[str, float]]],
        # {seed: {epoch: {erm_wga, dfr_wga, wga_improvement}}}
    ) -> Dict[int, Dict[str, float]]:
        # Returns: {epoch: {mean_erm_wga, mean_dfr_wga, mean_wga_improvement, std_wga_improvement}}
        ...

    def compute_pearson(
        self,
        aggregated: Dict[int, Dict[str, float]],
        t_star: float,
    ) -> Dict[str, float]:
        # Returns: {pearson_r, pearson_p_twotailed, pearson_p_onetailed,
        #           epochs_past_tstar, improvements}
        ...

    def evaluate_gate(self, pearson_r: float) -> Dict[str, object]:
        # Returns: {gate_passed, pearson_r, threshold, decision, note}
        ...

    def verify_monotonicity(
        self,
        improvements: List[float],  # len=5, ordered by conditions
    ) -> Dict[str, object]:
        # Returns: {is_monotonic, n_positive_diffs, n_diffs, positive_fraction}
        ...
```

### Pseudo-code (compute_pearson)

```
1. epochs = sorted(aggregated.keys())  # [1, 2, 10, 20, 30]
2. x = [epoch - t_star for epoch in epochs]       # epochs_past_tstar
3. y = [aggregated[e]["mean_wga_improvement"] for e in epochs]  # improvements
4. r, p_two = pearsonr(x, y)
5. p_one = p_two / 2 if r > 0 else 1.0 - p_two / 2
6. return {pearson_r: r, pearson_p_twotailed: p_two,
           pearson_p_onetailed: p_one,
           epochs_past_tstar: x, improvements: y}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | aggregate_across_seeds | Mean/std of metrics over seeds per epoch condition |
| L-7-2 | compute_pearson + evaluate_gate + verify_monotonicity | Pearson r, one/two-tailed p, gate check (r>0.7), monotonicity diffs |

---

## E-4: FeatureExtractor [Complexity: 11, Medium, Budget: 2]

Applied: Standard PyTorch frozen backbone

### API Signatures

```python
class FeatureExtractor:
    def __init__(self, device: str):
        """No checkpoint_path at init — loaded per extract call."""
        ...

    def load_backbone(self, checkpoint_path: str) -> nn.Module:
        """Load ResNet-50, replace fc with Identity, load state_dict, eval+frozen.
        Returns backbone with model.fc = nn.Identity().
        """
        ...

    def extract(
        self,
        backbone: nn.Module,
        loader: DataLoader,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Extract layer4 AdaptiveAvgPool output.
        Returns: (features [N, 2048], labels [N], group_ids [N])
        Asserts features.shape[1] == 2048.
        """
        ...

    def extract_split(
        self,
        root: str,
        split: str,
        cfg: ExperimentConfig,
        checkpoint_path: str,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Build loader, load backbone, call extract().
        Returns: (features [N, 2048], labels [N], group_ids [N])
        """
        ...
```

### Pseudo-code (extract)

```
1. all_feats, all_labels, all_groups = [], [], []
2. with torch.no_grad():
   for batch in loader:
       imgs = batch["image"].to(device)         # [B, 3, 224, 224]
       feats = backbone(imgs).cpu().numpy()     # [B, 2048] (after fc=Identity)
       all_feats.append(feats)
       all_labels.append(batch["core_label"].numpy())
       all_groups.append(batch["group_id"].numpy())
3. features = np.concatenate(all_feats)   # [N, 2048]
4. assert features.shape[1] == 2048
5. return features, labels, group_ids
```

**Note**: `load_backbone` loads full state_dict first, then sets `model.fc = nn.Identity()` — avoids shape mismatch while discarding fc weights.

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| imgs | [B, 3, 224, 224] | ImageNet-normalized input |
| feats (per batch) | [B, 2048] | AdaptiveAvgPool output via Identity fc |
| features (full) | [N, 2048] | Concatenated all batches |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | load_backbone | Load ResNet-50 checkpoint; set fc=Identity; freeze; eval mode |
| L-4-2 | extract + extract_split | Batched feature extraction; group_id from batch; shape assert 2048 |

---

## Subtask Summary

| ID | Epic | Subtask | Description |
|----|------|---------|-------------|
| L-3-1 | E-3 | Training loop | ERM SGD loop with seed setup, batch["core_label"] key |
| L-3-2 | E-3 | Checkpoint saving | Save at specific epochs {1,2,10,20,30}; skip-if-exists |
| L-3-3 | E-3 | ERM WGA logging | Evaluate fc-layer WGA at each checkpoint |
| L-6-1 | E-6 | Training phase | Seed loop → train_seed → ckpt_map |
| L-6-2 | E-6 | Feature+DFR loop | Nested seed×epoch; feature cache dict; DFR per condition |
| L-6-3 | E-6 | Analysis+export | Aggregate, Pearson, gate, visualize, JSON |
| L-5-1 | E-5 | WGA + fit_dfr | worst_group_accuracy helper; LogReg(C=1.0, seed=42) |
| L-5-2 | E-5 | evaluate_checkpoint | ERM fc WGA via numpy matmul; DFR predict; log |
| L-7-1 | E-7 | Aggregate seeds | Mean/std metrics per epoch over 3 seeds |
| L-7-2 | E-7 | Pearson + gate | pearsonr, one-tailed p, gate r>0.7, monotonicity |
| L-4-1 | E-4 | load_backbone | ResNet-50 → fc=Identity; freeze; eval |
| L-4-2 | E-4 | extract | Batched extraction; group_id key; assert shape==2048 |

**Total: 12/12 subtasks used**

---

*Logic design for H-M4 — DFR efficacy vs. backbone training depth (t*=2 epochs from H-M3)*
*Generated: 2026-05-04*
