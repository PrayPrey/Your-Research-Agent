# Phase 2A Research Discussion Log

**Gap:** Architecture-Family-Specific Normalization of Geometric Signatures
**Gap ID:** gap-1
**Priority:** P1 (HIGH/PRIMARY)
**Mode:** UNATTENDED (Tikitaka Self-Contained Loop)
**Date:** 2026-08-10

---

## Discussion Briefing

### Research Gap Context

**Current State:** Existing approaches (WeightWatcher, Unterthiner 2020) compute weight statistics architecture-agnostically. Same thresholds apply across ResNet, ViT, ConvNeXt regardless of capacity differences.

**Missing Piece:** Normalization scheme accounting for architecture-specific capacity (depth × width × layer types). Within-family predictors leveraging architecture homogeneity.

**Potential Impact:** Enable accurate within-family model selection where cross-family predictors fail. Address stability issues from prior attempts (large models CV > 1.0).

### Previous Failure / Routing Context

**CRITICAL: This is a ROUTE_TO_0 recovery after 7 prior failures. The hypothesis MUST avoid these failed approaches:**

| Hypothesis | Failure Type | Root Cause | AVOID |
|------------|--------------|------------|-------|
| h-e1 Run 1 | IMPLEMENTATION_PROXY_MISMATCH | Random projection ≠ trained SANE encoder | Random projections as learned encoder proxy |
| h-e1 Run 2 | PARTIAL | Large models unstable (CV > 1.0), GroupNorm stable (CV = 0.0) | Architecture-agnostic thresholds |
| h-m1 Run 1 | HYPOTHESIS_FALSIFIED | ED PR >> EcD PR — bounded d* is CONTRASTIVE-INDUCED | Assuming bounded dimensionality is intrinsic |
| h-m2 Run 1 | MUST_WORK_GATE_FAILED | Single-layer NFN lacks capacity for ranking | Insufficient architecture capacity |
| h-m1 limitation | PARTIAL | Alpha metric p=0.55 (failed), r_eff/PR/d_MLE worked | Using alpha (power-law exponent) |
| h-e2 pivot | REQUIRES_REDESIGN | Random-init encoders near-equivariant | Untrained encoder assumptions |

**What Showed Promise:**
- Spectral features ARE extractable from pretrained models (h-e1 Run 2)
- Effective dimensionality metrics discriminate: r_eff, PR, d_MLE show large effect sizes
- GroupNorm models achieve perfect stability (CV = 0.0)
- Smaller models (resnet10t) consistently stable

**NEW APPROACH:** Direct spectral computation with architecture-aware normalization — no learned encoders, no alpha metric.

### Reference Papers

1. **Unterthiner et al. (2020)** - "Predicting Neural Network Accuracy from Weights" (arXiv:2002.11448)
   - Baseline: R² > 0.98 for ranking networks using simple weight statistics
   - Gap: Architecture-agnostic features

2. **Martin & Mahoney (2019)** - "Heavy-Tailed Self-Regularization" (arXiv:1901.08276)
   - Spectral analysis foundation, 5+1 training phases
   - Note: Alpha metric failed in prior attempts — use r_eff, PR instead

3. **Li et al. (2018)** - "Measuring Intrinsic Dimension" (arXiv:1804.08838)
   - Methodology for r_eff, PR, d_MLE computation

4. **Schürholt et al. (2022)** - "Model Zoos" (arXiv:2209.14764)
   - 50k+ model dataset for benchmarking

### Available Tools

- **WeightWatcher** (1759 stars): HTSR spectral analysis
- **timm** (37k stars): 1700+ pretrained models across architecture families
- **effective-dimension-pytorch**: KFAC-based effective dimension

### Feasibility Constraints

- MUST use existing datasets (timm model zoo)
- MUST use existing benchmarks (accuracy prediction R², MAE)
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic data or human evaluation
- NO learned encoders without pretrained checkpoints

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach architecture-aware normalization not as a simple scaling factor, but as a **learned transformation space**? Wait — that's exactly what failed before with SANE and CISE. Let me redirect.

Here's what excites me: the prior failure records show GroupNorm models achieved CV=0.0 while BatchNorm showed CV>1.0. This isn't just noise — it's a signal that **normalization layer type fundamentally reshapes weight geometry**. What if normalization layers act as geometric "anchors" that constrain weight manifold structure?

Consider this angle: instead of normalizing geometric features BY architecture capacity, what if we **cluster by normalization layer type FIRST**, then compute within-cluster geometric signatures? The architecture family (ResNet, ViT, ConvNeXt) might be less predictive than the normalization mechanism itself.

Cross-domain connection: In physics, symmetry constraints determine which manifold structures are accessible. BatchNorm has running statistics (breaks symmetry), GroupNorm is fully deterministic (preserves symmetry), LayerNorm operates channel-wise. These different symmetry structures could explain the stability differences we observed.

**Key Points:**
- Normalization layer type may be more fundamental than architecture family
- Symmetry-breaking (BatchNorm) vs symmetry-preserving (GroupNorm) could explain CV variance
- Propose: "Normalization-Aware Geometric Signatures" rather than architecture-aware

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing point about normalization layers, but let me stress-test this before we commit. The evidence from h-e1 Run 2 is suggestive but insufficient — we had only 11 models, and the GroupNorm result (CV=0.0) came from a single model (resnet50_gn).

What would disprove this? If we expanded to 50+ models per normalization type and found no systematic CV difference between BatchNorm and GroupNorm, that would falsify the normalization-primacy hypothesis. We need this as an explicit prediction.

More critically: the prior failures show that effective dimensionality metrics (r_eff, PR, d_MLE) discriminate while alpha does not. Any hypothesis we generate MUST specify:
1. Which metrics we compute (r_eff, PR, d_MLE — NOT alpha)
2. How we define "architecture-aware normalization" operationally
3. What quantitative threshold separates success from failure

For architecture-aware normalization, I propose this operationalization: normalize each geometric metric by the **theoretical maximum** for that layer shape. For a weight matrix W ∈ R^{m×n}, the maximum PR is min(m,n). Normalized PR = PR_observed / min(m,n). This gives a scale-invariant measure.

**Key Points:**
- Need n≥50 per normalization type for statistical power
- Explicit falsification: BatchNorm vs GroupNorm CV difference must be significant (p<0.05)
- Operationalize normalization: PR_normalized = PR_observed / min(m,n)

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess the scientific contribution here. The question is: does architecture-aware normalization of geometric signatures represent genuine novelty, or is it incremental engineering?

Looking at the prior art: Unterthiner (2020) achieved R² > 0.98 for accuracy prediction using architecture-agnostic features. If we're proposing architecture-aware variants and only improve from R² = 0.98 to R² = 0.985, that's not a contribution — it's noise.

The significance must come from a **qualitative capability**, not quantitative improvement. What could that be?

1. **Within-family model selection**: Unterthiner pooled all architectures. If architecture-aware features enable within-ResNet or within-ViT rankings where architecture-agnostic fails, THAT is novel.

2. **Transfer learning signals**: Can geometric signatures predict which pretrained models transfer well to unseen tasks? This is practically valuable and unexplored.

3. **Training dynamics inference**: Prior work (Martin & Mahoney) showed spectral properties reveal training phases. Architecture-aware analysis might reveal family-specific training patterns.

The h-e1 Run 2 partial result showing GroupNorm stability is interesting, but "different architectures behave differently" isn't surprising. We need to ask: **what actionable decision does this enable?**

**Key Points:**
- Significance requires capability gap, not incremental R² improvement
- Focus: within-family model selection where cross-family fails
- Must answer: "What decision does this enable that wasn't possible before?"

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in what's actually implementable with the constraints.

**Feasibility Assessment:**

1. **Data availability**: timm has ~1700 pretrained models. Within-family counts:
   - ResNet variants: ~80 models (resnet10t through resnet200d)
   - ViT variants: ~100 models
   - ConvNeXt: ~20 models
   - EfficientNet: ~50 models
   This is sufficient for within-family analysis with n≥20 per family.

2. **Metric computation**: r_eff, PR, d_MLE require only eigenvalue decomposition of weight matrices. This is O(min(m,n)³) per layer — expensive for large layers but tractable. WeightWatcher already implements this.

3. **Normalization-type labeling**: timm models are labeled. resnet50_gn vs resnet50 distinguishes GroupNorm. This metadata exists.

4. **Ground truth for prediction**: ImageNet top-1 accuracy is available for all timm models. This is our prediction target.

**Technical Soundness Check:**

The proposed normalization (PR / min(m,n)) is mathematically valid — it bounds the metric to [0,1] regardless of layer shape. This addresses the scale issue Dr. Vera raised.

However, one concern: layer-wise aggregation. A ResNet-50 has ~50 weight matrices. How do we aggregate PR across layers? Mean? Weighted by parameter count? This isn't trivial and affects prediction quality.

**Key Points:**
- timm provides sufficient data (80+ ResNets, 100+ ViTs)
- Metrics computable with existing WeightWatcher tooling
- Layer-wise aggregation strategy needs specification

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on the discussion, let me synthesize a concrete hypothesis that addresses the concerns raised.

**Emerging Hypothesis:**

"Within-architecture-family geometric signatures (layer-wise r_eff, PR aggregated by depth-weighted mean) predict model accuracy with higher R² than architecture-agnostic features, specifically achieving R² ≥ 0.85 for within-family ranking where cross-family pooled features achieve R² ≤ 0.60."

This addresses:
- **Dr. Sage's concern**: We claim a capability gap (within-family vs cross-family), not incremental improvement
- **Prof. Vera's requirement**: Specific quantitative threshold (R² ≥ 0.85 vs ≤ 0.60)
- **Prof. Pax's aggregation question**: Depth-weighted mean (layers closer to output weighted higher, as they correlate more with output properties)

**Strengthening with evidence:**

The h-e1 Run 2 data actually supports this: large models showed high CV (instability) when pooled cross-family, but GroupNorm models (a specific architectural choice) showed CV=0.0. If we restrict to within-family, we remove the cross-architecture confound.

**Refinement proposal:**

Instead of comparing R² across vs within family, let's frame it as: "Within-family geometric predictors explain variance that between-family features miss." This is testable via variance decomposition: total variance = between-family + within-family. Our claim is that within-family geometric signatures capture the within-family variance component.

**Key Points:**
- Hypothesis: within-family R² ≥ 0.85 where cross-family R² ≤ 0.60
- Aggregation: depth-weighted mean of layer-wise PR
- Evidence: h-e1 Run 2 showed within-type stability

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me identify where this breaks down.

**Flaw 1: R² threshold is arbitrary.**

Why R² ≥ 0.85? This looks like post-hoc rationalization. If we get R² = 0.80, do we claim failure? The threshold should emerge from the literature baseline. Unterthiner achieved R² > 0.98 for cross-architecture with sufficient data. If within-family with less data achieves R² = 0.85, is that better or worse?

**Flaw 2: Confounding model count with architecture.**

ResNet family has 80 models; ConvNeXt has 20. More data → higher R² mechanically. If ResNet achieves R² = 0.90 and ConvNeXt achieves R² = 0.60, is that architecture-specific or sample-size-specific?

**Flaw 3: Depth-weighted aggregation is unjustified.**

Why weight later layers higher? Prior work (Martin & Mahoney) found earlier layers show clearer heavy-tail signatures because they're more overparameterized. The aggregation scheme needs empirical validation, not assumption.

**What would convince me:**

1. **Control for sample size**: Report R² with bootstrap confidence intervals. Compare families at matched sample sizes (e.g., random 20-model subsets).

2. **Ablate aggregation**: Test mean, depth-weighted, parameter-weighted. Report which works best empirically.

3. **Baseline comparison**: Compare to Unterthiner's exact features on the same within-family subsets. If our geometric signatures don't beat their simple statistics within-family, we have no claim.

**Key Points:**
- R² threshold needs justification from baseline
- Must control for family sample size
- Aggregation scheme requires ablation study

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critique is valid — but let me reframe the novelty argument.

The core insight isn't "architecture-aware features beat architecture-agnostic features." That's incremental. The REAL novelty is: **geometric signatures reveal architecture-specific failure modes.**

Consider: h-e1 Run 2 showed ResNet-152 had CV > 1.0 (completely unstable) while ResNet-10t had low CV. This isn't about prediction accuracy — it's about **identifying which models have stable geometric signatures at all**.

New angle: **Geometric Signature Reliability as a Model Property.**

Hypothesis reframe: "The coefficient of variation (CV) of geometric signatures (r_eff, PR) across probe sets is itself predictive of model robustness. Models with CV < 0.3 exhibit more consistent behavior under distribution shift."

This is testable using existing robustness benchmarks (ImageNet-C, ImageNet-R, ImageNet-A). If low-CV models also show lower accuracy drop under corruption, we've found a new signal — not just prediction, but reliability estimation.

**Cross-domain connection:** In reliability engineering, variance in performance metrics signals brittleness. A machine with high variance in efficiency measurements is more likely to fail catastrophically. Same could apply to neural networks.

**Key Points:**
- Shift from "better prediction" to "reliability indicator"
- CV of geometric signatures may predict robustness to distribution shift
- Testable on ImageNet-C/R/A with existing timm models

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's reframe is interesting — CV as reliability indicator — but we're now discussing two separate hypotheses:

**H1 (Original):** Architecture-aware geometric signatures predict accuracy better within families.

**H2 (Dr. Nova's reframe):** CV of geometric signatures predicts robustness to distribution shift.

These are orthogonal. H2 is more novel but requires robustness benchmarks. Let me assess feasibility.

**H2 Testability:**

- ImageNet-C accuracy is available for many timm models via RobustBench leaderboard
- We'd compute: correlation(CV_geometric, Δ_accuracy_ImageNet_to_ImageNet-C)
- Prediction: negative correlation (low CV → smaller accuracy drop)

**Falsification for H2:**

If correlation is not significant (p ≥ 0.05) or positive (high CV → better robustness), hypothesis fails.

**Measurement validity:**

CV of geometric signatures requires computing signatures multiple times with different probe sets. This is computationally tractable — we sample different subsets of ImageNet validation images and recompute layer-wise features. If CV is computed correctly and still shows no correlation with robustness, the hypothesis is false.

**Recommendation:** 

We should pursue H2 as the primary hypothesis (higher novelty), with H1 as a supporting analysis. The failure records showed CV variance by architecture — now we connect that to robustness rather than just accuracy prediction.

**Key Points:**
- H2 (CV predicts robustness) is more novel than H1 (within-family prediction)
- Testable: correlation(CV_geometric, Δ_accuracy on ImageNet-C)
- Falsification: non-significant or positive correlation

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's framing of H2 clarifies the contribution. Let me assess field impact.

**Why H2 matters:**

Current robustness evaluation requires running models on corrupted datasets — expensive, especially for large model zoos. If geometric signature CV predicts robustness WITHOUT running inference, we enable:

1. **Model selection without evaluation**: Given 1000 pretrained models, select the most robust ones by computing cheap weight statistics, not expensive inference.

2. **Training diagnostics**: High CV during training might signal emerging brittleness, enabling early intervention.

3. **Architecture design insights**: If certain architectures consistently show low CV, we learn principles for robust architecture design.

**What's genuinely new:**

- Unterthiner predicted accuracy from weights — we predict robustness (different target)
- Martin & Mahoney analyzed spectral properties — we analyze variance of those properties across probe sets
- Neither connected weight geometry to distribution shift robustness

**Impact assessment:**

This is a **medium-high contribution** if the correlation holds. It's not paradigm-shifting, but it provides a new tool for model selection and training diagnostics using existing infrastructure.

**Remaining question:**

Is CV computed correctly? How many probe sets? What size? This operationalization matters for reproducibility.

**Key Points:**
- H2 enables model selection without expensive robustness evaluation
- Novel: connecting weight geometry variance to distribution shift
- Impact: medium-high practical tool

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me verify H2's technical feasibility.

**Probe Set Protocol:**

CV of geometric signatures requires:
1. Sample K probe sets (K=10-20 sufficient for CV estimation)
2. Each probe set: N=1000 images from ImageNet validation
3. For each probe set: compute layer-wise r_eff, PR for all layers
4. CV = std(metric across K sets) / mean(metric across K sets)

**Computational cost:**

For one model with L layers:
- K × L forward passes per probe set (for gradient-based features) — but we're using WEIGHT features, not activation features!

Wait — clarification needed. Are we computing geometric signatures from:
(a) **Weight matrices only** (static, no forward pass), or
(b) **Activation patterns** given inputs (requires inference)?

Prior discussion assumed (a) — WeightWatcher computes from weights. But CV across "probe sets" implies (b) — we need different inputs.

**Critical clarification:**

If we're computing weight-only statistics, CV is ZERO by definition — weights don't change with different inputs. The CV variance in h-e1 Run 2 likely came from:
- Different random seeds for probe matrix construction (for participation ratio estimation)
- Or different models, not different probe sets

**Revised feasibility:**

If CV means variance across RANDOM PROJECTION seeds (not input probe sets), then:
- Compute geometric signatures with K different random seeds
- CV measures signature stability to random initialization
- This IS computable without inference

**Key Points:**
- CRITICAL: Weight-only features have CV=0 unless randomness is in the estimator
- CV likely measures estimator variance, not input-dependence
- Feasibility confirmed IF CV = variance across random seeds

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Pax's clarification is crucial. Let me refine the hypothesis to address this.

**Source of CV Variance:**

Looking back at h-e1 Run 2, the CV computation used participation ratio (PR), which is deterministic given eigenvalues. However, computing eigenvalues for large matrices often uses randomized SVD (for efficiency), which introduces seed-dependent variance.

So CV measures: **estimator stability given compute budget constraints**.

**Refined Hypothesis:**

"The coefficient of variation (CV) of geometric signatures (r_eff, PR computed via randomized SVD with K=20 different seeds) reflects model conditioning. Models with CV < 0.3 exhibit:
(a) Better numerical stability in downstream fine-tuning (fewer NaN/Inf events)
(b) More consistent performance across random fine-tuning seeds"

This shifts the target from "robustness to distribution shift" to "numerical conditioning" — which is testable without robustness benchmarks.

**Connection to prior findings:**

- h-e1 Run 2 showed GroupNorm models had CV=0.0 — GroupNorm is known to improve training stability
- Large models had high CV — larger models are harder to condition numerically
- This fits the "conditioning → stability" narrative

**Simplified Testable Prediction:**

P1: CV_geometric correlates negatively with fine-tuning stability (measured as variance of final accuracy across 5 random seeds)

This uses existing fine-tuning infrastructure and requires no robustness benchmarks.

**Key Points:**
- CV measures estimator stability (randomized SVD seeds)
- Hypothesis: low CV → better numerical conditioning → stable fine-tuning
- Testable: correlation(CV_geometric, variance of fine-tuning accuracy)

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's refinement is better grounded, but let me stress-test.

**Concern 1: Circularity risk.**

If CV comes from randomized SVD, and GroupNorm models have CV=0.0, maybe GroupNorm weight matrices are just smaller or better conditioned — making randomized SVD more stable. We might be measuring "matrix conditioning" not "model robustness."

That's fine if we claim "geometric signature CV reflects weight matrix conditioning" — but then the novel claim is weaker. Matrix condition number is well-understood; CV of PR is just a convoluted way to measure it.

**Concern 2: Fine-tuning stability is confounded.**

Fine-tuning stability depends on: learning rate, optimizer, dataset, training duration. Variance across seeds could be dominated by these, not model conditioning. We'd need to control all hyperparameters carefully.

**Concern 3: GroupNorm CV=0.0 was n=1.**

One model showed this. Statistical claims require larger samples.

**What would convince me:**

1. Show CV correlates with actual condition number (κ = σ_max / σ_min). If correlation > 0.9, CV is redundant.

2. If CV captures something BEYOND condition number, that's interesting. Report partial correlation controlling for κ.

3. Fine-tuning experiment with fixed hyperparameters, 5 seeds, 50+ models. Report correlation with proper confidence intervals.

**Key Points:**
- CV might just proxy condition number — test this
- Control hyperparameters in fine-tuning stability experiment
- Need n >> 1 for GroupNorm finding to generalize

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex correctly identifies that CV might proxy condition number. Let me find what's genuinely novel.

**What CV captures that condition number doesn't:**

Condition number (κ) is a scalar for each matrix. CV aggregates across multiple random estimations, capturing how FLAT vs PEAKED the singular value spectrum is.

Consider: Two matrices with identical κ but different spectral shapes:
- Matrix A: few large singular values, many tiny ones (peaked)
- Matrix B: gradually decaying singular values (flat)

Both have same κ, but randomized SVD converges faster on A (dominated by top singular values) than B. So CV reflects spectral SHAPE, not just extremes.

**New angle: Spectral Shape as Generalization Signal**

Heavy-tail theory (Martin & Mahoney) shows that well-trained models have specific spectral decay patterns. If CV reflects spectral shape, and spectral shape reflects training quality, then CV may predict generalization without computing full spectral analysis.

**Revised Hypothesis:**

"The CV of participation ratio (computed via 20 randomized SVD seeds) captures spectral shape information beyond condition number. Models with low CV have flatter spectral decay and exhibit better generalization to held-out data (lower gap between train and test accuracy)."

**Key experiment:**

Compute for each model: CV_PR, condition_number, generalization_gap. Report:
- correlation(CV_PR, generalization_gap)
- partial_correlation(CV_PR, generalization_gap | condition_number)

If partial correlation significant, CV captures novel information.

**Key Points:**
- CV reflects spectral shape, not just condition number
- Flat spectra → fast SVD convergence → low CV
- Test: partial correlation controlling for condition number

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's spectral shape argument is sound. Let me formalize the hypothesis for experimental design.

**Final Hypothesis Statement:**

*Under [scope]:* Pretrained image classification models from timm (ResNet, ViT, EfficientNet families)

*If [intervention]:* We compute CV of participation ratio across 20 randomized SVD seeds for each weight matrix, then aggregate via depth-weighted mean

*Then [outcome]:* CV_PR correlates negatively with generalization (operationalized as validation accuracy minus training accuracy, or equivalently, ImageNet top-1 accuracy for pretrained models)

*Because [mechanism]:* CV reflects spectral shape — models with flatter spectral decay have lower CV and better-conditioned loss landscapes, enabling generalization

**Testable Predictions:**

P1 (Primary): Pearson correlation(CV_PR, accuracy) < -0.3 with p < 0.05, n ≥ 100 models

P2 (Mechanism): Partial correlation(CV_PR, accuracy | condition_number) remains significant, confirming CV captures more than just conditioning

P3 (Architecture-specific): Within ResNet family, correlation strengthens (|r| > 0.5) compared to cross-family pooled

**Success Criteria:**

- P1 must pass (MUST_WORK gate)
- P2 passing adds mechanistic evidence
- P3 passing supports architecture-aware value

**Falsification:**

- P1 fails if correlation non-significant or positive
- P2 fails if partial correlation drops below 0.1
- P3 fails if within-family correlation weaker than cross-family

**Key Points:**
- Hypothesis: CV_PR negatively correlates with accuracy
- Three predictions with specific thresholds
- P1 is MUST_WORK; P2, P3 strengthen claim

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis moves beyond simple "architecture-aware features" to connect spectral SHAPE (not just condition number) to generalization. The CV of participation ratio as a cheap proxy for spectral decay pattern is genuinely novel — prior work measured spectral properties directly but didn't connect estimator variance to model quality.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three explicit predictions with quantitative thresholds. P1 is the gate (correlation < -0.3, p < 0.05). P2 tests mechanism specificity via partial correlation. P3 tests architecture-aware value. Each prediction has clear falsification criteria. Reproducible with standard tools (randomized SVD, timm models, public accuracy data).

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** If P1 passes, this provides a cheap model quality signal computable without inference. Practical value for model selection from large zoos. However, if the correlation is weak (-0.3 to -0.4), the predictive utility is limited. Significance depends on effect size. Field contribution is solid but not transformative.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Fully implementable with existing tools. Randomized SVD is standard (sklearn, scipy). timm provides models and accuracy labels. No learned encoders, no new data collection, no human evaluation. Computational cost is tractable (~1 minute per model for 20-seed CV computation). Avoids all prior failure modes (no random projection proxies, no alpha metric, no architecture-agnostic thresholds).

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a refined hypothesis connecting the coefficient of variation (CV) of participation ratio—computed via randomized SVD with 20 seeds—to model generalization quality. The core claim is that CV reflects spectral shape information beyond condition number: models with flatter spectral decay exhibit lower CV and generalize better.

The primary prediction (P1) states that CV_PR correlates negatively with ImageNet accuracy (r < -0.3, p < 0.05) across 100+ timm models. The mechanism prediction (P2) requires that this correlation persists when controlling for condition number, confirming CV captures novel information. The architecture-aware prediction (P3) expects stronger correlation within families like ResNet.

This hypothesis avoids all prior failure modes: no learned encoders (direct SVD), no alpha metric (using PR/r_eff), no architecture-agnostic thresholds (testing P3 explicitly). The approach is feasible using existing timm infrastructure and WeightWatcher tooling. If P1 passes, we have a cheap, interpretable model quality signal; if P2 passes, we understand WHY it works.

Experimental setup: 100+ models from timm (ResNet, ViT, EfficientNet families), compute layer-wise CV_PR with 20 seeds, aggregate via mean, correlate with ImageNet top-1 accuracy. Baseline comparison: Unterthiner features on same models.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Effect size matters — r = -0.3 explains only 9% of variance. If this is the ceiling, practical utility is limited.
- **Concern 2:** Aggregation scheme (mean vs depth-weighted) still needs empirical validation in P1 analysis.
- **Concern 3:** Confound: model size correlates with both accuracy and computational stability. Must control for parameter count.
- **Mitigation Strategy:** Report R² and partial correlations controlling for model size. Ablate aggregation schemes. Set minimum useful effect size threshold (|r| ≥ 0.5 for practical utility).

---

## Emerged Hypothesis Summary

### Core Statement

**Under** pretrained image classification models from timm (n ≥ 100), **if** we compute the coefficient of variation (CV) of participation ratio across 20 randomized SVD seeds and aggregate layer-wise metrics via mean, **then** CV_PR correlates negatively with model accuracy (r < -0.3, p < 0.05), **because** CV reflects spectral shape — flatter decay enables better generalization.

### Causal Mechanism

1. **Step 1:** Model training shapes weight matrix spectral properties (supported by Martin & Mahoney 2019)
2. **Step 2:** Spectral shape (flat vs peaked decay) affects randomized SVD convergence rate
3. **Step 3:** Flat spectra → consistent SVD across seeds → low CV
4. **Step 4:** Flat spectra also indicate smooth loss landscapes → better generalization (supported by Li et al. 2018)
5. **Conclusion:** Low CV ↔ flat spectra ↔ good generalization

### Variables

**Independent Variable (IV):**
- CV_PR: Coefficient of variation of participation ratio computed via 20 randomized SVD seeds, aggregated by layer-wise mean
- Type: Continuous
- Operationalization: std(PR across seeds) / mean(PR across seeds), averaged over all weight matrices

**Dependent Variable (DV):**
- Model accuracy: ImageNet top-1 validation accuracy
- Type: Continuous (0-100%)
- Source: timm model metadata

**Controlled Variables:**
- Architecture family (for P3 analysis)
- Parameter count (partial correlation control)
- Training dataset (ImageNet-1K only)

### Key Assumptions

- A1: Randomized SVD introduces meaningful variance that reflects spectral properties (not just numerical noise)
- A2: timm models span sufficient diversity in training quality
- A3: ImageNet accuracy is a valid proxy for generalization
- A4: Layer-wise mean aggregation preserves predictive signal
- A5: Participation ratio is more informative than condition number alone

### Null Hypothesis

H0: There is no significant negative correlation between CV_PR and model accuracy (r ≥ 0 or p ≥ 0.05).

### Predictions

- **P1 (Primary, MUST_WORK):** correlation(CV_PR, accuracy) < -0.3 with p < 0.05, n ≥ 100
- **P2 (Mechanism):** partial_correlation(CV_PR, accuracy | κ) significant after controlling for condition number
- **P3 (Architecture-aware):** |correlation within ResNet family| > |correlation cross-family|

### Novelty

Prior work measured spectral properties directly (eigenvalues, alpha exponent). This hypothesis measures **estimator variance** of spectral metrics, connecting computational stability of spectral decomposition to model quality. This is novel — no prior work used SVD seed variance as a model quality signal.

### Scope & Boundaries

**Applies to:** Pretrained image classification models, timm zoo, models with 2D conv or linear layers
**Does not apply to:** Language models (different architecture), randomly initialized models, models < 1M parameters
**Known limitations:** Effect size may be moderate; aggregation scheme not yet validated; fine-tuning behavior not tested

### Experimental Setup

- **Dataset:** timm model zoo (100+ models: ResNets, ViTs, EfficientNets)
- **Metrics:** CV_PR, condition number, ImageNet top-1 accuracy
- **Tools:** WeightWatcher (spectral analysis), sklearn (randomized SVD), timm (models)
- **Baseline:** Unterthiner et al. features correlation on same models

### Related Work & Baselines

- **Unterthiner et al. (2020):** Weight statistics predict accuracy (R² > 0.98 cross-architecture)
- **Martin & Mahoney (2019):** Spectral analysis reveals training quality
- **Li et al. (2018):** Intrinsic dimension methodology

### Phase 2B Readiness Seeds

- **H-E1 (Existence):** CV_PR negatively correlates with accuracy
- **H-M1 (Mechanism):** CV reflects spectral shape beyond condition number
- **H-C1 (Condition):** Within-family correlation stronger than cross-family

### Established Facts

- Spectral features ARE extractable from pretrained models (h-e1 Run 2)
- r_eff, PR, d_MLE show large effect sizes; alpha does NOT (h-m1 limitation)
- GroupNorm models showed CV=0.0, BatchNorm showed higher CV (h-e1 Run 2)
- Existing baseline: R² > 0.98 for accuracy prediction (Unterthiner)
