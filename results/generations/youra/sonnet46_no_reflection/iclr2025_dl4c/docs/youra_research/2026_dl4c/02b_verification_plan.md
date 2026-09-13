---
hypothesis_id: H-StructuralEfficiency-v1
date: 2026-05-19
confidence: 0.78
total_hypotheses: 5
research_mode: incremental
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
completedAt: "2026-05-19T00:00:00Z"
---

# Verification Plan: Structural Efficiency of Policy Movement: Execution-RL vs DPO for Code Generation

**Date:** 2026-05-19
**Hypothesis ID:** H-StructuralEfficiency-v1
**Confidence:** 0.78
**Total Hypotheses:** 5

---

## 0. Established Facts & Scope Reduction

**Scope Reduction: 40%** — Four claims are BUILD_ON (established, no re-verification needed):

| Claim | Status | Evidence |
|-------|--------|----------|
| Execution-feedback RL outperforms SFT baseline on code generation benchmarks | BUILD_ON | CodeRL, PPOCoder, CoTran, TÜLU 3 |
| Binary pass/fail reward is inferior to variable-level execution trajectory | BUILD_ON | CodeRL+ +4.6% pass@1 improvement |
| TRL library unifies GRPO, DPO, and PPO trainers | BUILD_ON | huggingface/trl v1.3.0 |
| evalplus (HumanEval+/MBPP+) is standard evaluation harness | BUILD_ON | Used by Llama 3.1, TÜLU 3, DeepSeek-Coder, StarCoder2 |

**PROVE_NEW claims (Phase 2B-4 scope):**
1. No controlled RLHF/DPO vs execution-RL comparison under identical model+data+benchmark conditions
2. Execution-feedback RL induces higher structural efficiency (semantic AST edit distance per unit KL) than DPO

**Phase 2B-4 Instructions:** Only generate hypotheses for PROVE_NEW claims. Four established facts cited as prior work without re-verification.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under controlled post-training conditions (identical base model DeepSeek-Coder-7B, training data, and compute budget), if execution-feedback RL (GRPO with binary or error-type rewards) is applied instead of DPO, then execution-RL achieves higher structural efficiency of policy movement — measured as greater semantically-relevant AST edit distance per unit KL divergence from the base model — because execution reward directly penalizes functional incorrectness at the program level, forcing probability mass reallocation toward control-flow and data-flow transformations rather than surface-level stylistic changes.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in structural efficiency of policy movement (semantic AST edit distance per unit KL) between execution-RL and DPO at matched KL budgets; any pass@1 differences are fully explained by total KL or entropy differences alone, with no residual structural alignment effect.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval+ / MBPP+ / LiveCodeBench (standard) | Canonical function-level benchmarks used by all baselines; LiveCodeBench provides contamination-free OOD evaluation |
| **Model** | DeepSeek-Coder-7B-instruct | Open-weight SOTA code LLM, permissive license, 7B scale tractable for multi-condition fine-tuning |

**Dataset Details:**
- Source: evalplus (HumanEval+/MBPP+); LiveCodeBench official repo
- Path: evalplus/evalplus (pip install evalplus); livecodebench/livecodebench

**Model Details:**
- Type: Decoder-only transformer, code-specialized
- Source: deepseek-ai/deepseek-coder-7b-instruct-v1.5 (HuggingFace)

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| TÜLU 3 RLVR (Lambert et al., 2024) | ~60-65% HumanEval+ pass@1 (est. 7B scale) | HumanEval, MBPP (combined) |
| CodeRL+ binary RLVR (Jiang et al., 2025) | +4.6% pass@1 over binary baseline | HumanEval, MBPP |
| PPOCoder (Shojaee et al., 2023) | Significant gains over SFT | MBPP, CodeContests |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | KL divergence is valid budget for policy movement when normalized by semantic behavioral change | Standard RLHF practice; Monte Carlo estimation via token log-probabilities is established | Predictions 1,2,5 all depend on KL normalization — metric meaningless; mitigated by AST edit vs KL sanity plot |
| A2 | AST control-flow and data-flow edit distance is meaningful proxy for semantically relevant code transformation | Control-flow/data-flow edits directly determine program execution; surface edits do not | Structural efficiency metric conflates meaningful/meaningless changes; mitigated by pre-validating AST classifier on 50 held-out problems |
| A3 | Partial correctness density reflects latent structural scaffolding exploitable by fine-grained rewards | ReCode [Fan et al., 2025]; CodeRL+ variable-level gains suggest exploitable intermediate states | Prediction 4 granularity interaction loses mechanistic interpretation |
| A4 | DPO preference pairs generated via execution oracle constitute a fair comparison | Deterministic preference labels; eliminates human annotation noise | Results may not generalize to human-preference DPO |
| A5 | LiveCodeBench distribution shift is sufficient to test transfer generalization | Recent competitive programming problems (post-2023), contamination-free | R² threshold may be artificially inflated/deflated; mitigated by reporting Spearman rank correlation |

### 1.6 Research Gap & Novelty

First controlled comparison of execution-feedback RL vs DPO/RLHF under identical model+data+benchmark conditions (fills confirmed literature gap). First structural efficiency metric (semantic-edit-per-KL) for alignment training signal quality — reusable beyond code for any verifiable-reward post-training setting. Preference calibration gap as named failure mode with diagnostic protocol. Novelty confirmed: CodeRL+ compares variable-level vs binary within execution-RL (no DPO baseline); TÜLU 3 applies methods sequentially not as alternatives; RL Survey [Wang et al., 2024] explicitly notes absence of controlled comparison.

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
**H-E1: Existence of Structural Efficiency Differential**

**Statement**: Under controlled KL-matched conditions, if execution-feedback RL (GRPO) is applied instead of DPO on identical base model and data, then execution-RL exhibits ≥20% higher semantic-edit-per-KL than DPO, because execution reward forces probability mass toward control-flow and data-flow AST transformations.

**Rationale**: This is the foundational existence check. Before investigating the mechanism, we must empirically demonstrate that structural efficiency (AST edit distance ÷ KL) is actually higher for execution-RL than DPO. This validates the PROVE_NEW claim #1 and establishes the metric itself as meaningful.

**Variables** (from Phase 2A):
- Independent: Alignment method (SFT+DPO vs SFT+GRPO-binary, SFT+GRPO-error-type)
- Dependent: Semantic-edit-per-KL at KL-matched checkpoints (±5% tolerance)
- Controlled: Base model (DeepSeek-Coder-7B), training prompts, total training tokens, evaluation harness

**Verification Protocol**:
1. Train all alignment conditions (SFT-only, SFT+DPO, SFT+GRPO-binary, SFT+GRPO-error-type) with dense checkpoint saving
2. Compute per-checkpoint KL divergence (Monte Carlo, fixed held-out prompt set) and identify matched checkpoints (±5% tolerance)
3. Parse model outputs at matched checkpoints to compute AST semantic edit distance (zss library, control-flow + data-flow nodes only)
4. Compute semantic-edit-per-KL ratio and bootstrap 95% CI for execution-RL minus DPO differential
5. Evaluate gate: CI excludes zero AND magnitude ≥20%

**Success Criteria** (PoC):
- Primary: Bootstrap 95% CI for efficiency differential excludes zero and magnitude ≥20%
- Secondary: AST edit distance vs KL sanity plot shows positive correlation (validates KL as proxy)

**Failure Response**:
- IF fails: PIVOT — reduce threshold to directional (CI excludes zero, any magnitude) or investigate AST classifier validity

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 5 (sh1_existence) + Prediction P1

---
**H-M1: Program-Level Signal Forces Structural Reallocation**

**Statement**: Under controlled conditions, if execution reward directly signals functional incorrectness at program level, then the model reallocates probability mass toward control-flow and data-flow AST transformations (not surface edits), because program-level correctness objectives create gradient pressure specifically on execution-relevant code structures.

**Rationale**: H-M1 tests the first mechanistic step: does execution reward specifically target semantically relevant AST nodes? This distinguishes structural reallocation from general output distribution shift. It is the core causal link between execution reward and the structural efficiency differential found in H-E1.

**Variables**:
- Independent: Reward signal type (execution-RL vs DPO)
- Dependent: Proportion of AST edits in control-flow/data-flow nodes vs surface nodes
- Controlled: Same as H-E1; KL-matched checkpoints

**Verification Protocol**:
1. Decompose AST edits at matched checkpoints into: (a) control-flow nodes (if/for/while/try), (b) data-flow nodes (assignments, function calls, returns), (c) surface nodes (comments, whitespace, string literals, variable names)
2. Compute edit distribution proportions for execution-RL vs DPO
3. Test that execution-RL has significantly higher proportion of (a)+(b) edits vs DPO (Mann-Whitney U, p < 0.05)
4. Verify reward-correctness correlation during training (Spearman ρ between reward signal and pass@1 at each checkpoint)

**Success Criteria**:
- Primary: Execution-RL proportion of semantic (control-flow + data-flow) edits significantly higher than DPO (p < 0.05)
- Secondary: Reward-correctness Spearman ρ > 0.5 during training

**Failure Response**:
- IF fails: EXPLORE — check if AST decomposition taxonomy is too coarse; consider finer node classification

**Dependencies**: H-E1 (structural efficiency differential must be established first)

**Source**: Phase 2A Causal Step 1-2

---
**H-M2: Structural Reallocation Produces Higher Semantic-Edit-Per-KL**

**Statement**: Under controlled conditions, if probability mass reallocation toward control-flow and data-flow AST transformations occurs, then this produces measurably higher semantic-edit-per-KL (structural movement efficiency), because the same unit of policy divergence yields more semantically relevant behavioral change.

**Rationale**: H-M2 links the structural reallocation from H-M1 directly to the efficiency metric. It validates that the efficiency metric captures something real about the quality of policy movement, not just total quantity of change. This tests PROVE_NEW claim #2 at the metric level.

**Variables**:
- Independent: Proportion of semantic AST edits (from H-M1)
- Dependent: Semantic-edit-per-KL at matched checkpoints
- Controlled: KL budget, total training tokens

**Verification Protocol**:
1. Use H-M1 edit decomposition data to compute per-checkpoint semantic edit proportions
2. Compute correlation between semantic edit proportion and semantic-edit-per-KL across checkpoints
3. Run mixed-effects regression: semantic-edit-per-KL ~ semantic_proportion + KL + entropy + method + (1|problem)
4. Test that semantic_proportion coefficient is positive and significant (p < 0.05)

**Success Criteria**:
- Primary: Semantic proportion positively predicts semantic-edit-per-KL after KL and entropy controls (p < 0.05)
- Secondary: R² for regression ≥ 0.30

**Failure Response**:
- IF fails: EXPLORE — KL may not be the right normalization; consider entropy-normalized efficiency

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 3

---
**H-M3: Structural Efficiency Mediates Pass@1 and Calibration**

**Statement**: Under controlled conditions, if structural movement efficiency (semantic-edit-per-KL) is higher for execution-RL, then this mediates pass@1 gains in mixed-effects regression after controlling for total KL and entropy, and negatively correlates with Expected Calibration Error (ECE), because structurally efficient policy updates are functionally correct and calibrated rather than stylistically confident.

**Rationale**: H-M3 tests the critical mediational claim — the mechanism connecting structural efficiency to the outcomes researchers care about (correctness and calibration). This validates PROVE_NEW claim #2 at the outcome level and establishes semantic-edit-per-KL as a useful diagnostic, not just a descriptive metric.

**Variables**:
- Independent: Semantic-edit-per-KL (from H-E1/H-M2)
- Dependent: (a) Δpass@1, (b) ECE under entropy-matched conditions
- Controlled: Total KL, entropy, alignment method

**Verification Protocol**:
1. Run mixed-effects regression (Prediction P2): Δpass@1 ~ semantic-edit/KL + KL + entropy + method + (1|problem); test coefficient on semantic-edit/KL
2. Apply temperature scaling to equalize marginal entropy; compute Spearman ρ between problem-level semantic-edit/KL and problem-level ECE contribution (Prediction P3)
3. Run Sobel mediation test to confirm semantic-edit-per-KL as mediator for method → pass@1 effect
4. Evaluate both gates: P2 significant at p < 0.05 AND P3 ρ ≤ −0.3

**Success Criteria**:
- Primary (P2): Mixed-effects coefficient on semantic-edit/KL significant at p < 0.05 after KL/entropy controls; Sobel test confirms mediation
- Primary (P3): Spearman ρ ≤ −0.3 between structural efficiency and ECE under entropy-matched conditions (p < 0.05)

**Failure Response**:
- IF P2 fails but P3 holds: SCOPE — separate correctness mediation claim, retain calibration claim
- IF both fail: EXPLORE — examine whether effect is confounded by problem difficulty

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 4; Predictions P2, P3

---
**H-M4: Structural Efficiency Mediates OOD Transfer**

**Statement**: Under controlled conditions, if structural movement efficiency explains in-distribution gains, then problem-level structural efficiency on HumanEval+/MBPP+ predicts pass@1 on LiveCodeBench (OOD transfer), with R² ≥ 0.25, because models with higher structural efficiency have learned more generalizable control-flow and data-flow transformations.

**Rationale**: H-M4 tests the generalization implication of the structural efficiency mechanism. If structural efficiency truly reflects learning of generalizable code transformations (not benchmark-specific patterns), it should predict OOD performance. This is the strongest test of the causal claim and provides direct motivation for the metric as an alignment training diagnostic.

**Variables**:
- Independent: In-distribution structural efficiency (semantic-edit-per-KL on HumanEval+/MBPP+)
- Dependent: pass@1 on LiveCodeBench (OOD)
- Controlled: KL-matched checkpoints, model scale

**Verification Protocol**:
1. Evaluate all trained models on LiveCodeBench at KL-matched checkpoints (zero-shot)
2. Compute Spearman rank correlation between in-distribution semantic-edit-per-KL and LiveCodeBench pass@1 across methods and checkpoints
3. Run OLS regression: LiveCodeBench pass@1 ~ structural_efficiency + KL + method; compute R²
4. Evaluate gate: R² ≥ 0.25 AND Spearman ρ > 0 (p < 0.05)

**Success Criteria**:
- Primary: R² ≥ 0.25 for LiveCodeBench pass@1 predicted by in-distribution structural efficiency
- Secondary: Spearman rank correlation positive and significant (p < 0.05)

**Failure Response**:
- IF fails: SCOPE — OOD transfer may require larger KL budget; report as negative result with mechanistic explanation

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4; Prediction P5 (from 02_synthesis.yaml measurement plan)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Bootstrap 95% CI excludes zero AND ≥20% efficiency differential | STOP — reassess hypothesis |
| H-M1 | MUST_WORK | Execution-RL semantic edit proportion significantly higher (p < 0.05) | PIVOT — revisit AST taxonomy |
| H-M2 | SHOULD_WORK | Semantic proportion positively predicts efficiency (p < 0.05) | EXPLORE — alternative normalization |
| H-M3 | SHOULD_WORK | P2: mediation significant; P3: ρ ≤ −0.3 | SCOPE — separate claims if partial |
| H-M4 | SHOULD_WORK | R² ≥ 0.25 for OOD prediction | SCOPE — report as negative result |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (1+1+1+1+gate) |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: KL invalidity as policy movement proxy | A1 | H-E1, H-M2, H-M4 | High |
| R2: AST classifier conflates semantic/surface edits | A2 | H-E1, H-M1, H-M2 | High |
| R3: Partial correctness density not exploitable | A3 | H-M3 (granularity sub-claim) | Medium |
| R4: Execution-oracle DPO unrepresentative | A4 | H-E1, H-M1 (generalizability) | Medium |
| R5: LiveCodeBench distribution too extreme | A5 | H-M4 | Low |

### 4.2 Mitigation Strategies

**Risk R1: KL invalidity**
- Prevention: Plot AST edit distance vs KL across all checkpoints before main analysis; require positive Spearman ρ as sanity check
- Detection: If sanity plot shows flat or negative relationship, KL proxy is invalid
- Response: PIVOT to entropy-normalized efficiency or absolute AST edit distance (not per-KL)

**Risk R2: AST classifier taxonomy**
- Prevention: Pre-validate AST classifier on 50 held-out problems with manual annotation before main analysis
- Detection: Inter-rater agreement < 0.8 or classifier assigns >30% of stylistic changes to semantic category
- Response: Refine taxonomy; add validation category for borderline nodes (e.g., variable renaming that changes semantics)

**Risk R3: Partial correctness not exploitable**
- Prevention: Check Jaccard stability distribution of training problems before granularity sub-experiment
- Detection: <10% of problems in high-stability tertile
- Response: SCOPE — skip granularity interaction (P4); retain other predictions

**Risk R4: Execution-oracle DPO unrepresentative**
- Prevention: Explicitly specify DPO pair construction protocol in paper methods section; run sensitivity check with temperature-varied sampling for pair diversity
- Detection: DPO with oracle pairs performs atypically vs published DPO results
- Response: Report as controlled variant; add ablation note distinguishing oracle-DPO from human-preference DPO

**Risk R5: LiveCodeBench too extreme**
- Prevention: Report Spearman rank correlation alongside R²; verify base pass@1 rates are non-trivial (>5%)
- Detection: Mean pass@1 on LiveCodeBench < 5% or > 80% for all methods
- Response: Include hard-bin subset of LiveCodeBench; report effect sizes with appropriate caveats

### 4.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | KL invalidity as proxy | A1 | High | H-E1,H-M2,H-M4 | AST vs KL sanity plot pre-analysis |
| R2 | AST classifier conflation | A2 | High | H-E1,H-M1,H-M2 | Pre-validate on 50 held-out problems |
| R3 | Partial correctness unexploitable | A3 | Medium | H-M3 | Check Jaccard stability distribution |
| R4 | Oracle DPO unrepresentative | A4 | Medium | H-E1,H-M1 | Sensitivity check + explicit protocol |
| R5 | LiveCodeBench too extreme | A5 | Low | H-M4 | Spearman ρ + base rate check |

Critical: 0 | High: 2 | Medium: 2 | Low: 1

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root / Foundation]
    H-E1  (EXISTENCE — no dependencies)
    Gate: MUST_WORK
         │
         ▼
[Level 1 - Core Mechanism / Structural Reallocation]
    H-M1  (MECHANISM — program-level signal → AST reallocation)
    Gate: MUST_WORK
         │
         ▼
[Level 2 - Metric Validation]
    H-M2  (MECHANISM — structural reallocation → higher efficiency metric)
    Gate: SHOULD_WORK
         │
         ▼
[Level 3 - Outcome Mediation]
    H-M3  (MECHANISM — efficiency mediates pass@1 + calibration)
    Gate: SHOULD_WORK
         │
         ▼
[Level 4 - Generalization]
    H-M4  (MECHANISM — efficiency predicts OOD transfer)
    Gate: SHOULD_WORK

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
| 3 | H-M3 | H-M2 | SHOULD_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │ W7
─────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  [Gate 1]       │        ◆│         │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼────────
PHASE 2: Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │         │ ████    │
  H-M4           │         │         │         │         │ ████
  [Gate 2]       │         │        ◆│         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼────────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

- Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
- Total Duration: 7 weeks (2 + 2 + 1 + 1 + 1)
- Slack Available: 0 weeks (all sequential)
- Formula: 2 (H-E1) + 4 (H-M1-4, first=2 weeks, rest=1 week each) = 7 weeks

### 5.5 Resource Summary

- Total Hypotheses: 5 (H-E1: 1, H-M1-4: 4, H-C: 0)
- Verification Phases: 2
- Total Duration: 7 weeks
- Execution Mode: Sequential chain
- Execution Order: H-E1 → Gate 1 → H-M1 → H-M2 → H-M3 → H-M4 → Gate 2

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Execution-feedback RL (GRPO) achieves higher structural efficiency of policy movement than DPO under controlled conditions, and this structural efficiency mediates improvements in functional correctness, calibration, and OOD transfer.

**Supporting Evidence:**
1. CodeRL [Le et al., 2022], PPOCoder [Shojaee et al., 2023]: unit-test feedback provides accurate functional correctness signal — empirical foundation for causal step 1
2. CodeRL+ [Jiang et al., 2025]: variable-level trajectory shows +4.6% over binary reward — suggests model learns to modify semantically relevant structures (indirect evidence for step 2)
3. Objective mismatch theory: DPO optimizes log-probability ratios between preference pairs, which may increase confidence in stylistically plausible but functionally incorrect outputs ("preference calibration gap") — theoretical grounding

**Strengths:**
- Clear causal mechanism with 4 sequential steps, each independently falsifiable
- Novel metric (semantic-edit-per-KL) that operationalizes the theoretical claim measurably
- 5 pre-registered quantitative predictions with explicit failure criteria make the hypothesis reviewer-proof
- Controlled experimental design eliminates confounds (same model, data, compute budget)

**Expected Outcomes:**
- P1: ≥20% higher semantic-edit-per-KL for execution-RL at KL-matched checkpoints
- P2: semantic-edit-per-KL mediates pass@1 in mixed-effects regression
- P3: structural efficiency negatively correlates with ECE (ρ ≤ −0.3)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in structural efficiency of policy movement between execution-RL and DPO at matched KL budgets; any pass@1 differences are fully explained by total KL or entropy differences alone.

**Counter-Arguments:**
1. KL divergence is token-level and local; functional correctness is program-level and global — the normalization may be meaningless (A1 violation risk)
2. DPO with execution-oracle pairs is a strong baseline — oracle-derived preference labels may already pressure semantic code structures
3. The 20% threshold for efficiency differential is arbitrary and may not be practically significant — smaller effects could still be real

**Potential Failure Points:**
- R1: KL invalidity invalidates the metric entirely (affects H-E1, H-M2, H-M4)
- R2: AST classifier conflates surface/semantic changes, inflating apparent execution-RL advantage
- Phase 2A key tension: "KL divergence is token-level and local; functional correctness is program-level and global. Whether token-level KL is a valid budget for program-level behavioral change requires empirical validation."

**Conditions Under Which H0 Would Be Supported:**
- Bootstrap 95% CI for efficiency differential includes zero (P1 fails)
- Mixed-effects coefficient on semantic-edit/KL is non-significant after KL/entropy controls (P2 fails)
- Structural efficiency and ECE are uncorrelated (P3 fails)

### 6.3 Synthesis

The hypothesis H-StructuralEfficiency-v1 presents a testable and theoretically grounded claim about the mechanistic advantage of execution-feedback RL over DPO. The thesis is supported by established literature on execution-RL benefits and a clear causal chain. The null hypothesis raises valid concerns about the KL normalization and the representativeness of oracle-based DPO.

**Resolution Path:** The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Pre-analysis AST-vs-KL sanity plot validates KL as proxy before committing to the metric
2. **Sequential mechanism testing (H-M1-M4):** Tests each causal link independently — early failure stops costly later experiments
3. **Gate conditions:** MUST_WORK gates at H-E1 and H-M1 ensure the foundation is solid before investing in outcome claims

**Conditions for Thesis Support:**
- H-E1 gate passes (existence demonstrated)
- H-M1 gate passes (structural reallocation mechanism confirmed)
- H-M3 provides mediation evidence (P2 or P3 significant)

**Conditions for Antithesis Support:**
- H-E1 fails: CI includes zero → fundamental metric is invalid or effect doesn't exist
- H-M1 fails: No structural reallocation → mechanism doesn't operate as theorized
- Both P2 and P3 fail in H-M3 → structural efficiency is epiphenomenal to pass@1 and calibration

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 + H-M1 + H-M3 all pass → thesis validated for paper
2. **Partial Support:** H-E1 + H-M1 pass but H-M3/H-M4 mixed → metric is real but mediation incomplete → refined thesis with scope limitations
3. **No Support:** H-E1 or H-M1 fail → H0 supported → route to Phase 0 for new direction

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Metric validity | Semantic-edit-per-KL captures structural alignment | KL is token-level, not program-level | Pre-analysis sanity plot; entropy alternative |
| Mechanism specificity | Execution-RL specifically targets semantic AST nodes | Oracle DPO also targets semantic code | H-M1 AST decomposition test |
| Outcome mediation | Structural efficiency mediates correctness/calibration | Effect explained by total KL or entropy | Mixed-effects regression + Sobel mediation test |
| Generalization | Structural efficiency predicts OOD transfer | Distribution shift too extreme or too mild | Spearman ρ + base rate checks |

**Overall Robustness Score:** Medium-High (theoretically grounded, pre-analysis validation steps address main risks)

**Confidence in Verification Plan:** 0.78

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-StructuralEfficiency-v1 — Execution-RL achieves higher structural efficiency (semantic-edit-per-KL ≥20%) than DPO under controlled conditions, mediating correctness, calibration, and OOD transfer.
- ID: H-StructuralEfficiency-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (40% scope reduction from 4 BUILD_ON established facts)
- Sub-Hypotheses: 5 total (H-E1: existence, H-M1-M4: mechanism chain)
- Phases: 2 phases over 7 weeks
- Critical Gates: Gate 1 (H-E1, MUST_WORK) + Gate 2 (H-M1, MUST_WORK)

**Risk Assessment:** Medium
- Primary concerns: (1) KL invalidity as proxy — addressed by pre-analysis sanity plot; (2) AST classifier taxonomy — addressed by 50-problem pre-validation

**Immediate Action:** Begin Phase 1 with H-E1 (requires: training all 5 conditions, dense checkpoint saving, AST classifier pre-validation)

### 7.2 Conclusions

**Key Achievements:**
- 5 hypotheses structured across 2 verification phases
- H0 explicitly addressed: no structural efficiency difference (effect explained by KL/entropy alone)
- Scope reduced by 40% by treating 4 established facts as BUILD_ON (not re-verified)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Execution-RL achieves ≥20% higher semantic-edit-per-KL than DPO at KL-matched checkpoints
- Gate 1: MUST PASS — if fails, STOP and reassess hypothesis

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Program-level signal forces probability mass toward semantic AST nodes
- H-M2: Structural reallocation produces higher semantic-edit-per-KL metric
- H-M3: Structural efficiency mediates pass@1 (P2) and ECE calibration (P3)
- H-M4: In-distribution structural efficiency predicts LiveCodeBench OOD transfer (R² ≥ 0.25)
- Gate 2: H-M1 must pass; H-M2-M4 failures narrow scope but don't invalidate

**Critical Decision Points:**
1. **Gate 1 (Foundation):** H-E1 must demonstrate structural efficiency differential → FAIL = STOP
2. **Gate 2 (Mechanism Core):** H-M1 must confirm structural reallocation mechanism → CRITICAL FAIL = execute PIVOT strategy
3. **Partial Outcomes (H-M2-M4):** Individual failures narrow scope but pipeline continues to Phase 5

**Open Questions:**
- What threshold of semantic-edit-per-KL predicts practical performance gains? (threshold calibration needed pre-registration)
- Does structural efficiency advantage hold for DeepSeek-Coder-1.3B (smaller scale) and 13B (larger scale)?
- Is the preference calibration gap observed for execution-oracle DPO, human-annotated DPO, or both?

**Recommendations:**
1. **Immediate Actions:** Pre-validate AST semantic-edit classifier on 50 held-out problems; verify 20% and R²=0.25 thresholds against effect size back-calculation from CodeRL+/PPOCoder before pre-registration
2. **Resource Allocation:** 7 weeks critical path; reserve 1-week buffer for AST classifier pre-validation delays; dense checkpoint saving requires additional disk storage (~50-100GB)
3. **Failure Management:** Document all gate failures with detailed metrics; execute PIVOT strategies for H-M1; SCOPE reductions for H-M2-M4; write Serena memory on significant failures

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-StructuralEfficiency-v1, schema v10.0.0)
- Supplementary: 02_synthesis.yaml (measurement plan, 5 predictions)
- Discussion: 15 exchanges, 6 agents, 12 citations, convergence at exchange 15

**B. MCP Tool Usage Summary**
- MCP calls: 3 (ClearThought scientificmethod ×1, collaborativereasoning ×1, structuredargumentation ×1)
- Mode: Incremental (4-6 calls target met)

---

*Generated by YouRA Phase 2B (v6.0) | 2026-05-19*
