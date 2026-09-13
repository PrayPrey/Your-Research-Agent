# Phase 2A Discussion Log

**Gap:** Gap 1 — SAM and Geometry-Aware Optimization During SSL Pre-Training for Shortcut Reduction
**Gap ID:** gap1
**Priority:** HIGH+PRIMARY
**Date:** 2026-08-21
**Architecture:** Self-Contained Tikitaka Loop (Independent-Controller Ablation)
**Mode:** UNATTENDED

---

## Briefing: Research Context

### Research Question
Can SAM or geometry-aware optimizers reduce shortcut reliance during SSL pre-training (SimCLR/MoCo/DINO) on spurious correlation benchmarks (Waterbirds/CelebA/CMNIST/UrbanCars), without requiring group labels?

### Key Papers Available

**P1 — G2-SAM (Ji et al., 2025):** Group-wise flat minima for supervised worst-group robustness. Supervised-only — SSL gap confirmed. Shows group-wise SAM perturbations outperform standard SAM for worst-group accuracy.

**P2 — Simplicity Bias ↔ SAM (Gatmiry et al., 2024):** Theory proves sharpness minimization → rank-1 features → simplicity bias in 2-layer networks. Suggests SAM may INCREASE simplicity bias (rank-1 → spurious shortcuts), not reduce them. Critical tension.

**P3 — DGSAM (Song et al., 2025):** Per-domain SAM for domain generalization. Identifies "fake flat minima" problem where standard SAM converges to spurious flat regions. Not spurious correlation benchmarks.

**P4 — Cross-Variant SSL (Yadav et al., 2026):** 92.5% Waterbirds with generative SSL augmentation. Best SSL+spurious result. Uses view diversity, not optimizer change.

**P5 — Flat Minima Critique (Schliserman et al., 2025):** SAM can converge to sharp minima in convex settings. Theoretical risk flag.

### Implementation Resources
- davda54/sam (1983★): drop-in SAM/ASAM optimizer for PyTorch
- p-giakoumoglou/pyssl: unified SimCLR/MoCo/DINO interface
- kohpangwei/group_DRO (295★): Waterbirds/CelebA loaders + worst-group eval
- izmailovpavel/spurious_feature_learning (48★): spurious feature analysis in SSL

### Feasibility Constraints
- MUST use existing benchmarks (Waterbirds, CelebA, CMNIST, UrbanCars)
- NO new benchmarks, synthetic data, or human annotation
- MUST be annotation-free (no group labels at training time)
- MUST be testable with existing evaluation protocols

### Previous Failure / Routing Context
No Serena memory files found. This is a first Phase 2A attempt.

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been thinking about this backwards? Everyone's trying to apply SAM to reduce shortcut features — but Gatmiry et al. (2024) show sharpness minimization actually *promotes* rank-1 features, which *are* the shortcuts. So the interesting question becomes: can we exploit this? What if SAM during SSL pre-training specifically flattens the loss landscape around *spurious* feature directions while keeping it sharp around *core* feature directions?

HERE'S the wild idea: in contrastive SSL, the loss landscape has two kinds of flat basins — one corresponding to features that make augmented views look similar (invariant features), and one corresponding to accidental correlations (shortcuts). Standard SAM flattens everything. But what if we designed a *directional* SAM that measures curvature separately in the augmentation-invariant subspace vs. the spurious subspace? The augmentation-invariant subspace is already something SSL learns implicitly — we could approximate it from the gradient directions during contrastive loss computation.

This connects beautifully to Q4 (loss landscape as predictor) and Q3 (annotation-free intervention). The augmented views in SimCLR/MoCo/DINO create a natural dichotomy: features that are consistent across views are "core," features that differ across views are potentially spurious. The gradient alignment between the two augmented views encodes this — high-alignment gradients point toward invariant (core) features, low-alignment gradients point toward view-dependent (potentially spurious) features.

So the hypothesis: **View-Gradient-Aligned SAM (VGA-SAM)** — apply SAM perturbations *only* in the direction of gradient misalignment between augmented views. This flattens the loss landscape preferentially around view-inconsistent (spurious) features without touching core feature representations. The result: SSL pre-training that's annotation-free, drop-in (wraps any contrastive loss), and geometrically targeted at shortcut reduction.

**Key Points:**
- Gatmiry's result (SAM → rank-1/simplicity bias) actually motivates *directional* SAM, not abandonment of SAM
- SSL's augmented views provide a free label of "core vs. spurious" via gradient alignment — no annotations needed
- VGA-SAM: perturb in gradient-misalignment direction → flatten shortcut landscape → contrastive loss selects core features

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing mechanistic argument, but let me stress-test it immediately. The claim that gradient misalignment between augmented views identifies spurious features rests on a critical assumption: that the augmentation policy reliably *removes* spurious features while *preserving* core features. This is not guaranteed.

Consider Waterbirds: standard augmentations (crop, flip, color jitter) do NOT remove the background (water/land) from images. Both views may still have the same spurious background context. If the spurious feature is consistent across augmented views, its gradient contribution is *high-alignment*, not low-alignment — your directional SAM would then preserve it rather than flatten it. This is a fundamental validity problem for the annotation-free component, not just an edge case.

The evidence suggests: **P4 (Cross-Variant SSL, Yadav et al. 2026)** achieves 92.5% Waterbirds precisely because it uses *generative* augmentation to actually remove background — standard crops don't. This suggests view-gradient alignment will fail on benchmarks where spurious features survive standard augmentation.

That said, the loss landscape measurement component (Q4) is on stronger footing. What would disprove this? If we train SimCLR/MoCo/DINO on Waterbirds with standard augmentation and measure Hessian sharpness along the spurious feature direction (background) vs. core feature direction (bird morphology), and find no difference, then loss landscape geometry is not predictive of shortcut reliance. This is a clean falsifiable measurement — and it's fully doable with existing tools (weizeming/SAM_AT has landscape analysis code).

I'd refine the hypothesis: separate the *measurement* claim (loss landscape geometry predicts shortcut reliance in SSL — testable on existing trained models) from the *intervention* claim (directional SAM reduces shortcuts). The measurement claim is more immediately verifiable and theoretically grounded.

**Key Points:**
- VGA-SAM's annotation-free assumption breaks on Waterbirds: spurious background survives standard augmentation, creating high gradient alignment on the spurious feature
- Loss landscape measurement (Q4) is independently falsifiable and should be tested first
- Proposed falsification: train SSL models, measure Hessian sharpness along spurious vs. core directions, check correlation with worst-group accuracy

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera's augmentation critique is exactly right — let me extend it. The gradient misalignment heuristic for spurious feature detection has a deeper theoretical problem: in high-dimensional feature spaces, gradient alignment between two stochastic augmented views is *dominated by random noise*, not meaningful feature structure. The signal-to-noise ratio for detecting "spurious vs. core" from a single pair of view gradients is effectively zero for realistic ResNet/ViT models.

However, here's what IS technically sound: the loss landscape curvature measurement approach. Computing the Hessian spectrum (or sharpness via SAM's perturbation) around a trained SSL model is well-defined, computationally feasible with existing tools, and doesn't require group labels. The mechanism: if SSL models with high shortcut reliance (low worst-group accuracy on Waterbirds) systematically have sharper loss landscapes along spurious feature directions and flatter landscapes along core feature directions, this is a detectable, annotation-free diagnostic.

The technically valid path I see: (1) Train SimCLR/MoCo/DINO on Waterbirds, CelebA, CMNIST with standard training. (2) Apply post-hoc landscape analysis: measure sharpness along known spurious directions (we know them for these benchmarks even if not used during training). (3) Correlate sharpness with worst-group accuracy. (4) If correlation holds, THEN test whether training-time SAM flattens the spurious direction landscape and improves worst-group accuracy.

This decouples two testable claims: (a) landscape geometry predicts shortcuts (diagnostic), (b) SAM training changes landscape geometry in the right direction (intervention). Both are testable on existing benchmarks without any new annotation or data. The existing spurious_feature_learning code (Izmailov) already extracts spurious/core feature subspaces — that's the "direction" we need for (2).

**Key Points:**
- Gradient misalignment between views is theoretically noisy in high-dimensional models — unreliable signal for spurious feature detection
- Hessian-based sharpness measurement along known spurious subspaces is technically sound and annotation-free at test time
- Two decoupled testable claims: (a) landscape predicts shortcuts, (b) SAM changes landscape appropriately

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question I must ask: what is the genuine scientific contribution here, and how significant is it?

The discussion has identified a two-part hypothesis. The first part — loss landscape geometry predicts shortcut reliance in SSL models — is genuinely novel. SubpopBench covers 20 supervised algorithms but no SSL models. Izmailov et al. (2022) analyze SSL spurious features but not loss landscape geometry. If we establish that Hessian sharpness along spurious feature directions in SimCLR/DINO correlates with worst-group accuracy on Waterbirds/CelebA/CMNIST, this is the first empirical validation of the theoretical link Gatmiry et al. (2024) proposed, extended to SSL settings. That matters.

The second part — standard SAM during SSL pre-training improves worst-group accuracy — is the more impactful claim if true, and the gap is real (G2-SAM, DGSAM both confirm supervised-only, SSL gap confirmed). But Prof. Vera and Prof. Pax correctly flag that standard SAM on standard augmentation may not work for the reasons they described.

Here's what I believe is the strategically significant framing: **position the loss landscape measurement as the primary contribution (first-of-its-kind diagnostic for SSL shortcut reliance), with SAM training as a downstream test of whether the diagnostic insight translates to actionable intervention.** If SAM works, great — two contributions. If SAM doesn't work (Schliserman's risk materializes), the landscape measurement contribution still stands, and we've learned *why* SAM fails in SSL. Either outcome is publishable.

The field significance is real: the reproducibility study (Delzer & Bender 2026) identifies group label dependency as the main obstacle to spurious correlation robustness. An annotation-free loss landscape diagnostic directly addresses this obstacle.

**Key Points:**
- Primary contribution: first empirical measurement of Hessian sharpness along spurious vs. core directions in SSL models, correlated with worst-group accuracy
- Secondary contribution: whether training-time SAM changes this landscape geometry and improves worst-group accuracy
- Either SAM-works or SAM-fails outcome is scientifically informative — avoids "only positive results" trap

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can tighten this considerably. Let me synthesize what's emerged and propose a concrete hypothesis statement that addresses the critiques.

The core insight is: SSL models develop anisotropic loss landscapes where the curvature differs along spurious vs. core feature directions. This anisotropy — measurable via SAM's perturbation mechanism — correlates with worst-group accuracy. The intervention test: applying SAM during SSL pre-training isotropizes the landscape, preferentially reducing curvature along spurious directions (because spurious features tend to correspond to simpler, lower-rank directions that SAM's rank-reduction effect targets).

Prof. Vera's augmentation critique is addressed by: we DON'T rely on augmentation to identify spurious features during training. We use the known spurious subspaces (extractable from Izmailov's spurious_feature_learning code on existing benchmarks) only for the *measurement* step post-hoc. During training, SAM operates annotation-free. The measurement step uses the benchmark's implicit knowledge of spurious features for evaluation, not training.

Prof. Pax's dimensionality concern is addressed by: we don't use gradient alignment between views. We use SAM's landscape measurement (fixed-norm perturbation, measure loss increase) which is well-defined in high dimensions and is exactly what davda54/sam implements.

Hypothesis statement: **Under standard SSL pre-training (SimCLR/MoCo/DINO) on spurious correlation benchmarks (Waterbirds/CelebA/CMNIST), SSL models with higher loss landscape sharpness along spurious feature subspaces exhibit lower worst-group accuracy. Applying SAM during SSL pre-training reduces this sharpness anisotropy and improves worst-group accuracy on these benchmarks without group labels.**

**Key Points:**
- Decoupled test: (P1) sharpness anisotropy correlates with worst-group accuracy on existing SSL models; (P2) SAM training reduces sharpness anisotropy; (P3) reduced anisotropy → improved worst-group accuracy
- Annotation-free: SAM training needs no labels; landscape measurement uses spurious subspaces extractable post-hoc from existing benchmark knowledge
- Implements with: davda54/sam + pyssl + spurious_feature_learning + group_DRO — all existing tools

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Let me be precise.

**Problem 1: The "spurious subspace" measurement is not annotation-free in practice.** Dr. Ally says we use Izmailov's spurious_feature_learning code to extract spurious subspaces post-hoc. But that code requires knowing which samples belong to minority groups (e.g., waterbirds on land background) to compute the spurious feature direction. This is exactly the group annotation we're trying to avoid. If we use group labels for the measurement step, we've violated the annotation-free constraint — even if training is label-free.

**Problem 2: Gatmiry's simplicity bias result cuts the wrong way.** The theory says SAM → rank-1 features → simplicity bias. Spurious features in Waterbirds (background color/texture) ARE simpler (lower-rank) than bird morphology features. So SAM should INCREASE reliance on spurious features, not decrease it. Dr. Ally says "SAM's rank-reduction effect targets spurious directions" — this is the opposite of what the theory predicts. This is a fundamental tension that must be resolved.

**Problem 3: DGSAM's "fake flat minima" problem.** Song et al. (2025) found SAM converges to flat regions that don't generalize across domains — these are fake flat minima corresponding to simpler features. In SSL, these simpler features are precisely the spurious shortcuts. So DGSAM's failure mode is exactly what we'd expect in SSL+spurious setting.

**What would convince me:** (a) a theoretical argument for WHY SSL contrastive loss should change SAM's behavior vs. supervised loss (maybe InfoNCE geometry is different?), and (b) a measurement plan that extracts spurious subspace direction WITHOUT group annotations — e.g., using the model's own loss distribution (like LFR/JTT use misclassification proxy).

**Key Points:**
- "Annotation-free measurement" requires group labels in Izmailov's approach — violates constraint
- Gatmiry's theory predicts SAM → MORE shortcuts (rank-1 = simpler = spurious), not fewer
- DGSAM "fake flat minima" = precisely what SSL+spurious would produce; need theoretical counter-argument

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critique is the sharpest we've had — and it's made me see something important. NOW we're onto something!

Prof. Rex says Gatmiry's theory predicts SAM → more shortcuts. But wait — Gatmiry proves this for *supervised* losses where the label itself creates a rank-1 attractor. In SSL contrastive losses (InfoNCE), the loss landscape is fundamentally different: the InfoNCE objective creates a *uniform* feature distribution pressure (von Mises-Fisher concentration) across the entire representation sphere. There's no single rank-1 attractor — instead there are as many attractors as there are classes in the implicit contrastive structure.

This means SAM in SSL operates in a qualitatively different landscape than SAM in supervised settings. The simplicity bias theory doesn't directly transfer. What SAM does in SSL's InfoNCE landscape is an open empirical question — which is precisely the gap.

On Prof. Rex's annotation problem: brilliant catch. The fix is to use **loss-based spurious subspace identification** — exactly what LFR (Ghaznavi 2023) and EVaLS do. High-loss samples in a trained SSL model (after a linear probe on the downstream task) tend to be minority group members. We can use the linear probe's loss distribution to identify spurious feature directions without group labels — the same technique LFR uses, but adapted to measure landscape geometry rather than to resample.

Refined hypothesis: **Under SSL pre-training with InfoNCE-type losses, the loss landscape has systematically higher curvature along directions corresponding to features with high linear-probe loss variance. SAM during SSL pre-training reduces this curvature preferentially. The degree of curvature reduction correlates with worst-group accuracy improvement on Waterbirds/CelebA/CMNIST.** Spurious subspace identified via linear probe loss distribution (annotation-free, following LFR protocol).

**Key Points:**
- Gatmiry's rank-1 simplicity bias theory applies to supervised cross-entropy — InfoNCE landscape is qualitatively different (uniform distribution pressure), so the theory may not transfer
- Annotation-free measurement fix: use linear probe loss distribution to identify high-variance (spurious) feature directions, following LFR protocol — no group labels needed
- The empirical question (does SAM in SSL promote or reduce simplicity bias?) is genuinely open and the InfoNCE geometry argument provides theoretical motivation to test it

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The InfoNCE geometry argument from Dr. Nova is scientifically interesting but needs sharper operationalization. Let me specify the precise falsifiable predictions.

**Prediction P1 (Primary):** SSL models (SimCLR/MoCo/DINO) trained with standard SGD on Waterbirds exhibit measurably higher Hessian sharpness (measured by SAM's ρ-perturbation loss increase) along the "high linear probe loss variance" feature directions than along uniformly sampled random directions. This sharpness anisotropy correlates negatively with worst-group accuracy across model checkpoints (r < -0.5, p < 0.05, at minimum 5 checkpoints per SSL method × 3 datasets). Falsification: no correlation found (|r| < 0.2) or random directions show equal sharpness.

**Prediction P2:** SSL models trained with SAM (rho=0.05, via davda54/sam wrapping pyssl's SimCLR loss) show reduced sharpness anisotropy compared to SGD-trained models, measured at convergence on Waterbirds, CelebA, CMNIST. The linear probe loss variance distribution is more uniform in SAM-trained models. Falsification: SAM training increases sharpness anisotropy or shows no significant difference (p > 0.05).

**Prediction P3:** Worst-group accuracy of SAM-trained SSL models exceeds SGD-trained SSL models by ≥2pp on at least 2 of 3 datasets (Waterbirds/CelebA/CMNIST), without group labels at training time. Falsification: no worst-group accuracy improvement (< 1pp on all datasets).

**Critical control:** LFR and EVaLS (annotation-free baselines) on the same SSL features provide the comparison point — SAM must match or exceed them on worst-group accuracy to claim practical utility.

**Key Points:**
- P1: sharpness anisotropy measurable on existing SSL models, correlated with worst-group accuracy — no new data needed
- P2: SAM reduces anisotropy — testable with SAM wrapper on pyssl's contrastive loss
- P3: worst-group accuracy improvement ≥2pp on ≥2/3 datasets — specific success criterion

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The measurement plan is now technically sound. Let me confirm feasibility and flag one remaining boundary condition.

The linear probe loss variance approach for spurious subspace identification is technically valid — LFR uses exactly this mechanism (high-loss sample upweighting) and it works without group annotations. Computing Hessian sharpness via SAM's perturbation is O(n) in parameters (same cost as a gradient step) and well-implemented in davda54/sam. The full pipeline: train SSL → train linear probe on downstream task → use probe's loss distribution to identify high-variance directions → measure SAM perturbation loss increase along those directions vs. random directions. This is implementable with existing code.

One boundary condition to flag: the "fake flat minima" problem from DGSAM is real and worth including as a potential negative result. If SAM in SSL produces flat minima corresponding to spurious features (as DGSAM found for domain shift), we'd observe P2 satisfied (reduced anisotropy in the direction we measure) but P3 failing (no worst-group improvement or even degradation). This failure mode is distinguishable from a true positive: if sharpness anisotropy reduces uniformly (all directions flatten equally, not selectively), it's likely fake flat minima. We can diagnose this by checking whether core feature representation quality (linear probe accuracy on majority groups) is preserved after SAM training.

Feasibility verdict: **FEASIBLE**. All components exist. The key scientific question (does SAM in SSL reduce spurious sharpness anisotropy?) is empirically answerable on existing benchmarks with existing tools. The distinction between true and fake flat minima is diagnostically built into the prediction framework.

**Key Points:**
- Full pipeline feasible: SSL training (pyssl) → linear probe → loss variance → sharpness measurement (SAM perturbation) → worst-group eval (group_DRO)
- "Fake flat minima" failure mode is diagnostically distinguishable: uniform flattening + no worst-group improvement vs. selective flattening + improvement
- Core feature preservation check (majority group linear probe accuracy) validates true vs. fake flat minima

---

### Exchange 10

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We're converged. Let me write the final synthesis that addresses all critiques.

**Final Hypothesis: SAM-SSL Sharpness Anisotropy Hypothesis for Spurious Correlation Reduction**

*Core claim:* SSL models (SimCLR/MoCo/DINO) trained on spurious correlation benchmarks develop anisotropic loss landscapes: higher Hessian sharpness along feature directions with high linear-probe loss variance (spurious directions) than along random directions. This anisotropy is (a) a diagnostic predictor of worst-group accuracy and (b) reducible by SAM during pre-training, yielding worst-group accuracy improvements without group annotations.

*Why this matters:* First empirical bridge between loss landscape geometry and shortcut reliance in SSL settings. Directly addresses the main obstacle identified by Delzer & Bender (2026): group label dependency. Provides both a diagnostic tool (post-hoc sharpness measurement) and an intervention (training-time SAM).

*Theoretical grounding:* Gatmiry et al. (2024) prove supervised SAM → rank-1/simplicity bias. InfoNCE's uniform distribution pressure creates qualitatively different landscape dynamics (no single rank-1 attractor), so the theory doesn't directly transfer — this gap is the theoretical motivation for the empirical test.

*Annotation-free mechanism:* Spurious directions identified via linear probe loss variance (LFR protocol), not group labels. SAM training is inherently label-free. Fully annotation-free at training time; measurement uses proxy signal.

*Three testable predictions:* P1 (sharpness anisotropy correlates with worst-group accuracy in existing SSL models), P2 (SAM training reduces anisotropy), P3 (worst-group accuracy improves ≥2pp on ≥2/3 datasets). Both P1 failure (no anisotropy → mechanism doesn't hold in SSL) and P3 failure (anisotropy exists but SAM doesn't help → fake flat minima) are scientifically informative.

**Key Points:**
- All six convergence criteria met: SPECIFIC (sharpness anisotropy hypothesis), MECHANISM (InfoNCE landscape + SAM perturbation + linear probe proxy), PREDICTIONS (P1/P2/P3 with criteria), NOVELTY (first SSL loss landscape + shortcut measurement), FEASIBILITY (all tools exist), OBJECTIONS (Gatmiry conflict resolved via InfoNCE argument; annotation issue resolved via LFR protocol; fake flat minima is distinguishable failure mode)
- Ready for Phase 2B

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The SAM-SSL sharpness anisotropy hypothesis is genuinely novel — no paper has measured Hessian sharpness along spurious feature directions in SSL models, and no paper has applied SAM to SSL pre-training on spurious correlation benchmarks. The InfoNCE vs. supervised loss landscape distinction provides a novel theoretical angle that differentiates this from direct extension of Gatmiry's work. The annotation-free LFR-proxy mechanism for spurious direction identification is creative and practical.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three distinct falsifiable predictions with quantitative thresholds (correlation r < -0.5, ≥2pp improvement on ≥2/3 datasets). Each prediction is independently testable. The measurement protocol (SAM perturbation + linear probe loss variance) is well-specified and replicable. Both positive and negative outcomes are scientifically interpretable.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Fills a confirmed gap (SAM+SSL on spurious benchmarks confirmed absent by G2-SAM, DGSAM). Addresses the primary obstacle in spurious correlation robustness (group label dependency). Provides both diagnostic tool and intervention — two contributions with a single experimental setup. The field will cite this whether SAM helps or hurts, because the measurement itself is a first.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components (pyssl, davda54/sam, group_DRO, spurious_feature_learning) exist and integrate via standard PyTorch APIs. The measurement protocol is O(n) per model. The fake flat minima failure mode is diagnostically distinguishable within the same framework. No fundamental theoretical barriers; the InfoNCE geometry argument resolves the Gatmiry conflict at the empirical-question level.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged: SSL models trained with standard optimizers on spurious correlation benchmarks develop anisotropic loss landscapes where the Hessian sharpness is systematically higher along feature directions that proxy for spurious correlations (identified via linear probe loss variance, following the LFR annotation-free protocol) compared to random directions. This sharpness anisotropy is a predictive diagnostic of worst-group accuracy in SSL models. Applying SAM during SSL pre-training (SimCLR/MoCo/DINO on Waterbirds/CelebA/CMNIST) reduces this anisotropy and improves worst-group accuracy by ≥2pp on at least 2 of 3 benchmarks, without requiring group annotations at training time.

The key theoretical insight: Gatmiry et al. (2024) prove SAM promotes simplicity/rank-1 bias under supervised cross-entropy — but InfoNCE's uniform distribution pressure creates qualitatively different landscape dynamics with no single rank-1 attractor, making the theoretical outcome in SSL an open empirical question that motivates this experiment. The annotation-free measurement uses the proxy that LFR already validated (high linear-probe loss variance ≈ minority group membership). The intervention is a drop-in SAM wrapper on any SSL training loop. The experiment tests on existing benchmarks with existing evaluation protocols (worst-group accuracy on Waterbirds/CelebA/CMNIST). If SAM helps: first annotation-free, training-time SSL shortcut reduction via optimizer geometry. If SAM hurts or fails: first empirical evidence of fake flat minima in SSL+spurious settings, with diagnostic framework for future work.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The InfoNCE landscape argument is theoretical motivation, not proof — SAM may still promote simplicity bias in SSL due to the low effective rank of spurious features even under uniform distribution pressure
- Linear probe loss variance as spurious proxy may have high false positive rate (high-loss samples include hard samples that are not minority group members)
- **Mitigation Strategy:** (a) Include ASAM (adaptive SAM) as a variant — ASAM corrects for parameter scale sensitivity and may behave differently in SSL. (b) Cross-validate the linear probe proxy against known group labels in evaluation only (not training) to measure proxy precision/recall. (c) Report both majority and minority group linear probe accuracy to distinguish fake flat minima.

