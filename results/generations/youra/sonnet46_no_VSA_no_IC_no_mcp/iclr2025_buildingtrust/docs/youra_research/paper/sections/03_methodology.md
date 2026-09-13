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

**Cell structure.** Our design produces 5 adversarial cells: {advglue\_mnli, anli\_r1, anli\_r2, anli\_r3, advglue\_qqp}, each paired with its clean baseline. (SST-2 adversarial data was insufficient for ECE measurement and excluded.) The minimum cell size is n=78 (AdvGLUE QQP), which satisfies our minimum coverage requirement (≥50 examples per cell) with confirmation via coverage heatmap (Figure 3).

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
