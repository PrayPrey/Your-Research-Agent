# Phase 2B: Verification Planning Output
**Generated**: 2026-08-24T07:30:00Z  
**Workflow**: phase2b-planning  
**Execution Mode**: UNATTENDED

---

## Main Hypothesis

**ID**: H-FailureRouting-v1  
**Title**: Failure-Type Routing Framework for Automated LLM Diagnosis and Correction

**Statement**:  
Under TruthfulQA single-entity factual questions with gold-labeled model failures, automated failure-type routing (entity-error → RAG, non-entity-error → COT) based on attention pattern analysis will achieve higher correction success rates than mismatched routing, because entity-substitution failures concentrate attention on incorrect entities (low entropy) while non-entity failures distribute attention broadly (high entropy).

**Controlled Variables**:
- Dataset: TruthfulQA single-entity factual questions subset
- Models: GPT-3.5 and Llama-2-7B
- NER Tool: spaCy
- Retrieval Corpus: Wikipedia
- Sample Size: N=100 (50 entity-error, 50 non-entity-error per model)
- Significance Level: α = 0.05
- Correction Threshold: ≥20 percentage points or ≥50% relative improvement

---

## Sub-Hypotheses Breakdown

### H-C1: Pre-Validation Conditions (CONDITION)
**Type**: MUST_WORK  
**Status**: READY (no prerequisites)  
**Statement**: Pre-validation conditions are met: NER tool achieves ≥90% accuracy on entity identification, and Wikipedia achieves ≥90% coverage for entity-error test cases.

**Rationale**: Validates measurement assumptions A1 (NER accuracy) and A2 (Wikipedia coverage) before pattern detection experiments. Foundation for all subsequent hypotheses.

**Falsification**: If NER accuracy < 90% OR Wikipedia coverage < 90%, measurement validity compromised.

---

### H-E1: Attention Entropy Difference (EXISTENCE)
**Type**: MUST_WORK  
**Status**: NOT_STARTED (prerequisite: H-C1)  
**Statement**: Entity-substitution errors exhibit significantly lower attention entropy over NER-identified entity spans compared to non-entity errors (p < 0.05, entity-error mean < non-entity-error mean).

**Rationale**: Tests causal mechanism Step 1 (Pattern Emergence). If attention pattern signature doesn't exist, entire routing framework fails.

**Falsification**: p ≥ 0.05 OR opposite direction (entity-error entropy ≥ non-entity-error entropy) in either GPT-3.5 or Llama-2-7B.

**Maps to Phase 2A Prediction**: P1 (primary prediction)

---

### H-M1: Entropy-Based Classification (MECHANISM)
**Type**: MUST_WORK  
**Status**: NOT_STARTED (prerequisite: H-E1)  
**Statement**: Attention entropy classification (low vs high threshold) correctly identifies failure types with ≥70% accuracy compared to gold-labeled entity-error vs non-entity-error categories.

**Rationale**: Tests causal mechanism Step 2 (Diagnostic Routing). Validates that entropy difference is actionable for classification, not just statistically significant.

**Falsification**: Classification accuracy < 70% on held-out test set in either model.

**Maps to Phase 2A Prediction**: Extension of P1 (converts statistical difference to classification utility)

---

### H-M2: Matched Correction Effectiveness (MECHANISM)
**Type**: MUST_WORK  
**Status**: NOT_STARTED (prerequisite: H-M1)  
**Statement**: Matched correction routing (entity-error → RAG) achieves higher success rates than mismatched routing (entity-error → COT) by ≥20 percentage points or ≥50% relative improvement, replicated across GPT-3.5 and Llama-2-7B.

**Rationale**: Tests causal mechanism Step 3 (Correction Effectiveness). Proves routing framework has practical utility, not just diagnostic capability.

**Falsification**: Difference < 20 points AND relative improvement < 50% in either model, OR opposite direction (COT > RAG).

**Maps to Phase 2A Prediction**: P2 (correction validation)

---

## Dependency Graph

```
H-C1 (Pre-validation)
  ↓
H-E1 (Pattern Detection)
  ↓
H-M1 (Classification)
  ↓
H-M2 (Correction)
```

**Sequential Validation Logic**:
1. H-C1 validates measurement assumptions (NER, Wikipedia)
2. H-E1 proves attention pattern signature exists
3. H-M1 proves pattern enables classification
4. H-M2 proves classification enables effective correction

**All gates are MUST_WORK** — failure at any level invalidates routing framework.

---

## Risk Analysis

### High-Risk Hypotheses (Blocking)
- **H-E1**: If attention entropy shows no difference or opposite direction, entire mechanism fails. Multi-model replication (GPT-3.5 + Llama-2-7B) reduces architecture-specific pattern risk.
- **H-C1**: If NER or Wikipedia coverage fails validation, measurement validity compromised. Pre-validation step mitigates this before expensive experiments.

### Moderate-Risk Hypotheses
- **H-M1**: Even if H-E1 passes (statistical difference), classification may fail if entropy distributions overlap significantly. 70% accuracy threshold set conservatively.
- **H-M2**: Correction success depends on RAG retrieval quality and COT baseline performance. Pilot experiment (N=20) grounds threshold expectations.

### Mitigation Strategies
1. **Multi-model testing**: GPT-3.5 + Llama-2-7B replication reduces architecture-specific risk
2. **Pre-validation**: H-C1 validates assumptions before pattern experiments
3. **Pilot grounding**: N=20 pilot establishes realistic correction baselines (mentioned in Phase 2A Exchange 13)
4. **Scope restriction**: Single-entity subset eliminates ambiguous hybrid failures

---

## Timeline Estimate

**Phase 2C (Experiment Design)**: 4 experiment designs (1 per sub-hypothesis)  
**Phase 3 (Implementation Planning)**: 4 PRD/Architecture/PRP packages  
**Phase 4 (PoC Validation)**: Sequential execution H-C1 → H-E1 → H-M1 → H-M2  
**Phase 5 (Baseline Comparison)**: Compare matched routing vs random routing and aggregate correction baselines

**Critical Path**: H-C1 → H-E1 → H-M1 → H-M2 (no parallelization due to dependencies)

---

## Dialectical Analysis

**Thesis**: Attention patterns enable automated failure diagnosis with causal correction validation.

**Antithesis**: Attention patterns may be architecture-specific, dataset-specific, or too noisy for reliable classification.

**Synthesis**: Multi-model testing (GPT-3.5 + Llama-2-7B) + explicit scope boundaries (TruthfulQA, entity-errors only) + pre-validation steps establish proof-of-concept while acknowledging generalization as future work. Conservative thresholds (≥70% classification, ≥20 point correction improvement) reduce false positive risk.

---

## Phase 5 Baseline Comparison (Deferred)

**Baselines to Compare**:
1. **Random Routing**: Assign entity-errors to RAG or COT randomly (50/50 split) — measures improvement over chance
2. **Aggregate Correction**: Apply single correction method (RAG or COT) to all failures regardless of type — tests value of failure-type routing

**DETERMINES_SUCCESS Gate**: Main hypothesis passes if matched routing outperforms both baselines. Phase 5 validates end-to-end framework after Phase 4 proves individual mechanisms.

---

## Open Questions (Future Work)

1. **Generalization beyond entity-errors**: Do reasoning errors, knowledge gaps, hybrid failures have distinct attention signatures?
2. **Automated failure classification**: Can entropy-based classification replace manual gold labels for deployment?
3. **Cross-benchmark generalization**: Do patterns generalize to FEVER, adversarial datasets, other factuality benchmarks?
4. **Scalability**: Can framework handle 1000s of failures for systematic failure-mode discovery?

---

## Archon Project Status

**Pipeline Project**: Not created (Archon CLI unavailable in current environment)  
**Degraded Mode**: verification_state.yaml created without Archon integration  
**Impact**: Manual task tracking required for Phase 3/4, no automated Archon task updates

---

## Next Steps

1. **Phase 2C**: Generate experiment design for H-C1 (pre-validation conditions)
2. **Hypothesis Loop**: Process sub-hypotheses sequentially H-C1 → H-E1 → H-M1 → H-M2 through Phase 2C → Phase 3 → Phase 4
3. **Phase 5**: Baseline comparison after all sub-hypotheses validated
4. **Phase 6**: Paper writing if DETERMINES_SUCCESS gate passes

---

**Status**: Phase 2B Complete — 4 sub-hypotheses generated, dependency graph established, ready for Phase 2C experiment design.
