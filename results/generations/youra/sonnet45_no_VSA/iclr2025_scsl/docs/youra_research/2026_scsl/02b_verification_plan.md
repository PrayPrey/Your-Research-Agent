# Phase 2B: Verification Planning

**Generated:** 2026-07-11  
**Hypothesis ID:** h-s1  
**Pipeline Project:** Anonymous Pipeline: Minimal Research Scope Test  
**Mode:** Incremental (Phase 2A available)

---

## Executive Summary

This verification plan decomposes the validated hypothesis from Phase 2A into 2 testable sub-hypotheses with clear success criteria, risk mitigation strategies, and execution roadmap. The plan focuses on proving the core semantic validity principle through minimal viable experiments on MNIST.

**Hypotheses:**
- **H-E1 (Existence):** Asymmetric digit degradation effect
- **H-M (Mechanism):** 4-step causal chain with dose-response

**Target:** Prove semantic invalidity degrades model performance (Phase 4 PoC validation)

---

## Section 1: Main Hypothesis Overview

### 1.1 Core Statement

**Hypothesis ID:** h-s1

**Statement:**  
Data augmentations that violate semantic constraints (producing invalid/ambiguous class labels) degrade per-class test accuracy on affected classes compared to no augmentation or semantically valid augmentations. This effect exhibits dose-response behavior: higher augmentation frequency → stronger degradation.

**Specific Instantiation (MNIST):**  
Horizontal flip augmentation on MNIST introduces label noise for asymmetric digits {2,3,5,6,7,9} (flipped versions are non-canonical), causing measurable test accuracy degradation on those classes compared to baseline or positive control (rotation ±15°). Symmetric digits {0,1,8} are unaffected.

**Confidence Level:** 0.75

### 1.2 Alternative Hypothesis (H0)

No significant difference in asymmetric digit accuracy between baseline and flip conditions (Wilcoxon p ≥ 0.05)

### 1.3 Experimental Setup

**Dataset:**
- Name: MNIST
- Type: standard
- Source: torchvision.datasets (auto-download)
- Details: 60k train, 10k test, 10 classes, 28×28 grayscale

**Model:**
- Name: Standard CNN
- Type: custom
- Architecture: 2 conv layers [32,64 filters], MaxPool, Dropout [0.25,0.5], 2 FC [128→10]

**Training Protocol:**
- Optimizer: Adam (lr=0.001)
- Batch size: 64
- Epochs: 30
- Early stopping: 5 epochs patience on validation accuracy
- Loss: CrossEntropyLoss

**Conditions:**
1. Baseline: ToTensor + Normalize only
2. Flip30: RandomHorizontalFlip(p=0.3) + Normalize
3. Flip50: RandomHorizontalFlip(p=0.5) + Normalize
4. Flip90: RandomHorizontalFlip(p=0.9) + Normalize
5. Rotation: RandomRotation(±15°) + Normalize

### 1.4 Related Work Baseline

- Standard CNN on MNIST without augmentation: ~99% test accuracy
- Literature gap: No prior work explicitly tests semantic validity of standard augmentations on MNIST

---

## Section 2: Sub-Hypothesis Inventory

### Hypothesis Inventory Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          HYPOTHESIS INVENTORY (2 hypotheses)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID   | Type      | Statement (Brief)                                    | Prerequisites | Source              |
|------|-----------|------------------------------------------------------|---------------|---------------------|
| H-E1 | Existence | Asymmetric digits degrade under flip, symmetric stable | None        | Phase 2A SH1/Pred 1 |
| H-M  | Mechanism | 4-step causal chain with dose-response relationship  | H-E1          | Phase 2A Causal Mech|

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 2.1 H-E1: Asymmetric Digit Degradation Effect

**Statement:** When horizontal flip augmentation is applied to MNIST training data, asymmetric digits {2,3,5,6,7,9} will show reduced test accuracy compared to baseline, while symmetric digits {0,1,8} remain unaffected.

**Rationale:** This hypothesis validates the core phenomenon that semantic invalidity degrades model performance. If confirmed, it establishes that "standard" augmentations can harm accuracy when they violate domain-specific semantic constraints.

**Variables:**
- Independent: Augmentation Type (Baseline/HorizontalFlip/Rotation±15°), Digit Symmetry Group
- Dependent: Per-Class Test Accuracy (0-100% for each of 10 classes)
- Controlled: Model Architecture, Training Hyperparameters

**Verification Protocol:**
1. Train models on Baseline, Flip (p=0.5), and Rotation (±15°) conditions with n=5 seeds
2. Measure per-class test accuracy for all 10 digit classes
3. Group accuracy by symmetry: Symmetric {0,1,8} vs Asymmetric {2,3,5,6,7,9}
4. Statistical test: Wilcoxon signed-rank on asymmetric accuracy (Flip vs Baseline), require p<0.05 AND Cohen's d≥0.5
5. Verify positive control: Rotation should NOT differentially harm asymmetric digits

**Success Criteria:**
- Primary: Asymmetric digit accuracy significantly lower under Flip vs Baseline (p<0.05, d≥0.5)
- Secondary: Symmetric digit accuracy stable across conditions
- Positive Control: Rotation does NOT create differential effect

**Failure Response:** ABANDON (core phenomenon does not exist)

**Dependencies:** None (foundational hypothesis)

**Gate Type:** MUST_WORK

---

### 2.2 H-M: Semantic Invalidity → Label Noise → Dose-Response Degradation

**Statement:** The mechanism operates through four causal steps: (1) Horizontal flip creates non-canonical asymmetric digit images, (2) These invalid images retain original labels creating label noise, (3) Training on label noise degrades test accuracy on affected classes, (4) Degradation magnitude increases monotonically with flip probability.

**Rationale:** This hypothesis tests the complete causal chain from augmentation to outcome, including the critical dose-response relationship that strengthens the mechanistic claim.

**Variables:**
- Independent: Flip Probability (p ∈ {0.0, 0.3, 0.5, 0.9})
- Dependent: Asymmetric Digit Accuracy, Accuracy Degradation
- Controlled: Random Seed (n=5), Model Architecture, Training Protocol

**Verification Protocol:**
1. Train models at multiple flip probabilities: p=0.0, p=0.3, p=0.5, p=0.9 with n=5 seeds each
2. Measure asymmetric digit accuracy at each flip probability level
3. Compute accuracy degradation: Baseline accuracy - Flip accuracy
4. Test dose-response: Spearman rank correlation (expect ρ<0, p<0.05)
5. Verify monotonic degradation: Higher flip probability → lower accuracy

**Success Criteria:**
- Primary: Spearman ρ significantly negative (p<0.05), indicating monotonic dose-response
- Secondary: Degradation visible at p=0.3, stronger at p=0.5, strongest at p=0.9
- Mechanism Validation: Each causal step observable

**Failure Response:** EXPLORE (effect exists per H-E1 but mechanism unclear)

**Dependencies:** H-E1 must pass

**Gate Type:** SHOULD_WORK

---

## Section 3: Risk Analysis

### Risk Summary Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk                     | Source | Severity | Affected  | Mitigation              |
|----|--------------------------|--------|----------|-----------|-------------------------|
| R1 | Semantic invalidity false| A1     | Critical | H-E1, H-M | Visual inspection, ABORT|
| R2 | Label implementation bug | A2     | High     | H-M       | Code review, Fix & rerun|
| R3 | Label noise too severe   | A3     | Medium   | H-M       | Limit p≤0.9, monitor acc|
| R4 | Symmetry partition issue | A4     | Medium   | H-E1      | Per-digit analysis      |
| R5 | Rotation control fails   | A5     | Critical | H-E1, H-M | Pilot test, alt control |

Critical Risks: 2 (R1, R5)
High Risks: 1 (R2)
Medium Risks: 2 (R3, R4)
Low Risks: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Risk Details

**R1: Semantic Invalidity Assumption Violation**
- Mitigation: Visual inspection of flipped digits before experiments
- Early Warning: If H-E1 shows no differential effect on asymmetric digits
- Response: ABORT hypothesis if assumption proven false

**R2: Label Preservation Implementation Error**
- Mitigation: Code review of augmentation pipeline, unit tests
- Early Warning: Sanity check during training (sample batches)
- Response: Fix implementation, re-run experiments

**R3: Model Cannot Learn from Label Noise**
- Mitigation: Limit flip probability (max p=0.9), monitor baseline accuracy
- Early Warning: Baseline accuracy <50% under flip conditions
- Response: Reduce flip probability, re-run

**R4: Symmetry Partition Ambiguity (digit '6' → '9')**
- Mitigation: Per-digit analysis (disaggregate asymmetric group)
- Early Warning: Digit '6' shows anomalous behavior
- Response: Exclude digit '6' from analysis, recompute statistics

**R5: Rotation Control Invalidity**
- Mitigation: Pilot test rotation control, literature review
- Early Warning: Prediction 3 fails (rotation harms asymmetric digits)
- Response: Use alternative control (translation, brightness)

---

## Section 4: Execution Roadmap

### 4.1 Dependency Graph (DAG)

```
┌─────────────────────────────────────────┐
│           HYPOTHESIS DAG                │
└─────────────────────────────────────────┘

   ┌──────┐
   │ H-E1 │  ← Foundation (no prerequisites)
   └───┬──┘
       │
       ▼
   ┌──────┐
   │ H-M  │  ← Mechanism (requires H-E1 success)
   └──────┘
```

**Execution Order:** Sequential (H-E1 → H-M)

**Gate Conditions:**
- H-E1: MUST_WORK (existence required)
- H-M: SHOULD_WORK (mechanism strengthens claim)

### 4.2 Timeline Estimate

| Hypothesis | Dependencies | Estimated Time | Type       |
|------------|--------------|----------------|------------|
| H-E1       | None         | ~2 hours       | Existence  |
| H-M        | H-E1         | ~2 hours       | Mechanism  |

**Total Sequential Time:** ~4 hours (with parallelization: ~3 hours)

**Critical Path:** H-E1 → H-M (linear)

---

## Section 5: Dialectical Analysis

### Thesis

Semantic validity predicts augmentation effectiveness: augmentations that violate domain-specific semantic constraints (e.g., horizontal flip on asymmetric MNIST digits) degrade model performance by introducing label noise.

### Antithesis

Network robustness: Deep learning models are robust to label noise and should learn invariant features regardless of augmentation semantic validity. The effect size (1-2% degradation) is negligible given MNIST's high baseline accuracy (~99%).

### Synthesis

Both perspectives have merit: networks ARE robust to moderate label noise (A3 assumption), but semantic invalidity creates CLASS-SPECIFIC label noise that affects per-class accuracy differentially. The small effect size is scientifically meaningful as it establishes the PRINCIPLE that semantic validity matters, even if practical magnitude is modest on easy datasets like MNIST. Stronger effects expected on harder datasets.

### Robustness Assessment

- **Supporting Evidence:** PyTorch official examples avoid horizontal flip for MNIST (implicit semantic concern), label noise literature shows class-specific noise degrades accuracy
- **Counter-Evidence:** High baseline accuracy (~99%) may mask small effects, network capacity might compensate
- **Resolution:** Per-class analysis with adequate statistical power (n=5 seeds, Cohen's d≥0.5) ensures effect is detectable and meaningful

---

## Section 6: Conclusions & Next Steps

### Achievements

✅ 2 testable sub-hypotheses defined (H-E1, H-M)  
✅ Clear verification protocols with statistical thresholds  
✅ Risk analysis with mitigation strategies (5 risks identified)  
✅ Execution roadmap with dependency graph  
✅ Dialectical analysis for robustness  

### Execution Order

1. **H-E1 (Foundation):** Validate asymmetric digit degradation effect
2. **H-M (Mechanism):** Test 4-step causal chain with dose-response

### Decision Points

- **H-E1 Pass → Continue to H-M**
- **H-E1 Fail → ABORT hypothesis** (core phenomenon does not exist)
- **H-M Fail (H-E1 Pass) → EXPLORE mechanism** (effect exists but causal chain unclear)

### Next Steps

1. **Phase 2C:** Design detailed experiment specifications for each hypothesis
2. **Phase 3:** Implementation planning (PRD, Architecture, PRP)
3. **Phase 4:** Coding & validation (run experiments, statistical analysis)

### Open Questions

- Will 1-2% degradation be statistically detectable with n=5 seeds?
- Does rotation ±15° truly preserve semantic validity (positive control check)?
- Can we generalize findings beyond MNIST to other domains?

---

## Appendix: Scope Reduction from Phase 2A

**Established Facts Registry:** None (all claims require verification)

**Scope Reduction:** 0%

**Phase 2B-4 Instructions:** Verify all claims empirically

---

**Workflow Complete:** 2026-07-11  
**Next Phase:** Phase 2C (Experiment Design)
