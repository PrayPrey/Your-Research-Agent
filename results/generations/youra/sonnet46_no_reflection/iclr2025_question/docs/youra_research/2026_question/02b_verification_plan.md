---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-dag-construction", "step-06-risk-analysis", "step-07-timeline", "step-08-dialectical-analysis", "step-09-executive-summary", "step-10-finalize"]
status: complete
startedAt: "2026-05-20T00:43:00"
completedAt: "2026-05-20T00:55:00"
hypothesis_id: "H-EGSH-v1"
pipeline_project_id: "d93a479b-d013-43f6-afa5-1479d3648efe"
---

# Verification Plan: Epistemic Geometry Scaling Hypothesis (EGSH)

**Date:** 2026-05-20
**Hypothesis ID:** H-EGSH-v1
**Confidence:** 0.78
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the Llama-3 model family evaluated on standard factual QA benchmarks (TriviaQA, NaturalQuestions), if model scale increases from 8B to 70B base checkpoints while holding dataset splits, evaluation harness, and benchmark conditions fixed, then semantic-structural UQ methods (SE, KLE) will show a significantly larger AUROC advantage over token-probability than at smaller scale, AND correctness-predictive information will shift to deeper transformer layers — because larger model capacity enables richer semantic equivalence class representations that surface-level token distributions cannot capture.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in the relative AUROC advantage of semantic-structural UQ methods (SE, KLE) over token-probability between Llama-3-8B and Llama-3-70B base checkpoints on TriviaQA and NaturalQuestions; all methods scale proportionally (no method × scale interaction).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA + NaturalQuestions (primary); TruthfulQA (secondary) (standard) | TriviaQA and NQ are factual retrieval benchmarks with ground-truth correctness labels and standard splits; directly targeted by the EGSH scaling hypothesis. TruthfulQA serves as scope boundary test (P4). |
| **Model** | Llama-3-8B-Base, Llama-3-70B-Base; Llama-3-70B-Instruct (control) | Same model family with controlled scale variation; base checkpoints eliminate RLHF confounds; 70B-instruct as within-scale control to distinguish scale-driven from post-training effects |

**Dataset Details:**
- Source: HuggingFace datasets hub; original benchmark repositories
- Path: Standard test splits; identical across all methods

**Model Details:**
- Type: autoregressive decoder-only LLM
- Source: meta-llama/Meta-Llama-3-8B, meta-llama/Meta-Llama-3-70B on HuggingFace

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| Semantic Entropy (Farquhar et al. 2024) | AUROC ~0.72–0.79 | TriviaQA, NQ, BioASQ, SQuAD |
| SelfCheckGPT (Manakul et al. 2023) | AUROC on WikiBio with GPT-3 | WikiBio |
| Semantic Entropy Probes (Kossen et al. 2024) | Comparable to generative SE | TriviaQA, NQ (Llama-2) |
| KLE (Nikitin et al. 2024) | AUROC competitive with SE | TriviaQA, NQ, BioASQ |
| Token-probability (max softmax) | AUROC ~0.67 on TriviaQA | TriviaQA (Llama-2-70B) |
| LM-Polygraph (20+ UQ methods) | Multi-method benchmark | Multiple benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Llama-3-8B and 70B base checkpoints share sufficient pretraining data distribution similarity | Meta Llama-3 technical report: shared corpus; base-model control eliminates RLHF differences | Results remain valid as empirical observations but mechanistic interpretation weakens |
| A2 | AUROC over binary correctness labels is valid proxy for UQ quality on TriviaQA/NQ | Standard metric in SE, SelfCheckGPT, LM-Polygraph papers; exact-match normalization established in QA literature | Cross-method comparisons may be contaminated; mitigated by single evaluation harness |
| A3 | Probe-based MI approximation (linear and 2-layer MLP) captures relevant correctness-predictive signal | Linear probes standard in representation analysis; SEPs demonstrate effectiveness for UQ | Nonlinear structure may not be captured; mitigated by 2-layer MLP nonlinear baseline |
| A4 | N=10 samples per query provides stable sampling-based UQ estimates | Farquhar et al. 2024 used N=10; sufficient for AUROC stability on TriviaQA/NQ scale | High variance in sampling-based methods; mitigated by bootstrap CI on all AUROC estimates |
| A5 | TriviaQA and NQ represent factual retrieval epistemic uncertainty | Both benchmarks are standard factual QA with ground-truth labels; P4 predicts attenuation on TruthfulQA | If TriviaQA/NQ contain significant adversarial items, benchmark-specific prediction harder to interpret |

### 1.6 Research Gap & Novelty

**Gap:** No controlled cross-paradigm UQ comparison exists on identical model/split/metric conditions; prior work evaluates methods at fixed scale only (Kang et al. 2025 survey identifies evaluation fragmentation as key limitation).

**Novelty:** Three methodological contributions: (1) permutation-corrected layer-wise probe gap G_corrected(l) as a metric for isolating epistemic accessibility from generic representational expressiveness; (2) cumulative-MI depth quantile d_50 as a scale-robust depth measure; (3) convergent multi-diagnostic framework (external AUROC interaction + internal depth shift) for structural UQ claims. The reframing from "which method ranks first" to "how does uncertainty reorganize with scale" is genuinely new.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Semantic-Structural UQ Advantage Exists at Both Scales**

**Statement**: Under Llama-3 base checkpoints on TriviaQA and NaturalQuestions with identical splits and harness, if SE and KLE are compared to token-probability, then SE/KLE show statistically higher AUROC at both 8B and 70B scales — because semantic equivalence class aggregation captures uncertainty signals that vocabulary distributions cannot.

**Rationale**: This is the foundation hypothesis. The method×scale interaction (H-M3) is only meaningful if the semantic-structural UQ advantage exists at both scales. Establishing existence first ensures later mechanism tests are built on confirmed ground.

**Variables** (from Phase 2A):
- Independent: UQ method paradigm (SE, KLE vs token-probability)
- Dependent: AUROC for correctness prediction at each scale
- Controlled: Model scale (both), dataset splits, evaluation harness, N=10 sampling

**Verification Protocol** (full TriviaQA test: 17,944q; NQ test: 3,610q):
1. Generate greedy decode + N=10 samples per query for Llama-3-8B-Base and 70B-Base via UQLM
2. Apply all 6 UQ methods (token-prob, SelfCheckGPT-BERTScore/NLI, SE, KLE, SEPs) through unified UQLM harness
3. Compute AUROC per method per model on full standard test splits; bootstrap CI (1000 resamples)
4. Test SE > token-prob and KLE > token-prob at each scale via paired bootstrap (one-sided, α=0.05)
5. Confirm advantage holds on both TriviaQA and NQ independently

**Success Criteria** (PoC):
- Primary: SE AUROC > token-prob AUROC at both 8B and 70B, with 95% CI excluding zero, on both TriviaQA and NQ
- Secondary: KLE AUROC > token-prob AUROC at both scales (extends existence to both SE and KLE)

**Failure Response**:
- IF fails at 8B only: PIVOT — re-examine SE implementation; check UQLM normalization
- IF fails at both scales: ABANDON H-M* — semantic advantage does not exist; reassess EGSH
- IF KLE fails only: SCOPE — EGSH narrowed to SE only

**Dependencies**: None (foundation)

**Source**: Phase 2A sh1_existence, prediction P1 baseline prerequisite

---

**H-M1: Semantic Representations Shift Deeper with Scale**

**Statement**: Under Llama-3 base checkpoints, if model scale increases from 8B to 70B, then the cumulative-MI 50th-percentile depth d_50 shifts significantly deeper at 70B — because larger capacity enables richer semantic equivalence class representations that localize to deeper transformer layers.

**Rationale**: This tests the first causal step of EGSH: that scale drives depth reorganization of semantic representations. The d_50 metric is robust to argmax instability and directly operationalizes the "deeper semantic structure" claim.

**Variables**:
- Independent: Model scale (8B vs 70B base)
- Dependent: d_50 = layer index at which cumulative MI(h_l; y) reaches 50% of total MI, normalized by L
- Controlled: Probe architecture (2-layer MLP, 1024 hidden, 5-fold CV), JL-projection dimensionality matching

**Verification Protocol**:
1. Extract hidden states at all transformer layers for TriviaQA/NQ test queries (greedy decode) at both scales
2. Train 2-layer MLP probe (1024 hidden, ReLU, LR=1e-3, batch=256, 5-fold CV) per layer on binary correctness labels
3. Compute G_true(l) and G_perm(l) (permuted labels); derive G_corrected(l) = G_true - G_perm per layer
4. Compute cumulative MI profile from G_corrected; derive d_50 at both scales
5. Bootstrap CI (1000 resamples) on d_50 shift; apply JL-projection (70B→8B dim) and re-run as dimensionality control

**Success Criteria**:
- Primary: d_50_70B > d_50_8B with 95% bootstrap CI excluding zero on TriviaQA
- Secondary: Effect preserved under JL-projection dimensionality control; consistent on NQ

**Failure Response**:
- IF d_50 does not shift: EXPLORE — check if G_corrected peak pattern changes even without d_50 shift
- IF JL-projection eliminates effect: PIVOT — dimensionality artifact; reframe H-M1 around G_corrected peak only

**Dependencies**: H-E1

**Source**: Phase 2A causal step 1, prediction P3 (d_50 component)

---

**H-M2: Token-Probability Saturates While SE/KLE Gain Advantage**

**Statement**: Under Llama-3 base checkpoints, if scale increases from 8B to 70B, then token-probability AUROC does NOT improve at the same rate as SE/KLE AUROC — because lexical ambiguity compression at scale saturates vocabulary-level uncertainty signals while semantic aggregators (SE, KLE) capture the remaining equivalence-class uncertainty.

**Rationale**: This tests the second causal step: differential scaling of UQ signal quality. Asymmetric improvement (SE/KLE > token-prob improvement) is the key evidence that saturation is occurring, not uniform scaling.

**Variables**:
- Independent: UQ method paradigm × model scale
- Dependent: AUROC improvement from 8B to 70B per method (AUROC^70B - AUROC^8B)
- Controlled: Dataset splits, harness, sampling parameters; within-scale control (70B-instruct vs base)

**Verification Protocol**:
1. Compute AUROC for all methods at both scales from H-E1 experiment
2. Calculate per-method AUROC improvement: Δ_method = AUROC^70B - AUROC^8B for each method
3. Compare Δ_SE, Δ_KLE vs Δ_TP using bootstrap CI on difference of improvements
4. Apply within-scale control: repeat with Llama-3-70B-Instruct to separate scale vs RLHF effects
5. Compute two-way ANOVA (method × scale) on AUROC to test interaction term significance

**Success Criteria**:
- Primary: Δ_SE > Δ_TP and Δ_KLE > Δ_TP with 95% CI excluding zero (directional saturation)
- Secondary: 70B-Instruct shows smaller differential than 70B-Base (distinguishes scale from RLHF)

**Failure Response**:
- IF all methods improve equally: PIVOT — uniform scaling, not saturation; weaken mechanistic claim
- IF instruct shows same differential as base: EXPLORE — RLHF may co-drive the effect

**Dependencies**: H-M1

**Source**: Phase 2A causal step 2, prediction P1 (differential component), P2

---

**H-M3: Method×Scale AUROC Interaction Exceeds Pre-Registered Threshold**

**Statement**: Under Llama-3 base checkpoints on TriviaQA and NaturalQuestions, the method×scale AUROC interaction Δ = (AUROC_SE^70B - AUROC_TP^70B) - (AUROC_SE^8B - AUROC_TP^8B) > 0.02 with 95% bootstrap CI excluding zero — because the growing semantic-structure advantage at 70B manifests as a measurable interaction effect pre-registered at δ = 0.02.

**Rationale**: H-M3 is the primary quantitative test of EGSH. It operationalizes the interaction claim with a pre-registered threshold and requires cross-dataset consistency. This is the "gate" test whose outcome determines whether the EGSH interaction is scientifically credible.

**Variables**:
- Independent: UQ method paradigm × model scale
- Dependent: Δ = (AUROC_SE^70B - AUROC_TP^70B) - (AUROC_SE^8B - AUROC_TP^8B); pre-registered δ = 0.02
- Controlled: Identical splits, harness; TruthfulQA as scope boundary test (P4)

**Verification Protocol**:
1. Compute Δ for SE and KLE separately on TriviaQA and NQ full test splits from H-E1/H-M2 data
2. Bootstrap CI (1000 resamples) on Δ; test CI excludes zero AND Δ > 0.02 on both datasets
3. Repeat analysis with KLE as second confirmatory test of the interaction
4. Apply P4 scope test: compute Δ on TruthfulQA (817q, mc1_targets); compare to TriviaQA/NQ
5. Test two-way ANOVA interaction term (method × scale) for statistical significance

**Success Criteria**:
- Primary: Δ_SE > 0.02 with 95% bootstrap CI excluding zero on BOTH TriviaQA and NQ
- Secondary: Same criterion met for Δ_KLE; P4 shows Δ_TruthfulQA significantly < Δ_TriviaQA/NQ

**Failure Response**:
- IF Δ > 0 but < 0.02: EXPLORE — effect exists but below pre-registered threshold; report as suggestive
- IF CI includes zero: ABANDON — no significant interaction; H0 supported
- IF TruthfulQA shows same Δ as TriviaQA/NQ: SCOPE — effect is domain-general, not factual-retrieval specific

**Dependencies**: H-M2

**Source**: Phase 2A causal step 3, prediction P1 (primary), P4 (scope)

---

**H-M4: Permutation-Corrected Probe Gap Narrows at Deeper Layers at 70B**

**Statement**: Under Llama-3 base checkpoints, the permutation-corrected layer-wise probe gap G_corrected(l) narrows at 70B relative to 8B at deeper transformer layers, reflecting that epistemic uncertainty becomes more organizationally accessible with scale — because increased capacity enables correctness-predictive information to be more linearly decodable from deeper representations.

**Rationale**: H-M4 provides the internal representational evidence corroborating the external AUROC interaction (H-M3). Convergence of both external and internal diagnostics is required to support the structural reorganization claim of EGSH. G_corrected isolates epistemic accessibility from generic representational expressiveness via permutation calibration.

**Variables**:
- Independent: Model scale (8B vs 70B base)
- Dependent: G_corrected(l) = G_true(l) - G_perm(l) per transformer layer; peak layer shift
- Controlled: Fixed-capacity 2-layer MLP probes, 5-fold CV, JL-projection dimensionality matching

**Verification Protocol**:
1. From H-M1 probe training: compare G_corrected(l) profiles at 8B vs 70B layer-by-layer
2. Identify peak G_corrected layer at each scale; test if peak shifts deeper at 70B
3. Test G_corrected magnitude at deep layers: larger at 70B than 8B (increased epistemic accessibility)
4. Confirm effect under JL-projection (70B hidden dim → 8B dim) as dimensionality control
5. Compute SelfCheck-NLI vs SE partial correlation controlling for type-token ratio (P2 diagnostic)

**Success Criteria**:
- Primary: G_corrected peak shifts to deeper layers at 70B; effect preserved under JL-projection
- Secondary: G_corrected magnitude at deep layers (>70th percentile of layers) larger at 70B; P2 partial correlation increases from 8B to 70B for NLI scorer but not BERTScore

**Failure Response**:
- IF G_corrected does not narrow or shift: EXPLORE — check if effect is layer-range specific
- IF JL-projection eliminates effect: PIVOT — dimensionality artifact; report with caveat

**Dependencies**: H-M3

**Source**: Phase 2A causal step 4, prediction P3 (G_corrected component), P2

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | SE & KLE AUROC > token-prob at both 8B & 70B, CI excludes zero | STOP — semantic advantage absent; reassess EGSH |
| H-M1 | MUST_WORK | d_50_70B > d_50_8B with 95% CI excluding zero; preserved under JL-projection | EXPLORE layer-range specific effects; reframe around G_corrected peak |
| H-M2 | SHOULD_WORK | Δ_SE > Δ_TP and Δ_KLE > Δ_TP with 95% CI excluding zero | PIVOT — uniform scaling; weaken mechanistic claim; document as limitation |
| H-M3 | MUST_WORK | Δ_SE > 0.02 with 95% CI excluding zero on BOTH TriviaQA and NQ | ABANDON if CI includes zero; EXPLORE if 0 < Δ < 0.02 |
| H-M4 | SHOULD_WORK | G_corrected peak shifts deeper at 70B; preserved under JL-projection | EXPLORE layer-range specifics; report with caveat if JL-projection eliminates effect |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: 70B hidden state extraction compute | A3 (probe MI approximation) | H-M1, H-M4 | Critical |
| R2: Multiple comparison inflation | A2 (AUROC validity) | H-M3, H-M4 | High |
| R3: Training-data confound irreducibility | A1 (pretraining similarity) | H-M2, H-M3 | High |
| R4: KLE implementation unavailability | A2 (cross-method comparison) | H-E1, H-M2, H-M3 | Medium |
| R5: N=10 sample instability at 70B | A4 (N=10 sufficiency) | H-E1, H-M2, H-M3 | Medium |

### 4.2 Mitigation Strategies

**Risk R1: 70B Hidden State Extraction Compute (Critical)**

**Source Assumption:** A3 — Probe-based MI approximation captures relevant correctness-predictive signal

**Description:** Extracting all-layer hidden states for 17,944 TriviaQA + 3,610 NQ queries at 70B scale requires hundreds of GB GPU memory per batch. Computation time may exceed practical limits.

**Affected Hypotheses:** H-M1, H-M4

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** Use activation offloading (CPU offload via `accelerate`); process in batches of 64 queries; cache extracted hidden states to disk immediately after each batch
2. **Detection:** Run pilot extraction on 100 queries to estimate time/memory budget before full run
3. **Response:**
   - PIVOT: If full extraction infeasible, use random stratified subset of 1,000 queries per dataset (statistically adequate for d_50 estimation)
   - SCOPE: If only shallow layers feasible, restrict G_corrected analysis to first 50% of layers and note limitation

**Early Warning Indicators:**
- Pilot run exceeds 4 hours per 100 queries → switch to batch offloading
- GPU OOM on batch size 64 → reduce to 16

---

**Risk R2: Multiple Comparison Inflation (High)**

**Source Assumption:** A2 — AUROC validity as UQ quality proxy

**Description:** Testing 5 hypotheses with multiple metrics (AUROC, d_50, G_corrected, Δ) on 2–3 datasets without pre-specified correction inflates Type I error.

**Affected Hypotheses:** H-M3 (primary), H-M4 (secondary)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Pre-register primary tests (P1: Δ>0.02 CI excludes zero on TriviaQA+NQ; P3: d_50 shift CI excludes zero) before data collection
2. **Detection:** Track all statistical tests performed; flag any post-hoc tests added during analysis
3. **Response:**
   - PIVOT: Apply Holm correction to all secondary tests (P2, P4, G_corrected layer analysis)
   - SCOPE: Report primary pre-registered tests separately from exploratory secondary analyses

**Early Warning Indicators:**
- More than 10 statistical tests performed on same dataset → apply family-wise correction

---

**Risk R3: Training-Data Confound Irreducibility (High)**

**Source Assumption:** A1 — Llama-3 8B and 70B share sufficient pretraining data distribution similarity

**Description:** Observed method×scale interaction may reflect training-data volume or compute-budget differences rather than parameter count (capacity). This confound is irreducible given the two-point scale comparison.

**Affected Hypotheses:** H-M2, H-M3 (mechanistic interpretation)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Use base-model checkpoints only (eliminate RLHF confound); apply within-scale instruct control (70B-Base vs 70B-Instruct) to distinguish scale-driven from post-training effects
2. **Detection:** Compare 70B-Base vs 70B-Instruct Δ — large difference implicates RLHF, not scale
3. **Response:**
   - SCOPE: Explicitly frame all mechanistic claims as correlational, not causal; add "within Llama-3 family" qualifier throughout
   - PIVOT: If instruct shows same Δ as base, explore whether RLHF alone drives the effect

**Early Warning Indicators:**
- Δ_instruct ≈ Δ_base → training-data confound less likely; RLHF confound more prominent
- Δ_base >> Δ_instruct → base-model scale driving effect (consistent with hypothesis)

---

**Risk R4: KLE Implementation Unavailability (Medium)**

**Source Assumption:** A2 — cross-method AUROC comparison valid

**Description:** KLE (Nikitin et al. 2024) may not be integrated in UQLM or LM-Polygraph with Llama-3 support; custom integration may add weeks of engineering.

**Affected Hypotheses:** H-E1 (secondary), H-M2 (secondary), H-M3 (secondary)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Verify KLE availability in LM-Polygraph before experiment start (Week 0 check)
2. **Detection:** Attempt KLE integration on 50-query pilot; if fails after 3 days, escalate
3. **Response:**
   - SCOPE: If KLE unavailable, SE alone satisfies H-M3 primary criterion; KLE tests become secondary/deferred
   - PIVOT: Use LM-Polygraph's existing Mahalanobis Distance or p(True) as alternative 5th method

**Early Warning Indicators:**
- No LM-Polygraph PR for Llama-3 KLE within 1 week of search → scope to SE primary

---

**Risk R5: N=10 Sample Instability at 70B (Medium)**

**Source Assumption:** A4 — N=10 samples per query provides stable estimates

**Description:** At 70B scale, N=10 sampling costs 10× greedy inference. Budget constraints may force N<10, destabilizing SE/SelfCheckGPT AUROC estimates.

**Affected Hypotheses:** H-E1, H-M2, H-M3 (SE/SelfCheckGPT tests)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Run N=5 vs N=10 stability pilot on 500 random TriviaQA queries at 70B; confirm AUROC difference < 0.005
2. **Detection:** Monitor bootstrap CI width; if CI > 0.03 for AUROC, flag instability
3. **Response:**
   - SCOPE: If N=10 infeasible at 70B, use N=5 with explicit limitation note; bootstrap CI still valid
   - PIVOT: Prioritize SE at 70B over SelfCheckGPT-BERTScore/NLI (SE is higher-priority for H-M3)

**Early Warning Indicators:**
- Bootstrap CI width > 0.03 at N=10 on pilot → increase to N=20 for critical tests

### 4.3 Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | 70B hidden state extraction compute | A3 | Critical | H-M1, H-M4 | Activation offloading; batch processing; 1K-query fallback |
| R2 | Multiple comparison inflation | A2 | High | H-M3, H-M4 | Pre-register primary tests; Holm correction for secondary |
| R3 | Training-data confound irreducibility | A1 | High | H-M2, H-M3 | Base-model control; within-scale instruct comparison; correlational framing |
| R4 | KLE implementation unavailability | A2 | Medium | H-E1, H-M2, H-M3 | Verify LM-Polygraph Week 0; SE-only fallback for primary criterion |
| R5 | N=10 sample instability at 70B | A4 | Medium | H-E1, H-M2, H-M3 | N=5 stability pilot; bootstrap CI monitoring; N=5 fallback |

Critical Risks: 1 | High Risks: 2 | Medium Risks: 2 | Low Risks: 0

---

## 5. Dependency Graph & Timeline

### 5.1 DAG

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1  (EXISTENCE — no dependencies)
    Gate 1: MUST_WORK
         │
         ▼
[Level 1 - Mechanism Step 1]
    H-M1  (MECHANISM — Semantic depth shift d_50)
    ← H-E1
    Gate: MUST_WORK
         │
         ▼
[Level 2 - Mechanism Step 2]
    H-M2  (MECHANISM — Token-prob saturation vs SE/KLE)
    ← H-M1
    Gate: SHOULD_WORK
         │
         ▼
[Level 3 - Mechanism Step 3]
    H-M3  (MECHANISM — AUROC interaction Δ > 0.02)
    ← H-M2
    Gate: MUST_WORK (Primary quantitative test)
         │
         ▼
[Level 4 - Mechanism Step 4]
    H-M4  (MECHANISM — G_corrected probe gap narrows)
    ← H-M3
    Gate: SHOULD_WORK
         │
         ▼
[VERIFICATION COMPLETE]

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
| 3 | H-M3 | H-M2 | MUST_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2    │ W3-4    │ W5      │ W6      │ W7      │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation │         │         │         │         │         │
  H-E1 (Existence)  │ ████████│         │         │         │         │
  [Gate 1 ◆]        │        ◆│         │         │         │         │
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms │         │         │         │         │         │
  H-M1 (d_50 shift) │         │ ████████│         │         │         │
  H-M2 (saturation) │         │         │ ████    │         │         │
  H-M3 (Δ>0.02)     │         │         │         │ ████    │         │
  H-M4 (G_corrected)│         │         │         │         │ ████    │
  [Gate 2 ◆]        │         │         │         │         │        ◆│
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work  |  ◆ = Gate decision point
Total Duration: 7 weeks
Note: H-M2/M3/M4 share data from H-M1 extraction run (no re-inference needed)
═══════════════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1, compute-heavy) + 1 + 1 + 1 (H-M2/3/4, reuse data)

Slack Available: 0 weeks (fully sequential)

Key Observation: H-M2, H-M3, and H-M4 reuse the hidden state
extraction and AUROC computations from H-E1 and H-M1.
Wall-clock time dominated by H-M1 (70B hidden state extraction).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
  - Existence: 1 (H-E1)
  - Mechanism: 4 (H-M1 to H-M4)
  - Condition: 0 (none required)

Verification Phases: 2
  1. Foundation (H-E1): full test splits, N=10 sampling, 6 UQ methods
  2. Mechanisms (H-M1–4): layer-wise probes, hidden state extraction,
     AUROC interaction tests, scope boundary (TruthfulQA P4)

Datasets:
  - TriviaQA rc.nocontext test: 17,944 questions (primary)
  - NaturalQuestions open-domain test: 3,610 questions (primary)
  - TruthfulQA mc1_targets test: 817 questions (scope boundary P4)

Models:
  - Llama-3-8B-Base (meta-llama/Meta-Llama-3-8B)
  - Llama-3-70B-Base (meta-llama/Meta-Llama-3-70B)
  - Llama-3-70B-Instruct (within-scale control)

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential (data reuse across H-M2/3/4)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1–2
  - Generate N=10 samples + greedy decode for all test queries at 8B and 70B
  - Apply 6 UQ methods via UQLM; compute AUROC + bootstrap CI
  - Gate 1: SE/KLE AUROC > token-prob at both scales → PASS to Step 3

Step 2: Evaluate Gate 1
  - PASS → Proceed to H-M1
  - FAIL → STOP and reassess EGSH

Step 3: Execute H-M1 (d_50 depth shift) — Week 3–4
  - Extract all-layer hidden states at 8B and 70B (activation offloading)
  - Train 2-layer MLP probes per layer (5-fold CV); compute G_corrected(l)
  - Derive cumulative MI profile and d_50; bootstrap CI on shift
  - Apply JL-projection dimensionality control

Step 4: Execute H-M2 (token-prob saturation) — Week 5
  - Reuse AUROC values from H-E1; compute per-method improvement Δ_method
  - Apply within-scale control (70B-Instruct); run two-way ANOVA interaction test

Step 5: Execute H-M3 (AUROC interaction Δ>0.02) — Week 6
  - Compute Δ for SE and KLE; bootstrap CI; test against pre-registered δ=0.02
  - Run P4 scope test on TruthfulQA; compare Δ_TruthfulQA vs Δ_TriviaQA/NQ

Step 6: Execute H-M4 (G_corrected narrowing) — Week 7
  - Compare G_corrected(l) profiles at 8B vs 70B from H-M1 data
  - Compute P2 partial correlation (SelfCheck-NLI vs SE controlling for TTR)
  - Gate 2: H-M1 + H-M3 must pass → proceed to Phase 2C

Step 7: Evaluate Gate 2
  - PASS → Verification complete → proceed to Phase 2C experiment design
  - PARTIAL → Document limitations; proceed with supported hypotheses
  - FAIL (H-E1 or H-M3) → Reassess EGSH; route to Phase 2A revision
```

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

**Core Claim:** Semantic-structural UQ methods (SE, KLE) show a significantly larger AUROC advantage over token-probability at Llama-3-70B than at 8B base checkpoints on TriviaQA and NaturalQuestions, AND correctness-predictive information shifts to deeper transformer layers with scale — because larger capacity enables richer semantic equivalence class representations that surface-level token distributions cannot capture.

**Supporting Evidence:**
1. Causal mechanism: capacity enables depth-localized semantic equivalence class representations (analogous to vision transformer feature hierarchies)
2. Key assumptions A1-A5 all have targeted supporting evidence and mitigation strategies for violation
3. Four convergent predictions (P1-P4) with pre-registered quantitative thresholds (δ=0.02, 95% CI)

**Strengths:**
- Four independently falsifiable predictions with pre-registered thresholds — fully quantitative
- Convergent multi-diagnostic framework (external AUROC + internal MI depth + probe gap)
- G_corrected and d_50 are new methodological contributions in their own right
- All major confounds addressed: RLHF, dimensionality, generic expressiveness, output diversity

**Expected Outcomes:**
- Primary (P1): Δ_SE > 0.02 with CI excluding zero on TriviaQA AND NQ
- Secondary (P3): d_50_70B > d_50_8B with CI excluding zero; G_corrected narrows at 70B
- Scope test (P4): Δ_TruthfulQA significantly smaller than Δ_TriviaQA/NQ

### 6.2 Antithesis Development

**Null Hypothesis (H0):** There is no significant method×scale interaction: all UQ methods scale proportionally from 8B to 70B, preserving relative AUROC rankings. Token-probability, SE, and KLE all improve by similar Δ amounts; no depth shift occurs in MI profiles — because observed differences reflect training-data volume artifacts, not capacity-driven semantic reorganization.

**Counter-Arguments:**
1. Training-data confound: Llama-3-70B is trained on substantially more data; AUROC improvement may reflect data richness rather than architectural capacity
2. Dimensionality inflation: 70B hidden states have higher dimensionality, providing trivially better probe accuracy without JL-projection control
3. Output diversity inflation: larger models generate more lexically diverse outputs, inflating SE scores through larger equivalence classes, not better calibration

**Potential Failure Points:**
- R3 (High): Training-data confound materializes → interaction is observational artifact
- R1 (Critical): 70B hidden state extraction infeasible → H-M1/H-M4 cannot be tested
- R2 (High): Multiple comparison inflation → false positive on H-M3 interaction

**Conditions Under Which H0 Would Be Supported:**
- Δ ≤ 0.02 or CI includes zero on at least one dataset for both SE and KLE
- d_50 does not shift or shifts shallower at 70B; JL-projection eliminates G_corrected effect
- Token-prob shows equivalent Δ as SE/KLE → uniform scaling, not reorganization

### 6.3 Synthesis

**Balanced Assessment:**

The EGSH presents a testable, multi-diagnostic claim that epistemic uncertainty reorganizes from surface to deep representations as LLM scale increases. The null hypothesis raises valid concerns: the training-data confound is genuinely irreducible, and dimensionality/diversity inflation are real methodological risks. However, the antithesis cannot explain differential scaling between semantic-structural and token-based methods under a uniform training-data-volume account, and the convergent multi-diagnostic design specifically addresses each concern.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes semantic advantage existence before mechanism testing
2. **Sequential mechanism testing (H-M1–4):** Tests 4-step causal chain step-by-step with targeted controls at each step
3. **Explicit correlational framing:** All mechanistic claims scoped as correlational within-family, not causal — antithesis concern acknowledged in paper framing
4. **Convergence requirement:** All three diagnostic types must confirm for strong claim; partial confirmation (2-3) still scientifically valuable

**Conditions for Thesis Support:**
- H-E1 and H-M3 MUST_WORK gates pass (primary quantitative tests)
- d_50 shift confirmed (H-M1); G_corrected narrows (H-M4) — corroborating internal evidence

**Conditions for Antithesis Support:**
- H-E1 fails (SE/KLE advantage absent at both scales)
- H-M3 CI includes zero (no significant interaction)
- JL-projection eliminates d_50 shift (pure dimensionality artifact)

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M3 pass + d_50 shifts + G_corrected narrows → EGSH strongly validated
2. **Partial Support:** H-E1 + H-M3 pass but H-M1/H-M4 inconclusive → external AUROC interaction confirmed without internal mechanistic evidence; publishable with appropriate scoping
3. **Weak Support:** H-E1 passes, H-M3 Δ > 0 but < 0.02 → suggestive but below pre-registered threshold; report as exploratory
4. **No Support:** H-E1 or H-M3 fails → H0 supported; reassess EGSH

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence (H-E1) | SE/KLE > token-prob at both scales | SE advantage may disappear at one scale | Full test split (17,944 + 3,610q); bootstrap CI |
| Depth shift (H-M1) | d_50 deeper at 70B | Dimensionality inflation drives probe accuracy | JL-projection (70B→8B dim); permutation correction |
| Saturation (H-M2) | Token-prob improves slower than SE/KLE | Uniform training-data scaling | Within-scale instruct control; two-way ANOVA interaction |
| Interaction (H-M3) | Δ > 0.02, CI excludes zero | Training-data confound | Pre-registered threshold; base-model control; correlational framing |
| Probe gap (H-M4) | G_corrected narrows at 70B | Generic expressiveness inflation | Permutation-calibrated baseline per layer |
| Scope (P4) | Attenuation on TruthfulQA | Domain-general effect | TruthfulQA directional pre-registration |

**Overall Robustness Score:** High (convergent multi-diagnostic design with pre-registered thresholds)

**Confidence in Verification Plan:** 0.78 (from Phase 2A; consistent with synthesis assessment of 0.76)

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** EGSH — SE/KLE show larger AUROC advantage over token-prob at 70B vs 8B Llama-3 base, AND correctness-predictive information shifts to deeper layers with scale.
- ID: H-EGSH-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (60% scope reduction from Phase 2A BUILD_ON claims)
- Sub-Hypotheses: 5 total — H-E: 1, H-M: 4, H-C: 0
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (Gate 1: H-E1; Gate 2: H-M1+H-M3)

**Risk Assessment:** High (R1: 70B compute critical; R3: training-data confound high)
- Primary concerns: 70B hidden state extraction feasibility; irreducible training-data confound

**Immediate Action:** Begin Phase 1 with H-E1 (Week 0: verify KLE availability + run N=10 stability pilot)

### 7.2 Final Summary

**Key Achievements:**
- 5 hypotheses across 2 phases with convergent multi-diagnostic design
- H0 addressed: uniform scaling null directly falsifiable via pre-registered Δ>0.02 threshold
- All 5 confounds addressed with targeted controls (RLHF, dimensionality, diversity, expressiveness, argmax)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: SE/KLE AUROC > token-prob at both 8B and 70B base on TriviaQA+NQ full test splits
- Gate 1: MUST PASS — failure stops pipeline

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: d_50 depth shift (2 weeks, compute-heavy — 70B hidden state extraction)
- H-M2: Token-prob saturation differential (1 week, reuses H-E1/H-M1 data)
- H-M3: AUROC interaction Δ>0.02 on TriviaQA+NQ (1 week, primary gate)
- H-M4: G_corrected probe gap narrowing (1 week, reuses H-M1 probe data)
- Gate 2: H-M1 + H-M3 must pass

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess EGSH — no semantic advantage exists
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 AND H-M3 must pass
   - H-M1 FAIL → EXPLORE layer-range specifics; d_50 metric may need refinement
   - H-M3 FAIL (CI includes zero) → H0 supported; ABANDON mechanistic claim
   - H-M3 PASS but < 0.02 → EXPLORE; suggestive but below pre-registered threshold
   - H-M2, H-M4 FAIL → Document limitation; SHOULD_WORK gates allow partial confirmation

**Open Questions:**
- Exact computational budget for layer-wise MI/probe analysis at 70B scale (activation offloading needed)
- Whether KLE implementation is available in UQLM/LM-Polygraph with Llama-3 support
- Whether N=5 is sufficient for SE stability at 70B (N=10 stability pilot recommended in Week 0)

**Recommendations:**

1. **Immediate Actions (Week 0 pre-experiment):**
   - Verify KLE availability in LM-Polygraph; run 50-query pilot integration test
   - Run N=5 vs N=10 stability pilot on 500 TriviaQA queries at 70B
   - Estimate 70B hidden state extraction time on 100-query pilot batch

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path; build 1-week buffer for R1 (compute risk)
   - Plan CPU offload storage: ~100–200 GB disk for all-layer hidden states at 70B

3. **Failure Management:**
   - Pre-register all primary tests (P1, P3) before data collection begins
   - Document all intermediate results (AUROC at each scale) regardless of gate outcome

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/20260520_question/03_refinement.yaml (ID: H-EGSH-v1)
- Schema: Phase 2A-Dialogue v10.0.0; 16 discussion exchanges; all 6 convergence criteria met

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (3× scientificmethod for H-E1, H-M1/2, H-M3/4; 1× collaborativereasoning for risk analysis; 3× structuredargumentation for dialectical analysis)
- Tools: mcp__clearThought__scientificmethod (3×), mcp__clearThought__collaborativereasoning (1×), mcp__clearThought__structuredargumentation (3×)

**C. Scope Reduction Summary**
- Total Phase 2A claims: 7
- BUILD_ON (excluded from Phase 2B): 5 (SE outperforms token-prob, SelfCheckGPT, SEPs, KLE, RLHF confidence inflation)
- PROVE_NEW (Phase 2B targets): 2 (cross-paradigm interaction, depth reorganization)
- Scope reduction: 60% — only PROVE_NEW claims generate sub-hypotheses

---

*Generated by YouRA Phase 2B | 2026-05-20*
