# Verification Plan: Multi-Dimensional Truthfulness

**Date:** 2026-08-24
**Hypothesis ID:** H-TruthfulnessDimensions-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under evaluation of N≥30 diverse LLMs (varied architecture, scale, training) on truthfulness benchmarks, if TruthfulQA, HaluEval, and FactScore measure partially independent reliability dimensions, then inter-benchmark correlations will be moderate (r between unrelated-benchmark baseline and 0.7) while intra-benchmark correlations remain high (r > 0.7), and factor analysis will reveal 2-3 components rather than a single factor, because these benchmarks target distinct failure modes: misconception resistance, generation coherence, and factual precision respectively.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in correlation structure — all truthfulness benchmarks measure the same underlying construct, with inter-benchmark r > 0.7 and single-factor solution explaining >80% variance.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Multi-benchmark Evaluation Suite (standard) | All established benchmarks measuring aspects of truthfulness; enables correlation analysis |
| **Model** | Open LLM Leaderboard Model Population | Diverse architectures, scales, training approaches for robust correlation estimation |

**Dataset Details:**
- Source: TruthfulQA (sylinrl/TruthfulQA), HaluEval (RUCAIBox/HaluEval), FactScore (shmsw25/FActScore)
- Path: Public GitHub repositories

**Model Details:**
- Type: Decoder-only transformers
- Source: HuggingFace Hub

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Single Benchmark Evaluation | Standard practice, no correlation data | Individual benchmarks |
| BenchBench Agreement Testing | Shows benchmarks can disagree | Meta-benchmark |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Benchmark scores are reliable measurements with low noise | All benchmarks have published reliability statistics; HaluEval uses 35K samples | Low correlations could reflect noise, not true independence |
| A2 | Model population (N≥30) is representative of current LLM landscape | Open LLM Leaderboard includes diverse architectures, scales, training approaches | Correlation structure may not generalize beyond tested models |
| A3 | Factor analysis assumptions approximately hold for benchmark scores | Continuous scores, reasonable sample size; IRT analysis as robustness check | Factor structure may be artifacts; IRT results would diverge |
| A4 | Format differences (MC vs generation) don't dominate construct differences | Will test via format-controlled analyses | Apparent multi-dimensionality may reflect format, not constructs |
| A5 | Unrelated-benchmark baseline (MMLU-Physics vs HaluEval) provides valid reference | These measure different domains; expected near-zero correlation | Threshold interpretation becomes arbitrary |

### 1.6 Research Gap & Novelty

**First empirical correlation and factor structure study for truthfulness benchmarks specifically.** Key innovation: Quantifying multi-dimensionality vs single-factor truthfulness using latent structure analysis.

Differentiation:
- BenchBench (2024): Proposes methodology but doesn't apply to truthfulness
- Ailem et al. (2024): Prompt-level within-benchmark correlations; we study model-level cross-benchmark
- Moving Target (2026): Studies score drift; we study snapshot correlation structure

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Moderate Inter-Benchmark Correlations Exist

**Type:** EXISTENCE
**Statement:** Under evaluation of N≥30 diverse LLMs on TruthfulQA, HaluEval, and FactScore, inter-benchmark correlations will be moderate (r > unrelated-benchmark baseline AND r < 0.7), demonstrating partially independent reliability dimensions.

**Rationale:** This is the foundational hypothesis. If inter-benchmark correlations are either too high (r > 0.7, suggesting single construct) or too low (r ≈ 0, suggesting noise), the multi-dimensional truthfulness claim fails.

**Variables:**
- IV: Benchmark type (TruthfulQA, HaluEval, FactScore)
- DV: Inter-benchmark Spearman correlation coefficient
- CV: Model architecture, scale, training approach

**Success Criteria:**
- Primary: r(cross-benchmark) > r(MMLU-Physics vs HaluEval) AND r < 0.7
- Secondary: Intra-benchmark r > 0.7 (reliability check)

**Gate:**
- Type: MUST_WORK
- If Fail: Entire hypothesis fails; multi-dimensionality not supported

**Prerequisites:** None

**Verification Protocol:**
1. Select 30+ models from Open LLM Leaderboard with diverse architectures
2. Run all benchmarks (TruthfulQA, HaluEval, FactScore, MMLU baseline)
3. Compute Spearman correlation matrix for all benchmark pairs
4. Compare cross-benchmark correlations to unrelated-benchmark baseline
5. Verify r falls in moderate range (> baseline, < 0.7)

---

#### H-M1: TruthfulQA Tests Misconception Resistance

**Type:** MECHANISM
**Statement:** TruthfulQA specifically measures resistance to popular misconceptions (imitative falsehoods), a capability distinct from general knowledge retrieval measured by MMLU.

**Rationale:** If TruthfulQA correlates perfectly with MMLU, it measures general knowledge, not misconception resistance. The benchmark was designed to elicit imitative falsehoods that appear correct but are false.

**Variables:**
- IV: Benchmark (TruthfulQA vs MMLU)
- DV: Correlation coefficient between TruthfulQA and MMLU
- CV: Model population diversity

**Success Criteria:**
- Primary: r(TruthfulQA, MMLU) < r(MMLU subtasks internal)
- Secondary: Models exist with high MMLU but low TruthfulQA (divergent profiles)

**Gate:**
- Type: MUST_WORK
- If Fail: TruthfulQA may not measure unique construct

**Prerequisites:** H-E1

**Verification Protocol:**
1. Compute r(TruthfulQA, MMLU) across model population
2. Identify models with divergent profiles (high MMLU, low TruthfulQA)
3. Analyze error patterns on TruthfulQA for these models
4. Confirm misconception-type errors dominate

---

#### H-M2: HaluEval Tests Generation Coherence

**Type:** MECHANISM
**Statement:** HaluEval measures generation coherence and consistency maintenance, capabilities distinct from TruthfulQA's misconception resistance.

**Rationale:** HaluEval tests hallucinated details in QA, dialogue, and summarization. If it correlates perfectly with TruthfulQA, they test the same process.

**Variables:**
- IV: Benchmark (HaluEval vs TruthfulQA)
- DV: Correlation coefficient
- CV: Model population, evaluation format

**Success Criteria:**
- Primary: r(HaluEval, TruthfulQA) < 0.7
- Secondary: HaluEval subtask correlations (QA vs Summ) > cross-benchmark r

**Gate:**
- Type: SHOULD_WORK
- If Fail: HaluEval and TruthfulQA may overlap more than expected

**Prerequisites:** H-M1

**Verification Protocol:**
1. Compute r(HaluEval, TruthfulQA) across model population
2. Compare to intra-HaluEval correlations (QA vs Summarization)
3. Identify models with divergent HaluEval vs TruthfulQA profiles
4. Analyze error types for divergent models

---

#### H-M3: FactScore Tests Factual Precision

**Type:** MECHANISM
**Statement:** FactScore measures atomic factual precision via retrieval-based verification, a capability distinct from both TruthfulQA and HaluEval.

**Rationale:** FactScore decomposes claims and verifies against Wikipedia. If it correlates perfectly with other benchmarks, no unique contribution.

**Variables:**
- IV: Benchmark (FactScore vs others)
- DV: Correlation coefficients
- CV: Model population, Wikipedia retrieval corpus

**Success Criteria:**
- Primary: r(FactScore, TruthfulQA) < 0.7 AND r(FactScore, HaluEval) < 0.7
- Secondary: FactScore errors categorically differ from other benchmark errors

**Gate:**
- Type: SHOULD_WORK
- If Fail: FactScore may not measure unique dimension

**Prerequisites:** H-M2

**Verification Protocol:**
1. Compute r(FactScore, TruthfulQA) and r(FactScore, HaluEval)
2. Run PCA on all benchmark scores
3. Verify FactScore loads on different component than others
4. Analyze error types specific to FactScore (retrieval failures vs generation errors)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | r > baseline AND r < 0.7 | STOP - hypothesis fails |
| H-M1 | MUST_WORK | r(TruthfulQA, MMLU) < internal MMLU | Document limitation |
| H-M2 | SHOULD_WORK | r(HaluEval, TruthfulQA) < 0.7 | Continue with caveat |
| H-M3 | SHOULD_WORK | r(FactScore, others) < 0.7 | Continue with caveat |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption Risks

**R1: Benchmark Noise Masking True Independence** (from A1)
- Source: A1 - Benchmark scores are reliable with low noise
- Severity: HIGH
- Description: If benchmark scores have high measurement noise, low correlations could reflect noise rather than true independence of constructs.
- Affected: H-E1, H-M1, H-M2, H-M3
- Mitigation: Use benchmarks with published reliability statistics (HaluEval: 35K samples). Report confidence intervals on correlations. If reliability <0.7, flag results as tentative.

**R2: Model Population Not Representative** (from A2)
- Source: A2 - Model population N≥30 is representative
- Severity: MEDIUM
- Description: Correlation structure may not generalize if model sample is biased toward certain architectures or scales.
- Affected: All hypotheses
- Mitigation: Require diverse architectures (Llama, Mistral, Falcon, Phi, Qwen), scales (7B-70B), and training approaches (base, instruct, RLHF, DPO). Report architecture breakdown.

**R3: Factor Analysis Artifacts** (from A3)
- Source: A3 - Factor analysis assumptions hold
- Severity: MEDIUM
- Description: Factor structure could be artifacts of method rather than true latent structure.
- Affected: H-E1 (factor analysis component)
- Mitigation: Run IRT analysis as robustness check. If PCA and IRT diverge significantly, report both and discuss discrepancy.

**R4: Format Confound Dominance** (from A4)
- Source: A4 - Format differences don't dominate construct differences
- Severity: HIGH
- Description: Observed multi-dimensionality could reflect MC vs generation format differences, not underlying constructs.
- Affected: H-E1, H-M1, H-M2
- Mitigation: Run format-controlled analyses (generation-only track, MC-only track). If format explains more variance than benchmark type, report as limitation.

**R5: Invalid Baseline Reference** (from A5)
- Source: A5 - Unrelated-benchmark baseline provides valid reference
- Severity: LOW
- Description: If unrelated-benchmark correlation (MMLU-Physics vs HaluEval) is not near-zero, threshold interpretation becomes arbitrary.
- Affected: H-E1
- Mitigation: Compute baseline first. If r > 0.3, reconsider threshold interpretation or use absolute 0.5/0.7 cutoffs with justification.

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Noise masking independence | A1 | H-E1, H-M1, H-M2, H-M3 | HIGH |
| R2: Non-representative models | A2 | All | MEDIUM |
| R3: Factor analysis artifacts | A3 | H-E1 | MEDIUM |
| R4: Format confound dominance | A4 | H-E1, H-M1, H-M2 | HIGH |
| R5: Invalid baseline reference | A5 | H-E1 | LOW |

### 4.3 Mitigation Strategies

| Risk | Prevention | Detection | Response |
|------|-----------|-----------|----------|
| R1 | Use high-sample benchmarks | Compute reliability estimates | Report with confidence intervals |
| R2 | Require architecture diversity | Check representation stats | Document limitations |
| R3 | Plan IRT robustness check | Compare PCA vs IRT results | Report both if divergent |
| R4 | Plan format-controlled analyses | Variance decomposition | Report format as covariate |
| R5 | Compute baseline first | Check baseline r magnitude | Use absolute cutoffs if needed |

---

## 5. Dependency Graph (DAG)

### 5.1 ASCII DAG

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────┐
    │  H-E1: Moderate Correlations    │
    │  Gate: MUST_WORK                │
    └─────────────┬───────────────────┘
                  │
                  ▼
[Level 1 - Mechanism Chain Start]
    ┌─────────────────────────────────┐
    │  H-M1: TruthfulQA Distinctness  │
    │  Gate: MUST_WORK                │
    └─────────────┬───────────────────┘
                  │
                  ▼
[Level 2 - Mechanism Chain Mid]
    ┌─────────────────────────────────┐
    │  H-M2: HaluEval Distinctness    │
    │  Gate: SHOULD_WORK              │
    └─────────────┬───────────────────┘
                  │
                  ▼
[Level 3 - Mechanism Chain End]
    ┌─────────────────────────────────┐
    │  H-M3: FactScore Distinctness   │
    │  Gate: SHOULD_WORK              │
    └─────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 (MUST_WORK gates)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Fail Action |
|-------|------------|---------------|-----------|-------------|
| 0 | H-E1 | None | MUST_WORK | STOP pipeline |
| 1 | H-M1 | H-E1 | MUST_WORK | Document limitation |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Continue with caveat |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Continue with caveat |

---

## 6. Timeline (Gantt)

### 6.1 ASCII Gantt

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2     │ W3       │ W4       │ W5       │
─────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation  │          │          │          │          │
  H-E1               │ ████████ │          │          │          │
  [Gate 1]           │        ◆ │          │          │          │
─────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms  │          │          │          │          │
  H-M1               │          │ ████████ │          │          │
  H-M2               │          │          │ ████████ │          │
  H-M3               │          │          │          │ ████████ │
  [Gate 2]           │          │          │          │        ◆ │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work │ ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 6.2 Critical Path

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

**Total Duration:** 5 weeks
- Foundation (H-E1): 2 weeks
- Mechanism chain (H-M1-3): 3 weeks

**Slack Available:** 0 weeks (fully sequential)

**Gate Points:**
- Gate 1 (Week 2): H-E1 must show moderate correlations
- Gate 2 (Week 5): Mechanism chain validated

### 6.3 Resource Summary

**Total Hypotheses:** 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)

**Compute Resources:**
- ~400 GPU-hours total across 30 models
- All datasets publicly available
- Standard tools: scipy, factor_analyzer, lm-eval

**Verification Phases:** 2
1. Foundation (H-E1): Correlation computation
2. Mechanisms (H-M1-3): Per-benchmark distinctness analysis

---

## 7. Dialectical Analysis

### 7.1 Thesis Statement

**Core Claim:** Truthfulness benchmarks (TruthfulQA, HaluEval, FactScore) measure partially independent reliability dimensions, evidenced by moderate inter-benchmark correlations and multi-factor structure.

**Supporting Evidence:**
1. Benchmarks use fundamentally different evaluation paradigms (MC vs generation vs retrieval-based)
2. Each targets distinct failure modes: misconception resistance, generation coherence, factual precision
3. Prior work (BenchBench, Ailem et al.) shows benchmark heterogeneity exists

**Strengths:**
- Grounded in established benchmark documentation
- Clear causal mechanism linking paradigm differences to correlation structure
- Falsifiable predictions with quantitative thresholds

### 7.2 Antithesis Development

**Null Hypothesis (H0):** All truthfulness benchmarks measure the same underlying construct, with inter-benchmark r > 0.7 and single-factor solution explaining >80% variance.

**Counter-Arguments:**
1. Observed differences may reflect measurement format (MC vs generation), not underlying constructs
2. Model population may be too homogeneous to reveal true correlation structure
3. Benchmark reliability issues could inflate or deflate correlations artificially

**Potential Failure Points:**
- R1: Noise masking true correlation structure
- R4: Format confounds dominating construct differences
- R3: Factor analysis producing methodological artifacts

**Conditions Supporting H0:**
- If all inter-benchmark r > 0.7, single unified truthfulness construct
- If single factor explains >80% variance in PCA
- If format-controlled analyses eliminate multi-dimensionality

### 7.3 Synthesis

**Balanced Assessment:**

The multi-dimensional truthfulness hypothesis is plausible given distinct evaluation paradigms, but the null hypothesis raises valid methodological concerns about format confounds and measurement reliability.

**Resolution Path:**

1. **H-E1 foundation test:** Directly measures correlation structure with baseline reference
2. **Format-controlled analyses:** Separate generation-only and MC-only tracks isolate format effects
3. **IRT robustness check:** Validates factor structure against alternative method
4. **Gate conditions:** H-E1 MUST_WORK gate allows early falsification if H0 is supported

**Outcome Space:**
- **Full Support:** Inter-benchmark r moderate (baseline < r < 0.7), 2-3 factors → Thesis validated
- **Partial Support:** Some benchmark pairs r > 0.7 → Refined thesis with noted overlap
- **H0 Supported:** All r > 0.7 and single factor → Antithesis validated (also publishable finding)

### 7.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Moderate correlations exist | Could be noise or artifact | H-E1 with baseline reference |
| Mechanism | Distinct failure modes | Format confounds | Format-controlled analyses |
| Reliability | Benchmarks are stable | Measurement noise | IRT robustness check |
| Factor Structure | 2-3 factors | Single factor | PCA + IRT comparison |

**Overall Robustness:** HIGH — Win-win design where either outcome is publishable

**Confidence in Verification Plan:** 0.75

---

## 8. Executive Summary

**Main Hypothesis:** H-TruthfulnessDimensions-v1
- Tests whether TruthfulQA, HaluEval, FactScore measure independent dimensions
- Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E1, H-M1, H-M2, H-M3)
- Duration: 5 weeks, 2 phases
- Critical Gates: 2 (H-E1 MUST_WORK, H-M1 MUST_WORK)

**Risk Assessment:** MEDIUM (2 High risks: noise masking, format confounds)

**Win-Win Design:** Either outcome (multi-factor or single-factor) is publishable

**Immediate Action:** Begin with H-E1 correlation computation

### Conclusions

**Key Achievements:**
- 4 sub-hypotheses defined with clear success criteria
- Sequential dependency chain: H-E1 → H-M1 → H-M2 → H-M3
- Risk mitigation strategies for all 5 assumptions
- Dialectical analysis confirms robustness (win-win outcome)

**Verification Order:**
1. Phase 1: H-E1 (Foundation) - 2 weeks - MUST_WORK gate
2. Phase 2: H-M1-M3 (Mechanisms) - 3 weeks - H-M1 MUST_WORK

**Critical Decisions:**
- Gate 1 fail → STOP pipeline, single-factor hypothesis supported
- Gate 2 fail → Document which mechanism step breaks down

**Open Questions:**
- Exact correlation values unknown until data collected
- Optimal factor rotation method to determine empirically
- Whether format confounds dominate requires analysis

### Next Steps

1. **Proceed to Phase 2C:** Design detailed experiment for H-E1
2. **Select Model Population:** Choose 30+ diverse LLMs from Open LLM Leaderboard
3. **Set Up Evaluation Infrastructure:** Configure lm-evaluation-harness, FactScore package
4. **Compute Baseline:** r(MMLU-Physics, HaluEval) as reference threshold

---

## Appendix

### A. Established Facts (BUILD_ON - Not Re-Verified)

| Claim | Evidence |
|-------|----------|
| Benchmark agreement is not guaranteed | BenchBench, Perlitz et al. 2024 |
| Non-random correlations exist within benchmark test prompts | Ailem et al. 2024 |
| TruthfulQA, HaluEval, FactScore use different evaluation paradigms | Published benchmark papers |

**Scope Reduction:** 25% (3 BUILD_ON claims, 1 PROVE_NEW claim)

### B. Phase 2B State

**verification_state.yaml:** Generated (ABLATION MODE - state block in session)

**Pipeline Tasks Updated:**
- Phase 2B: DONE
- Phase 2C: DOING

**Hypothesis Tasks Created:**
- H-E1: 13d1b3ad-9a82-4720-b0ed-94fe9b85e349
- H-M1: 89c141a2-4536-4105-8fd9-cccb4c214f55
- H-M2: 5b6a2fc4-213b-47b6-ac09-cb93acf7ba10
- H-M3: f4bcbc49-c6fe-4b4c-a973-e41b8fd31282
