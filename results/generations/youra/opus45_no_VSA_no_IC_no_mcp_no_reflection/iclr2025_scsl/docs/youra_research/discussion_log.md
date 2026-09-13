# Phase 2A Discussion Log

## Briefing

**Gap ID:** Gap-3-TrainingDynamics
**Gap Title:** Training Dynamics Exploitation for Robustification
**Research Question:** How can the temporal dynamics of spurious vs core feature learning be exploited as an intervention mechanism during training?

### Gap Context

**Current State:** Research shows spurious features learned faster than core features (simplicity bias). JTT uses this observation but only as a heuristic for sample identification, not as a principled intervention point.

**Missing Piece:** Methods that exploit the temporal dynamics of spurious vs core feature learning as an intervention mechanism (e.g., curriculum, staged training, gradient modification) rather than just observation.

**Supporting Evidence:**
- Shah et al. (2020) "Simplicity Bias" - Documents timing but not intervention
- Kirichenko et al. (2023) "DFR" - Post-training intervention, not dynamics-based
- Liu et al. (2021) "JTT" - Uses dynamics for sample ID, not direct intervention

### Feasibility Constraints (Pipeline-Enforced)
- Must use existing real datasets (Waterbirds, CelebA, WILDS)
- Must use existing benchmarks (worst-group accuracy)
- No new rubrics, no synthetic data, no human evaluation

### Available Papers
None prepared (MCP unavailable).

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the script entirely on how we think about simplicity bias? Everyone's been treating the early learning of spurious features as a problem to detect and correct. But what if it's actually an *opportunity*?

Here's my wild idea: What if we deliberately accelerate the spurious feature learning phase, let it saturate completely, and then "freeze" those neurons while forcing the network to learn something new for the remaining variance? It's like letting a child eat all their candy first so they have no choice but to eat vegetables next.

The papers tell us spurious features are learned early because they're "simpler" — lower-frequency patterns, higher signal-to-noise ratio in the training data. But nobody's asked: what happens to the loss landscape after spurious features are maximally exploited? My intuition says there's a second learning phase waiting to be discovered — a regime where the network HAS to find core features because the spurious ones can't explain the remaining errors.

This connects to something from neuroscience — the idea of "synaptic consolidation" where early-learned patterns get stabilized while new learning proceeds in parallel. What if we applied this to DNNs? Early stopping everyone talks about, but what about "early freezing followed by continued learning"?

**Key Points:**
- Reframe simplicity bias as opportunity, not obstacle
- Hypothesis: Saturate spurious feature learning, then freeze and continue
- Unexplored: Loss landscape dynamics AFTER spurious phase completes
- Cross-domain: Neuroscience synaptic consolidation as inspiration

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova raises an intriguing idea, but let's be precise about what we're claiming. "Saturate spurious features then freeze" is a mechanism proposal. What would disprove it?

First, we need operational definitions. When exactly has spurious feature learning "saturated"? I propose: saturation occurs when the model's accuracy on majority-group samples plateaus while minority-group accuracy remains low. This is measurable on Waterbirds/CelebA without new annotations — we use the existing group labels for evaluation only, not training.

Second, what does "freeze" mean mechanically? If we freeze entire layers, we lose capacity for core features. If we freeze specific neurons, we need a detection criterion. I suggest: freeze neurons with highest activation variance across majority-group samples, since spurious features should show high variance (background vs bird) while core features (bird shape) show lower variance.

The falsifiable prediction: If we freeze high-variance neurons at the point of majority-group saturation and continue training, worst-group accuracy should improve relative to standard training. If it doesn't, the hypothesis fails.

**Key Points:**
- Define "saturation" operationally: majority-group plateau + minority-group lag
- Freeze criterion: neurons with highest activation variance on majority group
- Falsifiable: frozen-then-continue must beat standard ERM on worst-group accuracy
- No new benchmarks needed — Waterbirds/CelebA suffice

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask: does this actually advance the field beyond JTT and DFR?

JTT already exploits early learning dynamics — it identifies "spurious-reliant" samples by their early correctness and upweights errors. DFR shows last-layer retraining captures core features. 🔭 Dr. Nova's "freeze then continue" is positioned between these: earlier intervention than DFR, different mechanism than JTT.

Here's what makes this genuinely new: JTT and DFR are both *reactive* — they wait for the problem to manifest (easy samples, or final representations) then correct. The "saturate-freeze-continue" approach is *proactive* — it deliberately induces a phase transition in the learning dynamics. That's a paradigm shift from "fix the spurious bias" to "engineer the training trajectory."

This matters because reactive approaches require multiple training runs (JTT) or held-out data with group labels (DFR). A single-run, dynamics-engineered approach would be more practical.

However, the contribution is incremental if freeze-then-continue simply replicates DFR's effect earlier. We need to show it learns DIFFERENT representations, not just faster.

**Key Points:**
- Novel positioning: proactive trajectory engineering vs reactive correction
- Must differentiate from JTT (sample-level) and DFR (representation-level)
- Contribution: single-run method without multiple training phases or held-out groups
- Risk: may just be "early DFR" — need representation analysis to distinguish

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The mechanism 🔭 Dr. Nova proposes has a fundamental technical challenge.

The claim is: freeze neurons that encode spurious features, then continue training to learn core features. But neurons in DNNs don't encode single features cleanly — they're distributed representations. Freezing "the background neurons" assumes we can identify which neurons correspond to which concepts, which is the core difficulty in interpretability research.

🔬 Prof. Vera's proposal — freeze high-variance neurons — is more tractable but has a flaw: high variance might also capture core feature variation (different bird species). We'd freeze the features we want to preserve.

Here's what worries me: the synaptic consolidation analogy from neuroscience assumes localized representations, which biological neurons have but artificial neurons typically don't. Can this work in principle?

I think YES, with a modification: instead of freezing neurons, freeze GRADIENT directions. Specifically, project gradients orthogonal to the spurious subspace. This is mathematically well-defined and doesn't require neuron-level interpretability. The spurious subspace can be estimated from majority-group samples.

**Key Points:**
- Neuron freezing assumes localized representations — DNNs have distributed ones
- High-variance criterion may freeze core features too
- Alternative: gradient projection orthogonal to spurious subspace
- This is technically feasible without interpretability assumptions

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this by synthesizing the proposals. Let me bridge the disagreements.

🔭 Dr. Nova's core insight remains valid: exploit the temporal separation between spurious and core feature learning. ⚙️ Prof. Pax correctly identifies that neuron-level freezing is problematic. The solution: freeze in *representation space*, not neuron space.

Here's the refined hypothesis:

**Gradient Subspace Freezing (GSF):** During early training (before majority-group saturation), identify the gradient subspace that primarily reduces loss on majority-group samples. After saturation, project all subsequent gradients orthogonal to this subspace. This forces the network to find new features — which must be core features — to reduce remaining loss.

This addresses:
- 🔬 Prof. Vera's falsifiability: worst-group accuracy improvement is the test
- 🎯 Dr. Sage's novelty: single-run, no sample identification, no held-out groups
- ⚙️ Prof. Pax's feasibility: gradient projection is mathematically tractable

The mechanism: early gradients encode "shortcuts to low loss" (spurious features). By orthogonalizing later gradients, we prevent reinforcement of these shortcuts and force exploration of the remaining loss landscape.

**Key Points:**
- Refined hypothesis: Gradient Subspace Freezing (GSF)
- Mechanism: early gradients define spurious subspace, later gradients projected orthogonal
- Single-run, no sample IDs, no held-out group labels needed
- Testable on existing benchmarks with existing metrics

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Show me the evidence that early gradients cleanly separate spurious from core features.

The assumption is: gradients in early training point toward spurious features, so orthogonalizing later gradients avoids them. But what if early gradients are a *mixture* of spurious and core directions? Then orthogonalizing throws away both.

Worse: Shah et al.'s simplicity bias shows spurious features are learned *first*, not *only*. Core features continue learning throughout training, just slower. If we orthogonalize at epoch T, we might cut off core feature gradients that were just starting to emerge.

My concrete concern: the "saturation point" 🔬 Prof. Vera defined (majority-group plateau) might occur BEFORE core feature gradients are distinguishable. We'd freeze everything important.

What would convince me: empirical evidence that early gradient subspace is primarily spurious. Specifically: project late-stage gradients onto early-stage subspace and show this projection correlates with spurious feature amplification, not core feature learning.

Also: what's the computational cost of maintaining gradient subspace estimates? If it doubles training time, this loses against just running JTT.

**Key Points:**
- Challenge: early gradients may mix spurious and core directions
- Timing problem: saturation point may precede core feature emergence
- Required evidence: early subspace projection correlates with spurious, not core
- Practical concern: computational overhead vs JTT baseline

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔍 Prof. Rex, you've identified the critical weakness — and it sparks a refinement! What if we don't freeze at a single saturation point, but *continuously* adapt the orthogonalization?

Here's the evolved idea: **Progressive Gradient Orthogonalization (PGO)**. Instead of one freeze point, we:
1. Maintain a running estimate of the "easy direction" subspace (gradients that rapidly reduce majority-group loss)
2. Continuously project new gradients partially orthogonal to this subspace
3. Increase the orthogonalization strength as training progresses

This addresses the timing problem: we don't need to identify the perfect saturation point. The method adapts continuously.

The computational cost is manageable: we're storing a low-rank approximation of cumulative gradients (similar to Adam's momentum), then doing a projection (matrix multiply). Comparable to optimizer state overhead.

🛡️ Dr. Ally, can you formalize this into testable predictions?

**Key Points:**
- Evolution: Progressive Gradient Orthogonalization (PGO) vs single-point GSF
- Addresses timing sensitivity through continuous adaptation
- Computational cost: comparable to Adam momentum storage
- Mechanism: "easy direction" subspace estimated continuously, orthogonalized progressively

---

### Exchange 8

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Now THAT's stronger! Let me formalize the hypothesis.

**Hypothesis: Progressive Gradient Orthogonalization (PGO)**

**Core Claim:** Under standard supervised classification with spurious correlations, if we progressively project training gradients orthogonal to the cumulative "easy gradient" subspace, then worst-group accuracy improves relative to ERM, because the model is forced to learn features that generalize beyond majority-group shortcuts.

**Variables:**
- IV: Orthogonalization strength schedule (none, linear increase, step increase)
- DV: Worst-group accuracy on held-out test set
- Controlled: Architecture, learning rate, batch size, dataset

**Mechanism (3 steps):**
1. Early training: Network follows "easy" gradients toward spurious features
2. PGO accumulates these directions into subspace S
3. Later gradients projected orthogonal to S → must find alternative (core) features

**Predictions:**
- P1 (Primary): PGO improves worst-group accuracy by ≥5% over ERM on Waterbirds
- P2: PGO matches or exceeds JTT without requiring two training runs
- P3: Representations from PGO show higher core-feature alignment (measured by probing)

**Falsification:** If PGO ≤ ERM on worst-group accuracy, or if PGO representations show LESS core feature alignment than ERM, hypothesis fails.

**Key Points:**
- Formalized as Under-If-Then-Because structure
- Three testable predictions with existing benchmarks
- Clear falsification criteria
- Feasible with Waterbirds/CelebA, worst-group accuracy metric

---

### Exchange 9

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests 🛡️ Dr. Ally's formalization is methodologically sound. Let me stress-test the experimental design.

**Confounds to control:**
1. Orthogonalization may simply reduce effective learning rate. Control: match final loss between PGO and ERM.
2. Low-rank subspace approximation quality varies. Control: report rank and reconstruction error.
3. "Easy gradient" subspace might collapse (become uninformative). Control: track subspace condition number.

**Success criteria for P1:**
- ≥5% worst-group accuracy improvement over ERM
- Statistical significance: p < 0.05 with 5 random seeds
- Effect persists across both Waterbirds and CelebA

**Success criteria for P3 (representation alignment):**
- Train linear probes for core features (bird type, hair color) and spurious features (background, gender)
- Core probe accuracy higher for PGO than ERM
- Spurious probe accuracy lower for PGO than ERM

This meets my standards for falsifiability and rigor.

**Key Points:**
- Three confounds identified with control strategies
- Statistical significance requirement: p < 0.05, 5 seeds
- P3 requires linear probe analysis for core vs spurious features
- Experimental design is complete and executable

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Okay, this could work. Let me verify the technical implementation is sound.

**Gradient subspace estimation:** Maintain rank-k SVD of cumulative gradients. Update incrementally using incremental SVD (O(nk²) per batch). With k=10-50 and standard batch sizes, this adds <10% overhead. Feasible.

**Projection operation:** Given subspace S (n×k matrix), project gradient g → g - S(S^T g). Single matrix multiply per batch. Negligible overhead.

**Memory:** Store k×n matrix for subspace. For ResNet-50, n ≈ 25M parameters. With k=50, that's 1.25B floats = 5GB. Within modern GPU memory. Feasible.

**Orthogonalization schedule:** Linear increase from 0 to α_max over T epochs. One hyperparameter (α_max) plus existing epochs. Manageable search space.

The fundamental barriers are addressable. Implementation is straightforward PyTorch: hook gradient computation, project, continue.

**Key Points:**
- Computational overhead: <10% training time
- Memory: ~5GB additional for rank-50 subspace on ResNet-50
- Implementation: gradient hook + SVD update + projection
- No fundamental barriers — technically feasible

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** PGO represents a paradigm shift from reactive correction (JTT, DFR) to proactive trajectory engineering. The continuous gradient orthogonalization is a genuinely new mechanism not present in prior work.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three clear predictions with quantitative success criteria. P1 (5% worst-group improvement) and P3 (probe analysis) provide direct falsification paths. Confounds identified with control strategies.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE-STRONG
- **Assessment:** Advances field by enabling single-run robustification without sample identification or held-out groups. Contribution is incremental if effect size is small. Strong if P2 (matches JTT) holds.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Implementation requires only gradient hooks and incremental SVD. <10% overhead, 5GB memory. No interpretability assumptions. Executable on existing hardware and datasets.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on **Progressive Gradient Orthogonalization (PGO)**: a method that continuously projects training gradients orthogonal to the cumulative "easy gradient" subspace. The core claim is that this forces networks to learn core features by blocking reinforcement of spurious shortcuts.

The mechanism operates in three phases: (1) early training accumulates gradient directions that rapidly reduce majority-group loss into subspace S, (2) progressive orthogonalization projects subsequent gradients away from S, (3) the network must find alternative features to reduce remaining loss — these are core features since spurious ones are already exploited.

Key predictions: PGO improves worst-group accuracy by ≥5% over ERM on Waterbirds (P1), matches JTT without two training runs (P2), and produces representations with higher core-feature alignment measurable via linear probes (P3).

The approach is feasible with <10% computational overhead and standard GPU memory. It requires no group annotations during training, no multiple training runs, and uses existing benchmarks (Waterbirds, CelebA, worst-group accuracy) for evaluation.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Early gradient subspace may still contain core feature directions — orthogonalization could harm early core learning
- Optimal rank k for subspace is dataset-dependent and may require tuning
- **Mitigation Strategy:** Ablate rank k (10, 25, 50) and orthogonalization schedules. Include "core feature gradient overlap" analysis to verify subspace is primarily spurious.

---

