# Phase 2A: Research Discussion Log

**Date:** 2026-08-29
**Gap ID:** gap-1
**Gap Title:** Cross-Architecture Distillation Methodology
**Architecture:** Self-Play Tikitaka (Claude-only, independent-controller ablation)

---

## Briefing

### Research Gap

**Gap 1: Cross-Architecture Distillation Methodology**

- **Relevance:** PRIMARY
- **Impact:** HIGH - Core blocker
- **Current State:** DistilBERT distills within same architecture family. Mamba-2 proves duality but no distillation methodology exists.
- **Missing Piece:** Method for mapping Transformer attention to SSM state matrices during distillation.

### Key Research Question

Can knowledge distillation from pre-trained Transformers to sub-quadratic architectures (Mamba, RWKV, RetNet) achieve comparable downstream task performance while maintaining linear-time inference complexity?

### Theoretical Foundation

- **Mamba-2 (2024):** Proves Transformer-SSM duality theoretically
- **DistilBERT (2019):** Soft-target distillation methodology (same-architecture only)

### Available Resources

- state-spaces/mamba (10K+ stars) - Official Mamba, CUDA kernels
- BlinkDL/RWKV-LM (11K+ stars) - Official RWKV
- microsoft/torchscale (2K+ stars) - Contains RetNet
- LongBench benchmark (4K-128K context evaluation)

### Feasibility Constraints (Pipeline-Enforced)

- Must use **existing real datasets and existing benchmarks**
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data
- No human evaluation or annotation

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the entire distillation paradigm on its head? Instead of trying to force Transformer attention patterns into SSM state matrices—which feels like cramming a square peg into a round hole—we leverage Mamba-2's theoretical duality proof to create a *principled translation layer*.

Here's what excites me: Mamba-2 showed that attention and selective SSM are mathematically equivalent under certain conditions. What if we don't distill the *representations* but rather distill the *computational trajectory*? Think about it—attention computes a weighted sum over all positions, while SSM maintains a compressed state. But Mamba-2 proves these can compute the same function!

I see three unconventional angles worth exploring:

1. **Trajectory Matching:** Instead of matching hidden states layer-by-layer (what DistilBERT does), match the *dynamics*—how information flows through the network. Train the SSM to produce the same output trajectories as the Transformer when given identical inputs.

2. **Attention-to-State Projection:** Use the Mamba-2 duality to derive an analytical mapping. If A·B = Attention, can we solve for the SSM parameters (A, B, C, D matrices) that reproduce it? This would be distillation through mathematical translation, not gradient-based learning!

3. **Hybrid Progressive Distillation:** Start with a hybrid model (Transformer layers + SSM layers), then progressively *convert* Transformer layers to SSM using the duality, while fine-tuning on soft targets. The conversion uses theory; the fine-tuning fixes practical gaps.

**Key Points:**
- Mamba-2 duality isn't just theoretical—it's a *recipe* for principled conversion
- Trajectory matching may preserve long-context behavior better than state matching
- Analytical conversion + gradient refinement could be faster than pure distillation

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but let me apply some scientific rigor here. The Mamba-2 duality proof has specific conditions that must hold—it's not a universal equivalence. Before we design experiments, we need to understand exactly *when* the translation is theoretically valid.

Let me stress-test each proposal:

**On Trajectory Matching:** This is testable, but we need precise definitions. What exactly is a "trajectory"? If we mean the sequence of hidden states h₁, h₂, ..., hₙ, then we're back to state matching. If we mean input-output behavior, that's functional equivalence—but Transformers and SSMs may achieve it through entirely different internal representations. The question becomes: *What specific metric defines trajectory similarity, and what threshold indicates successful distillation?*

**On Analytical Conversion:** The Mamba-2 duality shows that for *specific configurations*, attention can be expressed as SSM operations. But real pretrained Transformers have learned attention patterns that may not fall within this tractable subset. We need to quantify: *What percentage of a pretrained Transformer's attention patterns can be analytically converted vs. require approximation?*

**On Hybrid Progressive:** This is the most testable. We can measure performance at each conversion step. But the key falsification test is: *Does progressive conversion preserve long-context capabilities, or does each step degrade them?*

For any hypothesis we choose, I propose this falsification criterion: **If distilled SSM performance drops more than 5% relative to the teacher Transformer on LongBench at 8K+ context lengths, while the same teacher-student gap is <2% at 2K context, the distillation methodology fails to preserve long-context reasoning.**

**Key Points:**
- Mamba-2 duality has conditions—we must verify they hold for real pretrained models
- Define "trajectory similarity" with a measurable metric before claiming success
- LongBench performance gap at different context lengths is the acid test

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what makes any of these approaches a genuine *contribution* rather than an engineering exercise?

I've reviewed hundreds of distillation papers. DistilBERT succeeded because it established that 6 layers can match 12 layers at 97% performance—a clear, reproducible claim. What's the equivalent claim here?

Let me evaluate the three proposals against contribution criteria:

**Trajectory Matching:** Potentially significant if it demonstrates that *dynamics preservation* matters more than *state preservation* for cross-architecture transfer. This would be a new finding with implications beyond just Transformer→SSM. But without theory explaining *why* dynamics matter, it's empirical observation, not scientific contribution.

**Analytical Conversion:** This is where the real contribution lies. If we can derive closed-form SSM parameters from attention weights, that's a theoretical contribution that others can build on. It would answer: "What mathematical structure must be preserved when converting attention to SSM?" That's publishable regardless of downstream performance.

**Hybrid Progressive:** Engineering contribution only, unless we discover something unexpected—like certain layer types convert better than others, or conversion order matters fundamentally. Without such findings, it's ablation, not innovation.

My recommendation: **Focus on the analytical conversion angle.** Even partial success (converting 60% of attention heads analytically, fine-tuning the rest) advances the field. The research question becomes: "What properties of attention patterns determine whether they can be exactly converted to SSM operations, and what approximation errors occur when exact conversion is impossible?"

**Key Points:**
- Contribution must be theoretical or demonstrate new understanding, not just engineering
- Analytical conversion offers the clearest path to scientific contribution
- The key question is *what* can be converted exactly vs. what requires approximation

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what's actually achievable here. I'm seeing some elegant theory, but theory doesn't run on GPUs.

**Technical Feasibility Analysis:**

**Analytical Conversion:** Mamba-2's duality proof relies on specific parameterizations. The Δ, A, B, C matrices in Mamba have constrained forms (diagonal A, low-rank B, etc.). Real attention weights don't have these constraints. Deriving SSM parameters from arbitrary attention matrices is an *underdetermined system*—there are infinitely many SSM configurations that could approximate a given attention pattern.

However, this isn't fatal. We can formulate it as an optimization: find SSM parameters that minimize the reconstruction error of attention outputs. This is well-posed and computationally tractable.

**Trajectory Matching:** Technically feasible. We're essentially doing sequence-to-sequence distillation where the loss is computed on hidden state sequences. The main question is whether gradient signal is strong enough when matching entire trajectories rather than individual states.

**Hybrid Progressive:** Most straightforward. We can literally use Mamba-2's architecture (which interleaves attention and SSM blocks) and train to remove attention blocks one at a time. Each step is a standard fine-tuning run.

**Measurement Validity:** All three approaches can be evaluated on LongBench—that's an existing benchmark with established metrics. No new benchmarks needed.

**Fundamental Barriers:**

1. **State dimension mismatch:** Transformer hidden dim (e.g., 768) vs SSM state expansion (e.g., 16x) creates a representation bottleneck.
2. **Positional encoding:** Transformers use absolute/relative position embeddings. SSMs use recurrence. How to transfer positional knowledge is non-obvious.

Both barriers are addressable through architecture choices, not fundamental impossibilities.

**Key Points:**
- Analytical conversion is underdetermined but can be posed as optimization
- State dimension mismatch and positional encoding transfer are the key technical challenges
- All approaches are measurable with existing benchmarks (LongBench)

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES! I see a coherent hypothesis emerging from this discussion. Let me synthesize and strengthen it.

We're converging on **Analytical-Conversion-with-Gradient-Refinement**: derive initial SSM parameters from attention weights using Mamba-2 duality principles, then fine-tune to close the gap. This combines Dr. Nova's theoretical insight, Prof. Vera's falsifiability demands, Dr. Sage's contribution clarity, and Prof. Pax's feasibility grounding.

Let me strengthen against the concerns raised:

**Addressing the Underdetermined System (Prof. Pax):** The analytical conversion doesn't need to be *exact*. We formulate it as: given attention weights W_Q, W_K, W_V, find SSM parameters (A, B, C, Δ) that minimize ||Attention(X) - SSM(X)||² over a calibration dataset. This is a well-posed optimization problem. The theoretical contribution is characterizing *when* this approximation is tight vs. loose.

**Addressing Contribution Concern (Dr. Sage):** Our core claim is: "The approximation error of attention-to-SSM conversion is predictable from attention pattern statistics (entropy, sparsity, locality)." This is testable and generalizable—if true, practitioners know which attention heads convert well and which need more fine-tuning.

**Addressing Falsifiability (Prof. Vera):** We adopt your criterion. Additionally: "If attention patterns with high entropy (>2.5 nats) have conversion error >2x that of low-entropy patterns, the predictability claim is supported."

**Handling State Dimension (Prof. Pax):** Use the teacher's hidden dimension as the SSM state dimension. Mamba-2 allows this flexibility. The state expansion factor becomes a hyperparameter to study, not a barrier.

**Core Hypothesis (Strengthened):**

*Under standard NLP tasks (classification, QA, summarization), if attention patterns are analytically converted to SSM parameters using Mamba-2 duality-inspired optimization, then distilled SSM models achieve within 3% of teacher Transformer accuracy, because the conversion preserves the essential input-output mapping while enabling O(n) inference.*

**Key Points:**
- Analytical conversion + gradient refinement is the unified approach
- Approximation error predictability is the novel contribution
- Falsification: LongBench gap >5% at 8K context = methodology fails
- State dimension is a hyperparameter, not a barrier

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Let me be direct about the gaps I still see.

**Gap 1: The "Duality-Inspired Optimization" is Vague**

Dr. Ally says we minimize ||Attention(X) - SSM(X)||² but this glosses over critical details:
- Over what inputs X? Random? From training data? 
- At what layer? All layers simultaneously?
- How do we handle multi-head attention? Convert each head independently?

Without these details, "analytical conversion" is just rebranded distillation. Show me the algorithm.

**Gap 2: Calibration Dataset Dependency**

If we optimize SSM parameters on a calibration set, we're fitting to that distribution. What happens on out-of-distribution inputs? Long-context performance might degrade not because of architecture mismatch, but because calibration was on short sequences.

This is testable: calibrate on short sequences only, evaluate on LongBench. If performance drops >10%, the method lacks generalization.

**Gap 3: The 3% Threshold is Arbitrary**

Why 3%? DistilBERT achieves <3% degradation on GLUE, but that's same-architecture. Cross-architecture might inherently lose more information. What if the true theoretical limit is 5% for attention→SSM? Setting 3% as the bar might doom a valid methodology.

I'd accept: "Within 1.5x the degradation of same-architecture distillation (DistilBERT-like)" as a fairer threshold.

**Gap 4: No Comparison to Naive Baseline**

What if we just train Mamba from scratch on the teacher's outputs? If analytical conversion doesn't outperform this naive distillation baseline, the "duality-inspired" framing adds no value.

**What would convince me:**
1. Concrete algorithm with specified inputs, layer handling, and head conversion strategy
2. Calibration generalization test (short→long)
3. Comparison to naive distillation baseline
4. Threshold relative to same-architecture distillation, not absolute

**Key Points:**
- Algorithm details are missing—specify exactly how conversion works
- Calibration on short sequences must generalize to long context
- Success threshold should be relative to same-architecture baseline
- Must outperform naive output-matching distillation

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex, you're absolutely right—and this is exactly the constructive pressure we need. Let me sharpen the idea with concrete details.

**The Algorithm (Attention-to-SSM Conversion):**

For each attention head in layer l:
1. **Sample calibration inputs:** 1000 sequences from validation set (not training), varying lengths 512-4096 tokens
2. **Compute attention outputs:** A_l(X) = softmax(QK^T/√d)V for each sample
3. **Initialize SSM:** Use the closed-form Mamba-2 duality mapping as initialization: Δ = 1/seq_len, A = -exp(W_Q·W_K^T), B = W_V, C = W_O
4. **Optimize:** Fine-tune (A, B, C, Δ) to minimize ||A_l(X) - SSM_l(X)||² with gradient descent (100 steps, AdamW)
5. **Merge heads:** Concatenate converted SSMs, add a learned projection layer

**Multi-head handling:** Each head converts independently, then we learn a lightweight fusion layer (like multi-head SSM in Mamba-2).

**Calibration Generalization Test:** Brilliant idea. We include this as a required ablation:
- Calibrate on sequences ≤1024 tokens only
- Evaluate on LongBench at 4K, 8K, 16K
- If degradation at 8K is >2x degradation at 4K, flag as poor generalization

**Relative Threshold:** Agreed. New criterion: "Attention-to-SSM distillation should achieve ≤1.5x the performance gap of same-architecture DistilBERT-style distillation on matched model sizes."

**Naive Baseline Comparison:** Essential. We include:
- Baseline 1: Train Mamba from scratch on teacher soft labels (pure KD)
- Baseline 2: Our analytical conversion + refinement
- If Baseline 2 doesn't outperform Baseline 1 on LongBench, the duality-inspired conversion adds no value.

This addresses all of Prof. Rex's concerns with concrete, testable specifications.

**Key Points:**
- Algorithm specified: closed-form init + 100-step optimization per layer
- Multi-head handling: independent conversion + learned fusion
- Generalization test: calibrate short, evaluate long
- Must beat naive distillation baseline to claim contribution

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Now we have something testable. Let me formalize the experimental design.

**Hypothesis (Final Form):**

*H1: Attention-to-SSM conversion using duality-inspired initialization followed by layer-wise optimization achieves performance within 1.5x the degradation of same-architecture distillation, while reducing inference complexity from O(n²) to O(n).*

**Null Hypothesis:**

*H0: Attention-to-SSM conversion performance is statistically indistinguishable from naive output-matching distillation (no benefit from duality-inspired initialization).*

**Experimental Design:**

| Component | Specification |
|-----------|---------------|
| Teacher | BERT-base (12 layers, 768 dim) or GPT-2 (12 layers, 768 dim) |
| Student | Mamba-equivalent (12 SSM layers, 768 state dim) |
| Calibration | 1000 sequences, lengths 512-4096, from validation split |
| Training | Layer-wise conversion + 3 epochs full fine-tuning on task |
| Baselines | (1) Naive KD, (2) Same-arch distillation (DistilGPT-2) |

**Evaluation:**

| Benchmark | Metric | Success Criterion |
|-----------|--------|-------------------|
| GLUE (short) | Accuracy/F1 | ≤1.5x gap of same-arch KD |
| LongBench (4K) | Task accuracy | ≤1.5x gap of same-arch KD |
| LongBench (8K) | Task accuracy | ≤2x degradation vs 4K |
| Inference | Latency | <50% of teacher at 4K+ |

**Falsification Criteria:**

1. If duality-init equals naive KD (p>0.05, paired t-test), H0 accepted
2. If LongBench 8K degradation >3x vs 4K, generalization fails
3. If any metric >2x same-arch distillation gap, methodology insufficient

**Key Points:**
- H1 is now formally stated with measurable success criteria
- Null hypothesis enables statistical significance testing
- Three falsification criteria provide clear failure modes
- Existing benchmarks (GLUE, LongBench) used throughout

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

This has crystallized into a genuine contribution. Let me assess the final significance.

**What's New (Novelty Assessment):**

1. **First principled cross-architecture distillation method** using theoretical duality (Mamba-2 paper proves equivalence but doesn't provide conversion algorithm)
2. **Quantitative characterization** of which attention patterns convert well vs. poorly (entropy/sparsity analysis)
3. **Generalization analysis** of short-calibration-to-long-inference transfer

**Differentiation from Prior Work:**

| Prior Work | Our Contribution |
|------------|------------------|
| DistilBERT | Same-architecture only | Cross-architecture with duality |
| Mamba-2 | Proves duality | Operationalizes it for distillation |
| Naive KD | Black-box matching | Structure-preserving conversion |

**Impact Potential:**

- **Immediate:** Enables deployment of sub-quadratic models on long-context tasks without training from scratch
- **Methodological:** Establishes a template for cross-architecture transfer via theoretical bridges
- **Theoretical:** Quantifies the attention→SSM approximation gap

**Remaining Contribution Risk:**

The risk is that duality-inspired initialization provides only marginal improvement over naive KD. If the final performance gap between our method and naive baseline is <1% absolute, reviewers may question whether the complexity is justified.

**Mitigation:** Include compute cost comparison. If duality-init converges in 1/10th the training steps, that's a valid contribution even if final accuracy matches.

**Key Points:**
- First cross-architecture distillation using theoretical duality
- Clear differentiation from DistilBERT (same-arch) and Mamba-2 (theory-only)
- Include training efficiency comparison to strengthen contribution claim

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility sign-off. Let me verify this is implementable with existing resources.

**Implementation Checklist:**

| Requirement | Status | Source |
|-------------|--------|--------|
| Mamba codebase | ✓ Available | state-spaces/mamba (GitHub) |
| BERT/GPT-2 teacher | ✓ Available | HuggingFace Transformers |
| LongBench benchmark | ✓ Available | THUDM/LongBench (GitHub) |
| GLUE benchmark | ✓ Available | HuggingFace Datasets |
| Duality equations | ✓ Published | Mamba-2 paper, Section 3 |

**Technical Soundness:**

1. **Closed-form initialization:** Derivable from Mamba-2 equations. The mapping A = -exp(W_Q·W_K^T) is a reasonable first-order approximation (exponential ensures A is negative definite as required).

2. **Optimization tractability:** 100 gradient steps per layer × 12 layers = 1200 total steps. With batch size 32, calibration dataset 1000 samples, this is ~40 epochs through calibration data. Tractable.

3. **Memory:** Converting BERT-base to Mamba-base: 110M parameters each. Fits in 16GB GPU memory with gradient checkpointing.

**No Fundamental Barriers:**

- State dimension: 768 (matching BERT hidden dim)
- Positional encoding: SSM handles through recurrence; no explicit conversion needed
- Multi-head: Independent conversion + learned fusion (standard practice)

**Theoretical Validity:**

The hypothesis mechanism (duality-preserving conversion) is mathematically sound. The approximation quality depends on how well real attention patterns satisfy Mamba-2's duality conditions—which is exactly what the experiments will measure.

**Key Points:**
- All required codebases publicly available
- Conversion optimization is computationally tractable
- No fundamental barriers to implementation
- Hypothesis mechanism is theoretically valid

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We have convergence. Let me synthesize the final hypothesis.

**Emerged Hypothesis Summary:**

**Title:** Duality-Guided Cross-Architecture Distillation (DG-CAD)

**Core Claim:** Under standard NLP tasks, if Transformer attention layers are converted to SSM layers using Mamba-2 duality-inspired closed-form initialization followed by layer-wise optimization, then the resulting sub-quadratic model achieves performance within 1.5x the degradation of same-architecture distillation, because the duality-preserving initialization provides a strong starting point that reduces optimization difficulty and preserves long-context reasoning structure.

**Mechanism:**
1. For each attention head, derive initial SSM parameters using Mamba-2 duality equations
2. Optimize SSM parameters to minimize layer-wise reconstruction error on calibration set
3. Fine-tune full model on downstream task with soft labels from teacher

**Predictions:**
- P1: DG-CAD outperforms naive KD by ≥1% on LongBench at 8K context (primary)
- P2: Attention heads with entropy <2.0 nats convert with <5% reconstruction error
- P3: Calibration on 1K-token sequences generalizes to 8K with <2x degradation

**Experimental Design:**
- Teacher: BERT-base or GPT-2 (12 layers, 768 dim)
- Student: Mamba-12 (12 SSM layers, 768 state dim)
- Benchmarks: GLUE, LongBench (4K, 8K, 16K context)
- Baselines: Naive KD, Same-arch DistilBERT/DistilGPT-2

**Falsification:**
- If DG-CAD = Naive KD (p>0.05), duality initialization adds no value
- If LongBench 8K gap >3x LongBench 4K gap, generalization fails

**Key Points:**
- Hypothesis fully specified with mechanism, predictions, and falsification
- All benchmarks are existing (GLUE, LongBench)—no new evaluation needed
- Clear comparison baselines defined
- Ready for Phase 2B

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I'm satisfied. My concerns have been addressed:

1. **Algorithm specified:** Closed-form init + 100-step layer-wise optimization + fine-tuning
2. **Generalization test:** Short-calibration-to-long-inference included as P3
3. **Relative threshold:** 1.5x same-architecture gap, not arbitrary absolute
4. **Naive baseline:** Comparison to output-matching KD is required

**Remaining Concerns (Minor):**

1. **Entropy threshold (2.0 nats):** This number needs justification. We should compute entropy distribution over BERT attention heads first and set threshold at median.

2. **Calibration set size (1000):** May be insufficient for 768-dim SSM. Consider 5000 if memory allows.

**Mitigation Strategy:**
- Set entropy threshold dynamically based on per-model statistics (median entropy)
- Report results at both 1000 and 5000 calibration samples as ablation

These are minor refinements, not blockers. The hypothesis is ready for Phase 2B.

**Key Points:**
- All major concerns addressed
- Entropy threshold should be set from data, not a priori
- Calibration set size is an ablation, not a design flaw
- Hypothesis approved for Phase 2B

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** Duality-guided cross-architecture distillation is genuinely novel. While distillation and duality exist separately, their combination for Transformer→SSM conversion is unexplored. The analytical initialization approach differentiates from black-box distillation methods.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Hypothesis is fully falsifiable. Three clear failure criteria: (1) no improvement over naive KD, (2) poor short→long generalization, (3) gap exceeding 1.5x same-architecture distillation. All measurable with existing benchmarks.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This addresses a genuine gap in the literature. Mamba-2 proves duality but provides no transfer methodology. This work operationalizes the theory, enabling practical deployment of sub-quadratic models without full retraining.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are technically feasible. Required codebases (Mamba, Transformers) are publicly available. Optimization is tractable. No fundamental barriers to implementation—only engineering effort.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on **Duality-Guided Cross-Architecture Distillation (DG-CAD)**. The core insight is that Mamba-2's theoretical duality proof can be operationalized as a closed-form initialization for SSM parameters when converting Transformer attention layers. This initialization, followed by layer-wise optimization on a calibration set and fine-tuning on downstream tasks, should outperform naive output-matching distillation.

The mechanism is sound: duality-preserving initialization provides a better starting point in parameter space, reducing optimization difficulty and preserving the computational structure that enables long-context reasoning. The prediction is that this approach achieves performance within 1.5x the degradation of same-architecture distillation (DistilBERT-style) while reducing inference complexity from O(n²) to O(n).

Key design choices: (1) layer-wise conversion preserves gradient flow better than end-to-end, (2) calibration on varying-length sequences (512-4096) ensures generalization to longer contexts, (3) entropy-based attention pattern analysis provides interpretable failure mode detection.

Experimental validation will use BERT-base as teacher, Mamba-12 as student, evaluated on GLUE (short context) and LongBench (4K-16K context). Comparison baselines are naive knowledge distillation and same-architecture DistilBERT.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The entropy threshold (2.0 nats) needs empirical calibration from actual BERT attention patterns
- Calibration set size (1000 vs 5000) should be ablated
- **Mitigation Strategy:** Set entropy threshold at median of observed distribution; report both calibration sizes as ablation study

---


