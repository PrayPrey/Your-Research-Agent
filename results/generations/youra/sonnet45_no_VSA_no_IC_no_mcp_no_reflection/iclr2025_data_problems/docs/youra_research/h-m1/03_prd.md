# Product Requirements Document: H-M1

**Hypothesis:** Data curation (deduplication, filtering, domain mixing) increases information density per token, measured by entropy reduction and Fisher information increase

**Date:** 2026-08-28  
**Author:** Anonymous  
**Version:** 1.0  
**Phase:** 3 - Implementation Planning  

---

## Executive Summary

This PRD specifies implementation requirements for validating the causal mechanism between data curation and information density (H-M1). Building on H-E1's validated correlation findings (Q(D) metrics → info density, r > 0.5), this experiment tests whether active curation manipulation increases information density via entropy reduction and Fisher information metrics.

**Core Deliverable:** Training pipeline measuring information density across 9 curation conditions (fractional factorial: dedup × filter × domain_mix) using GPT-2 125M on C4 subsets.

**Success Criteria:** Entropy reduction >20% AND Fisher info increase >15% between uncurated baseline and full curation condition.

---

## Problem Statement

### Background

H-E1 validated that Q(D) metrics correlate with information density (dedup ratio r=0.72, composite Q(D) r=0.78). However, correlation ≠ causation. We need experimental validation that curation *actively drives* density increases.

### Research Question

Does controlled manipulation of curation dimensions (deduplication, filtering, domain mixing) causally increase information density per token in foundation model training data?

### Hypothesis Gate

- **Type:** MUST_WORK (foundation hypothesis)
- **Impact:** Blocks Phase 5 and all dependent hypotheses (h-m2, h-c1) if failed
- **Modification Budget:** 1 attempt → Phase 2A-Dialogue if still fails

---

## Functional Requirements

### FR-1: Dataset Preparation Pipeline

**Priority:** P0  
**Owner:** Data Preparation Module

**Requirements:**

1.1. Sample 50GB subset from C4 corpus (HuggingFace `allenai/c4` en split)  
1.2. Generate 9 curation conditions via fractional factorial design:
   - Dedup dimension: {0.0, 0.5, 0.95} (MinHash LSH, Jaccard threshold 0.8)
   - Filter dimension: {none, median-perplexity, top-25%}
   - Domain mix: {uniform, quality-weighted}
   - Conditions: baseline (0/0/0), dedup-low, dedup-high, filter-med, filter-high, mix-only, dedup+filter, dedup+mix, full-curation

1.3. Deduplication: MinHash LSH with 128 permutations  
1.4. Filtering: Perplexity scoring via GPT-2 small baseline  
1.5. Domain stats: Compute Herfindahl Index for diversity measurement  
1.6. Tokenization: GPT-2 BPE tokenizer  
1.7. Output format: Per-condition dataset cached to disk (~10B tokens each)

**Acceptance Criteria:**
- [ ] 9 distinct dataset subsets created
- [ ] Dedup ratio matches target (0%, 50%, 95%)
- [ ] Filter quality thresholds applied correctly
- [ ] Domain HHI computed for each subset

**Dependencies:** HuggingFace Datasets, datasketch (MinHash), GPT-2 tokenizer

---

### FR-2: Information Density Analyzer

**Priority:** P0  
**Owner:** Core Mechanism Module

**Requirements:**

2.1. Wrap GPT-2 125M training loop with `InformationDensityAnalyzer` module  
2.2. Compute token-level entropy during forward pass:
   - Shannon entropy via softmax normalization: `-(probs * log_probs).sum()`
   - Batch-wise averaging for corpus-level metric
   - Log every 100 steps

2.3. Compute Fisher Information Matrix trace after backward pass:
   - Diagonal FIM approximation: sum of squared gradients
   - O(d) complexity (not O(d²) full matrix)
   - Formula: `fisher_trace = sum((param.grad ** 2).sum() for param in model.parameters())`
   - Log every 100 steps

2.4. Training wrapper interface:
   ```python
   loss, entropy, fisher_trace = analyzer.forward(input_ids, labels)
   ```

2.5. Metric persistence: Save entropy/Fisher trajectories per condition to disk

**Acceptance Criteria:**
- [ ] Entropy values in expected range (4-6 bits/token for C4)
- [ ] Fisher trace non-negative and finite
- [ ] No NaN/Inf values in logged metrics
- [ ] Minimal overhead (<5% wall-clock time increase)

**Dependencies:** PyTorch, GPT-2 base model

---

### FR-3: Training Pipeline (Per Condition)

**Priority:** P0  
**Owner:** Training Module

**Requirements:**

3.1. Train GPT-2 125M on each of 9 curation conditions independently  
3.2. Hyperparameters (fixed across all conditions):
   - Optimizer: AdamW (β1=0.9, β2=0.95, eps=1e-8, weight_decay=0.1)
   - Learning rate: 6e-4 peak, cosine decay, 2000 warmup steps
   - Batch size: 256 effective (32 micro-batch × 8 accumulation)
   - Training steps: 50,000 per condition
   - Gradient clipping: 1.0 max norm
   - Dropout: 0.1

3.3. Seed: Fixed seed=42 (single run per condition)  
3.4. Checkpointing: Save model every 5000 steps  
3.5. Logging: Entropy, Fisher trace, perplexity every 100 steps  
3.6. Compute budget: ~50 GPU-hours (9 conditions × single V100)

**Acceptance Criteria:**
- [ ] All 9 conditions complete 50k training steps
- [ ] Hyperparameters identical across conditions
- [ ] No early stopping (fixed budget enforced)
- [ ] Checkpoints saved at specified intervals

**Dependencies:** HuggingFace Transformers, FR-2 (InformationDensityAnalyzer)

---

### FR-4: Evaluation Metrics

**Priority:** P0  
**Owner:** Evaluation Module

**Requirements:**

4.1. **Primary Metric 1:** Entropy Reduction
   - Baseline: Condition 1 (uncurated, dedup=0.0, filter=0, mix=0)
   - Comparison: Condition 9 (full curation, dedup=0.95, filter=2, mix=1)
   - Formula: `reduction = 100 * (baseline_entropy - curated_entropy) / baseline_entropy`
   - **Gate threshold:** >20%

4.2. **Primary Metric 2:** Fisher Information Increase
   - Baseline: Condition 1
   - Comparison: Condition 9
   - Formula: `increase = 100 * (curated_FIM - baseline_FIM) / baseline_FIM`
   - **Gate threshold:** >15%

4.3. **Secondary Metric:** Per-Dimension Monotonicity
   - Dedup dimension: Conditions 1, 2, 3 (expect entropy decrease with dedup ratio)
   - Filter dimension: Conditions 1, 4, 5 (expect entropy decrease with filter level)
   - Mix dimension: Conditions 1, 6 (expect entropy decrease with quality-weighted mixing)
   - **Gate threshold:** All 3 dimensions show monotonic effect

4.4. **Auxiliary Metric:** Perplexity
   - Standard LM perplexity on held-out C4 validation split
   - Not a gate metric (confirmation only)

**Acceptance Criteria:**
- [ ] Gate criteria computed at step 50,000 for all conditions
- [ ] Monotonicity check automated for 3 dimensions
- [ ] Results logged to structured format (JSON/CSV)

**Dependencies:** FR-3 (trained models), NumPy/Pandas for metric computation

---

### FR-5: Visualization

**Priority:** P1  
**Owner:** Visualization Module

**Requirements:**

5.1. **Required Figure:** Gate metrics bar chart (entropy reduction %, Fisher info increase %)  
5.2. Entropy trajectory line plot (9 conditions over 50k steps)  
5.3. Fisher information trajectory line plot (9 conditions)  
5.4. Ablation heatmap (dedup × filter × mix dimensions)  
5.5. Scatter plot: Fisher info vs Entropy (9 conditions, labeled)  
5.6. Perplexity vs curation strength (supplementary)

**Acceptance Criteria:**
- [ ] All figures saved to `{hypothesis_folder}/figures/`
- [ ] Legend distinguishes 9 conditions clearly
- [ ] Gate threshold lines marked on bar chart
- [ ] Figures embedded in 04_validation.md report

**Dependencies:** matplotlib/seaborn, FR-4 (metrics)

---

## Non-Functional Requirements

### NFR-1: Reproducibility

- Fixed seed (42) across all experiments
- Deterministic data sampling
- Hyperparameters logged per run
- PyTorch deterministic mode enabled

### NFR-2: Compute Efficiency

- Diagonal FIM (O(d) not O(d²))
- Streaming dataset loading (no full 50GB RAM load)
- Gradient accumulation for memory efficiency
- Single GPU per condition (no multi-GPU overhead)

### NFR-3: Code Quality

- Type hints for all public functions
- Docstrings for core modules
- Unit tests for metric computation (entropy, FIM)
- Integration test: end-to-end single condition run

### NFR-4: Observability

- Logging: INFO level for step progress, DEBUG for metric values
- Tensorboard integration for real-time monitoring
- CUDA memory tracking
- Wall-clock time per condition logged

---

## Success Criteria

### Phase 4 Gate (MUST_WORK)

✅ **PASS** if:
1. Entropy reduction > 20% (condition 9 vs 1)
2. Fisher info increase > 15% (condition 9 vs 1)
3. All 3 curation dimensions show monotonic effect

⚠️ **PARTIAL** if:
- Only 2/3 criteria met, OR marginal effect (10-20% reduction)
- Route to modification: Increase curation strength or sample size

❌ **FAIL** if:
- <10% effect size, OR opposite direction
- Route to Phase 2A-Dialogue for hypothesis reformulation

### Implementation Success

- [ ] All 9 conditions trained to 50k steps
- [ ] No NaN/Inf in logged metrics
- [ ] Gate metrics computed and logged
- [ ] Visualization figures generated
- [ ] 04_validation.md report written

---

## Dependencies

### Internal (Prerequisite Hypothesis)

- **H-E1 (VALIDATED):** Reuses C4 dataset, GPT-2 125M, entropy measurement methodology

### External Libraries

- PyTorch >= 2.0
- HuggingFace Transformers >= 4.30
- HuggingFace Datasets >= 2.12
- datasketch (MinHash LSH)
- NumPy, Pandas, matplotlib/seaborn
- (Optional) Tensorboard for logging

---

## Out of Scope

- Multi-seed runs (single seed=42 sufficient for PoC)
- Full FIM computation (diagonal approximation only)
- Test set evaluation (focus on training dynamics)
- Hyperparameter tuning (fixed from h-e1/literature)
- Multi-GPU training (single V100 per condition)

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Dedup removes too much data | Medium | High | Monitor dataset size after dedup; fallback to 80% threshold |
| Fisher computation unstable | Low | Medium | Gradient clipping at 1.0; log NaN checks |
| Compute budget exceeded | Low | Medium | Reduce steps to 30k if >60 GPU-hours |
| Effect size too small | Medium | High | 1 modification attempt budgeted per gate |

---

## Timeline (Phase 4 Estimate)

| Task | Effort |
|------|--------|
| Data preparation (FR-1) | 4-6 hours |
| Analyzer implementation (FR-2) | 2-3 hours |
| Training pipeline (FR-3) | 50 GPU-hours (parallel OK) |
| Evaluation + viz (FR-4, FR-5) | 2-3 hours |
| **Total:** | ~60 hours (mostly GPU wait) |

---

## Appendix: Traceability to Phase 2C

| Phase 2C Item | PRD Section |
|---------------|-------------|
| Dataset: C4 (50GB subset) | FR-1.1 |
| 9 curation conditions | FR-1.2 |
| Baseline model: GPT-2 125M | FR-3.1 |
| Entropy metric | FR-2.2, FR-4.1 |
| Fisher info metric | FR-2.3, FR-4.2 |
| Ablation design | FR-1.2 (fractional factorial) |
| Gate thresholds | FR-4.1, FR-4.2 (>20%, >15%) |
| Hyperparameters | FR-3.2 (from h-e1/HuggingFace) |

---

**Document Status:** COMPLETE  
**Next Step:** Architecture Design (Step 03)
