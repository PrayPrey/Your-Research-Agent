# Phase 2A Discussion Log
**Workflow:** phase2a-dialogue  
**Architecture:** Self-Contained Tikitaka Loop (Independent Controller Ablation)  
**Gap ID:** gap-2  
**Gap Title:** No PEFT Method Exploiting SSM State Structure (State-Aware PEFT)  
**Date:** 2026-08-31  
**Execution Mode:** UNATTENDED  

---

## Briefing Context

### Research Gap Selected
**Gap 2 (PRIMARY, Critical):** No existing PEFT method exploits the recurrent state structure (A/B/C matrices) of SSMs. All current PEFT methods (LoRA, AdaLoRA, IA³, DoRA) target projection layers only (in_proj, out_proj, x_proj), ignoring the SSM state dynamics that constitute the "memory" of these architectures.

### Key Technical Facts
- **Mamba-1:** A/B/C are `nn.Parameter` (not `nn.Linear`) — LoRA inapplicable directly; A_log must remain negative for stability
- **Mamba-2:** A is a scalar per SSM head — trivially adaptable via IA³-style multiplicative scaling
- **dt_proj** is `nn.Linear` and controls Δ (timescale gate) — partial state proxy, applies to standard LoRA
- **Experimental infrastructure:** state-spaces/mamba + huggingface/peft + EleutherAI/lm-eval-harness + GLUE/MMLU = complete, existing

### Papers Available
- P1: Mamba [Gu & Dao, 2023] — mamba_2312.00752_summary.md
- P2: Mamba-2 [Dao & Gu, 2024] — mamba2_2405.21060_summary.md
- P3: LoRA [Hu et al., 2022] — lora_2106.09685_summary.md

### Feasibility Constraints (Pipeline-Enforced)
- NO new benchmarks or rubrics
- NO synthetic/generated data
- NO human evaluation
- ONLY existing datasets (GLUE, MMLU, LongBench) and existing benchmarks

### Previous Failure / Routing Context
First Phase 2A attempt — no previous failure context. No Serena memory files found.

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we approach this from an angle nobody has tried yet — not just asking "can LoRA work on SSMs?" but instead asking "what does an SSM *need* that transformers don't, and how should PEFT reflect that?" The fundamental novelty here is that SSMs have *memory state* — a compressed representation of all past tokens — that transformers don't have in the same sense. Transformers grow their KV cache linearly; SSMs compress everything into a fixed-size state vector.

NOW we're onto something! The A matrix in Mamba controls *how fast information decays* in that state. In Mamba-1, A_log is a channel-wise log-scale decay parameter. In Mamba-2, it's reduced to a scalar per head. Here's the creative angle: when you fine-tune on a new task, you're not just asking the model to learn new input-output mappings — you're asking it to *remember different things for different durations*. A legal document task needs long-range dependency; a sentiment task needs short-range local context. The A matrix controls this temporal horizon.

What if state-aware PEFT is fundamentally about *task-adaptive memory horizons*? Instead of adding LoRA to projection layers (which only changes what gets put into and read from state), we should adapt *how long* information persists. For Mamba-2 with scalar A per head, this is breathtakingly simple: add a learned scalar offset to each head's decay rate. The parameter budget is O(num_heads) — essentially free. For Mamba-1, we could add a small learned bias to A_log per channel, clipped to maintain stability.

The cross-domain connection: this is analogous to how attention heads in transformers learn different "attention spans" — some heads attend locally, others globally. Task-specific fine-tuning of attention patterns is well-studied. State-aware PEFT is the SSM analog: task-specific temporal decay adaptation. What if we call this **"Temporal Decay Adaptation" (TDA)**?

**Key Points:**
- SSMs have a distinct inductive bias: fixed-size compressed memory with learnable decay
- Task-adaptive decay rates (A matrix) = the SSM-specific analog of attention span adaptation
- Mamba-2 scalar A makes this O(num_heads) parameter adaptation — near-zero overhead
- Hypothesis: TDA + standard LoRA on projections > naive LoRA alone, because projections only change what enters/exits state, not how state evolves

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing framing, but I need to immediately flag the testability structure here. "Task-adaptive memory horizons" is a beautiful intuition, but before we name it, we need to establish what a falsifiable test of this claim looks like. Let me be precise.

The evidence suggests the central claim is: *learning task-specific decay rates (A adaptation) provides accuracy gains beyond what projection-layer LoRA alone achieves on downstream NLP benchmarks.* This is testable. The experiment is clean: (1) Baseline A — full fine-tuning on Mamba-130m/370m/1.3b; (2) Baseline B — LoRA on {in_proj, out_proj, x_proj} only, rank r=8; (3) Treatment — LoRA on projections + learned scalar offset on A (Mamba-2) or learned bias on A_log (Mamba-1); (4) Evaluate on GLUE (SST-2, MNLI, QNLI, QQP) and MMLU. All of these exist. No new benchmarks needed.

What would convince me this hypothesis is wrong? If Treatment C achieves accuracy within 0.5% of Baseline B on all GLUE tasks, then the A-adaptation contributes nothing measurable. The null hypothesis is precisely: H₀ = adapting A provides no statistically significant accuracy improvement over projection-only LoRA at equal or lower trainable parameter count. This is a proper null.

What I want to stress-test: the stability concern. Mamba-1's A_log must remain negative (A = -exp(A_log), so A_log can be any real number but A is always negative — decay is guaranteed). Adding a learned bias to A_log preserves stability automatically. Prof. Pax should confirm this, but mathematically: A_bar = exp(Δ · A) ∈ (0,1) for A < 0, Δ > 0 — this bound is preserved regardless of A_log magnitude. So stability is not actually a concern for A_log adaptation in Mamba-1. This removes a key objection I anticipated.

What specific, measurable predictions can we make? At minimum: (P1) Treatment improves GLUE average ≥ 1% over Baseline B at matched parameter count; (P2) improvement is larger on tasks requiring longer-range dependencies (e.g., MNLI > SST-2); (P3) optimal learned A values differ systematically across tasks.

**Key Points:**
- Null hypothesis is clean and falsifiable: A-adaptation provides no gain over projection-only LoRA
- Stability concern is resolved: A_log adaptation preserves A < 0 automatically
- Experiment design uses only existing benchmarks (GLUE, MMLU) and existing models
- Prediction P2 (longer-range tasks benefit more from A adaptation) is the key distinguishing claim

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this mean for the field, and is there genuine novelty here worth a publication? Let me assess the significance landscape carefully.

The broader context: PEFT for transformers is mature — LoRA, AdaLoRA, DoRA, IA³ all have systematic evaluations on GLUE, MMLU, instruction tuning. The gap that matters is whether SSM-specific inductive biases warrant SSM-specific PEFT methods. This matters because if SSMs are to replace transformers in deployed systems (inference efficiency, constant memory), practitioners need fine-tuning guidance. Right now there is no guidance.

This matters because the contribution is twofold. First: the existence question — does any form of PEFT on Mamba achieve performance competitive with full fine-tuning? This alone answers a practitioner question. Second: the novelty question — does architecture-aware PEFT (adapting state dynamics) outperform architecture-agnostic PEFT (LoRA on projection layers)? This is the scientific contribution. If the answer to the second is yes, this establishes a new design principle: PEFT methods should be co-designed with the inductive biases of their target architecture.

What makes this genuinely new versus incremental? The key is the A-matrix adaptation angle. MambaPEFT-style work (if it exists) likely applies LoRA to projection layers only — treating Mamba as "just another architecture with linear layers." The state-aware PEFT idea is conceptually distinct: it exploits the recurrent structure that makes SSMs different. Whether it works empirically is the research question, but the conceptual framing is novel.

The significance claim that opens new research directions: if state-aware PEFT works for Mamba, the principle extends to RWKV (WKV operator), RetNet (retention decay γ), and future SSM architectures. This could become a general paradigm: "memory-aware PEFT" for any model with persistent state. That is field-shaping if validated.

**Key Points:**
- Dual contribution: existence proof (PEFT works on Mamba) + novelty claim (state-aware > naive)
- Opens new research direction: architecture-aware PEFT as general principle for recurrent models
- Significance depends on the empirical result — but the question is well-posed and answerable
- Practical impact: practitioners deploying Mamba need fine-tuning guidance; this provides it

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here and examine whether the proposed mechanism is technically sound before we get too excited. I want to validate three things: (1) is A-adaptation in Mamba-1 actually as simple as a learned bias on A_log? (2) is the Mamba-2 scalar-A adaptation even distinguishable from standard LoRA on nearby layers? (3) is the parameter budget comparison fair?

On (1): Prof. Vera is correct that A_log adaptation preserves stability automatically — since A = -exp(A_log), any real value of A_log gives A < 0, so state decay is guaranteed stable. The learned bias δ ∈ ℝ^{d_model} adds per-channel adaptation with no constraints needed. Implementation: A_log_adapted = A_log_pretrained + δ where δ is the only trainable parameter. This is a bias term on a parameter tensor, not a LoRA decomposition — it's even simpler. For Mamba-130m with d_model=768, this is 768 floats — negligible.

On (2): This is where I have a genuine concern. In Mamba-2, A is a scalar per head and is already closely coupled to the linear projections. When we adapt the scalar A, are we really learning something structurally different from what LoRA on B and C matrices already captures? Consider: the output at each step is y_t = C_t · h_t where h_t = α · h_{t-1} + B_t · x_t. Adapting C (via LoRA) changes how state is *read*; adapting B (via LoRA) changes how input is *written* to state; adapting α changes *how much past state persists*. These are genuinely distinct operations — α controls memory horizon in a way B and C cannot replicate. So the mechanism is real and non-redundant with projection LoRA.

On (3): Fair comparison requires matching parameter counts. Naive LoRA on {in_proj, out_proj, x_proj} at rank r=8 for Mamba-130m (d_model=768) yields roughly: in_proj (768→3072, ~12K), out_proj (3072→768, ~12K), x_proj (3072→80, ~1.2K) per layer × 24 layers ≈ 600K trainable params. Adding A_log bias: 768 × 24 = 18K params — ~3% overhead. This is negligible and doesn't require reducing LoRA rank to compensate. The comparison is clean.

The mechanism is physically/mathematically valid. I'm satisfied this can work in principle.

**Key Points:**
- A_log bias is trivially stable: no constraints needed, A = -exp(A_log) is always negative
- α (scalar A in Mamba-2) is non-redundant with B/C LoRA — controls memory horizon uniquely
- Parameter overhead of A-adaptation is ~3% of naive LoRA budget — comparison is clean
- Implementation: just add a trainable bias tensor to A_log or a learned scalar multiplier to α

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this further by synthesizing what has emerged and proposing a concrete refinement that addresses the remaining weakness. The discussion has converged on something real: we have a technically sound, falsifiable, novel hypothesis. Let me defend and sharpen it.

The core hypothesis as it's emerging: **Under fine-tuning on standard NLP benchmarks (GLUE, MMLU), if we adapt Mamba's recurrent state decay parameters (A_log bias for Mamba-1; scalar A multiplier for Mamba-2) alongside standard LoRA on projection layers, then downstream task accuracy improves beyond projection-only LoRA, because the A-parameter controls task-specific memory horizons that projections cannot replicate — adaptation of decay rates allows the model to tune how much long-range context it retains per task.**

What evidence supports this claim? From Mamba paper [Gu & Dao, 2023]: A_log is initialized to log(-A) where A follows a specific initialization to match HiPPO polynomial projection bases — this initialization is optimal for general sequence modeling, not for specific tasks. Task-specific fine-tuning should benefit from relaxing this initialization toward task-relevant timescales. From Mamba-2 [Dao & Gu, 2024]: the scalar A per head creates a clean ablation — we can train models with A frozen vs. A adapted and directly measure the contribution.

One refinement I want to propose to address Prof. Rex's likely concern about confounding: we should also test dt_proj LoRA as an intermediate condition. dt_proj controls Δ (timescale/step-size), which indirectly modulates how much A contributes per step (A_bar = exp(Δ·A)). This creates a 4-condition experiment: (A) projection-only LoRA, (B) projection + dt_proj LoRA, (C) projection + A-adaptation, (D) full state-aware (projection + dt_proj + A-adaptation). This isolates the contribution of direct vs. indirect state adaptation.

**Key Points:**
- Core hypothesis is technically sound, falsifiable, and novel per persona assessments
- A_log initialization (HiPPO-based) is general-purpose — task-specific adaptation is theoretically motivated
- 4-condition ablation design isolates direct A-adaptation from indirect dt_proj-mediated adaptation
- The hypothesis subsumes Gap 1 (baseline PEFT benchmarking) as condition A

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — or at least where I need answers before I'll sign off. I have three specific concerns that need addressing.

**Concern 1: The dt_proj confound is larger than Dr. Ally acknowledged.** dt_proj is the primary mechanism through which the input modulates state dynamics in Mamba. Δ = softplus(dt_proj(x) + dt_bias) controls A_bar = exp(Δ·A). If we adapt dt_proj via LoRA in condition B, we're already indirectly adapting how much A influences the state at each step. The difference between condition B (dt_proj LoRA) and condition C (A_log bias) may be small in practice because both indirectly control the effective decay rate. Show me evidence that A_log bias and dt_proj LoRA are not largely redundant. Dr. Ally's 4-condition design addresses this partially but we need to verify the conditions are actually distinguishable.

**Concern 2: Scale sensitivity.** Mamba-130m is a small model. Results at 130m may not hold at 370m or 1.3b. The hypothesis should commit to at least one scale above 130m — otherwise a reviewer will reject it as too preliminary. What would convince me is: results replicated on at least Mamba-370m. This uses an existing checkpoint and existing benchmarks — it's just compute.

**Concern 3: The baseline for GLUE is weak.** GLUE tasks are mostly classification with short inputs (SST-2: ~20 tokens, MNLI: ~100 tokens). The A-adaptation "memory horizon" hypothesis predicts stronger effects on longer-range tasks. If we only evaluate on GLUE, we might see no effect (short sequences don't need long memory) and incorrectly conclude state-aware PEFT doesn't work. We need at least one longer-range benchmark — LongBench or SCROLLS — where the memory horizon theory predicts a larger effect.

**Mitigation strategy:** Include (a) Mamba-370m alongside 130m; (b) at least one long-context benchmark (LongBench subset — existing, no new rubrics); (c) report dt_proj-only vs. A_log-only conditions separately to test redundancy.

**Key Points:**
- dt_proj LoRA and A_log bias may be partially redundant — must test both independently
- Scale validation at ≥370m required for credibility
- Short-sequence GLUE alone is insufficient — long-context benchmark (LongBench) needed to validate "memory horizon" claim
- These concerns are addressable within the existing infrastructure — no new benchmarks required

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer) + 🛡️ **Dr. Ally** (Synthesis):

Prof. Rex has done exactly what we needed — sharpened the design. NOW we're onto something truly solid. Let me address all three concerns and finalize the hypothesis.

On **Concern 1 (dt_proj redundancy)**: The mathematical distinction is clean. dt_proj LoRA changes Δ as a function of input x — it's *input-dependent* timescale adaptation. A_log bias changes the *base decay rate* unconditionally — it shifts the prior distribution of how fast information decays, independent of input. These are complementary, not redundant: dt_proj LoRA adapts "how much does THIS token affect the timescale?" while A_log bias adapts "what is the default forgetting rate for this task?" Think of it as fine-tuning the prior (A) vs. fine-tuning the likelihood update (Δ). In the 4-condition experiment, we expect: projection-only < projection+dt_proj < projection+A_log < projection+dt_proj+A_log, with the A_log conditions showing a qualitatively different gain pattern (larger on long-context tasks).

On **Concern 2 (scale)**: Agreed. The hypothesis commits to Mamba-130m AND Mamba-370m as minimum. Both have pretrained checkpoints on HuggingFace. The 370m experiment uses identical code — just swapping the model checkpoint.

On **Concern 3 (benchmark scope)**: Agreed and incorporated. The evaluation suite will be: GLUE (SST-2, MNLI, QNLI, QQP) for short-range + LongBench (2WikiMultihopQA, NarrativeQA subset) for long-range. LongBench is an existing benchmark with existing Mamba evaluation not yet published — this is an open slot.

**Final hypothesis after all refinements:**

Under fine-tuning of Mamba SSMs (130m, 370m) on NLP classification and long-context benchmarks (GLUE + LongBench subset), if we adapt the recurrent state decay parameters (A_log bias for Mamba-1; scalar A multiplier for Mamba-2) in addition to standard LoRA on projection layers (in_proj, out_proj, x_proj, dt_proj), then downstream task accuracy improves beyond projection-only LoRA (GLUE average ≥1%, LongBench ≥2%), because A-adaptation modifies task-specific memory horizons (base forgetting rate) in a way that projection-layer LoRA cannot replicate, with the gain pattern being qualitatively larger on longer-range tasks.

**Key Points:**
- All three of Prof. Rex's concerns incorporated into experimental design
- dt_proj and A_log adaptation are mathematically distinct (input-dependent vs. unconditional decay adaptation)
- Evaluation: GLUE + LongBench subset — all existing, no new benchmarks
- Scale: Mamba-130m + Mamba-370m — both existing checkpoints
- 4-condition ablation: projection-only → +dt_proj → +A_log → full state-aware

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The "Temporal Decay Adaptation" framing is genuinely novel — no prior PEFT work targets the SSM state decay parameter directly. The conceptual contribution (memory-horizon adaptation as distinct from projection adaptation) opens a new design axis for PEFT co-designed with recurrent inductive biases. This is not incremental — it's a new category of parameter-efficient adaptation.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Null hypothesis is clean: H₀ = A-adaptation provides no statistically significant accuracy improvement over projection-only LoRA at matched parameter count. The 4-condition ablation on GLUE + LongBench with two model scales provides multiple independent falsification opportunities. Success criteria are quantitative and pre-specified.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Dual contribution structure is well-motivated: existence proof (PEFT works on Mamba at all) plus novel principle (state-aware > naive). If validated, establishes architecture-aware PEFT as a general paradigm for recurrent models (RWKV, RetNet, future SSMs). Practical impact is immediate — practitioners need this guidance.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Implementation is straightforward: A_log bias is a bias tensor addition (no constraints needed due to exp transform); scalar A multiplier in Mamba-2 is a learned per-head scalar. Parameter overhead is ~3% of naive LoRA budget. All required models and benchmarks exist. The mechanism is physically and mathematically sound with no fundamental barriers.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on a well-specified, falsifiable, and novel hypothesis: **State-Aware LoRA (SA-LoRA)** for Mamba SSMs. The core claim is that fine-tuning Mamba's recurrent state decay parameters (A_log bias in Mamba-1; scalar A multiplier in Mamba-2) alongside standard LoRA on projection layers improves downstream NLP task accuracy beyond projection-only LoRA, because A-adaptation modifies task-specific memory horizons in a way projection layers cannot replicate.

The proposed mechanism has three steps: (1) LoRA on projection layers adapts what information enters and exits the SSM state; (2) A_log bias adaptation shifts the base decay rate, allowing the model to retain information for task-appropriate durations (longer for multi-hop QA, shorter for sentiment); (3) Together, these two forms of adaptation are complementary — one controls the channel, the other controls the filter. The null hypothesis (A-adaptation provides no gain) is falsified if GLUE average improves ≥1% or LongBench improves ≥2% under state-aware conditions versus projection-only baseline.

The experimental design is clean: 4 conditions × 2 model scales (Mamba-130m, 370m) × 2 benchmark suites (GLUE, LongBench subset) using all existing infrastructure. No new data collection, no human annotation, no new benchmarks required. The hypothesis is immediately executable.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The dt_proj LoRA condition (B) and A_log bias condition (C) may show smaller separation than theory predicts if Mamba's training has already partially co-adapted Δ and A
- LongBench evaluation requires Mamba to handle long sequences in generation mode — verify lm-eval-harness supports Mamba for generation tasks (not just classification)
- **Mitigation Strategy:** Include a diagnostic — report the learned A_log biases after fine-tuning and verify they differ systematically across GLUE tasks (should be smaller magnitude for SST-2, larger for MNLI). If biases are near-zero across all tasks, the null hypothesis holds and the experiment is self-reporting. For LongBench generation: test on 2WikiMultihopQA (extractive QA, shorter outputs) as primary long-context task.
