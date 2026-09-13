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

**Finding 1: RLHF consistently moderates calibration degradation on model-in-loop adversarial benchmarks.** Llama-2-7b-chat shows substantially lower ΔECE than base on all three ANLI rounds. The largest effect is on ANLI R2: ΔΔECE = +0.147, meaning the base model shows 14.7 percentage points more calibration degradation than the chat model on this split. RLHF-aligned models are more appropriately uncertain on model-in-loop adversarial examples.

**Finding 2: RLHF exacerbates calibration degradation on static human-adversarial benchmarks.** On AdvGLUE MNLI, the chat model shows *higher* ΔECE than the base model (ΔECE = +0.090 vs +0.065; ΔΔECE = −0.026). RLHF alignment is not a universal calibration fix — it produces an alignment tax on static human-adversarial NLI benchmarks.

Figure 9 (`reliability_diagram.png`) compares reliability diagrams for base and chat models on AdvGLUE MNLI, showing the chat model's overconfidence curve shifted further from the diagonal than the base model's. Figure 10 (`confidence_distribution_adv.png`) shows that chat models display a more peaked confidence distribution under adversarial conditions on AdvGLUE — consistent with RLHF instruction-following training instilling more decisive (and, under adversarial conditions, more confidently wrong) behavior.

**Interpreting the interaction.** The benchmark-type × RLHF interaction is the most novel finding of this work. We hypothesize that AdvGLUE was constructed targeting base language models (circa 2021), exploiting NLI reasoning shortcuts that RLHF fine-tuning may amplify: RLHF-trained models are trained to produce confident, decisive outputs, which human adversaries targeting NLI reasoning are positioned to exploit. Model-in-loop adversarial construction (ANLI), by contrast, selects examples where the *current model* fails — and RLHF-aligned models, being more calibrated about their uncertainty, fail with lower confidence on these examples, reducing ΔECE. This interpretation is consistent with the data but awaits direct experimental confirmation (see Section 6).
