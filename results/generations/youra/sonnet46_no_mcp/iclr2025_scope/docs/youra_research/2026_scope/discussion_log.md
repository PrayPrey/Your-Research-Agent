# Phase 2A Discussion Log
# Gap: Joint KV Cache Eviction and Fine-Tuning Co-Optimization
# Generated: 2026-05-04
# Architecture: Self-Contained Tikitaka Loop v9.0.0 (Fallback Mode — Claude writes all exchanges)

## Briefing Context

**Research Gap:** Gap 1 — Joint KV Cache Eviction and Fine-Tuning Co-Optimization (CRITICAL/PRIMARY)

**Core Problem:**
KV cache eviction methods (H2O, StreamingLLM, SnapKV) are applied post-hoc to pre-trained or separately fine-tuned models. PEFT methods (AdaLoRA, DoRA) are applied without awareness of KV cache budget constraints. The two are treated as independent optimization problems.

**Missing Piece:**
A systematic study on whether KV cache eviction policies can be jointly optimized with PEFT adaptation — whether eviction-aware fine-tuning (training adapters while simulating reduced KV cache budgets) improves both throughput and task accuracy on LongBench/SCROLLS compared to sequential (evict then fine-tune) baselines.

**Key Papers:**
- H2O: Heavy-Hitter Oracle (arXiv:2306.14048) — cumulative attention scoring, post-hoc eviction
- SnapKV (arXiv:2404.14469) — query-aware KV clustering on LongBench, no PEFT
- AdaLoRA (arXiv:2303.10512) — adaptive rank PEFT, no KV cache awareness
- DoRA (arXiv:2402.09353) — magnitude+direction decomposition PEFT
- StreamingLLM (arXiv:2309.17453) — attention sink eviction

**Benchmarks (existing, no new data):**
- LongBench, SCROLLS — long-context accuracy
- Throughput: tokens/sec on standard hardware

**Feasibility Constraints:**
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data
- No human evaluation or annotation
- Must be immediately testable on existing real datasets

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the entire paradigm? Right now, everyone treats KV cache eviction as a *deployment* problem — you train your model, then you figure out how to serve it cheaply. But what if eviction awareness was baked into *training itself*?

Here's the wild idea: during LoRA/AdaLoRA fine-tuning, we simulate KV cache budgets by randomly masking out evicted tokens from the attention computation. Not post-hoc — during the forward pass. The adapter learns to be robust to token absence. This is analogous to how dropout trains networks to be robust to neuron absence, but applied to token memory rather than hidden units.

The H2O paper [Zhang et al., 2023] shows that "heavy hitter" tokens — those with high cumulative attention scores — dominate the useful KV cache. What if AdaLoRA's rank allocation was *guided* by which tokens survive eviction? Adapters that work on eviction-surviving tokens need lower rank (the signal is clean), while adapters applied to volatile tokens need higher rank to capture uncertainty. This creates a natural co-optimization signal.

What really excites me: this could mean that a model fine-tuned with KV-budget simulation at 20% cache retention might *outperform* a full-cache model on LongBench, because it learns to extract maximum information from limited memory — a kind of forced information compression that improves generalization. The SnapKV paper [Li et al., 2024] shows query-aware clustering improves accuracy; what if adapters learn to mimic and amplify this?

**Key Points:**
- Eviction-aware training: simulate KV cache budget constraints during LoRA fine-tuning (dropout analogy)
- Rank-budget coupling: AdaLoRA rank allocation guided by token eviction importance scores
- Counter-intuitive prediction: eviction-constrained fine-tuning may surpass full-cache baselines on LongBench

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's dropout analogy is evocative, but let's make it falsifiable. The core claim needs to be stripped to a testable nucleus: does training LoRA adapters under simulated KV eviction improve LongBench accuracy relative to sequential baselines?

I see two distinct hypotheses buried in what Nova said, and we must not conflate them. First: *eviction-robust adapters* — adapters trained with KV budget simulation generalize better to evicted-cache inference. Second: *rank-budget coupling* — AdaLoRA rank allocation guided by H2O attention scores improves parameter efficiency. These are testable independently, and conflating them produces a confounded experiment.

For the first hypothesis, the experiment is clean: take a base LLM (e.g., LLaMA-2-7B), fine-tune with standard AdaLoRA vs. AdaLoRA with simulated 50% KV eviction (mask tokens with lowest H2O scores during training), then evaluate on LongBench with both full-cache and 50%-evicted cache inference. The primary DV is LongBench accuracy; secondary is throughput. Falsification criterion: if eviction-trained adapters perform no better than standard adapters at 50% cache eviction, the hypothesis is false.

The dropout analogy is concerning mechanistically. Dropout acts on *individual neurons* independently, preserving sequence structure. KV eviction removes *entire token positions*, which breaks positional dependencies in a fundamentally different way. The adapter might learn to be robust to missing tokens, but it might also learn degenerate shortcuts — attending only to surviving tokens regardless of their relevance. What experimental control rules this out?

**Key Points:**
- Two separable hypotheses: (1) eviction-robust adapters, (2) rank-budget coupling — test independently
- Clean experimental design: AdaLoRA vs. AdaLoRA+KV-sim on LLaMA-2-7B, evaluate on LongBench
- Critical concern: token-position eviction breaks sequence structure unlike dropout — must control for degenerate shortcuts

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's separation of hypotheses is essential rigor, but I want to step back and assess what this research actually contributes to the field — because the *why it matters* will determine whether this is an ICML paper or a workshop note.

The field is moving in two directions simultaneously: (a) longer contexts via architectural innovation (Mamba, linear attention), and (b) cheaper inference via compression (KV eviction, quantization). What's conspicuously absent is the *intersection* — methods that make *fine-tuned* models inference-efficient. The entire PEFT literature assumes full KV cache at inference time. This is the genuine gap.

The contribution, if it works, is threefold. For practitioners: a drop-in fine-tuning recipe that produces models deployable under strict memory budgets without post-hoc accuracy loss. For theory: evidence that KV cache structure is a learnable signal during adaptation, not just a post-training engineering constraint. For the field: a new axis of evaluation — (accuracy, throughput) under fixed KV budget — that changes how we compare PEFT methods.

What worries me about the current framing is scope creep. The research question spans five sub-directions (KV cache, sub-quadratic, MoE, RAG, PEFT). This paper should laser-focus on KV+PEFT. The comparison baseline must be: standard AdaLoRA → H2O eviction at inference. The proposed method: AdaLoRA with KV-budget simulation during training → H2O eviction at inference. If this one comparison is compelling, the paper stands on its own.

The significance claim I would defend: first systematic study of *fine-tuning-eviction co-design*, establishing whether joint optimization is better than sequential application. This is cleanly positioned against H2O and SnapKV (which assume fixed pre-trained models) and against AdaLoRA/DoRA (which ignore inference constraints).

**Key Points:**
- Core contribution: first systematic study of fine-tuning–eviction co-design on LongBench/SCROLLS
- Scope discipline: laser-focus on KV+PEFT; drop sub-quadratic, MoE, RAG from this hypothesis
- New evaluation axis: (accuracy, throughput) at fixed KV budget changes PEFT comparison landscape

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground this in what's mechanistically possible. The eviction-aware training idea is theoretically sound — there's no physical or mathematical barrier. But there are two technical details that determine whether it works in principle.

First: the eviction policy during training must be *differentiable or at least approximable* for the adapter to learn from it. H2O's heavy-hitter selection is non-differentiable (it's a top-k operation on attention scores). If we apply it as a hard mask during forward passes, the gradient signal is still valid — the adapter sees what tokens are available and learns accordingly. This is essentially a structured form of attention masking, which is mathematically well-defined. No issue here.

Second: the eviction policy at training time must match the eviction policy at inference time. If training simulates H2O at 50% budget but inference uses SnapKV's query-aware clustering, the distribution mismatch will degrade performance. The experiment must fix the eviction policy across training simulation and inference evaluation. This is a methodological constraint, not a fundamental barrier.

The rank-budget coupling idea from Dr. Nova is less obviously feasible. AdaLoRA's SVD-based rank allocation uses importance scores from gradient information — coupling it to attention-based eviction scores creates a two-signal optimization that could interfere. The theoretical justification for why these signals align is not obvious. I'd recommend decoupling: test eviction-robust training with *fixed* rank first, then explore rank-budget coupling as a second ablation.

The LongBench evaluation is entirely feasible — it's a standard benchmark with public data. Throughput measurement requires specifying hardware (GPU model, batch size) in the experimental setup, but this is a reporting detail, not a barrier.

**Key Points:**
- Hard-mask eviction during training is mathematically valid (structured attention masking) — no fundamental barrier
- Critical constraint: eviction policy at training simulation must match inference eviction policy exactly
- Decouple rank-budget coupling from eviction-robust training — test the simpler hypothesis first

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — and I think we're converging on something genuinely strong here. Let me synthesize what's emerged and propose a refined hypothesis that addresses all the concerns raised.

Prof. Vera correctly identified two separable sub-hypotheses. Prof. Pax confirmed the mechanistic soundness of eviction simulation during training. Dr. Sage scoped it to KV+PEFT only. Here's the refined core:

**Refined Hypothesis:** Eviction-aware LoRA fine-tuning — training LoRA adapters on a pre-trained LLM while applying hard H2O-style KV eviction masks during the forward pass (simulating a fixed cache budget ratio r) — produces adapters that achieve higher task accuracy on LongBench than the sequential baseline (standard LoRA fine-tuning + H2O eviction at inference only), when both are evaluated under the same KV cache budget r at inference time.

This addresses Prof. Vera's falsifiability concern: the null hypothesis is that the two methods are statistically indistinguishable on LongBench accuracy at matched KV budget. The testable prediction is that eviction-aware adapters show ≥2% LongBench accuracy improvement over sequential baselines at r=50% KV retention. The 2% threshold is chosen to be both practically meaningful and detectable with LongBench's task variance.

Prof. Pax's concern about policy mismatch is addressed by fixing H2O as both the training simulation policy and the inference eviction policy throughout. Rank-budget coupling is demoted to an optional ablation — we don't need it for the core claim.

The remaining open question: what's the right range of cache budget ratios r to test? I'd suggest r ∈ {25%, 50%, 75%} — this captures aggressive compression, moderate compression, and near-full cache, giving a curve rather than a point comparison.

**Key Points:**
- Refined hypothesis: eviction-aware LoRA training → better LongBench accuracy than sequential baseline at matched KV budget
- Null hypothesis: no statistically significant difference between joint and sequential approaches on LongBench
- Testable prediction P1: ≥2% LongBench improvement at r=50% KV retention; test across r ∈ {25%, 50%, 75%}

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down: Dr. Ally's refined hypothesis is clean, but it has three unstated assumptions that could each invalidate the result.

**Assumption 1: Base model dependence.** The hypothesis is stated for "a pre-trained LLM" — but eviction patterns are highly model-specific. H2O's heavy-hitter distribution in LLaMA-2-7B may look completely different from Mistral-7B. If results hold only for one base model, the contribution is narrow. The experiment needs at least two base models, or the scope must be explicitly limited to one model with justification.

**Assumption 2: Task distribution specificity.** LongBench covers 21 tasks across 6 categories (single-doc QA, multi-doc QA, summarization, few-shot learning, synthetic tasks, code). Eviction-aware training may help on long-dependency tasks (multi-doc QA) but hurt on tasks where all tokens are needed (code completion). Reporting a single aggregate LongBench score obscures this. The experiment must report per-category results, or the 2% improvement claim could be masking task-specific regression.

**Assumption 3: Training data confound.** If the fine-tuning data distribution already contains long-context examples, the adapter may learn long-context robustness independently of the eviction simulation. The experiment must control for fine-tuning data — using the same instruction tuning data for both baseline and eviction-aware variants, with the only difference being the eviction mask during training.

What would convince me: per-category LongBench results on two base models, with matched fine-tuning data and matched eviction policy. If eviction-aware training shows consistent improvement across at least 4/6 LongBench categories on both models, I'm satisfied.

**Key Points:**
- Assumption 1: Results must hold on ≥2 base models, or scope must be explicitly narrowed with justification
- Assumption 2: Report per-category LongBench results — aggregate score can mask task-specific regression
- Assumption 3: Control for fine-tuning data distribution — same data for baseline and eviction-aware variants

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's stress-test is exactly what this hypothesis needed — and the good news is that all three concerns are addressable within the experimental design without requiring new data or annotations.

For Assumption 1 (model dependence): we test on LLaMA-2-7B and Mistral-7B-v0.1 — both have open weights, LongBench evaluation scripts exist for both, and they have meaningfully different attention patterns. This doubles the experimental scope but doesn't require new benchmarks.

For Assumption 2 (task distribution): LongBench's 21 tasks naturally decompose into the 6 categories Prof. Rex identified. Per-category reporting is just a different aggregation of the same evaluation run — no extra data needed.

For Assumption 3 (training data confound): use a fixed instruction-tuning subset — specifically the Alpaca-52k dataset or the LongAlpaca-12k dataset (which has long-context examples). The key is that *both* baseline and eviction-aware variants use identical data; the eviction mask is the only independent variable.

NOW we're onto something! The hypothesis is: eviction-aware LoRA training, with H2O eviction masks at fixed ratios r ∈ {25%, 50%, 75%}, improves LongBench per-category accuracy over sequential baselines on LLaMA-2-7B and Mistral-7B-v0.1, with matched fine-tuning data (LongAlpaca-12k) and matched H2O inference eviction policy. The mechanism is that adapters trained under token scarcity learn more information-efficient representations — compressed attention that extracts more from fewer tokens.

The throughput gain is a secondary metric: at r=50% KV retention, memory footprint drops by 50% with H2O, enabling larger batch sizes and higher throughput. This is independently valuable regardless of accuracy results.

**Key Points:**
- Model scope: LLaMA-2-7B + Mistral-7B-v0.1 (open weights, LongBench scripts exist)
- Fine-tuning data: LongAlpaca-12k, identical for baseline and eviction-aware variants
- Secondary metric: throughput (tokens/sec) at matched KV budget — independently valuable

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The joint eviction-aware fine-tuning paradigm is genuinely novel — no existing work trains PEFT adapters with simulated KV budget constraints. The dropout analogy to token-position eviction opens a creative research direction. The potential for eviction-constrained adapters to outperform full-cache baselines is a paradigm-shifting prediction that the community hasn't tested.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is now precisely falsifiable: standard LoRA+H2O-eviction vs. eviction-aware LoRA+H2O-eviction, evaluated on LongBench with per-category reporting. Null hypothesis is clear. Success criterion (≥2% LongBench improvement at r=50%) is quantitative and pre-registered. Confounds (training data, eviction policy) are controlled by design.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** First systematic study of fine-tuning–eviction co-design fills a genuine gap in the PEFT literature. Results on two base models with per-category reporting establish whether joint optimization is universally better or task-specific. The throughput-accuracy tradeoff curve across r ∈ {25%, 50%, 75%} provides actionable guidance for practitioners deploying LLMs under memory constraints.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Mechanistically sound — H2O hard-mask eviction during training is mathematically valid structured attention masking. No fundamental barriers. LLaMA-2-7B and Mistral-7B-v0.1 have open weights and LongBench evaluation tooling. LongAlpaca-12k is publicly available. H2O has open-source implementation (FMInference/H2O). The experiment is fully reproducible with existing tools.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is: **Eviction-aware LoRA fine-tuning** — training LoRA adapters on pre-trained LLMs (LLaMA-2-7B, Mistral-7B-v0.1) while applying hard H2O-style KV eviction masks at fixed budget ratios r during the forward pass — produces adapters that achieve higher per-category LongBench accuracy than the sequential baseline (standard LoRA fine-tuning followed by H2O eviction at inference) when both are evaluated under the same KV cache budget ratio r at inference time.

The causal mechanism is token-scarcity regularization: adapters trained under enforced token absence learn more information-efficient attention representations, extracting higher utility from surviving KV cache entries. This is analogous to dropout as a regularizer, but operating at the token-position level rather than the neuron level.

The core prediction is a ≥2% LongBench accuracy improvement over sequential baselines at r=50% KV retention, with consistent improvement across at least 4/6 LongBench task categories on both base models. Secondary prediction: r=50% eviction reduces KV cache memory by 50%, enabling proportional throughput improvement (tokens/sec) at matched batch size.

The experimental design is fully specified: LongAlpaca-12k fine-tuning data (identical for baseline and proposed method), H2O eviction policy fixed across training simulation and inference, evaluation on LongBench 21 tasks with per-category reporting, tested at r ∈ {25%, 50%, 75%}. No new benchmarks, synthetic data, or human annotation required. All components publicly available.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The 2% success threshold is reasonable but somewhat arbitrary — results should be reported with confidence intervals and significance testing (e.g., paired t-test across LongBench tasks)
- LongAlpaca-12k's long-context distribution may favor eviction-aware training by construction — a sanity check on standard Alpaca-52k (short-context) would confirm the benefit is specific to long-context adaptation
- **Mitigation Strategy:** Report both LongAlpaca-12k and Alpaca-52k fine-tuning variants; apply statistical significance testing on per-category results; this adds one additional experimental variant without requiring new data
