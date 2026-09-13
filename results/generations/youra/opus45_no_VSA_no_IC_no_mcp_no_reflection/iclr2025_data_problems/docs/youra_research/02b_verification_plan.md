# Verification Plan: EDMP - Training-Free Domain Mixing Optimization

**Date:** 2026-08-28
**Hypothesis ID:** H-EDMP-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 0. Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON - DO NOT RE-TEST)

| # | Claim | Evidence | Status |
|---|-------|----------|--------|
| 1 | Domain mixing ratios affect downstream LLM performance | DoReMi, SlimPajama research established this empirically | BUILD_ON |
| 2 | Embedding similarity correlates with transfer performance | Domain adaptation literature, DSIR (Park et al.) | BUILD_ON |

### 0.2 Claims Requiring Verification (PROVE_NEW)

| # | Claim | Evidence Needed |
|---|-------|-----------------|
| 1 | Training-free prediction of optimal domain mixing via embeddings is possible | Novel hypothesis to be validated |

### 0.3 Scope Reduction

**Reduction:** 66% of claims are established facts (2 of 3 claims BUILD_ON)

**Phase 2B-4 Instructions:**
Domain mixing impact and embedding-transfer correlation are established. Focus Phase 2B on validating the EDMP scoring mechanism (similarity + diversity) and its predictive power for ranking optimization.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard LLM pretraining conditions with multi-domain corpora, if domain mixing is guided by embedding-based similarity + diversity scores computed from a mid-scale embedder (E5-large) against downstream task exemplars, then downstream task performance will improve by ≥3% on average compared to heuristic methods (perplexity-based, random selection), because embedding geometry captures task-relevant information content that correlates with transfer utility.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in downstream performance (MMLU, HellaSwag, ARC) between models trained on EDMP-selected domain mixtures and models trained on perplexity-selected or randomly-selected domain mixtures, given equal training compute.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | The Pile (standard) | 22 domain-labeled subsets enable controlled domain mixing experiments |
| **Model** | Pythia-1B | Open weights, well-documented training; scale suitable for ablations |

**Dataset Details:**
- Source: EleutherAI
- Path: https://pile.eleuther.ai/

**Model Details:**
- Type: decoder-only transformer
- Source: EleutherAI

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| DoReMi | ~2-3% over baseline mixtures | The Pile | Requires proxy model training; not training-free |
| DSIR | Improves fine-tuning transfer | Various | Task-specific importance sampling; doesn't address pretraining mixture |
| Random/equal mixing | Baseline | Standard | No principled optimization; leaves performance on table |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Embedding geometry captures task-relevant information content | Retrieval benchmarks show semantic similarity in embedding space | EDMP scores would not correlate with transfer utility |
| A2 | Task exemplar embeddings represent downstream task distribution | Validation sets are designed to cover task distribution | Similarity scores would be unrepresentative; use larger exemplar sets |
| A3 | Domain rankings are stable across embedder model scales | To be validated; partial support from transfer learning literature | EDMP would require scale-specific embedders, reducing generality |
| A4 | Similarity + diversity scoring captures both relevance and complementarity | Set cover metrics capture complementarity in recommendation systems | Missing domain interactions; would need pairwise interaction terms |
| A5 | Embedding computation is substantially cheaper than proxy model training | Inference-only vs. gradient computation; ~32 vs. 100+ GPU-hours estimated | Training-free claim weakened; still valuable if faster even at similar cost |

### 1.6 Research Gap & Novelty

**Gap:** Existing domain mixing methods (DoReMi) require expensive proxy model training. No training-free approach exists for predicting optimal domain mixtures.

**Novelty:** Training-free domain mixing optimization via embedding geometry. Combining similarity (task-relevance) with diversity (complementarity) in a unified scoring function, computable without any model training.

**Differentiation:**
- vs. DoReMi: EDMP uses frozen embeddings only, no proxy model training
- vs. DSIR: EDMP provides multi-task ranking via benchmark exemplars, not single-task importance sampling
- vs. Perplexity-based: EDMP uses task-grounded embeddings, not model-dependent perplexity

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | READY |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | READY |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | READY |

---

### 2.2 Hypothesis Specifications

#### H-E1: EDMP Score Computability

**Type:** EXISTENCE
**Statement:** Under multi-domain corpus conditions, if domains are sampled and embedded with E5-large against task exemplars, then EDMP similarity + diversity scores can be reliably computed for all domain-task pairs, because embedding extraction and scoring are deterministic operations on fixed model weights.

**Variables:**
- IV: Domain corpus samples (n=1000 tokens per domain)
- DV: EDMP score (continuous, range [0,1])
- CV: Embedder model (E5-large), task exemplars (MMLU validation set)

**Success Criteria:**
- All 22 Pile domains produce valid EDMP scores
- Score variance < 5% across repeated computations
- Computation completes in < 2 GPU-hours for all domains

**Gate:**
- Type: MUST_WORK
- If Fail: Scoring mechanism fundamentally flawed; hypothesis invalid

**Prerequisites:** None

**Verification Protocol:**
1. Sample 1000 tokens from each of 22 Pile domains
2. Embed all samples using E5-large
3. Compute similarity to MMLU exemplar embeddings
4. Compute diversity contribution via embedding space coverage
5. Combine into EDMP score: similarity × (1 + diversity_bonus)
6. Verify numerical stability and reproducibility

---

#### H-M1: Embedding Extraction Captures Domain Semantics

**Type:** MECHANISM
**Statement:** Under standard embedding conditions, if domain tokens are embedded with E5-large, then embeddings cluster by domain with semantic structure, because transformer embeddings encode distributional semantics.

**Variables:**
- IV: Domain corpus (22 Pile domains)
- DV: Embedding cluster quality (silhouette score, t-SNE visualization)
- CV: Embedder model, sample size per domain

**Success Criteria:**
- Silhouette score > 0.3 for domain clustering
- t-SNE shows visually distinct domain clusters
- Semantic neighbors (e.g., math domains) cluster together

**Gate:**
- Type: MUST_WORK
- If Fail: Causal step 1 broken; embeddings don't capture domain semantics

**Prerequisites:** H-E1 (scores computable)

**Verification Protocol:**
1. Extract embeddings for all 22 domains
2. Compute pairwise cosine similarities
3. Run k-means clustering (k=22)
4. Measure silhouette score
5. Generate t-SNE visualization
6. Verify semantic coherence of clusters

---

#### H-M2: Scoring Function Correlates with Transfer Utility

**Type:** MECHANISM
**Statement:** Under EDMP scoring conditions, if domains are ranked by similarity + diversity scores against task exemplars, then rankings correlate with actual transfer performance (Kendall's τ > 0.5), because embedding similarity predicts distributional alignment.

**Variables:**
- IV: EDMP domain rankings
- DV: Kendall's τ correlation with actual performance rankings
- CV: Task exemplar set (MMLU validation), embedder model

**Success Criteria:**
- Kendall's τ > 0.5 between EDMP rank and oracle rank
- Top-3 EDMP domains overlap ≥ 2 with oracle top-3
- Correlation holds for multiple downstream tasks

**Gate:**
- Type: MUST_WORK
- If Fail: Causal step 2 broken; scoring doesn't predict performance

**Prerequisites:** H-M1 (embeddings meaningful)

**Verification Protocol:**
1. Compute EDMP rankings for all 22 domains
2. Train single-domain models (small scale, 100M tokens each)
3. Evaluate on MMLU to get oracle rankings
4. Compute Kendall's τ between EDMP and oracle
5. Repeat for HellaSwag, ARC
6. Assess consistency across tasks

---

#### H-M3: Ranking Aggregation Produces Effective Mixtures

**Type:** MECHANISM
**Statement:** Under EDMP ranking conditions, if top-K domains are selected by combined score, then training on selected mixture outperforms random-K selection by ≥3%, because top-K selection concentrates training on high-utility domains.

**Variables:**
- IV: Domain selection method (EDMP top-K vs random-K vs equal-weight)
- DV: Downstream benchmark performance (MMLU average)
- CV: Training compute (10B tokens), model architecture (Pythia-1B)

**Success Criteria:**
- EDMP top-3 mixture outperforms random-3 by ≥3% on MMLU
- EDMP top-3 outperforms equal-weight by ≥2%
- Improvement consistent across MMLU, HellaSwag, ARC

**Gate:**
- Type: MUST_WORK
- If Fail: Causal step 3 broken; ranking aggregation ineffective

**Prerequisites:** H-M2 (rankings predictive)

**Verification Protocol:**
1. Select top-3 domains by EDMP score
2. Train Pythia-1B on EDMP mixture (10B tokens)
3. Train Pythia-1B on random-3 mixture (10B tokens)
4. Train Pythia-1B on equal-weight mixture (10B tokens)
5. Evaluate all models on MMLU, HellaSwag, ARC
6. Compare performance differences

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Scores computable for all domains | STOP: Fundamental flaw |
| H-M1 | MUST_WORK | Silhouette > 0.3 | STOP: Embeddings not semantic |
| H-M2 | MUST_WORK | Kendall's τ > 0.5 | STOP: Scoring doesn't predict |
| H-M3 | MUST_WORK | ≥3% improvement over random | STOP: Selection ineffective |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Existence | H-E1 | 1 day |
| Phase 2: Mechanism Chain | H-M1, H-M2, H-M3 | 3-5 days |

**Total Duration:** 4-6 days (PoC verification)

---

## 4. Risk Analysis

### 4.1 Risk Identification

| Risk ID | Risk | Source | Probability | Impact | Mitigation |
|---------|------|--------|-------------|--------|------------|
| R1 | Embeddings don't capture task-relevant semantics | A1 violation | Medium | Critical | Validate with retrieval benchmarks first |
| R2 | Task exemplars unrepresentative | A2 violation | Low | High | Use larger exemplar set (full validation split) |
| R3 | Scale-dependent rankings | A3 violation | Medium | Medium | Test with multiple embedder scales |
| R4 | Diversity term adds noise, not signal | A4 violation | Medium | Medium | Ablate: test similarity-only vs similarity+diversity |
| R5 | Embedding compute not cheaper than proxy training | A5 violation | Low | Low | Measure actual GPU-hours; still valuable if faster |

### 4.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Detection Point |
|------|---------------------|-----------------|
| R1 | H-M1, H-M2 | H-M1 clustering quality |
| R2 | H-M2, H-M3 | H-M2 correlation analysis |
| R3 | H-M2 | H-M2 cross-scale validation |
| R4 | H-M3 | H-M3 ablation study |
| R5 | N/A (efficiency claim) | Post-experiment cost analysis |

### 4.3 Mitigation Strategies

| Risk | Strategy | Trigger | Fallback |
|------|----------|---------|----------|
| R1 | Pre-validate embedding quality on retrieval task | Silhouette < 0.2 | Try alternative embedder (BGE, OpenAI) |
| R2 | Expand exemplar set to full validation split | Top-3 overlap < 1 | Use stratified sampling across task types |
| R3 | Test rankings with 2+ embedder scales | τ variance > 0.2 across scales | Use scale-specific embedders |
| R4 | Run similarity-only ablation | Diversity degrades performance | Remove diversity term |
| R5 | N/A | N/A | Document actual costs; claim remains valid if faster |

---

## 5. Dependency Graph

### 5.1 DAG Visualization

```
                    ┌─────────────────────────────────────────────┐
                    │           PHASE 2B DEPENDENCY GRAPH         │
                    └─────────────────────────────────────────────┘

    ┌─────────┐
    │  H-E1   │  EXISTENCE: Score Computability
    │MUST_WORK│
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  H-M1   │  MECHANISM: Embedding Extraction
    │MUST_WORK│  (Causal Step 1)
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  H-M2   │  MECHANISM: Scoring Correlation
    │MUST_WORK│  (Causal Step 2)
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  H-M3   │  MECHANISM: Ranking Aggregation
    │MUST_WORK│  (Causal Step 3)
    └─────────┘
         │
         ▼
    ┌─────────────────────────┐
    │  PHASE 5: H-CP*         │
    │  Baseline Comparison    │
    │  (DoReMi, perplexity)   │
    └─────────────────────────┘
```

### 5.2 Dependency Hierarchy

| Level | Hypotheses | Dependencies | Gate |
|-------|------------|--------------|------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | MUST_WORK |
| 3 | H-M3 | H-M2 | MUST_WORK |
| 4 | H-CP* (Phase 5) | H-M3 | DETERMINES_SUCCESS |

---

## 6. Timeline (Gantt)

### 6.1 Gantt Chart

```
                    PHASE 2B-4 TIMELINE
    ═══════════════════════════════════════════════════════════
    
    Day:    1       2       3       4       5       6
            ├───────┼───────┼───────┼───────┼───────┼───────┤
    
    H-E1    ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    [GATE]        ▼
    
    H-M1    ░░░░░░░░████████████████░░░░░░░░░░░░░░░░░░░░░░░░░
    [GATE]                        ▼
    
    H-M2    ░░░░░░░░░░░░░░░░░░░░░░░░████████████████░░░░░░░░░
    [GATE]                                        ▼
    
    H-M3    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████░
    [GATE]                                                ▼
    
    ═══════════════════════════════════════════════════════════
    Legend: ████ Active    ░░░░ Waiting    ▼ Gate Check
```

### 6.2 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

All hypotheses on critical path (linear dependency chain). No parallel execution possible within Phase 2B-4.

**Bottlenecks:**
- H-M2: Requires training single-domain models for oracle rankings (most compute-intensive)
- H-M3: Requires training 3 models for comparison (final validation)

### 6.3 Resource Summary

| Hypothesis | GPU-Hours | Wall Time | Blocking? |
|------------|-----------|-----------|-----------|
| H-E1 | 2 | 4 hours | Yes |
| H-M1 | 4 | 6 hours | Yes |
| H-M2 | 48 (22 small models) | 2 days | Yes |
| H-M3 | 96 (3 full models) | 2 days | Yes |
| **Total** | **150** | **4-6 days** | - |

### 6.4 Execution Order

1. **H-E1** (Day 1): Verify EDMP scores computable
2. **H-M1** (Day 1-2): Validate embedding semantics
3. **H-M2** (Day 2-4): Test scoring correlation
4. **H-M3** (Day 4-6): Validate mixture effectiveness

---

## 7. Dialectical Analysis

### 7.1 Thesis

**Claim:** Embedding-based Domain Mixing Prediction (EDMP) enables training-free optimization of domain mixtures for LLM pretraining by leveraging semantic similarity and diversity scores.

**Supporting Arguments:**
1. Embedding geometry encodes distributional semantics (established in retrieval literature)
2. DSIR demonstrated similarity-based selection improves transfer
3. Diversity captures complementarity beyond pure similarity
4. No proxy model training required - pure inference

### 7.2 Antithesis (H0 Defense)

**Counter-Claim:** EDMP scores do not predict domain utility better than random chance because:

1. **Surface similarity ≠ training utility:** Embedding similarity captures lexical/semantic overlap, not gradient-level training signal
2. **Task exemplars are sparse:** Validation sets may not represent full downstream distribution
3. **Diversity term is arbitrary:** No theoretical grounding for why embedding space coverage predicts complementarity
4. **Scale mismatch:** Mid-scale embedder (E5) may not predict optimal mixtures for different target scales

**Strongest Objection:** The causal chain assumes embedding similarity → distributional alignment → training utility, but the second link is unproven. DoReMi's proxy model captures gradient-level signals that embeddings cannot.

### 7.3 Synthesis

**Resolution:** The thesis-antithesis tension can be resolved through empirical validation:

1. **H-M2 directly tests** the similarity → utility link via Kendall's τ correlation
2. **Ablation studies** can isolate diversity term contribution
3. **Cross-scale validation** addresses scale mismatch concern
4. **If τ > 0.5:** Embedding geometry is a valid proxy for training utility (thesis supported)
5. **If τ < 0.4:** Embeddings insufficient; gradient-level signals required (antithesis supported)

**Key Insight:** EDMP doesn't need to match DoReMi performance; it needs to beat random selection while being training-free. The value proposition is compute savings, not absolute performance.

### 7.4 Robustness Assessment

| Aspect | Robustness | Justification |
|--------|------------|---------------|
| Core Mechanism | Medium | Depends on unproven similarity → utility link |
| Falsifiability | High | Clear Kendall's τ threshold; binary outcome |
| Scope Boundaries | High | Well-defined applicability constraints |
| Mitigation Options | High | Multiple fallback strategies documented |

**Overall Robustness:** MEDIUM-HIGH

The hypothesis is well-structured with clear falsification criteria. Main risk is the unproven causal link, which will be directly tested.

---

## 8. Executive Summary

### 8.1 Overview

This verification plan decomposes the EDMP hypothesis into 4 sub-hypotheses forming a linear dependency chain. All hypotheses are MUST_WORK gates - failure at any step invalidates the methodology.

### 8.2 Key Points

- **4 sub-hypotheses:** H-E1 (existence), H-M1-M3 (3-step mechanism chain)
- **66% scope reduction:** 2 of 3 claims established; only PROVE_NEW claim verified
- **4-6 day timeline:** Sequential verification, ~150 GPU-hours
- **Clear falsification:** Kendall's τ < 0.4 rejects hypothesis
- **Phase 5 deferred:** Baseline comparison (DoReMi) handled in Phase 5

### 8.3 Decision Points

| Gate | Decision | If Pass | If Fail |
|------|----------|---------|---------|
| H-E1 | Scores computable? | → H-M1 | STOP |
| H-M1 | Embeddings semantic? | → H-M2 | STOP |
| H-M2 | τ > 0.5? | → H-M3 | STOP |
| H-M3 | ≥3% over random? | → Phase 5 | STOP |

### 8.4 Open Questions for Phase 2C

1. Which embedder (E5, BGE, OpenAI) produces most predictive scores?
2. Optimal sample size per domain for reliable embedding estimation?
3. Whether diversity term adds value over similarity alone?

---

## Appendix A: Variable Summary

| Variable | Value |
|----------|-------|
| hypothesis_id | H-EDMP-v1 |
| confidence_level | 0.75 |
| causal_chain_count | 3 |
| scope_reduction | 66% |
| transfer_validation | false |
| total_hypotheses | 4 |

---

## Appendix B: Phase 2A Traceability

| Phase 2A Section | Phase 2B Usage |
|------------------|----------------|
| core_statement | Section 1.1-1.2 |
| variables | Hypothesis specifications |
| causal_mechanism | H-M1, H-M2, H-M3 derivation |
| key_assumptions | Risk Analysis (Section 4) |
| predictions | Success criteria derivation |
| experimental_setup | Section 1.3-1.4 |

---

**Document Status:** COMPLETE
**Steps Completed:** [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
**Next Phase:** Step 10 - Finalize (verification_state.yaml generation)
