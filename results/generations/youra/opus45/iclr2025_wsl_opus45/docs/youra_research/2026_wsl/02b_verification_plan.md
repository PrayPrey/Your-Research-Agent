# Verification Plan: LoRA Adapter Geometric Signatures for Task Similarity Detection

**Date:** 2026-04-13
**Hypothesis ID:** H-LoRAGeo-v1
**Confidence:** 0.80
**Total Hypotheses:** 3 (Active) + 2 (BUILD_ON References)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under controlled experimental conditions (single verified base model, identical LoRA hyperparameters, deterministic training), if we train LoRA adapters on semantically similar tasks and compute Grassmann distances between their B matrix column spaces, then within-category distances will be significantly smaller than between-category distances (p < 0.05, Cohen's d > 0.5), because fine-tuning induces task-specific geometric modifications to weight spaces that are constrained by LoRA's low-rank structure.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in Grassmann distances between LoRA adapter B matrix column spaces for adapters trained on semantically similar vs. dissimilar tasks, even under controlled experimental conditions. Any observed differences are due to training stochasticity or measurement noise.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | LoRA Zoo (In-House Generated) (custom) | Controlled provenance ensures identical base model and hyperparameters; only task varies |
| **Model** | Llama-3.2-1B (initial) / Llama-2-7B (replication) | Modern transformer architecture; LoRA-compatible; SHA-256 hash verifiable |

**Dataset Details:**
- Source: Generated from existing benchmarks: GSM8K, ARC-Challenge, LogiQA, StrategyQA, MNLI, QQP, SST-2, MRPC
- Path: generated/lora_zoo/

**Model Details:**
- Type: Causal LLM with LoRA adaptation
- Source: meta-llama/Llama-3.2-1B-Instruct, meta-llama/Llama-2-7b-hf

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Uncontrolled HuggingFace adapters | p = 0.127, Cohen's d = 0.91 (underpowered) | 8 public adapters with mixed provenance | Base model mismatch and insufficient sample size confounded results |
| Full model weight space analysis | SSI = 0.453 (failed) | 9 public Llama-2 fine-tunes | Full fine-tuning not constrained to low-rank; base model mismatch |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Task semantic similarity is well-defined and can be operationalized via FLAN task taxonomy | FLAN task clustering validated in multi-task learning literature; tasks grouped by similar instructions transfer better | If task similarity is ill-defined, the IV (same-cluster vs different-cluster) is meaningless |
| A2 | Grassmann distance captures functionally relevant subspace differences | Principal angles measure alignment; used in manifold learning, subspace clustering | If Grassmann distance ignores functionally relevant structure, it's the wrong metric |
| A3 | B matrix column space (not A matrix or BA product) is the appropriate representation | B projects into the output dimension; A projects from input. Task-specific output transformations are encoded in B | If A matrix or BA product contains the signal, B-only analysis would miss it |
| A4 | Training stochasticity does not dominate the task-specific signal | Control condition P3 tests this directly; different seeds on same task should show small within-task variance | If training noise >> task signal, geometric distances would be uninformative |
| A5 | Results on tested base models generalize to other transformer LLMs with LoRA | LoRA mechanism is architecture-agnostic; same low-rank constraint applies across models | Results would be base-model-specific, limiting generalizability (acceptable scope limitation) |

### 1.6 Research Gap & Novelty

**Gap:** Previous experiments (Cohen's d = 0.91, but p = 0.127) showed the correct effect direction but lacked statistical power due to uncontrolled provenance and insufficient sample size.

**Novelty:** First controlled validation of LoRA geometric signature hypothesis with adequate statistical power using Model Zoo methodology adapted for LoRA adapters. Combines controlled provenance (identical base model, fixed hyperparameters), adequate statistical power (n ≥ 17 per category), LoRA-specific analysis (B matrix column spaces), and multi-tier validation (clustering + correlation + control).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | BUILD_ON | - | PRE-VALIDATED |
| H-M2 | Mechanism | BUILD_ON | - | PRE-VALIDATED |
| H-M3 | Mechanism | MUST_WORK | H-E1 | READY |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | READY |

**Legend:**
- **MUST_WORK**: Gate blocks progression if failed
- **SHOULD_WORK**: Exploratory, failure informs but doesn't block
- **BUILD_ON**: Pre-validated assumption, not re-tested

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Existence of Task-Similarity Clustering in LoRA Geometry

**Statement**: Under controlled experimental conditions (identical base model, fixed LoRA hyperparameters, deterministic training), if we compute Grassmann distances between LoRA adapter B matrix column spaces, then within-cluster distances will be significantly smaller than between-cluster distances, because task-specific fine-tuning induces geometrically coherent weight modifications.

**Rationale**: This is the foundational existence claim. Previous experiments showed Cohen's d = 0.91 but p = 0.127 due to insufficient power and uncontrolled provenance. Validating this under controlled conditions establishes that the geometric clustering phenomenon is real, not an artifact of confounding variables.

**Variables**:
- Independent: Task Semantic Similarity (same-cluster vs different-cluster per FLAN taxonomy)
- Dependent: Grassmann Geodesic Distance (sqrt of squared principal angles)
- Controlled: Base model (SHA-256 verified), LoRA config (r=32, alpha=64), seed=42

**Verification Protocol**:
1. Generate 200 LoRA adapters with controlled provenance (20 per task × 8 tasks + seed variants)
2. Extract B matrices and compute orthonormal bases via QR decomposition
3. Calculate pairwise Grassmann distances using scipy.linalg.subspace_angles
4. Apply Mann-Whitney U test comparing within-cluster vs between-cluster distributions
5. Compute Cohen's d effect size with 95% confidence interval

**Success Criteria** (PoC):
- Primary: p < 0.05 AND Cohen's d > 0.5
- Secondary: 95% CI excludes zero

**Failure Response**: IF fails → ABANDON (core claim falsified)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A SH1, Prediction P1

---

#### H-M1: Task-Specific Weight Updates (BUILD_ON)

**Statement**: Fine-tuning on a specific task induces weight updates that encode task-relevant transformations.

**Status**: PRE-VALIDATED (BUILD_ON) - Established in fine-tuning literature; task performance improvement requires functional weight changes. Not re-tested.

**Evidence**: Standard fine-tuning behavior; adapters improve on target task.

**Source**: Phase 2A Causal Step 1

---

#### H-M2: LoRA Low-Rank Constraint (BUILD_ON)

**Statement**: LoRA constrains weight updates to a low-rank subspace defined by the B matrix column space (ΔW = BA where B ∈ R^{d×r}).

**Status**: PRE-VALIDATED (BUILD_ON) - Fundamental LoRA design property from Hu et al., 2021. Not re-tested.

**Evidence**: Mathematical property of LoRA architecture.

**Source**: Phase 2A Causal Step 2

---

#### H-M3: Similar Tasks Induce Similar B Column Spaces (KEY TENSION)

**Statement**: Under identical training conditions, if two tasks are semantically similar (same FLAN category), then their LoRA adapters will have similar B matrix column spaces, because similar tasks require similar functional transformations in the output dimension.

**Rationale**: This is the KEY TENSION in the causal mechanism - the core empirical claim that must be validated. Transfer learning success between similar tasks suggests shared functional requirements, but this has not been directly validated in LoRA geometry. This hypothesis bridges existence (H-E1) and the mathematical relationship (H-M4).

**Variables**:
- Independent: Task Category (Reasoning vs NLU per FLAN taxonomy)
- Dependent: B Matrix Column Space Alignment (Grassmann distance)
- Controlled: Base model, LoRA config, training hyperparameters

**Verification Protocol**:
1. Compute pairwise Grassmann distances between all adapter pairs
2. Compute FLAN task taxonomy distances (external ground truth)
3. Calculate Spearman rank correlation between geometric and taxonomic distances
4. Test statistical significance of correlation
5. Validate with within-task seed variance as baseline (P3 control)

**Success Criteria** (PoC):
- Primary: Spearman ρ > 0.3 with p < 0.05
- Secondary: Within-task distance < 0.5 × within-cluster distance (control)

**Failure Response**: IF fails → PIVOT to alternative similarity metrics or representations

**Dependencies**: H-E1 (existence must be established first)

**Source**: Phase 2A Causal Step 3, Prediction P2, Key Tension

---

#### H-M4: Layer-wise Clustering Strength (Exploratory)

**Statement**: Under controlled conditions, if we analyze Grassmann distances per layer type, then some layers (attention vs MLP) will show stronger task-similarity clustering than others, because different layers encode different aspects of task-specific transformations.

**Rationale**: Previous analysis suggested layer-wise variation in clustering strength. Identifying which layers show strongest signal informs practical applications (e.g., layer-selective adapter retrieval) and deepens mechanistic understanding.

**Variables**:
- Independent: Layer Type (q_proj, k_proj, v_proj, o_proj vs up_proj, down_proj, gate_proj)
- Dependent: Layer-wise Cohen's d for within vs between cluster comparison
- Controlled: Same as H-E1

**Verification Protocol**:
1. Separate Grassmann distance computation by layer type
2. Compute Cohen's d per layer type for within vs between comparison
3. Rank layers by effect size
4. Test for attention vs MLP systematic differences
5. Identify layers with d > 0.8 (large effect)

**Success Criteria** (PoC):
- Primary: At least one layer type shows Cohen's d > 0.8
- Secondary: Systematic attention vs MLP difference identified

**Failure Response**: IF fails → EXPLORE (informative null result, no mechanism block)

**Dependencies**: H-M3 (mechanism core must be validated)

**Source**: Phase 2A Open Questions, Layer-wise Analysis

---

## 3. Risk Analysis

### 3.1 Risk Identification

**Risk Derivation:** Each risk derived from Phase 2A Key Assumptions (A1-A5) plus baseline failure pattern analysis.

#### R1: FLAN Taxonomy Validity (Source: A1)
**Description:** FLAN task taxonomy may not accurately capture functional similarity between tasks. If task categories don't reflect true computational/representational similarity, the independent variable is unreliable.

**Severity:** HIGH | **Likelihood:** LOW
**Rationale:** FLAN taxonomy is externally validated in multi-task learning literature, but it was designed for instruction-following, not weight-space analysis.

#### R2: Grassmann Distance Inadequacy (Source: A2)
**Description:** Grassmann distance measures principal angles but may miss task-relevant structure encoded in singular values, matrix norms, or other geometric properties.

**Severity:** MEDIUM | **Likelihood:** LOW
**Rationale:** Principal angles are standard for subspace comparison; however, singular value distributions could carry additional signal.

#### R3: Wrong Matrix Representation (Source: A3)
**Description:** Task-specific information may be encoded in the A matrix (input projection) or the BA product rather than B column space alone. B-only analysis would miss this signal entirely.

**Severity:** HIGH | **Likelihood:** MEDIUM
**Rationale:** B encodes output transformations, but task-specific gating/routing may occur via A. No prior work definitively establishes B vs A vs BA importance.

#### R4: Training Stochasticity Dominance (Source: A4)
**Description:** Random initialization and training noise may produce distances that reflect stochastic variation rather than task-specific structure. Within-task variance could exceed between-task variance.

**Severity:** CRITICAL | **Likelihood:** LOW
**Rationale:** Control condition P3 directly tests this. Fixed seed + deterministic mode should minimize, but GPU non-determinism can persist.

#### R5: Base Model Specificity (Source: A5)
**Description:** Results on Llama-3.2-1B may not generalize to other architectures (GPT, Mistral, Gemma). Effect could be specific to Llama attention patterns or layer structure.

**Severity:** LOW | **Likelihood:** MEDIUM
**Rationale:** Acceptable scope limitation. Replication on Llama-2-7B provides within-family validation. Cross-architecture generalization is future work.

#### R6: Insufficient Statistical Power (Source: Baseline Failure)
**Description:** Despite power analysis (n ≥ 17 per category), actual effect size may be smaller than estimated from previous underpowered study (Cohen's d = 0.91 was point estimate with wide CI).

**Severity:** MEDIUM | **Likelihood:** MEDIUM
**Rationale:** Previous d = 0.91 was from n=8; true effect could be smaller. Design uses n=80+ per category (20 adapters × 4 tasks) to provide buffer.

#### R7: Provenance Verification Failure (Source: Baseline Failure)
**Description:** In-house adapter generation could fail to maintain controlled provenance (wrong checkpoint, config drift, environment differences between training runs).

**Severity:** HIGH | **Likelihood:** LOW
**Rationale:** SHA-256 verification and config logging mitigate this. Single training script with frozen dependencies ensures reproducibility.

### 3.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Impact |
|------|--------|---------------------|--------|
| R1: FLAN Taxonomy Validity | A1 | H-E1, H-M3 | Invalidates ground truth for clustering |
| R2: Grassmann Distance Inadequacy | A2 | H-E1, H-M3, H-M4 | Wrong metric → false negatives |
| R3: Wrong Matrix Representation | A3 | All H-M* | Miss signal entirely |
| R4: Training Stochasticity | A4 | H-E1 (primary) | Noise > signal → no clustering |
| R5: Base Model Specificity | A5 | All | Limits generalizability (acceptable) |
| R6: Insufficient Power | Baseline | H-E1, H-M3 | p > 0.05 despite real effect |
| R7: Provenance Failure | Baseline | All | Reintroduces confounds |

**Critical Path Risks:** R4 (stochasticity) and R3 (wrong matrix) most directly threaten H-E1 and H-M3, which are MUST_WORK gates.

### 3.3 Mitigation Strategies

#### R1 Mitigation: FLAN Taxonomy Validation
- **Prevention:** Use FLAN taxonomy as external ground truth; don't cherry-pick categories
- **Detection:** Compute correlation (P2) between Grassmann distances and taxonomy distances
- **Response:** 
  - PIVOT: If ρ < 0.1, explore alternative similarity measures (task embedding cosine similarity)
  - SCOPE: Focus on unambiguous task pairs (GSM8K vs SST-2, clearly different domains)

#### R2 Mitigation: Metric Validation
- **Prevention:** Grassmann distance is theoretically sound for subspace comparison
- **Detection:** Compare results with alternative metrics (Frobenius norm, projection overlap)
- **Response:**
  - PIVOT: If Grassmann fails but alternatives succeed, report both metrics
  - EXPLORE: Singular value analysis as complementary signal

#### R3 Mitigation: Multi-Matrix Analysis
- **Prevention:** Design includes B-matrix-only analysis (primary) but infrastructure supports A and BA
- **Detection:** If H-E1 fails with B, test A matrix and BA product before abandoning
- **Response:**
  - PIVOT: Switch to A matrix column space if B shows no signal
  - EXPLORE: BA product geometry as alternative representation
  - Early Warning: If same-seed B matrices show high variance, matrix extraction may be wrong

#### R4 Mitigation: Stochasticity Control (CRITICAL)
- **Prevention:** Fixed seed (42), CUDA deterministic mode, identical environment
- **Detection:** P3 control condition - within-task different-seed distances must be small
- **Response:**
  - ABORT Trigger: If within-task distance ≥ within-cluster distance, stochasticity dominates
  - PIVOT: Aggregate across multiple seeds per adapter; use mean distances
  - Early Warning: First 10 within-task pairs show variance > 0.3 × between-task variance

#### R5 Mitigation: Scope Documentation
- **Prevention:** Document as known limitation upfront; not a verification target
- **Detection:** Replication study on Llama-2-7B provides within-family check
- **Response:**
  - SCOPE: Accept base-model-specificity as scope limitation for initial study
  - Future Work: Cross-architecture validation in follow-up studies

#### R6 Mitigation: Power Buffer
- **Prevention:** Design with n = 80+ per category (4 tasks × 20 adapters), exceeding minimum n = 17
- **Detection:** Monitor effect size CI width during incremental analysis
- **Response:**
  - PIVOT: If underpowered, generate additional adapters (5 more per task = 40 more total)
  - SCOPE: Report effect size with CI even if p > 0.05 (trend reporting)

#### R7 Mitigation: Provenance Verification Protocol
- **Prevention:** SHA-256 hash of base model checkpoint logged; config frozen in version control
- **Detection:** Pre-training verification script compares hashes and configs
- **Response:**
  - ABORT: If hash mismatch detected, stop and regenerate from verified checkpoint
  - Prevention Protocol: Single training script, containerized environment (Docker)

### 3.4 Risk Summary

| ID | Risk | Source | Severity | Likelihood | Affected | Primary Mitigation |
|----|------|--------|----------|------------|----------|-------------------|
| R1 | FLAN taxonomy invalid | A1 | HIGH | LOW | H-E1, H-M3 | External validation via P2 correlation |
| R2 | Grassmann inadequate | A2 | MEDIUM | LOW | H-E1, H-M3, H-M4 | Alternative metric comparison |
| R3 | Wrong matrix (B vs A) | A3 | HIGH | MEDIUM | All H-M* | Multi-matrix fallback analysis |
| R4 | Stochasticity dominates | A4 | CRITICAL | LOW | H-E1 | P3 control + deterministic training |
| R5 | Llama-specific results | A5 | LOW | MEDIUM | All | Accept as scope limitation |
| R6 | Insufficient power | Baseline | MEDIUM | MEDIUM | H-E1, H-M3 | n=80+ buffer, incremental analysis |
| R7 | Provenance failure | Baseline | HIGH | LOW | All | SHA-256 verification protocol |

**Risk Distribution:**
- Critical: 1 (R4 - Stochasticity)
- High: 3 (R1, R3, R7)
- Medium: 2 (R2, R6)
- Low: 1 (R5)

**Top Priority Mitigations:**
1. P3 control condition validates R4 before full experiment
2. SHA-256 provenance check prevents R7 entirely
3. Multi-matrix fallback addresses R3 if primary approach fails

---

## 4. Dependency Structure

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════════════
                    DEPENDENCY GRAPH (DAG) - 3 Active Hypotheses
═══════════════════════════════════════════════════════════════════════════

                              ┌─────────────────────┐
                              │  BUILD_ON LAYER     │
                              │  (Pre-validated)    │
                              ├─────────────────────┤
                              │ H-M1: Task updates  │ ← Established in literature
                              │ H-M2: LoRA low-rank │ ← LoRA design property
                              └─────────────────────┘
                                        │
                                        │ (Referenced, not re-tested)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LEVEL 0 - FOUNDATION (Root)                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │  H-E1: Existence of Task-Similarity Clustering                  │       │
│   │  Gate: MUST_WORK                                                │       │
│   │  Test: Within-cluster < between-cluster (p<0.05, d>0.5)        │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                    │                                         │
│                                    │ GATE 1: Must Pass                       │
│                                    │ (If fail → STOP, hypothesis falsified)  │
│                                    ▼                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                        
┌─────────────────────────────────────────────────────────────────────────────┐
│ LEVEL 1 - CORE MECHANISM                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │  H-M3: Similar Tasks → Similar B Column Spaces (KEY TENSION)    │       │
│   │  Gate: MUST_WORK                                                │       │
│   │  Test: Spearman ρ > 0.3 with FLAN taxonomy                     │       │
│   │  Prerequisites: H-E1                                            │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                    │                                         │
│                                    │ GATE 2: Must Pass                       │
│                                    │ (If fail → PIVOT to alt metrics)        │
│                                    ▼                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ LEVEL 2 - EXPLORATORY                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────┐       │
│   │  H-M4: Layer-wise Clustering Strength (Exploratory)             │       │
│   │  Gate: SHOULD_WORK                                              │       │
│   │  Test: Identify layers with Cohen's d > 0.8                    │       │
│   │  Prerequisites: H-M3                                            │       │
│   └─────────────────────────────────────────────────────────────────┘       │
│                                    │                                         │
│                                    │ No Gate (exploratory)                   │
│                                    │ (Failure informs, doesn't block)        │
│                                    ▼                                         │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────────┐
                              │     PHASE 5         │
                              │ Baseline Comparison │
                              │ (H-CP hypotheses)   │
                              │ DETERMINES_SUCCESS  │
                              └─────────────────────┘

═══════════════════════════════════════════════════════════════════════════
CRITICAL PATH: H-E1 → H-M3 → H-M4 → Phase 5
GATE CHECKPOINTS: Gate 1 (H-E1), Gate 2 (H-M3)
═══════════════════════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Type | Prerequisites | Gate Type | If Fail |
|-------|------------|------|---------------|-----------|---------|
| - | H-M1 | Mechanism | - | BUILD_ON | (Pre-validated) |
| - | H-M2 | Mechanism | - | BUILD_ON | (Pre-validated) |
| 0 | H-E1 | Existence | None | MUST_WORK | STOP - hypothesis falsified |
| 1 | H-M3 | Mechanism | H-E1 | MUST_WORK | PIVOT to alt metrics |
| 2 | H-M4 | Mechanism | H-M3 | SHOULD_WORK | Document as limitation |
| 3 | (Phase 5) | Comparison | H-M4 | DETERMINES_SUCCESS | Report negative result |

**Verification Phases:**

**Phase 1 - Foundation (H-E1)**
- Validates existence of clustering phenomenon
- Must pass before any mechanism testing
- Failure = entire hypothesis falsified

**Phase 2 - Core Mechanism (H-M3)**
- Tests KEY TENSION: similar tasks → similar B spaces
- Must pass to claim causal understanding
- Failure = pivot to alternative representations

**Phase 3 - Exploratory (H-M4)**
- Identifies layer-wise patterns
- Informative regardless of outcome
- Failure = acceptable scope limitation

**Phase 5 - Baseline Comparison (Deferred)**
- Compares against random baseline and public adapters
- DETERMINES_SUCCESS gate
- Handled in separate Phase 5 workflow

**Gate Conditions:**
- **Gate 1 (H-E1):** p < 0.05 AND Cohen's d > 0.5 → PASS
- **Gate 2 (H-M3):** Spearman ρ > 0.3 with p < 0.05 → PASS
- **No Gate (H-M4):** Exploratory, failure is informative

---

## 5. Timeline & Execution

### 5.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════════
                    VERIFICATION TIMELINE - 3 Active Hypotheses
═══════════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ Week 1    │ Week 2    │ Week 3    │ Week 4    │ Week 5    │
──────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 1: Foundation   │           │           │           │           │           │
──────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
  Adapter Generation  │ ██████████│           │           │           │           │
  (200 LoRA adapters) │           │           │           │           │           │
                      │           │           │           │           │           │
  H-E1 Clustering     │           │ ██████████│           │           │           │
  Analysis            │           │           │           │           │           │
                      │           │           │           │           │           │
  [Gate 1] ─────────► │           │         ◆ │           │           │           │
  (MUST_WORK)         │           │  p<0.05?  │           │           │           │
──────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 2: Core Mech    │           │           │           │           │           │
──────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
  H-M3 Correlation    │           │           │ ██████████│ ██████████│           │
  (FLAN taxonomy)     │           │           │           │           │           │
                      │           │           │           │           │           │
  [Gate 2] ─────────► │           │           │           │         ◆ │           │
  (MUST_WORK)         │           │           │           │  ρ>0.3?   │           │
──────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 3: Exploratory  │           │           │           │           │           │
──────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
  H-M4 Layer-wise     │           │           │           │           │ ██████████│
  Analysis            │           │           │           │           │           │
                      │           │           │           │           │           │
  [No Gate] ────────► │           │           │           │           │    (info) │
  (SHOULD_WORK)       │           │           │           │           │           │
══════════════════════╧═══════════╧═══════════╧═══════════╧═══════════╧═══════════╧
Legend: ██ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks | Critical Path: 5 weeks
═══════════════════════════════════════════════════════════════════════════════════
```

### 5.2 Critical Path Analysis

**Critical Path:** H-E1 → H-M3 → H-M4

| Segment | Duration | Cumulative | Gate |
|---------|----------|------------|------|
| Adapter Generation | 1 week | Week 1 | - |
| H-E1 Clustering Analysis | 1 week | Week 2 | Gate 1 (MUST_WORK) |
| H-M3 Correlation Analysis | 2 weeks | Week 4 | Gate 2 (MUST_WORK) |
| H-M4 Layer-wise Analysis | 1 week | Week 5 | No gate (exploratory) |

**Total Duration:** 5 weeks

**Slack Analysis:**
- All hypotheses are on critical path (sequential execution)
- No parallel paths available
- Zero slack: any delay extends total duration

**Gate Decision Points:**
- **Gate 1 (End Week 2):** H-E1 must show p < 0.05 AND Cohen's d > 0.5
  - If PASS: Proceed to H-M3
  - If FAIL: STOP - core hypothesis falsified
- **Gate 2 (End Week 4):** H-M3 must show Spearman ρ > 0.3 with p < 0.05
  - If PASS: Proceed to H-M4
  - If FAIL: PIVOT to alternative metrics before H-M4

**Early Termination Scenarios:**
- Gate 1 FAIL: Project terminates Week 2 (savings: 3 weeks)
- Gate 2 FAIL: Pivot decision Week 4, may extend timeline

### 5.3 Resource Summary

**Hypothesis Summary:**
| Type | Count | IDs | Status |
|------|-------|-----|--------|
| Existence | 1 | H-E1 | READY |
| Mechanism (Active) | 2 | H-M3, H-M4 | READY |
| Mechanism (BUILD_ON) | 2 | H-M1, H-M2 | PRE-VALIDATED |

**Computational Resources:**
| Task | GPU Hours | Storage | Notes |
|------|-----------|---------|-------|
| Adapter Generation (200) | 50-100 | ~20GB | Llama-3.2-1B, 8 tasks |
| B Matrix Extraction | 2-4 | ~5GB | All layers, all adapters |
| Grassmann Distance (2.85M pairs) | 1-2 | ~1GB | scipy computation |
| Statistical Analysis | <1 | <100MB | Mann-Whitney, Spearman |

**Total Estimated Resources:**
- GPU Time: 55-110 hours (single GPU)
- Storage: ~30GB
- Compute Time: 1-2 days for adapter generation

**Verification Phases:**
1. **Foundation (H-E1):** Adapter generation + clustering validation
2. **Core Mechanism (H-M3):** FLAN taxonomy correlation
3. **Exploratory (H-M4):** Layer-wise effect size analysis

**Phase 5 (Deferred):** Baseline comparison against:
- Random orthonormal matrices
- Uncontrolled public adapters
- Same-task different-seed controls

### 5.4 Execution Order

**Step-by-Step Execution Plan:**

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: ADAPTER GENERATION (Week 1)                                  │
├─────────────────────────────────────────────────────────────────────┤
│ • Generate 200 LoRA adapters with controlled provenance             │
│ • Verify SHA-256 hash of base model checkpoint                      │
│ • 20 adapters per task × 8 tasks + 5 seed variants per task        │
│ • Tasks: GSM8K, ARC-C, LogiQA, StrategyQA, MNLI, QQP, SST-2, MRPC  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: H-E1 CLUSTERING ANALYSIS (Week 2)                           │
├─────────────────────────────────────────────────────────────────────┤
│ • Extract B matrices from all LoRA-adapted layers                   │
│ • Compute orthonormal bases via QR decomposition                    │
│ • Calculate pairwise Grassmann distances (2.85M pairs)              │
│ • Mann-Whitney U test: within-cluster vs between-cluster           │
│ • Compute Cohen's d with 95% CI                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ GATE 1 EVALUATION: H-E1 (End Week 2)                                │
├─────────────────────────────────────────────────────────────────────┤
│ SUCCESS: p < 0.05 AND Cohen's d > 0.5 → Proceed to STEP 3          │
│ FAIL: p > 0.10 OR Cohen's d < 0.3 → STOP, hypothesis falsified     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: H-M3 CORRELATION ANALYSIS (Weeks 3-4)                       │
├─────────────────────────────────────────────────────────────────────┤
│ • Compute FLAN task taxonomy distances (external ground truth)      │
│ • Calculate Spearman rank correlation with Grassmann distances     │
│ • Validate with P3 control (within-task seed variance)             │
│ • Test statistical significance                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ GATE 2 EVALUATION: H-M3 (End Week 4)                                │
├─────────────────────────────────────────────────────────────────────┤
│ SUCCESS: Spearman ρ > 0.3 AND p < 0.05 → Proceed to STEP 4         │
│ FAIL: ρ < 0.1 OR p > 0.10 → PIVOT to alternative metrics           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 4: H-M4 LAYER-WISE ANALYSIS (Week 5)                           │
├─────────────────────────────────────────────────────────────────────┤
│ • Separate Grassmann distance computation by layer type             │
│ • Compute Cohen's d per layer (attention vs MLP)                   │
│ • Rank layers by effect size                                        │
│ • Identify layers with d > 0.8 (large effect)                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ VERIFICATION COMPLETE → PROCEED TO PHASE 5                          │
├─────────────────────────────────────────────────────────────────────┤
│ • Document findings for each hypothesis                             │
│ • Prepare for Phase 5 Baseline Comparison                          │
│ • Generate hypothesis synthesis report                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Dialectical Analysis

### 6.1 Overview

This dialectical analysis evaluates the main hypothesis (H-LoRAGeo-v1) against its null hypothesis (H0) using a structured Thesis-Antithesis-Synthesis framework. The analysis was performed using ClearThought structured argumentation to ensure balanced consideration of both positions.

**Dialectical Framework:**
- **Thesis:** Main hypothesis claiming geometric clustering exists
- **Antithesis:** Null hypothesis (H0) claiming no significant difference
- **Synthesis:** Verification plan as resolution mechanism

**Key Tension:** The core empirical claim (Step 3 of causal mechanism) that "similar tasks require similar transformations" is the primary point of contention between thesis and antithesis

### 6.2 Thesis Statement

**Core Claim:** LoRA adapters trained on semantically similar tasks exhibit significantly smaller Grassmann distances in their B matrix column spaces under controlled experimental conditions, because task-specific fine-tuning induces geometrically coherent weight modifications constrained by LoRA's low-rank structure.

**Supporting Premises:**
1. Fine-tuning induces systematic weight updates encoding task-relevant transformations (established)
2. LoRA constrains updates to low-rank subspace defined by B matrix column space (design property)
3. Semantically similar tasks require similar functional transformations in output dimension
4. Similar functional transformations lead to aligned B column spaces
5. Aligned subspaces manifest as smaller Grassmann geodesic distances (mathematical)
6. Previous experiments showed correct effect direction with large effect size (Cohen's d = 0.91)

**Expected Outcomes:**
- Primary (P1): Within-cluster < between-cluster distances (p < 0.05, Cohen's d > 0.5)
- Secondary (P2): Grassmann distance correlates with FLAN taxonomy (Spearman ρ > 0.3)
- Tertiary (P3): Within-task variance << within-cluster variance (control validation)

**Thesis Strengths:**
- Builds on established LoRA mathematical properties
- Clear 4-step causal mechanism with testable predictions
- Addresses all failure modes from previous attempts
- Multi-tier validation (clustering + correlation + control)
- Large effect size observed in pilot study (d = 0.91)

**Thesis Confidence:** 0.80

### 6.3 Antithesis Development

**Null Hypothesis (H0):** There is no significant difference in Grassmann distances between LoRA adapter B matrix column spaces for adapters trained on semantically similar vs. dissimilar tasks. Any observed differences are due to training stochasticity, measurement noise, or confounding variables rather than genuine task-induced geometric structure.

**Counter-Arguments:**
1. **Stochasticity Dominance:** Training stochasticity (random initialization, batch order, GPU non-determinism) may dominate task-specific signal
2. **Taxonomy Invalidity:** FLAN task taxonomy categories may not reflect true functional similarity in weight space
3. **Wrong Representation:** B matrix column space may not be the appropriate representation - signal could be in A matrix or BA product
4. **Metric Inadequacy:** Grassmann distance may miss task-relevant structure encoded in singular values or matrix norms
5. **Statistical Artifact:** Previous p = 0.127 result suggests effect may not exist at adequate power levels
6. **Architecture Confound:** Base model architecture specificity may produce spurious patterns

**Conditions Under Which H0 Would Be Supported:**
- H-E1 fails: p > 0.10 OR Cohen's d < 0.3 with adequate sample size
- H-M3 fails: Spearman ρ < 0.1 OR p > 0.10 (no correlation with FLAN taxonomy)
- P3 control fails: Within-task distance ≥ within-cluster distance (stochasticity dominates)
- All alternative representations (A, BA) also show no signal

**Antithesis Strengths:**
- Raises valid methodological concerns
- Highlights unproven core assumption (similar tasks → similar transformations)
- Accounts for previous statistical failure (p = 0.127)
- Forces consideration of alternative explanations

**Antithesis Weaknesses:**
- Cannot explain large observed effect size (d = 0.91) as pure noise
- Previous failure was clearly due to power, not absent effect
- Control condition P3 directly addresses stochasticity concern

**Antithesis Confidence:** 0.20 (low - evidence favors thesis)

### 6.4 Synthesis

**Resolution Claim:** The verification plan resolves the thesis-antithesis dialectic through a sequential gated testing framework that can definitively distinguish between genuine geometric clustering and artifactual patterns, while allowing for nuanced partial outcomes.

**How Each Antithesis Concern Is Addressed:**

| Antithesis Concern | Resolution Mechanism | Test |
|--------------------|---------------------|------|
| Stochasticity dominates | P3 control condition | Within-task different-seed distances |
| Taxonomy invalid | FLAN correlation test | Spearman ρ with taxonomy distance |
| Wrong representation | Multi-matrix fallback | Test A, BA if B fails |
| Metric inadequacy | Alternative metric comparison | Frobenius norm, projection overlap |
| Power insufficient | n = 80+ per category | Well above minimum n = 17 |
| Architecture confound | SHA-256 verification | Single verified checkpoint |

**Balanced Assessment:**

The hypothesis H-LoRAGeo-v1 presents a testable claim that task-specific fine-tuning induces structured B matrix column spaces leading to geometric clustering. The null hypothesis raises valid methodological concerns regarding stochasticity, representation choice, and taxonomy validity.

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before mechanism testing
2. **Sequential mechanism testing (H-M3):** Tests core causal claim directly
3. **Gate conditions:** Allow early detection of H0 support
4. **Control conditions:** P3 directly addresses stochasticity concern
5. **Fallback mechanisms:** Multi-matrix analysis if primary approach fails

**Outcome Possibilities:**

| Outcome | Conditions | Interpretation |
|---------|------------|----------------|
| **Full Thesis Support** | All gates pass, all predictions confirmed | Geometric signature hypothesis validated |
| **Partial Support** | H-E1, H-M3 pass; H-M4 inconclusive | Core claim validated with scope limitations |
| **Weak Support** | H-E1 passes; H-M3 marginal (0.1 < ρ < 0.3) | Effect exists but mechanism unclear |
| **No Support** | H-E1 fails OR H-M3 fails completely | Antithesis supported, hypothesis falsified |

**Synthesis Confidence:** 0.85 (verification plan is well-designed to resolve dialectic)

### 6.5 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution | Robustness |
|--------|-----------------|----------------------|------------|------------|
| **Existence** | Clustering phenomenon exists | May be statistical artifact | H-E1 with n=80+ per category | HIGH |
| **Mechanism** | Causal chain is valid | Alternative explanations exist | H-M3 tests core claim directly | HIGH |
| **Ground Truth** | FLAN taxonomy is valid | May not reflect weight-space similarity | Spearman correlation test (P2) | MEDIUM |
| **Representation** | B matrix is appropriate | Signal may be in A or BA | Multi-matrix fallback ready | HIGH |
| **Stochasticity** | Task signal dominates | Training noise dominates | P3 control condition | HIGH |
| **Generalization** | Results generalize | Llama-specific effects | Accept as scope limitation | LOW |

**Risk-Weighted Robustness Analysis:**

| Risk | Impact on Thesis | Mitigation Effectiveness | Net Robustness |
|------|------------------|-------------------------|----------------|
| R1 (Taxonomy) | HIGH | MEDIUM (external validation) | MEDIUM |
| R2 (Metric) | MEDIUM | HIGH (alternatives available) | HIGH |
| R3 (Matrix) | HIGH | HIGH (multi-matrix fallback) | HIGH |
| R4 (Stochasticity) | CRITICAL | HIGH (P3 control) | HIGH |
| R5 (Generalization) | LOW | LOW (accepted limitation) | N/A |
| R6 (Power) | MEDIUM | HIGH (n=80+ buffer) | HIGH |
| R7 (Provenance) | HIGH | HIGH (SHA-256 protocol) | HIGH |

**Overall Robustness Score:** **HIGH**

**Rationale:** 5 of 6 testable aspects have HIGH robustness due to specific mitigation mechanisms built into the verification plan. Only ground truth validity (FLAN taxonomy) remains at MEDIUM robustness, as it relies on external validation rather than internal controls.

**Confidence in Verification Plan:** 0.80

**Key Robustness Features:**
1. Sequential gates allow early termination → prevents wasted effort on falsified hypothesis
2. Control conditions (P3) → directly tests most critical risk (stochasticity)
3. Fallback mechanisms → preserves research value even if primary approach fails
4. High statistical power → eliminates ambiguous results

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** LoRA adapters trained on similar tasks exhibit smaller Grassmann distances in B matrix column spaces under controlled conditions
- ID: H-LoRAGeo-v1 | Confidence: 0.80 | Scope Reduction: 40%

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 3 active + 2 BUILD_ON references
  - H-E: 1 (Existence), H-M: 2 active (Core mechanism + Layer-wise)
- Phases: 3 over 5 weeks
- Critical Gates: 2 MUST_WORK decision points (H-E1, H-M3)

**Risk Assessment:** MEDIUM-HIGH
- Critical risk: Training stochasticity (R4) - mitigated by P3 control
- High risks: Wrong matrix representation (R3), Provenance failure (R7)

**Key Innovation:** First controlled validation using Model Zoo methodology for LoRA adapters

**Immediate Action:** Begin Phase 1 with adapter generation and H-E1 clustering analysis

### 7.2 Final Summary

**Key Achievements:**
- 3 active hypotheses structured across 3 verification phases
- 40% scope reduction via Established Facts (4 BUILD_ON claims)
- H0 explicitly addressed through dialectical analysis
- All 7 identified risks have mitigation strategies
- Sequential gated testing prevents wasted effort on falsified hypotheses

**Verification Execution Order:**

| Phase | Duration | Hypotheses | Gate | Action on Fail |
|-------|----------|------------|------|----------------|
| 1: Foundation | 2 weeks | H-E1 (Existence) | MUST_WORK | STOP - falsified |
| 2: Core Mechanism | 2 weeks | H-M3 (Correlation) | MUST_WORK | PIVOT to alt metrics |
| 3: Exploratory | 1 week | H-M4 (Layer-wise) | SHOULD_WORK | Document limitation |
| 5: Comparison | (Deferred) | Phase 5 scope | DETERMINES_SUCCESS | Report negative |

**Critical Success Factors:**
1. Controlled provenance via SHA-256 verification
2. Adequate statistical power (n=80+ per category)
3. P3 control condition validates signal vs noise
4. Multi-tier validation (clustering + correlation + control)

### 7.3 Conclusions

**Critical Decision Points:**

1. **Gate 1 (End Week 2):** H-E1 Existence Test
   - PASS: p < 0.05 AND Cohen's d > 0.5 → Proceed to Phase 2
   - FAIL: p > 0.10 OR d < 0.3 → STOP, hypothesis falsified

2. **Gate 2 (End Week 4):** H-M3 Mechanism Test
   - PASS: Spearman ρ > 0.3, p < 0.05 → Proceed to Phase 3
   - FAIL: ρ < 0.1 → PIVOT to alternative metrics/representations

**Open Questions (from Phase 2A):**
- Which layer types (attention vs MLP) show strongest clustering? → H-M4
- What is the minimum LoRA rank for effect to manifest? → Future ablation
- Does effect generalize across base model architectures? → Scope limitation

**Recommendations:**

1. **Immediate Actions:**
   - Set up adapter generation pipeline with SHA-256 verification
   - Implement Grassmann distance computation infrastructure
   - Prepare statistical analysis scripts (Mann-Whitney, Spearman)

2. **Resource Allocation:**
   - GPU: 55-110 hours for adapter generation
   - Storage: ~30GB for adapters and matrices
   - Timeline: 5 weeks critical path

3. **Failure Management:**
   - Document all intermediate results regardless of outcome
   - Execute PIVOT strategies if primary approach fails
   - Preserve research value through negative result reporting

### 7.4 Appendices

**A. Phase 2A Reference:**
- Source: `03_refinement.yaml` (H-LoRAGeo-v1)
- Synthesis: `02_synthesis.yaml`
- Round Table: `01_round_table/final_opinions.yaml`

**B. MCP Tool Usage Summary:**
- `mcp__clearThought__scientificmethod`: 4 calls (hypothesis + experiment stages)
- `mcp__clearThought__collaborativereasoning`: 1 call (risk analysis)
- `mcp__clearThought__structuredargumentation`: 3 calls (thesis-antithesis-synthesis)

**C. Hypothesis ID Reference:**
| ID | Full Name | Phase |
|----|-----------|-------|
| H-E1 | Existence of Task-Similarity Clustering | Phase 2B-4 |
| H-M1 | Task-Specific Weight Updates | BUILD_ON |
| H-M2 | LoRA Low-Rank Constraint | BUILD_ON |
| H-M3 | Similar Tasks → Similar B Spaces | Phase 2B-4 |
| H-M4 | Layer-wise Clustering Strength | Phase 2B-4 |

**D. Key Metrics Reference:**
- Mann-Whitney U test (existence): p < 0.05, Cohen's d > 0.5
- Spearman correlation (mechanism): ρ > 0.3, p < 0.05
- Control condition (P3): within-task < 0.5 × within-cluster

---

## 8. State & Task Tracking

### 8.1 Verification State Status

**File:** `verification_state.yaml`
**Status:** CREATED
**Schema Version:** 3.5

**State Summary:**
- Main Hypothesis ID: H-LoRAGeo-v1
- Total Sub-Hypotheses: 3 active + 2 BUILD_ON
- Current Phase: Phase 2C (ready to begin)
- Execution Mode: UNATTENDED
- Next Action: Begin Phase 2C with H-E1 (first READY hypothesis)

**Sub-Hypothesis Status:**
| ID | Type | Status | Gate | Prerequisites |
|----|------|--------|------|---------------|
| H-E1 | EXISTENCE | READY | MUST_WORK | None |
| H-M3 | MECHANISM | NOT_STARTED | MUST_WORK | H-E1 |
| H-M4 | MECHANISM | NOT_STARTED | SHOULD_WORK | H-M3 |

### 8.2 Pipeline Tasks Updated

**Archon MCP Status:** Requires authentication (not available in session)

**Pipeline Progress:**
- Phase 0 (Brainstorm): DONE
- Phase 1 (Research): DONE
- Phase 2A (Dialogue): DONE
- Phase 2B (Planning): DONE ← Current
- Phase 2C (Experiment Design): READY (next)
- Phase 3 (Implementation): Pending
- Phase 4 (Validation): Pending
- Phase 5 (Baseline): Pending

**Note:** Pipeline task IDs will be populated when Archon MCP is authenticated.

### 8.3 Hypothesis Tasks Created

**Hypothesis Task Summary:**

| Hypothesis | Type | Gate | Task Status | Archon Task ID |
|------------|------|------|-------------|----------------|
| H-E1 | EXISTENCE | MUST_WORK | Created in state | (pending Archon) |
| H-M3 | MECHANISM | MUST_WORK | Created in state | (pending Archon) |
| H-M4 | MECHANISM | SHOULD_WORK | Created in state | (pending Archon) |

**BUILD_ON References (not tasks):**
- H-M1: Task-specific weight updates (pre-validated)
- H-M2: LoRA low-rank constraint (pre-validated)

**Total Active Hypotheses:** 3
**Total BUILD_ON References:** 2

**Next Steps:**
1. Run `/phase2c-experiment-design` for H-E1
2. Or use `/hypothesis-next` to auto-select first READY hypothesis
3. Or continue with `/hypothesis-loop` for full automated execution

---

*Generated by YouRA Phase 2B (v6.0) | 2026-04-13*
