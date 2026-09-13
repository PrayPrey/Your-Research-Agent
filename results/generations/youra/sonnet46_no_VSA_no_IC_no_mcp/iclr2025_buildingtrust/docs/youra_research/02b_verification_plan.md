---
title: "Verification Plan: H-DeltaECE-v1"
hypothesis_id: "H-DeltaECE-v1"
date: "2026-08-25"
workflow: "phase2b-planning"
research_mode: "incremental"
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

# Verification Plan: H-DeltaECE-v1

**Date:** 2026-08-25
**Hypothesis ID:** H-DeltaECE-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## Section 0: Established Facts & Scope Reduction

**Scope Reduction: 67%** (4 of 6 claims are BUILD_ON — do not re-verify)

| Claim | Status | Evidence |
|-------|--------|----------|
| ECE measures confidence-accuracy gap (Guo 2017) | BUILD_ON | arXiv 1706.04599, ~4000 citations |
| Modern NNs systematically overconfident | BUILD_ON | Guo 2017; Minderer 2021 |
| Distribution shift degrades calibration | BUILD_ON | Minderer 2021 (ImageNet-C, ObjectNet) |
| Adversarial NLP benchmarks cause 15-30% accuracy drops | BUILD_ON | Wang 2021 AdvGLUE; Nie 2020 ANLI |
| ECE on adversarial NLP benchmark splits for open-weight LLMs unmeasured | **PROVE_NEW** | Systematic gap — no published study |
| ΔECE as deployment reliability signal is unvalidated | **PROVE_NEW** | No published AUROC validation |

**Phase 2B-4 Instructions:** BUILD_ON claims cited as prior work. Verification protocols focus on the two PROVE_NEW claims only.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under adversarial text perturbation on existing NLP benchmarks (AdvGLUE, ANLI, BIG-Bench Hard MC), if open-weight LLMs (Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, Mistral-7B-instruct) are evaluated using logit-based 15-bin Expected Calibration Error on multiple-choice task formats, then ΔECE (ECE_adversarial − ECE_clean) will be positive (> 0.05) for ≥60% of model × task combinations, because adversarial perturbation preserves ground-truth labels while changing surface features in ways that trigger high model confidence on incorrect answers — exposing systematic overconfidence invisible in clean-benchmark evaluation.

### 1.2 Alternative Hypothesis (H0)

There is no significant increase in ECE between adversarial and clean benchmark splits (ΔECE ≤ 0 for ≥60% of model × task combinations), indicating LLMs appropriately reduce confidence under adversarial inputs (well-calibrated under distribution shift).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | AdvGLUE + ANLI + BIG-Bench Hard (MC subset) (standard) | AdvGLUE and ANLI are the primary adversarial benchmarks identified in Gap 1; BBH adds commonsense domain coverage. Clean counterparts (GLUE, MultiNLI) provide ECE baseline for ΔECE computation. |
| **Model** | Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, Mistral-7B-instruct | Open-weight models allow logit extraction; base vs. chat variant comparison enables RLHF effect study (P2); Mistral-7B provides cross-architecture data point |

**Dataset Details:**
- Source: HuggingFace datasets hub
- Path: tau/commonsense_qa (clean GLUE); AdvGLUE (adversarial GLUE); facebook/anli; lukaemon/bbh

**Model Details:**
- Type: open-weight decoder-only transformer
- Source: meta-llama/Llama-2-7b-hf, meta-llama/Llama-2-7b-chat-hf, meta-llama/Llama-2-13b-chat-hf, mistralai/Mistral-7B-Instruct-v0.1

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Clean-split ECE (Guo 2017 protocol on LLMs) | ECE ~0.05-0.15 for LLMs on clean benchmarks (Kadavath 2022) | TriviaQA, MMLU, BIG-Bench (clean) |
| Accuracy-based robustness evaluation (AdvGLUE, ANLI) | 15-30% accuracy drop under adversarial perturbation | AdvGLUE, ANLI |
| Verbal uncertainty elicitation (Kadavath 2022, Xiong 2023) | Calibrated verbal probabilities for Claude/GPT-3/GPT-4 | TriviaQA, MMLU |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Logit-based ECE on answer-token distributions for MC tasks is valid calibration measure for LLMs | Standard practice in LLM evaluation (Kadavath 2022; lm-evaluation-harness) | ECE measurements reflect tokenization/prompt artifacts, not calibration |
| A2 | AdvGLUE and ANLI adversarial examples preserve ground-truth labels for majority of instances | AdvGLUE: human-verified; ANLI: model-in-the-loop construction with human validation | ΔECE increase reflects label noise rather than miscalibration — addressed by label-preservation stratification |
| A3 | Clean benchmark counterparts (GLUE, MultiNLI) are appropriate baselines | AdvGLUE derived from GLUE; ANLI designed as adversarial MultiNLI — same task, different perturbation | ΔECE conflates task difficulty with calibration — controlled by restricting to same task categories |
| A4 | Public HuggingFace checkpoints are representative of their model families | Official Meta/Mistral AI releases; widely used as reference points in academic evaluation | Results may not generalize to proprietary/fine-tuned variants — explicitly scoped to open-weight models |
| A5 | 15-bin equal-width ECE with logit-based confidence captures meaningful calibration signal | 15-bin ECE is standard (Guo 2017); sensitivity analysis with bin counts is robustness check | Results depend on binning choice — mitigated by reporting ECE + calibration reliability diagrams |

### 1.6 Research Gap & Novelty

**Gap:** No published study combines ECE measurement with adversarial NLP benchmark splits for open-weight LLMs. Existing work covers calibration on clean benchmarks (Kadavath 2022, Xiong 2023) or accuracy-only adversarial evaluation (Wang 2021, Nie 2020) — never the intersection.

**Novelty:** First systematic measurement of ΔECE on adversarial NLP splits; first AUROC validation of ΔECE as a deployment reliability signal. Key innovation: combining two mature traditions (calibration measurement + adversarial NLP) that have never been combined — filling a direct measurement gap without requiring new benchmarks, data, or annotation.

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
**H-E1: ECE Measurement Feasibility on Adversarial NLP Splits**

**Statement**: Under standard lm-evaluation-harness with logit extraction, if open-weight LLMs (Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, Mistral-7B-instruct) are evaluated on AdvGLUE and ANLI multiple-choice splits, then logit-based 15-bin ECE can be reliably computed for all 4 models × 3 task types = 12 (model, task) cells, with sufficient coverage (≥200 examples per cell), because AdvGLUE and ANLI are available on HuggingFace and lm-evaluation-harness natively extracts answer-token logits for MC tasks.

**Rationale**: This existence hypothesis establishes the measurement infrastructure before testing the main effect. ECE computation requires answer-token probability distributions; confirming this is extractable and meaningful for all model-task cells is the foundation for ΔECE calculation. Without this, no downstream hypothesis is testable.

**Variables:**
- Independent: Model identity (4 variants), benchmark split (clean vs. adversarial)
- Dependent: ECE value computed per (model, task, split) cell; cell coverage count
- Controlled: 15-bin equal-width ECE implementation, lm-evaluation-harness version, prompt template

**Verification Protocol:**
1. Run lm-evaluation-harness on all 4 models × 3 tasks × 2 splits (clean + adversarial) = 24 evaluation runs; extract logits for answer tokens.
2. Confirm ≥200 valid examples per (model, task, split) cell with non-degenerate logit distributions (not collapsed to argmax).
3. Compute 15-bin ECE for each cell; verify ECE values fall in plausible range [0.0, 0.5] and calibration reliability diagrams show non-flat signal.
4. Cross-check against known clean-split ECE baselines (Kadavath 2022: ECE ~0.05-0.15) for sanity.
5. Report: coverage table, ECE distributions, reliability diagrams for all 12 (model, task) pairs.

**Success Criteria (PoC: Direction-based):**
- Primary: ≥200 examples per cell, ECE computable for all 24 cells with valid distributions
- Secondary: Clean-split ECE values consistent with published LLM calibration range (0.05-0.15)

**Failure Response:**
- IF fails (sparse coverage or degenerate logits): PIVOT — switch to BBH-MC subset only, reduce to 2 models, or use probability calibration via verbal elicitation as fallback

**Dependencies:** None (foundation — independent of all other hypotheses)

**Source:** Phase 2A Section 5 (sh1_existence), Section 2 (experimental_setup), Prediction P1

---

---
**H-M1: Label Preservation Enables Valid ΔECE Computation**

**Statement**: Under adversarial text perturbation on AdvGLUE and ANLI benchmark splits, if ground-truth labels are stratified by label-preservation confidence, then ≥80% of adversarial examples maintain correct ground-truth labels and produce valid ΔECE signal, because AdvGLUE uses human-verified label preservation and ANLI uses model-in-the-loop adversarial construction with human validation — ensuring the perturbation changes surface features rather than semantic content.

**Rationale**: This mechanism hypothesis tests Step 1 of the causal chain: that adversarial perturbation preserves labels. This is the critical prerequisite for ΔECE to measure miscalibration rather than label noise. Without label preservation, ΔECE could reflect annotation artifacts rather than the calibration failure of interest.

**Variables:**
- Independent: Adversarial perturbation type (lexical substitution, paraphrase, syntactic — AdvGLUE; model-in-the-loop — ANLI)
- Dependent: Label preservation rate per adversarial example set; ΔECE contribution from label-preserved vs. label-uncertain examples
- Controlled: Label-preservation stratification method (human-annotation confidence scores from AdvGLUE metadata)

**Verification Protocol:**
1. Load AdvGLUE and ANLI adversarial splits; extract label-preservation confidence scores from dataset metadata where available.
2. Stratify adversarial examples into high-confidence-preserved (≥0.9) and uncertain groups; compute ECE separately for each stratum.
3. Verify that label-preserved examples show ΔECE signal while uncertain examples show higher variance — confirming label noise is not confounding the primary measure.
4. Compute overall label preservation rate across all adversarial examples; verify ≥80% meet high-preservation threshold.
5. Report: preservation rates per benchmark, stratum-level ECE comparison, flagged uncertain examples.

**Success Criteria (PoC: Direction-based):**
- Primary: ≥80% adversarial examples retain correct ground-truth labels
- Secondary: ΔECE signal is larger and more consistent in high-preservation stratum than uncertain stratum

**Failure Response:**
- IF fails (label preservation < 70%): PIVOT — restrict analysis to AdvGLUE human-verified subset only; document ANLI limitation; narrow ΔECE claim to AdvGLUE only

**Dependencies:** H-E1 (ECE computation infrastructure must be established)

**Source:** Phase 2A Section 1.3 Causal Step 1, Section 1.4 Assumption A2

---

---
**H-M2: Adversarial Perturbation Causes Accuracy Drop Without Proportional Confidence Reduction**

**Statement**: Under adversarial perturbation on AdvGLUE and ANLI splits, if open-weight LLMs are evaluated on label-preserved adversarial examples (H-M1 confirmed), then mean accuracy drops by ≥10 percentage points while mean maximum softmax confidence remains ≥0.70 across ≥60% of (model, task) cells, because adversarial perturbations alter surface features that disrupt model predictions without triggering the model's uncertainty-reduction mechanisms — leaving confidence high while accuracy falls.

**Rationale**: This mechanism hypothesis tests Step 2 of the causal chain: that the accuracy-confidence gap opens under adversarial stress. This is the direct precondition for elevated ECE — ECE increases mathematically when confidence stays high while accuracy drops. Confirming this gap exists in the specific model-task combinations studied validates the mechanism before measuring its ECE consequence.

**Variables:**
- Independent: Input perturbation condition (clean vs. adversarial split per H-M1-verified pairs)
- Dependent: ΔAcc = Accuracy(adversarial) − Accuracy(clean); mean max softmax confidence on adversarial examples
- Controlled: Same lm-evaluation-harness protocol and prompt templates as H-E1; label-preserved examples only (H-M1 filter)

**Verification Protocol:**
1. For each (model, task) pair, compute accuracy on clean and adversarial splits; calculate ΔAcc per pair.
2. For adversarial split examples with wrong predictions, extract max softmax confidence values; compute mean confidence.
3. Verify: ΔAcc ≤ −0.10 (10pp drop) for ≥60% of (model, task) cells; mean confidence on wrong adversarial predictions ≥ 0.70.
4. Plot accuracy vs. confidence scatter per (model, task) to visualize the gap opening.
5. Report: ΔAcc per cell, confidence distributions on adversarial misclassifications, cross-model comparison.

**Success Criteria (PoC: Direction-based):**
- Primary: ≥60% of (model, task) cells show ΔAcc ≤ −0.10 with mean adversarial confidence ≥ 0.70 on wrong predictions
- Secondary: Base models (Llama-2-7B-base) show larger confidence-accuracy gap than chat variants

**Failure Response:**
- IF fails (models lower confidence proportionally): Document as EXPLORE — models may be adaptively uncertain; refine hypothesis to focus only on task types/models where gap exists

**Dependencies:** H-E1, H-M1

**Source:** Phase 2A Section 1.3 Causal Step 2, Key Tension (alignment effect), Prediction P2

---

---
**H-M3: Confidence-Accuracy Gap Manifests as Elevated ΔECE**

**Statement**: Under the conditions confirmed in H-M1 and H-M2, if ΔECE = ECE(adversarial) − ECE(clean) is computed for all label-preserved (model, task) cells, then ΔECE > 0.05 for ≥60% of model × task combinations and mean ΔECE > 0 across all combinations, because ECE mathematically captures the confidence-accuracy gap (ECE = Σ|acc(b) − conf(b)| × |b|/n), and the gap confirmed in H-M2 (high confidence, low accuracy) directly increases ECE on adversarial splits.

**Rationale**: This mechanism hypothesis tests Step 3 of the causal chain and directly addresses the primary prediction (P1). Given the gap confirmed in H-M2, this tests whether ECE captures it reliably as a measurable, reproducible signal. This is the core empirical claim of H-DeltaECE-v1 and the primary contribution of the study.

**Variables:**
- Independent: Input perturbation condition (clean vs. adversarial split, filtered by H-M1); model family
- Dependent: ΔECE = ECE(adversarial) − ECE(clean) per (model, task) cell; proportion of cells exceeding ΔECE > 0.05 threshold
- Controlled: 15-bin equal-width ECE; same examples used in H-M2 accuracy analysis; label-preserved subset only

**Verification Protocol:**
1. Compute 15-bin logit-based ECE for each (model, task) on both clean and adversarial splits using H-E1 infrastructure.
2. Calculate ΔECE = ECE(adversarial) − ECE(clean) for all 12 (model, task) cells; count proportion with ΔECE > 0.05.
3. Test: proportion ≥ 60% of cells with ΔECE > 0.05; mean ΔECE > 0 across all cells (one-sample t-test, H0: mean ≤ 0).
4. Generate calibration reliability diagrams for representative (model, task) pairs showing clean vs. adversarial calibration curves.
5. Report: full ΔECE table, proportion test result, statistical significance, calibration reliability diagram comparison.

**Success Criteria (PoC: Direction-based):**
- Primary: ≥60% of model × task combinations show ΔECE > 0.05; mean ΔECE > 0 (p < 0.05, one-sample t-test)
- Secondary: Calibration reliability diagrams show visible miscalibration shift on adversarial splits

**Failure Response:**
- IF fails (ΔECE ≤ 0 for majority): Antithesis supported — document as EXPLORE; investigate whether models' uncertainty mechanism is adaptive; report as negative result on LLM calibration robustness

**Dependencies:** H-E1, H-M1, H-M2

**Source:** Phase 2A Section 1.3 Causal Step 3, Prediction P1, ECE definition (Guo 2017)

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ECE computable for all 24 cells, ≥200 examples/cell | STOP — reassess measurement approach; pivot model/task scope |
| H-M1 | MUST_WORK | ≥80% adversarial examples preserve ground-truth labels | PIVOT — restrict to AdvGLUE human-verified subset only |
| H-M2 | SHOULD_WORK | ≥60% cells show ΔAcc ≤ −0.10 with high confidence on errors | EXPLORE — document as finding; investigate adaptive uncertainty |
| H-M3 | SHOULD_WORK | ≥60% cells ΔECE > 0.05; mean ΔECE > 0, p < 0.05 | EXPLORE — report as negative result; check calibration reliability diagrams |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 4 weeks (1+1+1 after first) |

**Total Duration:** 5 weeks

---

## 4. Risk Analysis

### 4.1 Risk Identification

**Risk R1: ECE Measurement Validity (from A1)**

**Source Assumption:** A1 — Logit-based ECE on answer-token distributions for MC tasks is a valid calibration measure for LLMs.

**Description:** lm-evaluation-harness may extract logits that do not correspond to semantically meaningful answer-token probabilities due to tokenization edge cases, prompt format sensitivity, or model-specific logit behavior.

**Affected Hypotheses:** H-E1, H-M3

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Pre-validate logit extraction on 10 known examples per model × task; verify softmax distributions sum to ~1 and answer tokens are correctly identified.
2. **Detection:** Flag cells where max softmax confidence is pathological (>0.999 for all examples or <0.5 mean max confidence); examine calibration reliability diagrams for degenerate patterns.
3. **Response:**
   - PIVOT: If logit extraction fails for specific tasks, switch to verbal confidence elicitation for those tasks.
   - SCOPE: Restrict to tasks where logit extraction is validated (AdvGLUE binary classification is most reliable).
   - ABORT: If logit extraction is invalid for ≥50% of cells, fundamental measurement problem — halt H-E1, redesign protocol.

**Early Warning Indicators:**
- Clean-split ECE values outside published range (0.05-0.15) for all models
- Logit distributions showing near-uniform probability mass across all answer tokens

---

**Risk R2: Label Noise Confound (from A2)**

**Source Assumption:** A2 — AdvGLUE and ANLI adversarial examples preserve ground-truth labels for majority of instances.

**Description:** If adversarial perturbations alter the semantic content such that ground-truth labels no longer apply, ΔECE would reflect annotation noise rather than calibration failure under legitimate perturbation.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Apply label-preservation stratification from H-M1 before computing ΔECE for H-M3; use only high-preservation examples (≥0.9 confidence) for primary analysis.
2. **Detection:** Compare ΔECE between high-preservation and uncertain example strata; if ΔECE is similar in both strata, label noise is not confounding.
3. **Response:**
   - PIVOT: Report ΔECE separately for high-preservation and full adversarial sets; primary claim scoped to high-preservation subset.
   - SCOPE: Restrict ANLI analysis to R1 and R2 rounds where adversarial construction is most controlled.
   - ABORT: If label preservation < 50% globally, ANLI is not usable for this study; restrict to AdvGLUE only.

**Early Warning Indicators:**
- Label preservation rate < 70% in H-M1 verification
- ΔECE values are inconsistent across repeated sampling of adversarial examples (indicating high variance from noise)

---

**Risk R3: Task Difficulty Confound (from A3)**

**Source Assumption:** A3 — Clean benchmark counterparts (GLUE, MultiNLI) are appropriate baselines for adversarial calibration comparison.

**Description:** AdvGLUE and ANLI adversarial splits may be intrinsically harder tasks independent of adversarial perturbation, causing ΔECE to reflect task difficulty rather than perturbation-induced miscalibration.

**Affected Hypotheses:** H-M2, H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Restrict ΔECE computation to same task categories across clean and adversarial splits (NLI vs NLI, classification vs classification); do not compare across task types.
2. **Detection:** Run ablation with matched-difficulty clean examples (random hard subset of GLUE with similar accuracy level as adversarial); if ΔECE is similar, task difficulty is confounding.
3. **Response:**
   - PIVOT: Report ΔECE controlling for ΔAcc (partial correlation); claim narrows to "adversarial perturbation causes additional miscalibration beyond difficulty increase."
   - SCOPE: Report ΔAcc as a covariate; use multiple regression ΔECE ~ ΔAcc + perturbation_type.

**Early Warning Indicators:**
- ΔAcc strongly correlated with ΔECE (r > 0.9), suggesting all ECE increase is explained by accuracy drop
- Clean-split accuracy on hard subsets matches adversarial accuracy, yet ΔECE is near zero

---

**Risk R4: Open-Weight Model Representativeness (from A4)**

**Source Assumption:** A4 — Public HuggingFace checkpoints are representative of their model families.

**Description:** Specific checkpoint versions (e.g., Llama-2-7b-hf) may have been updated or may not represent typical deployment configurations (4-bit quantization, different prompt formats).

**Affected Hypotheses:** H-E1, H-M2, H-M3

**Severity:** Low

**Mitigation Strategy:**
1. **Prevention:** Pin exact HuggingFace checkpoint hash; record model card versions; run all 4 models with consistent precision (bfloat16 unless VRAM-constrained).
2. **Detection:** If results for Mistral-7B diverge sharply from Llama-2 family, check whether different prompt template is affecting logit extraction.
3. **Response:**
   - SCOPE: Explicitly document checkpoint versions and precision in all reported results; scope generalization to "these specific checkpoints."

**Early Warning Indicators:**
- Mistral-7B shows qualitatively different logit behavior than Llama-2 variants

---

**Risk R5: ECE Bin Count Sensitivity (from A5)**

**Source Assumption:** A5 — 15-bin equal-width ECE captures meaningful calibration signal across different task types.

**Description:** For tasks with small adversarial sample sizes (some AdvGLUE subtasks have ~1000 examples), 15 equal-width bins may produce noisy ECE estimates with high variance.

**Affected Hypotheses:** H-E1, H-M3

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Compute ECE with 10-bin and 15-bin variants for all cells; report both; primary analysis uses 15-bin as pre-registered.
2. **Detection:** Flag cells with <100 examples per bin on average; treat ECE estimates for sparse cells as unreliable.
3. **Response:**
   - PIVOT: Use adaptive binning (equal-count bins) for sparse tasks; report alongside fixed-bin ECE.
   - SCOPE: Report expected calibration error + calibration reliability diagrams for full transparency.

**Early Warning Indicators:**
- High variance in ΔECE across bootstrap resamples (SE > 0.03)
- ECE values inconsistent between 10-bin and 15-bin implementations

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: ECE Measurement Validity | A1 | H-E1, H-M3 | High |
| R2: Label Noise Confound | A2 | H-M1, H-M2, H-M3 | High |
| R3: Task Difficulty Confound | A3 | H-M2, H-M3 | Medium |
| R4: Model Representativeness | A4 | H-E1, H-M2, H-M3 | Low |
| R5: ECE Bin Count Sensitivity | A5 | H-E1, H-M3 | Medium |

Critical Risks: 0 | High Risks: 2 | Medium Risks: 2 | Low Risks: 1

---

## 5. Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1: Existence (ECE Measurement Feasibility)
    Gate Type: MUST_WORK
         │
         ▼ [Gate 1: MUST PASS]
[Level 1 - Mechanism Step 1]
    H-M1: Label Preservation Validates ΔECE Signal
    Gate Type: MUST_WORK
    Prerequisites: H-E1
         │
         ▼ [Gate 2: MUST PASS]
[Level 2 - Mechanism Step 2]
    H-M2: Accuracy Drop Without Confidence Reduction
    Gate Type: SHOULD_WORK
    Prerequisites: H-M1
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3: Confidence-Accuracy Gap → Elevated ΔECE (P1)
    Gate Type: SHOULD_WORK
    Prerequisites: H-M2

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Bottleneck: H-E1 (MUST_WORK, no predecessors)
═══════════════════════════════════════════════════════════
```

### 5.1 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.2 Verification Phases

**Phase 1 - Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | ECE extraction and coverage on 24 cells | MUST PASS |

→ **Gate 1**: H-E1 fails → STOP, reassess measurement protocol before any mechanism testing.

**Phase 2 - Core Mechanisms (3 hypotheses, sequential)**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS |
| H-M2 | H-M1 | SHOULD PASS |
| H-M3 | H-M2 | SHOULD PASS |

→ **Gate 2**: H-M1 must pass (label preservation is prerequisite for valid ΔECE). H-M2/H-M3 failures document limitations but don't invalidate study.

---

## 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2    │ W3-4    │ W5      │ W6      │ W7
────────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 1: Foundation
  H-E1             │ ████████│         │         │         │
  [Gate 1]         │         │ ◆       │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 2: Mechanisms
  H-M1             │         │ ████████│         │         │
  H-M2             │         │         │ ████████│         │
  H-M3             │         │         │         │ ████████│
  [Gate 2]         │         │         │         │         │ ◆
────────────────────┼─────────┼─────────┼─────────┼─────────┼────────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 5 weeks (2 + 1 + 1 + 1)
  - H-E1: 2 weeks (foundation; 24 evaluation runs + validation)
  - H-M1: 1 week (label-preservation stratification analysis)
  - H-M2: 1 week (accuracy-confidence gap analysis)
  - H-M3: 1 week (ΔECE computation + statistical testing)
Slack Available: 0 weeks (fully sequential)
```

### 5.5 Resource Summary

```
Total Hypotheses: 4
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 0 (not applicable)

Verification Phases: 2
1. Foundation (H-E1) — MUST_WORK
2. Mechanisms (H-M1-3) — MUST_WORK → SHOULD_WORK → SHOULD_WORK

Total Duration: 5 weeks
Critical Path Length: 5 weeks
Execution Mode: Sequential chain (no parallelization)
Scope Reduction: 67% (4 of 6 claims are BUILD_ON — not re-verified)
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Under adversarial text perturbation on existing NLP benchmarks, open-weight LLMs evaluated with logit-based 15-bin ECE will show ΔECE > 0.05 for ≥60% of model × task combinations, because adversarial perturbation exposes systematic overconfidence invisible in clean-benchmark evaluation.

**Supporting Evidence:**
1. ECE mathematically captures confidence-accuracy gap (Guo 2017) — adversarial accuracy drops (15-30%, Wang 2021) without corresponding confidence reduction produce measurable ECE increase.
2. Distribution shift degrades calibration in vision models (Minderer 2021) — the analogous mechanism in NLP adversarial settings is untested but theoretically expected.
3. Adversarial examples preserve labels (AdvGLUE human-verified, ANLI model-in-the-loop) — ensuring ΔECE reflects miscalibration, not annotation noise.

**Strengths:**
- Grounded in established theory: ECE formula directly predicts ΔECE > 0 given H-M2's confidence-accuracy gap
- Two existing adversarial benchmarks with label preservation guarantees
- Incremental claim: does not require new benchmarks, data, or methodology

**Expected Outcomes:**
- Primary (P1): ΔECE > 0.05 for ≥60% of model × task combinations
- Secondary (P2): Llama-2-7B-base shows significantly higher ΔECE than Llama-2-7B-chat (RLHF reduces calibration degradation)
- Tertiary (P3): Per-model mean ΔECE correlates positively with AUROC(entropy) as failure predictor (Spearman r > 0.5)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant increase in ECE between adversarial and clean splits (ΔECE ≤ 0 for ≥60% of model × task combinations) — LLMs appropriately reduce confidence under adversarial inputs.

**Counter-Arguments:**
1. LLMs may be intrinsically uncertainty-aware: RLHF-aligned models (Llama-2-chat, Mistral-instruct) could be calibrated to hedge under out-of-distribution inputs, producing ΔECE ≤ 0.
2. Label noise confound: AdvGLUE and ANLI perturbations may introduce sufficient label noise to make ΔECE a noise signal rather than a calibration signal (Risk R2).
3. Multiple-choice ECE ≠ deployment calibration: The logit-based ECE on constrained MC tasks may not reflect calibration in real deployment scenarios (open-ended generation, free-form QA).

**Potential Failure Points:**
- H-E1 fails: ECE computation is not feasible for open-weight LLMs on adversarial benchmarks at required coverage
- H-M1 fails: Label noise in adversarial examples is too high to construct valid ΔECE signal
- H-M2 fails: Models reduce confidence proportionally to accuracy (well-calibrated under adversarial stress)

**Conditions Under Which H0 Would Be Supported:**
- ΔECE ≤ 0 for majority of (model, task) cells — models are adaptively uncertain
- Label preservation < 70% in AdvGLUE/ANLI — ΔECE reflects annotation noise
- RLHF alignment fully accounts for calibration robustness — base vs. chat difference explains all ΔECE > 0 cases

### 6.3 Synthesis

**Balanced Assessment:**

H-DeltaECE-v1 presents a well-grounded testable claim derived from established theory (ECE formulation, adversarial NLP accuracy drops). However, the null hypothesis raises valid concerns about RLHF-induced uncertainty calibration and label noise confounds. The key unresolved tension (identified in Phase 2A): whether miscalibration under adversarial inputs is a fundamental property of all LLMs or a property of base models that RLHF alignment mitigates.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation (H-E1):** Confirms measurement feasibility before claiming any effect
2. **Label preservation (H-M1):** Separates miscalibration from label noise confound
3. **Gap confirmation (H-M2):** Tests whether the confidence-accuracy gap actually opens
4. **ECE signal (H-M3):** Confirms the gap manifests as measurable ΔECE

**Conditions for Thesis Support:**
- H-E1 and H-M1 MUST_WORK gates pass
- H-M2 and H-M3 confirm accuracy-confidence gap and ΔECE > 0.05 signal

**Conditions for Antithesis Support:**
- H-M2 fails: models lower confidence proportionally (adaptive calibration)
- H-M3 fails despite H-M2 passing: ECE doesn't capture the gap measured in H-M2

**Nuanced Outcome Possibilities:**
1. **Full Support:** All 4 hypotheses pass → ΔECE is a valid, measurable reliability signal for LLMs under adversarial stress
2. **Partial Support:** H-E1+H-M1 pass, H-M3 passes, H-M2 borderline → ΔECE signal confirmed even without full mechanism characterization; publish as measurement contribution
3. **Alignment Effect Found:** H-M3 confirmed for base models only, not chat → Refine thesis: "base LLMs miscalibrate under adversarial stress; RLHF mitigates this"
4. **No Support:** H-E1 or H-M1 fails → Fundamental measurement or label problem; antithesis supported; negative result published on ECE feasibility for adversarial NLP evaluation

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | ECE measurable via logit extraction | Logit-based ECE may be invalid for LLMs | H-E1 test with calibration diagram validation |
| Label Validity | AdvGLUE/ANLI preserve ground truth | Label noise may confound ΔECE | H-M1 stratification analysis |
| Mechanism | High confidence + low accuracy = high ECE | Models may reduce confidence adaptively | H-M2 direct confidence-accuracy gap test |
| ECE Signal | ΔECE > 0 follows mathematically from H-M2 | Small effect size may not exceed 0.05 threshold | H-M3 with multiple threshold checks |

**Overall Robustness Score:** High (strong theoretical foundation, grounded in established ECE theory and existing adversarial benchmark data)

**Confidence in Verification Plan:** 0.80

---

## 7. Executive Summary & Conclusions

### Executive Summary

**Main Hypothesis:** ΔECE (ECE_adversarial − ECE_clean) > 0.05 for ≥60% of model × task combinations across 4 open-weight LLMs on AdvGLUE, ANLI, and BBH-MC adversarial splits.
- ID: H-DeltaECE-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue available)
- Sub-Hypotheses: 4 total — H-E: 1, H-M: 3
- Phases: 2 phases over 5 weeks
- Critical Gates: 2 decision points (Gate 1: H-E1 MUST_WORK; Gate 2: H-M1 MUST_WORK)

**Scope Reduction:** 67% — 4 of 6 claims are BUILD_ON (prior validated work), not re-verified.

**Risk Assessment:** Medium
- Primary concerns: (1) ECE validity for LLM logit extraction; (2) label noise confound in adversarial examples

**Immediate Action:** Begin Phase 1 with H-E1 — run lm-evaluation-harness on 4 models × 3 tasks × 2 splits.

### Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases (1 existence + 3 mechanism) derived from Phase 2A 3-step causal chain
- H0 explicitly addressed via dialectical analysis; antithesis failure conditions are testable
- Scope reduced 67% by leveraging Phase 2A Established Facts (ECE fundamentals, adversarial benchmark behavior)
- 5-week critical path with clear PIVOT/EXPLORE/STOP responses per gate

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Confirm ECE extractable from 4 LLMs × 3 tasks × 2 splits; ≥200 examples/cell
- Gate 1: MUST PASS — failure means measurement infrastructure infeasible

**Phase 2: Core Mechanisms** (3 weeks sequential)
- H-M1: Label preservation ≥80% in adversarial splits (Week 3)
- H-M2: Accuracy drop ≥10pp with maintained confidence ≥0.70 on errors for ≥60% cells (Week 4)
- H-M3: ΔECE > 0.05 for ≥60% cells, mean ΔECE > 0 (p < 0.05) (Week 5)
- Gate 2: H-M1 must pass; H-M2/H-M3 failures document limitations only

**Critical Decision Points:**

1. **Gate 1 (H-E1):** ECE infrastructure feasible?
   - FAIL → STOP: Redesign measurement protocol before proceeding
   - PASS → Proceed to Phase 2

2. **Gate 2 (H-M1):** Label preservation sufficient?
   - FAIL: PIVOT to AdvGLUE-only; narrow ΔECE claim
   - PASS → Continue mechanism chain

**Open Questions (from Phase 2A):**
- What is the appropriate bin count for ECE on small adversarial subtask samples (~1000 examples)?
- Does 4-bit quantization (BitsAndBytes) affect ECE measurement vs. full-precision inference?
- How should confidence be defined for tasks with >3 answer choices (BBH-MC subtasks with 4-5 options)?

**Recommendations:**

1. **Immediate Actions:**
   - Pin HuggingFace checkpoint hashes before evaluation; run pre-validation on 10 examples per cell
   - Set up lm-evaluation-harness environment with logit extraction enabled; confirm bfloat16 precision

2. **Resource Allocation:**
   - Allocate 5 weeks for critical path; reserve 1 week buffer for hardware/environment issues
   - GPU compute: ~24 evaluation runs × 4 models (A100 or equivalent recommended for 13B model)

3. **Failure Management:**
   - Document all gate outcomes; execute PIVOT strategies immediately on gate failure
   - Negative results (H0 supported) are publishable as LLM calibration robustness findings

### Appendices

**A. Phase 2A Reference**
- Source: `03_refinement.yaml` (ID: H-DeltaECE-v1, generated: 2026-08-25)
- Phase 2A architecture: Self-Contained Tikitaka Loop (6 personas, 8 exchanges, STRONG convergence)

**B. MCP Tool Usage Summary**
- This run: UNATTENDED mode without MCP access (ablation session)
- Standard run would use: mcp__clearThought__scientificmethod (3× for H-E1, H-M integrated, validation), mcp__clearThought__collaborativereasoning (1× for risk expert panel), mcp__clearThought__structuredargumentation (1× for dialectical analysis)

