# Phase 2A Discussion Log

**Gap ID:** gap-1
**Gap Title:** No Cross-Benchmark ECE Measurement Under Adversarial Perturbation
**Architecture:** Self-Contained Tikitaka Loop (independent-controller ablation — Claude plays all personas)
**Execution Mode:** UNATTENDED
**Date:** 2026-08-25

---

## Briefing Context

### Selected Research Gap

**Gap 1 (PRIMARY, CRITICAL):** No published study has computed Expected Calibration Error (ECE) on adversarial NLP benchmark splits (AdvGLUE, ANLI, BIG-Bench Hard) and compared it to clean-split ECE as a systematic miscalibration diagnostic for LLMs.

**Current State:** ECE measured for image models (Guo 2017, Minderer 2021); LLM self-calibration studied (Kadavath 2022, Xiong 2023); adversarial benchmarks used for accuracy only (Wang et al. 2021 AdvGLUE, Nie et al. 2020 ANLI). The intersection — ECE on adversarial NLP splits for open-weight LLMs — is unmeasured.

**Missing Piece:** A unified pipeline that (1) loads adversarial splits alongside clean counterparts, (2) extracts logits from open-weight LLMs (Llama-2/3, Mistral), (3) computes ECE per task per split, (4) reports calibration delta (ΔECE = perturbed ECE − clean ECE) as the miscalibration signal.

**Feasibility Constraints (MANDATORY):**
- No new benchmarks or rubrics
- No synthetic/generated data
- No human annotation
- Only existing real datasets (AdvGLUE, ANLI, BIG-Bench Hard, TruthfulQA, MMLU, WinoGrande) and existing benchmarks

### Previous Failure / Routing Context

First Phase 2A execution. No Serena memory files found. No routing archive exists. Proceeding as fresh hypothesis generation.

### Reference Papers Available
- P1: Guo et al. 2017 — ECE framework (image domain)
- P2: Minderer et al. 2021 — Calibration ≠ accuracy; distribution shift degrades calibration
- P3: Kadavath et al. 2022 — LLM self-calibration on clean benchmarks
- P4: Wang et al. 2021 — AdvGLUE (adversarial benchmark, accuracy-only)

---

## Discussion Transcript

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

Welcome to this discussion on what I believe is a genuinely exciting research gap. The core observation is elegant: we have two mature research traditions — calibration measurement (Guo 2017, Minderer 2021) and adversarial robustness benchmarking (AdvGLUE, ANLI) — that have never been systematically combined for LLMs. The novelty here isn't methodological invention; it's the intersection.

Let me propose three unconventional angles worth exploring:

**Angle 1: The Confidence Collapse Hypothesis.** When a model's accuracy drops 20% under adversarial perturbation (as Wang et al. 2021 documented), what happens to its confidence distribution? My intuition: models don't just get more wrong — they get confidently wrong. The overconfidence grows as the gap between predicted confidence and actual accuracy widens. If ΔECE (perturbed ECE − clean ECE) is consistently large and positive across model families, this is a *systematic* pattern, not noise.

**Angle 2: Task-Type ECE Signature.** Different task types may exhibit different calibration collapse profiles under adversarial input. NLI tasks (ANLI) may show different ΔECE patterns than QA tasks (TruthfulQA under distribution shift) or commonsense tasks (WinoGrande). A cross-task ECE profile could serve as a "miscalibration fingerprint" for a model family.

**Angle 3: ΔECE as Reliability Predictor.** The research question asks whether miscalibration patterns "predict real-world reliability failure." Could ΔECE measured on existing adversarial benchmarks serve as a leading indicator of deployment failure? This connects the measurement study to a predictive claim that goes beyond description.

I'll start with Angle 1 as the primary hypothesis core — it's the most directly testable with existing tools (lm-evaluation-harness + ECE computation) and existing benchmarks.

**Key Points:**
- Gap is intersection of two mature traditions, not a new methodology
- Confidence Collapse Hypothesis: adversarial perturbation causes systematic overconfidence growth
- ΔECE (perturbed − clean ECE) as the primary measurement unit
- Task-type ECE signatures could reveal cross-domain patterns

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova raises compelling directions, but I need to sharpen the falsifiability before we commit. The "Confidence Collapse Hypothesis" is attractive but needs precise operationalization to be testable.

First, let me stress-test Angle 1. Dr. Nova claims models get "confidently wrong" under adversarial perturbation. This is testable, but we need to specify: (a) which models, (b) which perturbation types, (c) which ECE computation method, and (d) what constitutes a "large" ΔECE. Without these, the hypothesis is unfalsifiable.

**Sharpened Hypothesis Proposal:**
*Under adversarial text perturbation from AdvGLUE/ANLI, open-weight LLMs (Llama-2-7B, Llama-2-13B, Mistral-7B) will exhibit ΔECE > 0 (miscalibration increase) on adversarial splits compared to clean GLUE/MultiNLI splits, measured via 15-bin ECE on token-level probability distributions.*

This is falsifiable: if ΔECE ≤ 0 for most models and tasks, the hypothesis fails. We would instead observe that models appropriately reduce confidence under adversarial inputs (better calibration under stress), which would be a surprising and noteworthy null finding.

**On Angle 2 (Task-Type Signatures):** This is descriptive science, which is valuable but needs a primary testable claim. I'd reframe it as: "Does ΔECE magnitude differ significantly across task types (NLI vs. QA vs. commonsense)?" This is testable via a task-type × model interaction effect.

**Critical Measurement Choice:**
We must decide: logit-based ECE or verbally-elicited ECE? For open-weight models via lm-evaluation-harness, logit-based is feasible and grounded in Guo 2017. Verbal ECE (Kadavath-style) would require a different evaluation protocol. I recommend logit-based ECE as primary — it's reproducible and doesn't require additional model calls.

**Key Points:**
- Hypothesis needs precise operationalization: specific models, perturbation types, ECE method
- Falsification condition: ΔECE ≤ 0 (models appropriately reduce confidence) would be surprising null
- Logit-based ECE is more rigorous and reproducible than verbal elicitation for this study
- Task-type × model interaction as secondary analysis

---

### Exchange 3

🎯 **Dr. Sage** (Research Impact Evaluator):

This conversation is clarifying the hypothesis well. Let me evaluate significance from an impact perspective.

**Why this matters for the field:** The premise that high accuracy implies trustworthiness is a dangerous conflation in LLM deployment. Models are increasingly used in high-stakes settings — medical QA, legal reasoning, financial advice — where a model that is wrong *and* confident is far more dangerous than one that is wrong *and* uncertain. If ΔECE is consistently large under adversarial perturbation, this reframes the entire LLM evaluation paradigm: accuracy rankings (MMLU leaderboard) are insufficient for deployment decisions.

**Target Venue:** ICLR 2025 Workshop on Building Trust in Language Models. This framing — "existing benchmarks already contain the signal we need to detect miscalibration; we just haven't been measuring it" — is a powerful message. It requires no new data collection, no human annotation, and uses open tools (lm-evaluation-harness).

**Impact amplifier:** If ΔECE predicts failure modes, this becomes an *actionable* diagnostic. A practitioner could run a small subset of AdvGLUE/ANLI on their model, compute ΔECE, and use it as a deployment readiness signal. This bridges the paper → practice gap.

**Scope question:** Should the study focus on gap-1 alone (ECE on adversarial benchmarks) or also include gap-2 (cross-family comparison)? My recommendation: tackle both simultaneously. Gap 2 is essentially the same experiment run across model families — it's marginal additional compute for substantially richer findings. Including Llama-2-7B, Llama-2-13B, Mistral-7B, and possibly Falcon-7B creates a cross-family comparison at low cost.

**Key Points:**
- Significance: reframes LLM evaluation from accuracy-only to calibration-aware
- Directly actionable: ΔECE as deployment readiness diagnostic using existing benchmarks
- Scope expansion: Gap 2 (cross-family) is free marginal experiment alongside Gap 1
- Venue alignment: ICLR 2025 Workshop on Building Trust explicitly targets this type of finding

---

### Exchange 4

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Strong conceptual alignment so far. Let me ground-truth feasibility — this is where many elegant hypotheses die.

**The critical technical question:** Can we actually extract logit-based ECE from LLMs on AdvGLUE/ANLI via lm-evaluation-harness? The answer is: **yes for multiple-choice format, conditional for free-form tasks.**

For multiple-choice classification (ANLI is 3-class NLI: entailment/neutral/contradiction; AdvGLUE includes SST-2 as binary), the model produces a distribution over answer tokens (A/B/C or positive/negative). The probability mass on the correct answer token is the confidence score. ECE computation on these confidence scores is standard.

**Where it gets complex:** BIG-Bench Hard includes open-ended generation tasks where a single confidence score is ill-defined. We'd need to restrict to multiple-choice BIG-Bench Hard subsets. This is feasible — ~50% of BBH tasks have multiple-choice formats.

**Compute requirement:** Running Llama-2-7B/13B, Mistral-7B on AdvGLUE + ANLI + BBH (multiple-choice subset) requires approximately 4-8 GPU-hours on A100 hardware, which is accessible on standard research compute. For Llama-2-13B, 16GB VRAM is sufficient with 4-bit quantization.

**Data availability check:**
- AdvGLUE: ✅ HuggingFace datasets (`tau/commonsense_qa` for clean; `AdvGLUE` for adversarial)
- ANLI: ✅ `facebook/anli` on HuggingFace; clean counterpart is MultiNLI
- BIG-Bench Hard: ✅ `lukaemon/bbh` on HuggingFace

**Clean baseline identification:** Each adversarial benchmark needs a clean counterpart for ΔECE computation:
- AdvGLUE (adversarial GLUE) → clean baseline: GLUE (same tasks, clean inputs)
- ANLI → clean baseline: MultiNLI (same task, non-adversarial)
- BBH → clean baseline: original BIG-Bench (non-Hard subsets or clean BBH examples)

**Key Points:**
- Logit-based ECE is feasible for multiple-choice tasks; restrict BBH to MC subsets
- Models: Llama-2-7B, Llama-2-13B, Mistral-7B on A100 — ~4-8 GPU-hours total
- All benchmark data available on HuggingFace datasets
- Clean baseline mapping: AdvGLUE→GLUE, ANLI→MultiNLI, BBH→clean BIG-Bench

---

### Exchange 5

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent convergence across all four perspectives. Let me synthesize into a coherent, strengthened hypothesis that addresses all concerns raised.

**Core Synthesis:** The hypothesis has three testable components that build on each other:

**(H-Primary) ECE Degradation Under Adversarial Perturbation:**
LLMs that maintain high accuracy on clean NLP benchmarks will exhibit systematic ECE increase (ΔECE > 0) when evaluated on adversarial counterparts (AdvGLUE, ANLI), indicating that adversarial perturbation exposes overconfidence that is invisible in clean-split evaluation. This claim is testable, falsifiable (ΔECE ≤ 0 is a null), and uses exclusively existing benchmarks.

**(H-Secondary) Cross-Family Calibration Signature:**
ECE degradation magnitude (ΔECE) will vary systematically across model families (Llama-2-7B, Llama-2-13B, Mistral-7B), with RLHF-aligned or instruction-tuned variants showing different ΔECE profiles than base models. This provides the cross-family comparison (Gap 2) at marginal cost.

**(H-Predictive) ΔECE as Failure Predictor:**
ΔECE on adversarial benchmark splits will correlate positively with downstream error rates on held-out adversarial examples, suggesting ΔECE as an automated deployment reliability signal — testable via AUROC of ΔECE-percentile ranking against per-example error labels using benchmark ground truth (no human annotation needed).

**Mechanism:** Adversarial text perturbations change input surface features while preserving task labels. A well-calibrated model should respond by reducing confidence on perturbed inputs (uncertainty appropriately increases). An overconfident model will maintain high confidence despite lower accuracy — the gap is ECE. The mechanism is the decoupling of accuracy degradation from confidence adjustment.

**Strengthening from Prof. Vera:** Logit-based ECE, 15-bin computation, specific model list — these are incorporated. The hypothesis is falsifiable in both directions (ΔECE consistently high = hypothesis confirmed; ΔECE ≈ 0 = models ARE appropriately uncertain under adversarial inputs = equally interesting finding).

**Key Points:**
- Three-component hypothesis: ECE degradation (primary), cross-family signature (secondary), ΔECE as predictor (tertiary)
- Mechanism: adversarial perturbation should increase uncertainty; overconfidence = miscalibration
- Both positive and null findings are publishable and interesting
- All three components testable with existing benchmarks and open tools

---

### Exchange 6

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Dr. Ally's synthesis is well-constructed. My job is to stress-test it before we converge. Here are the sharpest objections:

**Objection 1: The "adversarial ECE" conflation problem.**
AdvGLUE perturbs *inputs* while preserving *labels*. But if perturbations sometimes shift the ground truth label (ambiguous cases that adversarial examples exploit), then ECE degradation may reflect label noise rather than miscalibration. We'd be measuring noise-induced ECE rather than genuine calibration failure. **Mitigation:** AdvGLUE includes human verification of label preservation. ANLI was designed with model-in-the-loop annotation. These constraints partially address this — but we should report % of examples where label ambiguity might confound results.

**Objection 2: Multiple-choice logit ECE is not the same as deployment ECE.**
When we compute ECE from the probability on answer token A vs B vs C, we're measuring a restricted distribution. In real deployment, LLMs generate free text, and confidence is more diffuse. The hypothesis claims ΔECE predicts "real-world reliability failure" but the measurement is on multiple-choice tasks. **Mitigation:** Frame scope clearly — this study measures *benchmark calibration* under adversarial perturbation. The claim is that benchmark ΔECE is a proxy for deployment risk, not a direct measurement. AUROC analysis (H-Predictive) provides the validation.

**Objection 3: Model selection bias.**
Llama-2-7B, Mistral-7B are instruction-tuned models by default (via HuggingFace). If we use instruction-tuned checkpoints, we're measuring RLHF-aligned calibration. If base models, we're measuring pre-RLHF calibration. We need to specify exactly which checkpoints and justify the choice. Base vs. instruction-tuned comparison would be ideal.

**Mitigation Strategy:**
1. Report label preservation statistics for AdvGLUE/ANLI used
2. Explicitly scope claim to "benchmark calibration under adversarial perturbation" not "deployment calibration"
3. Include both base and instruction-tuned variants for at least one model family (Llama-2-7B-base vs. Llama-2-7B-chat)

**Remaining Concerns:**
- Label noise confound in adversarial examples
- Multiple-choice ECE → deployment ECE gap requires explicit framing
- Model checkpoint specification (base vs. instruction-tuned)

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

Prof. Rex's objections are well-taken and actually strengthen the hypothesis by forcing precision. Let me address the novelty angle in light of these concerns.

**On the Label Noise Objection:** This actually opens a secondary novelty angle. We could compute ECE conditioned on label-preservation confidence: for AdvGLUE examples with highest human agreement on label preservation, ΔECE should be cleanest. If ΔECE is high even on the cleanest subset, the miscalibration claim is most robust. This within-dataset stratification is a novel analytical contribution.

**On Multiple-Choice ECE vs. Deployment ECE:** Prof. Rex is right to flag this. My reframing: the claim should be "adversarial benchmark ΔECE as a *standardized calibration stress test*" — analogous to how stress testing financial models uses synthetic scenarios that don't perfectly mirror real market crashes but are validated as predictive. The AUROC validation provides empirical grounding.

**Novel Contribution Restatement:**
Prior work either measures calibration on clean benchmarks OR measures accuracy on adversarial benchmarks. This study is the first to measure calibration *on* adversarial benchmarks, directly filling the intersection. The novelty is both the measurement and the finding, regardless of direction.

**What makes this publishable regardless of result:**
- ΔECE consistently positive: first evidence that adversarial robustness ≠ calibration robustness
- ΔECE ≈ 0: first evidence that LLMs are appropriately uncertain under adversarial inputs (surprising and important for trust deployment)
- ΔECE negative: models become *better* calibrated under adversarial inputs (most surprising — would require mechanistic explanation)

All three outcomes are publishable because the measurement itself is the contribution.

**Key Points:**
- Label-preservation stratified analysis as within-dataset robustness check
- Reframe as "calibration stress test" analogous to financial stress testing
- Publication-positive result regardless of ΔECE direction — measurement fills a genuine gap
- Both Llama-2-7B-base and -chat should be included for base vs. RLHF comparison

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

Final validation pass before I give my verdict. The hypothesis has sharpened considerably.

**What we have now:**
- Clear IV: adversarial perturbation (AdvGLUE / ANLI / BBH-MC) vs. clean counterparts (GLUE / MultiNLI / BIG-Bench)
- Clear DV: ΔECE = ECE(adversarial split) − ECE(clean split), computed via 15-bin logit-based ECE
- Specific models: Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, Mistral-7B-instruct
- Falsification conditions specified: ΔECE ≤ 0 is the null
- Scope bounded: multiple-choice NLP tasks, existing benchmarks, open-weight models

**Prediction structure (testable):**
- P1: ΔECE > 0 for majority of model × task combinations (primary claim)
- P2: ΔECE magnitude varies by model family, with base models showing higher ΔECE than aligned variants (alignment improves calibration robustness)
- P3: Per-model mean ΔECE correlates positively with AUROC of entropy as failure predictor (r > 0, p < 0.05)

**Success criteria:**
- P1: ΔECE > 0.05 for ≥60% of model × task combinations (effect size threshold)
- P2: Llama-2-7B-base ΔECE significantly higher than Llama-2-7B-chat (paired t-test, p < 0.05)
- P3: Spearman correlation between mean ΔECE and AUROC(entropy) > 0.5 across models

**This is scientifically sound.** All three predictions are testable with existing data and tools. The study is reproducible, benchmarks are public, models are publicly available. I give this my STRONG endorsement.

**Key Points:**
- IV/DV/models fully specified; falsification conditions clear
- Three testable predictions with quantitative success criteria
- Fully reproducible: public benchmarks, public models, standard tools
- STRONG verdict from falsifiability perspective

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis fills a genuine measurement gap — the intersection of calibration science and adversarial NLP evaluation that has been overlooked despite both traditions being mature. The result is publishable regardless of direction (positive, null, or negative ΔECE). The "calibration stress test" framing and label-preservation stratification add analytical novelty beyond the measurement itself.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three predictions with quantitative success criteria, specified models, clear falsification conditions (ΔECE ≤ 0), and logit-based ECE on multiple-choice tasks — this is a properly operationalized hypothesis. The restriction to MC tasks and explicit base vs. instruction-tuned model comparison address the main validity threats.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** Directly relevant to the ICLR 2025 Workshop on Building Trust in LLMs. Reframes LLM evaluation from accuracy-only to calibration-aware using existing benchmarks. If ΔECE is large, the finding challenges accuracy-based deployment decisions across the field. ΔECE as deployment readiness diagnostic is a practical, actionable contribution.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Technically sound. Logit extraction via lm-evaluation-harness is standard; AdvGLUE, ANLI, BBH available on HuggingFace; Llama-2/Mistral accessible via HuggingFace Hub with 4-bit quantization; 4-8 GPU-hours on A100. No compute bottlenecks. ECE computation library available (google-research/robustness-metrics or custom 15-bin implementation). Entirely feasible.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The hypothesis that emerged from this discussion is: **LLMs exhibit systematic calibration degradation under adversarial text perturbation, where ECE increases when evaluated on adversarial NLP benchmark splits (AdvGLUE, ANLI) compared to their clean counterparts (GLUE, MultiNLI), indicating that adversarial perturbation exposes overconfidence that clean-benchmark evaluation fails to detect.**

The proposed experiment measures ΔECE = ECE(adversarial split) − ECE(clean split) using logit-based 15-bin ECE on multiple-choice NLP tasks, across four open-weight LLMs: Llama-2-7B-base, Llama-2-7B-chat, Llama-2-13B-chat, and Mistral-7B-instruct. The study uses exclusively existing publicly available benchmarks and models, requires no human annotation, and can be completed in under 8 GPU-hours on A100 hardware.

Three testable predictions with quantitative success criteria: (P1) ΔECE > 0.05 for ≥60% of model × task combinations; (P2) base models show significantly higher ΔECE than aligned variants; (P3) per-model mean ΔECE correlates positively with AUROC of entropy-based failure prediction.

The mechanism: adversarial perturbation should trigger increased uncertainty in a well-calibrated model; failure to do so (high confidence on wrong answers) is the miscalibration signal. The proposed study can confirm, refute, or nuance this mechanism using existing data.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- Label noise in adversarial examples may confound ECE measurement for a subset of examples — mitigated by label-preservation stratification
- Multiple-choice ECE is not identical to deployment-setting calibration — scope must be explicitly bounded in the paper
- Checkpoint specification matters: base vs. instruction-tuned comparison is required, not optional
- **Mitigation Strategy:** Include both Llama-2-7B-base and Llama-2-7B-chat; report label-preservation statistics; frame scope as "benchmark calibration stress test" rather than direct deployment calibration measurement; validate ΔECE as deployment proxy via AUROC analysis.
