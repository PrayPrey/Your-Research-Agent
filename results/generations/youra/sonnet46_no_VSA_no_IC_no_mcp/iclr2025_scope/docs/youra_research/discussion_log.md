# Phase 2A Discussion Log
**Date:** 2026-08-27
**Gap:** Gap 1 — No Systematic Benchmark Comparison of Query-Aware Token Importance Metrics
**Architecture:** Independent-Controller Self-Play (Claude plays all personas; no external orchestrator)
**Execution Mode:** UNATTENDED (#batch-mode)

---

## Previous Failure / Routing Context

**Source:** `.serena/memories/superseded_h-m2.md`
**Status:** SUPERSEDED — ROUTED_TO_PHASE_2A

### Summary
Hypothesis h-m2 tested LoRA-Q (LoRA-adapted model + query-aware KV eviction) vs. SnapKV on LongBench v1 (narrativeqa/hotpotqa/2wikimqa, 10 examples, 20% KV budget, LLaMA-2-7B base). Results: LoRA-Q F1=0.89, SnapKV F1=0.00 (macro-avg). Delta=0.89 < required gate threshold of ≥1.0.

### Failure Diagnosis
- Root cause: SnapKV degenerates completely (F1=0.00) at 80% KV eviction on base (non-instruct) LLaMA-2-7B — making the delta comparison invalid
- Both methods suffer from extreme eviction ratio + base model combination
- Gate threshold unreliable when baseline collapses

### Redesign Constraints (MANDATORY — applied to Gap 1 selection and hypothesis generation)
1. **AVOID:** base (non-instruct) model + extreme eviction (≥80%) combination
2. **USE:** instruction-tuned model (e.g., Llama-2-7b-chat-hf or LLaMA-3-8B-instruct)
3. **USE:** lighter eviction ratios (50% or 60% eviction = 40%-50% KV retention) OR lower gate threshold
4. **AVOID:** LoRA × KV eviction as the primary comparison (this was h-m2's focus; Gap 1 redirects to metric comparison)
5. **NEW DIRECTION:** Gap 1 — metric ablation (cumulative attention vs. prefill observation vs. attention entropy vs. warm-up attention) on shared benchmarks. This sidesteps the h-m2 failure entirely.

---

## Briefing Context

### Research Gap
**ID:** Gap 1
**Title:** No Systematic Benchmark Comparison of Query-Aware Token Importance Metrics
**Priority:** HIGH + PRIMARY | Blocks Q1 + Q2
**Description:** H2O, SnapKV, and ScissorHands each propose different importance metrics (cumulative attention, prefill observation, warm-up attention) but evaluate on disjoint benchmark sets, different model families, and at different eviction ratios. No paper ablates all metric families under identical experimental conditions.

### Missing Piece
Controlled ablation comparing: (1) cumulative attention (H2O), (2) prefill-observation window (SnapKV), (3) warm-up attention (ScissorHands), (4) attention entropy (novel baseline), (5) static window (StreamingLLM, baseline) — under identical conditions: same model (LLaMA-2-7B-chat or LLaMA-3-8B-instruct), same benchmarks (LongBench v1/v2), same KV budgets (20%, 40%, 60% retention), same hardware.

### Papers Available
- P1: H2O (2306.14048) — cumulative attention metric, base models
- P2: SnapKV (2404.14469) — prefill observation, instruct models
- P3: ScissorHands (2305.17118) — warm-up attention, base/small models
- P4: StreamingLLM (2309.17453) — static baseline, multi-arch

### Feasibility Constraints (Pipeline-Enforced)
- No new benchmarks — use LongBench v1, SCROLLS, NarrativeQA (existing)
- No synthetic data — real datasets only
- No human evaluation — automated metrics (F1, exact match, ROUGE) only
- Immediately testable with existing tools (HuggingFace transformers + peft)

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The fundamental novelty opportunity here is striking: four distinct token importance metrics have been proposed independently across three years, yet no one has placed them side-by-side under identical conditions. This is not a minor gap — it means the field's practical choice of metric (cumulative attention vs. prefill observation vs. warm-up heuristic) is currently based on cherry-picked comparisons across different models and benchmarks.

My proposed angle: rather than treating this purely as an ablation study, we should frame the hypothesis around **why** metric families differ in their effectiveness. Specifically, prefill-observation metrics (SnapKV-style) are fundamentally more query-aware than cumulative-attention metrics (H2O-style) because they condition on the actual query tokens being answered — and this conditional alignment with the query should produce systematically better retention of relevant KV entries on question-answering tasks vs. summarization tasks.

This means we can make a **directional prediction**: on extractive QA tasks (NarrativeQA, HotpotQA) where query-token alignment matters most, SnapKV-style prefill observation should outperform H2O-style cumulative attention. On summarization tasks (where the "query" is diffuse), the gap should narrow or reverse. That's a testable, falsifiable, novel claim.

The failure of h-m2 teaches us to use instruct models and moderate eviction ratios — SnapKV's own paper uses LLaMA-2-chat at 40%-60% retention. We should standardize on LLaMA-2-7B-chat at 50% KV retention as the primary experimental condition.

**Key Points:**
- Metric comparison across H2O / SnapKV / ScissorHands / attention entropy is the gap
- Prefill-observation should outperform cumulative attention on QA specifically (task-conditional prediction)
- Use LLaMA-2-7B-chat + LongBench + 50% KV retention to avoid h-m2 failure mode
- Frame as: query-task alignment of the metric predicts its relative advantage by task type

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing framing, but I want to sharpen the falsifiability. The claim that "prefill-observation outperforms cumulative attention on QA tasks" needs precise operationalization.

First, the confound problem: SnapKV was evaluated exclusively on instruct models while H2O was evaluated on base models. The controlled experiment must hold everything constant except the importance metric computation itself.

Second, what exactly is "attention entropy" as a fifth metric? It needs precise definition: H(i) = -Σ_t α_{t,i} log α_{t,i} where the sum runs over all decode positions t attending to position i.

Third, the success criterion must be binary: best query-aware metric beats StreamingLLM (static baseline) by ≥2.0 F1 points at 50% KV retention on LongBench v1, across LLaMA-2-7B-chat. This avoids the baseline-collapse problem from h-m2 since StreamingLLM doesn't collapse at 50% retention.

**Key Points:**
- Hold implementation constant, vary only the metric computation — cleanest ablation
- Attention entropy: H(i) = -Σ_t α_{t,i} log α_{t,i}
- Gate: best query-aware metric beats StreamingLLM by ≥2.0 F1 on LongBench at 50% KV
- Instruct model (LLaMA-2-7B-chat) mandatory per h-m2 failure context

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Prof. Vera's precision is necessary, but let me evaluate the significance angle. Is this gap worth a full hypothesis cycle? Yes — with important qualification.

The impact case: every practitioner deploying KV eviction today must choose a method without a principled basis. The choice is made by "which paper claimed best numbers," which is confounded by different evaluation setups. A controlled ablation that isolates the metric component provides direct practical guidance.

Dr. Nova's task-conditional framing adds a second layer of significance: if prefill observation has comparative advantage on QA and cumulative attention has advantage on summarization, then the right metric is task-dependent — immediately actionable for multi-task systems.

For Phase 2B planning: minimum sufficient experiment is 3-4 metrics × 2 KV budgets (40%, 60% retention) × LongBench v1 subset (NarrativeQA, HotpotQA, 2WikiMQA for QA + GovReport, QMSum for summarization) × 1 model = ~30-40 runs. Tractable at ~3 GPU-hours on A100.

**Key Points:**
- Impact: resolves practitioners' metric choice problem with controlled evidence
- Task-conditional advantage is the novel scientific claim
- Minimum sufficient experiment: 4 metrics, 2 budgets, 5-task LongBench subset, 1 model
- ~30 runs on A100 — tractable within Phase 4 budget

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Sage's estimate is right. Let me verify implementation realism.

What exists today: SnapKV (FasterDecoding/SnapKV) — working HuggingFace plugin, actively maintained. StreamingLLM (mit-han-lab/streaming-llm) — working, multi-arch. H2O needs ~50 lines in HuggingFace past_key_values hooks. ScissorHands — no maintained repo, needs ~80 lines from paper. Attention entropy — ~10 lines on top of any existing hook.

The cleanest controlled ablation uses a single codebase with a pluggable eviction function: `evict_fn(kv_cache, scores) -> pruned_kv_cache`. Each metric is just a different `score_fn(attention_weights) -> per_token_scores`. This eliminates implementation-level confounds entirely.

LLaMA-2-7B-chat-hf runs on single A100 40GB at FP16 for sequences up to 4096 tokens. LongBench is standard HuggingFace dataset with existing eval scripts.

**Feasibility verdict:** HIGH. 2000 inference runs × ~5s/run = ~3 GPU-hours. Very tractable.

**Key Points:**
- Unified codebase with pluggable score_fn eliminates implementation confounds
- SnapKV and StreamingLLM have working repos; H2O and ScissorHands need ~50-80 line implementations
- LLaMA-2-7B-chat-hf + LongBench + HuggingFace = standard stack, no new infra
- 3 GPU-hours on A100 — within Phase 4 budget

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Let me synthesize the emerging hypothesis with precision.

**Strengthened Hypothesis (Under-If-Then-Because):**
Under long-context QA inference with LLaMA-2-7B-chat at 50% KV retention on LongBench NarrativeQA+HotpotQA+2WikiMQA+MuSiQue (QA) and GovReport+QMSum (summarization), if we apply prefill-observation importance scoring (SnapKV-style) vs. cumulative-attention scoring (H2O-style) vs. static window (StreamingLLM), both query-aware methods implemented with matched eviction timing at prefill, then prefill-observation achieves ≥2.0 F1 points higher than cumulative-attention on QA tasks, with δF1(QA) > δF1(Summ), because query-conditioned observation windows retain tokens that are semantically aligned with the specific question being answered, whereas cumulative scoring retains globally-attended structural tokens (initial positions, sentence boundaries) that are less discriminative for specific query answering.

Gate: prefixobs F1 ≥ cumulative F1 + 2.0 on 4-task QA average at 50% KV retention on LLaMA-2-7B-chat. Bootstrap 95% CI non-overlapping as statistical criterion.

Avoids h-m2 failure: instruct model, 50% retention (not base + 80% eviction), no LoRA interaction.

**Key Points:**
- Core claim: query-task alignment of metric determines relative advantage on QA vs. summarization
- Falsification: prefixobs ≈ cumulative on QA F1 → query-awareness mechanism refuted
- Gate: prefixobs ≥ cumulative + 2.0 F1 on 4 QA tasks at 50% KV, LLaMA-2-7B-chat
- Avoids h-m2 failure mode entirely

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Three serious concerns:

**Concern 1: Timing confound.** SnapKV compresses at prefill; H2O compresses per decode step. These are two confounds: (a) the importance scoring function and (b) when eviction happens. The solution: implement H2O-at-prefill (compute cumulative attention at end of prefill, evict once) — ~20 lines of code. This 2×2 design (metric type × eviction timing) cleanly separates the causal attribution.

**Concern 2: Sample size.** 50 examples/task gives wide confidence intervals. Specify 100 examples/task with 95% bootstrap CI non-overlapping as the statistical criterion, not point estimate difference.

**Concern 3: Task coverage.** NarrativeQA + HotpotQA only is 2 tasks — overfitting risk. Minimum credible: 4 QA tasks (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue) + 2 summarization tasks (GovReport, QMSum) for valid task-conditional contrast.

**Mitigation Strategy:** Add H2O-at-prefill condition; specify 100 examples/task; expand to 4 QA + 2 summarization tasks. All addressable without changing the core hypothesis.

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer) — responding to Prof. Rex:

Prof. Rex's Concern 1 is the most valuable scientifically. The 2×2 design (metric × timing) transforms this from a benchmark paper into a mechanistic study. The causal story becomes:

- If SnapKV-at-prefill > H2O-at-prefill: **metric** (query-conditioned window vs. cumulative) is what matters
- If SnapKV-at-prefill ≈ H2O-at-prefill > H2O-at-decode: **timing** (prefill vs. decode) is what matters
- If all ≈ each other: null result on both mechanism and timing

This 2×2 design adds one implementation variant (~20 lines) and ~1.5 GPU-hours. Worth it for the scientific clarity.

For Concern 3: expand to 4 QA + 2 summarization — this allows quantitative test: δF1(QA) vs. δF1(Summ). Include ScissorHands as 4th metric for completeness.

For Concern 1: 100 examples/task, bootstrap 95% CI.

The hypothesis is converged. All objections are addressable in Phase 2B experimental design.

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect) — convergence assessment:

Convergence criteria verified:
- **SPECIFIC:** Prefixobs F1 ≥ cumulative F1 + 2.0 on 4 QA tasks at 50% KV, LLaMA-2-7B-chat ✅
- **MECHANISM:** Query-conditioned window → query-aligned token retention → QA accuracy advantage; tested via 2×2 metric×timing ablation ✅
- **PREDICTIONS:** P1: prefixobs ≥ cumulative + 2.0 F1 (QA). P2: δF1(QA) > δF1(Summ). P3: H2O-at-prefill > H2O-at-decode ✅
- **NOVELTY:** No prior paper ablates metric vs. timing under identical conditions; task-conditional advantage claim is new ✅
- **FEASIBILITY:** Unified HuggingFace codebase, LLaMA-2-7B-chat, LongBench, ~6 GPU-hours ✅
- **OBJECTIONS:** h-m2 failure avoided; timing confound addressed (2×2); sample size specified (100 examples, 95% CI) ✅

**CONVERGED.**

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The 2×2 metric×timing design isolates a mechanistic question no prior paper has asked. The task-conditional prediction (δF1(QA) > δF1(Summ)) is a genuinely novel testable claim that goes beyond "which method wins overall." This reframes the KV eviction literature around mechanism rather than benchmark ranking.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** All three predictions are binary-testable with quantitative thresholds (≥2.0 F1, 95% CI, specific task sets). The 2×2 design allows causal attribution. Null hypothesis (no significant metric difference at 50% retention) is clearly defined. Ready for Phase 2B experimental protocol design.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Resolves the practitioners' metric-choice problem with controlled evidence. Task-conditional metric selection is immediately actionable for multi-task deployment systems. Addresses a real gap in the 2023-2024 KV eviction literature with minimum sufficient experimental scope.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Single unified HuggingFace codebase with pluggable score_fn eliminates implementation confounds. All models and datasets publicly available. Approximately 6 GPU-hours on A100. Implementation complexity is low — SnapKV plugin exists; H2O-at-prefill is ~20 lines; attention entropy is ~10 lines. No new infrastructure required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged is: **Under long-context QA inference using LLaMA-2-7B-chat at 50% KV retention on LongBench (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue as QA tasks; GovReport and QMSum as summarization contrast), if we apply prefill-observation importance scoring (SnapKV-style query-conditioned window) versus cumulative-attention scoring (H2O-style), implemented with matched eviction timing (both at prefill) and matched eviction ratio, then prefill-observation achieves ≥2.0 F1 points higher macro-average than cumulative-attention on QA tasks, with a larger advantage gap on QA than on summarization tasks (δF1(QA) > δF1(Summ)), because query-conditioned observation windows selectively retain KV entries that are semantically aligned with the specific tokens of the question being answered — whereas cumulative attention retains tokens with globally high structural salience (initial tokens, sentence boundaries) that are less discriminative for specific query answering.**

The secondary prediction (H2O-at-prefill > H2O-at-decode) tests whether the timing of eviction independently contributes to accuracy. The tertiary prediction (all query-aware metrics beat StreamingLLM by ≥5.0 F1) establishes the floor against the static baseline. This hypothesis explicitly avoids the h-m2 failure mode: instruct model, 50% KV retention (not 80% eviction), no LoRA interaction. It uses existing benchmarks, existing models, automated metrics, and is testable immediately.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Attention entropy metric definition must be finalized before implementation: H(i) = -sum_h sum_t alpha_{h,t,i} * log(alpha_{h,t,i} + eps) averaged across heads
- The 2.0 F1 gate was calibrated from SnapKV paper numbers on slightly different task sets — could be miscalibrated; bootstrap CI is essential, not optional
- ScissorHands (warm-up attention) should be included as a 4th metric condition for completeness — adds ~80 lines of implementation and ~1.5 GPU-hours
- **Mitigation Strategy:** Include ScissorHands as 4th metric; implement attention entropy with explicit formula; treat 2.0 F1 as the target effect size for power analysis; require 95% CI non-overlapping as the statistical criterion

---

*Discussion log complete. 8 exchanges. Converged at Exchange 8.*
