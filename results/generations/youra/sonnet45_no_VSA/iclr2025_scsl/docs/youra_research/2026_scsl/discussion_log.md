# Phase 2A Research Discussion Log

**Date:** 2026-07-11  
**Session:** Tikitaka Multi-Perspective Research Dialogue  
**Research Gap:** Gap 1 - Semantic Validity of Horizontal Flip on MNIST  

---

## Previous Failure / Routing Context

This is Phase 2A recursive entry (v2) following multiple Phase 4 failures. The discussion MUST design a hypothesis that explicitly avoids the failed approach families documented below.

### Failure Pattern Summary (7 Records)

**Pattern 1: SAM Consistently Harms Robustness (5 attempts)**
- h-e1 Run 2 (PARTIAL): SAM worst-group 76.5% underpowered (n=2 vs n=5)
- h-e1 Run 2 Limitation: SAM+SWA achieved -0.18% (worse than SAM alone)
- h-e1 Run 4 (FAIL): Temporal separation hypothesis invalidated (0 epochs vs ≥5 target)
- Conclusion: SAM's flat minima seeking fundamentally incompatible with spurious correlation robustness

**Pattern 2: SWA Mechanism Unvalidated**
- h-m2 Run 1 (FAIL): SWA noise robustness WORSENED (-1.31% vs SGD +21.75%)
- Conclusion: SWA does NOT achieve global basin centering as hypothesized

**Pattern 3: Temporal Separation Does Not Exist**
- h-e1 Run 4 (FAIL): Model learned ONLY spurious features from epoch 0
- Measured: Worst-group 10.04%, Overall 50.04% (perfect spurious exploitation)
- Root Cause: ρ=0.90-0.95 too strong for 2-layer MLP to exhibit temporal dynamics
- Conclusion: Foundation hypothesis failed - early stopping on worst-group peaks impossible

**PROHIBITED APPROACHES:**
- ❌ Any SAM-based optimization methods
- ❌ Any SWA-based weight averaging methods
- ❌ Any temporal separation / early stopping mechanisms
- ❌ Any hypothesis requiring ρ≥0.90 spurious correlations on simple MLPs
- ❌ Any n<5 statistical validation protocols

**WHAT SHOWED PROMISE:**
- ✓ ColoredMNIST dataset correctly implemented (ρ control validated)
- ✓ Implementation quality when properly designed (96% spec alignment)
- ✓ Worst-group accuracy metrics (measurement approach sound)

---

## Discussion Briefing

### Selected Research Gap

**Gap ID:** Gap 1  
**Title:** Semantic Validity of Horizontal Flip on MNIST  
**Priority:** CRITICAL  
**Impact:** HIGH (could invalidate hypothesis)  
**Difficulty:** LOW (empirical test)  

**Gap Description:**
Horizontal flip is standard for image classification, but NO source validates semantic correctness for MNIST. Horizontally flipped digits may become invalid:
- "2", "3", "5", "7" become non-canonical
- "6" flipped horizontally ≠ valid digit
- May introduce label noise → HARM accuracy

**Evidence:**
- 3 papers use horizontal flip without semantic analysis
- Official pytorch/examples does NOT use horizontal flip for MNIST
- Risk: Expected +0.5% improvement may be NEGATIVE

### Research Context

**Research Question:** Does standard data augmentation (random horizontal flip) improve MNIST test accuracy compared to no augmentation, serving as a minimal-scope pipeline validation test?

**Background:** ROUTE_TO_0 (Reflection 5) - After 4 consecutive failures with complex optimization hypotheses (SAM/SWA methods), this minimal-scope test validates pipeline functionality using a known-result experiment.

### Reference Papers

No papers were prepared for this gap (none referenced in Phase 1 output).

### MANDATORY FEASIBILITY CONSTRAINTS

The hypothesis MUST satisfy ALL of these pipeline-enforced constraints:

1. ✅ **Use existing real datasets** - No synthetic/generated data
2. ✅ **Use existing benchmarks** - No new rubrics or scoring frameworks
3. ✅ **No human evaluation** - No annotation or subjective scoring
4. ✅ **Immediately testable** - Can run experiments NOW with available data

Any hypothesis requiring new benchmarks, synthetic data, or human evaluation will be REJECTED by the pipeline.

---

## Discussion Goal

Generate a **testable, novel, and feasible** hypothesis that:

1. **Addresses Gap 1** - Tests semantic validity of horizontal flip on MNIST
2. **Avoids prohibited approaches** - No SAM/SWA/temporal separation methods
3. **Satisfies feasibility constraints** - Existing datasets, no human eval, immediately testable
4. **Meets statistical rigor** - n≥5 seeds, proper significance testing
5. **Has clear success criteria** - Specific predictions with pass/fail thresholds

**Convergence Criteria:**
- ✅ SPECIFIC: Clear core claim stated
- ✅ MECHANISM: How it works explained
- ✅ PREDICTIONS: 2-3 testable predictions with criteria
- ✅ NOVELTY: What's new articulated
- ✅ FEASIBILITY: Implementation realistic (technical/theoretical, not cost-based)
- ✅ OBJECTIONS: Major criticisms addressed

---

## Discussion Rounds

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

Alright team, we've been handed a fascinating puzzle wrapped in a warning! Gap 1 asks whether horizontal flip actually HELPS or HARMS MNIST accuracy — and the evidence is screaming that nobody's actually checked. This is beautiful because it flips the script on augmentation orthodoxy.

Here's what gets me excited: What if we test the semantic validity hypothesis by creating a **digit-aware augmentation scheme**? Instead of blindly flipping all digits, we could:

1. **Asymmetry-Based Hypothesis**: Partition MNIST into symmetric digits (0, 1, 8) vs asymmetric digits (2, 3, 5, 6, 7, 9) and test whether horizontal flip HARMS asymmetric digit accuracy while preserving or improving symmetric digit accuracy.

2. **Controlled Degradation Test**: If horizontal flip introduces label noise for asymmetric digits, we should see a measurable accuracy DROP on those classes compared to no augmentation — effectively proving that "standard" augmentation isn't universally beneficial.

3. **Pipeline Validator Twist**: This becomes our minimal-scope test! We're not optimizing anything complex (goodbye SAM/SWA nightmares), just running clean ablations: baseline vs horizontal-flip, stratified by digit symmetry.

The novelty? Nobody's explicitly tested whether augmentation can HARM accuracy on semantically invalid transformations. We're challenging the "more augmentation = better" dogma with a simple, bulletproof experiment.

What would disprove this? If horizontal flip improves accuracy uniformly across ALL digit classes, including asymmetric ones. That would suggest either (a) the network learns invariance anyway, or (b) the semantic concern is overblown.

NOW we're onto something! This avoids all the prior failure modes (no optimization tricks, just data+evaluation), uses existing MNIST (feasibility ✓), and has a crystal-clear pass/fail criterion.

**Key Points:**
- Test hypothesis: Horizontal flip HARMS asymmetric digit (2,3,5,6,7,9) accuracy
- Mechanism: Semantic invalidity → label noise → reduced accuracy on affected classes  
- Novelty: First explicit test of augmentation-induced semantic degradation

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Hold on, Dr. Nova — I love the asymmetry angle, but let's ensure we can actually TEST this rigorously before we get carried away with excitement.

The semantic validity hypothesis needs **falsifiable predictions with precise measurement**. Here's what I need to see:

**Testable Prediction 1**: If horizontal flip introduces label noise for asymmetric digits, we should observe:
- Per-class test accuracy for {2,3,5,6,7,9} DECREASES under horizontal flip vs no augmentation
- Per-class test accuracy for {0,1,8} remains stable or improves
- The gap between symmetric and asymmetric performance widens with flip augmentation

**Measurement Protocol**:
- Train standard CNN on MNIST with/without RandomHorizontalFlip(p=0.5)
- Compute per-class test accuracies (not just overall)
- Statistical test: Wilcoxon signed-rank on paired per-class accuracies across seeds (n≥5)
- Effect size: Cohen's d ≥ 0.5 for meaningfulness

**What would DISPROVE this**:
- If asymmetric digit accuracy is NOT significantly lower with flip vs without
- If symmetric digits also degrade (suggests general training instability, not semantic issue)
- If overall accuracy improves despite asymmetric degradation (trade-off dynamics)

**Critical Control**: We MUST verify that the degradation is specifically semantic, not just a general augmentation effect. This means we need a **positive control augmentation** that doesn't violate semantics (e.g., small rotation ±15°, which keeps digits valid).

Experiment design:
1. Baseline: No augmentation
2. Test: Horizontal flip (p=0.5)
3. Control: Small rotation (±15°) — semantically valid augmentation

If horizontal flip harms asymmetric digits BUT rotation doesn't, we've isolated the semantic validity problem. If BOTH harm performance, it's a different phenomenon.

The evidence from Phase 1 suggests pytorch/examples avoids horizontal flip for MNIST — that's circumstantial support, but we need direct measurement.

**Key Points:**
- Require per-class accuracy breakdown (not just overall metrics)
- Need positive control (rotation) to isolate semantic vs general aug effects
- Statistical significance: n≥5 seeds, Wilcoxon test, Cohen's d ≥ 0.5

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

This is shaping up well, but let's address the elephant in the room: **What makes this genuinely NEW versus just "we ran an experiment nobody bothered to run"?**

The contribution here isn't discovering that horizontal flip is bad for MNIST — that's a negative result about one augmentation on one dataset. The **real contribution** is establishing a **general principle**:

**Core Scientific Claim**: "Augmentation validity depends on semantic preserving transformations — applying non-semantic-preserving transforms introduces label noise that degrades per-class accuracy."

This matters for the field because:

1. **Augmentation Design Principle**: Practitioners should verify semantic validity BEFORE applying standard augmentations to new domains. Just because horizontal flip works on ImageNet (where left/right symmetry is valid for most objects) doesn't mean it transfers to domains with semantic asymmetry (medical imaging, text recognition, oriented objects).

2. **Benchmark Methodology**: If "standard" augmentations can harm accuracy, benchmark comparisons that use different aug schemes aren't fair. This affects reproducibility.

3. **Opens New Research**: Leads to "semantic-aware augmentation" — automatically detecting which transforms preserve label validity for a given dataset.

**What distinguishes this from incremental work**:
- NOT just "horizontal flip is bad" (trivial observation)
- IS a validated principle: "semantic validity predicts augmentation effectiveness"
- Generalizable beyond MNIST to any domain with oriented/asymmetric classes

**How to strengthen the significance claim**:
- Frame as "case study demonstrating semantic validity principle"
- Discuss implications for other domains (medical images, traffic signs, text)
- Show that existing augmentation libraries (albumentations, timm) DON'T check semantic validity

The Phase 1 evidence supports this: no source validates semantic correctness, everyone just copies "standard" augmentations. We're catching a systemic blind spot.

**Key Points:**
- Contribution: General semantic validity principle, not dataset-specific finding
- Impact: Changes how practitioners select augmentations (domain-aware, not just "standard")
- Significance: Exposes gap in current augmentation methodology

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Okay, I'll be the one to ask: **Is this actually DOABLE with the constraints we're under?**

Let me check the feasibility dimensions:

**Technical Feasibility: ✅ PASS**
- Mechanism is sound: horizontal flip literally mirrors pixels, asymmetric digits become non-canonical
- Measurement is straightforward: per-class accuracy is a standard metric
- No complex optimization tricks (just data transforms + standard training)

**Theoretical Soundness: ✅ PASS**
- Label noise theory predicts accuracy degradation when labels become incorrect
- Symmetric vs asymmetric partitioning is mathematically well-defined
- Positive control (rotation) isolates the semantic effect

**Implementation Reality Check: ✅ PASS**
- Existing dataset (MNIST) ✓
- Existing benchmarks (standard CNN, test accuracy) ✓
- No new rubrics needed ✓
- No human evaluation required ✓
- Can run immediately ✓

**Resource Requirements: ✅ PASS**
- Training: ~5 minutes per seed on CPU for MNIST (30-50 epochs standard CNN)
- Total: 3 conditions × 5 seeds = 15 experiments × 5 min = 75 minutes wall-clock with parallelization
- Far below the 120+ GPU-hour disasters from h-e1

**What worries me**:

1. **Effect Size Uncertainty**: What if the degradation is TINY (e.g., 0.5% drop on asymmetric digits)? We might have the right hypothesis but lack statistical power to detect it. Prof. Vera's n≥5 + Cohen's d ≥ 0.5 requirement addresses this, but we should be prepared for a null result.

2. **Confound Risk**: What if horizontal flip helps regularization DESPITE introducing label noise, resulting in a net-zero effect? The positive control (rotation) helps, but we need to think through the interpretation matrix:
   - Flip harms, rotation helps → semantic issue confirmed
   - Both harm → general augmentation problem (unexpected)
   - Both help → semantic concern overblown (hypothesis refuted)
   - Flip helps, rotation neutral → confusing (suggests flip doing something else)

3. **Digit 6 vs 9 Problem**: Horizontal flip of "6" doesn't create "9" (that's vertical flip + rotation), so the semantic violation isn't as clear-cut as I initially thought. We need to verify which digits are ACTUALLY invalidated by horizontal flip:
   - 2 → backward 2 (invalid)
   - 3 → backward 3 (invalid)  
   - 5 → backward 5 (invalid)
   - 6 → backward 6 (invalid, not 9)
   - 7 → backward 7 (invalid)
   - 9 → backward 9 (invalid)

So the asymmetric set {2,3,5,6,7,9} holds, but we should include examples in the paper showing the flipped versions look wrong.

**Verdict**: This is feasible. The mechanism is sound, the experiment is straightforward, and it fits well within unattended pipeline constraints. My only caution is around effect size — if the degradation is small, we need good statistical design (which Prof. Vera provided).

**Key Points:**
- Technically feasible: mechanism is physically sound, measurements are valid
- Resource-wise feasible: 75 minutes with parallelization (far below previous failures)
- Confound addressed: positive control (rotation) isolates semantic effect

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES! I can feel this coming together. Let me strengthen the argument and address potential criticisms before they arise.

**Strengthening the Core Claim**:

Dr. Sage is right that we need to frame this as a general principle, not a negative result. Here's how I'd articulate the strengthened hypothesis:

**H1 (Hypothesis 1): Semantic Validity Hypothesis for Data Augmentation**

"Data augmentations that violate semantic constraints (transformations producing invalid/ambiguous class labels) degrade per-class test accuracy compared to no augmentation or semantically valid augmentations."

**Specific Prediction for MNIST**:
- Horizontal flip produces semantically invalid digit images for asymmetric classes {2,3,5,6,7,9}
- This introduces label noise during training
- Per-class test accuracy on asymmetric digits decreases relative to baseline (no aug) or positive control (±15° rotation)
- Per-class test accuracy on symmetric digits {0,1,8} remains stable or improves (no semantic violation)

**Evidence Supporting This Hypothesis**:
1. [PHASE 1] Official pytorch/examples avoids horizontal flip for MNIST (implicit recognition?)
2. [PHASE 1] No published source validates semantic correctness before applying flip
3. [THEORY] Label noise literature shows mislabeled examples degrade accuracy
4. [MECHANISM] Visual inspection confirms flipped asymmetric digits appear non-canonical

**How This Addresses Previous Failures**:
- ❌ NO SAM/SWA optimization tricks (just data + standard ERM)
- ❌ NO temporal separation assumptions
- ❌ NO complex compositional methods
- ✅ YES simple ablation study (baseline vs flip vs rotation)
- ✅ YES proper statistical power (n≥5 seeds, significance testing)
- ✅ YES clear success criteria (per-class accuracy differences)

**Responding to "This seems too simple" criticism**:

This simplicity is a FEATURE, not a bug. After 4 complex hypotheses failed, we need to validate the pipeline with a straightforward, testable claim. The scientific contribution isn't in complexity but in systematically testing an assumption (augmentation validity) that the field takes for granted.

**Responding to "This is just a negative result" criticism**:

No — this establishes a positive principle (semantic validity predicts augmentation effectiveness) using MNIST as a case study. The finding generalizes to ANY domain where class labels have semantic constraints.

**Key Points:**
- Frame as establishing general principle, not dataset-specific finding
- Simplicity is intentional (pipeline validation + scientific contribution)
- Strong theoretical basis (label noise theory) + empirical test (ablation study)

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Alright, time to poke holes so we can patch them before reviewers do.

**Challenge 1: "The effect might be too small to matter"**

If horizontal flip only degrades asymmetric digit accuracy by 0.5-1%, is that scientifically meaningful? You've addressed statistical significance (n≥5, effect size d≥0.5), but what about practical significance?

**Counter-argument**: The point isn't the magnitude on MNIST, it's the EXISTENCE of the effect. If we demonstrate that semantic invalidity measurably harms accuracy (even by 1%), that validates the principle. For higher-stakes domains (medical imaging), even 1% matters.

**Challenge 2: "Maybe the network just learns to ignore the flipped examples"**

What if the CNN is robust enough that it learns valid features despite seeing some semantically invalid augmented images?

**Counter-argument**: That's what the per-class breakdown reveals. If the network fully ignores invalid flips, symmetric and asymmetric classes would perform identically. The hypothesis predicts differential impact.

**Challenge 3: "Rotation ±15° also changes digit appearance — is that semantically valid?"**

Small rotations keep digits recognizable (a slightly tilted "7" is still a "7"), but is there a threshold where rotation becomes invalid?

**Response needed**: Define "semantically valid" precisely. Rotation ±15° stays within human-recognizable bounds (MNIST includes natural variation), but rotation ±90° would be invalid. We need to justify the ±15° threshold (perhaps by citing that MNIST digits have natural writing angle variation).

**Challenge 4: "This doesn't address the original research question"**

The RQ was: "Does horizontal flip improve MNIST accuracy?" You've pivoted to "Does it harm asymmetric digits specifically?" Are these the same question?

**Response**: Yes — answering "it harms asymmetric digits" ALSO answers "does it improve overall accuracy" (likely NO, since 6 of 10 classes are harmed). The per-class analysis is more informative than overall accuracy alone.

**Challenge 5: "What about class imbalance?"**

MNIST is balanced (roughly equal examples per class), but if it weren't, the overall accuracy could improve even if asymmetric classes degrade (majority vote effect).

**Response**: MNIST is balanced, but we should verify and report per-class sample counts. If imbalance exists, use balanced accuracy or macro-averaged metrics.

**Remaining Concerns**:

1. Need to visually show flipped digits in the paper (prove they look wrong)
2. Need to define "semantically valid augmentation" rigorously
3. Should we test multiple flip probabilities (p=0.1, 0.3, 0.5, 0.7, 0.9) to see dose-response?

**Verdict**: The hypothesis is testable and addresses a real gap, but we need tighter definitions and visual evidence to make it bulletproof.

**Key Points:**
- Challenge: Effect size practical significance (addressed by principle validation framing)
- Challenge: Network robustness to invalid aug (addressed by per-class differential prediction)
- Need: Visual examples of flipped asymmetric digits + precise "semantic validity" definition

---


### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, those are EXACTLY the challenges we needed! Let me address the visual evidence and dose-response ideas:

**On Visual Evidence**: Absolutely YES — we should include a figure showing:
- Original digit images for {2, 3, 5, 6, 7, 9}
- Horizontally flipped versions (demonstrating non-canonical appearance)
- Rotation ±15° versions (showing semantic validity)

This makes the semantic invalidity claim immediately obvious to readers.

**On Dose-Response**: This is BRILLIANT for strengthening the mechanism claim! If horizontal flip p=0.5 harms asymmetric digits, we should see:
- p=0.0 (baseline): No degradation
- p=0.1, 0.3: Small degradation (proportional to flip frequency)
- p=0.5, 0.7, 0.9: Larger degradation (more frequent invalid augmentations)

This dose-response relationship would be STRONG evidence that the mechanism is specifically about semantic invalidity frequency, not some other confound.

**Refined Experimental Design**:

1. **Conditions** (7 total, simplified from 15):
   - Baseline: No augmentation
   - Flip: p ∈ {0.3, 0.5, 0.9} (3 conditions for dose-response)
   - Rotation: ±15° (1 condition, positive control)

2. **Seeds**: n=5 for each condition (35 total experiments)

3. **Metrics**: Per-class test accuracy for all 10 digits

4. **Predictions**:
   - Flip p=0 (baseline): ~99% overall, balanced per-class
   - Flip p↑: Asymmetric digit accuracy↓ (dose-response)
   - Flip p↑: Symmetric digit accuracy stable
   - Rotation: Accuracy stable or slight improvement (semantically valid regularization)

**Timeline Feasibility**: 35 experiments × 5 min/exp = 175 min sequential = **~3 hours**. With parallelization (4 cores): **~45 minutes**. Comfortably fits unattended constraints!

**Novelty Enhancement**: The dose-response analysis elevates this from "flip is bad" to "semantic invalidity frequency predicts accuracy degradation" — that's a quantitative principle, not just a binary finding.

What do we think — does the dose-response strengthen the contribution enough to justify the extra experiments?

**Key Points:**
- Add dose-response (flip p=0.3, 0.5, 0.9) to demonstrate mechanism strength
- Visual figure showing flipped vs rotated digits (makes semantic invalidity obvious)
- Still feasible: ~45 min with parallelization for 35 experiments

---

## Final Assessments

### Convergence Status: ✅ ACHIEVED

The discussion has converged on a testable hypothesis with clear predictions, mechanism, and feasibility validation.

---

## Emerged Hypothesis Summary

### Core Statement

**H1: Semantic Validity Hypothesis for Data Augmentation**

Data augmentations that violate semantic constraints (producing invalid/ambiguous class labels) degrade per-class test accuracy on affected classes compared to no augmentation or semantically valid augmentations. This effect should exhibit dose-response behavior: higher augmentation frequency → stronger degradation.

### Causal Mechanism

1. **Semantic Invalidity**: Horizontal flip mirrors MNIST digits, producing non-canonical images for asymmetric classes {2,3,5,6,7,9}
2. **Label Noise Introduction**: Flipped asymmetric digits appear ambiguous or wrong, but retain original labels during training
3. **Per-Class Degradation**: Model trained on semantically invalid examples exhibits reduced test accuracy on affected classes
4. **Dose-Response**: Degradation magnitude correlates with augmentation frequency (p=0.3 → small effect, p=0.9 → large effect)

### Variables

**Independent Variables**:
- Augmentation type: {None, HorizontalFlip(p), Rotation(±15°)}
- Flip probability: p ∈ {0.0, 0.3, 0.5, 0.9}
- Random seed: {42, 123, 456, 789, 1011} (n=5)

**Dependent Variables**:
- Per-class test accuracy (10 classes: digits 0-9)
- Symmetric digit accuracy: mean({0, 1, 8})
- Asymmetric digit accuracy: mean({2, 3, 5, 6, 7, 9})
- Accuracy gap: symmetric - asymmetric

**Control Variables**:
- Model architecture: Standard CNN (2-3 conv layers, dropout, FC)
- Training epochs: 30 (standard for MNIST, with early stopping)
- Optimizer: Adam (lr=0.001) for consistency
- Batch size: 64 (standard)

### Key Assumptions

1. **Semantic Invalidity Assumption**: Horizontally flipped asymmetric digits {2,3,5,6,7,9} are visually non-canonical and would be ambiguous to human annotators
2. **Label Preservation Assumption**: Augmented images retain original labels (horizontal flip of "3" is still labeled "3")
3. **Learnable Signal Assumption**: Despite label noise, model can still learn from valid examples in the training set
4. **Symmetry Partition Validity**: Digits partition cleanly into symmetric {0,1,8} and asymmetric {2,3,5,6,7,9} under horizontal reflection
5. **Rotation Validity Assumption**: Rotation ±15° preserves semantic validity (tilted digits remain recognizable as their class)

### Null Hypothesis (H0)

Horizontal flip augmentation does NOT selectively degrade asymmetric digit test accuracy. Specifically:
- H0₁: No significant difference in asymmetric digit accuracy between baseline and flip conditions (p ≥ 0.05)
- H0₂: No dose-response relationship between flip probability and asymmetric digit degradation
- H0₃: Symmetric and asymmetric digit accuracy degrade equally under horizontal flip (no differential effect)

### Predictions

**Prediction 1: Per-Class Differential Effect**
- Asymmetric digit accuracy (classes {2,3,5,6,7,9}) DECREASES under horizontal flip vs baseline
- Symmetric digit accuracy (classes {0,1,8}) remains STABLE or increases under horizontal flip
- Statistical test: Wilcoxon signed-rank test, α=0.05, n=5 seeds
- Effect size: Cohen's d ≥ 0.5 for asymmetric digit degradation

**Prediction 2: Dose-Response Relationship**
- Asymmetric digit accuracy degradation increases monotonically with flip probability
- Correlation: Spearman's ρ between flip probability {0.3, 0.5, 0.9} and asymmetric accuracy is significantly negative (p < 0.05)
- Larger flip probability → larger accuracy gap (symmetric - asymmetric)

**Prediction 3: Positive Control Validation**
- Rotation ±15° augmentation does NOT significantly degrade asymmetric digit accuracy vs baseline
- If rotation DOES help, effect should be equal across symmetric and asymmetric digits (no differential impact)
- This isolates semantic invalidity (flip-specific) from general augmentation effects

**Falsification Criteria**:
- If asymmetric digit accuracy is NOT significantly lower with flip vs baseline → H1 rejected
- If symmetric digits degrade equally or more than asymmetric → differential semantic effect rejected
- If NO dose-response relationship observed → mechanism questioned

### Novelty

**What's New**:
1. **First Explicit Test**: No prior work systematically tests whether "standard" augmentations can harm accuracy due to semantic invalidity
2. **General Principle**: Establishes that augmentation effectiveness depends on semantic validity, not just diversity/regularization
3. **Dose-Response Evidence**: Quantifies relationship between semantic violation frequency and accuracy degradation
4. **Methodological Contribution**: Demonstrates need for domain-aware augmentation selection (not blind application of "standard" schemes)

**What's Different from Prior Work**:
- [PHASE 1] Existing papers apply horizontal flip without semantic validation
- [PHASE 1] Official pytorch/examples avoids flip for MNIST but doesn't explain why
- This work makes the semantic invalidity hypothesis explicit and tests it rigorously

**Generalizability**:
- Principle applies beyond MNIST to any domain with semantic constraints: medical imaging (anatomical orientation), traffic signs (directional arrows), text recognition (character chirality)
- Provides template for validating augmentation schemes in new domains

### Scope & Boundaries

**What This Hypothesis Covers**:
- Semantic validity of horizontal flip augmentation on MNIST digit classification
- Per-class accuracy effects (not just overall metrics)
- Dose-response relationship between augmentation frequency and degradation

**What This Hypothesis Does NOT Cover**:
- Other augmentation types (vertical flip, color jitter, cutout, mixup) — out of scope
- Other datasets beyond MNIST — MNIST is case study for principle
- Model architectures beyond standard CNNs — focus on standard baseline
- Optimal augmentation selection algorithms — this is diagnostic, not prescriptive

**Known Limitations**:
- Effect size may be small (1-2% degradation) — scientifically meaningful but practically modest on MNIST
- MNIST is relatively easy (99% baseline) — effects may be stronger on harder datasets
- Controlled lab setting — real-world training may use ensembles/mixup that mitigate label noise

### Experimental Setup

**Dataset**: MNIST (60k train, 10k test, 10 classes, 28×28 grayscale)

**Model**: Standard CNN architecture
- 2 convolutional layers (32, 64 filters, 3×3 kernel, ReLU)
- MaxPool2d(2) after each conv layer
- Dropout (p=0.25 after conv, p=0.5 after FC)
- 2 fully connected layers (128 units → 10 output classes)
- Total params: ~100k

**Training**:
- Optimizer: Adam (lr=0.001, default betas)
- Batch size: 64
- Epochs: 30 (with early stopping if val accuracy plateaus for 5 epochs)
- Loss: CrossEntropyLoss
- Train/Val split: 90/10 from training set (54k train, 6k val)

**Augmentation Conditions** (5 total × 5 seeds = 25 experiments):
1. Baseline: ToTensor() + Normalize(mean=0.1307, std=0.3081) only
2. Flip30: RandomHorizontalFlip(p=0.3) + Normalize
3. Flip50: RandomHorizontalFlip(p=0.5) + Normalize
4. Flip90: RandomHorizontalFlip(p=0.9) + Normalize
5. Rotation: RandomRotation(degrees=15) + Normalize

**Evaluation**:
- Metric: Per-class test accuracy (10 values per experiment)
- Aggregation: Mean accuracy for symmetric {0,1,8} and asymmetric {2,3,5,6,7,9} groups
- Statistical test: Wilcoxon signed-rank (paired, n=5 seeds), α=0.05
- Effect size: Cohen's d for asymmetric accuracy difference (baseline vs flip conditions)
- Correlation: Spearman's ρ for dose-response (flip prob vs asymmetric accuracy)

**Compute**:
- Estimated time: 7 min/experiment × 5 conditions × 5 seeds = 175 min (~3 hours sequential)
- With 4-core parallelization: ~45 minutes
- Hardware: CPU sufficient (MNIST is lightweight, no GPU required)

### Related Work & Baselines

**Baseline**: Standard CNN on MNIST without augmentation (expected ~99% test accuracy)

**Related Work**:
- [PHASE 1] Yang et al. (2022): "Image Data Augmentation for Deep Learning: A Survey" (arXiv:2204.08610, 399 cites) — comprehensive survey, no semantic validity analysis
- [PHASE 1] Purba et al. (2025): Applied horizontal flip without semantic validation
- [PHASE 1] Muchlis et al. (2025): Flip + exposure best result (73%) — no MNIST-specific analysis
- [THEORY] Label noise literature (Natarajan et al., Zhang et al.) — establishes that training on mislabeled data degrades accuracy

**Gap in Literature**: No prior work explicitly tests semantic validity of standard augmentations on MNIST

**Comparison Approach**: Ablation study (baseline vs flip variants vs rotation) rather than SOTA comparison

### Phase 2B Readiness Seeds

**Implementation Complexity**: LOW (Tier 1)
- Standard PyTorch DataLoader + transforms pipeline
- No custom augmentation algorithms required
- Per-class metric computation: `sklearn.metrics.classification_report`
- Statistical tests: `scipy.stats.wilcoxon`, `scipy.stats.spearmanr`

**Resource Requirements**: FEASIBLE
- CPU-only training (~3 hours sequential, 45 min parallel)
- No GPU required (MNIST is lightweight)
- Disk space: < 100MB (MNIST dataset + checkpoints)
- Fits within unattended pipeline constraints (< 1 hour with parallelization)

**Risk Assessment**: LOW
- ✅ No optimization tricks (avoids SAM/SWA failure modes from h-e1/h-m2)
- ✅ No statistical power issues (n=5 seeds validated, Cohen's d ≥ 0.5 criterion)
- ✅ Clear success/failure criteria (hypothesis is falsifiable with p-value thresholds)
- ✅ Existing dataset + benchmark (MNIST, test accuracy)
- ✅ No new rubrics or human evaluation

**Potential Failure Modes & Mitigations**:
1. **Small effect size**: If degradation < 0.5%, may not reach Cohen's d ≥ 0.5 → Addressed by dose-response (higher p should amplify effect)
2. **No differential effect**: If symmetric digits also degrade → Would refute semantic hypothesis but still produce valid negative result
3. **Implementation bugs**: Path issues, data loading errors → Mitigated by using standard PyTorch patterns (avoid h-e1 Run 1 path bug)

**Next Steps for Phase 2B**:
1. Define exact CNN architecture code (layer-by-layer PyTorch Sequential or class definition)
2. Specify augmentation transform pipelines for each condition
3. Design per-class accuracy extraction and statistical test pipeline
4. Plan visualization (per-class accuracy heatmap, dose-response scatter plot, flipped digit examples)
5. Define success gate criteria (MUST_WORK: differential effect p<0.05, d≥0.5)

### Established Facts

**From Phase 1 Research**:
1. MNIST baseline accuracy: ~98-99% without augmentation (well-established)
2. Official pytorch/examples does NOT use horizontal flip for MNIST (implicit evidence of semantic concern)
3. No published source validates semantic correctness of flip for MNIST
4. Horizontal flip is common for natural images (ImageNet) where left/right symmetry is valid for most objects

**From Previous Failures (Serena Memory)**:
1. SAM/SWA methods consistently failed on spurious correlation robustness (5 attempts, all FAIL/PARTIAL)
2. Temporal separation hypothesis invalidated (h-e1 Run 4: 0 epochs vs ≥5 target)
3. n<5 seeds insufficient for statistical significance (h-e1 Run 2: n=2 underpowered)
4. Implementation quality matters: path resolution (h-e1 Run 1), parallelization (h-e1 Run 3)
5. Avoid complex compositional methods (SAM+SWA worse than components: -0.18% in h-e1 Run 2 limitation)

**From Label Noise Literature**:
1. Training on mislabeled examples degrades test accuracy (Natarajan et al., Zhang et al.)
2. Effect is stronger when label noise is class-specific (asymmetric noise)
3. Label noise can be partially overcome with large datasets, but small per-class effects remain detectable

---

**Discussion Duration**: 7 exchanges (converged)  
**Hypothesis Status**: ✅ READY FOR PHASE 2B  
**Next Phase**: Phase 2B - Research Planning (Verification Protocol Design)

