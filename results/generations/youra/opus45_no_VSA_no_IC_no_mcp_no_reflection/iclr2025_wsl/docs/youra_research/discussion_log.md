# Phase 2A Discussion Log

## Metadata
- **Generated:** 2026-08-29
- **Gap ID:** gap-1-cross-arch-generalization
- **Gap Title:** Cross-Architecture Generalization of Weight Features
- **Architecture:** Self-Play Tikitaka (Claude plays all personas)

---

## Briefing Context

### Research Gap
**Gap 1: Cross-Architecture Generalization of Weight Features**

**Current State:** Weight-space accuracy prediction demonstrated within single architecture families (CNNs). Hugging Face hosts diverse architectures (ViT, ConvNeXt, Swin) with fundamentally different weight tensor structures.

**Missing Piece:** Systematic evaluation of whether weight statistics (spectral norms, Frobenius norms) maintain predictive power across architecturally distinct model families (attention-based vs convolution-based).

**Potential Impact:** High - If cross-architecture features exist, enables unified model selection tool for heterogeneous model zoos.

### Reference Papers
1. **Unterthiner et al. (2020)** - "Predicting Neural Network Accuracy from Weights" - Direct predecessor establishing feasibility
2. **Eilertsen et al. (2020)** - "Classifying the classifier: dissecting the weight space of neural networks" - Weight space analysis methodology
3. **Schürholt et al. (2022)** - "Model Zoos: A Dataset of Diverse Populations of Neural Network Models" - Dataset paradigm for weight-space research
4. **Martin & Mahoney (2021)** - "Implicit Self-Regularization in Deep Neural Networks" - Heavy-tailed theory linking weight distributions to generalization

### Key Research Questions
1. Do weight statistics (spectral norms, Frobenius norms) maintain predictive power across CNN/ViT boundaries?
2. Are there architecture-invariant weight features that predict ImageNet accuracy?
3. What architecture-specific adaptations are needed for attention-based models?

### Feasibility Constraints (Pipeline-Enforced)
- MUST use existing real datasets (ImageNet, Hugging Face Model Hub)
- MUST use existing benchmarks (ImageNet validation accuracy)
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or subjective scoring

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if the problem isn't finding *universal* weight features, but discovering *structural invariants* that map across architectures? 

Consider this: CNNs use convolution kernels, ViTs use attention matrices, but both ultimately learn to extract hierarchical features. Unterthiner's weight statistics worked because they captured something about learned representations, not about convolution specifically. The question is: what's the architectural-invariant analog?

Here's a wild idea: instead of computing spectral norms on raw weight matrices (which have different shapes across architectures), we could compute them on *effective receptive field operators*. A 3x3 conv kernel and a self-attention head both define operators that mix spatial information — the spectral properties of these operators might be comparable even when raw weights aren't.

Another angle: Martin & Mahoney's heavy-tailed theory isn't about architecture at all — it's about learning dynamics. If both CNNs and ViTs exhibit power-law weight distributions when well-trained, the *exponent* of that distribution might be architecture-invariant even when the *shape* of weight tensors differs.

**Key Points:**
- Look for structural invariants, not raw feature equivalence
- Effective receptive field operators as architecture-agnostic abstraction
- Heavy-tailed exponents may transfer where raw statistics don't

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's ideas are intriguing, but let me stress-test them. The claim that "effective receptive field operators" can be compared across architectures needs precise operationalization.

For a conv layer, the spectral norm is well-defined: largest singular value of the weight matrix reshaped appropriately. For self-attention, we have Q, K, V projections plus the attention operation itself. What exactly would we measure? The spectral norm of W_Q? Of W_Q @ W_K^T? The expected spectral norm over input distributions?

The falsifiability question: if we claim heavy-tailed exponents are architecture-invariant, we need to predict *specific* values. What power-law exponent do we expect for a well-trained ViT-B/16 on ImageNet? If we can't predict it, we can only observe post-hoc, which weakens the hypothesis.

A concrete test: download 100 ResNet variants and 100 ViT variants from Hugging Face with known ImageNet accuracies. Compute candidate features (Frobenius norms, spectral norms, heavy-tailed exponents) for each. Train separate regressors for each architecture family, then test cross-architecture: does the ResNet regressor predict ViT accuracy? That's the falsifiable experiment.

**Key Points:**
- Need precise operationalization of "spectral norm" for attention
- Hypothesis must make specific, falsifiable predictions
- Cross-regressor generalization is the key test

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess what's genuinely novel here versus incremental extension.

Unterthiner et al. (2020) showed weight→accuracy prediction works for CNNs. Simply repeating this for ViTs is incremental — useful but not a significant contribution. The *significant* question is: does a **single unified predictor** work across architectures?

If yes, the impact is substantial: practitioners could use weight statistics as a model selection criterion across any architecture, without architecture-specific calibration. This would be a genuine tool, not just a research curiosity.

If no (separate predictors needed per architecture family), that's still valuable — it reveals something fundamental about how different architectures encode learning. But it's a smaller contribution.

The field-advancing claim would be: "We identify architecture-invariant features that predict generalization quality regardless of whether the model is attention-based or convolution-based." That opens questions about what's truly fundamental in learned representations.

What I don't want to see is a paper that just says "we measured things on ViTs too." The contribution must be about *transfer* or *invariance*, not replication.

**Key Points:**
- Unified predictor across architectures = significant contribution
- Architecture-specific predictors = smaller but valid contribution
- The novelty is in transfer/invariance, not replication

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in what we can actually measure and compute.

**Technically feasible:**
- Downloading 100+ models per architecture family from Hugging Face: trivial
- Computing Frobenius norms, spectral norms: well-defined, library support exists
- Computing heavy-tailed exponents via Hill estimator or similar: established methods
- Training MLP regressors: standard ML

**Technically questionable:**
- "Effective receptive field operators" — this is hand-wavy. For CNNs, we can compute receptive fields analytically. For ViTs with dynamic attention patterns, there's no static operator to analyze. This path requires significant theoretical development before it's measurable.
- Comparing spectral norms across architectures directly assumes comparable scaling, which may not hold.

**My recommendation:** Start with the simplest possible features — layer-wise Frobenius norms, model-wide spectral norm of the largest layer, heavy-tailed exponent of all weights concatenated. These are architecture-agnostic computations. If they transfer, great. If not, we learn something. Don't over-engineer before validating the basic premise.

The theoretical elegance of "effective receptive field operators" is appealing, but we don't need it to answer the research question. Simpler features first.

**Key Points:**
- Simple features (Frobenius, spectral, heavy-tailed) are immediately measurable
- "Effective receptive field" requires too much theoretical development
- Validate basic premise before adding complexity

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize what's emerged and propose a concrete hypothesis.

Prof. Vera's cross-regressor experiment is exactly right — that's our falsifiable test. Prof. Pax's call for simplicity is wise. Dr. Nova's intuition about structural invariants guides what we're looking for. Dr. Sage's framing about unified vs separate predictors defines our contribution tiers.

**Proposed Hypothesis:**

*Under:* Collections of pretrained vision models on Hugging Face Model Hub (ResNet, ViT, ConvNeXt families)

*If:* We extract architecture-agnostic weight statistics (heavy-tailed exponent α, mean spectral norm ratio, normalized Frobenius norm) and train a single regression model

*Then:* This unified predictor achieves correlation r ≥ 0.6 with true ImageNet validation accuracy across all architecture families

*Because:* Well-trained models exhibit similar implicit self-regularization signatures (per Martin & Mahoney) regardless of architecture, and these signatures encode generalization quality

**Predictions:**
1. Heavy-tailed exponent α is predictive (r > 0.4) for both CNNs and ViTs individually
2. A unified regressor trained on mixed architectures outperforms architecture-specific regressors when tested on held-out architecture families
3. Models with α in range [2.0, 2.5] will cluster in the top 30% of accuracy regardless of architecture

**Key Points:**
- Concrete hypothesis with falsifiable predictions
- Tests unified predictor (major contribution) vs architecture-specific (minor contribution)
- Uses only simple, immediately measurable features

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I have concerns with this hypothesis. Let me probe them.

**Concern 1: Confounded by model size.** Larger models (more parameters) tend to have higher accuracy AND different weight statistics simply due to scale. If we're just predicting "big model = good model," we haven't found anything about generalization quality. The predictor must beat a baseline of "log(parameter count)."

**Concern 2: Heavy-tailed exponent variance.** Martin & Mahoney showed heavy-tailed behavior in specific architectures under specific training regimes. Has this been validated for ViTs? For models trained with different regularization (mixup, RandAugment)? The exponent might vary with training recipe more than generalization.

**Concern 3: Prediction P3 is suspicious.** Claiming models with α in [2.0, 2.5] will be in top 30% accuracy requires that α is stable across architectures, that the range is meaningful for ViTs, and that the relationship is monotonic. None of these are established.

**What would convince me:**
1. Show that weight features improve over parameter count baseline
2. Control for training procedure (compare models with same ImageNet training recipe)
3. Validate heavy-tailed theory holds for ViTs before using it as a predictor

**Key Points:**
- Must beat parameter count baseline
- Confounds from model size and training recipe
- Heavy-tailed theory unvalidated for modern architectures

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex raises valid concerns. Let me address them and refine the hypothesis.

**Addressing Concern 1 (Model Size Confound):**
Yes, we must beat the baseline. Refined prediction: "The unified weight-feature regressor achieves R² > (baseline R² + 0.15) where baseline is log(parameter_count) regression." This makes the bar clear.

**Addressing Concern 2 (Heavy-Tailed Variance):**
Rather than assuming heavy-tailed theory holds, we make it a *testable sub-hypothesis*: "H-M1: Heavy-tailed exponents computed on ViT attention weight matrices exhibit comparable variance to those computed on CNN conv weights." If H-M1 fails, we fall back to Frobenius/spectral features only.

**Addressing Concern 3 (Prediction P3):**
I withdraw P3 as stated. It was over-specific. Replace with: "P3: The top 20% of models by predicted accuracy (from weight features) has >80% overlap with top 20% by true accuracy, for both CNN and ViT families separately."

**Refined Hypothesis:**

*Core Claim:* Simple architecture-agnostic weight statistics (heavy-tailed exponent, spectral norm, Frobenius norm) can predict ImageNet validation accuracy across architecture families better than model size alone.

*Null Hypothesis H0:* Weight statistics do not improve prediction over log(parameter_count) baseline.

*Testable Predictions:*
- P1: Heavy-tailed exponent is computable and has bounded variance for ViTs (validates applicability)
- P2: Unified regressor R² > (baseline R² + 0.15) on held-out architecture family
- P3: Top 20% predicted ∩ top 20% actual > 80% within each architecture family

**Key Points:**
- Explicit baseline (parameter count) that must be beaten
- Heavy-tailed applicability to ViT is a testable sub-hypothesis
- Refined predictions are falsifiable and architecture-aware

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** MODERATE
- **Assessment:** The core idea (architecture-invariant weight features) is novel as a research question. However, the features themselves (Frobenius, spectral, heavy-tailed) are established. Novelty lies in demonstrating transfer, not in the features.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is clearly falsifiable with the cross-regressor experiment. Specific quantitative predictions (R² improvement, overlap percentages) can be tested. The baseline comparison prevents trivial success.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** If successful, provides a useful model selection tool. The contribution is practical rather than theoretical. Impact depends on effect size — marginal improvement over baseline won't excite the field.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All proposed measurements are technically well-defined and computable. Uses existing datasets (Hugging Face, ImageNet). No new benchmarks or data collection required. Can be executed immediately.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a testable hypothesis about cross-architecture weight feature generalization. The core claim is that simple architecture-agnostic weight statistics (heavy-tailed exponent α, spectral norms, Frobenius norms) can predict ImageNet validation accuracy for pretrained vision models across architecture families (ResNet, ViT, ConvNeXt) better than a parameter-count baseline.

The mechanism draws on Martin & Mahoney's theory that well-trained networks exhibit implicit self-regularization reflected in heavy-tailed weight distributions, which should manifest regardless of whether the architecture uses convolution or attention. The hypothesis is that these regularization signatures encode generalization quality in a transferable way.

Three testable predictions emerged: (1) heavy-tailed exponents can be computed with bounded variance on ViT attention weights, validating the theory's applicability; (2) a unified regressor achieves R² at least 0.15 higher than parameter-count baseline when tested on held-out architecture families; (3) top 20% predicted models have >80% overlap with top 20% actual accuracy within each architecture family.

The experimental setup uses existing Hugging Face models with known ImageNet accuracies, requires no new benchmarks, and can be executed with standard tools. This satisfies all feasibility constraints.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Training procedure confound not fully controlled — models trained with different augmentation may have different weight statistics independent of generalization
- Effect size uncertainty — we don't know if R² + 0.15 is achievable or if the true effect is smaller
- **Mitigation Strategy:** Include training recipe as a covariate if metadata is available; report confidence intervals on all effect sizes; treat sub-hypothesis H-M1 (heavy-tailed validity for ViT) as gatekeeping — if it fails, interpret results accordingly

