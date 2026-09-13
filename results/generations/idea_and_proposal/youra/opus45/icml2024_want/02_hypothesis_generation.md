# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-EcoParallel-v1
**Confidence Level:** 0.72

**Main Hypothesis:**
Under heterogeneous GPU cluster conditions (A100/V100/T4 mix), if a neural hyper-heuristic dynamically selects parallelism strategies (TP/PP/DP/FSDP) at stage-level granularity (4-6 stages) using ecological-niche-inspired geometric partitioning in 3D feature space [compute_TFLOPS, memory_GB, bandwidth_GB/s], then training throughput will improve by 12-18% compared to static parallelism baselines (pure FSDP, pure TP, or manual hybrid configurations) because:
1. The neural strategy selector learns hardware-workload affinity patterns from proxy model training
2. Geometric partitioning clusters similar device capabilities for optimal assignment
3. Stage-level multi-strategy blending enables fine-grained optimization without excessive synchronization overhead

**Alternative Hypothesis (H0):**
Static parallelism strategies (FSDP, TP, or manual hybrid) achieve equivalent or superior training throughput on heterogeneous GPU clusters compared to neural-selected adaptive strategies, due to:
- H0a: Synchronization overhead at stage boundaries negates any efficiency gains from adaptive selection
- H0b: Neural selector fails to generalize beyond training configurations, producing suboptimal predictions
- H0c: 3D feature space is insufficient to capture hardware-workload affinity, resulting in random-like partitioning

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Hardware Heterogeneity Degree | Independent | Coefficient of variation of TFLOPS across GPUs in cluster | 0.2 (low) to 0.8 (high) |
| Neural Selector Architecture | Independent | 3-layer MLP (input: stage features, output: strategy logits) | Hidden dims: [128, 64, 32] |
| Geometric Partitioning Config | Independent | 3D feature space with Voronoi-like clustering | Features: [compute, memory, bandwidth] |
| Number of Stages | Independent | Model partitioned into N stages for strategy selection | 4-6 stages |
| Training Throughput | Dependent | Samples processed per second over full training epoch | Expected: 12-18% improvement |
| Communication Overhead | Dependent | % of training time in collective operations | Expected: 15-20% reduction |
| Memory Efficiency | Dependent | Peak GPU memory utilization | Expected: 10-15% improvement |
| Global Batch Size | Controlled | Fixed across all experiments | 512 samples |
| Optimizer Configuration | Controlled | AdamW with cosine learning rate schedule | lr=1e-4 |
| Dataset | Controlled | Standard LLM pretraining corpus | OpenWebText or RedPajama |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Hardware Profiling → 3D Feature Representation → Geometric Partitioning → Neural Strategy Selection → Training Throughput Improvement
     [Step 1]                [Step 2]                  [Step 3]                   [Step 4]                    [Outcome]
```

**Step 1:** GPU capabilities profiled and normalized to 3D feature space
**Step 2:** Voronoi-like clustering groups devices with similar capability profiles
**Step 3:** 3-layer MLP outputs strategy probabilities per stage
**Step 4:** Matched hardware-workload pairs minimize communication overhead

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | H2 (Tang 2025) | Compute/memory/comm metrics sufficient for heterogeneous optimization | Strong |
| Step 2 → Step 3 | Geometrized Task Scheduling (Chen 2025) | Voronoi partitioning polynomial-time solvable | Medium |
| Step 3 → Step 4 | Neural Hyper-Heuristic (2025) | Learned selection outperforms fixed heuristics by 28.49% | Strong |
| Step 4 → Outcome | C-ADP, H2, OmniLearn | Adaptive parallelism yields 14-85% training time reduction | Strong |

**Key Tension:**
- **Tension:** H2 uses static HeteroPP (computed offline) while EcoParallel proposes runtime-adaptive selection.
- **Resolution:** EcoParallel uses transfer learning from proxy models to amortize optimization cost, then applies lightweight runtime selection. This verification plan tests whether transfer learning quality (>80% selector accuracy) justifies the runtime overhead.

### 1.4 Key Assumptions

1. **Stage-level granularity is sufficient** (4-6 stages instead of 100+ layers)
   - Evidence: CollaPipe (2025) shows variable-sized segments effective
   - Consequence if violated: Synchronization overhead could negate efficiency gains

2. **Transfer learning generalizes across model sizes**
   - Evidence: Neural hyper-heuristic shows strategy selection transfers
   - Consequence if violated: Meta-training cost increases linearly with target model count

3. **3D feature space captures essential hardware characteristics**
   - Evidence: H2 uses compute/memory/communication as primary factors
   - Consequence if violated: Need higher-dimensional representation

4. **PyTorch/DeepSpeed primitives support multi-strategy coordination**
   - Evidence: Existing FSDP/ZeRO implementations
   - Consequence if violated: Requires custom CUDA kernels

### 1.5 Scope & Boundaries

**Applies to:**
- Transformer-based models (GPT, LLaMA, BERT, T5), 1B-70B parameters
- Heterogeneous GPU clusters: NVIDIA A100/V100/T4 mix, 8-32 GPUs
- Training workloads (not inference)

**Does NOT apply to:**
- Homogeneous clusters, non-transformer architectures, single-GPU, inference, cross-vendor heterogeneity

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Training Throughput vs Baseline 16.37%)**:
EcoParallel will achieve training throughput improvement of >12% on heterogeneous GPU clusters compared to best static baseline.

*Measurement*: Throughput > baseline + 12% with p < 0.05, paired t-test, n ≥ 20 runs
*Success*: >12% improvement | *Stretch*: >16% | *Falsification*: ≤8%

**Secondary Predictions:**

**P2 (Communication Overhead)**: 15-20% reduction in collective operation time
**P3 (Transfer Learning)**: >80% strategy selection accuracy from GPT-2 small to LLaMA-7B

**Falsification Criteria:**

1. **Primary Failure**: Throughput improvement ≤ 8%
2. **Mechanism Failure**: Transfer learning accuracy < 60%
3. **Overhead Failure**: Stage boundary synchronization > 5% of training time

### 1.7 SOTA Baseline

| Method | Performance | Year |
|--------|-------------|------|
| H2 (HeteroPP) | 16.37% speedup | 2025 |
| C-ADP | 21.6x FLOPS improvement | 2025 |
| OmniLearn | 14-85% time reduction | 2025 |

**Thresholds:** Primary >12% | Stretch >16% | Falsification ≤8%

### 1.8 Statistical Verification Design

- **Sample Size:** n ≥ 20 runs per configuration
- **Test:** Paired t-test, α = 0.05 (one-tailed)
- **Effect Size:** Cohen's d ≥ 0.8 expected
- **Configurations:** 18 (3 heterogeneity × 2 models × 3 clusters)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the neural hyper-heuristic selector produce non-random parallelism strategy selections that correlate with training performance?"

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual cause of performance improvement?"
- H-M1: Hardware profiling accuracy
- H-M2: Geometric partitioning meaningfulness
- H-M3: Neural selector transfer learning
- H-M4: Stage boundary overhead management

**SH3 (Comparison):**
"Does EcoParallel outperform static baselines and match/exceed SOTA adaptive methods?"

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-EcoParallel-v1
- [x] Confidence level: 0.72
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified and resolution proposed
- [x] Key assumptions with consequences (4 assumptions)
- [x] Testable predictions with primary marked
- [x] Falsification criteria with thresholds
- [x] SOTA baselines identified
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Resource Requirements:** Minimum 8 GPUs, 2 nodes for heterogeneity evaluation
2. **Data Availability:** AWS mixed instance types or simulated heterogeneity
3. **Transfer Learning Scope:** 15-20 proxy model configurations needed
4. **Priority Order:** SH1 → H-M3 → SH3

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
