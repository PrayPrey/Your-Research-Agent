---
title: "Verification Plan: Contamination-Correction Signature of Deduplication"
hypothesis_id: H-ContaminationCorrectionSignature-v1
date: "2026-08-25"
status: in_progress
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
status: complete
completedAt: "2026-08-25T00:00:00Z"
---

# Verification Plan: Contamination-Correction Signature of Deduplication

**Date:** 2026-08-25
**Hypothesis ID:** H-ContaminationCorrectionSignature-v1
**Confidence:** 0.78
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)

---

## 0. Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON — DO NOT RE-TEST)

| Claim | Evidence | Status |
|-------|----------|--------|
| Deduplication of training data improves downstream benchmark performance on average | Lee et al. 2022 (arXiv 2107.06499) | BUILD_ON |
| Pythia and OLMo/Dolma model families release open checkpoints with documented curation choices | Biderman et al. 2023, Groeneveld et al. 2024, Soldaini et al. 2024 | BUILD_ON |
| lm-evaluation-harness supports unified evaluation of Pythia and OLMo on MMLU, HellaSwag, ARC, WinoGrande | EleutherAI/lm-evaluation-harness | BUILD_ON |

### 0.2 Claims to PROVE NEW (Hypothesis Generation Scope)

| Claim | Rationale |
|-------|-----------|
| Deduplication produces a per-benchmark contamination-correction signature (not uniform shift) | Novel claim — prior work reports aggregate effects only |
| Direction of per-benchmark performance change correlates with n-gram contamination overlap | Novel mechanistic prediction — not demonstrated in prior literature |

**Scope Reduction: 60%** — 3 of 5 claims are BUILD_ON; Phase 2B focuses on 2 PROVE_NEW claims only.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the setting of existing open pretrained language model families (Pythia suite) trained on corpora with and without deduplication (Pile vs dedup-Pile), if training data deduplication removes repeated near-duplicate documents that overlap with standard benchmark test patterns, then the resulting benchmark performance profile will show a characteristic contamination-correction signature: benchmarks with higher Pile n-gram contamination will score lower in dedup-Pile models (memorization inflation removed), while benchmarks with lower contamination will show relatively stable or improved performance, because deduplication selectively removes the near-memorization advantage conferred by repeated training examples that partially overlap with benchmark test content.

### 1.2 Alternative Hypothesis (H0)

At token-count-matched checkpoints, Pythia dedup-Pile and Pile models show no statistically significant difference in few-shot performance on any of {MMLU, HellaSwag, ARC, WinoGrande}, using Bonferroni-corrected α = 0.0125 (0.05/4), and per-benchmark performance changes show no significant correlation with estimated n-gram overlap between Pile and each benchmark's test set.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Pile vs dedup-Pile + MMLU, HellaSwag, ARC-Challenge, WinoGrande (standard) | Pile vs dedup-Pile provides the exact controlled curation comparison the hypothesis requires. The 4 benchmarks cover knowledge-intensive (MMLU, ARC) and reasoning-intensive (HellaSwag, WinoGrande) tasks, enabling profile analysis across capability dimensions. |
| **Model** | Pythia (160M, 410M, 1B, 6.9B) — Pile and dedup-Pile variants (Decoder-only GPT-NeoX) | Same architecture across curation variants; 154 intermediate checkpoints enable token-count matching; multiple scales enable robustness check and scale-interaction analysis |

**Dataset Details:**
- Source: EleutherAI (Pile/dedup-Pile training corpora); standard NLP benchmark repositories
- Path: Pythia checkpoints: huggingface.co/EleutherAI/pythia-*; benchmarks via lm-evaluation-harness

**Model Details:**
- Type: Decoder-only GPT-NeoX
- Source: EleutherAI/pythia on HuggingFace

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Lee et al. 2022 — Deduplicating Training Data Makes LMs Better | Aggregate performance improvement from dedup on GPT-2-scale models | Various NLP benchmarks at GPT-2 scale |
| Biderman et al. 2023 — Pythia suite Pile vs dedup-Pile results | Tabulated benchmark results for Pythia Pile and dedup-Pile at various scales | Standard benchmarks via lm-evaluation-harness |
| Shi et al. 2023 — Min-k% prob contamination detection | Contamination detection on various benchmarks | Multiple NLP benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pythia intermediate checkpoints have sufficient granularity for token-count matching between Pile and dedup-Pile training runs | Biderman et al. 2023 releases 154 checkpoints per model, spaced at logarithmic intervals | Residual data-volume confound; reported as limitation with matched-step robustness check |
| A2 | N-gram contamination estimates (13-gram overlap and min-k% prob) reliably reflect the extent to which repeated Pile documents overlap with benchmark test content | Shi et al. 2023 validated min-k% on multiple benchmarks; 13-gram overlap is standard (GPT-4 TR methodology) | Correlation test loses statistical power; use two independent estimators as robustness check |
| A3 | The deduplication-removed documents in Pile are representative of high-repetition content rather than uniquely informative documents | Exact substring deduplication targets documents appearing multiple times — by definition high-repetition | If unique high-value documents are removed by dedup, performance drops could reflect data quality loss rather than contamination correction |
| A4 | Few-shot lm-evaluation-harness results are stable enough to detect the contamination signature signal above noise | lm-evaluation-harness is deterministic for greedy decoding; variance mitigated by using full benchmark test sets | Underpowered study; increase evaluation coverage or use all benchmark items |
| A5 | The Pythia Pile vs dedup-Pile comparison isolates deduplication as the sole curation variable (architecture, optimizer, context length held constant) | Biderman et al. 2023 explicitly designed Pile and dedup-Pile Pythia variants for controlled comparison | Identification fails; no within-family controlled comparison exists — study cannot proceed |

### 1.6 Research Gap & Novelty

Prior deduplication work (Lee et al. 2022, Biderman et al. 2023) reports aggregate or tabulated benchmark effects without mechanistic prediction. Prior contamination work (Shi et al. 2023, GPT-4 TR) detects presence of test data in training but does not connect contamination magnitude to curation-driven performance differentials. This hypothesis bridges the two: using contamination estimates to predict the direction and magnitude of deduplication's benchmark effects, making the mechanism testable and falsifiable. The "contamination-correction signature" framing is genuinely novel — per-benchmark directional prediction from first principles using quantified contamination estimates.

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
**H-E1: Contamination-Correction Signature Exists**

**Statement**: Under the setting of Pythia Pile and dedup-Pile model variants at token-count-matched checkpoints, if training corpus deduplication removes repeated near-duplicate documents, then Pythia dedup-Pile models will show statistically significant per-benchmark performance differences compared to Pile models on at least one of {MMLU, HellaSwag, ARC-Challenge, WinoGrande} (Bonferroni-corrected α = 0.0125), because the presence or absence of repeated training documents with benchmark overlap produces a detectable signature in benchmark accuracy profiles.

**Rationale**: This is the foundational existence check. Before testing whether the signature correlates with contamination magnitude (mechanism), we must confirm the signature exists at all. If dedup-Pile and Pile models are statistically indistinguishable, the entire mechanistic hypothesis is falsified and no further testing is warranted.

**Variables** (from Phase 2A):
- Independent: Training corpus deduplication (categorical: Pile vs dedup-Pile)
- Dependent: Per-benchmark few-shot accuracy on MMLU, HellaSwag, ARC-Challenge, WinoGrande
- Controlled: Model architecture (GPT-NeoX), parameter count (160M/410M/1B/6.9B), token count (matched via 154 intermediate checkpoints), evaluation protocol

**Verification Protocol**:
1. Load Pythia dedup-Pile final checkpoint metadata to identify total training token count for each model size (160M, 410M, 1B, 6.9B).
2. Find the Pile intermediate checkpoint with closest token count using Pythia's 154-checkpoint index.
3. Run lm-evaluation-harness (identical version, identical few-shot prompts) on all 8 model variants (4 sizes × 2 corpus) at token-count-matched checkpoints.
4. Compute pairwise accuracy differences (dedup-Pile minus Pile) per benchmark per model size; apply paired t-test with Bonferroni correction (α = 0.0125 per benchmark).
5. Check if ≥1 benchmark shows p < 0.0125 at ≥2 model sizes — constitutes existence confirmation.

**Success Criteria** (PoC):
- Primary: At least one benchmark shows Bonferroni-corrected significant difference (p < 0.0125) at ≥2 model sizes
- Secondary: Performance differential direction is consistent across model sizes (not random sign)

**Failure Response**:
- IF fails: STOP — H0 supported; the contamination-correction mechanism is not detectable with this experimental design

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 (sh1_existence), Prediction P1

---

**H-M1: Deduplication Removes Contaminated Near-Duplicate Documents**

**Statement**: Under the setting of the Pile training corpus and its deduplicated variant, if exact substring deduplication is applied, then the removed documents will show measurably higher n-gram overlap with standard benchmark test sets than the retained documents, because exact substring deduplication by design targets repeatedly occurring content, and repeatedly occurring benchmark-adjacent content is a subset of such repetitions.

**Rationale**: This tests the first causal link — that the documents removed by deduplication are specifically those with benchmark overlap, not random documents. Confirming this link distinguishes contamination-correction from generic data-quality improvement as the mechanism.

**Variables**:
- Independent: Document status (removed by dedup vs retained in dedup-Pile)
- Dependent: Per-document n-gram overlap with benchmark test sets (13-gram overlap rate)
- Controlled: Benchmark test sets (MMLU/HellaSwag/ARC/WinoGrande fixed), n-gram tool version

**Verification Protocol**:
1. Sample ~10,000 documents from Pile that were removed by exact substring deduplication (using dedup-Pile vs Pile diff metadata or corpus-level diffing).
2. Sample ~10,000 retained documents from dedup-Pile (matching size distribution).
3. Apply 13-gram overlap estimation (google-research/deduplicate-text-datasets) against each benchmark test set.
4. Compute mean n-gram overlap for removed vs retained documents per benchmark.
5. Apply Mann-Whitney test — confirm removed documents show significantly higher benchmark overlap (p < 0.05).

**Success Criteria**:
- Primary: Removed documents show significantly higher n-gram overlap with ≥2 benchmarks (p < 0.05)
- Secondary: Effect is largest for high-contamination benchmarks (MMLU expected > WinoGrande)

**Failure Response**:
- IF fails: PIVOT — contamination-correction mechanism may not explain the H-E1 signature; data-quality alternative explanation becomes primary

**Dependencies**: H-E1 (signature must exist before testing its mechanism)

**Source**: Phase 2A Causal Step 1, Causal Step 2

---

**H-M2: Pile-Trained Models Develop Measurable Memorization of Repeated Benchmark-Adjacent Patterns**

**Statement**: Under the setting of Pythia Pile and dedup-Pile models at token-count-matched checkpoints, if Pile training corpus contains repeated documents with benchmark n-gram overlap, then Pile-trained models will show detectably higher min-k% probability scores on benchmark test items compared to dedup-Pile models, because repeated exposure to near-duplicate content encoding benchmark test patterns drives near-memorization of those patterns.

**Rationale**: This tests the memorization link in the causal chain — that the contaminated repetitions in Pile actually produce a memorization signal in the trained model, rather than merely being present without effect. Min-k% probability is an established proxy for pretraining data memorization.

**Variables**:
- Independent: Training corpus (Pile with repetitions vs dedup-Pile without)
- Dependent: Min-k% probability score on benchmark test items
- Controlled: Model size (run at 1B and 6.9B for power), checkpoint matched by token count, min-k% implementation (Shi et al. 2023 reference implementation)

**Verification Protocol**:
1. Load Pythia-1B and Pythia-6.9B (both Pile and dedup-Pile variants) at token-count-matched checkpoints.
2. Apply Shi et al. 2023 min-k% method to all benchmark test items (MMLU, HellaSwag, ARC, WinoGrande — full test sets, ≥500 items per benchmark).
3. Compute per-item min-k% probability; aggregate mean per benchmark per model.
4. Compare Pile vs dedup-Pile min-k% scores using paired t-test; apply Bonferroni correction across 4 benchmarks.
5. Check if high-contamination benchmarks (identified in H-M1) show larger memorization signal difference than low-contamination benchmarks.

**Success Criteria**:
- Primary: Pile models show significantly higher min-k% probability on ≥2 benchmarks vs dedup-Pile (p < 0.0125)
- Secondary: Magnitude of memorization difference correlates with benchmark contamination level from H-M1

**Failure Response**:
- IF fails: EXPLORE — min-k% may not capture near-memorization (vs verbatim); try alternative memorization metrics or document similarity approaches

**Dependencies**: H-M1 (contaminated documents must be confirmed removed before testing memorization effect)

**Source**: Phase 2A Causal Step 3

---

**H-M3: Performance Differential Direction Correlates with Contamination Magnitude**

**Statement**: Under the setting of Pythia dedup-Pile vs Pile benchmark accuracy differentials at token-count-matched checkpoints, if benchmarks vary in their estimated n-gram contamination overlap with the Pile corpus, then the per-benchmark accuracy differential (dedup-Pile minus Pile) will show positive correlation with contamination overlap estimate (Pearson r ≥ 0.5), because higher contamination means greater near-memorization advantage for Pile models and thus greater accuracy drop in dedup-Pile when that advantage is removed.

**Rationale**: This is the core quantitative mechanistic test — the distinguishing prediction of the contamination-correction hypothesis vs a generic data-quality hypothesis. A generic quality improvement would produce a uniform positive shift; the contamination-correction signature produces a graded response proportional to contamination level, with potentially negative differentials for high-contamination benchmarks.

**Variables**:
- Independent: Per-benchmark n-gram contamination overlap estimate (continuous, from H-M1)
- Dependent: Per-benchmark accuracy differential (dedup-Pile minus Pile) at token-count-matched checkpoints
- Controlled: Model size (aggregate across 160M/410M/1B/6.9B), token-count matching protocol, contamination estimator (dual: 13-gram + min-k%)

**Verification Protocol**:
1. Collect contamination estimates from H-M1 (13-gram overlap per benchmark) and H-M2 (min-k% differential per benchmark).
2. Collect accuracy differentials from H-E1 (dedup-Pile minus Pile per benchmark).
3. Compute Pearson and Spearman correlation between contamination estimate vector (4 benchmarks) and accuracy differential vector (4 benchmarks), aggregated across model sizes.
4. Test significance (p < 0.05) for both correlation estimators.
5. Report correlation coefficients with confidence intervals; check directionality (positive correlation confirms hypothesis).

**Success Criteria**:
- Primary: Pearson r ≥ 0.5 and Spearman ρ ≥ 0.5, p < 0.05, across both contamination estimators
- Secondary: High-contamination benchmarks show negative accuracy differentials (dedup-Pile scores lower)

**Failure Response**:
- IF fails (r < 0.3): EXPLORE — contamination may not be the primary driver; document volume effect (15% token reduction) may dominate; run robustness check with additional benchmarks

**Dependencies**: H-M1 (contamination estimates), H-M2 (memorization confirmation), H-E1 (accuracy differentials)

**Source**: Phase 2A Causal Step 4, Prediction P2

---

**H-M4: Token-Count Matching Controls for Data Volume Confound**

**Statement**: Under the setting of comparing step-matched vs token-count-matched Pythia checkpoint pairs, if the ~15% token reduction in dedup-Pile is a confound for the contamination-correction signature, then step-matched comparisons will show larger (possibly noisier) accuracy differentials than token-count-matched comparisons, and the contamination-performance correlation will be weaker under step-matching, because the volume effect adds a uniform downward shift that competes with the contamination-correction signal.

**Rationale**: This robustness check directly tests the key methodological concern identified by Prof. Rex in Phase 2A (Exchange 6): if token-count matching does not adequately control the volume confound, the H-M3 correlation result is confounded. Confirming that token-count matching changes the results validates the experimental design choice.

**Variables**:
- Independent: Checkpoint matching method (step-matched vs token-count-matched)
- Dependent: Accuracy differential magnitude and contamination-performance correlation coefficient
- Controlled: Model sizes, benchmarks, contamination estimators (same as H-M3)

**Verification Protocol**:
1. Run lm-evaluation-harness on step-matched Pythia checkpoint pairs (same training step for Pile and dedup-Pile).
2. Compute accuracy differentials under step-matching; compute contamination-performance correlation.
3. Compare correlation coefficient under step-matching vs token-count-matching (from H-M3).
4. If token-count matching yields stronger correlation and smaller uniform bias, volume confound is confirmed and controlled.
5. Report both results as robustness check in final analysis.

**Success Criteria**:
- Primary: Token-count-matched correlation ≥ step-matched correlation, demonstrating the methodological value of token-count matching
- Secondary: Step-matched differentials show larger uniform negative bias (consistent with volume effect)

**Failure Response**:
- IF fails (no difference between matching methods): document as robustness confirmation — volume confound is negligible with existing checkpoint granularity; simplifies interpretation

**Dependencies**: H-M3 (need correlation result from token-matched runs to compare)

**Source**: Phase 2A key_tension, A1, Causal mechanism note on data volume confound

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥1 benchmark p < 0.0125 at ≥2 model sizes | STOP — H0 supported, abort study |
| H-M1 | MUST_WORK | Removed docs show significantly higher contamination overlap | PIVOT — data-quality alternative becomes primary |
| H-M2 | SHOULD_WORK | Pile models show higher min-k% probability on ≥2 benchmarks | EXPLORE — try alternative memorization metrics |
| H-M3 | SHOULD_WORK | Pearson r ≥ 0.5, p < 0.05 for contamination-accuracy correlation | EXPLORE — extend to additional benchmarks; data volume may dominate |
| H-M4 | SHOULD_WORK | Token-matched correlation ≥ step-matched correlation | Document — volume confound negligible |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (H-M1: 2 wk, H-M2-4: 1 wk each) |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Insufficient Checkpoint Granularity for Token-Count Matching**
- Source Assumption: A1 — Pythia's 154 checkpoints may not permit matching within 5% of dedup-Pile token count
- Affected Hypotheses: H-E1, H-M2, H-M3, H-M4
- Severity: **High**
- Likelihood: Medium (154 checkpoints at logarithmic spacing; dedup-Pile ~207B tokens may not have close match)

**Mitigation Strategy:**
1. Prevention: Pre-check checkpoint metadata before running evaluations; compute exact token counts for all 154 Pile checkpoints and identify the closest match
2. Detection: If matching is outside ±5%, flag as approximation in all results tables
3. Response:
   - PIVOT: Report both step-matched and token-count-matched results; treat divergence as informative about volume effects (becomes H-M4 result)
   - SCOPE: If matching is >10% off, treat as robustness check rather than primary method

**Early Warning Indicators:**
- Pile checkpoint metadata shows logarithmic spacing with large gaps near 207B token mark
- Dedup-Pile final token count falls between two widely spaced intermediate Pile checkpoints

---

**Risk R2: Contamination Estimator Unreliability**
- Source Assumption: A2 — N-gram overlap estimates may not reliably reflect actual benchmark contamination
- Affected Hypotheses: H-M1, H-M3
- Severity: **High**
- Likelihood: Medium (4 benchmarks is a small correlation sample; min-k% can be noisy for short test items)

**Mitigation Strategy:**
1. Prevention: Use two independent estimators (13-gram overlap + min-k% probability); require consistency across both
2. Detection: If 13-gram and min-k% contamination rankings disagree, flag as estimator inconsistency
3. Response:
   - PIVOT: Add MMLU subcategory breakdown (57 subtasks) to increase correlation sample size from 4 to potentially 8-12 data points
   - SCOPE: If both estimators agree on ranking but disagree on magnitude, use rank correlation (Spearman) as primary metric

**Early Warning Indicators:**
- 13-gram overlap and min-k% produce different contamination rankings across the 4 benchmarks
- Correlation p-value is marginal (0.05 < p < 0.15) despite reasonable r

---

**Risk R3: Data Quality Loss Confound (Unique Documents Removed)**
- Source Assumption: A3 — Dedup removes representative repetitions, not uniquely informative content
- Affected Hypotheses: H-M1, H-M2, H-M3
- Severity: **Medium**
- Likelihood: Low (exact substring dedup by definition targets repeated, not unique, content)

**Mitigation Strategy:**
1. Prevention: Analyze removed document diversity (topic, perplexity) to confirm high-repetition characterization
2. Detection: If low-contamination benchmarks show unexpected large performance drops in dedup-Pile, flag data quality concern
3. Response:
   - EXPLORE: Check if performance drops on low-contamination benchmarks are consistent with topic-overlap explanation (not contamination-correction)

**Early Warning Indicators:**
- WinoGrande (expected low contamination) shows larger performance drop than MMLU (expected high contamination) in dedup-Pile models

---

**Risk R4: Statistical Power Insufficient for P2 Correlation Test**
- Source Assumption: A4 — 4 benchmark accuracy measurements may be underpowered for r ≥ 0.5 detection
- Affected Hypotheses: H-M3
- Severity: **Medium**
- Likelihood: Medium (n=4 gives 80% power for r≥0.8 but only ~50% for r≥0.5)

**Mitigation Strategy:**
1. Prevention: Use full benchmark test sets (not subsets) to minimize within-benchmark variance; aggregate across model sizes to create more data points per benchmark
2. Detection: Report power analysis with actual sample sizes before committing to correlation test
3. Response:
   - PIVOT: Expand to additional benchmarks if power is insufficient (BoolQ, PIQA, LAMBADA have public test sets and can be contamination-estimated)
   - SCOPE: Use per-model-size correlation (4 benchmarks × 4 sizes = 16 data points with mixed-effects model)

**Early Warning Indicators:**
- Power analysis shows < 70% power for r=0.5 with n=4 at α=0.05

---

**Risk R5: Confound from Architecture and Compute Differences**
- Source Assumption: A5 — Pythia Pile vs dedup-Pile isolates deduplication as sole curation variable
- Affected Hypotheses: All (H-E1 through H-M4)
- Severity: **Critical**
- Likelihood: Very Low (A5 is the strongest assumption — Biderman et al. explicitly designed for this comparison)

**Mitigation Strategy:**
1. Prevention: Document that Pythia Pile/dedup-Pile share identical architecture, optimizer, hyperparameters per Biderman et al. 2023 — this is a design guarantee, not an inference
2. Detection: Cross-check Biderman et al. 2023 Table 1 for any training differences not documented in the paper
3. Response:
   - ABORT: If undocumented training differences found, study cannot proceed without confound; report as limitation requiring new experimental setup

**Early Warning Indicators:**
- Biderman et al. 2023 supplemental materials reveal unreported differences in training setup

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Insufficient checkpoint granularity | A1 | H-E1, H-M2, H-M3, H-M4 | High |
| R2: Contamination estimator unreliability | A2 | H-M1, H-M3 | High |
| R3: Data quality loss confound | A3 | H-M1, H-M2, H-M3 | Medium |
| R4: Statistical power for correlation | A4 | H-M3 | Medium |
| R5: Architecture/compute confound | A5 | All | Critical |

**Risk Summary:**
- Critical: 1 (R5)
- High: 2 (R1, R2)
- Medium: 2 (R3, R4)
- Low: 0

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1: Contamination-Correction Signature Exists
    (EXISTENCE - no dependencies)
         │
         ▼
[Level 1 - Core Mechanism]
    H-M1: Deduplication Removes Contaminated Documents ← H-E1
         │
         ▼
[Level 2 - Memorization]
    H-M2: Pile Models Show Higher Memorization Signal ← H-M1
         │
         ▼
[Level 3 - Correlation]
    H-M3: Differential Correlates with Contamination ← H-M2, H-M1, H-E1
         │
         ▼
[Level 4 - Robustness]
    H-M4: Token-Count Matching Validates Design ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M1, H-M2, H-E1 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Verification Phases

**Phase 1 — Foundation:**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | Bonferroni-corrected significance on ≥1 benchmark at ≥2 model sizes | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP; H0 supported; contamination-correction mechanism unsupported.

**Phase 2 — Core Mechanisms (4 hypotheses):**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS |
| H-M2 | H-M1 | Should pass |
| H-M3 | H-M1, H-M2, H-E1 | Should pass |
| H-M4 | H-M3 | Should pass |

→ **Gate 2**: H-M1 must pass. Later H-M failures = document limitation, not abort.

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2   │ W3-4   │ W5     │ W6     │ W7
──────────────────┼────────┼────────┼────────┼────────┼────────
PHASE 1: Foundation
  H-E1            │ ██████ │        │        │        │
  [Gate 1]        │        │ ◆      │        │        │
──────────────────┼────────┼────────┼────────┼────────┼────────
PHASE 2: Mechanisms
  H-M1            │        │ ██████ │        │        │
  H-M2            │        │        │ ████   │        │
  H-M3            │        │        │        │ ████   │
  H-M4            │        │        │        │        │ ████
  [Gate 2]        │        │        │        │        │      ◆
──────────────────┼────────┼────────┼────────┼────────┼────────
═══════════════════════════════════════════════════════════════════
Legend: ██████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 + 1 + 1 (H-M2-4) = 7 weeks

Slack Available: 0 weeks (all sequential)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1, H-M2, H-M3, H-M4)
- Condition: 0 (scope boundaries are qualitative, not testable)

Verification Phases: 2
1. Foundation (H-E1)
2. Mechanisms (H-M1 to H-M4)

Total Duration: 7 weeks
Critical Path: 7 weeks
Execution Mode: Sequential chain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Execution Order

**Step 1**: Execute H-E1 (Foundation) — Week 1-2
**Step 2**: Evaluate Gate 1 → If pass, proceed; if fail, STOP
**Step 3**: Execute H-M1 (Contaminated docs removed) — Week 3-4
**Step 4**: Evaluate H-M1 Gate (MUST_WORK) → If fail, PIVOT to data-quality alternative
**Step 5**: Execute H-M2 (Memorization signal) — Week 5
**Step 6**: Execute H-M3 (Contamination-performance correlation) — Week 6
**Step 7**: Execute H-M4 (Token-count matching robustness) — Week 7
**Step 8**: Evaluate Gate 2 → Synthesize mechanism evidence

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Deduplication of pretraining corpora produces a
contamination-correction signature: per-benchmark accuracy
changes in dedup-Pile vs Pile are proportional to n-gram
contamination overlap between Pile and each benchmark's test set.

Supporting Evidence:
1. Three established mechanisms: dedup removes repeated docs
   (Biderman 2023); contamination is detectable (Shi 2023);
   repeated patterns inflate benchmark scores (Lee 2022)
2. Explicit experimental design by Biderman et al. for
   controlled Pile vs dedup-Pile comparison (A5 confirmed)
3. Testable, directional predictions pre-specified before
   seeing results (P1: Bonferroni sig; P2: r ≥ 0.5)

Strengths:
- Mechanism is physically plausible — memorization of repeated
  benchmark-adjacent content is established theory
- Uses existing open-source artifacts — no retraining needed
- Cross-family extension (OLMo) provides consistency check
- Pre-specified directional predictions resist post-hoc fitting

Expected Outcomes:
- P1: ≥1 benchmark Bonferroni-corrected significant (α=0.0125)
- P2: Contamination-differential correlation r ≥ 0.5
- P3 (exploratory): Dolma shows lower contamination than Pile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): At token-count-matched checkpoints,
Pythia dedup-Pile and Pile models show no statistically
significant difference in few-shot performance on any of
{MMLU, HellaSwag, ARC, WinoGrande} (Bonferroni α=0.0125),
and per-benchmark changes show no significant positive
correlation with contamination estimates.

Counter-Arguments:
1. Data volume confound: dedup-Pile has ~15% fewer tokens —
   volume reduction alone could explain performance differences
   without any contamination-specific mechanism
2. Contamination estimates are proxies — 13-gram overlap and
   min-k% may not reliably capture the specific repeated
   patterns that cause benchmark inflation
3. 4-benchmark correlation (P2 with n=4) is statistically
   underpowered — r≥0.5 detection requires large effect size
   for significance with so few data points

Potential Failure Points:
- R1: Checkpoint granularity too coarse for token-count match
- R2: Contamination estimators produce inconsistent rankings
- R4: n=4 correlation test yields marginal, unreplicable result

Conditions Under Which H0 Would Be Supported:
- All 4 benchmarks show p > 0.0125 in pairwise comparisons
- Contamination-accuracy correlation r < 0.3
- Token-count-matched and step-matched results are identical
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment: H-ContaminationCorrectionSignature-v1
presents a theoretically well-grounded and operationally
feasible claim with pre-specified directional predictions.
However, the antithesis raises three legitimate technical
challenges: data volume confound, estimator reliability,
and statistical power for the correlation test.

Resolution Path: The verification plan addresses this dialectic:
1. H-E1 tests existence with Bonferroni correction — if
   signature is not detectable, no further testing warranted
2. H-M1 and H-M2 test whether the proposed mechanism
   (contaminated doc removal → memorization reduction) is
   the actual driver vs generic quality improvement
3. H-M4 explicitly tests the volume confound (token-matched
   vs step-matched), providing a definitive resolution of
   the most serious antithesis concern

Conditions for Thesis Support:
- H-E1 and H-M1 MUST_WORK gates pass
- H-M3 correlation r ≥ 0.5 confirms quantitative prediction
- H-M4 confirms token-count matching resolves volume confound

Conditions for Antithesis Support:
- H-E1 fails: no detectable signature → H0 fully supported
- H-M1 fails: contaminated docs not selectively removed →
  contamination-correction mechanism is incorrect
- H-M3 r < 0.3 and H-M4 shows no difference between matching
  methods → volume effect dominates, not contamination

Nuanced Outcome Possibilities:
1. Full Support: All hypotheses pass → thesis validated,
   contamination-correction signature confirmed
2. Partial Support: H-E1/H-M1 pass, H-M3 marginal →
   refined thesis: signature exists but magnitude modest
3. Volume Dominates: H-E1 passes but H-M3 fails, H-M4
   shows step-matched ≈ token-matched → volume explanation
4. No Support: H-E1 fails → H0 supported, study terminated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Per-benchmark differential is detectable with Bonferroni correction | No significant differences exist; noise dominates | H-E1 test (n=4 model sizes, 4 benchmarks) |
| Mechanism: doc removal | Dedup removes contaminated docs selectively | Dedup removes random docs; contamination profile unchanged | H-M1 test (removed vs retained doc n-gram overlap) |
| Mechanism: memorization | Pile models develop memorization of repeated patterns | Repeated content doesn't cause detectable memorization | H-M2 test (min-k% probability comparison) |
| Mechanism: correlation | Differential proportional to contamination magnitude | Generic quality effect; no contamination-specific pattern | H-M3 test (Pearson/Spearman correlation, n=4 or extended) |
| Validity: volume confound | Token-count matching removes data volume confound | 15% token reduction is the actual cause, not contamination | H-M4 test (step-matched vs token-matched comparison) |

**Overall Robustness Score:** High (well-specified mechanism, pre-specified predictions, explicit confound controls)

**Confidence in Verification Plan:** 0.78

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Deduplication produces a contamination-correction signature — per-benchmark accuracy changes correlated with n-gram contamination overlap between Pile and benchmark test sets.
- ID: H-ContaminationCorrectionSignature-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (60% scope reduction — 3 of 5 claims are BUILD_ON)
- Sub-Hypotheses: 5 total (H-E1 + H-M1–H-M4)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (Gate 1: existence, Gate 2: mechanism chain)

**Risk Assessment:** High
- Primary concerns: (1) checkpoint granularity for token-count matching, (2) statistical power for 4-benchmark correlation test

**Immediate Action:** Begin Phase 1 with H-E1 — run lm-evaluation-harness on 8 Pythia model variants at token-count-matched checkpoints

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases, fully specified with verification protocols
- H0 addressed: all falsification conditions explicitly defined
- 60% scope reduction via BUILD_ON claim separation

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Confirm per-benchmark significant difference exists (Bonferroni-corrected)
- Gate 1: MUST PASS — failure terminates study

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Dedup removes contaminated documents (MUST PASS)
- H-M2: Pile models show memorization signal (should pass)
- H-M3: Contamination-accuracy correlation r ≥ 0.5 (should pass)
- H-M4: Token-count matching robustness check (should pass)
- Gate 2: H-M1 must pass; H-M2-4 failures documented as limitations

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP; H0 supported; contamination-correction unsupported
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → PIVOT to data-quality alternative explanation
   - H-M2-4 FAIL → Document as limitation; publish existence result (H-E1) with incomplete mechanism

**Open Questions:**
- What is Pythia's checkpoint resolution near 207B tokens — can we match within 5%?
- Do google-research/deduplicate-text-datasets n-gram tools support corpus-vs-benchmark overlap without full index?
- Is n=4 benchmarks sufficient for P2 correlation, or must we extend to MMLU subcategories?

**Recommendations:**

1. **Immediate Actions:**
   - Pre-check Pythia checkpoint token count metadata (resolves R1 before committing to protocol)
   - Run lm-eval-harness pilot on Pythia-160M only to validate evaluation pipeline

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path
   - Reserve 2-week buffer for contamination estimation setup (n-gram tools can be slow on large corpora)

3. **Failure Management:**
   - Document all gate results regardless of outcome
   - If H-M3 underpowered, execute MMLU subcategory expansion before concluding failure

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-ContaminationCorrectionSignature-v1)
- Generated: 2026-08-25, 8 exchanges, 6 convergence criteria met

**Appendix B: MCP Tool Usage**
- Total MCP calls: 0 (no-MCP ablation mode — LLM-based analysis used throughout)
- Scope: Incremental mode (Phase 2A pre-mapped hypothesis structure used directly)
