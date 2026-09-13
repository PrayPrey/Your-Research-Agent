# Verification Plan: Architecture-Family Robustness Fingerprinting in NLP

**Date:** 2026-07-29
**Hypothesis ID:** H-ArchRobustFingerprint-v1
**Confidence:** 0.75
**Total Hypotheses:** 5
**Mode:** Incremental (Phase 2A UNATTENDED, 37% scope reduction)
**Status:** complete
**stepsCompleted:** ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]

---

## Executive Summary

**Main Hypothesis:** Scale-matched transformer models exhibit architecture-family-specific Δ*-vector profiles across adversarial NLP benchmarks that replicate within families and enable above-chance classification.
- ID: H-ArchRobustFingerprint-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (37% scope reduction — 5 BUILD_ON claims pre-validated)
- Sub-Hypotheses: 5 total (H-E1: 1, H-M: 4, H-C: 0)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 MUST_WORK decision points

**Risk Assessment:** Medium
- Primary concerns: Small decoder-only family (2 models at base scale); AdvGLUE surrogate bias on encoder-generated examples

**Immediate Action:** Begin Phase 1 with H-E1 (Δ*-vector existence + reliability)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under scale-matched conditions (~110-250M parameters) on existing NLP adversarial benchmarks,
if transformer models are grouped by architecture family (encoder-only, decoder-only, encoder-decoder)
and evaluated on the full AdvGLUE/ANLI/CheckList suite using normalized vulnerability (Δ* = (Acc_clean − Acc_adv)/Acc_clean),
then each architecture family will exhibit a characteristic Δ*-vector profile across perturbation attack types
that (a) shows greater within-family similarity than between-family similarity,
(b) replicates across surrogate-diverse benchmark partitions (automatic vs. human-crafted),
and (c) enables above-chance architecture-family classification (≥60% leave-one-model-out, 95% CI > 33%),
because bidirectional attention topology (encoder-only) vs. causal attention (decoder-only) vs.
cross-attention (encoder-decoder) constrains feature geometry differently under distribution shift,
producing systematically different sensitivity to local (lexical/character-level) vs. global
(semantic/syntactic) perturbations.

### 1.2 Alternative Hypothesis (H0)

There is no significant Architecture × AttackType interaction in normalized vulnerability (Δ*)
after conditioning on clean accuracy and pretraining objective (p ≥ 0.05, bootstrap), AND
leave-one-model-out classification accuracy does not exceed chance (33%) for 3 architecture families,
indicating that robustness degradation patterns are model-specific noise rather than architecture-family properties.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | AdvGLUE + ANLI-R3 + CheckList (standard) | Covers surrogate-generated and surrogate-free attack types; enables cross-partition surrogate-bias falsification test; most rigorous adversarial NLP benchmark with semantic validity guarantees |
| **Model** | Scale-matched base-scale transformer models (7-8 models) | Covers all three architecture families at matched scale (~110-250M); includes within-family objective contrast (BERT vs. ELECTRA); tokenizer contrast; all publicly available |

**Dataset Details:**
- Source: adversarialglue.github.io (AdvGLUE); allennlp.org/anli (ANLI); checklist.github.io (CheckList)
- Path: Publicly available downloads; no local path required

**Model Details:**
- Type: Pre-trained language model + GLUE fine-tuning
- Source: HuggingFace Model Hub: bert-base-uncased, roberta-base, google/electra-base-discriminator, albert-base-v2, gpt2, facebook/opt-125m, t5-base, facebook/bart-base

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| EMNLP 2023 BERT/GPT-2/T5 GLUE robustness comparison | Qualitative only; no formal statistics | GLUE (8 tasks, 8 perturbation types) | Only 3 models; no AdvGLUE/ANLI/CheckList; no scale control; no interaction test; no fingerprint classification |
| TrustLLM multi-dimension evaluation [Sun et al., 2024] | 16 LLMs across 6 dimensions | 30+ datasets across 6 trustworthiness dimensions | Does not isolate architecture family as IV; no cross-benchmark Δ-vector characterization; no classification |
| Random Baseline (architecture classification) | 33% accuracy | N/A — 3-class random baseline | Theoretical chance baseline for leave-one-model-out classifier |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Architecture family is dominant driver of Δ*-vector clustering vs. scale/tokenizer/objective | Decoder > encoder robustness trend consistent across retrieval (Li et al.) and explanation (Zhang et al.) domains | Contribution shifts to 'pretraining signal bias'; publishable but requires reframing |
| A2 | AdvGLUE curation (≥4/5 annotator agreement, ~10% retention) provides valid, diverse stimulus set | AdvGLUE is most rigorous adversarial NLP benchmark; Fleiss κ ~0.6 post-curation; human-crafted subset (ANLI, CheckList) provides surrogate-free validation | If fingerprint only appears in auto examples (not human-crafted), effect is surrogate-induced artifact |
| A3 | Δ*-vector reliability (split-half r ≥ 0.7) achievable for ≥50 aggregated examples per attack category | AdvGLUE Table 1 reports 200-500 examples per major category; base-scale × 3 families × 5 tasks meets threshold for major attack types | If fewer than 5 attack categories pass reliability filter, Δ*-vector dimensionality too low for meaningful clustering |
| A4 | Attention concentration ΔC is meaningful proxy for feature geometry change; computable from HuggingFace | HuggingFace supports output_attentions=True for all target models; perturbed positions identifiable from AdvGLUE metadata | If ΔC does not differ across families or fails to mediate Δ*, mechanistic claim unsupported; descriptive+predictive claims still stand |
| A5 | Seven base-scale models provide sufficient within-family variation for LOMO classification | Encoder-only: 4 models; decoder-only: 2 models (borderline); encoder-decoder: 2 models; LOMO feasibility marginal for decoder family | If within-family variance too high (2 decoder models not reliably similar), fingerprint requires larger model set |

### 1.6 Research Gap & Novelty

**Gap:** No existing paper treats architecture family as primary IV while controlling for scale across the full AdvGLUE/ANLI/CheckList suite. EMNLP 2023 used only 3 models on GLUE without AdvGLUE/ANLI; TrustLLM did not isolate architecture family.

**Novelty:** Architecture-family robustness fingerprinting — treating normalized vulnerability Δ*-vectors as a characteristic profile of each architecture family, testable across surrogate-diverse benchmarks, and usable for architecture identification from robustness behavior alone. Combines: (a) multi-dimensional Δ*-vector characterization, (b) cross-benchmark surrogate-diversity validation, (c) formal architecture-family classification, and (d) mechanistic mediation via attention topology.

**Key Innovation:** Reframing robustness from 'which model is more robust' to 'what is the architecture-family perturbation vulnerability signature.'

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | Architecture-family-specific Δ*-vector profiles exist and are reliable | MUST_WORK | None | READY |
| H-M1 | MECHANISM | Attention topology shapes token representation aggregation during inference | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Local perturbations trigger differential attention redistribution by topology | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | Attention redistribution pattern determines feature geometry at classification head | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | Systematic geometry difference produces characteristic Δ*-vectors enabling LOMO classification | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Architecture-Family Δ*-Vector Profiles Exist and Are Reliable**

**Type:** EXISTENCE
**Statement:** Under scale-matched conditions (~110-250M parameters), if transformer models are grouped by architecture family (encoder-only, decoder-only, encoder-decoder) and evaluated on AdvGLUE/ANLI/CheckList using Δ* = (Acc_clean − Acc_adv)/Acc_clean, then each family will exhibit a characteristic Δ*-vector profile showing greater within-family similarity than between-family similarity (permutation MANOVA η² > 0.15 in ≥50% of reliable attack categories), replicating across surrogate-diverse partitions.

**Rationale:**
Architecture topology (bidirectional vs. causal vs. cross-attention) structurally constrains how token representations are aggregated under perturbation. If this structural difference produces systematically different sensitivity profiles, it should be detectable as a reliable Δ*-vector signature before testing the causal mechanism. This hypothesis establishes the empirical foundation that must hold for all subsequent mechanism tests to be meaningful.

**Variables (from Phase 2A):**
- Independent: Architecture Family (encoder-only, decoder-only, encoder-decoder) × Attack Type (C1-C11 grouped)
- Dependent: Normalized Vulnerability Δ* = (Acc_clean − Acc_adv)/Acc_clean
- Controlled: Model scale (~110-250M), clean accuracy (covariate), pretraining objective (covariate), tokenizer (covariate)

**Verification Protocol:**
1. Fine-tune 7-8 base-scale models on GLUE (SST-2, MNLI, QQP, QNLI, RTE) using standardized protocol.
2. Evaluate on AdvGLUE (C1-C11), ANLI-R3, and CheckList; compute Δ* per model × attack-type × task.
3. Apply split-half reliability filter: retain attack categories with r ≥ 0.7 and ≥50 aggregated examples.
4. Partition AdvGLUE into 3 groups: A (C1-C5 word-level auto), B (C6-C7 sentence-level auto), C (C8-C11 human-crafted).
5. Fit mixed-effects model: Δ* ~ ArchFamily × AttackType + Objective + Tokenizer + CleanAccuracy + (1|Model); bootstrap 1,000 iterations.
6. Run permutation MANOVA: compute η² (between-family/total) per reliable attack category.
7. Train Δ*-vector nearest-neighbor classifier; run leave-one-model-out cross-validation cross-partition (train A+B, test C).

**Success Criteria (PoC: Direction-based):**
- Primary: Architecture × AttackType interaction p < 0.05 (bootstrap CI excludes zero)
- Secondary: Permutation MANOVA η² > 0.15 in ≥50% of reliable attack categories

**Failure Response:**
- IF fails: STOP — fundamental existence claim unconfirmed; reassess hypothesis (route to Phase 2A-Dialogue for reformulation)

**Dependencies:** None (foundation)

**Source:** Phase 2A SH1 (phase2b_readiness.sh1_existence) + P1 primary prediction

---
**H-M1: Attention Topology Shapes Token Representation Aggregation**

**Type:** MECHANISM (Step 1 of causal chain)
**Statement:** Under scale-matched conditions, if transformer models differ in attention topology (bidirectional vs. causal vs. cross-attention), then this structural property shapes how the model aggregates token representations during inference, producing systematically different representational geometries — measurable as differential ΔC patterns (attention concentration change on perturbed spans) per topology type.

**Rationale:**
This is the foundational causal claim: attention topology (not scale or objective) is the primary architectural determinant of how perturbations propagate through the network. Establishing this step is prerequisite to testing whether topology-driven differences in representation aggregation cause the observed Δ*-vector divergence. The ELECTRA vs. BERT within-encoder contrast provides the critical objective confound control.

**Variables:**
- Independent: Attention Topology (bidirectional/causal/cross-attention) as structural property
- Dependent: Attention Concentration ΔC = C(adv, perturbed span) − C(clean, same span) per layer
- Controlled: Model scale, pretraining objective (ELECTRA vs. BERT contrast isolates topology from objective)

**Verification Protocol:**
1. Extract attention weights via HuggingFace output_attentions=True for clean and perturbed inputs across all 7-8 models.
2. Identify perturbed token positions from AdvGLUE attack metadata (approximate via word-diff if metadata unavailable).
3. Compute ΔC_ℓ = C_ℓ(adv, perturbed span) − C_ℓ(clean, same span) per layer per model.
4. Aggregate mean(ΔC) across layers per model × attack-type.
5. Compare mean(ΔC) across architecture families for word-level attacks (C1-C5).
6. ELECTRA vs. BERT contrast: test if ΔC differs within encoder-only family (objective test) or clusters together (topology dominates).

**Success Criteria:**
- Primary: mean(ΔC) systematically higher in encoder-only models vs. decoder-only for word-level attack types
- Secondary: ELECTRA and BERT cluster together in ΔC space (topology > objective)

**Failure Response:**
- IF fails: PIVOT to narrower claim — topology difference exists in Δ* but ΔC is not the pathway; retain H-E1 and descriptive contribution

**Dependencies:** H-E1 (Δ*-vector profiles must exist before testing mechanism)

**Source:** Phase 2A causal_mechanism step 1 + A4 assumption + P3 prediction

---
**H-M2: Local Perturbations Trigger Differential Attention Redistribution by Topology**

**Type:** MECHANISM (Step 2 of causal chain)
**Statement:** Under word-level local perturbation (AdvGLUE C1-C5: word substitution, character noise), bidirectional attention (encoder-only) globally redistributes attention mass to the perturbed token (amplifying its representational influence), while causal attention (decoder-only) processes the perturbation locally in sequence (bounded redistribution), and cross-attention (encoder-decoder) shows an intermediate pattern — as measured by ΔC per architecture family across word-level attack categories.

**Rationale:**
This step links attention topology (H-M1) to the observable ΔC pattern: the direction and magnitude of redistribution should differ predictably between bidirectional and causal architectures. Decoder models (73% lower explanation flip rates per Zhang et al. 2026) provide indirect support; this test makes the mechanism direct and measurable. Failure of this step would indicate the redistribution difference is not the operative pathway.

**Variables:**
- Independent: Attack Type (word-level C1-C5 vs. sentence-level C6-C7 vs. human-crafted C8-C11)
- Dependent: ΔC direction and magnitude per architecture family per attack type
- Controlled: Clean accuracy, model scale, perturbed token position identification method

**Verification Protocol:**
1. Stratify ΔC by attack partition: word-level (C1-C5), sentence-level (C6-C7), human-crafted (C8-C11).
2. Test directional prediction: encoder-only ΔC > 0 (positive redistribution to perturbed token) for word-level attacks.
3. Test decoder-only bounded redistribution: ΔC near zero or lower magnitude than encoder-only.
4. Compare ΔC patterns across attack partitions to assess topology × attack-type interaction.
5. Statistical test: mixed-effects model ΔC ~ Topology × AttackType + CleanAccuracy + (1|Model).

**Success Criteria:**
- Primary: Encoder-only ΔC significantly higher than decoder-only for word-level attacks (C1-C5)
- Secondary: Topology × AttackType interaction significant in ΔC model

**Failure Response:**
- IF fails: EXPLORE — ΔC may not be the right proxy; consider alternative geometric measures; descriptive Δ* fingerprint remains intact

**Dependencies:** H-M1

**Source:** Phase 2A causal_mechanism step 2

---
**H-M3: Attention Redistribution Determines Feature Geometry at Classification Head**

**Type:** MECHANISM (Step 3 of causal chain)
**Statement:** The attention redistribution pattern (differential ΔC by topology) determines which features the model's classification head receives under perturbed inputs — bidirectional global redistribution creates a distinct clean vs. perturbed feature geometry for encoder-only models, while locally bounded redistribution (decoder-only) preserves feature geometry more robustly under lexical perturbation — producing the topology-specific Δ* profile observed in H-E1.

**Rationale:**
This step connects the ΔC mechanism (H-M2) to the observable Δ* outcome (H-E1). The FLUKE finding (capability ≠ robustness) implies that representational processing under distribution shift differs from capability in clean contexts — consistent with this step. If redistribution drives geometry, the ΔC mediation test should reduce the Architecture × WordLevel coefficient. This is the core mechanistic link in the causal chain.

**Variables:**
- Independent: Attention redistribution pattern (ΔC measured in H-M2)
- Dependent: Architecture × WordLevel interaction coefficient in mixed-effects Δ* model
- Controlled: Clean accuracy, pretraining objective, tokenizer family

**Verification Protocol:**
1. Fit base model: Δ* ~ ArchFamily × AttackType + Objective + Tokenizer + CleanAccuracy + (1|Model).
2. Record Architecture × WordLevel coefficient (β_base).
3. Fit full model: add mean(ΔC) as fixed effect.
4. Record Architecture × WordLevel coefficient in full model (β_full).
5. Compute reduction: (β_base − β_full) / β_base × 100%.
6. Bootstrap 1,000 iterations for CI on reduction percentage.
7. Run Sobel test or bootstrap mediation test.

**Success Criteria:**
- Primary: Architecture × WordLevel coefficient reduction ≥30% when mean(ΔC) added (bootstrap CI excludes zero)
- Secondary: Sobel test mediation p < 0.05

**Failure Response:**
- IF fails: EXPLORE — attention concentration is not the operative pathway; document ΔC as descriptive finding; retain Δ*-vector fingerprint claim as empirical observation without mechanistic explanation

**Dependencies:** H-M2

**Source:** Phase 2A causal_mechanism step 3 + P3 prediction (≥30% coefficient reduction)

---
**H-M4: Systematic Geometry Differences Enable Architecture-Family Classification from Δ*-Vectors**

**Type:** MECHANISM (Step 4 of causal chain — predictive validation)
**Statement:** The systematic difference in feature geometry under perturbation (H-M3) produces a characteristic Δ*-vector for each architecture family that is more similar within-family than between-family, enabling above-chance architecture-family classification: ≥60% leave-one-model-out accuracy (95% bootstrap CI lower bound > 33%) in cross-partition evaluation (train on automatic C1-C7, test on human-crafted C8-C11).

**Rationale:**
This step validates the completeness of the causal chain by testing the downstream predictive consequence: if topology → redistribution → geometry → profile, then Δ*-vectors should carry enough architecture-family signal to enable classification generalizing across surrogate-diverse benchmark partitions. Cross-partition generalization is the key falsification test for surrogate bias. ≥60% with CI > 33% against a 3-class baseline (33% chance) confirms the fingerprint is real and not surrogate-induced.

**Variables:**
- Independent: Training partition (automatic C1-C7 vs. human-crafted C8-C11)
- Dependent: Leave-one-model-out classification accuracy; 95% bootstrap CI
- Controlled: Architecture family size, Δ*-vector dimensionality (reliable categories only)

**Verification Protocol:**
1. Compute Δ*-vector per model (reliable attack categories only, r ≥ 0.7).
2. Train nearest-neighbor or logistic classifier on one partition.
3. Evaluate leave-one-model-out cross-validation on the other partition.
4. Compute cross-partition accuracy: train A+B (C1-C7), test C (C8-C11); and vice versa.
5. Bootstrap 1,000 iterations; compute 95% CI for classification accuracy.
6. Compare against 33% chance baseline (3-class: encoder/decoder/encoder-decoder).

**Success Criteria:**
- Primary: ≥60% LOMO accuracy with 95% CI lower bound > 33% in cross-partition evaluation
- Secondary: If decoder-only family borderline (2 models), report encoder vs. decoder binary accuracy ≥75%

**Failure Response:**
- IF fails: EXPLORE — fingerprint may be valid within-partition but not cross-partition; narrow claim to surrogate-specific fingerprint; reduce publication target from NeurIPS/ICML to EMNLP

**Dependencies:** H-M3

**Source:** Phase 2A causal_mechanism step 4 + P2 prediction (≥60% LOMO, CI > 33%)

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 (MUST_WORK) → H-M1 (MUST_WORK) → H-M2 (SHOULD_WORK) → H-M3 (SHOULD_WORK) → H-M4 (SHOULD_WORK)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Architecture × AttackType p < 0.05 + η² > 0.15 in ≥50% reliable categories | STOP — route to Phase 2A-Dialogue |
| H-M1 | MUST_WORK | mean(ΔC) systematically higher in encoder-only for word-level attacks | PIVOT to descriptive-only contribution |
| H-M2 | SHOULD_WORK | Encoder-only ΔC > decoder-only for C1-C5 (Topology × AttackType interaction significant) | EXPLORE — document ΔC as negative finding |
| H-M3 | SHOULD_WORK | Architecture coefficient reduction ≥30% when mean(ΔC) added (CI excludes zero) | EXPLORE — retain Δ* fingerprint, drop mechanistic claim |
| H-M4 | SHOULD_WORK | ≥60% LOMO accuracy cross-partition with 95% CI > 33% | EXPLORE — narrow to within-partition fingerprint |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks (W1-2) |
| Gate 1 decision | — | W2 end |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks (W3-6) |
| Gate 2 decision | — | W6 end |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): Architecture-Objective Confound**
- Source: A1 — Architecture family assumed to dominate over pretraining objective
- Description: ELECTRA (RTD) may cluster away from BERT (MLM) within encoder-only family, suggesting objective drives Δ*-vector clustering rather than attention topology
- Severity: High
- Likelihood: Medium
- Affected Hypotheses: H-E1, H-M1 (mechanism attribution), H-M3 (mediation claim)
- Mitigation:
  1. Prevention: Include ELECTRA vs. BERT as explicit within-encoder contrast in analysis plan
  2. Detection: Compare ELECTRA position in Δ*-vector space relative to BERT vs. other encoder models
  3. Response: PIVOT — reframe contribution as 'pretraining signal bias' if ELECTRA separates; still publishable but mechanism story changes

**Risk R2 (from A2): Surrogate Bias Invalidates Fingerprint**
- Source: A2 — AdvGLUE curation used encoder-family surrogates; may inflate encoder vulnerability artificially
- Description: The Δ*-vector fingerprint appears in auto-generated (C1-C7) examples but disappears on human-crafted (C8-C11) examples — effect is surrogate-induced
- Severity: High
- Likelihood: Medium
- Affected Hypotheses: H-E1, H-M4
- Mitigation:
  1. Prevention: Three-partition design (A/B/C) with cross-partition classifier generalization as primary falsification test
  2. Detection: Compare η² between automatic and human-crafted partitions; if auto >> human-crafted, surrogate bias likely
  3. Response: SCOPE — narrow claim to 'surrogate-generated vulnerability fingerprint'; document as limitation; target lower-tier venue

**Risk R3 (from A3): Insufficient Δ*-Vector Reliability**
- Source: A3 — Reliability (r ≥ 0.7) requires ≥50 examples per attack category
- Description: Fewer than 5 attack categories pass the split-half reliability filter, making Δ*-vector dimensionality too low for meaningful clustering
- Severity: High
- Likelihood: Low
- Affected Hypotheses: H-E1, H-M4 (classification)
- Mitigation:
  1. Prevention: Aggregate at attack-type level (not attack-method level) to pool examples across tasks within attack category
  2. Detection: Run reliability analysis first; count qualifying categories before committing to full pipeline
  3. Response: SCOPE — aggregate more broadly (e.g., combine word-level attacks into single dimension); report remaining reliability constraints explicitly

**Risk R4 (from A4): ΔC Extraction Failure or Non-Informativeness**
- Source: A4 — Attention concentration ΔC requires perturbed-token position metadata
- Description: AdvGLUE attack metadata (perturbed positions) not available in released files; ΔC computation approximate; ΔC does not systematically differ across families
- Severity: Medium
- Likelihood: Medium
- Affected Hypotheses: H-M1, H-M2, H-M3
- Mitigation:
  1. Prevention: Confirm AdvGLUE metadata availability before committing to ΔC analysis; prepare word-diff fallback
  2. Detection: Pilot extraction on 10 examples per model; verify position identification
  3. Response: EXPLORE — if ΔC uninformative, retain descriptive (H-E1) and predictive (H-M4) claims; drop mechanistic chain; adjust contribution framing

**Risk R5 (from A5): Insufficient Decoder-Only Family Representation**
- Source: A5 — Only 2 base-scale decoder models (GPT-2 + OPT-125M); LOMO classification borderline feasible
- Description: Within-family variance among decoder models is too high to establish reliable Δ*-vector; leave-one-model-out with 2 members is degenerate
- Severity: Medium
- Likelihood: Medium
- Affected Hypotheses: H-E1, H-M4
- Mitigation:
  1. Prevention: Add OPT-350M as third decoder-only model; or use GPT-2-medium (117M → 345M, slightly above range but acceptable)
  2. Detection: Compute within-family variance for decoder-only vs. encoder-only as ratio; if ratio > 1.5, family size is inadequate
  3. Response: SCOPE — report binary classification (encoder-only vs. decoder-only, 4 vs. 2 models) as primary; 3-class as exploratory

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Architecture-Objective Confound | A1 | H-E1, H-M1, H-M3 | High |
| R2: Surrogate Bias Invalidates Fingerprint | A2 | H-E1, H-M4 | High |
| R3: Insufficient Δ*-Vector Reliability | A3 | H-E1, H-M4 | High |
| R4: ΔC Extraction Failure | A4 | H-M1, H-M2, H-M3 | Medium |
| R5: Decoder-Only Family Too Small | A5 | H-E1, H-M4 | Medium |

**Risk Summary:** Critical: 0 | High: 3 | Medium: 2 | Low: 0

### 4.3 Baseline Failure Patterns → Additional Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| EMNLP 2023 only 3 models, no formal test | If only 3 models yield same result, reviewers claim no advancement | Always run 7-8 models; emphasize formal interaction test + reliability filter |
| TrustLLM no architecture stratification | If results correlated with TrustLLM model-level scores, contribution blurred | Explicitly test and report architecture stratification as novel design choice |

---

## 5. Dependency Graph & Timeline Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence — no dependencies)
    [MUST_WORK gate]
         │
         ▼
[Level 1 - Core Mechanism]
    H-M1 ← H-E1 [MUST_WORK gate]
         │
         ▼
[Level 2 - Redistribution Mechanism]
    H-M2 ← H-M1 [SHOULD_WORK gate]
         │
         ▼
[Level 3 - Geometry Mechanism]
    H-M3 ← H-M2 [SHOULD_WORK gate]
         │
         ▼
[Level 4 - Predictive Validation]
    H-M4 ← H-M3 [SHOULD_WORK gate]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks (all sequential)
═══════════════════════════════════════════════════════════
```

### 5.1 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.2 Gantt Timeline (ASCII)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │        ◆│         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │     ████│         │
  H-M4           │         │         │         │ ████████│
  [Gate 2]       │         │         │         │        ◆│
─────────────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3/H-M4 parallel) = 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 0 (H-M4 overlap) ≈ 6 weeks

Slack Available: 0 weeks (fully sequential)

Gate Decisions:
  Gate 1 (W2): H-E1 MUST_WORK → stop or proceed
  Gate 2 (W6): H-M1 MUST_WORK + H-M2/M3/M4 SHOULD_WORK assessment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.4 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0

Verification Phases: 2
1. Foundation (H-E1)
2. Mechanisms (H-M1 through H-M4)

Total Duration: 6 weeks
Critical Path Length: 6 weeks
Execution Mode: Sequential chain

Compute estimate: hours-to-days for base-scale models on GLUE/AdvGLUE
Models: 7-8 publicly available HuggingFace models
Datasets: 3 public adversarial benchmarks (no annotation required)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Execution Order

```
Step 1: Execute H-E1 (Foundation — Δ*-vector existence + reliability) — W1-2
Step 2: Evaluate Gate 1 — If pass, proceed to mechanism chain
Step 3: Execute H-M1 (Attention topology shapes representation aggregation) — W3-4
Step 4: Execute H-M2 (Differential redistribution under perturbation) — W5
Step 5: Execute H-M3 (Redistribution → feature geometry → ΔC mediation) — W5
Step 6: Execute H-M4 (Predictive LOMO classification cross-partition) — W6
Step 7: Evaluate Gate 2 — H-M1 MUST_WORK; H-M2/M3/M4 SHOULD_WORK assessment
Final: Verification complete → Phase 2C experiment design
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Scale-matched transformer models exhibit architecture-family-specific
perturbation vulnerability signatures (Δ*-vectors) driven by attention topology differences.

Supporting Evidence:
1. Decoder > encoder robustness to local perturbations: Li et al. [2026] (retrieval),
   Zhang et al. [2026] (73% lower explanation flip rates for decoder LLMs)
2. Capability ≠ robustness (FLUKE 2025): must measure vulnerability directly;
   architecture differences are structural, not performance-predictable
3. Robust training fails to close gap (+3-4 points only — AdvGLUE 2021):
   suggests robustness is structurally determined, not training-determined

Strengths:
- Convergent indirect evidence across multiple domains for decoder > encoder robustness
- Pre-registered disconfirmation criteria with explicit quantitative thresholds
- Three-partition cross-generalization design directly addresses surrogate bias

Expected Outcomes:
- P1: Architecture × AttackType interaction p < 0.05 (bootstrap) in ≥2/3 partitions
- P2: ≥60% LOMO classification accuracy, 95% CI > 33% (cross-partition)
- P3: ΔC mediation reduces Architecture × WordLevel coefficient ≥30%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant Architecture × AttackType interaction in Δ* after
conditioning on clean accuracy and pretraining objective (p ≥ 0.05, bootstrap). LOMO
classification ≤ 33% chance. Robustness patterns are model-specific noise, not
architecture-family properties.

Counter-Arguments:
1. AdvGLUE surrogate bias: encoder-family models generated ~90% of adversarial examples;
   may artificially inflate encoder vulnerability (circular)
2. Pretraining objective confound: ELECTRA (RTD) differs from BERT (MLM) in more than
   attention topology (generator-discriminator training changes gradient flow)
3. Only 2 decoder-only models at base scale: LOMO classification with 2 members is
   degenerate; within-family variance may exceed between-family variance

Potential Failure Points:
- Failure 1 (R2): Fingerprint disappears in human-crafted partition C8-C11 — surrogate artifact
- Failure 2 (R1): ELECTRA separates from BERT — objective drives clustering, not topology
- Failure 3 (R5): Decoder-only family variance too high to establish reliable fingerprint

Conditions Under Which H0 Would Be Supported:
- Architecture × AttackType interaction p ≥ 0.05 after objective + tokenizer controls
- η² < 0.15 in majority of reliable attack categories
- LOMO classification ≤ 40% or CI overlapping 33% baseline in cross-partition evaluation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:
The hypothesis H-ArchRobustFingerprint-v1 presents a well-grounded claim that attention
topology produces characteristic vulnerability profiles. The antithesis raises valid concerns
about surrogate bias (AdvGLUE encoder-generated examples), pretraining objective confound
(ELECTRA-BERT), and decoder family size (2 models).

Resolution Path:
1. Foundation verification (H-E1): Δ*-vector existence + cross-partition replication
   directly tests surrogate bias concern before committing to mechanism tests
2. Sequential mechanism testing (H-M1→H-M4): ELECTRA/BERT contrast at H-M1 resolves
   objective confound; ΔC mediation at H-M3 makes mechanism direct and measurable
3. Gate conditions: H-E1 MUST_WORK ensures we stop before wasting resources on mechanism
   tests if the fundamental phenomenon doesn't exist

Conditions for Thesis Support:
- H-E1: Architecture × AttackType interaction p < 0.05 + η² > 0.15 in ≥50% reliable categories
- H-M4: ≥60% LOMO accuracy cross-partition with CI > 33%

Conditions for Antithesis Support:
- H-E1 fails (interaction p ≥ 0.05 or η² < 0.15 in majority)
- H-M4 fails (LOMO ≤ 40% or CI overlapping 33% in cross-partition)

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1-4 all pass → NeurIPS/ICML level contribution
2. Partial Support (Descriptive): H-E1 passes + H-M3/M4 fail → EMNLP level contribution
3. Partial Support (Local): H-E1 passes only for word-level attacks → narrow claim,
   EMNLP findings paper
4. No Support: H-E1 fails → Route to Phase 2A-Dialogue for hypothesis redesign
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Δ*-vector profiles exist (topology-driven) | May be surrogate artifact or noise | H-E1 cross-partition test |
| Mechanism | Attention topology → ΔC → feature geometry → Δ* | Objective/tokenizer drives clustering, not topology | H-M1 ELECTRA/BERT contrast + H-M3 ΔC mediation |
| Scope | Applies to all base-scale transformers | Limited to encoder-surrogate attack context | Three-partition replication design |
| Predictive power | Δ*-vector enables architecture classification | Within-partition artifact, not generalizable | H-M4 cross-partition LOMO test |
| Performance comparison | Architecture selection is primary robustness lever | Robust training is sufficient; architecture a secondary factor | Phase 5 (deferred) |

**Overall Robustness Score:** Medium-High (strong cross-partition design; limited decoder family size is binding constraint)
**Confidence in Verification Plan:** 0.75

---

## 7. Conclusions

**Key Achievements:**
- 5 hypotheses across 2 phases with sequential dependency chain
- H0 addressed: no significant Architecture × AttackType interaction (p ≥ 0.05) and LOMO ≤ 33% chance
- Pre-registered disconfirmation criteria for all 5 sub-hypotheses
- Three-partition cross-generalization design embedded in H-E1 + H-M4

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Δ*-vector profiles exist + cross-partition reliability test
- Gate 1: MUST PASS — failure routes to Phase 2A-Dialogue

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Attention topology shapes representation aggregation [MUST_WORK]
- H-M2: Differential redistribution under local perturbation [SHOULD_WORK]
- H-M3: Redistribution determines feature geometry (ΔC mediation) [SHOULD_WORK]
- H-M4: Systematic geometry → Δ*-vector → LOMO classification [SHOULD_WORK]
- Gate 2: H-M1 must pass; H-M2/M3/M4 failures narrow scope but don't invalidate

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 MUST_WORK
   - FAIL → STOP, route to Phase 2A-Dialogue for hypothesis redesign
   - PASS → Proceed to Phase 2 mechanism chain

2. **Gate 2 (Mechanisms):** H-M1 MUST_WORK; H-M2/M3/M4 SHOULD_WORK
   - H-M1 FAIL → PIVOT to descriptive-only contribution (fingerprint without mechanism)
   - H-M2/M3/M4 FAIL (any subset) → EXPLORE + document as scope/limitation

**Open Questions:**
- Will ΔC mediation evidence hold at base scale? Need to confirm HuggingFace attention extraction API behavior for all 7-8 target models.
- Is surrogate fooling count metadata available in the released AdvGLUE dataset files?
- Does ELECTRA cluster with BERT or separate (resolves objective vs. architecture confound)?
- Is the decoder-only family fingerprint stable with only 2 models (GPT-2 + OPT-125M)?

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (split-half reliability analysis first, before full evaluation)
   - Add OPT-350M as third decoder-only model to strengthen classification feasibility
   - Confirm AdvGLUE attack metadata availability before committing to ΔC analysis

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path
   - Reserve OPT-350M compute budget (~125M additional HuggingFace model)
   - Pre-register analysis decisions before data collection

3. **Failure Management:**
   - If H-E1 borderline: aggregate word-level + sentence-level attacks before splitting; run power analysis
   - If ΔC metadata unavailable: use word-diff approximation + document as limitation
   - Document all failures with explicit falsification criteria met

---

## 8. Appendices

### A. Phase 2A Reference
- **Source:** `docs/youra_research/03_refinement.yaml` (ID: H-ArchRobustFingerprint-v1)
- **Generated at:** 2026-07-29T12:30:00Z
- **Discussion exchanges:** 16 (all 6 convergence criteria met)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 4 (ClearThought scientificmethod: 2 hypothesis + 2 experiment stages)
- **Tools:** mcp__clearThought__scientificmethod (Call 1: H-E1 hypothesis+experiment; Call 2: H-M-integrated hypothesis+experiment)
- **Archon:** Pipeline project created + Phase 2B task created/updated

### C. Scope Reduction Summary
- **BUILD_ON claims (5, not re-verified):**
  1. LLMs show dramatic performance drops on adversarially perturbed benchmarks
  2. Robust training yields only +3-4 point improvements on AdvGLUE
  3. Decoder-only models exhibit greater robustness to character/word-level noise than encoder-only
  4. Model capability to use linguistic features does not predict robustness
  5. AdvGLUE curation used BERT/RoBERTa encoder surrogates
- **PROVE_NEW claims (3, basis for H-E1, H-M1-4, H-M4):**
  1. Architecture-stratified, scale-controlled, cross-benchmark Δ*-vector study
  2. Above-chance architecture-family classification from Δ*-vectors
  3. Attention concentration ΔC as mechanistic mediator
