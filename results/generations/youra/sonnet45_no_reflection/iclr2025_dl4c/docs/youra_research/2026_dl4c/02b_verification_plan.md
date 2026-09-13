# Verification Plan: Aspect-Factorized Multi-Objective Code Alignment

**Date:** 2026-05-11
**Hypothesis ID:** H-AspectFactorization-v1
**Confidence:** 0.8
**Total Hypotheses:** 2

---

## 0. Established Facts & Scope Reduction

**BUILD_ON (Do NOT re-verify):**
- Current single-objective alignment methods (PPOCoder, CodeRL, RLHF/DPO) optimize in isolation
- Multi-objective optimization via weighted rewards requires manual per-domain tuning
- Existing code benchmarks (HumanEval, MBPP) measure execution correctness via unit tests
- Multi-task learning and disentanglement methods push orthogonal subspaces in representation learning

**PROVE_NEW (Generate hypotheses for these):**
- Static analysis tools (CodeQL, SonarQube) and profiling (pytest-benchmark) provide reliable metrics for quality/security/efficiency measurement

**Scope Reduction:** 40% of claims are BUILD_ON → Focus verification on 1 PROVE_NEW claim + novel mechanisms

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under multi-objective code generation contexts (correctness, quality, security, efficiency), if human expert code modifications exhibit aspect-dominant directional structure in outcome space (validated via spectral analysis of commit-level causal edits with representation-space alignment), then aspect-factorized policy architectures (gated LoRA adapters with orthogonality constraints) enable post-training multi-objective controllability on existing benchmarks, because the model exploits empirically discovered latent geometry that mirrors human expert cognitive factorization of programming concerns.

### 1.2 Alternative Hypothesis (H0)

There is no significant aspect-dominant structure in human code modifications (flat eigenspectrum λ₄/λ₅ ≤ 2.0, or high cross-aspect coupling >0.3×), indicating multi-objective code alignment is intrinsically entangled and architectural factorization provides no controllability advantage over standard weighted multi-objective RL.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | GitHub Commit Corpus (Multi-Aspect Labeled) (standard) | Provides real-world labeled data for empirical separability validation (Phase 1). Commit-level causal edits are natural experiments showing human expert aspect-specific modifications. |
| **Model** | CodeLlama-7B | Standard pretrained code model with sufficient capacity for LoRA adaptation. 7B size balances expressiveness with computational feasibility (~100 GPU-hours training budget). |

**Dataset Details:**
- Source: GitHub public repositories, filtered for minimal-diff commits (AST distance <20) with aspect labels (security, refactor, performance, bugfix)
- Path: To be mined via GitHub API + commit message analysis + expert validation subset (n=500)

**Model Details:**
- Type: Pretrained Code LLM
- Source: Meta AI open-source release

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Weighted PPOCoder | Grid search over 25 weight combinations w∈[0,1]^4 for (correctness, quality, security, efficiency), train separate models to estimate Pareto frontier | Various |
| LoRA-only (no factorization) | Standard LoRA fine-tuning with multi-objective loss but no architectural separation or orthogonality constraints | - |
| LoRA + Orthogonality (no gating) | LoRA adapters with L_ortho regularization but no learned routing - tests necessity of functional separation beyond geometric orthogonality | - |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Static analysis tools (CodeQL, SonarQube) and profiling (pytest-benchmark) provide reliable and construct-valid metrics for quality, security, efficiency | Phase 0 validation required: ICC ≥0.8 for test-retest reliability, r≥0.7 correlation with blinded expert judgment on n=200 sample | If metrics fail validation, covariance structure becomes measurement artifact - cannot interpret separability. Mitigation: drop unreliable metrics, proceed with ≥3/4 validated metrics |
| A2 | Minimal-diff commits (AST edit distance <20) with commit labels (security, refactor, performance, bugfix) represent approximately single-aspect intent | Phase 1C validation: n=500 commits with blinded expert tagging of primary vs secondary aspects. Target purity >70% (one aspect rated major, others minor/none) | If purity <70%, mixture noise inflates apparent separability (Simpson's paradox). Mitigation: mixture modeling with expert-weighted covariance correction |
| A3 | Pretrained code models (CodeLlama-7B) encode geometry reflecting human code patterns from pretraining, enabling representation-metric alignment | Phase 1B CCA test: if model geometry were random relative to outcome structure, CCA coefficients would be near-zero. Target: CCA >0.7 for ≥3/4 aspects | If CCA <0.5, model geometry doesn't reflect outcome structure - architectural factorization becomes external supervision not latent discovery. Still useful but different theoretical claim |
| A4 | Gated routing with sparsity constraints (≤2 aspects per token) enforces functional separation beyond geometric orthogonality | Ablation test comparing LoRA-only vs LoRA+orthogonal vs LoRA+gated. If gating provides no controllability improvement, simpler architecture sufficient | If gating doesn't help, weight orthogonality alone is sufficient - removes architectural complexity. Not a failure, just simpler solution |
| A5 | Post-training steering operates in approximately linear regime within local controllability band (α ∈ [0, 1-2]) | Controllability band analysis: measure steering as function of α, identify monotonic interval. Nonlinearity beyond band is expected and acceptable | If linearity breaks down within narrow band (<0.4 width), practical controllability is limited. Mitigation: report band width explicitly, don't over-claim range |

### 1.6 Research Gap & Novelty

Three-part contribution:
1. **Empirical discovery**: First systematic quantification of aspect-dominant structure in real code modifications via spectral analysis with directional stability tests and representation-space alignment validation
2. **Architectural innovation**: Gated aspect-factorized adapters validated through rotation test (exploits natural geometry, not imposed flexibility) with ablations showing necessity of functional separation
3. **Validation methodology**: Permutation-tested separability + sample-efficiency gaps + counterfactual human discrimination establish new validation standard for multi-objective alignment claims

**Differentiation:**
- vs. Weighted multi-objective RL: We validate data-level separability first, don't assume conflict
- vs. General disentanglement: Apply to alignment for code with intervention validation + human feedback
- vs. PPOCoder: Multi-aspect simultaneous optimization + post-training controllability

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M-Integrated | MECHANISM | MUST_WORK | H-E1 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Aspect-Dominant Structure Existence

**Statement**: Under multi-objective code generation contexts with GitHub commit data (10K minimal-diff commits), if human expert modifications are analyzed via spectral decomposition of residual covariance matrices, then aspect-dominant directional structure will emerge with median cross-aspect coupling ≤0.2× primary effect and spectral gap λ₄/λ₅>2.0, because developers cognitively factorize programming concerns into separable dimensions.

**Rationale**: This hypothesis validates the foundational empirical assumption that human code modifications exhibit separable structure across quality aspects. Without this separability in real data, the entire architectural factorization approach lacks empirical grounding.

**Variables**:
- Independent: Commit Type (categorical: security, refactor, performance, bugfix)
- Dependent: Cross-Aspect Coupling (median ratio ≤0.2), Spectral Gap (λ₄/λ₅>2.0)
- Controlled: Metric Reliability (ICC≥0.8, construct validity r≥0.7), Edit Size, File Entropy

**Verification Protocol**:
1. Collect 10K minimal-diff commits (AST distance <20) from GitHub with aspect labels via message parsing + expert validation (n=500 subset for purity >70%)
2. Compute metrics: Δcorrectness (test pass rate), Δquality (SonarQube), Δsecurity (CodeQL alerts), Δefficiency (pytest-benchmark)
3. Perform residual covariance analysis after confound regression (edit size, file entropy), eigenanalysis, permutation test (1000 shuffles)
4. Measure directional stability via on-axis projection z-scores and leave-one-repo-out cross-validation
5. Validate commit purity via expert annotation; apply mixture modeling if purity <70%

**Success Criteria** (MUST_WORK):
- Primary: Cross-aspect coupling ≤0.2× (95% CI), spectral gap λ₄/λ₅>2.0 (exceeds 95th percentile of permutation null), on-axis projection z-score >2.0
- Secondary: Purity >70%, metric validation passed (ICC≥0.8, r≥0.7)

**Failure Response**:
- IF fails (flat spectrum λ₄/λ₅≤2.0 or coupling >0.3×): ABANDON architectural factorization → Publish negative result that multi-objective code alignment is intrinsically entangled → Pivot to co-adaptive methods

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.6 Prediction P1, Section 5 SH1

---

#### H-M-Integrated: Four-Step Causal Chain Mechanism

**Statement**: Under conditions where H-E1 confirms empirical separability, if aspect-factorized architectures (gated LoRA adapters) are trained on natural axes from eigenanalysis, then the complete causal chain operates: (M1) representation-metric alignment emerges (CCA>0.7 for ≥3/4 aspects), (M2) natural-axis training reaches controllability 30% faster than rotated axes, (M3) gating provides functional separation beyond orthogonality, and (M4) post-training steering enables human-validated controllability (band width ≥1.0, discrimination ≥60%), because architectural inductive bias matches discovered latent geometry.

**Rationale**: This integrated mechanism hypothesis tests the full causal story from outcome geometry → representation alignment → architectural exploitation → behavioral controllability. Each sub-mechanism (M1-M4) has specific falsification conditions, enabling fine-grained diagnosis of failure modes.

**Variables**:
- Independent: Architectural Configuration (LoRA-only / LoRA+orthogonal / LoRA+gated), Training Axis (natural / rotated)
- Dependent: CCA coefficients (M1), Sample Efficiency Gap % (M2), Controllability Band Width (M3-M4), Human Discrimination % (M4)
- Controlled: Base Model (CodeLlama-7B), Training Data (10K commits, purity >70%), Steering Coefficient α∈[0,3]

**Verification Protocol**:
1. (M1) Freeze CodeLlama-7B, extract hidden states at layers [8,16,24] for pre/post commit code, compute CCA between metric eigenvectors and representation PCA directions
2. (M2) Train LoRA+gated on both natural and rotated axes for 50K steps, measure step at which band width≥1.0 first achieved, compute efficiency gap percentage and rotation degradation
3. (M3) Ablation study: compare final controllability metrics across LoRA-only vs LoRA+orthogonal vs LoRA+gated architectures
4. (M4) Steering experiments with α∈[0,3] to identify local controllability bands (monotonic target increase, <5% correctness degradation, <10% other-metric degradation)
5. Human validation: n=100 code review tasks with correct-aspect vs mismatched-aspect steering, measure preference discrimination

**Success Criteria** (MUST_WORK):
- M1: CCA >0.7 for ≥3/4 aspects at any layer [8,16,24]
- M2: ≥30% sample-efficiency gap + >30% degradation under rotation
- M3: Gating shows measurable controllability improvement over LoRA+orthogonal
- M4: Band width ≥1.0 + ≥60% human discrimination accuracy

**Failure Response**:
- IF M1 fails (CCA <0.5): Theoretical claim shifts from "exploiting latent geometry" to "imposing external structure" → Still useful but different contribution
- IF M2 fails (no efficiency gap): Architecture is flexible not structure-aligned → Simpler baseline sufficient
- IF M3 fails (gating no benefit): Weight orthogonality alone sufficient → Remove architectural complexity
- IF M4 fails (narrow bands <0.4 or chance discrimination): Controllability fragile → Report limitations explicitly

**Dependencies**: H-E1 (requires empirical separability confirmation)

**Source**: Phase 2A Section 1.3 Causal Mechanism (4 steps), Section 1.6 Predictions P2-P3, Section 5 SH2

---

---

## 3. Risk Analysis

### 3.1 Identified Risks

**Risk R1: Metric Unreliability**
- **Source:** A1 (Static analysis tools reliability)
- **Description:** If CodeQL, SonarQube, or pytest-benchmark fail validation (ICC<0.8 or construct validity r<0.7), covariance structure becomes measurement artifact
- **Severity:** High (blocks H-E1 interpretation)
- **Likelihood:** Medium (tools are established but validation needed)

**Risk R2: Commit Label Impurity**
- **Source:** A2 (Minimal-diff commits represent single-aspect intent)
- **Description:** If purity <70% (commits affect multiple aspects), mixture noise inflates apparent separability via Simpson's paradox
- **Severity:** High (invalidates H-E1 separability claims)
- **Likelihood:** Medium (depends on label quality and expert agreement)

**Risk R3: Weak Representation-Metric Alignment**
- **Source:** A3 (Pretrained models encode human code patterns)
- **Description:** If CCA <0.5, model geometry doesn't reflect outcome structure—architectural factorization becomes external supervision not latent discovery
- **Severity:** Medium (shifts theoretical claim but doesn't invalidate method)
- **Likelihood:** Medium (pretrained models may not encode aspect structure)

**Risk R4: Gating Redundancy**
- **Source:** A4 (Gated routing enforces functional separation)
- **Description:** If gating provides no controllability improvement over LoRA+orthogonal, architectural complexity is unnecessary
- **Severity:** Low (simplifies solution but doesn't fail hypothesis)
- **Likelihood:** Low (gating should provide separation)

**Risk R5: Narrow Controllability Bands**
- **Source:** A5 (Post-training steering operates in linear regime)
- **Description:** If linearity breaks down within narrow band (<0.4 width), practical controllability is limited
- **Severity:** Medium (limits applicability)
- **Likelihood:** Medium (local linearity not guaranteed)

### 3.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 | A1 | H-E1 (blocks), H-M-Integrated (cascades) | High |
| R2 | A2 | H-E1 (invalidates) | High |
| R3 | A3 | H-M-Integrated (M1 component) | Medium |
| R4 | A4 | H-M-Integrated (M3 component) | Low |
| R5 | A5 | H-M-Integrated (M4 component) | Medium |

### 3.3 Mitigation Strategies

**R1 Mitigation: Metric Unreliability**
1. **Prevention:** Run Phase 0 metric validation experiment BEFORE Phase 1 data collection (ICC≥0.8, r≥0.7 with expert judgment on n=200)
2. **Detection:** Monitor test-retest reliability during pilot runs; check construct validity correlation
3. **Response:**
   - If 3/4 metrics pass: Proceed with validated metrics only, drop unreliable ones
   - If <3/4 pass: ABANDON covariance analysis, PIVOT to supervised quality prediction without separability claims

**R2 Mitigation: Commit Label Impurity**
1. **Prevention:** Expert annotation of n=500 commits for purity validation before full analysis; measure primary-aspect dominance
2. **Detection:** Compute purity score (percentage where one aspect is rated major, others minor/none); target >70%
3. **Response:**
   - If purity 60-70%: Apply mixture modeling with expert-weighted covariance correction
   - If purity <60%: ABANDON aspect-dominant claims, PIVOT to multi-aspect entanglement analysis, publish negative result

**R3 Mitigation: Weak Representation-Metric Alignment**
1. **Prevention:** Run CCA analysis early (Phase 1B) before committing to architectural design
2. **Detection:** CCA coefficients <0.5 for majority of aspects indicate weak alignment
3. **Response:**
   - If CCA 0.5-0.7: Proceed but report as "moderate alignment," adjust theoretical claims to "guided supervision"
   - If CCA <0.5: Shift claim from "exploiting latent geometry" to "imposing external structure"—still useful contribution, different theory

**R4 Mitigation: Gating Redundancy**
1. **Prevention:** Include LoRA+orthogonal ablation in experimental design from start
2. **Detection:** Compare final controllability metrics across all three architectures (LoRA-only, LoRA+orthogonal, LoRA+gated)
3. **Response:**
   - If gating shows no benefit: Remove gating, use simpler LoRA+orthogonal architecture—not a failure, just efficiency gain

**R5 Mitigation: Narrow Controllability Bands**
1. **Prevention:** Test steering across full α∈[0,3] range with fine granularity (0.2 increments)
2. **Detection:** Measure band width where monotonicity holds with <5% correctness degradation
3. **Response:**
   - If band width 0.4-1.0: Report limited but usable controllability
   - If band width <0.4: Report narrow applicability, recommend future work on extending linear regime

### 3.4 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Metric Unreliability | A1 | High | H-E1, H-M-Integrated | Phase 0 validation, drop unreliable metrics if needed |
| R2 | Commit Label Impurity | A2 | High | H-E1 | Expert validation n=500, mixture modeling if purity <70% |
| R3 | Weak Alignment (CCA) | A3 | Medium | H-M-Integrated (M1) | Early CCA test, adjust theoretical claims if <0.5 |
| R4 | Gating Redundancy | A4 | Low | H-M-Integrated (M3) | Ablation study, simplify if no benefit |
| R5 | Narrow Bands | A5 | Medium | H-M-Integrated (M4) | Full α range test, report limited applicability if needed |

**Risk Distribution:**
- Critical: 0
- High: 2 (R1, R2)
- Medium: 2 (R3, R5)
- Low: 1 (R4)

---

## 4. Hierarchical Structure

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
    DEPENDENCY GRAPH (DAG) - 2 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1: Aspect-Dominant Structure Existence
         │
         │ Gate 1: MUST_WORK
         │ → If FAIL: ABANDON (publish negative result)
         │
         ▼
[Level 1 - Mechanism: Causal Chain]
    H-M-Integrated: 4-Step Mechanism
         │         (M1→M2→M3→M4)
         │
         │ Gate 2: MUST_WORK
         │ → If M1 fails: Shift theoretical claim
         │ → If M2 fails: Simpler architecture
         │ → If M3 fails: Remove gating
         │ → If M4 fails: Report limitations
         │
         ▼
    [Terminal: Phase 4 Complete]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M-Integrated (sequential execution)
Parallelization: None (strict dependency chain)
═══════════════════════════════════════════════════════════
```

**Verification Phases:**

**Phase 1 - Foundation (Gate: MUST_WORK)**
| Hypothesis | Test | Success Criteria | Failure Response |
|------------|------|------------------|------------------|
| H-E1 | Empirical separability | Cross-coupling ≤0.2×, λ₄/λ₅>2.0 | ABANDON → Publish negative result |

→ **Gate 1**: If H-E1 fails, multi-objective alignment is intrinsically entangled. Stop verification, publish finding.

**Phase 2 - Mechanism Chain (Gate: MUST_WORK)**
| Component | Test | Success Criteria | Failure Response |
|-----------|------|------------------|------------------|
| M1 | Representation-metric alignment | CCA >0.7 for ≥3/4 aspects | Shift claim to "guided supervision" |
| M2 | Sample efficiency | ≥30% gap, >30% rotation degradation | Simpler architecture sufficient |
| M3 | Architectural necessity | Gating improves over orthogonal | Remove gating complexity |
| M4 | Controllability | Band width ≥1.0, ≥60% discrimination | Report narrow applicability |

→ **Gate 2**: Each sub-mechanism has specific pivot. Full chain success = strong contribution; partial = documented limitations.

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Parallelizable |
|-------|-----------|---------------|-----------|----------------|
| 0 | H-E1 | None | MUST_WORK | - |
| 1 | H-M-Integrated | H-E1 | MUST_WORK | No |

**Execution Constraints:**
- **Strict Sequential**: H-E1 must complete before H-M-Integrated begins
- **No Parallelization**: 2 hypotheses in single dependency chain
- **Early Termination**: Gate 1 failure stops entire verification pipeline

---

## 5. Timeline Planning

### 5.1 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
    VERIFICATION TIMELINE - 2 Hypotheses
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ Week 1-2 │ Week 3   │ Week 4   │ Week 5   │ Week 6
─────────────────────┼──────────┼──────────┼──────────┼──────────┼────────
PHASE 1: Foundation
  H-E1 (Separability)│ ████████ │          │          │          │
  [Gate 1]           │          │ ◆        │          │          │
─────────────────────┼──────────┼──────────┼──────────┼──────────┼────────
PHASE 2: Mechanism Chain
  H-M-Integrated     │          │ ████████ │ ████████ │ ████████ │
   • M1 (CCA)        │          │ ████     │          │          │
   • M2 (Efficiency) │          │          │ ████     │          │
   • M3 (Gating)     │          │          │          │ ████     │
   • M4 (Control)    │          │          │          │          │ ████
  [Gate 2]           │          │          │          │          │     ◆
─────────────────────┼──────────┼──────────┼──────────┼──────────┼────────
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════════════
```

**Phase Breakdown:**
- **Week 1-2**: H-E1 empirical separability validation (data collection, metric validation, covariance analysis)
- **Week 3**: H-M-Integrated M1 (representation-metric CCA analysis)
- **Week 4**: H-M-Integrated M2 (sample efficiency gap measurement with rotation test)
- **Week 5**: H-M-Integrated M3 (architectural ablation: LoRA variants)
- **Week 6**: H-M-Integrated M4 (controllability bands + human discrimination validation)

### 5.2 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M-Integrated (M1→M2→M3→M4)

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 4 (H-M sub-mechanisms)

Slack Available: 0 weeks (strict sequential dependencies)

Bottlenecks:
- H-E1 (Gate 1): 2 weeks - data collection + validation
- M2 (Sample Efficiency): Requires full training runs (2 configs × 50K steps)

Early Termination Points:
- Week 2: Gate 1 failure → STOP, publish negative result
- Week 3: M1 CCA <0.5 → Shift theoretical claim
- Week 4: M2 no efficiency gap → Simplify architecture
- Week 5: M3 gating redundant → Remove complexity
- Week 6: M4 narrow bands → Document limitations

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 2
- Existence: 1 (H-E1)
- Mechanism: 1 (H-M-Integrated with 4 sub-mechanisms)

Verification Phases: 2
1. Foundation (H-E1) - Empirical separability
2. Mechanism Chain (H-M-Integrated) - 4-step causal validation

Total Duration: 6 weeks
Critical Path Length: 6 weeks (100% on critical path)
Execution Mode: Sequential chain (no parallelization)

Computational Resources:
- H-E1: Data mining (GitHub API), metric computation (~10 GPU-hours)
- M1: CCA analysis (~100 GPU-hours for representation extraction)
- M2: Training runs (2 configs × 50K steps × ~40 GPU-hours = ~80 GPU-hours)
- M3: Ablation (3 architectures × ~40 GPU-hours = ~120 GPU-hours)
- M4: Steering + human validation (~20 GPU-hours + $500 for n=100 reviews)

Total Estimated: ~330 GPU-hours + $500 human annotation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.4 Execution Order

**Step 1**: Execute H-E1 (Foundation) - Week 1-2
- Collect 10K minimal-diff commits from GitHub
- Run Phase 0 metric validation (ICC≥0.8, r≥0.7)
- Compute residual covariance, eigenanalysis, permutation test
- Validate commit purity (expert annotation n=500)

**Step 2**: Evaluate Gate 1 (Week 2 end)
- **PASS** (cross-coupling ≤0.2×, λ₄/λ₅>2.0) → Proceed to H-M-Integrated
- **FAIL** (flat spectrum or coupling >0.3×) → ABORT, publish negative result on intrinsic entanglement

**Step 3**: Execute H-M-Integrated M1 (Representation Alignment) - Week 3
- Freeze CodeLlama-7B, extract hidden states at layers [8,16,24]
- Compute CCA between metric eigenvectors and representation PCA
- **Decision**: CCA <0.5 → shift theoretical claim but continue

**Step 4**: Execute H-M-Integrated M2 (Sample Efficiency) - Week 4
- Train LoRA+gated on natural axes and rotated axes (50K steps each)
- Measure step to controllability threshold, compute efficiency gap
- Run rotation test for degradation measurement
- **Decision**: No gap → simplify to LoRA+orthogonal

**Step 5**: Execute H-M-Integrated M3 (Architectural Necessity) - Week 5
- Train all 3 variants: LoRA-only, LoRA+orthogonal, LoRA+gated
- Compare final controllability metrics across architectures
- **Decision**: Gating no benefit → remove gating complexity

**Step 6**: Execute H-M-Integrated M4 (Controllability Validation) - Week 6
- Steering experiments with α∈[0,3] to identify local bands
- Measure band width (monotonic target increase, degradation limits)
- Human code review discrimination (n=100 tasks, correct vs mismatched steering)
- **Decision**: Narrow bands <0.4 → document limited applicability

**Step 7**: Evaluate Gate 2 (Week 6 end)
- Assess which sub-mechanisms (M1-M4) passed
- Full success (all 4) → Strong contribution
- Partial success → Document limitations, publish graded results

**Final**: Verification complete, proceed to Phase 5 baseline comparison

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Under multi-objective code generation contexts (correctness, quality, security, efficiency), if human expert code modifications exhibit aspect-dominant directional structure in outcome space (validated via spectral analysis of commit-level causal edits with representation-space alignment), then aspect-factorized policy architectures (gated LoRA adapters with orthogonality constraints) enable post-training multi-objective controllability on existing benchmarks, because the model exploits empirically discovered latent geometry that mirrors human expert cognitive factorization of programming concerns.

**Supporting Evidence:**
1. **Causal Mechanism**: Four-step chain from outcome structure → representation alignment → architectural exploitation → controllability, each with specific empirical tests
2. **Established Theory**: Multi-task learning and disentanglement methods demonstrate orthogonal subspaces in representation learning (BUILD_ON claim)
3. **Testable Predictions**: Spectral gap λ₄/λ₅>2.0, CCA>0.7, ≥30% sample-efficiency gap, controllability bands ≥1.0

**Strengths:**
- **Geometry-first approach**: Validates empirical separability before architectural commitment, avoiding premature factorization
- **Complete falsifiable pipeline**: Each mechanism step (M1-M4) has specific failure conditions and pivot strategies
- **Graded outcomes**: Partial success still yields valuable contributions (e.g., CCA 0.5-0.7 shifts claim but remains useful)

**Expected Outcomes:**
- Primary: Aspect-dominant structure confirmed (cross-coupling ≤0.2×, spectral gap >2.0)
- Secondary: Representation-metric alignment emerges (CCA >0.7 for ≥3/4 aspects)
- Tertiary: Natural-axis training shows 30% efficiency advantage over rotated axes

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant aspect-dominant structure in human code modifications (flat eigenspectrum λ₄/λ₅ ≤ 2.0, or high cross-aspect coupling >0.3×), indicating multi-objective code alignment is intrinsically entangled and architectural factorization provides no controllability advantage over standard weighted multi-objective RL.

**Counter-Arguments:**
1. **Measurement Artifact Risk**: Apparent separability could arise from noisy metrics (R1) or repository clustering rather than genuine cognitive factorization
2. **Commit Label Impurity**: If purity <70% (R2), mixture noise inflates separability via Simpson's paradox—commits actually affect multiple aspects simultaneously
3. **Weak Model-Outcome Alignment**: Pretrained models may not encode aspect-specific geometry (R3), making architectural factorization external supervision not latent discovery

**Potential Failure Points:**
- **H-E1 failure**: Flat spectrum or failed permutation test → No empirical separability exists → Entire thesis collapses
- **M1 failure (CCA <0.5)**: Model geometry doesn't reflect outcome structure → Architectural approach is imposed not discovered
- **M2 failure (no efficiency gap)**: Natural axes provide no advantage → Architecture is flexible not structure-aligned
- **M4 failure (narrow bands <0.4)**: Practical controllability too limited → Method lacks real-world applicability

**Conditions Under Which H0 Would Be Supported:**
- If λ₄/λ₅ ≤ 2.0 or permutation test fails (p>0.05) → Multi-objective code is intrinsically entangled
- If cross-aspect coupling >0.3× → Human modifications are not cognitively factorized
- If rotation test shows no degradation → Architecture doesn't exploit specific geometry
- If all baselines (weighted PPOCoder) achieve similar controllability → No architectural advantage

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-AspectFactorization-v1 presents a testable claim that aspect-dominant structure in human code modifications enables architectural factorization for multi-objective controllability. However, the null hypothesis raises valid concerns that apparent separability may be measurement artifact, repository clustering, or that multi-objective code alignment is intrinsically entangled.

**Resolution Path:**

The verification plan addresses this dialectic through a four-tier validation strategy:

1. **Tier 1 - Metric Validation (Phase 0)**: Establishes measurement reliability (ICC≥0.8, r≥0.7) before analyzing separability, mitigating R1
2. **Tier 2 - Empirical Separability (H-E1)**: Permutation testing, directional stability, and leave-one-repo-out analysis rule out statistical artifacts
3. **Tier 3 - Mechanism Decomposition (M1-M4)**: Each causal step has specific success/failure criteria, enabling fine-grained diagnosis
4. **Tier 4 - Robustness Testing**: Rotation test, distribution shift (security-CTF), and human discrimination validate beyond in-distribution performance

**Conditions for Thesis Support:**
- H-E1 passes (cross-coupling ≤0.2×, λ₄/λ₅>2.0, permutation p<0.05)
- M1 passes (CCA >0.7 for ≥3/4 aspects) → Model geometry reflects outcome structure
- M2 passes (≥30% efficiency gap + rotation degradation) → Natural axes provide advantage
- M4 passes (band width ≥1.0, human discrimination ≥60%) → Practical controllability achieved

**Conditions for Antithesis Support:**
- H-E1 fails (flat spectrum or failed permutation) → Intrinsic entanglement confirmed, publish negative result
- M1 fails (CCA <0.5) → Architectural factorization is external supervision, not latent discovery
- M2 fails (no efficiency gap, no rotation effect) → Architecture is flexible baseline, not structure-aligned

**Nuanced Outcome Possibilities:**
1. **Full Thesis Support**: All gates pass → Aspect-factorization validated, strong contribution across empirical + architectural + methodological dimensions
2. **Partial Thesis Support**: H-E1 + M1 pass, M2-M4 mixed → Separability exists but architectural exploitation limited, refine approach
3. **Theoretical Pivot**: H-E1 + M1 pass, M2 fails → Shift claim from "latent discovery" to "guided supervision," still useful contribution with different theory
4. **Antithesis Support**: H-E1 fails → Multi-objective code alignment is intrinsically entangled, redirect field toward co-adaptive methods, publish high-impact negative result

### 6.4 Robustness Assessment

**Dialectical Robustness:**

The verification plan demonstrates dialectical strength through:
- **Pre-registered falsification criteria**: H0 support conditions defined before experiments, preventing post-hoc rationalization
- **Graded pivot strategies**: Each failure mode (R1-R5) has specific mitigation or pivot, avoiding binary success/failure
- **Valuable negative results**: H-E1 failure yields publishable finding on intrinsic entanglement, incentivizing honest reporting

**Residual Tensions:**
- **Commit purity vs separability**: If purity 60-70%, mixture modeling can correct but introduces modeling assumptions
- **CCA threshold ambiguity**: CCA 0.5-0.7 zone requires theoretical claim adjustment—not clear failure but not strong support
- **Human discrimination generalization**: n=100 code review tasks may not represent full distribution of multi-objective scenarios

**Mitigation of Tensions:**
- Commit purity: Pre-register purity threshold (70%), apply mixture correction with sensitivity analysis if 60-70%
- CCA ambiguity: Report as "moderate alignment" with adjusted theoretical framing, don't over-claim
- Human validation: Supplement with distribution shift tests (security-CTF, refactoring benchmarks) to demonstrate robustness beyond single task type

**Overall Dialectical Balance:**

The thesis-antithesis-synthesis structure ensures robust verification by:
1. Acknowledging H0 as legitimate scientific alternative, not strawman
2. Designing experiments that can support either thesis or antithesis
3. Providing clear decision criteria for when to pivot vs when to claim success
4. Valuing negative results equally with positive outcomes

---

## 7. Executive Summary

**Main Hypothesis:** Multi-objective code generation via aspect-factorized architectures that exploit empirically validated aspect-dominant structure in human code modifications to enable post-training controllability.

- ID: H-AspectFactorization-v1, Confidence: 0.8
- Scope Reduction: 40% (4/5 claims BUILD_ON, 1/5 PROVE_NEW)

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-validated)
- Sub-Hypotheses: 2 total
  - H-E1: Empirical separability existence
  - H-M-Integrated: 4-step causal mechanism (M1→M2→M3→M4)
- Duration: 6 weeks (sequential execution)
- Critical Gates: 2 decision points (Gate 1: Foundation, Gate 2: Mechanism)

**Risk Assessment:** Medium-High
- High risks: R1 (Metric Unreliability), R2 (Commit Impurity)
- Mitigation: Phase 0 validation, expert purity checks, mixture modeling

**Resources:** ~330 GPU-hours + $500 human validation

**Immediate Action:** Begin H-E1 with GitHub commit corpus mining and metric validation

---

### 7.1 Key Achievements

**Verification Plan Highlights:**
- **2 hypotheses** decomposed from 4-step causal chain with complete falsification criteria
- **H0 dialectical framing**: Intrinsic entanglement alternative provides publishable negative result path
- **Scope efficiency**: 40% reduction via BUILD_ON claims (benchmarks, baselines, disentanglement methods)
- **Graded outcomes**: 4 nuanced outcome paths (full support / partial / theoretical pivot / antithesis support)
- **Resource-constrained design**: ~330 GPU-hours feasible within typical research project budget

---

### 7.2 Verification Execution Order

**Phase 1: Foundation** (Weeks 1-2)
- **H-E1**: Aspect-dominant structure existence
  - Collect 10K minimal-diff commits, validate metrics (ICC≥0.8), perform spectral analysis
  - Success: Cross-coupling ≤0.2×, λ₄/λ₅>2.0, permutation p<0.05
- **Gate 1**: MUST_WORK
  - FAIL → ABORT, publish negative result on intrinsic entanglement
  - PASS → Proceed to Phase 2

**Phase 2: Mechanism Chain** (Weeks 3-6)
- **H-M-Integrated** (4 sub-mechanisms):
  - **M1** (Week 3): Representation-metric CCA alignment (target >0.7 for ≥3/4 aspects)
    - Failure response: Shift theoretical claim to "guided supervision"
  - **M2** (Week 4): Sample efficiency via natural vs rotated axes (target ≥30% gap)
    - Failure response: Simpler architecture sufficient
  - **M3** (Week 5): Architectural necessity via ablation (LoRA variants)
    - Failure response: Remove gating complexity
  - **M4** (Week 6): Controllability + human validation (band width ≥1.0, discrimination ≥60%)
    - Failure response: Document narrow applicability
- **Gate 2**: MUST_WORK (with graded pivots per sub-mechanism)
  - Full success (M1-M4 pass) → Strong contribution
  - Partial success → Document limitations, publish graded results

---

### 7.3 Critical Decision Points

**1. Gate 1 (Foundation - Week 2):** H-E1 must demonstrate empirical separability
- **FAIL** (flat spectrum λ₄/λ₅≤2.0 or coupling >0.3×) → STOP entire pipeline
  - Action: Publish high-impact negative result: "Multi-objective code alignment is intrinsically entangled"
  - Redirect field toward co-adaptive methods that don't assume separability
- **PASS** → Proceed to mechanism validation with empirical foundation established

**2. Gate 2 (Mechanism - Week 6):** Mechanism chain validation with graded outcomes
- **M1 Critical**: CCA <0.5 → Shift theoretical claim but continue
- **M2 Simplification**: No efficiency gap → Use LoRA+orthogonal (simpler)
- **M3 Reduction**: Gating redundant → Remove complexity
- **M4 Limitation**: Narrow bands → Document applicability constraints

**3. Pivot Decision Matrix:**

| Outcome | M1 | M2 | M3 | M4 | Interpretation |
|---------|----|----|----|----|----------------|
| Full Success | ✓ | ✓ | ✓ | ✓ | Strong contribution across all dimensions |
| Partial 1 | ✓ | ✓ | ✗ | ✓ | Separability + controllability, simpler architecture |
| Partial 2 | ✓ | ✗ | ✗ | ✓ | Guided supervision, baseline controllability |
| Theoretical Pivot | ✓ | ✗ | ✗ | ✗ | Moderate alignment, imposed structure not discovery |
| Foundation Only | ✗ | - | - | - | Empirical separability finding only |

---

### 7.4 Open Questions (from Phase 2A)

1. **Partial Factorization**: If only 3/4 aspects separate cleanly (e.g., efficiency entangles with correctness), how does partial factorization perform? Need graded theoretical predictions.

2. **Controllability Limits**: What is maximum steering coefficient α before controllability degrades nonlinearly? Must characterize band width per task type.

3. **CCA as Proxy**: Does representation-metric alignment strength (CCA) predict controllability band width? Can use CCA as early indicator of steering quality.

4. **Repository-Level Generalization**: How does method generalize to repository-level tasks (SWE-bench) vs function-level (HumanEval/MBPP)? Test on both scales.

---

### 7.5 Recommendations

**Immediate Actions:**
1. **Week 0**: Run Phase 0 metric validation experiment (ICC, construct validity, n=200)
2. **Week 1**: Begin GitHub commit corpus mining (target 10K minimal-diff commits)
3. **Week 1**: Expert annotation setup for purity validation (n=500 subset)

**Resource Allocation:**
- **Computational**: Reserve ~330 GPU-hours (spread over 6 weeks)
- **Human annotation**: Budget $500 for commit purity validation (n=500) + code review (n=100)
- **Early detection**: Run Phase 0 metric validation first (2-3 days) before committing to full data collection

**Risk Mitigation Priorities:**
1. **R1 (Metric Unreliability)**: Phase 0 validation MUST complete successfully before Phase 1
2. **R2 (Commit Impurity)**: Expert annotation on subset before full covariance analysis
3. **R3 (Weak CCA)**: Run M1 early (Week 3) to detect theoretical pivot need before extensive training

**Success Criteria Communication:**
- Pre-register all thresholds (cross-coupling ≤0.2×, CCA >0.7, etc.) before experiments
- Commit to publishing negative results if H-E1 fails
- Report graded outcomes transparently (partial success is valid contribution)

---

### 7.6 Appendices

**A. Hypothesis ID Reference:**
- H-E1: Aspect-Dominant Structure Existence
- H-M-Integrated: 4-Step Causal Mechanism
  - M1: Representation-Metric Alignment (CCA)
  - M2: Sample Efficiency (Natural vs Rotated Axes)
  - M3: Architectural Necessity (Gating vs Orthogonality)
  - M4: Controllability Validation (Steering + Human Discrimination)

**B. Gate Type Definitions:**
- **MUST_WORK**: Failure triggers major pivot or pipeline abort
- **SHOULD_WORK**: Failure documents limitation but allows continuation
- **DETERMINES_SUCCESS**: Final comparison determining publishability (Phase 5)

**C. Risk ID Reference:**
- R1: Metric Unreliability (Source: A1)
- R2: Commit Label Impurity (Source: A2)
- R3: Weak Representation-Metric Alignment (Source: A3)
- R4: Gating Redundancy (Source: A4)
- R5: Narrow Controllability Bands (Source: A5)

**D. Timeline Formula:**
```
Total Duration = 2 weeks (H-E1 foundation)
               + 4 weeks (H-M-Integrated: M1→M2→M3→M4)
               = 6 weeks total
```

**E. Next Steps:**
1. Complete Phase 2B finalization (verification_state.yaml generation)
2. Proceed to Phase 2C for detailed experiment design (H-E1 first)
3. Execute hypothesis verification loop via Phase 3 → 4 → 5
4. Generate paper in Phase 6 with dialectically balanced reporting

---

*Generated by YouRA Phase 2B Planning | 2026-05-11*
*Verification Plan Status: READY for Phase 2C Experiment Design*
