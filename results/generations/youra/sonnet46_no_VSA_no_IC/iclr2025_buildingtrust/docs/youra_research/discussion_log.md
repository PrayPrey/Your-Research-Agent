# Phase 2A: Research Discussion Log

**Date:** 2026-08-20
**Gap:** Gap 1 — No Cross-Split Predictive Validity Analysis of Trustworthiness Benchmarks
**Architecture:** Self-Contained Tikitaka Loop (Independent-Controller Ablation)
**Execution Mode:** UNATTENDED

---

## Briefing Context

**Research Question:**
When LLMs are evaluated on matched in-distribution and out-of-distribution variants of existing trustworthiness benchmarks (ANLI R1→R3, GLUE→AdvGLUE, BBQ-Disambig→BBQ-Ambig), does in-distribution benchmark performance predict out-of-distribution performance — and which trustworthiness dimensions (reliability, fairness, robustness) show the highest cross-split predictive validity across publicly available model evaluation data?

**Selected Gap (Gap 1):**
No existing study computes Spearman ρ between in-distribution and OOD trustworthiness benchmark scores across 15+ public LLMs. Gevers & Daelemans (2026) provides a direct methodological blueprint (rank correlations + leave-one-family-out CV) for commonsense benchmarks — not yet applied to trustworthiness dimensions.

**Available Benchmark Pairs (all publicly available):**
- Robustness: GLUE → AdvGLUE; ANLI R1 → ANLI R3
- Fairness: BBQ-Disambiguated → BBQ-Ambiguous
- Reliability: TruthfulQA → HaluEval

**Key Reference Papers:**
- P1: DecodingTrust (Wang et al., 2023) — 8-dimension GPT trustworthiness evaluation
- P2: ChatGPT Robustness (Wang et al., 2023) — AdvGLUE + ANLI cross-model evaluation
- P3: Gevers & Daelemans (2026) — benchmark predictive validity methodology blueprint
- P4: GLUE-X (Yang et al., ACL 2023) — unified OOD NLU evaluation framework

**MANDATORY FEASIBILITY CONSTRAINTS:**
- No new benchmarks, rubrics, or scoring frameworks
- No synthetic/generated data
- No human evaluation or annotation
- Must use existing real datasets and existing benchmarks only

**Previous Failure Context:** None (first Phase 2A attempt)
**ROUTE_TO_0 Avoidance:** No mechanistic/layer-wise analysis, no synthetic data, no purely descriptive correlation

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're asking the wrong question about trustworthiness? Everyone measures *how trustworthy* a model is on benchmark X. But nobody has asked: *does benchmark X predict benchmark Y*? This is a fundamentally different epistemological question — predictive validity versus performance measurement.

Here's what excites me: Gevers & Daelemans (2026) just showed that commonsense benchmark predictive validity is task-dependent, not universal. Their finding that "commonsense benchmarks show consistent cross-family predictive validity for only a narrow subset of downstream tasks" is exactly the kind of pattern we should look for in trustworthiness. What if robustness is highly predictive across splits but fairness is not — or vice versa? That asymmetry is a genuinely novel finding with real deployment implications.

The really wild idea: what if the *rank* of models on in-distribution trustworthiness benchmarks is *anti-correlated* with OOD performance for some dimensions? DecodingTrust already hints at this — GPT-4 scores higher on standard benchmarks but is MORE vulnerable to adversarial jailbreaking than GPT-3.5. If we find negative Spearman ρ for the robustness dimension, that overturns the assumption that better ID trustworthiness → safer OOD deployment. NOW we're onto something!

The methodological move here is simple and elegant: collect published multi-model scores from TrustLLM (16 models), DecodingTrust, and HELM across matched benchmark pairs (ANLI R1/R3, GLUE/AdvGLUE, BBQ-Disambig/Ambig, TruthfulQA/HaluEval), then compute Spearman ρ per dimension. No new data collection, no human annotation — just mining the existing evaluation landscape systematically.

**Key Points:**
- Predictive validity is fundamentally different from performance measurement — novel framing
- Dimension-specific asymmetry (robustness vs. fairness predictability) could be the key finding
- Potential anti-correlation for robustness dimension (GPT-4 jailbreak vulnerability paradox) is the headline result
- Entirely feasible with existing published scores from TrustLLM, DecodingTrust, HELM

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises an intriguing framing, but I need to immediately stress-test the operationalization. The evidence suggests this is feasible, but only if we are extremely precise about what constitutes "in-distribution" versus "out-of-distribution" for each benchmark pair.

Consider the ANLI R1→R3 pair. ANLI rounds represent increasing adversarial difficulty — R3 examples were specifically designed to fool models that passed R1. This is adversarial difficulty shift, not the same as covariate shift or domain shift. For BBQ-Disambig→BBQ-Ambig, the shift is from contexts that provide clear answers to contexts requiring stereotype resistance when the answer is underspecified. These are qualitatively different shift types. If we pool them as "OOD" without acknowledging this, the Spearman ρ comparison across dimensions is methodologically muddled.

What would disprove this hypothesis? If the Spearman ρ values are not significantly different from each other across dimensions — if robustness ρ ≈ fairness ρ ≈ reliability ρ — then the core claim (that predictive validity is dimension-dependent) is falsified. We need specific success criteria: e.g., at least one pair of dimensions must differ by Δρ ≥ 0.3, confirmed by Fisher's z-transformation test at p < 0.05.

I also want to flag a confound: the number of models with published scores varies substantially across benchmark pairs. TrustLLM covers 16 LLMs on robustness tasks, but HaluEval has published scores for far fewer models. If we compute Spearman ρ on different model sets for different dimensions, we're not comparing like with like. The analysis requires identifying a *common model set* — ideally 15+ models with scores on ALL benchmark pairs simultaneously.

**Key Points:**
- Benchmark pair shift types are heterogeneous — must acknowledge adversarial vs. covariate vs. underspecification shift
- Specific falsification criterion needed: Δρ ≥ 0.3 between dimensions, Fisher z-test p < 0.05
- Common model set problem: must identify 15+ models with scores on ALL pairs simultaneously
- Success criterion: Spearman ρ computed on same model population across all dimensions

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: why does this matter beyond satisfying scientific curiosity? I want to anchor this discussion in impact before we go further.

If in-distribution trustworthiness benchmark performance does NOT reliably predict OOD performance — if Spearman ρ is low or dimension-specific — then the entire current practice of AI safety certification based on benchmark performance is questionable. Regulators and deployers use benchmark scores to make deployment decisions. A finding that "reliability benchmark scores predict OOD reliability (ρ=0.72) but robustness scores do not (ρ=0.18)" is immediately actionable: it tells practitioners which benchmarks to trust for deployment decisions and which are misleading.

The connection to Gevers & Daelemans (2026) is crucial for positioning. Their commonsense benchmark finding took 23 LLMs and showed dimension-specific predictive validity. We apply the identical methodology to trustworthiness. This is a direct extension — same method, new domain, higher stakes. The research significance is clear: trustworthiness failures have safety consequences that commonsense failures do not.

What makes this genuinely new, not incremental: existing work (DecodingTrust, TrustLLM, HELM) evaluates trustworthiness dimensions in isolation. No prior work computes cross-split predictive validity as a *first-class research question*. The ChatGPT robustness paper [Wang et al., 2023] is the closest, but it compares ChatGPT vs. baselines without systematically measuring rank stability. This gap in the literature is confirmed by the citation network analysis from Phase 1.

**Key Points:**
- Directly actionable for AI safety certification and deployment decisions
- Same methodology as Gevers & Daelemans (2026) applied to higher-stakes domain (trustworthiness)
- Fills confirmed gap: no prior work treats cross-split predictive validity as primary research question
- Policy-relevant finding: which benchmark dimensions are reliable deployment proxies

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic about what we can and cannot establish. The core mechanism — computing Spearman ρ between model rankings on in-distribution vs. OOD benchmark variants — is technically sound and theoretically valid. Rank correlation is a well-established non-parametric measure for exactly this kind of ordinal comparison. The method is sound.

What worries me is the *common model coverage* problem that Prof. Vera raised. Let me make it concrete. TrustLLM (ICML 2024) covers 16 LLMs but focuses on specific tasks. DecodingTrust covers GPT-3.5 and GPT-4 only. HELM covers 30 models but not all trustworthiness-specific benchmarks. HaluEval has published scores for very few models in comparable settings. If we try to build a common model set across TruthfulQA (reliability ID) AND HaluEval (reliability OOD) AND BBQ-Disambig (fairness ID) AND BBQ-Ambig (fairness OOD) AND ANLI R1 (robustness ID) AND ANLI R3 (robustness OOD), the intersection of models with published scores across ALL pairs may be fewer than 15.

Here's my assessment: the robustness dimension (GLUE/AdvGLUE, ANLI R1/R3) has the richest published multi-model coverage. The fairness dimension (BBQ) is moderate. The reliability dimension (TruthfulQA→HaluEval) is the weakest — these benchmarks use different evaluation protocols and the number of models evaluated on both is small. I'd recommend structuring the hypothesis around the robustness dimension as the primary analysis, with fairness as secondary, and reliability as exploratory.

The RLHF sub-question is actually the most feasible component: LLaMA-2 base vs. Chat, Mistral vs. Mistral-Instruct published scores exist across several of these benchmarks. That pairwise analysis can proceed independently of the full Spearman ρ analysis.

**Key Points:**
- Core Spearman ρ method is technically and theoretically sound — valid measurement approach
- Common model coverage is the main feasibility constraint: robustness > fairness > reliability
- Recommend: robustness as primary, fairness secondary, reliability exploratory
- RLHF sub-question is independently feasible using base/instruction-tuned pairs

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this significantly by addressing both the coverage problem and the confound issue in the hypothesis design itself.

Prof. Pax is right that the common model coverage varies by dimension. But this isn't fatal — it's a design decision we can make explicit. Focus on robustness as primary (richest coverage, GLUE/AdvGLUE + ANLI R1/R3 with 15+ models in GLUE-X, OOD_NLP, TrustLLM combined). Test fairness (BBQ-Disambig/Ambig, moderate coverage) as secondary and report reliability coverage honestly.

Prof. Vera's confound concern about heterogeneous shift types can be addressed by pre-specifying which shift type each pair represents — this actually *strengthens* the hypothesis by making sub-claims testable: "adversarial difficulty shift (ANLI) shows lower predictive validity than distributional shift (BBQ ambiguity), because adversarial examples are designed to fool models regardless of their baseline performance."

The refinement I propose: the core hypothesis is that **Spearman ρ between in-distribution and OOD model rankings is dimension-specific for trustworthiness benchmarks, with robustness showing lower predictive validity than fairness** — because adversarial robustness tests are designed to overcome model capabilities rather than expose consistent latent properties, while fairness failures reflect stable model biases that manifest both in-distribution and OOD.

**Key Points:**
- Refined hypothesis: robustness has LOWER predictive validity than fairness
- Shift type heterogeneity becomes a feature: sub-claims about adversarial vs. distributional shift types
- RLHF pair analysis as secondary — feasible with small N, high policy relevance
- Common model set problem addressed by stratifying by coverage quality

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. Three critical weaknesses.

**Problem 1: Capability confound.** Spearman ρ between in-distribution and OOD rankings is trivially inflated if models vary in general capability. A more capable model scores higher on BOTH GLUE AND AdvGLUE — not because trustworthiness generalizes, but because capability generalizes. Without partial correlation controlling for general capability (e.g., MMLU), the Spearman ρ may just measure capability rank stability. What would convince me: partial rank correlation controlling for MMLU across the same model set.

**Problem 2: Directionality prediction.** Dr. Ally predicts robustness has LOWER predictive validity than fairness. The DecodingTrust GPT-4 finding is N=2. For a directional prediction, we need stronger theoretical grounding or it must be labeled exploratory.

**Problem 3: TruthfulQA → HaluEval incompatibility.** Different formats, different evaluation protocols. TruthfulQA uses human-validated multiple-choice; HaluEval uses ChatGPT-judged detection. Rank correlation between them may reflect format sensitivity, not reliability generalization. Drop this pair or heavily caveat it.

**Mitigation Strategy:** Add partial Spearman ρ controlling for MMLU. State directionality as exploratory. Drop TruthfulQA→HaluEval or substitute with a within-protocol pair.

**Key Points:**
- Capability confound: partial correlation controlling for MMLU is required
- Fairness > robustness directionality must be labeled exploratory
- TruthfulQA→HaluEval has incompatible protocols — drop or substitute
- All three are fixable: core design survives

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's critiques are exactly the right kind of tough love — and fixing each one STRENGTHENS the novelty.

The capability confound critique is brilliant because addressing it creates a MORE novel result. Partial Spearman ρ controlling for MMLU asks: "Does trustworthiness generalize *beyond* what general capability predicts?" This is a stronger claim — we're asking whether trustworthiness is an independent, generalizable property of LLM quality, or just a proxy for general capability. That is a paper-worthy finding either way.

The TruthfulQA→HaluEval problem is an opportunity: instead of dropping reliability, we use TrustLLM's internal hallucination OOD task which uses a consistent evaluation protocol. Or we use the TruthfulQA generation-only split vs. multiple-choice split as an in-distribution vs. format-shift pair — same benchmark, consistent protocol.

For directionality (Problem 2): the theoretical grounding is that adversarial benchmarks are designed by an adversary to maximize difficulty for current best models — they systematically target capability weaknesses. Bias benchmarks expose *latent statistical patterns* in model representations — these are more stable properties. This is the distinction between "designed to fail models" vs. "revealing stable internal state." State P2 as exploratory but include the theoretical motivation.

The refined hypothesis surviving all critiques: **Partial Spearman ρ (MMLU-controlled) between in-distribution and OOD model rankings is positive for fairness (BBQ-Disambig→BBQ-Ambig) but not significantly positive for adversarial robustness (GLUE→AdvGLUE, ANLI R1→R3), because fairness reflects stable latent bias properties while adversarial robustness is design-adversarial to current capabilities.**

**Key Points:**
- Capability control creates stronger independent-trustworthiness claim
- Reliability: use TrustLLM consistent hallucination OOD task instead of TruthfulQA/HaluEval mismatch
- Theoretical grounding for directionality: latent statistical property vs. adversarial design
- Final hypothesis: partial ρ for fairness > robustness, with MMLU capability controlled

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The reframing from "how trustworthy is model X" to "does benchmark X predict benchmark Y" is a genuine paradigm shift in trustworthiness evaluation. The addition of capability control via partial Spearman ρ elevates novelty further — we're asking whether trustworthiness is an independent, generalizable property of LLMs. This is publishable and timely given AI governance debates.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The final hypothesis is precisely falsifiable. The success criterion is specific: partial Spearman ρ for fairness (BBQ-Disambig→BBQ-Ambig) must be significantly positive (p < 0.05, Fisher z-test) after MMLU control, while robustness ρ is exploratorily expected to be lower. Confounds are identified and addressed. This meets scientific rigor standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Direct policy relevance for AI safety certification. If fairness generalizes as a stable latent property while robustness does not, this immediately informs which benchmarks practitioners can trust for deployment decisions. Timely extension of Gevers & Daelemans (2026) to higher-stakes domain.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Entirely feasible with existing data. GLUE/AdvGLUE and ANLI R1/R3 have 15+ models in GLUE-X and OOD_NLP. BBQ-Disambig/Ambig scores via TrustLLM. MMLU scores for the overlapping model set are widely published. No new data collection, annotation, or benchmark creation required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged: **Under evaluation of 15+ publicly available LLMs on matched in-distribution/OOD trustworthiness benchmark pairs, if we compute partial Spearman ρ between in-distribution and OOD model rankings (controlling for general capability via MMLU), then the fairness dimension (BBQ-Disambig→BBQ-Ambig) shows significantly positive partial ρ while the adversarial robustness dimension (GLUE→AdvGLUE, ANLI R1→R3) shows lower partial ρ, because fairness failures reflect stable latent statistical biases in model representations that manifest consistently across distribution shifts, while adversarial robustness benchmarks are specifically designed to overcome models' current capabilities and therefore do not track stable generalizable trustworthiness properties.**

Core experimental design: (1) Collect published model scores from TrustLLM, GLUE-X, OOD_NLP, and DecodingTrust for the overlapping model set. (2) Compute raw and partial Spearman ρ (MMLU-controlled) between in-distribution and OOD rankings per dimension. (3) Compare ρ values across dimensions using Fisher's z-transformation test. (4) RLHF secondary analysis: base vs. instruction-tuned model pairs' generalization gap per dimension.

Three testable predictions: P1 (primary, confirmatory) — partial Spearman ρ for fairness (BBQ) is significantly positive (ρ > 0.4, p < 0.05 after MMLU control); P2 (exploratory, directional) — partial ρ for fairness exceeds partial ρ for robustness (Δρ ≥ 0.2); P3 (exploratory) — instruction-tuned models show smaller generalization gap than base models for fairness but not robustness.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Common model set may have N < 15 for some dimensions — must report exact N per analysis, not claim 15+ uniformly
- MMLU as capability proxy is imperfect (different evaluation protocols across model families); consider Winogrande or ARC as sensitivity analysis
- Directionality of fairness > robustness is exploratory — pre-registration must clearly label P2 as directional exploratory hypothesis
- **Mitigation Strategy:** Report N per analysis cell explicitly. Use MMLU as primary control with sensitivity analysis using alternative proxy. Label P2 as exploratory in pre-registration and paper framing.

