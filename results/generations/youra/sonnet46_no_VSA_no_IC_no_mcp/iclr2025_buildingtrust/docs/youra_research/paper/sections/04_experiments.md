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
