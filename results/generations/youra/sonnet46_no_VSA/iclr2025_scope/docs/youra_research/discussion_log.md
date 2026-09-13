# Phase 2A Discussion Log

**Gap ID:** gap-1  
**Gap Title:** No cross-strategy accuracy comparison on LongBench v2 task-category splits for converted models  
**Started:** 2026-08-03T14:00:00Z  
**Architecture:** Self-Contained Tikitaka Loop  
**Execution Mode:** UNATTENDED  

---

## Previous Failure / Routing Context

**Recursive Entry v4** — Phase 2A invoked after prior hypothesis failures. Mandatory context from Serena memories:

### h-e1 — SUPERSEDED (2026-08-03T12:30:00Z)

- **Reason:** Gate FAIL — LongBench v2 retrieval↔compression axis NOT empirically separable. PC1 explains 98.85% variance (threshold <60%); max cross-cluster Spearman ρ = 1.0000 (threshold <0.70). Overall model capability (transformers ~40-50% vs SSMs ~22-28%) dominates all variance, making axis separability untestable without controlling for capability tier.
- **Prohibited redesign direction:** Any hypothesis that tests retrieval vs. compression "axis structure" without first controlling for the ~20pp capability gap between transformer and SSM families.
- **Proposed direction (from supersede record):** Control for overall capability via normalization or residualization; test within SSM family only; or use relative axis scores.
- **Reusable components:** `build_accuracy_matrix()`, `run_pca()`, `compute_cross_cluster_spearman()`, `evaluate_gates()`, `verify_mechanism_activated()`, `generate_all_figures()` from prior codebase.
- **Data collected (reusable):** 8 baselines (5 transformers + 3 SSMs) across 6 LongBench v2 categories.

### h-m2 (Run 1) — PARTIAL (2026-08-03T12:00:00Z)

- **Reason:** Experiment incomplete — Condition B (H2O + 10% boundary reservation) not yet finished. Condition A showed catastrophic eviction at 50% KV compression (boundary retention = 10.4%, accuracy = 2.8%).
- **Prohibited redesign direction:** KV cache eviction approaches, H2O-style greedy eviction, boundary token preservation in KV compression. Catastrophic degradation at 50% KV compression is a fundamental limitation.
- **Env note:** Use `youra-h-m3-v2` env (torch 2.11.0+cu128) for LLaMA-3-8B; avoid `youra-h-m1`.
- **What showed promise:** MOHAWK-style distillation pipeline; LongBench v2 evaluation infrastructure; boundary token retention metric.

### Constraints for New Hypothesis

1. **MUST NOT** test retrieval↔compression axis separability without capability-tier controls
2. **MUST NOT** involve KV cache eviction, H2O, or greedy budget-based compression
3. **MUST** use existing benchmarks (LongBench v2, SCROLLS) — no new benchmarks
4. **MUST** be testable with existing open-source models and datasets immediately
5. **MUST NOT** require human evaluation, synthetic data, or new annotations

---

## Research Briefing

**Research Gap (Gap 1 — Critical/Primary):**

No existing paper compares all three sub-quadratic conversion strategies (MOHAWK SSM distillation, LAWCAT linear attention substitution, hybrid layer replacement) on the SAME LongBench v2 task-category splits. Each existing method is evaluated on a different benchmark:
- MOHAWK/phi-mamba: perplexity + standard lm-eval tasks
- LAWCAT: passkey retrieval / S-NIAH / BABILong (up to 22K tokens)
- DSLA-Serve: internal long-context QA/summarization
- None: LongBench v2's 6 task categories (single-doc QA, multi-doc QA, summarization, few-shot, synthetic, code)

**Research Questions this addresses:**
- DQ1: Which conversion strategy achieves highest accuracy retention?
- DQ3: Do retrieval-heavy tasks show larger post-conversion drops than summarization/QA?

**Available Papers (5 prepared as MD):**
- P1: `papers/arxiv_2509_18467.md` — LAWCAT (EMNLP 2025)
- P2: `papers/arxiv_2408_10189.md` — MOHAWK (NeurIPS 2024)
- P3: `papers/arxiv_2507_09025.md` — Lizard linearization framework
- P4: `papers/arxiv_2505_07793.md` — Overflow Prevention / recurrent LLMs on LongBench v2
- P5: `papers/arxiv_2507_00449.md` — SSM long-context limitations

**Evaluation Infrastructure (ready):**
- THUDM/LongBench (1210★) — 6 task categories, 503 questions, 8k–2M context
- EleutherAI/lm-evaluation-harness — LongBench v2 PR #3256
- goombalab/mohawk + goombalab/phi-mamba
- zeyuliu1037/LAWCAT

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The gap before us is genuinely exciting — and the failure history makes the path clearer, not murkier. H-E1 taught us that *overall model capability* dominates when we treat transformer and SSM families as interchangeable experimental units. H-M2 taught us that KV compression is a dead end at aggressive rates. Both failures point toward the same unexplored territory: **what happens to task-specific accuracy patterns when we surgically convert a single transformer into a sub-quadratic architecture, holding the starting point constant?**

Here's the unconventional angle I want to put on the table: we've been thinking about this as "which conversion strategy wins overall?" But the richer question is **"does conversion introduce a task-type × strategy interaction?"** If MOHAWK-converted LLaMA-3-8B drops 30% on multi-doc QA but only 5% on summarization, while LAWCAT-converted LLaMA-3-8B shows the opposite pattern, that's a finding worth a paper — even if neither achieves ≥90% overall retention.

The novelty here is the **controlled factorial design**: same base model (LLaMA-3-8B), three conversion strategies (MOHAWK, LAWCAT, zero-shot hybrid replacement), evaluated on LongBench v2's 6 task categories. No prior work has held the base model constant across strategies. MOHAWK reports results for Phi-1.5→Mamba; LAWCAT reports for Mistral-7B→linear attention; DSLA-Serve uses their own internal eval. We'd be the first to hold the base model fixed and compare across strategies on a standardized long-context benchmark.

Three angles worth exploring:

1. **Task-type differential degradation**: The theoretical prediction is that retrieval-heavy tasks (multi-doc QA, synthetic) should degrade more than compression-friendly tasks (summarization, few-shot) because retrieval requires attending to specific needle tokens in long contexts, which SSMs and linear attention can't do perfectly.

2. **Conversion depth × task interaction**: MOHAWK has three stages (matrix alignment → hidden state alignment → weight transfer). We could ask: at Stage 1 conversion only (incomplete conversion), is the task-type interaction already visible, or does it emerge only at full conversion?

3. **The "capability-matched baseline" solution**: H-E1's PC1 dominance problem came from comparing different-capability models. The solution is simple: use the *same* base transformer as both the experimental unit (convert it) and the baseline (don't convert it). The delta is pure conversion effect, controlling capability perfectly.

**Key Points:**
- Fixed base model (LLaMA-3-8B) eliminates H-E1's capability confound completely
- Task-type × strategy interaction is the novel scientific contribution
- MOHAWK + LAWCAT pipelines are runnable today; LongBench v2 eval is ready
- No new benchmarks, no synthetic data, no human annotation needed

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, your instinct to hold the base model constant is correct. The evidence suggests that prior comparisons conflated architectural effects with capability and data scale. MOHAWK demonstrates that, for Phi-1.5→Phi-Mamba, most of the teacher's downstream accuracy can be retained with only 3B tokens and strong stage complementarity (Stages 1–3 outperform Stage 3 alone) [MOHAWK, 2024]. However, the crucial question for LLaMA‑3‑8B is not *whether* conversion can work in principle, but **whether the structured mixer can approximate LLaMA's attention matrices sufficiently well at 8B scale**. What would disprove feasibility? If Stage 1 Frobenius distances between LLaMA attention matrices and the SSD/SSM mixer remain an order of magnitude above those reported for Llama2-7B fits (e.g., >0.5 at N=64 where ~0.097 was achieved on WT-103) [MOHAWK, 2024], and this correlates with ≥15% absolute accuracy loss on long-context tasks, then the architectural expressivity is insufficient for full conversion.

Your proposed task-type × strategy interaction must be formalized as a falsifiable prediction. Here is one: **Retrieval-heavy LongBench categories (multi-doc QA, synthetic needle tasks) will exhibit ≥2× larger relative accuracy drop than summarization/few-shot tasks after full MOHAWK conversion.** Success criterion: statistically significant interaction (two-way ANOVA, p<0.01) between {task type} × {conversion strategy}. Failure criterion: uniform degradation across task types (no significant interaction). Without explicit thresholds, "differential degradation" becomes interpretive rather than scientific.

On feasibility: MOHAWK required 3B tokens for a 1.5B model and substantial Stage 3 stabilization (reduced LR, clipping) [MOHAWK, 2024]. LLaMA‑3‑8B is ~5× larger. A linear scaling of distillation tokens would imply ~15B tokens; anything substantially lower risks underfitting the mixer. Therefore, we should pre-register a scaling test: run Stage 1–2 on 8B for 1B tokens and measure hidden-state L2 alignment (as in Eq. 4 tracking). If L2 plateaus at >1.5× the relative alignment error observed in Phi-Mamba, we halt—the student cannot align adequately at this budget. This is the "early failure detector" that protects compute.

Critically, we must control for hybrid baselines. MOHAWK's hybrid (4 attention layers retained) recovers most of the teacher's average score (66.0 vs 67.2) [MOHAWK, 2024]. Prediction: **If full 8B conversion loses >10% average LongBench accuracy but a 4-layer hybrid loses <5%, then full conversion is unjustified.** That is a clear disconfirmation pathway for the "full replacement is viable" claim. Additionally, we must report matrix-approximation error per layer and correlate it with per-task degradation. If no correlation emerges, the theoretical basis (matrix expressivity ↔ accuracy) is weakened.

Finally, edge cases: long-context extrapolation beyond 2k tokens. MOHAWK distillation used 2048-length sequences [MOHAWK, 2024]. If we evaluate at 16k–32k without distillation at those lengths, any degradation could reflect distribution shift rather than architectural limits. Therefore, conversion must include long-context distillation data; otherwise, the test is confounded.

The evidence suggests your design can be rigorous—but only if we predefine quantitative failure conditions and scaling checkpoints. Without them, we risk producing an interpretive ablation study rather than a decisive test of feasibility.

**Key Points:**
- Define explicit falsification thresholds (e.g., ≥15% absolute loss or non-significant task × strategy interaction).
- Use Stage 1–2 alignment metrics as early feasibility gates before full 8B distillation.
- Compare full conversion against hybrid baselines; if hybrid clearly dominates, full replacement is not justified.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera, your alignment metric gates are exactly the kind of compute-protecting mechanism we need, but I want to ground the feasibility discussion in what LAWCAT actually found about the distillation token budget [Liu et al., LAWCAT 2025]. LAWCAT achieved >90% passkey retrieval at 22K tokens using only 1K-length sequences during distillation and "less than 0.1% pre-training tokens compared with pre-training models." If Mistral-7B's pre-training used ~1T tokens, that's <1B distillation tokens for a 7B model — not 15B. The key mechanism is LAWCAT's causal Conv1D layer, which captures local dependencies that global linear attention misses, allowing the student to generalize beyond its distillation context length.

This changes the feasibility calculus considerably. For LLaMA-3-8B, which is comparable in size to Mistral-7B, we might need ~1B tokens rather than ~15B. That's within a single-GPU reasonable compute budget (~2-4 days on A100). However, LAWCAT was evaluated only on S-NIAH and BABILong — both synthetic retrieval tasks. The unresolved question is whether this token efficiency generalizes to LongBench v2's diverse task categories (single-doc QA, multi-doc QA, summarization, few-shot, code). If LAWCAT's 90% retrieval efficiency is task-specific to needle-in-a-haystack, then the summarization/few-shot categories might show very different efficiency profiles.

This raises the central practical concern: **do we need separate distillation recipes per task category, or is one unified distillation sufficient?** The Phase 1 literature found that DSLA-Serve (ICML 2025) uses layer-selective replacement with different ratios per layer. If attention layers early in the network handle local context and later layers handle long-range retrieval, a single conversion strategy may not be uniformly appropriate. This is testable: hold distillation data constant, convert with MOHAWK vs. LAWCAT vs. uniform layer replacement, and measure category-specific accuracy on LongBench v2.

On the MOHAWK pipeline for LLaMA-3-8B specifically: `goombalab/mohawk` uses YAML-configured DDP/FSDP and integrates directly with `lm-evaluation-harness`. The LAWCAT repo (`zeyuliu1037/LAWCAT`) uses Flash Linear Attention. Both pipelines exist and are runnable. The realistic bottleneck is **GPU memory and time**, not code availability. LLaMA-3-8B MOHAWK Stage 1+2 at 1B tokens (bf16, gradient checkpointing) needs ~4× A100 80GB for ~3-5 days. LAWCAT at the same token budget is closer to 2× A100. This is tight but feasible for a research compute allocation.

The recommendation: start with LAWCAT conversion of LLaMA-3-8B (lower token budget, faster), run LongBench v2 category eval, use that as the "baseline conversion" result. Then run MOHAWK Stage 1+2 only and compare. If the task-type × strategy interaction exists, it will appear in this smaller experiment before we commit to full MOHAWK Stage 3.

**Key Points:**
- LAWCAT token budget is ~1B not ~15B; single GPU feasible in 3-5 days
- LAWCAT's efficiency advantage may be retrieval-task-specific — LongBench v2 categories test this
- Staggered execution (LAWCAT first, then MOHAWK) protects compute while building evidence
- Both pipelines runnable today: Flash Linear Attention + lm-evaluation-harness + THUDM/LongBench

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is finally becoming testable. But here's where this still breaks down: you're implicitly assuming that **MOHAWK's matrix-approximation results at 1.3B–7B scale transfer cleanly to LLaMA‑3‑8B**. Show me the evidence for that. In MOHAWK [2024], SSD achieves Frobenius ≈0.097 at N=64 when fitting Llama2‑7B attention matrices, and general SSM ≈0.046. Fine. But that's at sequence length 512 and on a random head sample. Your LongBench evaluation targets 16k–32k. The mixing matrix structure at 512 is not necessarily representative of 32k. If matrix fit quality degrades superlinearly with N, your entire "expressivity ↔ accuracy" correlation could collapse at long context. What would convince me is: fit Frobenius error **as a function of N up to 4k at least**, before any full distillation. If error scales badly, stop.

Second unstated assumption: that task-type degradation reflects architectural limits rather than **distillation distribution shift**. MOHAWK distilled on C4 with length 2048 and showed strong downstream retention on short-context reasoning tasks (Winogrande, ARC, etc.) with only 3B tokens [MOHAWK, 2024]. But those tasks don't probe retrieval over 20k tokens. If your LongBench multi-doc QA drops 25%, is that because SSMs can't retrieve needles — or because you never distilled on sequences longer than 2k? Right now, your hypothesis conflates architecture with training curriculum. To make this causal, you need a 2×2: {short-only distillation, mixed-length distillation} × {MOHAWK, LAWCAT}. If long-context distillation erases the task-type interaction, your architectural claim weakens substantially.

Now about your interaction claim. "≥2× larger relative drop for retrieval-heavy tasks" is a start, but it's soft. Relative to what baseline variance? LongBench categories differ in intrinsic variance and ceiling effects. A 10% drop from 90→80 is not the same as 60→50. I want **per-task normalized degradation**: (Student − Teacher) / (Teacher − RandomBaseline). Then test interaction via mixed-effects modeling, not just ANOVA, because tasks are nested within categories. What would convince me is a statistically robust interaction that survives normalization and multiple-comparison correction. Otherwise, you're reporting noise with a narrative.

On feasibility: Pax is optimistic about LAWCAT's 1B-token efficiency. Maybe. But LAWCAT's evidence base is synthetic retrieval (S‑NIAH, BABILong). MOHAWK, in contrast, demonstrated stage complementarity and showed Stage 1+2 measurably improve over Stage 3 alone [MOHAWK, 2024]. That tells us matrix and hidden-state alignment are not decorative — they matter. If you run LAWCAT first, fine, but you must include an ablation equivalent to "Stage 3 only" in MOHAWK terms. If LAWCAT behaves like pure logit distillation and underperforms once tasks require structural reasoning, that's the critical comparison.

Finally, your hybrid baseline is not optional. MOHAWK Table 2 shows that retaining just 4 attention layers recovers most teacher performance (66.0 vs 67.2 avg) [MOHAWK, 2024]. If your full 8B conversion loses >10% average LongBench accuracy while a 4-layer hybrid loses <5%, the rational conclusion is that **full replacement is architecturally inferior for general-purpose long-context reasoning**. Pre-register that. If you're unwilling to accept that outcome, then this isn't a stress test — it's advocacy.

**Key Points:**
- Test mixer expressivity scaling with sequence length before full distillation; 512-token fits don't guarantee 32k fidelity.
- Separate architectural limits from distillation distribution shift via a 2×2 curriculum × strategy design.
- Pre-register hybrid dominance as a valid disconfirmation of full conversion viability.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Rex has correctly identified the architectural-vs-curriculum confound. But I want to zoom out from the mechanistic debate and address the significance question directly: **does this experiment matter enough to be worth doing, given what the field already knows?**

The Overflow Prevention paper [2505.07793] evaluated Falcon3-Mamba, RecurrentGemma, and RWKV6 on LongBench v2 — these are scratch-trained SSMs, not converted ones. The result: chunk-based recurrent inference is competitive with transformers on most categories. But the key point is they evaluated *scratch-trained* models at 7-9B. If converted models perform comparably to scratch-trained SSMs on LongBench v2, the paper's message is "conversion wastes effort." If they outperform significantly, the message is "transformer priors matter." Either outcome is publishable — but the second outcome is far more impactful.

LAWCAT [Liu et al., 2025] concludes: "LAWCAT thus provides an efficient pathway to high-performance, long-context linear models suitable for edge deployment, reducing reliance on extensive long-sequence training data and computational resources." The phrase "reducing reliance on long-sequence training data" is the key claim. If we can show that converted models generalize better across LongBench v2 task categories than same-scale scratch-trained SSMs despite shorter distillation, that directly supports this claim with stronger evidence than S-NIAH can provide.

The impact case is clear: a paper that provides the first **controlled head-to-head comparison** of (a) converted LLaMA-3-8B via MOHAWK vs. LAWCAT, (b) hybrid 4-layer retained baseline, and (c) best scratch-trained SSM at matched parameter count (Mamba-3B or RWKV-7B), all evaluated on LongBench v2's 6 categories, fills a gap that every subsequent conversion paper will need to cite. The "significance" criterion for this research is not "does one strategy win clearly" — it's "does the community now have a systematic comparison it currently lacks?"

Prof. Rex's 2×2 curriculum design is scientifically stronger, but it doubles the GPU compute. Given feasibility constraints, I recommend a **staged significance design**: Stage 1 — LAWCAT vs. MOHAWK on LongBench v2 (short-context distillation only, fixing curriculum). This is the minimal publishable unit. Stage 2 — if task-type × strategy interaction is significant, add mixed-length distillation arm to isolate curriculum effect. Stage 2 only runs if Stage 1 finds a significant interaction. This design is sequentially valid and publishable at Stage 1 if the interaction result is compelling.

The impact question for the hypothesis is therefore: is a task-type × strategy interaction at fixed distillation curriculum novel and significant? Yes — because the field has no data on this, the comparison uses a standardized benchmark, and the result directly informs practitioners on which strategy to use for which application (retrieval vs. summarization workloads).

**Key Points:**
- Scratch-trained SSM baseline (from Overflow Prevention paper) anchors the "does conversion help?" question
- LAWCAT's own significance claim ("reduces reliance on long-sequence training") is directly testable on LongBench v2
- Staged design: Stage 1 (fixed curriculum, 2 strategies) → Stage 2 (curriculum ablation) only if Stage 1 finds interaction

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

Rex is correct: before we debate curricula or token budgets, we must test *expressivity scaling*. MOHAWK demonstrates a clear correlation between Frobenius matrix fit and downstream accuracy — SSD ≈0.097 vs. Toeplitz ≈12 at N=64, with corresponding large accuracy gaps [MOHAWK, 2024]. The evidence suggests that structured mixer fidelity is not cosmetic; it is mechanistically linked to task retention. However, those fits were conducted at sequence length 512. Our first falsifiable checkpoint: **fit LLaMA‑3‑8B attention matrices with SSD/general SSM at N ∈ {512, 1k, 2k, 4k}.** Pre‑register the criterion: if Frobenius error scales superlinearly such that error(N=4k) ≥ 3× error(N=512), or exceeds 0.3 absolute, we suspend full conversion.

On the architectural-versus-curriculum confound: MOHAWK distilled exclusively at length 2048 on C4 [MOHAWK, 2024], yet showed strong retention on short-context reasoning tasks. What would disprove an architectural limitation claim? If **mixed-length distillation (50% 2k, 50% 8k)** eliminates the task-type × strategy interaction observed under short-only distillation, then degradation was curricular, not structural. The minimal rigorous design is a 2×2: {short-only, mixed-length} × {MOHAWK, LAWCAT}. Mixed-effects model required; success criterion: significant interaction (p<0.01 after correction) that persists under normalization.

Regarding hybrids: MOHAWK's Hybrid retaining 4 attention layers achieves 66.0 vs. teacher 67.2 average — within ~1.2 points [MOHAWK, 2024, Table 2]. Pre‑register disconfirmation condition: **If full LLaMA‑3‑8B conversion loses ≥10% normalized average accuracy on LongBench v2 while a 4-layer hybrid loses ≤5%, full replacement is not justified.**

Finally, during Stage 2 (hidden-state alignment), MOHAWK tracks L2 distance between attention block and SSM block outputs [MOHAWK, 2024]. Pre‑register a threshold: if median layerwise L2 alignment after 200M tokens remains >1.5× the relative error in Phi-Mamba's successful runs, terminate. The best experiments are designed to fail early.

**Key Points:**
- Test mixer expressivity scaling (Frobenius vs. sequence length) before full distillation; halt if error grows ≥3× or exceeds 0.3.
- Use a 2×2 curriculum × strategy design with mixed-effects modeling to separate architectural limits from distillation shift.
- Pre‑register hybrid dominance (≤5% loss vs. ≥10% for full conversion) as a valid disconfirmation of full replacement viability.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

The discussion has converged on a genuinely powerful experimental design. Let me synthesize what's emerged and strengthen the hypothesis formulation so it survives Prof. Rex's scrutiny while remaining tractable.

The core insight from LAWCAT [Liu et al., 2025] that I want to anchor on: "LAWCAT provides an efficient pathway to high-performance, long-context linear models suitable for edge deployment, reducing reliance on extensive long-sequence training data and computational resources." This is a strong operational claim. The problem is it was evaluated only on synthetic retrieval tasks (S-NIAH, BABILong). Our experiment directly tests whether this efficiency claim generalizes to LongBench v2's diverse realistic tasks — and whether it holds equally across task categories or differentially.

The strengthened hypothesis: **Under fixed-budget distillation (≤1B tokens, short-context curriculum), a task-type × conversion-strategy interaction exists in accuracy retention on LongBench v2 categories, such that retrieval-heavy categories (multi-doc QA, synthetic) exhibit ≥2× larger normalized degradation than generation-heavy categories (summarization, few-shot) for MOHAWK-SSM conversion, but not (or significantly less so) for LAWCAT-linear-attention conversion.** This is testable, falsifiable (if degradation is uniform across categories or strategies, the interaction fails), avoids H-E1's capability confound (fixed base model = pure conversion effect), avoids H-M2's direction (no KV eviction, no greedy compression), and uses existing benchmarks only.

Prof. Rex's 2×2 curriculum design is the right long-term design, but Sage's staged approach is the right execution strategy: Stage 1 (short-only distillation, MOHAWK vs. LAWCAT, LongBench v2 evaluation) is the minimal publishable contribution. Stage 2 (mixed-length distillation arm) only runs if Stage 1 finds a significant interaction, because the causal isolation question is only interesting if there's something to isolate.

The mechanism I'm proposing for why the interaction exists: SSM state space models lose positional information about token indices (they have bounded state size), making exact needle retrieval degrade more than compression/integration tasks, which can be done with lossy state summaries. Linear attention (LAWCAT) uses causal Conv1D to preserve local dependencies while the global linear attention handles integration — so it may be better at summarization but still weak at exact retrieval. The prediction is thus *directional* for each strategy: MOHAWK-SSM degrades more on retrieval, LAWCAT degrades less on retrieval but more on tasks requiring complex long-range dependency integration.

This mechanism is falsifiable: if LAWCAT and MOHAWK show identical task-type profiles, the architectural distinction doesn't matter for task-type effects. If LAWCAT is uniformly better, that's a different finding (efficiency without task-type trade-off, also publishable).

**Key Points:**
- Strengthened hypothesis: task-type × strategy interaction where MOHAWK-SSM degrades more on retrieval, LAWCAT-linear-attention degrades more on integration tasks
- Mechanism: SSM state-size limit → retrieval degradation; Conv1D local context (LAWCAT) → better short-range retrieval but different long-range pattern
- Staged execution: Stage 1 is complete and publishable on its own
- Fixed base model (LLaMA-3-8B) is the clean within-subject control for capability

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

This is finally tightening up. But here's where I'm still unconvinced.

First: your entire interaction hypothesis rests on the assumption that MOHAWK-style structured mixers retain their matrix-approximation advantage at longer sequence lengths. The evidence comes from fitting attention matrices at **length 512** (1000 samples, random head) with Frobenius ≈0.097 for SSD and ≈0.046 for general SSM at N=64 [MOHAWK, 2024]. That's encouraging — but LongBench v2 runs at 16k–32k. If the effective approximation error grows with sequence length due to state compression or numerical drift, your hypothesized retrieval degradation may simply be *approximation breakdown*, not architectural trade-off.

What would convince me: fit teacher attention matrices at **N ∈ {512, 1k, 2k, 4k}** and plot Frobenius vs. N on log–log axes. If error grows worse than O(log N) or exceeds 0.3 absolute by 4k, halt. No 8B distillation until this curve exists.

Second: MOHAWK's Stage 2 hidden-state alignment materially improves downstream accuracy over Stage 3 alone [MOHAWK, 2024, Table 3]. Block-level functional matching matters. If your converted 8B underperforms on retrieval-heavy LongBench categories, I will ask: what were the Stage 2 L2 alignment curves? Pre-register a termination criterion (e.g., median L2 plateauing >1.5× Phi-Mamba's final ratio after 200M tokens).

Third: your interaction definition needs sharper teeth. I want a formal mixed-effects model with task nested within category, strategy and category as fixed effects, random intercepts for task, and normalization by teacher headroom. If the interaction term survives p<0.01 with Holm correction, good. Also: include the **4-layer hybrid baseline** as a third level in the strategy factor. MOHAWK shows Hybrid-4 gets within ~1.2 points of teacher average [MOHAWK, 2024, Table 2]. If full replacement shows category-specific collapse while Hybrid doesn't, some attention layers are structurally necessary for that category.

Finally: add a **needle position sweep** for retrieval tasks — accuracy vs. needle depth percentile. If SSM accuracy decays monotonically with depth while LAWCAT's is flatter, that supports the bounded-state argument.

**Key Points:**
- Verify matrix-approximation error scaling with sequence length before committing to 8B distillation.
- Track and pre-register hidden-state L2 alignment thresholds.
- Test task-type × strategy interaction via mixed-effects modeling with a Hybrid baseline and depth-sensitive retrieval diagnostics.

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex, your staged gates are exactly right but I want to quantify whether they're actually feasible given our compute constraints, not just theoretically appropriate.

The matrix fitting test (N ∈ {512, 1k, 2k, 4k}) is cheap — it's a forward pass through LLaMA-3-8B to extract attention matrices, then an optimization to fit the SSD mixer. MOHAWK reports this takes <1 GPU-day for Llama2-7B [MOHAWK, 2024]. For LLaMA-3-8B it's comparable. This gate costs <1 GPU-day and should absolutely be done first. If it fails, we save 3-5 GPU-days of distillation. Pre-registering the halt criterion (error ≥3× at N=4k relative to N=512, or absolute >0.3) is zero cost and high value.

The hidden-state L2 tracking during Stage 2 is already implemented in MOHAWK's training code (they explicitly log it in the paper). Integrating this into our LLaMA-3-8B MOHAWK run is ~1 hour of code adaptation. Not a barrier.

The needle position sweep (accuracy vs. depth percentile) is doable on LongBench v2's synthetic and multi-doc QA subsets. The key is that LongBench v2 already categorizes documents by their length, and the eval harness supports per-example logging. This adds ~2 hours of post-processing code. Also not a barrier.

The mixed-effects model: this is a stats analysis after data is collected. Standard `lme4`-equivalent in Python (`statsmodels` or `pymer4`). ~4 hours of analysis code. Fine.

The real feasibility question is: can we run LAWCAT + MOHAWK + Hybrid-4 all on LongBench v2 within a realistic single-GPU allocation? Let me estimate:
- LAWCAT LLaMA-3-8B distillation (1B tokens, 2×A100): ~3 days
- MOHAWK Stage 1+2 LLaMA-3-8B (1B tokens, 4×A100): ~4 days
- Hybrid-4 LLaMA-3-8B (retain 4 attention layers, MOHAWK Stage 3 only, 1B tokens, 2×A100): ~2 days
- LongBench v2 eval all 3 models (503 questions, batch inference): ~6 hours per model

Total: ~10 GPU-days of 2×A100, ~4 days of 4×A100. This is a realistic 2-week experiment for a team with access to a DGX-equivalent cluster.

The one unresolved feasibility concern: LAWCAT uses Flash Linear Attention backend, which requires specific CUDA versions. `goombalab/mohawk` uses standard FSDP. We need to verify compatibility on the same cluster before committing the full experiment. This is a 1-day preliminary check.

**Key Points:**
- Matrix fitting gate (<1 GPU-day) is the cheapest insurance against 10 GPU-days of wasted distillation
- All diagnostic tools (L2 tracking, needle sweep, mixed-effects model) are implementable with <10 hours of code work
- Full experiment (LAWCAT + MOHAWK + Hybrid-4 + LongBench v2 eval) = ~10-14 GPU-days of 2-4×A100
- Flash Linear Attention / FSDP compatibility check needed before committing

---

### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence from MOHAWK shows a tight coupling between matrix approximation fidelity and downstream accuracy: SSD/SSM families achieve markedly lower Frobenius error than Toeplitz or low-rank projections, and correspondingly higher task accuracy [MOHAWK, 2024, Tables 6–7]. However, those fits were conducted at sequence length 512. LongBench v2 operates at 16k–32k. I endorse the proposed scaling study, but I will sharpen it: for N ∈ {512, 1k, 2k, 4k}, compute per-layer Frobenius error distributions (not just means) and fit a log–log slope. Pre-register disconfirmation: if the median slope exceeds 0.5 (super–√N growth) or the 90th percentile error exceeds 0.3 at N=4k, we suspend claims of structural adequacy.

On the distillation side, MOHAWK demonstrates that Stage 2 (hidden-state alignment) materially improves over Stage 3 alone, indicating complementarity rather than redundancy [MOHAWK, 2024, Table 3]. Therefore I require pre-registered monitoring of the layerwise L2 alignment with explicit thresholds: define alignment ratio as ‖AttnBlock(u)−StudentBlock(u)‖₂ / ‖AttnBlock(u)‖₂. If the median ratio after 200M Stage-2 tokens exceeds 0.15 or fails to decrease monotonically across checkpoints, we treat any downstream deficit as training failure, not architectural evidence.

For retrieval subsets: conduct a needle-depth sweep and fit accuracy as a function of depth percentile. The SSM hypothesis predicts a negative slope significantly below zero (β_depth < −0.2 in logistic regression); LAWCAT should show a flatter profile. Disconfirmation condition: if both slopes are statistically indistinguishable from zero after Holm correction, the bounded-state explanation is unsupported.

Finally, the Hybrid-4 baseline is not optional. MOHAWK shows Hybrid-4 recovers near-teacher averages (66.0 vs. 67.2) [MOHAWK, 2024, Table 2]. Pre-register dominance criterion: if Hybrid-4 exhibits ≤5% normalized degradation across all categories while full replacement exhibits ≥10% in any category, we conclude some attention layers are structurally necessary for that category.

**Key Points:**
- Pre-register quantitative instability thresholds for matrix-fit scaling (slope and 90th percentile error).
- Treat hidden-state alignment as a gate: explicit L2 ratio criteria distinguish training failure from architectural limitation.
- Require depth-sensitive retrieval diagnostics and a Hybrid-4 dominance test.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

I want to bring in what the Overflow Prevention paper found for LongBench v2 on scratch-trained recurrent models [arxiv 2505.07793]. That paper evaluates Falcon3-Mamba, RecurrentGemma, and RWKV6 on LongBench v2. The key finding for our hypothesis: recurrent models with overflow-prevention (chunk-based inference with state reset) are competitive with transformers on *most* LongBench categories but show systematic degradation on multi-document QA and synthetic retrieval tasks that require precise long-range needle access. This is exactly the degradation pattern we're predicting for SSM-converted models.

This gives us an anchor for our success criterion that we've been missing. The Overflow Prevention paper provides a concrete degradation baseline for scratch-trained SSMs on LongBench v2 categories. Our hypothesis predicts: MOHAWK-converted LLaMA-3-8B will show *similar* task-type degradation patterns to scratch-trained Mamba/RWKV on retrieval categories, but *better* performance on summarization/few-shot categories (due to transformer prior). LAWCAT-converted LLaMA-3-8B will show intermediate profiles.

This is the significance anchor: we're not just claiming "there's a task-type interaction" — we're predicting that conversion preserves the transformer's advantage on generation tasks while inheriting the SSM's weakness on retrieval tasks. The Overflow Prevention paper gives us the scratch-trained SSM baseline. MOHAWK Phi-Mamba gives us a precedent for how much the transformer prior helps. We need LLaMA-3-8B converted with MOHAWK and LAWCAT evaluated on the same LongBench v2 to close the triangle.

The impact framing: this paper becomes the definitive evidence for "when should practitioners convert a transformer to sub-quadratic, and for which tasks?" The answer, based on our hypothesis, is: "convert for generation/summarization workloads; keep attention (or hybrid) for retrieval workloads." This is immediately actionable for production systems.

**Key Points:**
- Overflow Prevention paper provides scratch-trained SSM degradation baseline on LongBench v2 (directly reusable)
- Predicted pattern: converted transformer inherits SSM retrieval weakness but preserves generation advantage
- Framing: "when to convert and for which tasks" — actionable for practitioners
- Complete the triangle: scratch-trained SSM (from prior paper) + MOHAWK-converted + LAWCAT-converted on same eval

---

### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — now we're finally triangulating mechanism instead of waving at patterns. But here's where this still breaks down.

You're implicitly assuming that MOHAWK's matrix-approximation advantage at length 512 transfers cleanly to LongBench v2 regimes (16k–32k). The structured mixer evidence — SSD ≈0.097 Frobenius at N=64 [MOHAWK, 2024, Tables 6–7] — is compelling at 512 tokens. But MOHAWK's distillation itself is trained at **sequence length 2048** on C4. LongBench v2 pushes far beyond this. If the semi-separable mask induces effective rank collapse or numerical attenuation over long horizons, retrieval failure may be a *long-range stability issue*, not a bounded-state representational limit. What would convince me: show that the per-layer matrix-fit slope (log–log error vs. N) remains ≤0.5 and that the spectral norm of the induced mixing matrix does not decay with depth position.

Second: your use of Overflow Prevention as a baseline is smart — but dangerous. Those models are scratch-trained recurrent architectures. MOHAWK students inherit pretrained embeddings, MLPs, norms. If converted LLaMA-3-8B matches scratch Mamba's retrieval degradation, that strengthens the architectural argument. But if it does *better*, you must explain why transformer priors compensate. I want a mediation analysis: retrieval accuracy ~ (strategy) + (alignment ratio) + (matrix-fit error @ 2k) + (perplexity gap).

Third: if Hybrid-4 preserves retrieval while full replacement collapses, localize *which layers* matter. Run three hybrids: keep 4 early, 4 middle, 4 late. If only late-attention hybrids rescue retrieval, this isn't about memory — it's about content-addressable selection near decoding.

Finally: pre-register this — if final perplexity gap vs. teacher exceeds 5% relative, you cannot interpret downstream degradation architecturally. Perplexity is your sanity check.

**Key Points:**
- LongBench extrapolation requires explicit long-range matrix-fit and spectral stability analysis beyond 2k tokens.
- Architectural claims must survive mediation controlling for alignment quality and perplexity gaps.
- Hybrid experiments must localize *which* attention layers are necessary, not just whether some are.

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex, the layer-localization extension is genuinely novel and I want to incorporate it — but not at the cost of making the hypothesis untestable in a single experiment. Let me propose a scope-bounded version that preserves the publishable core while addressing your architectural necessity concern.

LAWCAT [Liu et al., 2025] explicitly characterizes their architecture as combining "causal Conv1D layers to enhance local dependency modeling and normalized gated linear attention to improve generalization across varying context lengths." This duality — local dependency (Conv1D) + global integration (linear attention) — suggests a natural prediction: LAWCAT's retrieval degradation should be *shallower* as a function of needle depth than MOHAWK's SSM, because Conv1D preserves local token-to-token attention in the first few hops from any given retrieval target. This is mechanistically distinct from MOHAWK's pure SSM state update.

The scope-bounded experiment I'm defending:

**Primary claim:** Under ≤1B token short-context distillation, MOHAWK-SSM and LAWCAT-linear-attention convert LLaMA-3-8B with different task-type accuracy profiles on LongBench v2. MOHAWK shows larger degradation on retrieval-heavy categories (multi-doc QA, synthetic); LAWCAT shows more uniform degradation.

**Secondary claim (layer localization — partial):** A 4-layer Hybrid baseline (middle layers retained, following MOHAWK's best result) preserves most performance. If full replacement collapses on specific categories while Hybrid doesn't, we flag those categories as "attention-necessary" but reserve exact layer attribution for follow-up work.

This is the right scope for Phase 2A. Prof. Rex's full layer-localization experiment (early/middle/late) requires 3 additional model trains at 8B. That's 6+ more GPU-days. Worth doing in Phase 4 as a mechanism ablation *if* the primary claim is confirmed. If we fold everything into the primary experiment, we'll never finish.

The LAWCAT paper's conclusion directly supports our hypothesis scope: "reducing reliance on extensive long-sequence training data" is testable on LongBench v2 without any of the extensions. The primary experiment is sufficient for a publishable contribution, and mechanism localization is the Phase 4/follow-up story.

Concretely, the hypothesis I'm advocating: **H-Conv1D-v1 — Under fixed-budget (≤1B tokens) short-context distillation, the task-type accuracy retention pattern of LLaMA-3-8B converted to linear attention (LAWCAT) differs significantly from that converted to SSM (MOHAWK) on LongBench v2, with SSM conversion showing ≥2× larger normalized degradation on retrieval-heavy categories.**

**Key Points:**
- Scope-bound: primary claim (2-strategy comparison on LongBench v2) is publishable without layer localization
- LAWCAT's Conv1D mechanism is the mechanistic basis for predicting differential retrieval profiles
- Layer-localization (early/middle/late hybrid) is Phase 4 ablation, not Phase 2A hypothesis
- H-Conv1D-v1 is the hypothesis name: it highlights the LAWCAT architectural distinction

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

I will accept H-Conv1D-v1 as a testable primary claim — but only if we make the degradation criterion mathematically unambiguous. Define normalized degradation as: Δ_norm = (Acc_teacher − Acc_student) / Acc_teacher, computed per category, averaged across tasks pre-registered as "retrieval-heavy" (multi-doc QA, synthetic needle). Disconfirmation condition: if Δ_norm^SSM / Δ_norm^LAWCAT < 2.0 with 95% bootstrap CI excluding 2.0, the hypothesis fails. No post-hoc category reassignment.

Long-range stability gate before interpreting any retrieval deficit as architectural:
1) Fit Frobenius error vs. N for N ∈ {512, 1k, 2k, 4k, 8k}
2) Compute log–log slope per layer
3) Require median slope ≤0.5 and 90th percentile Frobenius error ≤0.3 at 8k

If violated, retrieval degradation is attributed to scaling instability, not bounded-state limits.

Training sanity gates: median hidden-state alignment ratio (Stage 2) must be ≤0.15, final perplexity gap vs. teacher ≤5% relative. If either fails, suspend architectural interpretation. Run regression: Acc_retrieval ~ Strategy + Alignment + PPL_gap + MatrixError_2k. If Strategy retains significant coefficient (p<0.01), architectural claims survive.

Hybrid-4 as explicit falsifier: if Hybrid-4 shows ≤5% normalized degradation on retrieval while full replacement exceeds 10%, at least some attention layers are structurally necessary.

Secondary prediction from LAWCAT's Conv1D mechanism: |β_depth^SSM| ≥ 2 × |β_depth^LAWCAT| in needle-depth logistic regression. Disconfirmation: if slopes statistically indistinguishable after Holm correction, mechanistic distinction is unsupported.

**Key Points:**
- Define ≥2× criterion precisely with bootstrap CIs and pre-registered category sets.
- Introduce long-range stability gates (error scaling, spectral norm decay).
- Alignment ratio + perplexity gap as mandatory sanity checks; Hybrid-4 and depth-slope as explicit falsifiers.

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Vera, the long-range stability gate (Frobenius at N ∈ {512, 1k, 2k, 4k, 8k}) is scientifically right, but I want to confirm its computational feasibility before we hard-commit to it.

For LLaMA-3-8B, extracting attention matrices at N=8k requires: batch of 1 sequence of length 8192, forward pass through 32 layers (each 32 heads × 128 head_dim), storing the 32×32×8192×8192 attention matrix per layer in float32 — that's 32 layers × (8192×8192 × 4 bytes) = ~8GB just for one layer's attention matrix. Full attention materialization at 8k is on the edge of GPU memory for A100 80GB. We need to do this per-head-sample, not full matrix. MOHAWK used a 1000-sample random subset at 512 [MOHAWK, 2024]. Same approach at 8k with chunked attention logging is feasible, but requires custom hooks in the forward pass.

Practically: (a) implement attention matrix logging hooks using `register_forward_hook`, (b) compute Frobenius between per-head attention matrices and their SSM mixer approximations for 100 samples per N. At N=8k with 100 samples, this is ~3 hours on a single A100. Total for all 5 N values: ~12 hours. This is feasible as a Day 0 gate check.

The spectral norm of the mixing matrix is cheaper: it's a property of the SSD recurrence kernel, not the full attention matrix. Can be computed analytically from the SSM parameters. ~30 minutes of Python computation.

Prof. Vera's mediation regression: Acc_retrieval ~ Strategy + Alignment + PPL_gap + MatrixError_2k. This is a post-hoc analysis on collected data, ~2 hours of statsmodels code. Feasible.

Summary: the complete gate check protocol takes ~2 days of A100 compute and ~1 day of code instrumentation. This is a reasonable "Day 0" investment before the main distillation runs (10-14 days). It protects the entire downstream investment.

The integrated hypothesis H-Conv1D-v1 now has: pre-registered failure conditions (Prof. Vera), feasible gates (Prof. Pax confirmed), mechanism (Dr. Ally), significance (Dr. Sage), and falsifiers (Prof. Rex). This is a well-structured hypothesis.

**Key Points:**
- Frobenius gate at N=8k requires custom forward hooks but feasible in ~12 hours of A100 compute
- Spectral norm check: analytic computation, ~30 minutes
- Full gate protocol: ~2 days before committing to 10-14 day distillation runs
- H-Conv1D-v1 is now hypothesis-complete: failure conditions, mechanism, significance, falsifiers all specified

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** H-Conv1D-v1 addresses a genuine gap — no prior work holds the base model constant across sub-quadratic conversion strategies while evaluating on a standardized long-context benchmark with task-category breakdown. The task-type × strategy interaction prediction is novel; predicting differential MOHAWK vs. LAWCAT profiles based on architectural distinctions (bounded state vs. Conv1D local context) has not appeared in any prior paper. The use of existing infrastructure (LongBench v2, MOHAWK pipeline, LAWCAT pipeline) with a single well-controlled factorial design makes this immediately executable.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is unusually well-specified for a Phase 2A output. Explicit: (1) pre-registered normalized degradation criterion (Δ_norm ≥ 2× with 95% bootstrap CI), (2) long-range stability gates (Frobenius scaling, spectral norm), (3) training sanity gates (alignment ratio ≤0.15, perplexity gap ≤5%), (4) mediation regression to isolate architecture from training quality, (5) depth-slope falsifier (|β_depth^SSM| ≥ 2× |β_depth^LAWCAT|). Five independent disconfirmation pathways. This meets strong falsifiability standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The community currently has no controlled head-to-head comparison of conversion strategies on LongBench v2. The finding — whichever way it goes — directly answers the practitioner question "when should I convert and for which tasks?" Anchoring against scratch-trained SSM baselines from Overflow Prevention [2505.07793] positions this as closing an important triangle in the conversion literature. Publication venues: ICML, NeurIPS, EMNLP systems track.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All components are runnable now. LAWCAT (≤1B tokens, ≤3 days on 2×A100), MOHAWK Stage 1+2 (≤1B tokens, ≤4 days on 4×A100), Hybrid-4 (≤2 days on 2×A100), LongBench v2 eval (~6 hours per model). Day 0 gate check (Frobenius scaling, spectral norm) costs ~2 days and protects the downstream investment. Flash Linear Attention/FSDP compatibility is the one pre-check needed. Total: 2-week experiment on a typical research cluster.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

H-Conv1D-v1 emerged from this discussion as a well-structured, feasible, and genuinely novel hypothesis. The core claim: **under fixed-budget (≤1B tokens) short-context distillation, the task-type accuracy retention pattern of LLaMA-3-8B converted to linear attention with Conv1D (LAWCAT) differs significantly from that converted to SSM (MOHAWK) on LongBench v2, with SSM conversion showing ≥2× larger normalized degradation on retrieval-heavy categories (multi-doc QA, synthetic).**

The proposed mechanism: MOHAWK-SSM compresses context into bounded state vectors, causing lossy retrieval of specific needle tokens over long ranges. LAWCAT's causal Conv1D preserves local token-to-token attention in the first few hops from any retrieval target, producing a shallower depth-degradation slope. Both strategies inherit the base transformer's capability (fixing H-E1's confound). Neither involves KV eviction (avoiding H-M2's failure mode).

The experimental design: Day 0 gate check (Frobenius vs. N, spectral norm); Day 1-7 LAWCAT distillation; Day 8-14 MOHAWK distillation + Hybrid-4; Day 15 LongBench v2 evaluation of all three; Day 16 analysis (mixed-effects model, depth-slope, mediation regression). Five pre-registered disconfirmation criteria govern interpretation. Scratch-trained SSM baselines from Overflow Prevention [2505.07793] anchor the "conversion vs. scratch" comparison without requiring additional training.

The failure conditions are clear and pre-registered. The success criteria are quantitative. The infrastructure exists. This is Phase 2B-ready.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Full layer-localization (early/middle/late hybrid) was deferred — if the primary claim is confirmed, mechanism attribution requires this in Phase 4
- MOHAWK distillation at 8B scale carries optimization instability risk (loss spikes noted in original paper); perplexity gate must be enforced strictly
- Flash Linear Attention CUDA compatibility with the target cluster must be verified before commit
- Distillation curriculum was fixed to short-context only; the architecture-vs-curriculum confound remains open for Stage 2 (deferred to Phase 4 follow-up)
- **Mitigation Strategy:** (1) perplexity gate ≤5% relative enforced before LongBench evaluation; (2) CUDA compatibility day-0 check; (3) curriculum ablation registered as Phase 4 secondary analysis; (4) if Layer-localization needed, pre-plan 3 additional hybrid models at Phase 4 level

