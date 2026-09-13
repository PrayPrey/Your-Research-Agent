# Phase 2A: Research Discussion Log

## Metadata
- **Gap ID**: GAP-1
- **Gap Title**: Discriminative Weight Features for Binary Depth Classification
- **Start Time**: 2026-04-21T05:07:51.979235
- **Architecture**: Self-Contained Tikitaka Loop v9.0.0
- **Execution Mode**: UNATTENDED

## Discussion Briefing

### Research Gap
**Title:** Discriminative Weight Features for Binary Depth Classification

**Context:** This is a ROUTE_TO_0 Recovery (Run 4) after previous failure:
- Run 3 attempted continuous correlation (|ρ| = 0.859 < 0.90 threshold)
- Pivoted to binary classification for larger effect size
- Sample size increased from n=5 to n=20 for adequate statistical power

**Current State:** Existing literature focuses on weight-based model compression, pruning efficiency, and transfer learning quality - not on using weight statistics to classify architectural properties like depth. The correlation between weight norms and depth was observed in Run 3 (|ρ| = 0.859), but translating this into binary classification features is unexplored.

**Missing Piece:** Which aggregated weight statistics (layer-wise norm distributions, spectral features, tensor moments) are most discriminative for separating shallow (depth ≤ 34) vs deep (depth ≥ 50) CNNs? Prior work analyzes weights for compression and transfer learning, not for architecture property classification.

### Phase 1 Key Findings
(Refer to `01_targeted_research.md` for detailed findings)

Key lessons from Run 3 failure:
1. Binary classification has larger effect size than correlation
2. Adequate sample size (n=20) vs Run 3's underpowered n=5
3. Exploratory threshold (accuracy > 70%) vs Run 3's rigid (ρ ≥ 0.90)
4. Controlled architecture families to minimize confounding

### Available Papers
(No papers prepared - test environment without MCP servers)

### Research Repos
(None)

### Feasibility Constraints (MANDATORY)
**Pipeline-Enforced Rules:**
- ✅ Use existing real datasets only (no synthetic data)
- ✅ Use existing benchmarks only (no new rubrics)
- ✅ No human evaluation or annotation required
- ✅ Testable immediately with pretrained models

**EXISTENCE-Tier Constraints:**
- Maximum 2 epics, 6 tasks
- 0 model training (pretrained only)
- sklearn classifiers only (no custom algorithms)
- 2 GPU hours maximum

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the entire weight analysis paradigm on its head? Instead of treating weight statistics as mere architectural fingerprints, let's see them as a **compressed representation of learned computational capacity**. The brilliant pivot from Run 3's correlation approach to binary classification isn't just about statistical power—it's about recognizing that shallow vs. deep networks inhabit fundamentally different regions of weight space geometry.

Here's my wild idea: Layer-wise Frobenius norms aren't just numbers—they're **signatures of hierarchical feature abstraction**. Deep networks (≥50 layers) develop highly specialized weight distributions in their middle layers that shallow networks (≤34 layers) simply cannot achieve. Think of it like this: a 5-story building and a 50-story skyscraper don't just differ in height—their structural engineering, load distribution, and material stress patterns are categorically different. The same principle applies to neural network weights!

The creative angle we should explore: **spectral fingerprinting**. Beyond simple norms, what if we compute the singular value decomposition (SVD) spectra of weight matrices at critical layers? Deep networks should exhibit distinct spectral decay patterns—their weight matrices likely have more concentrated singular values (indicating specialized features) compared to shallow networks' more uniform distributions. This could be our discriminative feature that Run 3's simple norms couldn't capture.

Let me propose three unconventional approaches to investigate:

1. **Weight Trajectory Curvature**: Instead of static statistics, compute how weight norm distributions *change* across layer depth. Deep networks might show non-linear progression patterns (early plateau, mid-layer explosion, late compression) while shallow networks follow simpler monotonic patterns.

2. **Cross-Layer Correlation Structure**: Analyze correlation matrices between consecutive layer weights. Deep networks with residual connections should show unique correlation signatures that shallow networks lack.

3. **Distribution Moment Fingerprints**: Go beyond mean/std to capture skewness and kurtosis of weight distributions at different depth ranges. My intuition says deep networks develop heavy-tailed distributions in middle layers (specialized features) while shallow networks remain more Gaussian.

**Key Points:**
- Binary classification amplifies the signal by comparing extreme cases—brilliant recovery from Run 3
- Weight statistics encode *computational capacity*, not just architectural metadata
- Spectral features (SVD-based) may provide stronger discriminative power than simple norms
- Success criterion (accuracy > 70%) is appropriately exploratory for EXISTENCE-tier validation

NOW we're onto something! This isn't just about counting layers—it's about discovering the geometric signature of depth in weight space!

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Hold on, 🔭 Dr. Nova. Your enthusiasm for spectral fingerprinting is infectious, but we need to ground this in testable predictions *before* we get lost in geometric poetry. Let me stress-test your ideas against the EXISTENCE-tier constraints.

Your SVD spectral decay proposal—brilliant in theory, but let's be precise: **What exactly would falsify this?** If we compute singular values for, say, the 10th convolutional layer in ResNet-18 (shallow) vs. ResNet-50 (deep), you're claiming the deep network shows more concentrated spectra. That's testable. But we need success criteria: "Concentrated" means what, quantitatively? Top-5 singular value ratio > X? Spectral entropy < Y?

Here's what worries me about Run 3's ghost: correlation |ρ| = 0.859 is actually quite strong, but it failed the p < 0.05 test due to n=5. Now we're proposing *more complex features* (SVD, cross-layer correlations) with the same small model count per architecture family. **What if feature complexity dilutes our statistical power again?**

My testable predictions framework for binary classification (shallow ≤ 34 vs. deep ≥ 50):

**Prediction 1 (Simple Features First):**
If we extract mean + std of layer-wise Frobenius norms (2 features per model), logistic regression trained on 16 models will achieve test accuracy > 70% on 4 held-out models. Success criterion: Accuracy ≥ 70%. Falsification: Accuracy ≤ 60% indicates weight norms alone are insufficient.

**Prediction 2 (Spectral Enhancement - Conditional):**
If Prediction 1 succeeds (≥70%), adding spectral features (top-3 singular value ratios from 3 representative layers = 9 features) improves accuracy by ≥5 percentage points. Falsification: No improvement suggests spectral information is redundant with norms.

**Prediction 3 (Confound Control):**
Classification accuracy on same-width comparisons (ResNet-18 vs. ResNet-34, both width=64 base; ResNet-50 vs. ResNet-101, both width=256 base) remains ≥65%. Falsification: Accuracy drops below 60%, indicating width confounding.

**Key Points:**
- Start with simplest features (mean/std of norms) to establish baseline—don't over-engineer on attempt #1
- Hierarchical testing: simple features → spectral features → cross-layer features (if time permits)
- Each feature set needs explicit success/failure thresholds
- Null result acceptance: If even simple norms fail (<60% accuracy), depth is not weight-fingerprinted

What would disprove each of 🔭 Dr. Nova's three proposals? That's the question we must answer before coding.

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Both of you raise vital points, but let's zoom out: **Why does this matter to the field?** The workshop theme is "Neural Network Weights as a New Data Modality"—our contribution needs to demonstrate that weight statistics can answer questions that metadata or functional evaluation cannot.

Building on 🔬 Prof. Vera's hierarchy of testable predictions, I want to position this work's significance. If we succeed at EXISTENCE-tier (accuracy > 70% on shallow vs. deep classification), here's the research impact:

**Immediate Contribution:**
This would be the *first demonstration* that architectural depth—a fundamental network property—can be inferred from weight statistics alone without forward passes, activation analysis, or metadata parsing. That's genuinely new. Prior work uses weights for compression (magnitude pruning) or transfer learning (weight similarity), but not for architectural property inference.

**Broader Implications:**
1. **Model Zoo Navigation**: Hugging Face hosts 1M+ models with inconsistent metadata. Weight-based classification enables reliable architecture categorization without running inference on each model.

2. **Model Verification**: Detect mislabeled models (claimed deep but weight stats suggest shallow) for trustworthy model selection.

3. **Research Questions Unlocked**: If depth is weight-fingerprinted, what other properties are? Width? Training dataset size? Optimization algorithm? This opens a new research direction.

**Positioning vs. Prior Work:**
The key differentiation from Run 3 is our methodological shift. Run 3 asked "How strongly do norms correlate with depth?" (correlation analysis). We're asking "Can norms *classify* depth categories?" (decision boundary discovery). This is more aligned with practical use cases—users want to know "Is this model shallow or deep?" not "What's the Pearson correlation coefficient?"

However, 🔬 Prof. Vera's concern about feature complexity is well-founded. If we need 50+ features to hit 70% accuracy, the signal is weak—diminishing significance. **The cleaner the classification boundary, the stronger the contribution.**

**Key Points:**
- Success at 70% with simple features (mean/std norms) = strong contribution
- Success at 70% requiring complex features (SVD + cross-layer + moments) = weaker contribution
- Failure (<60%) = valuable null result: "Depth is not strongly encoded in weight statistics"
- True impact comes from *simplicity* of the discovered relationship

What makes this genuinely new versus incremental improvement over Run 3?

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's get real about what we can actually achieve within the constraints. I'm not worried about GPU costs—those are implementation details. What concerns me is whether the proposed measurement methods are *scientifically sound* given the confounding variables we can't control.

🔬 Prof. Vera flagged the width confound: ResNet-18 (64 base width) vs. ResNet-50 (256 base width) differs in *both* depth AND width. That's a fundamental measurement validity issue. Even if we achieve 80% accuracy, we won't know if we're classifying depth or width. Here's the harsh truth: **we cannot train controlled experiments** (0 training constraint), so we're stuck with pretrained models that vary on multiple dimensions simultaneously.

The theoretical feasibility question: **Can depth be isolated from width in weight statistics?** Let me think through the mechanism:

- Layer-wise Frobenius norm = sqrt(sum of squared weights) = sensitive to both layer count (depth) and parameter count per layer (width)
- A wide shallow network (e.g., VGG-16 with 4096-dim FC layers) might have larger total norms than a narrow deep network (e.g., MobileNet-v2 with depth-wise separable convolutions)
- This means raw norms confound depth with width

**Measurement validity check:**
For 🔭 Dr. Nova's spectral features to work, we need depth-specific mechanisms that aren't explained by width:
1. Residual connections in deep networks → weight matrices should show specific correlation patterns → Testable via SVD? YES, theoretically sound.
2. Gradient flow in deep networks → weight initialization patterns should differ from shallow → Testable via distribution moments? YES, if we examine layer-specific initialization artifacts.

**What could fundamentally break this approach?**
If pretrained model weights are re-initialized or heavily fine-tuned post-pretraining, architectural signatures might be erased. We're assuming pretrained models retain training process fingerprints. That's an unstated assumption.

**Feasibility verdict:**
🔬 Prof. Vera's Prediction 1 (simple norms, 70% accuracy) is *scientifically achievable* if depth signal exists. The measurement method is valid. However, interpretation requires caution—we're measuring "depth OR correlated properties" not "depth isolated." That's acceptable for EXISTENCE tier.

**Key Points:**
- Width confounding is a fundamental measurement issue, not a budget issue
- Spectral features are theoretically valid for detecting residual connection patterns
- Success requires pretrained models to retain architectural signatures (assumption)
- 70% accuracy threshold is appropriate—doesn't require perfect isolation of depth

Can the proposed measurements actually work in principle? Yes. But claim scope must be honest about confounds.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this hypothesis by directly addressing the confound concerns! Building on ⚙️ Prof. Pax's realism and 🔬 Prof. Vera's testing hierarchy, let me synthesize a robust hypothesis that acknowledges confounds while maintaining scientific validity.

**Core Hypothesis (strengthened):**
Under the scope of pretrained CNN architectures from standard model families (ResNet, VGG, DenseNet), if we extract layer-wise weight norm statistics (mean, std) and train a logistic regression classifier on 16 models (8 shallow: depth ≤ 34, 8 deep: depth ≥ 50), then test accuracy on 4 held-out models will exceed 70%, because deeper networks develop distinctive weight distribution patterns due to accumulated gradient transformations and architectural constraints (residual connections, normalization layers).

**Mechanism refinement (addressing ⚙️ Prof. Pax's concern):**
We're not claiming to isolate depth from all confounds. We're claiming that **depth-correlated patterns** (which may include width, training epochs, architecture family) are sufficiently distinctive for binary classification. This is *appropriate for EXISTENCE tier*—we're establishing that the phenomenon exists, not explaining its pure causal mechanism.

**Confound mitigation strategy:**
While we cannot train controlled models, we can use architecture family sampling:
- Shallow group: ResNet-18, ResNet-34, VGG-11, VGG-13, VGG-16 (varies width within shallow)
- Deep group: ResNet-50, ResNet-101, ResNet-152, DenseNet-121, DenseNet-169 (varies width within deep)

If classification succeeds *despite* intra-group width variation, the depth signal is real.

**Experimental predictions (integrating 🔬 Prof. Vera's framework):**

**P1 (Primary):** Binary classification with simple features (mean/std of layer norms) achieves test accuracy > 70%. This validates that weight statistics encode depth-correlated information.

**P2 (Robustness):** Accuracy on cross-architecture validation (train on ResNet+VGG, test on DenseNet) > 65%. This shows the pattern generalizes beyond single architecture families.

**P3 (Null Hypothesis):** If accuracy ≤ 60%, we accept that depth is not strongly fingerprinted in weight statistics, and the field should explore alternative approaches (e.g., activation statistics, which require forward passes).

**Key Points:**
- Acknowledge confounds explicitly—we're classifying "depth-correlated patterns" not "pure depth"
- Multi-family sampling provides robustness evidence
- Clear success (>70%), partial success (60-70%), and failure (<60%) thresholds
- This builds on Run 3's correlation finding (|ρ| = 0.859) by making it actionable

NOW we have a defensible hypothesis that's both ambitious (70% threshold) and honest (confound acknowledgment)!

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down: **you're all assuming pretrained models have stable, architecture-specific weight signatures**. What if they don't? Let me play devil's advocate and find the critical weaknesses before reviewers do.

**Critical Flaw #1: Training Recipe Dominance**
What if weight statistics are dominated by training hyperparameters (learning rate, optimizer, batch size) rather than architecture? Example:
- ResNet-18 trained with SGD (lr=0.1, momentum=0.9) for 90 epochs
- ResNet-50 trained with Adam (lr=0.001) for 120 epochs

Your classifier might learn "SGD vs. Adam" instead of "shallow vs. deep." How do you rule this out with 0 training constraint?

**Critical Flaw #2: Dataset Fingerprinting**
Pretrained models are trained on different datasets with different preprocessing:
- ResNet variants: ImageNet (1000 classes, mean=[0.485, 0.456, 0.406] normalization)
- VGG variants: ImageNet (1000 classes, different normalization)
- DenseNet variants: ImageNet (1000 classes, but different augmentation)

What if your classifier learns dataset preprocessing artifacts rather than depth? Your 70% accuracy could be spurious.

**Critical Flaw #3: Confound Correlation ≠ Mechanism Validation**
🛡️ Dr. Ally's "depth-correlated patterns" admission is honest but scientifically weak. If we can't isolate depth from width/training/dataset, we're just building a **multi-factor fingerprinting classifier** that happens to align with depth labels. That's fine for model zoo navigation (practical use case) but weak for understanding weight space geometry (scientific contribution).

**What would convince me this is valid?**

1. **Ablation Study**: Show that classification fails when you randomly permute layer order (depth structure destroyed) but succeeds on original models. This proves depth *structure* matters, not just total parameter count.

2. **Negative Control**: Train the classifier on random labels (shuffle depth categories) and show it fails to achieve >60% accuracy. This proves the classifier isn't just overfitting to 20 models.

3. **Feature Attribution**: Use logistic regression coefficients to identify which layer ranges contribute most to classification. If mid-to-deep layers dominate (layers 20-40), that supports depth mechanism. If early layers dominate, it suggests initialization artifacts.

**Remaining concerns after mitigation:**
- 20 models is adequate for *detection* (is there signal?) but not for *generalization* (will it work on unseen architectures like EfficientNet, ConvNeXt?)
- 2 epics / 6 tasks is tight—if P1 fails, there's no time to iterate on P2 spectral features
- Null results are valuable BUT you must commit: if accuracy ≤ 60%, will you publish this as "Depth is not weight-fingerprinted" or route to Phase 0?

**Key Points:**
- Training recipe and dataset confounds could dominate depth signal
- "Depth-correlated patterns" is too vague for strong scientific claims
- Need ablation studies to validate mechanism, not just classification success
- Commit to null result action plan now—pivot or publish?

What evidence would actually convince skeptical reviewers that depth (not confounds) drives the classification?

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent challenges, 🔍 Prof. Rex! Let me refine the hypothesis to address your critical flaws while keeping it feasible within EXISTENCE-tier constraints.

**Refined Hypothesis (Final):**

**Core Claim:** Pretrained CNN architectures exhibit weight distribution signatures that correlate with architectural depth, enabling binary classification (shallow ≤ 34 layers vs. deep ≥ 50 layers) with accuracy > 70% using simple aggregated statistics (mean/std of layer-wise Frobenius norms).

**Scope & Boundaries:**
- **Applies to:** Pretrained CNNs from standard ImageNet training recipes (ResNet, VGG, DenseNet families)
- **Does not apply to:** Randomly initialized models, models trained on non-ImageNet datasets, architectures with fundamentally different paradigms (Transformers, RNNs)
- **Known limitations:** Classification success may be influenced by correlated factors (width, training recipe, architecture family). We are testing for *depth-correlated patterns*, not isolating pure depth causality.

**Causal Mechanism (Hypothesized):**
Deep networks (≥50 layers) develop distinct weight norm distributions due to:
1. **Gradient accumulation**: Deeper networks experience more gradient transformation steps, leading to characteristic weight magnitude patterns
2. **Architectural constraints**: Residual connections (ResNet), dense connections (DenseNet), or bottleneck layers create depth-specific weight structures
3. **Normalization effects**: Batch normalization statistics accumulate differently across 50+ layers vs. <34 layers

**Testable Predictions:**

**P1 (Primary - EXISTENCE validation):** Binary logistic regression trained on aggregated weight statistics (mean, std of layer-wise Frobenius norms) from 16 pretrained models achieves ≥70% accuracy on 4 held-out models. This establishes that depth-correlated information exists in weight statistics.

**P2 (Robustness check):** Classification accuracy on within-family subsets (ResNet-only, VGG-only) remains ≥65%. If accuracy drops <60%, depth signal is confounded with architecture family rather than depth itself.

**P3 (Null hypothesis):** Random label shuffle (assign shallow/deep labels randomly to same 20 models) produces accuracy ≤55% (near chance). This validates that the classifier learns signal, not overfits to model-specific artifacts.

**Experimental Design:**
- **Dataset**: 20 pretrained CNNs from PyTorch torchvision (no downloads required)
  - Shallow (n=10): ResNet-18/34, VGG-11/13/16/19, AlexNet, SqueezeNet, MobileNet-v2, ShuffleNet
  - Deep (n=10): ResNet-50/101/152, Wide-ResNet-50/101, DenseNet-121/169/201, ResNeXt-50/101
- **Features**: For each model, extract Frobenius norm for each convolutional/linear layer → compute mean, std, min, max (4 features total)
- **Classifier**: sklearn LogisticRegression (L2 regularization, default hyperparameters)
- **Validation**: 80/20 train/test split (16 train, 4 test), stratified by depth category
- **Success criterion**: Test accuracy ≥ 70%

**Addressing 🔍 Prof. Rex's Concerns:**

1. **Training recipe dominance**: We use models from same source (PyTorch torchvision) with standardized ImageNet training. This minimizes (but doesn't eliminate) training recipe variance.

2. **Dataset fingerprinting**: All models trained on ImageNet 1K with similar preprocessing. If classification succeeds, it's on architecture differences, not dataset differences.

3. **Mechanism validation**: P2 (within-family accuracy ≥65%) and P3 (random label accuracy ≤55%) provide evidence against pure confound explanation. Not perfect isolation, but better than correlation alone.

**Null Result Plan (Committing Now):**
- If P1 accuracy ≤ 60%: Accept that simple weight norms are insufficient. Document as "Weight statistics alone do not strongly fingerprint CNN depth." Publish as negative result at workshop OR route to Phase 0 for alternative approach (activation statistics, functional evaluation).
- If P1 = 60-70%: Marginal result. Proceed to Phase 2B but flag as "weak signal" for careful design.
- If P1 ≥ 70%: Strong signal. Proceed to Phase 2B with confidence.

**Key Points:**
- Explicit scope boundaries and confound acknowledgment
- Three-tier validation (P1: existence, P2: robustness, P3: null control)
- Feasible within 2 epics, 6 tasks, 0 training, sklearn-only constraints
- Null result plan committed upfront—no ambiguity

**Consensus Hypothesis Summary:**
"Simple weight statistics (mean/std of layer norms) can classify pretrained CNNs as shallow vs. deep with >70% accuracy, demonstrating that architectural depth leaves measurable signatures in weight distributions despite confounding factors."

**Alternative Hypothesis (H0):**
"There is no significant difference in weight distribution statistics between shallow and deep pretrained CNNs sufficient for >70% binary classification accuracy."

This hypothesis is testable, falsifiable, scoped appropriately, and honest about limitations. Are we converged?

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The pivot from correlation to binary classification is methodologically creative, and the hypothesis introduces weight distribution signatures as a novel lens for architectural property inference. Moving beyond compression/transfer learning applications to architectural fingerprinting represents genuine innovation in the "weights as data modality" space.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three-tier prediction framework (P1: existence, P2: robustness, P3: null control) provides clear falsification criteria. Success threshold (70% accuracy) and failure threshold (≤60%) eliminate ambiguity. The experimental design is testable with explicit success/failure outcomes at each stage.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** Demonstrates practical utility (model zoo navigation, verification) and opens new research direction (weight-based property inference). However, confound acknowledgment ("depth-correlated patterns" rather than "pure depth") limits theoretical impact. Strong contribution if simple features succeed (70% with mean/std only); weaker if complex features required.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Hypothesis is technically and theoretically sound within stated scope. Measurement methods (Frobenius norms, logistic regression) are scientifically valid. Width confounding is acknowledged and mitigated through multi-family sampling. Pretrained model availability and sklearn-only constraint make this immediately executable. The 2 epic, 6 task, 0 training limit is realistic for EXISTENCE-tier validation.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Core Hypothesis:** Pretrained CNN architectures exhibit weight distribution signatures that enable binary classification (shallow ≤34 layers vs. deep ≥50 layers) with >70% accuracy using aggregated statistics (mean/std of layer-wise Frobenius norms), demonstrating that architectural depth leaves measurable fingerprints in weight space despite confounding factors.

**Causal Mechanism:** Deep networks develop distinctive weight norm patterns through (1) accumulated gradient transformations across 50+ layers, (2) architectural constraints from residual/dense connections, and (3) differential batch normalization effects. These mechanisms create depth-specific signatures that simple statistical features can capture.

**Key Predictions:**
- **P1 (Primary):** Binary logistic regression on weight norm statistics achieves ≥70% test accuracy on held-out models
- **P2 (Robustness):** Within-family validation (ResNet-only, VGG-only) maintains ≥65% accuracy
- **P3 (Null Control):** Random label shuffle produces ≤55% accuracy (validates signal over noise)

**Experimental Approach:** Extract layer-wise Frobenius norms from 20 pretrained PyTorch models (10 shallow, 10 deep), compute mean/std/min/max (4 features), train sklearn LogisticRegression on 16 models, test on 4 held-out models. Success = test accuracy ≥70%.

**Novelty:** First demonstration of weight-statistics-only architectural depth classification, extending weight analysis beyond compression/transfer learning to property inference.

**Scope & Limitations:** Applies to pretrained ImageNet CNNs (ResNet, VGG, DenseNet families). Classification success reflects "depth-correlated patterns" (may include width, training recipe) rather than isolated depth causality. Appropriate for EXISTENCE-tier validation.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Confound Correlation:** Classification may learn "depth + width + training recipe" rather than depth alone. Mitigation: Multi-family sampling provides evidence but doesn't guarantee isolation.
- **Generalization Uncertainty:** 20 models span only 3 architecture families (ResNet, VGG, DenseNet). Generalization to unseen families (EfficientNet, ConvNeXt) is untested.
- **Training Recipe Dominance Risk:** All models from PyTorch torchvision (standardized recipes) reduces variance but doesn't eliminate it. If training hyperparameters dominate weight statistics, classification succeeds for wrong reasons.

**Mitigation Strategy:** 
- P2 (within-family validation ≥65%) tests whether signal is architecture-family-specific
- P3 (random label ≤55%) validates signal over overfitting
- Null result plan commits to publishing negative findings if accuracy ≤60%
- Confound acknowledgment in hypothesis scope prevents overclaiming

**Acceptable Risk Level:** For EXISTENCE-tier validation, demonstrating that *some combination* of architectural properties (including depth) is weight-fingerprinted is sufficient. Pure causal isolation is MECHANISM-tier work.

---

