# Phase 2B: Verification Planning
# Hypothesis Decomposition & Experimental Strategy

**Generated**: 2026-08-28T08:15:00Z  
**Main Hypothesis**: H-QualityScaling-v1  
**Execution Mode**: UNATTENDED  
**Pipeline Project ID**: 099e4908-7e83-4727-ba82-a135512ff747

---

## Executive Summary

Phase 2B decomposes the main hypothesis "Data Quality as Compute Efficiency Multiplier in FM Scaling Laws" into 4 testable sub-hypotheses with clear dependency structure and gate requirements.

**Key Results**:
- 4 sub-hypotheses generated (1 EXISTENCE, 2 MECHANISM, 1 CONDITION)
- Linear dependency chain: H-E1 → H-M1 → H-M2 → H-C1
- Critical path length: 4 sequential validation steps
- 3 MUST_WORK gates (foundation hypotheses), 1 SHOULD_WORK gate (generalization condition)

---

## Main Hypothesis

**ID**: H-QualityScaling-v1  
**Title**: Data Quality as Compute Efficiency Multiplier in Foundation Model Scaling Laws

**Statement**:
> Under foundation model pretraining conditions, if data quality Q(D) is increased through systematic curation (deduplication, filtering, mixing), then model performance at fixed compute budget improves following a predictable tradeoff surface, because Q(D) acts as a compute efficiency multiplier where higher quality data reduces compute required to reach target performance.

**Source**: `03_refinement.yaml` Section 1.1

---

## Sub-Hypothesis Decomposition

### H-E1: Existence of Measurable Quality Metrics (MUST_WORK)

**Type**: EXISTENCE  
**Status**: READY (no prerequisites)  
**Gate**: MUST_WORK

**Statement**:
Data quality metrics Q(D) (dedup ratio, domain diversity, perplexity, token efficiency) are measurable and correlate with information density in foundation model training data.

**Rationale**:
Foundation hypothesis. If Q(D) metrics don't correlate with information density, entire framework collapses. Must establish measurement validity before testing mechanisms.

**Success Criteria**:
- Pearson correlation r > 0.5 between each Q(D) component and entropy-based information density
- All 4 metrics (dedup, diversity, perplexity, efficiency) show monotonic relationship with information density
- Measurements reproducible across C4 subsets (variance < 10%)

**Experimental Approach**:
1. Sample C4 subsets with controlled quality variations
2. Compute Q(D) metrics: dedup_ratio, domain_diversity (Herfindahl index), avg_perplexity, token_efficiency
3. Measure information density via token-level entropy and n-gram redundancy
4. Statistical correlation analysis + scatter plots

**Dependencies**: None

---

### H-M1: Information Density Mechanism (MUST_WORK)

**Type**: MECHANISM  
**Status**: NOT_STARTED (awaits H-E1)  
**Gate**: MUST_WORK

**Statement**:
Data curation (deduplication, filtering, domain mixing) increases information density per token, measured by entropy reduction and Fisher information increase.

**Rationale**:
Causal mechanism step 1-2 from refinement (Section 1.3). Proves Q(D) improvements create measurable information density gains. Required for compute multiplier claim.

**Success Criteria**:
- Entropy reduction >20% after aggressive deduplication (95% vs 0%)
- Fisher information matrix trace increases >15% with higher Q(D)
- Effect holds across 3 curation dimensions (dedup, filter, mix)

**Experimental Approach**:
1. Train small probe models (125M params) on curated vs uncurated C4 subsets
2. Measure gradient statistics (Fisher information) during training
3. Compute token-level entropy and perplexity distributions
4. Ablation study: vary one quality dimension at a time

**Dependencies**: H-E1 (requires validated Q(D) metrics)

---

### H-M2: Compute Efficiency Multiplier (MUST_WORK)

**Type**: MECHANISM  
**Status**: NOT_STARTED (awaits H-M1)  
**Gate**: MUST_WORK

**Statement**:
Higher data quality Q(D) reduces compute required to reach target performance, producing convex iso-performance curves with >15% compute reduction per Q(D) standard deviation increase.

**Rationale**:
Core scaling law prediction (Prediction P1 from Section 1.6). Directly tests compute-quality tradeoff surface. Failure invalidates resource allocation claims.

**Success Criteria**:
- Iso-performance curves convex (positive second derivative) for 2+ target loss values
- >15% compute reduction when Q(D) increases by 1 std dev
- Power-law relationship holds in log-log plot (R² > 0.85)

**Experimental Approach**:
1. Grid search over (compute budget, Q(D) level) combinations
2. Train 1B parameter models at each grid point to completion
3. Plot iso-performance contours (points with same final loss)
4. Fit convexity test + measure compute savings per Q(D) unit

**Scale**: ~20 training runs (5 compute levels × 4 quality levels)

**Dependencies**: H-M1 (requires proven information density mechanism)

---

### H-C1: Cross-Scale Stationarity (SHOULD_WORK)

**Type**: CONDITION  
**Status**: NOT_STARTED (awaits H-M2)  
**Gate**: SHOULD_WORK

**Statement**:
Q(D) composition weights are stationary across model scales (1B, 7B, 30B parameters), enabling universal quality metric.

**Rationale**:
Generalization test (Assumption A2 from Section 1.4). Validates whether same Q(D) formula works across scales. Failure limits applicability but doesn't invalidate core mechanism.

**Success Criteria**:
- Q(D) weights fitted on 1B models generalize to 7B/30B with <20% performance degradation
- Rank correlation of quality interventions preserved across scales (Spearman ρ > 0.7)
- If stationarity fails, document scale-specific weights

**Experimental Approach**:
1. Fit Q(D) weights via validation on 1B models (from H-M2 data)
2. Test fitted Q(D) on 7B and 30B models at 3 quality levels each
3. Compare predicted vs actual compute-performance tradeoffs
4. If failure: fit scale-specific weights and document regime boundaries

**Scale**: ~9 additional runs (2 scales × 3 quality levels + 3 baselines)

**Gate Rationale**: SHOULD_WORK because scale-specific weights still valuable (domain adaptation). Not foundational failure.

**Dependencies**: H-M2 (requires working Q(D) formula to test stationarity)

---

## Dependency Graph (DAG)

```
H-E1 (EXISTENCE)
  ↓
H-M1 (MECHANISM: Information Density)
  ↓
H-M2 (MECHANISM: Compute Multiplier)
  ↓
H-C1 (CONDITION: Stationarity)
```

**Critical Path**: 4 hypotheses, fully sequential  
**Parallelization Opportunities**: None (linear dependency chain)

---

## Risk Analysis

### High-Risk Gates (MUST_WORK)

1. **H-E1**: If Q(D) metrics don't correlate with information density → fundamental measurement failure, invalidates framework
2. **H-M1**: If curation doesn't increase information density → causal mechanism broken, no theoretical foundation
3. **H-M2**: If no compute-quality tradeoff exists → core claim false, entire scaling law fails

### Mitigation Strategies

- **H-E1 failure**: Explore alternative quality proxies (e.g., model-based quality scores, semantic diversity)
- **H-M1 failure**: Test non-linear Q(D) formulations or interaction effects
- **H-M2 failure**: Route to Phase 0 (fundamental rethink) or Phase 2A-Dialogue (refine mechanism)

### Medium-Risk Gates (SHOULD_WORK)

1. **H-C1**: Stationarity failure → domain-specific Q(D) weights still useful, limits universal applicability

---

## Resource Budget

### Compute Requirements

- **H-E1**: ~10 GPU-hours (125M probe models, entropy analysis)
- **H-M1**: ~50 GPU-hours (125M models with gradient logging, ablation studies)
- **H-M2**: ~2000 GPU-hours (20 × 1B models trained to convergence)
- **H-C1**: ~1800 GPU-hours (6 × 7B models + 3 × 30B models)

**Total**: ~3860 GPU-hours (assumes V100 equivalent)

### Dataset Requirements

- C4 dataset (publicly available via HuggingFace)
- Subset sizes: 10GB (H-E1), 50GB (H-M1), 200GB (H-M2/H-C1)
- Storage: ~500GB total with curation variations

---

## Timeline & Phases

### Phase 2C: Experiment Design (per hypothesis)
- Draft detailed experiment spec (metrics, baselines, ablations)
- Estimated: 4 × Level 1.5 specs

### Phase 3: Implementation Planning
- Generate PRD, Architecture, PRP for each hypothesis
- Complexity tiers: H-E1 (Tier 1), H-M1 (Tier 2), H-M2 (Tier 2), H-C1 (Tier 3)

### Phase 4: PoC Validation
- Execute experiments, validate MUST_WORK gates
- Critical: H-E1, H-M1, H-M2 must pass before Phase 5

### Phase 5: Baseline Comparison
- Compare Q(D)-optimized training vs Chinchilla baseline
- DETERMINES_SUCCESS gate: our method must outperform standard scaling

---

## Gate Strategy

### MUST_WORK Gates (3)
- **Purpose**: Foundation hypotheses; failure blocks Phase 5
- **Action on PARTIAL**: 1 modification attempt → Phase 2A-Dialogue if still fails
- **Action on FAIL**: Route to Phase 0 (fundamental flaw)

### SHOULD_WORK Gates (1)
- **Purpose**: Generalization/condition tests; failure doesn't block Phase 5
- **Action on PARTIAL/FAIL**: Document limitation, proceed with validated scope

### Phase 5 DETERMINES_SUCCESS
- **Trigger**: All MUST_WORK gates passed
- **Criterion**: Our Q(D)-optimized approach outperforms Chinchilla baseline
- **Action on PASS**: Proceed to Phase 6 (paper writing)
- **Action on PARTIAL**: Route to Phase 0 (approach fundamentally inferior)

---

## Dialectical Analysis

### Thesis
Data quality Q(D) as scalar compute efficiency multiplier enables predictive resource allocation via learnable linear projection from multi-dimensional quality metrics.

### Antithesis
Multi-dimensional quality interactions (e.g., dedup helpful at small scale, harmful at large scale) require complex non-linear model. Linear scalar Q(D) oversimplifies.

### Synthesis
Start with learnable linear projection Q(D) (validated via H-E1/H-M1). Test stationarity empirically (H-C1). Accept domain-specific or scale-specific weights if needed. Theory remains valid with bounded applicability.

**Resolution**: Stationarity is empirical question, not theoretical requirement. SHOULD_WORK gate on H-C1 reflects this.

---

## Success Metrics

### Phase 2B Completion Criteria ✓
- [x] Main hypothesis parsed from Phase 2A outputs
- [x] 4 sub-hypotheses generated with clear statements
- [x] Dependency graph constructed (DAG)
- [x] Gate types assigned (3 MUST_WORK, 1 SHOULD_WORK)
- [x] Risk analysis completed
- [x] Timeline/resource budget estimated
- [x] Verification state initialized

### Readiness for Phase 2C
- H-E1 status: READY (no prerequisites)
- Experiment design template available
- Controlled variables defined (from 03_refinement.yaml Section 1.2)

---

## Controlled Variables (from Phase 2A)

**Dataset**: C4 (Colossal Clean Crawled Corpus)  
**Model**: GPT-2 architecture (decoder-only transformer)  
**Optimizer**: AdamW with fixed learning rate schedule  
**Hyperparameters**:
- Model sizes: 1B, 7B, 30B parameters
- Batch size: fixed per scale
- Learning rate: Chinchilla-optimal schedule
- Training seeds: 3 per condition

---

## Next Steps

1. **Immediate**: Begin Phase 2C with H-E1 (experiment design generation)
2. **Sequence**: Process hypotheses in dependency order (H-E1 → H-M1 → H-M2 → H-C1)
3. **Gate enforcement**: Stop pipeline if any MUST_WORK gate fails after modification attempt

---

## Appendix: Phase 2A Source Files

- `03_refinement.yaml`: Main hypothesis, variables, predictions, mechanism
- `02_synthesis.yaml`: Measurement plan, validation strategy
- `01_round_table/final_opinions.yaml`: Agent consensus on novelty, falsifiability, significance

**Phase 2B completed**: 2026-08-28T08:15:00Z
