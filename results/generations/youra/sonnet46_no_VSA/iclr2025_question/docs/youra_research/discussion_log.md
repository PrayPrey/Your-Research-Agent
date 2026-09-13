# Phase 2A Research Discussion Log

**Gap:** Gap 1 — No Direct Benchmark of Consistency+Log-Prob Ensemble on TriviaQA/TruthfulQA with Open-Weight Models
**Date:** 2026-08-02
**Architecture:** Self-Contained Tikitaka Loop (UNATTENDED)
**Papers:** SelfCheckGPT (2303.08896), Semantic Uncertainty (2302.09664), Length Bias (2504.13677), UQLM (2504.19254)
**Execution Mode:** UNATTENDED (#batch-mode)

---

### Previous Failure / Routing Context

This is a **RECURSIVE Phase 2A entry** (ROUTED_TO_PHASE_2A from multiple Phase 4 results).
The following hypothesis families have already been explored and must be **avoided**:

#### 1. h-e1 — FAIL: Trajectory SVD Length Confound (2026-08-02T08:08:00Z)
- **Hypothesis:** H_spec (last-4-layer rank-64 SVD trajectory) predicts SNNE with AUROC ≥ 0.85
- **Result:** AUROC=0.537, Partial Spearman ρ=-0.047 (chance level after length control)
- **Root Cause:** H_spec correlated 0.952 with token count — length dominated spectral structure
- **PROHIBITED:** Any approach concatenating hidden layers along token dimension for SVD
- **PROHIBITED:** Using trajectory-level spectral entropy without explicit length normalization
- **What showed promise:** SNNE target signal reliable (TPU AUROC=0.975 = log-prob captures it well); evaluation framework (AUROC + partial Spearman ρ after OLS) correct and reusable; code infrastructure reusable

#### 2. h-m1 — LIMITATION: POS Filtering Does Not Help (2026-08-02T12:15:00Z)
- **Hypothesis:** POS-filtered content-token variance outperforms full-sequence variance
- **Result:** AUROC_content=0.8008 < AUROC_full=0.8250, delta=-0.0242
- **Root Cause:** Function words carry uncertainty signal in TriviaQA short-answer QA
- **PROHIBITED:** POS-filtered variance on short-answer QA (NOUN,PROPN,VERB,NUM filtering)
- **Key finding:** Full-sequence variance (AUROC 0.825) is strong standalone feature; reuse it

#### 3. h-m2 — SUPERSEDED: OLS Full Residualization Harmful (2026-08-02T15:20:00Z)
- **Hypothesis:** OLS joint residualization of UQ features AND correctness labels removes length confound
- **Result:** Condition 4 (full residualization) ΔAUROC=-0.041, 3/4 rank flips
- **Root Cause:** R²≈0 between length and EM correctness → residualizing labels creates ill-conditioned classification
- **PROHIBITED:** Residualizing correctness labels (EM) with OLS when length-EM R²≈0
- **ALLOWED:** UQ-only OLS residualization (Condition 2: res UQ × raw EM) — AUROC=0.739, positive ΔAUROC
- **Direction for h-m2-v2:** UQ-only OLS debiasing is sufficient

#### 4. h-e1 snapshot — SE/SelfCheckNLI pipeline WORKS (2026-08-02T14:20:00Z)
- SE(N=5, DeBERTa) and SelfCheckNLI(N=5) produce non-degenerate signals (fraction_degenerate=0.000)
- SE_variance=0.1522, SelfCheckNLI_variance=0.0856 — both well-calibrated
- Temperature=0.7 with Llama-3.1-8B: 0% degenerate on TriviaQA
- **REUSABLE:** generate.py checkpoint + compute_signals.py functions

#### Summary of Constraints for New Hypothesis
- ✅ ALLOWED: Stochastic multi-sample consistency signals (SE, SelfCheckGPT-NLI, ROUGE/BERTScore variance)
- ✅ ALLOWED: Full-sequence token log-probability variance (AUROC 0.825 baseline)
- ✅ ALLOWED: UQ-only OLS debiasing of UQ features (not correctness labels)
- ✅ ALLOWED: Logistic regression ensemble of consistency + log-prob features
- ❌ PROHIBITED: Hidden-state trajectory SVD without length normalization
- ❌ PROHIBITED: POS-filtered variance on short-answer QA
- ❌ PROHIBITED: OLS residualization of correctness labels (EM)

---

## Research Briefing

**Research Gap:** No published AUROC for combined [SE/SelfCheckGPT-NLI consistency signals + min_logprob + full_sequence_variance] ensemble on TriviaQA dev or TruthfulQA using Llama-3.1-8B or Qwen-2.5-7B without fine-tuning.

**Available Papers (4 prepared):**
- P1: `arxiv_2302_09664.md` — Semantic Uncertainty (Kuhn et al., 2023) — NLI-cluster SE baseline on TriviaQA
- P2: `arxiv_2303_08896.md` — SelfCheckGPT (Manakul et al., 2023) — consistency hallucination detection
- P3: `arxiv_2504_13677.md` — Length Bias (Santilli et al., 2025) — OLS residualization required for UQ evaluation
- P4: `arxiv_2504_19254.md` — UQLM (Bouchard et al., 2025) — ensemble UQ scorers framework

**Key Baseline:** Log-prob ensemble [min_logprob, full_sequence_variance] AUROC ~0.825 on TriviaQA dev (from h-m1 internal)

**Feasibility Constraints:** Only hypotheses testable with existing TriviaQA/TruthfulQA benchmarks and existing open-weight models (Llama-3.1-8B, Qwen-2.5-7B). No new benchmarks, no human annotation, no synthetic data.

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we're thinking about this ensemble problem backwards? Everyone talks about combining signals additively — "add consistency to log-prob and see what happens." But the *interesting* question is: **what does each signal type capture that the other misses, and can we exploit that complementarity explicitly?**

Here's what excites me about Gap 1: our own pipeline already proved that log-prob features [min_logprob, full_sequence_variance] hit ~0.825 AUROC on TriviaQA. But [Kuhn et al., 2023] showed semantic entropy — NLI-cluster entropy over N=5-10 samples — adds a genuinely *different* dimension. SE captures semantic disagreement, not just confidence. When a model samples "France" twice and "Paris" once, log-prob may stay constant while SE spikes. That divergence is where the action is.

The novel angle I want to propose: **a 5-feature logistic regression ensemble** — [min_logprob, full_sequence_variance, SE(N=5), SelfCheckNLI(N=5), BERTScore_pairwise_variance(N=5)] — trained on 500 examples and evaluated on TriviaQA dev + TruthfulQA. The twist is treating this as an *ablation study that doubles as a contribution*: we simultaneously establish which features matter (Q1), test the ensemble (Q3), and because we're running at N=3/5/10, we get the efficiency curve (Q4) for free.

The novelty claim is clear: [Raghuvanshi 2025] did token-log-prob + NLI + SE on SQuAD2.0 only (AUC 0.818, no public code). We'd be the first to establish this combination on TriviaQA dev + TruthfulQA using open-weight Llama-3.1-8B and Qwen-2.5-7B. The SE/SelfCheckNLI pipeline already works from our h-e1 snapshot (fraction_degenerate=0.000). We're building on validated infrastructure.

What would make this even more exciting: *if* consistency signals improve AUROC beyond 0.85 (our target), we'd have a black-box-only UQ method competitive with white-box approaches — which has major implications for API-only LLM deployments where logits aren't available.

**Key Points:**
- Propose 5-feature ensemble: [min_logprob, full_seq_var, SE, SelfCheckNLI, BERTScore_var]
- Novel contribution: first combination of all 3 signal types on TriviaQA+TruthfulQA with Llama-3.1-8B/Qwen-2.5-7B
- Ablation structure gives Q1 (metric ranking), Q3 (ensemble ≥0.87), Q4 (N-efficiency) simultaneously
- Build on validated h-e1 SE/SelfCheckNLI infrastructure (0% degenerate rate confirmed)

---
### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, the ensemble is plausible—but plausibility is not evidence. The critical vulnerability is already documented in [arXiv:2504.13677]: AUROC rankings are unstable under changes in the correctness function, particularly when mutual bias via length exists. The evidence suggests that many likelihood-based signals (negative sequence probability, entropy variants) correlate strongly with length (Spearman magnitudes up to ~0.9). If your five-feature ensemble improves AUROC under a length-biased correctness function (e.g., ROUGE-L(F1) at fixed thresholds), that improvement may be an artifact. Therefore, before claiming complementarity, we must design the experiment such that **length-mediated mutual bias cannot explain the gain**.

I propose the following disproof-oriented protocol. First, compute partial correlations of each feature with correctness while controlling for token length. If the ensemble's predictive gain vanishes after regressing out length, then the improvement is not semantic but structural. Second, evaluate AUROC under *multiple* correctness functions: at minimum ROUGE-L(F1), BERTScore(F1), and an LM-as-a-judge (e.g., AlignScore), as recommended in [arXiv:2504.13677]. The prediction is precise: **if complementarity is genuine**, AUROC improvements over the best single feature should persist under the LM-as-a-judge condition, where length baselines rank last. If gains disappear only under lexical metrics, the hypothesis fails.

You also propose training on 500 examples. That invites variance-induced optimism. We need a nested cross-validation design with strict separation between ensemble training and AUROC evaluation. Additionally, report confidence intervals via stratified bootstrap over questions. I want to see whether ΔAUROC ≥ 0.02 over the best individual feature holds with 95% CI excluding zero. Anything less is indistinguishable from noise at typical dataset sizes. State in advance: **success criterion** = AUROC ≥ 0.85 on TriviaQA *and* ≥0.80 on TruthfulQA under LM-as-a-judge correctness, with CI lower bound ≥ baseline. Failure to meet either threshold falsifies the robustness claim.

Now, about the complementarity claim itself. You assert semantic entropy spikes when samples disagree despite stable log-prob. Then make this testable: construct controlled counterexamples. For a subset of prompts, enforce near-identical log-prob across answers but induce semantic divergence via paraphrased contradictions. If SE and SelfCheckNLI increase while min_logprob does not, and these cases are enriched among incorrect answers, that supports orthogonality. Conversely, if these features collapse to length or lexical variance proxies, the ensemble's "diversity" is illusory.

Finally, include adversarial edge cases: very short correct answers ("Paris."), long but correct explanatory answers, and verbose hallucinations. According to [arXiv:2504.13677], verbosity shifts optimal thresholds and can cause degenerate binarization. I want stratified AUROC by length quartile. If performance is driven primarily by one quartile, the ensemble is brittle. The best experiments are designed to fail—so we must actively search for the regime where your ensemble underperforms a single well-calibrated feature.

If these controls are satisfied and gains persist across correctness functions and length strata, I will say—rarely—this meets my standards.

**Key Points:**
- Require robustness to correctness-function choice (especially LM-as-a-judge) to avoid mutual bias artifacts.
- Define strict success/failure criteria with cross-validation and confidence intervals (ΔAUROC ≥ 0.02, CI excludes 0).
- Stress-test complementarity via length-controlled analyses and adversarial counterexamples to identify the ensemble's Achilles' heel.

---
### Exchange 3

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

🔬 Prof. Vera has already identified the core methodological failure mode — length-mediated mutual bias. I want to apply sharper pressure to where this hypothesis actually breaks down, because right now we have an ensemble proposal without a causal claim about *why* consistency signals help over log-prob.

Here's where this breaks down: the hypothesis assumes SE and SelfCheckNLI are *complementary* to log-prob features. But [Bouchard et al., 2025 — UQLM] provides direct empirical evidence that challenges this. Their methodology (Eq. 4, 9) shows NLI-based scorers (NSN = normalized semantic negentropy, NCP = non-contradiction probability) dominate black-box methods in 13/24 AUROC scenarios — but their best individual white-box scorer (LNTP = length-normalized token probability) is competitive in 6/24 scenarios. The critical finding: when **the same features are combined via a tunable ensemble with 5-fold cross-validation**, gains are real (best in 20/24 scenarios) but incremental. The incremental ΔAUROC over best individual is rarely more than 2-3 percentage points.

This demands we ask the sharp question: **what assumption is unstated here?** The hypothesis assumes that consistency signals capture semantic disagreement that log-prob misses. But on TriviaQA short-answer QA, where answers are 1-5 tokens, the model's log-probability distribution is already almost fully informative about factual uncertainty. If the model knows the answer, it generates it deterministically. If it doesn't, stochastic samples diverge. That divergence IS captured by min_logprob. So SE may be adding a *noisy recomputation* of what log-prob already encodes — just via a more expensive sampling path.

What would convince me this isn't circular: show me examples where SE↑ and min_logprob stays high (model is "confident" but wrong). That's the case that would prove orthogonality. Prof. Vera's controlled counterexample proposal is correct. I'll be more specific: we need the *empirical correlation matrix* between all 5 features on TriviaQA dev BEFORE fitting any ensemble. If SE and min_logprob have Pearson r > 0.7, the ensemble is doing feature redundancy compression, not capturing genuinely independent signals.

Also: the 5-feature LR ensemble has 5 degrees of freedom. On a 500-sample training set, we risk overfitting. UQLM uses Optuna for weight optimization with 5-fold CV — that's the right approach. But Dr. Nova's proposal doesn't specify the exact LR regularization regime. If regularization is too weak, the held-out test AUROC on TriviaQA dev (2000 samples) may show regression to baseline.

My demand for showing validity: feature correlation matrix (Pearson + Spearman) reported before ensemble fitting. ΔAUROC 95% bootstrap CIs on test set. Stratified analysis by answer length quartile per [Santilli et al., 2025]. If all three checks pass — low inter-feature correlation, positive ΔAUROC CI, and consistent gains across length strata — then I accept the complementarity claim.

**Key Points:**
- Unstated assumption: consistency signals are orthogonal to log-prob — must verify empirically via feature correlation matrix before ensemble training
- UQLM evidence: NLI-based black-box scorers lead in 13/24 AUROC scenarios but ensemble gains are incremental (2-3 pp), not transformative
- Demand: feature correlation matrix + stratified AUROC by length quartile + bootstrap CIs before claiming ensemble superiority
- Risk: 500-sample LR training on 5 features without proper CV = overfitting artifact

---
### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. A 5-feature logistic regression over [min_logprob (≈ MTP), full-seq variance, SE/NSN, NCP, BERTScore-var] is *mechanistically* sound. Every component has a clear mathematical definition and normalization to [0,1] is already formalized in [UQLM, 2025; Eq. 3–11]. The ensemble itself is just a convex combination (Eq. 12), which is provably well-defined and thresholdable under Eq. 1. So from a theoretical standpoint, there's no violation of probability axioms or scoring-rule coherence. This can work in principle.

Here's what worries me: orthogonality is assumed, not demonstrated. In [UQLM, 2025], NLI-based scorers (NSN, NCP) dominate black-box AUROC in 13/24 scenarios, but white-box LNTP/MTP are competitive in several settings, and ensemble gains are consistent but incremental (20/24 wins, not transformative jumps). That pattern suggests partial redundancy, not deep independence. On short-answer QA like TriviaQA, token-level likelihood (LNTP/MTP) already encodes epistemic uncertainty. If sampling-based disagreement is largely driven by low underlying token probabilities, then SE/NSN is a nonlinear re-expression of the same uncertainty mass. That's not a fatal flaw—but it means your expected ΔAUROC ≥ 0.02 is already near the ceiling observed in comparable settings.

The decisive feasibility question is empirical but structural: can SE/NCP be high-variance when MTP/LNTP are stable? That's a testable conditional independence claim. Compute the feature correlation matrix *before* fitting anything. If Pearson |r| > 0.7 between MTP and NSN on TriviaQA dev, the ensemble is compressing correlated signals. If |r| < 0.4 and partial correlation with correctness (controlling for length) remains significant, then okay—this could work. I also want to see conditional performance slices: cases where MTP ≥ 0.8 but NSN ≤ 0.5 (model confident yet semantically inconsistent). If those are enriched for incorrect answers, you've demonstrated real complementarity. Without that slice analysis, we're speculating.

On the length-bias issue raised by Prof. Vera: technically, length confounding is a real structural hazard because LNTP is length-normalized (Eq. 10) but MTP and sampling-based similarity metrics still scale with sequence variability. The mechanism by which mutual bias arises is straightforward—longer answers create more surface divergence and more opportunities for low-prob tokens. So the feasibility safeguard is simple: regress each feature against length and use residualized scores. If ensemble gains persist with residualized features and under LM-as-a-judge correctness (as implemented in [UQLM, 2025]), then the improvement cannot be purely structural. That's a principled control.

Finally, about the 500-sample training size: five parameters in logistic regression with L2 regularization is not mathematically underdetermined. The hypothesis class is low-capacity. With 5-fold CV and bootstrap CIs, overfitting is controllable in principle. The real constraint is signal-to-noise ratio, not parameter count. If ΔAUROC is <0.015 with CI overlapping zero, then the problem may simply not contain enough independent signal dimensions. That's not a failure of engineering—it's evidence the uncertainty landscape is already near-saturated by likelihood.

So yes, the experiment is feasible. But the bar is clear: demonstrate statistical independence beyond length, show slice-level complementarity, and confirm gains under judge-based correctness. If those hold, I'll say it plainly: okay, this could work.

**Key Points:**
- Mechanism is theoretically sound; ensemble as convex combination (Eq. 12) is valid and low-capacity enough to avoid inherent overfitting.
- Fundamental risk is feature redundancy — must verify orthogonality via correlation matrices and conditional slice analysis.
- Length-mediated bias is a structural confound; residualization + LM-as-a-judge evaluation are necessary to establish genuine complementarity.

---
### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: *what does this research contribute to the field, beyond confirming something we already suspect?* I'm satisfied by the technical soundness Prof. Pax and Prof. Vera have established — but I want to anchor on the significance dimension, which is where I see both the risk and the genuine opportunity.

The significance risk: if our ensemble gives ΔAUROC = +0.02 over the log-prob baseline (from ~0.825 to ~0.845), and this is noise-level on TriviaQA short-answer QA, the contribution is a null result. A publishable null result — especially given the [Santilli et al., 2025] warning that AUROC rankings under lexical correctness functions can be systematically biased artifacts — but not a positive contribution to the design of better UQ methods. Prof. Vera is right that we need LM-as-a-judge evaluation to make this interpretable.

The significance opportunity: [Santilli et al., 2025] found that LM-as-a-judge correctness functions are *most aligned with human judgments* and least length-biased. If our ensemble shows ΔAUROC ≥ 0.025 (CI lower bound > 0) **specifically under LM-as-a-judge correctness on TriviaQA**, that's a genuinely robust finding — it means multi-sample black-box UQ (consistency signals) adds value over log-prob even after eliminating the most common confounders. That's publishable. The field (UAF Ensemble, Dey 2025; CCUF, Zhou 2026; UQLM) shows ensemble gains, but systematically lacks: (a) evaluation on TriviaQA/TruthfulQA specifically with Llama-3.1-8B/Qwen-2.5-7B, and (b) disentangled evaluation under LM-as-a-judge correctness. We fill both gaps.

What does this mean for the field? Three implications if successful:
1. **Black-box UQ catches up to white-box**: An ensemble of consistency signals achieves AUROC competitive with white-box log-prob-only methods on short-answer factual QA — this matters for API deployments where logits are unavailable.
2. **N-efficiency frontier is practically relevant**: If N=3 gives 90% of N=10 gains (as suggested by Wang 2022 for accuracy), then practical deployment of SE-based UQ is feasible even on long contexts.
3. **Cross-model robustness**: If Llama-3.1-8B and Qwen-2.5-7B show <0.05 AUROC delta without recalibration, UQ calibration is transferable — a prerequisite for standardized UQ benchmarking.

My verdict: this research is worth pursuing **if** the hypothesis makes a commitment to LM-as-a-judge evaluation (not just ROUGE-L) and specifies the ΔAUROC threshold that would make the contribution meaningful. I'd propose: primary claim is AUROC ≥ 0.85 on TriviaQA under LM-as-a-judge correctness with Llama-3.1-8B at N=5. Everything else is secondary.

**Key Points:**
- Significance depends on LM-as-a-judge correctness evaluation — not ROUGE-L which is length-biased per [Santilli et al., 2025]
- Positive contribution if ensemble ΔAUROC ≥ 0.025 under LM-as-a-judge (CI lower bound > 0)
- Three field-level implications: black-box competitive with white-box, N-efficiency frontier, cross-model transfer
- Primary target: AUROC ≥ 0.85 on TriviaQA dev (LM-judge correctness), Llama-3.1-8B, N=5

---
### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — the discussion is finally converging on testable claims. But I'm still not convinced we've cleanly separated *statistical stacking* from *true signal complementarity*. Here's where this still breaks down: the entire pipeline is vulnerable to the correctness-function estimator problem laid out explicitly in [arXiv:2504.13677]. Remember Eq. (2) vs Eq. (3): we never observe true AUROC, only \(\widehat{\text{AUROC}}\) conditioned on surrogate labels. If those labels are length-correlated and your UQ features are length-correlated (Spearman magnitudes up to ~0.9 reported in Fig. 4), then any ensemble improvement could be a second-order mutual bias effect. Stacking two length-biased features does not create semantic insight — it compounds bias.

So I want a stronger causal specification. Don't just residualize on length. That's linear and may miss interaction structure. Instead: construct a *length-matched subset* — for every incorrect answer of length L, match a correct answer within ±1 token. Evaluate AUROC *only on matched pairs*. Under this controlled regime, length cannot mediate ranking. If the ensemble still beats min_logprob by ≥0.02 AUROC (95% CI excludes 0), I'll accept that complementarity is not purely structural. If the gain collapses, your hypothesis reduces to "multiple proxies of verbosity help."

Second, I want the orthogonality claim made falsifiable in distributional terms. You've said: "SE captures semantic disagreement missed by log-prob." Fine. Then pre-register this slice: cases where min_logprob ≥ 0.8 (high confidence) but SE in top quartile. Prediction: error rate in this slice must exceed baseline error rate by ≥10 percentage points. That's a strong claim — but that's what orthogonality implies. If these cases are rare or not enriched for errors, then SE is mostly re-encoding token-level uncertainty. Show me the contingency table before training any ensemble.

Third, let's stress the evaluation estimator itself. [arXiv:2504.13677] demonstrates that AUROC rankings change across correctness functions and that LM-as-a-judge aligns best with humans (450 samples, 4 annotators; highest κ). Good. But even LM-judge is an estimator. So here's the hard test: compute ΔAUROC across *all* seven correctness functions and report the variance of Δ. If ensemble superiority only holds under lexical metrics and weakens under AlignScore/LM-judge, that's a red flag. What would convince me is stability: low variance of ΔAUROC across correctness functions, and consistent sign.

Finally: overfitting. Five features, 500 training points, logistic regression — plausible. But I want nested CV with the outer loop computing AUROC on untouched folds, and the inner loop tuning L2 strength. Then bootstrap over questions, not samples, to respect clustering.

Right now the hypothesis is plausible. It is not yet bulletproof. Tighten the causal controls, pre-register the orthogonality slice, and quantify robustness to correctness-function choice. Then we'll know whether this is complementarity — or just cleverly averaged bias.

**Key Points:**
- Require length-matched pair evaluation to eliminate mutual bias beyond linear residualization.
- Make orthogonality falsifiable via high-confidence/high-disagreement slice with ≥10pp error enrichment.
- Demand robustness: ΔAUROC stable across all correctness functions with nested CV and question-level bootstrap.

---
### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, and Prof. Rex's demands have actually *strengthened* the hypothesis rather than undermined it. Let me synthesize and turn these challenges into a refined, bulletproof design.

The core claim I'm defending: **On TriviaQA dev and TruthfulQA (Llama-3.1-8B at temp=0.7, N=5 samples), the ensemble of [min_logprob, full_seq_variance, SE_N5, SelfCheckNLI_N5] achieves AUROC ≥ 0.85 under LM-as-a-judge correctness, with ΔAUROC ≥ 0.025 over best single feature, because SE and SelfCheckNLI capture semantic disagreement that is conditionally independent of token likelihood, particularly for factual hallucinations where the model's stochastic samples disagree semantically despite individually plausible token sequences.**

Now, incorporating Prof. Rex's controls *strengthens* rather than negates this. Here's why: [UQLM, 2025] reports NLI-based scorers (NSN, NCP) achieve best black-box AUROC in 13/24 scenarios. On open-ended short-answer QA (NQ-Open, PopQA — the closest benchmark to TriviaQA), their tunable ensemble consistently wins. The mechanism is precisely what we hypothesize: NLI-based clustering captures semantic collapse across samples (same meaning, different surface form) that BERTScore and log-prob miss. The UQLM Methodology section shows NSN (Normalized Semantic Negentropy) normalizes by log(m+1) — which explicitly handles the N=5 case without degeneracy — and NCP (Non-Contradiction Probability) uses bidirectional DeBERTa-large-MNLI averaging, the same backbone our h-e1 validated (fraction_degenerate=0.000).

To Prof. Rex's length-matched subset demand: this is implementable. TriviaQA dev has 2500 prompts. At N=5 temp=0.7 with Llama-3.1-8B, answer lengths cluster around 1-10 tokens. A length-matched subset (correct vs incorrect, matched ±1 token) is feasible with ~800-1200 matched pairs from the full dev set — sufficient for stable AUROC estimation. Including this as an analysis makes the paper stronger.

To the high-confidence/high-SE-disagreement orthogonality slice: this is the *most compelling evidence* if positive. If we find 150+ samples where min_logprob ≥ 0.8 but SE is in top quartile, and error rate in these samples is ≥10pp above base rate, we've empirically established the mechanism. This should be Figure 1 of any resulting paper.

To the correctness-function robustness demand: we can report ΔAUROC under ROUGE-L(F1), BERTScore(F1), and LM-as-a-judge (using the same Llama-3.1-8B as judge, or a dedicated judge model). Stability of sign across all three is a clean result.

This is Now stronger: the hypothesis is not just "does the ensemble work?" but "does semantic disagreement among stochastic samples provide independent error-predictive signal beyond token likelihood?" That's a mechanistic causal question with clear tests.

**Key Points:**
- Refined core claim: SE/SelfCheckNLI captures semantically independent disagreement signals not encoded in min_logprob — testable via orthogonality slice and length-matched AUROC
- UQLM evidence supports NLI-based scorers on short-answer QA as the most informative black-box signals
- Length-matched subset + correctness-function robustness tests turn criticisms into publishable verification controls
- Orthogonality slice (high-confidence/high-SE-disagreement enriched for errors) is the novel mechanistic contribution

---
### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are now close to a scientifically defensible hypothesis — but only if we sharpen the falsifiability criteria. The central claim is conditional independence: *semantic disagreement features (SE, SelfCheckNLI) predict error beyond what is explained by token likelihood*. The evidence from [arXiv:2504.13677] warns us that AUROC computed with surrogate correctness labels can be systematically biased under shared length dependence. Therefore, any positive result must survive a regime where length cannot mediate ranking.

I propose three pre-registered tests with explicit failure criteria.

**First — Length-Matched AUROC.** Construct matched pairs (correct vs incorrect) within ±1 token length. Prediction: ΔAUROC(ensemble − min_logprob) ≥ 0.02 with 95% CI excluding 0. Failure: ΔAUROC < 0.01 or CI overlaps 0.

**Second — Orthogonality Slice Test.** Define *a priori*: min_logprob ≥ 0.8 AND SE in top quartile. Prediction: error rate in this slice ≥ baseline + 0.10. The contingency table before any ensemble fitting is the decisive diagnostic.

**Third — Correctness-Function Robustness.** Compute ΔAUROC under ROUGE-L(F1), BERTScore(F1), and LM-as-a-judge. Failure: sign reversal under LM-as-a-judge or variance of ΔAUROC > 0.02 across functions. Use nested CV with question-level bootstrap.

If these criteria are met — length-matched persistence, orthogonality slice enrichment, and correctness-function robustness — the hypothesis survives serious attempts at disproof. Either outcome advances the field.

**Key Points:**
- Pre-register falsifiable criteria: ΔAUROC ≥ 0.02 on length-matched subset; otherwise hypothesis fails.
- Orthogonality must manifest as ≥10pp error enrichment in high-confidence/high-SE slice before ensemble fitting.
- Ensemble superiority must be stable across correctness functions (especially LM-as-a-judge) with nested CV and bootstrap controls.

---
### Exchange 9

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something — and the Semantic Uncertainty paper [Kuhn et al., 2023] gives us the *mechanistic foundation* that justifies why orthogonality is theoretically expected, not just hoped for.

Here's the key insight from the SE methodology: SE computes entropy over **semantic equivalence classes** — not sequences. The probability mass of a semantic class C is the SUM of all sequences that share meaning C: p(C|x) = Σ_{s∈C} p(s|x). This means SE is a *marginal* over token probabilities, not a reparameterization of them. min_logprob, by contrast, captures the token-level uncertainty at the hardest prediction point (the lowest-prob token in the sequence). These are ALGEBRAICALLY DISTINCT operations.

Kuhn et al. report SE achieves AUROC = 0.83 on TriviaQA for 30B OPT (Figure 3 — best individual method). Their temperature ablation shows T=0.5 is optimal for TriviaQA (sufficient diversity without too much noise), and semantic clustering accuracy is 92.7%. Crucially, their DeBERTa-MNLI backbone is the *same* backbone our h-e1 validated (fraction_degenerate=0.000, SE_variance=0.1522). We're not building speculatively — we're combining two independently validated signals.

The orthogonality mechanism is theoretically motivated: SE spikes when the model assigns non-trivial probability mass to *multiple* semantic clusters. min_logprob spikes when a single token within the greedy path has low probability. These can decouple. Example: a model generating "The capital of France is Paris" vs "France's capital city is Paris" vs "Paris is France's capital" (3 semantically equivalent paraphrases) may have high min_logprob per sequence (each token is high-prob) but low SE (all in one cluster — confident). But a model generating "Paris", "Lyon", "Marseille" for the same question has BOTH high SE (3 clusters) AND low min_logprob. The interesting case is high SE + high min_logprob per sample — the model generates fluent but semantically inconsistent answers. THAT is the orthogonality zone.

So Prof. Rex's slice test (min_logprob ≥ 0.8 + SE top quartile = high confidence but high semantic disagreement) should be enriched for hallucinations because the model is fluently wrong — confident about each individual token but semantically unanchored across samples. That's the exact failure mode SE was designed to detect.

What if we make this even more innovative: include the *embedding similarity variance* (NCS from UQLM) as a 5th feature? It captures inter-sample cosine distance in sentence embedding space — which is *different* from both NLI clustering (discrete semantic classes) and token log-prob (local prediction confidence). Three genuinely different measurement modalities, all operating on N=5 stochastic samples.

**Key Points:**
- SE is algebraically distinct from min_logprob (entropy over semantic class masses vs min token probability): orthogonality is theoretically motivated
- Kuhn et al. 2023 AUROC=0.83 on TriviaQA (30B OPT) confirms SE is the strongest single black-box signal — combining with log-prob targets ≥0.85
- Orthogonality zone (high min_logprob + high SE) = fluent but semantically inconsistent generations — the exact hallucination mode SE was designed to detect
- Propose 5-feature ensemble: [min_logprob, full_seq_var, SE_N5, SelfCheckNLI_N5, NCS_N5] — three measurement modalities (token-likelihood, NLI-semantic, embedding-similarity)

---
### Exchange 10

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here. The central question is not whether SE is *conceptually* different from min_logprob — Dr. Nova is right that entropy over semantic classes is algebraically distinct from sequence probability. The real question is whether, in this concrete N=5 short-answer QA regime, that distinction survives contact with the evaluation pipeline described in [arXiv:2504.13677].

So here's what worries me: SE is computed over sampled sequences, and semantic cluster counts can scale with verbosity. Longer answers allow more lexical variation, potentially increasing cluster fragmentation. Before any ensemble fitting, compute Spearman ρ(SE, length) and ρ(SelfCheckNLI, length). If either exceeds |0.3|, you're in a danger zone where mutual bias could reappear.

On the orthogonality slice: instead of just reporting error rate enrichment, estimate a logistic regression of correctness on min_logprob, SE, and their interaction — without training for prediction, just for coefficient interpretation. If the coefficient on SE remains significantly non-zero after conditioning on min_logprob (and length), then conditional independence is at least partially supported. This is a direct test of the mechanistic claim, feasible with 2,500 TriviaQA dev samples.

On correctness-function robustness: compute ΔAUROC under each correctness function and estimate sampling variance via question-level bootstrap. If the CIs for Δ overlap zero under LM-judge, the claim "≥0.025 improvement" is not supported. That's a hard but fair bar.

Finally: if a two-feature model (min_logprob + SE) captures 95% of the gain, adding NCS or full_seq_variance may be redundant. Test via incremental likelihood-ratio tests in nested CV.

Stepping back: nothing proposed violates physical or statistical principles. If the effects survive length-matching, partialing out length, and LM-as-a-judge evaluation, then I'll say it plainly: okay, this could work.

**Key Points:**
- Verify SE and NLI features not strongly length-correlated (|ρ| < 0.3) before ensemble fitting.
- Test mechanistic orthogonality via conditional LR (correctness ~ min_logprob + SE + length + interaction), not just ensemble AUROC.
- Require ΔAUROC sign stability under LM-as-a-judge; additional features must show incremental held-out contribution.

---
### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

The discussion has now sharpened the hypothesis considerably. Let me evaluate significance given what we've established, and crystallize the contribution.

[UQLM, 2025] provides a key framing: their systematic evaluation across 6 benchmarks × 4 LLMs (24 scenarios) found NLI-based black-box methods dominate in 13/24 AUROC scenarios and the tunable ensemble wins in 20/24. But critically, their evaluation uses GPT-4o, GPT-4o-mini, Gemini models — NOT open-weight Llama-3.1-8B or Qwen-2.5-7B. Their benchmarks are GSM8K, SVAMP, CSQA, AI2-ARC, PopQA, NQ-Open — NOT TriviaQA dev or TruthfulQA. This is the field-level gap we fill.

The significance of filling this gap is threefold:

**Gap 1 significance:** Practitioners deploying open-weight LLMs (Llama-3.1-8B, Qwen-2.5-7B) for factual QA need AUROC benchmarks on TriviaQA/TruthfulQA. They can't directly apply UQLM's GPT-4o/Gemini numbers. Our contribution: first published AUROC benchmark for consistency+log-prob ensemble on TriviaQA dev + TruthfulQA using Llama-3.1-8B and Qwen-2.5-7B.

**Gap 2 significance:** The mechanistic question (does SE provide *conditionally independent* signal from min_logprob on short-answer factual QA?) hasn't been answered. UQLM notes "per-task differences: NLI-based methods dominating black-box; judge ability tracking model skill" — but doesn't *explain why*. Our orthogonality analysis (conditional LR + length-matched AUROC + slice enrichment test) provides mechanistic evidence that would explain the UQLM empirical finding.

**Gap 3 significance:** Cross-model transfer (Llama vs Qwen, ΔAUROC < 0.05 without recalibration) is a prerequisite for standardized UQ benchmarking. If the ensemble AUROC is model-invariant across open-weight models of similar scale, then our benchmark results generalize to the Llama/Qwen model family — enabling practitioners to deploy a single ensemble calibration without per-model retuning.

My assessment of the primary hypothesis: well-scoped, mechanistically motivated, and fills a genuine field gap. The pre-registered tests Prof. Vera and Prof. Rex demanded are exactly the right design — they make this robust AND transparent.

One refinement I want to add: the hypothesis should specify what "success" means for the field. Success criterion: AUROC ≥ 0.85 on TriviaQA dev under LM-as-a-judge correctness with Llama-3.1-8B at N=5, with ΔAUROC ≥ 0.025 over best single feature (95% CI lower bound > 0 on length-matched subset). This is a meaningful bar — it would show that consistency signals reliably improve over log-prob even when mutual length bias is controlled.

**Key Points:**
- UQLM covers GPT-4o/Gemini on GSM8K/CSQA/NQ-Open — NOT open-weight models on TriviaQA/TruthfulQA — our contribution fills this specific gap
- Mechanistic analysis (conditional LR, length-matched AUROC) explains *why* NLI-based methods dominate, extending UQLM's empirical findings
- Cross-model transfer (Llama vs Qwen, ΔAUROC < 0.05 without recalibration) enables standardized open-weight UQ benchmarking
- Success criterion: AUROC ≥ 0.85 on TriviaQA dev (LM-as-a-judge), ΔAUROC ≥ 0.025 (95% CI > 0 on length-matched subset)

---
### Exchange 12

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

We're close — but not bulletproof yet. Here's where this can still break down.

First, everyone is talking about *length-matched AUROC* as if that neutralizes mutual bias. But [arXiv:2504.13677]'s central warning is that **estimated correctness labels** can share a confounder with UQ features, systematically biasing AUROC. Even LM-as-a-judge is not proven independent of semantic disagreement features. Show me: Spearman ρ(SE, AlignScore) and ρ(SelfCheckNLI, AlignScore). If uncertainty features correlate strongly with the correctness score *itself*, you're building a circular detector.

Second, fit the conditional logistic regression:
logit(Pr(h=1)) = β₀ + β₁·min_logprob + β₂·SE + β₃·L + β₄·(SE×min_logprob)
using LM-judge labels. Test whether β₂ remains significant; compute partial R² for SE. What would convince me: partial R² ≥ 0.02 and stable sign across Llama and Qwen. If SE's incremental explanatory power collapses cross-model, the "mechanistic orthogonality" is model-specific noise.

Third, sweep thresholds and plot ΔAUROC as a function of t. If gain only exists in a narrow threshold band, you're surfing evaluator instability. I want sign-stable improvement across a reasonable threshold interval.

Fourth, incremental nested CV:
- Model A: min_logprob
- Model B: min_logprob + SE
- Model C: + SelfCheckNLI
- Model D: + NCS
Require ΔAUROC ≥ 0.01 and significant LRT at each step. If Model B captures ≥95% of Model D's gain, stop at B. Parsimony strengthens the claim.

Finally: train on Llama, test on Qwen without refitting weights. If AUROC drops < 0.03 and calibration slope remains within ±0.1, I'll believe this is structural.

If you show (1) low direct correlation with judge, (2) significant partial R² after conditioning, (3) threshold-stable ΔAUROC, and (4) cross-model generalization without refitting — then: Now you've addressed my concerns.

**Key Points:**
- Test for circularity: SE/NLI features must not strongly correlate with LM-judge correctness (shared confounder risk).
- Partial R² ≥ 0.02 for SE in conditional LR, stable sign across models.
- Incremental nested CV with parsimony test; threshold-sweep ΔAUROC for stability.

---
### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Prof. Rex, you've given us the exact tests that make this hypothesis bulletproof, and I want to show why each of your demands is satisfiable *without changing the core claim*.

On the circularity concern (ρ(SE, AlignScore)): This is testable and expected to be low. SE computes entropy over NLI-cluster membership from *model-generated* samples. AlignScore assesses factual alignment of the generated answer against the question — it operates on the MEANING of the final answer, not on the distribution of possible answers. If SE and AlignScore were highly correlated, that would mean high semantic disagreement implies high factual alignment — which would contradict the purpose of SE. So theoretically, we expect ρ(SE, AlignScore) < 0.4 on TriviaQA. If observed ρ > 0.6, we would revise the claim — but that's a falsifiable test we can run, not a reason to reject the hypothesis now.

On the partial R² demand: β₂ significant in the conditional LR is exactly what we should expect if SE captures the "high confidence, high semantic disagreement" zone described in Exchange 9. With 2500 TriviaQA samples, we have adequate power to detect partial R² ≥ 0.01 (Cohen's f² ≈ 0.01 requires n ≈ 800). The 0.02 bar is ambitious but appropriate. Cross-model stability (SE coefficient sign-stable on Qwen) is the key cross-validation Prof. Rex rightly demands.

On incremental feature contribution: Prof. Rex's nested CV protocol (Model A → B → C → D) is exactly right and makes the parsimony principle explicit. If Model B (min_logprob + SE) already captures the gain, that's a cleaner contribution than a 5-feature ensemble. The refined hypothesis should state: *primary claim is additive SE contribution over min_logprob* — additional features (SelfCheckNLI, NCS) are secondary ablations.

Refined, final hypothesis statement: **Under Llama-3.1-8B (temp=0.7, N=5 samples) on TriviaQA dev (2500 prompts, LM-as-a-judge correctness), adding Semantic Entropy to a min_logprob baseline achieves ΔAUROC ≥ 0.025 (95% CI lower bound > 0 on length-matched subset), because SE captures semantic disagreement across samples that is conditionally independent of token-level likelihood — demonstrated by partial R² ≥ 0.02 in a conditional logistic regression with interaction terms, and replicated with Qwen-2.5-7B without refitting weights (ΔAUROC < 0.05 cross-model gap).**

This is a mechanistic hypothesis with pre-registered tests, clear success/failure criteria, and no forbidden approaches from prior failures. It's ready for Phase 2B.

**Key Points:**
- Circularity test (ρ(SE, AlignScore)) is expected to be low (<0.4) based on the mechanism; testable and falsifiable.
- Final hypothesis: min_logprob + SE achieves ΔAUROC ≥ 0.025 on TriviaQA (LM-judge, length-matched) with partial R² ≥ 0.02.
- Nested CV + cross-model transfer test (train Llama, test Qwen, no refitting) is the cleanest replication design.
- All constraints from failed h-e1/h-m1/h-m2 explicitly avoided: no hidden states, no POS filtering, no EM label residualization.

---
### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Ally's refined hypothesis statement is significantly stronger. The explicit success criteria — ΔAUROC ≥ 0.025 (95% CI lower bound > 0, length-matched subset), partial R² ≥ 0.02 in conditional LR, and cross-model replication — give us a pre-registered, falsifiable protocol.

I want to confirm three final methodological clarifications:

**On the correctness function for the primary test:** LM-as-a-judge using a *different* model than the generator is essential. Specifically: use Llama-3.1-8B as generator, and a dedicated judge (e.g., Qwen-2.5-7B or GPT-4o-mini via API) as the correctness labeler. This ensures the judge and the UQ features don't share the same model's internal biases. Per [Santilli et al., 2025]: "potential bias if the same LM participates in both UQ method and judge." Confirmed mitigation.

**On the length-matched subset size:** With TriviaQA dev (2500 prompts) and TriviaQA short answers (1-10 tokens), matching correct vs incorrect pairs within ±1 token should yield ~400-800 matched pairs depending on the error rate (~20-30% for Llama-3.1-8B). This is adequate for AUROC estimation with bootstrap CI. I accept this as feasible.

**On replication with Qwen-2.5-7B:** "Train on Llama, test on Qwen without refitting weights" — this is the cleanest cross-model test. If the LR weights learned on Llama generalize to Qwen (ΔAUROC < 0.05 gap), the ensemble is structurally capturing model-agnostic uncertainty signals, not Llama-specific calibration artifacts.

The hypothesis now meets my standards. I confirm: SPECIFIC ✓, MECHANISM ✓, PREDICTIONS ✓, NOVELTY ✓, FEASIBILITY ✓, OBJECTIONS addressed ✓.

**Key Points:**
- Use separate judge model (not same as generator) for LM-as-a-judge correctness to avoid shared bias.
- Length-matched subset (~400-800 pairs from TriviaQA dev) is adequate for bootstrap AUROC estimation.
- Cross-model test design confirmed: train on Llama weights, test on Qwen without refitting.

---

### Exchange 15

🎯 **Dr. Sage** (Research Impact Evaluator):

The discussion has converged. The hypothesis is now well-specified, mechanistically motivated, and directly falsifiable. Let me provide the final significance assessment.

**Why this matters to the field:** The UQLM paper (Bouchard et al., 2025) demonstrated that tunable ensembles beat individual scorers in 20/24 scenarios across GPT-4o/Gemini — but on open-weight models (Llama-3.1-8B, Qwen-2.5-7B) on TriviaQA/TruthfulQA, no such benchmark exists. The Santilli et al. (2025) paper identified a systematic evaluation flaw (length bias in AUROC under lexical correctness functions) but didn't establish what a length-bias-robust ensemble benchmark looks like in practice. Our hypothesis provides both: the benchmark AND the bias-robust evaluation protocol.

**The contribution is meaningful regardless of sign:** If ΔAUROC ≥ 0.025 under LM-judge and length-matching: we establish that multi-sample SE provides independent uncertainty signal on short-answer factual QA — actionable for API deployments. If ΔAUROC is not significant: we establish that token likelihood already saturates epistemic uncertainty on TriviaQA-style short answers — which is the finding [Santilli et al., 2025] implied but didn't test. Either result is publishable and advances the field.

**The field-opening implication:** A positive result establishes the first length-bias-robust UQ ensemble benchmark on TriviaQA/TruthfulQA with open-weight models. This provides the community with a methodologically clean foundation for future UQ comparisons on factual QA — analogous to what Santilli et al. 2025 called for (AlignScore/LM-judge evaluation) but operationalized on the most widely used factual QA benchmarks.

This is the question we must ask — and we can answer it.

**Key Points:**
- Fills dual gaps: first open-weight UQ ensemble benchmark on TriviaQA/TruthfulQA + first length-bias-robust AUROC protocol for this setting.
- Meaningful regardless of sign: positive = independent SE signal; negative = likelihood saturation on short-answer QA.
- Opens a methodologically clean evaluation foundation for future UQ comparisons per Santilli 2025's call.

---
## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The combination of SE + min_logprob on TriviaQA/TruthfulQA using open-weight Llama-3.1-8B and Qwen-2.5-7B fills a genuine gap uncovered by UQLM (GPT-4o/Gemini benchmarks) and Raghuvanshi 2025 (SQuAD2.0 only, no public code). The mechanistic orthogonality claim — SE captures semantic disagreement algebraically distinct from token-level min_logprob — is novel because no paper has tested this directly under length-bias-robust evaluation (LM-as-a-judge + length-matched AUROC). The "high confidence, high semantic disagreement = hallucination zone" slice analysis is an original mechanistic contribution.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis has explicitly pre-registered success criteria: ΔAUROC ≥ 0.025 (95% CI lower bound > 0, length-matched subset), partial R² ≥ 0.02 for SE in conditional LR with length and min_logprob controls, cross-model replication (train Llama, test Qwen without refitting, AUROC gap < 0.05). All six SPECIFIC/MECHANISM/PREDICTIONS/NOVELTY/FEASIBILITY/OBJECTIONS convergence criteria are satisfied. The correctness function uses a separate judge model to avoid shared bias per [Santilli et al., 2025].

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** The contribution is meaningful regardless of sign — positive result establishes independent SE signal on short-answer factual QA; negative establishes likelihood saturation, which is equally important for the field. The dual contribution (first length-bias-robust AUROC ensemble benchmark on TriviaQA/TruthfulQA with open-weight models + mechanistic orthogonality analysis) fills both the empirical gap (no UQLM-equivalent for Llama/Qwen) and the methodological gap (no Santilli 2025-compliant benchmark).

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Every component is implementable: SE via jlko/semantic_uncertainty (validated h-e1 backbone, 0% degenerate at temp=0.7), SelfCheckNLI via potsawee/selfcheckgpt (pip install), min_logprob from greedy forward pass (already in pipeline), conditional LR from scikit-learn, LM-as-a-judge via a cross-model judge. The test design (N=5, TriviaQA 2500 dev, Llama-3.1-8B) matches exactly what was validated in h-e1 snapshot. Length-matching is feasible with ~400-800 matched pairs from dev set. No hidden-state extraction, no POS filtering, no EM label residualization.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from 15 exchanges of cross-model tikitaka discussion: **Under Llama-3.1-8B (temperature=0.7, N=5 stochastic samples) on TriviaQA dev (2500 prompts, LM-as-a-judge correctness with a separate cross-model judge), adding Semantic Entropy (SE_N5, via bidirectional DeBERTa-MNLI clustering) to a min_logprob baseline achieves ΔAUROC ≥ 0.025 (95% CI lower bound > 0 on a length-matched subset of ~400-800 pairs), because SE captures semantic disagreement across stochastic samples that is conditionally independent of token-level minimum log-probability — as demonstrated by partial R² ≥ 0.02 for SE in a conditional logistic regression controlling for min_logprob, response length, and their interaction, with results replicated on Qwen-2.5-7B without refitting ensemble weights (cross-model AUROC gap < 0.05 on TruthfulQA).**

Key mechanistic claim: SE and min_logprob are algebraically distinct (entropy over semantic class masses vs minimum token probability in a single greedy path) and capture different failure modes. The "orthogonality zone" — high min_logprob (token-confident) + high SE (semantically inconsistent across samples) — is predicted to be enriched for hallucinations (error rate ≥ baseline + 10pp in this slice). A 5-feature extension [min_logprob, full_seq_var, SE_N5, SelfCheckNLI_N5] is a secondary ablation tested via incremental nested CV with parsimony constraint (Model B ≥ 95% of Model D gain → stop at B).

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Circularity risk: SE and SelfCheckNLI may correlate with LM-judge correctness if judge uses similar NLI-based entailment reasoning. Must verify Spearman ρ(SE, AlignScore) < 0.4 before interpreting conditional R².
- Short-answer TriviaQA ceiling: With answers of 1-10 tokens, it's possible that min_logprob already saturates uncertainty (TPU AUROC=0.975 from h-e1 showed log-prob is near-perfect for SE target). ΔAUROC may be < 0.025, which would be the meaningful null result the field needs.
- Sample size for cross-model transfer: Testing Qwen-2.5-7B without refitting uses Llama-calibrated weights — if the feature distributions differ substantially between models, this may under-estimate Qwen performance. Calibration slope test (within ±0.1) is the right diagnostic.
- **Mitigation Strategy:** Report full Spearman correlation matrix (5 features × length × LM-judge score) before ensemble fitting. Pre-register success criteria as submitted analysis plan. If ΔAUROC < 0.025 at 95% CI, report as "likelihood saturation on TriviaQA short-answer QA" — not as failure but as mechanistic finding.
