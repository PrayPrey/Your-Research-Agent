# Logic: H-M3

**Hypothesis:** EK-FAC/TracIn/TRAK attribution methods have architecture-dependent performance due to curvature assumptions.

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M2)
**Status:** No active Serena project registered (same as H-M2/H-M3 architecture doc) — fell back to direct `Read` of `h-m2/code/*.py` (actual implementation, not spec).
**Analyzed Path:** `docs/youra_research/h-m2/code/`
**Relevant Symbols:** `load_sst2_splits`, `build_dataloader`, `TextDataset` (data_loader.py); `load_bert_classifier`, `load_gpt2_classifier` (models.py); `finetune`, `save_checkpoint`, `load_checkpoint` (finetune.py); `ExperimentConfig` (config.py).
**Signature discrepancies found vs architecture doc:**
- `load_checkpoint(model, path, device)` — takes **3 args** including `device` (arch doc listed 2-arg version). Use actual signature.
- H-M2 `finetune()` has no per-epoch checkpoint saving; only `save_checkpoint(model, path)` exists as a separate call. H-M3's `finetune_with_checkpoints` must call `save_checkpoint` inside the epoch loop (new code, not reuse).

---

## External Dependencies API

```python
# From: h-m2/code/data_loader.py (ACTUAL CODE, unmodified reuse)
def load_sst2_splits() -> tuple[list, list, list, list]:
    """Returns (train_texts, train_labels, val_texts, val_labels)."""

def build_dataloader(tokenizer, texts, labels, batch_size, max_length=128, shuffle=True) -> DataLoader: ...

# From: h-m2/code/models.py (ACTUAL CODE, unmodified reuse)
def load_bert_classifier(model_id="bert-base-uncased") -> tuple[nn.Module, "AutoTokenizer"]: ...
def load_gpt2_classifier(model_id="gpt2") -> tuple[nn.Module, "GPT2Tokenizer"]: ...

# From: h-m2/code/finetune.py (ACTUAL CODE — pattern reused, NOT imported directly;
# H-M3 needs mislabel injection + per-epoch checkpoints, so h-m3/finetune.py reimplements)
def save_checkpoint(model, path: str) -> None: ...
def load_checkpoint(model, path: str, device: str) -> nn.Module:  # note: 3 args, includes device!
    ...
```

---

## A-1: Data + Mislabel Pipeline [Complexity: 6]

**Applied:** Standard PyTorch / numpy seeded shuffling.

### API Signatures

```python
# mislabel.py
def inject_mislabels(labels: list[int], fraction: float, seed: int) -> tuple[list[int], list[int]]:
    """Flip binary labels for `fraction` of indices (seeded). Returns (flipped_labels, mislabeled_indices)."""

def save_mislabeled_indices(indices: list[int], path: str) -> None: ...
def load_mislabeled_indices(path: str) -> list[int]: ...
```

### Pseudo-code

```
1. rng = np.random.default_rng(seed)
2. n_flip = int(len(labels) * fraction)
3. idx = rng.choice(len(labels), size=n_flip, replace=False)
4. flipped = labels.copy(); flipped[idx] = 1 - flipped[idx]  # binary flip
5. return flipped, sorted(idx.tolist())
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_sst2_splits reuse | Import from h-m2 data_loader (no change) |
| L-1-2 | inject_mislabels | Seeded flip, 5% fraction |
| L-1-3 | save/load_mislabeled_indices | JSON persist for ground truth |
| L-1-4 | Wire into run_experiment | Apply same indices to both BERT/GPT-2 train sets |

---

## A-2: Model + Fine-tune with Checkpoints [Complexity: 8]

**Applied:** Standard PyTorch training loop (extends h-m2 `finetune`).

### API Signatures

```python
# finetune.py
def finetune_with_checkpoints(
    model: nn.Module, tokenizer, train_loader: DataLoader,
    epochs: int, lr: float, device: str,
    ckpt_dir: str, ckpt_prefix: str,
) -> list[str]:
    """Trains `epochs` epochs; saves state_dict after each epoch. Returns ckpt paths (len == epochs)."""

def load_checkpoint(model: nn.Module, path: str, device: str) -> nn.Module: ...  # matches h-m2 signature exactly
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, 128] | B = train_batch_size |
| logits | [B, 2] | binary SST-2 |

### Pseudo-code

```
1. model.to(device); optimizer = AdamW(model.parameters(), lr)
2. for epoch in range(epochs):
3.     train one epoch (same loop as h-m2 finetune())
4.     path = f"{ckpt_dir}/{ckpt_prefix}_epoch{epoch+1}.pt"
5.     save_checkpoint(model, path); paths.append(path)
6. return paths
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load_bert/gpt2_classifier reuse | h-m2 models.py, unmodified |
| L-2-2 | finetune_with_checkpoints | Epoch loop + per-epoch save |
| L-2-3 | load_checkpoint reuse | 3-arg signature verified from h-m2 |
| L-2-4 | Wire into run_experiment | Train BERT + GPT-2 on mislabeled data, 3 ckpts each |

---

## A-3: EK-FAC Attribution [Complexity: 15]

**Applied:** kronfluence `Analyzer`/`FactorArguments`/`ScoreArguments` pattern (Kronecker-factored curvature).

### API Signatures

```python
# ekfac_attribution.py
def fit_ekfac_factors(model: nn.Module, task: "kronfluence.Task", train_loader: DataLoader,
                       strategy: str = "ekfac") -> "kronfluence.Analyzer":
    """Fits Kronecker factors via kronfluence.Analyzer.fit_all_factors(strategy=strategy)."""

def compute_ekfac_scores(analyzer: "kronfluence.Analyzer", query_loader: DataLoader,
                          train_loader: DataLoader, strategy: str) -> np.ndarray:
    """Pairwise influence scores. Returns [n_query, n_train]."""

def run_ekfac_strategy_ablation(model: nn.Module, task, train_loader: DataLoader,
                                 query_loader: DataLoader, strategies: list[str]) -> dict[str, np.ndarray]:
    """{strategy_name: scores[n_query, n_train]} for identity/diagonal/kfac/ekfac."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores | [n_query=872, n_train=67349] | pairwise influence matrix |
| per-train aggregate | [67349] | mean(abs(scores), axis=0) for AUC |

### Pseudo-code

```
1. analyzer = Analyzer(analysis_name=f"{arch}_ekfac", model=model, task=task)
2. analyzer.fit_all_factors(factors_name=strategy, dataset=train_loader.dataset,
                             factor_args=FactorArguments(strategy=strategy))
3. analyzer.compute_pairwise_scores(scores_name=strategy, factors_name=strategy,
                                     query_dataset=query_loader.dataset,
                                     train_dataset=train_loader.dataset)
4. scores = analyzer.load_pairwise_scores(strategy)["all_modules"]  # [n_query, n_train]
5. return scores.numpy()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | kronfluence Task subclass | compute_train_loss / compute_measurement for seq classification |
| L-3-2 | fit_ekfac_factors | 4-strategy factor fitting |
| L-3-3 | compute_ekfac_scores | pairwise scoring per strategy |
| L-3-4 | run_ekfac_strategy_ablation | loop strategies, collect scores dict |

---

## A-4: TracIn Attribution [Complexity: 12]

**Applied:** TracIn gradient dot-product across checkpoints (captum `TracInCP`-style, manual grad dot fallback).

### API Signatures

```python
# tracin_attribution.py
def compute_tracin_scores(model: nn.Module, checkpoint_paths: list[str], query_loader: DataLoader,
                           train_loader: DataLoader, lr: float, device: str) -> np.ndarray:
    """Sum_t lr * <grad(query), grad(train)> over checkpoints. Returns [n_query, n_train]."""

def run_checkpoint_count_ablation(model: nn.Module, checkpoint_paths: list[str], query_loader: DataLoader,
                                   train_loader: DataLoader, lr: float, device: str,
                                   counts: list[int]) -> dict[int, np.ndarray]:
    """{n_ckpts: scores} using first n_ckpts of checkpoint_paths (in training order)."""
```

### Pseudo-code

```
1. scores = zeros(n_query, n_train)
2. for ckpt_path in checkpoint_paths:
3.     model = load_checkpoint(model, ckpt_path, device)  # h-m2 signature
4.     for q_batch in query_loader: grad_q = per-example grad of loss wrt params  # flatten to [Bq, P]
5.     for t_batch in train_loader: grad_t = per-example grad of loss wrt params  # flatten to [Bt, P]
6.     scores += lr * (grad_q @ grad_t.T)
7. return scores
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | per-example gradient extraction | vmap/loop-based grad, flatten last-layer or full params |
| L-4-2 | compute_tracin_scores | checkpoint loop + dot product accumulation |
| L-4-3 | run_checkpoint_count_ablation | vary 1/2/3 checkpoints |
| L-4-4 | memory-safe batching | chunk query x train pairs to avoid OOM |

---

## A-5: TRAK Attribution [Complexity: 14]

**Applied:** traker `TRAKer` featurize/score/finalize workflow (random JL projection).

### API Signatures

```python
# trak_attribution.py
def compute_trak_scores(model: nn.Module, task: str, train_loader: DataLoader, query_loader: DataLoader,
                         proj_dim: int, seed: int, train_set_size: int) -> np.ndarray:
    """Returns [n_query, n_train] TRAK scores for one seed/proj_dim."""

def run_trak_seed_ensemble(model: nn.Module, task: str, train_loader: DataLoader, query_loader: DataLoader,
                            proj_dim: int, seeds: list[int], train_set_size: int) -> list[np.ndarray]:
    """List of scores[n_query, n_train] per seed, for cross-seed rank correlation."""

def run_proj_dim_ablation(model: nn.Module, task: str, train_loader: DataLoader, query_loader: DataLoader,
                           seeds: list[int], proj_dims: list[int], train_set_size: int) -> dict[int, np.ndarray]:
    """{proj_dim: mean_scores_over_seeds[n_query, n_train]}."""
```

### Pseudo-code

```
1. traker = TRAKer(model=model, task=task, train_set_size=train_set_size,
                    proj_dim=proj_dim, save_dir=..., device=device)
2. traker.load_checkpoint(model.state_dict(), model_id=0)
3. for batch in train_loader: traker.featurize(batch=(input_ids, attn, labels), num_samples=len(batch))
4. traker.finalize_features()
5. traker.start_scoring_checkpoint(exp_name=f"seed{seed}", checkpoint=model.state_dict(), model_id=0, num_targets=len(query_loader.dataset))
6. for batch in query_loader: traker.score(batch=..., num_samples=len(batch))
7. scores = traker.finalize_scores(exp_name=f"seed{seed}")  # [n_train, n_query] -> transpose
8. return scores.T
```

### Subtasks [3/3 used — reduced from 4 to fit budget]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | TRAK ModelOutput/task wrapper | featurize/score functions for seq classification |
| L-5-2 | compute_trak_scores + run_trak_seed_ensemble | single-run + multi-seed loop |
| L-5-3 | run_proj_dim_ablation | vary proj_dim, average over seeds |

---

## A-6: Cross-Method Metrics [Complexity: 7]

**Applied:** sklearn `roc_auc_score` + scipy `spearmanr`.

### API Signatures

```python
# metrics.py
def compute_mislabeled_auc(influence_scores: np.ndarray, mislabeled_indices: list[int], n_train: int) -> float:
    """influence_scores: [n_query, n_train] or [n_train] aggregate. AUC of |score| detecting mislabeled_indices."""

def compute_rank_correlation(score_list: list[np.ndarray]) -> float:
    """Avg pairwise Spearman rho over score_list (e.g. TRAK seeds)."""

def compute_relative_arch_diff(bert_auc: float, gpt2_auc: float) -> float:
    """|bert_auc - gpt2_auc| / max(bert_auc, gpt2_auc)."""
```

### Pseudo-code

```
compute_mislabeled_auc:
1. agg = mean(abs(influence_scores), axis=0) if influence_scores.ndim==2 else influence_scores  # [n_train]
2. y_true = zeros(n_train); y_true[mislabeled_indices] = 1
3. return roc_auc_score(y_true, agg)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | compute_mislabeled_auc | score aggregation + roc_auc_score |
| L-6-2 | compute_rank_correlation | pairwise spearmanr, average |
| L-6-3 | compute_relative_arch_diff | relative diff formula |
| L-6-4 | Aggregate results dict builder | {method: {arch: auc}} for verify/visualize |

---

## A-7: Ablation A1 — TRAK proj dim [Complexity: 8]

Uses `run_proj_dim_ablation` (A-5). Compute AUC per proj_dim via `compute_mislabeled_auc`; compute variance across seeds via `np.var` on `run_trak_seed_ensemble` outputs.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Run TRAK at 1024/2048/4096 | call run_proj_dim_ablation |
| L-7-2 | AUC per proj_dim | compute_mislabeled_auc per dim |
| L-7-3 | Variance across seeds | np.var(stack(seed_scores), axis=0).mean() |
| L-7-4 | Record to results dict | {proj_dim: {auc, variance}} |

---

## A-8: Ablation A2 — TracIn checkpoints [Complexity: 7]

Uses `run_checkpoint_count_ablation` (A-4). AUC per checkpoint count via `compute_mislabeled_auc`.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Run TracIn 1/2/3 ckpts | run_checkpoint_count_ablation |
| L-8-2 | AUC per count | compute_mislabeled_auc |
| L-8-3 | Signal magnitude comparison | mean(abs(scores)) per count |
| L-8-4 | Record to results dict | {n_ckpts: {auc, signal}} |

---

## A-9: Ablation A3 — EK-FAC strategy [Complexity: 8]

Uses `run_ekfac_strategy_ablation` (A-3). AUC per strategy via `compute_mislabeled_auc`.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | Run identity/diagonal/kfac/ekfac | run_ekfac_strategy_ablation |
| L-9-2 | AUC per strategy | compute_mislabeled_auc |
| L-9-3 | Compare vs full ekfac baseline | relative AUC delta |
| L-9-4 | Record to results dict | {strategy: {auc}} |

---

## A-10: Gate Verification [Complexity: 5]

### API Signatures

```python
# verify.py
def verify_gate(results: dict, threshold: float = 0.10) -> dict:
    """results: {method: {"bert": auc, "gpt2": auc}} for ekfac/tracin/trak.
    Returns {"pass": bool, "per_method_diff": {method: rel_diff}, "max_diff": float, "max_method": str}."""
```

### Pseudo-code

```
1. diffs = {m: compute_relative_arch_diff(r["bert"], r["gpt2"]) for m, r in results.items()}
2. gate_pass = any(d > threshold for d in diffs.values())
3. return {"pass": gate_pass, "per_method_diff": diffs, "max_diff": max(diffs.values()), "max_method": argmax}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-10-1 | Build results dict from A-6 outputs | {ekfac,tracin,trak}x{bert,gpt2} AUCs |
| L-10-2 | verify_gate implementation | per-method diff + any>threshold |
| L-10-3 | Compare vs PRD expected direction | GPT-2>BERT for ekfac, BERT>=GPT-2 for tracin |
| L-10-4 | Write gate result to results.yaml | pass/fail + diffs |

---

## A-11: Visualization Suite [Complexity: 9]

### API Signatures

```python
# visualize.py
def plot_gate_comparison(results: dict, out_path: str) -> None:
    """6-bar chart: 3 methods x 2 archs, AUC on y-axis. REQUIRED."""

def plot_quality_heatmap(results: dict, out_path: str) -> None:
    """method x arch heatmap of AUC."""

def plot_score_distributions(score_dict: dict[str, np.ndarray], out_path: str) -> None:
    """Violin plots of influence score distributions per method."""

def plot_rank_correlation_matrix(corr_matrix: np.ndarray, method_names: list[str], out_path: str) -> None: ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-11-1 | plot_gate_comparison | required 6-bar chart |
| L-11-2 | plot_quality_heatmap | seaborn heatmap |
| L-11-3 | plot_score_distributions | violin via seaborn.violinplot |
| L-11-4 | plot_rank_correlation_matrix | TRAK cross-seed + cross-method corr |

---

## A-12: Orchestration + Reporting [Complexity: 6]

### API Signatures

```python
# run_experiment.py
def main() -> None:
    """Load SST-2 -> inject 5% mislabels -> finetune BERT & GPT-2 w/ epoch ckpts ->
    per-arch: EK-FAC/TracIn/TRAK scores -> mislabeled AUC -> ablations A1-A3 ->
    verify_gate -> figures -> results.yaml."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-12-1 | Pipeline wiring | call all modules in sequence per PRD FR-1..FR-6 |
| L-12-2 | results dict assembly | nested {method:{arch:auc}}, ablations, gate |
| L-12-3 | results.yaml writer | yaml.safe_dump |
| L-12-4 | Figure generation calls | invoke all 4 visualize.py functions |
