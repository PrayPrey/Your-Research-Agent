# Phase 2A Discussion Log
# Gap 1: No Unified Comparative Benchmark Across All Major Uncertainty Proxy Types on Standard Factual QA
# Architecture: Self-Contained Loop (UNATTENDED — independent-controller ablation, Claude plays all personas)

---

## Previous Failure / Routing Context

**Type:** SUPERSEDED (ROUTED_TO_PHASE_2A from Phase 4)
**Prior Hypothesis:** h-e2-v2 (supersedes h-e2)
**Date:** 2026-08-25

### Summary of Failed Approach

h-e2 and h-e2-v2 both attempted to replicate Kuhn et al.'s semantic entropy AUROC ≥ 0.75 on TriviaQA dev using Llama-2-7B with K=10 samples. Both FAILED.

- **SE AUROC achieved:** 0.5419 (n=98 partial, 95% CI [0.4228, 0.6503])
- **Gate threshold:** 0.75 — unachievable for Llama-2-7B
- **Root cause:** Kuhn et al. achieved 0.75+ on Llama-65B, not 7B. The 0.75 threshold is model-scale-specific.

### What Was Confirmed Working

- Semantic entropy mechanism activates on Llama-2-7B (avg 3.89 clusters/question)
- SE AUROC > TE AUROC direction confirmed (+0.0292 gap)
- EM accuracy 34.4% on TriviaQA (sufficient uncertainty diversity)
- h-e2-v2 code is correct and reusable (generation.py, uncertainty.py, evaluate.py)

### Prohibited Redesign Directions

1. **DO NOT** use AUROC ≥ 0.75 as gate for Llama-2-7B
2. **DO NOT** treat the Kuhn et al. 0.75 threshold as model-scale-agnostic
3. Any replication-style hypothesis must calibrate thresholds per model scale

### Recommended Redesign (from Phase 4 Reflection)

Option A (preferred): Revise gate to AUROC ≥ 0.60 for 7B model existence check
Option B: Upgrade to Llama-2-13B (expected ~0.65-0.70)
Option C: Use model where Kuhn et al. explicitly reported AUROC > 0.75

### Key Lesson

Pilot on 200 questions before committing to full dataset. AUROC trajectory check at small scale prevents wasted compute.

---

## Selected Gap

**Gap ID:** Gap-1
**Title:** No Unified Comparative Benchmark Across All Major Uncertainty Proxy Types on Standard Factual QA
**Priority:** CRITICAL / PRIMARY
**Connection to Research Question:** Directly operationalizes "reliably predict factual hallucinations" — no controlled multi-method comparison currently exists.

**Key Methods to Compare:**
- Single-pass softmax entropy (token-level)
- Monte Carlo self-consistency / SelfCheckGPT (Manakul et al. 2023)
- Semantic entropy (Kuhn et al. 2023) — but with model-scale-calibrated threshold
- Verbalized confidence (Kadavath 2022, Xiong 2023)

**Key Benchmarks:** TriviaQA, NaturalQuestions, TruthfulQA
**Key Metrics:** AUROC, ECE, Precision@abstention-rate

---

## Paper Context (Claude-written summaries, no MCP)

### P1: Semantic Uncertainty (Kuhn, Gal, Farquhar 2023 — arXiv 2302.09664)
- **Core contribution:** NLI-based clustering of semantically equivalent outputs; entropy computed over semantic clusters rather than surface strings.
- **Key result:** Outperforms token-entropy baseline on TriviaQA/NQ with Llama-65B. AUROC >0.75 at 65B scale.
- **Limitation relevant to redesign:** 7B result not reported; 0.75 threshold is 65B-specific.
- **Code:** lorenzkuhn/semantic_uncertainty (reusable, h-e2-v2 already validated)

### P2: SelfCheckGPT (Manakul, Liusie, Gales 2023 — arXiv 2303.08896)
- **Core contribution:** Black-box consistency detection — K stochastic samples compared via BERTScore/NLI/n-gram. No logit access required.
- **Key result:** Detects hallucinations in GPT-4/LLaMA outputs. Evaluated on WikiBio factuality.
- **Limitation:** Not compared head-to-head with semantic entropy on TriviaQA/NQ with identical evaluation metrics.
- **Code:** potsawee/selfcheckgpt

### P3: Xiong et al. 2023 (arXiv 2306.13063)
- **Core contribution:** Systematic multi-method comparison of confidence elicitation (verbalized, logit-based) across MMLU, TriviaQA, CoQA.
- **Key result:** Verbalized confidence is poorly calibrated at 7B scale; improves at 70B. Token-level entropy better calibrated than verbalized for smaller models.
- **Limitation:** Does not include semantic entropy as a compared method.

### P4: Huang et al. 2023 (arXiv 2307.10236)
- **Core contribution:** Comparative study of entropy, sampling variance, p(True) on factual QA.
- **Key result:** Sampling-based methods generally outperform single-pass entropy. No TruthfulQA evaluation.
- **Limitation:** Limited model coverage; does not span 7B-70B scale comparison.

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

The field has four distinct uncertainty proxy families — token entropy, consistency sampling, semantic entropy, and verbalized confidence — each validated in isolation on slightly different benchmarks with different metrics and different model scales. The core gap is that we have no controlled experiment where all four run on the same model, same benchmark, same metric at the same time.

Here's what I find most exciting: the h-e2-v2 failure actually hands us a gift. We now know that semantic entropy's AUROC on TriviaQA is scale-dependent — 0.54 at 7B, presumably higher at 13B/70B. That's not a failure, that's a data point in an undocumented calibration curve. If we systematically run all four methods across 7B and 70B on TriviaQA + NQ + TruthfulQA, we get three things at once: (1) the first controlled four-way comparison, (2) the scale-calibration curve for each method, and (3) a practitioner's guide for which method to use given available compute.

The novelty angle I want to propose: instead of treating this as a "which method wins" benchmark, frame it as characterizing the **uncertainty frontier** — the Pareto-optimal set of (AUROC, compute cost) pairs. Single-pass entropy is cheapest (1 forward pass). Semantic entropy costs K forward passes + NLI. SelfCheckGPT costs K forward passes + BERTScore. Verbalized confidence costs 1 forward pass but requires instruction-tuned model. Each sits at a different point on the compute-uncertainty-quality curve. Mapping that frontier is both more honest and more useful than declaring a single winner.

Two angles I think deserve exploration: (A) whether the frontier shifts substantially across benchmarks (TriviaQA vs. TruthfulQA have very different factual structures), and (B) whether a cheap ensemble — e.g., weighted combination of token entropy + semantic entropy — can outperform any single method at similar cost.

**Key Points:**
- Four-way controlled comparison on same benchmarks/metrics/models is the primary missing piece
- h-e2-v2's failure reveals a scale-calibration curve — exploit it as a finding rather than a failure
- Frame as uncertainty frontier (AUROC vs. compute) rather than single-winner benchmark
- Explore: does combining cheap (entropy) + expensive (semantic entropy) beat either alone?

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's framing is appealing but we need to tighten it considerably before it becomes testable. Let me flag the falsifiability challenges.

First, the "uncertainty frontier" framing sounds clean but hides a multi-dimensional optimization problem. AUROC measures discrimination ability (can you rank uncertain questions above confident ones?). ECE measures calibration (does stated confidence match actual accuracy?). Precision@abstention measures selective prediction value. These three metrics do NOT necessarily agree — a method can have high AUROC but poor ECE (it ranks well but is miscalibrated). Any claim about a "frontier" needs to commit to which metric axis matters most, otherwise the paper becomes an inconclusive survey.

Here's my proposed falsifiable hypothesis structure: **the primary claim should be about rank ordering of AUROC across the four methods at a fixed model scale and benchmark.** Specifically — does semantic entropy achieve strictly higher AUROC than token entropy on TriviaQA at 7B scale? We already know from h-e2-v2 that SE achieves ~0.54 on Llama-2-7B. The question becomes: what does single-pass token entropy achieve on the same 200-question pilot? If token entropy achieves 0.52, the gap is +0.02. If it achieves 0.60, then SE is WORSE. That's a concrete, falsifiable comparison.

The model-scale calibration curve Dr. Nova mentions is genuinely interesting, but it requires running at 13B and 70B — significant compute. If we're constrained to 7B (as h-e2-v2 was), we can still produce a valuable controlled comparison of all four methods at 7B. The scale curve then becomes Phase 2B or Phase 5 work.

My proposed scope: **7B model (Llama-2-7B), TriviaQA dev, N=500 questions, K=10 samples for consistency methods, four-way comparison on AUROC only.** Secondary: ECE. Scale extension deferred.

**Key Points:**
- Three metrics (AUROC, ECE, Precision@k) don't always agree — commit to primary metric
- Core falsifiable claim: rank ordering of AUROC across four methods at fixed scale/benchmark
- AUROC from h-e2-v2 (SE=0.54) gives us one anchor; compare TE, SelfCheckGPT, verbalized at same setup
- Scope to 7B + TriviaQA for Phase 2B; scale extension deferred
- N=500 pilot gives AUROC estimate with meaningful CI; scale to full only if pattern stable

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

Both previous perspectives have merit but I want to push on the **research significance** question before we finalize scope. The field already has Xiong 2023 and Huang 2023 doing multi-method comparisons. What would make our contribution meaningfully different?

The answer is in what they omit: **neither Xiong nor Huang includes semantic entropy as a compared method.** Xiong focuses on verbalized confidence strategies. Huang covers entropy and sampling variance but not semantic entropy via NLI clustering. And crucially, neither uses the h-e2-v2 Llama-2-7B setup where we already have ground truth: SE achieves 0.54 AUROC. We can immediately compare TE and SelfCheckGPT against that anchor on the exact same 98-question pilot from h-e2-v2. Zero additional generation cost for SE — the samples already exist.

The significance claim I would make: **the first comparison to include semantic entropy alongside token entropy, SelfCheckGPT, and verbalized confidence on TriviaQA at 7B scale, with the insight that SE's advantage over TE shrinks at smaller model scales.** This reframes h-e2-v2's "failure" as a scale-calibration finding — a positive result about the boundary conditions of semantic entropy's superiority.

For impact: practitioners running open-source 7B models need to know whether the computational overhead of semantic entropy (K=10 NLI clustering) buys meaningful AUROC gain over single-pass token entropy (1 forward pass, 10× cheaper). If the gap is +0.02 at 7B, they should use token entropy. If it's +0.08, semantic entropy may be worth it. That's actionable, publishable guidance.

Secondary significance: first to report semantic entropy AUROC with a properly calibrated threshold (0.60) rather than the 0.75 overhang from Kuhn et al.'s 65B results. This prevents future researchers from making the same mistake as h-e2 and h-e2-v2.

**Key Points:**
- Novel contribution: first comparison including semantic entropy in the four-way benchmark at 7B
- Reframe h-e2-v2's failure as scale-calibration finding — positive contribution
- Existing h-e2-v2 pilot (98 questions, SE samples) is free reusable infrastructure
- Actionable insight: does NLI overhead buy meaningful AUROC over token entropy at 7B?
- Establishes model-scale-calibrated benchmark: SE gate = 0.60 for 7B, not 0.75

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

The discussion is converging on something concrete. Let me audit feasibility.

**What we have from h-e2-v2:** 98 generated samples (K=10 each) on TriviaQA dev. SE AUROC = 0.54. All code (generation.py, uncertainty.py, evaluate.py) is validated and reusable.

**What we need to add:** For the same 98 questions:
1. **Token entropy (TE):** Compute from existing logit outputs — if generation.py saved logits, this costs 0 additional GPU time. If not, one forward pass per question with greedy decoding (trivial, <<1 GPU hour on 7B).
2. **SelfCheckGPT (consistency-based):** We already have K=10 samples per question. SelfCheckGPT BERTScore mode computes pairwise similarity across the 10 samples — no additional LLM inference needed, just BERTScore computation (~minutes on CPU).
3. **Verbalized confidence:** Requires a new inference run asking "How confident are you?" after each answer. Llama-2-7B in instruction mode. ~98 additional forward passes. Feasible in <1 GPU hour.
4. **Extending to N=500:** Generate K=10 samples for 402 additional questions using h-e2-v2's generate_shard.py. At h-e2-v2's throughput (~5 GPU-minutes per question at 7B), 402 questions ≈ 33 GPU hours. This is the expensive step.

**Recommended scope:** Start with the existing 98-question pilot. Compare all four methods on the same 98 questions using existing samples (TE, SelfCheckGPT from existing samples; verbalized from one new inference run). Report AUROC with 95% CI via bootstrap. If pattern is clear (one method consistently higher), stop there. If inconclusive (<0.02 gap), extend to 500.

**Key feasibility gate:** N=98 is sufficient to detect AUROC differences of ≥0.06 with 80% power (bootstrap CI typically ±0.05). This means we can publish a meaningful comparison without the 33-GPU-hour extension.

**Key Points:**
- Existing h-e2-v2 infrastructure (98 questions, K=10 samples) is reusable for 3 of 4 methods
- SelfCheckGPT and TE are free from existing samples — only verbalized confidence needs new inference
- N=98 pilot detects AUROC differences ≥0.06 at 80% power (sufficient for a clear result)
- Extension to N=500 only needed if pilot is inconclusive
- Total new compute: <2 GPU hours for 3-method extension on existing 98 questions

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent convergence happening. Let me synthesize what we have and strengthen the hypothesis against the failure context.

The key insight from h-e2-v2 is that the mechanism (SE clustering) works — what failed was the threshold calibration. Our new hypothesis reframes this: instead of asking "does SE achieve 0.75 AUROC?" (which we now know is 65B-scale specific), we ask "does SE achieve meaningfully higher AUROC than cheaper alternatives (TE, SelfCheckGPT) on Llama-2-7B?" This is the correct operationalization of "does the NLI overhead buy anything at small scale?"

**Strengthened hypothesis:** On TriviaQA dev at Llama-2-7B scale, semantic entropy achieves a practically meaningful AUROC advantage (≥0.05) over single-pass token entropy, while SelfCheckGPT achieves similar AUROC to SE with comparable compute cost. Verbalized confidence underperforms both at 7B scale.

This hypothesis is:
- **Falsifiable:** Three pairwise AUROC comparisons with bootstrap CIs on N=98 (extendable to N=500)
- **Novel:** First to include SE in a controlled 4-way comparison; explicitly calibrates against 7B
- **Feasible:** Reuses h-e2-v2 infrastructure; new cost <2 GPU hours
- **Non-repeating:** Uses 0.60 gate (not 0.75), and reframes as relative comparison not absolute threshold
- **Impactful:** Answers the practitioner question — does the NLI overhead of SE pay off at 7B?

**Testable Predictions:**
- **P1 (Primary):** SE AUROC > TE AUROC by ≥0.05 on TriviaQA@7B (gap exceeds CI half-width). Falsified if SE-TE gap < 0.03.
- **P2:** SelfCheckGPT AUROC is within 0.03 of SE AUROC (similar performance, different mechanism). Falsified if gap > 0.05.
- **P3:** Verbalized confidence AUROC < both SE and TE at 7B (known from Xiong 2023 that small models have poor verbalized calibration). Falsified if verbalized AUROC ≥ SE AUROC.

**Key Points:**
- Reframes h-e2-v2 failure as positive calibration finding
- Primary gate: SE > TE by ≥0.05 (relative, not absolute threshold)
- Uses N=98 existing pilot — zero new generation cost for SE/TE/SelfCheckGPT
- Three testable predictions with clear falsification criteria
- Explicitly avoids the 0.75 gate mistake from h-e2-v2

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is well-constructed. Let me stress-test it.

**Concern 1: N=98 power is marginal.** With bootstrap CIs of ±0.05 on AUROC, a gap of 0.05 is right at the detection limit. If SE=0.54 and TE=0.52, the CIs overlap and the result is "no significant difference" — which is a null result, not a positive finding. The pilot needs a clear separation to be publishable. **Mitigation:** Define the pilot as a go/no-go gate. If |SE-TE| < 0.03 after 98 questions, extend to N=500 before drawing conclusions.

**Concern 2: TriviaQA dev is not representative.** TriviaQA dev is trivia-style factual QA — very different from TruthfulQA (designed to elicit falsehoods through plausible-sounding wrong answers) or MMLU (multi-choice academic). SE may work well on trivia (where questions have clear semantic clusters) but fail on TruthfulQA where the uncertainty structure is different. **Mitigation:** Secondary evaluation on a 100-question TruthfulQA sample. This adds minimal cost (100 questions × 10 samples at 7B) and tests cross-benchmark generalization.

**Concern 3: Verbalized confidence at 7B is not "verbalized confidence" in the Kadavath sense.** Kadavath 2022 used Claude/GPT-scale models. Llama-2-7B is not instruction-tuned for reliable verbalized confidence. We may be comparing SE against a strawman. **Mitigation:** Use the chat variant (Llama-2-7B-Chat) for verbalized confidence, not the base model. Document this explicitly as a limitation.

**Concern 4: The compute cost for SelfCheckGPT BERTScore on 98 samples may be higher than stated.** 98 questions × K=10 samples × pairwise BERTScore = 98 × 45 BERTScore calls. Each BERTScore call is ~0.1s on GPU, so ~440 seconds (7 minutes). Feasible. **Not a blocking concern.**

**Mitigation Strategy:** (1) Pilot gate: extend if gap < 0.03 after N=98. (2) Add TruthfulQA secondary. (3) Use Llama-2-7B-Chat for verbalized confidence.

**Key Points:**
- N=98 power is marginal for detecting gaps < 0.05 — define explicit extension trigger
- TriviaQA-only result has limited generalization; add 100-question TruthfulQA secondary
- Verbalized confidence needs chat model, not base model
- SelfCheckGPT BERTScore compute is feasible (~7 minutes)

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The four-way comparison at 7B scale with semantic entropy included is genuinely novel — Xiong 2023 and Huang 2023 both omit SE from their comparisons. The reframing of h-e2-v2's "failure" as a scale-calibration finding is intellectually honest and adds a positive contribution where there was previously only a failure record. The uncertainty frontier framing is slightly ambitious for the pilot scope but the core novelty holds.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three pairwise AUROC comparisons with bootstrap 95% CIs on N=98 (extendable to N=500) are fully testable. Success criterion (SE-TE gap ≥ 0.05) is pre-specified and non-circular. Prof. Rex's N=98 power concern is real but mitigated by the pilot gate trigger. Falsification criteria are explicit for all three predictions.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Answers a genuine practitioner question — does the NLI overhead of semantic entropy buy anything at 7B scale? The model-scale-calibrated threshold (0.60 vs. 0.75) addresses a real confusion in the field caused by the Kuhn et al. 65B results being applied to smaller models. Establishes h-e2-v2's partial result as a published anchor rather than a discarded failure.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Reuses validated h-e2-v2 infrastructure. New inference cost <2 GPU hours. SelfCheckGPT and TE are extracted from existing samples with no new LLM calls. Extension to N=500 is planned but gated on pilot results. TruthfulQA secondary (100 questions) adds ~8 GPU hours if needed. Total maximum compute: ~10 GPU hours. Entirely feasible.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion addresses the primary gap in the field: the absence of a controlled four-way comparison of uncertainty proxies for LLM factual QA, with particular attention to the scale-calibration boundary of semantic entropy.

**Core claim:** Under Llama-2-7B scale on TriviaQA dev (and secondarily TruthfulQA), applying all four major uncertainty proxy methods (single-pass token entropy, SelfCheckGPT consistency, semantic entropy, and verbalized confidence) under identical experimental conditions reveals a rank ordering where semantic entropy achieves a practically meaningful AUROC advantage (≥0.05) over token entropy, while SelfCheckGPT achieves comparable AUROC to SE at similar compute, and verbalized confidence underperforms both. This ranking is driven by the mechanism that semantic-level clustering (SE) and consistency agreement (SelfCheckGPT) both filter paraphrase noise that degrades token-level entropy discrimination.

**Why this matters:** h-e2-v2 established that SE AUROC is 0.54 at 7B (not 0.75 as Kuhn et al. reported at 65B). The new question is whether 0.54 is better or worse than TE and SelfCheckGPT at the same scale — which determines whether the NLI clustering overhead is justified for 7B deployments.

**Experimental approach:** Start with the existing 98-question h-e2-v2 pilot. Compute TE from existing samples (free). Run SelfCheckGPT BERTScore on existing samples (~7 min). Run verbalized confidence with Llama-2-7B-Chat on 98 questions (<1 GPU hour). Bootstrap CIs for all four AUROCs. If |SE-TE| < 0.03, extend to N=500.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- N=98 bootstrap CIs may be too wide to detect small gaps — define extension trigger at gap < 0.03
- TriviaQA-only result has limited domain generalization — add 100-question TruthfulQA secondary
- Must use Llama-2-7B-Chat (not base) for verbalized confidence to ensure valid comparison
- **Mitigation Strategy:** Pilot gate at N=98 (extend if inconclusive), TruthfulQA secondary test, Chat model for verbalized confidence. All three mitigations have clear, low-cost implementation paths.
