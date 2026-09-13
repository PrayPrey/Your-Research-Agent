# Product Requirements Document: H-M3
# Latent Space Interpolation via EquiSSL-perm Decoder

**Hypothesis ID:** H-M3
**Type:** MECHANISM (PoC)
**Date:** 2026-08-05
**Author:** Anonymous
**Phase:** 3 Implementation Planning

---

## stepsCompleted
- [x] Step 1: Problem Statement
- [x] Step 2: Functional Requirements
- [x] Step 3: Data Specification
- [x] Step 4: Evaluation Protocol
- [x] Step 5: Dependencies
- [x] Step 6: Success Criteria
- [x] Step 7: Non-Functional Requirements

---

## 1. Executive Summary

H-M3 tests whether the EquiSSL-perm latent space (trained in H-M1) enables functional model interpolation. The core claim: decoding the latent midpoint z_mid = (z_A + z_B) / 2 via the graph decoder produces an MLP checkpoint with higher task accuracy than naive weight-space averaging θ_avg = (θ_A + θ_B) / 2, measured over 500+ MLP checkpoint pairs from the SANE MultiZoo training data.

**No new training required.** H-M3 is a pure evaluation experiment using frozen EquiSSL-perm encoder + graph decoder from H-M1/H-E1.

Key tasks:
1. Load frozen EquiSSL-perm encoder (H-M1) and graph decoder (H-E1)
2. Build 500+ same-task MLP pair dataset from SANE MultiZoo training zoo
3. For each pair: encode both models, compute latent midpoint, decode to weights
4. For each pair: compute weight-space average (baseline)
5. Evaluate both methods on task test sets (MNIST/SVHN/CIFAR-10 accuracy)
6. Statistical analysis: paired t-test, Cohen's d, task-stratified breakdown
7. Visualizations: gate metric bar chart + 3 additional figures

Gate (SHOULD_WORK): mean(acc_latent) > mean(acc_ws) AND p < 0.05 by paired t-test over 500+ pairs. Failure: DOCUMENT as scope limitation, continue to H-M4.

---

## 2. Problem Statement

H-M1 and H-M2 established that EquiSSL-perm (permutation-equivariant graph encoder + decoder) achieves R²=0.3274 on ViT zoo property prediction — the strongest embedding structure in the pipeline. H-M3 probes a qualitatively different capability: does this structured latent space support *generative* model interpolation?

Weight-space averaging is known to produce poor-performing models when model symmetries are not aligned (permutation mismatch). Latent-space interpolation via an equivariant encoder — which canonicalizes model representations before embedding — may bypass this alignment problem, producing midpoint decoded models that retain functional accuracy.

**Prior art:** Schürholt et al. (NeurIPS 2022) showed hyper-representation interpolation beats weight-space averaging for model initialization. H-M3 tests the analogous claim for EquiSSL-perm latent space on MLP classifier pairs.

Gate condition (SHOULD_WORK): mean(acc_latent) > mean(acc_ws) with p < 0.05. If fails: DOCUMENT — contrastive training does not create functional latent geometry for MLP interpolation; continue to H-M4.

---

## 3. Functional Requirements

### FR-1: Frozen Model Loading
Load frozen EquiSSL-perm encoder and graph decoder from H-M1/H-E1 checkpoints.
- **Encoder:** `docs/youra_research/h-m1/checkpoints/equi_perm_seed0.pt` (EquiSSL-perm, permutation-equivariant)
- **Decoder:** `docs/youra_research/h-e1/checkpoints/decoder_seed0.pt` (graph decoder from H-E1 contrastive autoencoder)
- Both in `.eval()` mode; no gradient computation
- Device: GPU if available, CPU fallback

### FR-2: MLP Pair Dataset Construction
Build 500+ same-task MLP checkpoint pairs from SANE MultiZoo training data.
- Source: `docs/youra_research/h-e1/code/data/` — MultiZoo MLP checkpoints (already cached from H-E1/M1 training)
- Tasks: MNIST, SVHN, CIFAR-10 (same tasks used in H-E1/M1 training)
- Pair selection: same task + same architecture, different training runs (distinct θ_A, θ_B)
- Pair count: **500+ pairs** — enumerate all unique unordered pairs within each (task, architecture) group; sample to 500+ stratified across tasks
- Reproducibility: fixed seed=42 for pair sampling
- Record per pair: task_id, path_a, path_b, accuracy_a, accuracy_b
- Output: `h-m3/data/mlp_pairs.json` (500+ entries)

### FR-3: Latent Interpolation Method (Proposed)
For each MLP pair (θ_A, θ_B):
1. Load checkpoints as state_dicts
2. Convert each to graph representation using H-M1 graph construction (`weights_to_graph`)
3. Encode both via EquiSSL-perm encoder: z_A = encoder(graph_A), z_B = encoder(graph_B)
4. Compute latent midpoint: z_mid = (z_A + z_B) / 2.0
5. Decode via graph decoder: θ_decoded = decoder(z_mid)
6. Evaluate on task test set → acc_latent

### FR-4: Weight-Space Averaging Baseline
For each MLP pair (θ_A, θ_B):
1. Load both state_dicts
2. Compute: θ_avg[k] = (θ_A[k] + θ_B[k]) / 2.0 for all keys k
3. Load into MLP architecture matching task config
4. Evaluate on task test set → acc_ws

### FR-5: Task Accuracy Evaluation
For each generated checkpoint (latent-interpolated and weight-space-averaged):
- Load weights into matching MLP architecture (task-specific input/output dims)
- Evaluate on full task test sets: MNIST (10k), SVHN (26k), CIFAR-10 (10k)
- Metric: top-1 accuracy (correct / total)
- Test data: load standard test splits from torchvision (no preprocessing beyond what training used)

### FR-6: Statistical Analysis
Compute and report:
- `delta = acc_latent - acc_ws` per pair
- **Primary:** `scipy.stats.ttest_rel(acc_latent_list, acc_ws_list)` → t-statistic, p-value
- **Effect size:** Cohen's d = mean(delta) / std(delta)
- **Direction:** % pairs where acc_latent > acc_ws
- **Task breakdown:** mean(delta) per task (MNIST / SVHN / CIFAR-10)
- **Accuracy vs parent:** mean(acc_latent) vs mean(min(acc_A, acc_B)) — does decoded model exceed weaker parent?
- Save results: `h-m3/results/hm3_results.json`

### FR-7: Visualization (4 Figures)
Save all figures to `h-m3/figures/`:
1. **Gate Metrics Comparison (MANDATORY):** Bar chart — mean accuracy of latent interpolation vs weight-space averaging across all 500+ pairs, with error bars (std), annotated p-value and gate result
2. **Task-stratified results:** Bar chart of mean Δacc broken down by MNIST / SVHN / CIFAR-10
3. **Δacc distribution histogram:** Distribution of per-pair accuracy differences with vertical line at 0 and annotated mean
4. **Pair accuracy scatter:** Scatter plot of (acc_A, acc_B) colored by Δacc sign — shows whether improvement concentrates in high/low accuracy pairs

### FR-8: Ablation Variants (Required)
Both methods MUST be evaluated:
1. **Latent interpolation (proposed):** EquiSSL-perm encoder → latent midpoint → graph decoder → task accuracy
2. **Weight-space averaging (baseline):** θ_avg = (θ_A + θ_B) / 2 → task accuracy

No additional ablation variants needed (single encoder checkpoint, no λ sweep).

### FR-9: Results Report
Generate `h-m3/04_validation.md` with:
- Summary: n_pairs, tasks, gate result
- Table: mean ± std accuracy for both methods per task and overall
- Statistical results: t-statistic, p-value, Cohen's d, % pairs positive
- Gate evaluation: PASS or DOCUMENT with interpretation
- Figure references
- Conclusion: does EquiSSL-perm latent space enable functional model interpolation?

---

## 4. Data Specification

### 4.1 MLP Checkpoint Pairs (Primary Dataset)
| Property | Value |
|----------|-------|
| Name | SANE MultiZoo MLP subset (same-task pairs) |
| Source | HSG-AIML/MultiZoo-SANE (arXiv:2504.10141); ModelZoos/ModelZooDataset (NeurIPS 2022) |
| Type | standard (real trained MLP classifiers) |
| Size | 500+ pairs (stratified across MNIST/SVHN/CIFAR-10) |
| Download | **REUSE** — already cached: `docs/youra_research/h-e1/code/data/` |
| Status | REUSE — validated in H-E1/H-M1 training |
| Format | PyTorch state_dicts (.pt files) + accompanying .json metadata (task, accuracy) |

### 4.2 Task Test Sets (Evaluation)
| Task | Dataset | Test Size | Source |
|------|---------|-----------|--------|
| MNIST | torchvision.datasets.MNIST | 10,000 | Auto-download (torchvision) |
| SVHN | torchvision.datasets.SVHN | 26,032 | Auto-download (torchvision) |
| CIFAR-10 | torchvision.datasets.CIFAR10 | 10,000 | Auto-download (torchvision) |

### 4.3 Reused Checkpoints
| Model | Path | Status |
|-------|------|--------|
| EquiSSL-perm encoder | `h-m1/checkpoints/equi_perm_seed0.pt` | Available (H-M1) |
| Graph decoder | `h-e1/checkpoints/decoder_seed0.pt` | Available (H-E1) |

**Note:** If path aliases differ in actual H-M1 code, use Serena/grep to find the actual checkpoint filename.

---

## 5. Evaluation Protocol

### 5.1 Primary Metric
- **Mean Δacc** = mean(acc_latent − acc_ws) over 500+ pairs
- Reported: mean, std, 95% CI

### 5.2 Statistical Test
- Paired t-test: `scipy.stats.ttest_rel(acc_latent_list, acc_ws_list)`
- Report: t-statistic, p-value (two-tailed)
- Gate threshold: p < 0.05 AND mean(Δacc) > 0

### 5.3 Gate Evaluation
| Outcome | Condition | Action |
|---------|-----------|--------|
| PASS | mean(Δacc) > 0 AND p < 0.05 | EquiSSL-perm latent geometry enables functional interpolation |
| DOCUMENT | mean(Δacc) ≤ 0 OR p ≥ 0.05 | "NT-Xent contrastive training does not create functional latent geometry for MLP interpolation; P3 disconfirmed"; continue to H-M4 |

### 5.4 Secondary Metrics
- Effect size: Cohen's d ≥ 0.2 (small effect, publishable)
- % pairs where acc_latent > acc_ws (should be > 50% if gate passes)
- Task-stratified mean Δacc per MNIST / SVHN / CIFAR-10

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- Pair sampling: fixed seed=42
- Deterministic evaluation: torch.no_grad(), model.eval()
- Save pair list to `h-m3/data/mlp_pairs.json` before evaluation loop

### NFR-2: Code Organization (FULL Tier, INCREMENTAL)
- Primary: new script `h-m3/run_hm3.py` reusing H-M1 utilities
- Reuse: `h-m1/code/` graph construction, model loading utilities
- New: interpolation evaluation script (adapted from H-M1 framework)
- Minimal new code — only the interpolation loop and new evaluation harness

### NFR-3: Experiment Scale
- **Minimum 500 MLP pairs** — NOT trivially small samples (10-50 pairs is insufficient for p<0.05)
- Full task test sets (MNIST 10k, SVHN 26k, CIFAR-10 10k) — NOT subsets
- Statistical power: 500+ pairs provides adequate power for paired t-test (Cohen's d ≥ 0.2 detectable at α=0.05, β=0.8)

### NFR-4: Reuse from H-M1/H-E1
- Graph construction: reuse `h-m1/code/data/weights_to_graph.py` (or equivalent)
- Model loading: reuse `h-m1/code/models/` encoder loading utilities
- Decoder loading: reuse `h-e1/code/models/` decoder utilities
- Bug fixes from H-E1/H-M1/H-M2 MUST be applied (check 04_validation.md for known fixes)

### NFR-5: Computational Budget
- 500+ pair evaluations × 2 methods × ~0.1s per MLP eval = ~100-200s total
- No GPU training required; GPU optional for encoder/decoder inference speed
- Pair list construction: ~1 min (enumerate combinations from cached zoo)

---

## 7. Dependencies

### 7.1 Python Packages (Reuse H-M1 Environment)
```
torch>=2.0.1
torch-geometric>=2.3.0
pytorch-scatter
numpy
scikit-learn
scipy
einops
torchvision
matplotlib
seaborn
tqdm
pyyaml
```

### 7.2 External Repositories (Reference)
| Repo | Purpose |
|------|---------|
| odyboufalaki/Symmetry-Aware-Graph-Metanetwork-Autoencoders | Interpolation logic template (orbit_interpolation_ng.py) |
| HSG-AIML/MultiZoo-SANE | MLP checkpoint zoo source |

### 7.3 H-M1/H-E1 Artifacts (Required)
- `h-m1/code/` — graph construction, encoder loading, model utilities
- `h-m1/checkpoints/equi_perm_seed0.pt` — EquiSSL-perm encoder
- `h-e1/checkpoints/decoder_seed0.pt` — graph decoder
- `h-e1/code/data/` — SANE MultiZoo MLP checkpoint cache

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Code runs without error | No exceptions on 500+ pairs | Required |
| 500+ pairs evaluated | n_pairs ≥ 500 | Required |
| Both methods evaluated for all pairs | acc_latent + acc_ws for each pair | Required |
| Paired t-test reported | t-stat, p-value | Required |
| Cohen's d reported | effect size | Required |
| 4 figures generated | Saved to h-m3/figures/ | Required |
| Gate evaluated | PASS or DOCUMENT | Required (SHOULD_WORK) |
| 03_tasks.yaml within budget | ≤ 30 tasks (FULL) | Required |

---

## 9. Out of Scope

- New encoder training (frozen EquiSSL-perm from H-M1 only)
- Multi-seed interpolation experiments (single encoder seed 0)
- Interpolation at points other than α=0.5 (midpoint only)
- Cross-task interpolation (same-task pairs only)
- Extension to ViT checkpoint interpolation (H-M4 scope)
- Hyperparameter tuning for the decoder
