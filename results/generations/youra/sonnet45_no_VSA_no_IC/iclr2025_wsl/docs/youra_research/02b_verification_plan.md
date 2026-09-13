# Verification Plan: Hierarchical Weight Space Embeddings for Cross-Architecture Model Property Inference

**Date:** 2026-08-20
**Hypothesis ID:** H-HierarchicalWeightEmbedding-v1
**Confidence:** 0.80
**Total Hypotheses:** 2

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under heterogeneous model zoos (ModelZooDataset, SANE, ViTModelZoo) containing CNNs, Transformers, RNNs, and MLPs trained on overlapping task sets, if we train a hierarchical variational autoencoder with architecture-type-aware tokenization and three-level supervision (coarse labels → contrastive learning → zero-shot transfer), then same-task different-architecture models will cluster more tightly (measured via within-cluster sum of squares) than different-task same-architecture models, because task-level functional constraints and training-induced regularities create architecture-invariant structural features in weight distributions that persist across computational primitives (convolution vs attention vs recurrence).

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in embedding space clustering tightness between same-task different-architecture model pairs and different-task same-architecture model pairs. Any observed clustering is attributable to architecture-specific weight patterns rather than task-invariant structure.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ModelZooDataset + SANE + ViTModelZoo (Heterogeneous Splits) (standard) | Provides heterogeneous architecture populations (CNNs, Transformers, RNNs, MLPs) with controlled task annotations. SANE extends to inhomogeneous zoos addressing the gap identified by Falk et al. (2025). Pre-Phase 1 dataset audit verifies ≥30 models per architecture-task cell for statistical validity (Assumption A1). |
| **Model** | Hierarchical VAE with Architecture-Type-Aware Tokenization | Level 1 (NFN/UNF): Preserves local neuron-permutation equivariance within architectures. Level 2 (pooling): Collapses to layer summaries, sacrifices local equivariance for cross-architecture compatibility. Level 3 (Transformer): Handles variable-length sequences, discovers relational structure via self-attention. Three-level supervision (coarse labels → contrastive → zero-shot) breaks circularity. |

**Dataset Details:**
- Source: ModelZooDataset (NeurIPS 2022 Dataset Track), SANE (ICML 2024), ViTModelZoo (2025)
- Path: https://github.com/ModelZoos/ModelZooDataset, https://github.com/HSG-AIML/SANE, https://github.com/ModelZoos/ViTModelZoo

**Model Details:**
- Type: Variational Autoencoder (3-level hierarchy)
- Source: Custom architecture combining NFN (github.com/AllanYangZhou/nfn), UNF (github.com/AllanYangZhou/universal_neural_functional), and Transformer sequence modeling

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| ProbeGen (Kahana et al. 2024) | 30-1000x fewer FLOPs than prior methods on single-architecture weight space learning | Model zoos with homogeneous architectures |
| SANE (ICML 2024) | Demonstrates sequential weight processing and model generation on large zoos | MultiZoo-SANE (adapted for inhomogeneous zoos but not fully unified) |
| Architecture-Conditioned MLP | Baseline performance on model zoo classification tasks | ModelZooDataset |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Model zoos contain sufficient cross-architecture coverage (≥30 models per architecture-task cell) for statistical validity | ModelZooDataset (NeurIPS 2022) + SANE extensions (Falk 2025) target heterogeneous populations, but exact coverage unknown until dataset audit | Statistical tests underpowered, clustering results may reflect sampling noise rather than genuine task structure. Mitigation: treat sparse samples as robustness test (natural experiment) |
| A2 | Task labels from model zoo metadata are accurate and granular enough to define meaningful task clusters | ModelZooDataset uses controlled training, SANE uses verified task annotations | Supervised labels introduce noise, contrastive learning discovers spurious correlations. Mitigation: validate via zero-shot transfer to unlabeled models (breaks label dependency) |
| A3 | Permutation-invariant pooling (Level 2) retains sufficient task-relevant information despite discarding neuron-level details | Deep Sets (Zaheer 2017) shows sum/mean pooling preserves set-level structure; hierarchical VAEs in vision maintain reconstruction quality | Cross-architecture alignment fails because critical information is lost in pooling. Mitigation: measure reconstruction task accuracy degradation (accept if <30%) |
| A4 | Training-induced regularities (augmentation strategies, optimization dynamics) are orthogonal to task-induced structure, or at least separable | None — identified as potential confound by Prof. Rex (Exchange 6) | Clustering reflects training procedures rather than tasks, invalidating task-invariance claim. Mitigation: explicit ablation comparing same-task different-procedure vs different-task same-procedure |
| A5 | Architecture families (CNN, Transformer, RNN, MLP) are metrically compatible — cross-architecture alignment is mathematically feasible | None — requires empirical validation via CKA+UMAP feasibility gates (Prof. Pax Exchange 4, Prof. Rex Exchange 6) | No linear or nonlinear alignment exists, cross-architecture bridge is infeasible. Mitigation: CKA gate in Phase 1 (if CKA same-task <0.6, stop and reject hypothesis) |

### 1.6 Research Gap & Novelty

**Gap:** No existing method enables unified weight-space embeddings for heterogeneous model zoos containing different architecture families. NFN/UNF handle single architectures. Task arithmetic requires shared base models. SANE processes homogeneous zoos.

**Novelty:** First demonstration that task-level functional constraints create architecture-invariant structure in weight distributions, enabling cross-architecture model property inference on heterogeneous unlabeled collections. Hierarchical equivariance tradeoff: preserve local neuron-permutation symmetries (micro-level) while sacrificing them for cross-architecture generalization (macro-level). Operationalized via 3-level VAE. Compositional meta-space design exploits heterogeneity as signal rather than treating it as obstacle (paradigm shift from NFN/UNF homogeneous-only methods).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M-integrated | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Dataset Coverage Audit

**Type:** EXISTENCE

**Statement:** Under heterogeneous model zoo datasets (ModelZooDataset, SANE, ViTModelZoo), if we audit architecture-task cell coverage, then at least 70% of cells will contain ≥30 models, sufficient for statistical validity, because these datasets were specifically designed for inhomogeneous zoo research and target diverse architecture families.

**Rationale:**
Dataset coverage determines statistical validity for bootstrap testing (n=100 resamples). Insufficient coverage (sparse cells) invalidates clustering comparisons. This hypothesis validates assumption A1 (≥30 models per architecture-task cell) via Pre-Phase 1 audit before wasting effort on infeasible training.

**Variables:**
- Independent: Architecture-Task Cell Coverage (percentage of architecture-task combinations with ≥30 models)
- Dependent: Statistical Validity Threshold (binary: sufficient ≥70% cells OR insufficient <70%)
- Controlled: Dataset Composition (fixed: ModelZooDataset + SANE + ViTModelZoo)

**Verification Protocol:**
1. Download/access all three datasets and extract metadata (architecture type, task label)
2. Create architecture-task cross-tabulation matrix counting models per cell
3. Flag cells with <30 models and calculate coverage percentage
4. Generate coverage heatmap visualization showing distribution
5. Validate critical cells (ImageNet-CNN, ImageNet-Transformer) meet ≥30 threshold

**Success Criteria (Pre-Phase 1 Gate):**
- Primary: ≥70% of architecture-task cells contain ≥30 models
- Secondary: All critical cells (ImageNet-CNN, ImageNet-Transformer, CIFAR-CNN) contain ≥30 models
- Fallback: 50-70% coverage BUT critical cells covered (apply scope reduction)

**Failure Response:**
- IF <50% coverage: ABANDON (insufficient data, need collection phase)
- IF 50-70% coverage AND critical cells sparse: PIVOT (reduce to homogeneous subsets, loses novelty)
- IF ≥70% coverage but critical cells sparse: EXPLORE (substitute comparable cells)

**Gate:**
- Type: MUST_WORK
- If Fail: Blocks Phase 1 (CKA feasibility gate cannot proceed without sufficient data)

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.4 Assumption A1, Section 5 SH1 (existence verification)

---

#### H-M-integrated: Hierarchical VAE Mechanism Chain

**Type:** MECHANISM

**Statement:** Under heterogeneous model zoos with architecture-specific encoders (NFN/UNF), hierarchical pooling, and Transformer sequence modeling, if we train the 3-level VAE with contrastive supervision, then same-task different-architecture models will exhibit (1) task-invariant weight patterns at layer-summary level, (2) higher CKA similarity (>0.6) than different-task pairs (<0.4), (3) tighter clustering (lower WCSS) in latent space, and (4) successful cross-architecture relational discovery via self-attention, because task constraints dominate architecture-specific implementation details at coarse-grained scale.

**Rationale:**
This integrates the 4-step causal chain (task constraints → equivariant encoding → pooling → Transformer relational discovery) into a single testable mechanism. Validates core novelty claim: hierarchical design trades local equivariance for cross-architecture generalization. Phase 1 CKA gate provides early falsification if architecture subspaces are incompatible before expensive VAE training.

**Variables:**
- Independent: Architecture Pair Type (same-task vs different-task model pairs across CNN/Transformer/RNN/MLP)
- Dependent (Primary): Embedding Clustering Tightness (WCSS normalized by between-cluster variance, lower = tighter)
- Dependent (Secondary): CKA Representation Similarity (Centered Kernel Alignment score, range [0,1])
- Controlled: VAE Training Configuration (latent dim D=512, Transformer layers L=6, contrastive margin m=0.3)

**Verification Protocol:**
1. Phase 1: Train architecture-specific encoders (NFN for CNNs, UNF for Transformers/RNNs/MLPs) and compute CKA similarity on validation set (100 same-task pairs, 100 different-task pairs)
2. CKA Feasibility Gate: Check median CKA(same-task) >0.6 AND median CKA(different-task) <0.4 — if fails, stop and reject mechanism
3. Phase 2-3: Train full hierarchical VAE with three-level supervision (coarse task labels → contrastive triplet loss → zero-shot transfer to unlabeled models)
4. Phase 4: Extract latent embeddings for all models and compute WCSS for same-task clusters and different-task clusters
5. Bootstrap hypothesis test (n=100 resamples) comparing WCSS distributions, threshold p<0.01 and Cohen's d>0.5
6. Ablation test: Remove architecture-type token embeddings and re-evaluate clustering to verify Transformer learns architecture-aware relational structure

**Success Criteria (PoC: Mechanism Validation):**
- Primary: Mean WCSS(same-task) < Mean WCSS(different-task) with p<0.01 and Cohen's d>0.5
- Secondary (Phase 1 Gate): CKA same-task >0.6 AND different-task <0.4
- Ablation: Removing architecture tokens degrades clustering by ≥15pp (validates Transformer contribution)

**Failure Response:**
- IF CKA gate fails: ABANDON (architecture subspaces incompatible, no linear/nonlinear bridge exists)
- IF WCSS test fails (p≥0.01): PIVOT (task structure weaker than architecture patterns, try supervised fine-tuning)
- IF ablation shows tokens redundant: EXPLORE (mechanism simpler than proposed, pooling alone may suffice)

**Gate:**
- Type: MUST_WORK
- If Fail: Blocks Phase 5 (no point comparing to baseline if core mechanism doesn't work)

**Dependencies:** H-E1 (requires sufficient dataset coverage for statistical validity)

**Source:** Phase 2A Section 1.3 Causal Mechanism (4-step chain), Section 1.6 Predictions P1-P2, Section 5 SH2 (mechanism verification)

---

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 3. Execution

### 3.1 Dependency Chain

═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 2 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Dataset Coverage Audit)
    Gate: MUST_WORK
    ├─ IF PASS (≥70% coverage): → H-M-integrated
    ├─ IF PARTIAL (50-70%, critical cells OK): → H-M-integrated (scope reduction)
    └─ IF FAIL (<50% coverage): → STOP (insufficient data)
         │
         ▼
[Level 1 - Core Mechanism]
    H-M-integrated (Hierarchical VAE 4-step chain)
    Prerequisites: H-E1
    Gate: MUST_WORK
    │
    ├─ Phase 1 Sub-gate: CKA Feasibility
    │  ├─ IF PASS (CKA same-task >0.6): → Continue to VAE training
    │  └─ IF FAIL (CKA <0.6): → STOP (subspaces incompatible)
    │
    ├─ Phase 4 Sub-gate: WCSS Clustering Test
    │  ├─ IF PASS (p<0.01, d>0.5): → Phase 5 (Baseline Comparison)
    │  ├─ IF PARTIAL (p<0.05 OR d=0.2-0.5): → Modify mechanism
    │  └─ IF FAIL (p≥0.05): → STOP (task structure doesn't exist)
    │
    └─ Phase 4 Ablation: Architecture Token Contribution
       ├─ IF tokens contribute ≥15pp: → Mechanism confirmed
       └─ IF tokens redundant: → Simplify (pooling alone may suffice)
         │
         ▼
[Terminal: Phase 5]
    Baseline Comparison (DETERMINES_SUCCESS gate)
    Prerequisites: H-M-integrated PASS
    (Phase 5 handled separately, not in Phase 2B scope)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M-integrated (CKA gate) → H-M-integrated (WCSS test)
Parallelization: None (sequential verification with early stop gates)
═══════════════════════════════════════════════════════════

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥70% cells with ≥30 models OR critical cells covered | STOP if <50% coverage; SCOPE if 50-70% + critical OK |
| H-M-integrated (CKA sub-gate) | MUST_WORK (Phase 1) | CKA same-task >0.6 AND different-task <0.4 | STOP (architecture subspaces incompatible, no bridge exists) |
| H-M-integrated (WCSS test) | MUST_WORK (Phase 4) | Mean WCSS(same-task) < WCSS(different-task), p<0.01, Cohen's d>0.5 | FAIL: STOP (task structure doesn't exist); PARTIAL: Modify mechanism |
| H-M-integrated (Ablation) | SHOULD_WORK | Removing arch tokens degrades clustering ≥15pp | If redundant: Simplify mechanism (not a blocker) |

### 3.3 Timeline

═══════════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 2 Hypotheses (Sequential with Early Stop Gates)
═══════════════════════════════════════════════════════════════════════════════

Phase/Hypothesis          │ Pre-Ph1 │ Phase 1 │ Phase 2-3 │ Phase 4 │
                          │ (W1)    │ (W2-3)  │ (W4-5)    │ (W6-7)  │
──────────────────────────┼─────────┼─────────┼───────────┼─────────┤
PRE-PHASE 1: Dataset Audit
  H-E1 (Coverage Audit)   │ ████    │         │           │         │
  [Gate 1: Coverage]      │     ◆   │         │           │         │
  Decision: PASS/PARTIAL/FAIL       │         │           │         │
──────────────────────────┼─────────┼─────────┼───────────┼─────────┤
PHASE 1: CKA Feasibility
  H-M (CKA Gate)          │         │ ████████│           │         │
  [Gate 2a: CKA]          │         │         ◆           │         │
  Decision: PASS → Continue         │  FAIL → STOP        │         │
──────────────────────────┼─────────┼─────────┼───────────┼─────────┤
PHASE 2-3: VAE Training
  H-M (Hierarchical VAE)  │         │         │ ██████████│         │
  (Level 1→2→3 Training)  │         │         │           │         │
──────────────────────────┼─────────┼─────────┼───────────┼─────────┤
PHASE 4: PoC Validation
  H-M (WCSS Test)         │         │         │           │ ████    │
  H-M (Ablation)          │         │         │           │     ████│
  [Gate 2b: WCSS]         │         │         │           │       ◆ │
  Decision: PASS → Phase 5          │         │  FAIL → STOP        │
──────────────────────────┼─────────┼─────────┼───────────┼─────────┤

═══════════════════════════════════════════════════════════════════════════════
Legend:
  ████ = Active work
  ◆    = Gate decision point (MUST_WORK gates block on FAIL)
  
Critical Path: H-E1 → H-M (CKA) → H-M (VAE) → H-M (WCSS)
Total Duration: 7 weeks (Pre-Phase 1: 1w, Phase 1: 2w, Phase 2-3: 2w, Phase 4: 2w)
Slack: 0 weeks (all sequential, early stop gates)

Early Stop Efficiency:
- IF H-E1 FAIL (W1): Save 6 weeks (stop before Phase 1)
- IF CKA FAIL (W3): Save 4 weeks (stop before VAE training)
- IF WCSS FAIL (W7): Documented failure, proceed to Phase 0 or 2A-Dialogue

═══════════════════════════════════════════════════════════════════════════════

**Critical Path Analysis:**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL PATH: H-E1 → H-M (3 sub-gates)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Path Breakdown:
1. H-E1 (Dataset Audit): 1 week
   → Gate 1: Coverage check
   
2. H-M Phase 1 (CKA Feasibility): 2 weeks
   → Gate 2a: Architecture compatibility (early stop)
   
3. H-M Phase 2-3 (VAE Training): 2 weeks
   (No gate — training phase)
   
4. H-M Phase 4 (PoC Validation): 2 weeks
   → Gate 2b: WCSS clustering test + ablation

Total: 7 weeks (sequential execution)
Slack: 0 weeks (no parallelization opportunities)

Gate Efficiency:
- 2 early-stop gates save wasted effort on infeasible mechanisms
- Gate 1 (W1): Blocks 6 weeks if insufficient data
- Gate 2a (W3): Blocks 4 weeks if subspaces incompatible

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Resource Summary:**

| Component | Count | Phases | Notes |
|-----------|-------|--------|-------|
| **Total Hypotheses** | 2 | 4 phases | H-E1 (Pre-Phase 1), H-M (Phase 1, 2-3, 4) |
| **MUST_WORK Gates** | 3 | W1, W3, W7 | Early stop gates reduce wasted effort |
| **MCP Calls (Phase 2B)** | 2 | Step 3 | H-E1 + H-M (incremental mode) |
| **Dataset Requirements** | 3 zoos | Pre-Phase 1 | ModelZooDataset, SANE, ViTModelZoo |
| **Training Compute** | GPU | Phase 2-3 | Hierarchical VAE training (2 weeks) |
| **Validation Runs** | 200 pairs | Phase 1 | CKA similarity computation |
| **Bootstrap Resamples** | 100 | Phase 4 | WCSS hypothesis test |

Total Duration: **7 weeks** (Pre-Phase 1 through Phase 4)
Phase 5 (Baseline Comparison): Additional 2-3 weeks (not in Phase 2B scope)

**Execution Order:**

1. **Pre-Phase 1** (Week 1): Dataset audit → H-E1
   - Action: Verify ≥30 models per architecture-task cell
   - Gate Decision: PASS (≥70%) | PARTIAL (50-70%, critical OK) | FAIL (<50%)
   
2. **Phase 1** (Weeks 2-3): CKA feasibility → H-M (sub-gate 2a)
   - Action: Train arch-specific encoders, compute CKA on 200 pairs
   - Gate Decision: PASS (same-task >0.6, diff-task <0.4) | FAIL (incompatible)
   
3. **Phase 2-3** (Weeks 4-5): VAE training
   - Action: Train 3-level hierarchical VAE with contrastive supervision
   - No gate (training phase)
   
4. **Phase 4** (Weeks 6-7): PoC validation → H-M (sub-gate 2b)
   - Action: WCSS bootstrap test + ablation study
   - Gate Decision: PASS (p<0.01, d>0.5) | PARTIAL | FAIL (p≥0.05)

**Total Duration:** 7 weeks

---

## 5. Dialectical Analysis

**Thesis (Main Hypothesis):**
Task-level functional constraints create architecture-invariant structural features in weight distributions, enabling cross-architecture model property inference via hierarchical VAE.

**Antithesis (H0 / Skeptical View):**
Architecture-specific weight patterns dominate task structure. Observed clustering reflects computational primitives (convolution vs attention vs recurrence) rather than task-invariant regularities. Cross-architecture alignment is either infeasible (subspaces incompatible) or trivial (architecture labels alone predict clustering).

**Synthesis (Robustness Assessment):**
Truth likely intermediate: Task structure exists but is weaker than architecture structure at fine-grained scale. Hierarchical design's key insight is trading micro-level equivariance (where architecture dominates) for macro-level expressivity (where task structure emerges via coarse-grained pooling). CKA feasibility gate (Phase 1) tests whether task signal is strong enough to overcome architecture noise. WCSS bootstrap test (Phase 4) quantifies relative strength (effect size Cohen's d). Training procedure ablation (Risk R4) disentangles task vs optimization effects. Three gates provide falsification at multiple scales: dataset existence (H-E1), subspace compatibility (CKA), and clustering tightness (WCSS).

**Key Tension Resolved:**
Equivariance vs Expressivity — Hierarchical VAE preserves neuron-permutation symmetries locally (Level 1), sacrifices them for cross-architecture generalization globally (Level 2), and discovers relational structure via attention (Level 3). This is not a compromise but an intentional design: exploit equivariance where it holds (within-architecture), abandon it where it breaks (across-architecture).

---

## 6. Executive Summary

**Main Hypothesis:** Hierarchical Weight Space Embeddings for Cross-Architecture Model Property Inference
- ID: H-HierarchicalWeightEmbedding-v1, Confidence: 0.80
- Core Claim: Task constraints create architecture-invariant weight structure enabling zero-shot cross-architecture clustering

**Verification Structure:**
- Mode: Incremental (Phase 2A data loaded)
- Sub-Hypotheses: 2 total (H-E1: Dataset Coverage, H-M-integrated: 4-step mechanism chain)
- Phases: 4 phases (Pre-Phase 1, Phase 1 CKA Gate, Phase 2-3 VAE Training, Phase 4 PoC)
- Duration: 7 weeks (sequential execution with early-stop gates)
- Critical Gates: 3 decision points (Coverage, CKA Feasibility, WCSS Clustering)

**Scope Reduction:** 25% of claims already established (BUILD_ON: NFN equivariance, UNF extension, Task arithmetic)
- Only generate hypotheses for PROVE_NEW claim: Heterogeneous zoo unified representation

**Risk Assessment:** HIGH
- Primary concerns: R5 (Architecture subspace incompatibility — CRITICAL), R1 (Dataset coverage — HIGH), R4 (Training procedure confound — HIGH)
- Mitigation: Early-stop gates (CKA in Phase 1, coverage in Pre-Phase 1) prevent wasted effort on infeasible mechanisms

**Immediate Action:** Begin Pre-Phase 1 with H-E1 (Dataset Coverage Audit)

---

## 7. Conclusions

### 7.1 Key Achievements

- **2 hypotheses** decomposed from 4-step causal chain (H-E1 existence + H-M-integrated mechanism)
- **Sequential verification** with 3 MUST_WORK gates providing early falsification
- **H0 addressed:** "No significant difference in clustering tightness between same-task different-architecture pairs and different-task same-architecture pairs" — testable via bootstrap p<0.01 threshold
- **Scope efficiently reduced:** 25% of claims excluded as BUILD_ON (NFN, UNF, Task arithmetic already validated)

### 7.2 Verification Execution Order

**Pre-Phase 1: Dataset Audit** (1 week)
- H-E1: Verify ≥30 models per architecture-task cell in ModelZooDataset + SANE + ViTModelZoo
- Gate 1: MUST PASS (≥70% coverage OR critical cells covered)
- Decision: PASS → Phase 1 | PARTIAL → Scope reduction | FAIL → STOP (insufficient data)

**Phase 1: CKA Feasibility Gate** (2 weeks)
- H-M (sub-gate 2a): Train architecture-specific encoders (NFN/UNF), compute CKA on 200 pairs
- Gate 2a: MUST PASS (same-task CKA >0.6 AND different-task <0.4)
- Decision: PASS → Phase 2-3 VAE training | FAIL → STOP (architecture subspaces incompatible)

**Phase 2-3: Hierarchical VAE Training** (2 weeks)
- H-M: Train 3-level VAE (equivariant encoding → pooling → Transformer) with contrastive supervision
- No gate (training phase)

**Phase 4: PoC Validation** (2 weeks)
- H-M (sub-gate 2b): WCSS bootstrap test + architecture token ablation
- Gate 2b: MUST PASS (Mean WCSS(same-task) < WCSS(different-task), p<0.01, Cohen's d>0.5)
- Decision: PASS → Phase 5 (Baseline Comparison) | PARTIAL → Modify mechanism | FAIL → STOP

### 7.3 Critical Decision Points

1. **Gate 1 (H-E1 Dataset Coverage):**
   - PASS (≥70% cells with ≥30 models): → Proceed to Phase 1
   - PARTIAL (50-70%, critical cells OK): → Scope reduction, proceed with caution
   - FAIL (<50% coverage): → STOP, insufficient data for statistical validity

2. **Gate 2a (H-M CKA Feasibility):**
   - PASS (same-task >0.6, different-task <0.4): → Continue to VAE training
   - FAIL (CKA thresholds not met): → STOP, architecture subspaces incompatible (R5 realized)

3. **Gate 2b (H-M WCSS Clustering):**
   - PASS (p<0.01, d>0.5): → Phase 5 Baseline Comparison
   - PARTIAL (p<0.05 OR d=0.2-0.5): → Modify mechanism, retry once
   - FAIL (p≥0.05): → STOP, task structure doesn't exist at coarse-grained scale

### 7.4 Open Questions

From Phase 2A Section 5:
- What is the optimal latent dimension D for balancing expressivity and overfitting?
- Does the contrastive margin m=0.3 generalize across different task domains (vision vs NLP)?
- Can hierarchical design extend to generative models (GANs, Diffusion) via task-space reformulation?
- Is permutation-invariant pooling the best choice, or should we explore Set Transformer with memory?

### 7.5 Recommendations

**Immediate Actions:**
1. Begin Pre-Phase 1 H-E1 (Dataset Coverage Audit) — download ModelZooDataset, SANE, ViTModelZoo
2. Set up measurement infrastructure: CKA computation, WCSS bootstrap testing, coverage heatmap visualization
3. Prepare NFN/UNF encoder codebases for Phase 1 training

**Resource Allocation:**
- GPU compute: Phase 2-3 VAE training (2 weeks)
- Dataset storage: ~500GB for 3 model zoos (estimate)
- Validation compute: 200 CKA pair computations (Phase 1), 100 bootstrap resamples (Phase 4)

**Risk Mitigation Priority:**
1. **Pre-Phase 1:** Execute H-E1 dataset audit immediately (blocks entire pipeline if insufficient)
2. **Phase 1:** CKA feasibility gate provides early stop before expensive VAE training
3. **Phase 4:** Training procedure ablation (R4) disentangles task vs optimization effects

**Baseline Comparison Strategy (Phase 5):**
- Compare against ProbeGen (architecture-specific SOTA), SANE (homogeneous sequential), Architecture-Conditioned MLP (architecture-blind)
- Success criterion: Outperform all three on heterogeneous task prediction with p<0.01
- Adversarial metadata test (P3): >90% accuracy on 100% corrupted labels proves unique weight-based information

---

## Appendix

### A. Hypothesis ID Mapping

| Hypothesis ID | Type | Phase | Source |
|---------------|------|-------|--------|
| H-E1 | Existence | Pre-Phase 1 | Phase 2A Assumption A1, SH1 |
| H-M-integrated | Mechanism (4-step chain) | Phase 1, 2-3, 4 | Phase 2A Causal Mechanism (steps 1-4), SH2 |

### B. Phase 2A Integration

**Loaded from 03_refinement.yaml:**
- Section 0: Established Facts (25% scope reduction)
- Section 1.1: Core statement (hypothesis ID, confidence, Under-If-Then-Because)
- Section 1.2: Variables (IV: Architecture Pair Type, DV: WCSS, CV: VAE config)
- Section 1.3: Causal Mechanism (4-step chain → H-M-integrated)
- Section 1.4: Key Assumptions (A1-A5 → Risks R1-R5)
- Section 1.5: Scope (applies to discriminative models, excludes generative)
- Section 1.6: Predictions (P1: WCSS clustering, P2: CKA similarity, P3: Zero-shot accuracy)
- Section 2: Experimental Setup (ModelZooDataset + SANE + ViTModelZoo, Hierarchical VAE)
- Section 4: Related Work (ProbeGen, SANE, Architecture-Conditioned MLP baselines)
- Section 5: Phase 2B Readiness (SH1, SH2, SH3 → hypothesis generation seeds)

**Phase 2A → Phase 2B Mapping:**
- SH1 (existence) → H-E1 (Dataset Coverage Audit)
- SH2 (mechanism) → H-M-integrated (4-step causal chain)
- SH3 (comparison) → Phase 5 (Baseline Comparison, not in Phase 2B scope)
- Causal steps (4) → Integrated into single H-M hypothesis (tight coupling)
- Scope boundaries → Condition hypotheses skipped (documented as constraints)

### C. Workflow Metadata

**Phase 2B Workflow:** phase2b-planning
**Execution Mode:** UNATTENDED (#batch-mode)
**Research Mode:** Incremental (Phase 2A data loaded)
**MCP Calls:** 2 (scientificmethod for H-E1 + H-M-integrated)
**Output File:** `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_wsl/docs/youra_research/02b_verification_plan.md`

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RISK ANALYSIS FROM PHASE 2A ASSUMPTIONS (A1-A5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Risk R1: Insufficient Dataset Coverage**

**Source Assumption:** A1 - Model zoos contain sufficient cross-architecture coverage (≥30 models per architecture-task cell) for statistical validity

**Description:** Dataset audit reveals <70% of architecture-task cells meet the ≥30 model threshold. Sparse cells create underpowered statistical tests where clustering results may reflect sampling noise rather than genuine task structure. Critical cells (ImageNet-CNN, ImageNet-Transformer) may also be sparse.

**Affected Hypotheses:** H-E1 (existence gate), H-M-integrated (statistical validity of WCSS bootstrap test)

**Severity:** HIGH (blocks entire pipeline if critical cells sparse)

**Mitigation Strategy:**
1. **Prevention:** Pre-Phase 1 audit with clear thresholds (≥70% overall OR critical cells covered)
2. **Detection:** Coverage heatmap reveals sparse regions immediately
3. **Response:**
   - PIVOT (50-70% coverage): Treat sparse cells as robustness test (natural experiment testing generalization)
   - SCOPE (<50% coverage, critical cells OK): Reduce scope to well-covered architecture families only
   - ABORT (<50% coverage, critical cells sparse): Insufficient data, need collection phase before proceeding

**Early Warning Indicators:**
- Coverage heatmap shows concentrated sparsity in RNN-vision or MLP-NLP regions
- Critical cells (ImageNet-CNN, ImageNet-Transformer, CIFAR-CNN) contain <20 models

---

**Risk R2: Noisy Task Labels**

**Source Assumption:** A2 - Task labels from model zoo metadata are accurate and granular enough to define meaningful task clusters

**Description:** Model zoo metadata contains mislabeled or overly coarse task annotations (e.g., "ImageNet classifier" conflates ImageNet-1K with ImageNet-21K). Supervised labels introduce noise into contrastive learning, causing latent space to discover spurious correlations instead of genuine task structure.

**Affected Hypotheses:** H-M-integrated (contrastive learning stage relies on label quality)

**Severity:** MEDIUM (mitigated by zero-shot transfer validation)

**Mitigation Strategy:**
1. **Prevention:** Validate task labels via model config inspection (match reported task to architecture design)
2. **Detection:** Zero-shot transfer accuracy on adversarially mislabeled models <85% indicates label dependency
3. **Response:**
   - PIVOT: Use unsupervised clustering (no labels) + verify via zero-shot transfer
   - SCOPE: Restrict to high-confidence labels only (verified via metadata cross-check)
   - ABORT (if zero-shot fails entirely): Labels fundamentally unreliable, hypothesis infeasible

**Early Warning Indicators:**
- Zero-shot task prediction on corrupted metadata models <85% accuracy
- Contrastive loss plateaus early without discovering latent structure

---

**Risk R3: Information Loss in Pooling**

**Source Assumption:** A3 - Permutation-invariant pooling (Level 2) retains sufficient task-relevant information despite discarding neuron-level details

**Description:** Pooling layer summaries (mean/sum over neuron clusters) discards critical fine-grained weight patterns needed for cross-architecture alignment. Reconstruction task accuracy degrades >30%, indicating task-relevant information lost. Cross-architecture clustering fails because coarse summaries are too lossy.

**Affected Hypotheses:** H-M-integrated (hierarchical VAE Level 2 pooling step)

**Severity:** MEDIUM (empirical validation via reconstruction test)

**Mitigation Strategy:**
1. **Prevention:** Measure reconstruction task accuracy after pooling (accept if degradation <30%)
2. **Detection:** Task prediction accuracy drops >30% when using pooled representations vs raw weights
3. **Response:**
   - PIVOT: Replace mean/sum pooling with Set Transformer with memory (learnable pooling)
   - SCOPE: Reduce pooling aggressiveness (pool over smaller neuron groups)
   - ABORT (if >50% degradation): Pooling fundamentally incompatible with task preservation

**Early Warning Indicators:**
- Reconstruction accuracy <70% on held-out models
- Layer-summary representations fail to predict tasks better than random (accuracy <55% on 10-class dataset)

---

**Risk R4: Training Procedure Confound**

**Source Assumption:** A4 - Training-induced regularities (augmentation strategies, optimization dynamics) are orthogonal to task-induced structure, or at least separable

**Description:** Clustering reflects training procedures (data augmentation strategies, optimizer choice, learning rate schedules) rather than task labels. Same-augmentation different-task models cluster more tightly than same-task different-augmentation models, invalidating the task-invariance claim. Training regularities dominate task constraints.

**Affected Hypotheses:** H-M-integrated (clustering tightness interpretation)

**Severity:** HIGH (invalidates core novelty claim if not disentangled)

**Mitigation Strategy:**
1. **Prevention:** Explicit ablation comparing same-task different-procedure vs different-task same-procedure clustering
2. **Detection:** Procedure-based clustering is tighter than task-based clustering (reversed hypothesis)
3. **Response:**
   - PIVOT: Add training-procedure as additional controlled variable (normalize out via conditioning)
   - SCOPE: Restrict to models trained with identical procedures (reduces dataset coverage)
   - ABORT (if procedure effect >>task effect): Training regularities are the dominant signal, not tasks

**Early Warning Indicators:**
- Same-augmentation pairs cluster tighter than same-task pairs (procedure>task signal)
- Ablation shows procedure accounts for >60% of clustering variance

---

**Risk R5: Architecture Subspace Incompatibility**

**Source Assumption:** A5 - Architecture families (CNN, Transformer, RNN, MLP) are metrically compatible — cross-architecture alignment is mathematically feasible

**Description:** Phase 1 CKA gate reveals architecture subspaces are metrically incompatible (same-task CKA <0.6, indicating no alignment exists). No linear or nonlinear transformation can bridge CNN weight space to Transformer weight space while preserving task structure. Cross-architecture hypothesis is infeasible.

**Affected Hypotheses:** H-M-integrated (Phase 1 CKA feasibility gate)

**Severity:** CRITICAL (early falsification, blocks entire mechanism)

**Mitigation Strategy:**
1. **Prevention:** Phase 1 CKA+UMAP feasibility gate provides early stop signal before expensive VAE training
2. **Detection:** CKA same-task <0.5 OR different-task >0.5 (subspaces not separable)
3. **Response:**
   - PIVOT: Try nonlinear alignment (kernel CKA, Procrustes with polynomial features)
   - SCOPE: Reduce to architecture pairs with known compatibility (CNN-MLP only)
   - ABORT (if CKA same-task <0.4): No alignment exists, cross-architecture hypothesis fundamentally infeasible

**Early Warning Indicators:**
- CKA same-task <0.5 (below threshold for meaningful alignment)
- UMAP visualization shows architecture clusters completely separated (no task-based overlap)

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Mitigation Priority |
|------|--------|---------------------|----------|---------------------|
| R1 | A1 | H-E1, H-M-integrated | HIGH | 1 (Pre-Phase 1 audit) |
| R2 | A2 | H-M-integrated | MEDIUM | 3 (Zero-shot validation) |
| R3 | A3 | H-M-integrated | MEDIUM | 4 (Reconstruction test) |
| R4 | A4 | H-M-integrated | HIGH | 2 (Ablation study) |
| R5 | A5 | H-M-integrated | CRITICAL | 1 (Phase 1 CKA gate) |

---

### 4.3 Baseline Failure Patterns

| Baseline Method | Limitation | Risk Mapping | Our Mitigation |
|-----------------|------------|--------------|----------------|
| ProbeGen | Limited to single architecture type, does not handle heterogeneous collections | R5 (architecture compatibility) | Hierarchical design explicitly handles cross-architecture via Level 2 pooling + Level 3 Transformer |
| SANE | Heterogeneous extension incomplete, no explicit cross-architecture alignment mechanism | R5 (architecture compatibility) | Architecture-type-aware tokenization + CKA feasibility gate validates alignment before training |
| Architecture-Conditioned MLP | Does not exploit task-invariant structure, treats architecture as opaque feature | R4 (training procedure confound) | Explicit ablation tests task vs procedure effects, contrastive learning discovers latent structure |

---

### 4.4 Risk Summary

**Critical Risks:** 1 (R5 - Architecture subspace incompatibility)
**High Risks:** 2 (R1 - Dataset coverage, R4 - Training procedure confound)
**Medium Risks:** 2 (R2 - Noisy labels, R3 - Pooling information loss)
**Low Risks:** 0

**Overall Risk Profile:** HIGH — Two MUST_WORK gates (H-E1 dataset audit, H-M-integrated CKA feasibility) provide early falsification before expensive training. Training procedure ablation (R4) is essential to validate core novelty claim.

**Recommended Mitigation Order:**
1. R5 (CKA gate) + R1 (dataset audit) — Pre-Phase 1 blockers
2. R4 (ablation study) — Phase 4 validation of core claim
3. R2 (zero-shot transfer) — Phase 4 robustness check
4. R3 (reconstruction test) — Phase 2-3 design validation

---
