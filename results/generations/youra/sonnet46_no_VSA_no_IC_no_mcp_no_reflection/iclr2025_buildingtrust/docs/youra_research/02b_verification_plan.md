---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-08-31T00:00:00Z"
hypothesisId: H-AlignFingerprint-v1
researchMode: incremental
totalHypotheses: 4
---

# Verification Plan: Alignment Fingerprinting — DPO vs SFT Trustworthiness Profile Detection

**Date:** 2026-08-31
**Hypothesis ID:** H-AlignFingerprint-v1
**Confidence:** 0.72
**Total Hypotheses:** 4 (H-E1, H-M1, H-M2, H-M3)
**Research Mode:** Incremental (Phase 2A available)
**Scope Reduction:** 60% (3 BUILD_ON claims skipped)

---

## 0. Established Facts & Scope Reduction

### 0.1 Established Facts Registry (DO NOT RE-VERIFY)

| Claim | Status | Evidence |
|-------|--------|----------|
| RLHF-aligned models score higher than SFT-only on TruthfulQA | BUILD_ON | InstructGPT (Ouyang et al., 2022, arXiv:2203.02155) |
| DPO achieves RLHF-comparable alignment quality on MT-Bench | BUILD_ON | DPO paper (Rafailov et al., 2023, arXiv:2305.18290) |
| Multi-dimensional trustworthiness benchmarks are not perfectly correlated | BUILD_ON | DecodingTrust (Wang et al., 2023, arXiv:2306.11698) |

**Scope Reduction:** 3/5 claims (60%) treated as established baselines. Phase 2B focuses only on PROVE_NEW claims.

### 0.2 PROVE_NEW Claims (Verification Targets)

| Claim | Target Hypothesis |
|-------|------------------|
| DPO vs SFT trustworthiness profile difference is detectable via benchmark suite | H-E1 |
| Alignment strategy produces a classifiable fingerprint in 4D benchmark space | H-M1, H-M2, H-M3 |

**Transfer Validation:** Not applicable (no cross-domain mechanism transfer in this hypothesis).

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under inference-only evaluation of 7B-parameter language models fine-tuned on the same base model with matched data using DPO vs SFT alignment strategies, if we evaluate models on a 4-benchmark trustworthiness suite (TruthfulQA MC2, BBQ, WinoGrande, WinoGender), then DPO-aligned models will exhibit a systematically different trustworthiness profile from SFT-aligned models — specifically higher fairness scores (BBQ, WinoGender) and neutral-to-lower truthfulness scores (TruthfulQA MC2) — and this profile difference will be detectable by a k-NN classifier with leave-one-out cross-validation (≥67% accuracy, permutation p≤0.05 across ≥6 matched model pairs), because DPO preference optimization rewards annotator-preferred responses that avoid bias-triggering patterns without explicitly rewarding factual accuracy.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in the 4D trustworthiness profile (TruthfulQA MC2, BBQ, WinoGrande, WinoGender scores) between DPO-aligned and SFT-aligned models trained on matched data; k-NN classifier accuracy is at or below chance (≤50%) and permutation test p > 0.05. BBQ fairness scores show no consistent directional pattern (sign test p > 0.125).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA MC2 + BBQ + WinoGrande + WinoGender (lm-evaluation-harness) | All 4 benchmarks measure distinct trustworthiness dimensions and are standard lm-eval tasks requiring no custom data collection |
| **Model** | HuggingFaceH4/zephyr-7b-sft-full + zephyr-7b-dpo-full (primary pair) + ≥5 community DPO/SFT pairs | Best available controlled comparison: same base model (Mistral-7B), same training data, only alignment strategy differs |

**Dataset Details:**
- Source: EleutherAI/lm-evaluation-harness
- Path: `pip install lm-eval; lm_eval --tasks truthfulqa_mc2,bbq,winogrande,winograd_wsc`

**Model Details:**
- Type: 7B autoregressive language model
- Source: HuggingFace Hub — alignment-handbook official checkpoints + community

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Majority-class classifier | 50% (if balanced classes) | Any | Does not use benchmark features; lower bound |
| Random classifier | 50% | Any | 2-class baseline; lower bound |
| Single-benchmark k-NN (TruthfulQA MC2 only) | Unknown | TruthfulQA MC2 | Tests whether 4D adds value over best single benchmark |
| InstructGPT RLHF | RLHF > SFT on TruthfulQA | TruthfulQA subset | No DPO comparison, no unified suite, no fingerprinting |
| DecodingTrust GPT eval | Multi-dim scores for GPT-3.5/4 | DecodingTrust 8-dim | Alignment strategy not IV; models differ in capability AND alignment simultaneously |

### 1.5 Key Assumptions

| ID | Assumption | Supporting Evidence | If Violated |
|----|------------|--------------------|----|
| A1 | ≥6 DPO/SFT matched model pairs with clear documentation on HuggingFace Hub | alignment-handbook provides at least 1 clean pair (Zephyr); community adds more | Insufficient pairs for permutation test; study becomes descriptive/pilot |
| A2 | lm-evaluation-harness correctly implements TruthfulQA MC2, BBQ, WinoGrande | Standard tasks with extensive community testing; version pinned | Benchmark scores may not measure intended constructs |
| A3 | Base model architecture and size controlled by selecting matched pairs | alignment-handbook SFT/DPO pairs use identical base models | Profile differences may be attributable to base model variation |
| A4 | DPO preference data encodes bias-avoidance at sufficient density for measurable BBQ/WinoGender effects | UltraFeedback and similar datasets penalize stereotyped responses | DPO fairness advantage absent; null result on fairness dimensions |
| A5 | k-NN (k=1) in 4D Euclidean space is appropriate for small n | Non-parametric, no distributional assumptions, LOO valid for small n | Different distance metrics or k values may be needed |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First empirical demonstration of alignment fingerprinting via classifier in standard benchmark score space — treating alignment strategy identification as a detection problem rather than an explanation problem.

**Key Innovation:** Reframes alignment-trustworthiness question as a classification/detection task: can you identify a model's alignment strategy from its 4D benchmark profile alone? Methodologically agnostic about mechanism while being directly practically useful for model auditing.

**Differentiation:**
- DecodingTrust: Evaluates GPT models across trustworthiness dimensions but does not use alignment strategy as IV or test fingerprinting/classification
- InstructGPT: Evaluates RLHF vs SFT on TruthfulQA only — no DPO, no unified multi-benchmark suite, no fingerprinting framing
- DPO paper: Evaluates on capability benchmarks (MT-Bench) only — no trustworthiness benchmarks, no SFT comparison on unified trust suite

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Alignment Strategy Produces Measurably Different 4D Trustworthiness Profile

**Type:** EXISTENCE
**Statement:** Under inference-only evaluation of ≥6 matched DPO/SFT 7B model pairs on a 4-benchmark trustworthiness suite (TruthfulQA MC2, BBQ, WinoGrande, WinoGender) via lm-evaluation-harness, the 4D benchmark score vectors of DPO-aligned models will be systematically separable from SFT-aligned models, detectable by a k-NN (k=1) classifier with leave-one-out cross-validation achieving ≥67% accuracy and permutation test p≤0.05 (1000 permutations).

**Rationale:**
This is the foundational existence check — the entire hypothesis rests on whether a detectable trustworthiness profile fingerprint exists at all. If the fingerprint does not exist (k-NN accuracy ≤50%), then neither the mechanism hypotheses nor any downstream claims about DPO's selective bias-avoidance can be supported empirically. The k-NN detection framing makes this maximally falsifiable: either the separation is statistically detectable or it is not.

**Variables (from Phase 2A):**
- Independent: Alignment strategy (DPO vs SFT; categorical, 2 levels)
- Dependent: k-NN LOO cross-validation accuracy over 4D benchmark vector (primary); 4D score vector per model pair (TruthfulQA MC2, BBQ, WinoGrande, WinoGender)
- Controlled: Base model architecture (matched pairs, same base checkpoint); model size (7B only); evaluation harness version (pinned commit hash)

**Verification Protocol:**
1. Curate ≥6 matched DPO/SFT 7B model pairs from alignment-handbook + community; document alignment evidence for each pair.
2. Pin lm-evaluation-harness version; confirm BBQ and WinoGender task availability; run all 4 benchmarks for all models.
3. Construct n×4 score matrix; verify reproducibility with 2-run check on 2 random models.
4. Run sklearn k-NN (k=1, Euclidean) LOO CV on n×4 matrix with DPO/SFT binary labels.
5. Run permutation test (1000 permutations, random label shuffling); report LOO accuracy and p-value.

**Success Criteria (PoC: Direction-based):**
- Primary: LOO accuracy ≥ 0.67 AND permutation p ≤ 0.05
- Informative null: LOO accuracy < 0.50 = fingerprint absent (publishable null result)
- Inconclusive zone: 0.50 ≤ accuracy < 0.67 = fingerprint weak/present but below threshold

**Failure Response:**
- IF LOO accuracy < 0.50: ABANDON fingerprint framing; result is informative null — publish as "standard benchmarks cannot detect alignment strategy"
- IF 0.50 ≤ accuracy < 0.67: EXPLORE — expand model pairs, try alternative distance metrics (cosine, Mahalanobis); document as inconclusive

**Dependencies:** None (foundation hypothesis)
**Source:** Phase 2A Section 5 (sh1_existence), Section 1.6 (P1)

---

#### H-M1: DPO Preference Optimization Encodes Bias-Avoidance Signal from Human Annotator Preferences

**Type:** MECHANISM
**Statement:** Under inference-only evaluation of matched DPO/SFT 7B model pairs, if DPO training data (human preference pairs) systematically rewards responses that avoid bias-triggering language, then DPO-trained models will score higher on BBQ (social bias avoidance) and WinoGender (gender bias avoidance) benchmarks compared to matched SFT-trained models, with directional consistency in ≥4/6 matched pairs on BBQ (one-sided binomial sign test, p≤0.125).

**Rationale:**
This tests the first causal step: that DPO's preference optimization signal carries sufficient bias-avoidance information to produce measurable downstream effects on fairness benchmarks. A positive result on H-M1 distinguishes the mechanism from a generic "DPO improves everything" story — the prediction is selective (fairness up, not truthfulness). H-M1 depends on H-E1 having confirmed a detectable profile difference exists.

**Variables (from Phase 2A):**
- Independent: Alignment strategy (DPO vs SFT)
- Dependent: BBQ score (primary for H-M1); WinoGender score (secondary); sign of (BBQ_DPO - BBQ_SFT) per pair
- Controlled: Base model, size, evaluation harness version, training data source (documented per pair)

**Verification Protocol:**
1. Use BBQ and WinoGender scores from H-E1 benchmark run (no additional compute required).
2. For each matched pair, compute sign of (BBQ_DPO - BBQ_SFT) and (WinoGender_DPO - WinoGender_SFT).
3. Count pairs where DPO > SFT on BBQ; run one-sided binomial sign test (n≥6, k=count of DPO>SFT).
4. Repeat for WinoGender as secondary check.
5. Compute Fisher's criterion for BBQ and WinoGender to assess discriminative power.

**Success Criteria (PoC: Direction-based):**
- Primary: ≥4/6 pairs show DPO > SFT on BBQ; binomial p ≤ 0.125 (one-sided, n=6)
- Secondary: ≥4/6 pairs show DPO > SFT on WinoGender (exploratory, no strict threshold)

**Failure Response:**
- IF ≤3/6 pairs show DPO > SFT on BBQ: EXPLORE — check whether community model confounds explain absence; PIVOT to descriptive framing without directional mechanism claim

**Dependencies:** H-E1 (existence must be confirmed)
**Source:** Phase 2A Section 1.3 (causal step 1), Section 1.6 (P3)

---

#### H-M2: DPO Lacks Explicit Factual Accuracy Reward Producing Neutral-to-Lower TruthfulQA Scores

**Type:** MECHANISM
**Statement:** Under inference-only evaluation of matched DPO/SFT 7B model pairs, if DPO's training objective maximizes preference likelihood without explicit factual accuracy reward while SFT instruction data includes explicit factual Q&A pairs, then SFT-aligned models will score equal-to-or-higher on TruthfulQA MC2 compared to matched DPO-aligned models, with TruthfulQA MC2 showing the highest between-group variance relative to within-group variance (Fisher's criterion) among the 4 benchmark dimensions.

**Rationale:**
This tests the second causal step: that the absence of an explicit truthfulness reward in DPO produces a measurable signal in the TruthfulQA dimension. The Fisher's criterion prediction is particularly important — if TruthfulQA MC2 is the most discriminative single dimension, it supports the mechanism story that DPO's divergence from SFT is strongest on the factual accuracy axis. This is a directional claim that can be falsified if BBQ or WinoGrande ranks higher by Fisher's criterion.

**Variables (from Phase 2A):**
- Independent: Alignment strategy (DPO vs SFT)
- Dependent: TruthfulQA MC2 score (primary for H-M2); Fisher's criterion rank among 4 benchmarks
- Controlled: Same as H-M1

**Verification Protocol:**
1. Use TruthfulQA MC2 scores from H-E1 benchmark run.
2. Compute Fisher's criterion = (μ_DPO - μ_SFT)² / (σ²_DPO + σ²_SFT) for each of 4 benchmarks.
3. Rank benchmarks by Fisher's criterion; check if TruthfulQA MC2 ranks first.
4. Compute sign of (TruthfulQA_SFT - TruthfulQA_DPO) per pair to check directionality.
5. Document as supporting H-M2 if TruthfulQA MC2 ranks first by Fisher's criterion.

**Success Criteria (PoC: Direction-based):**
- Primary: TruthfulQA MC2 ranks first among 4 benchmarks by Fisher's criterion
- Secondary: ≥4/6 pairs show SFT ≥ DPO on TruthfulQA MC2 (directional consistency)

**Failure Response:**
- IF another benchmark ranks first by Fisher's criterion: EXPLORE — document which dimension is most discriminative; partial support for overall fingerprint even without mechanism confirmation

**Dependencies:** H-M1 (mechanism chain — H-M2 builds on bias-avoidance signal confirmed in H-M1)
**Source:** Phase 2A Section 1.3 (causal step 2), Section 1.6 (P2)

---

#### H-M3: DPO-SFT Profile Divergence Creates Detectable Fingerprint Shape in 4D Benchmark Space

**Type:** MECHANISM
**Statement:** Under inference-only evaluation of ≥6 matched DPO/SFT 7B model pairs, if DPO systematically improves fairness benchmarks (BBQ, WinoGender) while SFT maintains higher or equal truthfulness (TruthfulQA MC2), then the combined 4D profile shape — not just overall score level — constitutes a detectable alignment fingerprint, evidenced by the k-NN classifier's above-chance performance being driven by the multi-dimensional shape rather than any single benchmark dimension (confirmed by comparison of 4D vs 1D k-NN accuracy).

**Rationale:**
This tests the third causal step: that the combination of H-M1 (fairness advantage) and H-M2 (truthfulness parity/disadvantage) jointly produce a recognizable multi-dimensional profile shape. The critical test is whether the 4D classifier outperforms the best single-dimension classifier — if 4D ≈ 1D (TruthfulQA MC2 alone), then the "profile shape" framing is not supported. H-M3 provides the synthesis of the mechanism chain into the fingerprinting claim.

**Variables (from Phase 2A):**
- Independent: Alignment strategy (DPO vs SFT)
- Dependent: Δ accuracy (4D k-NN vs best single-dim k-NN); dimensionality contribution to classification
- Controlled: Same model pairs as H-E1/H-M1/H-M2; same k-NN setup (k=1, Euclidean, LOO)

**Verification Protocol:**
1. Run 4 additional single-dimension k-NN classifiers (one per benchmark) using same LOO CV setup.
2. Compare 4D LOO accuracy vs best single-dimension LOO accuracy.
3. If 4D > best 1D: profile shape contributes beyond single dimension → H-M3 supported.
4. If 4D ≈ best 1D: fingerprint is effectively one-dimensional → H-M3 partially supported (fingerprint exists but is simpler than claimed).
5. Document contribution breakdown for paper.

**Success Criteria (PoC: Direction-based):**
- Primary: 4D k-NN accuracy > best single-dimension k-NN accuracy (profile shape adds value)
- Secondary: Multiple benchmarks contribute non-zero discriminative power (Fisher's criterion > 0 for ≥2 benchmarks)

**Failure Response:**
- IF 4D ≈ best 1D: EXPLORE — simplify claim from "4D profile fingerprint" to "single-dimension alignment signal"; still publishable with revised framing

**Dependencies:** H-M2 (completes the 3-step mechanism chain)
**Source:** Phase 2A Section 1.3 (causal step 3), Section 1.6 (P2, P1 joint)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | LOO accuracy ≥0.67 AND permutation p≤0.05 | STOP — publish informative null or pivot entirely |
| H-M1 | MUST_WORK | ≥4/6 pairs BBQ DPO>SFT, binomial p≤0.125 | EXPLORE confounds; PIVOT to descriptive framing |
| H-M2 | SHOULD_WORK | TruthfulQA MC2 ranks first by Fisher's criterion | Document limitation; partial mechanism support still valid |
| H-M3 | SHOULD_WORK | 4D accuracy > best 1D accuracy | Simplify to 1D fingerprint claim; still publishable |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Gate 1 | Decision point | End of Week 2 |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 3 weeks |
| Gate 2 | Decision point | End of Week 5 |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): Insufficient Model Pairs**
- Description: Fewer than 6 clean DPO/SFT matched pairs identified on HuggingFace Hub with sufficient alignment documentation
- Severity: High
- Likelihood: Medium
- Affected Hypotheses: H-E1, H-M1 (permutation test requires ≥6 pairs for p≤0.05)
- Mitigation:
  1. Prevention: Begin model curation before benchmark runs; target 8-10 pairs to have buffer
  2. Detection: After Phase 1 model survey, count clean pairs before any compute
  3. Response: IF <6 clean pairs → SCOPE: relabel as pilot study, use exact binomial for whatever n available; document as limitation
- Early Warning: <5 pairs found after 1 week of curation

**Risk R2 (from A2): lm-eval-harness Task Incompatibility**
- Description: BBQ task or WinoGender not correctly available in pinned lm-eval version; score does not measure intended construct
- Severity: Medium
- Likelihood: Medium
- Affected Hypotheses: H-M1 (BBQ, WinoGender), H-M2 (TruthfulQA MC2)
- Mitigation:
  1. Prevention: Pre-run compatibility check on 1 model before full evaluation; pin harness commit
  2. Detection: Compare scores on Zephyr-7B-DPO against published numbers (alignment-handbook reports)
  3. Response: IF BBQ unavailable → PIVOT to WinoGrande as fairness proxy; IF WinoGender unavailable → drop WinoGender (3D instead of 4D); document substitution
- Early Warning: Zephyr-7B TruthfulQA MC2 score deviates >5 points from published benchmarks

**Risk R3 (from A3): Base Model Confound**
- Description: Community DPO/SFT pairs may use different base model checkpoints, introducing confounds not controlled by matching
- Severity: Medium
- Likelihood: Medium
- Affected Hypotheses: H-M1 to H-M3 (all mechanism hypotheses)
- Mitigation:
  1. Prevention: Document base model checkpoint for every pair; flag any pairs without confirmed matching
  2. Detection: Stratify results by "clean alignment-handbook pairs" vs "community pairs"; check if pattern holds in clean pairs alone
  3. Response: IF clean pairs (n=1-3) show same pattern as community pairs → confound is unlikely; IF divergent → restrict claims to alignment-handbook pairs only
- Early Warning: >30% of pairs cannot confirm base model match

**Risk R4 (from A4): DPO Preference Data Lacks Bias-Avoidance Signal**
- Description: DPO preference pairs used by community models may not encode sufficient bias-avoidance signal to produce measurable BBQ/WinoGender effects
- Severity: Medium
- Likelihood: Medium
- Affected Hypotheses: H-M1 (directional prediction for BBQ)
- Mitigation:
  1. Prevention: Document preference dataset used for each DPO model pair; flag pairs using datasets known to not emphasize safety/bias
  2. Detection: Null result on BBQ sign test (≤3/6 DPO>SFT)
  3. Response: IF null on BBQ → PIVOT: drop directional mechanism claim; retain fingerprint claim if H-E1 passes; document as "fingerprint exists but mechanism is not bias-avoidance"
- Early Warning: After running H-E1, BBQ dimension shows near-zero Fisher's criterion

**Risk R5 (from A5): k-NN (k=1) Instability in Small-n Setting**
- Description: k-NN with k=1 may produce unstable LOO estimates when n is small (6-10 pairs); a single outlier pair could dominate classification
- Severity: Low
- Likelihood: Low
- Affected Hypotheses: H-E1, H-M3 (both use k-NN LOO)
- Mitigation:
  1. Prevention: Plan sensitivity analysis — run k=3 and k=5 alongside k=1; report all three
  2. Detection: Compare k=1, k=3, k=5 accuracy; high variance = instability
  3. Response: IF k=1 unstable → report k that maximizes accuracy as primary; permutation test still valid regardless of k
- Early Warning: k=1 and k=3 differ by >20 percentage points in LOO accuracy

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Insufficient model pairs | A1 | H-E1, H-M1, H-M2, H-M3 | High |
| R2: lm-eval incompatibility | A2 | H-M1, H-M2 | Medium |
| R3: Base model confound | A3 | H-M1, H-M2, H-M3 | Medium |
| R4: DPO lacks bias-avoidance signal | A4 | H-M1 | Medium |
| R5: k-NN k=1 instability | A5 | H-E1, H-M3 | Low |

**Critical Risks:** 0 | **High Risks:** 1 (R1) | **Medium Risks:** 3 (R2, R3, R4) | **Low Risks:** 1 (R5)

### 4.3 Baseline Failure Pattern Analysis

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| InstructGPT: no DPO, no unified suite | Out-of-scope comparison requests | Pre-register scope; DPO vs SFT only |
| DecodingTrust: model version confounded with alignment | Reviewer challenge on comparability | Emphasize matched-pair design as key control |
| DPO paper: no trustworthiness benchmarks | Gap between established result and ours | Frame as novel extension, not replication |

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1 (EXISTENCE — no prerequisites)
    Gate: MUST_WORK
         │
         ▼
[Level 1 - Core Mechanism: Bias-Avoidance Signal]
    H-M1 ← H-E1
    Gate: MUST_WORK
         │
         ▼
[Level 2 - Core Mechanism: Factual Accuracy Gap]
    H-M2 ← H-M1
    Gate: SHOULD_WORK
         │
         ▼
[Level 3 - Synthesis: Profile Shape Detection]
    H-M3 ← H-M2
    Gate: SHOULD_WORK
         │
         ▼
    [COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
No parallelization (all sequential)
═══════════════════════════════════════════════════════════
```

### 5.2 Verification Phases with Gate Conditions

**Phase 1 — Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | k-NN LOO CV on 4D benchmark scores, n≥6 pairs | MUST_WORK |

→ **Gate 1:** If H-E1 fails (accuracy <0.50) → STOP, publish informative null. If inconclusive (0.50–0.67) → EXPLORE.

**Phase 2 — Core Mechanisms (3 hypotheses)**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST_WORK |
| H-M2 | H-M1 | SHOULD_WORK |
| H-M3 | H-M2 | SHOULD_WORK |

→ **Gate 2:** H-M1 must pass. H-M2/H-M3 failures narrow mechanism claims but do not invalidate fingerprint.

### 5.3 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 4 Hypotheses (5 Weeks Total)
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2          │ W3-4          │ W5
─────────────────┼───────────────┼───────────────┼──────────────
PHASE 1: Foundation
  H-E1           │ ████████████ │               │
  [Gate 1]       │             ◆│               │
─────────────────┼───────────────┼───────────────┼──────────────
PHASE 2: Mechanisms
  H-M1           │               │ ████████████ │
  H-M2           │               │               │ ████
  H-M3           │               │               │     ████
  [Gate 2]       │               │              ◆│
─────────────────┼───────────────┼───────────────┼──────────────
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════

Note: H-M1 takes 2 weeks (W3-4) because it includes benchmark run
infrastructure setup (model curation, harness pinning, reproducibility
check). H-M2 and H-M3 are computed from the same benchmark run
(no additional inference needed) — 1 week each for analysis and
documentation.
```

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) - 1 (H-M2/H-M3
           share same benchmark run as H-M1) = 5 weeks
Slack Available: 0 weeks (all sequential)

Note: H-M1, H-M2, H-M3 share the same benchmark run compute.
H-M2 and H-M3 are primarily statistical analysis tasks on the
existing score matrix — minimal additional compute.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (not applicable)

Verification Phases: 2
1. Foundation (H-E1) — 2 weeks
2. Mechanisms (H-M1, H-M2, H-M3) — 3 weeks

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain

Compute Estimate: ~32 GPU hours (A100)
- Phase 1: ~20 GPU hours (all model pairs, all 4 benchmarks)
- Phase 2: ~12 GPU hours (2-run reproducibility check on 2 models)
- Analysis: CPU only (sklearn k-NN, permutation test, Fisher's criterion)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Execution Order

```
Step 1: Curate ≥6 matched DPO/SFT 7B model pairs (Week 1)
Step 2: Pin lm-evaluation-harness; confirm task availability (Week 1)
Step 3: Execute H-E1 — run all benchmarks for all models (Week 1-2)
Step 4: Evaluate Gate 1 — compute k-NN LOO + permutation test (End Week 2)
        IF accuracy <0.50: STOP → publish informative null
        IF accuracy ≥0.67 AND p≤0.05: PASS → proceed
        IF 0.50≤accuracy<0.67: EXPLORE
Step 5: Execute H-M1 — BBQ/WinoGender sign test (Week 3-4)
Step 6: Execute H-M2 — Fisher's criterion rank (Week 4)
Step 7: Execute H-M3 — 4D vs 1D k-NN comparison (Week 5)
Step 8: Evaluate Gate 2 — H-M1 must pass (End Week 5)
Step 9: Write up results and submit
```

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim:
  DPO-aligned 7B LMs exhibit a detectable trustworthiness profile
  fingerprint in standard benchmark score space (4D: TruthfulQA MC2,
  BBQ, WinoGrande, WinoGender), identifiable by k-NN LOO CV with
  ≥67% accuracy and permutation p≤0.05 over ≥6 matched model pairs.
  The mechanism is DPO's selective bias-avoidance reward without
  explicit factual accuracy reward, producing a characteristic 4D
  shape (higher fairness, neutral-to-lower truthfulness).

Supporting Evidence:
1. DPO and RLHF training objectives demonstrably different from SFT
   (Rafailov et al., 2023; Ouyang et al., 2022) — objective difference
   is a necessary condition for profile divergence
2. Trustworthiness dimensions are partially independent (DecodingTrust,
   Wang et al., 2023) — makes selective profile shift mechanistically
   possible
3. Human annotators systematically prefer bias-avoiding responses in
   UltraFeedback and similar DPO datasets — provides the implicit
   signal for bias-avoidance reward

Strengths:
- Inference-only design: no training access needed, highly reproducible
- Detection framing: maximally falsifiable (accuracy < 0.50 = null)
- Matched-pair control: strongest available control for confounds
- Both positive and null results are impactful and publishable
- k-NN + permutation test: valid for small n, no distributional assumptions

Expected Outcomes:
- Primary (P1): LOO accuracy ≥0.67, permutation p≤0.05
- Secondary (P2): TruthfulQA MC2 ranks first by Fisher's criterion
- Tertiary (P3): BBQ DPO>SFT in ≥4/6 pairs, binomial p≤0.125
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis Development

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0):
  There is no significant difference in the 4D trustworthiness
  profile between DPO and SFT models trained on matched data;
  k-NN accuracy ≤50%, permutation p>0.05, BBQ no consistent
  directional pattern.

Counter-Arguments:
1. DPO paper (Rafailov et al.) showed DPO ≈ RLHF on MT-Bench —
   if DPO and SFT converge on capability benchmarks, they may
   also converge on trustworthiness benchmarks via the same
   generalization mechanism
2. Community DPO models may use vastly different preference data
   (some safety-focused, some not) — heterogeneity in preference
   data source could wash out any systematic signal
3. 4-benchmark suite is a narrow proxy for trustworthiness;
   the specific benchmarks chosen may not be sensitive enough
   to detect the hypothesized DPO-specific signal

Potential Failure Points:
- R1: <6 clean model pairs → underpowered permutation test
- R4: DPO preference data lacks bias-avoidance density → no BBQ signal
- R3: Community model confounds → spurious between-group variance

Conditions Under Which H0 Would Be Supported:
- k-NN LOO accuracy < 0.50 (below chance) on full model set
- BBQ directional test ≤3/6 pairs DPO>SFT
- WinoGender shows no consistent direction
- Fisher's criterion near-equal across all 4 benchmarks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:
  The hypothesis H-AlignFingerprint-v1 presents a testable,
  falsifiable claim about a detectable alignment fingerprint
  in standard benchmark space. The key insight — reframing as
  a detection problem rather than a mechanistic explanation —
  sidesteps the unverifiable causal chain while retaining
  empirical testability. However, the null hypothesis raises
  valid concerns about small sample size, preference data
  heterogeneity, and benchmark sensitivity.

Resolution Path:
  The verification plan addresses this dialectic through:
  1. Foundation verification (H-E1): Establishes whether the
     fingerprint exists at all before committing to mechanism
  2. Sequential mechanism testing (H-M1→H-M3): Tests each
     step of the proposed causal chain independently
  3. Gate conditions: H-E1 (MUST_WORK) allows early detection
     of H0 support — if H-E1 fails, the plan terminates
     cleanly with an informative null result
  4. Pre-registered null criterion (accuracy <0.50) prevents
     post-hoc rationalization of inconclusive results

Conditions for Thesis Support:
- H-E1: LOO accuracy ≥0.67 AND permutation p≤0.05
- H-M1: ≥4/6 pairs BBQ DPO>SFT
- (H-M2/H-M3 provide mechanism support but not required for
  fingerprint claim)

Conditions for Antithesis Support:
- H-E1 LOO accuracy < 0.50 (fingerprint absent)
- H-E1 permutation p > 0.05 (not statistically significant)
- Both are pre-registered null criteria — informative and publishable

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1-3 all pass → alignment fingerprint
   confirmed with mechanism support
2. Partial Support A: H-E1 passes, H-M1 fails → fingerprint exists
   but mechanism is not bias-avoidance; revise mechanism claim
3. Partial Support B: H-E1 passes, H-M2/H-M3 fail → fingerprint
   exists; mechanism is simpler than 3-step chain
4. No Support: H-E1 fails → informative null; publish as evidence
   that standard benchmarks cannot detect alignment strategy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Profile difference detectable by k-NN LOO | Small n → underpowered; community confounds | H-E1 test with permutation p-value; n≥6 minimum |
| Mechanism (Fairness) | DPO encodes bias-avoidance via preference | Preference data heterogeneous; signal weak | H-M1 sign test + BBQ Fisher's criterion |
| Mechanism (Truthfulness) | DPO lacks explicit factual reward | DPO may generalize to truthfulness anyway | H-M2 Fisher's criterion rank |
| Profile Shape | 4D shape adds over 1D | TruthfulQA MC2 alone may explain fingerprint | H-M3 4D vs 1D k-NN comparison |

**Overall Robustness Score:** Medium-High (well-specified tests, small-n acknowledged, null result publishable)
**Confidence in Verification Plan:** 0.72

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** DPO-aligned 7B LMs exhibit a detectable trustworthiness profile fingerprint in 4D standard benchmark space, identifiable by k-NN LOO CV (≥67% accuracy, permutation p≤0.05, n≥6 matched pairs)
- ID: H-AlignFingerprint-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (60% scope reduction from 3 BUILD_ON claims)
- Sub-Hypotheses: 4 total (H-E1 + H-M1 + H-M2 + H-M3; no H-C)
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1 at end of Week 2, Gate 2 at end of Week 5)

**Risk Assessment:** Medium
- Primary concern R1: Model pair scarcity (≥6 clean pairs required; mitigation: alignment-handbook + community)
- Secondary concern R3: Community model confounds (mitigation: stratified analysis by pair quality)

**Immediate Action:** Begin model curation and lm-eval-harness setup; run H-E1 benchmark in Week 1-2

### 7.2 Conclusions

**Key Achievements:**
- 4 sub-hypotheses defined across 2 verification phases
- 60% scope reduction: 3 BUILD_ON claims skipped (RLHF>SFT on TruthfulQA; DPO≈RLHF capability; trustworthiness independence)
- H0 clearly operationalized: accuracy <0.50 = informative null
- Both positive and null results are publishable

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: k-NN LOO CV on 4D benchmark scores from ≥6 matched model pairs
- Gate 1: MUST PASS (accuracy ≥0.67, p≤0.05) — STOP if accuracy <0.50

**Phase 2: Core Mechanisms** (3 weeks)
- H-M1: BBQ/WinoGender sign test — bias-avoidance signal (MUST_WORK)
- H-M2: Fisher's criterion rank — TruthfulQA MC2 most discriminative (SHOULD_WORK)
- H-M3: 4D vs 1D k-NN comparison — profile shape adds value (SHOULD_WORK)
- Gate 2: H-M1 must pass

**Critical Decision Points:**

1. **Gate 1 (Foundation — End Week 2):**
   - accuracy ≥0.67 AND p≤0.05 → PASS → proceed to Phase 2
   - accuracy <0.50 → STOP → publish informative null
   - 0.50≤accuracy<0.67 → EXPLORE → expand pairs or try alternative metrics

2. **Gate 2 (Mechanisms — End Week 5):**
   - H-M1 passes → Core mechanism supported → PASS
   - H-M1 fails → EXPLORE confounds → PIVOT to descriptive framing
   - H-M2/H-M3 fail → Document limitation, mechanism simpler than claimed

**Open Questions (from Phase 2A):**
- Exact model pairs available with confirmed clean DPO/SFT labels on HuggingFace — requires manual curation before Phase 4 execution
- lm-evaluation-harness version compatibility for BBQ task — requires pre-experiment setup check
- Whether WinoGender setup is feasible within lm-eval-harness or requires manual script
- Minimum effect size: what constitutes a practically meaningful trustworthiness profile difference?

**Recommendations:**

1. Immediate Actions:
   - Begin model curation (target 8-10 pairs for buffer); confirm alignment-handbook Zephyr-7B pair as anchor
   - Set up and pin lm-evaluation-harness; test BBQ and WinoGender task availability before full run
   - Pre-register predictions P1-P3 before any benchmark runs

2. Resource Allocation:
   - Allocate 5 weeks critical path; budget for ~32 GPU hours on A100
   - Reserve 1-week buffer for model curation if <6 pairs found initially

3. Failure Management:
   - If H-E1 fails: publish null result as "standard benchmarks insufficient for alignment detection" — positive contribution either way
   - If H-M1 fails: retain fingerprint framing (H-E1), revise mechanism claim
   - Document all intermediate results for transparency

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-AlignFingerprint-v1, generated 2026-08-31)
- Architecture: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- Convergence: 11 exchanges, all 6 criteria satisfied

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls: 2 (simulated in ABLATION MODE — no actual MCP available)
- Tools: scientificmethod ×2 (H-E1 verification, H-M integrated chain)
- Note: In full pipeline, Archon and ClearThought would be called; ablation mode simulates outputs

**Appendix C: Scope Reduction Detail**
- Claims skipped (BUILD_ON): 3 of 5 total claims (60% reduction)
  1. RLHF > SFT on TruthfulQA (InstructGPT, 2022)
  2. DPO ≈ RLHF on capability benchmarks (DPO paper, 2023)
  3. Trustworthiness dimensions partially independent (DecodingTrust, 2023)
- Claims verified (PROVE_NEW): 2 of 5
  1. DPO vs SFT trustworthiness profile difference detectable via benchmark suite → H-E1
  2. Alignment strategy produces classifiable fingerprint in 4D benchmark space → H-M1/H-M2/H-M3
