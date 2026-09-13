# Verification Plan: Attention-Probe Router for Task-Conditioned KV Cache Compression

**Date:** 2026-08-10
**Hypothesis ID:** H-AttnProbeRouter-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the constraint of fixed memory budget and LongBench benchmark, if we characterize KV compression response profiles across eviction and quantization strategies per task, then an attention-probe-based router will select task-appropriate configurations achieving ≥5% AUPC improvement over best single strategy, because early attention patterns encode task structure that correlates with compression tolerance.

### 1.2 Alternative Hypothesis (H0)
There is no task-dependent structure in compression response (k* = 1) OR attention features do not predict optimal compression (AUPC(router) ≤ AUPC(best-single)).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LongBench (standard) | 21 tasks across 6 categories; standard long-context evaluation; enables task-dependent analysis |
| **Model** | Llama-2-7B | Standard benchmark model; KV cache is significant memory consumer at 7B scale |

**Dataset Details:**
- Source: https://github.com/THUDM/LongBench
- Path: huggingface: THUDM/LongBench

**Model Details:**
- Type: decoder-only transformer
- Source: meta-llama/Llama-2-7b-hf

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Best-Single-Strategy | Select single best compression config (task-agnostic) based on average AUPC across all tasks | LongBench |
| H2O-Default | <2% accuracy drop at 20% retention | WikiText, PG-19 |
| StreamingLLM-Default | Infinite streaming with sink tokens | Streaming perplexity |
| Full-KV | No compression (upper bound) | LongBench |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Attention patterns stabilize within first 100 tokens | StreamingLLM shows initial tokens have special role; attention structure forms early | Probe may capture incomplete task representation; need longer probe window |
| A2 | LongBench tasks adequately represent deployment workloads | 21 datasets across 6 categories; widely used in long-context literature | Findings may not generalize to production tasks |
| A3 | Compression effects are model-dependent but probe features generalize within architecture family | Llama-2 family shares attention patterns; LoRA shows transfer within families | Need per-model router training |
| A4 | AUPC captures deployment-relevant trade-offs | Standard metric in multi-objective optimization; covers full Pareto frontier | May miss specific operating points important for certain deployments |
| A5 | Lightweight router (logistic regression) is sufficient | If clusters are well-separated, simple classifier suffices | Need more complex classifier; adds inference latency |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** Task-conditioned compression selection based on empirically-derived Pareto characterization

**Key Innovation:** Attention-probe router: using first-100-token attention features to predict optimal compression strategy

**Differentiation:**
- vs H2O [Zhang 2023]: H2O makes per-token eviction decisions; we make per-task strategy selection
- vs Ada-KV [Feng 2024]: Ada-KV adapts per-head; we adapt per-task based on attention probe
- vs RocketKV [Behnam 2025]: RocketKV is fixed two-stage; we select strategy dynamically based on task

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | Pending |
| H-M1 | Mechanism | MUST_WORK | H-E1 | Pending |
| H-M2 | Mechanism | MUST_WORK | H-M1 | Pending |
| H-M3 | Mechanism | MUST_WORK | H-M2 | Pending |
| H-M4 | Mechanism | MUST_WORK | H-M3 | Pending |

---

### 2.2 Hypothesis Specifications

#### H-E1: Task-Dependent Compression Clusters Exist

**Statement**: Under LongBench benchmark evaluation, if we apply gap statistic clustering to task-level compression response profiles (21 tasks × 6 configs), then k* > 1 distinct clusters will emerge, because tasks with different structural requirements exhibit systematically different compression tolerances.

**Rationale**: This existence hypothesis validates the foundational premise that not all tasks respond identically to compression. If k* = 1, the entire routing hypothesis collapses since there would be nothing to route between.

**Variables**:
- Independent: Compression strategy (eviction ratio × quantization level)
- Dependent: Cluster count k* from gap statistic
- Controlled: Model (Llama-2-7B), benchmark (LongBench), hardware (A100)

**Verification Protocol**:
1. Run Llama-2-7B baseline on all 21 LongBench tasks with full KV cache.
2. Apply 6 compression configs to each task, record accuracy retention.
3. Construct 21×6 response matrix, apply gap statistic with B=500 bootstrap samples.
4. Compute gap(k) - E[gap_null(k)] - SE for k=1..6.
5. Report k* (first k where gap criterion met).

**Success Criteria**:
- Primary: k* > 1 with gap > standard error
- Secondary: Cluster separation > 0.5 silhouette score

**Failure Response**: IF fails → ABANDON (no task structure means routing has no basis)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1, Prediction P1

---

#### H-M1: Early Attention Entropy Reflects Task Structure

**Statement**: Under first-100-token attention extraction, if we compute per-head entropy across LongBench tasks, then entropy variance across tasks will exceed within-category variance, because tasks requiring broad context integration show different attention patterns than focused retrieval tasks.

**Rationale**: This mechanism step establishes that attention patterns carry task-relevant information that could inform routing decisions. Without this link, the router would have no predictive signal.

**Variables**:
- Independent: LongBench task type (21 tasks, 6 categories)
- Dependent: Attention entropy (mean across heads/layers)
- Controlled: Token window (first 100), model architecture

**Verification Protocol**:
1. Forward pass on each task sample, capture attention weights.
2. Compute Shannon entropy per head per layer over first 100 tokens.
3. Aggregate: mean entropy per task, variance across tasks, variance within categories.
4. Apply F-test comparing between-category vs within-category variance.

**Success Criteria**:
- Primary: Between-task entropy variance > within-category variance (F-test p<0.05)
- Secondary: Interpretable pattern (e.g., QA higher entropy than summarization)

**Failure Response**: IF fails → PIVOT (try alternative features: head sparsity, top-k concentration)

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---

#### H-M2: High-Entropy Tasks Tolerate Eviction Better

**Statement**: Under eviction-based KV compression (40-80% retention), if tasks are stratified by attention entropy, then high-entropy tasks will show higher accuracy retention than low-entropy tasks, because distributed attention means removing individual tokens has less impact.

**Rationale**: This step links the observable feature (entropy) to a specific compression mechanism (eviction), validating one arm of the routing decision logic.

**Variables**:
- Independent: Task entropy quartile (high vs low)
- Dependent: Accuracy retention under eviction
- Controlled: Eviction method (H2O), model, evaluation scripts

**Verification Protocol**:
1. Split 21 tasks into high/low entropy groups using median from H-M1.
2. Run eviction configs (40%, 80% retention) on both groups.
3. Compute mean accuracy retention per group per config.
4. Statistical test: t-test or Mann-Whitney comparing groups.

**Success Criteria**:
- Primary: High-entropy group shows significantly higher retention (p<0.05)
- Secondary: Effect size Cohen's d > 0.5

**Failure Response**: IF fails → EXPLORE (check if relationship is non-linear or threshold-based)

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2

---

#### H-M3: Low-Entropy Tasks Tolerate Quantization Better

**Statement**: Under quantization-based KV compression (int8/int4), if tasks are stratified by attention entropy, then low-entropy tasks will show higher accuracy retention than high-entropy tasks, because concentrated attention benefits from precision preservation.

**Rationale**: This completes the entropy-tolerance relationship, showing eviction and quantization have opposite preferences, which justifies adaptive strategy selection.

**Variables**:
- Independent: Task entropy quartile (high vs low)
- Dependent: Accuracy retention under quantization
- Controlled: Quantization method, model, evaluation scripts

**Verification Protocol**:
1. Use same high/low entropy split from H-M2.
2. Run quantization configs (int8, int4) on both groups.
3. Compute mean accuracy retention per group per config.
4. Statistical test: t-test or Mann-Whitney comparing groups.

**Success Criteria**:
- Primary: Low-entropy group shows significantly higher retention (p<0.05)
- Secondary: Inverse correlation with H-M2 results

**Failure Response**: IF fails → EXPLORE (quantization may be universally better/worse)

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3

---

#### H-M4: Router Achieves AUPC Improvement

**Statement**: Under 3-fold cross-validation on LongBench, if we train a logistic regression router on attention features to predict optimal compression config, then AUPC(router) > 1.05 × AUPC(best-single) on held-out tasks, because the entropy-tolerance relationship enables task-appropriate selection.

**Rationale**: This is the culminating mechanism test that validates the entire hypothesis. If the router cannot outperform a fixed strategy, the research contribution is null.

**Variables**:
- Independent: Router selection vs best-single-strategy
- Dependent: AUPC (Area Under Pareto Curve)
- Controlled: CV fold structure, evaluation protocol

**Verification Protocol**:
1. Extract features: mean_entropy, head_sparsity, top-k concentration per task.
2. Train logistic regression on 14 tasks (train fold), predict cluster from H-E1.
3. Map predicted cluster to compression config, run inference.
4. Compute AUPC for router-selected configs vs best-single on 7 held-out tasks.
5. Repeat for all 3 folds, report mean improvement.

**Success Criteria**:
- Primary: Mean AUPC(router) > 1.05 × AUPC(best-single) across folds
- Secondary: 95% CI excludes 1.0

**Failure Response**: IF fails → ABANDON or pivot to Phase 5 baseline comparison

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Prediction P2

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | k* > 1 clusters | ABANDON entire hypothesis |
| H-M1 | MUST_WORK | Entropy variance F-test p<0.05 | PIVOT to alternative features |
| H-M2 | SHOULD_WORK | High-entropy eviction advantage p<0.05 | EXPLORE non-linear relationship |
| H-M3 | SHOULD_WORK | Low-entropy quantization advantage p<0.05 | EXPLORE alternative mechanism |
| H-M4 | MUST_WORK | AUPC > 1.05 × best-single | ABANDON or document partial success |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | ~2 GPU-hours |
| Phase 2: Mechanism | H-M1, H-M2, H-M3, H-M4 | ~3 GPU-hours |

**Total Duration:** ~5 GPU-hours on A100

---

## 4. Risk Analysis

### 4.1 Risk Identification

| ID | Risk | Source | Severity | Likelihood |
|----|------|--------|----------|------------|
| R1 | Attention patterns unstable in first 100 tokens | A1 | High | Medium |
| R2 | LongBench not representative of deployment | A2 | Medium | Low |
| R3 | Probe features don't generalize across model sizes | A3 | High | Medium |
| R4 | AUPC misses deployment-critical operating points | A4 | Medium | Low |
| R5 | Logistic regression classifier insufficient | A5 | Medium | Medium |

### 4.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact |
|------|---------------------|--------|
| R1 | H-M1, H-M4 | Probe captures incomplete task representation; router predictions unreliable |
| R2 | All (H-E1 to H-M4) | Findings may not generalize to production workloads |
| R3 | H-M4 | Need per-model router training; increased deployment complexity |
| R4 | H-M4 | Router optimizes wrong objective; deployment benefit unclear |
| R5 | H-M4 | Router accuracy insufficient; need complex classifier adding latency |

### 4.3 Mitigation Strategies

**R1: Attention Pattern Instability**
- Prevention: Run pilot study measuring entropy stability across token windows (50, 100, 200, 500)
- Detection: Monitor entropy variance as token window increases; plateau indicates stability
- Response: 
  - PIVOT: Extend probe window to first 200-500 tokens
  - SCOPE: Use only tasks where patterns stabilize within 100 tokens

**R2: Benchmark Representativeness**
- Prevention: Compare LongBench task distribution to real deployment logs (if available)
- Detection: Check if discovered clusters align with expected deployment categories
- Response:
  - PIVOT: Supplement with additional benchmarks (SCROLLS, InfiniteBench)
  - SCOPE: Document limitations, claim applicability to LongBench-like tasks only

**R3: Cross-Model Generalization**
- Prevention: Design features to be architecture-agnostic (relative entropy, normalized sparsity)
- Detection: Run pilot on Llama-2-13B to check feature stability
- Response:
  - PIVOT: Train separate routers per model size
  - SCOPE: Claim applicability to Llama-2-7B only; generalization is future work

**R4: AUPC Metric Mismatch**
- Prevention: Consult with deployment engineers on relevant operating points
- Detection: Plot full Pareto frontier; check if AUPC winners match intuitive preferences
- Response:
  - PIVOT: Use weighted AUPC emphasizing deployment-relevant region
  - SCOPE: Report multiple metrics (accuracy@50%, memory@95%acc)

**R5: Classifier Complexity**
- Prevention: Start with logistic regression; measure cluster separability
- Detection: If CV accuracy < 80%, classifier is insufficient
- Response:
  - PIVOT: Upgrade to gradient boosting or small MLP
  - SCOPE: Accept ~5ms latency increase for better accuracy

### 4.4 Risk Summary

| ID | Risk | Severity | Mitigation Summary |
|----|------|----------|-------------------|
| R1 | Unstable attention in 100 tokens | High | Extend probe window if needed |
| R2 | LongBench not representative | Medium | Document scope, supplement if needed |
| R3 | Cross-model generalization | High | Per-model router or limit claims |
| R4 | AUPC metric mismatch | Medium | Multi-metric reporting |
| R5 | Classifier insufficient | Medium | Upgrade classifier complexity |

**Risk Distribution:** Critical: 0, High: 2, Medium: 3, Low: 0

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────┐
    │  H-E1: Clustering Exists (k* > 1)  │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘
                     │
                     ▼
[Level 1 - Mechanism Step 1]
    ┌─────────────────────────────────────┐
    │  H-M1: Attention Entropy Encodes   │
    │        Task Structure               │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘
                     │
                     ▼
[Level 2 - Mechanism Step 2]
    ┌─────────────────────────────────────┐
    │  H-M2: High-Entropy Tolerates      │
    │        Eviction Better              │
    │  Gate: SHOULD_WORK                  │
    └─────────────────────────────────────┘
                     │
                     ▼
[Level 3 - Mechanism Step 3]
    ┌─────────────────────────────────────┐
    │  H-M3: Low-Entropy Tolerates       │
    │        Quantization Better          │
    │  Gate: SHOULD_WORK                  │
    └─────────────────────────────────────┘
                     │
                     ▼
[Level 4 - Mechanism Step 4]
    ┌─────────────────────────────────────┐
    │  H-M4: Router Achieves 5% AUPC     │
    │        Improvement                  │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Levels: 5 (sequential chain)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Fail Action |
|-------|------------|---------------|-----------|-------------|
| 0 | H-E1 | None | MUST_WORK | ABANDON |
| 1 | H-M1 | H-E1 | MUST_WORK | PIVOT |
| 2 | H-M2 | H-M1 | SHOULD_WORK | EXPLORE |
| 3 | H-M3 | H-M2 | SHOULD_WORK | EXPLORE |
| 4 | H-M4 | H-M3 | MUST_WORK | ABANDON/Document |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses (~5 GPU-hours on A100)
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis       │ Hour 1  │ Hour 2  │ Hour 3  │ Hour 4  │ Hour 5  │
───────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation    │         │         │         │         │         │
  H-E1 (126 runs)      │ ████████│█████████│         │         │         │
  [Gate 1]             │         │    ◆    │         │         │         │
───────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms    │         │         │         │         │         │
  H-M1 (feature ext)   │         │         │ ███     │         │         │
  H-M2 (eviction test) │         │         │    ████ │         │         │
  H-M3 (quant test)    │         │         │         │ ███     │         │
  H-M4 (router CV)     │         │         │         │    █████│█████    │
  [Gate 2]             │         │         │         │         │    ◆    │
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active computation | ◆ = Gate decision point
Total Duration: ~5 GPU-hours (A100)
═══════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Duration Breakdown:**
| Phase | Hypotheses | GPU-Hours | Description |
|-------|------------|-----------|-------------|
| Foundation | H-E1 | ~2.0 | 21 tasks × 6 configs = 126 runs |
| Mechanism | H-M1 | ~0.3 | Attention extraction (1 pass per task) |
| Mechanism | H-M2 | ~0.5 | Eviction ablation (subset rerun) |
| Mechanism | H-M3 | ~0.5 | Quantization ablation (subset rerun) |
| Mechanism | H-M4 | ~1.7 | 3-fold CV (router training + evaluation) |

**Total:** ~5 GPU-hours on A100
**Slack:** 0 (fully sequential chain)

### 5.5 Resource Summary

| Resource | Requirement |
|----------|-------------|
| GPU | 1× A100 (40GB or 80GB) |
| Compute | ~5 GPU-hours total |
| Storage | ~50GB (model + KV cache snapshots) |
| Model | Llama-2-7B (meta-llama/Llama-2-7b-hf) |
| Dataset | LongBench (21 tasks, 6 categories, ~3500 samples) |
| Dependencies | transformers, bitsandbytes, sklearn |

### 5.6 Execution Order

1. **Execute H-E1** (Foundation): Run all 126 task-config combinations, compute gap statistic
2. **Evaluate Gate 1**: If k* = 1 → ABANDON; else continue
3. **Execute H-M1** (Feature Extraction): Extract attention entropy per task
4. **Execute H-M2** (Eviction Test): Compare high/low entropy groups under eviction
5. **Execute H-M3** (Quantization Test): Compare groups under quantization
6. **Execute H-M4** (Router Training): 3-fold CV with logistic regression router
7. **Evaluate Gate 2**: If AUPC improvement < 5% → document partial success
8. **Final**: Verification complete, proceed to Phase 2C experiment design

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

**Core Claim:** Early attention patterns encode task structure that predicts optimal KV cache compression strategy, enabling a router to achieve ≥5% AUPC improvement over fixed strategies.

**Supporting Evidence:**
1. Tasks exhibit distinct compression tolerance profiles (testable via gap statistic k* > 1)
2. Attention entropy in first 100 tokens correlates with task structure
3. High-entropy tasks tolerate eviction; low-entropy tasks tolerate quantization
4. Lightweight logistic regression can map attention features to optimal config

**Strengths:**
- Builds on established H2O heavy-hitter theory
- Clear 4-step causal mechanism with testable predictions
- Practical deployment impact (~400MB savings at 7B scale)
- Uses existing benchmarks (LongBench) and baselines

### 6.2 Antithesis Development

**Null Hypothesis (H0):** There is no task-dependent structure in compression response (k* = 1) OR attention features do not predict optimal compression (AUPC(router) ≤ AUPC(best-single)).

**Counter-Arguments:**
1. All LongBench tasks may respond similarly to compression (homogeneous response)
2. Attention patterns may not stabilize within 100 tokens
3. Entropy-tolerance correlation may be non-existent or reversed
4. Best-single strategy may already be near-optimal (5% ceiling not achievable)

**Conditions Under Which H0 Would Be Supported:**
- Gap statistic returns k* = 1 (no cluster structure)
- Attention entropy shows no variance across task types
- High-entropy tasks do NOT tolerate eviction better
- Router AUPC ≤ best-single AUPC on held-out data

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-AttnProbeRouter-v1 presents a testable claim linking attention patterns to compression strategy selection. The null hypothesis raises valid concerns about homogeneous compression response across tasks.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Gap statistic determines existence before mechanism testing
2. **Sequential mechanism testing (H-M1-M4):** Tests causal chain step-by-step with early termination
3. **Pre-committed thresholds:** k* > 1, AUPC > 1.05× prevent post-hoc flexibility

**Nuanced Outcome Possibilities:**
| Outcome | Condition | Publication Value |
|---------|-----------|-------------------|
| Full Support | All gates pass, AUPC > 1.05× | Method paper with practical impact |
| Partial Support | k* > 1 but AUPC < 1.05× | Characterization paper documenting ceiling |
| No Support | k* = 1 or H-M1 fails | Negative result paper quantifying limits |

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Task clusters exist | May be artifact | H-E1 gap statistic |
| Mechanism | Entropy-tolerance link | Alternative explanations | H-M1-M3 ablations |
| Performance | ≥5% AUPC improvement | Marginal improvement | H-M4 3-fold CV |
| Scope | Llama-2-7B validated | Single architecture | Document limitation |

**Overall Robustness Score:** HIGH (pre-committed thresholds, sequential gates, all outcomes publishable)

**Confidence in Verification Plan:** 0.75

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Attention-probe router selects task-appropriate KV cache compression for ≥5% AUPC improvement
- ID: H-AttnProbeRouter-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Duration: ~5 GPU-hours on A100
- Critical Gates: 3 MUST_WORK (H-E1, H-M1, H-M4)

**Risk Assessment:** Medium (2 high, 3 medium risks)
- Primary concerns: Attention stability (R1), cross-model generalization (R3)

**Immediate Action:** Begin Phase 1 with H-E1 clustering verification

### 7.2 Final Summary

**Verification Execution Order:**

| Step | Hypothesis | Gate | Action if Fail |
|------|------------|------|----------------|
| 1 | H-E1 | MUST_WORK | ABANDON |
| 2 | H-M1 | MUST_WORK | PIVOT to alternative features |
| 3 | H-M2 | SHOULD_WORK | EXPLORE non-linear |
| 4 | H-M3 | SHOULD_WORK | EXPLORE alternative |
| 5 | H-M4 | MUST_WORK | Document partial success |

### 7.3 Conclusions

**Key Achievements:**
- 5 hypotheses with clear verification protocols
- Sequential dependency chain with gate conditions
- All outcomes (positive, partial, null) are publishable
- Modest compute requirement (~5 GPU-hours)

**Critical Decision Points:**
1. Gate 1 (H-E1): k* > 1 → continue; k* = 1 → ABANDON
2. Gate 2 (H-M1): F-test p<0.05 → continue; else PIVOT
3. Gate 3 (H-M4): AUPC > 1.05× → success; else document ceiling

**Open Questions:**
- Does probe generalize across Llama model sizes (7B → 13B → 70B)?
- Do discovered clusters align with LongBench categories?
- Is 5% AUPC improvement achievable or is effect smaller?

**Recommendations:**
1. Start H-E1 immediately (126 task-config runs)
2. Monitor attention entropy stability across token windows
3. Pre-register analysis plan before running H-M4 CV

### 7.4 Appendices

**A. Phase 2A Reference:**
- Source: docs/youra_research/03_refinement.yaml
- Hypothesis ID: H-AttnProbeRouter-v1

**B. MCP Tool Usage:**
- scientificmethod: 4 calls (H-E1 hypothesis+experiment, H-M hypothesis+experiment)
- structuredargumentation: 3 calls (thesis, antithesis, synthesis)

---

## 8. Verification State

**Status:** COMPLETE
**Pipeline Tasks Updated:** Phase 2B → done, Phase 2C → doing
**Hypothesis Tasks Created:** 5 tasks (H-E1, H-M1, H-M2, H-M3, H-M4)

**State File:** `verification_state.yaml`
**Next Phase:** Phase 2C - Experiment Design (use `/phase2c-experiment-design` or `/hypothesis-next`)
