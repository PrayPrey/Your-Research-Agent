# Phase 2A Discussion Log

**Date:** 2026-08-19
**Architecture:** Self-Contained Tikitaka Loop
**Execution Mode:** UNATTENDED

---

## Briefing Context

### Selected Research Gap

**Gap ID:** gap-1
**Title:** Temporal Dynamics of Spurious vs Core Feature Learning
**Priority:** HIGH | **Relevance:** PRIMARY

**Current State:** Simplicity bias (Shah et al. 2020) shows DNNs prefer simple features. Gradient starvation (Pezeshki et al. 2021) explains suppression mechanism. But precise temporal ordering on standard benchmarks is not characterized.

**Missing Piece:** Quantitative analysis of when (which epochs, which loss values) spurious features emerge relative to core features on Waterbirds/CelebA/ColoredMNIST.

**Potential Impact:** High - Would enable intervention timing strategies

### Key Literature

1. **Simplicity Bias in Deep Learning** (Shah et al., 2020, arXiv:2006.07710) - DNNs learn linearly-separable features first
2. **Gradient Starvation** (Pezeshki et al., 2021, arXiv:2011.09468) - Dominant features suppress gradient flow to minority features
3. **Last Layer Re-Training is Sufficient** (Kirichenko et al., 2023, arXiv:2204.02937) - Both core and spurious features ARE learned, weighted differently
4. **Edge of Stability** (Cohen et al., 2021, arXiv:2103.00065) - Progressive sharpening phenomenon

### Available Resources

- **Benchmarks:** Waterbirds, CelebA, ColoredMNIST (group-annotated)
- **Implementations:** p-lambda/wilds, kohpangwei/group_DRO, facebookresearch/DomainBed
- **Metrics:** Worst-group accuracy, feature probe analysis

### Feasibility Constraints (MANDATORY)

- Must use existing benchmarks only
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data
- No human evaluation or annotation
- Testable immediately with existing real datasets

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if the key to understanding shortcut learning isn't just WHAT features are learned, but WHEN? The literature tells us simplicity bias causes DNNs to prefer easy features (Shah et al. 2020), and gradient starvation explains why this persists (Pezeshki et al. 2021). But here's what excites me: Kirichenko et al. 2023 showed both spurious AND core features ARE learned in the representation — the problem is at the classifier level!

This opens an entirely different angle: What if we could CHARACTERIZE the exact epoch when spurious features become dominant in classifier attention? Imagine tracking not just accuracy curves, but the RATIO of gradient magnitude flowing to spurious vs core features across training. We could identify a "shortcut crystallization point" — the moment when the classifier commits to the easy solution.

Here's my wild idea: What if there's a universal "danger zone" in training — perhaps 30-50% through — where interventions could redirect learning toward causal features? We could test this immediately on Waterbirds/ColoredMNIST by:
1. Training linear probes at each epoch to measure spurious vs core feature separability
2. Computing gradient flow ratios to different feature types
3. Looking for phase transitions in worst-group accuracy dynamics

Cross-domain insight from physics: This reminds me of critical phenomena — systems often exhibit sharp transitions. What if shortcut learning has a "critical epoch" analogous to phase transitions?

**Key Points:**
- Focus on WHEN (temporal dynamics), not just WHAT
- "Shortcut crystallization point" hypothesis — a critical epoch where shortcuts lock in
- Testable immediately using linear probes + gradient analysis on existing benchmarks

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's "shortcut crystallization point" is intriguing, but let me stress-test this. The evidence suggests we need precise operationalization before this becomes testable science.

First concern: How do we MEASURE "spurious feature dominance" without circular reasoning? If we train linear probes on frozen representations, we're measuring separability — but spurious features like background in Waterbirds may be MORE separable than bird shapes throughout training, not just at a "crystallization point."

What would disprove this hypothesis? If spurious feature probe accuracy rises monotonically without a phase transition, that would falsify the "critical epoch" claim. We need to define:
1. **Quantitative threshold:** What constitutes "crystallization"? A >X% drop in worst-group accuracy? A gradient ratio crossing Y?
2. **Temporal precision:** Epoch-level? Batch-level? The edge of stability phenomenon (Cohen et al. 2021) operates at sub-epoch timescales.
3. **Benchmark consistency:** Does the "danger zone" appear at the same relative training point across Waterbirds, CelebA, AND ColoredMNIST?

A concrete falsifiable prediction: "On Waterbirds with ResNet-50, worst-group accuracy will show a sharp (>10% in <5 epochs) decline between epochs 15-25 (out of 100), coinciding with spurious feature probe accuracy exceeding core feature probe accuracy."

**Key Points:**
- Need operational definitions: What EXACTLY constitutes "crystallization"?
- Falsification criterion: Monotonic rise without phase transition would disprove hypothesis
- Cross-benchmark consistency required for generalizability claim

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: What does this mean for the field if validated?

Prof. Vera's falsifiability concerns are valid, but let me add the significance lens. The existing literature establishes: (1) simplicity bias exists (Shah 2020), (2) gradient starvation perpetuates it (Pezeshki 2021), (3) representations contain both features (Kirichenko 2023). What's genuinely NEW here?

The contribution would be a **temporal characterization framework** — moving from static descriptions ("DNNs prefer simple features") to dynamic understanding ("shortcuts crystallize at epoch X under conditions Y"). This matters because:

1. **Intervention timing:** Current methods (DRO, JTT, DFR) apply corrections uniformly or post-hoc. Knowing the critical window enables targeted interventions at the precise moment.
2. **Theoretical unification:** Connecting simplicity bias + gradient starvation + edge of stability into a single temporal narrative would be a synthesis contribution.
3. **Practical impact:** Training schedules could be redesigned — perhaps "shortcut-aware learning rate decay" that increases regularization exactly when crystallization is detected.

However, I must temper enthusiasm: If the "danger zone" varies wildly across datasets/architectures, the practical utility diminishes. We need to establish whether this is a UNIVERSAL phenomenon or benchmark-specific.

**Key Points:**
- Genuine novelty: Moving from static to dynamic/temporal understanding
- Impact pathway: Enables precisely-timed interventions (not post-hoc corrections)
- Risk: If highly variable across settings, practical value is limited

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The theoretical mechanism is plausible, but what evidence supports that we can actually MEASURE this?

Technical feasibility check:
1. **Linear probe separability:** Straightforward. Train logistic regression on frozen embeddings at checkpoints. Existing code in DomainBed supports this. ✓
2. **Gradient flow ratios:** Trickier. We need to identify WHICH neurons/channels encode spurious vs core features, then track gradient magnitudes. Kirichenko et al.'s DFR paper suggests feature attribution methods could work, but this introduces noise.
3. **Phase transition detection:** Statistically meaningful transition detection requires dense checkpoint sampling (every epoch or finer), increasing storage/compute overhead.

Here's what worries me: The "crystallization point" may be a smooth crossover, not a sharp transition. Physical phase transitions require specific symmetry-breaking conditions. Neural network training loss landscapes may not have equivalent structure. We should hedge the hypothesis:

**Strong form:** Sharp phase transition exists at identifiable epoch.
**Weak form:** Gradual regime shift where spurious dominance accelerates.

The weak form is more likely true and still actionable. We can test both by measuring the SECOND DERIVATIVE of worst-group accuracy — sharp transitions show large negative second derivatives.

**Key Points:**
- Linear probes: feasible ✓. Gradient flow ratios: feasible but noisy. Phase detection: feasible with dense checkpoints.
- Physical phase transition analogy may be overstated — hedge with weak-form hypothesis
- Second derivative of worst-group accuracy as transition detector

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this against the concerns raised! Prof. Vera demands falsifiability, Dr. Sage asks about impact, Prof. Pax flags measurement challenges. Here's how we address all three:

**Addressing Vera's falsifiability:** The hypothesis becomes falsifiable with this prediction structure:
- **H1 (testable):** "The rate of worst-group accuracy decline accelerates during a localized training window (the 'shortcut crystallization zone'), identifiable via second derivative analysis."
- **Falsification:** If worst-group accuracy decline is constant-rate throughout training (linear decay), H1 is false.
- **Success criterion:** Statistically significant negative peak in d²(WGA)/d(epoch)² within the first 50% of training, present in ≥2/3 benchmarks.

**Addressing Sage's impact:** The unified temporal framework enables:
1. **Shortcut Detection Metric:** The second derivative signal itself becomes an early-warning indicator.
2. **Intervention Trigger:** When d²(WGA)/d(epoch)² drops below threshold, increase regularization or switch to group-balanced sampling.
3. **Architecture-agnostic:** Test on ResNet-50, ViT-B/16 to show generality.

**Addressing Pax's feasibility:** Prof. Pax is right that sharp transitions may not exist. But the weak form (accelerating regime shift) is EQUALLY useful practically. We measure:
- **Primary DV:** Worst-group accuracy trajectory (directly from existing benchmarks)
- **Secondary DV:** Linear probe accuracy for spurious vs core features
- **Mechanism signal:** Gradient ratio (optional, for mechanistic understanding)

**Key Points:**
- Second derivative of WGA as the core metric — falsifiable, measurable
- Success criterion: Significant negative d²(WGA)/d² peak in ≥2/3 benchmarks
- Weak form (accelerating decline) equally actionable for intervention timing

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down: Dr. Ally's refinements are solid, but I see three remaining holes.

**Hole 1: Confound — learning rate schedule.** Standard training uses decaying LR. A "crystallization point" might simply reflect LR decay crossing a threshold, not intrinsic shortcut dynamics. Control: Compare constant LR vs. decaying LR schedules. The crystallization signal should persist with constant LR to claim it's intrinsic.

**Hole 2: What assumption is unstated?** We're assuming spurious features have HIGHER initial gradient signal. But what if they have SIMILAR signal initially, and crystallization reflects cumulative feedback? The mechanism matters for intervention design.

**Hole 3: Sample size for transition detection.** Second derivative estimation requires smoothing, which obscures sharp transitions. We need to specify the smoothing window (e.g., 5-epoch rolling average) and test sensitivity to this choice.

What would convince me this is valid:
1. Crystallization effect persists under constant LR.
2. Effect replicates across 3 benchmarks with consistent relative timing (e.g., always 20-40% through training).
3. Effect size is large enough to be practically useful (>5% WGA difference if intervened vs. not).

Show me data addressing these, and I'll be convinced.

**Key Points:**
- Confound: LR schedule decay may masquerade as crystallization — need constant LR control
- Unstated assumption: Why do spurious features get early gradient dominance?
- Sensitivity test: Second derivative estimation requires specified smoothing parameters

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges are excellent — this is how hypotheses get sharpened! Let me address and synthesize.

The LR confound is real. BUT — this actually strengthens our hypothesis framing! If crystallization timing correlates with LR schedule, that's USEFUL information: it means interventions should be timed relative to LR schedule phases, not absolute epochs. We test both:
- **Experiment A:** Fixed LR — test if intrinsic crystallization exists
- **Experiment B:** Standard decaying LR — test if schedule modulates timing

For the mechanism question: Simplicity bias (Shah 2020) already explains WHY spurious features dominate early — they're more linearly separable initially. Gradient starvation (Pezeshki 2021) explains the FEEDBACK loop. Our contribution isn't re-proving these mechanisms — it's QUANTIFYING their temporal dynamics on standard benchmarks.

Final synthesized hypothesis:

**Core claim:** Under standard SGD training on spurious-correlation benchmarks, there exists a localized training phase (the "shortcut crystallization zone") where the classifier's reliance on spurious features accelerates, detectable via second-derivative analysis of worst-group accuracy.

**Mechanism:** Simplicity bias creates early spurious feature advantage; gradient starvation amplifies it; crystallization marks when feedback loop dominance becomes self-reinforcing.

**Predictions:**
1. d²(WGA)/d(epoch)² shows significant negative peak in first 50% of training (Waterbirds, CelebA, ColoredMNIST)
2. Effect persists under constant LR (intrinsic, not schedule artifact)
3. Peak timing is benchmark-relative (not absolute epoch), appearing at 20-40% of training duration

**Key Points:**
- LR schedule as modulator, not confounder — test both fixed and decaying
- Mechanism already established in literature; we quantify temporal dynamics
- Three testable predictions with clear success/failure criteria

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The temporal framing ("when" not just "what") is genuinely novel. Moving from static descriptions of simplicity bias to quantifiable dynamic signatures represents a paradigm shift in how we study shortcut learning. The "crystallization zone" concept is original.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is now properly falsifiable. Specific predictions (second derivative peak in first 50% of training, persistence under constant LR, consistency across 3 benchmarks) provide clear success/failure criteria. The weak-form hedge (accelerating decline) ensures we capture reality even without sharp transitions.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This matters for two reasons: (1) practical utility — knowing crystallization timing enables intervention design, and (2) theoretical unification — connecting simplicity bias, gradient starvation, and edge-of-stability into a temporal narrative. Publication potential in top ML venues.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All measurements are technically sound and achievable with existing tools. Worst-group accuracy: direct from benchmarks. Linear probes: standard practice. Second derivative: straightforward calculus with appropriate smoothing. Dense checkpoints increase storage but remain tractable. No fundamental barriers.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis is: **Under standard SGD training on spurious-correlation benchmarks (Waterbirds, CelebA, ColoredMNIST), there exists a localized training phase — the "Shortcut Crystallization Zone" — where the classifier's reliance on spurious features accelerates, detectable via second-derivative analysis of worst-group accuracy.**

The causal mechanism: Simplicity bias creates initial spurious feature advantage (Shah 2020); gradient starvation amplifies through feedback loop (Pezeshki 2021); crystallization marks the point where this feedback becomes self-reinforcing and difficult to reverse.

Core predictions:
1. **P1 (Primary):** The second derivative of worst-group accuracy (d²WGA/dt²) shows a statistically significant negative peak during the first 50% of training on all three benchmarks.
2. **P2:** This crystallization effect persists under constant learning rate training (not an LR schedule artifact).
3. **P3:** The crystallization zone timing is benchmark-relative (appearing at 20-40% of total training duration), not absolute-epoch-dependent.

Experimental approach: Train ResNet-50 on Waterbirds/CelebA/ColoredMNIST with dense checkpointing (every epoch). Compute worst-group accuracy at each checkpoint. Apply 5-epoch rolling average smoothing, compute second derivative, test for significant negative peak in first 50% of training. Repeat with constant LR to control for schedule confound.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- **Concern 1:** Smoothing window choice (5-epoch) is somewhat arbitrary; sensitivity analysis needed
- **Concern 2:** Three benchmarks may not establish universality; future work should extend to CivilComments (NLP)
- **Mitigation Strategy:** Report results across multiple smoothing windows (3, 5, 7 epochs); acknowledge benchmark-specific variations; frame as "characterization study" rather than "universal law"

---

