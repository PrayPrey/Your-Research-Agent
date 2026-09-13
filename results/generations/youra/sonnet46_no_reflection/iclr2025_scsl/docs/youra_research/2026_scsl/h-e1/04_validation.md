# Phase 4 Validation Report: h-e1

**Generated:** 2026-05-20T03:30:00
**Execution Mode:** UNATTENDED
**Pipeline Position:** Phase 3 → [Phase 4] → Phase 0 (ROUTED)

---

## Hypothesis Summary

| Field | Value |
|-------|-------|
| **ID** | h-e1 |
| **Type** | EXISTENCE |
| **Gate Type** | MUST_WORK |
| **Final Gate Result** | FAIL |
| **Reflection Outcome** | ROUTED_TO_PHASE_0 |
| **Duration** | ~2 hours (training + extraction + evaluation) |

**Hypothesis Statement:**
> Under spurious-correlation settings (Waterbirds, CelebA) with pretrained ResNet-50 initialization, k-means clustering (k=2) on penultimate-layer embeddings at epoch 5 of ERM training recovers spurious feature axes with AMI>=0.5 and worst-cluster purity>=75% across >=5 random seeds.

---

## Code Generation Summary

### Task Statistics

| Metric | Value |
|--------|-------|
| Total Tasks | 15 |
| Completed | 15 |
| Coder-Validator Cycles | 1/5 |
| SDD-Compliant Tasks | 15 |

### Generated Files

| File | Description |
|------|-------------|
| `code/data/datasets.py` | WaterBirdsDataset, CelebADataset, get_dataloader |
| `code/models/__init__.py` | Models package |
| `code/models/resnet.py` | ERMModel with get_feature_extractor, save/load_checkpoint |
| `code/train.py` | ERM training loop with epoch-5 checkpoint |
| `code/extract.py` | Penultimate-layer embedding extraction |
| `code/cluster.py` | K-means probe, AMI, worst-cluster purity |
| `code/visualize.py` | t-SNE, bar charts, cluster composition figures |
| `code/evaluate.py` | Gate evaluation and results reporting |
| `code/run_experiment.py` | End-to-end orchestration |
| `code/tests/test_datasets.py` | Dataset unit tests |
| `code/tests/test_models.py` | Model unit tests |
| `code/tests/test_cluster.py` | Clustering unit tests |
| `code/tests/test_evaluate.py` | Evaluation unit tests |
| `code/configs/waterbirds.yaml` | Waterbirds experiment config |
| `code/configs/celeba.yaml` | CelebA experiment config |

---

## Code Quality Checklist

- [✓] Syntax validation passed
- [✓] Type hints compliance
- [✓] API signatures match 03_logic.md
- [✓] Test files generated for all modules
- [✓] All 15 tasks completed (IMPL/TEST/VERIFY phases passed)
- [✓] No mock data detected

---

## Experiment Execution

### Training Results

| Dataset | Epochs | Final Loss | Final Acc | Embeddings Shape |
|---------|--------|-----------|-----------|-----------------|
| Waterbirds | 5 | 0.0881 | 96.66% | (4795, 2048) |
| CelebA | 5 | 0.1240 | 95.00% | (162770, 2048) |

### Clustering Results (K-Means k=2, Epoch 5 Penultimate Embeddings)

| Dataset | AMI | Worst-Cluster Purity | AMI Random | Purity Random | Mechanism OK |
|---------|-----|---------------------|------------|---------------|-------------|
| Waterbirds | **0.7622** | **0.8919** | 0.0001 | 0.7276 | ✓ True |
| CelebA | **0.2578** | **0.4557** | -0.0000 | 0.4395 | ✗ False |

---

## Gate Evaluation

| Field | Value |
|-------|-------|
| **Gate Type** | MUST_WORK |
| **Overall Result** | FAIL |
| **Gate Satisfied** | False |
| **AMI Threshold** | >= 0.5 |
| **Purity Threshold** | >= 0.75 |

### Per-Dataset Gate Results

| Dataset | AMI | AMI>=0.5 | Purity | Purity>=0.75 | Dataset Pass |
|---------|-----|---------|--------|-------------|-------------|
| Waterbirds | 0.7622 | ✓ YES | 0.8919 | ✓ YES | ✓ PASS |
| CelebA | 0.2578 | ✗ NO | 0.4557 | ✗ NO | ✗ FAIL |
| **Overall** | | | | | **✗ FAIL** |

---

## Reflection Analysis (Step 6b)

### Gate Type
MUST_WORK — both datasets required to pass. CelebA failure triggers routing.

### Root Cause Analysis

**What Worked (Waterbirds):**
- ERM with pretrained ResNet-50 develops highly separable spurious feature representations by epoch 5
- K-means (k=2) successfully recovers the bird-background spurious direction with AMI=0.762 >> random baseline (0.0001)
- Worst-cluster purity=0.892 confirms clean group separation
- Mechanism clearly activated: spurious-direction clustering is feasible when spurious feature is visually dominant (bird-on-water vs bird-on-land)

**What Failed (CelebA):**
- CelebA AMI=0.258 is above random (-0.000) but well below the 0.5 threshold
- Worst-cluster purity=0.456 is near-random and below the 0.75 threshold
- `mechanism_ok = False`
- Root causes:
  1. **Feature strength asymmetry:** CelebA's spurious correlation (blonde hair ↔ female) is a fine-grained texture feature, much subtler than Waterbirds' habitat background. ERM embeddings at epoch 5 may not have developed sufficiently separable representations for this weaker spurious feature.
  2. **Class imbalance:** CelebA has high class imbalance (~80% non-blonde). K-means with k=2 struggles to separate minority-cluster features when the embedding manifold is dominated by majority-class variance.
  3. **Epoch timing:** The hypothesis specifies epoch 5 as the probe point. For CelebA with its larger dataset (162K samples), epoch 5 may not yet constitute sufficient "early training" for shortcut consolidation to produce cluster-separable spurious features.
  4. **Embedding dimensionality vs. cluster separability:** 2048-dimensional ResNet penultimate embeddings require strong between-group variance to yield clean k-means separation; CelebA spurious groups may not have this structure at epoch 5.

### Reflection Decision

**Outcome: ROUTED_TO_PHASE_0**

The MUST_WORK gate requires the spurious-direction recovery mechanism to function on BOTH datasets. CelebA failure indicates:
- The existence hypothesis is **not universally valid** across spurious-correlation benchmarks
- The failure is not a minor parameter issue (threshold adjustment) — purity=0.456 is far below 0.75
- This is a **fundamental scope issue**: the hypothesis needs to be reconsidered either (a) with a narrowed scope (Waterbirds only), or (b) with a revised mechanism (different probe epoch, different clustering approach, or different embedding layer)

SELF_MODIFY is not appropriate because:
- The modification would require changing the core mechanism (epoch, clustering, or dataset scope) which constitutes a hypothesis-level change
- The gap is too large (purity 0.456 vs 0.75 target) for minor self-recovery

**Action:** Route to Phase 0 for hypothesis redesign incorporating lessons learned.

---

## Next Steps

**Routing: Phase 0 (Brainstorming)**

Based on the CelebA failure, Phase 0 should consider:
1. **Narrow scope:** Hypothesis valid for Waterbirds but not CelebA — could pursue Waterbirds-only variant
2. **Revised probe epoch:** Try later epochs (10, 15, 20) for CelebA where shortcut consolidation may be more advanced
3. **Alternative clustering:** PCA-based directional probing instead of k-means may be more robust to class imbalance
4. **Different layer:** Probe intermediate ResNet layers instead of penultimate for CelebA
5. **Dataset-adaptive threshold:** Different AMI/purity thresholds for different spurious feature strengths

---

## Phase 2C Handoff

### Proven Components (Waterbirds-validated)

| Component | File | Status | Notes |
|-----------|------|--------|-------|
| ERM Training Loop | `train.py` | ✓ Validated | 5-epoch checkpoint, SGD+momentum |
| Embedding Extractor | `extract.py` | ✓ Validated | Penultimate layer, shape (N, 2048) |
| K-means Probe | `cluster.py` | ✓ Validated (Waterbirds) | AMI + worst-cluster purity |
| Waterbirds Dataset | `data/datasets.py` | ✓ Validated | Group metadata correctly loaded |
| ResNet-50 Model | `models/resnet.py` | ✓ Validated | get_feature_extractor works correctly |
| Visualizations | `visualize.py` | ✓ Generated | t-SNE, bar charts, cluster composition |

### Optimal Hyperparameters (Waterbirds)

```yaml
waterbirds:
  model: ResNet-50 (ImageNet pretrained)
  optimizer: SGD
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.001
  batch_size: 32
  probe_epoch: 5
  clustering:
    k: 2
    n_init: 10
    seed: 42
```

### Lessons Learned

**What Worked:**
- Pretrained ResNet-50 ERM on Waterbirds develops strong spurious-direction embeddings early (epoch 5)
- K-means k=2 is effective when spurious feature is visually dominant (habitat background)
- AMI is a robust metric for spurious direction recovery (clearly separates signal from noise)
- Worst-cluster purity correctly identifies near-perfect group separation

**What Didn't Work:**
- CelebA's fine-grained spurious feature (hair color) is not captured by epoch-5 k-means
- Class imbalance (80/20 split) interferes with k-means cluster purity
- Universal AMI>=0.5 / purity>=0.75 thresholds are too strict for heterogeneous datasets

**Key Insight:**
The spurious-direction recovery mechanism is **feature-strength dependent**. Strong, visually dominant spurious features (habitat) are recoverable at epoch 5; subtle, texture-based spurious features (hair color) require either more training or different probe methodology.

### Recommendations for Dependent Hypotheses

**For revised H-E1 (Phase 0 output):**
- Consider dataset-specific thresholds or dataset-specific probe epochs
- Investigate alternative clustering approaches robust to class imbalance (e.g., GMM, spectral clustering)
- Expand to ≥5 seeds to characterize variance across random initializations

**For H-M1 (BLOCKED — prerequisite h-e1 failed):**
- Cannot proceed until H-E1 is validated on both datasets
- If revised H-E1 uses Waterbirds-only scope, H-M1 can proceed with Waterbirds data

---

## Generated Figures

| Figure | Path | Description |
|--------|------|-------------|
| metrics_bar.png | `figures/metrics_bar.png` | AMI and Purity bar chart for both datasets |
| tsne_class_waterbirds.png | `figures/tsne_class_waterbirds.png` | t-SNE colored by class label (Waterbirds) |
| tsne_group_waterbirds.png | `figures/tsne_group_waterbirds.png` | t-SNE colored by group ID (Waterbirds) |
| tsne_cluster_waterbirds.png | `figures/tsne_cluster_waterbirds.png` | t-SNE colored by k-means cluster (Waterbirds) |
| cluster_composition_waterbirds.png | `figures/cluster_composition_waterbirds.png` | Cluster group composition (Waterbirds) |
| tsne_class_celeba.png | `figures/tsne_class_celeba.png` | t-SNE colored by class label (CelebA) |
| tsne_group_celeba.png | `figures/tsne_group_celeba.png` | t-SNE colored by group ID (CelebA) |
| tsne_cluster_celeba.png | `figures/tsne_cluster_celeba.png` | t-SNE colored by k-means cluster (CelebA) |
| cluster_composition_celeba.png | `figures/cluster_composition_celeba.png` | Cluster group composition (CelebA) |

---

## Appendix

### Output Files

| File | Status |
|------|--------|
| `04_validation.md` | ✓ Generated |
| `04_checkpoint.yaml` | ✓ Updated |
| `experiment_results.json` | ✓ Generated |
| `code/results/h-e1/overall_results.json` | ✓ Generated |
| `code/results/h-e1/overall_results.yaml` | ✓ Generated |
| `code/embeddings/h-e1/waterbirds_epoch5.npy` | ✓ Generated |
| `code/embeddings/h-e1/celeba_epoch5.npy` | ✓ Generated |
| `figures/*.png` | ✓ 9 figures generated |

### Checkpoint State

- hypothesis_id: h-e1
- coder_validator_cycles: 1
- tasks_completed: 15/15
- gate_result: FAIL
- reflection_outcome: ROUTED_TO_PHASE_0
- serena_memory: to be written

---

*Phase 4 validation report generated in UNATTENDED mode.*
*Gate: MUST_WORK FAIL → ROUTED_TO_PHASE_0*
