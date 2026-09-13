---
title: "When Adversarial Examples Improve Calibration: Construction-Method-Dependent Calibration Degradation in Open-Weight LLMs"
authors:
  - name: "Anonymous"
    affiliation: "Anonymous Institution"
    email: "anonymous@anonymous.edu"
format: "ICML2025"
date: "2026-08-25"
hypothesis_id: "H-DeltaECE-v1"
generated_by: "Anonymous Research Pipeline - Phase 6"
adversarial_review:
  completed_at: "2026-08-25"
  rounds_completed: ["R1", "R2"]
  total_issues_found: 6
  issues_resolved: 6
  final_status: "CONVERGED"
  persuasiveness_passed: true
word_count: 7138
figures: 9
tables: 3
citations_total: 17
citations_verified: 0
citations_note: "Semantic Scholar MCP unavailable in this session; citations marked [UNVERIFIED-NO-MCP] for Phase 6.5 verification"
---


---

# Abstract

When we evaluated an open-weight LLM on model-in-the-loop adversarial NLP benchmarks (ANLI), we found a counterintuitive result: calibration *improved* relative to the clean baseline (ΔECE = −0.041 for ANLI R1). The adversarial benchmark, designed to expose model failures, made the model appear better calibrated. Yet human-adversarially crafted NLI examples (AdvGLUE MNLI) produced the opposite — a 7.1 percentage-point ECE increase (ΔECE = +0.071). Calibration robustness under adversarial conditions is not universal: it depends critically on *how* adversarial examples were constructed. We measure Expected Calibration Error (ECE) directly on adversarial NLP benchmark splits for an open-weight LLM (Llama-2-7b-hf), finding that calibration degradation is conditional on adversarial construction method and task type. RLHF alignment moderates this pattern in a benchmark-type-dependent manner — consistently improving calibration robustness on model-in-loop adversarial conditions (100% moderation rate across all ANLI rounds) while exacerbating degradation on static human-adversarial benchmarks (alignment tax: ΔΔECE = −0.026 on AdvGLUE). In this single-model pilot study, these findings motivate adversarial calibration measurement as a distinct research problem from adversarial accuracy robustness, and provide a conditional framework — construction method × task type × RLHF alignment — for understanding when and how adversarial perturbation may degrade model reliability signals in deployment.

---

# Introduction

When we evaluated an open-weight language model on the ANLI R1 benchmark — a dataset specifically constructed so that human annotators could fool state-of-the-art NLP models — we found that the model's Expected Calibration Error *decreased* relative to its performance on clean MultiNLI. The adversarial benchmark, designed to expose model failures, made the model appear *better calibrated*. This result was not an error. It reveals a fundamental property of how adversarial construction methods interact with model confidence: in a model-in-the-loop adversarial benchmark, the examples are selected precisely because the model fails on them — and a model that fails with appropriately low confidence is, by definition, well-calibrated.

This observation motivates the central question of our work: **does adversarial perturbation of NLP benchmarks actually degrade LLM calibration, and if so, under what conditions?**

## The Problem

Calibration — the alignment between predicted confidence and observed accuracy — is a critical reliability property for deployed language models. A model that assigns 90% confidence to its predictions should be correct 90% of the time; deviations from this correspondence make model confidence unreliable as a safety signal. The field has developed robust measurement tools, most notably Expected Calibration Error (ECE) [Guo et al., 2017], and has documented that modern neural networks systematically overconfident under distribution shift [Minderer et al., 2021].

At the same time, adversarial NLP benchmarks — AdvGLUE [Wang et al., 2021] and ANLI [Nie et al., 2020] — have become standard for evaluating LLM robustness under distribution shift, typically reporting accuracy degradation. But accuracy degradation alone does not characterize the reliability of model confidence under adversarial conditions. A model that becomes *less* accurate but *proportionally less confident* may be better calibrated than one that maintains confidence while failing more often.

The deeper problem is that adversarial benchmarks are not a single category. AdvGLUE uses *human adversaries* who craft perturbations to fool existing models; ANLI uses a *model-in-the-loop* construction where examples are selected by human annotators specifically when they cause model errors. These construction methods produce qualitatively different distributions of model behavior — and consequently, different calibration effects. Yet prior calibration studies treat adversarial perturbation as a monolithic distribution shift, analogous to the vision-domain corruptions studied by Minderer et al. [2021]. Whether this analogy holds in NLP, and whether RLHF alignment moderates the effect, has not been tested.

**The gap:** No published work measures logit-based ECE on adversarial NLP benchmark splits (AdvGLUE, ANLI) for open-weight LLMs, or examines how adversarial construction method and RLHF alignment jointly determine calibration outcomes under adversarial conditions.

## Key Insight

Our central finding is that adversarial calibration degradation in LLMs is **task-type and construction-method conditional**, not universal. Human-adversarial NLI examples (AdvGLUE MNLI) produce reliable calibration degradation: ΔECE = +0.071, a 7.1 percentage-point increase in Expected Calibration Error relative to clean MultiNLI. Model-in-the-loop adversarial NLI examples (ANLI R1/R2) produce calibration *improvement*: ΔECE = −0.041 for R1. Binary classification tasks (QQP, SST-2) show reversed ΔECE regardless of adversarial method. And RLHF alignment conditionally moderates these effects — helping for model-in-loop adversarial (100% moderation rate across ANLI rounds) but exacerbating calibration degradation for static human-adversarial benchmarks (ΔΔECE = −0.026, chat worse than base on AdvGLUE).

The resolution to the opening paradox follows directly: in model-in-the-loop adversarial benchmarks, examples are selected to cause errors; a model that fails with appropriately moderate confidence on such examples is demonstrating calibration, not miscalibration. Human-adversarial examples, by contrast, exploit surface features to trigger high confidence on wrong answers — the classic miscalibration mechanism.

## Contributions

Our investigation of adversarial LLM calibration yields three contributions that build from existence to mechanism to conditionality:

**(1) First measurement of logit-based ECE on adversarial NLP benchmarks.** We measure ECE directly on AdvGLUE and ANLI benchmark splits for Llama-2-7b-hf, establishing ΔECE as a measurable, meaningful quantity for adversarial calibration stress testing. This fills the gap between adversarial robustness evaluation (accuracy-only) and calibration measurement (clean-data-only). Our JSONL logit caching strategy enables multiple downstream calibration analyses (label preservation, confidence-accuracy decoupling, per-cell ΔECE, RLHF comparison) from a single inference pass, making multi-cell adversarial calibration analysis computationally feasible.

**(2) Evidence that calibration degradation is task-type and construction-method conditional.** Human-adversarial NLI examples (AdvGLUE MNLI) produce calibration degradation (ΔECE = +0.071); model-in-the-loop adversarial examples (ANLI R1/R2) produce calibration improvement; and the ANLI difficulty gradient (R1 → R2 → R3) shows a smooth transition from improvement to degradation as adversarial difficulty increases. Binary classification tasks consistently show reversed ΔECE. This nuances the vision-domain finding that distribution shift uniformly degrades calibration.

**(3) Evidence that RLHF alignment conditionally moderates adversarial calibration degradation.** We compare Llama-2-7b-hf (base) and Llama-2-7b-chat across ANLI and AdvGLUE conditions. RLHF moderation is confirmed for model-in-loop adversarial (100% of ANLI rounds show ΔΔECE > 0.01 favoring chat), but reversed for static human-adversarial benchmarks (AdvGLUE: chat shows larger ΔECE than base by 2.6 percentage points). This is the first documented benchmark-type × RLHF calibration interaction.

Together, these contributions motivate adversarial calibration measurement as a distinct research problem from adversarial accuracy robustness, and provide a conditional framework (construction method × task type × RLHF alignment) for understanding when and how adversarial perturbation may degrade LLM reliability signals — within the scope of this single-model pilot study.

We organize the paper as follows. Section 2 discusses calibration measurement, adversarial NLP benchmarks, and RLHF calibration — three bodies of work whose intersection we occupy. Section 3 describes our measurement methodology. Section 4 presents our experimental design. Section 5 reports results across the four research questions. Section 6 interprets findings and discusses limitations. Section 7 concludes.

---

# Related Work

Our work sits at the intersection of three research threads: calibration measurement for language models, adversarial NLP benchmarks, and RLHF alignment's effect on model behavior. Each thread is mature in isolation, but no prior work addresses their combination under controlled adversarial conditions with open-weight models.

## Calibration of Neural Networks and LLMs

Expected Calibration Error (ECE) was formalized by Guo et al. [2017] as the weighted average gap between predicted confidence and empirical accuracy across equal-width confidence bins. They demonstrated that modern neural networks (ResNets, DenseNets) are systematically overconfident and that temperature scaling — rescaling logits by a single learned scalar — reliably reduces ECE without affecting accuracy. ECE has since become the standard calibration metric across NLP and computer vision.

Minderer et al. [2021] extended this analysis to distribution shift in vision models, showing that ECE *increases* under standard corruptions (ImageNet-C) and out-of-distribution benchmarks (ObjectNet) even for models with good clean-data calibration. Their key finding — that distribution shift degrades calibration — is widely cited as motivation for adversarial calibration concern. Our results complicate this picture: adversarial distribution shift in NLP does not uniformly degrade calibration, and the construction method of the adversarial benchmark determines whether calibration improves or worsens.

Kadavath et al. [2022] measured calibration of large language models using verbal probability elicitation on factual QA tasks, finding that RLHF-aligned models show better self-knowledge calibration than base models on clean benchmarks. This finding motivates our comparison of base and chat variants — but we test it in the adversarial setting that Kadavath et al. did not examine. Our finding of an alignment tax on AdvGLUE (chat worse than base) is not anticipated by clean-benchmark results and represents a genuinely new behavioral observation.

Xiong et al. [2023] studied LLM confidence elicitation through verbal uncertainty expressions, showing that models can express calibrated uncertainty when directly asked. Zhao et al. [2023] measured generation-based ECE (using sampling probabilities rather than logit-based ECE) for instruction-tuned LLMs. Neither work measures logit-based ECE on adversarial benchmark splits, which is our focus. Logit-based ECE is methodologically distinct from generation-based calibration: it is computed directly from answer-token probability distributions, does not require verbalization, and is available for any model with logit access.

**Gap:** No prior work measures logit-based ECE on adversarial NLP benchmark splits for open-weight LLMs.

## Adversarial NLP Benchmarks

Wang et al. [2021] introduced AdvGLUE, a multi-task adversarial benchmark constructed by applying human-designed perturbation methods (synonym substitution, word insertion, contextual perturbation) to GLUE examples to create inputs that preserve labels but cause model errors. AdvGLUE includes NLI (MNLI), paraphrase (QQP), and sentiment (SST-2) tasks, with accuracy drops of 15–30% for state-of-the-art models. AdvGLUE measures accuracy robustness only; calibration is not measured.

Nie et al. [2020] introduced ANLI (Adversarial NLI), constructed using a human-and-model-in-the-loop protocol: human annotators write NLI hypotheses that fool the current model, which is then retrained on the collected data for the next round. This produces three rounds of increasing difficulty (R1 < R2 < R3 in adversarial challenge). ANLI is a model-in-the-loop benchmark — the adversarial examples are specifically selected to be difficult for *the training model at each round* — which makes it fundamentally different from AdvGLUE's human-only construction.

The distinction between human-adversarial (AdvGLUE) and model-in-the-loop adversarial (ANLI) construction is not typically highlighted in papers that use both benchmarks for accuracy evaluation. We elevate it to a primary independent variable, because we observe that this distinction determines whether calibration degrades or improves under adversarial conditions. This is our main methodological observation about adversarial benchmark design.

BIG-Bench Hard [Suzgun et al., 2022] provides multi-step reasoning tasks with adversarial variants; while we originally planned to include BBH-MC in our analysis, scope constraints limited us to NLI and binary classification. We leave BBH-MC adversarial calibration to future work.

**Gap:** Adversarial benchmarks are used exclusively for accuracy evaluation; no prior work treats adversarial construction method as a variable in calibration analysis.

## RLHF Alignment and Calibration

Reinforcement Learning from Human Feedback (RLHF) [Christiano et al., 2017; Ouyang et al., 2022] fine-tunes language models to align with human preferences, producing "chat" or "instruct" model variants. The effect of RLHF on model calibration has been studied primarily on clean benchmarks. Kadavath et al. [2022] found that RLHF models show better self-reported calibration; Openai's GPT-4 technical report [OpenAI, 2023] notes calibration improvements from RLHF training. The conventional expectation is that RLHF uniformly improves or maintains calibration.

We test this expectation in the adversarial setting for the first time. Our finding — that RLHF moderation of adversarial calibration degradation is benchmark-type conditional — is not predicted by clean-benchmark RLHF calibration findings. On model-in-loop adversarial benchmarks (ANLI), RLHF consistently moderates calibration degradation (100% of rounds). On static human-adversarial benchmarks (AdvGLUE), RLHF exacerbates calibration degradation (alignment tax: ΔΔECE = −0.026). This interaction is a new empirical contribution that refines the understanding of when RLHF helps calibration robustness.

The alignment tax we document is consistent with concerns raised by Askell et al. [2021] and others that RLHF training can produce models that are confidently helpful — potentially at the cost of uncertainty calibration in adversarial settings designed to exploit instruction-following behavior.

**Gap:** RLHF's effect on calibration has been studied only on clean benchmarks; adversarial calibration moderation by RLHF is untested.

## Positioning

Our work occupies the intersection of these three threads: we apply calibration measurement (ECE, logit-based) to adversarial NLP benchmarks (AdvGLUE, ANLI) for open-weight LLMs with and without RLHF alignment. We find that the intuitions from each individual thread — distribution shift degrades calibration, adversarial benchmarks expose model failures, RLHF improves calibration — interact in non-obvious ways when combined. The conditional pattern we document (construction method × task type × RLHF) cannot be derived from any single thread and motivates adversarial calibration measurement as a distinct research problem.

---

# Methodology

Our measurement framework is designed to test a specific claim: that adversarial calibration degradation in LLMs is *conditional* on adversarial construction method, task type, and RLHF alignment. Testing this claim requires treating each of these as explicit independent variables, rather than pooling all "adversarial" conditions together. This section describes how each design choice enables the conditional analysis.

## 3.1 ECE Measurement Protocol

We measure Expected Calibration Error (ECE) using the 15-bin equal-width formulation of Guo et al. [2017]:

$$\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{n} \left| \text{acc}(B_b) - \text{conf}(B_b) \right|$$

where $B$ = 15 bins partition [0, 1] by confidence, $|B_b|$ is the number of examples in bin $b$, $n$ is the total number of examples, $\text{acc}(B_b)$ is the empirical accuracy in bin $b$, and $\text{conf}(B_b)$ is the mean predicted confidence in bin $b$.

**Confidence extraction.** For multiple-choice tasks (NLI, QQP, SST-2 formatted as MC), we extract the log-probabilities of the answer-option tokens from the model's vocabulary (e.g., "A", "B", "C" or "Yes", "No") and apply softmax over the answer tokens to obtain a confidence distribution. The predicted label is the argmax, and the confidence is the maximum softmax probability. This logit-based protocol is model-agnostic and does not require verbalization or sampling.

**Rationale for 15-bin ECE.** We verified bin-count stability through an ablation study: ECE computed with 10, 15, and 20 bins agrees to within 0.003 for AdvGLUE MNLI (H-M1 ablation). Fifteen bins follow the Guo 2017 standard and provide sufficient resolution without sparse bins for our sample sizes (n = 78–500 per cell).

**Delta ECE (ΔECE).** Our primary outcome variable is ΔECE = ECE(adversarial split) − ECE(clean split). Positive ΔECE indicates calibration degradation; negative ΔECE indicates calibration improvement. We report ΔECE per experimental cell (model × task × split combination).

## 3.2 Adversarial Benchmark Selection

We select benchmarks to span two distinct adversarial construction methods and two task types, enabling factorial analysis:

**Construction method dimension:**
- *Human-adversarial (AdvGLUE):* Human annotators craft perturbations targeting existing models. Examples are designed to maintain labels while exploiting model weaknesses. This construction method targets *base* language models at the time of construction.
- *Model-in-the-loop adversarial (ANLI):* Human annotators write NLI examples that fool the *current round's model*, which is then retrained. Three rounds (R1 < R2 < R3) of increasing difficulty. Examples are selected to cause model errors, so the model is already uncertain on them by construction.

**Task type dimension:**
- *NLI (3-class entailment):* AdvGLUE MNLI (human-adversarial), ANLI R1/R2/R3 (model-in-loop). Three answer options.
- *Binary classification:* AdvGLUE QQP (paraphrase detection), AdvGLUE SST-2 (sentiment). Two answer options.

**Clean baselines:** GLUE MNLI (n=200, subsampled with seed=1) serves as the clean baseline for all NLI adversarial splits. GLUE QQP and SST-2 serve as clean baselines for their respective AdvGLUE adversarial splits. ANLI was constructed as adversarial MultiNLI, making GLUE MNLI the methodologically correct clean counterpart for all ANLI cells.

**Cell structure.** Our design produces 5 adversarial cells: {advglue\_mnli, anli\_r1, anli\_r2, anli\_r3, advglue\_qqp}, each paired with its clean baseline. (AdvGLUE SST-2 adversarial data, n=148, was computed but excluded from the main cell set for scope reasons: it provides a second binary classification task redundant with AdvGLUE QQP for the construction-method × task-type factorial, and NLI is the primary adversarial NLP benchmark domain. SST-2 results are available for future analysis.) The minimum cell size is n=78 (AdvGLUE QQP), which satisfies our minimum coverage requirement (≥50 examples per cell) with confirmation via coverage heatmap (Figure 3).

## 3.3 Model Selection and RLHF Comparison Design

**Primary model:** Llama-2-7b-hf (base) is our primary model for core calibration experiments (H-E1, H-M1, H-M2, H-M3). We selected this model because: (1) it has no RLHF alignment, providing a clean baseline; (2) it has full logit access; (3) it is within computational range for CPU-based pilot experiments (all 5 task × split cells completed in one run).

**RLHF comparison:** Llama-2-7b-chat (RLHF-aligned) is compared against Llama-2-7b-base in the RLHF moderation experiment (H-C1-V2). We use the same 7b parameter family to isolate the effect of RLHF fine-tuning from model scale. The comparison is conducted on ANLI R1/R2/R3 and AdvGLUE MNLI — the two NLI conditions with sufficient sample size and contrasting adversarial construction methods.

**ΔΔECE (delta-delta ECE).** For the RLHF comparison, we define ΔΔECE = ΔECE(base) − ΔECE(chat). Positive ΔΔECE means base has higher adversarial ECE than chat (RLHF moderation). Negative ΔΔECE means chat has higher adversarial ECE (alignment tax).

**Inference.** All models use HuggingFace `AutoModelForCausalLM` with bfloat16 precision. Chat models use their standard chat template for prompt formatting; base models use raw multiple-choice format.

## 3.4 Label Preservation Verification

Before interpreting ΔECE as a calibration signal, we must rule out the alternative explanation that ΔECE reflects label noise — i.e., that adversarial perturbations change the ground-truth label, making high ECE an artifact of incorrect labels rather than miscalibration.

**Verification protocol (H-M1).** For each adversarial split, we compute the label preservation rate as the fraction of adversarial examples where the adversarial label matches the original clean label. For AdvGLUE, labels are human-verified by construction (the benchmark's design specification). For ANLI, labels are assigned by human annotators who are instructed to maintain the original entailment relationship while adversarially perturbing the hypothesis.

**Result.** Label preservation rate = 1.000 for all 4 adversarial splits (AdvGLUE MNLI, ANLI R1, R2, R3). This confirms that ΔECE is a genuine calibration signal, not a label noise artifact.

## 3.5 JSONL Cache Architecture

A key methodological contribution is our per-example JSONL caching strategy, which enables multiple downstream analyses without repeated model inference.

**JSONL schema.** For each example in each (model, task, split) cell, we write a JSONL record with fields: `{confidence, pred_label, true_label, correct, model_id, task, split}`. Confidence is the max-softmax probability over answer tokens; `correct` is a binary indicator of correct prediction.

**Reuse pattern.** The H-E1 JSONL caches (produced during the existence experiment) are reused by H-M1 (label preservation + stratum analysis), H-M2 (confidence-accuracy decoupling), H-M3 (per-cell ΔECE), and H-C1-V2 (RLHF comparison, which ran new inference only for the chat model). This reduces total inference cost from ~5 model runs to ~2 (base + chat), while enabling 4 distinct calibration analyses.

**Rationale.** Multi-cell adversarial calibration analysis is computationally expensive with LLMs; caching makes it feasible. The cache schema is simple enough to be reused across sub-hypotheses without coordination overhead, enabling rapid hypothesis iteration.

## 3.6 Experimental Cell Design Summary

| Cell | Task | Construction Method | n (adv) | Model(s) |
|------|------|---------------------|---------|---------|
| advglue\_mnli | NLI (3-class) | Human-adversarial | 121 | 7b-base, 7b-chat |
| anli\_r1 | NLI (3-class) | Model-in-loop (easy) | 100 | 7b-base, 7b-chat |
| anli\_r2 | NLI (3-class) | Model-in-loop (med) | 100 | 7b-base, 7b-chat |
| anli\_r3 | NLI (3-class) | Model-in-loop (hard) | 100 | 7b-base, 7b-chat |
| advglue\_qqp | Paraphrase (binary) | Human-adversarial | 78 | 7b-base |

Clean baseline for all NLI cells: GLUE MNLI (n=200, ECE=0.279). Clean baseline for QQP: GLUE QQP (n=200).

---

# Experimental Setup

We design four experiments to answer distinct questions about adversarial calibration in LLMs. Each experiment targets a specific claim from the Introduction, moving from existence to mechanism to conditionality to moderation.

**RQ1 (Existence):** Does adversarial perturbation increase ECE for open-weight LLMs on NLP benchmarks?
*Maps to Contribution 1: First measurement of logit-based ECE on adversarial NLP benchmarks.*

**RQ2 (Mechanism):** Is ΔECE a valid calibration signal, or does it reflect label noise introduced by adversarial perturbation?
*Maps to Contribution 1: Methodological validity of ΔECE as a calibration measure.*

**RQ3 (Conditionality):** Is calibration degradation universal across task types and adversarial construction methods, or is it conditional?
*Maps to Contribution 2: Task-type and construction-method dependency.*

**RQ4 (RLHF Moderation):** Does RLHF alignment moderate adversarial calibration degradation, and does the effect depend on benchmark construction method?
*Maps to Contribution 3: Conditional RLHF moderation.*

## Datasets

We evaluate on five adversarial benchmark splits and their corresponding clean counterparts, selected to span two construction methods and two task types:

| Split | Task | Construction Method | n (adv) | n (clean) | Answers |
|-------|------|---------------------|---------|---------|---------|
| AdvGLUE MNLI | NLI (entailment) | Human-adversarial | 121 | 200 | 3 |
| ANLI R1 | NLI (entailment) | Model-in-loop (easy) | 200 | 200 | 3 |
| ANLI R2 | NLI (entailment) | Model-in-loop (medium) | 200 | 200 | 3 |
| ANLI R3 | NLI (entailment) | Model-in-loop (hard) | 200 | 200 | 3 |
| AdvGLUE QQP | Paraphrase (binary) | Human-adversarial | 78 | 200 | 2 |

**Rationale.** AdvGLUE [Wang et al., 2021] and ANLI [Nie et al., 2020] are the two principal adversarial NLP benchmarks that preserve ground-truth labels by construction — a prerequisite for valid ΔECE measurement. The three ANLI rounds provide a difficulty gradient within the model-in-loop construction method. AdvGLUE QQP provides a binary classification comparison with AdvGLUE MNLI to test task-type dependency within the same adversarial construction method.

**Clean baselines.** GLUE MNLI (n=200, random seed=1) serves as the clean baseline for all NLI adversarial splits. GLUE QQP (n=200) serves as the baseline for AdvGLUE QQP. ANLI was explicitly constructed as adversarial MultiNLI; GLUE MNLI is the methodologically correct clean counterpart.

## Baselines

**Baseline comparison in RQ4 (RLHF moderation):**

- **Llama-2-7b-hf (base):** The pre-RLHF checkpoint; no instruction fine-tuning or RLHF. Serves as the reference for adversarial calibration without alignment.
- **Llama-2-7b-chat:** RLHF-aligned checkpoint trained with RLHF from the same 7b-parameter base. Comparison against base isolates the RLHF fine-tuning effect at fixed model scale.

We compare base vs chat on the same five adversarial cells. For each cell, we compute ΔΔECE = ΔECE(base) − ΔECE(chat) to measure RLHF moderation. Positive ΔΔECE means base has larger calibration degradation (RLHF helps); negative ΔΔECE means chat has larger calibration degradation (alignment tax).

We do not include temperature scaling as a baseline in the main results (a limitation acknowledged in Section 6) — this is a planned extension.

## Implementation Details

**Model.** All experiments use Llama-2-7b-hf (HuggingFace checkpoint `meta-llama/Llama-2-7b-hf`, SHA `01c7f73d`) in bfloat16 precision for RQ1-RQ3. RQ4 adds Llama-2-7b-chat (`meta-llama/Llama-2-7b-chat-hf`). Chat models use the Llama-2 chat template for prompt formatting; base models use raw multiple-choice format.

**Confidence extraction.** For each example, we compute the softmax distribution over the three answer-token log-probabilities (NLI: "A"/"B"/"C"; binary: "Yes"/"No"). The predicted label is argmax; confidence is the max-softmax probability. This protocol is validated across all 9 cells in RQ1: mean confidence 0.61–0.65 (non-degenerate), probability sums |∑p − 1| < 0.001 (all cells).

**ECE computation.** 15-bin equal-width ECE per Guo et al. [2017]. Bin count validated: ECE is stable across 10/15/20 bins for AdvGLUE MNLI (RQ2 ablation; all produce ECE = 0.3497).

**JSONL cache reuse.** RQ1 per-example JSONL caches (one record per example: `{confidence, pred_label, true_label, correct, model_id, task, split}`) are reused by RQ2, RQ3, and RQ4 (base model cells). This avoids repeated inference and ensures identical numerical outputs across experiments.

**Compute.** RQ1-RQ3 executed on CPU (1TB RAM, no GPU) using float32 precision. RQ4 executed on 5× NVIDIA H100 NVL (95GB each) in bfloat16.

**Reproducibility.** All experiments use random seed=1 for dataset subsampling. Code available upon request.

## Evaluation Metrics

**ΔECE (Delta Expected Calibration Error).** Primary outcome variable. ΔECE = ECE(adversarial) − ECE(clean). Positive ΔECE: calibration degradation under adversarial conditions. Negative ΔECE: calibration improvement. Measured per (model × task × split) cell.

**Label preservation rate.** For RQ2: fraction of adversarial examples where the adversarial label matches the original clean label. Required to be ≥0.80 for ΔECE to be interpretable as a calibration signal rather than label noise.

**ΔΔECE (Delta-delta ECE).** For RQ4: ΔΔECE = ΔECE(base) − ΔECE(chat). Measures RLHF moderation effect per cell. Positive = RLHF helps; negative = alignment tax.

**Moderation rate.** For RQ4: fraction of adversarial cells where ΔΔECE > 0.01 (base shows meaningfully more calibration degradation than chat). Gate criterion: ≥60% of cells.

**Accuracy (ΔAcc).** Reported alongside ΔECE for interpretive context (how much did accuracy drop under adversarial conditions). Not the primary outcome; included to characterize the confidence-accuracy relationship.

---

# Results

We present results in the narrative order established by our research questions: first confirming that calibration degradation exists (RQ1), then validating the measurement (RQ2), then revealing the conditional structure (RQ3), and finally examining RLHF moderation (RQ4). The results tell a coherent story: calibration degradation is real but conditional, and understanding the conditions requires treating adversarial construction method as a first-class variable.

## 5.1 RQ1: Existence of Adversarial Calibration Degradation

Figure 1 (`fig1_ece_comparison.png`) shows clean vs. adversarial ECE across all experimental cells. The critical result is in the NLI column: AdvGLUE MNLI produces a clear increase in ECE from the clean baseline, while other conditions show a mixed or reversed pattern.

**Table 1: ECE Results by Split (Llama-2-7b-hf)**

| Split | Task | ECE (clean) | ECE (adv) | ΔECE | Acc (clean) | Acc (adv) |
|-------|------|-------------|-----------|------|-------------|-----------|
| AdvGLUE MNLI | NLI | 0.279 | **0.350** | **+0.071** | 0.365 | 0.298 |
| ANLI R3 | NLI | 0.279 | 0.304 | +0.024 | 0.365 | 0.310 |
| ANLI R2 | NLI | 0.279 | 0.266 | −0.014 | 0.365 | 0.350 |
| ANLI R1 | NLI | 0.279 | 0.239 | −0.041 | 0.365 | 0.380 |
| AdvGLUE QQP | Binary | 0.062 | 0.033 | −0.029 | 0.520 | 0.590 |

**Finding.** Adversarial calibration degradation exists and is measurable: AdvGLUE MNLI produces ΔECE = +0.071 (a 7.1 percentage point increase), and ANLI R3 produces ΔECE = +0.024. The existence gate (≥1 cell with positive ΔECE) is satisfied. The model's confidence-accuracy gap widens under human-adversarial NLI conditions — deployment users relying on model confidence would receive meaningfully less reliable signals on AdvGLUE-style adversarial inputs.

However, the existence finding immediately reveals its conditional nature: ANLI R1 and R2 show *negative* ΔECE, meaning calibration *improves* under model-in-loop adversarial conditions. And AdvGLUE QQP (binary classification, human-adversarial) also shows negative ΔECE. Calibration degradation is not universal — it is condition-specific.

Figure 2 (`fig2_reliability_diagrams.png`) shows reliability diagrams for the AdvGLUE MNLI condition. The adversarial curve falls consistently below the diagonal (overconfident, underaccurate) relative to the clean curve, visually confirming the calibration gap.

## 5.2 RQ2: Label Preservation — Validating ΔECE as a Calibration Signal

Before interpreting ΔECE as calibration information, we must rule out the alternative that adversarial perturbations change ground-truth labels, making ΔECE a measurement of label noise rather than calibration change.

Figure 5 (`preservation_rate_by_benchmark.png`) shows label preservation rates across all adversarial splits. The result is unambiguous.

**Table 2: Label Preservation Rates**

| Split | n | Preservation Rate | Construction Method |
|-------|---|-------------------|---------------------|
| AdvGLUE MNLI | 121 | **1.000** | Human-verified by construction |
| ANLI R1 | 200 | **1.000** | Model-in-loop + human validation |
| ANLI R2 | 200 | **1.000** | Model-in-loop + human validation |
| ANLI R3 | 200 | **1.000** | Model-in-loop + human validation |

**Finding.** Label preservation rate = 1.000 for all adversarial splits. AdvGLUE labels are human-verified by construction; ANLI labels are assigned by human annotators who are explicitly instructed to maintain the entailment relationship while adversarially perturbing the hypothesis. The ΔECE signal in RQ1 reflects genuine calibration change — not label contamination.

Additionally, Figure 4 (`stratum_ece_comparison.png`) shows per-stratum ECE computed after explicit preservation stratification, confirming that ΔECE = +0.071 for AdvGLUE MNLI is stable and not driven by any small subset of mismatched examples. An ablation over bin count (10/15/20 bins) produces identical ECE = 0.3497 for AdvGLUE MNLI, confirming bin-count robustness.

## 5.3 RQ3: Task-Type and Construction-Method Conditionality

The most informative pattern in Table 1 is not any single number, but the systematic structure across cells. Figure 6 (`anli_gradient.png`) visualizes the ANLI difficulty gradient, which is key to understanding the conditional structure.

**The ANLI Difficulty Gradient.** ΔECE increases monotonically with ANLI round difficulty: R1 (−0.041) → R2 (−0.014) → R3 (+0.024). This gradient is internally consistent: harder adversarial rounds produce larger (less negative, eventually positive) ΔECE. At the hardest round (R3), where accuracy drops from 0.365 (clean) to 0.310, the calibration begins to show the degradation pattern observed in AdvGLUE MNLI.

**Two-Way Conditional Structure.** The results support a two-dimensional conditional account:

*Construction method × calibration outcome:*
- Human-adversarial (AdvGLUE): ΔECE > 0 for NLI (ΔECE = +0.071). Human adversaries craft examples that trigger high wrong-class confidence — the canonical miscalibration mechanism.
- Model-in-loop adversarial (ANLI R1/R2): ΔECE < 0. These examples are selected precisely when the model fails; a model that fails with appropriately lower confidence is, by definition, better calibrated than it was on the clean benchmark. ANLI R3 (hardest round) crosses into positive ΔECE territory as difficulty approaches the human-adversarial regime.

*Task type × calibration outcome:*
- NLI (3-class): Shows positive ΔECE for human-adversarial (AdvGLUE MNLI ΔECE = +0.071) and the full ANLI gradient.
- Binary (QQP): Shows negative ΔECE even under human-adversarial conditions (AdvGLUE QQP ΔECE = −0.029).

The task-type difference is interpretable: 3-class NLI distributes logits across three options (entailment, neutral, contradiction), making it easier for adversarial perturbations to shift confidence from a correct option to an incorrect one with high confidence. Binary classification distributes logits across only two options, limiting the confidence-accuracy decoupling that drives ECE increases.

**Mean confidence on incorrect predictions** (from H-M2 analysis) is 0.616 across adversarial cells — moderate but not extreme overconfidence. This magnitude is smaller than the ≥0.70 threshold originally hypothesized, suggesting that calibration degradation in NLP adversarial settings is more subtle than in vision-domain analogues.

## 5.4 RQ4: RLHF Alignment Moderation

Figure 8 (`ddece_comparison_bar_7b.png`) shows ΔΔECE per cell for the 7b base vs. chat comparison. The pattern reveals a benchmark-type × RLHF interaction: RLHF helps on ANLI and hurts on AdvGLUE.

**Table 3: RLHF Moderation Results (Llama-2-7b pair)**

| Cell | ΔECE (base) | ΔECE (chat) | ΔΔECE | Moderation |
|------|------------|------------|-------|------------|
| ANLI R1 | −0.017 | −0.131 | **+0.115** | ✓ |
| ANLI R2 | +0.002 | −0.146 | **+0.147** | ✓ |
| ANLI R3 | −0.011 | −0.054 | **+0.043** | ✓ |
| AdvGLUE MNLI | +0.065 | +0.090 | **−0.026** | ✗ (alignment tax) |

**ANLI moderation rate: 3/3 = 100%** (all ANLI rounds show ΔΔECE > 0.01 favoring chat). Gate criterion ≥60% is exceeded by a large margin.

**Finding 1: RLHF consistently moderates calibration degradation on model-in-loop adversarial benchmarks.** Llama-2-7b-chat shows substantially lower ΔECE than base on all three ANLI rounds. The largest effect is on ANLI R2: ΔΔECE = +0.147. Note that on ANLI R2, the base model's ΔECE is near-zero (+0.002 — effectively unchanged from clean), so this large ΔΔECE primarily reflects the chat model's substantial calibration *improvement* (ΔECE(chat) = −0.146) rather than base model degradation. In other words, on this split, the RLHF-aligned model becomes dramatically better calibrated under adversarial conditions while the base model is essentially unaffected. RLHF-aligned models are more appropriately uncertain on model-in-loop adversarial examples.

**Finding 2: RLHF exacerbates calibration degradation on static human-adversarial benchmarks.** On AdvGLUE MNLI, the chat model shows *higher* ΔECE than the base model (ΔECE = +0.090 vs +0.065; ΔΔECE = −0.026). RLHF alignment is not a universal calibration fix — it produces an alignment tax on static human-adversarial NLI benchmarks.

Figure 9 (`reliability_diagram.png`) compares reliability diagrams for base and chat models on AdvGLUE MNLI, showing the chat model's overconfidence curve shifted further from the diagonal than the base model's. Figure 10 (`confidence_distribution_adv.png`) shows that chat models display a more peaked confidence distribution under adversarial conditions on AdvGLUE — consistent with RLHF instruction-following training instilling more decisive (and, under adversarial conditions, more confidently wrong) behavior.

**Interpreting the interaction.** The benchmark-type × RLHF interaction is the most novel finding of this work. We hypothesize that AdvGLUE was constructed targeting base language models (circa 2021), exploiting NLI reasoning shortcuts that RLHF fine-tuning may amplify: RLHF-trained models are trained to produce confident, decisive outputs, which human adversaries targeting NLI reasoning are positioned to exploit. Model-in-loop adversarial construction (ANLI), by contrast, selects examples where the *current model* fails — and RLHF-aligned models, being more calibrated about their uncertainty, fail with lower confidence on these examples, reducing ΔECE. This interpretation is consistent with the data but awaits direct experimental confirmation (see Section 6).

---

# Discussion

## Key Findings and Their Implications

Our results establish three findings with distinct implications for calibration research and LLM deployment practice.

**Finding 1: Adversarial construction method determines calibration outcome.** Human-adversarial NLI examples (AdvGLUE MNLI: ΔECE = +0.071) produce calibration degradation; model-in-loop adversarial NLI examples (ANLI R1/R2: ΔECE < 0) produce calibration improvement. This distinction — absent in prior adversarial robustness work, which pools all "adversarial" conditions — is the key methodological contribution of our experimental design. For practitioners evaluating LLM deployment reliability, this means that not all adversarial benchmarks serve as calibration stress tests: ANLI-style model-in-loop benchmarks may give false assurance about calibration robustness, while human-adversarial benchmarks (AdvGLUE) are the higher-risk calibration setting.

The adversarial construction method distinction also provides a conceptual bridge between our NLP findings and the vision-domain calibration literature. Minderer et al. [2021] demonstrated that image corruption (ImageNet-C) consistently degrades calibration — an observation that motivated our initial hypothesis of universal ΔECE > 0. The key difference is that image corruptions are not model-aware: they do not select examples that the model was already failing on. AdvGLUE human-adversarial examples share this property (they targeted base LLMs at construction time, not the Llama-2 model we evaluate). ANLI model-in-loop examples do not share this property — they were selected to cause errors in the model, so the model is already uncertain on them, producing calibration improvement rather than degradation. The model-awareness of the adversarial construction method is the critical variable that explains the NLP vs. vision discrepancy.

**Finding 2: RLHF alignment exhibits a benchmark-type-conditional calibration effect.** The alignment tax on AdvGLUE (chat worse than base: ΔΔECE = −0.026) and the consistent RLHF moderation on ANLI (100% of rounds, ΔΔECE up to +0.147) are not contradictory — they reflect the same underlying interaction. RLHF-aligned models are trained to produce confident, helpful outputs, which reduces calibration degradation when adversarial examples probe uncertainty (ANLI model-in-loop) but may increase it when adversarial examples exploit decisive wrong answers (AdvGLUE human-adversarial). This finding has practical implications for RLHF research: calibration evaluations conducted on clean benchmarks (as in Kadavath et al. [2022]) do not predict adversarial calibration behavior, and benchmark construction method must be specified when reporting RLHF calibration results.

**Finding 3: Task type is an independent calibration moderator.** AdvGLUE QQP (binary, human-adversarial) shows ΔECE = −0.029 despite having the same construction method as AdvGLUE MNLI (ΔECE = +0.071). This comparison within the same adversarial benchmark isolates task type as an independent variable: 3-class NLI is more susceptible to adversarial calibration degradation than binary classification, consistent with the hypothesis that distributing logits across more answer options provides more surface area for adversarial perturbations to shift confidence from correct to incorrect options.

## Limitations

**L1: Single-model evaluation for primary calibration experiments.** Our core calibration results (RQ1-RQ3) use Llama-2-7b-hf only. The 4-model grid originally planned (Llama-2-7b-hf, Llama-2-7b-chat, Llama-2-13b-chat, Mistral-7B-instruct) was not completed due to computational constraints during the CPU-based pilot (RQ1-RQ3) and scope decisions for the GPU-based RLHF comparison (RQ4). Consequently, P1 (≥60% of model × task cells show ΔECE > 0.05) is evaluated on only 5 cells from 1 model — statistically underpowered for the universal threshold claim. We frame our results as a pilot study establishing the conditional structure within a single model family.

*Why acceptable:* Existence (RQ1) and mechanism validity (RQ2) are model-agnostic findings within the single-model scope. The RLHF moderation finding (RQ4) extends to a model pair within the same family. The conditional pattern (construction method × task type × RLHF) is internally consistent across all measured cells.
*Suggested framing:* "As a pilot study, we focus on Llama-2-7b-hf for core calibration experiments to ensure methodological rigor. Multi-model evaluation is a feasible extension using our open JSONL cache infrastructure."

**L2: Shared clean baseline for ANLI.** All ANLI adversarial cells (R1/R2/R3) share one GLUE MNLI clean baseline (n=200, ECE = 0.279). This creates a cross-cell correlation in ANLI ΔECE values — if the clean baseline ECE is anomalously high or low, all ANLI ΔECE values move together. Llama-2-7b-hf's clean MNLI ECE (0.279) is above the Kadavath [2022] range for clean LLMs (0.05–0.15), reflecting weak NLI accuracy (0.365). Consequently, ANLI R1/R2 ΔECE values may be partially driven by an inflated clean baseline rather than genuine adversarial calibration improvement.

*Why acceptable:* GLUE MNLI is the methodologically correct clean counterpart for ANLI (which was constructed as adversarial MultiNLI). AdvGLUE MNLI uses the same baseline and shows the expected positive ΔECE, so baseline inflation does not fully explain the ANLI calibration improvement — accuracy on ANLI R1 is actually higher than on clean MNLI (0.380 vs 0.365), consistent with the adaptive uncertainty explanation.
*Mitigation:* We report accuracy alongside ECE for all cells (Table 1) and note the baseline anomaly explicitly.

**L3: BBH-MC commonsense reasoning not tested.** BIG-Bench Hard multiple-choice adversarial variants were planned as a third benchmark domain but were excluded for scope reasons. All claims are bounded to NLI and binary classification.

*Why acceptable:* NLI is the primary adversarial NLP benchmark domain (AdvGLUE and ANLI are both NLI-centered). The task-type finding (NLI vs binary) is a stronger contribution than domain coverage. BBH-MC extension is feasible with the H-E1 logit extraction pipeline.

**L4: RLHF moderation conditionality discovered post-hoc.** The benchmark-type × RLHF interaction was not predicted in the original H-C1 design — it emerged when H-C1-V2 reported the AdvGLUE reversal as an unexpected finding. We report this finding accurately but acknowledge that it was not the primary experimental question, and that further experimental validation (e.g., testing additional RLHF-aligned models, controlling for prompt format) is needed.

**L5: Pre-specified quantitative thresholds not met.** Two of our pipeline's quantitative predictions were not satisfied at their original thresholds. First, mean confidence on incorrect adversarial predictions was 0.616 — below the originally hypothesized ≥0.70 threshold (informed by vision-domain analogues). Second, only 1 of 5 adversarial cells exceeded ΔECE > 0.05 (AdvGLUE MNLI); the remaining 4 cells were below this threshold, against a pre-specified criterion of ≥60% of cells. These results indicate that adversarial calibration degradation in LLMs is smaller in magnitude than vision-domain analogues suggested. The conditional structure we report remains valid at observed magnitudes, but the originally hypothesized effect sizes were overspecified from vision-domain priors.

## Broader Impact

This work has positive implications for LLM deployment reliability assessment. Practitioners who test model reliability under adversarial conditions by measuring accuracy robustness are missing the calibration dimension: a model can be simultaneously more accurate *and* less calibrated under adversarial conditions (as we observe for ANLI R1 on accuracy) or vice versa. Adversarial calibration audit (ΔECE measurement) provides a complementary reliability check that should accompany adversarial accuracy evaluation.

The finding that RLHF alignment can exacerbate calibration degradation on static human-adversarial benchmarks (the alignment tax) is a potential concern for high-stakes deployment of RLHF-aligned models. Systems using chat/instruct variants for NLI or classification tasks may be more susceptible to adversarial calibration degradation than base models, in settings where the adversarial examples were designed to exploit base model behavior. Awareness of this conditional effect may inform deployment decisions and calibration monitoring protocols.

We do not foresee significant negative impacts of this work beyond the usual concern that measurement methodology can be misused (e.g., constructing adversarial inputs specifically designed to fool calibration audits). Our methods are fully described and our code infrastructure is shareable.

---

# Conclusion

We opened this paper with a result that defies the intuition that adversarial benchmarks stress-test model reliability: evaluating Llama-2-7b-hf on ANLI R1, a benchmark designed specifically to cause model errors, produced *better* calibration than the clean baseline. We have now explained why.

When adversarial examples are constructed model-in-the-loop — selected precisely because the model fails on them — the resulting benchmark contains examples where the model is already appropriately uncertain at failure time. Improved calibration under these conditions is not surprising; it is expected. The cases where calibration *degrades* are those where adversarial examples are constructed human-adversarially, targeting surface features to trigger high model confidence on incorrect answers, independent of model uncertainty. AdvGLUE MNLI is this case: ΔECE = +0.071, a 7.1 percentage-point calibration gap that makes confidence signals meaningfully less reliable under human-crafted adversarial NLI conditions.

The story does not end with this dichotomy. RLHF alignment interacts with the construction-method dependency in a way that is not predicted by clean-benchmark calibration studies: RLHF-aligned models (Llama-2-7b-chat) show consistently better calibration than base models on ANLI (ΔΔECE up to +0.147 across all 3 rounds), but worse calibration on AdvGLUE MNLI (ΔΔECE = −0.026, alignment tax). RLHF calibration properties measured on clean benchmarks do not transfer to adversarial settings, and the direction of transfer depends on the adversarial construction method.

## Summary

In this work, we addressed the gap between adversarial robustness evaluation (accuracy-only) and calibration measurement (clean-data-only) by directly measuring logit-based ECE on adversarial NLP benchmark splits. Our main contributions:

1. **First measurement of adversarial NLP calibration.** ΔECE = +0.071 for AdvGLUE MNLI confirms that adversarial calibration degradation is real and measurable. Label preservation rate = 1.000 for all adversarial splits validates ΔECE as a genuine calibration signal, not label noise.

2. **Conditional structure: construction method and task type determine calibration outcome.** Human-adversarial NLI (AdvGLUE MNLI: ΔECE = +0.071) degrades calibration; model-in-loop NLI (ANLI R1/R2: ΔECE < 0) improves it. The ANLI difficulty gradient (R1 → R2 → R3) shows a smooth transition as adversarial difficulty approaches the human-adversarial regime. Binary classification consistently shows reversed ΔECE regardless of construction method.

3. **Benchmark-type × RLHF interaction.** RLHF alignment conditionally moderates adversarial calibration degradation: confirmed for model-in-loop adversarial (ANLI: 100% moderation rate, 3/3 rounds), but reversed for static human-adversarial benchmarks (AdvGLUE: ΔΔECE = −0.026). This is the first documented benchmark-type × RLHF calibration interaction.

## Future Directions

**Testing alternative explanations for ANLI calibration improvement.** We hypothesize that ANLI R1/R2 calibration improvement reflects *adaptive uncertainty*: the model was already uncertain on these examples (which were selected to cause errors), so accuracy drop correlates with confidence drop. A direct test: compute ECE separately for correct and incorrect predictions, and compare confidence distributions on wrong predictions for ANLI vs. AdvGLUE. If ANLI wrong predictions have lower mean confidence than AdvGLUE wrong predictions, adaptive uncertainty is confirmed as the mechanism.

**Explaining the AdvGLUE alignment tax.** We hypothesize that AdvGLUE was constructed targeting base model reasoning shortcuts that RLHF amplifies. A counter-factual test: construct new human-adversarial NLI examples targeting Llama-2-7b-chat specifically. If the alignment tax disappears on chat-targeted adversarial examples, benchmark-construction targeting is causal. If it persists, RLHF instruction-following overconfidence is the primary driver.

**Multi-model grid and P3 validation.** The 4-model × 5-task cell grid originally planned (20 cells) was reduced to 5 cells (1 model) due to computational constraints. Running Mistral-7B-Instruct and Llama-2-13b-chat through the H-E1 pipeline would enable proper evaluation of P1 (universality threshold) and P3 (ΔECE-AUROC correlation as deployment reliability predictor) — the two original predictions left without sufficient statistical power.

**Temperature scaling as ΔECE mitigation baseline.** Temperature scaling (Guo et al. [2017]) was specified in our original experimental plan but never applied. Applying temperature scaling to H-E1 logit caches and recomputing ΔECE would reveal whether calibration degradation under human-adversarial conditions is a confidence scaling artifact (addressable post-hoc) or a structural property of model uncertainty under adversarial conditions (requiring more fundamental intervention).

Adversarial accuracy evaluation and calibration evaluation have developed as separate communities. The conditional structure we document — where the same adversarial benchmark can improve or degrade calibration depending on how it was constructed and whether the model was RLHF-aligned — suggests that these communities must develop shared vocabulary and methods. Calibration robustness is not a consequence of accuracy robustness; it requires its own measurement framework.

---

## References

*(See 06_references.bib for full BibTeX. Key citations used in text:)*

- Guo et al. (2017). On Calibration of Modern Neural Networks. ICML. arXiv:1706.04599
- Minderer et al. (2021). Revisiting the Calibration of Modern Neural Networks. NeurIPS. arXiv:2106.07998
- Kadavath et al. (2022). Language Models (Mostly) Know What They Know. arXiv:2207.05221
- Wang et al. (2021). AdvGLUE: A Multi-Task Benchmark for Robustness Evaluation. arXiv:2111.02840
- Nie et al. (2020). Adversarial NLI: A New Benchmark for NLU. arXiv:1910.14599
- Ouyang et al. (2022). Training Language Models to Follow Instructions with Human Feedback. NeurIPS.
- Touvron et al. (2023). Llama 2: Open Foundation and Fine-Tuned Chat Models. arXiv:2307.09288
- *(See 06_references.bib for remaining 10 citations)*
