# Phase 2A Discussion Log

**Workflow:** phase2a-dialogue  
**Architecture:** Self-Contained Tikitaka Loop (independent-controller ablation — Claude plays all personas)  
**Gap ID:** gap_1  
**Gap Title:** Zero-Shot SWA Layer Conversion Accuracy Bounds Without Fine-Tuning in Llama-2-7B  
**Date:** 2026-08-22  
**Execution Mode:** UNATTENDED  

---

## Briefing Context

### Research Gap Selected

**Gap 1 (PRIMARY — Critical):** Zero-Shot SWA Layer Conversion Accuracy Bounds Without Fine-Tuning in Llama-2-7B

**Description:** SWAA (2025) demonstrates FA→SWA conversion but requires lightweight fine-tuning as a recovery strategy after naive conversion causes catastrophic quality collapse. No work has measured zero-shot (no fine-tuning) SELECTIVE layer conversion accuracy bounds in Llama-2-7B with quantified thresholds. The question: does replacing k=4 and k=8 highest-entropy layers (of 32 total) with SWA (w=512) maintain WikiText-103 perplexity within 2 points and GLUE SST-2 accuracy within 2 percentage points, without any fine-tuning?

**Why selected:** PRIMARY relevance; blocks Q1, Q2, Q3 (accuracy thresholds); most critical path to answering the main research question.

### Key Papers Available

- **P1: SWAA (Yu et al., 2025)** arXiv:2512.10411 — FA→SWA without retraining; fine-tuning required for recovery
- **P2: HIES (Choi et al., 2025)** arXiv:2510.13832 — Entropy signal for head pruning; +15.2% vs importance-only
- **SWARR (Liu et al., 2026)** arXiv:2606.11634 — SFT alone insufficient after SWA; RL needed
- **SWAT (Fu et al., 2025)** arXiv:2502.18845 — SWA with proper position encoding
- **Longformer (Beltagy, 2020)** arXiv:2004.05150 — O(n·w) SWA theory
- **Mistral 7B (Jiang, 2023)** arXiv:2310.06825 — Production SWA from scratch at 7B
- **Michel et al. (2019)** arXiv:1905.10650 — Heads removable at test time without accuracy loss
- **Raganato et al. (2020)** arXiv:2002.10260 — Fixed attention patterns preserve quality
- **Entropy-Lens (Ali et al., 2025)** arXiv:2502.16570 — Entropy as information signature across layers

### Implementation Context

- HuggingFace `AttentionMaskConverter(sliding_window=w)` native support
- PyTorch `create_sliding_window_attn_mask` (executorch)
- Target: Llama-2-7B, 32 layers, k=4 and k=8 selective conversion
- Benchmarks: WikiText-103 perplexity, GLUE SST-2 accuracy
- Baselines: random k, last k, entropy-guided top-k

### ROUTE_TO_0 Failure History

- Attempts 1-4: SSM/Mamba-based (exhausted)
- h-e1 (PARTIAL/LIMITATION): Evolutionary layer search (NSGA-II, 1875 GPU-hours — infeasible)
- h-m3 (SHOULD_WORK/FAIL): Syntactic proxy for attention uncorrelated (p=0.9537)
- Current direction avoids all: uses direct entropy signal, modifies attn_mask only, pilot < 1 GPU-hour

### Previous Failure / Routing Context

No Serena memory files found. First Phase 2A attempt for this research direction.

---

## Feasibility Constraints (Pipeline-Enforced)

- REJECT: Ideas requiring new benchmarks, rubrics, or scoring frameworks
- REJECT: Ideas requiring synthetic/generated data or future data
- REJECT: Ideas requiring human evaluation or annotation
- ACCEPT ONLY: Hypotheses testable immediately using existing real datasets and existing benchmarks

---


### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been thinking about this backwards? SWAA panics because it converts ALL layers at once — the model's entire global context mechanism is gutted simultaneously. But what if selective conversion of k=4 highest-entropy layers is fundamentally different? Those layers, by having HIGH entropy, are already behaving like local-context scanners — their attention distributions are already diffuse, already not relying on sharp global pointers. Replacing them with an explicit local window (w=512) might not cause catastrophic collapse at all, because we're aligning the mechanism with what the layer is ALREADY DOING.

Here's the wild idea: the catastrophic collapse in SWAA isn't about SWA being bad — it's about imposing local constraints on layers that NEED global context (low entropy layers that attend sharply to distant tokens). High-entropy layers are already informationally "flat" — their entropy tells us they don't have strong global preferences. Michel et al. [2019] showed 70-90% of heads are removable at test time — these are the high-entropy, diffuse heads. We're just formalizing that at the layer level.

The novelty here is the SELECTIVITY + CRITERION combination. Nobody has used layer-level entropy aggregation as a threshold for SWA conversion in causal decoders. Mistral 7B shows SWA works from scratch at 7B scale — but that's full training. We're asking: can we achieve a SUBSET of that benefit zero-shot by targeting only the layers that entropy analysis says can handle it?

**Key Points:**
- High-entropy layers may already be operating as de facto local scanners — SWA conversion aligns mechanism with behavior
- SWAA's catastrophic collapse was full-model; selectivity may avoid it entirely
- Layer-level entropy aggregation from head-level entropy (HIES validated at head level) is the novel methodological step
- Immediately testable: WikiText-103 + GLUE SST-2 on Llama-2-7B; no new benchmarks needed

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises a compelling mechanistic intuition, but I need to stress-test it immediately. The claim "high-entropy layers are already behaving as local-context scanners" is a hypothesis itself, not an established fact. Entropy measures distributional flatness — but flatness over what? Over positions within the 512-token SWA window? Or over the FULL sequence including long-range dependencies?

The critical falsification point: if a high-entropy layer is attending diffusely to positions BEYOND 512 tokens, then forcing SWA (w=512) will destroy exactly those diffuse long-range dependencies. The result is NOT approximating what the layer was doing — it's amputating a key part of it. Entropy doesn't distinguish between "diffuse local" and "diffuse global."

However, this is testable. The experiment design: (1) measure entropy per layer on 100 calibration sequences, (2) convert k=4 highest-entropy layers to SWA(w=512), (3) measure WikiText-103 perplexity and GLUE SST-2 accuracy vs baseline. The success criterion Dr. Nova's intuition predicts: ≤2pt perplexity degradation at k=4. The falsification criterion: >5pt perplexity degradation would suggest entropy is not a valid proxy for local-sufficiency.

The comparison baseline (entropy vs random vs last-k selection) is the scientific heart of this experiment. If entropy-guided selection at k=4 produces LESS degradation than random-k=4 or last-k=4 at matched conversion count, we've validated entropy as a layer-level selection criterion. What would convince me this hypothesis is wrong: entropy-guided k=4 produces equal or WORSE perplexity than random-k=4, OR any conversion (even k=1) causes >5pt perplexity degradation regardless of selection criterion.

**Key Points:**
- Entropy = distributional flatness, but doesn't distinguish local vs global diffuseness — key confound
- Falsification: entropy-guided k=4 worse than or equal to random-k=4 would kill the entropy criterion claim
- Full experimental design is clear: calibration entropy → selective SWA → WikiText-103 + SST-2 vs baselines
- SWARR (2026) full-model SFT finding doesn't apply to selective zero-shot conversion

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what does this contribute to the field if it works, AND if it fails? Both outcomes have value — a good sign for the hypothesis.

If the hypothesis SUCCEEDS (k=4 entropy-guided conversion ≤2pt perplexity, ≤2pp SST-2): we've demonstrated that pre-trained LLMs contain layers whose attention patterns are sufficiently local that zero-shot SWA substitution is accuracy-preserving. This opens a new class of post-training efficiency interventions — "attention pattern surgery" guided by signal statistics. The paper contribution: first empirical demonstration of zero-shot selective SWA conversion in decoder LLMs with quantified bounds, tested on existing benchmarks.

If the hypothesis PARTIALLY FAILS (k=4 works but k=8 degrades beyond threshold): we've characterized the scaling behavior of selective SWA conversion and identified the boundary condition. The contribution becomes a characterization paper: "entropy-guided SWA conversion is safe up to k* layers, where k* depends on the model's per-layer entropy distribution." Still a novel, publishable finding on existing benchmarks.

If the hypothesis FAILS entirely: we've demonstrated that the high-entropy intuition is wrong — local window attention doesn't approximate high-entropy layers' behavior, refuting a non-obvious and reasonable claim. This is publishable as a negative result that redirects the field away from this approach.

This matters because: efficient inference is among the most active research areas. Mistral 7B (3809 cit.) proves SWA works at 7B from scratch. The "why not retrofit it?" question is natural and this work provides the first quantitative zero-shot answer, using existing datasets (WikiText-103, GLUE SST-2) and an existing model (Llama-2-7B).

**Key Points:**
- Positive, partial, and negative results all contribute — low publication risk
- Direct applicability: any causal decoder LLM, CPU-only entropy scoring, no new benchmarks
- Connects to large citation-count papers (Longformer 5840, Michel 1454, Mistral 3809)
- Novel contribution: first quantitative bounds for zero-shot selective SWA conversion in decoder LLMs

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here about what's technically sound and what might break. The mechanism — entropy scoring → layer selection → attn_mask replacement → zero-shot inference — is physically valid at each step. HuggingFace's `AttentionMaskConverter(sliding_window=w)` is production code; PyTorch's `create_sliding_window_attn_mask` is verified. Entropy extraction via `output_attentions=True` on a 100-sequence calibration set is standard (same as GPTQ/AWQ quantization calibration). These are not theoretical — they are concrete, working code paths.

What worries me: position encoding compatibility. Llama-2-7B uses RoPE (Rotary Position Embedding). The full-attention pre-training exposed each layer to positions 0 to seqlen-1. When we impose SWA (w=512), the model will see position pairs (i, j) where j < i-512 as masked. RoPE is designed to handle arbitrary relative positions — but the question is whether trained RoPE coefficients at relative distances >512 are "dead" (never activating) or "confused" (activating but irrelevant). SWAT (Fu et al., 2025) found attention sinks and softmax variance issues at SWA boundaries — this is real, not theoretical.

However — for SELECTIVE k=4 conversion, the remaining 28 full-attention layers still see long-range dependencies and can compensate. The 4 SWA layers lose >512-token reach, but if entropy analysis is correct (those layers weren't using it meaningfully), the 28-layer global context propagates through the residual stream. This is the mechanism that needs formalization: residual stream as a global context bus for SWA layers.

The implementation is feasible within 1 GPU-hour on 1 H100 for Llama-2-7B: entropy scoring (~15 min), SWA conversion (minutes), perplexity eval on WikiText-103 (~20-30 min per configuration). Consistent with the PILOT < 1 GPU-HOUR constraint from h-e1 lessons.

**Key Points:**
- Mechanism is technically sound: HF AttentionMaskConverter + RoPE + residual stream global bus
- RoPE compatibility: selective conversion leaves 28 unmodified layers for global position context
- SWAT boundary effects are real but likely minor for k/32 << 1 selective conversion
- Feasible under 1 GPU-hour pilot constraint

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this significantly based on what's emerged. Prof. Pax's insight about the residual stream as a global context bus is exactly the mechanism we need to formalize — and it also addresses Prof. Vera's confound about "diffuse global vs diffuse local" entropy.

Here's the refined mechanistic claim: **In Llama-2-7B, high-entropy layers are layers where the contribution of global attention context is already subordinate to the local residual stream signal from surrounding full-attention layers. Therefore, replacing these layers with SWA(w=512) preserves functional behavior because (a) their own attention is already diffuse/low-weight globally, and (b) global context is available via residual stream from the 28 remaining full-attention layers.**

This addresses Prof. Vera's concern: the claim isn't that "high-entropy = diffuse local only." It's that "high-entropy layers contribute less unique global information than low-entropy layers, and whatever global context they need is accessible through the residual stream." This is testable and distinguishes entropy-guided selection from random selection.

What evidence supports this refinement? Michel et al. [2019]: high-entropy heads (flat attention) are prunable without accuracy loss — our claim is the layer-level analog. Raganato et al. [2020]: some transformer layers learn fixed/positional patterns that are effectively local — the equivalent of SWA. Entropy-Lens [Ali et al., 2025]: entropy evolves across layers as information signature — layers with persistently high entropy may not perform complex global retrieval.

The refined hypothesis: entropy-guided selective SWA conversion (k=4, then k=8) maintains perplexity within 2pt/5pt and SST-2 within 2pp/5pp vs baseline, BECAUSE high-entropy layers are functionally redundant with global context available from the residual stream of retained full-attention layers.

**Key Points:**
- Residual stream global bus mechanism formalizes why selective (not full-model) conversion avoids catastrophic collapse
- "Diffuse global vs diffuse local" confound addressed: redundancy with residual stream is the key property
- Michel et al. + Raganato et al. provide layer-level evidence for the redundancy claim
- Hypothesis is now mechanistically grounded, not just empirically hoped for

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down — precisely, so it can be fixed.

**Break Point 1: The residual stream "global bus" claim is untested.** Dr. Ally posits that high-entropy layers can rely on global context from residual stream of adjacent full-attention layers. But in Llama-2-7B, each layer's residual stream is a function of all PREVIOUS layers' outputs — not all layers simultaneously. If layers 5, 10, 15, 20 are the high-entropy ones selected for SWA conversion, some appear BEFORE many full-attention layers have contributed global context to the residual stream. The "global bus is always available" assumption may only hold for high-entropy layers appearing LATE in the stack.

**Break Point 2: 100-sequence calibration stability.** Entropy estimates from 100 sequences may have high variance — different 100-sequence samples might yield different rank orderings of layers. The stability of the entropy ranking must be explicitly tested (rank correlation across seeds). Without stability, the selection criterion is noise.

**Break Point 3: WikiText-103 perplexity may not reflect SST-2 behavior.** A language modeling loss may be preserved even when classification-relevant attention patterns are disrupted, because SST-2 classification may depend more heavily on global context. The two benchmarks might diverge.

**Mitigation Strategies:** (1) Report which layer POSITIONS the entropy criterion selects — if predominantly later layers, the residual bus claim holds. (2) Run entropy scoring on 3 different 100-sequence subsets and report Spearman ρ. (3) Treat WikiText-103 and SST-2 as independent experiments with separate success thresholds.

**Key Points:**
- Layer depth position matters for the residual bus claim — not all positions have equal residual stream richness
- Calibration stability must be explicitly validated (Spearman ρ across seeds)
- WikiText-103 and SST-2 may diverge — treat as independent benchmarks
- All three break points are testable — not fatal, require explicit experimental steps

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex's concerns are precise and addressable — each has a concrete mitigation already within scope.

**On depth position:** Prof. Rex is correct that the global bus claim is stronger for later-layer high-entropy layers. But this is a FEATURE: we explicitly report which depth positions entropy selects and examine whether they cluster in later layers. If yes — mechanism confirmed. If early layers are selected — we've identified a boundary condition where the global bus isn't yet rich enough. Either way, scientific insight. This is an OUTPUT of the experiment, not an assumption.

**On calibration stability:** 100 sequences is standard for GPTQ/AWQ. For entropy rank stability, we add: run entropy on 3 non-overlapping 100-sequence subsets from WikiText-103, compute Spearman ρ for top-8 layer rankings. If ρ > 0.8, calibration is stable. If ρ < 0.7, use 300 sequences. Minor protocol addition, no additional compute budget needed at inference time.

**On benchmark divergence:** Prof. Rex correctly identifies that WikiText-103 (generative) and SST-2 (discriminative) test different aspects. We treat them as independent: (a) WikiText-103 perplexity ≤2pt at k=4, ≤5pt at k=8; (b) SST-2 accuracy ≥98% of baseline at k=4. If they diverge — LM preserved, classification hurt — that finding itself characterizes which attention functions are most sensitive to SWA conversion, publishable as a finding.

**Converged hypothesis statement:** In Llama-2-7B (32 layers), replacing the k=4 highest-entropy layers (by mean per-layer attention entropy on a 100-sequence calibration set) with SWA(w=512), zero-shot, is hypothesized to maintain WikiText-103 perplexity within 2 points and GLUE SST-2 accuracy within 2 percentage points of the full-attention baseline, because high-entropy layers contribute less unique global context and the residual stream of the 28 retained full-attention layers provides sufficient global context compensation. The entropy criterion is validated against random-k and last-k selection baselines at matched k.

All convergence criteria met: SPECIFIC claim with thresholds, MECHANISM via residual stream bus, PREDICTIONS P1-P3 with quantified success criteria, NOVELTY vs SWAA (zero-shot selective vs fine-tuning-required full-model), FEASIBILITY confirmed (< 1 GPU-hour, existing code paths), OBJECTIONS addressed (depth position analysis, calibration stability, benchmark divergence).

**Key Points:**
- Depth position analysis is an experiment output — adds mechanistic insight without assumptions
- Calibration stability test (Spearman ρ, 3 seeds) is minor protocol addition
- Independent benchmark thresholds handle WikiText-103 vs SST-2 divergence
- All 6 convergence criteria now met — discussion ready for structuring

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The entropy-guided selective layer conversion is genuinely novel. The key innovation — using layer-level attention entropy as a zero-shot SWA-convertibility signal in causal decoder LLMs — has not been demonstrated before. SWAA converts all layers with fine-tuning; this work converts k/32 layers without fine-tuning, guided by an entropy criterion that HIES literature validates at head level. The framing of "entropy as local-context sufficiency proxy" is a new mechanistic lens that could influence how the community thinks about attention pattern heterogeneity across depth.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has clear success and falsification criteria: ≤2pt perplexity at k=4, ≤5pt at k=8 on WikiText-103; SST-2 within 2pp/5pp of baseline. Comparison baselines (random-k, last-k) provide experimental contrast to validate the entropy criterion specifically. Calibration stability check (Spearman ρ across seeds) adds methodological robustness. The hypothesis would be definitively falsified if entropy-guided k=4 produces equal or worse perplexity than random-k=4, or if any selective conversion (even k=1) causes >5pt degradation.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The work is positioned at the intersection of efficient inference and attention pattern analysis. Both positive and negative results are publishable and informative. Connection to Longformer (5840 cit.), Michel et al. (1454 cit.), and Mistral 7B (3809 cit.) ensures broad legibility. If successful, opens a new class of post-training attention surgery; if negative, characterizes the boundary conditions of SWA retrofitting — both advance the field.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The technical mechanism is sound: HuggingFace AttentionMaskConverter, PyTorch sliding window mask, RoPE compatibility (selective conversion preserves 28/32 full-attention layers for global position context). Pilot is within 1 GPU-hour on 1 H100 (entropy scoring ~15min, eval ~30min per configuration). No new packages required. The calibration procedure (100 sequences, output_attentions=True) is identical to quantization calibration practice.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is: **Entropy-Guided Zero-Shot Selective Sliding Window Attention Conversion in Llama-2-7B** (H-EntropySWA-v1).

Under the setting of Llama-2-7B (32 attention layers) with no fine-tuning, if the k=4 layers with highest mean per-layer attention entropy (measured on a 100-sequence calibration set using output_attentions=True) are replaced with sliding window attention (window size w=512 tokens), then WikiText-103 perplexity will remain within 2 points and GLUE SST-2 accuracy within 2 percentage points of the full-attention baseline, BECAUSE high-entropy layers already contribute less unique global context than low-entropy layers (supported by Michel et al. 2019 and Raganato et al. 2020 at head/layer level), and the residual stream of the 28 remaining full-attention layers provides sufficient global context for the converted layers.

The causal mechanism has three steps: (1) attention entropy on a calibration set identifies layers with diffuse, low-information-value global attention patterns; (2) replacing those layers with SWA(w=512) aligns the mechanism with measured behavior; (3) the 28 retained full-attention layers propagate global context through the residual stream, compensating for the SWA layers' reduced reach.

Three testable predictions: P1 — k=4 entropy-guided SWA conversion maintains WikiText-103 perplexity within 2pt of baseline (primary, immediate test); P2 — entropy-guided k=4 outperforms random-k=4 and last-k=4 on perplexity preservation (validates criterion); P3 — k=8 conversion characterizes the conversion capacity boundary (≤5pt or >5pt provides boundary estimate).

The experimental design uses entirely existing benchmarks (WikiText-103 from HuggingFace datasets, GLUE SST-2), an existing model (Llama-2-7B from meta-llama/Llama-2-7b-hf), and existing code paths (HF AttentionMaskConverter). No new benchmarks, no synthetic data, no human annotation required — fully compliant with pipeline feasibility constraints.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Entropy rank ordering may be Llama-2-7B-specific; generalization to other causal decoders untested (note as future work)
- Calibration domain: WikiText-style calibration may bias entropy estimates toward generative tasks; compare to SST-2-domain calibration as ablation
- Window size w=512 is fixed; sensitivity to w=256 or w=1024 is unexplored
- **Mitigation Strategy:** (1) Run entropy scoring with both WikiText and SST-2 calibration sequences and report whether selected layer sets differ. (2) Include window size as secondary ablation if compute budget allows. (3) Note Llama-2-7B specificity as explicit limitation with architecture-agnostic generalization as future work.

