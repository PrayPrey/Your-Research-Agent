# PRD: H-M2 (TC-SSM Low-Rank Task Conditioning)

**Date:** 2026-08-28
**Hypothesis:** Under TC-SSM architecture, if low-rank projections (rank 16-64) modulate Mamba's Δ, B, C matrices based on task embeddings, then state space dynamics will be task-conditioned with <2x overhead.
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## 1. Executive Summary

Validate that low-rank projections (LoRA-style, rank 16-64) can efficiently modulate Mamba SSM's Δ, B, C matrices based on task embeddings from H-M1, achieving task-conditioned state space dynamics with computational overhead below 2x vanilla Mamba.

---

## 2. Problem Statement

Mamba SSMs lack native task-conditioning mechanisms. Adding full-rank task modulation would be prohibitively expensive. This experiment tests whether low-rank projections provide sufficient expressiveness for task conditioning while maintaining computational efficiency.

**Success Criteria:**
- FLOPs overhead < 2.0x vanilla Mamba
- State variance differs significantly across task embeddings (ANOVA p < 0.05)

---

## 3. Functional Requirements

### FR-1: Data Loading
Load SuperGLUE validation subsets (BoolQ: 3,270, RTE: 277, WiC: 638 samples) for forward-pass measurement inputs.

### FR-2: LowRankProjection Module
Implement down-projection (task_emb_dim → rank) and up-projection (rank → target_dim) with near-zero initialization.

### FR-3: VanillaMambaWrapper
Wrap mamba_ssm.Mamba as baseline for overhead comparison.

### FR-4: TaskConditionedMamba Module
Implement Δ/B/C low-rank modulation with:
- Additive modulation (base + task_mod)
- Variant switch (delta_only vs all_matrices)
- get_state() for variance analysis

### FR-5: Load Frozen H-M1 Embeddings
Import TaskEmbeddingEncoder from H-M1 checkpoint, freeze weights.

### FR-6: FLOPs/Overhead Measurement
- count_flops() via torch.profiler
- measure_overhead() wall-clock timing ratio
- per_matrix_breakdown() for Δ/B/C contribution

### FR-7: State Variance Analysis
ANOVA (scipy.stats.f_oneway) across task embeddings to verify state differentiation.

### FR-8: Rank Ablation Framework
- run_rank_ablation(): sweep rank=16/32/64
- run_matrix_ablation(): sweep delta_only vs all_matrices

### FR-9: Visualization
Generate overhead bar chart, rank ablation plot, state variance heatmap, per-matrix pie chart.

### FR-10: Experiment Orchestration
End-to-end runner with gate check (overhead < 2.0x, p < 0.05).

---

## 4. Data Specification

### Primary Dataset
**SuperGLUE (subset)** - Standard HuggingFace version

| Task | Validation Samples | Purpose |
|------|-------------------|---------|
| BoolQ | 3,270 | Binary QA |
| RTE | 277 | Binary NLI |
| WiC | 638 | Word sense |

**Total:** 4,185 samples across 3 tasks

### Loading
```python
from datasets import load_dataset
tasks = ['boolq', 'rte', 'wic']
datasets = {task: load_dataset('super_glue', task)['validation'] for task in tasks}
```

Auto-download via HuggingFace - no manual data preparation required.

---

## 5. Model Specification

### Baseline: Vanilla Mamba (mamba-370m)
- d_model: 1024
- d_state: 16
- d_conv: 4
- expand: 2

### Proposed: TC-SSM
- Same base dimensions
- Low-rank modulation: rank ∈ {16, 32, 64}
- Modulation targets: delta_only or all_matrices (Δ, B, C)
- Task embedding input from H-M1 (frozen)

---

## 6. Evaluation Metrics

### Primary Metric
**FLOPs Overhead Ratio:** TC-SSM_time / Vanilla_time
- Threshold: < 2.0x
- Stretch goal: < 1.5x (rank=32)

### Secondary Metrics
- State variance per task (ANOVA F-statistic, p-value)
- Per-matrix overhead breakdown (Δ vs B vs C)
- Rank vs overhead curve

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0
mamba-ssm>=1.0
datasets
scipy
matplotlib
```

### 7.2 External References
- H-M1 checkpoint: TaskEmbeddingEncoder weights
- mamba-ssm: Official Mamba implementation

---

## 8. Ablation Variants

| Variant | What it Tests | Expected Outcome |
|---------|---------------|------------------|
| rank=16 | Minimum rank | ~1.2x overhead, reduced expressiveness |
| rank=32 | Default | ~1.3x overhead, balanced |
| rank=64 | Higher rank | ~1.5x overhead, better modulation |
| delta_only | Single matrix | Lowest overhead, partial conditioning |
| all_matrices | Δ+B+C | Full overhead, complete conditioning |

---

## 9. Success Criteria

### Gate Check (MUST_WORK)
1. `overhead_ratio < 2.0` for default config (rank=32, all_matrices)
2. `state_variance_p_value < 0.05` (states differ by task)

### Stretch Goals
- Overhead < 1.5x with rank=32
- Clear rank-overhead tradeoff curve
