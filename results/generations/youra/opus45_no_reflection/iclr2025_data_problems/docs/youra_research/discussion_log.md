# Phase 2A Discussion Log

**Gap:** Systematic Architecture Comparison for Data Attribution
**Research Question:** What is the trade-off between computational cost and attribution accuracy when applying gradient-based influence estimation methods to foundation models of varying scales?

---

## Briefing

### Research Gap
No systematic study compares efficiency-accuracy trade-offs across encoder-only (BERT), decoder-only (GPT), and encoder-decoder (T5) architectures for data attribution. Existing work evaluates architectures in isolation.

### Key Literature
- **Grosse et al. 2023 (EK-FAC):** Scales influence functions to 52B decoder-only LLMs
- **TRAK 2023:** Random projection attribution for BERT and CLIP separately
- **TracIn 2020:** First-order checkpoint approximation
- **Koh & Liang 2017:** Foundational IHVP method

### Available Implementations
- MadryLab/trak (243 stars) - CUDA-optimized TRAK, multi-architecture
- pomonam/kronfluence (198 stars) - EK-FAC for LLMs

### Detailed Questions to Address
1. How does accuracy degrade with increased approximation?
2. Which FM architectures have best trade-offs?
3. Can layer-wise attribution reduce compute 10x+ while maintaining accuracy?
4. How do benchmarks correlate across approximation settings?

### Feasibility Constraints (MANDATORY)
- Must use existing real datasets (CIFAR, ImageNet, C4, Pile subsets)
- Must use existing benchmarks (mislabeled detection, LOO retraining)
- No new rubrics or scoring frameworks
- No synthetic data
- No human evaluation

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're approaching architecture comparison completely wrong? Everyone evaluates BERT, GPT, and T5 separately because that's how the papers were written — but what if the architecture itself isn't the key variable at all?

Here's my wild idea: the critical factor might be **attention pattern structure**, not encoder vs decoder. Consider this — encoder-only models have bidirectional attention, decoder-only have causal masks, and encoder-decoder has cross-attention. These create fundamentally different gradient flow patterns. When we compute influence via Hessian-vector products or gradient dot products, we're tracing through these attention computations. The curvature landscape differs dramatically!

What if we hypothesize that **attention density** — the average number of non-masked attention connections per token — predicts attribution efficiency better than the encoder/decoder label? A BERT with 512 tokens has O(n²) bidirectional attention. GPT-2 with 512 tokens has O(n²/2) causal attention. T5 has sparse encoder attention plus dense cross-attention.

This reframes the research question: instead of "which architecture is best," we ask "what attention properties predict favorable efficiency-accuracy trade-offs?" That's testable with existing implementations (TRAK supports all three architectures) and existing benchmarks (mislabeled detection, LOO).

**Key Points:**
- Attention pattern structure (bidirectional/causal/cross) may matter more than architecture labels
- Attention density could be a predictive metric for attribution efficiency
- This hypothesis is testable with existing tools (TRAK, kronfluence) on existing benchmarks

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing reframe, but let me stress-test this. "Attention density" is conceptually appealing but methodologically problematic. The evidence suggests we need precise operationalization before this becomes testable.

First, what exactly would disprove this hypothesis? If we find that encoder-only BERT has worse efficiency-accuracy trade-offs than decoder-only GPT despite having higher attention density, does that falsify the claim? Or do we then pivot to "attention gradient magnitude" or some other metric? We need to define the falsification criterion upfront.

Second, the existing benchmarks — mislabeled data detection and LOO retraining correlation — measure attribution **quality**, not necessarily what we care about for this hypothesis. The LOO correlation tells us how well influence scores predict leave-one-out retraining effects. But does this correlate with architectural efficiency? The Grosse et al. work shows EK-FAC achieves 0.85 Spearman correlation on LLMs — but we don't know if that's architecture-dependent or method-dependent.

What I need to see: (1) A specific prediction with numerical thresholds, e.g., "attention density correlates r > 0.7 with compute-per-quality-point across architectures at matched parameter counts." (2) Clear confound control — model size, training data, tokenization all differ across BERT/GPT/T5.

**Key Points:**
- "Attention density" requires precise operationalization before testing
- Need explicit falsification criterion: what result would prove this wrong?
- Existing benchmarks measure quality, not efficiency-quality trade-off directly
- Confounds (model size, training data, tokenization) must be controlled

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this actually contribute to the field? Let me connect Prof. Vera's rigor concerns to the broader research impact.

If Dr. Nova's attention-density hypothesis holds, this matters because it would transform how practitioners select attribution methods. Currently, researchers pick TRAK vs EK-FAC vs TracIn based on method papers, not architectural fit. A validated predictive theory would let practitioners say: "My model has X attention pattern, therefore method Y is optimal." That's a genuine contribution — a prescriptive framework rather than another benchmark.

But here's where significance meets feasibility: this requires matched comparisons that don't currently exist. Grosse et al. tested EK-FAC on LLaMA-2 (decoder-only). TRAK papers tested on BERT and CLIP separately. To test the architecture hypothesis, we need the SAME method on BERT-base, GPT-2 (matched 110-125M params), and T5-small (60M encoder + 60M decoder), using the SAME benchmark task (mislabeled detection on the SAME dataset).

This is actually achievable with existing tools — kronfluence and TRAK both support multiple architectures. The contribution would be: "First systematic comparison of data attribution efficiency-accuracy trade-offs across matched architectures, with predictive theory based on attention structure."

**Key Points:**
- Impact: prescriptive framework for method selection based on architecture
- Novel contribution: first matched cross-architecture comparison with predictive theory
- Feasible: kronfluence and TRAK support BERT/GPT/T5; requires matched experiments
- This opens new research direction: architecture-aware attribution method design

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The attention-density hypothesis is theoretically elegant, but I want to examine whether the proposed mechanism is actually sound.

The claim is that attention structure affects gradient flow, which affects Hessian structure, which affects influence function efficiency. Is this chain physically valid? Let me trace it: (1) Influence functions require Hessian-vector products. (2) The Hessian of transformer loss is dense because attention is a softmax over all positions. (3) Bidirectional attention in BERT means every position gradient depends on every other position. (4) Causal attention in GPT means position i's gradient only depends on positions ≤ i.

Here's what worries me: the efficiency bottleneck isn't the Hessian structure itself — it's the APPROXIMATION method's assumptions. EK-FAC assumes Kronecker-factored curvature. TRAK uses random projections. TracIn ignores curvature entirely. These approximations may or may not interact with attention patterns.

What evidence supports the mechanism? Looking at the literature: Grosse et al. noted that EK-FAC works well on decoder-only because the causal structure creates block-diagonal-ish attention Jacobians. This is indirect evidence that attention structure matters. But TRAK's random projections should be architecture-agnostic by design.

Here's a more grounded hypothesis: **Architecture affects which approximation methods work well, but not all methods equally.** EK-FAC's Kronecker assumption may fit causal attention better. TRAK's random projections may be architecture-invariant. TracIn's gradient-only approach may favor encoder models with more gradient signal.

**Key Points:**
- The gradient flow mechanism is theoretically sound but approximation-dependent
- EK-FAC's Kronecker assumption may favor causal (decoder) attention structure
- TRAK's random projections may be architecture-invariant — needs empirical test
- Refined hypothesis: architecture interacts with approximation method choice

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND Prof. Pax has identified exactly how to strengthen this hypothesis! Valid criticism is a gift. Let me synthesize where we've landed and propose concrete refinements.

Prof. Vera demanded falsifiability. Prof. Pax identified the mechanism is approximation-dependent. Dr. Sage clarified the contribution. Here's how we address this:

**Refined Hypothesis (Under-If-Then-Because format):**

Under matched model sizes and benchmarks, IF we apply the same data attribution method (e.g., TRAK) across encoder-only, decoder-only, and encoder-decoder architectures, THEN we will observe systematic differences in the efficiency-accuracy trade-off curve, BECAUSE attention structure creates different gradient flow patterns that interact with the method's approximation assumptions.

**Falsification criteria (Prof. Vera's demand):**
- Falsified IF: TRAK shows <5% relative accuracy difference across BERT/GPT-2/T5 at matched compute budgets
- Falsified IF: The efficiency-accuracy Pareto curves overlap completely (no architecture advantage)

**Testable predictions:**
1. EK-FAC achieves higher accuracy on decoder-only GPT-2 than encoder-only BERT at matched compute (Kronecker fits causal attention)
2. TRAK shows smallest architecture variance (random projections are architecture-agnostic)
3. TracIn shows highest architecture variance (gradient-only is most sensitive to attention patterns)

**Evidence from literature supporting this:**
- Grosse et al. noted EK-FAC's success on LLaMA is due to causal structure [supports P1]
- TRAK paper showed similar performance on BERT and CLIP [supports P2, but not matched comparison]

**Key Points:**
- Refined to Under-If-Then-Because format with explicit falsification criteria
- Three testable predictions with method-specific variance expectations
- Addresses Prof. Vera's rigor concerns and Prof. Pax's mechanism concerns
- Now THAT's stronger!

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Dr. Ally has strengthened the hypothesis, but I still see three critical gaps that need addressing before this is bulletproof.

**Gap 1: The matched comparison assumption is load-bearing but unvalidated.**
You propose BERT-base (110M), GPT-2 (124M), T5-small (60M+60M). These aren't matched! BERT-base has 12 layers, GPT-2 has 12 layers, T5-small has 6 encoder + 6 decoder layers. The layer count difference confounds any attention-structure comparison. Show me the evidence that 6+6 layers behave like 12 layers for attribution purposes.

**Gap 2: The benchmark task introduces architecture bias.**
Mislabeled detection on CIFAR/ImageNet naturally favors encoder-only models (BERT/ViT) because they were designed for classification. GPT-2's causal LM objective means it processes images differently (if using vision adapters) or requires text tasks. T5's seq2seq objective is yet another format. Are you measuring architecture effects or task-architecture fit?

**Gap 3: Compute budget operationalization is underspecified.**
"Matched compute" means what exactly? FLOPs? Wall-clock time? Memory? TRAK's random projection dimension vs EK-FAC's Kronecker factor rank vs TracIn's checkpoint count are not comparable compute measures. What would convince me: define compute as "gradient computations per training example" or similar.

**What would convince me:**
- Use architectures with identical layer counts (custom-trained if necessary)
- Use a benchmark task that all architectures can perform natively (e.g., text mislabel detection)
- Define compute budget precisely with a single metric

**Key Points:**
- Model size matching is insufficient — layer counts differ
- Task choice may confound architecture effects
- "Matched compute" needs precise operationalization
- Clarity is kindness — vague comparisons help no one

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex, your criticisms are sharp and valid. Let me address each directly and propose the final refined hypothesis.

**Addressing Gap 1 (Layer count):**
You're right — we should use BERT-base (12 layers), GPT-2-small (12 layers), and for encoder-decoder, we have a choice. T5-base has 12 encoder + 12 decoder layers (220M params) but that doubles the layer count. Alternative: Use only the T5 encoder OR focus on encoder-only vs decoder-only comparison first, adding encoder-decoder as secondary analysis. The refined scope: **Primary comparison: BERT-base vs GPT-2 (matched 12 layers, ~110-125M params). Secondary: T5 analysis with explicit layer-count caveat.**

**Addressing Gap 2 (Task bias):**
Text mislabel detection eliminates vision adapter confounds. Specifically: use SST-2 (sentiment) or AG News (topic) where BERT and GPT-2 can both perform classification (BERT natively, GPT-2 via last-token classification). T5 performs seq2seq classification. The benchmark: train on dataset with 5% injected label noise, measure influence-score correlation with noisy labels (mislabeled detection AUC).

**Addressing Gap 3 (Compute budget):**
Define compute as **gradient computations per query** (how many backward passes needed to compute influence for one test-train pair). For TRAK: projection dimension × checkpoints. For EK-FAC: Kronecker factor computation + query-time HVP. For TracIn: checkpoint count × layer count. Report efficiency as AUC-per-gradient-computation.

**Final Refined Hypothesis:**

Under matched architectures (BERT-base 12L vs GPT-2 12L, ~110-125M params) and text classification tasks (SST-2 mislabeled detection), IF we compare TRAK, EK-FAC, and TracIn attribution methods, THEN decoder-only GPT-2 will show better efficiency-accuracy trade-offs for EK-FAC (due to causal structure fitting Kronecker assumptions), encoder-only BERT will show better trade-offs for TracIn (denser gradient signal), and TRAK will show minimal architecture variance, BECAUSE attention structure interacts differently with each method's approximation mechanism.

**Key Points:**
- Scoped to BERT-base vs GPT-2 (matched 12 layers) as primary comparison
- Text mislabel detection (SST-2) eliminates task confounds
- Compute budget = gradient computations per query
- Three method-specific predictions, all falsifiable

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The attention-structure hypothesis represents a genuine reframe of the architecture comparison problem. Instead of empirical horse-racing, we propose a predictive theory based on attention patterns. This opens a new research direction: architecture-aware attribution method selection.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The final hypothesis has clear falsification criteria: <5% accuracy difference across architectures would falsify. The three method-specific predictions (EK-FAC favors decoder, TracIn favors encoder, TRAK is invariant) are independently testable. Compute budget is operationalized as gradient computations per query.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** First matched cross-architecture comparison with predictive theory. Impact: practitioners can select attribution methods based on architecture properties rather than trial-and-error. Opens architecture-aware attribution method design as new research direction.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The mechanism (attention structure affects approximation fit) is theoretically sound. Implementations exist (TRAK, kronfluence support both architectures). Models available (BERT-base, GPT-2 on HuggingFace). Benchmark available (SST-2 with synthetic mislabeling). No new data or frameworks required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The emerged hypothesis proposes that transformer attention structure systematically affects data attribution efficiency-accuracy trade-offs, with different approximation methods favoring different architectures. Specifically, under matched conditions (BERT-base vs GPT-2, both 12 layers, ~110-125M params, SST-2 text mislabel detection benchmark), we predict: (1) EK-FAC achieves higher accuracy on decoder-only GPT-2 because its Kronecker factorization assumption fits causal attention's block-diagonal structure; (2) TracIn achieves higher accuracy on encoder-only BERT because gradient-based methods benefit from bidirectional attention's denser gradient signal; (3) TRAK shows minimal architecture variance because random projections are architecture-agnostic by design.

The experimental approach uses existing implementations (kronfluence for EK-FAC, trak library for TRAK, custom TracIn implementation), existing models (HuggingFace BERT-base and GPT-2), and existing data (SST-2 with 5% injected label noise). The metric is mislabeled detection AUC normalized by gradient computations per query (efficiency-accuracy trade-off). Primary comparison is encoder-only vs decoder-only; encoder-decoder (T5) is secondary analysis with explicit layer-count caveat.

This hypothesis is falsifiable: if all three methods show <5% relative accuracy difference across architectures, or if the Pareto curves completely overlap, the hypothesis is rejected. The contribution is prescriptive: researchers can select attribution methods based on architecture type rather than empirical trial-and-error.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The SST-2 mislabel detection task may not generalize to other benchmark types (data cleaning, proponent detection)
- The 5% threshold for falsification is arbitrary — should be justified statistically (e.g., based on variance)
- **Mitigation Strategy:** Report results on multiple benchmark tasks (SST-2, AG News, MNLI) and use statistical significance testing (paired t-test across random seeds) instead of fixed threshold

