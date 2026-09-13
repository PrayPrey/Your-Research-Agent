# Phase 2A Hypothesis Refinement Summary

**Generated:** 2026-07-11  
**Hypothesis ID:** h-s1 (Semantic Validity Hypothesis)  
**Version:** 1  
**Session:** Tikitaka Multi-Perspective Research Dialogue (7 exchanges)  
**Convergence:** ✅ ACHIEVED  

---

## Executive Summary

After 4 consecutive Phase 4 failures with complex optimization methods (SAM/SWA), Phase 2A generated a simple, testable hypothesis addressing Gap 1 from Phase 1: **Does horizontal flip augmentation harm MNIST accuracy due to semantic invalidity?**

**Core Finding:** Data augmentations that violate semantic constraints (producing invalid/ambiguous class labels) degrade per-class test accuracy on affected classes compared to no augmentation or semantically valid augmentations, with dose-response behavior.

**MNIST Instantiation:** Horizontal flip produces non-canonical images for asymmetric digits {2,3,5,6,7,9}, causing measurable test accuracy degradation on those classes. Symmetric digits {0,1,8} are unaffected. Degradation correlates with flip probability (p=0.3 → small, p=0.9 → large).

**Novelty:** First explicit test of whether "standard" augmentations can harm accuracy due to semantic invalidity. Establishes general principle: augmentation effectiveness depends on semantic validity, not just diversity/regularization.

**Feasibility:** ✅ HIGH — 25 experiments, ~45 min with parallelization, CPU-only, existing dataset, no GPU required.

**Risk:** ✅ LOW — Avoids all previous failure modes (no SAM/SWA, n≥5 seeds, proper statistical tests, simple design).

**Status:** ✅ READY FOR PHASE 2B (Verification Protocol Design)

---

## Hypothesis Statement

### H1: Semantic Validity Hypothesis for Data Augmentation

**General Principle:**  
Data augmentations that violate semantic constraints (transformations producing invalid or ambiguous class labels) degrade per-class test accuracy on affected classes compared to no augmentation or semantically valid augmentations. This effect exhibits dose-response behavior: higher augmentation frequency → stronger degradation.

**MNIST-Specific Claim:**  
Horizontal flip augmentation on MNIST introduces label noise for asymmetric digits {2,3,5,6,7,9} because flipped versions are visually non-canonical (backward "3" is not a valid digit). This causes measurable test accuracy degradation on asymmetric classes compared to:
1. Baseline (no augmentation)
2. Positive control (rotation ±15°, semantically valid)

Symmetric digits {0,1,8} are unaffected (horizontal reflection preserves their shape). Degradation magnitude correlates with flip probability (dose-response).

---

## Causal Mechanism (4 Steps)

1. **Semantic Invalidity**  
   Horizontal flip mirrors MNIST digits, producing non-canonical images for asymmetric classes {2,3,5,6,7,9}. For example, flipped "3" appears as backward "3" (invalid digit), not a different valid class like "E".

2. **Label Noise Introduction**  
   Flipped asymmetric digits appear ambiguous or wrong to human observers, but retain their original labels during training (standard augmentation behavior). This introduces class-specific label noise.

3. **Per-Class Degradation**  
   Model trained on semantically invalid examples (mislabeled data) exhibits reduced test accuracy on the affected classes. Label noise literature confirms this effect (Natarajan et al., Zhang et al.).

4. **Dose-Response**  
   Degradation magnitude correlates with augmentation frequency:
   - p=0.3: Small label noise → small accuracy drop
   - p=0.5: Moderate label noise → moderate drop
   - p=0.9: High label noise → large drop

---

## Testable Predictions

### Prediction 1: Per-Class Differential Effect

**Claim:**  
Asymmetric digit accuracy (classes {2,3,5,6,7,9}) DECREASES under horizontal flip vs baseline.  
Symmetric digit accuracy (classes {0,1,8}) remains STABLE or increases under horizontal flip.

**Metric:**  
Per-class test accuracy, grouped by symmetry:
- `Symmetric Accuracy = mean({class_0, class_1, class_8})`
- `Asymmetric Accuracy = mean({class_2, class_3, class_5, class_6, class_7, class_9})`

**Statistical Test:**  
Wilcoxon signed-rank test (paired, n=5 seeds), α=0.05  
Effect size: Cohen's d ≥ 0.5 for asymmetric degradation

**Falsification:**  
If asymmetric accuracy is NOT significantly lower with flip vs baseline (p ≥ 0.05 OR d < 0.5) → Hypothesis REJECTED  
If symmetric digits degrade equally or more → Differential semantic effect REJECTED

---

### Prediction 2: Dose-Response Relationship

**Claim:**  
Asymmetric digit accuracy degradation increases monotonically with flip probability:  
Flip p=0.3 < Flip p=0.5 < Flip p=0.9 (in terms of degradation magnitude)

**Metric:**  
Spearman rank correlation between flip probability {0.3, 0.5, 0.9} and asymmetric accuracy across seeds

**Statistical Test:**  
Spearman's ρ, α=0.05  
Expected: ρ significantly negative (higher p → lower accuracy)

**Falsification:**  
If NO monotonic relationship observed (ρ not significantly negative, p ≥ 0.05) → Mechanism QUESTIONED  
If relationship is NON-MONOTONIC (e.g., p=0.5 worse than p=0.9) → Dose-response REJECTED

---

### Prediction 3: Positive Control Validation

**Claim:**  
Rotation ±15° augmentation does NOT significantly degrade asymmetric digit accuracy vs baseline.  
If rotation DOES help, effect should be equal across symmetric and asymmetric digits (no differential impact).

**Purpose:**  
Isolates semantic invalidity (flip-specific) from general augmentation effects (regularization).

**Metric:**  
Per-class test accuracy under rotation vs baseline, grouped by symmetry

**Statistical Test:**  
Wilcoxon signed-rank test for rotation vs baseline  
Check for differential effect (symmetric vs asymmetric degradation)

**Falsification:**  
If rotation significantly harms asymmetric digits differentially → NOT a semantic-specific effect (general augmentation problem)

---

## Novelty & Contribution

### What's New

1. **First Explicit Test**  
   No prior work systematically tests whether "standard" augmentations can harm accuracy due to semantic invalidity. Existing papers apply horizontal flip without validation.

2. **General Principle Established**  
   Augmentation effectiveness depends on semantic validity, not just diversity or regularization strength. This is a methodological contribution to augmentation selection.

3. **Dose-Response Evidence**  
   Quantifies relationship between semantic violation frequency and accuracy degradation (quantitative principle, not just binary finding).

4. **Methodological Contribution**  
   Demonstrates need for domain-aware augmentation selection. Practitioners should verify semantic validity BEFORE applying "standard" schemes to new domains.

### What's Different from Prior Work

- **[Phase 1 Finding]** Existing papers apply horizontal flip without semantic validation
- **[Phase 1 Finding]** Official pytorch/examples avoids flip for MNIST but doesn't explain why
- **This Work:** Makes semantic invalidity hypothesis explicit, tests it rigorously with statistical validation

### Generalizability

The principle applies beyond MNIST to ANY domain with semantic constraints:

- **Medical Imaging:** Anatomical orientation matters (left/right kidney, cardiac structures)
- **Traffic Signs:** Directional arrows (→ flipped ≠ ←, semantically different)
- **Text Recognition:** Character chirality (b/d, p/q distinguish by orientation)
- **Oriented Objects:** Airplanes, vehicles (direction matters for classification)

This work provides a template for validating augmentation schemes in new domains.

---

## Experimental Design

### Dataset
MNIST (60k train, 10k test, 10 classes, 28×28 grayscale)

### Model Architecture
Standard CNN:
- Conv2d(1, 32, kernel=3, padding=1) → ReLU → MaxPool2d(2)
- Conv2d(32, 64, kernel=3, padding=1) → ReLU → MaxPool2d(2) → Dropout(0.25)
- Flatten → Linear(3136, 128) → ReLU → Dropout(0.5)
- Linear(128, 10)
- Total params: ~100k

### Training Configuration
- **Optimizer:** Adam (lr=0.001, default betas)
- **Batch Size:** 64
- **Epochs:** 30 (with early stopping: 5 epochs patience on val accuracy)
- **Loss:** CrossEntropyLoss
- **Train/Val Split:** 90/10 from training set (54k train, 6k val)

### Augmentation Conditions (5 total)

1. **Baseline:** `ToTensor() + Normalize(mean=0.1307, std=0.3081)`
2. **Flip30:** `RandomHorizontalFlip(p=0.3) + Normalize`
3. **Flip50:** `RandomHorizontalFlip(p=0.5) + Normalize`
4. **Flip90:** `RandomHorizontalFlip(p=0.9) + Normalize`
5. **Rotation:** `RandomRotation(degrees=15) + Normalize`

### Seeds
n=5: {42, 123, 456, 789, 1011}

**Total Experiments:** 5 conditions × 5 seeds = **25 experiments**

### Evaluation Metrics

**Primary:**
- Per-class test accuracy (10 classes: digits 0-9)
- Symmetric accuracy: mean({0, 1, 8})
- Asymmetric accuracy: mean({2, 3, 5, 6, 7, 9})
- Accuracy gap: symmetric - asymmetric

**Statistical Tests:**
- Wilcoxon signed-rank test (paired, n=5, α=0.05)
- Cohen's d effect size (threshold: d ≥ 0.5)
- Spearman rank correlation for dose-response

### Compute Requirements

- **Time Estimate:** ~3 hours sequential, **~45 minutes** with 4-core parallelization
- **Hardware:** CPU sufficient (no GPU required)
- **Disk Space:** <100MB (MNIST dataset + checkpoints)

---

## Validation Gate (MUST_WORK)

### Gate Criteria (All Must Pass)

1. **Differential Effect:**  
   Asymmetric digit accuracy significantly lower with flip vs baseline (Wilcoxon p<0.05, Cohen's d≥0.5)

2. **Dose-Response:**  
   Spearman ρ between flip probability {0.3, 0.5, 0.9} and asymmetric accuracy is significantly negative (p<0.05)

3. **Positive Control:**  
   Rotation ±15° does NOT significantly harm asymmetric digits differentially (isolates semantic effect)

### Decision Tree

- **SUCCESS (3/3 criteria):** Semantic validity principle validated → Proceed to Phase 6 (Paper Writing)
- **PARTIAL (1-2 criteria):** Mechanism partially supported → Phase 4.5 Synthesis + decide on EXPLORE vs ABANDON
- **FAIL (0 criteria):** Hypothesis rejected, no semantic effect detected → ABANDON or redesign

---

## How This Avoids Previous Failures

### Lessons from 7 Failure Records Incorporated

| Previous Failure | Avoidance Strategy |
|---|---|
| h-e1/h-m2: SAM/SWA consistently harmed robustness | ✅ No SAM/SWA — simple ablation design (baseline vs aug) |
| h-e1 Run 4: Temporal separation invalidated | ✅ No temporal separation assumptions — static experiment design |
| h-e1 Run 2: n=2 underpowered | ✅ n=5 seeds validated, proper statistical tests |
| h-e1 Run 3: No parallelization (3× slower) | ✅ Parallelization planned (45 min vs 3 hours) |
| h-e1 Run 1: Path bugs | ✅ Standard PyTorch patterns, avoid hardcoded paths |
| h-e1 Limitation: 120 GPU-hours incompatible | ✅ CPU-only, 45 min total (fits unattended constraints) |
| h-e1 Run 2 Limitation: SAM+SWA worse than components | ✅ No compositional methods — single augmentation per condition |

### What Showed Promise (Preserved)

- ✅ Per-class accuracy metrics (measurement approach from h-e1)
- ✅ Statistical significance testing (Wilcoxon, Cohen's d validated in h-e1 Run 2)
- ✅ Multi-seed validation protocol (n=5 learned from failures)

---

## Persona Consensus Summary

### Unanimous Agreement (6/6 Personas)

- Hypothesis is **testable** with clear falsification criteria
- Mechanism is **theoretically sound** (label noise → degradation)
- Novelty is **genuine** (first explicit test of semantic invalidity)
- Feasibility is **high** (existing dataset, simple design, low compute)
- **Avoids all previous failure modes**
- Dose-response strengthens quantitative claim

### Strong Support (4/6)

- 🔭 **Dr. Nova:** "Exactly what we needed — simple, testable, scientifically meaningful"
- 🎯 **Dr. Sage:** "Establishes general principle, not just dataset-specific finding"
- 🛡️ **Dr. Ally:** "Defensible, grounded in theory, ready to defend against 'trivial' criticism"
- ⚙️ **Prof. Pax:** "Feasibility checks pass, low-risk, avoids all failure modes"

### Conditional Support (2/6)

- 🔬 **Prof. Vera:** "Methodologically sound, but power concern if effect <0.5%" (mitigated by dose-response)
- 🔍 **Prof. Rex:** "Most concerns addressed, but need visual evidence and rigorous definitions"

### Recommendation

✅ **PROCEED TO PHASE 2B** (Verification Protocol Design)  
**Confidence:** HIGH  
**Consensus:** 6/6 support (4 strong, 2 conditional with minor reservations)

---

## Next Steps

### Phase 2B (Verification Protocol)

1. Formalize gate criteria decision tree
2. Define exact success/partial/fail thresholds
3. Specify contingency plans if predictions don't hold

### Phase 2C (Experiment Design)

1. Finalize CNN architecture code (PyTorch Sequential or nn.Module)
2. Specify augmentation transform pipelines for each condition
3. Design per-class accuracy extraction pipeline
4. Plan statistical test code (Wilcoxon, Cohen's d, Spearman)
5. Design visualizations:
   - Per-class accuracy heatmap (10 classes × 5 conditions)
   - Dose-response scatter plot (flip prob vs asymmetric accuracy)
   - Flipped digit examples (show semantic invalidity visually)

### Phase 3 (Implementation Planning)

1. PRD: Define requirements for experiment runner
2. Architecture: Code structure, data pipeline, training loop, evaluation
3. PRP: Parallelization strategy, checkpoint saving, error handling

### Phase 4 (Coding & Validation)

1. Implement training pipeline
2. Run 25 experiments
3. Compute statistical tests
4. Generate visualizations
5. Validate against gate criteria

---

## Supporting Evidence

### From Phase 1 Research

- MNIST baseline ~98-99% without augmentation (well-established)
- PyTorch official examples **avoid** horizontal flip for MNIST (implicit semantic concern)
- No published source validates semantic correctness before applying flip
- Horizontal flip common for ImageNet (left/right symmetry valid for most objects)

### From Label Noise Literature

- Training on mislabeled examples degrades test accuracy (Natarajan et al., Zhang et al.)
- Effect stronger when label noise is class-specific (asymmetric noise)
- Partial learning still possible with large datasets

### From Serena Memory (Previous Failures)

- SAM/SWA methods failed 5 times (avoid optimization tricks)
- Temporal separation hypothesis invalidated (models learn spurious features immediately)
- n<5 seeds insufficient (h-e1 Run 2 underpowered at n=2)
- Implementation quality matters (paths, parallelization)
- Avoid compositional complexity (SAM+SWA worse than SAM alone)

---

**Status:** ✅ HYPOTHESIS READY FOR VERIFICATION PROTOCOL DESIGN  
**Next Phase:** Phase 2B - Research Planning  
**Estimated Timeline:** Phase 2B (30 min) → Phase 2C (1 hour) → Phase 3 (2 hours) → Phase 4 (4-6 hours)  
**Overall Risk:** **LOW** — All previous failure modes avoided, feasibility validated

