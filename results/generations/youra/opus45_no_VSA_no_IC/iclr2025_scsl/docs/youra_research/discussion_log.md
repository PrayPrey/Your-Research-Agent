# Phase 2A Discussion Log

**Gap ID:** gap-1
**Gap Title:** Unified Compression Pipeline Optimization
**Generated:** 2026-08-25
**Mode:** UNATTENDED Self-Play

---

## Briefing Context

**Research Gap:** Current model compression techniques (pruning, quantization, distillation) exist separately. Joint approaches emerging but not standardized. Ordering effects under-explored.

**Missing Piece:** Principled framework for optimal compression ordering, layer-specific strategies, combined technique interactions.

**Impact:** HIGH - 50-80% size reduction with <1% accuracy loss possible

**Key Evidence:**
- Prune-Quantize-Distill (arXiv 2604.04988): Ordered pipeline emerging
- Joint Pruning+Quant (arXiv 2502.16638): Joint training possible
- Pruning vs Quantization (arXiv 2307.02973): No clear winner
- intel/neural-compressor: Multi-technique, no unified ordering
- microsoft/geta: Joint framework, limited archs

---

### Previous Failure / Routing Context

**CRITICAL: Prior Failure Record (h-m2 Run 1)**

- **Status:** FAIL
- **Failure Type:** COMPUTATIONAL_INFEASIBILITY
- **Root Cause:** Hessian eigenvector computation using Lanczos iteration too slow for ResNet-50 (~23M params). Each checkpoint required 2-3+ minutes for eigenvector computation.

**What NOT To Do:**
- Do NOT attempt full Lanczos on ResNet-50+ models
- Do NOT schedule Hessian analysis within standard timeout windows
- Do NOT assume pytorch-hessian-eigenthings runs quickly

**What Showed Promise:**
- Training loop works correctly
- Gradient direction computation is fast
- Checkpoint saving/loading works
- Probe training is efficient

**Required Pivots:**
- Use ResNet-18 or smaller backbone for any curvature analysis
- Use power iteration instead of full Lanczos
- Consider gradient-only proxy metrics (no Hessian)
- Sample fewer checkpoints

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach compression ordering not as a fixed pipeline but as a LEARNABLE sequence? The papers show pruning-then-quantization and quantization-then-pruning give different results — but nobody's asking the meta-question: can we predict optimal ordering from architecture features?

Here's my wild idea: **Architecture-Aware Compression Sequencing (AACS)**. Instead of one-size-fits-all ordering, we learn a lightweight predictor that examines layer properties (parameter count, activation statistics, gradient norms) and recommends compression order per-layer or per-block.

Cross-domain connection: This mirrors neural architecture search (NAS) — but instead of searching architectures, we're searching compression sequences. The search space is tractable because compression techniques are finite (prune, quantize, distill, their orderings).

Given our prior failure with Hessian methods on large models, I propose using gradient-only features. Gradient norms and activation statistics are cheap to compute — no eigendecomposition needed.

**Key Points:**
- Transform fixed pipeline into learnable sequence prediction
- Use gradient-only features (avoiding costly Hessian computation)
- Per-layer optimization rather than global ordering

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing direction, but let me stress-test this. The core claim needs precision: What exactly predicts optimal compression ordering?

For testability, we need:
1. **Clear metric**: What defines "optimal"? Accuracy retention per compression ratio? Pareto frontier distance?
2. **Falsifiable prediction**: "For architectures with property X, order A outperforms order B by >Y%"
3. **Control conditions**: Same total compression, different orderings, isolated from confounds

The gradient-only feature approach is smart given h-m2's failure, but we need specific predictions. I propose: "Layers with high gradient variance benefit more from quantization-first, while layers with sparse gradients benefit from pruning-first."

What would disprove this? If ordering has no systematic relationship with gradient statistics across multiple architectures.

**Key Points:**
- Define "optimal" precisely (Pareto frontier position?)
- Need specific, falsifiable predictions about ordering-feature relationships
- Control experiments isolating ordering effects from magnitude effects

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question I must ask: Does this genuinely advance the field, or is it incremental engineering?

Looking at the evidence: intel/neural-compressor exists with multi-technique support but "no unified ordering." GETA proposes joint training but on "limited archs." The gap is real — nobody has a principled, architecture-aware framework.

If AACS works, the contribution is: **Transforming compression from art to science**. Currently practitioners try orderings empirically. A predictive framework changes the game.

However, the bar is high. The field has seen many "learned X" papers that show modest gains. To matter, AACS must demonstrate:
1. Predictions generalize across architecture families (CNNs, Transformers, MLPs)
2. Overhead of prediction is negligible vs. trial-and-error
3. Meaningful gap over random/default ordering

What new research directions does this open? If successful: automated compression for edge deployment, theoretical understanding of technique interactions.

**Key Points:**
- Genuine gap exists (no principled ordering framework)
- Impact depends on generalization across architecture families
- Opens automated compression pipelines for deployment

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in reality. The mechanism proposed: lightweight predictor using gradient/activation features predicting optimal compression order.

Technical feasibility analysis:
1. **Feature computation**: Gradient norms, activation statistics — YES, these are cheap. A forward-backward pass gives everything needed.
2. **Predictor model**: Can be tiny (linear classifier, small MLP). No computational barrier.
3. **Ground truth labels**: HERE's the challenge. To train a predictor, we need examples of "optimal orderings" — which requires actually trying multiple orderings on many models.

The fundamental question: Is there SIGNAL in the features? This is empirically testable. We can compute features, try orderings, and measure correlation without building the full predictor.

Given h-m2's lesson, I approve using gradient-only features. No Hessian = no timeout risk.

Remaining concern: "Optimal" may be highly dataset-dependent, not just architecture-dependent. The predictor might need task context too.

**Key Points:**
- Feature computation is cheap (gradient norms, activation stats)
- Ground truth generation requires exhaustive ordering trials
- Core feasibility question: Is there signal in features?
- May need task/dataset context, not just architecture features

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Building on all perspectives, let me synthesize and strengthen. Prof. Pax identifies the core question: "Is there signal?" This is actually GREAT — it's a clear, testable sub-hypothesis.

Refined hypothesis structure:
- **H1 (Existence)**: Compression ordering effects are systematic (not random)
- **H2 (Mechanism)**: Layer-level features predict optimal ordering
- **H3 (Comparison)**: Predicted ordering outperforms default/random

To address Prof. Pax's ground truth concern: We don't need exhaustive search. We can sample strategically — compare the 6 permutations of {prune, quantize, distill} on a small set of diverse architectures. If ordering effects are large (>2% accuracy difference), signal exists.

To address Dr. Sage's generalization concern: Start with one architecture family (CNNs), demonstrate the principle, then test transfer to Transformers. This is standard practice.

Avoiding h-m2's failure: ALL features are first-order (gradients, activations). No second-order (Hessian). Using ResNet-18 for initial validation, not ResNet-50.

**Key Points:**
- Break into testable sub-hypotheses (existence, mechanism, comparison)
- Ground truth: Strategic sampling of 6 orderings, not exhaustive
- Start with CNNs, test transfer to Transformers
- First-order features only, ResNet-18 for validation

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down:

1. **The "optimal" problem**: Optimal for what? Accuracy at fixed size? Size at fixed accuracy? The Pareto frontier is multi-dimensional. Different orderings may dominate at different operating points.

2. **Interaction effects**: Pruning changes weight distributions, affecting quantization ranges. Quantization introduces noise, affecting pruning importance scores. These interact non-linearly. A linear predictor using pre-compression features may miss this.

3. **The distillation wildcard**: Distillation requires a teacher. Does ordering matter relative to when distillation is applied? This adds complexity.

What would convince me:
- Clear definition: "Optimal" = best accuracy at 4x compression ratio
- Evidence: Ordering effects are large (>2% accuracy) and CONSISTENT across seeds
- Mechanism: Features predict ordering with >70% accuracy on held-out architectures

The hypothesis is worth testing, but needs tighter specification.

**Key Points:**
- "Optimal" needs single operating point definition (e.g., 4x compression)
- Interaction effects may defeat simple predictors
- Distillation adds complexity (teacher dependency)
- Need consistency across seeds, generalization across architectures

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's challenges sharpen the hypothesis! Let me propose a refinement that addresses the concerns:

**SIMPLIFIED SCOPE**: Focus on pruning vs. quantization ordering ONLY. Drop distillation for now — it's a confound. This gives us 2 orderings to compare, not 6.

**FIXED OPERATING POINT**: Define optimal as "highest accuracy at 50% parameter reduction + INT8 quantization." Single point, no Pareto ambiguity.

**THE MECHANISM HYPOTHESIS**: The key insight from the papers — pruning removes parameters, changing weight statistics. Quantization bins weights, losing precision. If a layer has many near-zero weights, prune first (removes noise). If weights are well-separated, quantize first (preserves structure).

Testable prediction: **Layers with high weight sparsity (many near-zero) benefit from prune-first. Layers with bimodal weight distributions benefit from quantize-first.**

This is falsifiable, measurable, and requires no Hessian computation.

**Key Points:**
- Simplify to prune vs. quantize only (drop distillation)
- Fixed operating point: 50% param reduction + INT8
- Mechanism: Weight distribution statistics predict ordering preference
- Testable via weight histogram analysis

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

NOW we have something testable. Let me formalize:

**Core Hypothesis (H-AACS-v1)**:
- **Under:** Standard CNN architectures (ResNet-18/34)
- **If:** We measure pre-compression weight distribution statistics (sparsity, kurtosis)
- **Then:** We can predict whether prune-first or quantize-first yields higher accuracy at 50%+INT8
- **Because:** Sparsity indicates noise-dominated weights (prune first), bimodality indicates structure (quantize first)

**Falsification criteria:**
- If ordering preference shows no correlation with weight statistics (r < 0.3)
- If prediction accuracy < 55% (barely above random)
- If effect size < 1% accuracy difference (not practically significant)

**Experiment design:**
1. Take ResNet-18 pretrained on ImageNet
2. For each layer: compute weight sparsity, kurtosis
3. Apply both orderings (P-then-Q, Q-then-P) at 50%+INT8
4. Measure per-layer contribution to accuracy delta
5. Correlate features with ordering preference

This requires: ~2 hours training, no Hessian, using existing benchmarks.

**Key Points:**
- Formalized Under-If-Then-Because structure
- Clear falsification: r<0.3, accuracy<55%, effect<1%
- Experiment uses existing datasets/benchmarks
- Computationally feasible (~2 hours, no Hessian)

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me verify technical feasibility of this refined proposal:

**Feature computation:**
- Weight sparsity: `(weights.abs() < threshold).mean()` — O(n), trivial
- Kurtosis: `scipy.stats.kurtosis(weights)` — O(n), trivial
- Both computed pre-compression, no training needed

**Compression implementation:**
- Pruning: Magnitude-based unstructured pruning — standard, well-supported
- Quantization: Post-training INT8 — standard in PyTorch/ONNX
- Both orderings implementable in <100 lines

**Measurement:**
- Per-layer accuracy contribution — this is the tricky part
- Option 1: Layer-wise ablation (expensive)
- Option 2: Compare full-model accuracy across orderings, attribute to layer features statistically
- Option 2 is feasible

**Timeline:** ResNet-18 on ImageNet subset (10% for speed), 2 orderings, 3 seeds = 6 runs. Each run ~1 hour on single GPU. Total: <10 hours.

**Verdict:** Technically feasible. No fundamental barriers. The hypothesis is tight and testable.

**Key Points:**
- Feature computation is O(n), trivial
- Compression techniques are standard, well-supported
- Use statistical attribution, not per-layer ablation
- Total compute: <10 GPU-hours, well within feasibility

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

Assessing refined hypothesis impact:

**Contribution clarity:** We're testing whether pre-compression weight statistics predict optimal prune/quantize ordering. This is NOVEL — the cited papers compare orderings but don't predict them from features.

**Generalization path:** Start with ResNet-18, extend to ResNet-34/50, then test Transformers. The mechanism (weight distribution statistics) should transfer because all DNNs have weights.

**If hypothesis FAILS:**
- Contribution: "Ordering effects exist but are not predictable from static features"
- Still publishable: Negative result with rigorous methodology
- Opens question: What DOES predict ordering?

**If hypothesis SUCCEEDS:**
- Contribution: First predictive framework for compression ordering
- Impact: Automated compression pipeline selection
- Extensions: Add more techniques, more architectures, online adaptation

Either outcome advances knowledge. The hypothesis is well-scoped for a single experiment.

**Key Points:**
- Novel: Prediction of ordering from features (not just comparison)
- Publishable either way (positive or negative result)
- Clear extension path (more techniques, architectures)
- Well-scoped for single rigorous experiment

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis transforms compression ordering from empirical trial-and-error to predictive science. Cross-pollination from NAS (learnable search) to compression (learnable ordering) is creative. Using weight statistics as features is simple but unexplored in this context.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Clear falsification criteria (r<0.3, accuracy<55%, effect<1%). Experiment design is rigorous with controlled variables. Statistical correlation approach avoids confounds. The hypothesis is maximally testable.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE
- **Assessment:** Genuine contribution if successful — first predictive ordering framework. But scope is limited (prune/quantize only, CNNs). Impact depends on generalization to more techniques and architectures. Publishable either way.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All computations are O(n) with standard libraries. No Hessian, no eigendecomposition. ResNet-18 on ImageNet subset keeps runtime under 10 hours. Technical barriers are zero.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on **H-AACS-v1: Architecture-Aware Compression Sequencing**. The core claim is that pre-compression weight distribution statistics (sparsity, kurtosis) can predict whether pruning-first or quantization-first yields better accuracy at a fixed operating point (50% parameter reduction + INT8).

The mechanism posits that sparse-weight layers have noise-dominated magnitudes that pruning removes efficiently, while bimodally-distributed weight layers have structure that quantization preserves better. This creates a layer-specific ordering preference detectable from cheap-to-compute features.

The experimental approach uses ResNet-18 pretrained on ImageNet, computes weight features per layer, applies both orderings, and correlates features with ordering preference using statistical methods. Total compute is under 10 GPU-hours. Falsification is clear: if correlation < 0.3 or prediction accuracy < 55%, the hypothesis fails.

This avoids h-m2's failure mode entirely — no Hessian computation, gradient-only features, small model (ResNet-18), and well under timeout windows.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Interaction effects between layers may confound per-layer analysis. A layer's ordering preference may depend on neighboring layers' choices.
- The 50%+INT8 operating point is arbitrary. Findings may not generalize to other compression levels.
- Weight statistics are static. Dynamic features (activations during inference) might be more predictive.
- **Mitigation Strategy:** Start with the static approach. If successful, extend to dynamic features. If interactions matter, move to block-level rather than layer-level analysis. Report operating-point sensitivity in analysis.
