# Experiment Design: H-M3

**Date:** 2026-08-05
**Author:** Anonymous
**Hypothesis Statement:** Under the EquiSSL setting trained on SANE MultiZoo, if contrastive autoencoder training (NT-Xent + MSE reconstruction, λ=best validated) is applied, then the resulting latent space enables functional model interpolation: decoded midpoint model (z = (zA + zB)/2, then decode to weights via graph decoder) achieves higher task accuracy than naive weight-space averaging ((θA + θB)/2), averaged over 500+ MLP pairs from the training zoo (p < 0.05, paired t-test).
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (SHOULD_WORK) Template** — Tests generative quality of EquiSSL latent space. Reuses EquiSSL model from H-E1/M1. No new encoder training required.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** H-M2 COMPLETED (DOCUMENT — scale equivariance does not improve over perm-only; EquiSSL R²=0.1846, EquiSSL-perm R²=0.3274, ΔR²=−0.1428). Pipeline continues.
**Gate Status:** SHOULD_WORK — latent midpoint decoded model > weight-space average (p < 0.05, 500+ MLP pairs); DOCUMENT if fails, continue to H-M4

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M2 (COMPLETED, DOCUMENT)

### Gate Condition
SHOULD_WORK: Mean accuracy(latent interpolation via EquiSSL decoder) > mean accuracy(weight-space averaging), p < 0.05 by paired t-test over 500+ MLP checkpoint pairs from SANE MultiZoo training data.

**Failure response:** DOCUMENT as scope limitation — contrastive training does not create functional latent geometry for model interpolation; P3 is disconfirmed. Continue to H-M4. Do NOT stop pipeline.

---

## Continuation Context

**Previous Hypothesis Chain:** H-E1 → H-M1 → H-M2 → H-M3 (current)

**Established Results:**
- H-E1 PASS: MMD ratio = 2.575 (EquiSSL reduces architectural distribution shift; λ=0.1 best)
- H-M1 PASS: EquiSSL R²=0.210, EquiSSL-perm R²=0.231, SANE R²=0.072 on ViT zoo (graph encoders >> SANE)
- H-M2 DOCUMENT: ΔR²=−0.1428 (scale equivariance does NOT improve over permutation-only; LayerNorm in ViTs removes scale gauge freedom)

**Key carryover for H-M3:**
- EquiSSL encoder + graph decoder checkpoint: `docs/youra_research/h-e1/checkpoints/seed0` (λ=0.1, best from H-E1)
- EquiSSL-perm encoder checkpoint: `docs/youra_research/h-m1/checkpoints` (seed 0)
- SANE MultiZoo training data: MLP checkpoint pairs available locally from H-E1/M1 training
- **Note:** H-M3 uses EquiSSL-perm (permutation-only) decoder for interpolation, since H-M2 confirmed EquiSSL-perm achieves higher ViT R² (0.3274 vs 0.1846). This is the stronger baseline and the more interesting interpolation test.

### Previous Hypothesis Results (if applicable)

**H-M2 validation (seed 0):**
- EquiSSL (scale+perm): R² = 0.1846 on ViT zoo
- EquiSSL-perm (perm-only): R² = 0.3274 on ViT zoo
- ΔR² = −0.1428 — scale equivariance is not causally necessary for cross-arch SSL transfer with LayerNorm ViTs
- Finding: permutation equivariance + graph representation suffices; corroborated by arXiv:2510.08300 (LayerNorm removes scale freedom)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1:** "latent space interpolation neural network weights" — No relevant results (diffusers/image generation only; low similarity ~0.46)

**Query 2:** "weight space averaging model merging interpolation" — No relevant results (diffusers image community only; low similarity ~0.46)

**Archon assessment:** Archon KB contains no prior EquiSSL or weight-space interpolation experiments relevant to this hypothesis. All reference implementations sourced from Exa.

### Archon Code Examples

No relevant code examples found (all results from diffusers image pipeline, similarity < 0.44). Not applicable to weight-space autoencoder interpolation.

### Exa GitHub Implementations

**Critical find — odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders (arXiv:2511.12601):**
- ScaleGMN + Neural Graphs autoencoder framework for canonicalizing neural networks
- **Experiment 3 is exactly the interpolation experiment we need:** `analysis/orbit_interpolation.py` and `analysis/orbit_interpolation_ng.py`
- Command: `python analysis/orbit_interpolation.py --conf $MODEL_CONFIG --ckpt $MODEL_WEIGHTS --dataset_size 512 --num_runs 10 --orbit_transformation $INTERPOLATION_TYPE --save_matrices`
- Tests latent space interpolation vs naive weight interpolation (same task we need)
- **Key finding from paper:** Latent space interpolation on functionally identical network pairs performs on par with canonicalized weight space interpolation (Figure 8) — demonstrates latent representations are robust to weight perturbations
- Paper uses INR (Implicit Neural Representation) pairs; we adapt to MLP classifier pairs from SANE MultiZoo

**HSG-AIML/MultiZoo-SANE (arXiv:2504.10141):**
- MLP checkpoint pairs available from SANE MultiZoo (heterogeneous zoo with task metadata)
- Same-task checkpoint pairs: models trained on same dataset/task with varying accuracy levels
- 500+ pairs available from MLP subset of MultiZoo

**HSG-AIML/SANE (ICML 2024):**
- Sequential autoencoder for neural network weights
- Graph decoder reconstructs weight tensors from latent code (token sequence)
- `model_sampling.py` provides weight generation from latent codes (interpolation by construction)

**ModelZoos/ModelZooDataset (NeurIPS 2022):**
- Original model zoo dataset: MLP models trained on MNIST, SVHN, CIFAR-10 with varying hyperparameters
- Each model has accuracy label + task label → enables same-task pair selection

**Schürholt et al. NeurIPS 2022 (Hyper-Representations as Generative Models):**
- Weight sampling from hyper-representations via latent space interpolation
- Layer-wise loss normalization key for stable generation
- Demonstrates interpolation in hyper-rep space produces performant models

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-M3 is a new experiment (not reproducing existing paper) combining:
1. EquiSSL encoder+decoder from H-E1 (already implemented locally in `docs/youra_research/h-e1/code/`)
2. Interpolation logic adapted from `odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders`

**Recommended Implementation Path:**
- Primary: Reuse EquiSSL-perm encoder+decoder from H-M1 codebase (`docs/youra_research/h-m1/code/`) + new interpolation script
- Fallback: Adapt `analysis/orbit_interpolation_ng.py` from `odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders` to SANE MultiZoo MLP pairs
- Justification: EquiSSL-perm achieved higher R² than EquiSSL (H-M2 result); interpolation test should use the stronger model. The odyboufalaki repo provides exact interpolation script template.

### Code Analysis (Serena MCP)

Serena MCP not invoked — H-M3 does not require analysis of external codebase. The implementation reuses existing code from H-E1/M1 with a new interpolation evaluation script. Serena would add no value here.

---

## Experiment Specification

### Dataset

**Name:** SANE MultiZoo — MLP subset, same-task checkpoint pairs
**Version/Source:** HSG-AIML/MultiZoo-SANE (arXiv:2504.10141); ModelZoos/ModelZooDataset (NeurIPS 2022)
**Type:** standard (real MLP checkpoints from public model zoo)
**NOT synthetic** — these are real trained MLP classifiers from the SANE MultiZoo training data

**Dataset details:**
- Source zoo: SANE MultiZoo MLP subset — models trained on MNIST, SVHN, CIFAR-10 (same tasks used in H-E1/M1 training)
- Pair selection criterion: Same task (same dataset + same architecture), different accuracy (θ_A, θ_B from distinct training runs)
- Pair count: **500+ pairs** (statistically meaningful; full available pairs from MLP portion of training zoo)
- Evaluation benchmark: Each MLP pair evaluated on its task test set (MNIST/SVHN/CIFAR-10 test split)
- Splits: No train/test split for dataset itself — use all available same-task pairs; encoder/decoder already trained (frozen)
- Already cached locally from H-E1/M1 training: `docs/youra_research/h-e1/code/data/`

**Pair sampling strategy:**
- Filter training zoo by (task, architecture) groups
- Within each group, enumerate all unique unordered pairs (θ_A, θ_B) where θ_A ≠ θ_B
- Randomly sample to reach 500+ pairs, stratified across tasks (MNIST/SVHN/CIFAR-10)
- Record: task_id, accuracy_A, accuracy_B, model_path_A, model_path_B

**Loading Information** (for Phase 4 download):
- Method: Local filesystem (already cached from H-E1/M1)
- Identifier: `docs/youra_research/h-e1/code/data/` — MultiZoo MLP checkpoints
- Code:
```python
import os, itertools, random
from pathlib import Path

def load_mlp_pairs(zoo_dir, min_pairs=500, seed=42):
    random.seed(seed)
    pairs = []
    # Group by task
    tasks = {}
    for f in Path(zoo_dir).rglob("*.pt"):
        meta = load_meta(f)  # task, accuracy from accompanying .json
        task = meta['task']
        tasks.setdefault(task, []).append((f, meta['accuracy']))
    # Build pairs within same task
    for task, models in tasks.items():
        for (p_a, acc_a), (p_b, acc_b) in itertools.combinations(models, 2):
            pairs.append({'task': task, 'path_a': p_a, 'acc_a': acc_a,
                          'path_b': p_b, 'acc_b': acc_b})
    random.shuffle(pairs)
    return pairs[:max(min_pairs, len(pairs))]
```

### Models

#### Baseline Model

**Weight-space averaging baseline:**
- Method: θ_avg = (θ_A + θ_B) / 2 (naive linear interpolation in parameter space)
- No encoder/decoder involved
- Evaluation: load θ_avg into MLP architecture; evaluate on task test set → accuracy_ws_avg

**This is not a learned model** — it is a deterministic operation on raw weights. No loading required.

**Loading Information** (for Phase 4 download):
- Method: Computed in-memory from loaded checkpoint pair
- Identifier: Same checkpoints as dataset
- Code:
```python
def weight_space_average(state_dict_a, state_dict_b):
    avg = {}
    for key in state_dict_a:
        avg[key] = (state_dict_a[key] + state_dict_b[key]) / 2.0
    return avg
```

#### Proposed Model

**Architecture:** EquiSSL-perm encoder (neural-graphs, permutation-equivariant) + MLP graph decoder → latent midpoint → decoded weights

**Why EquiSSL-perm over EquiSSL:** H-M2 result (R²=0.3274 > 0.1846). EquiSSL-perm produces better-structured latent space for MLP+CNN-trained zoo; also the interpolation test measures functional geometry quality independent of cross-arch transfer.

**Core Mechanism Implementation:**

```python
import torch
from torch_geometric.data import Batch

def encode_model(encoder, checkpoint_path, device):
    """Encode a single MLP checkpoint into latent z."""
    state_dict = torch.load(checkpoint_path, map_location=device)
    graph = weights_to_graph(state_dict)  # reuse H-M1 graph construction
    graph = graph.to(device)
    with torch.no_grad():
        z = encoder(graph)  # shape: [latent_dim]
    return z

def latent_midpoint_decode(encoder, decoder, path_a, path_b, device):
    """Core H-M3 mechanism: encode pair, average in latent, decode to weights."""
    z_a = encode_model(encoder, path_a, device)
    z_b = encode_model(encoder, path_b, device)
    z_mid = (z_a + z_b) / 2.0           # midpoint in latent space
    with torch.no_grad():
        weights_decoded = decoder(z_mid)  # decode back to weight tensors
    return weights_from_decoder_output(weights_decoded)  # reuse H-M1 decoder utils

def weight_space_average(state_dict_a, state_dict_b):
    """Baseline: naive linear interpolation in parameter space."""
    return {k: (state_dict_a[k] + state_dict_b[k]) / 2.0 for k in state_dict_a}

def evaluate_model_accuracy(state_dict, task, test_loader, device):
    """Load weights into MLP architecture and measure test accuracy."""
    model = MLP(task_config[task]).to(device)
    model.load_state_dict(state_dict)
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            pred = model(x).argmax(dim=1)
            correct += (pred == y).sum().item()
            total += len(y)
    return correct / total

def run_interpolation_experiment(encoder, decoder, pairs, test_loaders, device):
    """Main loop: evaluate both methods on 500+ pairs."""
    results = []
    for pair in pairs:
        sd_a = torch.load(pair['path_a'], map_location=device)
        sd_b = torch.load(pair['path_b'], map_location=device)
        # Method 1: latent space interpolation
        sd_latent = latent_midpoint_decode(encoder, decoder, pair['path_a'], pair['path_b'], device)
        acc_latent = evaluate_model_accuracy(sd_latent, pair['task'],
                                             test_loaders[pair['task']], device)
        # Method 2: weight-space averaging
        sd_ws = weight_space_average(sd_a, sd_b)
        acc_ws = evaluate_model_accuracy(sd_ws, pair['task'],
                                          test_loaders[pair['task']], device)
        results.append({
            'pair_id': pair['id'], 'task': pair['task'],
            'acc_latent': acc_latent, 'acc_ws': acc_ws,
            'delta': acc_latent - acc_ws
        })
    return results
```

### Training Protocol

**No new training required.** H-M3 is a pure evaluation experiment using frozen EquiSSL-perm encoder+decoder from H-M1.

**Setup:**
- Load frozen EquiSSL-perm checkpoint: `docs/youra_research/h-m1/checkpoints/equissl_perm_seed0.pt`
- Load frozen graph decoder: `docs/youra_research/h-e1/checkpoints/decoder_seed0.pt` (from H-E1 contrastive autoencoder training)
- Both encoder and decoder in `.eval()` mode; no gradient computation

**Computational budget:**
- 500+ pair evaluations × 2 methods × ~0.1s per model eval = ~100-200 seconds total
- No GPU training; CPU-feasible for MLP inference; GPU optional for speed

**Pair sampling:** Fixed seed=42 for reproducibility. All 500+ pairs sampled before evaluation loop begins.

**Statistical analysis:**
- Primary: paired t-test on (acc_latent − acc_ws) across all pairs
- Report: mean(Δacc), std(Δacc), t-statistic, p-value
- Effect size: Cohen's d = mean(Δacc) / std(Δacc)
- Breakdown by task: MNIST / SVHN / CIFAR-10 subgroup results

### Evaluation

**Primary metric:** Mean accuracy difference: mean(acc_latent − acc_ws) over 500+ pairs

**Gate condition:** mean(Δacc) > 0 AND p < 0.05 by paired t-test → PASS (SHOULD_WORK)
- Fail condition: mean(Δacc) ≤ 0 OR p ≥ 0.05 → DOCUMENT (pipeline continues to H-M4)

**Secondary metrics:**
1. Effect size: Cohen's d ≥ 0.2 (small effect) preferred for publishable claim
2. Task breakdown: % pairs where latent interpolation beats weight-space average (should be > 50%)
3. Accuracy of interpolated models vs parent model accuracy (latent midpoint accuracy vs min(acc_A, acc_B))

**Success criteria (PoC — direction-based, no statistical tests beyond p<0.05):**
- Primary: mean(Δacc) > 0 with p < 0.05 paired t-test over 500+ pairs
- Secondary: mean accuracy improvement > 1% absolute (meaningful functional difference)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Classification accuracy (top-1) on task test sets
- Library: `scipy.stats.ttest_rel` for paired t-test; `sklearn.metrics.accuracy_score` or manual
- Code:
```python
from scipy.stats import ttest_rel
import numpy as np

def compute_statistics(results):
    deltas = np.array([r['delta'] for r in results])
    t_stat, p_value = ttest_rel(
        [r['acc_latent'] for r in results],
        [r['acc_ws'] for r in results]
    )
    cohen_d = deltas.mean() / deltas.std()
    return {
        'mean_delta': deltas.mean(),
        'std_delta': deltas.std(),
        'n_pairs': len(deltas),
        't_statistic': t_stat,
        'p_value': p_value,
        'cohen_d': cohen_d,
        'pct_pairs_positive': (deltas > 0).mean()
    }
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing mean accuracy of latent interpolation vs weight-space averaging across all 500+ pairs, with error bars (std), and annotated p-value

#### Additional Figures (LLM Autonomous)

1. **Task-stratified results:** Bar chart of mean Δacc broken down by MNIST / SVHN / CIFAR-10 — reveals whether latent geometry advantage is task-specific
2. **Pair accuracy scatter:** Scatter plot of (acc_A, acc_B) pairs colored by Δacc sign — shows whether improvement is concentrated in high/low accuracy pairs
3. **Δacc distribution histogram:** Distribution of per-pair accuracy differences with vertical line at 0 — visualizes effect size
4. **Latent space quality:** t-SNE of EquiSSL-perm latent codes for MLP training zoo, colored by task accuracy — confirms smooth latent structure enabling interpolation

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/h-m3/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (encoder, decoder, interpolation, evaluation all complete)
2. `mean(acc_latent) > mean(acc_ws)` across 500+ pairs (direction confirmed)
3. p < 0.05 by paired t-test

**DOCUMENT condition (not a failure — pipeline continues):**
- mean(acc_latent) ≤ mean(acc_ws) OR p ≥ 0.05
- Document as: "NT-Xent contrastive training does not create functional latent geometry for MLP interpolation in this setting; prediction P3 disconfirmed"
- H-M4 proceeds regardless

---

## Appendix: Reference Implementations

### 1. odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders (arXiv:2511.12601)
- **Relevance:** Direct implementation of ScaleGMN/NeuralGraphs autoencoder + latent interpolation experiment
- **Key files:** `analysis/orbit_interpolation.py`, `analysis/orbit_interpolation_ng.py`
- **Adaptation needed:** Replace INR pairs with SANE MultiZoo MLP classifier pairs; replace reconstruction loss metric with task accuracy metric
- **Key insight from paper:** Latent space interpolation with MLP decoder (linear cost) performs on par with weight-space interpolation for functionally identical INR pairs

### 2. HSG-AIML/SANE (ICML 2024)
- **Relevance:** SANE uses sequential autoencoder with weight generation from latent codes — interpolation is a natural use case
- **Key insight:** SANE demonstrates weight generation (not just compression); interpolation in latent space produces valid weight tensors

### 3. Schürholt et al. NeurIPS 2022 (Hyper-Representations as Generative Models)
- **Relevance:** Establishes that interpolation in hyper-representation latent space produces performant models
- **Key method:** Layer-wise loss normalization + latent interpolation → new model weights that outperform weight-space averaging for ensemble/initialization
- **Direct precedent for H-M3:** This is the conceptual foundation for expecting latent-midpoint-decoded models to outperform naive weight averaging

### 4. ModelZoos/ModelZooDataset (NeurIPS 2022 D&B track)
- **Relevance:** Original source of MLP checkpoint pairs with task metadata (accuracy, task label, architecture)
- Pairs can be constructed from same-task MLP models with distinct random seeds/hyperparameters

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-05

### Workflow History for This Hypothesis

- H-M2 DOCUMENT result confirmed pipeline continuation to H-M3
- H-M3 experiment design initiated: 2026-08-05T14:27:27Z
- MCP searches: Archon (4 queries, no relevant results — diffusers/image only), Exa (4 searches, 6 key repos found)
- Key implementation reference identified: odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders (arXiv:2511.12601)

---

*MCP Tools Used: Archon (Knowledge + Code, 4 queries, no relevant results), Exa (GitHub + Web, 4 searches, 6 repos found)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
