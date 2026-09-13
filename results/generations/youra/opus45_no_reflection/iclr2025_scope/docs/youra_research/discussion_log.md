# Phase 2A Research Discussion Log

**Workflow:** phase2a-dialogue (Self-Contained Tikitaka Loop)
**Gap ID:** gap1
**Gap Title:** Systematic Comparison of Distillation Methods Across Sequence Lengths
**Started:** 2026-08-18T13:43:00Z

---

## Research Gap Briefing

### Gap Description
Multiple distillation methods exist (MOHAWK, CAB, T2MD, MambaInLlama) but are evaluated on different benchmarks, sequence lengths, and source models. No unified comparison exists.

**Missing Piece:** Head-to-head comparison of distillation strategies (MOHAWK vs CAB vs T2MD) on identical source model, using LongBench/SCROLLS at varying sequence lengths (4K, 8K, 16K, 32K).

**Potential Impact:** Practitioners would have clear guidance on which distillation method to use for their specific sequence length requirements.

### Available Papers

| ID | Paper | Key Contribution |
|----|-------|------------------|
| P1 | Mamba (Gu & Dao, 2023) | Selective SSM with input-dependent parameters, 5x Transformer throughput |
| P2 | MOHAWK (Bick et al., 2024) | Three-stage distillation: MatMul, Hidden, Weight transfer |
| P3 | T2MD (Yao et al., 2025) | DiT-to-Mamba with layer-level teacher forcing |
| P4 | CAB (Wang et al., 2025) | Attention Bridge for Q/K→B/C alignment, data-efficient |

### Feasibility Constraints (Pipeline-Enforced)

- **REJECT** ideas requiring new benchmarks, rubrics, or scoring frameworks
- **REJECT** ideas requiring synthetic/generated data or future follow-up data
- **REJECT** ideas requiring human evaluation or subjective scoring
- **ACCEPT ONLY** hypotheses testable immediately using existing datasets and benchmarks

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting research gap! We have four distinct distillation paradigms sitting in isolation - MOHAWK's three-stage matrix-to-logit alignment, CAB's lightweight attention bridge bypassing quadratic maps, T2MD's layer-level teacher forcing for diffusion, and MambaInLlama's hybrid approach. Yet nobody has systematically compared them under controlled conditions.

Here's what excites me: each method makes fundamentally different assumptions about *what* to transfer. MOHAWK [Bick et al., 2024] assumes the mixing matrices themselves carry the core "quadratic knowledge" and progressively aligns them. CAB [Wang et al., 2025] takes a radically different view - it says "don't match the full attention map, just align the implicit (Q,K) carriers to (C,B) projections via a lightweight MLP bridge." T2MD [Yao et al., 2025] introduces teacher forcing to prevent error accumulation in causal Mamba blocks.

What if the optimal distillation strategy is *sequence-length dependent*? At 4K tokens, maybe direct matrix matching (MOHAWK Stage 1) works fine because the attention maps are tractable. But at 32K tokens, CAB's O(L) token-level alignment might preserve more signal than trying to match O(L²) attention matrices that become increasingly sparse and noisy. This is a testable prediction!

I propose three unconventional angles:
1. **Length-Adaptive Distillation**: Switch distillation objective based on input length during training
2. **Hybrid-Method Fusion**: Combine MOHAWK's weight transfer with CAB's bridge - use matrix alignment for early layers, attention bridge for later layers
3. **Cross-Architecture Transfer Learning**: Use one distillation method to create a "universal intermediate representation" that transfers to multiple target architectures

**Key Points:**
- Four distillation paradigms exist with fundamentally different transfer assumptions
- Sequence length may determine which approach preserves most knowledge
- No unified benchmark exists comparing methods on LongBench at 4K-32K contexts

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises interesting possibilities, but let's ground this in testable specifics. The claim that "optimal distillation strategy is sequence-length dependent" needs precise operationalization.

Looking at the methodologies: MOHAWK [Bick et al., 2024] reports training on 3B tokens with sequence length 2048. CAB [Wang et al., 2025] uses 200M tokens for attention alignment plus 2-4B for soft distillation. T2MD [Yao et al., 2025] operates in the vision domain at 512×512 resolution. These are fundamentally different experimental setups - comparing them directly is methodologically unsound without controlling for:

1. **Source model architecture and size** - Phi-1.5 (1.3B) vs DistilGPT2 vs PixArt-α
2. **Training data distribution** - C4 vs OpenWebText vs image-caption pairs
3. **Target architecture variants** - Mamba vs Mamba-2 vs hybrid configurations

For a falsifiable hypothesis, I propose we test: "On LongBench single-document QA tasks, CAB-style token-level alignment achieves higher performance retention (DV: F1 relative to teacher) than MOHAWK-style matrix matching at sequences >16K tokens, while the reverse holds at <8K tokens."

The success criterion must be specific: if CAB outperforms MOHAWK by >3 F1 points at 32K but underperforms by >2 F1 points at 4K, we confirm the length-dependent hypothesis. If performance ordering is consistent across lengths, we reject it.

**Key Points:**
- Current methods use incompatible experimental setups
- Need controlled comparison: same source model, same data, same evaluation
- Proposed falsifiable criterion: 3+ F1 point crossover between methods across sequence lengths

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

🔬 Prof. Vera's methodological rigor is essential, but let me assess what this research would actually contribute to the field.

The significance question: Why does comparing distillation methods matter beyond academic curiosity? Looking at the papers, I see a compelling answer. MOHAWK claims Phi-Mamba achieves "substantially stronger performance compared to all past open-source non-Transformer models" with only 3B training tokens - that's <1% of typical pretraining compute. CAB demonstrates effectiveness with just 200M alignment tokens. If we can identify *which* method works best *when*, practitioners save enormous compute exploring the wrong approach.

The deeper contribution: These distillation methods embody fundamentally different theories of what makes Transformers work:
- MOHAWK says: "The attention mixing pattern itself encodes knowledge"
- CAB says: "Token-level Q/K representations are the core signal; explicit attention maps are redundant"
- T2MD says: "Error accumulation in sequential models requires teacher forcing"

A systematic comparison doesn't just rank methods - it tests these theoretical claims. If CAB matches MOHAWK with 10x less compute, it suggests attention maps are indeed redundant for knowledge transfer. That's a significant finding about *what* Transformers learn.

For genuine impact, we need to answer: "Given a practitioner with a pretrained Transformer and fixed compute budget, which distillation method maximizes downstream task performance on long-context workloads?"

**Key Points:**
- Research addresses practical problem: minimizing compute for Transformer-to-SSM conversion
- Theoretical significance: tests competing theories of what knowledge Transformers encode
- Impact criterion: actionable guidance for practitioners with compute constraints

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what's technically achievable here. The fundamental barrier isn't compute budget - it's the architectural mismatch between attention and SSM sequence mixing.

Looking at Mamba's core mechanism [Gu & Dao, 2023]: the selective SSM uses input-dependent B, C, Δ parameters that control propagation/forgetting along the sequence. This creates a *causal* dependency structure - token t's representation depends only on tokens 1...t. Attention, by contrast, is inherently *non-causal* during training and allows arbitrary token interactions.

MOHAWK addresses this by viewing both as "mixing matrices" - but the attention matrix is dense while Mamba's equivalent is structured (semi-separable with learned causal mask). At 32K tokens, materializing the attention matrix requires O(32K²) = 1B elements per head per layer. This is precisely why CAB's token-level alignment avoids explicit attention maps.

Here's what worries me about the length-dependent hypothesis: At longer sequences, attention becomes increasingly *sparse* in practice - most weights concentrate on local context plus a few global anchors. But Mamba's selective mechanism doesn't naturally replicate this sparsity pattern. The real question is whether distillation can transfer the *sparsity structure* that emerges in trained attention, not just the dense attention values.

For theoretical soundness, I suggest focusing on: "Can SSM recurrence faithfully approximate the effective receptive field patterns of trained attention at different sequence lengths?"

**Key Points:**
- Architectural mismatch: causal SSM vs non-causal attention is fundamental
- Memory constraint: O(L²) attention maps become intractable at 32K tokens
- Core technical question: can SSM recurrence capture attention's emergent sparsity patterns?

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and I think ⚙️ Prof. Pax's architectural analysis actually *strengthens* our hypothesis! Let me synthesize and refine.

The architectural mismatch Prof. Pax identifies is exactly *why* different distillation methods might excel at different sequence lengths:

1. **Short sequences (<8K)**: Attention matrices are tractable, dense, and capture fine-grained token interactions. MOHAWK's direct matrix alignment can faithfully transfer this dense mixing pattern to Mamba's semi-separable structure.

2. **Long sequences (>16K)**: Attention becomes effectively sparse - most information flows through local windows plus global anchors. CAB's token-level (Q,K)→(C,B) alignment may better capture these *functional* attention carriers without being distracted by the sparse noise in the full attention map.

To address Prof. Vera's methodological concerns, here's a refined hypothesis with evidence:

**Core Hypothesis (Under-If-Then-Because):**
- **Under**: Transformer-to-Mamba distillation on LongBench single-document QA
- **If**: We compare MOHAWK-style matrix alignment vs CAB-style token-level alignment
- **Then**: CAB achieves higher teacher-student F1 ratio at sequences >16K, while MOHAWK achieves higher ratio at <8K
- **Because**: At long sequences, attention sparsifies and token-level representations (Q,K) become more informative than the noisy full attention map; at short sequences, dense attention patterns contain additional mixing information that matrix alignment captures

The paper summaries support this: CAB explicitly avoids O(L²) attention maps, while MOHAWK Stage 1 directly minimizes ||TeacherMixer - StudentMixer||.

**Key Points:**
- Architectural mismatch explains why methods differ by sequence length
- Short sequences: dense attention favors matrix alignment (MOHAWK)
- Long sequences: sparse attention + token-level carriers favor CAB approach

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down: the hypothesis assumes we can isolate "distillation method" as the independent variable, but the papers use fundamentally different target architectures.

Show me the evidence that Mamba-2 (used in MOHAWK/Phi-Mamba) and original Mamba (used in some CAB experiments) are equivalent targets. MOHAWK explicitly modifies Mamba-2 by:
- Converting multi-value to multi-head structure
- Eliminating Δ discretization parameter
- Removing post-convolution nonlinearity
- Initializing gates to constant 1

These modifications make Phi-Mamba a *different architecture* from vanilla Mamba-2. If Phi-Mamba outperforms CAB's target architecture at short sequences, is that due to MOHAWK's distillation method or Phi-Mamba's architectural modifications?

Second concern: the "attention sparsifies at long sequences" claim needs quantification. What's the effective sparsity at 4K vs 32K? The Mamba paper [Gu & Dao, 2023] shows selective mechanisms handle "selective copying" - but that's a synthetic task. Does this transfer to naturalistic long-context QA?

For the hypothesis to be convincing, you need:
1. **Same target architecture** across all distillation methods
2. **Quantified attention sparsity** at each sequence length being tested
3. **Control for source model quality** - Phi-1.5 vs DistilGPT2 differ substantially

What would convince me: Run CAB's attention bridge with MOHAWK's Phi-Mamba modifications on the same source model. Then we're comparing methods, not architectures.

**Key Points:**
- Confound: different target architectures across methods
- Need: same modified Mamba-2 as target for all distillation approaches
- Require: quantified attention sparsity metrics at each sequence length
- Control: identical source model (e.g., Phi-1.5) for all conditions

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔍 Prof. Rex makes a crucial point about confounds - but what if we turn this into an *opportunity* for novel contribution?

Imagine this: instead of picking one existing distillation method, we design a **unified distillation framework** that can instantiate MOHAWK, CAB, or hybrid variants through configuration. This framework would:

1. Use MOHAWK's Phi-Mamba architecture modifications (multi-head SSM, no Δ, open gates) as the **standard target** - these modifications are well-motivated and enable weight transfer
2. Implement both **matrix-level** (MOHAWK Stage 1) and **token-level** (CAB attention bridge) alignment as pluggable objectives
3. Allow **staged composition**: e.g., CAB token alignment for early layers, MOHAWK matrix alignment for later layers, or vice versa

This reframes our hypothesis from "which existing method is best" to "what objective function maximizes transfer at each sequence length?" That's a more fundamental scientific question.

The crossover prediction remains: I predict that token-level objectives dominate at L>16K while matrix-level objectives dominate at L<8K. But now we can also explore the 8K-16K transition zone with hybrid objectives.

This also addresses feasibility: we're not reimplementing four separate codebases. We build one framework and ablate components.

**Key Points:**
- Novel contribution: unified distillation framework with pluggable objectives
- Standardize on MOHAWK's Phi-Mamba modifications as target architecture
- Test matrix-level vs token-level objectives (and hybrids) as the core comparison
- More fundamental question: optimal objective function vs optimal method

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

🔭 Dr. Nova's unified framework idea resolves the confound issue elegantly. Let me sharpen the experimental design.

**Independent Variables:**
1. **Distillation objective type**: Matrix-level (MOHAWK Stage 1) vs Token-level (CAB bridge) vs Hybrid (staged)
2. **Sequence length**: 4K, 8K, 16K, 32K tokens

**Controlled Variables (must be identical across conditions):**
- Source model: Phi-1.5 (1.3B parameters)
- Target architecture: Modified Mamba-2 (MOHAWK's Phi-Mamba modifications)
- Training data: C4, same tokenization
- Training tokens: 3B total (matching MOHAWK's reported setup)
- Evaluation: LongBench single-document QA subset

**Dependent Variables:**
- Primary: Teacher-student F1 ratio (normalized by teacher performance at each length)
- Secondary: Perplexity retention, inference throughput

**Falsifiable Predictions:**
1. At 4K tokens: Matrix-level > Token-level by ≥2 F1 points
2. At 32K tokens: Token-level > Matrix-level by ≥3 F1 points
3. At 8K-16K: Hybrid objective outperforms both pure approaches

**Success/Failure Criteria:**
- If predictions 1 AND 2 hold: Strong support for length-dependent distillation
- If only one holds: Partial support, method has universal advantage at one regime
- If neither holds: Reject length-dependent hypothesis; seek alternative explanations

The 3B token budget and Phi-1.5 source are chosen to match MOHAWK's setup, enabling direct comparison with their published results.

**Key Points:**
- Clear 2x4 factorial design: objective type × sequence length
- Standardized on MOHAWK setup for direct comparability
- Three falsifiable predictions with specific effect size thresholds
- Success criteria distinguish strong/partial/null support

---

### Exchange 9

🎯 **Dr. Sage** (Research Impact Evaluator):

The experimental design is sound. Let me assess whether this will genuinely advance the field.

**Novelty assessment:** This would be the *first* controlled comparison of distillation objective types (matrix vs token-level) across sequence lengths. Prior work (MOHAWK, CAB, T2MD) each validates their approach in isolation. A unified framework comparison is genuinely new.

**Contribution type:** This is a *systematic analysis* contribution - similar in spirit to "A Systematic Analysis of Hybrid Linear Attention" [Wang et al., 2025] that trained 72 models to establish optimal hybrid ratios. Our contribution establishes optimal *distillation objectives* as a function of sequence length.

**Impact projection:**
- **Immediate**: Practitioners get lookup table: "For target sequence length L, use objective X"
- **Theoretical**: Resolves whether attention maps or token-level representations are the essential knowledge carriers
- **Methodological**: Unified framework becomes a research tool for future distillation studies

**Gap addressed:** The original research gap was "no unified comparison across sequence lengths." This proposal directly addresses it with a controlled experimental design.

**What elevates this from incremental to significant:** The length-dependent crossover prediction, if confirmed, reveals something fundamental about the structure of attention knowledge. It's not just "method A beats method B" - it's "the optimal knowledge representation changes with context scale."

**Key Points:**
- First controlled comparison of distillation objective types across sequence lengths
- Systematic analysis contribution (similar to Hybrid Analysis paper)
- Resolves theoretical question about essential attention knowledge carriers
- Practical impact: actionable lookup table for practitioners

---

### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The experimental design is theoretically sound. Let me verify technical feasibility.

**Compute requirements assessment:**
- MOHAWK reports 3B tokens on "C4" with 8×A100 GPUs
- Factorial design: 3 objective types × 4 sequence lengths = 12 conditions
- If each condition requires 3B tokens: 36B total tokens, ~12x MOHAWK's compute
- **Mitigation**: Use same pretrained Phi-1.5 initialization; only vary distillation objective. Share Stage 3 (weight transfer) across conditions.

**Memory feasibility at 32K:**
- Matrix-level objective requires materializing attention: 32K² × 4 bytes × heads × layers
- For Phi-1.5 (32 heads, 24 layers): 32K² × 4 × 32 × 24 = 3.1TB per batch - **infeasible**
- **Solution**: At 32K, matrix-level objective computes on sub-sampled attention (e.g., 1K uniformly sampled positions), or uses memory-efficient chunked attention. This is a methodological adaptation, but necessary.

**LongBench evaluation:**
- Single-doc QA tasks support sequences up to ~32K
- Public dataset, established metrics (F1, Exact Match)
- Evaluation is feasible on single GPU per model

**Realistic scope adjustment:**
Given compute constraints, I recommend starting with:
- 2 objectives (matrix vs token-level, not hybrid initially)
- 3 sequence lengths (4K, 16K, 32K - skip 8K to reduce conditions)
- 1.5B tokens per condition (half MOHAWK's budget, but sufficient for signal)

This gives 6 conditions × 1.5B = 9B tokens total - achievable on 8×A100 in ~2 weeks.

**Key Points:**
- Full factorial design requires 36B tokens - infeasible at scale
- 32K matrix-level objective needs adaptation (sub-sampling or chunking)
- Recommended scope: 2 objectives × 3 lengths = 6 conditions, ~9B tokens total
- Timeline: ~2 weeks on 8×A100

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent pragmatic scoping from ⚙️ Prof. Pax. Let me synthesize our refined hypothesis.

**Refined Core Hypothesis:**

"On long-context NLU tasks (LongBench single-document QA), the optimal distillation objective for Transformer-to-Mamba conversion depends on sequence length: token-level alignment (CAB-style) outperforms matrix-level alignment (MOHAWK-style) at sequences ≥16K, while matrix-level alignment outperforms at sequences ≤4K, because attention matrices become effectively sparse at long contexts and token-level Q/K representations better capture the functional attention signal."

**Variables (Refined):**
- **IV**: Distillation objective type {Matrix-level, Token-level}
- **IV**: Sequence length {4K, 16K, 32K}
- **DV (Primary)**: Teacher-student F1 ratio on LongBench single-doc QA
- **DV (Secondary)**: Perplexity retention rate

**Controlled**: Source (Phi-1.5), Target (Phi-Mamba), Data (C4), Budget (1.5B tokens/condition)

**Causal Mechanism (3 steps):**
1. **Attention sparsification**: As sequence length increases, trained attention weights concentrate on local context + sparse global anchors
2. **Information density shift**: At long sequences, essential mixing information resides in the token-level Q/K projections rather than the full L×L attention map
3. **Distillation objective match**: Token-level objectives capture this concentrated signal efficiently; matrix-level objectives are distracted by sparse noise in the attention map

**Testable Predictions:**
- P1: At 4K, Matrix-level achieves ≥97% F1 retention vs ≤93% for Token-level
- P2: At 32K, Token-level achieves ≥90% F1 retention vs ≤85% for Matrix-level
- P3: Crossover occurs in 8K-16K range (interpolate from 4K and 32K data points)

**Key Points:**
- Hypothesis: optimal distillation objective is length-dependent
- Mechanism: attention sparsification shifts information density to token-level
- Predictions: specific retention rates with crossover in 8K-16K range
- Scope: 6 conditions, 9B tokens, ~2 weeks compute

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis is stronger, but I still see gaps. Let me stress-test the mechanism and predictions.

**Mechanism critique:**
The claim "attention sparsifies at long sequences" is reasonable but unverified for Phi-1.5 specifically. What if Phi-1.5 (trained on 150B tokens with max length 2048) doesn't exhibit meaningful sparsification at 32K because it was never trained on such lengths? You'd be extrapolating attention behavior outside the training distribution.

**Counter-prediction:**
If Phi-1.5's attention at 32K is *degenerate* (uniformly distributed or collapsed) rather than *sparse-but-structured*, then neither distillation method will work well. Both matrix-level and token-level will underperform because there's no meaningful signal to transfer.

**What would convince me:**
1. Visualize Phi-1.5 attention patterns at 4K, 16K, 32K on actual LongBench examples before distillation
2. Quantify sparsity: compute effective attention rank or entropy at each length
3. If sparsity doesn't increase with length, revise the mechanism hypothesis

**Alternative hypothesis:**
Perhaps the length-dependent effect isn't about attention sparsity, but about *error accumulation* in sequential models. At longer sequences, Mamba's recurrent state accumulates more error per step. Token-level objectives might be more robust to this because they align local representations rather than global mixing patterns.

This alternative predicts the same crossover but via a different mechanism. Distinguishing them requires measuring both attention sparsity AND recurrent state error during distillation.

**Key Points:**
- Concern: Phi-1.5 wasn't trained on 32K; attention behavior may be degenerate
- Requirement: visualize and quantify attention sparsity before distillation
- Alternative mechanism: recurrent error accumulation, not attention sparsity
- Distinguishing test: measure both sparsity and recurrent error

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

🔍 Prof. Rex raises a critical point about Phi-1.5's training distribution. But here's a creative reframe: what if we *embrace* the length extrapolation challenge?

The practical use case for Transformer-to-SSM distillation is precisely this: organizations have pretrained Transformers (with limited context windows) and want to convert them to SSMs that can handle *longer* contexts. Testing distillation methods on in-distribution lengths only answers half the question.

**Novel experimental design:**
Instead of viewing 32K as a confound, make it a *primary test condition*:

1. **In-distribution distillation** (4K): Both methods should work; establishes baseline
2. **Moderate extrapolation** (16K): 8x teacher's training length; tests robustness
3. **Aggressive extrapolation** (32K): 16x teacher's training length; tests limits

This reframes the hypothesis: "Token-level distillation enables better length generalization than matrix-level distillation because it captures the *functional structure* of attention rather than the *specific values* which may be unreliable at extrapolated lengths."

To address Prof. Rex's alternative (error accumulation vs sparsity), we can add a diagnostic:
- Measure **hidden state drift** between teacher attention output and student Mamba output at each layer
- If drift increases faster for matrix-level distillation at long sequences, error accumulation is implicated
- If drift is similar but final performance differs, the issue is the objective's robustness to length extrapolation

**Key Points:**
- Reframe 32K as "aggressive extrapolation" test, not confound
- New hypothesis: token-level distillation enables better length *generalization*
- Diagnostic: measure hidden state drift to distinguish error accumulation vs sparsity mechanisms
- Practical relevance: real use case involves length extrapolation

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

I can work with this reframing. Let me formalize the updated experimental design.

**Revised Hypothesis (Length Generalization):**

"Token-level distillation objectives enable Mamba to generalize to longer sequences (beyond teacher's training distribution) more effectively than matrix-level objectives, because token-level representations capture functional attention structure that extrapolates, whereas matrix-level objectives overfit to specific attention values that degrade at unseen lengths."

**Updated IV/DV:**
- **IV1**: Distillation objective {Matrix-level, Token-level}
- **IV2**: Sequence length regime {In-distribution (4K), Moderate extrapolation (16K), Aggressive extrapolation (32K)}
- **DV1 (Primary)**: F1 retention relative to teacher (teacher evaluated at 4K, its training regime)
- **DV2 (Diagnostic)**: Per-layer hidden state drift (L2 distance between teacher attention output and student Mamba output)

**Updated Predictions:**
- P1: At 4K (in-distribution), Matrix-level ≥ Token-level (≤2 F1 point difference)
- P2: At 16K (moderate extrapolation), Token-level > Matrix-level by ≥3 F1 points
- P3: At 32K (aggressive extrapolation), Token-level > Matrix-level by ≥5 F1 points
- P4: Hidden state drift increases with sequence length for both methods, but more steeply for Matrix-level

**Null Hypothesis:**
There is no significant difference in F1 retention between distillation objectives across sequence lengths. The interaction term (Objective × Length) is not significant at p<0.05.

**Statistical Test:**
2×3 factorial ANOVA with F1 retention as DV. Planned contrasts for predictions P1-P3.

**Key Points:**
- Reformulated as length generalization hypothesis
- Predictions now specify expected effect sizes at each regime
- Added hidden state drift as diagnostic DV
- Formal null hypothesis and statistical test specified

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The length generalization framing is sound. Final feasibility check.

**Data availability:**
- LongBench single-document QA supports up to 32K context (verified in paper [Bai et al., 2023])
- Phi-1.5 publicly available via HuggingFace
- C4 dataset accessible via HuggingFace Datasets

**Implementation path:**
1. Fork MOHAWK's Phi-Mamba codebase (goombalab/phi-mamba)
2. Implement CAB's attention bridge module (wph6/CAB)
3. Integrate both objectives into unified training loop
4. Add hidden state drift logging at each layer

**Compute estimate (refined):**
- 6 conditions × 1.5B tokens = 9B tokens total
- At 2048 seq length, batch size 32, 8×A100: ~3 days per condition
- Total: ~18 days sequential, or ~3 days with condition parallelism

**Risk mitigation:**
- If 32K inference OOMs: use gradient checkpointing + reduced batch size
- If hidden state logging too expensive: sample 10% of batches
- If F1 retention too noisy: increase evaluation set size (full LongBench vs subset)

**Go/No-Go:**
All components exist. Implementation requires ~1 week engineering, ~3 weeks training+evaluation. Total: 4 weeks to results. This is feasible for a research contribution.

**Key Points:**
- All data and code components publicly available
- Implementation requires forking MOHAWK + CAB codebases
- Compute: ~18 days training, parallelizable to ~3 days
- Total timeline: 4 weeks to results

---

### Exchange 16

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

We have convergence! Let me synthesize the final hypothesis that emerged from our discussion.

**CONSENSUS HYPOTHESIS: Length-Dependent Distillation Objectives for Transformer-to-Mamba Conversion**

**Core Statement (Under-If-Then-Because):**
Under the setting of distilling a pretrained Transformer (Phi-1.5) into a Mamba-based architecture (Phi-Mamba) for long-context NLU tasks, if we compare token-level distillation objectives (CAB-style Q/K→C/B alignment) versus matrix-level objectives (MOHAWK-style attention map matching), then token-level objectives achieve superior F1 retention at extrapolated sequence lengths (≥16K) while matrix-level objectives achieve comparable or better performance at in-distribution lengths (≤4K), because token-level representations capture the functional structure of attention that generalizes to unseen lengths, whereas matrix-level objectives overfit to specific attention values that degrade under length extrapolation.

**Mechanism (3 Causal Steps):**
1. **Training distribution bound**: Phi-1.5 was trained on 2048-length sequences; attention patterns at 16K-32K are extrapolations
2. **Representation robustness**: Token-level Q/K projections encode local attention "intent" that transfers; full attention maps at extrapolated lengths contain extrapolation noise
3. **Objective-task match**: Token-level alignment transfers robust local representations; matrix-level alignment captures noise alongside signal

**Predictions:**
- P1: At 4K (in-distribution): Matrix-level ≥ Token-level (within 2 F1 points)
- P2: At 16K: Token-level > Matrix-level by ≥3 F1 points  
- P3: At 32K: Token-level > Matrix-level by ≥5 F1 points
- P4: Hidden state drift increases faster for matrix-level at long sequences

**Experimental Design:**
- 2×3 factorial: {Matrix, Token} × {4K, 16K, 32K}
- Source: Phi-1.5, Target: Phi-Mamba (MOHAWK modifications)
- Data: C4 (1.5B tokens/condition), Eval: LongBench single-doc QA
- Compute: 9B tokens total, ~4 weeks to results

**Key Points:**
- Hypothesis: token-level distillation enables better length generalization
- Mechanism: token representations are more robust to extrapolation than attention maps
- 4 testable predictions with specific effect sizes
- Feasible experimental design: 6 conditions, 4-week timeline

---

### Exchange 17

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

The hypothesis is now well-formed. I have one remaining concern that should be documented as a key assumption.

**Key Assumption (Critical):**
The hypothesis assumes that Phi-1.5's attention patterns at 32K, while extrapolated, still contain *some* meaningful structure that one objective can capture better than the other. If attention at 32K is completely degenerate (uniform or collapsed), both methods will fail equally, and the hypothesis is vacuously true.

**Mitigation (Built into design):**
Before main experiments, compute attention entropy at 4K, 16K, 32K on 100 LongBench examples. If entropy at 32K is within 2x of entropy at 4K, proceed. If entropy explodes (>10x), revise scope to exclude 32K.

**Remaining concerns (Minor, documented for Phase 2B):**
1. Phi-1.5's C4 pretraining may not align with LongBench evaluation domain
2. 1.5B tokens per condition may be insufficient for full convergence
3. Single source model limits generalizability claims

These don't invalidate the hypothesis but constrain the scope of conclusions.

**My verdict: PROCEED**
The hypothesis is novel, testable, and addresses the identified research gap. The experimental design controls for known confounds (architecture, data, compute). Predictions are falsifiable with specific effect sizes.

**Key Points:**
- Critical assumption: attention at 32K is not fully degenerate
- Mitigation: pre-experiment attention entropy check
- Minor concerns documented for Phase 2B to address
- Verdict: hypothesis is ready for experimental testing

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The length-dependent distillation hypothesis is genuinely novel. No prior work systematically compares distillation objectives across sequence lengths. The "length generalization" reframing elevates this from method comparison to fundamental insight about attention knowledge representation.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis specifies precise predictions (P1-P4) with quantified effect sizes (2, 3, 5 F1 points). The 2×3 factorial design with planned contrasts enables clear statistical testing. Null hypothesis explicitly defined. This is textbook falsifiability.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The contribution addresses a practical problem (compute-efficient Transformer-to-SSM conversion) with theoretical implications (what knowledge do attention maps encode?). Results will provide actionable guidance for practitioners and inform understanding of attention mechanisms.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components exist: Phi-1.5, MOHAWK/CAB codebases, LongBench benchmark. Compute requirements (9B tokens, 8×A100, 4 weeks) are realistic. Memory constraints at 32K are addressed via chunking/sampling. Implementation path is clear.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The research discussion converged on a clear, testable hypothesis about length-dependent distillation objectives. The core insight is that token-level distillation (aligning Q/K projections to C/B) better captures the functional structure of attention for length generalization, while matrix-level distillation (matching full attention maps) is effective at in-distribution lengths but degrades under extrapolation.

The hypothesis emerges from recognizing that existing distillation methods (MOHAWK, CAB, T2MD) make different assumptions about what to transfer, and these assumptions have different implications at different sequence lengths. By standardizing on a unified Phi-Mamba target architecture and comparing objectives directly, we can test which approach is optimal for practitioners targeting different context length regimes.

The experimental design is a 2×3 factorial comparing Matrix vs Token objectives across 4K, 16K, and 32K sequences, with F1 retention as the primary DV and hidden state drift as a diagnostic. Predictions specify expected effect sizes, enabling clear hypothesis testing.

The contribution is significant because it provides the first controlled comparison of distillation objective types, resolving a practical question (which method to use) while providing theoretical insight (token-level representations generalize better than attention maps).

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Phi-1.5 attention at 32K may be degenerate due to training distribution mismatch
- Single source model (Phi-1.5) limits generalizability
- 1.5B tokens per condition may be below full convergence
- **Mitigation Strategy:** Pre-experiment attention entropy check; document scope limitations; plan follow-up with additional source models if main hypothesis confirmed

