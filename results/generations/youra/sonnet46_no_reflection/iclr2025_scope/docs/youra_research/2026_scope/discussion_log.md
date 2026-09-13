# Phase 2A Research Discussion Log
# Gap: Joint LoRA Adapter Training and KV Cache Eviction Policy Co-Optimization
# Generated: 2026-05-20 | Architecture: Self-Contained Tikitaka Loop v10.0.0

---

## Discussion Briefing

**Research Gap Selected:** Gap 1 (HIGH+PRIMARY — Critical)

**Gap Title:** Joint LoRA Adapter Training and KV Cache Eviction Policy Co-Optimization

**Gap Description:**
No published work jointly trains LoRA adapter weights and KV eviction policies with evaluation on standard NLP benchmarks. Existing work (Locret, LESS, kvpress) applies KV compression to frozen or already-fine-tuned models. arXiv 2604.21335 introduces sub-token routing combining routed LoRA with value-group KV routing, but focuses on language modeling quality (perplexity/RULER), not standard NLP benchmark performance (GLUE/SuperGLUE/long-context benchmarks). Amazon ICR (EACL 2026) shows fine-tuning brings moderate KV compression robustness but does not optimize KV eviction jointly with adapter training.

**Missing Piece:** A training framework that jointly optimizes (1) LoRA adapter weights for task-specific performance and (2) KV eviction/compression parameters (e.g., retaining head weights, eviction thresholds, routing masks) within a single differentiable objective, evaluated on standard NLP benchmarks with memory/compute budget constraints.

**Key Papers for Reference:**
- [Locret 2024] Trained retaining heads for KV eviction — PEFT-style training, not co-trained with LoRA
- [LESS 2024] Low-rank recurrence + KV eviction design pattern
- [arXiv 2604.21335, 2025] Sub-token routing: routed LoRA + value-group KV routing (perplexity/RULER only)
- [Amazon ICR, EACL 2026] SFT/RL fine-tuning improves KV compression robustness moderately

**Key Repos:**
- NVIDIA/kvpress (★1025): Forward-hook KV compression, combinable with PEFT
- huangyuxiang03/Locret (★14): Trained retaining heads, extensible to co-train with LoRA
- amazon-science/icr-kv-caching (★1): SFT+RL + KV compression evaluation
- hjeon2k/LRAgent: Decomposes KV into base+LoRA components

**MANDATORY FEASIBILITY CONSTRAINTS (Pipeline-Enforced):**
- Reject: new benchmarks, rubrics, or scoring frameworks
- Reject: synthetic/generated data or future data that does not yet exist
- Reject: human evaluation, annotation, or subjective scoring
- Accept: hypotheses testable immediately using existing real datasets and existing benchmarks

**Research Question:** Can PEFT (LoRA-style) fine-tuning and KV cache compression strategies be jointly optimized to reduce inference cost and adaptation overhead for long-context foundation models, without sacrificing task-specific performance on standard NLP benchmarks?

**Participants:** Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we stopped thinking of LoRA and KV cache compression as separate post-hoc techniques and instead treated the eviction policy itself as a differentiable adapter? Here's the core idea: the same low-rank structure that makes LoRA so parameter-efficient can be used to parameterize KV importance scores. Imagine a shared low-rank matrix — call it the "resonance matrix" — whose left factor shapes the LoRA update for Q/K/V projections and whose right factor simultaneously scores each KV token for eviction likelihood.

What excites me is that this is not just engineering combination. arXiv 2604.21335 showed that sub-token routing can jointly gate LoRA paths and KV value groups using the same routing signal. But they evaluated only on perplexity and RULER. The genuine novelty here would be demonstrating that a single joint gradient — flowing from a GLUE/SuperGLUE task loss backward through both the adapter weights and the eviction head weights — produces better task performance AND better compression than decoupled training. That would be a real paradigm shift.

The cross-domain analogy: think of how QLoRA proved that joint quantization + LoRA training produces better results than post-hoc quantization of a LoRA-trained model. The same principle should hold for KV eviction — joint training should outperform "train LoRA first, then apply Locret." The Locret paper [Huang et al., 2024] showed that learned retaining heads can be trained with less than 1 GPU hour. If we co-train those heads with LoRA adapters end-to-end, we get a genuinely novel unified framework.

Three unconventional angles worth exploring: (1) The "resonance" angle: treat the LoRA bottleneck matrices as shared signal producers for both adaptation and eviction routing; (2) The "calibration" angle: use the task gradient to recalibrate which KV entries matter for downstream performance, not just perplexity; (3) The "gating" angle: let the LoRA router in arXiv 2604.21335's architecture also serve as the KV eviction mask with joint end-to-end training.

**Key Points:**
- Joint gradient through both LoRA weights AND eviction policy is the untested novelty
- arXiv 2604.21335 proves architectural feasibility; the gap is NLP benchmark evaluation
- QLoRA analogy: joint compression+adaptation consistently beats decoupled approaches
- Low-rank structure of LoRA is naturally suited to parameterize KV importance scoring

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's enthusiasm is infectious, but let me immediately ask: what experimental result would convince us this hypothesis is WRONG?

The core claim seems to be: "joint end-to-end training of LoRA adapter weights and KV eviction policy parameters outperforms the decoupled baseline on GLUE/SuperGLUE, while achieving equal or better memory compression ratio." That is testable and falsifiable. The null hypothesis is clear: joint training produces no statistically significant improvement in NLP benchmark accuracy over the decoupled approach under matched compression ratios.

The decoupled baseline must be carefully specified. Three variants: (B1) Train LoRA → freeze → apply Locret (no training); (B2) Train LoRA → freeze → apply kvpress (no training); (B3) Train LoRA → freeze → fine-tune Locret heads with LoRA frozen. B3 is the hardest to beat and the most scientifically important comparison.

The measurement protocol must specify: (1) same compression ratio (e.g., 50% KV budget) for all conditions; (2) same base model (LLaMA-3.1-8B); (3) same GLUE tasks (MNLI, SST-2, QNLI) plus at least one long-context benchmark (LongBench or RULER); (4) statistical significance testing across 3+ seeds. GLUE and LongBench are both existing real datasets — no new benchmarks needed.

What would falsify this? If the decoupled baseline B3 matches joint training performance within confidence intervals, joint end-to-end training provides no meaningful advantage. That would still be a publishable null result, but the hypothesis would be wrong.

**Key Points:**
- Falsification condition: decoupled baseline B3 matches joint training within CI
- Three baselines required: B1 (frozen Locret), B2 (kvpress), B3 (sequential fine-tune)
- Existing benchmarks suffice: GLUE + LongBench or RULER
- Statistical significance across 3 seeds is non-negotiable

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: why does the community need this now, and why would this finding matter beyond the immediate experiment?

The timing is significant. We are in a period where inference efficiency has become the primary bottleneck for LLM deployment — not accuracy. Models like LLaMA-3.1-8B can be fine-tuned with LoRA at low cost, but serving them at scale with long contexts remains expensive. The industry has converged on two independent solutions: PEFT for adaptation, KV compression for serving. The fact that nobody has formally tested whether joint training outperforms this decoupled status quo is a genuine gap — not an oversight, but a natural consequence of how the two communities evolved separately.

The scientific contribution here is not just a new method. It is a characterization study with a clear directional claim. If joint training wins, we provide the community with a principled justification to redesign fine-tuning pipelines for serving-aware adaptation. If it fails to beat B3 — sequential fine-tuning of each component — we save the community from an expensive research direction. Both outcomes are publishable and impactful.

What makes this genuinely non-incremental? arXiv 2604.21335 demonstrates architectural feasibility but evaluates on perplexity/RULER, not GLUE/SuperGLUE. LESS [Dong et al., 2024] combines low-rank recurrence with eviction but is not a LoRA adapter approach. There is no paper that directly addresses: "does end-to-end joint training of PEFT adapters and KV eviction parameters outperform decoupled training on standard NLP benchmarks?" That exact question is unaddressed.

**Key Points:**
- Timing is right: inference efficiency is the community's current primary challenge
- Both positive and null results are publishable and impactful
- Direct differentiation from arXiv 2604.21335: NLP benchmark evaluation is the missing piece
- Opens a new research direction: serving-aware PEFT training pipelines

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me be realistic. The mechanism needs scrutiny — not for cost reasons, but for technical soundness.

The core technical question: can we backpropagate a task loss jointly through LoRA adapter weights AND KV eviction/retaining head weights? The answer is yes, if the eviction mechanism is differentiable. Locret's retaining heads [Huang et al., 2024] are differentiable neural networks — there is no fundamental barrier to substituting a task loss gradient. The key concern is the eviction step itself: if eviction is implemented as hard top-k selection, the gradient does not flow through the selection operation.

This is solvable. Locret uses soft scoring during training and hard eviction at inference — the standard approach in learned sparse methods (see PruLong [Princeton, 2024] which learns 0/1 attention head masks via soft-to-hard training). arXiv 2604.21335 uses learned routing which is also differentiable during training. So the mechanism IS technically feasible.

The second concern: gradient interference. LoRA gradients flow through the adapter matrices into Q/K/V projections. Eviction head gradients flow through the retaining head which observes KV representations post-projection. These gradient paths are independent at the parameter level — they share the frozen base model weights but optimize separate parameter sets. Interference is unlikely in practice.

The proposed interventions can work in principle, and all evaluation infrastructure is publicly available.

**Key Points:**
- Hard top-k eviction blocks gradients — must use soft scoring during training (established practice)
- Gradient interference between LoRA and eviction head is unlikely (separate parameter sets)
- PruLong and Locret establish the soft-to-hard training pattern as technically sound
- Joint differentiable training IS feasible; no fundamental barrier exists

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND — Prof. Pax just gave us the key implementation detail that makes this hypothesis strong: soft-score eviction during training (differentiable), hard eviction at inference. This is exactly the established pattern in PruLong and Locret.

The emerging hypothesis: **Under standard PEFT fine-tuning conditions with a KV budget constraint, if LoRA adapter weights and KV eviction head weights are jointly trained end-to-end via a differentiable task loss (using soft scoring during training, hard eviction at inference), then the joint approach will achieve higher GLUE/SuperGLUE accuracy at a fixed KV compression ratio than decoupled baselines, because the eviction policy learns which KV entries are task-relevant rather than just attention-score-relevant.**

The "because" clause is crucial and novel: standard KV eviction policies (H2O, SnapKV, Locret) prioritize high-attention-score tokens. But task-relevant tokens for GLUE tasks (the hypothesis token in MNLI, the sentiment anchor in SST-2) may not always have the highest raw attention scores — especially after LoRA modifies Q/K projections. Joint training directly optimizes eviction for task outcomes.

The LRAgent implementation already decomposes KV into base+LoRA components, providing a natural starting codebase. We control for confounds by fixing the KV budget (50% KV retention) across all conditions and testing 3+ seeds.

**Key Points:**
- Strengthened causal mechanism: task-relevant KV tokens differ from high-attention KV tokens after LoRA
- Soft scoring during training resolves the gradient problem (established pattern)
- LRAgent codebase provides a natural starting point for implementation
- Fixed KV budget across all conditions controls the primary confound

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — or at least where I need convincing.

**First concern:** The hypothesis assumes that LoRA-modified Q/K projections systematically misalign with existing eviction heuristics. But where is the evidence? arXiv 2604.21335 uses a routed LoRA where the routing signal IS the eviction signal. If their approach works even with separate objectives (LM loss + routing), why would task-specific training provide meaningful additional benefit? We need a clearer argument for why task loss specifically changes which KV entries should be retained.

**Second concern:** GLUE tasks are predominantly short-context. The KV compression benefit is most significant for long-context scenarios. If we evaluate on standard GLUE (max 512 tokens), the KV cache is small and eviction barely matters — the compression ratio advantage disappears. The hypothesis needs to specify evaluation on long-context versions or use LongBench. But then we're not testing on "standard NLP benchmarks" in the traditional sense.

**Third concern:** The "because" mechanism — task-relevant tokens differ from high-attention tokens — is an assumption, not an established fact. If the LRAgent codebase already decomposes KV into base+LoRA components, we could run an attribution analysis to verify whether LoRA-modified attention patterns produce different eviction priorities. Without this, the mechanism is speculative.

**Mitigation Strategy:** Address concern 2 by explicitly including both short-context GLUE and long-context LongBench in the evaluation; compression ratio matters differently in each regime, and both are existing real benchmarks.

**Key Points:**
- Need evidence that task loss specifically changes eviction priorities vs. LM loss
- GLUE is short-context — KV compression benefits require long-context evaluation
- Must include both GLUE (task performance) and LongBench (where compression matters)
- Mechanism assumption (task-relevant differs from high-attention) needs empirical grounding

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex just made our hypothesis STRONGER by forcing precision. The short-context GLUE concern reshapes everything into a more interesting two-regime structure.

Here's the refined framing: the hypothesis operates in TWO conditions with different predictions. In SHORT-context GLUE (where KV cache is small and eviction rarely triggers), joint training acts as a regularizer — the eviction head learns which tokens are task-relevant, which may itself improve LoRA's Q/K attention pattern quality. We'd predict modest accuracy gains (1-2% on GLUE). In LONG-context settings (LongBench, RULER), where eviction actually matters, we'd predict stronger gains (3-5%) because the eviction policy now meaningfully changes what information survives to the attention layers.

This two-regime structure is actually NOVEL and more interesting than a single claim. No prior work has studied how joint training affects performance across the short-to-long-context transition. And both GLUE and LongBench are existing, real benchmarks — no new data needed.

On the concern about why task loss specifically helps vs. LM loss: language modeling rewards predicting the next token, which favors syntactic and local context retention. Task loss on classification rewards retaining the discriminative tokens — the sentiment anchor, the contradiction indicator, the entity. These can be different sets. arXiv 2604.21335 already shows that routing signal trained on LM loss behaves differently from raw attention scores — task loss should produce even more differentiated routing.

The two-regime experiment is the innovation.

**Key Points:**
- Two-regime evaluation: short-context GLUE (regularizer effect) + long-context LongBench (eviction effect)
- Different predictions for each regime: modest gains on GLUE, stronger on LongBench
- Task loss vs. LM loss: discriminative tokens differ from next-token-predictive tokens
- Both GLUE and LongBench are existing benchmarks — fully feasible immediately

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The two-regime framing is scientifically cleaner. Let me formalize the testable predictions.

**Prediction P1 (Primary — Long-context regime):** JointLoRA-KV achieves ≥3% higher accuracy than B3 (sequential LoRA→Locret fine-tune) on LongBench-QA tasks (NarrativeQA, Qasper, MultiFieldQA) at 50% KV budget, with p<0.05 across 3 seeds using LLaMA-3.1-8B. Falsification: B3 matches or exceeds joint training within CI.

**Prediction P2 (Secondary — Short-context regime):** JointLoRA-KV achieves ≥1% higher accuracy than B3 on GLUE (MNLI, SST-2, QNLI) at 50% KV budget AND matches standard LoRA (no eviction) within ±0.3% at 100% KV budget. Falsification: JointLoRA-KV degrades standard LoRA performance at full KV budget.

**Prediction P3 (Mechanism check — Attribution):** Attention attribution analysis shows that LoRA-modified attention weights assign statistically different importance scores to task-relevant tokens vs. Locret's retaining head scores on 100 MNLI examples from an existing fine-tuned model (Spearman ρ < 0.7). Falsification: ρ ≥ 0.7 (high correlation — no task-attention mismatch exists).

Baselines: B1 (LoRA → Locret frozen), B2 (LoRA → kvpress no training), B3 (LoRA → Locret sequential fine-tune). All use existing models, existing benchmarks. No new data, no human raters.

**Key Points:**
- P1 (primary): ≥3% LongBench QA improvement at 50% KV budget, p<0.05 across 3 seeds
- P2 (secondary): ≥1% GLUE improvement + no degradation at full KV budget
- P3 (mechanism): Attribution analysis confirms task-relevant differs from high-attention (ρ < 0.7)
- All feasibility constraints satisfied: existing datasets, models, and benchmarks only

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The measurement plan is technically valid. Let me verify the implementation path.

Base model: LLaMA-3.1-8B (HuggingFace). LoRA injection via PEFT library. Standard. ✅

KV eviction module: Locret retaining heads (public code). Replace distillation loss with cross-entropy task loss. Soft scoring during training already implemented in Locret. ✅

Joint training framework: LoRA adapter parameters and Locret retaining head parameters placed in the same optimizer. Gradients flow from task loss through both parameter sets independently — no architectural conflict. ✅

Evaluation: GLUE via HuggingFace datasets (existing). LongBench via public GitHub (existing). KV budget control via Locret's budget_ratio parameter (already implemented). ✅

Attribution analysis (P3): Forward pass with attention capture, Locret head scoring, Spearman correlation. Standard PyTorch operations. ✅

One minor implementation note: for GLUE with sequences ≤ 512 tokens, 50% KV budget retains 256 tokens — marginal eviction. We should verify Locret handles short sequences gracefully. This is an implementation detail, not a fundamental barrier.

No fundamental barriers. All proposed interventions can work in principle with publicly available infrastructure.

**Key Points:**
- LLaMA-3.1-8B + HuggingFace PEFT + Locret: all public, compatible, no barriers
- Joint optimizer over LoRA and retaining head parameters: technically straightforward
- All benchmarks (GLUE, LongBench) exist and are publicly accessible
- Short-sequence edge case: implementation detail, not fundamental barrier

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask now: have we achieved sufficient novelty differentiation from arXiv 2604.21335?

Mapping the differentiation on four dimensions: (1) Training objective: their routing is trained on language modeling loss; ours uses task-specific classification loss — the core testable claim. (2) Evaluation: they evaluate on perplexity and RULER; we evaluate on GLUE + LongBench QA — the genuine benchmark gap. (3) Granularity: their routing operates at the value group level (coarser); ours operates at the token level via retaining heads (Locret). (4) Architecture: they use a shared routing matrix; we use separately parameterized but jointly optimized components (LoRA A/B vs. retaining heads).

Our hypothesis is differentiated on ALL FOUR dimensions. The most scientifically important differentiation is (1): the claim that task-specific loss produces better-aligned eviction than language modeling loss is the core testable claim. If we prove this, we establish that serving-aware PEFT training requires task-aware eviction.

The related work positioning is clear: cite arXiv 2604.21335 as "closest prior work" differentiated on evaluation and training objective; cite Locret as the eviction baseline we build upon; cite LESS as the design pattern for low-rank + eviction combination; cite Amazon ICR as confirming the fine-tuning/KV compression interaction.

If the hypothesis validates, it redefines the fine-tuning pipeline: practitioners should not fine-tune with LoRA and then compress — they should co-train. This is a direct operational recommendation.

**Key Points:**
- Four-dimensional differentiation from arXiv 2604.21335: loss function, benchmarks, granularity, architecture
- Core novelty: task loss produces better eviction alignment than LM loss
- Clear related work positioning for all four key papers
- Operational implication: redefines recommended fine-tuning pipeline for practitioners

---

### Exchange 11

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me address Prof. Rex's remaining concern about mechanism evidence and bring the hypothesis to its final form.

Prof. Rex asked for evidence that task loss specifically changes eviction priorities vs. LM loss. We address this without new data: we use the MNLI attribution analysis (P3) as a pre-experiment diagnostic. Using an existing LoRA-fine-tuned LLaMA-3.1-8B on MNLI (publicly available fine-tuned checkpoints on HuggingFace Model Hub) and Locret retaining head scores, we compute the Spearman correlation. If ρ < 0.7, the mechanism assumption is empirically supported before we run the full joint training. This is a falsifiable pre-registration check using only existing models and existing data.

The hypothesis in its final form:

"Under standard PEFT conditions with a fixed KV budget (50% retention), jointly training LoRA adapter weights and KV eviction head weights end-to-end via a task classification loss (soft scoring during training, hard eviction at inference) will outperform the best decoupled baseline (sequential LoRA→Locret fine-tune, B3) by ≥3% on LongBench-QA tasks and ≥1% on GLUE (MNLI, SST-2, QNLI), because task-specific gradient signals direct eviction toward discriminatively relevant tokens rather than merely high-attention-score tokens, as confirmed by attribution analysis showing Spearman ρ < 0.7 between LoRA attention weights and Locret retaining scores."

Scope: applies to transformer LLMs with KV cache. Does NOT apply to SSM-based models (Mamba, RWKV) which have no KV cache.

**Key Points:**
- P3 attribution analysis serves as pre-experiment diagnostic using existing data only
- Final hypothesis is precise, falsifiable, and uses only existing benchmarks
- Scope boundary explicit: transformer KV cache models; excludes SSMs
- All Prof. Rex's concerns addressed with concrete methodological responses

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I'll acknowledge the improvements. The attribution analysis (P3) as a pre-experiment diagnostic is a genuine methodological contribution.

But one remaining concern must be addressed: the sequential baseline B3 is not trivial. Locret's retaining heads were trained in less than 1 GPU hour. If sequential fine-tuning of Locret heads after LoRA training already achieves near-optimal KV-task alignment, then joint training provides no additional value.

The hypothesis needs to clearly articulate WHY joint training beats B3. The argument: joint training allows the LoRA adapter weights themselves to adapt to the KV budget constraint — not just the eviction heads adapting to LoRA-modified representations. In B3, LoRA is frozen when Locret is fine-tuned, so adapter weights are optimized without awareness of future eviction. In joint training, LoRA learns to produce representations that are simultaneously task-discriminative AND eviction-friendly — discriminative information is concentrated in a smaller subset of KV entries. This "representation compression" effect would not be captured by B3.

If this is the mechanism, then P1 should be supplemented with a representation-level diagnostic: compare information content of the top-50% retained KV entries between joint training and B3. The hypothesis predicts that joint-trained models concentrate more task-relevant information in their retained KV entries. This is measurable with existing probing classifiers (train a linear probe on retained vs. evicted KV representations for MNLI label prediction — all existing data).

Adding this as Prediction P4: probing accuracy on retained KV entries ≥5% higher for joint vs. sequential. This directly tests the "representation compression" mechanism.

**Key Points:**
- B3 (sequential fine-tune) is not trivial — must clearly explain why joint training beats it
- Key mechanism: joint training lets LoRA adapt to the KV budget constraint
- "Representation compression": discriminative info concentrates in fewer KV entries
- P4 added: probing classifier on retained KV entries tests mechanism directly

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex just identified the REAL novelty! The representation compression effect is not a side observation — it IS the deepest claim.

The hypothesis is not simply "joint training gets better benchmark scores." The deeper claim is that joint LoRA+KV training induces a qualitatively different learned representation: one where the adapter explicitly concentrates task-discriminative information into a smaller, eviction-survivable subset of the KV cache. This is a new way of thinking about what PEFT optimization does to internal representations under serving constraints.

Cross-domain resonance with knowledge distillation: when a student is trained knowing it will have a compressed knowledge base, it learns to organize knowledge differently than a student trained without that constraint. The parallel for LLMs: train knowing some KV entries will be evicted → learn to front-load discriminative signal into high-retention entries.

The paradigm shift: we move from "efficiency is a post-processing step" to "efficiency-awareness during adaptation changes what the model learns." This is genuinely new framing that opens a research program, not just a single experiment.

The novelty story is now complete: (1) first systematic NLP benchmark evaluation of joint LoRA+KV training; (2) identification of the "representation compression" effect as the mechanism; (3) empirical validation via probing (P4) and attribution (P3); (4) operational recommendation to redesign PEFT pipelines as serving-aware.

**Key Points:**
- Representation compression = the deepest novelty claim, not just benchmark improvement
- Parallel to knowledge distillation: budget-awareness during training changes learned representations
- Paradigm shift: efficiency-awareness during adaptation changes what the model learns
- Novelty story complete: benchmark evaluation + mechanism identification + operational implications

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Excellent synthesis from Dr. Nova. Let me finalize the complete testable prediction set.

**Complete Prediction Set:**

**P1 (Primary — Benchmark Performance):** JointLoRA-KV achieves ≥3% higher accuracy than B3 on LongBench-QA (NarrativeQA, Qasper, MultiFieldQA) at 50% KV budget, p<0.05 across 3 seeds with LLaMA-3.1-8B. Falsification: B3 matches or exceeds joint training within CI.

**P2 (Secondary — Short-context + Boundary Condition):** JointLoRA-KV achieves ≥1% higher accuracy on GLUE (MNLI, SST-2, QNLI) at 50% KV budget AND matches standard LoRA (no eviction) within ±0.3% at 100% KV budget. Falsification: JointLoRA-KV degrades at full budget OR fails to improve on GLUE.

**P3 (Mechanism — Attribution Mismatch):** Spearman ρ < 0.7 between LoRA-modified attention scores and Locret retaining head scores on 100 MNLI examples from an existing fine-tuned model. Falsification: ρ ≥ 0.7.

**P4 (Mechanism — Representation Compression):** Linear probing accuracy on TOP-50% retained KV entries is ≥5% higher for JointLoRA-KV vs. B3 on MNLI task label prediction. Falsification: probing accuracy difference < 5%.

All predictions: existing models (LLaMA-3.1-8B + HuggingFace PEFT), existing benchmarks (GLUE, LongBench, MNLI), existing tools (captum, linear probe). No new data, no human raters, no new scoring frameworks.

All pipeline feasibility constraints satisfied:
- Existing benchmarks only (GLUE, LongBench, MNLI)
- Existing real data only
- No human evaluation
- No new scoring frameworks

**Key Points:**
- Four predictions: P1 (primary benchmark), P2 (short-context + boundary), P3 (attribution), P4 (probing)
- All falsifiable with quantitative thresholds
- All use existing datasets, models, and evaluation infrastructure
- All pipeline feasibility constraints satisfied

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Final feasibility verification. The complete experimental protocol is technically sound.

Implementation path:
1. LLaMA-3.1-8B from HuggingFace. LoRA injection via PEFT library. ✅
2. Locret retaining heads (public code). Replace distillation loss with cross-entropy task loss. Joint optimizer over LoRA A/B matrices and retaining head weights. ✅
3. GLUE tasks via HuggingFace datasets. Fine-tune on MNLI, SST-2, QNLI. ✅
4. LongBench evaluation via public GitHub. ✅
5. Attribution (P3): Forward pass with attention capture → Locret head scoring → Spearman correlation. Standard PyTorch. ✅
6. Probing (P4): Freeze joint-trained model → extract KV representations → train linear layer on retained vs. evicted entries → report accuracy. Standard ML evaluation. ✅

Scope confirmed: applies to transformer-based LLMs with KV cache (LLaMA, Mistral, Qwen families). Does not apply to SSMs (Mamba, RWKV) or linear attention models.

All 6 convergence criteria are now met:
- SPECIFIC: Clear core claim stated ✅
- MECHANISM: How it works explained (soft-to-hard training, representation compression) ✅
- PREDICTIONS: 4 testable predictions with quantitative criteria ✅
- NOVELTY: Differentiated from arXiv 2604.21335 on four dimensions ✅
- FEASIBILITY: All components publicly available, no fundamental barriers ✅
- OBJECTIONS: Sequential baseline B3, short-context concern, mechanism evidence all addressed ✅

**Key Points:**
- Full implementation path verified: all components public and compatible
- Short-sequence edge case on GLUE: implementation detail, not fundamental barrier
- Scope boundary explicit: transformer KV cache models only
- All 6 convergence criteria satisfied — discussion has converged

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis introduces a genuinely novel claim — that efficiency-awareness during adaptation (joint training) changes what the model learns, producing "representation compression" as a qualitatively new effect. The differentiation from arXiv 2604.21335 on four dimensions (loss function, benchmarks, granularity, architecture) is clean and defensible. The two-regime evaluation design (short-context GLUE + long-context LongBench) is itself a novel experimental contribution. This is not incremental improvement but a paradigm-level claim about what PEFT optimization can do under serving constraints.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously specified with four predictions (P1-P4), each with quantitative thresholds and explicit falsification conditions. The null hypothesis is clearly stated. The three-baseline design (B1, B2, B3) with B3 as the hardest comparator is methodologically sound. All predictions use existing benchmarks and real data — no ambiguity in evaluation protocol. The pre-experiment diagnostic (P3) adds a pre-registration component that strengthens scientific rigor.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The research addresses a genuine community need at the right moment — when inference efficiency is the primary bottleneck for LLM deployment. Both positive and null results are publishable and directionally important for the field. The operational implication — that PEFT pipelines should be redesigned as serving-aware — is a concrete recommendation that practitioners can act on. The "representation compression" mechanism, if validated, opens a new research program at the intersection of PEFT and efficient serving.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All implementation components are publicly available and technically compatible. The soft-to-hard training pattern for differentiable eviction is established in PruLong and Locret — no novel infrastructure required. Gradient paths for LoRA and retaining heads are independent at the parameter level — no interference. The one edge case (short sequences in GLUE) is an implementation detail, not a fundamental barrier. The complete evaluation infrastructure (GLUE, LongBench, captum, linear probing) exists today.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on a hypothesis that is specific, mechanistic, and directly testable with existing infrastructure. The core claim: jointly training LoRA adapter weights and KV eviction head weights end-to-end via a task classification loss — using soft scoring during training and hard eviction at inference — will outperform decoupled fine-tuning approaches (particularly the sequential LoRA→Locret baseline, B3) on both short-context GLUE tasks (MNLI, SST-2, QNLI) and long-context LongBench QA tasks, at a fixed 50% KV budget.

The mechanism is the key innovation: joint training induces "representation compression" — the LoRA adapter learns to concentrate task-discriminative information into a smaller subset of KV entries that will survive eviction, rather than distributing it across the full context. This is not captured by sequential fine-tuning (B3) because LoRA weights are frozen when the eviction heads are trained in B3. The mechanism is validated by two diagnostics: (P3) attribution analysis confirming that LoRA-modified attention scores and Locret retaining scores are misaligned (ρ < 0.7) using existing MNLI data, and (P4) probing classifier showing higher task-relevant information concentration in retained KV entries for joint training vs. sequential.

The experimental design uses LLaMA-3.1-8B (open weights), HuggingFace PEFT (LoRA), Locret (retaining heads, public code), GLUE (existing), LongBench (existing), and standard PyTorch evaluation tools. No new benchmarks, no synthetic data, no human raters. The hypothesis is fully testable immediately with existing resources. Both positive results (joint training wins) and null results (B3 matches joint training) are scientifically valuable and publishable.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The B3 baseline (sequential LoRA→Locret fine-tune) may be stronger than expected if Locret's retaining heads can rapidly adapt to LoRA-modified representations in 1 GPU hour — the performance gap for P1 (≥3% on LongBench) may be optimistic.
- GLUE performance differences at 50% KV budget on short sequences (P2, ≥1%) may be noise-level if eviction is rarely triggered at this context length — the effect may only be visible on longer GLUE variants or LongBench.
- The "representation compression" mechanism (P4) needs careful experimental design: the linear probe must be trained on KV representations from the same layer across conditions, controlling for representation scale differences.
- **Mitigation Strategy:** Pre-register all experimental details before running. Run P3 (attribution diagnostic) first as a cheap pre-experiment check — if ρ ≥ 0.7, revisit the mechanism assumption before committing to the full training run. For P2, supplement with LongBench if GLUE effects are below threshold.

---

