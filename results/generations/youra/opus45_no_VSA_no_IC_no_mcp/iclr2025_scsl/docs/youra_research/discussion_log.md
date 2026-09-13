# Phase 2A: Research Discussion Log

## Metadata
- **Date**: 2026-08-28
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Inline Discussion
- **Execution Mode**: UNATTENDED

---

## Research Briefing

### Selected Gap
**Gap 1: Temporal Dynamics of Spurious Feature Learning**
- **Classification**: PRIMARY
- **Priority**: HIGH
- **Impact**: Enable optimization-based early intervention

### Current State
Shah et al. (2020) demonstrated simplicity bias — DNNs learn simple features first. However, no study measures the temporal emergence of spurious vs. core feature reliance across different SGD hyperparameters (learning rate, batch size, momentum).

### Missing Piece
Epoch-by-epoch feature attribution analysis across LR/batch/momentum configurations to identify when models begin relying on spurious features.

### Key Papers (Inferred)
- Simplicity Bias (Shah et al., 2020, arXiv:2006.07710)
- Dataset Cartography (Swayamdipta et al., 2020, arXiv:2009.10795)
- JTT (Liu et al., 2021, arXiv:2107.09044)
- SAM (Foret et al., 2021, arXiv:2010.01412)
- Group DRO (Sagawa et al., 2020, arXiv:1911.08731)

### Research Question
What is the relationship between SGD optimization dynamics and the temporal emergence of spurious feature reliance? Can optimization-level interventions (LR schedules, batch size adjustments) mitigate shortcut learning without requiring group annotations?

### Feasibility Constraints
- Must use existing real datasets (Waterbirds, CelebA, CMNIST)
- Must use existing benchmarks (worst-group accuracy)
- No new rubrics, no synthetic data, no human evaluation

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from a temporal lens that nobody has explored? The simplicity bias literature tells us DNNs learn "simple" features first — but what exactly does "simple" mean in the context of spurious correlations? Here's my unconventional angle:

**The Spurious-Core Racing Hypothesis**: Spurious features aren't just "simple" — they're *fast*. They achieve high gradient signal early because they correlate strongly with labels in training data. Core features, being more robust but less discriminative on training data, get suppressed by the implicit competition in gradient descent. The key insight: this is a *race*, and the winner is determined by learning rate and batch size.

What excites me is the connection to loss landscape geometry. SAM finds flat minima, but what if spurious reliance corresponds to *sharper* local minima? If true, we could detect spurious dominance epochs by monitoring Hessian eigenvalues — no group labels needed!

Three wild angles to explore:
1. **Gradient magnitude tracking**: Monitor per-feature gradient norms across training. Spurious features should show early spikes then plateau.
2. **Learning rate as intervention**: High LR might "overshoot" spurious minima, forcing the model toward core features.
3. **Batch size as sampling control**: Small batches might inject enough noise to disrupt spurious correlations.

The paradigm shift here: instead of *detecting* spurious features post-hoc, we *predict* when they emerge and intervene mid-training. NOW we're onto something!

**Key Points:**
- Spurious features may dominate due to faster gradient signal, not just simplicity
- Loss landscape sharpness could be a spurious-reliance proxy
- Optimization hyperparameters as temporal intervention points

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's racing hypothesis is intriguing, but let me stress-test it. The evidence suggests we need precise operationalization before we can call this testable.

First, the critical question: **What would convince us this hypothesis is wrong?** If we cannot answer this, we don't have science.

Here's what I see as the falsification structure:
- **Null hypothesis (H0)**: There is no systematic relationship between SGD hyperparameters (LR, batch size) and the epoch at which spurious feature reliance emerges. The temporal dynamics are random or dominated by factors orthogonal to optimization.
- **Falsifier**: If we observe that varying LR/batch size across a wide range produces no statistically significant change in spurious feature emergence timing (measured via feature attribution methods like GradCAM or Integrated Gradients), the hypothesis fails.

What specific, measurable predictions can we make? I propose:
1. **Prediction P1**: Models trained with higher learning rates will show peak spurious feature attribution at later epochs than models with lower learning rates.
2. **Prediction P2**: Models trained with smaller batch sizes will exhibit more variance in spurious feature emergence timing.
3. **Prediction P3**: Loss landscape sharpness (measured by top Hessian eigenvalue) at the epoch of spurious feature dominance will be significantly higher than at convergence.

Confounds to control:
- Architecture (must fix to isolate optimizer effects)
- Random seed variance (multiple seeds per configuration)
- Dataset difficulty (test across Waterbirds, CelebA, CMNIST)

**Key Points:**
- H0 clearly defined: no relationship between SGD hyperparameters and spurious timing
- Three measurable predictions with clear success/failure criteria
- Confounds identified: architecture, seeds, datasets

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: **What makes this genuinely new versus incremental?**

Shah et al. (2020) showed simplicity bias exists. Dataset Cartography (2020) mapped training dynamics but didn't connect to spurious features. JTT (2021) addressed robustness without group labels but used a two-stage approach. SAM (2021) improved generalization via flat minima but didn't explicitly study spurious correlations.

**This matters because** the proposed work would be the FIRST to:
1. Provide epoch-level temporal characterization of spurious feature emergence
2. Connect optimization hyperparameters directly to shortcut learning timing
3. Propose single-stage, optimization-only robustification (no two-stage training like JTT)

The contribution is not just "another robustness method." It's a **mechanistic understanding** of WHY shortcuts emerge when they do, and HOW SGD dynamics control this timing. This opens entirely new research directions:
- Dynamic learning rate schedules designed to suppress spurious features
- Batch size curricula for robustness
- Real-time spurious detection during training

However, I must push back on one aspect: the significance depends heavily on **effect size**. If hyperparameter changes only shift spurious emergence by 1-2 epochs out of 100, the practical impact is minimal. We need to establish that the effect is large enough to matter.

**Key Points:**
- First temporal characterization of spurious feature emergence with optimization control
- Opens new research directions: dynamic schedules, curricula, real-time detection
- Effect size is critical — significance requires meaningful practical impact

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. Dr. Nova's hypothesis is exciting, but I need to assess **technical and theoretical feasibility**.

**Is the mechanism scientifically sound?**
Yes. Gradient descent dynamics are well-understood theoretically. The claim that different features have different "learning speeds" based on gradient magnitude is consistent with feature learning theory. The connection to loss landscape sharpness is supported by SAM literature.

**Are the measurement methods theoretically valid?**
Mostly yes, with caveats:
- GradCAM and Integrated Gradients are established attribution methods
- Hessian eigenvalue computation is well-defined but computationally expensive
- "Spurious feature attribution score" needs clear operationalization — we need to define exactly what we're measuring

**Can the proposed interventions work in principle?**
This is where I have concerns. The hypothesis assumes:
1. Spurious features and core features compete for gradient signal — **plausible but unproven**
2. Learning rate can "overshoot" spurious minima — **possible but mechanism unclear**
3. Small batches disrupt spurious correlations — **consistent with stochastic regularization literature**

**Fundamental barriers (not budgetary):**
- Feature attribution methods may not cleanly separate spurious vs. core features
- Spurious features might be learned through DIFFERENT pathways than core features, not competing ones
- The "racing" metaphor might be oversimplified — could be more complex dynamics

My assessment: **Technically feasible with important caveats**. The core measurements can be done, but interpretation requires careful validation.

**Key Points:**
- Gradient-based mechanism is theoretically sound
- Attribution methods are valid but need careful operationalization
- Key assumption (feature competition) needs verification as part of the hypothesis

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this against Prof. Pax's concerns! Let me build bridges here.

**Addressing the feature competition assumption:**
Prof. Pax rightly questions whether spurious and core features truly compete. Here's how we can verify this AS PART of our experimental design:
- Measure gradient norms for spurious vs. core features (using ground-truth labels from Waterbirds/CelebA)
- If competition exists, we should see inverse correlation: when spurious gradient norms are high, core feature gradient norms should be suppressed
- This becomes **sub-hypothesis H-M1**: "Spurious and core feature gradients exhibit competition dynamics"

**Strengthening the measurement approach:**
Prof. Vera's P1-P3 are good, but let me add concrete operationalization:
- "Spurious feature attribution" = GradCAM activation on spurious attribute (e.g., background in Waterbirds)
- "Core feature attribution" = GradCAM activation on core attribute (e.g., bird shape)
- "Peak spurious dominance epoch" = first epoch where spurious attribution > core attribution
- "Sharpness" = top eigenvalue of Hessian on loss (computed via power iteration for efficiency)

**Addressing the "racing vs. complex dynamics" concern:**
Even if the metaphor is oversimplified, the core claim remains testable: **optimization hyperparameters affect the timing and magnitude of spurious feature reliance**. Whether the underlying mechanism is "racing" or something more complex doesn't invalidate the empirical predictions.

What if we addressed this by adding a **mechanism-agnostic formulation**?
- Primary claim: "LR and batch size systematically affect spurious feature emergence timing"
- Secondary claim: "This effect is mediated by gradient competition" (testable via H-M1)

Now THAT's stronger!

**Key Points:**
- Feature competition can be verified via gradient norm correlation analysis
- Clear operationalization: GradCAM for attribution, Hessian eigenvalue for sharpness
- Mechanism-agnostic primary claim with testable secondary mechanism claim

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Let me be direct about the remaining gaps.

**Gap 1: Causal direction**
We're claiming "LR affects spurious timing." But what if the causation is reversed or confounded? Higher LR also affects convergence speed, loss scale, and generalization gap. How do we isolate the spurious-specific effect from these correlated phenomena?

**Gap 2: Ground truth dependency**
Dr. Ally's operationalization assumes we know which features are "spurious" vs. "core." In Waterbirds/CelebA, we have this ground truth. But the motivation is annotation-free robustness. If our method requires ground truth for measurement, it undermines the practical claim.

**Gap 3: Effect size specification**
Dr. Sage mentioned this, but no one has answered: **What effect size would we consider meaningful?** If high LR shifts peak spurious dominance from epoch 5 to epoch 7 (2 epochs), is that significant? We need a priori criteria.

**What would convince me:**
1. Show that LR effect on spurious timing is LARGER than its effect on general training dynamics (convergence, loss scale)
2. Demonstrate that the measurement approach works WITHOUT ground truth (use a proxy that generalizes)
3. Pre-register effect size thresholds before running experiments

**My assessment:** The hypothesis is promising but currently **underdetermined**. We have predictions but no clear decision rules for interpreting results. Without effect size criteria and causal isolation, positive results could be explained away and negative results blamed on insufficient effect size.

**Key Points:**
- Causal isolation needed: separate spurious effect from general LR effects
- Ground truth dependency undermines annotation-free motivation
- Effect size criteria must be pre-specified

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are fair, and I see a creative solution emerging! Let me connect some dots.

**On causal isolation:**
What if we use a **matched control design**? For each hyperparameter configuration, we measure BOTH:
1. General training dynamics (loss, accuracy trajectory)
2. Spurious-specific dynamics (spurious/core attribution ratio)

If LR affects spurious timing DIFFERENTLY than it affects general dynamics, we have evidence for spurious-specific causation. Imagine this: two configurations converge at similar speeds but show different spurious emergence patterns — that's the smoking gun.

**On ground truth dependency:**
This is actually an opportunity! The hypothesis testing uses ground truth, but the **intervention design** doesn't need it. Here's the paradigm shift:
- Phase 1 (understanding): Use Waterbirds/CelebA ground truth to discover which hyperparameter configurations delay spurious emergence
- Phase 2 (deployment): Apply those configurations to NEW datasets without ground truth
- The claim: "Configurations that delay spurious features on known benchmarks will improve worst-group accuracy on novel datasets"

This is testable on existing benchmarks! If configurations that delay spurious emergence on Waterbirds also improve worst-group accuracy on CelebA (transfer across datasets), we've validated the approach.

**On effect size:**
I propose: a shift of **≥10% of total training epochs** is meaningful. If training runs 50 epochs and we can shift peak spurious dominance by 5+ epochs, that's substantial time for intervention.

NOW we're onto something — matched controls, transfer validation, and pre-registered effect sizes!

**Key Points:**
- Matched control design isolates spurious-specific effects from general dynamics
- Two-phase approach: ground-truth discovery, then annotation-free deployment
- Effect size threshold: ≥10% of total training epochs

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's refinements address Prof. Rex's concerns systematically. Let me formalize the updated experimental design.

**Revised Predictions (with effect size criteria):**

**P1 (Primary)**: Models trained with learning rate 10x higher than baseline will show peak spurious feature dominance at epochs ≥10% later than baseline (e.g., epoch 10 vs. epoch 5 for 50-epoch training), while controlling for convergence speed.
- **Success criterion**: Spurious dominance epoch shift ≥ 5 epochs (for 50-epoch training)
- **Statistical test**: Paired t-test across 5 seeds, p < 0.05
- **Falsification**: If high-LR configurations show ≤2 epoch shift, hypothesis fails

**P2 (Secondary)**: Peak spurious dominance epoch will negatively correlate with final worst-group accuracy (r < -0.5, p < 0.05).
- **Success criterion**: Spearman correlation r < -0.5
- **Falsification**: If r ≥ -0.3, the practical relevance is questionable

**P3 (Mechanism)**: At peak spurious dominance epoch, loss landscape sharpness (top Hessian eigenvalue) will be ≥2x higher than at convergence.
- **Success criterion**: Eigenvalue ratio ≥ 2.0
- **Falsification**: If ratio < 1.5, sharpness-spurious connection fails

**Experimental Protocol:**
1. Dataset: Waterbirds (primary), CelebA (replication)
2. Model: ResNet-50 (fixed architecture)
3. Hyperparameters: LR ∈ {0.001, 0.01, 0.1}, Batch size ∈ {32, 128, 512}
4. Seeds: 5 per configuration (45 runs total)
5. Measurements: GradCAM attribution per epoch, Hessian eigenvalue at key epochs

This meets my standards for testability.

**Key Points:**
- P1: 10% epoch shift threshold with statistical test
- P2: Correlation with worst-group accuracy (practical validation)
- P3: 2x sharpness ratio for mechanism validation
- 45-run factorial design with replication

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The hypothesis has matured significantly. Let me assess the final contribution level.

**Contribution Assessment:**

1. **Novel empirical finding**: First temporal characterization linking SGD hyperparameters to spurious feature emergence timing. This is genuinely new — no prior work has measured this relationship.

2. **Mechanistic insight**: The gradient competition and sharpness hypotheses provide explanatory power beyond correlation. Even if the mechanism is later refined, the framework advances understanding.

3. **Practical method**: Optimization-only robustification without group labels. JTT requires two-stage training; Group DRO requires annotations. A single-stage, hyperparameter-based approach is simpler and more practical.

4. **New research directions opened**:
   - Dynamic LR schedules designed for robustness
   - Batch size curricula
   - Real-time spurious detection via attribution monitoring
   - Transfer of hyperparameter configurations across datasets

**Significance verdict: HIGH**

This work advances the field by:
- Providing the FIRST temporal understanding of spurious feature emergence
- Connecting optimization theory to shortcut learning
- Offering a practical, annotation-free method

The effect size criteria (10% epoch shift) ensure practical relevance. The transfer validation ensures the approach generalizes.

**Key Points:**
- Genuinely novel: first temporal characterization
- High practical impact: annotation-free, single-stage robustification
- Opens multiple new research directions
- Effect size criteria ensure meaningful contribution

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me give my final feasibility assessment.

**Technical soundness: VERIFIED**
- Gradient magnitude tracking: standard operation in PyTorch
- GradCAM attribution: well-established, efficient
- Hessian eigenvalue: computationally expensive but feasible via power iteration (sample 10 epochs)
- Factorial design (9 configs × 5 seeds): 45 runs, reasonable scope

**Measurement validity: VERIFIED**
- GradCAM on spurious/core regions: requires ground-truth segmentation (available for Waterbirds/CelebA)
- "Peak spurious dominance epoch": well-defined as argmax of spurious/core ratio
- Sharpness via Hessian: established metric from SAM literature

**Proposed interventions: FEASIBLE**
- High LR configurations: standard, no special implementation
- Batch size variations: standard
- Transfer to new datasets: requires measuring worst-group accuracy (needs group labels for evaluation, not training)

**Remaining technical risks:**
1. GradCAM resolution may not cleanly separate foreground/background in complex scenes
2. Hessian computation at scale requires efficient approximation
3. Spurious dominance "peak" may be noisy — consider smoothing or confidence intervals

**Overall verdict: Okay, this could work.** The experiment is technically feasible with standard ML tools. Key risks are manageable with careful implementation.

**Key Points:**
- All measurements feasible with standard ML tooling
- Hessian computation requires efficient approximation (power iteration)
- GradCAM resolution is a minor risk; smoothing mitigates noise
- Overall: technically feasible

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize the consensus hypothesis that has emerged.

**Consensus Hypothesis: Temporal SGD Control of Spurious Feature Emergence**

**Core Claim (Under-If-Then-Because format):**
Under standard supervised learning on datasets with spurious correlations (Waterbirds, CelebA), if we increase the learning rate or decrease the batch size, then peak spurious feature dominance will occur at later training epochs, because higher learning rates and smaller batches introduce optimization noise that disrupts the fast convergence to spurious feature reliance.

**Causal Mechanism (3 steps):**
1. **Step M1 (Early Training)**: Spurious features produce stronger gradient signal than core features due to higher training-set correlation, leading to faster initial learning.
2. **Step M2 (SGD Noise Injection)**: Higher LR and smaller batches introduce optimization noise that disrupts the gradient advantage of spurious features, delaying their dominance.
3. **Step M3 (Delayed Dominance → Better Generalization)**: Later spurious dominance allows more epochs for core feature learning, improving final worst-group accuracy.

**Testable Predictions:**
- P1: 10% epoch shift in peak spurious dominance with 10x LR increase
- P2: Negative correlation (r < -0.5) between peak dominance epoch and worst-group accuracy
- P3: 2x sharpness ratio at peak dominance epoch vs. convergence

**Novelty:**
First work to temporally characterize spurious feature emergence and propose optimization-only intervention.

**Experimental Approach:**
9 hyperparameter configurations × 5 seeds × 2 datasets (Waterbirds, CelebA) = 90 runs
Measurements: GradCAM attribution per epoch, Hessian eigenvalue at key epochs, worst-group accuracy

**Key Points:**
- Clear Under-If-Then-Because hypothesis structure
- 3-step causal mechanism with falsifiers
- 3 testable predictions with effect size criteria
- 90-run experimental design with replication

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Final stress-test before we converge.

**Concern 1: Confound — convergence speed**
Dr. Nova proposed matched controls. I accept this IF we explicitly measure and report convergence speed (epochs to 95% training accuracy) alongside spurious metrics. We must show the spurious timing effect is ORTHOGONAL to convergence speed changes.

**Concern 2: Attribution method reliability**
GradCAM is a heuristic. What if it gives noisy or inconsistent results? 
**Mitigation**: Use two attribution methods (GradCAM AND Integrated Gradients). If both show the same pattern, confidence increases. If they diverge, we report the discrepancy.

**Concern 3: Dataset specificity**
What if the effect only appears on Waterbirds but not CelebA?
**Mitigation**: Require the effect to be significant on BOTH datasets. If it only appears on one, the hypothesis is weakened but not completely falsified.

**What would convince me now:**
1. Report convergence speed as explicit confound control ✓ (addressed)
2. Use two attribution methods for robustness ✓ (add to protocol)
3. Require replication across datasets ✓ (addressed)

**My assessment: CONVERGED**

The hypothesis is now sufficiently well-defined, testable, and robust to criticism. We have:
- Clear predictions with effect size criteria
- Falsification conditions
- Confound controls
- Replication plan

**Now you've addressed my concerns.**

**Key Points:**
- Add convergence speed as explicit confound measurement
- Use two attribution methods (GradCAM + Integrated Gradients) for robustness
- Replication across Waterbirds and CelebA required
- Status: CONVERGED

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The temporal characterization of spurious feature emergence is genuinely novel. No prior work has connected SGD hyperparameters to the timing of shortcut learning. The paradigm shift from post-hoc detection to mid-training prediction opens multiple new research directions.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has clear, pre-registered predictions with quantitative success criteria (10% epoch shift, r < -0.5 correlation, 2x sharpness ratio). Falsification conditions are explicit. The experimental design (45-90 runs with replication) provides statistical power.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** High contribution level. First temporal characterization, practical annotation-free method, opens new research directions in dynamic optimization for robustness. Effect size criteria ensure meaningful practical impact.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Technically feasible with standard ML tooling. All measurements (GradCAM, Hessian eigenvalue, worst-group accuracy) are well-established. Minor risks (GradCAM resolution, Hessian computation cost) are manageable with careful implementation.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged proposes that SGD optimization dynamics — specifically learning rate and batch size — systematically control the timing of spurious feature emergence during training. The core mechanism is gradient competition: spurious features produce stronger initial gradient signal due to high training-set correlation, but optimization noise from higher learning rates and smaller batches disrupts this advantage, delaying spurious dominance. This delay allows more epochs for core feature learning, improving final worst-group accuracy.

The hypothesis is testable via three predictions: (P1) a 10x LR increase shifts peak spurious dominance by ≥10% of training epochs, (P2) later spurious dominance correlates negatively with worst-group accuracy (r < -0.5), and (P3) loss landscape sharpness at peak dominance is ≥2x higher than at convergence. The experimental design uses Waterbirds and CelebA benchmarks with factorial hyperparameter configurations (9 configs × 5 seeds × 2 datasets = 90 runs), measuring spurious vs. core feature attribution via GradCAM and Integrated Gradients.

The key innovation is temporal understanding: instead of detecting spurious features post-hoc, we characterize WHEN they emerge and how optimization controls this timing. This enables optimization-only robustification without group annotations — a simpler, single-stage alternative to JTT and Group DRO.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- GradCAM attribution may be noisy for complex scenes — mitigate with dual attribution methods (GradCAM + Integrated Gradients)
- Convergence speed must be measured as explicit confound control
- Effect must replicate across both Waterbirds and CelebA to be considered robust

**Mitigation Strategy:** The experimental protocol includes dual attribution methods, explicit convergence speed measurement, and cross-dataset replication requirement. These mitigations are built into the design.

---

## Emerged Hypothesis Summary

### Core Statement
Under standard supervised learning on datasets with spurious correlations, if we increase the learning rate or decrease the batch size, then peak spurious feature dominance will occur at later training epochs, because higher learning rates and smaller batches introduce optimization noise that disrupts the fast convergence to spurious feature reliance.

### Causal Mechanism
1. **M1**: Spurious features produce stronger gradient signal than core features due to higher training-set correlation
2. **M2**: Higher LR and smaller batches introduce optimization noise that disrupts spurious gradient advantage
3. **M3**: Delayed spurious dominance allows more core feature learning, improving worst-group accuracy

### Variables
- **IV**: Learning rate (0.001, 0.01, 0.1), Batch size (32, 128, 512)
- **DV (primary)**: Peak spurious dominance epoch, Worst-group accuracy
- **DV (secondary)**: Loss landscape sharpness, Spurious/core attribution ratio
- **Controlled**: Architecture (ResNet-50), Dataset, Random seed

### Key Assumptions
- A1: GradCAM reliably separates spurious vs. core feature attribution
- A2: Spurious and core features compete for gradient signal
- A3: Higher LR/smaller batch increases optimization noise
- A4: Delayed spurious dominance causally improves worst-group accuracy
- A5: Effects transfer across datasets with similar spurious structure

### Null Hypothesis
There is no significant relationship between SGD hyperparameters (LR, batch size) and the epoch at which spurious feature reliance peaks. Variations in LR and batch size do not systematically affect worst-group accuracy beyond their general effects on training dynamics.

### Predictions
- **P1 (Primary)**: 10x LR increase → ≥10% later peak spurious dominance epoch
- **P2**: Peak dominance epoch negatively correlates with worst-group accuracy (r < -0.5)
- **P3 (Mechanism)**: Sharpness at peak dominance ≥2x higher than at convergence

### Novelty
First temporal characterization of spurious feature emergence; first optimization-only (single-stage, no group labels) robustification approach based on hyperparameter control.

### Scope & Boundaries
- **Applies to**: Image classification with spurious correlations, ResNet-family architectures
- **Does not apply to**: NLP (requires separate study), architectures with fundamentally different dynamics (e.g., transformers may differ)
- **Known limitations**: Ground truth needed for measurement (but not for intervention deployment)

### Experimental Setup
- **Datasets**: Waterbirds (primary), CelebA (replication)
- **Model**: ResNet-50
- **Configurations**: 9 (3 LR × 3 batch size)
- **Seeds**: 5 per configuration
- **Measurements**: GradCAM + Integrated Gradients attribution, Hessian eigenvalue, worst-group accuracy

### Related Work & Baselines
- **JTT**: Two-stage training, 86% worst-group on Waterbirds — baseline to beat with single-stage approach
- **Group DRO**: Requires group labels, 91% worst-group — upper bound with annotations
- **ERM**: Standard training, ~75% worst-group — lower bound

### Phase 2B Readiness Seeds
- **SH1 (Existence)**: Spurious features must dominate earlier than core features in standard training
- **SH2 (Mechanism)**: Gradient competition between spurious and core features must be detectable
- **SH3 (Comparison)**: Deferred to Phase 5 — compare against JTT and ERM

### Established Facts
- Simplicity bias exists (Shah et al., 2020) — BUILD_ON
- DNNs learn simple features first — BUILD_ON
- SAM finds flat minima with better generalization — BUILD_ON
- JTT achieves annotation-free robustness via two-stage training — PROVE_NEW (we claim single-stage suffices)
