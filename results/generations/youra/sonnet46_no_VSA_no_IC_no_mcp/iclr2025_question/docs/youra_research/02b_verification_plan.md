---
hypothesis_id: H-SE4Way-v1
research_mode: incremental
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
status: in_progress
generated_at: "2026-08-25"
---

# Verification Plan: Four-Way Uncertainty Proxy Comparison at 7B Scale

**Date:** 2026-08-25
**Hypothesis ID:** H-SE4Way-v1
**Confidence:** 0.75
**Total Hypotheses:** 6

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under Llama-2-7B scale on TriviaQA dev (N>=98, extendable to N=500),
if all four major uncertainty proxy methods (single-pass token entropy [TE],
SelfCheckGPT consistency [SCG], semantic entropy [SE], and verbalized confidence [VC])
are applied under identical experimental conditions (same questions, same K=10 samples,
same AUROC metric against binary EM correctness labels),
then SE achieves a practically meaningful AUROC advantage over TE (SE-TE gap >= 0.05),
SelfCheckGPT achieves comparable AUROC to SE (|SCG-SE| <= 0.03),
and verbalized confidence underperforms both (VC < TE),
because semantic-level clustering (SE) and consistency agreement (SelfCheckGPT) both
filter paraphrase noise that degrades the discriminative power of token-level entropy,
while verbalized confidence requires larger model scale (>= 13B) to achieve reliable calibration.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in AUROC among the four uncertainty proxy methods
(TE, SE, SelfCheckGPT, verbalized confidence) on TriviaQA dev at Llama-2-7B scale.
All pairwise AUROC gaps fall within bootstrap 95% CI half-width (< 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA dev (standard) | h-e2-v2 already generated K=10 samples for 98 questions — zero-cost SE/SCG/TE comparison; extendable to N=500 |
| **Model** | Llama-2-7B (base) + Llama-2-7B-Chat (VC only) | Same as h-e2-v2; existing samples reusable. 7B scale tests where SE overhead is hardest to justify. |

**Dataset Details:**
- Source: mandarjoshi/trivia_qa (HuggingFace datasets)
- Path: N=98 from h-e2-v2 pilot (existing samples); extension to N=500 if needed

**Model Details:**
- Type: Autoregressive decoder LLM, 7B parameters
- Source: meta-llama/Llama-2-7b-hf and meta-llama/Llama-2-7b-chat-hf (HuggingFace)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Semantic Entropy (Kuhn et al. 2023) | AUROC > 0.75 at Llama-65B; ~0.54 at Llama-2-7B (h-e2-v2) | TriviaQA dev, NaturalQuestions |
| SelfCheckGPT (Manakul et al. 2023) | AUROC not reported on TriviaQA; WikiBio precision-recall documented | WikiBio |
| Verbalized Confidence (Xiong et al. 2023) | AUROC ~0.50-0.55 for 7B on MMLU/TriviaQA | MMLU, TriviaQA, CoQA |
| Token Entropy (Huang et al. 2023) | AUROC across multiple models; single-pass underperforms sampling | Factual QA (subset) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | h-e2-v2 98-question pilot is representative for detecting AUROC gaps >= 0.05 | Bootstrap CI at N=98 ~±0.05; gaps >= 0.05 detectable at ~80% power | Null result even if true gap exists; extension to N=500 required |
| A2 | Llama-2-7B-Chat is valid proxy for verbalized confidence at 7B scale | Xiong 2023 used instruction-tuned models; Chat variant is standard | VC AUROC measures prompt-following failure, not calibration |
| A3 | BERTScore pairwise similarity is valid consistency proxy for SelfCheckGPT | Manakul 2023 uses BERTScore; works across model sizes | SCG AUROC underestimates actual consistency-based discrimination |
| A4 | EM labels on TriviaQA dev are reliable binary correctness indicators | TriviaQA dev has verified gold answers; EM is standard metric | AUROC computed against noisy labels, degrading all four estimates equally |
| A5 | AUROC rank ordering at N=98/500 generalizes to full TriviaQA dev | h-e2-v2 used random sampling; same procedure maintained | Results pilot-specific; full 11,313-question eval required |

### 1.6 Research Gap & Novelty

**Gap:** No prior work provides a controlled four-way comparison including semantic entropy alongside TE, SelfCheckGPT, and verbalized confidence on TriviaQA at 7B scale.
- Xiong et al. 2023: excludes SE
- Huang et al. 2023: excludes SE and SCG
- Kuhn et al. 2023: only SE vs TE; uses 65B model
- Manakul et al. 2023: SCG on WikiBio only; no SE/TE comparison

**Novelty:** Reframes h-e2-v2's AUROC failure as a scale-calibration finding. Establishes model-scale-calibrated criterion (relative SE-TE gap >= 0.05) over absolute threshold (0.75). Enables practitioners to select the cheapest method meeting their discrimination needs at 7B scale.

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
| H-C1 | CONDITION | SHOULD_WORK | H-M4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Existence of Practically Meaningful SE-TE AUROC Gap at 7B Scale

**Type:** EXISTENCE
**Statement:** Under Llama-2-7B on TriviaQA dev (N>=98), if semantic entropy and token entropy are both computed on the same K=10 samples under identical conditions, then SE achieves AUROC >= TE + 0.05, because semantic-level clustering removes paraphrase noise that degrades token-level entropy's discriminative power.

**Rationale:** This is the foundational test. The h-e2-v2 pilot showed a directional SE > TE gap (+0.029) but used only 98 questions. Before testing the mechanism (H-M1–4) or cross-benchmark conditions (H-C1), we must confirm the SE-TE gap meets the practical significance threshold (0.05) on the same dataset.

**Variables (from Phase 2A):**
- Independent: Uncertainty proxy method (TE vs SE)
- Dependent: AUROC (hallucination detection) — primary
- Controlled: Llama-2-7B, TriviaQA dev N=98, K=10 samples, binary EM labels

**Verification Protocol:**
1. Load existing h-e2-v2 K=10 samples for 98 TriviaQA questions.
2. Compute TE: mean per-token Shannon entropy from greedy-decode logits (or saved logit outputs).
3. Compute SE: reuse h-e2-v2 NLI clustering code on same 98 questions.
4. Compute bootstrap AUROC (1000 iterations) for both methods against binary EM labels.
5. Evaluate: SE AUROC - TE AUROC >= 0.05 AND non-overlapping 95% CIs.

**Success Criteria (PoC: Direction-based):**
- Primary: SE AUROC - TE AUROC >= 0.05
- Secondary: Lower bound of SE bootstrap 95% CI > upper bound of TE bootstrap 95% CI

**Failure Response:**
- IF gap >= 0.03 but < 0.05: EXTEND to N=500 before declaring failure
- IF gap < 0.03 after N=500: ABANDON — SE overhead not justified at 7B; pivot to SCG-only evaluation
- IF gap >= 0.05: PASS — proceed to H-M1

**Dependencies:** None (foundation)
**Source:** Phase 2A SH1, Prediction P1, phase2b_4_instructions

---

#### H-M1: Token-Level Entropy is Degraded by Paraphrase Noise

**Type:** MECHANISM
**Statement:** Under Llama-2-7B on TriviaQA dev, if K=10 stochastic samples are generated for high- vs. low-uncertainty questions, then token entropy varies across semantically equivalent paraphrases (same meaning, different surface form), because TE aggregates over vocabulary distributions that encode surface variation, not semantic content.

**Rationale:** This is the first mechanistic step in the causal chain. Before testing whether SE/SCG filter this noise (H-M2/3), we must confirm that TE is actually sensitive to paraphrase variation — i.e., that the problem exists. If TE is robust to paraphrase, the noise-filtering mechanism is irrelevant.

**Variables:**
- Independent: Question difficulty (high vs low uncertainty) × paraphrase presence
- Dependent: Token entropy variance across semantically equivalent outputs
- Controlled: Llama-2-7B, TriviaQA dev, K=10 samples, temperature=0.7

**Verification Protocol:**
1. Identify 20 questions where h-e2-v2 K=10 samples contain paraphrase pairs (NLI: entailment, different surface form).
2. Compute per-token entropy for each sample in paraphrase pairs.
3. Measure entropy variance within paraphrase pairs vs. across semantically distinct clusters.
4. Test: entropy within paraphrase pairs shows non-trivial variance (> 0.1 nats).
5. Compare with SE clustering: paraphrase pairs should land in same cluster (NLI entailment).

**Success Criteria (PoC):**
- Primary: TE variance within paraphrase pairs > 0.1 nats on >= 15/20 selected questions
- Secondary: SE correctly clusters same paraphrase pairs into single cluster in >= 90% of cases

**Failure Response:**
- IF TE is robust to paraphrase: EXPLORE — noise-filtering mechanism incorrect; pivot to alternative mechanism (cluster-count entropy vs sequence-level aggregation)

**Dependencies:** H-E1 (must confirm gap exists before testing mechanism)
**Source:** Phase 2A Causal Step 2

---

#### H-M2: Semantic-Level Filtering (SE) Removes Paraphrase Noise

**Type:** MECHANISM
**Statement:** Under Llama-2-7B on TriviaQA dev, if SE applies NLI clustering before computing entropy, then SE entropy is invariant to within-cluster paraphrase variation, because NLI entailment groups surface variants into single cluster nodes, removing their contribution to entropy.

**Rationale:** This is the core mechanistic test for SE. Given H-M1 confirms paraphrase noise in TE, this step tests whether SE's NLI clustering actually eliminates that noise. The h-e2-v2 confirmed avg 3.89 clusters/question, suggesting clustering is active — now we test whether it selectively removes paraphrase variation specifically.

**Variables:**
- Independent: Whether samples are within-cluster paraphrases vs. cross-cluster semantic variants
- Dependent: SE entropy contribution per sample group
- Controlled: Llama-2-7B, same 20 questions from H-M1, h-e2-v2 NLI model

**Verification Protocol:**
1. For the same 20 questions from H-M1, extract NLI cluster assignments from h-e2-v2 code.
2. Compute SE entropy with and without merging within-cluster paraphrase groups.
3. Measure: SE entropy change when paraphrase pairs are split into separate pseudo-clusters.
4. Confirm: SE assigns entailment pairs to same cluster in >= 90% of cases (already tested in H-M1).
5. Validate: SE AUROC degrades when clustering is disabled (paraphrase pairs forced to separate clusters).

**Success Criteria (PoC):**
- Primary: SE AUROC drops >= 0.03 when NLI clustering is ablated (paraphrases treated as distinct)
- Secondary: Within-cluster entropy contribution is < 10% of total SE entropy

**Failure Response:**
- IF clustering ablation has no effect: EXPLORE — SE benefit comes from different mechanism (cluster count vs entropy computation)

**Dependencies:** H-M1 (paraphrase noise in TE must be confirmed)
**Source:** Phase 2A Causal Step 3 (SE component)

---

#### H-M3: Cross-Sample Consistency (SCG) Achieves Equivalent Semantic Filtering

**Type:** MECHANISM
**Statement:** Under Llama-2-7B on TriviaQA dev, if SelfCheckGPT BERTScore consistency is computed across K=10 samples, then SCG achieves AUROC within 0.03 of SE (|SCG-SE| <= 0.03), because BERTScore agreement implicitly captures semantic consistency without requiring NLI inference — a different mechanism achieving the same discrimination.

**Rationale:** If SCG achieves equivalent AUROC to SE with less computational overhead (no NLI model needed), practitioners should use SCG. This step validates the practical equivalence claim (P2) and tests whether semantic-level filtering is achievable through consistency agreement rather than explicit NLI clustering.

**Variables:**
- Independent: Uncertainty proxy method (SCG vs SE)
- Dependent: AUROC (hallucination detection)
- Controlled: Same 98 questions, K=10 samples, Llama-2-7B, BERTScore for SCG

**Verification Protocol:**
1. Compute SCG from existing h-e2-v2 K=10 samples using BERTScore pairwise consistency (~7 min CPU).
2. Uncertainty(SCG) = 1 - mean_pairwise_BERTScore across K=10 samples.
3. Compute bootstrap AUROC (1000 iterations) for SCG against binary EM labels.
4. Evaluate: |SCG AUROC - SE AUROC| <= 0.03.
5. Secondary: Compare computational cost (SE: NLI model required; SCG: BERTScore only).

**Success Criteria (PoC):**
- Primary: |SCG AUROC - SE AUROC| <= 0.03 (practical equivalence)
- Secondary: SCG AUROC > TE AUROC (confirming semantic-level advantage)

**Failure Response:**
- IF SCG AUROC > SE AUROC + 0.03: Document — SCG outperforms SE at 7B; revise narrative
- IF SCG AUROC < SE AUROC - 0.05: Document limitation — BERTScore insufficient as consistency proxy at 7B

**Dependencies:** H-M2 (SE mechanism established before comparing SCG)
**Source:** Phase 2A Causal Step 3 (SCG component), Prediction P2

---

#### H-M4: Verbalized Confidence Degrades at 7B Scale

**Type:** MECHANISM
**Statement:** Under Llama-2-7B-Chat on TriviaQA dev, if the model is prompted to self-report confidence (0-100%) after answering, then VC AUROC < TE AUROC AND VC AUROC < SE AUROC, because Llama-2-7B-Chat lacks sufficient meta-cognitive calibration at 7B scale — verbalized confidence does not track actual correctness.

**Rationale:** This tests the fourth causal step: that verbalized confidence is the weakest of the four methods at 7B scale. This distinguishes 7B-specific conclusions from the broader multi-method comparison and validates the scale-dependent calibration hypothesis (Xiong 2023).

**Variables:**
- Independent: Uncertainty proxy method (VC vs TE, SE)
- Dependent: AUROC (hallucination detection)
- Controlled: Llama-2-7B-Chat (for VC), same 98 TriviaQA questions, binary EM labels

**Verification Protocol:**
1. Run Llama-2-7B-Chat on 98 TriviaQA questions with prompt: "Answer the question, then rate your confidence 0-100%."
2. Extract reported confidence scores; normalize to [0,1].
3. Compute bootstrap AUROC (1000 iterations) for VC against binary EM labels.
4. Evaluate: VC AUROC < TE AUROC AND VC AUROC < SE AUROC.
5. Report ECE for VC as secondary metric (calibration quality).

**Success Criteria (PoC):**
- Primary: VC AUROC < TE AUROC (verbalized confidence loses to even the simplest baseline)
- Secondary: VC AUROC < SE AUROC by >= 0.05

**Failure Response:**
- IF VC AUROC >= TE AUROC: Document contradiction — 7B Chat model better calibrated than expected; narrow scope claim to non-Chat 7B models
- IF VC AUROC >= SE AUROC: PIVOT — verbalized confidence competitive at 7B; revise scale boundary

**Dependencies:** H-M3 (full four-method comparison ready)
**Source:** Phase 2A Causal Step 4, Prediction P3

---

#### H-C1: Four-Way AUROC Ranking Holds on TruthfulQA (Cross-Benchmark Condition)

**Type:** CONDITION
**Statement:** Under Llama-2-7B on TruthfulQA (yes/no subset, N>=200), if the same four uncertainty proxy methods are applied under identical conditions, then the AUROC ranking SE >= SCG > TE > VC holds, because the noise-filtering advantage of SE/SCG over TE is domain-general (not TriviaQA-specific), and VC scale-degradation is model-dependent (not benchmark-dependent).

**Rationale:** The primary hypothesis is scoped to TriviaQA. TruthfulQA uses a different question style (true/false, adversarial) and domain (misconceptions vs. trivia). If the ranking holds on TruthfulQA, the SE noise-filtering mechanism generalizes. Failure here narrows the claim to TriviaQA-specific rather than invalidating it.

**Variables:**
- Independent: Benchmark (TriviaQA vs TruthfulQA) × uncertainty method
- Dependent: AUROC, rank ordering of four methods
- Controlled: Llama-2-7B, K=10 samples, binary correctness labels, same AUROC metric

**Verification Protocol:**
1. Sample N=200 questions from TruthfulQA generation format (yes/no subset with binary EM labels).
2. Generate K=10 samples with Llama-2-7B (temperature=0.7) — new generation required.
3. Compute SE, SCG, TE, VC for all 200 questions using same code as H-E1–H-M4.
4. Compute bootstrap AUROC (1000 iterations) for each method.
5. Test: AUROC rank ordering SE >= SCG > TE > VC replicates on TruthfulQA.

**Success Criteria (PoC):**
- Primary: SE AUROC > TE AUROC on TruthfulQA (direction preserved)
- Secondary: VC AUROC < TE AUROC on TruthfulQA (scale-degradation is benchmark-agnostic)

**Failure Response:**
- IF ranking does not hold: Narrow scope claim to TriviaQA-only; document benchmark-specific limitation
- IF SE-TE gap inverts: EXPLORE — TriviaQA-specific finding; mechanism may not generalize

**Dependencies:** H-M4 (all four methods validated on TriviaQA before cross-benchmark test)
**Source:** Phase 2A Section 1.5 scope, phase2b_4_instructions, open_questions

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | SE-TE AUROC gap >= 0.05 | STOP if gap < 0.03 after N=500; extend to N=500 if 0.03 <= gap < 0.05 |
| H-M1 | MUST_WORK | TE paraphrase noise confirmed (variance > 0.1 nats) | EXPLORE alternative mechanism |
| H-M2 | SHOULD_WORK | SE AUROC drops >= 0.03 when clustering ablated | Document, explore alternative SE mechanism |
| H-M3 | SHOULD_WORK | \|SCG-SE\| <= 0.03 | Document deviation; SCG finding still reported |
| H-M4 | SHOULD_WORK | VC AUROC < TE AUROC | Narrow scale-boundary claim |
| H-C1 | SHOULD_WORK | SE > TE ranking holds on TruthfulQA | Narrow to TriviaQA-only scope |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (W3-4: H-M1; W5: H-M2; W6: H-M3; W7: H-M4) |
| Phase 2.5: Conditions | H-C1 | 1 week |

**Total Duration:** 8 weeks

---

## 4. Risk Analysis

### 4.1 Risk Identification (A1–A5 → R1–R5)

**Risk R1: Underpowered Pilot (from A1)**
- **Source Assumption:** A1 — 98 questions may be insufficient for gaps near 0.05
- **Description:** Bootstrap CI at N=98 ~±0.05; a true gap of 0.05 may not achieve statistical significance
- **Affected Hypotheses:** H-E1 (primary), H-M3 (SCG comparison)
- **Severity:** High
- **Mitigation Strategy:**
  1. Prevention: Define pilot gate — if gap < 0.03, extend to N=500 before declaring failure
  2. Detection: Report bootstrap 95% CIs for all AUROC estimates; flag overlapping CIs
  3. Response: EXTEND (N=500) if 0.03 <= gap < 0.05; ABANDON H-E1 if gap < 0.03 after N=500
- **Early Warning:** SE-TE gap in [0.03, 0.05] range with overlapping CIs after N=98

**Risk R2: VC Prompt-Following Failure (from A2)**
- **Source Assumption:** A2 — Llama-2-7B-Chat may not reliably follow confidence elicitation prompt
- **Description:** Chat model may refuse to give numeric confidence or give degenerate outputs (always 50%, always 100%)
- **Affected Hypotheses:** H-M4 (VC mechanism)
- **Severity:** Medium
- **Mitigation Strategy:**
  1. Prevention: Test prompt format on 10 pilot questions; use fallback prompts if needed
  2. Detection: Check distribution of VC outputs — flag if >20% are non-numeric or degenerate
  3. Response: If prompt fails, try alternative elicitation formats; if VC is systematically invalid, report as "VC AUROC unmeasurable" and scope H-M4 to Chat-format validity only
- **Early Warning:** >10% of VC responses non-numeric or constant

**Risk R3: BERTScore Insufficient for SCG (from A3)**
- **Source Assumption:** A3 — BERTScore pairwise similarity may not capture consistency well at 7B/TriviaQA
- **Description:** BERTScore may assign high similarity to semantically different short answers (e.g., "Paris" vs "Lyon" both score high in BERTScore despite being different cities)
- **Affected Hypotheses:** H-M3 (SCG mechanism)
- **Severity:** Medium
- **Mitigation Strategy:**
  1. Prevention: Validate BERTScore on 20 sample question pairs before full run
  2. Detection: Check correlation between BERTScore similarity and NLI entailment on 20 pairs
  3. Response: If BERTScore is poor proxy, switch to NLI-based consistency (SelfCheckGPT-NLI variant)
- **Early Warning:** BERTScore similarity > 0.8 for pairs that NLI labels as contradiction

**Risk R4: EM Label Noise (from A4)**
- **Source Assumption:** A4 — EM labels may be noisy for some TriviaQA answers (alternative phrasings counted wrong)
- **Description:** EM strictly requires exact string match; correct answers with different phrasing are labeled wrong, degrading all AUROC estimates equally
- **Affected Hypotheses:** All hypotheses (systematic bias, not differential)
- **Severity:** Low (affects all methods equally, does not change ranking)
- **Mitigation Strategy:**
  1. Prevention: Use TriviaQA's built-in answer alias list (multiple acceptable answers)
  2. Detection: Manually inspect 10 "EM=0" cases — count false negatives
  3. Response: If >20% false negatives, use normalized EM (lowercase, punctuation removal); report both
- **Early Warning:** >20% of EM=0 cases appear factually correct on manual inspection

**Risk R5: Pilot Not Representative (from A5)**
- **Source Assumption:** A5 — N=98 random sample may accidentally over/under-represent easy/hard questions
- **Description:** If pilot is biased toward easy questions, all methods score similarly (all high AUROC); if biased toward hard, all methods fail
- **Affected Hypotheses:** H-E1, H-C1 (generalization claims)
- **Severity:** Medium
- **Mitigation Strategy:**
  1. Prevention: Verify h-e2-v2 sampling was random (check random seed in generate_shard.py)
  2. Detection: Report question difficulty distribution (avg EM accuracy) for pilot vs. full dev set
  3. Response: If pilot accuracy differs from full dev by >10%, resample or extend to N=500
- **Early Warning:** Pilot avg EM accuracy deviates >10 percentage points from published TriviaQA dev accuracy

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Underpowered pilot | A1 | H-E1, H-M3 | High |
| R2: VC prompt failure | A2 | H-M4 | Medium |
| R3: BERTScore insufficient | A3 | H-M3 | Medium |
| R4: EM label noise | A4 | All (uniform) | Low |
| R5: Non-representative pilot | A5 | H-E1, H-C1 | Medium |

### 4.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Underpowered N=98 pilot | A1 | High | H-E1, H-M3 | Pilot gate: extend to N=500 if gap < 0.05 |
| R2 | VC prompt-following failure | A2 | Medium | H-M4 | Pre-test prompt; fallback formats |
| R3 | BERTScore noise proxy | A3 | Medium | H-M3 | Validate vs NLI; switch if needed |
| R4 | EM label noise | A4 | Low | All | Use answer alias list; normalized EM |
| R5 | Non-representative pilot | A5 | Medium | H-E1, H-C1 | Verify sampling; compare difficulty dist. |

Critical Risks: 0 | High: 1 | Medium: 3 | Low: 1

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 6 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - no dependencies)
         │
         ▼
[Level 1 - Mechanism: Paraphrase Noise in TE]
    H-M1 ← H-E1
         │
         ▼
[Level 2 - Mechanism: SE Noise Filtering]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Mechanism: SCG Equivalence]
    H-M3 ← H-M2
         │
         ▼
[Level 4 - Mechanism: VC Scale Degradation]
    H-M4 ← H-M3
         │
         ▼
[Level 5 - Condition: Cross-Benchmark]
    H-C1 ← H-M4
         │
         ▼
    [COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
═══════════════════════════════════════════════════════════
```

### 5.2 Verification Phases with Gate Conditions

**Phase 1 - Foundation (Week 1-2)**

| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | SE-TE AUROC gap >= 0.05 on N=98 pilot | MUST PASS |

Gate 1: If H-E1 fails (gap < 0.03 after N=500 extension) → STOP, reassess hypothesis direction.
If gap in [0.03, 0.05] → extend to N=500 before evaluating gate.

**Phase 2 - Core Mechanisms (Week 3-7)**

| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST_WORK (paraphrase noise must be confirmed) |
| H-M2 | H-M1 | SHOULD_WORK (SE filtering mechanism) |
| H-M3 | H-M2 | SHOULD_WORK (SCG equivalence) |
| H-M4 | H-M3 | SHOULD_WORK (VC degradation) |

Gate 2: H-M1 must pass. H-M2/3/4 failures document limitations but don't block Phase 5.

**Phase 2.5 - Conditions (Week 8)**

| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-C1 | H-M4 | SHOULD_WORK (cross-benchmark generalization) |

Gate 2.5: H-C1 failure narrows scope claim to TriviaQA-only; does not invalidate main finding.

### 5.3 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |
| 5 | H-C1 | H-M4 | SHOULD_WORK |

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 6 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2     │ W3-4     │ W5   │ W6   │ W7   │ W8
──────────────────┼──────────┼──────────┼──────┼──────┼──────┼────
PHASE 1: Foundation
  H-E1            │ ████████ │          │      │      │      │
  [Gate 1]        │          │ ◆        │      │      │      │
──────────────────┼──────────┼──────────┼──────┼──────┼──────┼────
PHASE 2: Mechanisms
  H-M1            │          │ ████████ │      │      │      │
  H-M2            │          │          │ ████ │      │      │
  H-M3            │          │          │      │ ████ │      │
  H-M4            │          │          │      │      │ ████ │
  [Gate 2]        │          │          │      │      │      │ ◆
──────────────────┼──────────┼──────────┼──────┼──────┼──────┼────
PHASE 2.5: Conditions
  H-C1            │          │          │      │      │      │ ████
  [Gate 2.5]      │          │          │      │      │      │   ◆
──────────────────┼──────────┼──────────┼──────┼──────┼──────┼────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

```
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
Total Duration: 8 weeks
  Formula: 2 (H-E1) + 1+1+1+1+1 (H-M1 to H-M4) + 1 (H-C1) = 8 weeks
Slack Available: 0 weeks (all sequential)
```

### 5.6 Resource Summary

Total Hypotheses: 6
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1–H-M4)
- Condition: 1 (H-C1)

Verification Phases: 3 (Foundation, Mechanisms, Conditions)
Total Duration: 8 weeks
Critical Path Length: 8 weeks
Execution Mode: Sequential chain

### 5.7 Execution Order

1. Execute H-E1 (Foundation) — Week 1-2 (reuses h-e2-v2 samples, zero generation cost)
2. Evaluate Gate 1 → if SE-TE gap < 0.03: STOP; if [0.03, 0.05]: extend N=500; if >= 0.05: PASS
3. Execute H-M1 (paraphrase noise in TE) — Week 3-4
4. Execute H-M2 (SE clustering ablation) — Week 5
5. Execute H-M3 (SCG equivalence) — Week 6
6. Execute H-M4 (VC degradation) — Week 7
7. Evaluate Gate 2 → H-M1 must pass
8. Execute H-C1 (TruthfulQA cross-benchmark) — Week 8
9. Evaluate Gate 2.5 → determines scope breadth
10. Verification complete → Phase 5

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Under Llama-2-7B on TriviaQA dev, semantic entropy achieves a practically meaningful AUROC advantage over token entropy (>= 0.05), SelfCheckGPT achieves comparable AUROC to SE (|SCG-SE| <= 0.03), and verbalized confidence underperforms both — because semantic-level methods filter paraphrase noise that degrades token-level entropy, while VC fails due to 7B-scale calibration limitations.

**Supporting Evidence:**
1. h-e2-v2 confirmed SE mechanism activation (avg 3.89 clusters/question) and directional SE > TE gap (+0.029) at 7B scale
2. Key assumptions A1–A5 are supported by published prior work (Xiong 2023, Manakul 2023, Kuhn 2023)
3. Testable predictions P1–P3 are specific, quantitative, and falsifiable

**Strengths:**
- Builds on existing validated infrastructure (h-e2-v2 samples, NLI clustering code)
- Reuses existing pilot data (zero new generation cost for SE, SCG, TE)
- Clear prior literature support for each causal step
- Practical criterion (relative gap >= 0.05) better calibrated to 7B scale than absolute threshold (0.75)

**Expected Outcomes:**
- P1: SE AUROC - TE AUROC >= 0.05 (directional advantage confirmed at larger sample)
- P2: |SCG AUROC - SE AUROC| <= 0.03 (consistency-based method matches NLI-based)
- P3: VC AUROC < TE AUROC (verbalized calibration degraded at 7B)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in AUROC among the four uncertainty proxy methods on TriviaQA dev at Llama-2-7B scale. All pairwise AUROC gaps fall within bootstrap 95% CI half-width (< 0.05).

**Counter-Arguments:**
1. Prior baselines suggest limited AUROC differentiation at 7B — h-e2-v2 gap was only +0.029 (below 0.05 threshold); power at N=98 is marginal
2. Assumption violations are plausible: A1 (N=98 underpowered), A3 (BERTScore may not proxy consistency well), A5 (pilot may be unrepresentative)
3. Scope limitations are real: TE may be more robust than expected at 7B because short factual answers have low paraphrase variation

**Potential Failure Points:**
- From R1: Bootstrap CIs overlap even if directional gap exists (N=98 underpowered)
- From R3: BERTScore assigns high similarity to semantically different short answers (SCG noise)
- From R5: h-e2-v2 pilot is 98 random questions; may have atypical difficulty distribution

**Conditions Under Which H0 Would Be Supported:**
- If SE AUROC - TE AUROC < 0.03 after N=500 extension (falsification criterion P1)
- If |SCG-SE| > 0.05 (SCG does not achieve semantic-level equivalence)
- If all four method AUROCs cluster within [0.50, 0.58] (all near random at 7B)

### 6.3 Synthesis

**Balanced Assessment:**

Hypothesis H-SE4Way-v1 presents a testable claim grounded in prior h-e2-v2 empirical evidence (+0.029 SE-TE directional gap) and multiple published papers supporting each causal step. However, the null hypothesis raises valid concerns: (1) the directional gap from h-e2-v2 is below the 0.05 significance threshold, and (2) power at N=98 is marginal for the claimed effect size.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Tests the primary claim directly, with an explicit pilot gate (extend to N=500 if gap < 0.05) to handle power concerns
2. **Sequential mechanism testing (H-M1–4):** Tests each causal step independently, allowing partial validation even if the full chain fails
3. **Gate conditions:** H-E1 and H-M1 as MUST_WORK gates allow early detection of H0 support without wasted downstream effort

**Conditions for Thesis Support:**
- H-E1 passes (SE-TE gap >= 0.05 after up to N=500 extension)
- H-M1 passes (TE paraphrase noise confirmed)
- P1 confirmed with non-overlapping bootstrap CIs

**Conditions for Antithesis Support:**
- H-E1 fails (SE-TE gap < 0.03 after N=500 extension)
- All four methods cluster in [0.50, 0.58] AUROC range
- SE-TE gap from h-e2-v2 was sampling artifact (does not replicate)

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M1 + H-M2/3/4 all pass → Four-way ranking validated with mechanism
2. **Partial Support:** H-E1 passes, some H-M fail → SE-TE gap exists but mechanism interpretation uncertain
3. **Existence Only:** H-E1 passes, H-M1 fails → Gap exists but paraphrase noise not the cause
4. **No Support:** H-E1 fails → Antithesis supported; h-e2-v2 gap was underpowered artifact

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | SE-TE gap >= 0.05 at 7B | Gap was underpowered artifact (+0.029 in pilot) | H-E1 test with N=98 + gate to N=500 |
| Mechanism | Paraphrase noise degrades TE; SE/SCG filter it | Short factual QA may have low paraphrase variation | H-M1 ablation study on paraphrase pairs |
| SCG Equivalence | BERTScore captures semantic consistency | BERTScore noisy for short factual answers | H-M3 with BERTScore validity check |
| VC Degradation | 7B-scale calibration is insufficient | Chat model may be better calibrated than base | H-M4 with degenerate output detection |
| Scope | Finding generalizes to TruthfulQA | TriviaQA-specific format advantage | H-C1 cross-benchmark validation |
| Performance | Outperforms random baseline significantly | Near-random AUROC at 7B (all ~0.54) | Phase 5 comparison against full-scale baselines |

**Overall Robustness Score:** Medium
- Strong: Infrastructure reuse (zero generation cost), directional prior evidence, specific falsification criteria
- Weak: N=98 power, h-e2-v2 pilot gap below threshold, BERTScore proxy validity

**Confidence in Verification Plan:** 0.75 (matches Phase 2A confidence — no new uncertainties identified)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-SE4Way-v1 — Four-way uncertainty proxy comparison (TE, SCG, SE, VC) at Llama-2-7B on TriviaQA dev
- ID: H-SE4Way-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (builds on h-e2-v2 infrastructure)
- Sub-Hypotheses: 6 total (H-E1, H-M1–4, H-C1)
- Phases: 3 phases over 8 weeks
- Critical Gates: 3 decision points (Gate 1: MUST_WORK, Gate 2: MUST_WORK H-M1, Gate 2.5: SHOULD_WORK)

**Risk Assessment:** Medium
- Primary concerns: R1 (N=98 underpowered), R3 (BERTScore proxy validity)

**Immediate Action:** Begin Phase 1 with H-E1 (reuses h-e2-v2 samples — zero generation cost, ~30 min to compute TE + re-run SE AUROC)

### 7.2 Conclusions

**Key Achievements:**
- 6 hypotheses across 3 phases with explicit gate conditions
- H0 formally addressed via dialectical analysis
- 60% scope reduction from Phase 2A Established Facts (5 claims already validated by h-e2-v2)
- Zero-cost H-E1 execution (existing K=10 samples reused)

**Verification Execution Order:**

Phase 1: Foundation (2 weeks)
- H-E1: SE AUROC > TE AUROC by >= 0.05 | Gate: MUST PASS

Phase 2: Core Mechanisms (5 weeks)
- H-M1: TE paraphrase noise confirmed (W3-4)
- H-M2: SE NLI clustering ablation (W5)
- H-M3: SCG BERTScore equivalence (W6)
- H-M4: VC metacognitive failure at 7B (W7)
- Gate 2: H-M1 must pass

Phase 2.5: Conditions (1 week)
- H-C1: TruthfulQA cross-benchmark ranking (W8)
- Gate 2.5: Narrow scope on failure

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 AUROC gap >= 0.05
   - Gap < 0.03 after N=500 → STOP, reassess hypothesis direction
   - Gap in [0.03, 0.05] → Extend to N=500 before evaluating
   - Gap >= 0.05 → PASS, proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 paraphrase noise must be confirmed
   - FAIL → EXPLORE alternative mechanism; document limitation
   - H-M2/3/4 failures → Document limitations, do NOT block Phase 5

3. **Gate 2.5 (Conditions):** H-C1 cross-benchmark ranking
   - FAIL → Narrow scope to TriviaQA-only; does not invalidate main finding

**Open Questions:**
- Does the SE-TE gap hold or shrink at N=500 (vs. N=98 pilot)?
- Is SCG AUROC equivalent to SE? If yes, practitioners should use SCG (no logit access needed)
- Does the AUROC ranking hold on TruthfulQA?
- What is Precision@20% abstention for each method — does SE justify its overhead?

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 (zero generation cost — load existing h-e2-v2 samples)
   - Run TE computation from saved logits (or one greedy-decode pass if logits unavailable)
   - Verify h-e2-v2 random sampling seed for A5 validation

2. **Resource Allocation:**
   - Allocate 8 weeks for critical path
   - Reserve N=500 extension budget (GPU hours for additional generation if pilot gate triggers)
   - H-C1 requires new generation (N=200 TruthfulQA questions — only new compute cost)

3. **Failure Management:**
   - Document all partial results with bootstrap CIs
   - Pilot gate (extend to N=500) is non-optional if gap < 0.05
   - Execute PIVOT/EXPLORE strategies per hypothesis failure responses

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-SE4Way-v1)
- Previous: h-e2-v2 SUPERSEDED (SE AUROC 0.5419 gate failed at 0.75 threshold; new hypothesis uses relative gap criterion)

**B. MCP Tool Usage Summary**
- Total MCP calls: 0 (ablation mode — no MCP available in this session)
- Scientific method reasoning: performed directly from Phase 2A structured data

