# Verification Plan: Structural Enumeration Preference in RLHF-Trained Reward Models

**Date:** 2026-03-24
**Hypothesis ID:** H-EnumPref-v1
**Confidence:** 0.78
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under conditions where RLHF-trained reward models (Bradley-Terry, scalar regression, or MoE objectives) are evaluated on response pairs that differ only in structural presentation, if responses enumerate multiple options (vs. synthesize into single recommendation), then reward scores will be significantly higher for enumerated responses (Cohen's d >= 0.3), because RLHF training encodes human raters' implicit preference for option enumeration as a high-detectability structural feature that signals epistemic navigability.

### 1.2 Alternative Hypothesis (H0)
Under strict controls for correctness, completeness, and response length, there is no significant difference in reward model scores between enumerated and synthesized responses (pooled |d| < 0.1 across ≥3 architecturally distinct RMs).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Custom Agency-Structure Stimulus Set v2 (custom) | Precise control over structure manipulation while maintaining content quality. Based on Attempt 2 methodology with enhanced controls. |
| **Model** | Multi-RM Evaluation Suite | Four architecturally distinct RMs spanning Bradley-Terry, scalar regression, and multi-objective training objectives. Enables cross-model replication. |

**Dataset Details:**
- Source: LLM-generated with human validation
- Path: generated during Phase 4

**Model Details:**
- Type: reward_model_ensemble
- Source: HuggingFace
- Models: RLHFlow/ArmoRM-Llama3-8B-v0.1, openbmb/UltraRM-13b, berkeley-nest/Starling-RM-7B-alpha, llm-blender/PairRM

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| MRMBench multi-dimensional probing | Correlates with downstream LLM alignment | Custom preference probing tasks |
| HumanAgencyBench 6-dimension evaluation | Low-to-moderate agency support in current LLMs | LLM-generated test scenarios |
| ArmoRM multi-objective scoring | 89.0 on RewardBench overall | HelpSteer-derived preferences |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Enumeration can be reliably operationalized via deterministic regex classifier | Standard NLP pattern matching; will validate with >95% human agreement | Effect could be artifact of inconsistent enumeration detection |
| A2 | Human raters' enumeration preference transferred to reward models during training | Standard RLHF learning dynamics; high-signal features are amplified | Would require alternative explanation for observed d=0.634 |
| A3 | Correctness and completeness manipulations are orthogonal (do not cross-contaminate) | Will validate via pre-RM human ratings with |d| < 0.2 cross-contamination | Interaction effects would be uninterpretable |
| A4 | Publicly available RMs (ArmoRM, UltraRM, Starling, PairRM) are representative of RLHF training | All trained on human preference data with standard objectives | Results may not generalize to proprietary models |
| A5 | Training data statistics (enumeration log-odds) are accessible for at least 2/4 models | HelpSteer and UltraFeedback datasets are public | Imprinting analysis limited; mechanism pathway weakened |

### 1.6 Research Gap & Novelty

**Research Gap:** No prior work has conducted rigorous behavioral probing for structural (non-content) preferences in reward models. Existing benchmarks (MRMBench, RewardBench) focus on content dimensions like helpfulness and harmlessness, while HumanAgencyBench evaluates LLM outputs rather than reward model preferences.

**Novelty:** First rigorous behavioral probe for structural preferences in RMs. Bridges RM interpretability literature (MRMBench) with human agency frameworks (HumanAgencyBench). Demonstrates methodology for isolating formatting priors from competence signals.

**Differentiation:**
- vs. MRMBench: Probes structural dimensions, not content dimensions
- vs. HumanAgencyBench: Probes RM preferences, not LLM outputs
- vs. RewardBench: Probes for specific structural biases, not RM accuracy

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | SHOULD_WORK | H-E1 | PENDING |
| H-M2 | Mechanism | SHOULD_WORK | H-E1 | PENDING |
| H-M3 | Mechanism | SHOULD_WORK | H-M1, H-M2 | PENDING |

---

### 2.2 Hypothesis Specifications

#### H-E1: Cross-Model Enumeration Preference Replication

**Statement:** Under controlled conditions (matched length, correctness, completeness), if RLHF-trained reward models evaluate enumerated vs. synthesized response pairs, then enumerated responses will receive significantly higher scores (d >= 0.3) across multiple architecturally distinct RMs, because enumeration is an independently encoded structural feature.

**Rationale:** This existence hypothesis validates that the observed enumeration preference (d=0.634 in ArmoRM) is not model-specific but reflects a robust, replicable pattern across RLHF-trained reward models. Cross-model replication is essential before investigating mechanism.

**Variables:**
- Independent: Response structure (enumerated vs. synthesized)
- Dependent: Reward model score (normalized 0-1)
- Controlled: Response length (±2%), correctness, completeness, prompt domain

**Verification Protocol:**
1. Generate 600 stimulus pairs (2×2×2 factorial: Structure × Correctness × Completeness)
2. Validate orthogonality via human ratings (require |d| < 0.2 cross-contamination)
3. Query all 4 RMs (ArmoRM, UltraRM, Starling-RM, PairRM) on complete stimulus set
4. Compute per-RM effect sizes with 95% confidence intervals
5. Test pooled effect against null threshold (d >= 0.3 vs. |d| < 0.1)

**Success Criteria (PoC):**
- Primary: Cohen's d >= 0.3 for structure main effect in ≥2 architecturally distinct RMs
- Secondary: ≥75% (3/4) RMs show positive enumeration effect (d > 0)

**Failure Response:**
- IF fails: ABANDON main hypothesis (H0 confirmed: no robust structural preference)

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1, Prediction P1

---

#### H-M1: Training Data Imprinting Analysis

**Statement:** Under analysis of RLHF training datasets, if enumerated responses are overrepresented in chosen (preferred) vs. rejected pairs, then log-odds ratio will be significantly positive, because human raters systematically prefer responses that enumerate options.

**Rationale:** This mechanism hypothesis tests the first causal step: whether the enumeration preference originates from human rater behavior in training data. Distributional evidence supports the imprinting pathway.

**Variables:**
- Independent: Response pairing (chosen vs. rejected in training data)
- Dependent: Enumeration log-odds ratio
- Controlled: Dataset source (HelpSteer, UltraFeedback)

**Verification Protocol:**
1. Apply pre-registered regex enumeration classifier to training datasets
2. Compute enumeration frequency in chosen vs. rejected responses
3. Calculate log-odds ratio with confidence intervals
4. Test against neutral baseline (log-odds ≈ 0)

**Success Criteria (PoC):**
- Primary: Log-odds ratio > 0 with 95% CI excluding zero in ≥1 dataset
- Secondary: Direction consistency across available datasets

**Failure Response:**
- IF fails: EXPLORE alternative pathway (effect may not require distributional imprinting)

**Dependencies:** H-E1 (existence must be confirmed first)

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Spurious Enumeration Control

**Statement:** Under comparison of true enumeration vs. spurious enumeration (markers without structural decomposition), if the effect is structural encoding rather than token bias, then spurious enumeration will show <30% of true enumeration's effect size, because reward models encode structural coherence not mere surface tokens.

**Rationale:** This mechanism hypothesis distinguishes genuine structural preference from superficial token bias. If spurious enumeration retains most of the effect, the preference is surface-level, not semantic.

**Variables:**
- Independent: Enumeration type (true vs. spurious vs. prose baseline)
- Dependent: Reward model score
- Controlled: Content, length, all other structural features

**Verification Protocol:**
1. Generate spurious enumeration variants (numeric markers without logical decomposition)
2. Create matched triplets: true enumeration, spurious enumeration, prose baseline
3. Query RMs on all triplets
4. Compute effect sizes: true vs. prose, spurious vs. prose
5. Calculate retention ratio: (spurious effect) / (true effect)

**Success Criteria (PoC):**
- Primary: Spurious enumeration retains <30% of true enumeration's effect relative to prose
- Secondary: True enumeration effect remains significant vs. prose baseline

**Failure Response:**
- IF fails: PIVOT to token-bias interpretation (structural encoding hypothesis weakened)

**Dependencies:** H-E1 (existence must be confirmed first)

**Source:** Phase 2A Prediction P3

---

#### H-M3: Structure-vs-Semantics Dissociation

**Statement:** Under comparison of numeric enumeration (structure only) vs. deliberative prose (semantics only), if enumeration preference is structural rather than semantic, then numeric lists without deliberative language will produce significant reward boost (d >= 0.2), because the structural signal is separable from deliberative content.

**Rationale:** This mechanism hypothesis tests whether enumeration structure and deliberative semantics are separable contributors to the preference. Dissociation evidence strengthens the structural encoding interpretation.

**Variables:**
- Independent: Response format (numeric enumeration vs. deliberative prose)
- Dependent: Reward model score
- Controlled: Content quality, length, factual accuracy

**Verification Protocol:**
1. Generate numeric-only enumerations (lists without explanatory deliberation)
2. Generate deliberative prose versions (reasoning without enumeration markers)
3. Query RMs on both formats with matched content
4. Compute effect size: numeric enumeration vs. deliberative prose
5. Test for dissociation: significant effect for structure independent of semantics

**Success Criteria (PoC):**
- Primary: Numeric-only enumeration shows d >= 0.2 vs. prose baseline
- Secondary: Effect persists when deliberative language is removed

**Failure Response:**
- IF fails: EXPLORE semantic-structure interaction (effect may require both components)

**Dependencies:** H-M1, H-M2 (training data and spurious control should inform interpretation)

**Source:** Phase 2A Prediction P4, Causal Steps 3-4

---

## 2.3 Risk Analysis

### Risk-Hypothesis Mapping

| Risk | Source | Description | Affected | Severity |
|------|--------|-------------|----------|----------|
| R1 | A1 | Enumeration classifier unreliable | H-E1, H-M1, H-M2 | High |
| R2 | A2 | Preference not transferred during training | H-M1 | Medium |
| R3 | A3 | Correctness/completeness cross-contamination | H-E1 | High |
| R4 | A4 | Public RMs not representative | H-E1, H-M2, H-M3 | Medium |
| R5 | A5 | Training data inaccessible | H-M1 | Low |

### Mitigation Strategies

**R1: Enumeration Classifier Reliability (High)**
- **Prevention:** Pre-register regex classifier with explicit rules; validate on held-out sample
- **Detection:** Compute inter-rater agreement (require >95% with human labels)
- **Response:** If <90% agreement, refine classifier before proceeding; document edge cases

**R2: Training Transfer Uncertainty (Medium)**
- **Prevention:** Use multiple RMs with different training objectives to isolate training effects
- **Detection:** Check cross-model consistency; if only 1 RM shows effect, training-specific
- **Response:** EXPLORE alternative pathway; effect may emerge from architecture not training data

**R3: Manipulation Cross-Contamination (High)**
- **Prevention:** Human validation pilot (n=100) before RM evaluation; require |d| < 0.2
- **Detection:** Check correctness ratings don't correlate with completeness manipulations
- **Response:** If contaminated, redesign stimulus generation; may need to drop one manipulation

**R4: Public RM Representativeness (Medium)**
- **Prevention:** Select architecturally diverse RMs (Bradley-Terry, scalar, MoE)
- **Detection:** Compare effect sizes across architectures; look for outliers
- **Response:** Document limitations for proprietary models; note generalization bounds

**R5: Training Data Access (Low)**
- **Prevention:** Focus on HelpSteer and UltraFeedback (confirmed public)
- **Detection:** Early check of data availability before H-M1 implementation
- **Response:** If only 1 dataset available, proceed with reduced scope; mechanism still testable

### Prior Failure Pattern Integration

From Phase 0 documented failures:

| Prior Failure | Lesson | Applied Mitigation |
|---------------|--------|-------------------|
| Attempt 1: Corpus comparison (d=0.016) | Lexical markers alone insufficient | Focus on RM behavioral probing, not corpus statistics |
| Attempt 2: Composite agency (d=0.131) | Factors cancel when aggregated | Isolate single factor (enumeration only) |

### Risk Summary

| Severity | Count | Risks |
|----------|-------|-------|
| High | 2 | R1 (Classifier), R3 (Cross-contamination) |
| Medium | 2 | R2 (Transfer), R4 (Representativeness) |
| Low | 1 | R5 (Data access) |

**Critical Path Risks:** R1 and R3 must be mitigated before H-E1 execution. Human validation pilot is MANDATORY.

---

## 3. Execution

### 3.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════════
                    DEPENDENCY GRAPH - 4 Hypotheses
═══════════════════════════════════════════════════════════════════════

[Level 0 - Foundation]                 GATE 1: MUST_WORK
                                       ┌─────────────────┐
                                       │      H-E1       │
                                       │   (Existence)   │
                                       │  Cross-Model    │
                                       │  Replication    │
                                       └────────┬────────┘
                                                │
                         ┌──────────────────────┼──────────────────────┐
                         │                      │                      │
                         ▼                      ▼                      │
[Level 1 - Mechanism]          GATE 2: SHOULD_WORK (parallel)         │
              ┌─────────────────┐    ┌─────────────────┐              │
              │      H-M1       │    │      H-M2       │              │
              │ Training Data   │    │    Spurious     │              │
              │   Imprinting    │    │    Control      │              │
              └────────┬────────┘    └────────┬────────┘              │
                       │                      │                        │
                       └──────────┬───────────┘                        │
                                  │                                    │
                                  ▼                                    │
[Level 2 - Integration]               GATE 3: SHOULD_WORK             │
                        ┌─────────────────┐                           │
                        │      H-M3       │ ◄─────────────────────────┘
                        │  Structure vs   │   (also depends on H-E1)
                        │   Semantics     │
                        │  Dissociation   │
                        └─────────────────┘

═══════════════════════════════════════════════════════════════════════
Critical Path: H-E1 → [H-M1 ∥ H-M2] → H-M3
Parallelization: H-M1 and H-M2 can execute simultaneously after H-E1
═══════════════════════════════════════════════════════════════════════
```

### 3.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Parallelizable |
|-------|-----------|---------------|-----------|----------------|
| 0 | H-E1 | None | MUST_WORK | N/A (root) |
| 1 | H-M1 | H-E1 | SHOULD_WORK | Yes (with H-M2) |
| 1 | H-M2 | H-E1 | SHOULD_WORK | Yes (with H-M1) |
| 2 | H-M3 | H-M1, H-M2 | SHOULD_WORK | No (convergence) |

### 3.3 Verification Phases with Gates

**Phase 1 - Foundation (MUST_WORK)**

| Hypothesis | Test | Pass Condition | Fail Action |
|------------|------|----------------|-------------|
| H-E1 | Cross-model enumeration preference | d >= 0.3 in ≥2 RMs | ABANDON |

→ **Gate 1**: If H-E1 fails → STOP entire pipeline (H0 confirmed)

**Phase 2 - Mechanism Exploration (SHOULD_WORK, Parallel)**

| Hypothesis | Test | Pass Condition | Fail Action |
|------------|------|----------------|-------------|
| H-M1 | Training data imprinting | Log-odds > 0 | EXPLORE alternative |
| H-M2 | Spurious enumeration control | Retention <30% | PIVOT interpretation |

→ **Gate 2**: Both inform H-M3 interpretation. Neither blocks continuation.

**Phase 3 - Integration (SHOULD_WORK)**

| Hypothesis | Test | Pass Condition | Fail Action |
|------------|------|----------------|-------------|
| H-M3 | Structure-semantics dissociation | d >= 0.2 numeric-only | EXPLORE interaction |

→ **Gate 3**: Failure narrows claims but doesn't invalidate existence finding.

### 3.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
                    VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ Day 1-2 │ Day 3-4 │ Day 5-6 │ Day 7-8 │
─────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation  │         │         │         │         │
  H-E1 (Existence)   │ ████████│ ████████│         │         │
  [Gate 1] ◆         │         │       ◆ │         │         │
─────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanism   │         │         │         │         │
  H-M1 (Imprinting)  │         │         │ ████████│         │  ← Parallel
  H-M2 (Spurious)    │         │         │ ████████│         │  ← Parallel
  [Gate 2] ◆         │         │         │       ◆ │         │
─────────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 3: Integration │         │         │         │         │
  H-M3 (Dissociate)  │         │         │         │ ████████│
  [Gate 3] ◆         │         │         │         │       ◆ │
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5-8 days (with parallel execution)
═══════════════════════════════════════════════════════════════════════════════
```

### 3.5 Critical Path Analysis

**Critical Path:** H-E1 → [H-M1 ∥ H-M2] → H-M3

| Metric | Value |
|--------|-------|
| Total Hypotheses | 4 |
| Sequential Steps | 3 (Foundation → Mechanism → Integration) |
| Parallel Opportunities | H-M1 and H-M2 execute simultaneously |
| Critical Path Duration | 5-8 days |
| Slack | 0 days (all on critical path) |

### 3.6 Execution Order

1. **Day 1-2:** Execute H-E1 (Cross-model replication)
2. **Day 2 (end):** Evaluate Gate 1 → If d >= 0.3 in ≥2 RMs, proceed
3. **Day 3-6:** Execute H-M1 and H-M2 in parallel
   - H-M1: Training data log-odds analysis
   - H-M2: Spurious enumeration control comparison
4. **Day 6 (end):** Evaluate Gate 2 → Inform H-M3 interpretation
5. **Day 7-8:** Execute H-M3 (Structure-semantics dissociation)
6. **Day 8 (end):** Evaluate Gate 3 → Determine claim scope

### 3.7 Resource Summary

| Resource | Allocation |
|----------|------------|
| Total Hypotheses | 4 |
| Existence Tests | 1 (H-E1) |
| Mechanism Tests | 3 (H-M1, H-M2, H-M3) |
| Condition Tests | 0 |
| Verification Phases | 3 |
| Estimated Duration | 5-8 days |
| GPU Requirements | Single GPU per RM evaluation |
| Data Requirements | 600 stimulus pairs, 2 training datasets |

---

## 4. Dialectical Analysis

### 4.1 Thesis

**Core Claim:** RLHF-trained reward models exhibit a robust, replicable structural preference for enumerated responses (d >= 0.3) that reflects independently encoded formatting features, not competence proxies.

**Supporting Evidence:**
1. Prior observation shows d=0.634 for enumeration in ArmoRM (n=512, p<0.00001)
2. Enumeration markers are high-detectability structural features providing stable gradients
3. Human raters systematically prefer responses presenting multiple options
4. Effect expected to replicate across architecturally distinct RMs

**Strengths:**
- Strong prior effect size (d=0.634) exceeds conventional thresholds
- Clear causal mechanism with testable intermediate steps
- Pre-registered classifier eliminates researcher degrees of freedom
- Cross-model replication design addresses single-model artifact concern

### 4.2 Antithesis (H0)

**Null Hypothesis:** Under strict controls for correctness, completeness, and response length, there is no significant difference in reward model scores between enumerated and synthesized responses (pooled |d| < 0.1 across ≥3 architecturally distinct RMs).

**Counter-Arguments:**
1. Observed effect may be confounded by uncontrolled competence signals
2. Enumeration might proxy for thoroughness or quality
3. Effect may be specific to ArmoRM's MoE architecture
4. RLHF training may encode diverse preferences that cancel out

**Conditions Under Which H0 Would Be Supported:**
- H-E1 fails: d < 0.3 across all tested RMs
- Spurious enumeration retains ≥70% of effect (token bias)
- Effect disappears under completeness controls (competence proxy)

### 4.3 Synthesis

**Balanced Assessment:**
The hypothesis H-EnumPref-v1 presents a testable claim that RLHF-trained RMs encode structural enumeration preference as an independent feature. However, the null hypothesis raises valid concerns regarding competence confounds and single-model generalization.

**Resolution Path:**
The verification plan addresses this dialectic through:
1. **H-E1 (Cross-model replication):** Tests existence across 4 architecturally distinct RMs
2. **H-M2 (Spurious control):** Distinguishes token bias from structural coherence
3. **2×2×2 factorial:** Isolates structure from correctness/completeness confounds
4. **Gate conditions:** Allow early detection of H0 support

**Outcome Possibilities:**

| Outcome | Conditions | Interpretation |
|---------|------------|----------------|
| **Full Support** | All hypotheses pass | Structural encoding validated |
| **Partial Support** | H-E1 passes, some H-M fail | Effect exists but mechanism unclear |
| **No Support** | H-E1 fails | H0 confirmed, no robust preference |

### 4.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | d=0.634 observed | May be artifact | H-E1 cross-model replication |
| Mechanism | Structural encoding | Competence proxy | H-M2 spurious control |
| Scope | Applies to RLHF RMs | Model-specific | 4 architectures tested |
| Controls | Enhanced from prior | May be insufficient | 2×2×2 factorial + human validation |

**Overall Robustness Score:** High

**Confidence in Verification Plan:** 0.85

**Rationale:** The plan directly addresses all antithesis concerns through experimental design. The spurious enumeration control (H-M2) is particularly valuable as a diagnostic. Gate conditions prevent sunk-cost continuation after critical failures.

---

## 5. Summary & Conclusions

### 5.1 Executive Summary

This verification plan decomposes the main hypothesis (H-EnumPref-v1) into 4 testable sub-hypotheses:
- **H-E1:** Cross-model replication of enumeration preference (MUST_WORK gate)
- **H-M1:** Training data imprinting analysis (SHOULD_WORK)
- **H-M2:** Spurious enumeration control (SHOULD_WORK)
- **H-M3:** Structure-semantics dissociation (SHOULD_WORK)

**Key Metrics:**
- Total Duration: 5-8 days
- Parallel Opportunities: H-M1 and H-M2
- Critical Path: H-E1 → [H-M1 ∥ H-M2] → H-M3
- Scope Reduction: 37.5% (BUILD_ON claims excluded)

### 5.2 Decision Points

| Gate | Hypothesis | Decision |
|------|------------|----------|
| Gate 1 | H-E1 | If d < 0.3 in all RMs → ABANDON |
| Gate 2 | H-M1, H-M2 | Inform interpretation; neither blocks |
| Gate 3 | H-M3 | If fails → narrow structural claims |

### 5.3 Success Criteria Summary

| Criterion | Threshold | Status |
|-----------|-----------|--------|
| Cross-model replication | d >= 0.3 in ≥2 RMs | Required |
| Direction consistency | ≥75% (3/4) RMs positive | Required |
| Spurious enumeration | <30% retention | Required for structural interpretation |
| Structure-semantics | d >= 0.2 numeric-only | Desired |

### 5.4 Open Questions

From Phase 2A discussion:
- Does enumeration preference moderate by domain (high-autonomy vs. low-autonomy prompts)?
- Can training data log-odds quantitatively predict downstream effect size?
- Does token-masking ablation reveal token-level vs. distributed structural encoding?

### 5.5 Recommendations

**Immediate Actions:**
- Start Phase 2C with H-E1 experiment design
- Set up RM inference infrastructure (4 models on HuggingFace)
- Prepare stimulus generation pipeline

**Risk Mitigation:**
- Conduct human validation pilot (n=100) before H-E1
- Pre-register enumeration classifier with explicit regex rules
- Document all failure cases for Serena memory

### 5.6 Next Steps

1. **Phase 2C:** Generate detailed experiment specifications for H-E1
2. **Phase 3:** Implementation planning with PRD/Architecture
3. **Phase 4:** Code implementation and PoC validation
4. **Phase 5:** Baseline comparison (if applicable)

---

## Appendices

### A. Phase 2A Reference

- **Source File:** `03_refinement.yaml`
- **Hypothesis ID:** H-EnumPref-v1
- **Confidence:** 0.78
- **Schema Version:** v10.0.0 (Free-Parse)

### B. MCP Tool Usage Summary

| Tool | Calls | Purpose |
|------|-------|---------|
| `scientificmethod` | 3 | H-E1 verification, mechanism chain, experiment design |
| `structuredargumentation` | 3 | Thesis, antithesis, synthesis |
| `rag_search_knowledge_base` | 1 | Past failure case search |

### C. Established Facts (BUILD_ON - Not Re-Tested)

| Claim | Evidence |
|-------|----------|
| d=0.634 for enumeration in ArmoRM | Attempt 2 per-factor analysis (n=512) |
| Composite agency factors cancel out | Enumeration +0.634, Transfer -0.374, Deference +0.061 |
| ArmoRM uses MoE aggregation | RLHFlow documentation |

---

*Generated by YouRA Phase 2B v6.0 | 2026-03-24*
