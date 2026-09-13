# Verification Plan: Human Semantic Accommodation Sensitivity to RLHF Alignment Quality

**Date:** 2026-03-15
**Hypothesis ID:** H-SemAccom-v1
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under conditions where human-AI conversations in the HH-RLHF dataset are stratified by RLHF alignment tier (helpful_base → helpful_rejection_sampling → helpful_online), if RLHF tier quality increases, then the baseline-adjusted semantic similarity between human follow-up turns and their preceding AI partner turns (C_sem = E[cos(H_{t+1}, A_t)] - E[cos(H_{t+1}, A_t^matched-shuffle)]) will increase monotonically with tier AND the human→AI accommodation coefficient will exceed the AI→human coefficient (directional asymmetry), because RLHF-optimized AI responses carry higher epistemic uptake signals that trigger greater adaptive semantic alignment in human responses, analogous to lower-power interlocutors accommodating more to higher-status partners [Danescu-Niculescu-Mizil et al., 2011].

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in baseline-adjusted semantic similarity (C_sem) between human and AI turns across HH-RLHF alignment tiers; or the H→AI and AI→H accommodation coefficients are equal (no directional asymmetry). Formally: C_sem^(H←A) ≤ C_sem^(A←H) and no monotonic tier ordering at d ≥ 0.1. Observed similarities reflect topical coherence of helpfulness-focused dialogues, not partner-specific semantic accommodation driven by RLHF quality gradient.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Anthropic/hh-rlhf (helpfulness splits) (standard) | Three-tier RLHF quality gradient directly operationalizes the IV; chosen/rejected structure provides within-tier quality control; ~273,617 conversation turns provides sufficient N for d ≥ 0.1 detection |
| **Model** | all-MiniLM-L6-v2 (primary); paraphrase-MiniLM-L6-v2, all-mpnet-base-v2 (robustness) | SBERT validated for semantic similarity measurement; CPU-capable (14K sentences/sec); no fine-tuning required; multi-model robustness test rules out geometry artifacts |

**Dataset Details:**
- Source: HuggingFace datasets
- Path: `datasets.load_dataset('Anthropic/hh-rlhf', data_dir='helpful-base|helpful-rejection-sampled|helpful-online')`

**Model Details:**
- Type: sentence-transformers (pre-trained, inference-only)
- Source: HuggingFace model hub / sentence-transformers library

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Function-word coordination (Danescu-Niculescu-Mizil et al. 2011) | C_m(b,a) = P(E_m^u2\|E_m^u1) - P(E_m^u2); p < 0.05 asymmetry in Wikipedia and Supreme Court | Wikipedia (240,436 exchanges), Supreme Court (50,389 exchanges) |
| Word-level LLM-human bidirectional adaptation (Chang & Wang 2025) | Word-level style matching confirmed in LLM-human dialog across cultures | Cross-cultural LLM-human interaction data |
| PM-grounded feature analysis on HH-RLHF (h-e1 Attempt 2) | Max d=0.136; keyword proxies insufficient; placebo features (length d=0.735) dominated | HH-RLHF (~118K assistant turns) |
| Human turn lexical features on HH-RLHF (h-e1 Attempt 3) | d_human=0.036; CI includes zero; hapax anti-monotonic | HH-RLHF (~89K human turns) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | SBERT cosine similarity of full-utterance embeddings is sensitive to accommodation-relevant semantic shifts, not only topical similarity | SBERT validated for STS tasks; element-wise difference |u-v| is most discriminative [Reimers & Gurevych 2019]; three-level control (actual > topic-matched > random) tests this assumption directly | C_sem measures topical coherence rather than accommodation; partner-specificity gap disappears; study reports null result for semantic accommodation |
| A2 | HH-RLHF tiers attract comparable user populations with similar intent distributions | All three tiers are helpfulness-oriented; same platform and annotation protocol [Bai et al. 2022]; but users may differ — requires KS test on prompt embedding distributions | Tier effect confounded by user selection bias; requires matching or weighting; claim narrows to 'conditional on matched prompt strata' |
| A3 | The chosen/rejected pair structure in HH-RLHF provides prompt-controlled quality variation (same prompt, different PM-score responses) | Directly encoded in HH-RLHF dataset format; confirmed in Bai et al. 2022 and Ouyang et al. 2022 RM training data structure | Within-tier Δ design fails; chosen and rejected responses differ on prompt in addition to quality — requires verification before analysis |
| A4 | Accommodation operates at the semantic/meaning level (not just surface stylistic level) for human-AI interactions | Three prior failures on surface features (d=0.036, d=0.136); SBERT captures meaning-level representations; CAT theory predicts meaning-level convergence | If SBERT cos_sim also fails (d < 0.1), the semantic accommodation hypothesis is refuted; ROUTE_TO_0 again |
| A5 | N_pairs ≥ 1000 per tier for within-tier chosen/rejected Δ test (statistical power requirement) | HH-RLHF contains paired conversations; total 273,617 turns; specific N_pairs must be verified empirically before committing to this prediction | Drop within-tier Δ as a pre-registered prediction; retain as exploratory; restrict to tier-level asymmetry predictions (P1, P2) |

### 1.6 Research Gap & Novelty

**Gap:** No prior work has applied semantic embedding-based measurement (SBERT cosine similarity) to quantify human accommodation to RLHF alignment quality gradients. Three prior attempts on HH-RLHF using surface lexical features (word_count, hapax_ratio, PM-grounded keywords) all failed (d ∈ [0.036, 0.136]), suggesting the effect exists at the semantic embedding level rather than surface level.

**Novelty:** Three simultaneous innovations: (1) semantic-level (SBERT) operationalization of CAT coordination framework in RLHF context; (2) directional asymmetry test (H→AI vs AI→H) in RLHF tier-stratified setting; (3) within-prompt PM-quality causal probe using HH-RLHF's chosen/rejected structure. Extends Danescu 2011 from function-word to semantic embedding level; extends Chang & Wang 2025 from word-level to SBERT cosine; provides operational measurement for BiAlign workshop's [Shen et al. 2025] theoretical gap (gap-1-sbert-accommodation).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-E1, H-M1 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M1, H-M2, H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Semantic Accommodation Existence — Partner-Specific C_sem > 0**

**Type:** EXISTENCE
**Statement:** Under HH-RLHF helpfulness conversations, if SBERT cosine similarity is computed between human follow-up turns and AI partner turns with matched-shuffle baseline subtraction, then C_sem^H←A = E[cos(SBERT(H_{t+1}), SBERT(A_t))] - E[cos(SBERT(H_{t+1}), SBERT(A_t^matched-shuffle))] > 0 AND partner-specificity gap holds (cos(H_next, A_actual) > cos(H_next, A_topic-matched) > cos(H_next, A_random), d ≥ 0.1 between adjacent levels), because semantic accommodation to a specific interlocutor produces interaction-specific alignment beyond topical coherence.

**Rationale:** This is the foundational existence proof for the entire study. Without C_sem > 0 with partner-specificity, neither tier-level monotonicity nor directional asymmetry can be interpreted as evidence of accommodation. This establishes that SBERT captures accommodation-relevant semantic variation, not merely topical persistence, via the three-level control hierarchy.

**Variables:**
- IV: Actual vs. topic-matched vs. random AI turn (three-level control)
- DV: C_sem = E[cos(SBERT(H_{t+1}), SBERT(A_t))] - shuffle baseline; cos(H_next, A_actual); cos(H_next, A_topic-matched)
- CV: Response length (residualized), lexical overlap (residualized), prompt embedding distribution (KS test)

**Verification Protocol:**
1. Encode all HH-RLHF helpful splits with all-MiniLM-L6-v2 (batch size 256, CPU); build K=5 KNN topic-matched control by prompt embedding from different conversations in same tier.
2. Compute C_sem with true random shuffle baseline for all tiers combined (pooled over tiers for existence test).
3. Compute three-level partner-specificity: cos(H_next, A_actual), cos(H_next, A_topic-matched), cos(H_next, A_random).
4. Test pairwise Mann-Whitney U + bootstrap Cohen's d (n=1000, seed=42) for each adjacent level contrast.
5. Report bootstrap CI for C_sem; check if lower bound > 0; confirm d ≥ 0.1 between actual and topic-matched.

**Success Criteria:**
- Primary: C_sem^H←A > 0 with bootstrap CI lower bound > 0
- Secondary: d ≥ 0.1 between cos(H_next, A_actual) and cos(H_next, A_topic-matched), with three-way inequality holding

**Gate:**
- Type: MUST_WORK
- If Fail: STOP pipeline; report null result for semantic accommodation existence; write Serena failure memory; ROUTE_TO_0 for new direction

**Prerequisites:** None

**Source:** Phase 2A Section 5 (sh1_existence), Prediction P2 (partner-specificity)

---

---
**H-M1: Tier-Monotonic Semantic Accommodation Scaling**

**Type:** MECHANISM
**Statement:** Under HH-RLHF helpfulness conversations stratified by RLHF alignment tier (helpful_base rank=1, helpful_rejection_sampling rank=2, helpful_online rank=3), if tier quality increases, then C_sem^H←A increases monotonically across tiers (Jonckheere-Terpstra p < 0.05, Cohen's d ≥ 0.1 for tier contrast), consistent across ≥ 2/3 SBERT models (all-MiniLM-L6-v2, paraphrase-MiniLM-L6-v2, all-mpnet-base-v2), because RLHF training produces progressively higher epistemic quality AI responses that trigger proportionally greater semantic alignment in human follow-up turns.

**Rationale:** This is the core mechanistic claim linking RLHF quality gradient to accommodation magnitude. It tests whether the existence-level C_sem (established in H-E1) is specifically driven by tier quality, not just an artifact of the dataset or SBERT geometry. Multi-model replication rules out geometry-specific artifacts. This is the primary test of Prediction P1.

**Variables:**
- IV: RLHF alignment tier (categorical, 3 levels: helpful_base/RS/online; rank 1/2/3)
- DV: C_sem^H←A per tier (continuous)
- CV: Prompt embedding distribution (KS test + IPW if distributions differ), response length, lexical overlap

**Verification Protocol:**
1. Compute C_sem^H←A per tier using matched-shuffle baseline for each of 3 SBERT models separately.
2. Run Jonckheere-Terpstra monotonicity test across three tiers (alternative: increasing).
3. Compute pairwise Mann-Whitney U + bootstrap Cohen's d (n=1000, seed=42) for all tier pairs; apply Bonferroni correction.
4. Run KS test on prompt embedding distributions across tiers; if KS p < 0.05, apply inverse-probability weighting and recompute.
5. Check consistency across ≥ 2/3 SBERT models; report all three models transparently.

**Success Criteria:**
- Primary: J-T p < 0.05 AND d ≥ 0.1 for tier contrast in ≥ 2/3 SBERT models
- Secondary: Monotonic direction consistent across all three models (even if only ≥ 2/3 significant)

**Gate:**
- Type: MUST_WORK
- If Fail: H-M2, H-M3, H-M4 blocked; document tier monotonicity failure; ROUTE_TO_0 or scope to existence-only claim

**Prerequisites:** H-E1

**Source:** Phase 2A Section 1.3 (causal steps 1, 3, 4), Section 1.6 (P1)

---

---
**H-M2: Directional Asymmetry — H→AI > AI→H Accommodation**

**Type:** MECHANISM
**Statement:** Under HH-RLHF tier-stratified conversations, C_sem^H←A (human accommodates to AI) systematically exceeds C_sem^A←H (AI accommodates to human) at ≥ 2/3 RLHF tiers (Mann-Whitney p < 0.05), consistent with the power asymmetry framework where lower-power interlocutors accommodate more to higher-status partners [Danescu-Niculescu-Mizil et al. 2011].

**Rationale:** This tests whether the tier effect reflects a genuine power asymmetry dynamic (human defers to RLHF-optimized AI) versus symmetric mutual coherence (both parties align symmetrically in helpfulness dialogues). The distinction is critical: asymmetry supports the epistemic authority mechanism, while symmetry supports topical coherence. This directly tests the directionality component of Prediction P1.

**Variables:**
- IV: Accommodation direction (H→AI vs AI→H; categorical, 2 levels)
- DV: C_sem (bilateral; continuous)
- CV: Tier (controlled by within-tier comparison), response length, lexical overlap

**Verification Protocol:**
1. Compute C_sem^A←H using the same matched-shuffle baseline framework (AI turn embeddings vs shuffled human turns).
2. Compare C_sem^H←A vs C_sem^A←H within each tier using Mann-Whitney U test.
3. Report directional asymmetry for each tier × SBERT model combination.
4. Analyze asymmetry pattern across tiers: check if asymmetry increases with tier quality (stronger epistemic authority at higher tiers).
5. Distinguish "H defers more" from "higher-tier AI is more contextually integrated" via regression controlling for AI response coherence proxies.

**Success Criteria:**
- Primary: C_sem^H←A > C_sem^A←H with p < 0.05 at ≥ 2/3 tiers
- Secondary: Asymmetry magnitude increases monotonically with tier (asymmetry^online > asymmetry^RS > asymmetry^base)

**Gate:**
- Type: SHOULD_WORK
- If Fail: Refines thesis to symmetric mutual coherence interpretation; does not block H-M4; document as scope limitation; reinterpret as evidence against epistemic authority hypothesis

**Prerequisites:** H-M1

**Source:** Phase 2A Section 1.3 (causal step 4), Section 1.6 (P1 directional component)

---

---
**H-M3: Within-Tier Quality Gradient — Chosen vs. Rejected Δ**

**Type:** MECHANISM
**Statement:** Within the same prompt (chosen/rejected pairs), human follow-up turns show higher semantic similarity to higher-PM-score AI responses (chosen) than to lower-PM-score responses (rejected): Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected) > 0, surviving ≥ 2/3 length-control operationalizations (raw, length-matched truncation, prompt-projected), conditional on N_pairs ≥ 1000 per tier being verified empirically.

**Rationale:** This provides a within-prompt quasi-experimental quality probe, controlling for prompt content and conversation context — the strongest available causal test for the quality-accommodation link. The HH-RLHF chosen/rejected structure is a unique empirical asset. If confirmed, it isolates the PM-score quality signal from tier-level confounds. Conditional on Assumption A5 (N_pairs ≥ 1000 per tier).

**Variables:**
- IV: PM-score quality within same prompt (chosen vs. rejected, categorical)
- DV: Δ = cos(H_next, A_chosen) - cos(H_next, A_rejected) (continuous)
- CV: Response length (three operationalizations), prompt embedding (projection control), tier

**Verification Protocol:**
1. Filter HH-RLHF to paired conversations (same prompt, chosen + rejected response); count N_pairs per tier.
2. If N_pairs < 1000 per tier: demote H-M3 to exploratory; skip gate evaluation; continue to H-M4 with exploratory note.
3. Compute Δ via three operationalizations: (a) raw cosine, (b) length-matched truncation of chosen to rejected length, (c) projecting out prompt embedding from both A vectors.
4. Bootstrap CI (n=1000, seed=42) for each operationalization; test if lower bound > 0.
5. Run linear regression of Δ on PM-score proxy controlling for length, bullet structure, politeness markers.

**Success Criteria:**
- Primary: E[Δ] > 0 with bootstrap CI lower bound > 0 in ≥ 2/3 operationalizations (conditional on N_pairs ≥ 1000)
- Secondary: Δ magnitude consistent across tiers; length-matched operationalization > 0 (length confound controlled)

**Gate:**
- Type: SHOULD_WORK
- If Fail (N_pairs sufficient): Demote Δ to null result; document length confound as possible explanation; H-M4 proceeds with reduced causal claim
- If Fail (N_pairs insufficient): Auto-demote to exploratory; not counted as falsification

**Prerequisites:** H-E1, H-M1

**Source:** Phase 2A Section 1.6 (P3), Section 1.4 (A5), Section 2 (baselines: chosen/rejected Δ)

---

---
**H-M4: PM-Score Mediates C_sem Above Surface-Feature Controls**

**Type:** MECHANISM
**Statement:** Under HH-RLHF tier-stratified conversations, PM-score proxy (chosen/rejected preference) positively predicts C_sem^H←A (β > 0, p < 0.05) after controlling for surface-feature controls (response length, bullet/list structure, politeness marker density, syntactic complexity), because the epistemic quality encoded in RLHF training drives accommodation above and beyond formatting signals.

**Rationale:** This tests the mechanistic specificity of the epistemic uptake sensitivity hypothesis: does RLHF-quality drive accommodation via epistemic content, or merely via formatting salience (bullet points, polite phrasing)? This is the weakest assumption in the causal chain (mechanism step 2) and the critical test for interpretable findings. Either outcome is informative: PM significance → epistemic quality mechanism; PM null → formatting salience mechanism.

**Variables:**
- IV: PM-score proxy (chosen/rejected preference; categorical mapped to quality gradient)
- DV: C_sem^H←A (continuous)
- CV: Response length (word count), bullet/list structure (instruction_decomp_density), politeness markers (politeness_freq), syntactic complexity (TTR, sentence length)

**Verification Protocol:**
1. Construct mediation regression: C_sem^H←A ~ PM_proxy + response_length + bullet_density + politeness_freq + syntactic_complexity + tier.
2. Test significance of PM_proxy coefficient (β_PM) after all surface-feature controls are included.
3. Compare β_PM (full model) to β_PM (PM-only model) to assess surface-feature mediation proportion.
4. Run robustness check: replace PM_proxy with tier rank; confirm tier effect also survives controls.
5. Report whether PM_proxy becomes non-significant when surface features are added (formatting hypothesis supported) or remains significant (epistemic quality hypothesis supported).

**Success Criteria:**
- Primary: β_PM > 0 and p < 0.05 in full mediation model with surface-feature controls
- Secondary: β_PM does not shrink to zero when surface features added (epistemic quality not fully mediated by formatting)

**Gate:**
- Type: SHOULD_WORK
- If Fail: Document mechanism as formatting-driven rather than epistemic; publish existence + tier results with mechanism caveat; reformulate as "RLHF formatting signals drive accommodation" hypothesis in future work

**Prerequisites:** H-M1, H-M2, H-M3

**Source:** Phase 2A Section 1.3 (causal step 2, key_tension), Section 1.6 (P3 regression component)

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 ─┐
              └─ H-M3 ─┴→ H-M4
```

Note: H-M2 and H-M3 both depend on H-M1 but not on each other; they can run in parallel. H-M4 requires all of H-M1, H-M2, H-M3.

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | C_sem > 0 (bootstrap CI lower bound > 0) AND d ≥ 0.1 partner-specificity | STOP pipeline; write Serena failure memory; ROUTE_TO_0 |
| H-M1 | MUST_WORK | J-T p < 0.05 AND d ≥ 0.1 in ≥ 2/3 SBERT models | Block H-M2/H-M3/H-M4; document tier monotonicity failure; ROUTE_TO_0 |
| H-M2 | SHOULD_WORK | C_sem^H←A > C_sem^A←H with p < 0.05 at ≥ 2/3 tiers | Refine to symmetric coherence interpretation; continue to H-M4 |
| H-M3 | SHOULD_WORK | E[Δ] > 0 in ≥ 2/3 operationalizations (if N_pairs ≥ 1000) | Demote to null; H-M4 proceeds with reduced causal claim |
| H-M4 | SHOULD_WORK | β_PM > 0 and p < 0.05 after surface-feature controls | Document as formatting-driven mechanism; publish with caveat |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Gate 1 | H-E1 MUST_WORK evaluation | End Week 2 |
| Phase 2: Core Mechanisms (parallel) | H-M1, H-M2, H-M3 | 2 weeks |
| Gate 2 | H-M1 MUST_WORK evaluation | End Week 4 |
| Phase 3: Mechanism Synthesis | H-M4 | 1 week |
| Gate 3 | H-M4 SHOULD_WORK evaluation | End Week 5 |

**Total Duration:** 5 weeks

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2    │ W3-4    │ W5
──────────────────┼─────────┼─────────┼─────────
PHASE 1: Foundation
  H-E1            │ ████████│         │
  [Gate 1]        │       ◆ │         │
──────────────────┼─────────┼─────────┼─────────
PHASE 2: Mechanisms (parallel execution)
  H-M1            │         │ ████████│
  H-M2            │         │ ████████│
  H-M3            │         │ ████████│
  [Gate 2]        │         │       ◆ │
──────────────────┼─────────┼─────────┼─────────
PHASE 3: Synthesis
  H-M4            │         │         │ ████████
  [Gate 3]        │         │         │       ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Description | Severity | Affected Hypotheses |
|------|--------|-------------|----------|---------------------|
| R1 | A1 | SBERT captures topical coherence not accommodation; partner-specificity gap vanishes | High | H-E1 (blocks all) |
| R2 | A2 | HH-RLHF tier user populations non-comparable; tier effect confounded by selection bias | Medium | H-M1, H-M2 |
| R3 | A3 | Chosen/rejected pairs don't share prompts cleanly; within-tier Δ design fails | Medium | H-M3 |
| R4 | A4 | SBERT also fails (d < 0.1); semantic accommodation hypothesis refuted entirely | Critical | All hypotheses |
| R5 | A5 | N_pairs < 1000 per tier; H-M3 underpowered | Medium | H-M3 |

### 4.2 Mitigation Strategies

**R1 (SBERT topical coherence):** Prevention: Use three-level control (actual > topic-matched > random) to directly test metric validity. Detection: If partner-specificity gap d < 0.1 between actual and topic-matched → R1 confirmed. Response: ABORT H-E1, report as methodological null result; ROUTE_TO_0.

**R2 (Tier population heterogeneity):** Prevention: KS test on prompt embedding distributions across all tier pairs before analysis. Detection: If KS p < 0.05 for any tier pair → apply inverse-probability weighting (IPW). Response: PIVOT to IPW-weighted analysis; narrow claim to "conditional on matched prompt strata."

**R3 (Chosen/rejected prompt mismatch):** Prevention: Empirically verify prompt matching in HH-RLHF structure before H-M3 commitment. Detection: If chosen and rejected responses derive from different prompts → R3 confirmed. Response: SCOPE H-M3 to exploratory; proceed to H-M4 without H-M3 gate.

**R4 (SBERT fundamental failure):** Prevention: None possible beyond dataset/method selection already made. Detection: H-E1 bootstrap CI includes zero; d < 0.1 for all baselines. Response: ABORT all hypotheses; write detailed Serena failure memory documenting fourth HH-RLHF failure; ROUTE_TO_0 with note that HH-RLHF may not exhibit measurable semantic accommodation at any feature level.

**R5 (N_pairs insufficient):** Prevention: Verify N_pairs empirically at start of H-M3. Detection: Count paired conversations per tier in HH-RLHF. Response: If N_pairs < 1000 per tier → auto-demote H-M3 to exploratory; mark as conditional result; H-M4 PM mediation proceeds without H-M3 support.

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** H-SemAccom-v1 — RLHF-optimized AI responses carry higher epistemic quality that triggers asymmetric human semantic accommodation, measurable via SBERT C_sem metric with partner-specificity validation.

**Supporting Evidence:**
1. CAT theory predicts accommodation to high-status/high-quality partners; empirically validated in Wikipedia/Supreme Court [Danescu 2011]
2. SBERT validated for semantic-level similarity (STS benchmarks); CPU-feasible at 14K sent/sec
3. Three prior surface-level failures (d=0.036, d=0.136) suggest effect exists at semantic embedding level
4. HH-RLHF chosen/rejected structure provides unique within-prompt quality probe

**Confidence:** 0.72

### 5.2 Antithesis

**Null Hypothesis (H0):** Observed semantic similarities reflect topical coherence of helpfulness-focused dialogues; no partner-specific accommodation driven by RLHF quality gradient.

**Counter-Arguments:**
1. Three prior HH-RLHF failures suggest this dataset may resist behavioral stratification
2. SBERT full-utterance embeddings may capture topic more than accommodation-specific semantic shifts
3. User population heterogeneity across tiers is a genuine untested confound

**Conditions for H0 Support:**
- H-E1 fails (d < 0.1 for partner-specificity gap)
- KS test shows distributions incomparable and IPW does not resolve tier effect
- C_sem^H←A ≈ C_sem^A←H (symmetric coherence, not asymmetric accommodation)

**Confidence:** 0.28

### 5.3 Synthesis

The verification plan resolves the dialectic through empirical gates with pre-specified failure conditions:

**Resolution Path:**
1. H-E1 (MUST_WORK) directly tests antithesis concern: three-level partner-specificity control distinguishes accommodation from topical coherence
2. H-M1 (MUST_WORK) tests tier-monotonicity with multi-model robustness, ruling out SBERT geometry artifacts
3. H-M2 distinguishes epistemic authority (asymmetric) from mutual coherence (symmetric) interpretations
4. H-M3 provides within-prompt causal probe isolating quality from confounds
5. H-M4 tests mechanism specificity (epistemic quality vs formatting salience)

**Nuanced Outcome Possibilities:**
- Full Support: H-E1 + H-M1 pass, H-M2 asymmetry holds → Thesis validated; existence + mechanism confirmed
- Partial Support: H-E1 + H-M1 pass, H-M2 symmetric → Refined to mutual coherence claim; publishable with scope adjustment
- Existence Only: H-E1 passes, H-M1 fails → C_sem exists but not tier-stratified; scope to single-tier existence claim
- No Support: H-E1 fails → Antithesis supported; fourth HH-RLHF failure across all feature levels; ROUTE_TO_0

**Overall Robustness:** High (both outcomes theoretically informative)

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | C_sem > 0 partner-specific | May be topical coherence | H-E1 three-level control |
| Mechanism | Tier quality drives C_sem monotonically | Dataset artifact or population confound | H-M1 + KS/IPW + multi-model |
| Direction | H→AI > AI→H (power asymmetry) | Symmetric mutual coherence | H-M2 bilateral test |
| Quality | PM-score predicts Δ above formatting | Formatting salience explains effect | H-M4 mediation regression |

---

## 6. Executive Summary

**Main Hypothesis:** H-SemAccom-v1 — Human semantic accommodation (C_sem) increases monotonically with RLHF tier quality, with H→AI > AI→H directional asymmetry
- ID: H-SemAccom-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (Phase 2A data loaded; 43% scope reduction via BUILD_ON claims)
- Sub-Hypotheses: 5 total (H-E1: 1, H-M: 4, H-C: 0)
- Phases: 3 phases over 5 weeks
- Critical Gates: 3 decision points (Gate 1: MUST_WORK H-E1, Gate 2: MUST_WORK H-M1, Gate 3: SHOULD_WORK H-M4)

**Risk Assessment:** Medium
- Primary concerns: R4 (SBERT fundamental failure, Critical), R1 (topical coherence confound, High)

**Immediate Action:** Begin Phase 1 with H-E1 (encode all HH-RLHF helpful splits with all-MiniLM-L6-v2; run partner-specificity test)

---

## 7. Conclusions

**Key Achievements:**
- 5 hypotheses across 3 execution phases with clear gate conditions
- H0 fully addressed: C_sem^(H←A) ≤ C_sem^(A←H) and no monotonic tier ordering
- 43% scope reduction: BUILD_ON claims (SBERT validity, tier structure, prior failures) not re-verified

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: C_sem^H←A > 0 with three-level partner-specificity validation
- Gate 1: MUST PASS → ROUTE_TO_0 on failure

**Phase 2: Core Mechanisms** (2 weeks, parallel)
- H-M1: Tier monotonicity (J-T + multi-model robustness)
- H-M2: Directional asymmetry (bilateral C_sem comparison) — parallel with H-M1
- H-M3: Within-tier chosen/rejected Δ (conditional on N_pairs ≥ 1000) — parallel with H-M1
- Gate 2: H-M1 MUST PASS

**Phase 3: Mechanism Synthesis** (1 week)
- H-M4: PM-score mediation above surface-feature controls
- Gate 3: SHOULD PASS → document mechanism as formatting-driven if fails

**Critical Decision Points:**
1. Gate 1 (Foundation): H-E1 must pass → STOP + ROUTE_TO_0 on failure
2. Gate 2 (Mechanisms): H-M1 must pass → H-M2/H-M3/H-M4 blocked on failure
3. Gate 3 (Synthesis): H-M4 should pass → caveat on mechanism interpretation if fails

**Open Questions:**
- Does N_pairs ≥ 1000 per tier hold for P3 chosen/rejected Δ? Verify before committing.
- Are prompt embedding distributions comparable across tiers? KS test required before analysis.
- Does PM score mediate C_sem after controlling for length, structure, politeness? Core mechanism question.
- Does asymmetry inversion (AI→H > H→AI at higher tiers) occur? Requires asymmetry pattern analysis.

**Recommendations:**
1. **Immediate Actions:** Start Phase 1 with H-E1 encoding (all-MiniLM-L6-v2 on all 3 splits, CPU); verify N_pairs and prompt distribution before Phase 2
2. **Resource Allocation:** 5 weeks for critical path; reserve 1 additional week for KS/IPW sensitivity analysis if R2 triggers
3. **Failure Management:** Document all failures with Serena memory; execute ROUTE_TO_0 if H-E1 or H-M1 fail; this would be fourth HH-RLHF failure

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-SemAccom-v1, schema v10.0.0)
- **Gap ID:** gap-1-sbert-accommodation
- **Convergence:** CONVERGE at Exchange 15 (15-exchange Tikitaka dialogue with 6 agents)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 5 (3x sequentialthinking + 3x structuredargumentation)
- **Tools:** mcp__clearThought__sequentialthinking (3x: hypothesis generation, verification design, risk/timeline synthesis); mcp__clearThought__structuredargumentation (3x: thesis, antithesis, synthesis)

---

*Generated by YouRA Phase 2B (Compact v1.0) | 2026-03-15*
