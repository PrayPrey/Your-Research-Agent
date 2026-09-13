# Verification Plan: Curation Parameter Dose-Response

**Date:** 2026-08-28
**Hypothesis ID:** H-CPDR-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under LLM pretraining on English web text corpora, if data curation parameters (perplexity filtering threshold, deduplication stringency) are systematically varied in controlled ablation, then quantifiable dose-response relationships with downstream benchmark performance will emerge, because there exists an optimal balance between data quality (strict filtering) and data diversity (permissive filtering).

### 1.2 Alternative Hypothesis (H0)
There is no non-monotonic relationship between curation parameters and benchmark performance; stricter filtering always improves or always harms performance monotonically, or curation parameters have no measurable effect on downstream benchmarks.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | RedPajama-v2 (subset) (standard) | Large-scale web corpus with raw and filtered versions; allows controlled parameter variation |
| **Model** | GPT-2 architecture variants | Well-characterized architecture with known scaling behavior; 125M/350M/1B checkpoints available |

**Dataset Details:**
- Source: togethercomputer/RedPajama-Data-v2
- Path: HuggingFace: togethercomputer/RedPajama-Data-v2

**Model Details:**
- Type: decoder-only transformer
- Source: Standard GPT-2 implementation (HuggingFace Transformers)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| No Filtering | Raw corpus without perplexity filtering or deduplication | RedPajama-v2 |
| RedPajama Defaults | Perplexity and dedup thresholds from RedPajama paper | RedPajama-v2 |
| CPDR-Optimized | Parameters selected via dose-response sweep | RedPajama-v2 |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | KenLM 5-gram perplexity is a valid proxy for data quality | Used by CCNet, C4, RedPajama pipelines; correlates with human quality judgments | Would need alternative quality metric (classifier-based, BERT perplexity) |
| A2 | 125M model benchmark behavior is informative for larger scales | Scaling laws literature shows consistent relative ordering | Would need to run full sweep at 1B+ scale (10x compute increase) |
| A3 | MinHash deduplication with Jaccard threshold captures relevant near-duplicates | Standard in text deduplication; validated against manual inspection | Semantic deduplication (embedding-based) might be required |
| A4 | Benchmark ensemble (HellaSwag, ARC-Easy, PIQA, WinoGrande) measures general reasoning | These benchmarks target different reasoning facets; ensemble reduces noise | Would need task-specific analysis instead of aggregate score |
| A5 | 10B tokens is sufficient to observe curation effects at 125M scale | Chinchilla-optimal for 125M is ~2.5B; 10B provides 4x overtraining for signal | Would need longer training or smaller models |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First controlled dose-response study for LLM curation parameters with proper confound control (fixed-token design)

**Key Innovation:** Treating curation parameters as continuous variables and mapping their effect surfaces, rather than comparing discrete pipeline configurations

**Differentiation:**
- vs DataComp (image curation sweeps): DataComp focused on vision; this extends to LLM pretraining with text-specific parameters
- vs How to Train Data-Efficient LLMs: That work studied perplexity filtering but varied multiple factors; this isolates each parameter
- vs RedPajama, Dolma pipeline papers: Those report final configurations without systematic ablation of individual parameters

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Dose-Response Existence**

**Statement**: Under LLM pretraining with fixed token budget, if curation parameters (perplexity threshold, deduplication stringency) are varied, then non-monotonic (concave) dose-response relationships will be observed in benchmark performance, because an optimal balance between quality and diversity exists.

**Rationale** (2-3 sentences):
This hypothesis validates that the phenomenon we study actually exists. If no non-monotonic relationship exists, the entire mechanism hypothesis chain becomes moot. It is the foundation for all subsequent hypotheses.

**Variables** (from Phase 2A):
- Independent: Perplexity Threshold (none to p90), Deduplication Stringency (none to exact_plus_fuzzy)
- Dependent: Benchmark Ensemble Score (PC1 of HellaSwag, ARC-Easy, PIQA, WinoGrande)
- Controlled: Training Token Budget (10B), Training Hyperparameters, Evaluation Set Integrity, Random Seed (3 seeds)

**Verification Protocol** (3-5 steps, 1 sentence each):
1. Run parameter sweep across perplexity thresholds (none, p10, p20, ..., p90) at 125M scale.
2. Run parameter sweep across deduplication levels (none, fuzzy_0.7, fuzzy_0.85, exact, exact_plus_fuzzy).
3. Fit polynomial regression (linear, quadratic, cubic) and compare via AIC/BIC.
4. Identify peak location if quadratic/cubic model selected over linear.

**Success Criteria** (PoC: Direction-based):
- Primary: Quadratic or higher-order model selected over linear (AIC/BIC)
- Secondary: Peak identifiable within parameter range

**Failure Response**:
- IF fails: ABANDON (entire hypothesis invalid if no dose-response exists)

**Dependencies**: None

**Source**: Phase 2A SH1, Prediction P1

---
**H-M1: Noise Dilution Mechanism**

**Statement**: Under LLM pretraining, if low perplexity thresholds include noisy/irrelevant data, then learning signal will be diluted, reducing sample efficiency, because high-perplexity samples often contain malformed or off-topic content.

**Rationale** (2-3 sentences):
This tests the first causal step: that noise in training data actually harms learning. Without this mechanism, the observed dose-response could be attributed to other factors. Standard observation in data curation literature supports this.

**Variables** (from Phase 2A):
- Independent: Perplexity Threshold (none, p10, p20)
- Dependent: Training loss convergence rate, Sample efficiency
- Controlled: Model architecture, Evaluation protocol

**Verification Protocol** (3-5 steps, 1 sentence each):
1. Train models with no-filter vs p20 filter on same token budget.
2. Measure loss curves and convergence rate.
3. Compare final benchmark performance.
4. Verify that filtered data shows faster convergence.

**Success Criteria** (PoC: Direction-based):
- Primary: Filtered model converges faster than no-filter baseline
- Secondary: Filtered model achieves higher benchmark score

**Failure Response**:
- IF fails: PIVOT (try alternative quality metrics)

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---
**H-M2: Quality-Diversity Tradeoff**

**Statement**: Under LLM pretraining, if noise is removed via filtering, then benchmark performance improves up to a point, but further filtering reduces performance, because excessively strict filtering removes diverse, edge-case, or domain-specific content.

**Rationale** (2-3 sentences):
This tests the second causal step: that overly strict filtering harms performance by reducing coverage. This mechanism explains why the dose-response curve is non-monotonic. Prior work (arXiv:2405.20541) notes optimal thresholds vary.

**Variables** (from Phase 2A):
- Independent: Perplexity Threshold (p50, p60, p70, p80, p90)
- Dependent: Benchmark Ensemble Score, Coverage diversity metrics
- Controlled: Token budget, Model architecture

**Verification Protocol** (3-5 steps, 1 sentence each):
1. Compare moderate filtering (p40-p60) vs strict filtering (p80-p90).
2. Measure benchmark performance at each threshold.
3. Calculate data diversity metrics (vocabulary coverage, topic distribution).
4. Verify that strict filtering reduces diversity AND performance.

**Success Criteria** (PoC: Direction-based):
- Primary: p90 (strictest) underperforms p50-p60 (moderate) on benchmarks
- Secondary: Diversity metrics decrease with stricter filtering

**Failure Response**:
- IF fails: EXPLORE (check if effect exists only for specific benchmarks)

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 3

---
**H-M3: Optimal Balance Point**

**Statement**: Under the quality-diversity tradeoff, if both extremes (no filter, strict filter) underperform, then an optimal balance point exists where quality and diversity are maximized, because the dose-response curve is concave with a measurable peak.

**Rationale** (2-3 sentences):
This tests the core claim that an optimal threshold can be identified. DataComp found such optima for vision; this validates the same pattern for LLM pretraining. This is the actionable output of the research.

**Variables** (from Phase 2A):
- Independent: Perplexity Threshold (full sweep)
- Dependent: Benchmark Ensemble Score
- Controlled: All other factors

**Verification Protocol** (3-5 steps, 1 sentence each):
1. Plot full dose-response curve from sweep data.
2. Fit polynomial and identify peak via derivative analysis.
3. Verify peak is within parameter range (not at boundary).
4. Calculate confidence interval for optimal threshold.

**Success Criteria** (PoC: Direction-based):
- Primary: Peak identified within p20-p80 range (not at boundary)
- Secondary: 95% CI for peak does not span >3 threshold levels

**Failure Response**:
- IF fails: DOCUMENT (plateau may exist instead of peak)

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 4

---
**H-M4: Scale-Invariant Optima**

**Statement**: Under the optimal curation parameters identified at 125M scale, if the same parameters are applied at 1B scale, then relative performance rankings will be preserved, because scaling laws show consistent relative ordering.

**Rationale** (2-3 sentences):
This tests whether the optimal parameters transfer across scales. If they do not, the practical value is limited. This is a key tension identified in Phase 2A.

**Variables** (from Phase 2A):
- Independent: Model Size (125M, 1B), Perplexity Threshold (optimal from H-M3)
- Dependent: Benchmark Ensemble Score relative to RedPajama defaults
- Controlled: Compute-matched training (same effective FLOPs)

**Verification Protocol** (3-5 steps, 1 sentence each):
1. Identify optimal threshold at 125M scale from H-M3.
2. Train 1B model with optimal threshold vs RedPajama defaults.
3. Compare relative improvement at 1B vs 125M.
4. Verify optimal threshold at 1B is within ±2 percentile points of 125M optimum.

**Success Criteria** (PoC: Direction-based):
- Primary: Optimal threshold at 1B within ±20% of 125M optimum
- Secondary: CPDR-optimized outperforms defaults at both scales

**Failure Response**:
- IF fails: DOCUMENT (scale-specific optima as finding)

**Dependencies**: H-M3

**Source**: Phase 2A Prediction P3, Causal Step 4

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Non-monotonic dose-response exists | STOP - hypothesis invalid |
| H-M1 | MUST_WORK | Noise dilution mechanism confirmed | PIVOT to alternative metrics |
| H-M2 | SHOULD_WORK | Quality-diversity tradeoff validated | EXPLORE specific benchmarks |
| H-M3 | SHOULD_WORK | Optimal peak identified | DOCUMENT plateau finding |
| H-M4 | SHOULD_WORK | Scale transfer validated | DOCUMENT scale-specific optima |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Assumption Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Perplexity not valid quality proxy | A1 | H-E1, H-M1, H-M2 | High |
| R2: Small model behavior not informative | A2 | H-M4 | High |
| R3: MinHash misses semantic duplicates | A3 | H-E1 | Medium |
| R4: Benchmark ensemble not representative | A4 | All | Medium |
| R5: Insufficient training tokens | A5 | H-E1, H-M1 | Low |

### 4.2 Mitigation Strategies

**R1: Perplexity Validity**
- Prevention: Validate KenLM correlation with human quality judgments on sample
- Detection: Compare with classifier-based quality scores
- Response: PIVOT to alternative metric if correlation < 0.5

**R2: Scale Transfer**
- Prevention: Run targeted 1B validation runs early
- Detection: Monitor loss curves for scale-dependent behavior
- Response: Document as scale-specific finding if optima differ

**R3: Deduplication Coverage**
- Prevention: Combine fuzzy + exact deduplication
- Detection: Manual inspection of sample duplicates
- Response: Add semantic deduplication layer if needed

**R4: Benchmark Representativeness**
- Prevention: Use ensemble to reduce single-benchmark bias
- Detection: Analyze individual benchmark variance
- Response: Report per-benchmark results in addition to ensemble

**R5: Token Budget**
- Prevention: Use 4x Chinchilla-optimal tokens (10B for 125M)
- Detection: Monitor loss convergence
- Response: Extend training if not converged

---

## 5. Dependency Graph

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism 1]
    H-M1 ← H-E1
         │
         ▼
[Level 2 - Mechanism 2]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Mechanism 3]
    H-M3 ← H-M2
         │
         ▼
[Level 4 - Mechanism 4]
    H-M4 ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5 │ W6 │ W7
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │         │ ◆       │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │         │ ████    │
  H-M4           │         │         │         │         │ ████
  [Gate 2]       │         │         │         │         │    ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4
**Total Duration:** 7 weeks (2 + 2 + 1 + 1 + 1)
**Slack Available:** 0 weeks (all sequential)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Data curation parameters exhibit non-monotonic dose-response relationships with benchmark performance, and optimal parameters can be identified via systematic sweep.

**Supporting Evidence:**
1. Information theory: noise dilutes learning signal
2. DataComp (vision): demonstrated optima exist for image curation
3. All major LLM pipelines use intermediate thresholds (not extremes)

**Strengths:**
- Clear causal mechanism grounded in information theory
- Precedent from vision domain (DataComp)
- Testable predictions with quantitative criteria

### 6.2 Antithesis (H0-Based)

**Null Hypothesis:** There is no non-monotonic relationship; stricter filtering always improves or always harms performance monotonically, or curation parameters have no measurable effect.

**Counter-Arguments:**
1. Scaling laws may override curation effects at sufficient scale
2. Benchmark ensemble may be insensitive to data quality differences
3. Optimal thresholds may be dataset-specific, not generalizable

**Conditions Under Which H0 Would Be Supported:**
- R² > 0.9 for linear fit across all parameter sweeps
- No identifiable peak within parameter range
- Variance across seeds exceeds variance across parameters

### 6.3 Synthesis

The verification plan addresses this dialectic through sequential hypothesis testing with gate conditions:

1. **H-E1 establishes existence first:** If no dose-response exists, we accept H0 early
2. **H-M1-M4 test mechanism sequentially:** Each step can fail independently
3. **Gate conditions allow early detection:** MUST_WORK gates prevent wasted effort

**Resolution Path:**
- Full Support: All gates pass → Thesis validated
- Partial Support: Some H-M fail → Refined thesis with documented limitations
- No Support: H-E1 or H-M1 fail → H0 supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Dose-response exists | May be artifact | H-E1 test with polynomial model selection |
| Mechanism | Noise dilution + diversity loss | Alternative explanations | H-M1-M2 sequential tests |
| Optimum | Peak identifiable | Plateau or monotonic | H-M3 derivative analysis |
| Scale Transfer | Optima consistent | Scale-specific | H-M4 validation at 1B |

**Overall Robustness:** Medium-High (strong theory, needs empirical validation)

---

## 7. Executive Summary

**Main Hypothesis:** Curation parameters show non-monotonic dose-response with benchmarks
- ID: H-CPDR-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 MUST_WORK gates (H-E1, H-M1)

**Risk Assessment:** Medium
- Primary concerns: Perplexity validity (R1), Scale transfer (R2)

**Immediate Action:** Begin Phase 1 with H-E1 parameter sweep

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-CPDR-v1)
- **Schema Version:** 10.0.0
- **Discussion Exchanges:** 12 (6 personas converged)

### B. Scope Reduction
- BUILD_ON claims (60%): Perplexity filtering efficacy, deduplication benefits, small model consistency
- PROVE_NEW claims (40%): Systematic dose-response mapping, cross-scale transfer
