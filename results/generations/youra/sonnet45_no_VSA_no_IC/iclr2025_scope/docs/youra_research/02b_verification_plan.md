# Phase 2B: Verification Plan

**Generated**: 2026-08-20  
**Main Hypothesis**: H-ProvenanceCache-v1  
**Pipeline Project**: dd500899-44fd-44d5-b7ea-7d7ec8f5c571

---

## Main Hypothesis

**Title**: Provenance-Aware KV Cache Management for RAG-Based Long-Context QA

**Core Statement**: Under RAG-based long-context QA tasks (LongBench multi-doc QA, 8k-32k tokens), if we implement provenance-aware KV cache eviction with diversity-aware scoring (query tokens prioritized → diverse high-relevance passages → diverse low-relevance passages for contrastive evidence → redundant passages evicted), then answer accuracy at restrictive cache budgets (10-25% retention) will improve by ≥10% relative to uniform eviction baselines (H2O, StreamingLLM), because retrieval relevance scores and passage diversity jointly predict attention concentration and reasoning utility during answer generation.

**Null Hypothesis (H0)**: There is no significant difference in answer accuracy between provenance-aware eviction and uniform eviction (H2O baseline) at 10-25% cache budgets on LongBench multi-doc QA tasks (two-tailed t-test, α=0.05).

---

## Sub-Hypotheses Inventory

### H-E1: Relevance-Attention Correlation (EXISTENCE)

**Statement**: Retrieval relevance scores correlate moderately (Spearman ρ > 0.3) with attention weights during answer generation.

**Gate**: MUST_WORK (foundation assumption - if fails, entire provenance hypothesis invalid)

**Prerequisites**: None (first validation step)

**Validation Method**: Pilot 1 attention analysis
- Measure attention weights from generated tokens to query/passage tokens
- Compute Spearman correlation between retrieval scores and attention weights
- Stratify by query complexity (simple vs complex) and answer correctness
- Test with both BM25 and semantic retriever (DPR/Contriever)

**Success Criterion**: Spearman ρ > 0.3 for both BM25 and semantic retriever

**Falsifier**: If ρ ≤ 0.3 or negative correlation, retrieval scores do not align with LLM attention patterns → provenance hypothesis invalidated → Phase 0 routing

**Compute Budget**: 1-2 GPU-hours

**Archon Task ID**: 8e5db332-77b0-4e63-816f-99dac9f2fbeb

---

### H-M1: Tiered Eviction Single-Hop (MECHANISM)

**Statement**: Provenance-aware tiered eviction (query > high-rel > low-rel) achieves ≥5% accuracy gain at 25% cache budget on single-hop QA vs H2O baseline.

**Gate**: MUST_WORK (core mechanism validation before multi-hop complexity)

**Prerequisites**: [H-E1] (requires relevance-attention correlation)

**Validation Method**: Pilot 2 single-hop experiment
- Implement tiered eviction: Tier 0 (query + top-1 passage), Tier 1 (high-relevance passages), Tier 2 (low-relevance passages)
- Test on LongBench single-hop QA subset (controlled setting, no multi-hop dependencies)
- Compare ProvenanceCache vs H2O vs FullKV at 25% cache budget
- Measure answer accuracy (exact match or F1 score)

**Success Criterion**: ≥5% relative accuracy gain vs H2O baseline at 25% cache budget

**Falsifier**: If gain < 5% or ProvenanceCache performs worse than H2O, core tiering mechanism fails → Phase 2A-Dialogue modification

**Compute Budget**: 5-8 GPU-hours

**Archon Task ID**: c1c99fbd-6b3c-43a0-929f-a60b48e5ea17

---

### H-M2: Diversity Ablation (MECHANISM)

**Statement**: Diversity-aware scoring (MMR-inspired passage selection) outperforms pure relevance-based eviction by ≥5% accuracy on multi-hop questions.

**Gate**: SHOULD_WORK (enhancement mechanism - failure doesn't invalidate core approach)

**Prerequisites**: [H-M1] (requires base tiered eviction working)

**Validation Method**: Full experiment diversity ablation
- Compare ProvenanceCache-Full (with diversity) vs ProvenanceCache-RelevanceOnly (no diversity)
- Test on LongBench multi-hop QA subset
- Diversity metric: Embedding distance (sentence-transformers) + entity non-overlap
- Measure accuracy difference on multi-hop questions specifically

**Success Criterion**: ≥5% accuracy gain on multi-hop questions with diversity-aware scoring

**Falsifier**: If no accuracy difference or diversity version performs worse, diversity heuristic is ineffective → fall back to relevance-only tiering (still novel)

**Compute Budget**: Included in full experiment (15-20 GPU-hours total)

**Archon Task ID**: 58c68171-7024-4896-b583-1a7bdd68812e

---

### H-M3: Query Complexity Stratification (MECHANISM)

**Statement**: Simple queries (low entity density, short length) show higher query-token attention concentration than complex queries, validating adaptive tiering.

**Gate**: SHOULD_WORK (refinement for edge cases)

**Prerequisites**: [H-E1] (requires attention analysis infrastructure)

**Validation Method**: Pilot 1 stratified attention analysis
- Measure query-token attention concentration by query characteristics:
  - Simple queries: word count < 10, entity density < 0.3
  - Complex queries: word count ≥ 10, entity density ≥ 0.3
- Compute attention concentration ratio: query tokens / all context tokens
- Statistical test: two-sample t-test (simple vs complex queries)

**Success Criterion**: Simple queries show significantly higher query-token attention concentration (p < 0.05)

**Falsifier**: If no difference or reverse pattern, query-anchoring hypothesis fails → fall back to uniform tiering (conservative)

**Compute Budget**: Included in Pilot 1 (1-2 GPU-hours)

**Archon Task ID**: ab065c0e-5f5f-4598-a6b0-2292bb0aa821

---

### H-M4: Integrated Policy Target Performance (MECHANISM)

**Statement**: Full ProvenanceCache policy (tiered + diversity-aware) achieves ≥10% relative accuracy gain at 25% cache budget vs H2O on LongBench multi-doc QA (primary prediction P1).

**Gate**: MUST_WORK (final integrated validation - main hypothesis success criterion)

**Prerequisites**: [H-M1, H-M2] (requires both tiering and diversity components)

**Validation Method**: Full experiment main comparison
- Baselines: FullKV (upper bound), H2O (primary), StreamingLLM (architectural), Random (lower bound)
- Cache budgets: 10%, 25%, 50%, 75% (Pareto frontier analysis)
- Dataset: LongBench multi-doc QA full suite
- Statistical test: two-tailed t-test (n ≥ 100 questions per condition, α=0.05)
- Stratified analysis by question type (single-hop vs multi-hop)

**Success Criterion**: ≥10% relative accuracy gain at 25% cache budget with p < 0.05

**Falsifier**: If gain < 10% or p ≥ 0.05, integrated policy provides no practical benefit → Phase 0 routing (fundamental approach issue)

**Compute Budget**: 15-20 GPU-hours

**Archon Task ID**: a443e5b4-80b6-4064-9e6d-f781cc647004

---

## Dependency Graph (DAG)

```
H-E1 (MUST_WORK)
  ├─→ H-M1 (MUST_WORK)
  │     ├─→ H-M2 (SHOULD_WORK)
  │     │     ↓
  │     └─→ H-M4 (MUST_WORK)
  └─→ H-M3 (SHOULD_WORK)
```

**Critical Path**: H-E1 → H-M1 → H-M4 (all MUST_WORK gates, ~20 GPU-hours)

**Parallel Validation**: H-M3 (query complexity) can run with H-E1, H-M2 (diversity) validates during H-M4 full experiment

---

## Risk Analysis

### High-Risk Dependencies (MUST_WORK Gates)

**Risk 1: H-E1 Failure (Relevance-Attention Correlation)**
- **Likelihood**: Medium (BM25 lexical scores might not align with semantic reasoning)
- **Impact**: Critical (invalidates entire provenance hypothesis)
- **Mitigation**: Multi-retriever validation (BM25 + semantic DPR/Contriever) tests robustness
- **Fallback**: If both retrievers show ρ ≤ 0.3 → Phase 0 routing (fundamental assumption broken)

**Risk 2: H-M1 Failure (Single-Hop Tiering)**
- **Likelihood**: Low (H2O established attention-based eviction works)
- **Impact**: High (core mechanism validation)
- **Mitigation**: Single-hop controlled setting isolates tiering from multi-hop complexity
- **Fallback**: If < 5% gain → Phase 2A-Dialogue modification (adjust tiering policy, test alternative metadata)

**Risk 3: H-M4 Failure (Integrated Performance)**
- **Likelihood**: Medium (multi-hop complexity + diversity heuristic uncertainty)
- **Impact**: Critical (main hypothesis success criterion)
- **Mitigation**: Full cache budget range (10-75%) + stratified analysis isolates failure modes
- **Fallback**: If < 10% gain → Phase 0 routing if fundamental, or Phase 2A-Dialogue if integration issue

### Medium-Risk Enhancements (SHOULD_WORK Gates)

**Risk 4: H-M2 Failure (Diversity Ablation)**
- **Likelihood**: Medium (embedding-based diversity might miss temporal/causal dependencies)
- **Impact**: Low (falls back to relevance-only tiering, still novel)
- **Mitigation**: Qualitative failure analysis identifies diversity heuristic breakdown cases
- **Fallback**: Publish relevance-only tiering results, acknowledge diversity limitation

**Risk 5: H-M3 Failure (Query Complexity Stratification)**
- **Likelihood**: Low (intuitive from QA literature)
- **Impact**: Low (falls back to uniform query treatment)
- **Mitigation**: Conservative stratification thresholds (entity density, word count)
- **Fallback**: Uniform tiering for all queries (simpler policy)

### Compute Budget Risk

**Total Estimate**: ~25 GPU-hours (Pilot 1: 1-2, Pilot 2: 5-8, Full: 15-20)

**Risk**: Budget overrun if pilots fail and require re-runs

**Mitigation**: 
- Pilot 1 cheap validation (1-2 hrs) decides whether to continue before Pilot 2 investment
- Pilot 2 single-hop (5-8 hrs) validates mechanism before expensive full experiment
- Hard stop if H-E1 or H-M1 fail (no sunk cost fallacy)

---

## Timeline & Execution Order

### Stage 1: Foundation Validation (Pilot 1)
**Duration**: 1-2 GPU-hours  
**Hypotheses**: H-E1 (MUST_WORK), H-M3 (SHOULD_WORK)  
**Decision Point**: STOP if H-E1 fails (ρ ≤ 0.3) → Phase 0 routing

### Stage 2: Mechanism Validation (Pilot 2)
**Duration**: 5-8 GPU-hours  
**Hypotheses**: H-M1 (MUST_WORK)  
**Prerequisites**: H-E1 PASS  
**Decision Point**: STOP if H-M1 fails (< 5% gain) → Phase 2A-Dialogue modification

### Stage 3: Full Integration (Full Experiment)
**Duration**: 15-20 GPU-hours  
**Hypotheses**: H-M2 (SHOULD_WORK), H-M4 (MUST_WORK)  
**Prerequisites**: H-M1 PASS  
**Decision Point**: PASS to Phase 5 if H-M4 succeeds, Phase 0 if fails

**Total Sequential Duration**: ~25 GPU-hours worst-case, ~20 hrs if H-M2/H-M3 skipped

---

## Dialectical Analysis

### Thesis
RAG provenance metadata (relevance scores, passage boundaries, query/passage/generated token types) predicts KV cache utility better than uniform attention-based eviction because retrieval creates semantic structure that H2O/StreamingLLM ignore.

### Antithesis (Objections & Challenges)

1. **Retrieval Score Misalignment**: BM25 lexical scores might anti-correlate with semantic reasoning utility (Prof. Rex challenge)
2. **Negative Evidence Paradox**: Low-relevance passages might contain critical contrastive evidence for ruling out wrong answers (Prof. Rex challenge)
3. **Query Ambiguity**: Vague/complex queries break simple query-anchoring assumption (Prof. Rex challenge)
4. **Multi-Hop Dependency Blindness**: Embedding-based diversity heuristic might miss temporal/causal dependencies where passages are semantically dissimilar but logically connected

### Synthesis (Resolution Strategy)

1. **Multi-Retriever Validation**: Test with both BM25 (lexical) and DPR/Contriever (semantic) retrievers → H-E1 validates alignment for both
2. **Diversity-Aware Scoring**: MMR-inspired diverse passage retention preserves low-relevance contrastive evidence → H-M2 validates this explicitly
3. **Query Complexity Stratification**: Adaptive tiering based on entity density and word count handles ambiguous queries → H-M3 validates stratification
4. **Full Budget Range + Failure Analysis**: Test 10-75% cache budgets + qualitative analysis of diversity heuristic breakdown cases → identifies operating limits

**Key Insight**: Three-tier pilot sequence (attention analysis → single-hop → multi-hop) validates each component of the synthesis before expensive integration, avoiding open-ended optimization.

---

## Phase 5 Baseline Comparison Preview

**Note**: Phase 5 baseline comparison is deferred until after sub-hypothesis validation (Phase 2C → Phase 3 → Phase 4). Current hypothesis is a measurement study comparing ProvenanceCache vs existing methods (H2O, StreamingLLM), not adapting a baseline repository.

**Baseline Method**: H2O (Zhang et al., NeurIPS 2023) - 20% cache retention maintains accuracy on generation tasks

**Expected Performance**:
- **H2O baseline**: ~60% accuracy on LongBench multi-doc QA at 25% cache budget (extrapolated from H2O paper generation task results)
- **ProvenanceCache target**: ≥66% accuracy (≥10% relative gain)

**Phase 5 Comparison Strategy**: 
- If H-M4 passes (≥10% gain vs H2O in Phase 4), Phase 5 will adapt H2O implementation from KVCache-Factory repository for controlled comparison
- Matched experimental conditions: same model (Llama-2-7B), same dataset (LongBench), same cache budgets (10-75%)
- Statistical validation: two-tailed t-test, n ≥ 100 questions, α=0.05

---

## Next Steps

1. **Phase 2C (Experiment Design)**: Generate detailed experiment specifications for each sub-hypothesis (dataset splits, evaluation metrics, hyperparameters, ablation configurations)

2. **Phase 3 (Implementation Planning)**: Create PRDs, architecture documents, and Archon task decomposition for Pilot 1, Pilot 2, and Full Experiment codebases

3. **Phase 4 (PoC Validation)**: Implement and validate each sub-hypothesis in sequence (H-E1 → H-M1 → H-M4), with MUST_WORK gate checks at each stage

4. **Phase 5 (Baseline Comparison)**: Adapt H2O baseline for controlled comparison if Phase 4 succeeds

---

## Verification State Metadata

**Project Name**: Provenance-Aware KV Cache Management  
**Main Hypothesis ID**: H-ProvenanceCache-v1  
**Created**: 2026-08-20  
**Schema Version**: 3.5  
**Archon Pipeline Project ID**: dd500899-44fd-44d5-b7ea-7d7ec8f5c571  

**Sub-Hypothesis Task Mapping**:
- H-E1: 8e5db332-77b0-4e63-816f-99dac9f2fbeb
- H-M1: c1c99fbd-6b3c-43a0-929f-a60b48e5ea17
- H-M2: 58c68171-7024-4896-b583-1a7bdd68812e
- H-M3: ab065c0e-5f5f-4598-a6b0-2292bb0aa821
- H-M4: a443e5b4-80b6-4064-9e6d-f781cc647004

**Execution Mode**: UNATTENDED (batch mode, no user confirmation)
