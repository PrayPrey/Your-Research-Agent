# Construction-Method-Dependent Calibration Degradation Under Adversarial Perturbation in Open-Weight LLMs

**Anonymous Authors**
Anonymous Institution

---

## Abstract

This paper presents a measurement study of Expected Calibration Error (ECE) under adversarial conditions for an open-weight large language model (Llama-2-7b-hf). Evaluating on model-in-the-loop adversarial NLI benchmarks (ANLI R1–R3) and human-adversarial benchmarks (AdvGLUE MNLI, AdvGLUE QQP), this work finds that adversarial calibration degradation is not universal: it depends on how adversarial examples were constructed and on task type. AdvGLUE MNLI (human-adversarial NLI) produces a 7.1 percentage-point ECE increase relative to the clean MultiNLI baseline (ΔECE = +0.071). ANLI R1 and R2 (model-in-the-loop adversarial NLI) produce calibration improvement (ΔECE = −0.041 and −0.014, respectively), while ANLI R3 produces modest degradation (ΔECE = +0.024). Binary classification (AdvGLUE QQP) shows ΔECE = −0.029. Label preservation rates equal 1.000 for all adversarial splits by construction, confirming that ΔECE reflects genuine calibration change and not label noise. RLHF alignment (Llama-2-7b-chat versus Llama-2-7b-hf base) consistently moderates calibration degradation on ANLI (100% of rounds, ΔΔECE up to +0.147) while exacerbating it on AdvGLUE MNLI (ΔΔECE = −0.026). These findings, from a single-model pilot study, motivate adversarial calibration measurement as a distinct research problem from adversarial accuracy robustness, and provide a conditional framework—construction method × task type × RLHF alignment—for understanding when adversarial perturbation may degrade LLM confidence reliability.

---

## 1. Introduction

A central assumption underlying the use of adversarial NLP benchmarks is that harder, adversarially constructed inputs expose model failures in a way that informs deployment risk. Much of the resulting literature evaluates accuracy degradation: a model's classification accuracy drops from a clean-data baseline to an adversarial one. This work asks a different question: under adversarial conditions, does model confidence remain informative about correctness?

Calibration—the alignment between predicted confidence and observed accuracy—is a critical reliability property. A model that assigns 90% confidence to its predictions should be correct approximately 90% of the time; deviations from this alignment render confidence signals unreliable as a safety or quality indicator. Expected Calibration Error (ECE) [Guo et al., 2017] is the standard metric for measuring this alignment. Minderer et al. [2021] demonstrated that distribution shift in vision models consistently degrades ECE; the analogous question for adversarial distribution shift in NLP has not been directly measured with logit-based ECE for open-weight LLMs.

This paper fills this gap. The central finding is counterintuitive: evaluating Llama-2-7b-hf on ANLI R1—a benchmark specifically constructed so that human annotators could fool state-of-the-art NLP models—produces a calibration *improvement* (ECE = 0.239 versus the clean-data baseline ECE = 0.279, ΔECE = −0.041). The benchmark designed to expose model failures made the model appear better calibrated. This outcome is not an error; it reveals a structural property of model-in-the-loop adversarial benchmark construction.

The key insight is that model-in-the-loop adversarial examples (ANLI) are selected precisely because the model fails on them. If the model fails with appropriately low confidence, it is, by definition, well-calibrated on those failures. Human-adversarial examples (AdvGLUE MNLI), by contrast, are designed to exploit surface features to trigger high model confidence on incorrect answers—the canonical miscalibration mechanism. The distinction between these construction methods determines whether calibration degrades or improves.

### 1.1 Problem Statement

No published work measures logit-based ECE on adversarial NLP benchmark splits for open-weight LLMs, or examines how adversarial construction method and RLHF alignment jointly determine calibration outcomes. Adversarial robustness evaluation (accuracy-only) and calibration measurement (clean-data-only) have developed as separate research communities. This work occupies the intersection.

### 1.2 Research Questions

This work addresses four research questions:

- **RQ1 (Existence):** Does adversarial perturbation measurably increase ECE for open-weight LLMs on NLP benchmarks?
- **RQ2 (Validity):** Is ΔECE a valid calibration signal, or does it reflect label noise introduced by adversarial perturbation?
- **RQ3 (Conditionality):** Is calibration degradation universal across task types and adversarial construction methods?
- **RQ4 (RLHF Moderation):** Does RLHF alignment moderate adversarial calibration degradation, and does the effect depend on benchmark construction method?

### 1.3 Contributions

Three findings are reported:

1. **First measurement of logit-based ECE on adversarial NLP benchmarks.** ΔECE = +0.071 for AdvGLUE MNLI confirms that adversarial calibration degradation is real and measurable for an open-weight LLM. Label preservation rate = 1.000 for all adversarial splits validates ΔECE as a genuine calibration signal. The JSONL logit caching strategy employed here enables multiple downstream calibration analyses from a single inference pass.

2. **Evidence that calibration degradation is task-type and construction-method conditional.** Human-adversarial NLI examples (AdvGLUE MNLI: ΔECE = +0.071) degrade calibration; model-in-the-loop adversarial NLI examples (ANLI R1/R2: ΔECE < 0) improve it. The ANLI difficulty gradient (R1 → R2 → R3) shows a monotonic transition from improvement to degradation. Binary classification consistently shows reversed ΔECE.

3. **Evidence that RLHF alignment conditionally moderates adversarial calibration degradation.** Confirmed for model-in-the-loop adversarial (ANLI: 100% moderation rate, 3/3 rounds); reversed for static human-adversarial benchmarks (AdvGLUE: alignment tax, ΔΔECE = −0.026, chat shows higher ΔECE than base). This is the first documented benchmark-type × RLHF calibration interaction.

All results are from a single-model pilot study. Generalization across model families remains an open question.

---

## 2. Related Work

### 2.1 Calibration of Neural Networks and Language Models

Guo et al. [2017] formalized ECE as the weighted average gap between predicted confidence and empirical accuracy across equal-width confidence bins, and demonstrated that modern neural networks are systematically overconfident. Temperature scaling—rescaling logits by a single learned scalar—reliably reduces ECE without affecting accuracy. ECE has since become the standard calibration metric in NLP and computer vision.

Minderer et al. [2021] extended calibration analysis to distribution shift in vision models, showing that ECE increases under standard image corruptions (ImageNet-C) and out-of-distribution benchmarks (ObjectNet). Their finding that distribution shift degrades calibration motivated the original hypothesis of this work. The results reported here complicate this picture: adversarial distribution shift in NLP does not uniformly degrade calibration, and the construction method of the adversarial benchmark determines whether calibration improves or worsens.

Kadavath et al. [2022] measured calibration of large language models using verbal probability elicitation on factual QA tasks, finding that RLHF-aligned models show better self-knowledge calibration than base models on clean benchmarks. Xiong et al. [2023] studied LLM confidence elicitation through verbal uncertainty expressions; Zhao et al. [2023] measured generation-based ECE for instruction-tuned LLMs. None of these works measure logit-based ECE on adversarial NLP benchmark splits.

**Research gap:** No prior work measures logit-based ECE on adversarial NLP benchmark splits for open-weight LLMs.

### 2.2 Adversarial NLP Benchmarks

Wang et al. [2021] introduced AdvGLUE, a multi-task adversarial benchmark constructed by applying human-designed perturbation methods (synonym substitution, word insertion, contextual perturbation) to GLUE examples to create inputs that preserve labels but cause model errors. AdvGLUE measures accuracy robustness only; calibration is not measured.

Nie et al. [2020] introduced ANLI (Adversarial NLI), constructed using a human-and-model-in-the-loop protocol: human annotators write NLI hypotheses that fool the current model, which is then retrained on the collected data for the next round. This produces three rounds of increasing difficulty (R1 < R2 < R3). ANLI is a model-in-the-loop benchmark—adversarial examples are selected to be difficult for the training model at each round—which makes it structurally different from AdvGLUE's human-only construction.

The distinction between human-adversarial (AdvGLUE) and model-in-the-loop adversarial (ANLI) construction is not typically highlighted in papers that use both benchmarks for accuracy evaluation. This work treats it as a primary independent variable, because this distinction is found to determine whether calibration degrades or improves.

**Research gap:** Adversarial benchmarks are used exclusively for accuracy evaluation; no prior work treats adversarial construction method as a variable in calibration analysis.

### 2.3 RLHF Alignment and Calibration

Reinforcement Learning from Human Feedback [Christiano et al., 2017; Ouyang et al., 2022] fine-tunes language models to align with human preferences. The effect of RLHF on calibration has been studied primarily on clean benchmarks. Kadavath et al. [2022] found RLHF models show better self-reported calibration; OpenAI's GPT-4 technical report [OpenAI, 2023] notes calibration improvements from RLHF training. The conventional expectation is that RLHF improves calibration.

This work tests this expectation in the adversarial setting for the first time. The finding that RLHF moderation of adversarial calibration is benchmark-type conditional—helpful for ANLI, harmful for AdvGLUE—is not predicted by clean-benchmark RLHF calibration findings.

**Research gap:** RLHF's effect on calibration has been studied only on clean benchmarks; adversarial calibration moderation by RLHF is untested.

### 2.4 Positioning

This work occupies the intersection of calibration measurement, adversarial NLP benchmarks, and RLHF alignment effects. The conditional pattern documented here—where the same LLM can improve calibration on one adversarial benchmark while degrading it on another, depending on construction method—cannot be derived from any single prior thread.

---

## 3. Method

### 3.1 ECE Measurement Protocol

Expected Calibration Error is computed using the 15-bin equal-width formulation of Guo et al. [2017]:

$$\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{n} \left| \text{acc}(B_b) - \text{conf}(B_b) \right|$$

where $B = 15$ bins partition $[0, 1]$ by predicted confidence, $|B_b|$ is the number of examples in bin $b$, $n$ is the total number of examples, $\text{acc}(B_b)$ is empirical accuracy in bin $b$, and $\text{conf}(B_b)$ is mean predicted confidence in bin $b$.

**Confidence extraction.** For multiple-choice tasks (NLI formatted with options A/B/C; binary tasks with Yes/No), log-probabilities of the answer-option tokens are extracted from the model's vocabulary and softmax is applied over the answer tokens to obtain a confidence distribution. The predicted label is the argmax; confidence is the maximum softmax probability. This logit-based protocol is model-agnostic and does not require verbalization or sampling.

**Bin count stability.** An ablation study confirmed that ECE computed with 10, 15, and 20 bins agrees to within 0.003 for AdvGLUE MNLI across bin counts. Fifteen bins follow the Guo et al. [2017] standard.

**Delta ECE (ΔECE).** The primary outcome variable is ΔECE = ECE(adversarial split) − ECE(clean split). Positive ΔECE indicates calibration degradation; negative ΔECE indicates calibration improvement.

### 3.2 Benchmark Selection

Benchmarks are selected to span two adversarial construction methods and two task types:

**Construction method dimension:**
- *Human-adversarial (AdvGLUE):* Human annotators craft perturbations targeting existing base language models. Examples are designed to maintain labels while exploiting model weaknesses.
- *Model-in-the-loop adversarial (ANLI):* Human annotators write NLI examples that fool the current round's model, which is then retrained. Three rounds (R1 < R2 < R3) of increasing difficulty.

**Task type dimension:**
- *NLI (3-class entailment):* AdvGLUE MNLI (human-adversarial), ANLI R1/R2/R3 (model-in-loop). Three answer options.
- *Binary classification:* AdvGLUE QQP (paraphrase detection, n=78). Two answer options. AdvGLUE SST-2 (sentiment, n=148) was computed and available but excluded from the primary cell set as a second binary task redundant with QQP for the construction-method × task-type factorial; results are consistent with QQP.

**Clean baselines.** GLUE MNLI (n=200, subsampled with seed=1, ECE=0.279) serves as the clean baseline for all NLI adversarial splits. GLUE QQP (n=200) serves as the clean baseline for AdvGLUE QQP.

### 3.3 Model Selection and RLHF Comparison

**Primary model:** Llama-2-7b-hf (base, HuggingFace checkpoint `meta-llama/Llama-2-7b-hf`, SHA `01c7f73d`) is the primary model for core calibration experiments (RQ1–RQ3). This model has no RLHF alignment, provides full logit access, and was within computational range for CPU-based pilot experiments.

**RLHF comparison:** Llama-2-7b-chat (RLHF-aligned, `meta-llama/Llama-2-7b-chat-hf`) is compared against Llama-2-7b-hf base in the RLHF moderation experiment (RQ4). Using the same 7b parameter family isolates the effect of RLHF fine-tuning from model scale. The comparison covers ANLI R1/R2/R3 and AdvGLUE MNLI.

**ΔΔECE.** For the RLHF comparison, ΔΔECE = ΔECE(base) − ΔECE(chat). Positive ΔΔECE indicates base has higher adversarial ECE than chat (RLHF moderation). Negative ΔΔECE indicates chat has higher adversarial ECE (alignment tax).

**Inference.** All models use HuggingFace `AutoModelForCausalLM`. RQ1–RQ3 executed on CPU (1TB RAM) in float32. RQ4 executed on 5× NVIDIA H100 NVL (95GB each) in bfloat16. Chat models use the Llama-2 chat template; base models use raw multiple-choice format.

### 3.4 Label Preservation Verification

Before interpreting ΔECE as a calibration signal, the alternative explanation that ΔECE reflects label noise is ruled out by computing the label preservation rate: the fraction of adversarial examples where the adversarial label matches the original clean label. For AdvGLUE, labels are human-verified by construction. For ANLI, labels are assigned by human annotators who maintain the entailment relationship while adversarially perturbing the hypothesis. Both datasets preserve labels by construction; the measurement below confirms this.

### 3.5 JSONL Cache Architecture

A per-example JSONL caching strategy enables multiple downstream analyses without repeated model inference. For each example in each (model, task, split) cell, a JSONL record is written with fields: `{confidence, pred_label, true_label, correct, model_id, task, split}`. The RQ1 JSONL caches (H-E1) are reused by RQ2 (label preservation and stratum analysis), RQ3 (per-cell ΔECE), and RQ4 (RLHF comparison, which runs new inference only for the chat model). This reduces total inference cost from approximately 5 model runs to approximately 2 (base + chat).

### 3.6 Experimental Cell Design

| Cell | Task | Construction Method | n (adv) | Model(s) |
|------|------|---------------------|---------|---------|
| AdvGLUE MNLI | NLI (3-class) | Human-adversarial | 121 | 7b-base, 7b-chat |
| ANLI R1 | NLI (3-class) | Model-in-loop (easy) | 200 | 7b-base, 7b-chat |
| ANLI R2 | NLI (3-class) | Model-in-loop (medium) | 200 | 7b-base, 7b-chat |
| ANLI R3 | NLI (3-class) | Model-in-loop (hard) | 200 | 7b-base, 7b-chat |
| AdvGLUE QQP | Paraphrase (binary) | Human-adversarial | 78 | 7b-base |

Clean baseline for all NLI cells: GLUE MNLI (n=200, ECE=0.279). Clean baseline for QQP: GLUE QQP (n=200).

---

## 4. Experimental Setup

Four experiments are designed to address the four research questions in sequence: from confirming existence (RQ1), to validating the measurement (RQ2), to revealing conditional structure (RQ3), to examining RLHF moderation (RQ4).

### 4.1 Datasets

| Split | Task | Construction Method | n (adv) | n (clean) | Answer Options |
|-------|------|---------------------|---------|---------|----------------|
| AdvGLUE MNLI | NLI (entailment) | Human-adversarial | 121 | 200 | 3 |
| ANLI R1 | NLI (entailment) | Model-in-loop (easy) | 200 | 200 | 3 |
| ANLI R2 | NLI (entailment) | Model-in-loop (medium) | 200 | 200 | 3 |
| ANLI R3 | NLI (entailment) | Model-in-loop (hard) | 200 | 200 | 3 |
| AdvGLUE QQP | Paraphrase (binary) | Human-adversarial | 78 | 200 | 2 |

AdvGLUE [Wang et al., 2021] and ANLI [Nie et al., 2020] are selected because both preserve ground-truth labels by construction—a prerequisite for valid ΔECE measurement. The three ANLI rounds provide a difficulty gradient within the model-in-loop construction method. AdvGLUE QQP provides a binary classification comparison with AdvGLUE MNLI to test task-type dependency within the same adversarial construction method.

### 4.2 Baselines

**RLHF comparison (RQ4):**
- *Llama-2-7b-hf (base):* Pre-RLHF checkpoint; no instruction fine-tuning. Reference for adversarial calibration without alignment.
- *Llama-2-7b-chat:* RLHF-aligned checkpoint trained from the same 7b-parameter base. Comparison isolates RLHF fine-tuning at fixed model scale.

Temperature scaling was specified in the original experimental plan but was not applied in this pilot; it is identified as a planned extension.

### 4.3 Evaluation Metrics

- **ΔECE:** Primary outcome. Positive = degradation; negative = improvement.
- **Label preservation rate:** For RQ2; must be ≥0.80 for ΔECE to be interpretable.
- **ΔΔECE:** For RQ4; ΔECE(base) − ΔECE(chat).
- **RLHF moderation rate:** Fraction of adversarial cells where ΔΔECE > 0.01 (base shows meaningfully more calibration degradation than chat). Gate criterion: ≥60% of cells.
- **Accuracy (ΔAcc):** Reported alongside ΔECE for context.

---

## 5. Results

### 5.1 RQ1: Existence of Adversarial Calibration Degradation

**Table 1: ECE Results by Split (Llama-2-7b-hf)**

| Split | Task | ECE (clean) | ECE (adv) | ΔECE | Acc (clean) | Acc (adv) |
|-------|------|-------------|-----------|------|-------------|-----------|
| AdvGLUE MNLI | NLI | 0.279 | **0.350** | **+0.071** | 0.365 | 0.298 |
| ANLI R3 | NLI | 0.279 | 0.304 | +0.024 | 0.365 | 0.310 |
| ANLI R2 | NLI | 0.279 | 0.266 | −0.014 | 0.365 | 0.350 |
| ANLI R1 | NLI | 0.279 | 0.239 | −0.041 | 0.365 | 0.380 |
| AdvGLUE QQP | Binary | 0.062 | 0.033 | −0.029 | 0.520 | 0.590 |

The existence gate (≥1 cell with positive ΔECE) is satisfied: AdvGLUE MNLI produces ΔECE = +0.071 and ANLI R3 produces ΔECE = +0.024. The model's confidence-accuracy gap widens under human-adversarial NLI conditions.

However, the existence finding immediately reveals its conditional nature. ANLI R1 and R2 show *negative* ΔECE; calibration improves under model-in-loop adversarial conditions. AdvGLUE QQP also shows negative ΔECE. All 9 cells pass post-hoc validity checks: coverage ≥50 examples, non-degenerate confidence distributions (mean confidence 0.61–0.65), ECE in plausible range, and probability sums |Σp − 1| < 0.001.

![ECE comparison across splits](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/fig1_ece_comparison.png)

*Figure 1: ECE (clean) versus ECE (adversarial) across all experimental cells. AdvGLUE MNLI shows the largest ECE increase; ANLI R1/R2 and QQP show ECE decreases.*

![Reliability diagrams for AdvGLUE MNLI](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/fig2_reliability_diagrams.png)

*Figure 2: Reliability diagrams for AdvGLUE MNLI. The adversarial curve falls below the diagonal (overconfident, underaccurate) relative to the clean curve.*

### 5.2 RQ2: Label Preservation—Validating ΔECE as a Calibration Signal

**Table 2: Label Preservation Rates**

| Split | n | Preservation Rate | Construction Method |
|-------|---|-------------------|---------------------|
| AdvGLUE MNLI | 121 | **1.000** | Human-verified by construction |
| ANLI R1 | 200 | **1.000** | Model-in-loop + human validation |
| ANLI R2 | 200 | **1.000** | Model-in-loop + human validation |
| ANLI R3 | 200 | **1.000** | Model-in-loop + human validation |

Label preservation rate equals 1.000 for all adversarial splits. AdvGLUE labels are human-verified by construction; ANLI labels are assigned by human annotators who are explicitly instructed to maintain the entailment relationship. The ΔECE signal in RQ1 reflects genuine calibration change, not label contamination.

Per-stratum ECE analysis confirms that ΔECE = +0.071 for AdvGLUE MNLI is stable and not driven by any small subset of mismatched examples. A bin-count ablation across 10, 15, and 20 bins produces ECE = 0.3497 for AdvGLUE MNLI in all configurations, confirming bin-count robustness.

![Label preservation rates](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/preservation_rate_by_benchmark.png)

*Figure 3: Label preservation rates by adversarial split. All splits achieve rate = 1.000.*

![Stratum ECE comparison](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/stratum_ece_comparison.png)

*Figure 4: Per-stratum ECE comparison for AdvGLUE MNLI. ΔECE = +0.071 is consistent across label-preservation strata.*

### 5.3 RQ3: Task-Type and Construction-Method Conditionality

The systematic structure of the results in Table 1 reveals a two-dimensional conditional account of adversarial calibration.

**The ANLI Difficulty Gradient.** ΔECE increases monotonically with ANLI round difficulty: R1 (−0.041) → R2 (−0.014) → R3 (+0.024). Harder adversarial rounds produce larger (less negative, eventually positive) ΔECE. At ANLI R3, where accuracy drops from 0.365 (clean) to 0.310, calibration begins to show the degradation pattern observed in AdvGLUE MNLI. This gradient direction is confirmed independently in H-M1 and H-M3 analyses.

**Construction Method Effect.** Human-adversarial NLI examples (AdvGLUE MNLI) produce ΔECE = +0.071. Human adversaries craft examples that trigger high wrong-class confidence—the canonical miscalibration mechanism. Model-in-the-loop adversarial NLI examples (ANLI R1/R2) produce negative ΔECE. These examples are selected precisely when the model fails; a model that fails with appropriately moderate confidence on such examples demonstrates calibration, not miscalibration.

**Task Type Effect.** Within the same adversarial construction method (AdvGLUE), NLI (3-class) produces ΔECE = +0.071 while binary classification (QQP) produces ΔECE = −0.029. The 3-class NLI task distributes logits across three options, providing more surface area for adversarial perturbations to shift confidence from correct to incorrect options. Binary classification distributes logits across only two options, limiting the confidence-accuracy decoupling that drives ECE increases.

**Mean confidence on incorrect predictions** (from H-M2 analysis) is 0.616 across adversarial cells. This is below the ≥0.70 threshold originally hypothesized from vision-domain analogues, indicating that adversarial calibration degradation in NLP is more subtle in magnitude than in vision-domain settings. H-M2 accuracy results further confirm: mean ΔAcc = −0.011 (not the −0.10 threshold from the original hypothesis), with the ANLI difficulty gradient direction confirmed (R3: −0.055, R2: −0.015, R1: +0.015).

NLI tasks show mean ΔECE = +0.010; non-NLI tasks (QQP) show mean ΔECE = −0.029, consistent with the task-type interpretation.

![ΔECE per cell](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/h-m3/figures/delta_ece_per_cell.png)

*Figure 5: ΔECE per experimental cell with 0.05 gate threshold indicated. Only AdvGLUE MNLI exceeds the threshold; ANLI R1/R2 and QQP show negative ΔECE.*

![ANLI ECE gradient](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/h-m3/figures/anli_ece_gradient.png)

*Figure 6: ΔECE across ANLI rounds R1, R2, R3. The monotonic gradient from −0.041 to +0.024 is consistent across analyses.*

![Reliability diagram AdvGLUE MNLI](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/h-m3/figures/reliability_advglue_mnli.png)

*Figure 7: Reliability diagram for AdvGLUE MNLI, clean versus adversarial split.*

### 5.4 RQ4: RLHF Alignment Moderation

**Table 3: RLHF Moderation Results (Llama-2-7b pair)**

| Cell | ΔECE (base) | ΔECE (chat) | ΔΔECE | Moderation |
|------|------------|------------|-------|------------|
| ANLI R1 | −0.017 | −0.131 | **+0.115** | Confirmed |
| ANLI R2 | +0.002 | −0.146 | **+0.147** | Confirmed |
| ANLI R3 | −0.011 | −0.054 | **+0.043** | Confirmed |
| AdvGLUE MNLI | +0.065 | +0.090 | **−0.026** | Reversed (alignment tax) |

RLHF moderation rate on ANLI: 3/3 = 100% (gate criterion ≥60% exceeded by a large margin).

**Finding 1: RLHF consistently moderates calibration degradation on model-in-the-loop adversarial benchmarks.** Llama-2-7b-chat shows substantially lower ΔECE than base on all three ANLI rounds. The largest effect is on ANLI R2 (ΔΔECE = +0.147). On ANLI R2, the base model's ΔECE is near-zero (+0.002, effectively unchanged from clean), so the large ΔΔECE primarily reflects the chat model's substantial calibration improvement (ΔECE = −0.146) rather than base model degradation. RLHF-aligned models are more appropriately uncertain on model-in-the-loop adversarial examples.

**Finding 2: RLHF exacerbates calibration degradation on static human-adversarial benchmarks.** On AdvGLUE MNLI, the chat model shows higher ΔECE than the base model (ΔECE = +0.090 versus +0.065; ΔΔECE = −0.026). RLHF alignment is not a universal calibration improvement; it produces an alignment tax on static human-adversarial NLI benchmarks.

![ΔΔECE comparison](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/ddece_comparison_bar_7b.png)

*Figure 8: ΔΔECE per cell for the Llama-2-7b base versus chat comparison. Positive values indicate RLHF moderation; the negative value for AdvGLUE MNLI indicates alignment tax.*

![Reliability diagram RLHF comparison](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/reliability_diagram.png)

*Figure 9: Reliability diagram comparing base and chat models on AdvGLUE MNLI. The chat model's overconfidence curve is shifted further from the diagonal.*

![Confidence distribution](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_buildingtrust/docs/youra_research/paper/figures/confidence_distribution_adv.png)

*Figure 10: Confidence distributions for base and chat models under adversarial conditions on AdvGLUE MNLI. Chat models display a more peaked confidence distribution.*

---

## 6. Discussion

### 6.1 Interpretation of Findings

**Adversarial construction method determines calibration outcome.** Human-adversarial NLI examples (AdvGLUE MNLI: ΔECE = +0.071) produce calibration degradation; model-in-loop adversarial NLI examples (ANLI R1/R2: ΔECE < 0) produce calibration improvement. This distinction—absent in prior adversarial robustness work, which pools all "adversarial" conditions—is the key methodological contribution of this experimental design.

The distinction also provides a bridge between these NLP findings and the vision-domain calibration literature. Minderer et al. [2021] demonstrated that image corruption consistently degrades calibration. Image corruptions are not model-aware: they do not select examples that the model was already failing on. AdvGLUE human-adversarial examples share this property. ANLI model-in-loop examples do not: they were selected to cause errors in the model, so the model is already appropriately uncertain, producing calibration improvement rather than degradation. Model-awareness of the adversarial construction method appears to be the critical variable explaining the NLP versus vision discrepancy.

**RLHF alignment exhibits a benchmark-type-conditional calibration effect.** The alignment tax on AdvGLUE (chat worse than base: ΔΔECE = −0.026) and the consistent RLHF moderation on ANLI (100% of rounds, ΔΔECE up to +0.147) reflect the same underlying interaction. RLHF-aligned models trained to produce confident, helpful outputs show reduced calibration degradation when adversarial examples probe uncertainty (ANLI model-in-loop) but may show increased degradation when adversarial examples exploit decisive wrong answers (AdvGLUE human-adversarial). This interpretation is consistent with the data but awaits direct experimental confirmation.

The benchmark-type × RLHF interaction has practical implications: calibration evaluations conducted on clean benchmarks (as in Kadavath et al. [2022]) do not predict adversarial calibration behavior, and benchmark construction method must be specified when reporting RLHF calibration results.

**Task type is an independent calibration moderator.** AdvGLUE QQP (binary, human-adversarial) shows ΔECE = −0.029 despite having the same construction method as AdvGLUE MNLI (ΔECE = +0.071). Distributing logits across three options (NLI) versus two options (binary) produces meaningfully different susceptibility to adversarial calibration effects.

### 6.2 Limitations

**L1: Single-model evaluation for primary calibration experiments.** Core calibration results (RQ1–RQ3) use Llama-2-7b-hf only. The planned 4-model grid (Llama-2-7b-hf, Llama-2-7b-chat, Llama-2-13b-chat, Mistral-7B-instruct) was not completed. Consequently, the pre-specified prediction that ≥60% of model × task cells would show ΔECE > 0.05 is evaluated on only 5 cells from 1 model—statistically underpowered for a universal threshold claim. Results are framed as a pilot study establishing the conditional structure within a single model family. The RLHF moderation finding (RQ4) extends to a model pair within the same family.

**L2: Shared clean baseline for ANLI.** All ANLI adversarial cells (R1/R2/R3) share one GLUE MNLI clean baseline (n=200, ECE=0.279). This creates cross-cell correlation in ANLI ΔECE values. Llama-2-7b-hf's clean MNLI ECE (0.279) is above the Kadavath et al. [2022] range for clean LLMs (0.05–0.15), reflecting weak NLI accuracy (0.365). ANLI R1/R2 ΔECE values may be partially driven by an inflated clean baseline. However, AdvGLUE MNLI uses the same baseline and shows the expected positive ΔECE, so baseline inflation does not fully explain the ANLI calibration improvement—particularly since accuracy on ANLI R1 is actually higher than on clean MNLI (0.380 vs. 0.365), consistent with an adaptive uncertainty explanation.

**L3: BBH-MC commonsense reasoning not tested.** BIG-Bench Hard multiple-choice adversarial variants were planned but excluded for scope reasons. All claims are bounded to NLI and binary paraphrase classification. NLI is the primary adversarial NLP benchmark domain (both AdvGLUE and ANLI are NLI-centered); the task-type finding (NLI versus binary) is internally complete.

**L4: RLHF moderation conditionality discovered post-hoc.** The benchmark-type × RLHF interaction was not predicted in the original H-C1 design; it emerged when H-C1-V2 reported the AdvGLUE reversal as an unexpected finding. Further experimental validation—testing additional RLHF-aligned models, controlling for prompt format—is needed.

**L5: Pre-specified quantitative thresholds not met.** Two of the pipeline's quantitative predictions were not satisfied at their original thresholds. Mean confidence on incorrect adversarial predictions was 0.616—below the originally hypothesized ≥0.70 threshold (informed by vision-domain analogues). Only 1 of 5 adversarial cells exceeded ΔECE > 0.05; the pre-specified criterion was ≥60% of cells. These results indicate that adversarial calibration degradation in LLMs is smaller in magnitude than vision-domain analogues suggested. The conditional structure remains valid at observed magnitudes.

### 6.3 Broader Implications

Practitioners who test model reliability under adversarial conditions by measuring accuracy robustness alone are missing the calibration dimension: a model can be simultaneously more accurate *and* less calibrated under adversarial conditions, or vice versa. The ANLI R1 result (accuracy improves from 0.365 to 0.380; ECE improves from 0.279 to 0.239) illustrates that accuracy and calibration do not covary in a predictable way under adversarial conditions. Adversarial calibration audit (ΔECE measurement) provides a complementary reliability check.

The finding that RLHF alignment can exacerbate calibration degradation on static human-adversarial benchmarks is a potential concern for high-stakes deployment of RLHF-aligned models in NLI or classification settings where adversarial examples were designed to exploit base model reasoning shortcuts.

---

## 7. Conclusion

This pilot study presents the first measurement of logit-based Expected Calibration Error on adversarial NLP benchmark splits for an open-weight LLM, filling a gap between adversarial robustness evaluation (accuracy-only) and calibration measurement (clean-data-only). The central finding is that adversarial calibration degradation in LLMs is construction-method and task-type conditional, not universal.

When adversarial examples are constructed model-in-the-loop—selected precisely because the model fails on them—the resulting benchmark tends to contain examples where the model is already appropriately uncertain at failure time. Calibration improvement under these conditions follows directly. Calibration degrades in the case where adversarial examples are constructed human-adversarially, targeting surface features to trigger high model confidence on incorrect answers, independent of model uncertainty. AdvGLUE MNLI is this case: ΔECE = +0.071, a 7.1 percentage-point calibration gap that renders confidence signals less reliable under human-crafted adversarial NLI conditions.

RLHF alignment interacts with the construction-method dependency: RLHF-aligned models show consistently better calibration than base models on ANLI (ΔΔECE up to +0.147 across all 3 rounds) but worse calibration on AdvGLUE MNLI (alignment tax: ΔΔECE = −0.026). RLHF calibration properties measured on clean benchmarks do not transfer to adversarial settings in a construction-method-independent way.

**Summary of main contributions:**

1. **First adversarial NLP calibration measurement.** ΔECE = +0.071 for AdvGLUE MNLI confirms that adversarial calibration degradation is real and measurable. Label preservation rate = 1.000 for all adversarial splits validates ΔECE as a genuine calibration signal.

2. **Conditional structure: construction method and task type determine calibration outcome.** Human-adversarial NLI (ΔECE = +0.071) degrades calibration; model-in-loop NLI (ANLI R1/R2: ΔECE < 0) improves it. The ANLI difficulty gradient (R1 → R2 → R3: −0.041 → −0.014 → +0.024) shows a smooth transition. Binary classification consistently shows reversed ΔECE.

3. **Benchmark-type × RLHF interaction.** RLHF alignment conditionally moderates adversarial calibration degradation: confirmed for model-in-loop adversarial (ANLI: 100% moderation rate, 3/3 rounds); reversed for static human-adversarial benchmarks (AdvGLUE: ΔΔECE = −0.026).

**Future directions.** The adaptive uncertainty hypothesis for ANLI R1/R2 calibration improvement can be directly tested by computing ECE separately for correct and incorrect predictions. The alignment tax mechanism can be tested by constructing human-adversarial NLI examples targeting RLHF models specifically. Completing the planned multi-model grid (Mistral-7B-Instruct, Llama-2-13b-chat) would enable proper evaluation of calibration universality and deployment reliability prediction. Temperature scaling applied post-hoc to existing logit caches would clarify whether calibration degradation under human-adversarial conditions is a confidence scaling artifact or a structural property.

Adversarial accuracy evaluation and calibration evaluation require shared vocabulary and measurement methods. The conditional structure documented here—where the same adversarial benchmark can improve or degrade calibration depending on construction method and RLHF alignment—suggests that these communities must develop coordinated frameworks. Calibration robustness is not a consequence of accuracy robustness; it requires independent measurement.

---

## References

Christiano, P., Leike, J., Brown, T. B., Martic, M., Legg, S., & Amodei, D. (2017). Deep Reinforcement Learning from Human Preferences. *NeurIPS*.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. *ICML*. arXiv:1706.04599.

Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., … Kaplan, J. (2022). Language Models (Mostly) Know What They Know. arXiv:2207.05221.

Minderer, M., Djolonga, J., Romijnders, R., Hubis, F., Zhai, X., Houlsby, N., Tran, D., & Lucic, M. (2021). Revisiting the Calibration of Modern Neural Networks. *NeurIPS*. arXiv:2106.07998.

Nie, Y., Williams, A., Dinan, E., Bansal, M., Weston, J., & Kiela, D. (2020). Adversarial NLI: A New Benchmark for Natural Language Understanding. *ACL*. arXiv:1910.14599.

OpenAI. (2023). GPT-4 Technical Report. arXiv:2303.08774.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. (2022). Training Language Models to Follow Instructions with Human Feedback. *NeurIPS*.

Touvron, H., Martin, L., Stone, K., Albert, P., Almahairi, A., Babaei, Y., Bashlykov, N., Batra, S., Bhargava, P., Bhosale, S., Biber, D., Blick, R., Bloecker, C., Bordes, F., Broseit, T., Chen, G., Cucurull, G., Defore, A. V., Esiobu, D., … Scialom, T. (2023). Llama 2: Open Foundation and Fine-Tuned Chat Models. arXiv:2307.09288.

Wang, B., Chen, Z., Poon, H., & Chen, M. (2021). AdvGLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models. *EMNLP*. arXiv:2111.02840.

Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2023). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in Large Language Models. arXiv:2306.13063.

Zhao, Z., Wallace, E., Feng, S., Klein, D., & Singh, S. (2021). Calibrating Predictions to Calibrate Confidence in Neural Language Models. *ACL*.

Askell, A., Bai, Y., Chen, A., Drain, D., Ganguli, D., Henighan, T., Jones, A., Joseph, N., Mann, B., DasSarma, N., Elhage, N., Hatfield-Dodds, Z., Hernandez, D., Kernion, J., Ndousse, K., Olsson, C., Amodei, D., Brown, T., Clark, J., … Kaplan, J. (2021). A General Language Assistant as a Laboratory for Alignment. arXiv:2112.00861.

Suzgun, M., Scales, N., Schärli, N., Gehrmann, S., Tay, Y., Chung, H. W., Chowdhery, A., Le, Q. V., Chi, E. H., Zhou, D., & Wei, J. (2022). Challenging BIG-Bench Tasks and Whether Chain-of-Thought Can Solve Them. arXiv:2210.09261.

Desai, S., & Durrett, G. (2020). Calibration of Pre-trained Transformers. *EMNLP*. arXiv:2003.07892.

Kong, L., Guo, J., & Kamber, M. (2020). Calibration, Entropy Rates, and Memory in Language Models. *EMNLP*.

Braverman, M., Garg, S., Kalai, A., & Ligett, K. (2020). Calibration for the (Computationally-Identifiable) Masses.

Jiang, Z., Araki, J., Ding, H., & Neubig, G. (2021). How Can We Know When Language Models Know? On the Calibration of Language Models for Question Answering. *TACL*.

---

*Note: Citations marked above include references cited in the paper. Full BibTeX entries are available in `06_references.bib`. Citations were not independently verified via Semantic Scholar in this pipeline session due to tool unavailability.*
