# Phase 2A Research Discussion Log

**Date:** 2026-08-18
**Workflow:** phase2a-dialogue (Self-Contained Tikitaka Loop)
**Execution Mode:** UNATTENDED

---

## Research Gap Briefing

### Selected Gap
**Gap ID:** gap1_temporal_measurement
**Title:** Explicit Temporal Measurement of Feature Learning Order
**Priority:** PRIMARY (Critical)
**Relevance:** Directly blocks answering main research question

### Gap Description
Existing methods (JTT, LfF) use indirect proxies (misclassification, loss values) to infer that spurious features are learned first. No direct measurement of when specific features emerge during training exists. Methods to explicitly track feature learning order during training are missing.

**Missing Piece:** Methods to explicitly track feature learning order during training. Metrics like feature probe accuracy at checkpoints or gradient-based attribution over epochs.

**Potential Impact:** HIGH - Direct evidence would validate or refute the temporal hypothesis and enable principled intervention design.

### Main Research Question
What is the relationship between training dynamics (specifically, the temporal ordering of feature learning during SGD optimization) and the model's reliance on spurious correlations, and can this relationship be exploited to improve worst-group robustness without requiring group annotations?

### Key Reference Papers

1. **Learning from Failure** (Nam et al., 2020) - arXiv:2007.02561
   - Key Insight: Infers early bias reliance but doesn't measure directly

2. **The Pitfalls of Simplicity Bias** (Shah et al., 2020) - arXiv:2006.07710
   - Key Insight: Proves simplest features learned but no temporal tracking

3. **Catapults in SGD** (Zhu et al., 2023) - arXiv:2306.04815
   - Key Insight: Loss dynamics affect feature learning but no per-feature timing

4. **Just Train Twice** (Liu et al., 2021) - arXiv:2107.09044
   - Key Insight: Uses early misclassifications as proxy for group membership

5. **Gradient Starvation** (Pezeshki et al., 2020) - arXiv:2011.09468
   - Key Insight: Cross-entropy starves complex features

### Relevant GitHub Implementations

- **anniesch/jtt** (72 stars): Two-stage training but no explicit feature tracking
- **kohpangwei/group_DRO** (294 stars): Baseline method for worst-group robustness
- **deeplearning-wisc/vit-spurious-robustness** (28 stars): Architecture comparison

### Feasibility Constraints (Pipeline-Enforced)

- Reject ideas requiring new benchmarks, rubrics, or scoring frameworks
- Reject ideas requiring synthetic/generated data or future follow-up data
- Reject ideas requiring human evaluation, annotation, or subjective scoring
- Accept only hypotheses testable immediately using existing real datasets and existing benchmarks

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from an entirely different angle? The existing literature—JTT, LfF, simplicity bias—all treats temporal feature learning as something to be *inferred* from downstream behavior. But imagine if we could *directly observe* feature emergence in real-time!

Here's a wild idea: what if the temporal ordering of feature learning isn't just a property we measure, but a **causal lever** we can manipulate? Shah et al. (2020) proved SGD finds simplest features first, but they never asked: can we *force* a different ordering? What if we could make the network learn core features *before* spurious ones through targeted gradient interventions?

I see three unconventional angles worth exploring:

1. **Linear Probe Trajectories as Feature Emergence Detectors**: Instead of training a single probe at convergence, train probes at *every* checkpoint. The epoch where a probe's accuracy crosses a threshold marks that feature's "emergence time." We'd get explicit timestamps for spurious vs. core features—no inference needed!

2. **Gradient Attribution Dynamics**: Gradient starvation (Pezeshki et al.) tells us some features get starved. But what if we tracked *which neurons* receive gradient signal at each epoch? The temporal activation pattern of gradient flow could reveal the learning order directly.

3. **Cross-Architecture Transfer as a Probe**: What if the "feature learning order" differs between ResNet and ViT? If we train both on Waterbirds and measure emergence times, divergent patterns would reveal architecture-specific dynamics that current methods completely ignore.

NOW we're onto something! The Catapults paper (Zhu et al., 2023) showed loss spikes correlate with feature learning—but they didn't connect this to spurious correlations specifically. What if those "catapult" events mark the *transition* from spurious to core feature learning?

**Key Points:**
- Direct measurement via linear probes at checkpoints could give explicit feature emergence times
- Gradient flow tracking could reveal which features are being learned when
- Cross-architecture comparison might expose dynamics invisible in ResNet-only studies

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova, your enthusiasm is infectious, but let's subject these ideas to rigorous scrutiny. The evidence must guide us, not excitement alone.

Your linear probe trajectory idea has merit, but I need precision. What specific, measurable predictions can we make? Let me propose a falsifiable hypothesis structure:

**Testable Prediction 1 (Temporal Ordering):** If we train linear probes on intermediate representations at epochs {1, 5, 10, 20, 50, convergence}, the probe accuracy for the spurious feature (e.g., background in Waterbirds) will reach 90% accuracy *before* the probe for the core feature (bird species). The emergence gap should be measurable in epochs.

What would disprove this? If core features emerge simultaneously with or before spurious features, the simplicity bias hypothesis fails for this setting.

**Testable Prediction 2 (Intervention Effectiveness):** If temporal ordering is indeed causal, then intervening at the "spurious-emergence epoch" (blocking gradient to spurious-feature neurons) should improve worst-group accuracy by ≥5 percentage points compared to standard ERM, without significant average accuracy loss.

However, I see confounds. The Waterbirds dataset has known characteristics—95% correlation between background and label. We need multiple datasets to rule out dataset-specific artifacts. I propose testing on Waterbirds, CelebA (hair color vs gender), and ColoredMNIST to establish generality.

The gradient attribution dynamics idea (point 2) concerns me. How do we *identify* which neurons encode spurious vs. core features without already knowing the features? This feels circular. The probe approach avoids this because probes are trained with explicit supervision.

**Key Points:**
- Define precise emergence time metric: epoch where probe accuracy crosses threshold (e.g., 80%)
- Require ≥3 datasets (Waterbirds, CelebA, ColoredMNIST) to rule out artifacts
- Intervention hypothesis: blocking gradient at emergence epoch should improve worst-group accuracy

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field? 🔬 Prof. Vera has sharpened the predictions, but let me assess whether this research direction genuinely advances our understanding or merely adds incremental measurement.

I see three potential contribution levels:

**Contribution Level 1 (Confirmatory):** Simply demonstrating that spurious features are learned before core features is confirmatory at best. Shah et al. (2020) and Nam et al. (2020) already strongly imply this. A direct measurement would be *nice* but not transformative.

**Contribution Level 2 (Mechanistic):** If we can show *why* the ordering occurs—connecting it to loss landscape geometry, gradient flow patterns, or feature complexity metrics—this opens new research directions. The Catapults paper (Zhu et al.) hints that loss spikes mark transitions. If we link emergence times to catapult events, we'd have a mechanistic explanation, not just observation.

**Contribution Level 3 (Interventional):** This matters because Prof. Vera's second prediction is where real impact lies. If we can demonstrate that *intervening* based on temporal dynamics improves robustness without annotations, we've created a new class of methods. JTT required training twice; we might achieve similar results in a single training run with dynamic intervention.

What makes this genuinely new vs. incremental? The novelty lies in:
1. **Direct measurement** (vs. inference from misclassification patterns)
2. **Architecture comparison** (ResNet vs. ViT dynamics—unexplored territory)
3. **Principled intervention** (using emergence timing to guide training, not just detect bias)

This matters because the field has moved from "groups exist" (Sagawa 2019) to "early training reveals groups" (JTT 2021), and the next step should be "temporal dynamics *explain* and *enable control of* group reliance."

**Key Points:**
- Simple confirmation of temporal ordering is incremental; mechanistic explanation is valuable
- Intervention-based method (single-run, no annotations) would be high-impact
- Must differentiate from JTT's two-stage approach—single-run dynamic intervention is the goal

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. 🎯 Dr. Sage envisions a "single-run dynamic intervention" that improves worst-group robustness without annotations. But what evidence supports that this can work in principle?

I see three feasibility concerns—all technical/theoretical, not budgetary:

**Concern 1: Feature Identification Without Ground Truth.** The linear probe approach (🔭 Dr. Nova) requires training probes for *specific* features. In Waterbirds, we know the spurious feature is "background." But the goal is annotation-free methods. If we need to know which feature is spurious to train a probe for it, we've re-introduced the annotation requirement through the back door.

However—here's what could work: train probes for *all salient visual features* (via unsupervised clustering or pretrained feature extractors). The feature that emerges fastest and correlates with labels is likely spurious. This turns the problem into unsupervised feature discovery, which is scientifically sound.

**Concern 2: Intervention Timing Precision.** 🔬 Prof. Vera proposes intervening at the "spurious-emergence epoch." But emergence isn't a discrete event—it's gradual. The measurement methods (probes at checkpoints) give coarse resolution. Is epoch-level granularity sufficient for effective intervention?

The Gradient Starvation paper (Pezeshki et al.) suggests feature learning occurs over extended periods. We may need batch-level or gradient-step-level tracking, which is theoretically feasible via gradient monitoring, though computationally intensive.

**Concern 3: Causal Identification.** Can we actually attribute gradient to spurious-feature neurons and block it selectively? Neurons aren't cleanly specialized; they're distributed representations. The intervention would need to target *directions in activation space*, not individual neurons.

This IS scientifically possible: compute the gradient projected onto the "spurious feature direction" (identified via probe weights) and subtract it. This is essentially adversarial direction regularization. The mechanism is sound.

**Key Points:**
- Annotation-free probe approach feasible via unsupervised feature clustering
- Epoch-level intervention granularity may be too coarse; batch-level monitoring more precise
- Gradient-space intervention (not neuron-level) is the correct formulation

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this by synthesizing the valid points from all perspectives! ⚙️ Prof. Pax raised real concerns, but each has a solution. Let me build our emerging hypothesis:

**Strengthening Point 1: Feature Identification.** Prof. Pax correctly notes that knowing which probe to train re-introduces annotations. But here's the defense: we don't need to identify *which* feature is spurious—only *which emerges first*. 

The refined approach: train multiple linear probes on diverse visual concepts (via pretrained feature extractors like CLIP). The concept whose probe accuracy rises fastest while correlating with labels is the likely spurious feature. No annotations needed—just temporal ordering measurement.

**Strengthening Point 2: Intervention Granularity.** Valid concern about epoch-level coarseness. But the hypothesis doesn't require precise timing for *intervention*—it requires precise timing for *detection*. The intervention can be continuous: as features emerge, apply increasing gradient regularization in their direction. Early emergence + label correlation = apply penalty. This is differentiable and doesn't need discrete thresholds.

**Strengthening Point 3: Distributed Representations.** Prof. Pax is correct that neurons aren't cleanly specialized. But the probe weights *define* a direction in activation space for each feature. The intervention becomes:

```
gradient_penalty = λ * (gradient · probe_direction)² for early-emerging features
```

This is essentially spectral regularization in feature space—well-established technique, now applied dynamically based on emergence timing.

**Emerging Hypothesis Structure:**
- **Core Claim:** The temporal order in which features emerge during SGD training predicts their spurious vs. core nature, and dynamically penalizing early-emerging label-correlated features improves worst-group robustness.
- **Mechanism:** Early-emerging features capture simple spurious correlations (simplicity bias). Penalizing gradient flow in these directions forces the network to learn core features.
- **Key Prediction:** Continuous dynamic regularization based on probe emergence timing will match or exceed JTT's worst-group accuracy without requiring two-stage training.

**Key Points:**
- Feature identification via unsupervised probing + temporal ordering (no annotation needed)
- Continuous gradient regularization, not discrete epoch intervention
- Spectral regularization in probe-defined feature directions is the mechanism

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down, 🛡️ Dr. Ally. Your synthesis is elegant, but I need to stress-test the unstated assumptions.

**Assumption 1: Early emergence implies spuriousness.** Is this always true? Consider ColoredMNIST where digit shape is the core feature. Shape is arguably "simple" too—it's low-frequency, learned quickly. The assumption that "early = spurious" may hold for Waterbirds (background texture is simpler than bird morphology) but fails when core features are also simple.

What would convince me: Show the emergence gap (spurious vs. core) varies with task complexity. In datasets where core features are complex, the gap should be large. Where core features are simple, the gap shrinks.

**Assumption 2: Probe accuracy reliably tracks feature learning.** Linear probes measure linear separability of representations. But what if the network learns features nonlinearly at first, then linearizes them? The probe trajectory might not reflect actual internal feature formation.

Show me: correlation between probe emergence times and other measures (gradient attribution, activation pattern analysis) to validate that probes aren't missing nonlinear learning phases.

**Assumption 3: The regularization won't hurt core feature learning.** If we penalize early-emerging features, won't we also slow down learning of *useful* simple features? In CelebA, "blonde hair" is spurious for male/female classification, but "hair presence" might be a useful precursor feature.

The mitigation I'd accept: show the regularization strength can be calibrated such that worst-group accuracy improves while average accuracy doesn't drop more than 1-2 percentage points.

**Hard Question:** Your mechanism assumes we can identify feature directions via unsupervised clustering. But CLIP features are pretrained on web data—they might encode the very spurious correlations we're trying to avoid. How do we ensure the probe targets the right features?

**Key Points:**
- Early emergence doesn't always mean spurious—depends on relative complexity
- Validate probes with alternative measures (gradient attribution, activation analysis)
- Show regularization can be calibrated to preserve average accuracy
- Address pretrained feature extractor bias (CLIP may encode spurious correlations)

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're getting somewhere! 🔍 Prof. Rex's stress tests reveal where we need creative solutions. Let me address each with paradigm-shifting ideas:

**On "early = spurious" assumption:** What if we don't assume early emergence means spurious? Instead, we look at *differential emergence between subgroups*. Here's the insight: in Waterbirds, the background feature emerges at the same rate for all groups (land/water birds), but the core feature (bird species) emerges *faster* for majority groups. The *rate divergence* across groups is the signal, not absolute timing!

This reframes the problem: we're not penalizing "early" features, we're penalizing features that show *uniform* emergence across what the model treats as groups.

**On probe reliability:** What if probes aren't the only measurement? Imagine combining three signals:
1. Linear probe accuracy trajectories
2. Gradient norm trajectories (which features receive gradient at each epoch)
3. Representation similarity dynamics (CKA between layers across epochs)

Multi-modal measurement! If all three agree on emergence ordering, we have robust evidence. If they disagree, that's scientifically interesting—different learning phases captured by different methods.

**On CLIP bias:** Here's a wild idea—what if CLIP's biases are *useful*? CLIP was trained on web data with spurious correlations. If a CLIP-derived probe identifies a feature as "emerging early," it's likely because CLIP already knows that feature is spuriously correlated with labels in web data. We're using CLIP's biases to *detect* our dataset's biases!

**Refined Hypothesis:** Under conditions where spurious features are simpler than core features (measurable via representation complexity metrics), if we apply dynamic gradient regularization to features showing uniform emergence across training samples, then worst-group accuracy improves because the network is forced to learn discriminative features that differentiate subgroups.

**Key Points:**
- Differential emergence rate across subgroups, not absolute timing, may be the true signal
- Multi-modal measurement (probes + gradient norms + CKA) for robust evidence
- CLIP's biases can be exploited to detect dataset biases—feature, not bug!

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova's refinement addresses my core concerns. Let me formalize the testable predictions with this updated framing:

**Final Hypothesis (Under-If-Then-Because Format):**
Under conditions where spurious features are learned uniformly across training samples while core features show differential learning rates across implicit groups, if we apply dynamic gradient regularization scaled by feature emergence uniformity, then worst-group accuracy improves by ≥5 percentage points over ERM, because the regularization forces the network to rely on discriminative features rather than group-invariant spurious correlations.

**Testable Predictions (Falsifiable):**

**P1 (Emergence Uniformity Detection):** Features whose probe accuracy trajectories show low variance across random sample subsets are more likely to be spurious. Measure: coefficient of variation of probe accuracy improvement rates across 5 random 20% subsets. Spurious features should have CV < 0.1; core features CV > 0.2.

**P2 (Intervention Effectiveness):** Applying gradient penalty λ*(grad·probe_direction)² to features with low CV (< 0.15) improves worst-group accuracy on Waterbirds by ≥5 pp over ERM baseline, without reducing average accuracy by more than 2 pp.

**P3 (Cross-Dataset Generalization):** The same λ calibration that works on Waterbirds also improves worst-group accuracy on CelebA and ColoredMNIST (≥3 pp improvement), demonstrating method generality.

**Falsification Criteria:**
- If CV fails to distinguish spurious from core features (no threshold separates them), the uniformity hypothesis fails
- If intervention improves worst-group accuracy but average accuracy drops >5 pp, the mechanism is too aggressive
- If method fails on CelebA/ColoredMNIST, findings are dataset-specific artifacts

This meets my standards. The predictions are precise, measurable, and falsifiable.

**Key Points:**
- CV of probe trajectory across subsets as emergence uniformity metric
- Threshold-based feature classification: CV < 0.15 = likely spurious
- ≥5 pp worst-group improvement with <2 pp average accuracy drop = success

---

### Exchange 9

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Now THAT's stronger! 🔬 Prof. Vera has given us precise success criteria. Let me synthesize the complete hypothesis ready for Phase 2B:

**CONSENSUS HYPOTHESIS:**

**Title:** Emergence Uniformity Regularization (EUR) for Annotation-Free Worst-Group Robustness

**Core Claim (Under-If-Then-Because):**
Under the Waterbirds/CelebA/ColoredMNIST benchmarks where spurious correlations cause poor worst-group performance, if we identify features by their emergence uniformity (low variance in probe learning rates across sample subsets) and apply gradient regularization proportional to uniformity, then worst-group accuracy improves by ≥5 percentage points over ERM, because uniform emergence indicates the feature is spuriously correlated with labels rather than discriminative.

**Mechanism (3-step causal chain):**
1. **Detection:** Train linear probes on pretrained features (e.g., CLIP visual encoder) at regular intervals. Compute coefficient of variation (CV) of accuracy improvement rates across random sample subsets.
2. **Classification:** Features with CV < 0.15 are classified as potentially spurious (learned uniformly); CV > 0.2 as likely core (learned differentially).
3. **Intervention:** Apply gradient regularization λ*(grad·probe_direction)² to low-CV features, forcing the network to rely on high-CV discriminative features.

**Key Predictions:**
- P1: CV reliably separates spurious from core features (AUC > 0.8 for classification)
- P2: EUR achieves ≥5 pp worst-group improvement on Waterbirds with <2 pp average drop
- P3: Method generalizes to CelebA and ColoredMNIST (≥3 pp improvement each)

**Novelty:**
- First method to use *emergence uniformity* (not absolute timing) as spuriousness signal
- Single-run training (unlike JTT's two-stage approach)
- Uses pretrained feature extractors without requiring annotation of spurious features

**Null Hypothesis (H0):**
There is no significant difference in worst-group accuracy between EUR and standard ERM training on spurious correlation benchmarks.

**Key Points:**
- Emergence Uniformity Regularization (EUR) is the proposed method name
- CV threshold 0.15 for spuriousness classification
- Three-dataset evaluation required for generalization claim

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The EUR approach introduces two genuinely novel concepts: (1) emergence uniformity as spuriousness signal, and (2) single-run dynamic regularization. This reframes the temporal dynamics question from "what emerges first" to "what emerges uniformly," which is a paradigm shift from JTT and LfF.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three falsifiable predictions defined with precise metrics (CV thresholds, percentage point improvements, cross-dataset generalization). The hypothesis structure follows Under-If-Then-Because format. Falsification criteria are clear: if CV cannot separate features or method fails on 2+ datasets, hypothesis is rejected.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This advances the field from "early training reveals groups" to "temporal dynamics enable single-run intervention." The practical impact is clear: no two-stage training, no group annotations. If successful, EUR could replace JTT as the standard annotation-free robustness method.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are technically sound: linear probes are standard, CV computation is trivial, gradient regularization is well-established. Using CLIP features is practical. No fundamental barriers identified. Implementation requires only standard PyTorch operations.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on **Emergence Uniformity Regularization (EUR)**, a method that exploits the observation that spurious features are learned uniformly across training samples while core features show differential learning rates across implicit groups.

The core insight emerged from synthesizing simplicity bias (Shah et al.) with gradient starvation (Pezeshki et al.): spurious features are simple and learned uniformly, while core features are complex and learned at different rates for different subgroups. By measuring the coefficient of variation (CV) of probe accuracy trajectories across random sample subsets, we can identify spurious features without any group annotations.

The intervention is continuous gradient regularization: features with low CV (< 0.15) receive gradient penalties proportional to their projection onto the probe direction. This forces the network to rely on high-CV discriminative features.

The hypothesis predicts ≥5 percentage point worst-group improvement on Waterbirds with <2 pp average accuracy drop, and ≥3 pp improvement on CelebA and ColoredMNIST for generalization.

This is testable immediately on existing benchmarks (Waterbirds, CelebA, ColoredMNIST) using existing metrics (worst-group accuracy). No new datasets, rubrics, or human evaluation required.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** CV threshold (0.15) was proposed but not validated. Initial experiments should include threshold sensitivity analysis.
- **Concern 2:** CLIP feature extractor may encode spurious correlations from web pretraining. Alternative extractors (ImageNet-pretrained, DINOv2) should be tested.
- **Concern 3:** Regularization strength λ calibration may be dataset-specific. Cross-validation strategy needed.
- **Mitigation Strategy:** Ablation studies on (1) CV threshold range [0.1, 0.2], (2) multiple pretrained extractors, (3) λ values [0.01, 0.1, 1.0] across all three datasets.

---

## Emerged Hypothesis Summary

### Core Statement
Under conditions where spurious features show uniform emergence across training samples (CV < 0.15) while core features show differential emergence (CV > 0.2), if we apply gradient regularization λ*(grad·probe_direction)² to low-CV features, then worst-group accuracy improves by ≥5 pp over ERM, because the regularization forces the network to rely on discriminative features rather than spurious correlations.

### Causal Mechanism
1. **Detection Phase:** Train linear probes on CLIP features at epoch checkpoints. Compute CV of accuracy improvement rates across 5 random 20% subsets.
2. **Classification Phase:** Features with CV < 0.15 classified as likely spurious; CV > 0.2 as likely core.
3. **Intervention Phase:** Apply continuous gradient penalty to low-CV feature directions during training.

### Variables
- **Independent Variable:** Gradient regularization strength λ (levels: 0, 0.01, 0.1, 1.0)
- **Dependent Variable (Primary):** Worst-group accuracy (%)
- **Dependent Variable (Secondary):** Average accuracy (%)
- **Controlled:** Dataset (Waterbirds, CelebA, ColoredMNIST), Architecture (ResNet-50), Optimizer (SGD), Feature extractor (CLIP ViT-B/16)

### Key Assumptions
- A1: Spurious features emerge uniformly across samples; core features emerge differentially
- A2: Linear probes on pretrained features capture relevant feature emergence patterns
- A3: CV threshold can distinguish spurious from core features with reasonable accuracy
- A4: Gradient regularization in probe directions effectively suppresses feature learning
- A5: CLIP features encode the relevant visual concepts for Waterbirds/CelebA/ColoredMNIST

### Null Hypothesis
There is no significant difference in worst-group accuracy between EUR (Emergence Uniformity Regularization) and standard ERM training on spurious correlation benchmarks.

### Predictions
- **P1 (Primary):** EUR achieves ≥5 pp worst-group accuracy improvement over ERM on Waterbirds
- **P2:** EUR achieves ≥3 pp worst-group improvement on CelebA
- **P3:** EUR achieves ≥3 pp worst-group improvement on ColoredMNIST
- **P4:** Average accuracy drop ≤2 pp across all datasets

### Novelty
- First method using emergence uniformity (not timing) as spuriousness signal
- Single-run training unlike JTT's two-stage approach
- No annotation of spurious features required

### Scope & Boundaries
- **Applies to:** Image classification with spurious correlations where spurious features are simpler than core features
- **Does not apply to:** Tasks where core and spurious features have similar complexity
- **Known limitations:** Requires pretrained feature extractor; CV threshold may need tuning per domain

### Experimental Setup
- **Dataset:** Waterbirds (primary), CelebA, ColoredMNIST
- **Model:** ResNet-50 (ImageNet-pretrained)
- **Feature Extractor:** CLIP ViT-B/16 (for probes)
- **Baselines:** ERM, JTT, Group DRO (oracle)

### Related Work & Baselines
- **ERM:** Standard empirical risk minimization (baseline)
- **JTT (Liu et al., 2021):** Two-stage training using early misclassifications; EUR aims to match with single-run
- **Group DRO (Sagawa et al., 2019):** Oracle method requiring group annotations; upper bound comparison

### Phase 2B Readiness Seeds
- Implementation uses standard PyTorch operations
- CLIP model available via transformers library
- Waterbirds/CelebA/ColoredMNIST have established data loaders
- Probe training is standard linear classification
- CV computation requires only numpy operations

### Established Facts
- Simplicity bias causes SGD to learn simple features first (Shah et al., 2020) - BUILD_ON
- Early misclassifications correlate with minority groups (Liu et al., 2021) - BUILD_ON
- Gradient starvation affects feature learning dynamics (Pezeshki et al., 2020) - BUILD_ON
- Emergence uniformity as spuriousness signal - PROVE_NEW
- CV threshold for feature classification - PROVE_NEW
- Single-run dynamic regularization effectiveness - PROVE_NEW

