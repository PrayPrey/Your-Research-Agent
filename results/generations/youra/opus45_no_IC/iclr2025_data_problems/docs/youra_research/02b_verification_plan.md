# Verification Plan: Contamination-Performance Transfer Function

**Date:** 2026-08-10
**Hypothesis ID:** H-ContamInflation-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the condition of language models trained on documented corpora with measurable n-gram overlap, if we increase cumulative benchmark-relevant exposure during training, then benchmark scores will show positive inflation residuals after capability detrending, because progressive memorization encodes benchmark content proportionally to exposure frequency.

### 1.2 Alternative Hypothesis (H0)
There is no significant correlation (Spearman r < 0.2, 95% CI upper bound < 0.35) between n-gram contamination exposure and benchmark score inflation after capability detrending.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | The Pile + Standard Benchmarks (standard) | Documented corpus enables ground-truth contamination measurement |
| **Model** | Pythia Model Family | Multiple sizes, documented training, checkpoint availability |

**Dataset Details:**
- Source: EleutherAI (The Pile), HuggingFace (benchmarks)
- Path: pile-corpus + lm-eval-harness tasks

**Model Details:**
- Type: decoder-only transformer
- Source: EleutherAI/pythia-*

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| N-gram decontamination (13-gram) | Removes verbatim overlaps | GPT-3 training, various benchmarks |
| TED (Test Data Deviation) | Distribution-based detection | Multiple LLM benchmarks |
| Kernel Divergence Score | Dataset-level detection | LLM benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | 13-gram overlap is a valid proxy for memorizable benchmark content | GPT-3 Appendix C established 13-gram as decontamination standard | Need alternative contamination measure (semantic embedding similarity) |
| A2 | WikiText-103 perplexity measures capability without contamination | WikiText-103 is separate corpus from The Pile | Use alternative OOD corpus for capability measurement |
| A3 | Pythia checkpoints provide sufficient contamination gradient | Checkpoints at 0-100% training see different cumulative content | Gradient may be too narrow; need synthetic contamination injection |
| A4 | Inflation effect is proportional to exposure, not threshold-based | Tested as P1 prediction | Revise to piecewise model with threshold detection |

### 1.6 Research Gap & Novelty

**Gap:** Existing methods (Sainz et al., Dong et al., Choi et al.) detect contamination presence but do not quantify its performance impact. The contamination-to-inflation pipeline is incomplete: detection → quantification → **impact modeling (MISSING)** → mitigation.

**Novelty:** First empirically-validated contamination-to-inflation transfer function using checkpoint-gradient methodology. This enables contamination-calibrated benchmark reporting without requiring clean baseline models.

**Key Innovation:** Checkpoint-gradient methodology enables contamination-performance correlation without clean baseline models by leveraging OOD perplexity detrending.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | pending |
| H-M1 | Mechanism | SHOULD_WORK | H-E1 | pending |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | pending |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | pending |
| H-M4 | Mechanism | MUST_WORK | H-M3 | pending |

---

### 2.2 Hypothesis Specifications

#### H-E1: Contamination-Inflation Correlation Exists

**Statement**: Under the condition of Pythia models trained on The Pile with measurable 13-gram overlap, if cumulative benchmark overlap increases across checkpoints, then benchmark score inflation residual will show positive correlation (r > 0.2) because memorization of benchmark content produces artificially elevated scores.

**Rationale**: This existence hypothesis validates the fundamental premise that contamination produces measurable performance inflation. Without demonstrating this correlation, the entire transfer function approach lacks empirical foundation.

**Variables**:
- Independent: Cumulative 13-gram benchmark overlap (%)
- Dependent: Benchmark score inflation residual (observed - predicted)
- Controlled: Model architecture (Pythia), corpus (The Pile), evaluation protocol

**Verification Protocol**:
1. Extract 13-grams from MMLU/ARC/HellaSwag/WinoGrande test sets (full standard test splits, ~15K+ samples total).
2. Compute cumulative overlap for each of 72 Pythia checkpoints (6 sizes × 12 checkpoints).
3. Evaluate all checkpoints using lm-eval-harness with standard settings.
4. Fit capability regression using WikiText-103 perplexity, compute inflation residuals.
5. Calculate Spearman correlation between contamination and inflation.

**Success Criteria**:
- Primary: Spearman r > 0.5 with p < 0.05
- Secondary: r > 0.2 establishes existence (minimum threshold)

**Failure Response**: IF fails → ABANDON (no correlation means no transfer function possible)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1, Prediction P1

---

#### H-M1: Training Corpus Contains Benchmark N-grams

**Statement**: Under the condition of using The Pile as training corpus, if we analyze n-gram overlap with standard benchmarks, then we will find measurable 13-gram overlap (>1% of benchmark content) because The Pile aggregates diverse internet text likely containing benchmark-similar content.

**Rationale**: This establishes the prerequisite that contamination exists in the training data. Prior work (Yang et al., 2023) found 8-18% overlap in RedPajama; we verify similar patterns in The Pile.

**Variables**:
- Independent: Benchmark test set content
- Dependent: 13-gram overlap percentage with The Pile
- Controlled: N-gram length (13), matching algorithm

**Verification Protocol**:
1. Extract all 13-grams from benchmark test sets.
2. Index The Pile training tokens into searchable structure.
3. Compute exact-match overlap percentage per benchmark.
4. Report overlap distribution across benchmarks.

**Success Criteria**:
- Primary: Measurable overlap >1% exists for at least one benchmark
- Secondary: Overlap varies across benchmarks (not uniform noise)

**Failure Response**: IF fails → PIVOT to semantic contamination measures

**Dependencies**: H-E1

**Source**: Phase 2A Causal Step 1

---

#### H-M2: Repeated Exposure Leads to Memorization

**Statement**: Under the condition of benchmark content present in training data, if exposure frequency increases across checkpoints, then memorization strength (measured via MIA signals or verbatim completion) will increase proportionally because transformer models encode frequently-seen sequences more strongly.

**Rationale**: This tests the memorization mechanism. MIMIR benchmark validates MIA signals correlate with training membership; we extend to checkpoint-level analysis.

**Variables**:
- Independent: Cumulative token exposure at checkpoint
- Dependent: Memorization strength (MIA score or completion rate)
- Controlled: Model architecture, evaluation method

**Verification Protocol**:
1. Select subset of contaminated benchmark items (high-overlap).
2. Measure MIA scores across Pythia checkpoints.
3. Alternatively: measure verbatim completion rates.
4. Correlate with cumulative exposure.

**Success Criteria**:
- Primary: Positive correlation between exposure and memorization signal
- Secondary: Later checkpoints show higher memorization than early

**Failure Response**: IF fails → EXPLORE alternative memorization measures

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 2

---

#### H-M3: Memorized Content Enables Inference Advantage

**Statement**: Under the condition of memorized benchmark content in model weights, if we compare model performance on contaminated vs. clean items, then contaminated items will show higher accuracy because memorization enables correct responses independent of true generalization.

**Rationale**: This tests whether memorization translates to performance advantage. Oren et al. (2024) showed verbatim completion on contaminated data; we extend to accuracy differential.

**Variables**:
- Independent: Item contamination status (contaminated vs. clean)
- Dependent: Per-item accuracy
- Controlled: Item difficulty (matched), model checkpoint

**Verification Protocol**:
1. Partition benchmark items by contamination status.
2. Match contaminated/clean items by difficulty proxy.
3. Compare accuracy on matched pairs.
4. Test statistical significance of difference.

**Success Criteria**:
- Primary: Contaminated items show higher accuracy than matched clean items
- Secondary: Effect size increases with contamination level

**Failure Response**: IF fails → EXPLORE timing/confidence signals instead

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3

---

#### H-M4: Inflation is Proportional to Contamination Level

**Statement**: Under the condition of established memorization-to-advantage pathway, if we model inflation as function of contamination, then the relationship will be monotonic and approximately linear because each additional unit of contamination contributes additively to inflation.

**Rationale**: This is the core PROVE_NEW claim. Linear proportionality enables transfer function derivation; threshold effects would require piecewise modeling.

**Variables**:
- Independent: Contamination level (continuous)
- Dependent: Inflation residual magnitude
- Controlled: Capability level (via detrending)

**Verification Protocol**:
1. Plot inflation residual vs. contamination across all 72 checkpoints.
2. Fit linear regression: inflation ~ contamination.
3. Test linearity assumption (residual analysis).
4. Extract slope coefficient for transfer function.

**Success Criteria**:
- Primary: Spearman r > 0.5 (strong correlation)
- Secondary: ≥3% inflation at 10% contamination level

**Failure Response**: IF fails → PIVOT to piecewise/threshold model

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Predictions P1/P2

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | r > 0.2, p < 0.05 | STOP: No correlation |
| H-M1 | SHOULD_WORK | Overlap >1% detected | PIVOT: Semantic measures |
| H-M2 | SHOULD_WORK | Positive exposure-memorization correlation | EXPLORE: Alternative signals |
| H-M3 | SHOULD_WORK | Contaminated > clean accuracy | EXPLORE: Timing signals |
| H-M4 | MUST_WORK | Linear fit r > 0.5 | PIVOT: Piecewise model |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk Identification

| ID | Risk | Source | Severity | Likelihood |
|----|------|--------|----------|------------|
| R1 | 13-gram may not capture all memorizable content | A1 | Medium | Medium |
| R2 | WikiText-103 perplexity may be contaminated | A2 | High | Low |
| R3 | Pythia contamination gradient may be too narrow | A3 | Medium | Medium |
| R4 | Inflation may be threshold-based, not proportional | A4 | Medium | Medium |

### 4.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact |
|------|---------------------|--------|
| R1 | H-E1, H-M1 | Core correlation may be underestimated |
| R2 | H-E1, H-M4 | Capability detrending may be biased |
| R3 | H-M2, H-M3, H-M4 | Insufficient variance to detect effects |
| R4 | H-M4 | Linear model assumption violated |

### 4.3 Mitigation Strategies

**R1: 13-gram Proxy Limitation**
- Prevention: Validate against shorter n-grams (8-gram) as sensitivity check
- Detection: Compare 13-gram vs. 8-gram overlap rankings
- Response: PIVOT to semantic embedding similarity if n-gram underestimates
- Early Warning: Low overlap (<1%) despite expected contamination

**R2: WikiText-103 Contamination**
- Prevention: Verify WikiText-103 not in The Pile (check data cards)
- Detection: Compute WikiText-103 overlap with The Pile
- Response: PIVOT to C4 perplexity or PTB as alternative OOD measure
- Early Warning: High WikiText-103 overlap (>5%)

**R3: Narrow Contamination Gradient**
- Prevention: Use all 12 checkpoints per model size (72 total data points)
- Detection: Check variance in contamination levels across checkpoints
- Response: SCOPE to model sizes with highest variance; EXPLORE synthetic injection
- Early Warning: Contamination variance <2% across checkpoints

**R4: Non-Proportional Inflation**
- Prevention: Plot scatter before fitting linear model; check visually
- Detection: Residual analysis; test for threshold effects
- Response: PIVOT to piecewise model with breakpoint detection
- Early Warning: Clear step-function pattern in scatter plot

### 4.4 Risk Summary

| ID | Risk | Severity | Mitigation Summary |
|----|------|----------|-------------------|
| R1 | 13-gram proxy limitation | Medium | Validate with 8-gram; pivot to embeddings |
| R2 | WikiText contamination | High | Verify OOD; pivot to C4/PTB |
| R3 | Narrow gradient | Medium | Use all 72 checkpoints; synthetic injection |
| R4 | Non-proportional effect | Medium | Residual analysis; piecewise model |

**Risk Counts:** Critical: 0, High: 1, Medium: 3, Low: 0

---

## 5. Visualizations

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────┐
    │  H-E1: Correlation Exists           │
    │  Gate: MUST_WORK                    │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 1 - Mechanism Step 1]
    ┌─────────────────────────────────────┐
    │  H-M1: Corpus Contains N-grams      │
    │  Gate: SHOULD_WORK                  │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 2 - Mechanism Step 2]
    ┌─────────────────────────────────────┐
    │  H-M2: Exposure → Memorization      │
    │  Gate: SHOULD_WORK                  │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 3 - Mechanism Step 3]
    ┌─────────────────────────────────────┐
    │  H-M3: Memorization → Advantage     │
    │  Gate: SHOULD_WORK                  │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 4 - Mechanism Step 4]
    ┌─────────────────────────────────────┐
    │  H-M4: Proportional Inflation       │
    │  Gate: MUST_WORK (PROVE_NEW)        │
    └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|-----------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | 1: Foundation |
| 1 | H-M1 | H-E1 | SHOULD_WORK | 2: Mechanisms |
| 2 | H-M2 | H-M1 | SHOULD_WORK | 2: Mechanisms |
| 3 | H-M3 | H-M2 | SHOULD_WORK | 2: Mechanisms |
| 4 | H-M4 | H-M3 | MUST_WORK | 2: Mechanisms |

**Gate Conditions:**
- **Gate 1 (H-E1):** If fails → STOP, no correlation exists
- **Gate 2 (H-M4):** If fails → PIVOT to piecewise/threshold model

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2     │ W3-4     │ W5       │ W6       │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation   │          │          │          │          │
  H-E1 (Existence)    │ ████████ │          │          │          │
  [Gate 1]            │          │ ◆        │          │          │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms   │          │          │          │          │
  H-M1 (N-grams)      │          │ ████████ │          │          │
  H-M2 (Memorization) │          │          │ ████     │          │
  H-M3 (Advantage)    │          │          │          │ ████     │
  H-M4 (Proportional) │          │          │          │     ████ │
  [Gate 2]            │          │          │          │        ◆ │
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Duration Breakdown:**
- H-E1 (Foundation): 2 weeks
- H-M1 (N-gram analysis): 2 weeks
- H-M2 (Memorization): 1 week
- H-M3 (Inference advantage): 1 week
- H-M4 (Proportionality): 1 week (overlaps with M3)

**Total Duration:** 6 weeks
**Slack Available:** 0 weeks (all sequential, no parallelization)

**Gate Decision Points:**
- Gate 1 (Week 2): H-E1 pass required to continue
- Gate 2 (Week 6): H-M4 pass required for transfer function claim

### 5.5 Resource Summary

**Total Hypotheses:** 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 through H-M4)
- Condition: 0 (not required)

**Verification Phases:** 2
1. Foundation (H-E1): Establish correlation exists
2. Mechanisms (H-M1-M4): Validate causal chain

**Compute Resources:**
- Pythia checkpoints: 72 (6 sizes × 12 checkpoints)
- Benchmark evaluations: ~120 runs (~120 GPU-hours)
- N-gram extraction: ~48 hours (one-time)

**Data Requirements:**
- The Pile (training corpus): Pre-indexed
- Benchmarks: MMLU, ARC, HellaSwag, WinoGrande (standard splits)
- WikiText-103: For OOD perplexity

### 5.6 Execution Order

1. **Week 1-2:** Execute H-E1 (correlation test across 72 checkpoints)
2. **Week 2:** Evaluate Gate 1 → If r > 0.2, proceed
3. **Week 3-4:** Execute H-M1 (n-gram overlap computation)
4. **Week 5:** Execute H-M2 (memorization signal analysis)
5. **Week 5-6:** Execute H-M3 (contaminated vs. clean comparison)
6. **Week 6:** Execute H-M4 (fit linear transfer function)
7. **Week 6:** Evaluate Gate 2 → If r > 0.5, claim validated
8. **Complete:** Transfer function derived, ready for Phase 5 baseline comparison

---

## 6. Dialectical Analysis

The verification plan employs thesis-antithesis-synthesis structure to ensure robust evaluation. The null hypothesis (H0) from Phase 2A serves as the antithesis foundation, providing clear falsification criteria.

### 6.1 Thesis

**Core Claim:** Cumulative benchmark-relevant n-gram exposure during LLM training produces measurable, proportional benchmark score inflation that can be quantified via a checkpoint-gradient transfer function.

**Supporting Evidence:**
1. Training corpus contains benchmark n-grams (Yang et al. 2023: 8-18% overlap in RedPajama)
2. Repeated exposure leads to memorization (MIMIR benchmark validates MIA-membership correlation)
3. Memorized content enables correct answers independent of generalization (Oren et al. 2024)
4. Inflation mechanism is testable via checkpoint gradient methodology

**Strengths:**
- Clear 4-step causal mechanism
- Checkpoint-gradient methodology requires no clean baseline models
- OOD perplexity detrending separates capability from contamination
- Pre-registered protocol eliminates post-hoc analysis concerns

**Expected Outcomes:**
- Primary: Spearman r > 0.5 between contamination and inflation
- Secondary: ≥3% inflation at 10% contamination level
- Tertiary: Exact-match benchmarks show higher inflation than generation benchmarks

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant correlation (Spearman r < 0.2, 95% CI upper bound < 0.35) between n-gram contamination exposure and benchmark score inflation after capability detrending.

**Counter-Arguments:**
1. Correlation may be confounded by capability growth during training
2. 13-gram overlap may not capture causally-relevant contamination
3. WikiText-103 detrending may itself be contaminated
4. Pythia-specific findings may not generalize

**Potential Failure Points:**
- R1: 13-gram proxy misses significant contamination modes
- R2: WikiText-103 is not truly OOD for The Pile
- R3: Contamination gradient too narrow for correlation detection
- R4: Effect is threshold-based, not proportional

**Conditions Under Which H0 Would Be Supported:**
- Spearman r < 0.2 with 95% CI upper bound < 0.35
- H-E1 fails: no detectable correlation
- Effect size < 1% at 10% contamination level

### 6.3 Synthesis

**Balanced Assessment:**
The hypothesis H-ContamInflation-v1 presents a testable claim that cumulative contamination produces proportional inflation. The null hypothesis raises valid concerns regarding confounds and generalizability.

**Resolution Path:**
The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before mechanism testing
2. **Sequential mechanism testing (H-M1-4):** Tests causal chain step-by-step
3. **Gate conditions:** Allow early detection of H0 support

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M4)
- Spearman r > 0.5 is confirmed
- Linear transfer function fits data

**Conditions for Antithesis Support:**
- H-E1 fails (r < 0.2)
- Effect size < 1% at 10% contamination
- Residual analysis shows non-linear pattern

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Transfer function validated
2. **Partial Support:** Some H-M fail → Refined thesis with limitations
3. **No Support:** H-E1 fails → Negative result publication (also valuable)

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Correlation exists | May be noise/confound | H-E1 test with r > 0.2 threshold |
| Mechanism | 4-step causal chain | Alternative explanations | H-M1-4 sequential validation |
| Scope | Applies to Pythia/Pile | Limited generalizability | Document as limitation; future work |
| Proportionality | Linear relationship | Threshold effects | H-M4 residual analysis |

**Overall Robustness Score:** HIGH

**Confidence in Verification Plan:** 0.80

**Key Strengths:**
- Pre-registered falsification criteria prevent confirmation bias
- Both positive and negative results are publishable
- Methodology contribution persists regardless of hypothesis outcome

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Cumulative n-gram exposure → proportional benchmark inflation
- ID: H-ContamInflation-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (H-E1, H-M4)

**Risk Assessment:** Medium
- Primary concerns: WikiText-103 contamination (R2), gradient narrowness (R3)

**Immediate Action:** Begin Phase 1 with H-E1 correlation test across 72 Pythia checkpoints

### 7.2 Final Summary

**Key Achievements:**
- 5 hypotheses across 2 phases defined
- H0 addressed: No correlation (r < 0.2) with clear falsification criteria
- 4-step causal chain mapped from Phase 2A

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Contamination-inflation correlation exists (r > 0.2)
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Corpus contains benchmark n-grams
- H-M2: Exposure leads to memorization
- H-M3: Memorization enables inference advantage
- H-M4: Inflation is proportional
- Gate 2: H-M4 must pass for transfer function claim

### 7.3 Conclusions

**Critical Decision Points:**
1. **Gate 1 (H-E1):** FAIL → STOP, no correlation exists; PASS → Proceed
2. **Gate 2 (H-M4):** FAIL → PIVOT to piecewise model; PASS → Transfer function validated

**Open Questions:**
- Does transfer function generalize across model families?
- How to extend to semantic contamination?
- Optimal threshold for practical significance?

**Recommendations:**
1. **Immediate:** Start H-E1 with 72 Pythia checkpoint evaluations
2. **Resources:** Allocate 6 weeks for critical path; ~120 GPU-hours for evaluations
3. **Failure Management:** Execute PIVOT strategies per risk mitigation plan

### 7.4 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-ContamInflation-v1)

**B. MCP Tool Usage Summary**
- Total MCP calls: 6
- Tools: scientificmethod (3x), structuredargumentation (3x)

**C. Sample Sizes**
- Pythia checkpoints: 72 (6 sizes × 12 checkpoints)
- Benchmark samples: Full standard test sets (~15K+ total)
- Statistical power: Adequate for r > 0.2 detection

---

## 8. State & Integration

### 8.1 Verification State

**Status:** GENERATED
**File:** verification_state.yaml
**Sub-Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)
**Next Hypothesis:** H-E1 (READY)

### 8.2 Pipeline Tasks

**Status:** SKIPPED (Archon MCP unavailable - timeout)
**Note:** Pipeline task updates will need to be performed manually or when Archon is available.

### 8.3 Hypothesis Tasks

**Status:** SKIPPED (Archon MCP unavailable - timeout)
**Note:** Hypothesis tasks will need to be created manually or when Archon is available.

**Planned Tasks:**
- H-E1: Contamination-Inflation Correlation Exists (EXISTENCE)
- H-M1: Corpus Contains Benchmark N-grams (MECHANISM)
- H-M2: Exposure Leads to Memorization (MECHANISM)
- H-M3: Memorization Enables Inference Advantage (MECHANISM)
- H-M4: Inflation is Proportional (MECHANISM)
