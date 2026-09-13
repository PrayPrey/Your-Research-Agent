# Phase 2A Research Discussion Log

**Workflow:** Phase 2A-Dialogue v9.0.0 (Self-Contained Tikitaka Loop)
**Date:** 2026-04-14
**Gap ID:** gap-1
**Gap Title:** No Existing Loss Trajectory Divergence Analysis for Spurious Correlation

---

## Discussion Briefing

### Research Context

**Primary Research Question:**
Do per-sample loss trajectories exhibit statistically significant divergence between minority and majority group samples during the first N epochs of training, and can trajectory-based features (convergence rate, variance, inflection points) predict group membership with AUC > 0.75 on existing spurious correlation benchmarks (Waterbirds, CelebA)?

### Background from Phase 1

**Key Findings:**
1. **Strong theoretical foundation exists:** Toneva et al. (2018, 933 citations) established per-sample training dynamics tracking; Li et al. (2025) shows 142-D training dynamics features are predictive
2. **No existing work on trajectory divergence for spurious correlation:** This represents a genuine research gap
3. **Implementation path is clear:** mtoneva/example_forgetting + PyTorch `reduction='none'` + deep_feature_reweighting benchmarks

**Three Critical Gaps Identified:**
1. No empirical evidence that loss trajectories diverge between groups
2. Unknown temporal emergence (epoch T) of trajectory divergence
3. No trajectory feature → group prediction benchmark (AUC > 0.75 criterion)

### Failure Context (ROUTE_TO_0 Recovery)

**Previous Attempt (h-e1 Attribution Divergence):**
- **Result:** ABANDON - IoU = 0.6477 (expected < 0.3)
- **Key Insight:** Attribution patterns are SIMILAR between groups, NOT different
- **Implication:** The problem is in HOW features are processed, not WHERE the model looks

**7+ Previous Failed Approaches:**
| Run | Approach | Why Failed | Key Insight |
|-----|----------|------------|-------------|
| 1 | GNGR (Gradient-Norm Guided Reweighting) | +1.14% WGA only | Detection ≠ Intervention |
| 2 | LC-GNR Layer Localization | Direction reversed | Encoder divergence > classifier |
| 3 | CISR/CMGR (SAM-based) | Feature collapse | SAM amplifies spurious features |
| 4 | VGCS (Velocity-Gated) | AUC=0.5146 (random) | Velocity doesn't separate groups |
| 5 | Cluster-Based SSL | AMI=0.28 < 0.40 | Spurious features are linear |
| 6 | Adaptive Margin Regularization | Insufficient | Margin doesn't target spurious features |
| 7 | Attribution Divergence | IoU=0.6477 | Groups use SAME input regions |

**Critical Constraints:**
- NO attribution-based methods
- NO velocity/learning-speed detection
- NO SAM/flat-minima interventions
- NO cluster-based diagnostics

### Validated Findings to Preserve

1. **Gradient norm detection works** (AUC=0.914, 8.8x minority/majority ratio)
2. **Encoder representations diverge** (CKA=0.115 between groups)
3. **Linear separability exists** in embeddings
4. **Attribution patterns are SIMILAR** between groups (IoU=0.6477)
5. **20-epoch POC validation** identifies failures early

### Key Reference Papers

1. **Toneva et al. (2018)** - "An Empirical Study of Example Forgetting during Deep Neural Network Learning" (933 citations)
   - Per-sample forgetting tracking; shows samples have distinct learning patterns
   - arXiv: 1812.05159

2. **Li et al. (2025)** - "Delving Into the Training Dynamics for Image Classification"
   - 142-D training dynamics features per sample; reveals predictive information
   
3. **Vita et al. (2024)** - "LTAU-FF: Loss Trajectory Analysis for Uncertainty"
   - Loss trajectory methodology; 2-3 orders of magnitude faster than ensembles
   - arXiv: 2402.00853

4. **Chen et al. (2025)** - "Evaluating the Dynamics of Membership Privacy in Deep Learning"
   - Privacy risk determined early in training; early-epoch signals exist

### Implementation Resources

- **mtoneva/example_forgetting** (180 stars) - Per-sample tracking infrastructure
- **deep_feature_reweighting** (110 stars) - Waterbirds/CelebA benchmarks
- **PyTorch `reduction='none'`** - Per-sample loss computation

### MANDATORY FEASIBILITY CONSTRAINTS (Pipeline-Enforced)

- Must use EXISTING real datasets and benchmarks (Waterbirds, CelebA)
- NO new benchmarks, rubrics, or scoring frameworks
- NO synthetic/generated data
- NO human evaluation or subjective scoring
- Hypotheses must be testable IMMEDIATELY with existing resources

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting opportunity we have here! After seven failed attempts, we're finally looking at something *fundamentally different* - the temporal dimension of learning. Let me paint a picture of why this could be transformative.

Consider this: All previous approaches treated spurious correlation as a *static* phenomenon - analyzing gradients at epoch T, attributions post-training, clusters at a snapshot. But spurious correlations are *learned* over time. They emerge through a dynamic process. What if the key to detection lies not in WHAT the model knows, but in HOW it came to know it?

Here's my creative framing: Think of loss trajectories as "learning fingerprints." Just as a forged signature might look correct at the end but reveal telltale hesitations in the stroke dynamics, minority samples might show distinctive "learning hesitations" in their loss curves - perhaps slower initial descent, higher variance, or delayed convergence.

Three unconventional angles I'd like to explore:

1. **The "Learning Resistance" Hypothesis**: Minority samples (waterbird-on-land) may exhibit *higher loss variance* early in training because the model struggles to reconcile conflicting signals (bird features vs. unexpected background). This isn't about where it looks (attribution similarity shows that's not the issue), but about the *difficulty* of processing what it sees.

2. **Temporal Divergence Before Accuracy Gap**: Chen et al. (2025) showed privacy risks are "determined early." What if trajectory divergence is similarly early? If minority trajectories diverge at epoch 3-5, but accuracy gaps emerge at epoch 10-15, we have a *predictive window* for intervention.

3. **Cross-Domain Signal**: Toneva's forgetting events + Li's 142-D features suggest per-sample dynamics are highly informative. But no one has asked: do these dynamics *systematically differ* between spurious correlation groups?

**Key Points:**
- Loss trajectories capture the *temporal process* of learning, not static snapshots
- High loss variance in early epochs could signal "learning difficulty" for minority samples
- The 20-epoch POC validation framework gives us a perfect testbed for trajectory analysis

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, the temporal framing is promising—but promise is not proof. The evidence suggests that if minority samples exhibit distinct "learning fingerprints," we must define these fingerprints in quantitatively falsifiable terms. For example, your *Learning Resistance Hypothesis* must specify measurable statistics: early-epoch loss mean, variance, slope of descent, or time-to-ε-convergence. What exact threshold separates minority from majority trajectories? Without such operationalization, any observed difference risks post hoc interpretation.

Let us formalize a testable prediction. Suppose we define, for each sample \(i\), (1) initial loss \(L_i^{(1)}\), (2) early slope \(s_i = \frac{L_i^{(5)} - L_i^{(1)}}{4}\), (3) variance over epochs 1–5, and (4) time to reach 95% of its minimum loss. The hypothesis predicts that minority samples (waterbird-on-land) will show significantly higher early variance and slower early slope than majority samples. The critical test: can a simple classifier trained *only on epochs 1–5 trajectory features* predict minority membership above chance (e.g., AUROC > 0.7)? If not, the "fingerprint" is too weak to be practically separable. What would disprove the hypothesis? If trajectory-based classification performs no better than random labeling under controlled splits, the temporal signal lacks discriminative power.

Your second proposal—temporal divergence preceding accuracy gaps—is particularly amenable to rigorous testing. We can compute distributional divergence (e.g., Wasserstein distance) between majority and minority trajectory feature distributions at each epoch. The hypothesis predicts significant divergence at epochs 3–5, before group accuracy gaps manifest. The falsifier is straightforward: if divergence only appears *after* accuracy gaps emerge, then trajectories are descriptive rather than predictive. To avoid circularity, group labels must not be used during trajectory extraction; otherwise, we risk encoding known structure into the features.

Now, we must address confounds. Minority samples may differ not because of spurious correlation, but because they are inherently harder or noisier. To control this, we need a synthetic benchmark where spurious correlation strength is manipulated while intrinsic sample difficulty is held constant. For instance, create a dataset with identical object features but systematically flipped backgrounds at controlled ratios (e.g., 95/5, 80/20, 60/40). The evidence would suggest a causal role for spurious correlation only if trajectory separability scales monotonically with spurious strength. If separability persists even when correlation is removed, we are measuring generic hardness, not spurious learning dynamics.

Finally, we must consider edge cases. What if strong regularization (e.g., mixup, weight decay) smooths early loss dynamics? What if curriculum learning alters convergence timing? A robust hypothesis should predict whether trajectory separability survives such interventions. If the signal vanishes under minor training modifications, it is fragile and unlikely to generalize.

I am cautiously receptive. But I will be satisfied only when we specify: (1) precise trajectory features, (2) predictive thresholds, (3) falsifiable divergence timing, and (4) controlled manipulation of spurious strength. Design the experiment to fail—then we will know whether the signal is real.

**Key Points:**
- Define trajectory "fingerprints" with precise, measurable statistics and AUROC-based separability criteria.
- Test whether temporal divergence precedes accuracy gaps using distributional distance metrics and early-epoch prediction.
- Control for intrinsic difficulty via synthetic manipulation of spurious correlation strength to establish causal validity.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here about what we can actually accomplish. Prof. Vera raises excellent methodological points, but I need to flag some feasibility considerations - and importantly, separate what's *technically sound* from what's *practically achievable* given our pipeline constraints.

**On the synthetic benchmark suggestion:** Prof. Vera proposes creating datasets with controlled spurious correlation ratios. While scientifically elegant, this *directly violates* our pipeline-enforced constraints: "NO synthetic/generated data." We must work with existing benchmarks - Waterbirds and CelebA. The good news? These already provide natural variation: Waterbirds has 95%/5% spurious correlation, and we can compare trajectory patterns across the four groups (landbird-land, landbird-water, waterbird-land, waterbird-water). This gives us implicit control without synthetic generation.

**Technical feasibility of trajectory extraction:** This is where I'm optimistic. The measurement approach is theoretically valid:

1. **Per-sample loss logging:** Trivial in PyTorch - `F.cross_entropy(logits, targets, reduction='none')` returns per-sample losses. We already have validated training infrastructure from 7 previous runs.

2. **Trajectory feature computation:** The four features Prof. Vera specifies (initial loss, early slope, variance, time-to-convergence) are simple statistics computable post-hoc from stored loss arrays. No exotic computation required.

3. **Classification pipeline:** Logistic regression or Random Forest on 4-D features is a solved problem. The 20-epoch POC framework means we can validate within hours, not days.

**What worries me technically:**

1. **Batch stochasticity:** Per-sample losses vary based on batch composition and data augmentation. We need deterministic evaluation passes (no augmentation, fixed batch order) to get clean trajectories. This is implementable but requires careful setup.

2. **Memory overhead:** Storing per-sample losses for all ~5,000 Waterbirds samples across 20 epochs = ~100K floats = trivial (~400KB). No memory barrier here.

3. **The gradient norm baseline:** We already know gradient norms achieve AUC=0.914 for minority detection. This is our comparison bar. If trajectory features can't match this, the approach adds complexity without benefit. However, trajectories might *complement* gradient norms - they're not mutually exclusive.

**On the confound concern:** I agree we can't fully isolate spurious correlation from intrinsic difficulty. But here's the key: our validated finding shows attribution patterns are *similar* (IoU=0.6477) between groups. If samples were just "harder," we'd expect different attention regions. The similarity suggests the model *tries* to use the same features but *struggles* with minority backgrounds. Loss trajectory divergence could capture this struggle directly.

**Fundamental barriers? None I can identify.** The mechanism is physically/mathematically possible: loss is a continuous signal, it varies per sample, and it can diverge between groups. The measurement is theoretically valid. The only question is whether the effect *exists* - and that's what the hypothesis tests.

**Key Points:**
- Synthetic benchmarks violate pipeline constraints; use natural group variation in Waterbirds/CelebA instead
- Per-sample loss tracking is trivially implementable with PyTorch's `reduction='none'`
- Main technical concern: deterministic evaluation passes to avoid stochastic noise in trajectory extraction
- No fundamental barriers identified - implementation is straightforward within existing infrastructure

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally becoming testable. But here's where this breaks down if we're not careful: you're still conflating *minority membership* with *spurious correlation effects*. Those are not identical. In Waterbirds, minority = atypical background. But minority samples could also differ in pose, lighting, species diversity, or annotation noise. If trajectory features separate groups, how do you know you're detecting "spurious learning dynamics" rather than "samples that happen to be rarer and therefore less represented in feature space"? Show me the evidence that trajectory divergence scales with **correlation strength**, not just with group frequency.

Prof. Vera is absolutely right to demand falsifiability. I'll sharpen it further. Your core causal claim seems to be: *early loss dynamics reflect the model's internal conflict between core and spurious features.* If that's true, then I expect a specific pattern:  
1. Early slope difference (epochs 1–5) between majority and minority.  
2. This difference should shrink under spurious-mitigation methods (e.g., group DRO or strong augmentation).  
3. The trajectory-based classifier's AUROC should drop toward 0.5 when trained on a debiased model.  

If AUROC stays high even after spurious mitigation, then you are not measuring spurious conflict—you are measuring intrinsic hardness. That's the critical stress test. What would convince me is a *delta-AUROC* analysis across training regimes: ERM vs. group DRO vs. heavy augmentation. The signal should attenuate when the spurious shortcut is weakened.

Now let's talk about the "temporal divergence before accuracy gap" claim. Be precise. Define the epoch of first statistically significant Wasserstein divergence between group loss distributions. Define the epoch where group accuracy differs by >5%. Your hypothesis requires:  
\[
\text{Epoch}_{divergence} < \text{Epoch}_{accuracy\ gap}
\]  
If divergence appears only after the accuracy gap, you are observing consequence, not cause. And don't cherry-pick epochs. Pre-register the window (e.g., 1–5) before looking at results. Otherwise this becomes a fishing expedition.

Another unstated assumption: that per-sample loss reflects "feature conflict." Why would it? Cross-entropy loss is a scalar proxy for prediction error, not internal representation alignment. Two samples can have identical losses but entirely different gradient directions. If your mechanism is conflict between core and spurious cues, then gradient alignment across epochs may be a more faithful signal than loss alone. Have you considered tracking cosine similarity of per-sample gradients over time? If loss trajectories work but gradient-direction trajectories don't, that weakens your mechanistic story.

Finally, Prof. Pax notes gradient norms already give AUC = 0.914. That's a very high bar. If trajectory features alone yield AUROC 0.65, this is incremental at best. The real question is: **Do trajectories add orthogonal information?** Train a classifier on gradient norm alone, then on trajectory features alone, then combined. If combined AUROC does not significantly exceed 0.914, the added complexity is unjustified. What would convince me is a statistically significant improvement (e.g., DeLong test) showing complementary signal.

You're close to something interesting. But until you isolate spurious strength effects, demonstrate attenuation under debiasing, pre-register divergence timing, and prove additive value beyond gradient norms, this remains a correlation story dressed up as causality.

**Key Points:**
- Separate minority membership from true spurious-correlation effects; test signal attenuation under debiasing methods.
- Pre-register and falsify the "early divergence precedes accuracy gap" claim with strict temporal criteria.
- Demonstrate additive value beyond strong baselines (AUC=0.914 gradient norms) to justify trajectory complexity.

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex, your challenges are valid and constructive - let me address them systematically while strengthening our hypothesis. YES, AND we can actually use your stress tests to make this hypothesis more robust.

**On separating minority membership from spurious correlation:**

You're right that we need to distinguish "rare samples" from "spuriously-correlated samples." Here's how we address this within pipeline constraints:

The **key insight** is Waterbirds' group structure. We have four groups:
- Group 0: Landbird-Land (majority, 73%)
- Group 1: Landbird-Water (minority, 5%)
- Group 2: Waterbird-Land (minority, 5%)
- Group 3: Waterbird-Water (majority, 18%)

If trajectory divergence were merely about *rarity*, then Groups 1 and 2 (both 5%) should show identical trajectory patterns. But if it's about *spurious conflict*, they should differ: Group 2 (waterbird-on-land) conflicts more because "water" is the spurious cue for waterbirds, while Group 1's conflict is different. **Prediction:** Trajectory features should show *asymmetric* patterns between minority groups, not symmetric patterns.

**On the delta-AUROC stress test:**

This is a brilliant refinement, and we can actually implement it. Our approach:
1. Train ERM model → extract trajectory features → compute AUROC for minority prediction
2. Train with strong augmentation (RandAugment/AugMax) → extract trajectories → compute AUROC
3. If AUROC_ERM >> AUROC_augmented, the signal is spurious-specific, not intrinsic hardness

However, I want to refine the expectation: AUROC shouldn't drop to *0.5* under debiasing - that would mean perfect removal of group information. A more realistic prediction: AUROC should drop by >0.1 (e.g., 0.75 → 0.65) under augmentation, showing partial attenuation.

**On temporal divergence pre-registration:**

Agreed completely. Let me propose the specific protocol:

1. **Pre-registered window:** Epochs 1-5 for divergence detection
2. **Divergence metric:** Wasserstein-1 distance between minority and majority loss distributions at each epoch
3. **Significance threshold:** p < 0.05 via permutation test (1000 permutations)
4. **Accuracy gap definition:** Epoch where WGA drops >5% below overall accuracy
5. **Success criterion:** Epoch_first_significant_divergence < Epoch_accuracy_gap

This makes the timing claim falsifiable. If divergence emerges only at epoch 8+ while accuracy gaps appear at epoch 6, hypothesis fails.

**On gradient norms as baseline:**

Prof. Rex, you make an excellent point. Let me reframe our value proposition:

Gradient norms (AUC=0.914) are measured at a *single epoch*. Trajectories capture *temporal evolution*. These are complementary, not competing signals. Our refined hypothesis:

**H-E1 (Existence):** Trajectory features alone achieve AUC > 0.75 for minority prediction
**H-E1-additive:** Combined (gradient norm + trajectory features) achieves AUC > 0.93 (statistically significant improvement via DeLong test)

If trajectories alone achieve 0.75 but add nothing to gradient norms, we've still validated that temporal information exists - even if it's redundant with instantaneous gradients. That's still scientifically valuable.

**On the mechanistic concern (loss vs. gradient direction):**

Valid point. Loss is a scalar; gradient direction is richer. However, for an *existence hypothesis*, we start simple. If loss trajectories don't work, gradient trajectories won't be easier. If loss trajectories DO work, we can explore gradient-based extensions in future work. This is the minimal viable hypothesis.

**Key Points:**
- Use asymmetric patterns between minority Groups 1 and 2 to separate rarity from spurious conflict
- Implement delta-AUROC stress test: ERM vs. augmented models to verify spurious-specificity
- Pre-register epochs 1-5 divergence window with explicit Wasserstein distance and p < 0.05 threshold
- Frame trajectory value as complementary to gradient norms, with additive AUROC as secondary test

---

### Exchange 6

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not merely whether trajectory features can predict minority membership—but what their existence would mean for the field. If early loss dynamics systematically encode spurious-feature conflict, then we are no longer diagnosing bias *post hoc* through accuracy gaps or attribution maps; we are observing it *during formation*. This matters because it shifts bias analysis from an outcome-level phenomenon to a dynamical systems property of training. That is a conceptual advance—if, and only if, it survives the stress tests Prof. Rex and Prof. Vera have articulated.

Right now, the novelty hinges on one distinction: are trajectories simply another proxy for sample hardness, or are they a window into shortcut learning dynamics? The asymmetric minority-group prediction that Dr. Ally proposes is promising. If Groups 1 and 2 (both 5%) diverge differently despite identical frequency, that weakens the "rarity" explanation. But the more decisive experiment, in my view, is the delta-AUROC across training regimes. If trajectory separability attenuates under GroupDRO or strong augmentation while intrinsic difficulty remains constant, then we have evidence that trajectories reflect *shortcut reliance*. If it does not attenuate, the hypothesis collapses into a rebranding of difficulty estimation. The field does not need another hardness metric—it needs mechanistic clarity about bias formation.

The temporal precedence claim is where true impact lies. If you can pre-register that Wasserstein divergence in epochs 1–5 reliably precedes a ≥5% worst-group accuracy gap, you are making a strong causal-temporal statement: early optimization dynamics forecast downstream inequity. This matters because it opens a new research direction—*early-warning diagnostics for bias*. Imagine adaptive training procedures that monitor divergence in real time and intervene before gaps solidify. That would meaningfully advance robustness research beyond static evaluation benchmarks.

However, impact will ultimately be judged relative to the gradient norm baseline (AUC = 0.914). If trajectory features merely reach 0.75 and add nothing beyond gradient norms, the contribution is incremental. But if (1) they provide additive predictive value, and (2) they uniquely exhibit temporal precedence before accuracy gaps, then you have identified a qualitatively new signal: temporal structure, not just magnitude. The community should care because nearly all current bias metrics are static snapshots. Demonstrating that bias has a measurable *developmental signature* during training reframes the problem.

Finally, consider how you will position this. The contribution is not "loss trajectories can classify minority samples." That is an empirical finding. The contribution is: *Spurious correlation leaves an early, measurable dynamical fingerprint in optimization trajectories that precedes and predicts downstream performance disparities.* That is a claim about learning theory, not just dataset behavior. But it must be earned with pre-registered criteria, attenuation under debiasing, and additive value over strong baselines. Without those, it remains correlation. With them, it opens a new line of inquiry into training-time fairness diagnostics.

**Key Points:**
- The true contribution is reframing bias as a dynamical property of training, not a post hoc accuracy artifact.
- Attenuation under debiasing and temporal precedence before accuracy gaps are the decisive falsification tests.
- Impact depends on demonstrating additive and conceptually distinct value beyond strong baselines like gradient norms.

---

### Exchange 7

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests we're converging on a well-structured hypothesis. Let me consolidate the testable framework that has emerged from this discussion and identify what remains to be specified.

**Consolidated Hypothesis Structure:**

We now have a multi-level hypothesis with clear falsification criteria:

**H-E1 (Existence - Primary):** Per-sample loss trajectories exhibit statistically significant divergence between minority and majority groups, measurable as trajectory-feature-based classification achieving AUROC > 0.75.

- **Trajectory features:** Initial loss L₁, early slope (L₅-L₁)/4, variance epochs 1-5, time-to-95%-convergence
- **Classifier:** Logistic regression or Random Forest
- **Falsifier:** AUROC ≤ 0.75 or not significantly different from 0.5 (p > 0.05)

**H-M1 (Mechanism):** Trajectory divergence reflects spurious-feature conflict, not intrinsic sample difficulty.

- **Test:** Delta-AUROC analysis: AUROC_ERM - AUROC_augmented > 0.1
- **Falsifier:** AUROC remains constant under augmentation/debiasing (Δ < 0.05)
- **Additional test:** Asymmetric patterns between Groups 1 and 2 (both 5% but different spurious conflicts)

**H-M2 (Temporal Precedence):** Trajectory divergence precedes accuracy gap emergence.

- **Pre-registered window:** Epochs 1-5 for divergence detection
- **Metric:** Wasserstein-1 distance, p < 0.05 via 1000-permutation test
- **Success criterion:** Epoch_first_significant_divergence < Epoch_accuracy_gap
- **Falsifier:** Divergence emerges only after accuracy gap (descriptive, not predictive)

**What would disprove the entire research direction?**

If H-E1 fails (AUROC ≤ 0.75), the trajectory signal is too weak to be useful. If H-E1 passes but H-M1 fails (no attenuation under debiasing), we've measured hardness, not spurious dynamics. If both pass but H-M2 fails (divergence follows accuracy gaps), trajectories are consequences, not early-warning signals.

**Remaining methodological specifications:**

1. **Deterministic evaluation:** Per-sample losses must be computed without data augmentation, with fixed batch ordering. This requires a separate evaluation pass each epoch.

2. **Cross-validation:** 5-fold stratified CV for AUROC estimation, ensuring minority samples are proportionally represented in each fold.

3. **Statistical testing:** Bootstrap confidence intervals for AUROC, permutation tests for divergence timing, DeLong test for comparing AUROCs between models.

4. **Baseline comparison:** Gradient norms at epoch T (existing AUC=0.914) as primary baseline. Combined model (gradient norm + trajectory features) to test additive value.

**What I need before endorsing this hypothesis as ready for Phase 2B:**

The experimental protocol is nearly complete. The key remaining question: what is the specific **epoch T** for gradient norm baseline comparison? If we compare trajectory features (epochs 1-5) against gradient norms at epoch 20, we're not comparing fairly. The comparison should use gradient norms from the same early window (epochs 1-5) to test whether trajectory *shape* adds information beyond instantaneous gradient *magnitude*.

**Key Points:**
- Three-level hypothesis structure (Existence → Mechanism → Temporal) with explicit falsification criteria at each level
- Methodological requirements: deterministic evaluation, stratified CV, appropriate statistical tests
- Fair baseline comparison requires using gradient norms from the same early-epoch window as trajectory features

---

### Exchange 8

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Nothing proposed so far violates physics or learning theory. Tracking per-sample loss across epochs is mathematically well-defined, and Wasserstein distances between empirical distributions are valid statistical objects. So at a basic level: yes, this mechanism is *possible*. But possibility isn't the bar — we need to ask whether the signal you're attributing to "spurious-feature conflict" can, in principle, be distinguished from generic optimization dynamics.

Here's what worries me: early loss divergence can arise purely from class-conditional margin differences under standard gradient descent. In overparameterized networks, samples that align with dominant feature directions will see faster margin growth. Minority samples that require alternative features will lag. That does not require "internal conflict" — it follows from anisotropic feature learning dynamics. In linearized NTK regimes, you can analytically show that convergence rates differ by alignment with top eigenfunctions of the kernel. So early divergence is not automatically evidence of spurious shortcuts; it could simply reflect spectral bias. The mechanism you're proposing must produce a *distinctive temporal signature* beyond what spectral bias predicts.

The attenuation test under GroupDRO or augmentation is therefore critical — and feasible. In principle, if GroupDRO equalizes gradient contributions across groups, then convergence rates in function space should equalize as well. If your divergence persists under strict group reweighting, then it cannot be attributed to shortcut dominance; it becomes a property of intrinsic separability. That's a clean mechanistic discriminator. But I'll add a refinement: don't just measure AUROC. Measure the *difference in early-epoch loss curvature* (second finite difference across epochs 1–5). Shortcut reliance should produce rapid early curvature for majority-aligned samples (fast initial descent, then plateau), whereas intrinsic hardness should produce uniformly slow descent. That curvature contrast is a stronger dynamical claim than slope alone.

On the temporal precedence claim: the inequality  
\[
\text{Epoch}_{divergence} < \text{Epoch}_{accuracy\ gap}
\]  
is testable and theoretically coherent. But be careful — accuracy is a thresholded statistic. Loss divergence can precede accuracy gaps purely because accuracy is piecewise constant. So precedence alone is not causal evidence. A stronger condition would be: divergence predicts the *future magnitude* of worst-group accuracy drop (e.g., regression of WGA at epoch 20 on Wasserstein distance at epoch 3). If early divergence explains significant variance in later disparity across random seeds, that's much harder to dismiss as threshold artifact.

Now regarding gradient norms (AUC = 0.914). Mechanistically, gradient norm is proportional to loss × local curvature. Trajectory features are temporally aggregated versions of related information. So in principle, redundancy is expected. The only way trajectories add orthogonal information is if *temporal ordering* encodes something static magnitudes cannot — e.g., oscillation, delayed descent, or curvature differences. If combined AUROC does not exceed the gradient baseline significantly, that's not a budget problem — it means the mechanism collapses to magnitude-based hardness. Perfectly acceptable scientifically, but it limits the theoretical claim.

Bottom line: nothing here is impossible. But the spurious-conflict story must survive three mechanistic alternatives — spectral bias, margin dynamics, and threshold artifacts in accuracy. If your signal attenuates under group reweighting, exhibits distinctive curvature patterns, and predicts future disparity across seeds, then I'll say: okay, this could work.

**Key Points:**
- Early loss divergence can arise from spectral bias and margin dynamics; spurious-conflict must show a distinct temporal signature.
- Attenuation under GroupDRO and analysis of early loss curvature provide mechanistic discrimination beyond slope or AUROC alone.
- Temporal precedence over accuracy gaps is insufficient; early divergence must predict future disparity magnitude to support causal interpretation.

---

### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something! Prof. Pax, your challenge about spectral bias and margin dynamics is exactly the kind of mechanistic scrutiny we need. Let me reframe what makes this hypothesis *genuinely novel* rather than just another optimization dynamics observation.

**The key insight we've been circling around:**

Here's what distinguishes "spurious conflict" from generic spectral bias: *symmetry breaking between minority groups*.

In pure spectral bias, samples that are "hard" should be uniformly hard across class labels. If minority samples (Groups 1 and 2, both 5%) simply require less-represented features, they should show *similar* trajectory patterns regardless of which class they belong to. But if spurious correlation is the driver, we expect *asymmetry*:

- **Group 2 (waterbird-on-land):** The model learns "water → waterbird" as a shortcut. When water is absent, it faces *conflict* between the learned shortcut and the actual bird features.
- **Group 1 (landbird-on-water):** The model learns "land → landbird" as a shortcut. When land is absent, it faces a different but analogous conflict.

The *direction* of conflict differs between these groups. Spectral bias predicts symmetric slowdown. Spurious-conflict predicts asymmetric signatures depending on which shortcut is violated.

**A creative test I hadn't thought of before:**

What if we compute *cross-group trajectory similarity*? Specifically:
- Compute average trajectory (loss curve) for each of the 4 groups
- Measure trajectory correlation: Is Group 2's trajectory more similar to Group 0 (same class, different background) or Group 3 (different class, same background)?

If trajectories cluster by *spurious attribute* (background) rather than by *class label*, that's strong evidence for spurious-conflict dynamics. If they cluster by class label, it's just class-conditional learning difficulty.

**Integrating Prof. Pax's curvature suggestion:**

The second finite difference (curvature) is brilliant. Here's how it fits:
- **Shortcut-aligned majority samples:** Fast initial descent (high negative slope), then plateau (curvature shifts from negative to near-zero)
- **Spurious-conflict minority samples:** Slower initial descent (lower negative slope), sustained descent (curvature stays negative longer)

This predicts a *temporal pattern*, not just a magnitude difference. Majority samples should show earlier curvature sign change (epoch 3-5) while minority samples show later sign change (epoch 7-10). That's a qualitatively different signature than spectral bias alone.

**On the predictive power test:**

Prof. Pax's suggestion to regress WGA at epoch 20 on Wasserstein distance at epoch 3 is excellent. But let me extend it: we should do this *across multiple random seeds* (say, 10 runs). If early divergence at epoch 3 predicts the variance in final WGA across seeds (R² > 0.5), that's causal evidence that's hard to dismiss. The seeds control for all fixed factors; only stochasticity in early learning differs.

**What's genuinely new here:**

1. **Temporal dynamics of bias formation** — no existing work characterizes when spurious reliance crystallizes during training
2. **Asymmetric signature prediction** — testable distinction from generic spectral bias
3. **Cross-seed predictive power** — goes beyond correlation to near-causal evidence
4. **Curvature-based temporal patterns** — qualitatively distinct from magnitude-only signals

Imagine this: we discover that by epoch 3-5, we can predict which runs will have severe WGA gaps at epoch 20. That's an *early warning system* for spurious correlation — something the field doesn't have today.

**Key Points:**
- Asymmetric trajectory patterns between Groups 1 and 2 distinguish spurious-conflict from generic spectral bias
- Cross-group trajectory clustering (by background vs. by class) provides direct evidence for spurious-feature influence
- Curvature sign-change timing offers a qualitative temporal signature beyond magnitude
- Cross-seed prediction of final WGA from early divergence provides near-causal evidence

---

### Exchange 10

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally getting interesting. But here's where this still breaks down unless you tighten it further.

First, the **symmetry-breaking argument** Dr. Nova proposes is promising—but right now it's hand-wavy. You're claiming spectral bias predicts symmetric slowdown across minority groups, while spurious-conflict predicts asymmetric signatures. Show me the formal prediction. In a linearized NTK regime with imbalanced feature alignment, what exactly would the expected loss curves look like for Groups 1 and 2? If both groups are equally misaligned with top eigenfunctions, spectral bias *can* produce asymmetric effects depending on feature-class correlations. So unless you specify what "symmetric" means quantitatively (e.g., difference in early curvature between Groups 1 and 2 ≤ ε under spectral-only simulations), reviewers will say this is post hoc storytelling.

Second, the **trajectory clustering test** (cluster by background vs. class) is clever—but be careful. Loss is computed with respect to the *class label*. So trajectories will mechanically reflect class-conditional error signals. If Group 2 clusters with Group 0 (same class), that might simply mean the classifier is optimizing correctly. What would convince me is this: compute trajectories in a representation space where the background feature is partially disentangled (e.g., via a linear probe predicting background from penultimate features). Then test whether trajectory similarity aligns more with background separability than class separability. Without that, clustering risks being a circular diagnostic.

Third, on **curvature and temporal signatures**—this is the strongest mechanistic angle so far. But you need a crisp, falsifiable prediction. For example:

- Let κᵢ = mean second finite difference over epochs 1–5.
- Prediction: κ_majority < 0 and sign(κ_majority) flips by epoch ≤ 5.
- Prediction: κ_minority remains < 0 through epoch ≥ 8.

If that timing gap disappears under GroupDRO, you've got a mechanistic discriminator. If curvature timing is identical across regimes, your "conflict" narrative collapses into generic convergence dynamics. Don't just measure curvature—pre-register the timing inequality.

Now let's talk about the cross-seed predictive claim. I like it. But here's the hard question: what's the unit of analysis? You're proposing R² > 0.5 when regressing WGA₍₂₀₎ on W₁-distance₍epoch3₎ across seeds. Fine. But if variance in WGA across seeds is small (say ±1%), even high R² is trivial. What would convince me is *effect size*: a 1 SD increase in early divergence predicts ≥3% absolute drop in final WGA. That's operationally meaningful. Otherwise, you're predicting noise.

And finally—the gradient norm baseline. Vera is absolutely right: if gradient norms at epochs 1–5 already give AUC ≈ 0.9, trajectories must demonstrate **incremental value under controlled feature ablation**. Here's a clean test:  
1. Train classifier on early gradient norms only.  
2. Train on trajectory-shape features only (normalized to remove magnitude).  
3. Train on both.  

If (3) significantly outperforms (1) via DeLong test (p < 0.01), then temporal ordering adds orthogonal information. If not, this is repackaged magnitude.

You are very close to a defensible mechanistic story. But right now, several of your "distinguishers" are qualitative. Tighten them into inequalities, timing thresholds, and effect-size commitments. What would convince me is this: (1) asymmetric curvature timing across minority groups inconsistent with spectral simulations, (2) attenuation under GroupDRO, and (3) early divergence predicting practically meaningful WGA variance across seeds. Do that, and I'll say you've isolated something real.

**Key Points:**
- Formalize symmetry-breaking predictions; define quantitative expectations under spectral bias to avoid post hoc interpretation.
- Pre-register curvature timing inequalities and test attenuation under GroupDRO as a mechanistic discriminator.
- Demonstrate additive value beyond gradient norms and require practically meaningful cross-seed effect sizes, not just statistical significance.

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex, your challenges are exactly what we need to make this hypothesis bulletproof. Let me synthesize our discussion into a tightened, falsifiable framework that addresses every concern raised.

**Consolidated Hypothesis with Quantitative Commitments:**

**H-E1: Loss Trajectory Divergence Existence**
- **Core claim:** Trajectory features predict minority group membership with AUROC > 0.75
- **Features:** L₁ (initial loss), slope (L₅-L₁)/4, variance(L₁...L₅), time-to-95%-min
- **Falsifier:** AUROC ≤ 0.75 or p > 0.05 vs. random baseline

**H-M1: Curvature Timing Asymmetry (Mechanism)**
- **Definition:** κᵢ = (Lᵢ₍ₜ₊₁₎ - 2Lᵢ₍ₜ₎ + Lᵢ₍ₜ₋₁₎) averaged over epochs 2-5
- **Pre-registered prediction:**
  - Majority groups: curvature sign flip (κ → 0) by epoch ≤ 5
  - Minority groups: curvature remains negative through epoch ≥ 8
  - **Timing gap:** Δ_epoch(curvature_flip) ≥ 3 epochs between majority and minority
- **Falsifier:** Timing gap < 2 epochs, or gap disappears under GroupDRO

**H-M2: Attenuation Under Debiasing**
- **Test:** Compare AUROC_ERM vs. AUROC_GroupDRO vs. AUROC_Augmented
- **Pre-registered prediction:** AUROC_ERM - AUROC_GroupDRO > 0.10
- **Falsifier:** Δ AUROC < 0.05 (signal persists despite debiasing)

**H-M3: Cross-Seed Predictive Power (Causal Evidence)**
- **Test:** Regress WGA₍epoch20₎ on W₁-distance₍epoch3₎ across 10 random seeds
- **Pre-registered prediction:**
  - R² > 0.5 for the regression
  - **Effect size:** 1 SD increase in early W₁-distance → ≥3% absolute WGA drop
- **Falsifier:** R² < 0.3 or effect size < 2% absolute

**Addressing Prof. Rex's Specific Concerns:**

1. **Symmetry-breaking formalization:**
   Rather than claiming theoretical predictions about NTK regimes (which we can't validate), we make an *empirical* prediction: If Groups 1 and 2 have indistinguishable trajectory distributions (Wasserstein distance between them < ε, with ε = 10% of majority-minority distance), then we cannot claim spurious-specificity. We pre-register: **W₁(Group1, Group2) / W₁(Minority, Majority) > 0.3** as evidence for asymmetric effects.

2. **Trajectory clustering circularity:**
   Acknowledged - the clustering test is secondary evidence, not primary. We focus on the curvature timing and attenuation tests as primary discriminators. If both pass, clustering becomes supporting evidence; if they fail, clustering is irrelevant.

3. **Gradient norm feature ablation:**
   Explicitly added as H-E1-additive:
   - Train on gradient norms only → AUROC_grad
   - Train on normalized trajectory shapes only → AUROC_shape
   - Train on both → AUROC_combined
   - **Pre-register:** AUROC_combined - AUROC_grad > 0.02, DeLong p < 0.01

**Scope Boundaries:**

This hypothesis tests *existence* of trajectory divergence and its basic mechanistic properties. We do NOT claim:
- That trajectory features are better than gradient norms (only that they add orthogonal information)
- That trajectory-based intervention will improve WGA (detection ≠ intervention, per our failure history)
- That this generalizes to all spurious correlation datasets (we test Waterbirds; CelebA is secondary validation)

**What success looks like:**
If H-E1 + H-M1 + H-M2 + H-M3 all pass, we've demonstrated:
1. Trajectory divergence EXISTS and is measurable
2. It reflects SPURIOUS dynamics (not just hardness) via attenuation
3. It has TEMPORAL structure (curvature timing) beyond static magnitude
4. It has CAUSAL relevance (predicts future WGA across seeds)

That's a complete scientific story: existence → mechanism → causation.

**Key Points:**
- All predictions now have quantitative thresholds and pre-registered falsifiers
- Curvature timing gap (≥3 epochs) and attenuation under GroupDRO (Δ > 0.10) are primary mechanistic tests
- Cross-seed effect size (≥3% WGA per SD) ensures practical, not just statistical, significance
- Scope explicitly limited to existence and mechanism; intervention claims deferred

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

This is substantially improved. You now have quantitative thresholds and explicit falsifiers, which is the minimum requirement for scientific credibility. However, several criteria remain vulnerable to hidden confounds. The evidence suggests your framework could be testable, but only if we sharpen the operational definitions and control for optimization-scale artifacts.

First, on **H‑M1 (curvature timing gap ≥ 3 epochs)**. I approve of the inequality structure, but you must define curvature flip operationally. What constitutes "flip to zero"? A sign change at a single epoch is unstable under stochastic noise. I recommend: define flip as the first epoch where the 3-point moving average of κ exceeds −ε for two consecutive epochs, with ε pre-registered (e.g., 0.002 in normalized loss units). Otherwise, your timing gap could be an artifact of minibatch variance. Additionally, losses must be normalized per-sample by initial loss (Lₜ / L₁) to remove magnitude effects; otherwise, curvature differences collapse to scale differences. What would disprove this mechanism? If, after normalization and smoothing, the curvature timing gap falls below 2 epochs in ≥70% of seeds, the temporal-conflict claim fails.

Second, **H‑M2 (attenuation under GroupDRO, ΔAUROC > 0.10)** is directionally correct but insufficiently controlled. GroupDRO changes both gradient weighting and effective learning rate per group. If divergence attenuates, is that because spurious reliance was removed—or because variance in per-sample gradients decreased? You must include a *control reweighting condition* that matches gradient variance without targeting groups (e.g., random balanced weighting). If attenuation occurs only under GroupDRO and not under variance-matched random weighting, then the evidence supports your interpretation. If both attenuate similarly, the mechanism reduces to gradient smoothing, not spurious conflict.

Third, the **cross-seed predictive test (H‑M3)** is the strongest component, but it requires power analysis. Ten seeds may be underpowered if between-seed WGA variance is small. Before running the regression, estimate the standard deviation of WGA across 30 pilot seeds. If σ_WGA < 2%, your ≥3% per SD effect size becomes implausible. I recommend pre-registering both R² > 0.5 and β ≥ 0.5·σ_WGA per SD of early divergence. More importantly: use nested cross-validation across seeds—fit the regression on half the seeds, evaluate predictive error on the held-out half. If predictive RMSE does not outperform a mean-baseline by ≥30%, then early divergence lacks practical forecasting value.

Finally, regarding additive value beyond gradient norms: AUROC differences of 0.02 can be statistically significant yet practically negligible. I suggest adding a calibration-based metric: compare expected calibration error (ECE) or Brier score when predicting minority membership. Temporal features should reduce miscalibration if they encode structure beyond magnitude. If AUROC improves but calibration does not, you are detecting ranking differences without probabilistic refinement—scientifically weaker.

If these controls are implemented and the inequalities hold under normalization, smoothing, variance-matched controls, and cross-seed validation, then I would consider the mechanism provisionally supported. If they fail under any of these stress tests, the hypothesis must be narrowed accordingly.

**Key Points:**
- Define curvature flip with smoothing and normalization; pre-register failure if timing gap collapses under noise control.
- Add variance-matched reweighting control to ensure attenuation is specific to spurious-feature mitigation.
- Require cross-seed predictive validation with effect-size thresholds and out-of-sample forecasting performance.

---

### Exchange 13

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: given the methodological refinements Prof. Vera has outlined, what is the realistic contribution this work can make to the field?

Let me assess the emerging hypothesis against three impact criteria:

**1. Novelty Assessment: STRONG**

The contribution is not "loss trajectories can classify minority samples" — that would be empirical trivia. The contribution is:

*"Spurious correlation leaves an early, measurable dynamical fingerprint in optimization trajectories that (a) precedes accuracy gaps, (b) attenuates under debiasing, and (c) predicts future performance disparities across training runs."*

This is genuinely new. Existing work on:
- **Example forgetting** (Toneva et al.) tracks binary correctness, not continuous loss dynamics
- **Training dynamics** (Li et al.) extracts features but doesn't apply them to spurious correlation
- **Group robustness** literature focuses on post-hoc accuracy metrics, not training-time signals

If the hypothesis survives all pre-registered tests, you've identified a *temporal signature of bias formation* — something the field doesn't currently have.

**2. Significance Assessment: CONDITIONAL**

The significance depends heavily on which sub-hypotheses pass:

| Scenario | Implication | Field Impact |
|----------|-------------|--------------|
| H-E1 passes, H-M1/M2/M3 fail | Trajectories detect minority status, but indistinguishable from hardness | LOW - just another difficulty metric |
| H-E1 + H-M2 pass, H-M3 fails | Trajectories reflect spurious dynamics, but don't predict future outcomes | MEDIUM - diagnostic insight without practical value |
| H-E1 + H-M1 + H-M2 + H-M3 all pass | Complete temporal-causal story | HIGH - opens new research direction |

The full contribution requires passing all tests. But even partial success has value: demonstrating that H-M2 (attenuation) works would already advance understanding of what debiasing methods actually do at the optimization level.

**3. Positioning for Maximum Impact:**

How does this mean for the field? If successful, this work:

1. **Shifts bias analysis from outcomes to dynamics** — instead of measuring WGA post-training, we can monitor divergence during training
2. **Provides an early-warning system** — if early divergence predicts final WGA (H-M3), practitioners can abort/adjust training runs early
3. **Offers mechanistic insight into debiasing** — if GroupDRO attenuates trajectory divergence (H-M2), we understand *why* it works at the optimization level
4. **Connects to broader optimization theory** — the curvature timing analysis (H-M1) links spurious correlation to spectral learning dynamics

**What the community should care about:**

The spurious correlation literature has focused on *what to do about it* (DRO, reweighting, augmentation) without deeply understanding *when and how it forms*. This hypothesis addresses the formation dynamics. Even if intervention remains challenging (our failure history shows detection ≠ intervention), understanding formation timing could enable new intervention strategies we haven't conceived yet.

**My recommendation:**

Proceed with the hypothesis as structured by Dr. Ally (Exchange 11), with Prof. Vera's refinements (Exchange 12). The scope is appropriately limited (existence + mechanism, not intervention). The falsification criteria are rigorous. The potential contribution is significant *if* the hypothesis survives stress tests.

If I were reviewing this as a paper submission, I would want to see: (1) pre-registration of all thresholds, (2) the variance-matched control condition, and (3) honest reporting if any sub-hypothesis fails. Partial results are scientifically valuable if interpreted correctly.

**Key Points:**
- Novelty is strong: first temporal characterization of spurious correlation formation dynamics
- Significance is conditional on passing the full hypothesis chain (H-E1 → H-M1 → H-M2 → H-M3)
- Position as "understanding bias formation" rather than "detecting minority samples" for maximum field impact
- Even partial success (e.g., H-M2 alone) provides mechanistic insight into debiasing methods

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here: the proposal is now scientifically testable. The inequalities are explicit, the falsifiers are stated, and—importantly—you've separated existence (H‑E1) from mechanism (H‑M1/M2) and causality (H‑M3). That's good structure. The remaining question is not "is this interesting?" but "can these quantities actually isolate a distinct mechanism in principle?"

On **H‑M1 (curvature timing gap)**: in principle, this is mechanically plausible. If majority samples align with top eigendirections of the Hessian (spectral bias story), they should enter the quadratic basin earlier, yielding earlier curvature flattening. If minority samples are governed by conflicting feature gradients, their effective Hessian along the optimization path can remain anisotropic longer, delaying curvature stabilization. That mechanism is mathematically coherent. But here's what worries me: curvature timing may be dominated by *loss scale and local Lipschitz variation*, not feature conflict. Vera's normalization (Lₜ / L₁) is necessary, but I would go further—compute curvature in log-loss space or on standardized residuals. If the ≥3 epoch timing gap survives normalization across ≥70% of seeds, then yes, this is consistent with a real dynamical separation. If it collapses, the mechanism reduces to scale heterogeneity.

On **H‑M2 (attenuation under GroupDRO)**: this is where feasibility becomes subtle. In principle, if divergence is caused by spurious-gradient alignment, reweighting minority groups should alter the effective gradient field and reduce trajectory separation. That's physically coherent. But Vera is right: any method that reduces gradient variance could attenuate divergence. So the variance-matched control is not optional—it's logically required. Without it, attenuation is not diagnostic. If GroupDRO uniquely reduces AUROC by >0.10 relative to both ERM and variance-matched random weighting, then the mechanism "spurious-feature conflict" remains viable. If all variance-reduction methods attenuate equally, then the phenomenon is generic optimization smoothing, not bias formation.

Now the hardest piece: **H‑M3 (cross-seed predictive power)**. In principle, early trajectory divergence *can* causally predict final WGA if early representation learning locks the model into a basin favoring spurious features. That is theoretically sound—early gradient steps disproportionately shape feature hierarchy. But the feasibility depends on variance magnitude. If WGA variance across seeds is tiny, no early signal can predict large downstream differences. So before committing to R² > 0.5, you must empirically verify that between-seed WGA variance is nontrivial (≥3–4%). Otherwise, the regression target lacks dynamic range. Also, the nested cross-seed validation Vera proposes is essential: without out-of-sample forecasting, you're fitting noise in a small sample of seeds.

Finally, I want to flag a conceptual boundary. Even if all hypotheses pass, you will have shown that early optimization dynamics encode future disparity—not that the divergence is uniquely attributable to "spuriousness" as opposed to structured hardness correlated with background. Mechanistically, those can look similar in gradient space. The attenuation + variance-matched control narrows this gap, but it doesn't mathematically prove feature causality. So interpret results as "optimization-mediated group divergence consistent with spurious-feature conflict," not definitive causal attribution. That keeps the claims aligned with what the measurements can actually support.

If the inequalities hold under normalization, smoothing, variance controls, and out-of-sample seed prediction, then yes—this could work. The mechanisms are physically plausible. The measurements are mathematically well-defined. The remaining risk is not impossibility, but overinterpretation.

**Key Points:**
- Curvature timing gaps are mechanically plausible but must survive strict normalization and smoothing to avoid scale artifacts.
- Attenuation under GroupDRO is only diagnostic if variance-matched controls fail to replicate the effect.
- Cross-seed prediction is theoretically sound but only feasible if WGA variance is sufficiently large and validated out-of-sample.

---

### Exchange 15

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now you've addressed my concerns. Let me summarize what would convince me this hypothesis is ready for execution:

**Final Checklist — What I Need Before Endorsement:**

✅ **H-E1 (Existence):** Clear. AUROC > 0.75 for trajectory features predicting minority membership. Falsifier is explicit.

✅ **H-M1 (Curvature Timing):** Now adequately specified with:
- Normalized loss (Lₜ/L₁) to remove scale effects
- 3-point moving average smoothing to handle stochasticity
- Curvature flip defined as κ > -0.002 for 2 consecutive epochs
- Timing gap ≥ 3 epochs between majority and minority
- Failure criterion: gap < 2 epochs in ≥70% of seeds

✅ **H-M2 (Attenuation):** Strengthened with variance-matched control:
- AUROC_ERM - AUROC_GroupDRO > 0.10
- AUROC_ERM - AUROC_RandomReweight < 0.05 (control must NOT attenuate)
- If both attenuate similarly, mechanism collapses to gradient smoothing

✅ **H-M3 (Cross-Seed Prediction):** Strengthened with:
- Pre-requisite: verify σ_WGA > 3% across pilot seeds
- R² > 0.5 in full regression
- Effect size: β ≥ 0.5·σ_WGA per SD early divergence
- Nested cross-validation: held-out RMSE beats mean baseline by ≥30%

**Remaining Concerns (Acceptable):**

1. **Causal interpretation limits:** Prof. Pax is right — even if all tests pass, we show "optimization-mediated group divergence consistent with spurious-feature conflict," not definitive causality. This is appropriate scientific hedging.

2. **Scope boundaries:** We're testing existence and mechanism, not intervention. Detection ≠ successful intervention (our failure history proves this). The hypothesis is scoped correctly.

3. **Partial results value:** Dr. Sage correctly notes that even partial success (e.g., H-M2 alone) provides insight. This is acceptable — science often proceeds incrementally.

**What would convince me this hypothesis is INVALID:**

1. If H-E1 fails (AUROC ≤ 0.75): trajectory signal too weak, entire approach abandoned
2. If H-M1 fails (timing gap < 2 epochs): temporal structure is noise, not mechanism
3. If H-M2 fails (attenuation matches random reweighting): we're measuring gradient variance, not spurious conflict
4. If H-M3 fails (R² < 0.3 or effect size trivial): early signals don't predict outcomes, no practical value

**My Verdict:**

The hypothesis framework is now rigorous. The falsification criteria are explicit and falsifiable. The scope is appropriately limited. The mechanistic story is coherent (though subject to interpretation limits).

I endorse proceeding to Phase 2B with this hypothesis structure. The primary hypothesis for PoC validation should be **H-E1** — does trajectory divergence exist? Only if H-E1 passes do we invest in the mechanism tests (H-M1, H-M2, H-M3).

**Recommended Execution Order:**
1. **H-E1** first (existence) — if fails, stop
2. **H-M2** second (attenuation) — most diagnostic for spurious-specificity
3. **H-M1** third (curvature timing) — mechanistic depth
4. **H-M3** last (cross-seed prediction) — requires most seeds, highest cost

This ordering minimizes wasted computation if early hypotheses fail.

**Key Points:**
- All sub-hypotheses now have explicit quantitative thresholds and falsification criteria
- Variance-matched control for H-M2 and cross-validation for H-M3 are required
- Execution order: H-E1 → H-M2 → H-M1 → H-M3 (fail-fast strategy)
- Hypothesis is ready for Phase 2B with appropriate scope limitations

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis represents a genuinely novel approach—examining the temporal dynamics of bias formation rather than static post-hoc metrics. No existing work characterizes when spurious correlation crystallizes during training, and the asymmetric trajectory signatures between minority groups offer a testable distinction from generic spectral bias.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis now meets rigorous scientific standards with explicit quantitative thresholds, pre-registered falsification criteria, and controlled experimental designs. The curvature timing definitions with smoothing/normalization, variance-matched controls for attenuation, and nested cross-validation for predictive power ensure the tests can genuinely fail if the mechanism is not real.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG (conditional on passing full chain)
- **Assessment:** If all sub-hypotheses pass, this work reframes bias as a dynamical systems property of training—a conceptual advance that opens new research directions in training-time fairness diagnostics. Even partial success (H-M2 alone) provides mechanistic insight into what debiasing methods actually do at the optimization level.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All proposed measurements are mathematically well-defined and computationally trivial. Per-sample loss tracking uses standard PyTorch functionality, trajectory features are simple statistics, and the 20-epoch POC framework provides validated infrastructure. No fundamental barriers exist—only empirical questions about whether the effects exist.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on a rigorous, multi-level hypothesis framework for **Loss Trajectory Divergence Analysis**:

**Core Claim:** Per-sample loss trajectories exhibit statistically significant divergence between minority and majority groups in spurious correlation settings, and this divergence (a) reflects spurious-feature conflict rather than intrinsic hardness, (b) shows distinctive temporal signatures in curvature dynamics, and (c) predicts future worst-group accuracy disparities across training runs.

**Hypothesis Chain:**
- **H-E1 (Existence):** Trajectory features (initial loss, early slope, variance, time-to-convergence) predict minority membership with AUROC > 0.75
- **H-M1 (Mechanism - Curvature):** Majority samples show curvature sign-flip by epoch ≤5; minority samples maintain negative curvature through epoch ≥8 (timing gap ≥3 epochs)
- **H-M2 (Mechanism - Attenuation):** Trajectory separability attenuates under GroupDRO (ΔAUROC > 0.10) but NOT under variance-matched random reweighting
- **H-M3 (Causation):** Early divergence (epoch 3) predicts final WGA across seeds with R² > 0.5 and effect size ≥3% absolute per SD

**Key Methodological Requirements:**
- Normalized loss (Lₜ/L₁) with 3-point moving average smoothing
- Variance-matched control condition for attenuation test
- Nested cross-validation for cross-seed prediction
- Execution order: H-E1 → H-M2 → H-M1 → H-M3 (fail-fast)

**Scope:** This hypothesis tests existence and mechanism of trajectory divergence. It does NOT claim that trajectory-based detection enables successful intervention (our failure history shows detection ≠ intervention).

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Even if all tests pass, causal attribution to "spurious features" vs. "structured hardness correlated with background" cannot be mathematically proven—only shown to be consistent with the spurious-conflict interpretation.
- **Concern 2:** Cross-seed predictive power (H-M3) depends on between-seed WGA variance being sufficiently large (σ > 3%); if variance is small, the test may be underpowered.
- **Mitigation Strategy:** Report results as "optimization-mediated group divergence consistent with spurious-feature conflict" rather than definitive causal claims. Verify σ_WGA > 3% in pilot runs before committing to H-M3.

---

## Emerged Hypothesis Summary

### Core Statement
Under standard ERM training on spurious correlation benchmarks (Waterbirds), if we track per-sample loss trajectories across epochs, then minority group samples will exhibit statistically distinguishable trajectory patterns (AUROC > 0.75) with delayed curvature stabilization (≥3 epochs later than majority), because the model experiences prolonged optimization conflict when spurious background features contradict learned shortcuts.

### Causal Mechanism
1. **Early training:** Model learns spurious correlations (e.g., "water background → waterbird") as dominant features
2. **Majority samples:** Background aligns with spurious cue → fast loss descent, early curvature stabilization (epoch ≤5)
3. **Minority samples:** Background conflicts with spurious cue → model struggles to reconcile features → slower descent, prolonged negative curvature (through epoch ≥8)
4. **Result:** Trajectory divergence emerges early (epochs 3-5) and predicts final WGA disparity

### Variables
- **Independent Variable:** Group membership (minority vs. majority based on spurious correlation)
- **Dependent Variables:** 
  - Primary: Trajectory-based AUROC for minority prediction
  - Secondary: Curvature timing gap, attenuation under GroupDRO, cross-seed R²
- **Controlled Variables:** Model architecture (ResNet-50), dataset (Waterbirds), training protocol (standard ERM)

### Key Assumptions
- A1: Per-sample loss can be reliably tracked without stochastic noise dominating the signal
- A2: Curvature differences reflect optimization dynamics, not just loss scale
- A3: GroupDRO specifically attenuates spurious reliance, not just gradient variance
- A4: Between-seed WGA variance is sufficient (≥3%) for predictive analysis

### Null Hypothesis
There is no significant difference in loss trajectory characteristics between minority and majority samples; trajectory-based features predict group membership at chance level (AUROC ≈ 0.5).

### Predictions
- P1 (Primary): Trajectory features achieve AUROC > 0.75 for minority prediction
- P2: Curvature timing gap between majority and minority ≥ 3 epochs
- P3: AUROC attenuates by > 0.10 under GroupDRO but < 0.05 under random reweighting
- P4: Early divergence predicts final WGA with R² > 0.5 across seeds

### Novelty
This is the first work to characterize the temporal dynamics of spurious correlation formation during training. While prior work (Toneva et al.) tracks forgetting events and (Li et al.) extracts training dynamics features, no existing work examines trajectory divergence specifically between spurious correlation groups or tests whether such divergence precedes and predicts downstream accuracy disparities.

### Scope & Boundaries
- **Applies to:** Spurious correlation settings where group labels exist, standard ERM training, image classification
- **Does not apply to:** Settings without identifiable spurious attributes, non-vision domains (without validation), intervention design (we test detection only)
- **Known limitations:** Causal interpretation limited to "consistent with" spurious-conflict mechanism

### Experimental Setup
- **Dataset:** Waterbirds (primary), CelebA (secondary validation)
- **Model:** ResNet-50 pretrained on ImageNet
- **Training:** Standard ERM, 20 epochs, with deterministic evaluation passes
- **Baselines:** Gradient norm detection (AUC = 0.914), random baseline

### Related Work & Baselines
- Toneva et al. (2018): Example forgetting — per-sample tracking foundation
- Li et al. (2025): 142-D training dynamics features — multi-dimensional characterization
- GroupDRO: Baseline debiasing method for attenuation test
- Gradient norm detection: Existing method achieving AUC = 0.914

### Phase 2B Readiness Seeds
- SH1 (Existence): Trajectory divergence exists and is measurable
- SH2 (Mechanism): Divergence reflects spurious dynamics, not generic hardness
- SH3 (Comparison): Deferred to Phase 5 baseline comparison

### Established Facts
- Gradient norm detection works for minority detection (AUC = 0.914) — BUILD_ON
- Attribution patterns are similar between groups (IoU = 0.6477) — BUILD_ON (motivates temporal approach)
- Encoder representations diverge (CKA = 0.115) — BUILD_ON
- Detection ≠ successful intervention — BUILD_ON (scope limitation)

