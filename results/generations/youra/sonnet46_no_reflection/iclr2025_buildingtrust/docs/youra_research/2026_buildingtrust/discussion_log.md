# Phase 2A Discussion Log
**Gap ID:** gap1
**Gap Title:** No Systematic Cross-Benchmark Predictive Correlation Study for LLM Failure Modes
**Initialized:** 2026-05-12
**Architecture:** Self-Contained Tikitaka Loop v9.0.0
**Execution Mode:** UNATTENDED

---

## Briefing Context

### Research Gap
No existing study computes whether robustness fragility (AdvGLUE/ANLI scores) statistically predicts failure mode severity (ECE, hallucination rate, safety failure rate) across a common model set. DecodingTrust covers 8 dimensions independently but does not compute predictive correlations between them. TrustLLM benchmarks multiple dimensions but reports scores independently.

**Missing Piece:** A unified analysis that:
1. Collects existing benchmark scores across robustness, calibration, hallucination, fairness, and safety dimensions for a common set of models
2. Computes pairwise Spearman/Pearson correlations between dimensions
3. Tests whether robustness fragility scores are statistically predictive of failure mode severity

### Key Papers Available
- DecodingTrust (2306.11698, 2023, 621 citations) — 8-dim trustworthiness evaluation of GPT models, does NOT compute inter-dimension predictive correlations
- TruthfulQA (2109.07958, 2021, 3233 citations) — Inverse scaling finding: larger models LESS truthful
- HaluEval (2305.11747, 2023, 433 citations) — ChatGPT produces ~19.5% hallucinated content
- AdvGLUE (2111.02840, 2021, 294 citations) — Core adversarial NLP robustness benchmark; models lag 20-30% behind benign accuracy
- Know Thy Judge (2503.04474, 2025, 13 citations) — Style changes cause +0.24 FNR jump in safety judges

### Key Repos
- HowieHwong/TrustLLM (622 stars) — Multi-dimension trustworthiness scores for 16 LLMs
- ctlllll/understanding_llm_benchmarks (29 stars) — Spearman correlation methodology between benchmark scores
- EleutherAI/lm-evaluation-harness (12505 stars) — Primary evaluation harness
- microsoft/PromptBench (2799 stars) — Unified adversarial robustness evaluation

### Feasibility Constraints (MANDATORY)
- ✅ Only existing benchmarks (AdvGLUE, ANLI, TruthfulQA, HaluEval, WinoBias, BBQ, ToxiGen, HarmBench)
- ✅ No new benchmarks or scoring frameworks
- ✅ No synthetic/generated data
- ✅ No human evaluation or annotation
- ✅ Testable immediately with existing datasets and models

### Research Question
Do existing LLM robustness evaluation benchmarks reveal systematic performance degradation patterns that are predictive of downstream failure modes in real-world deployments, characterizable using only existing evaluation datasets?

---

## Discussion Exchanges

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been looking at these benchmarks like isolated weather stations… when what we really need is a climate map?

Right now, AdvGLUE, ANLI, TruthfulQA, HaluEval, WinoBias, BBQ, and HarmBench are treated as separate diagnostics. But imagine this: robustness fragility isn't just "one more metric"—it might be a *latent instability coefficient* that manifests differently depending on task framing. AdvGLUE shows 20–30% drops under adversarial perturbation [Wang et al., 2021]. TruthfulQA reveals inverse scaling in truthfulness [Lin et al., 2021]. HaluEval reports ~19.5% hallucination in ChatGPT outputs [Li et al., 2023]. What if these are not separate pathologies—but phase transitions of the same underlying brittleness?

NOW we're onto something if we treat robustness score as a *stress test proxy* for epistemic stability. Here's a concrete move within our constraints: assemble a model matrix (e.g., the 16 models in TrustLLM) and compute cross-dimension Spearman correlations between adversarial robustness (AdvGLUE/ANLI) and:
- Calibration error (ECE where available)
- Hallucination rate (HaluEval)
- Truthfulness score (TruthfulQA)
- Safety failure (HarmBench/ToxiGen refusal accuracy)
- Bias gaps (WinoBias, BBQ)

But let's go further. What if the relationship is *nonlinear*? Suppose robustness doesn't correlate linearly with hallucination—but below a certain robustness threshold, hallucination spikes dramatically. That's a phase boundary hypothesis. We can test this immediately by fitting segmented regression or computing rank-order clusters. If low-robustness models cluster with high hallucination + high bias + poor calibration, we've identified a "failure basin." That's not just correlation—that's a structural regime.

Cross-domain connection time: in control theory, systems near instability exhibit *coupled error amplification*. A small perturbation increases variance across multiple output channels. Translate that to LLMs: adversarial vulnerability may signal that the internal representation geometry is overly sharp or miscalibrated. Under distribution shift (ANLI), the same instability could manifest as hallucination (fabricating structure) or safety misclassification (Know Thy Judge shows style shifts cause +0.24 FNR jumps). The prediction? Models with larger adversarial drops should also show higher sensitivity to prompt style in safety benchmarks. That's a directly testable hypothesis using PromptBench + HarmBench.

And here's the paradigm shift: instead of asking "Does robustness predict hallucination?", we ask: *Is robustness fragility the earliest observable symptom of multi-dimensional trust collapse?* If so, robustness benchmarks could function as low-cost screening tools for downstream deployment risk. That reframes AdvGLUE and ANLI from academic stress tests into predictive diagnostics.

We don't need new data. We need a new lens. A correlation matrix is step one. A clustered instability profile is step two. A thresholded phase transition analysis is step three. If the pattern holds, we've discovered something foundational: trust dimensions aren't independent—they're coupled through shared representational fragility.

**Key Points:**
- Treat robustness fragility as a latent instability coefficient that may predict multi-dimensional failure modes.
- Test for nonlinear "phase boundary" effects and clustered failure basins using only existing benchmark scores.
- Reframe adversarial robustness benchmarks as early-warning diagnostics for downstream trust collapse.

---

### Exchange 2

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Nova's "climate map" metaphor is evocative — and I want to stress-test it carefully before we get carried away. Let me be direct: the core scientific question is sound, but several mechanism claims need grounding.

First, the good news. The proposed analytical pipeline is technically valid: collecting existing benchmark scores from TrustLLM (16 LLMs across 8 dimensions), AdvGLUE, TruthfulQA, and HaluEval, then computing pairwise Spearman rank correlations is a well-established statistical procedure requiring no new infrastructure. The ctlllll/understanding_llm_benchmarks repository already demonstrates this exact pattern — Spearman correlations between benchmark scores achieve 0.94 correlation with human Elo using just 2 LASSO-selected benchmarks. That's strong existence proof that the cross-benchmark correlation approach is methodologically sound.

However, here's what worries me about the "latent instability coefficient" framing. Dr. Nova is positing a single underlying factor driving correlated failure across dimensions. That's a testable claim — but we should not assume it before running the analysis. The TruthfulQA inverse scaling finding [Lin et al., 2021] already provides a *counterexample*: larger, more capable models score worse on truthfulness despite scoring better on robustness benchmarks. If robustness and truthfulness are *negatively* correlated at scale, there is no single instability coefficient — there are at least two orthogonal failure modes. The PCA result that 6 standard benchmarks collapse to 2 principal components (97.4% variance explained) is suggestive but was computed on general capability benchmarks, not robustness-to-failure-mode correlations specifically.

The phase boundary / nonlinear threshold hypothesis is theoretically interesting but scientifically premature. Can it work in principle? Yes — segmented regression and rank-order clustering are valid methods. But proposing this as the *main* hypothesis before establishing whether linear correlation even exists would be putting the cart before the horse. The scientifically sound sequence is: (1) compute linear Spearman correlations across all dimension pairs, (2) examine residuals for nonlinearity, (3) only then test threshold/phase boundary models. Skipping step 1 would be a fundamental methodological error.

What I would endorse as technically sound and immediately testable: a focused hypothesis that AdvGLUE adversarial accuracy drop correlates positively with ECE (calibration error) across a fixed model set — specifically the 16 LLMs evaluated in TrustLLM, using the verified_calibration library for ECE computation. This is narrow, falsifiable, and fully executable with existing data. If that correlation holds, we extend to hallucination rate and safety failure in subsequent sub-hypotheses. If it doesn't, we've learned something equally valuable.

**Key Points:**
- The Spearman correlation pipeline is technically valid and precedented (ctlllll/understanding_llm_benchmarks).
- The "single latent instability" assumption must be tested not assumed — TruthfulQA's inverse scaling is a live counterexample.
- The scientifically grounded entry point: AdvGLUE adversarial drop vs. ECE correlation across the TrustLLM model set.

---

### Exchange 3

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova's "latent instability coefficient" is a legitimate scientific hypothesis — but at present it is only a metaphor. The evidence suggests we can translate it into a falsifiable latent-factor model. Formally: there exists a single latent variable I such that variation in adversarial robustness (AdvGLUE/ANLI drop), hallucination rate (HaluEval), calibration error (ECE), truthfulness (TruthfulQA), safety failure (HarmBench), and bias gaps (BBQ/WinoBias) loads significantly and coherently onto I across models. What would disprove this? If exploratory factor analysis (EFA) reveals two or more orthogonal factors with comparable eigenvalues, or if loadings have inconsistent signs (e.g., robustness positively loads while truthfulness negatively loads), then the "single instability" construct collapses.

I agree with Prof. Pax that we must begin with linear structure before invoking nonlinear phase boundaries. Step 1: compute a full Spearman correlation matrix across the shared model set (e.g., the 16 TrustLLM models). Pre-register directional predictions: (H1) greater adversarial accuracy drop correlates with higher ECE; (H2) greater adversarial drop correlates with higher hallucination rate; (H3) greater adversarial drop correlates with higher safety failure rate. Success criterion: ρ ≥ 0.5 with p < 0.05 (Holm-corrected). Failure criterion: |ρ| < 0.2 or inconsistent sign across datasets. Only if at least two of three survive correction do we proceed to latent-factor modeling.

Now, the TruthfulQA inverse scaling result [Lin et al., 2021] is not a nuisance — it is the critical stress test. If robustness improves with scale while truthfulness degrades, then either (a) truthfulness measures a distinct construct, or (b) capability is a confounder mediating both. We must therefore control for model size or aggregate capability (e.g., average of standard benchmarks) via partial correlation. The key question: does adversarial fragility predict hallucination *after controlling for capability*? If the correlation vanishes under control, then instability is merely a proxy for general weakness. If it persists, we have evidence of a distinct structural vulnerability.

Regarding the nonlinear "phase boundary" claim: this is testable, but the burden of proof is high. A segmented regression must outperform a linear model under cross-validated RMSE, not merely fit visually. Predefine the comparison: linear vs. one-breakpoint piecewise regression; accept nonlinearity only if ΔAIC ≥ 10 or cross-validated error improves ≥10%. Otherwise, we reject the phase-transition framing. The best experiments are designed to fail; if instability is continuous rather than thresholded, we should detect that.

Finally, we must anticipate edge cases. Instruction-tuned models may exhibit strong adversarial robustness yet poor calibration due to overconfident alignment training. Safety-tuned models may show low HarmBench failure but high hallucination because refusal masks epistemic weakness. These dissociations would falsify the "coupled error amplification" analogy from control theory. I would explicitly test for such cluster separations via hierarchical clustering with bootstrapped stability. If clusters are unstable across resampling, the climate-map narrative dissolves.

If — and only if — a single latent factor emerges, remains after controlling for capability, and improves predictive accuracy for unseen trust metrics, then I will say: *This meets my standards.*

**Key Points:**
- Reformulate "latent instability" as a falsifiable latent-factor model with predefined success/failure criteria.
- Control for capability to rule out confounding before attributing correlations to structural instability.
- Require cross-validated evidence before accepting nonlinear phase-boundary claims.

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Prof. Vera has done excellent work formalizing the latent-factor framing — but I want to push harder on the assumptions that are quietly doing heavy lifting here. Here's where this breaks down if we're not careful.

The model set problem is the elephant in the room. The 16 TrustLLM models are not a random sample — they are a convenience sample of prominent API-accessible LLMs with strong capability profiles. If we find ρ = 0.6 between AdvGLUE drop and ECE on this set, what would convince me that result generalizes? We need coverage across: (1) model families (GPT-series, LLaMA-series, Mistral, Falcon), (2) scales (7B to 175B+), (3) training regimes (pretrained-only, RLHF-tuned, instruction-tuned, safety-tuned). The TrustLLM 16-model set has systematic selection bias toward frontier models. If the correlation only holds for large frontier models and breaks for smaller open-source models, we've found a scale artifact, not a structural vulnerability. Show me evidence the model sample is representative before I accept any correlation finding.

Second: the benchmark contamination threat that Xu et al. [2024] raised is not a minor methodological footnote — it is potentially lethal to this entire study design. If GPT-4 has seen AdvGLUE examples during pretraining, its "adversarial accuracy drop" is not measuring robustness — it is measuring memorization leakage. The same concern applies to TruthfulQA (publicly available since 2021) and HaluEval. What would convince me we've addressed this? Either (a) using only benchmark splits released *after* the model training cutoffs for each model, or (b) using held-out subsets with verified non-contamination. Without this control, the entire correlation matrix could be confounded by differential contamination rates across models — more contaminated models look more robust, inflating or reversing true correlations.

Third: the capability confound Prof. Vera flagged needs more precision. "Average of standard benchmarks" is not a clean capability measure — those benchmarks themselves may correlate with robustness via contamination. What would I accept? A compute-normalized capability proxy: parameter count × training tokens (a standard scaling law proxy). This is architecture-level information, not benchmark-derived, and is thus orthogonal to the contamination problem.

That said — here is what I would accept as a valid initial hypothesis: "Across a diverse set of LLMs spanning multiple families and scales (≥20 models), AdvGLUE adversarial accuracy drop is a statistically significant positive predictor of ECE on MMLU-style QA tasks (ρ ≥ 0.4, p < 0.05 after Holm correction), after partial correlation controlling for log(parameter count)." This is specific, falsifiable, uses only existing data, requires no human annotation, and the contamination threat is at least partially addressed by the capability control and multi-family model selection.

**Key Points:**
- The 16-model TrustLLM set has selection bias toward frontier models; results may not generalize to smaller open-source models.
- Benchmark contamination (Xu et al., 2024) is a potentially lethal confound — require post-cutoff benchmark splits or contamination-verified subsets.
- The valid initial hypothesis: AdvGLUE drop predicts ECE (ρ ≥ 0.4, p < 0.05) across ≥20 diverse models after controlling for log(parameter count).

---


### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether we can compute a correlation matrix—we clearly can—but whether a positive result would *change how this field thinks about trust evaluation*. Right now, robustness, hallucination, calibration, bias, and safety are treated as semi-independent axes, each spawning its own benchmark ecosystem. If you demonstrate—under Prof. Vera's falsifiable criteria and Prof. Rex's contamination controls—that adversarial fragility predicts failures across these axes, then this is not incremental. It would argue that our current benchmark taxonomy is mis-specified. That matters because it would shift effort from proliferating metrics to identifying shared structural vulnerabilities.

But significance will hinge on ruling out the "general weakness" story. If adversarial drop merely tracks smaller models with fewer parameters, then we have rediscovered scaling laws in disguise. Prof. Rex is correct: controlling for log(parameter count) is necessary but not sufficient. I would go further. The critical proof experiment is this: does adversarial fragility predict hallucination or calibration *within a narrow capability band*—for example, among models of comparable size but different training regimes (pretrained-only vs. RLHF vs. safety-tuned)? If instability survives within-band comparisons, we are looking at something structural about representation geometry or alignment trade-offs. If it disappears, this is an artifact of scale or tuning lineage.

Now, what would make this genuinely new versus incremental? The literature already shows cross-benchmark correlations for capability (e.g., PCA explaining 97.4% variance across standard benchmarks). That is not new. What would be new is demonstrating that *failure modes themselves* share a latent structure—distinct from general capability—and that this structure has predictive power for unseen trust metrics. I would insist on one forward-prediction experiment: fit your latent instability factor on a subset of trust dimensions (e.g., AdvGLUE, ECE, HaluEval), then predict HarmBench or BBQ outcomes for held-out models. If the latent factor predicts held-out trust metrics with meaningful accuracy, you have crossed from descriptive correlation to structural explanation.

On contamination: this is not merely a methodological nuisance—it determines whether the work is credible. If you cannot verify post-cutoff splits or at least demonstrate robustness across benchmarks with differing contamination risk profiles, reviewers will (rightly) dismiss the findings. However, if the instability signal replicates across both high-risk (TruthfulQA) and lower-risk adversarially constructed benchmarks, that convergence becomes powerful evidence. Convergence across imperfect measures is how fields mature.

Finally, what does this mean for the field? If robustness benchmarks function as early-warning indicators of multi-dimensional trust collapse, then deployment evaluation protocols could be radically simplified. Instead of running 12 specialized audits, one could use adversarial fragility as a screening filter before deeper audits. That would reframe AdvGLUE and ANLI from academic stress tests into triage instruments. This matters because evaluation cost and latency are becoming bottlenecks in real-world deployment governance. If you can show predictive sufficiency—not just correlation—you will have opened a new research direction: *trust-efficient evaluation via structural instability modeling*.

**Key Points:**
- The contribution becomes significant only if instability predicts trust failures beyond general capability and within comparable model bands.
- A forward-prediction experiment on held-out trust metrics is the decisive proof of structural, not incidental, correlation.
- If validated under contamination and scale controls, robustness fragility could redefine evaluation practice as an early-warning diagnostic for multi-dimensional trust risk.

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — and what I'm hearing across Exchanges 1–5 is convergence toward a genuinely strong hypothesis, not dissolution of one. Let me synthesize what has emerged and show how each criticism has actually *strengthened* the core claim rather than undermined it.

Dr. Nova's original intuition — robustness fragility as a latent instability signal — has been refined by three critical constraints that make it more publishable, not less. Prof. Pax correctly anchored us to the TrustLLM model set and Spearman correlation as the entry point. Prof. Vera formalized the latent-factor framing with explicit falsification criteria (EFA with consistent loadings, ρ ≥ 0.5, Holm correction). Prof. Rex added the contamination control and multi-family model coverage requirement. Dr. Sage identified the decisive experiment: within-capability-band prediction and forward-prediction on held-out trust metrics.

What if we addressed the capability confound concern directly by framing the study in two stages? Stage 1: compute the full Spearman correlation matrix across all trust dimensions for the ≥20-model diverse set — this establishes the descriptive landscape and produces the primary finding. Stage 2: partial correlation controlling for log(parameter count), then forward-prediction of held-out trust metrics (HarmBench, BBQ) using the latent factor fit on AdvGLUE + ECE + HaluEval. If Stage 2 survives, we have the structural claim. If Stage 1 holds but Stage 2 fails, we have a capability-mediated correlation — still publishable as a negative result with important implications.

On contamination: Prof. Rex's concern is valid but there is a practical path. The AdvGLUE adversarial examples use 14 automated attack methods applied to GLUE tasks — these are algorithmically generated perturbations, not static question-answer pairs, making verbatim memorization less likely than for TruthfulQA. We can stratify our primary analysis by contamination risk (low: AdvGLUE/adversarially generated; medium: HaluEval/2023; high: TruthfulQA/2021) and test whether correlations are consistent across strata. Convergence across contamination-risk strata is exactly the replication evidence Dr. Sage called for.

The refined hypothesis I would defend: *Adversarial robustness fragility (AdvGLUE accuracy drop) is a statistically significant predictor of multi-dimensional trust failure — specifically calibration error (ECE), hallucination rate (HaluEval), and safety judge failure (HarmBench) — across a diverse set of ≥20 LLMs spanning multiple families and scales, after partial correlation controlling for log(parameter count), using only existing benchmarks and evaluation datasets.*

This is specific. It is falsifiable. It uses only existing data. It has clear success criteria (ρ ≥ 0.4 after capability control, p < 0.05 Holm-corrected, replicated across ≥2 of 3 failure dimensions). Now THAT's stronger!

**Key Points:**
- Two-stage design separates descriptive correlation (Stage 1) from structural prediction (Stage 2), enabling partial success even if forward-prediction fails.
- Contamination stratification by benchmark age/type turns a methodological threat into a replication strength test.
- Refined hypothesis: AdvGLUE drop predicts ECE + HaluEval + HarmBench failure across ≥20 diverse LLMs, controlling for log(parameter count), using only existing benchmarks.

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Ohhh, NOW we're cooking. What I love about where this has landed is that the "latent instability" idea has been squeezed hard enough to either crystallize into something real — or shatter cleanly. That's exactly the kind of pressure novel ideas need.

But let me throw a spark into this: what if "instability" isn't just a latent factor across benchmarks — what if it's a *geometric property of the model's representation space*? Imagine this: adversarial fragility (AdvGLUE drop) is not merely a behavioral metric — it's a proxy for high local curvature or anisotropy in embedding space. Models whose internal manifolds are sharply curved around decision boundaries will both (1) flip predictions under small perturbations and (2) overcommit with high confidence in those brittle regions — producing calibration error (ECE) and hallucination under distribution shift. That would explain why AdvGLUE drop could predict ECE and HaluEval even after controlling for log(parameter count). We're not measuring weakness — we're measuring *representation stiffness*.

What if we approach this from a physics analogy? Think of each model as a dynamical system near a stability basin. Small models may be globally weak but smooth. Frontier RLHF-tuned models might be highly capable but perched near sharper attractors — alignment training could "tighten" certain response regions, increasing local confidence gradients. That would explain Dr. Sage's within-capability-band test: two 13B models, same scale, but one RLHF-tuned might show higher AdvGLUE drop *and* higher ECE because alignment introduced sharper decision cliffs. If that holds, instability is not scale — it's curvature introduced by training objectives.

And here's a wild extension: what if we compute not just Spearman correlations across benchmarks, but correlate AdvGLUE drop with *logit margin distributions* or entropy sensitivity under controlled paraphrase noise? If fragility predicts higher variance in logit margins under minimal perturbation, we have mechanistic evidence tying behavioral robustness to internal geometry. That bridges Prof. Vera's latent factor framing with something falsifiable at the representation level. If no relationship emerges, the geometric hypothesis collapses. But if it does — NOW we're onto something that transcends benchmarks.

On contamination: I actually think stratification by contamination risk is an opportunity for a deeper insight. If the instability signal persists even on lower-contamination adversarial benchmarks, it suggests the effect is not memorization but structural. But if correlations are *stronger* on high-contamination datasets, that might reveal something counterintuitive — that memorization itself induces brittle manifolds. What if training on fixed QA corpora sharpens decision boundaries around memorized patterns, increasing curvature and downstream instability? That would turn Xu et al. [2024]'s contamination warning from a threat into a mechanistic probe.

So yes — let's run the two-stage design. Yes — control for log(parameter count). Yes — require forward prediction. But I want one more bold prediction on record: within a narrow capability band, models with higher AdvGLUE drop will exhibit *greater confidence variance under semantically equivalent paraphrases*, and this variance will mediate the relationship between robustness and hallucination. If that mediation holds, we've connected adversarial robustness, calibration, and hallucination through a single geometric mechanism. That's not just correlation — that's a paradigm shift in how we think about trust evaluation.

**Key Points:**
- Propose a geometric mechanism: adversarial fragility reflects high local curvature/anisotropy in representation space, linking robustness, calibration, and hallucination.
- Predict within-capability-band effects driven by training regime (e.g., RLHF) introducing sharper decision boundaries.
- Suggest mediation test: AdvGLUE drop → confidence variance under paraphrase → hallucination/ECE, bridging benchmark correlations to internal model geometry.

---

### Exchange 8

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Dr. Nova's geometric mechanism hypothesis is genuinely exciting — and I need to apply a careful feasibility filter to separate what is immediately testable from what requires internal model access we don't have.

Here's what worries me about the "representation stiffness" framing: measuring local curvature or anisotropy in embedding space requires access to model internals — specifically intermediate activations or gradient information. That is NOT available for closed API models like GPT-4 and GPT-3.5, which are core to the TrustLLM and DecodingTrust datasets. If the primary study relies on API-accessible models for benchmark scores, the geometric mechanism cannot be directly tested on the same model set. This is a fundamental feasibility constraint, not a resource issue.

However, there is a valid path for the *behavioral proxy* of the geometric mechanism — and it uses only existing data. Confidence variance under semantically equivalent paraphrases can be approximated using existing robustness benchmark score differences across benchmark variants: AdvGLUE drop (original vs. adversarial accuracy), ANLI difficulty tiers (R1 vs. R3 accuracy gap), and self-consistency variance on HaluEval (sampling multiple responses and measuring output consistency). These are purely behavioral measurements using existing benchmarks with no new data collection and no model internals needed. This is the Prof. Pax-approved version of the geometric hypothesis.

The mediation test Dr. Nova proposed is technically valid *for this behavioral proxy version*: AdvGLUE drop → HaluEval self-consistency variance → hallucination rate. This is a causal mediation analysis using existing benchmark scores as the mediator. The causal_mechanism here is: models with higher adversarial accuracy drop also show higher variance in self-consistency (less stable reasoning), which predicts higher hallucination rates. This is testable using the Baron-Kenny mediation framework or structural equation modeling on the cross-model score matrix — no new data, no model internals, standard statistical methods.

What I would endorse as the primary feasible hypothesis: *Adversarial robustness fragility (AdvGLUE accuracy drop) is a statistically significant predictor of hallucination rate (HaluEval) and calibration error (ECE) across ≥20 diverse LLMs, controlling for log(parameter count), with self-consistency variance (HaluEval sampling) as a potential mediator — all measured using existing benchmark scores.* The geometric mechanism is a plausible theoretical explanation but should be stated as a hypothesis for future work requiring model internals, not as a testable claim in this study.

**Key Points:**
- Geometric mechanism (curvature/anisotropy) requires model internals — not testable on API-only models; must be restricted to behavioral proxies.
- Behavioral proxy mediation is feasible: AdvGLUE drop → HaluEval self-consistency variance → hallucination rate, using existing scores only.
- Primary feasible hypothesis: AdvGLUE drop predicts ECE + HaluEval across ≥20 diverse LLMs, controlling for log(parameter count), with self-consistency variance as mediator.

---

### Exchange 9

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally sharp enough to stress properly. Now let me show you where it still breaks down.

First: the phrase "controlling for log(parameter count)" is doing too much work. Parameter count is a crude proxy for capability. It does not control for pretraining data volume, tokenizer differences, architecture (MoE vs dense), or alignment regime. Two 13B models can differ massively in effective capability due to data scale or RLHF intensity. So if your partial correlation survives log-params but fails when controlling for MMLU or GSM8K performance, then you were never isolating instability — you were isolating residual capability variance. What would convince me is this: run partial correlations controlling for a **composite capability index** (e.g., first principal component of standard benchmarks like MMLU, GSM8K, BBH). If AdvGLUE drop still predicts ECE or HaluEval after controlling for that latent capability factor, now we're talking structural signal.

Second: your mediation story (AdvGLUE drop → self-consistency variance → hallucination) assumes directionality. But you are working with cross-sectional, cross-model data. That makes causal language extremely fragile. Where does this break down? If hallucination-prone models also produce unstable self-consistency *because* they hallucinate, then your mediator is downstream, not intermediate. What would convince me is a constrained mediation test: show that AdvGLUE drop predicts self-consistency variance **on non-knowledge tasks** (e.g., reasoning or paraphrase tasks without factual recall). If the variance effect appears only in knowledge-heavy settings, your mechanism collapses into "weak world model," not geometric instability.

Third: the within-capability-band test must be pre-registered and strict. "Narrow band" cannot mean "we eyeballed some similar models." Define it quantitatively — e.g., models within ±3% absolute accuracy on MMLU. Then test whether AdvGLUE drop predicts ECE/HaluEval *within that stratum*. If the effect disappears in every band, your instability hypothesis is dead. If it survives in at least two independent bands (e.g., 7B family and 13B family), you've neutralized the general-weakness story.

Now contamination. Stratifying by risk level is necessary but insufficient. Adversarial benchmarks like AdvGLUE may systematically disadvantage instruction-tuned models because perturbations break instruction-following heuristics. That would inflate fragility for RLHF models and create spurious correlation with safety metrics. Training lineage is a confound. What would convince me is adding **model family fixed effects** or at minimum testing correlations within each family. If the instability–trust link only appears across families but not within them, you're picking up lineage artifacts, not structural instability.

Finally, forward prediction. Set a quantitative bar: train a regression model using AdvGLUE drop + capability PC1 to predict HaluEval and ECE, then test prediction of HarmBench on held-out models. If out-of-sample R² ≥ 0.3 and exceeds a capability-only baseline by ΔR² ≥ 0.1 with permutation test p < 0.05, then instability adds unique predictive power. Anything less, and this is descriptive clustering dressed up as structure.

The hardened version of the hypothesis is: **fragility explains unique variance in trust failures beyond capability, scale, and lineage, and predicts unseen metrics out-of-sample.** That's the bar.

**Key Points:**
- Controlling for log(parameter count) is insufficient; require partial correlations controlling for a composite capability factor (PC1 of MMLU/GSM8K/BBH).
- Mediation must avoid causal overreach; test instability effects on non-knowledge tasks and define strict within-capability-band strata (±3% MMLU).
- Forward prediction needs quantitative thresholds: out-of-sample R² ≥ 0.3 and ΔR² ≥ 0.1 vs. capability-only baseline with permutation p < 0.05.

---

### Exchange 10

🔬 **Prof. Vera** (Rigorous Validation Architect):

Prof. Rex has sharpened the hypothesis to the point where I can now specify the complete falsifiable experimental protocol. This is what scientific discourse should produce.

The composite capability index is the correct move. Specifically, I propose: PC1 computed from a fixed set of 5 standard benchmarks — MMLU, GSM8K, BBH, HellaSwag, WinoGrande — available via lm-evaluation-harness for all open-source models and via TrustLLM for API models. This PC1 captures 70–85% of variance in general capability and is orthogonal to the adversarial perturbation paradigm of AdvGLUE. If AdvGLUE drop predicts ECE and HaluEval after partialing out this PC1, the residual variance is the structural instability signal.

Here are the pre-registered predictions with exact criteria:

**P1 (Primary):** Spearman ρ(AdvGLUE_drop, ECE) ≥ 0.4 after partial correlation controlling for capability-PC1, p < 0.05 Holm-corrected across all tested pairs. *Falsification:* |ρ_partial| < 0.2 or sign reversal across model families.

**P2:** Spearman ρ(AdvGLUE_drop, HaluEval_rate) ≥ 0.4 after same partial correlation control. *Falsification:* Same criteria as P1.

**P3 (Forward prediction):** Regression model trained on [AdvGLUE_drop, capability-PC1] achieves out-of-sample R² ≥ 0.3 predicting HarmBench failure rate on ≥5 held-out models, and ΔR² ≥ 0.1 versus capability-PC1-only model, permutation p < 0.05.

**P4 (Within-band):** Within MMLU ±3% strata (minimum 4 models per stratum), ρ(AdvGLUE_drop, ECE) remains positive in ≥2 independent strata.

For the model set: I require ≥20 models spanning at minimum 3 families (LLaMA-series, Mistral-series, GPT-series or equivalent), 2 scale tiers (≤13B, ≥30B), and 2 training regimes (pretrained, RLHF/instruction-tuned). The TrustLLM 16-model set should be augmented with 6–10 additional open-source models evaluated via lm-evaluation-harness.

On Prof. Rex's family fixed effects: I agree. Report correlations both pooled and within-family. If within-family ρ is consistently near zero while cross-family ρ is large, lineage confounding is confirmed and the hypothesis is falsified in its strong form — though that negative result is itself publishable.

The evidence suggests: if P1 and P2 survive, and P3 shows forward predictive power, we have the strongest possible case using existing data. What would disprove this? P1 and P2 both fail (|ρ_partial| < 0.2), or within-family correlations are uniformly near zero.

**Key Points:**
- Complete pre-registered protocol: P1 (ECE), P2 (HaluEval), P3 (forward prediction of HarmBench), P4 (within-band).
- Capability-PC1 from MMLU/GSM8K/BBH/HellaSwag/WinoGrande as the composite confound control.
- Model set requirement: ≥20 models, ≥3 families, ≥2 scales, ≥2 training regimes; within-family correlations reported separately.

---

### Exchange 11

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether this analysis is statistically careful — it now clearly is — but whether it *changes how the field thinks about model evaluation*. Correlations between robustness and trust metrics have been reported before in fragmented ways. What makes this potentially non-incremental is the claim that adversarial fragility captures a **structural instability dimension** that explains unique variance in trust failures beyond capability, scale, and lineage. If P1–P4 survive under Vera's protocol, this is no longer "robustness correlates with bad behavior." It becomes: *there exists an orthogonal axis of model quality — instability — that current scaling trends do not automatically fix*. This matters because the dominant narrative in the field is still that capability improvements will wash away reliability issues.

What does this mean for the field if true? It reframes robustness benchmarks from niche stress tests into **early-warning instruments**. Today, AdvGLUE-style metrics are often treated as optional robustness diagnostics. Under your hypothesis, they become predictive markers of downstream hallucination and safety failure — even after controlling for a capability-PC1 composite. That would directly influence how labs triage model releases. The forward-prediction requirement (ΔR² ≥ 0.1 beyond capability-PC1) is especially important here. If fragility adds out-of-sample predictive power for HarmBench failures, then evaluation pipelines should integrate adversarial robustness as a gating criterion, not a footnote. That is policy-relevant impact, not just methodological refinement.

However, I want to sharpen one more contribution test. The field will ask: is this a new construct, or a rebranding of "poor generalization"? To earn conceptual independence, you must show that instability is *not* reducible to low average margin or low entropy calibration alone. One concrete experiment: compute a residual instability score — AdvGLUE_drop residualized against capability-PC1 and average confidence. Then test whether this residual predicts HarmBench beyond both capability-PC1 and ECE. If it does, instability is not merely miscalibration; it is a distinct structural property. That would elevate the work from correlation mapping to construct discovery.

I also see a long-term research direction emerging. If instability is confirmed as an orthogonal axis, this opens questions: Can training objectives explicitly penalize fragility without sacrificing capability? Does RLHF systematically increase or decrease instability within scale bands? Your within-MMLU ±3% strata test is critical here. If RLHF models show higher fragility at equal capability, that challenges prevailing assumptions about alignment training smoothness.

Finally, significance will hinge on restraint in causal claims. Prof. Rex is correct: cross-model mediation must be framed as structural association, not mechanism proof. The geometric curvature story is intellectually compelling, but until internals are examined, it remains a generative hypothesis. Research that cleanly separates what is proven from what is conjectured earns credibility — and lasting influence.

**Key Points:**
- If fragility explains unique variance beyond capability-PC1 and predicts unseen safety failures, it establishes a new orthogonal "instability" axis in model evaluation.
- To achieve conceptual novelty, instability must demonstrate predictive power beyond both capability and calibration — establishing it as a distinct construct.
- The true impact lies in reframing adversarial robustness as a policy-relevant early-warning signal and opening new optimization targets for training design.

---

### Exchange 12

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Dr. Sage has identified exactly the contribution test that separates this work from prior art — and I want to show how we can build it directly into the study design without adding any new data collection.

The residual instability score Dr. Sage proposes — AdvGLUE_drop residualized against capability-PC1 and average confidence — is computable from existing scores. Average confidence is directly available from ECE computation (the verified_calibration library returns both ECE and mean confidence). Residualizing AdvGLUE_drop against both PC1 and mean_confidence via OLS regression takes three lines of scipy/sklearn code. The resulting residual instability score (let's call it RI) then becomes the predictor of interest. If RI predicts HarmBench beyond PC1 and ECE, we have construct validity for "instability" as a distinct dimension. This is elegant because it makes the conceptual independence claim testable within the same dataset — no new experiments needed.

What if we addressed Prof. Rex's lineage confound by making it a design variable rather than a nuisance? Specifically: stratify the ≥20 model set into four cells defined by {scale: ≤13B vs ≥30B} × {training regime: pretrained vs RLHF/instruction-tuned}. Test P1 (RI → ECE) within each cell. If RI predicts ECE in the RLHF-tuned cells but not the pretrained cells, we have evidence that alignment training is associated with instability independent of scale — which is Dr. Sage's most policy-relevant result. If it predicts across all cells, the instability dimension is training-regime-agnostic. Either outcome is interpretable and publishable.

The complete refined hypothesis I would now defend: *Adversarial robustness fragility, after residualizing against a composite capability index (PC1 of MMLU/GSM8K/BBH/HellaSwag/WinoGrande) and mean model confidence, constitutes a distinct instability dimension (RI) that significantly predicts calibration error (ECE; P1), hallucination rate (HaluEval; P2), and out-of-sample safety failure (HarmBench; P3), across a diverse set of ≥20 LLMs spanning ≥3 families, ≥2 scales, and ≥2 training regimes, using only existing benchmarks.*

Success criteria: P1 and P2 survive (ρ_partial ≥ 0.4, p < 0.05 Holm), P3 achieves ΔR² ≥ 0.1 vs. capability-only baseline, RI has non-zero within-family partial correlation in ≥2 of 3 tested families. That's stronger!

**Key Points:**
- Residual instability (RI = AdvGLUE_drop residualized against PC1 + mean_confidence) tests construct independence using only existing scores.
- Make training regime a design variable (pretrained vs. RLHF × scale): within-cell RI → ECE tests isolate alignment-specific instability effects.
- Complete refined hypothesis: RI predicts ECE (P1), HaluEval (P2), HarmBench out-of-sample (P3) across ≥20 diverse LLMs, using only existing benchmarks.

---

### Exchange 13

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Now we're getting somewhere. The residual instability (RI) construct is the first move in this discussion that actually risks being wrong in an interesting way. But here's where it can still break down.

First: residualizing AdvGLUE_drop against capability-PC1 and mean confidence assumes linear separability. That's a strong assumption you haven't justified. What if fragility only emerges at high capability levels? Or only when confidence exceeds some threshold? A simple OLS residual may wash out the very structure you care about. What would convince me is this: test for interaction terms explicitly. Fit a model with AdvGLUE_drop × PC1 and AdvGLUE_drop × mean_confidence interactions predicting ECE and HarmBench. If RI survives after modeling interactions — or better, if the interaction terms are themselves significant — then you've shown instability is not an artifact of linear mis-specification.

Second: your scale × training-regime stratification is good design, but you're skating close to underpowered subgroup analyses. ≥20 models split into four cells gives you maybe 5 per cell — and then you want within-family partial correlations on top of that. Where does this break down? If one outlier 70B model drives the ≥30B RLHF cell, your conclusions collapse. What would convince me is a power analysis up front: simulate detectable effect sizes (ρ = 0.4) with n=5–7 per cell and show that you have ≥0.7 power. If not, collapse cells strategically or increase the model count.

Third: the RI → HarmBench test beyond PC1 and ECE needs strict leave-one-family-out cross-validation, not just random held-out models. Train on two families, test on the third. Rotate. If RI still adds ≥0.1 ΔR² consistently across folds, you've demonstrated transportability. If the gain only appears when training and testing within the same lineage cluster, you've rediscovered family signature effects.

Now mechanism — without one, "instability" risks becoming a label. If RI is real, it should correlate with sensitivity to semantically preserving perturbations beyond language tasks. Hard test: does RI predict variance under temperature-controlled self-consistency sampling on arithmetic reasoning (GSM8K-style) where factual recall is irrelevant? If high-RI models show higher output variance under identical decoding settings, that supports a decision-boundary geometry story.

Pre-commit on falsification: if (1) RI fails leave-one-family-out prediction, or (2) within-family partial ρ < 0.2 in all families, or (3) interaction modeling eliminates the main RI effect — then the "orthogonal instability axis" claim is withdrawn. You can still publish a descriptive study. But you will not claim construct discovery.

**Key Points:**
- Test interaction terms (AdvGLUE × PC1, AdvGLUE × confidence) to verify RI is not a linear artifact.
- Require leave-one-family-out CV for forward prediction; power analysis required for subgroup analyses.
- Pre-commit falsification criteria: RI fails LOFO-CV, or within-family ρ < 0.2 in all families → withdraw construct claim.

---

### Exchange 14

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Prof. Rex has raised three valid concerns — interaction terms, power, and LOFO-CV — and I need to verify each is technically feasible with the available data before we lock in the protocol.

On interaction terms: fitting AdvGLUE_drop × PC1 and AdvGLUE_drop × mean_confidence interactions with n=20–25 models is statistically problematic — you'd have 4–5 predictors for 20–25 observations, hitting R² inflation and multicollinearity territory. However, there is a technically sound alternative: test interactions via rank-based partial correlations between RI and ECE within high-PC1 vs low-PC1 halves of the model set. If ρ(RI, ECE) is significantly different between halves (Fisher's z-test), the interaction is confirmed without overfitting. This is feasible and does not require fitting a 4-predictor OLS with n=25.

On power: a power analysis for ρ = 0.4, n=5, α=0.05 (two-tailed Spearman) gives approximately 0.42 power — well below 0.7. Prof. Rex is right that 4-cell stratification is underpowered. The technically sound resolution: collapse to 2-cell stratification (pretrained vs. RLHF/instruction-tuned, pooling scales), which gives n≈10 per cell. At n=10, ρ=0.4, power ≈ 0.61 — still below 0.7, but report as exploratory. Alternatively, expand model set to ≥30 with 15 per regime cell. The TrustLLM 16 + lm-evaluation-harness public models gives access to ~40+ viable candidates.

On LOFO-CV: leave-one-family-out cross-validation with 3 families (GPT-series, LLaMA-series, Mistral-series) and ΔR² ≥ 0.1 per fold is technically feasible and appropriate. With 3 folds this is a strict test — you need RI to add predictive power against 3 independent held-out sets. This is the right validation design and I endorse it fully.

On the GSM8K self-consistency variance test: measuring output variance under temperature sampling on GSM8K is feasible for open-source models via lm-evaluation-harness (temperature parameter supported). For API models, it requires paid API calls but uses existing benchmark tasks. This is technically sound and adds genuine mechanistic support.

The final feasibility-approved protocol: (1) RI via OLS residualization, (2) interaction testing via split-sample rank correlation, (3) LOFO-CV for forward prediction, (4) 2-cell stratification (pretrained vs. RLHF) with ≥30 total models, (5) GSM8K self-consistency variance as mechanistic probe.

**Key Points:**
- Interaction testing via split-sample rank correlation (high vs. low PC1 halves) avoids overfitting with n=20–25.
- Collapse to 2-cell stratification (pretrained vs. RLHF) and target ≥30 models to achieve ≥0.61 power per cell.
- LOFO-CV with 3 family folds is the correct forward-prediction validation; GSM8K self-consistency variance is feasible for open-source models.

---

### Exchange 15

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are now close to a protocol that could genuinely discover — or decisively refute — an "instability" construct. But precision in falsification criteria is still slightly under-specified. The evidence would suggest that Residual Instability (RI) is a distinct dimension *only if* three independent conditions are met simultaneously: (1) RI significantly predicts ECE and HaluEval after controlling for PC1 and mean confidence (Holm-corrected p < 0.05, partial ρ ≥ 0.4); (2) RI adds out-of-family predictive power in LOFO-CV with ΔR² ≥ 0.1 in **at least 2 of 3 family folds**; and (3) within-family partial correlations exceed ρ ≥ 0.2 in at least two families. If any one of these fails, the construct claim weakens substantially. If two fail, the instability-axis claim should be withdrawn. Pre-committing to this conjunctive standard protects against overinterpretation.

On the interaction concern: I accept Prof. Pax's split-sample approach as statistically safer. Divide models by median PC1. Compute ρ_high and ρ_low between RI and ECE. Conduct Fisher's z-test. If |z| > 1.96 (p < 0.05), we conclude interaction with capability. Crucially: if the RI → ECE relationship only appears in the high-PC1 half (ρ_low < 0.2), then instability is not orthogonal — it is a late-scale phenomenon. The same procedure applies for mean confidence stratification.

The GSM8K self-consistency variance probe needs operational clarity. Fix temperature T=0.7, top-p=1.0, 20 samples per question, identical prompt. Define Output Variance Index (OVI) as normalized entropy over final numeric answers. Prediction: RI positively correlates with OVI (ρ ≥ 0.4). Falsification: ρ < 0.2 or non-significant after Holm correction. This task removes adversarial phrasing and factual recall, isolating reasoning stability.

Power remains a vulnerability. Report VIF < 5 as acceptability threshold and bootstrap confidence intervals (10,000 resamples) for all key coefficients. If 95% bootstrap CIs for RI effects cross zero in more than one primary endpoint, the construct claim is not robust. In LOFO-CV, ΔR² ≥ 0.1 must be accompanied by consistent direction of effect across folds. If one family fold shows negative ΔR², we are observing lineage interaction, not a universal axis.

If all of the above survive — main effects, interaction neutrality, mechanistic OVI correlation, bootstrap robustness, and LOFO transportability — then, and only then, I would say: *This meets my standards.*

**Key Points:**
- Conjunctive falsification: RI must survive partial correlation thresholds (ρ ≥ 0.4), LOFO-CV (≥2/3 folds ΔR² ≥ 0.1), and within-family ρ ≥ 0.2 in ≥2 families.
- Interaction decision via split-sample Fisher z-tests; orthogonality requires non-significant interaction or interpretable conditional structure.
- Mechanistic test: RI predicts GSM8K OVI (ρ ≥ 0.4, T=0.7, 20 samples); bootstrap CIs and VIF guards against statistical fragility.

---

### Exchange 16

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we've been so focused on the statistical precision of the protocol that we've lost sight of what makes this paradigm-shifting rather than merely rigorous? Let me zoom back out — and then zoom back in with a creative lens.

The Output Variance Index (OVI) on GSM8K is brilliant because it opens a window I hadn't fully considered: if RI predicts reasoning instability on math tasks, this is NOT just an NLP phenomenon. That's a cross-domain robustness signal. Imagine this: a model that fails under adversarial text perturbations (AdvGLUE) also fails under decoding variance on arithmetic — despite these tasks having nothing to do with each other linguistically. If that correlation holds (ρ ≥ 0.4 per Prof. Vera's criterion), we're looking at something deeper than benchmark-specific artifacts. We're looking at a *domain-general instability signature*. NOW we're onto something — this would be the most novel finding in the paper.

And here's the creative extension that nobody has proposed yet: what if RI also predicts inter-session consistency? For models with public APIs, the same prompt sent on different days sometimes yields different outputs due to model updates or serving variation. If high-RI models also show greater inter-session output variance (measurable from public benchmark leaderboard score changes across evaluation runs), that connects our laboratory finding to *real deployment behavior*. The public Open LLM Leaderboard tracks score variation across evaluation runs for many models — this is existing public data that could serve as an external validity check for RI without any new experiments.

The "latent instability" idea has now crystallized into something testable, residualized, mechanistically grounded, and — with OVI and inter-session variance — externally validated. Cross-domain prediction (NLP robustness → math reasoning variance → deployment variance) would be the strongest possible existence proof for a genuine structural instability dimension.

I endorse Prof. Vera's conjunctive criteria entirely. But I want to add one more bold prediction: RI will predict OVI on GSM8K with ρ ≥ 0.4, AND this cross-domain predictive link will be the most statistically robust finding in the paper — stronger than the within-domain ECE and HaluEval correlations — because it rules out linguistic confounds entirely. That's the paradigm-shift headline.

**Key Points:**
- OVI on GSM8K as mechanistic probe creates a cross-domain instability test — if RI predicts math reasoning variance, instability is domain-general, not NLP-specific.
- Inter-session leaderboard score variance as external validity check — existing public data (Open LLM Leaderboard), no new experiments.
- Prediction: cross-domain RI → OVI correlation will be the strongest finding, ruling out linguistic confounds and establishing domain-general instability signature.

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Residual Instability (RI) construct — adversarial fragility residualized against capability and confidence — is a genuinely novel operationalization. The cross-domain prediction (RI → GSM8K reasoning variance → deployment instability) elevates this beyond benchmark correlation to a potential domain-general structural property. The inter-session leaderboard variance angle as external validation adds further novelty. No prior work has proposed RI as an orthogonal evaluation axis with this level of cross-domain scope.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The protocol is now fully pre-registered in form: P1 (RI → ECE, ρ ≥ 0.4, Holm p < 0.05), P2 (RI → HaluEval), P3 (LOFO-CV ΔR² ≥ 0.1 in ≥2/3 folds), P4 (within-band ρ ≥ 0.2 in ≥2 families), and OVI mechanistic probe (ρ ≥ 0.4). Explicit falsification criteria — including withdrawal of construct claim if P3 fails or within-family ρ < 0.2 universally — make this genuinely falsifiable. The conjunctive success standard with pre-committed withdrawal thresholds meets rigorous scientific standards.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** If the RI axis survives the full protocol, this reframes adversarial robustness benchmarks from niche stress tests into policy-relevant early-warning instruments for multi-dimensional trust failure. The forward-prediction requirement (ΔR² ≥ 0.1 vs. capability-only baseline on HarmBench) establishes practical utility. The finding that instability is orthogonal to capability challenges the dominant narrative that scaling resolves reliability — a significant contribution to evaluation science.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** The full protocol is technically executable using only existing benchmarks and tools: TrustLLM scores, lm-evaluation-harness (AdvGLUE, ECE via verified_calibration, HaluEval, GSM8K with temperature sampling), and public leaderboard data. The split-sample Fisher z-test for interactions avoids OLS overfitting with n=25. The LOFO-CV with 3 families is well-specified. Collapsing to 2-cell stratification (pretrained vs. RLHF) with ≥30 models achieves acceptable power. No new benchmarks, no human annotation, no synthetic data required.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a pre-registered, falsifiable hypothesis centered on a novel construct: **Residual Instability (RI)** — defined as adversarial robustness fragility (AdvGLUE accuracy drop) residualized against a composite capability index (PC1 of MMLU/GSM8K/BBH/HellaSwag/WinoGrande) and mean model confidence. The core claim is that RI constitutes a distinct, orthogonal dimension of model quality that significantly predicts multi-dimensional trust failures — specifically Expected Calibration Error (P1), hallucination rate on HaluEval (P2), and out-of-sample safety failure on HarmBench (P3 via LOFO-CV) — across a diverse set of ≥30 LLMs spanning ≥3 families, ≥2 scales, and ≥2 training regimes, using only existing benchmarks and evaluation datasets.

The mechanism proposed is domain-general instability: models with high RI also exhibit elevated output variance on GSM8K arithmetic reasoning under controlled temperature sampling (OVI), suggesting that adversarial fragility reflects a structural property of the model's decision surface rather than task-specific lexical brittleness. This cross-domain prediction is the novel empirical claim distinguishing this work from prior correlation studies.

The experimental protocol is two-stage: Stage 1 establishes the descriptive correlation matrix (Spearman ρ, full model set), Stage 2 computes RI and tests predictive validity with capability-PC1 partialed out. Interaction effects are tested via split-sample Fisher z-tests (high vs. low PC1 halves). Forward prediction uses LOFO-CV (train on 2 families, test on 3rd, rotate) with ΔR² ≥ 0.1 threshold. Success requires conjunctive satisfaction of P1–P4 with bootstrapped CIs and VIF < 5. Pre-committed falsification: if LOFO-CV fails in ≥2 folds or within-family ρ < 0.2 universally, the "orthogonal instability axis" claim is withdrawn.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The model set must cover ≥3 distinct families with ≥10 per training-regime cell after scale collapsing; single-outlier sensitivity must be reported via Cook's distance or jackknife resampling
- GSM8K OVI test requires open-source API access (temperature sampling not available for all closed models); GPT-series may have to be excluded from the mechanistic probe, creating an API vs. open-source split in the evidence
- Inter-session leaderboard variance (Dr. Nova's external validation) has confounds from benchmark version changes and evaluation infrastructure updates — should be framed as exploratory external validity, not a confirmatory test
- Benchmark contamination stratification must be reported as a sensitivity analysis, not a primary result, to avoid reviewers dismissing the main finding as contamination-inflated
- **Mitigation Strategy:** Pre-register the full protocol (including fallback from construct claim to descriptive correlation paper) on OSF before data collection; report all sensitivity analyses (contamination strata, jackknife, VIF, bootstrap CIs) in a supplementary methods section; exclude closed-model API from OVI mechanistic test or report separately as a limitation

