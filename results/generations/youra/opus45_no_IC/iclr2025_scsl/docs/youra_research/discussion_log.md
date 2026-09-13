# Phase 2A Research Discussion Log

**Date:** 2026-08-12
**Gap ID:** gap-1-loss-trajectory
**Gap Title:** Per-Sample Loss Trajectory Analysis for Spurious Detection
**Architecture:** Self-Play Loop (Claude-only, IC-ablation)
**Min Exchanges:** 15
**Max Exchanges:** 20

---

## Previous Failure / Routing Context

### H-M1 Failure Record (MUST AVOID)

**Hypothesis:** SGD's implicit regularization drives parameters toward flat regions of the loss landscape, evidenced by decreasing Hessian trace during training.

**Result:** FAIL - Hessian trace INCREASED +363% (1460 → 6758) instead of decreasing.

**Root Cause:** SGD does NOT exhibit implicit sharpness minimization in pretrained + fine-tuning settings.

**PROHIBITED APPROACHES:**
- Loss landscape geometry hypotheses
- Hessian-based metrics as primary signal
- Implicit regularization assumptions about SGD

**REQUIRED PIVOT:**
- Observable training dynamics (loss values, learning order)
- Feature attribution without geometry assumptions
- Representation-based analysis

---

## Research Gap Context

**Gap:** Per-Sample Loss Trajectory Analysis for Spurious Detection

**Current State:** JTT and SPARE use binary ERM misclassification or early-training errors to identify minority samples. These methods treat training dynamics as a coarse binary signal (misclassified vs. correct) rather than analyzing the full loss trajectory curve per sample.

**Missing Piece:** No existing method systematically characterizes the SHAPE of per-sample loss curves (e.g., fast convergence → plateau vs. slow convergence → continued decrease) as a discriminative signal for spurious vs. core feature reliance.

**Key Evidence:**
- JTT (734 citations): Two-stage training closes 75% gap to group DRO
- SPARE (49 citations): Early detection via simplicity bias, +21.1% WGA, 12x faster
- LA-SSL (5 citations): Learning speed inversely correlates with spurious reliance
- DFR (202 citations): ERM learns good features; problem is classifier head

**Feasibility Constraints:**
- Must use existing datasets (Waterbirds, CelebA, MultiNLI)
- Must use existing benchmarks (WGA, accuracy)
- No synthetic data or new rubrics
- No human evaluation required

---

## Discussion Briefing

**Objective:** Generate a testable hypothesis for detecting spurious feature reliance through per-sample loss trajectory analysis.

**Paper References (P1-P4):**
- P1: JTT (Just Train Twice) - Two-stage training, upweight misclassified
- P2: SPARE - Early training detection via simplicity bias
- P3: LA-SSL - Learning speed as signal
- P4: DFR - ERM feature quality, last-layer retraining

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about this all wrong? JTT and SPARE treat loss as a binary signal - misclassified or not, early-learned or not. But loss trajectories are CURVES, not points! Imagine this: a sample that relies on spurious correlations might show a distinctive "fast-then-flat" pattern - rapid loss decrease as the model latches onto the easy shortcut, then a plateau because there's nothing more to learn. Meanwhile, samples requiring core features might show "slow-but-steady" - gradual decrease as the model builds genuine understanding.

The beauty here is that we're not measuring anything about the loss LANDSCAPE (which failed in H-M1). We're measuring the loss VALUES over time - a completely different signal! Think of it like tracking a student's test scores versus trying to understand the topology of what they're learning. One is observable, the other is inferred.

What excites me most is the potential for unsupervised detection. If spurious-reliant and core-reliant samples cluster into different trajectory SHAPES, we could use trajectory clustering (DTW-based, or learned trajectory embeddings) to discover these groups without any labels at all.

**Key Points:**
- Loss trajectory SHAPE (not landscape geometry) as discriminative signal
- "Fast-then-flat" vs "slow-but-steady" as candidate patterns
- Trajectory clustering for unsupervised group discovery

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova raises an intriguing direction, but I need testable specifics. What EXACTLY do we mean by "fast-then-flat" versus "slow-but-steady"? These are intuitive descriptions, not measurable predictions.

Let me propose operational definitions: For each sample $i$, record loss $L_i(t)$ at epochs $t \in \{1, 2, ..., T\}$. Define:
- **Convergence Speed**: $v_i = -\frac{1}{T_{half}} \sum_{t=1}^{T_{half}} \frac{dL_i}{dt}$ (average slope in first half)
- **Terminal Variance**: $\sigma_i = \text{Var}(L_i(t))$ for $t > T_{half}$ (stability in second half)

The hypothesis becomes: Spurious-reliant samples have HIGH $v_i$ (fast initial drop) and LOW $\sigma_i$ (stable plateau), while core-reliant samples have MODERATE $v_i$ and potentially HIGHER $\sigma_i$ or continued decrease.

What would FALSIFY this? If we find no correlation between $(v_i, \sigma_i)$ clusters and ground-truth group membership on Waterbirds or CelebA, the hypothesis fails. Specifically: if AUC for predicting minority-group membership from trajectory features is < 0.6, we reject.

The evidence from SPARE [Yang et al., 2023] supports this direction - they show simplicity bias causes spurious features to be learned EARLY. But they only use this as a binary threshold, not the full trajectory shape.

**Key Points:**
- Operational definitions: convergence speed $v_i$, terminal variance $\sigma_i$
- Falsification criterion: AUC < 0.6 for minority group prediction
- SPARE provides preliminary evidence but uses only early epochs

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in technical feasibility. 🔬 Prof. Vera's metrics are clean, but can we actually compute them reliably?

Per-sample loss logging is straightforward - we just store $L_i(t)$ during training. For ResNet-18 on Waterbirds (4795 training samples, 100 epochs), that's ~480K scalars - trivial storage. The computational overhead is essentially zero since we're logging what's already computed.

The theoretical soundness holds: loss is a direct observable, no landscape geometry involved. We're measuring OUTPUT of the training process, not internal optimizer state. This cleanly avoids the H-M1 failure mode.

However, I have concerns about confounds:
1. **Initialization effects**: Different random seeds could affect trajectory shapes. We need multiple runs.
2. **Label noise vs. spurious correlation**: Hard samples might show "slow-but-steady" for reasons OTHER than core feature reliance (e.g., label noise, out-of-distribution).
3. **Dataset-specific patterns**: Waterbirds has a specific spurious correlation structure (background). Does this generalize to CelebA (hair color) or MultiNLI (lexical overlap)?

The measurement approach is theoretically valid. The question is whether trajectory shape ACTUALLY correlates with spurious reliance, or whether we're measuring something else.

**Key Points:**
- Per-sample loss logging is computationally trivial
- Avoids H-M1 failure (observables, not geometry)
- Confounds: initialization variance, label noise, dataset specificity

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this contribute beyond JTT and SPARE?

JTT [Liu et al., 2021] already uses training dynamics - they upweight samples that remain misclassified after initial training. SPARE [Yang et al., 2023] identifies spurious correlations early via simplicity bias. Both achieve strong results.

If our trajectory shape analysis merely REPLICATES what binary misclassification already captures, this is incremental work. The contribution must be that trajectory SHAPE captures information that binary thresholds MISS.

Here's where it matters: JTT has a false positive problem. Some samples are misclassified not because they're minority-group, but because they're genuinely hard (label noise, ambiguous cases). The binary signal conflates these. If trajectory SHAPE can DISTINGUISH between "minority group but learnable" versus "genuinely hard/noisy", we add value.

Similarly, SPARE's early-epoch threshold is arbitrary. At what epoch do you measure? Trajectory analysis could provide a PRINCIPLED criterion - look for the inflection point where spurious learning saturates.

This matters because it opens new research directions: Can trajectory analysis work for NEW spurious correlations not seen in training? Can it enable ONLINE detection during training (stop before shortcuts are learned)?

**Key Points:**
- Must differentiate from JTT (binary) and SPARE (threshold)
- Value: distinguish "minority but learnable" from "genuinely hard"
- Opens: online detection, generalization to unseen spurious correlations

---

### Exchange 5

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. 🎯 Dr. Sage assumes trajectory shape contains MORE information than binary classification status, but where's the evidence?

Let me stress-test the core claim: "Spurious-reliant samples show fast-then-flat, core-reliant show slow-but-steady."

**Counter-example 1**: A minority-group sample (e.g., waterbird on land) might show SLOW convergence because the model is confused, not because it's learning core features. The "slow" signal could mean "hard to fit with shortcuts" rather than "learning robustly."

**Counter-example 2**: A majority-group sample with strong spurious correlation (waterbird on water) might show fast-then-flat AND be correctly classified - no information gain over binary status.

**Counter-example 3**: LA-SSL [Zhu et al., 2023] shows learning is SLOWER for minority samples. This contradicts Dr. Nova's "fast-then-flat for spurious" claim - minority samples (which rely LESS on spurious features) are the slow ones!

The direction from LA-SSL suggests the OPPOSITE pattern: spurious-reliant samples (majority) learn FAST, minority samples learn SLOW. This aligns with simplicity bias but contradicts the intuition that "spurious = fast convergence."

What would convince me: Show trajectory features have HIGHER AUC for minority detection than binary ERM error status. If not, we've just added complexity without benefit.

**Key Points:**
- LA-SSL suggests OPPOSITE pattern: majority (spurious) fast, minority slow
- Counter-examples challenge the core intuition
- Must demonstrate AUC improvement over binary baseline

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

🔍 Prof. Rex raises valid challenges - let me address them constructively.

The LA-SSL observation actually STRENGTHENS our hypothesis when properly framed. LA-SSL shows minority samples learn SLOWER overall. But "slower" conflates two things:
1. Minority samples may have DELAYED onset (model ignores them while learning shortcuts)
2. Minority samples may have DIFFERENT trajectory shape once learning begins

The refined hypothesis: It's not just SPEED but SHAPE. Specifically:
- **Majority spurious**: Fast drop → early plateau → stable
- **Minority core-reliant**: Delayed start → gradual decrease → may never plateau (continued learning)

This addresses Prof. Rex's counter-example 1: A confused minority sample shows DELAYED START (flat initially) then gradual decrease - distinct from "slow but steady from epoch 1."

For counter-example 2 (majority fast-then-flat): Yes, but combined with classification status, trajectory shape ADD information. A fast-then-flat sample that's ALSO correctly classified = strong majority confidence. A fast-then-flat sample that's misclassified = potential edge case worth investigating.

The key refinement: Use trajectory shape features TOGETHER with ERM error status, not as replacement. This is consistent with AFR [Qiu et al., 2023] which combines ERM errors with last-layer reweighting - we add trajectory features to this pipeline.

**Key Points:**
- Distinguish "delayed onset" from "slow throughout"
- Trajectory features AUGMENT binary ERM status, not replace
- Refined pattern: delay + shape, not just speed

---

### Exchange 7

🔬 **Prof. Vera** (Rigorous Validation Architect):

Building on 🛡️ Dr. Ally's refinement, let me formalize the updated hypothesis with precise testable predictions.

**Hypothesis H-LT1 (Loss Trajectory for Spurious Detection):**

Under standard ERM training of image classifiers, if we characterize per-sample loss trajectories by onset delay, convergence rate, and terminal stability, then minority-group samples will show statistically distinct trajectory clusters from majority-group samples, because simplicity bias causes models to prioritize spurious correlations, delaying learning of core features.

**Variables:**
- IV: Training regime (standard ERM)
- DV: Trajectory cluster membership prediction accuracy for minority groups
- Controlled: Architecture, optimizer, dataset

**Predictions:**
1. **P1 (Primary)**: K-means clustering on trajectory features $(d_i, v_i, \sigma_i)$ achieves AUC > 0.70 for predicting minority-group membership on Waterbirds, exceeding binary ERM-error baseline.
2. **P2**: Onset delay $d_i$ (epochs until loss drops 10% from initial) is significantly higher for minority samples (t-test, $p < 0.05$).
3. **P3**: The trajectory-based detector generalizes: trained on Waterbirds, tested on CelebA, achieves AUC > 0.60.

**Falsification**: If P1 fails (AUC ≤ 0.70 or not better than ERM-error baseline), hypothesis is rejected.

**Key Points:**
- Three trajectory features: onset delay $d_i$, convergence rate $v_i$, terminal stability $\sigma_i$
- Primary prediction: AUC > 0.70 for minority detection
- Falsification: AUC ≤ 0.70 or no improvement over baseline

---

### Exchange 8

🔭 **Dr. Nova** (Creative Novelty Explorer):

Now we're onto something! 🔬 Prof. Vera's formalization is solid, but let me push further on the NOVELTY angle.

What if trajectory features enable something JTT and SPARE CAN'T do: REAL-TIME intervention during training?

Current methods (JTT, DFR) require completing an initial training run, THEN applying corrections in a second stage. But if we can detect spurious-reliant samples DURING training by monitoring trajectory shape, we could:

1. **Early stopping per-sample**: Stop updating on samples showing "spurious-locked" trajectories (fast-flat pattern detected)
2. **Adaptive loss weighting**: Upweight samples showing "delayed onset" patterns in real-time
3. **Curriculum learning**: Present samples in order of trajectory shape complexity

This would be a paradigm shift! Instead of "train → detect → retrain", it's "detect while training → adapt in real-time."

The cross-domain angle: Trajectory shape analysis is model-agnostic. Unlike SPARE (which assumes simplicity bias in specific architectures), trajectory patterns might transfer across architectures (CNN, ViT, MLP) because they capture WHAT the model learns, not HOW it learns.

**Key Points:**
- Real-time intervention during training (not two-stage)
- Paradigm: detect-while-training, not train-detect-retrain
- Model-agnostic trajectory analysis for cross-architecture transfer

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔭 Dr. Nova's real-time intervention is exciting but needs feasibility grounding.

**Technical Feasibility of Real-Time Detection:**
- Computing rolling trajectory statistics: $O(1)$ per sample per epoch with running averages
- Memory: Store trajectory embedding per sample ~10 floats × 5K samples = 200KB - trivial
- Latency: No inference needed, just loss logging

**Theoretical Soundness:**
- Onset delay detection is well-defined: $d_i = \min\{t : L_i(t) < 0.9 L_i(0)\}$
- Convergence rate: slope of linear fit to log-loss in window $[d_i, d_i + W]$
- Terminal stability: variance in final 25% of epochs

The mechanism is physically realizable. The question is: do trajectory patterns STABILIZE early enough to act on them? If a sample's trajectory type only becomes clear at epoch 80 of 100, real-time intervention provides little benefit.

From SPARE evidence: spurious features are learned in EARLY epochs (first 20% of training). This suggests trajectory patterns should differentiate by epoch 20-30, enabling meaningful early intervention.

I see no fundamental barriers. The hypothesis is technically sound, measurements are valid, interventions can work in principle.

**Key Points:**
- Real-time computation is trivial ($O(1)$ per sample)
- Pattern must stabilize early for useful intervention (SPARE suggests yes)
- No fundamental barriers identified

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me assess the significance of what's emerging.

**Contribution Analysis:**

vs. JTT: We add trajectory SHAPE features to binary misclassification. Novel? Yes, but incremental. Impact: MEDIUM.

vs. SPARE: They use early-epoch threshold; we use full trajectory characterization. Novel? Yes, more principled. Impact: MEDIUM-HIGH.

vs. LA-SSL: They use learning speed; we use multi-dimensional trajectory features (onset, rate, stability). Novel? Yes, richer signal. Impact: MEDIUM.

**The breakthrough contribution**: Real-time intervention WITHOUT a separate identification stage. This is genuinely new. Current methods require completing training to identify spurious-reliant samples. We propose detecting DURING training.

**Why the community should care:**
1. Efficiency: No second training run needed
2. Applicability: Works with any loss-based training, no architecture modification
3. Interpretability: Trajectory shapes are human-understandable

**What this opens:**
- Online curriculum learning for robustness
- Transfer of trajectory detectors across datasets
- Foundation for "self-correcting" training dynamics

The real-time intervention angle elevates this from incremental to significant. The trajectory features alone are useful but not groundbreaking; the online application IS.

**Key Points:**
- Trajectory features alone: medium contribution
- Real-time intervention: significant contribution
- Opens: online curriculum, cross-dataset transfer, self-correcting training

---

### Exchange 11

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Let me stress-test the real-time intervention claim - this is where the hypothesis could fall apart.

**Concern 1: Chicken-and-egg problem.** To detect "spurious-locked" trajectories, we need to observe the full pattern (fast drop → plateau). But by the time we observe the plateau, the damage is done - the model has ALREADY learned the spurious correlation. Real-time intervention requires PREDICTING trajectory shape from EARLY observations, not detecting it after the fact.

**Concern 2: Intervention effects.** If we start upweighting "delayed onset" samples early, we CHANGE their trajectories. The very act of intervention invalidates our detection signal. This is fundamentally different from JTT where identification and intervention are separate stages.

**Concern 3: Computational cost of experimentation.** To validate this hypothesis, we need to log per-sample losses across many runs. With 5K samples × 100 epochs × 10 random seeds = 5M loss values per experiment. Across 3 datasets (Waterbirds, CelebA, MultiNLI) = 15M values. This is feasible but not trivial.

**What would convince me:** A causal experiment showing that early trajectory features (epochs 1-20) PREDICT final minority-group membership better than binary ERM error at epoch T_id (JTT's identification epoch).

**Key Points:**
- Must PREDICT trajectory shape from early observations
- Intervention changes trajectories (measurement confound)
- Need causal experiment: early features → minority prediction

---

### Exchange 12

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

🔍 Prof. Rex's challenges are sharp - let me address each.

**On chicken-and-egg:** The hypothesis doesn't require observing FULL trajectory to act. SPARE shows spurious features are learned in first ~20% of training. We propose: by epoch 20, onset delay $d_i$ is already observable. Samples that HAVEN'T started decreasing by epoch 20 are likely minority/core-reliant. This is early enough to upweight for remaining 80% of training.

Concrete prediction: At epoch $T_{early} = 0.2T$, samples with $d_i > T_{early}$ (still flat) are minority-group candidates. This gives us 80% of training for intervention.

**On intervention effects:** Valid concern. Here's the refinement: Split training into DETECTION phase (epochs 1-$T_{early}$, no intervention) and INTERVENTION phase (epochs $T_{early}$-$T$, apply upweighting). Detection phase maintains standard ERM so trajectories are unperturbed. Intervention phase uses detected samples. This is still "online" in sense that it's a single training run, not two separate runs like JTT.

**On computational cost:** 15M loss values is ~60MB of storage - trivial. Logging overhead is negligible. The REAL cost is hyperparameter search for $T_{early}$ and $d_i$ threshold, but this is standard ML practice.

**Key Points:**
- Act on onset delay $d_i$ by epoch 20 (SPARE evidence)
- Split into detection phase + intervention phase within single run
- Storage/compute costs are trivial

---

### Exchange 13

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let me refine the hypothesis based on discussion to date.

**Revised Hypothesis H-LT1.1:**

Under standard ERM training, if we measure onset delay $d_i$ (epochs until 10% loss reduction) in a detection phase (first 20% of training), then samples with $d_i > T_{early}$ will be enriched for minority-group membership, because simplicity bias causes majority-group samples to converge first on spurious features, delaying minority-group learning.

**Refined Predictions:**

**P1 (Primary):** At epoch $T_{early} = 0.2T$, the set of samples with $d_i > T_{early}$ has minority-group precision > 0.5 and recall > 0.3 on Waterbirds.

**P2 (Intervention Effect):** Training with 2x weight on samples with $d_i > T_{early}$ (intervention phase) improves WGA by ≥ 5% over standard ERM, approaching JTT performance without a second training run.

**P3 (Generalization):** The onset delay threshold transfers across datasets: threshold learned on Waterbirds achieves minority precision > 0.4 on CelebA.

**Null Hypothesis (H0):** Onset delay $d_i$ is uniformly distributed across minority/majority groups; threshold-based selection performs no better than random for minority identification.

**Falsification:** If P1 fails (precision ≤ 0.5 OR recall ≤ 0.3), reject H-LT1.1.

**Key Points:**
- Simplified to onset delay $d_i$ as primary feature
- Two-phase single-run design: detect (20%) + intervene (80%)
- Falsification: precision ≤ 0.5 OR recall ≤ 0.3

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The refined hypothesis H-LT1.1 is technically sound. Let me verify the mechanisms are physically possible.

**Measurement Validity:**
- Onset delay $d_i = \min\{t : L_i(t) < 0.9 L_i(0)\}$ is well-defined
- Requires storing per-sample initial loss $L_i(0)$ and checking threshold each epoch
- Computational cost: $O(N)$ comparisons per epoch - negligible

**Intervention Mechanism:**
- Upweighting samples with $d_i > T_{early}$ by factor 2x
- Standard reweighting operation in any DL framework
- No architectural modification needed

**Potential Barriers:**
1. **Initial loss variance:** If $L_i(0)$ varies widely across samples, the 10% threshold may not be comparable. Mitigation: use Z-score normalization.
2. **Numerical precision:** Very small loss changes might not be detected. Mitigation: use running average over 3-epoch window.
3. **Stochastic gradient effects:** Batch sampling affects individual sample losses. Mitigation: record loss only when sample appears in batch (natural data augmentation).

I see no FUNDAMENTAL barriers. These are engineering details, not theoretical obstacles. The hypothesis can be tested with standard PyTorch training loops and minimal modification.

**Key Points:**
- All measurements are computationally trivial
- Standard reweighting mechanism (no architecture changes)
- Engineering mitigations available for edge cases

---

### Exchange 15

🔭 **Dr. Nova** (Creative Novelty Explorer):

Before we converge, let me highlight what's TRULY novel here.

The literature has three paradigms:
1. **Two-stage (JTT, DFR):** Train → Identify → Retrain
2. **Early detection (SPARE):** Identify at fixed early epoch → Mitigate
3. **Learning speed (LA-SSL):** Continuous speed measurement → Sample

What we're proposing is **Adaptive Single-Run (ASR)**:
- No predetermined epoch for identification
- Detection adapts to per-sample learning dynamics
- Intervention begins WHEN trajectory pattern becomes clear (not at fixed epoch)

The novelty isn't just "use trajectory shape" - it's the PARADIGM of adaptive, per-sample, single-run robustification.

Cross-domain potential: This approach borrows from online learning and bandit algorithms - track each sample as an "arm" and adapt exploration/exploitation based on observed rewards (loss trajectory). This framing opens connections to multi-armed bandit literature for principled threshold selection.

**Key Points:**
- New paradigm: Adaptive Single-Run (ASR) robustification
- Per-sample adaptation, not fixed epoch threshold
- Connection to bandit algorithms for principled detection

---

### Exchange 16

🎯 **Dr. Sage** (Research Impact Evaluator):

Assessing final significance before convergence.

**Novelty Verdict:** STRONG

The Adaptive Single-Run paradigm is genuinely new. While JTT, SPARE, and LA-SSL all use training dynamics, none propose per-sample adaptive detection within a single training run. The connection to bandit literature opens theoretical grounding.

**Contribution to Field:**

1. **Methodological:** First method to use continuous trajectory shape for spurious detection
2. **Practical:** Single training run (vs. two-stage), lower computational cost
3. **Theoretical:** Connects spurious correlation to online learning frameworks

**Impact Assessment:**

- Immediate: Competitive WGA with simpler pipeline than JTT
- Medium-term: Foundation for real-time fairness monitoring
- Long-term: Bridges spurious correlation and online learning literature

**Remaining Gap:** The hypothesis focuses on onset delay $d_i$. The full trajectory shape (including convergence rate and terminal stability) remains unexplored. This is acceptable for initial validation but leaves room for future work.

**Key Points:**
- Novelty: STRONG (new paradigm)
- Immediate impact: simpler pipeline, competitive performance
- Long-term: theoretical connections to online learning

---

### Exchange 17

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Final stress-test before convergence.

**Remaining Concerns:**

1. **Effect size uncertainty:** We predict ≥5% WGA improvement. What if the improvement is 1-2%? Is this still meaningful? JTT achieves ~75% gap closure to group DRO. We should anchor expectations.

2. **Alternative explanation:** Onset delay might correlate with sample difficulty GENERALLY, not spurious correlation specifically. A sample could have delayed onset because it's near decision boundary, not because it's minority-group. Need to verify correlation with GROUP membership, not just DIFFICULTY.

3. **Computational comparison:** We claim "simpler pipeline than JTT." But JTT is extremely simple (train twice with upweighting). Our method requires continuous monitoring and adaptive thresholding. Is this actually simpler?

**What I'm now satisfied with:**
- Falsification criteria are clear (precision ≤ 0.5 OR recall ≤ 0.3)
- Mechanism is theoretically sound (simplicity bias → onset delay)
- SPARE evidence supports early detectability

**My verdict:** The hypothesis is well-formulated and testable. My concerns are empirical uncertainties, not logical flaws. Proceed to testing.

**Key Points:**
- Effect size needs anchoring (vs. JTT's 75% gap closure)
- Must verify GROUP correlation, not just DIFFICULTY
- Hypothesis is testable; concerns are empirical

---

### Exchange 18

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Final synthesis addressing 🔍 Prof. Rex's remaining concerns.

**On effect size:** We adjust prediction P2 to include baseline comparison: "WGA improvement ≥ 3% over ERM baseline, achieving ≥ 50% of JTT's improvement with single training run." This anchors expectations while acknowledging we may not fully match JTT's two-stage approach.

**On alternative explanation (difficulty vs. group):** This is testable. We add auxiliary prediction:
- P4: Onset delay $d_i$ correlates more strongly with group membership (r > 0.4) than with sample margin/confidence (r < 0.3).

This distinguishes "hard because minority" from "hard because ambiguous."

**On simplicity claim:** Retracted. JTT IS simpler in code. Our contribution is EFFICIENCY (single run) and THEORETICAL NOVELTY (adaptive detection), not implementation simplicity.

**Final Hypothesis Statement:**

*Under standard ERM training of image classifiers, samples that exhibit delayed onset of loss reduction (onset delay $d_i > T_{early}$) in the first 20% of training are enriched for minority-group membership, because simplicity bias causes majority-group samples to converge first on easily-learned spurious correlations. Intervening on these samples within the same training run improves worst-group accuracy.*

**Key Points:**
- Effect size anchored to ≥50% of JTT improvement
- P4 added: group correlation > difficulty correlation
- Contribution: efficiency + theory, not simplicity

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Adaptive Single-Run (ASR) paradigm is genuinely novel. Unlike JTT (two-stage), SPARE (fixed epoch), or LA-SSL (speed only), we propose per-sample adaptive detection within a single training run. The connection to bandit literature opens new theoretical directions.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has clear falsification criteria. P1 specifies precision > 0.5 and recall > 0.3 for minority detection using onset delay. Failure on either metric rejects the hypothesis. All variables (onset delay $d_i$, detection threshold $T_{early}$) are operationally defined.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Contributes a new paradigm (adaptive single-run), practical efficiency gains (one training run vs. two), and theoretical connections (online learning). Immediate impact as competitive method; long-term impact bridging spurious correlation and bandit literature.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All measurements are computationally trivial. Per-sample loss logging has zero overhead. Onset delay computation is $O(N)$ per epoch. Standard reweighting mechanism requires no architecture changes. No fundamental barriers identified.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

**Hypothesis H-LT1.1 (Loss Trajectory for Spurious Detection):**

Under standard ERM training of image classifiers on datasets with spurious correlations, samples that exhibit delayed onset of loss reduction—specifically, onset delay $d_i$ exceeding the early detection threshold $T_{early}$ (20% of total training)—are enriched for minority-group membership. This occurs because simplicity bias causes models to prioritize easily-learned spurious correlations in majority samples, delaying meaningful learning on minority samples that lack these shortcuts.

The causal mechanism: Majority-group samples (e.g., waterbirds on water backgrounds) provide redundant cues (both core and spurious features predict the label). Models learn spurious correlations first due to simplicity bias, causing rapid loss decrease for these samples. Minority-group samples (e.g., waterbirds on land) lack spurious cues, so learning requires core features, which takes longer—manifesting as delayed onset.

By detecting samples with delayed onset within the first 20% of training and upweighting them for the remaining 80%, we can improve worst-group accuracy within a single training run, achieving efficiency comparable to JTT while providing a more principled, adaptive detection mechanism.

**Experimental Approach:** Train ResNet-18 on Waterbirds with standard ERM. Log per-sample losses at each epoch. At epoch $T_{early} = 20$, identify samples with $d_i > T_{early}$. Apply 2x weighting for remaining training. Measure WGA improvement vs. ERM baseline.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Effect size uncertainty — improvement may be modest (1-3%) rather than substantial (5%+)
- **Concern 2:** Onset delay might correlate with general difficulty, not specifically minority-group membership
- **Concern 3:** The method requires continuous monitoring, which is more complex than JTT's simple two-stage approach

**Mitigation Strategy:**
- Anchor effect size expectations to ≥50% of JTT's improvement
- Include P4 to verify group correlation exceeds difficulty correlation
- Position contribution as efficiency + theory, not implementation simplicity

---

## Emerged Hypothesis Summary

### Core Statement
Under standard ERM training, if onset delay $d_i$ exceeds $T_{early}$ (20% of training epochs), then the sample is enriched for minority-group membership, because simplicity bias causes majority-group samples to converge first on spurious correlations.

### Causal Mechanism
1. Simplicity bias: Models learn "easy" patterns first
2. Spurious features are easier to learn than core features
3. Majority-group samples have redundant cues (spurious + core)
4. Minority-group samples lack spurious cues
5. Therefore: Majority samples show fast loss reduction; minority samples show delayed onset

### Variables
- **IV:** Training regime (standard ERM)
- **DV (Primary):** Minority-group precision/recall of onset delay detector
- **DV (Secondary):** Worst-group accuracy after intervention
- **Controlled:** Architecture (ResNet-18), optimizer (SGD), dataset structure

### Key Assumptions
- A1: Simplicity bias operates consistently across samples
- A2: Onset delay is observable by 20% of training
- A3: Minority/majority differences manifest in trajectory, not just final loss
- A4: Upweighting detected samples improves WGA

### Null Hypothesis
Onset delay $d_i$ is uniformly distributed across minority/majority groups; threshold-based selection is no better than random.

### Predictions
- **P1 (Primary):** At $T_{early}$, samples with $d_i > T_{early}$ have minority-group precision > 0.5 and recall > 0.3
- **P2:** WGA improvement ≥ 3% over ERM, achieving ≥ 50% of JTT's improvement
- **P3:** Threshold transfers: trained on Waterbirds, achieves minority precision > 0.4 on CelebA
- **P4:** Onset delay correlates more with group (r > 0.4) than difficulty (r < 0.3)

### Novelty
- New paradigm: Adaptive Single-Run (ASR) robustification
- Distinguishes from JTT (two-stage), SPARE (fixed epoch), LA-SSL (speed only)
- Connects to online learning / bandit literature

### Scope & Boundaries
- **Applies to:** Image classification with known spurious correlations, ERM training
- **Does not apply to:** NLP tasks (different trajectory dynamics), pre-trained models (initialization effects), datasets without clear majority/minority structure
- **Limitations:** Requires ground-truth groups for evaluation (not for training)

### Experimental Setup
- **Dataset:** Waterbirds (primary), CelebA (transfer), MultiNLI (stretch)
- **Model:** ResNet-18 (ImageNet pretrained)
- **Optimizer:** SGD (lr=0.001, momentum=0.9)
- **Epochs:** 100 (detection phase: 1-20, intervention phase: 21-100)

### Related Work & Baselines
- JTT: Two-stage, binary misclassification signal
- SPARE: Early-epoch detection, fixed threshold
- LA-SSL: Learning speed, self-supervised setting
- DFR: ERM features good, classifier head problem

### Phase 2B Readiness Seeds
- **Existence (SH1):** Onset delay differences between majority/minority groups must exist
- **Mechanism (SH2):** Simplicity bias causes majority-first learning
- **Comparison (SH3):** Deferred to Phase 5 (vs. JTT, SPARE baselines)

### Established Facts
- Simplicity bias causes spurious features to be learned early (SPARE, 2023)
- Minority samples learn slower overall (LA-SSL, 2023)
- ERM learns good features; problem is classifier (DFR, 2022)
- Binary misclassification identifies minority samples (JTT, 2021)

---

