---
hypothesis_title: "SymCanon-WSL: Symmetry Canonicalization for Weight Space Property Prediction"
hypothesis_id: "H-SymCanon-v1"
confidence_level: 0.75
total_hypothesis_count: 5
research_mode: incremental
scope_reduction_percentage: 67
causal_chain_count: 3
include_condition_hypotheses: true
condition_hypothesis_count: 1
requires_transfer_validation: false
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
completedAt: "2026-08-26T00:00:00Z"
generated_at: "2026-08-26T00:00:00Z"
---

# Verification Plan: SymCanon-WSL: Symmetry Canonicalization for Weight Space Property Prediction

**Date:** 2026-08-26
**Hypothesis ID:** H-SymCanon-v1
**Confidence:** 0.75
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the Schürholt model zoo benchmark setting (MNIST MLP zoo, 2-layer networks, ~50k models),
if MLP weight vectors are canonicalized to remove scaling and sign-flip symmetry orbits before
encoding with a permutation-equivariant encoder (NFT), then Spearman rank correlation with
held-out model properties (test accuracy, generalization gap, learning rate recovery) increases
by Δρ ≥ 0.05 relative to raw weight encoding, because canonical representations concentrate
property-relevant geometric information by eliminating symmetry-induced variance that dilutes
the prediction signal.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in Spearman ρ between canonicalized-weight NFT encoding
and raw-weight NFT encoding on Schürholt MNIST zoo property prediction tasks
(i.e., Δρ < 0.05 or Δρ ≤ noise floor).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Schürholt MNIST Model Zoo (standard) | ~50k trained 2-layer MLPs (784→64→10) with ground-truth test accuracy, generalization gap, and learning rate recovery labels. M=2 architecture makes sign-flip canonicalization well-defined. Confirmed loadable in h-e1. |
| **Model** | Neural Functional Transformer (NFT) | Confirmed working on Schürholt MNIST zoo in h-e1 (ρ~0.11 on all 3 tasks). M-agnostic (unlike DWSNets). Our equivariant encoder baseline. |

**Dataset Details:**
- Source: Schürholt et al. 2022 — Model Zoos: A Dataset of Diverse Populations of Neural Network Models
- Path: Available via ModelZoos GitHub / HuggingFace

**Model Details:**
- Type: Permutation-equivariant weight space encoder
- Source: Zhou et al. 2023 — Neural Functional Networks (or Neural Functional Transformers extension)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Layer-wise statistics (Unterthiner et al. 2020) | Spearman ρ~0.9 | Various model zoos |
| Raw weights → NFT (Condition A, h-e1 confirmed) | Spearman ρ~0.11 | Schürholt MNIST zoo |
| flat_mlp / flat_mlp_canon (h-e1 confirmed) | ρ not recorded | Schürholt MNIST zoo |
| Random normalization control → NFT (Condition E) | TBD (normalization artifact control) | Schürholt MNIST zoo |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Schürholt MNIST zoo models occupy diverse positions in weight space | Zoo contains ~50k models trained from different seeds with varying hyperparameters | Orbit variance negligible, canonicalization irrelevant |
| A2 | Scaling and sign-flip symmetries create non-negligible within-orbit variance (orbits are "fat") | MLP training from random init under gradient descent does not enforce canonical form | Canonicalization has no measurable effect |
| A3 | NFT capacity is a binding constraint (residual capacity spent on invariance learning) | NFT at ρ=0.11 is well below layer stats ρ~0.9 | Canonicalization will not help |
| A4 | Sign-flip canonicalization for M=2 is well-defined and implementable | For M=2, only one consecutive layer pair — sign-flip uniquely determined by majority sign | Condition C/D results are invalid |
| A5 | Frozen-encoder sub-experiment isolates representation quality from optimization dynamics | Standard transfer learning practice; frozen encoder re-use is common in representation learning | Frozen-encoder result may be unreliable |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First empirical ablation of scaling and sign-flip symmetry contribution to model property prediction accuracy using a preprocessing intervention on a real model zoo benchmark.

**Key Innovation:** Symmetry canonicalization as an encoder-agnostic preprocessing step for weight space learning — applicable to any equivariant or non-equivariant encoder without architectural modification.

**Differentiation:**
- NFN (Zhou 2023): establishes permutation equivariance but does not handle scaling/sign-flip or measure their empirical contribution.
- DWSNets (Navon 2023): characterizes scaling symmetry theoretically but provides no empirical ablation; incompatible with M=2 zoos.
- Schürholt et al. 2022: self-supervised pretraining; does not address symmetry group coverage.
- Unterthiner et al. 2020: permutation-agnostic; establishes the task but ignores weight space geometry.

**Scope Reduction (67%):** 5 of 7 established claims are BUILD_ON (pre-validated). Only 2 PROVE_NEW claims require hypothesis generation. This plan targets only the PROVE_NEW claims:
1. Scaling/sign-flip symmetries have NOT been empirically evaluated for property prediction accuracy
2. Symmetry canonicalization improves equivariant encoder property prediction (Δρ ≥ 0.05)

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-C1 | CONDITION | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Symmetry Orbit Non-Degeneracy in Schürholt MNIST Zoo**

**Statement**: Under the Schürholt MNIST model zoo benchmark (2-layer MLPs, ~50k models), if we measure the within-orbit geometric diameter of scaling and sign-flip symmetry orbits across the zoo's weight vectors, then orbit diameters are non-negligible (>ε_threshold), because MLP training from random initialization under gradient descent does not enforce any canonical form, allowing symmetry-induced variance to accumulate across the diverse model population.

**Rationale** (2-3 sentences):
This existence hypothesis validates the foundational premise of the entire SymCanon-WSL framework: that the symmetry orbits are "fat" enough to matter geometrically. Without non-negligible orbit diameter, canonicalization would have no geometric effect regardless of the mechanism. This must be confirmed before any mechanistic or performance claims are meaningful.

**Variables** (from Phase 2A variables):
- Independent: Presence/absence of symmetry canonicalization (Condition A vs. D)
- Dependent: Within-orbit weight vector distance (cosine / L2) for oracle-constructed orbit pairs
- Controlled: Zoo models, fixed orbit construction procedure, random seed

**Verification Protocol** (3-5 steps):
1. Sample 500+ model pairs from Schürholt MNIST zoo that differ only by scaling/sign-flip (oracle construction via known transformations).
2. Compute pairwise L2 and cosine distance between raw weight vectors within the same orbit.
3. Compare orbit diameter distribution against near-zero null hypothesis (H0: orbits are thin).
4. Confirm diameter > practical threshold (e.g., mean cosine distance > 0.05) on ≥90% of sampled pairs.
5. Report orbit diameter statistics with bootstrap 95% CIs.

**Success Criteria** (PoC: Direction-based):
- Primary: Mean within-orbit cosine distance > 0.05 with non-overlapping 95% CI above zero
- Secondary: Orbit diameter measurable across all 3 symmetry types (scaling, sign-flip, combined)

**Failure Response**:
- IF fails: PIVOT — orbits are near-degenerate; hypothesis premise fails; route to Phase 0 for new direction

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 1.3 (Step 1), Section 5 (sh1_existence)

---

**H-M1: NFT Capacity Allocation to Within-Orbit Variance**

**Statement**: Under the Schürholt MNIST zoo (raw weights, Condition A), if we examine NFT's internal representations for model weight vectors in the same symmetry orbit, then representation similarity (cosine similarity of NFT embeddings) is low for within-orbit pairs, because NFT has no explicit orbit-collapsing mechanism for scaling/sign-flip orbits, requiring it to allocate representational capacity to learning implicit invariance rather than property-predictive features.

**Rationale** (2-3 sentences):
This mechanism hypothesis tests Step 2 of the causal chain: that NFT's capacity is actually consumed by within-orbit variance rather than already being orbit-invariant by coincidence. If NFT representations are already orbit-invariant without explicit canonicalization, the mechanism fails and canonicalization gains cannot be attributed to capacity freeing. This intermediate test provides mechanistic evidence independent of final ρ improvement.

**Variables**:
- Independent: Whether weights are from the same orbit vs. different orbit (oracle label)
- Dependent: Cosine similarity of NFT embeddings for oracle orbit pairs
- Controlled: NFT architecture, frozen weights from Condition A training, fixed seed

**Verification Protocol**:
1. Train NFT on Condition A (raw weights) for property prediction on Schürholt MNIST zoo.
2. Construct 500+ oracle orbit pairs (same function, different canonical form via scaling/sign-flip).
3. Extract NFT embeddings for both members of each orbit pair.
4. Compute cosine similarity distribution for within-orbit pairs vs. cross-orbit pairs.
5. Test: within-orbit similarity < cross-orbit similarity (NFT does NOT naturally collapse orbits).

**Success Criteria**:
- Primary: Mean cosine similarity for within-orbit pairs significantly lower than same-property cross-orbit pairs
- Secondary: Variance of within-orbit NFT embeddings > variance after canonicalization (H-M3 comparison)

**Failure Response**:
- IF fails: EXPLORE — NFT may already be implicitly orbit-invariant; update mechanism; document finding; proceed to H-M2/H-M3 (failure here does not invalidate H-M3 performance improvement but changes the causal story)

**Dependencies**: H-E1 (orbits must be non-degenerate for this test to be meaningful)

**Source**: Phase 2A Section 1.3 (Step 2)

---

**H-M2: PCA Concentration of Property-Relevant Information in Canonical Representations**

**Statement**: Under Schürholt MNIST zoo, if we compute PCA on canonical weight vectors (Condition D: both canonicalizations) versus raw weight vectors (Condition A), then the first k principal components of canonical weights explain more variance in property labels (test accuracy, gen_gap, lr_recovery) — measured by R² of linear regression onto property labels — because canonicalization eliminates within-orbit variance orthogonal to property-predictive directions, concentrating the property signal in fewer principal components.

**Rationale** (2-3 sentences):
This is the Condition G (PCA concentration) experiment from Phase 2A — a direct mechanistic test of Step 3's concentration claim, independent of encoder performance. If canonical PCA explains more property variance than raw PCA, it confirms that the geometric structure of canonical weight space is more property-aligned, providing mechanism-level evidence beyond ρ improvement. This serves as a falsifier: if PCA concentration does not improve, a different causal pathway must explain any ρ improvement.

**Variables**:
- Independent: Canonicalization type (None/Condition A vs. Both/Condition D)
- Dependent: R² of linear regression from first k PCs onto property labels (accuracy, gen_gap, lr_recovery)
- Controlled: k (number of PCs, identical for both conditions), regression method, train/test split

**Verification Protocol**:
1. Flatten weight vectors for all Schürholt zoo models under Condition A (raw) and Condition D (both canonical).
2. Fit PCA on training split for each condition; transform test split.
3. Fit linear regression from first k PCs (k=10, 20, 50) onto each property label on test split.
4. Compare R² (canonical) vs. R² (raw) for each property and each k.
5. Test: R²_canonical > R²_raw on ≥2/3 tasks with non-overlapping bootstrap 95% CIs.

**Success Criteria**:
- Primary: R²_canonical > R²_raw for test accuracy at k=20 with non-overlapping 95% CI
- Secondary: Improvement holds on ≥2/3 properties; improvement monotonic in k up to some saturation

**Failure Response**:
- IF fails: DOCUMENT — ρ improvement (if it exists) is not mediated by PCA concentration; the causal pathway claim must be revised; proceed to H-M3 regardless (ρ improvement is independently valuable)

**Dependencies**: H-M1 (mechanism chain; H-M2 provides direct mechanistic evidence for Step 3)

**Source**: Phase 2A Section 1.3 (Step 3), Section 1.6 (P1/P2), experimental_conditions (G)

---

**H-M3: Canonicalization Improves NFT Spearman ρ on Schürholt MNIST Zoo**

**Statement**: Under Schürholt MNIST zoo property prediction, if MLP weight vectors are canonicalized with both scaling and sign-flip transformations (Condition D) before NFT encoding, then Spearman rank correlation with ground-truth test accuracy increases by Δρ ≥ 0.05 relative to raw weight NFT encoding (Condition A), and the improvement is symmetry-specific (not a normalization artifact), because concentrated canonical representations enable NFT to extract property-predictive features that were previously obscured by within-orbit variance.

**Rationale** (2-3 sentences):
This is the primary empirical hypothesis (P1) — the main performance claim of SymCanon-WSL. It tests whether canonicalization produces the predicted Spearman ρ improvement across the 7-condition ablation design (A through G). Crucially, Condition E (random normalization control) isolates the symmetry-specific effect from any general normalization benefit, and the frozen-encoder sub-experiment separates representation quality from training dynamics.

**Variables**:
- Independent: Canonicalization type (Conditions A, B, C, D, E, F)
- Dependent: Spearman ρ between NFT predictions and ground-truth test accuracy, gen_gap, lr_recovery
- Controlled: NFT architecture, optimizer, LR, epochs, train/test split, random seed (fixed)

**Verification Protocol**:
1. Run bootstrap CI check on Condition A (raw NFT) to verify statistical power for Δρ=0.05 detection before committing.
2. Implement scaling canonicalization (~20 lines PyTorch) and sign-flip canonicalization for M=2 (~30 lines PyTorch).
3. Run all 7 conditions (A–G) on Schürholt MNIST zoo; evaluate Spearman ρ on held-out split for all 3 tasks.
4. Run frozen-encoder sub-experiment: NFT trained on raw weights (Condition A), evaluate on canonicalized inputs (B–D), retrain only final regressor.
5. Compute bootstrap 95% CIs for all Spearman ρ; test ρ_D > ρ_A (P1) and ρ_D > ρ_E (P2) with non-overlapping CIs.

**Success Criteria**:
- Primary (P1): Δρ ≥ 0.05 for test accuracy (Condition D vs. A) with non-overlapping 95% CIs
- Secondary (P2): ρ_D > ρ_E on ≥2/3 tasks (symmetry-specific, not normalization artifact)
- Robustness: Improvement holds on ≥2/3 of 3 tasks; frozen-encoder result consistent

**Failure Response**:
- IF P1 fails only: EXPLORE — document null result; check if Condition B or C shows partial improvement; report as negative empirical finding
- IF P1 + P2 both pass but P1 marginal: DOCUMENT — report with explicit power limitations

**Dependencies**: H-M2 (mechanism chain complete; H-M3 is the terminal performance test)

**Source**: Phase 2A Section 1.6 (P1, P2), Section 1.3 (Step 3), experimental_conditions (A–G)

---

**H-C1: M=2 Scope Boundary Verification for Sign-Flip Canonicalization**

**Statement**: Under the Schürholt MNIST zoo (M=2 MLP), if the sign-flip canonicalization algorithm (majority-sign simultaneous flip for the single consecutive layer pair) is applied to 500+ sampled zoo models, then it produces a unique deterministic canonical form for ≥99% of models (i.e., the algorithm is well-defined and non-degenerate for M=2), because with only one consecutive layer pair, the sign-flip operation is uniquely determined by the majority sign of each neuron's incoming weights.

**Rationale** (2-3 sentences):
This condition hypothesis directly tests Assumption A4 (sign-flip canonicalization uniqueness for M=2) and validates the M=2 scope boundary before investing in the full experiment. If the algorithm produces ambiguous results on real zoo models (e.g., due to zero-weight neurons or degenerate majority votes), Conditions C and D are invalid and the experiment design must change. This is a low-cost pre-check that ensures Condition C/D results are interpretable.

**Variables**:
- Independent: Application of sign-flip canonicalization algorithm to M=2 zoo models
- Dependent: Fraction of models where canonicalization produces unique output (no ambiguous majority vote)
- Controlled: Zoo model population, algorithm implementation, random seed

**Verification Protocol**:
1. Sample 500 models from Schürholt MNIST zoo with known weight statistics.
2. Apply sign-flip canonicalization algorithm (majority sign of incoming weights per neuron, simultaneous flip of incoming + outgoing weights).
3. Check for degenerate cases: neurons with zero incoming weights, exact ties in sign majority.
4. Report: fraction of models with unique canonical form; distribution of degenerate cases.
5. Confirm: ≥99% models produce unique canonical form (or propose tie-breaking rule for remainder).

**Success Criteria**:
- Primary: ≥99% of sampled zoo models produce unique sign-flip canonical form
- Secondary: Degenerate cases (if any) are <1% and addressable with simple tie-breaking (e.g., positive sign default)

**Failure Response**:
- IF fails: SCOPE — if degenerate cases >5%, sign-flip canonicalization is underdetermined for Schürholt zoo in practice; fall back to scaling-only (Condition B) as primary; document boundary

**Dependencies**: H-M3 (condition hypothesis tests scope of primary result; run after main experiment)

**Source**: Phase 2A Section 1.4 (A4), Section 1.5 (scope boundaries), Section 5 (open_questions)

---

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-C1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Within-orbit cosine distance > 0.05 on ≥90% of orbit pairs | STOP — route to Phase 0 |
| H-M1 | MUST_WORK | NFT embeddings NOT naturally orbit-invariant (within < cross orbit similarity) | EXPLORE — update causal story; document; continue |
| H-M2 | SHOULD_WORK | R²_canonical > R²_raw on ≥2/3 tasks | DOCUMENT — causal pathway claim revised; continue |
| H-M3 | SHOULD_WORK | Δρ ≥ 0.05 on accuracy task; ρ_D > ρ_E on ≥2/3 tasks | EXPLORE — null result documented |
| H-C1 | SHOULD_WORK | ≥99% models produce unique sign-flip canonical form | SCOPE — fall back to scaling-only if >5% degenerate |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 4 weeks (1+1+2) |
| Phase 2.5: Conditions | H-C1 | 1 week |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): Weight Space Degeneracy**

**Source Assumption:** A1 — Schürholt MNIST zoo models occupy diverse positions in weight space

**Description:** If zoo models cluster in a small region of weight space (e.g., due to similar training dynamics, weight decay converging to similar norms), orbit variance may be negligible and canonicalization irrelevant.

**Affected Hypotheses:** H-E1 (directly — existence claim fails), H-M1, H-M2, H-M3 (cascade)

**Severity:** Critical (invalidates entire hypothesis if H-E1 fails gate)

**Mitigation Strategy:**
1. **Prevention:** Pre-check weight vector distribution via PCA + t-SNE before running full experiment; confirm spread.
2. **Detection:** H-E1 protocol measures orbit diameter directly; low diameter = early warning.
3. **Response:**
   - PIVOT: If clustering is zoo-specific, test on SVHN/CIFAR zoo (P3 exploratory path).
   - SCOPE: Narrow claim to "under zoo diversity conditions" if partial diversity found.
   - ABORT: If orbit diameter near-zero across all sampled pairs, route to Phase 0.

**Early Warning Indicators:**
- Low variance in weight L2 norms across zoo models (< 0.1 std)
- PCA of weight space showing near-1D structure

---

**Risk R2 (from A2): Thin Orbits (Near-Canonical Training)**

**Source Assumption:** A2 — Scaling/sign-flip orbits are non-negligible (orbits are "fat")

**Description:** If models happen to be nearly canonical already (e.g., weight decay enforces near-unit norms, batch norm equivalents remove sign freedom), canonicalization has no measurable effect even if orbits theoretically exist.

**Affected Hypotheses:** H-E1, H-M2, H-M3

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Verify Schürholt zoo training details (no batch norm, no weight norm constraints) before experiment.
2. **Detection:** H-E1 orbit diameter measurement. If diameter < 0.05 cosine distance, A2 is violated.
3. **Response:**
   - EXPLORE: Report "orbits thin in practice" as a finding; test on zoo with known norm diversity.
   - SCOPE: Narrow claim to "zoos with diverse weight norms."

**Early Warning Indicators:**
- Coefficient of variation of weight L2 norms < 0.05 across zoo models
- Scaling canonicalization (Condition B) produces near-identical weights to Condition A

---

**Risk R3 (from A3): NFT Capacity Not the Bottleneck**

**Source Assumption:** A3 — NFT capacity is a binding constraint

**Description:** If NFT's low ρ=0.11 is due to architectural mismatch (not symmetry-related capacity waste), canonicalization will not improve performance even if orbits are fat and NFT is not orbit-invariant.

**Affected Hypotheses:** H-M1, H-M2, H-M3

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** H-M1 directly tests whether NFT is orbit-aware; H-M2 (PCA) tests information concentration independently.
2. **Detection:** If H-M1 passes (NFT not orbit-invariant) but H-M3 fails (no ρ improvement), capacity is not the bottleneck.
3. **Response:**
   - EXPLORE: Test Condition F (flat_mlp + canonicalization) — if flat_mlp improves but NFT does not, architectural mismatch is the issue.
   - DOCUMENT: Report null result with mechanistic diagnosis.

**Early Warning Indicators:**
- H-M1 shows NFT IS already orbit-invariant (similarity of orbit pairs is high)
- Condition F (flat_mlp + canon) shows improvement but Condition D (NFT + canon) does not

---

**Risk R4 (from A4): Sign-Flip Canonicalization Ambiguity**

**Source Assumption:** A4 — Sign-flip canonicalization for M=2 is well-defined and unique

**Description:** If real zoo models have neurons with zero-weight or exact ties in sign majority, the canonicalization algorithm produces ambiguous or non-deterministic outputs, invalidating Conditions C and D.

**Affected Hypotheses:** H-C1 (direct), H-M3 (Conditions C, D affected)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** H-C1 pre-checks canonicalization uniqueness on 500 models before full experiment.
2. **Detection:** Any degenerate case found in H-C1 sampling.
3. **Response:**
   - SCOPE: Add tie-breaking rule (default positive sign); re-run algorithm with rule; re-test uniqueness.
   - SCOPE: Fall back to scaling-only (Condition B) as primary if degenerate cases >5%.

**Early Warning Indicators:**
- Any neuron with zero-mean incoming weight distribution in zoo sample
- >1% of neurons with tied sign majority

---

**Risk R5 (from A5): Frozen-Encoder Distribution Shift**

**Source Assumption:** A5 — Frozen NFT encoder trained on raw weights can reliably evaluate canonicalized inputs

**Description:** If NFT representations are highly sensitive to input distribution shift (raw vs. canonical weight statistics differ substantially), the frozen-encoder result may be unreliable or spuriously negative.

**Affected Hypotheses:** H-M3 (frozen-encoder sub-experiment)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Compare input weight statistics (mean, std) between raw and canonical conditions before frozen encoder evaluation.
2. **Detection:** If frozen-encoder results diverge strongly from full-finetuned results, distribution shift is likely.
3. **Response:**
   - EXPLORE: Report both fine-tuned and frozen-encoder results; if they diverge, report distribution shift finding.
   - SCOPE: Treat frozen-encoder result as exploratory if shift is large; focus on full fine-tuned results for P1.

**Early Warning Indicators:**
- Large difference in L2 norm distribution between raw and canonical weight vectors
- Fine-tuned vs. frozen-encoder ρ divergence > 0.05

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 — Weight Space Degeneracy | A1 | H-E1, H-M1, H-M2, H-M3 (cascade) | Critical |
| R2 — Thin Orbits | A2 | H-E1, H-M2, H-M3 | High |
| R3 — NFT Capacity Not Bottleneck | A3 | H-M1, H-M2, H-M3 | High |
| R4 — Sign-Flip Ambiguity | A4 | H-C1, H-M3 (Cond. C/D) | Medium |
| R5 — Frozen Encoder Distribution Shift | A5 | H-M3 (sub-exp) | Medium |

**Risk Summary:** Critical: 1 | High: 2 | Medium: 2 | Low: 0

### 4.3 Baseline Failure Patterns → Additional Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| DWSNets incompatible with M=2 (h-e1 failure) | Encoder selection risk: NFT may have similar hidden incompatibilities | Use NFT exclusively; confirmed working from h-e1 |
| NFT ρ=0.11 low absolute performance | Statistical power insufficient for Δρ=0.05 detection | Mandatory bootstrap CI pre-check (Step 1 of H-M3 protocol) |
| Schürholt zoo limited to MNIST (M=2) | Narrow generalizability claim | Explicit M=2 scope; P3 cross-zoo as exploratory |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1 — Orbit Non-Degeneracy (no dependencies)
         │
         ▼ [Gate 1: MUST_WORK]
[Level 1 - Mechanism: NFT Capacity]
    H-M1 ← H-E1
         │
         ▼
[Level 2 - Mechanism: PCA Concentration]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Mechanism: Spearman ρ Performance]
    H-M3 ← H-M2
         │
         ▼ [Gate 2: SHOULD_WORK for H-M3]
[Level 4 - Condition: M=2 Scope Boundary]
    H-C1 ← H-M3
         │
         ▼ [Gate 2.5: SHOULD_WORK]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-C1
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type | Gate Condition |
|-------|-----------|---------------|-----------|----------------|
| 0 | H-E1 | None | MUST_WORK | Orbit diameter non-negligible |
| 1 | H-M1 | H-E1 | MUST_WORK | NFT not naturally orbit-invariant |
| 2 | H-M2 | H-M1 | SHOULD_WORK | PCA R² improves with canonicalization |
| 3 | H-M3 | H-M2 | SHOULD_WORK | Δρ ≥ 0.05 (primary); ρ_D > ρ_E (specificity) |
| 4 | H-C1 | H-M3 | SHOULD_WORK | ≥99% unique canonical form for M=2 |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2    │ W3     │ W4     │ W5     │ W6  │ W7
──────────────────────┼─────────┼────────┼────────┼────────┼─────┼────
PHASE 1: Foundation   │         │        │        │        │     │
  H-E1               │ ████████│        │        │        │     │
  [Gate 1]           │       ◆ │        │        │        │     │
──────────────────────┼─────────┼────────┼────────┼────────┼─────┼────
PHASE 2: Mechanisms   │         │        │        │        │     │
  H-M1               │         │ ████████        │        │     │
  H-M2               │         │        │ ████████        │     │
  H-M3               │         │        │        │ ████████████ │
  [Gate 2]           │         │        │        │        │   ◆ │
──────────────────────┼─────────┼────────┼────────┼────────┼─────┼────
PHASE 2.5: Condition  │         │        │        │        │     │
  H-C1               │         │        │        │        │     │████
  [Gate 2.5]         │         │        │        │        │     │   ◆
═══════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-C1

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 1 (H-M1) + 1 (H-M2) + 2 (H-M3) + 1 (H-C1)

Slack Available: 0 weeks (all sequential)

Note: H-M3 allocated 2 weeks (full 7-condition ablation + bootstrap CIs
      is the most implementation-intensive step).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Condition: 1 (H-C1)

Verification Phases: 3
1. Foundation (H-E1): 2 weeks
2. Mechanisms (H-M1, H-M2, H-M3): 4 weeks
3. Conditions (H-C1): 1 week

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain
Compute: CPU-hours (not days); confirmed from h-e1 infrastructure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1**: Execute H-E1 (Foundation — orbit non-degeneracy) — Week 1-2
**Step 2**: Evaluate Gate 1 → MUST_WORK. If fail → STOP, route to Phase 0.
**Step 3**: Execute H-M1 (NFT capacity allocation mechanism) — Week 3
**Step 4**: Execute H-M2 (PCA concentration mechanism) — Week 4
**Step 5**: Execute H-M3 (Spearman ρ performance — full 7-condition ablation) — Week 5-6
**Step 6**: Evaluate Gate 2 → SHOULD_WORK for H-M3 (P1: Δρ≥0.05; P2: ρ_D>ρ_E).
**Step 7**: Execute H-C1 (M=2 sign-flip scope boundary check) — Week 7
**Step 8**: Evaluate Gate 2.5 → SHOULD_WORK. Failures narrow scope, do not invalidate H-M3.
**Final**: Verification complete → proceed to Phase 4.5 Synthesis.

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Symmetry canonicalization (scaling + sign-flip) applied
as an encoder-agnostic preprocessing step improves NFT-based property
prediction (Spearman ρ) by Δρ≥0.05 on Schürholt MNIST zoo because
it collapses within-orbit variance and concentrates property-relevant
geometric information.

Supporting Evidence:
1. Causal mechanism: NFT has no explicit orbit-collapsing mechanism
   for scaling/sign-flip → capacity waste is structurally inevitable
   (Navon 2023 symmetry characterization; mechanistic inference).
2. Baseline confirms headroom: NFT ρ=0.11 << layer stats ρ~0.9 (h-e1),
   suggesting significant unexploited representational potential.
3. Specificity design: 7-condition ablation (Conditions A–G) provides
   clean causal attribution; Condition E controls for normalization artifact.

Strengths:
- Built on confirmed working infrastructure (h-e1 NFT + Schürholt zoo)
- Zero new infrastructure required — immediate testability
- Encoder-agnostic framing: applicable beyond NFT to any equivariant encoder
- Geometric mechanism (PCA concentration) provides falsifiable causal path

Expected Outcomes:
- Primary (P1): Condition D Δρ ≥ 0.05 vs Condition A on test accuracy
- Secondary (P2): ρ_D > ρ_E (symmetry-specific, not normalization artifact)
- Tertiary (P3): Cross-zoo generalization (SVHN/CIFAR, exploratory)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): There is no significant difference in Spearman ρ
between canonicalized-weight NFT encoding and raw-weight NFT encoding
on Schürholt MNIST zoo property prediction tasks (Δρ < 0.05 or ≤ noise floor).

Counter-Arguments:
1. NFT may already learn approximate orbit invariance implicitly during
   training without explicit canonicalization (A3 violation risk).
2. The NFT ρ=0.11 baseline may reflect architectural limitations
   (not symmetry-related capacity waste); canonicalization cannot fix
   what equivariance design does not address.
3. Schürholt MNIST zoo may have near-canonical models already (weight
   decay or training dynamics enforce approximate canonical form), making
   orbit variance negligible in practice (A1/A2 violation risk).

Potential Failure Points:
- R1: Zoo weight vectors cluster near-canonically (H-E1 orbit diameter ≈ 0)
- R2: NFT adapts to within-orbit variance without performance cost (R3)
- R3: Δρ improvement exists but < 0.05 (insufficient to reject H0)
- R4/R5: Sign-flip canonicalization is ambiguous or introduces distribution shift

Conditions Under Which H0 Would Be Supported:
- H-E1 finds within-orbit cosine distance near zero (<0.05)
- H-M1 finds NFT embeddings nearly identical for orbit pairs (implicit invariance)
- H-M3 finds Δρ < 0.05 on test accuracy with overlapping 95% CIs
- Or if Δρ ≈ Δρ_E (effect not symmetry-specific, P2 fails)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

H-SymCanon-v1 presents a theoretically grounded and practically
falsifiable claim. The thesis rests on a clear 3-step causal chain
with direct experimental tests for each step (H-E1, H-M1/M2, H-M3).
However, the antithesis raises legitimate concerns: the low NFT
baseline (ρ=0.11) limits statistical power; Schürholt zoo training
dynamics may have inadvertently produced near-canonical models; and
NFT may implicitly learn orbit invariance without explicit help.

Resolution Path:

The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Tests orbit non-degeneracy BEFORE
   investing in mechanism or performance experiments.
2. Intermediate mechanism tests (H-M1, H-M2): Provides causal evidence
   independent of final ρ outcome — even a null P1 result is scientifically
   informative if H-M1 reveals NFT is already orbit-invariant.
3. Gate conditions: H-E1 MUST_WORK gate enables early abort if foundation
   fails, avoiding wasted computation.
4. 7-condition design (Conditions A–G): Conditions E (random norm control)
   and G (PCA concentration) provide falsifiers for alternative hypotheses.

Conditions for Thesis Support:
- H-E1 passes: orbits are fat
- H-M1 passes: NFT is not already orbit-invariant
- H-M3 confirms: Δρ ≥ 0.05 on primary task, ρ_D > ρ_E

Conditions for Antithesis Support:
- H-E1 fails (orbit diameter near zero) — fundamental premise absent
- H-M1 shows NFT already orbit-invariant (capacity argument fails)
- H-M3 Δρ < 0.05 with overlapping CIs (H0 not rejected)
- H-M3 Δρ ≈ ΔρE (effect is normalization artifact, not symmetry-specific)

Nuanced Outcome Possibilities:
1. Full Support: H-E1 + H-M1 + H-M2 + H-M3 all pass → Thesis validated
2. Mechanism Validated / Performance Marginal: H-E1+H-M1+H-M2 pass, H-M3 Δρ<0.05
   → Geometric claim supported; performance benefit below threshold; report as
   "mechanistic finding without predictive improvement" (still publishable)
3. Performance Improves / Mechanism Unclear: H-M3 passes, H-M2 fails
   → Alternative causal pathway; report ρ improvement as empirical without
   mechanistic explanation; PCA concentration hypothesis rejected
4. H0 Supported: H-E1 or H-M1 fails → Antithesis supported; route to Phase 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Orbit Existence | Orbits are fat in Schürholt zoo (A1, A2) | Zoo training may produce near-canonical weights | H-E1 direct orbit diameter measurement |
| NFT Capacity | Capacity wasted on implicit invariance (A3) | NFT may already be orbit-invariant | H-M1 embedding similarity test |
| Concentration Mechanism | PCA of canonical weights more property-aligned | Alternative causal pathway possible | H-M2 PCA R² experiment (Condition G) |
| Performance Claim | Δρ ≥ 0.05 (P1); symmetry-specific (P2) | Δρ < 0.05 or = normalization artifact | H-M3 7-condition ablation + bootstrap CIs |
| Scope (M=2) | Sign-flip well-defined for M=2 | Algorithm ambiguous in practice | H-C1 pre-check on 500 zoo models |

**Overall Robustness Score:** High — 7-condition design with mechanism tests and control conditions provides strong causal attribution; multiple independent falsification paths.

**Confidence in Verification Plan:** 0.75 (from Phase 2A)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-SymCanon-v1 — Symmetry canonicalization (scaling + sign-flip) as encoder-agnostic preprocessing improves NFT Spearman ρ by Δρ≥0.05 on Schürholt MNIST zoo.
- Confidence: 0.75 | Scope reduction: 67% (5 BUILD_ON claims not re-tested)

**Verification Structure:**
- Mode: Incremental (Phase 2A confirmed infrastructure)
- Sub-Hypotheses: 5 total (H-E1, H-M1, H-M2, H-M3, H-C1)
- Phases: 3 over 7 weeks | Critical Gates: 3 decision points

**Risk Assessment:** Medium-High
- Critical: R1 (weight space degeneracy) — mitigated by H-E1 gate
- High: R2 (thin orbits), R3 (NFT capacity not bottleneck) — mitigated by H-M1/M2

**Immediate Action:** Begin Phase 1 with H-E1 (orbit non-degeneracy check, 500 oracle orbit pairs)

### 7.2 Conclusions

**Key Achievements:**
- 5 sub-hypotheses across 3 phases covering existence, mechanism, and scope
- H0 addressed: "No significant Δρ between canonical and raw NFT encoding"
- 7-condition ablation design (A–G) provides causal attribution beyond simple comparison

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Within-orbit cosine distance > 0.05 for 500+ Schürholt zoo orbit pairs
- Gate 1: MUST PASS — if fails, route to Phase 0

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: NFT embedding similarity test (oracle orbit pairs) — Week 3
- H-M2: PCA R² concentration experiment (Condition G) — Week 4
- H-M3: Full 7-condition ablation, bootstrap CIs, frozen-encoder sub-exp — Week 5-6
- Gate 2: H-M3 Δρ≥0.05 (P1); ρ_D>ρ_E (P2) — SHOULD_WORK

**Phase 2.5: Conditions** (1 week)
- H-C1: Sign-flip uniqueness check on 500 zoo models — Week 7
- Gate 2.5: ≥99% unique canonical form — narrow scope on failure

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 MUST_WORK
   - FAIL → STOP, route to Phase 0, orbit premise absent
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M3 SHOULD_WORK
   - CRITICAL FAIL (Δρ<0 or normalization artifact) → Document null, route finding to Phase 2A
   - NULL RESULT (Δρ<0.05) → Document with power limitations; report mechanistic findings
   - PASS → Proceed to Phase 2.5 and Phase 4.5 Synthesis

3. **Gate 2.5 (Conditions):** H-C1 SHOULD_WORK
   - FAIL (>5% ambiguous) → Narrow scope to scaling-only; document M=2 boundary limitation

**Open Questions (from Phase 2A):**
- Is NFT baseline ρ=0.11 above noise floor for Δρ=0.05 detection? (Bootstrap CI pre-check)
- Are SVHN/CIFAR zoos accessible for P3 cross-zoo? (Verify before claiming P3 testability)
- Does sign-flip for M=2 produce unique canonical form in practice? (H-C1 answers this)
- Does the improvement hold with frozen NFT encoder? (H-M3 frozen-encoder sub-experiment)

**Recommendations:**

1. **Immediate Actions:**
   - Start Phase 1 with H-E1 — construct 500 oracle orbit pairs from Schürholt zoo
   - Run bootstrap CI check on Condition A (raw NFT, h-e1) before H-M3 commitment

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path; H-M3 is the most implementation-intensive
   - Reserve 1-week buffer for unexpected degenerate cases in H-C1

3. **Failure Management:**
   - Document all gate outcomes (pass/fail/partial) with quantitative evidence
   - Execute PIVOT/SCOPE strategies as defined per hypothesis
   - If H-E1 fails: do not run H-M1-3 (saves ~4 weeks of wasted computation)

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `03_refinement.yaml` (ID: H-SymCanon-v1, generated 2026-08-26)
- Architecture: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- Convergence: All 6 criteria met at Exchange 8; 5 of 6 agents STRONG verdict

**B. MCP Tool Usage Summary**
- Total MCP calls: 0 (ABLATION MODE — MCP tools not available; analysis conducted via structured Phase 2A parsing)
- ClearThought scientific method: simulated via Phase 2A causal chain structure
- Note: In standard mode, 4-6 MCP calls (scientificmethod × 2, collaborativereasoning × 1, structuredargumentation × 1)
