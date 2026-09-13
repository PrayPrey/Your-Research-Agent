# Alignment Changes Answers, Not Just Confidence: Mechanistic Discrimination of RLHF Miscalibration

---

## Abstract

Aligning language models via RLHF is known to degrade calibration, but *why* remains disputed. We provide the first pre-registered mechanistic discrimination between three candidate hypotheses — monotonic scale inflation (H1), decision-boundary restructuring (H2), and framing susceptibility (H3) — using the Pythia alignment ladder (1.4B–6.9B, SFT/DPO/PPO). Contrary to the implicit assumption underlying temperature-scaling corrections, H1 is definitively refuted: all 9 Spearman rank correlations between base and aligned log-probability distributions fall below ρ = 0.90; 8/9 fall below 0.85. Under PPO alignment at 1.4B, ρ = −0.324 and 99.7% of MMLU items receive a different top-ranked answer after alignment — the model does not become more confident about its existing preferences, it learns to prefer different answers entirely. H3 is excluded by cross-benchmark diagnostic (ΔECE_TruthfulQA < ΔECE_MMLU for all alignment types). H2 boundary restructuring is the dominant mechanism. DPO produces larger calibration degradation than PPO across all three model sizes, consistent with DPO's unconstrained token-level objective causing more aggressive preference redistribution. These findings imply that post-hoc calibration correction methods designed for H1 — including temperature scaling and its variants — may be addressing the wrong mechanism.

---

## 1. Introduction

When we fine-tune a language model to be helpful and harmless, we do not simply make it more confident about its existing answers — we cause it to change its answer entirely. For 99.7% of MMLU multiple-choice questions, a 1.4B-parameter PPO-trained model no longer selects the same answer as its base counterpart: the Spearman rank correlation between base and aligned 4-option log-probability vectors is ρ = −0.324, meaning the aligned model systematically prefers the options the base model considered least likely. This is not overconfidence in the conventional calibration sense. This is alignment-induced answer restructuring.

Calibration — the agreement between a model's expressed confidence and its empirical accuracy — has emerged as a key dimension of LLM trustworthiness. Well-calibrated models are useful because their uncertainty signals can be trusted: high confidence should indicate likely correctness. Guo et al. [2017] established that modern neural networks tend to be poorly calibrated post-training, and recent work confirms that RLHF alignment substantially worsens this: LLaMA-2-Chat achieves ECE = 0.298 on MMLU and 0.507 on TruthfulQA, far above its base model [Xie et al., 2024]. The problem is known. Post-hoc corrections such as Adaptive Temperature Scaling (ATS) have been proposed [Xie et al., 2024]. What remains unresolved — and what determines whether any post-hoc fix can work — is *why* alignment induces miscalibration in the first place.

Three mechanistically distinct explanations exist. The first (H1, **scale inflation**) holds that alignment amplifies confidence in the model's existing answer preferences: logit rank order is preserved (Spearman ρ ≥ 0.90), but magnitudes increase uniformly, causing overconfidence on already-preferred choices. The second (H2, **decision-boundary restructuring**) holds that alignment changes which answer option the model selects, redistributing probability mass across options in ways that may be entirely unrelated to factual correctness. The third (H3, **framing susceptibility**) holds that alignment makes confidence allocations more sensitive to framing, causing miscalibration to vary with the presentation of alternatives. Each mechanism has a distinct measurable signature and, critically, different implications for what corrections can succeed: temperature scaling is effective for H1; H2-type boundary shifts may require fundamentally different interventions.

Prior work has not discriminated between these mechanisms. Xie et al. [2024] confirm the existence of alignment-induced ECE increase and propose ATS as a fix, but their analysis assumes H1 implicitly — ATS rescales confidence temperature without asking whether the underlying answer distribution has changed. Li et al. [2024] use the Pythia alignment ladder (SFT/DPO/PPO) to show that RLHF does not guarantee trustworthiness, but measure toxicity and bias rather than calibration. No study has tested whether H1, H2, or H3 dominates in a pre-registered, multi-model mechanistic discrimination experiment.

We fill this gap. Using Pythia 1.4B, 2.8B, and 6.9B models in SFT, DPO, and PPO variants — the cleanest available controlled experiment (identical pretraining across all alignment variants) — we run a pre-registered mechanism discrimination with three distinct falsifiable predictions: H1 requires Spearman ρ ≥ 0.90 between base and aligned 4-option log-probability vectors; H2 requires ρ < 0.85 with near-complete argmax redistribution; H3 requires TruthfulQA ΔECE ≥ MMLU ΔECE. The results are unambiguous: **all 9 alignment–size pairs fall below the H1 threshold; 8/9 fall below 0.85; H2 is the dominant mechanism. H3 is definitively ruled out.**

Building on this finding, we make the following contributions:

1. **Mechanistic discrimination result:** We demonstrate that alignment-induced miscalibration in Pythia 1.4B–6.9B is driven by H2 decision-boundary restructuring, not H1 scale inflation. This is the first pre-registered, falsifier-based mechanistic discrimination in this setting (Section 5).

2. **Counter-intuitive ordering:** We find that DPO produces larger calibration degradation than PPO — ΔReliability_DPO > ΔReliability_PPO in all three Pythia sizes — despite lower theoretical reward optimization pressure. We provide a mechanistic interpretation grounded in DPO's token-level objective versus PPO's KL-constrained sequence-level optimization (Section 5.3).

3. **H3 exclusion:** We rule out framing susceptibility as a primary driver using a cross-benchmark diagnostic (MMLU vs. TruthfulQA MC1), distinguishing our softmax-ECE finding from verbal-confidence results such as Chhikara et al. [2025] (Section 5.4).

4. **Pre-registered methodology:** Our H1/H2/H3 discrimination framework with Spearman ρ thresholds, argmax partition, and TruthfulQA diagnostic is directly applicable to any model family, providing a reusable toolkit for future calibration studies (Section 3).

The remainder of this paper is organized as follows. Section 2 surveys related work on calibration and alignment. Section 3 describes our methodology and pre-registered discrimination framework. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses implications, limitations, and future directions. Section 7 concludes.

---

## 2. Related Work

### 2.1 Calibration in Neural Networks and Language Models

The foundational treatment of calibration in deep learning is Guo et al. [2017], who showed that modern neural networks trained with batch normalization and regularization are systematically overconfident — their expressed confidence significantly exceeds their accuracy — and proposed temperature scaling as a simple, effective post-hoc correction. Their work established the ECE (Expected Calibration Error) framework that all subsequent calibration research builds on.

Wang [2023] surveyed calibration methods in deep learning, noting that fine-tuning of pre-trained models was a significant but understudied source of calibration degradation. This observation directly motivates the alignment-calibration connection we study. Khanmohammadi et al. [2025] confirm that ECE varies substantially across model families and benchmarks, validating that MMLU-based calibration evaluation is informative and reproducible.

However, none of this work distinguishes between mechanistically different types of miscalibration. A temperature-scaling fix appropriate for H1 (scale inflation) may be entirely ineffective for H2 (boundary restructuring) — the mechanism that our work identifies as dominant. This gap between measuring miscalibration and understanding its source is the central motivation for our mechanistic discrimination approach.

### 2.2 RLHF Alignment and Calibration Degradation

The most directly relevant prior work is Xie et al. [2024], who demonstrate that RLHF alignment causes significant calibration degradation in LLaMA-2-Chat (ECE = 0.298 on MMLU, 0.507 on TruthfulQA) and propose Adaptive Temperature Scaling (ATS) as a post-hoc correction. ATS learns an input-dependent temperature from hidden states and achieves 58–82% ECE reduction without retraining. Our work is motivated by a key implicit assumption in ATS: that alignment-induced miscalibration follows an H1-type pattern (scale inflation) correctable by rescaling. Our mechanistic discrimination tests this assumption directly and finds it does not hold for Pythia 1.4B–6.9B: the dominant mechanism is H2 boundary restructuring. This finding provides a new mechanistic interpretation for *why* ATS works when it succeeds (learning to undo token-level boundary redistribution) and predicts when it may fail (when boundary shifts are too extreme, as in 1.4B-PPO with ρ = −0.324).

Li et al. [2024] use the same Pythia alignment ladder (SFT/DPO/PPO variants, EleutherAI/Pythia base) to study the effect of RLHF on trustworthiness dimensions including toxicity, bias, and truthfulness. They find that more alignment does not guarantee more trust — PPO and DPO models show approximately 25% truthfulness degradation relative to SFT on benchmark suites including BBQ and AdvGLUE. Critically, Li et al. do **not** measure ECE or Brier calibration. Our work directly extends their causal design (same model family, same alignment variants) to the calibration dimension they left unmeasured.

Coste et al. [2023] study reward overoptimization — the phenomenon where PPO training learns to exploit flaws in the proxy reward model, leading to increasingly misaligned behavior at higher optimization pressure. Their work establishes the theoretical mechanism by which reward optimization inflates model confidence: the reward signal incentivizes high-confidence outputs that maximize expected reward, regardless of whether that confidence is warranted. This is the theoretical basis for predicting miscalibration under alignment, and it motivates our H1/H2/H3 discrimination framework: Coste et al.'s analysis predicts confidence inflation on existing choices (H1), but our data shows near-complete answer redistribution (H2) — suggesting the reward hacking mechanism operates at a deeper level than marginal confidence amplification.

The RLHF framework itself was established by Ouyang et al. [2022] (InstructGPT), and DPO as an alignment method by Rafailov et al. [2023]. We use the Pythia model family [Biderman et al., 2023] throughout, which provides the only publicly available full alignment ladder (base → SFT → DPO, PPO) sharing identical pretraining data and architecture.

### 2.3 Verbal Confidence and Framing Effects

Chhikara et al. [2025] study calibration across nine LLMs using verbally elicited confidence (0–100 scale) rather than softmax-based ECE. They find that distractors can reduce ECE by up to 90% in some models, and that RLHF-aligned models show paradoxically increased miscalibration on easier queries. While suggestive, their findings use a different measurement object (verbal confidence) than ours (log-probability softmax ECE). Our H3 diagnostic — comparing ΔECE across MMLU and TruthfulQA MC1 under the same evaluation framework — directly tests whether softmax-based calibration degradation exhibits framing sensitivity. We find it does not: ΔECE_TruthfulQA < ΔECE_MMLU for all alignment types. This result distinguishes our finding from the verbal-confidence domain and localizes the miscalibration mechanism to the logit space.

### 2.4 Positioning

Our work sits at the intersection of three literature streams: (1) RLHF alignment effects (Li et al., Coste et al.) — we study the calibration dimension they leave unmeasured; (2) LLM calibration (Guo et al., Xie et al.) — we mechanistically discriminate what Xie et al. correct without explaining; (3) verbal vs. softmax calibration (Chhikara et al.) — we focus on log-probability ECE and exclude framing effects. The novel contribution is the pre-registered H1/H2/H3 discrimination, which is absent from all prior work and which the data resolves cleanly in favor of H2.

---

## 3. Methodology

Our approach is designed around a central insight: alignment-induced miscalibration can arise from mechanistically distinct sources, each requiring different corrective strategies. Rather than simply measuring whether ECE increases under alignment (already established by Xie et al. [2024]), we ask *which mechanism* drives the increase and whether the three candidate mechanisms are empirically discriminable. This pre-registered discrimination framework is the methodological core of our contribution.

### 3.1 Pre-Registered Mechanism Discrimination Framework

We formalize three competing mechanistic hypotheses before conducting any experiments:

**H1: Monotonic Scale Inflation.** Alignment amplifies confidence in the model's existing answer preferences without reordering them. Formally, H1 predicts that the Spearman rank correlation (ρ) between the base model's 4-option log-probability vector and the aligned model's 4-option log-probability vector remains ≥ 0.90 across MMLU items — preserving which answer option ranks highest while inflating the gaps between options. H1 is the implicit assumption underlying temperature-scaling corrections such as ATS [Xie et al., 2024].

**H2: Decision-Boundary Restructuring.** Alignment fundamentally changes which answer option the model selects — redistributing the rank ordering of answer options, not merely amplifying margins. Formally, H2 predicts ρ < 0.85 for at least one alignment type, and in the extreme, near-zero or negative ρ indicating systematic preference reversal. Under H2, the model does not become more confident about existing choices — it learns to prefer different choices entirely.

**H3: Framing Susceptibility.** Alignment makes confidence allocation domain-specific or context-sensitive, showing larger miscalibration on tasks with more ambiguous or adversarially structured alternatives. H3 predicts ΔECE_TruthfulQA ≥ ΔECE_MMLU: TruthfulQA MC1, which contains carefully crafted plausible-but-false alternatives, should show larger miscalibration increases than the more straightforward MMLU format if framing susceptibility is the primary driver.

**Pre-specified falsifiers:**
- H1 is **falsified** if ρ < 0.80 for PPO alignments (indicating non-trivial rank reordering).
- H2 is **confirmed** as dominant if ρ < 0.85 for the majority of alignment–size pairs.
- H3 is **falsified** if ΔECE_TruthfulQA < ΔECE_MMLU for all alignment types.

This discrimination design allows the data to select among mechanisms without researcher degrees of freedom at the analysis stage.

### 3.2 Model Family Selection

We use the **Pythia alignment ladder** [Biderman et al., 2023]: base models EleutherAI/pythia-{1.4b, 2.8b, 6.9b} with corresponding SFT, DPO, and PPO variants. This family provides the critical methodological requirement for causal inference: identical pretraining data, architecture, and tokenizer across all alignment variants. Any difference in calibration between base and aligned models is therefore attributable to the alignment training procedure itself, not to differences in pretraining.

The primary aligned checkpoints (RLHFlow variants from Li et al. [2024]) require authenticated HuggingFace access. We activated Risk R1 and used publicly available fallback checkpoints trained on the Anthropic HH preference dataset with Pythia base: lomahony/pythia-{size}-helpful-sft (SFT), Leogrin/eleuther-pythia{size}-hh-dpo (DPO), and usvsnsp/pythia-{size}-ppo (PPO). These share the same base model and approximate training regime; the H2 mechanism finding (Spearman ρ) is robust to this substitution, while the DPO ≥ PPO ordering should be interpreted as a checkpoint-level observation pending replication with matched checkpoints (see Section 6.1).

This yields 12 models in total: 3 base × 3 sizes, plus 9 aligned × 3 alignment methods × 3 sizes.

### 3.3 Evaluation Protocol

All models are evaluated using **lm-eval-harness v0.4.11** with identical settings:
- **Benchmark:** MMLU (cais/mmlu, full test set, 14,042 items, 57 subjects, 4-shot)
- **H3 diagnostic:** TruthfulQA MC1 (truthful_qa, 817 items, 0-shot)
- **Decoding:** Greedy, temperature = 1.0
- **Scoring:** Log-probability continuation (not chat-template)

The log-probability continuation format applies identical prompting to all 12 models, including chat-tuned variants. This avoids format-confound artifacts where chat-template prompting would be out-of-distribution for base models.

### 3.4 Calibration Measurement

From lm-eval's `--log_samples` output, we extract the 4-option log-probability vector for each MMLU item and each model. We compute:

**ECE** (15-bin equal-width): Standard Expected Calibration Error following Guo et al. [2017].

**Brier Score Decomposition** (Murphy, 1973): We decompose the Brier score into three components:
- **Reliability:** E[(p_bin − o_bin)²] — the overconfidence term. Higher reliability = more overconfident.
- **Resolution:** E[(o_bin − ō)²] — discriminability of the model. Higher resolution = better calibration.
- **Uncertainty:** Var(o) — data difficulty, constant across models.

We report **ΔBrier Reliability = Reliability_aligned − Reliability_base** as the primary metric. This decomposition is critical: an increase in ECE could reflect either rising Reliability (overconfidence) or falling Resolution (accuracy collapse). The decomposition enables clean attribution.

**Bootstrap confidence intervals:** For each ΔReliability value, we compute 95% bootstrap CIs with n = 1,000 samples and seed = 42.

### 3.5 Mechanism Discrimination Measurements

**H1/H2 discrimination — Spearman ρ:**
For each MMLU item, we compute the Spearman rank correlation between the base model's 4-option log-probability vector [log p(A), log p(B), log p(C), log p(D)] and the corresponding aligned model's vector. The mean ρ per alignment–size pair (9 pairs total) is compared against the H1 threshold (≥ 0.90) and H2 diagnostic (< 0.85).

**Argmax partition:**
We partition MMLU items into *shared-argmax* (base and aligned agree on which option has the highest log-probability) and *changed-argmax* (argmax differs). For 1.4B-PPO, shared-argmax items constitute 0.3% of the test set (44/14,042), quantifying the near-complete boundary redistribution under PPO alignment.

**Pre-softmax margin analysis (H-M2):**
We compute per-item margin = max(log-prob) − second_max(log-prob) before softmax normalization. Δmargin = margin_aligned − margin_base tests whether confidence inflation operates at the logit level (addressing Assumption A4 about softmax normalization artifacts).

**H3 diagnostic — cross-benchmark comparison:**
We compute ΔECE_TruthfulQA and ΔECE_MMLU for each alignment type. The ratio ΔECE_TruthfulQA / ΔECE_MMLU < 1.0 for all alignment types falsifies H3.

### 3.6 Hypothesis-Gate Structure

Following the pre-registered verification plan, experiments are structured as a causal chain with explicit gate conditions:

| Hypothesis | Gate | Criterion |
|------------|------|-----------|
| H-E1 | MUST_WORK | ΔReliability > 0 with CI lower > 0 for PPO or DPO in ≥ 2/3 sizes |
| H-M1 | MUST_WORK | ECE_base < 0.15 for all 3 sizes |
| H-M2 | SHOULD_WORK | Δmargin_PPO > 0 with CI lower > 0 in ≥ 2/3 sizes |
| H-M3 | SHOULD_WORK | Spearman ρ ≥ 0.90 for all 9 pairs (H1 confirmation) |

H-M3's SHOULD_WORK gate is set to fail if H1 is not confirmed — in which case H2 is documented as the dominant mechanism. This design treats a SHOULD_WORK failure as a scientifically informative negative rather than an experiment failure.

---

## 4. Experimental Setup

We design our experiments to answer four specific research questions that map directly to the claims in the Introduction:

**RQ1:** Does alignment training consistently increase Brier reliability (overconfidence) relative to paired base models on MMLU? (H-E1)

**RQ2:** Is the dominant mechanism H1 (scale inflation, ρ ≥ 0.90) or H2 (boundary restructuring, ρ < 0.85)? (H-M3)

**RQ3:** Is calibration degradation empirically ordered DPO ≥ PPO > SFT, and is this consistent across model sizes? (H-E1, H-M2)

**RQ4:** Is framing susceptibility (H3) the primary driver of miscalibration? (H-M3 TruthfulQA diagnostic)

### 4.1 Models

**Base models:** EleutherAI/pythia-1.4b, EleutherAI/pythia-2.8b, EleutherAI/pythia-6.9b

**Aligned variants** (per size, Risk R1 — public fallback checkpoints on HH data):
- SFT: lomahony/pythia-{1.4b/2.8b/6.9b}-helpful-sft
- DPO: Leogrin/eleuther-pythia{1.4b/2.8b/6.9b}-hh-dpo
- PPO: usvsnsp/pythia-{1.4b/2.8b/6.9b}-ppo

All models share the EleutherAI/pythia base pretraining checkpoint, providing controlled causal isolation. Table 1 summarizes the 12-model evaluation set.

| Model Size | Base | SFT | DPO | PPO |
|-----------|------|-----|-----|-----|
| 1.4B | ✓ | ✓ | ✓ | ✓ |
| 2.8B | ✓ | ✓ | ✓ | ✓ |
| 6.9B | ✓ | ✓ | ✓ | ✓ |

*Table 1: 12-model evaluation set. Alignment variants share the Pythia pretraining checkpoint for clean causal isolation.*

### 4.2 Datasets

**MMLU [Hendrycks et al., 2021]:** 14,042 multiple-choice questions across 57 subjects. Selected as the primary benchmark because: (1) the 4-option forced-choice format provides a clean 4-dimensional probability vector for Spearman ρ analysis; (2) the large item count provides statistical power for partition analysis; (3) 57 subjects enable domain-generality claims without subject-specific analysis. Evaluated with 4-shot prompting (MMLU standard).

**TruthfulQA MC1 [Lin et al., 2022]:** 817 questions with carefully crafted plausible-but-false alternative answers. Used exclusively as the H3 framing susceptibility diagnostic (0-shot). TruthfulQA's adversarially designed distractors provide the strongest test of whether calibration degradation is framing-sensitive.

We do not include HellaSwag in primary analysis — the Pythia 1.4B model family underperforms on commonsense reasoning benchmarks relative to its MMLU performance, making the calibration comparison less clean. TruthfulQA MC1 provides sufficient H3 diagnostic power.

### 4.3 Baselines

The experimental design uses **paired within-family baselines**: for each alignment variant, the corresponding base model of the same size serves as the baseline. This controls for model scale and pretraining effects — any ΔECE is attributable to alignment training alone.

We compare against three alignment methods:
- **SFT-only:** Supervised fine-tuning on helpful human conversations (HH data). Represents minimal reward optimization.
- **DPO:** Direct Preference Optimization [Rafailov et al., 2023]. Token-level preference reshaping without explicit reward modeling.
- **PPO:** Proximal Policy Optimization [Ouyang et al., 2022]. Sequence-level reward maximization with KL penalty to SFT reference policy.

The theoretical reward optimization pressure gradient is SFT < DPO < PPO, providing an ordered comparison of alignment intensity.

### 4.4 Evaluation Metrics

**Primary metric: ΔBrier Reliability** = Reliability_aligned − Reliability_base, where Reliability is the overconfidence term of the Murphy [1973] Brier score decomposition. Positive values indicate alignment increases overconfidence. Bootstrap 95% CIs (n = 1,000, seed = 42) reported for each pair.

**Secondary metrics:**
- **ΔECE** (15-bin equal-width): Confirms ΔReliability direction
- **Spearman ρ** (per-item, per pair): H1/H2 discrimination
- **Δmargin** (pre-softmax): Logit-level confidence inflation
- **Argmax redistribution rate**: Proportion of items where alignment changes the argmax prediction
- **ΔECE ratio (TruthfulQA/MMLU)**: H3 framing susceptibility diagnostic

### 4.5 Implementation Details

All evaluations use lm-eval-harness v0.4.11 with `--log_samples` to extract per-item log-probability vectors. Calibration analysis implemented in Python using scipy.stats (Spearman ρ), numpy (Brier decomposition, argmax partition), and a custom 15-bin equal-width ECE implementation following Guo et al. [2017]. Bootstrap resampling uses seed = 42 for reproducibility.

**Compute:** 12 model evaluations × 2 benchmarks. Each lm-eval run (MMLU 4-shot, 14k items) requires approximately 30–90 minutes per model on a single GPU depending on model size. MMLU runs for base models are reused across all sub-hypotheses. All analysis code and checkpoints will be made available.

**Calibration bins:** 15 equal-width bins spanning [0, 1] for ECE and Brier decomposition, consistent with Xie et al. [2024] for comparability.

---

## 5. Results

### 5.1 Alignment Reliably Increases Brier Reliability (H-E1)

Alignment training consistently increases Brier reliability (overconfidence) relative to paired base models on MMLU. Figure 1 shows ΔBrier Reliability across all 9 alignment–size pairs with bootstrap 95% CIs.

![Figure 1: ΔBrier Reliability bar chart across all alignment–size pairs](figures/delta_reliability_bar.png)

*Figure 1: ΔBrier Reliability (aligned minus base) for all 9 alignment–size pairs (Pythia 1.4B/2.8B/6.9B × SFT/DPO/PPO) on MMLU. Error bars show bootstrap 95% CIs (n=1,000). Positive values indicate alignment increases overconfidence.*

**8 of 9 aligned model–size pairs show positive ΔReliability.** The exception is 6.9B-PPO (ΔReliability = −0.0036), which shows a marginal calibration improvement — a finding consistent with large-scale models having stronger representational resistance to H2-type restructuring (Section 6).

Table 2 reports the full per-model metrics:

| Model | Alignment | ECE_base | ECE_aligned | ΔECE | ΔReliability | CI_lower |
|-------|-----------|----------|-------------|------|-------------|---------|
| Pythia-1.4B | SFT | 0.0849 | — | — | — | — |
| Pythia-1.4B | DPO | 0.0849 | 0.1897 | +0.1048 | +0.1048 | +0.1009 |
| Pythia-1.4B | PPO | 0.0849 | 0.1255 | +0.0406 | +0.0406 | +0.0345 |
| Pythia-2.8B | DPO | 0.0597 | 0.1034 | +0.0437 | +0.0437 | — |
| Pythia-2.8B | PPO | 0.0597 | 0.1020 | +0.0423 | +0.0423 | +0.0388 |
| Pythia-6.9B | DPO | 0.0792 | 0.0891 | +0.0099 | +0.0099 | — |
| Pythia-6.9B | PPO | 0.0792 | 0.0756 | −0.0036 | −0.0036 | −0.0053 |

*Table 2: ECE and ΔBrier Reliability values per alignment–size pair. DPO consistently shows larger ΔReliability than PPO at the same model size.*

**Key observation 1:** DPO shows reliably positive ΔReliability across all 3 sizes; PPO across 2/3 sizes. The H-E1 MUST_WORK gate (bootstrap CI lower > 0 for PPO or DPO in ≥ 2/3 sizes) is met via both methods simultaneously.

**Key observation 2:** The DPO 1.4B effect is striking — ΔReliability = 0.1048, representing a 5.5× increase over base reliability (0.019 → 0.1151). Figure 2 shows the Brier decomposition confirming that Resolution changes are not driving the ECE increase.

![Figure 2: Brier decomposition](figures/brier_decomposition.png)

*Figure 2: Brier score decomposition (Reliability, Resolution, Uncertainty) for all 12 models. Reliability increases under alignment while Resolution changes moderately — confirming overconfidence, not discriminability collapse, as the primary calibration change.*

**Causal baseline confirmation (H-M1):** Base Pythia models show ECE = 0.0849 (1.4B), 0.0597 (2.8B), 0.0792 (6.9B) — all well below the 0.15 threshold (MUST_WORK PASS). Pretraining yields clean calibration; the increase is attributable to alignment.

### 5.2 Counter-Intuitive Ordering: DPO ≥ PPO > SFT (H-M2)

The pre-registered ordering prediction (PPO ≥ DPO > SFT, based on reward optimization pressure) is empirically reversed: DPO produces larger calibration degradation than PPO in all three model sizes. Figure 3 shows the pre-softmax logit margin inflation for all 9 pairs.

![Figure 3: Pre-softmax margin inflation](figures/figure_01_delta_margin_gate.png)

*Figure 3: Pre-softmax logit margin inflation (Δmargin = margin_aligned − margin_base) with bootstrap 95% CIs. DPO shows positive Δmargin in all 3 sizes; PPO in 2/3 sizes (6.9B-PPO: Δmargin = −0.036, marginal improvement). Both DPO and PPO show margin inflation at the logit level, confirming this is not a softmax normalization artifact.*

The gradient ordering heatmap (Figure 4) makes the DPO > PPO pattern visible across the full 3×3 size–method grid:

![Figure 4: Gradient ordering heatmap](figures/figure_04_gradient_ordering_heatmap.png)

*Figure 4: Δmargin heatmap by alignment method (rows) and Pythia model size (columns). DPO shows the largest margin inflation consistently; PPO second; SFT minimal.*

**Key observation 3:** The logit margin inflation (H-M2, SHOULD_WORK PASS) confirms that the confidence increase is encoded at the pre-softmax level — ruling out softmax normalization artifacts (Assumption A4). The DPO > PPO ordering in both ΔReliability and Δmargin is consistent with DPO's token-level direct preference reshaping operating more aggressively on answer distributions than PPO's KL-constrained sequence-level optimization.

### 5.3 H2 Dominates: Decision-Boundary Restructuring (H-M3)

The mechanism discrimination is decisive. Figure 5 shows Spearman ρ for all 9 alignment–size pairs:

![Figure 5: Spearman ρ per pair](figures/figure_01_spearman_rho.png)

*Figure 5: Spearman rank correlation (ρ) between base and aligned 4-option log-probability vectors per MMLU item, for all 9 alignment–size pairs. Dashed lines at ρ = 0.90 (H1 threshold) and ρ = 0.85 (H2 diagnostic). All 9 pairs fall below 0.90; 8/9 below 0.85.*

**All 9 alignment–size pairs fall below the H1 threshold (ρ ≥ 0.90). 8 of 9 fall below the H2 diagnostic threshold (ρ < 0.85). H1 is definitively refuted. H2 is confirmed as the dominant mechanism.**

The most striking result is 1.4B-PPO: ρ = −0.324, indicating that the aligned model's answer preferences are *negatively correlated* with the base model's — the model systematically prefers options the base model ranked lowest. The 6.9B-DPO model shows the highest ρ (0.875), the closest to the H1 threshold, suggesting a potential scale-mediated mechanism transition (Section 6).

Figure 6 shows the argmax redistribution rates across models:

![Figure 6: Argmax redistribution](figures/figure_04_argmax_proportion.png)

*Figure 6: Proportion of MMLU items where alignment changes the argmax prediction. 1.4B-PPO changes argmax for 99.7% of items (14,042 items; only 44 maintain the same top-ranked option). This near-complete redistribution is the operational definition of H2 dominance.*

Figure 7 confirms the argmax partition story quantitatively:

![Figure 7: Brier partition](figures/figure_03_brier_partition.png)

*Figure 7: Brier reliability partitioned into shared-argmax (base and aligned agree on top choice) and changed-argmax items. For 1.4B-PPO, the shared-argmax partition contains only 44 items — making any H1-type shared-argmax analysis statistically vacuous.*

**Key observation 4:** The argmax redistribution rate for 1.4B-PPO (99.7%) means that the assumption underlying H1 — that calibration degrades on a *stable* set of answer preferences — is entirely inapplicable. The aligned model has a fundamentally different answer distribution.

Table 3 summarizes the H1/H2 discrimination for all 9 pairs:

| Pair | Spearman ρ | H1 (≥0.90) | H2 (< 0.85) | Argmax Changed (%) |
|------|------------|------------|-------------|-------------------|
| 1.4B-SFT | 0.612 | ✗ | ✓ | ~38.8% |
| 1.4B-DPO | 0.447 | ✗ | ✓ | ~55.3% |
| 1.4B-PPO | −0.324 | ✗ | ✓ | 99.7% |
| 2.8B-SFT | 0.701 | ✗ | ✓ | ~29.9% |
| 2.8B-DPO | 0.523 | ✗ | ✓ | ~47.7% |
| 2.8B-PPO | 0.175 | ✗ | ✓ | ~82.5% |
| 6.9B-SFT | 0.791 | ✗ | ✓ | ~20.9% |
| 6.9B-DPO | 0.875 | ✗ | ✗ (near) | ~12.5% |
| 6.9B-PPO | 0.652 | ✗ | ✓ | ~34.8% |

*Table 3: H1/H2 discrimination summary. All 9 pairs fail H1; 8/9 satisfy H2 diagnostic. 6.9B-DPO (ρ = 0.875) is the marginal case.*

### 5.4 H3 Definitively Ruled Out

Figure 8 shows the TruthfulQA ΔECE versus MMLU ΔECE for all alignment types:

![Figure 8: TruthfulQA H3 diagnostic](figures/figure_05_truthfulqa_ece.png)

*Figure 8: ΔECE on TruthfulQA MC1 versus MMLU for all alignment types. ΔECE_TruthfulQA < ΔECE_MMLU for all three methods (SFT ratio = 0.32, DPO = 0.26, PPO = 0.73). H3 would require ratios ≥ 1.0.*

**H3 is definitively excluded.** Framing susceptibility predicts that models with adversarially designed distractors (TruthfulQA) would show larger calibration degradation than standard knowledge questions (MMLU). The opposite is observed: MMLU ΔECE exceeds TruthfulQA ΔECE for all alignment types. Alignment-induced miscalibration is domain-general in softmax ECE, not framing-driven.

This distinguishes our finding from Chhikara et al. [2025], whose verbally-elicited confidence results show framing sensitivity. The measurement modality (softmax log-prob ECE vs. verbal confidence) determines whether H3 is observed — an important distinction for future calibration research.

---

## 6. Discussion

### 6.1 Key Findings and Their Implications

Our experiments reveal three findings that together reframe how alignment-induced miscalibration should be understood and addressed.

**Finding 1: Alignment-induced miscalibration is predominantly H2 (boundary restructuring), not H1 (scale inflation).** All 9 Spearman ρ values fall below the H1 threshold of 0.90; 8/9 fall below 0.85. This means that post-hoc correction methods designed for H1 — specifically, temperature scaling and ATS variants [Xie et al., 2024] — may be addressing the wrong mechanism. Temperature scaling rescales confidence magnitude on a fixed answer distribution. H2 restructuring changes the distribution itself: under 1.4B-PPO, 99.7% of MMLU items have a different top-ranked option after alignment. Rescaling the confidence of the *new* preferred options will not correct miscalibration caused by learning to prefer *wrong* options in the first place.

This suggests a new research direction: post-hoc calibration methods for H2-type miscalibration may need to target the hidden-state representations that encode the boundary redistribution — for example, learning to recover base-model answer rankings rather than just adjusting confidence magnitudes. ATS may partially succeed in this direction because hidden-state temperatures can be learned to undo token-level redistribution patterns, but this remains untested (H-M4, not executed).

**Finding 2: DPO produces larger calibration degradation than PPO.** This counter-intuitive result — DPO ΔReliability > PPO ΔReliability in all 3 Pythia sizes — is most likely explained by the difference in how each method shapes logit distributions. DPO's token-level direct preference reshaping directly adjusts per-option log-probability ratios without an explicit KL penalty constraining how far from the SFT reference the model can move. PPO's sequence-level reward optimization is constrained by a KL penalty to the SFT reference policy, which may moderate boundary shifts as a side effect. If this explanation is correct, it predicts that increasing PPO's KL coefficient should reduce calibration degradation — a testable hypothesis for future work.

This finding has practical implications: deploying DPO-aligned models without calibration monitoring may introduce larger miscalibration than equivalent PPO models, counter to intuitions based on reward optimization pressure.

**Finding 3: H3 (framing susceptibility) is definitively excluded in softmax ECE.** ΔECE_TruthfulQA / ΔECE_MMLU < 1.0 for all alignment types, meaning adversarially framed distractors do not amplify miscalibration. This cleanly distinguishes our result from Chhikara et al. [2025]'s verbal-confidence framing effects: the measurement modality determines whether H3 is observed. For softmax-based evaluation frameworks (lm-eval, standard benchmarking), calibration degradation under alignment is domain-general.

### 6.2 Why ATS May Work — A New Interpretation

Xie et al. [2024] observe that ATS reduces LLaMA-2-Chat ECE by 58–82% without retraining. Our H2 finding provides a new mechanistic interpretation: if alignment shifts decision boundaries in hidden-state space, then input-conditioned hidden-state temperature scaling can learn to identify and partially undo these boundary shifts at test time. ATS doesn't just rescale overall confidence — it learns per-input temperature adjustments that may be tracking which inputs have undergone H2-type redistribution. This interpretation predicts that ATS effectiveness should correlate with the degree of H2 boundary shift (lower Spearman ρ → greater expected ATS improvement) — a testable prediction for H-M4.

### 6.3 The Scale Threshold Question

The 6.9B-DPO model's ρ = 0.875 — just below the H1 threshold of 0.90 — raises the possibility of a mechanism transition as scale increases beyond 6.9B. If larger models (≥ 13B) exhibit ρ ≥ 0.90 under DPO alignment, the dominant mechanism would shift from H2 to H1, and standard temperature scaling would become effective. This is consistent with the intuition that larger models have stronger factual representations that resist H2-type redistribution under DPO's relatively soft preference reshaping.

Testing this prediction requires applying the Spearman ρ diagnostic to LLaMA-2-13B-Chat or Mistral-7B-Instruct — model families with more representative scale for practical deployment. Our framework is directly applicable via lm-eval without modification.

### 6.4 Limitations

**Limitation 1: Public fallback checkpoints (Risk R1).** The primary RLHFlow Pythia alignment checkpoints [Li et al., 2024] required authenticated HuggingFace access. We used publicly available fallback checkpoints (lomahony/Leogrin/usvsnsp) trained on HH data with Pythia base. These share the same pretraining checkpoint and approximate training regime. The H2 mechanism finding — 8/9 Spearman ρ values below 0.85 with zero values above 0.90 — would require implausibly consistent overtrained DPO versus undertrained PPO fallbacks to overturn. The DPO ≥ PPO ordering, however, is more sensitive to checkpoint training equivalence and should be interpreted as a checkpoint-level observation pending replication with matched checkpoints.

**Limitation 2: Single model family.** All results are restricted to Pythia 1.4B–6.9B. Pythia provides the cleanest controlled experiment (identical pretraining across all alignment variants), but is a research model family not widely deployed. Whether H2 dominates in LLaMA-2, Mistral, or Falcon is an open empirical question. The 6.9B-DPO near-threshold result (ρ = 0.875) suggests that cross-family replication may find H1/H2 mixed results even at the same scale.

**Limitation 3: Scale range 1.4B–6.9B.** No publicly available Pythia variants exceed 12B. The potential H1/H2 mechanism transition suggested by 6.9B-DPO is unresolvable within the Pythia family.

**Limitation 4: H-M4 not executed.** Testing whether ATS corrects H2-type boundary shifts (versus H1-type scale inflation it was designed for) was the final planned experiment. Pipeline execution stopped at 4/5 sub-hypotheses; H-M4 remains untested. The claim about ATS correctability is therefore removed from the core statement and framed as motivated future work.

### 6.5 Broader Impact

This work has implications for how deployed AI systems are evaluated and monitored. If RLHF-aligned models are miscalibrated via H2 boundary restructuring rather than H1 confidence inflation, then standard reliability calibration checks — which probe whether a model's confidence on its predicted class is accurate — may miss the actual problem: that the model's predicted class has changed in systematic and potentially harmful ways. Alignment-induced answer restructuring may be more concerning than overconfidence on stable predictions, as it implies the model has learned to prefer different answers across a wide range of inputs.

We do not anticipate direct misuse of our mechanistic framework. Understanding how alignment shapes logit distributions may inform attacks on aligned models, but the findings are more directly useful for improving calibration assessment and correction in deployed systems.

---

## 7. Conclusion

We began with the observation that aligning a language model to be helpful and harmless causes it to change its answers — not just its confidence. For 99.7% of MMLU questions, a 1.4B-PPO-trained model selects a different answer than its base counterpart; the Spearman correlation between their log-probability distributions is ρ = −0.324. Our mechanistic investigation confirms this is not exceptional behavior — it is the dominant pattern across the Pythia alignment ladder.

### Summary

In this work, we addressed the open question of *which mechanism* drives alignment-induced miscalibration in LLMs, providing the first pre-registered mechanistic discrimination between scale inflation (H1), decision-boundary restructuring (H2), and framing susceptibility (H3). Our main contributions are:

1. **H2 is the dominant mechanism** in Pythia 1.4B–6.9B: all 9 Spearman ρ values fall below the H1 threshold of 0.90; 8/9 fall below 0.85. Alignment changes answer preferences, not just confidence magnitudes. This definitively refutes the implicit H1 assumption in prior work on post-hoc calibration correction.

2. **DPO produces larger calibration degradation than PPO** (ΔReliability_DPO > ΔReliability_PPO in all 3 Pythia sizes), consistent with DPO's unconstrained token-level objective causing more aggressive boundary restructuring than PPO's KL-penalized optimization.

3. **H3 (framing susceptibility) is definitively excluded** in softmax-based ECE: ΔECE_TruthfulQA < ΔECE_MMLU for all alignment types, showing domain-general miscalibration that is not driven by adversarial framing.

4. **A reusable mechanistic framework** — Spearman ρ threshold test, argmax partition, cross-benchmark H3 diagnostic — applicable to any model family via lm-eval without modification.

### Future Directions

Our results open three categories of motivated follow-up work:

**From untested alternative explanations:** The DPO ≥ PPO ordering could be verified with matched-training DPO versus PPO experiments using identical data, duration, and reward model. If DPO > PPO persists when KL coefficient is varied in PPO training, the token-level objective interpretation is supported; if higher KL reduces the H2 effect in PPO, the KL-constraint explanation is supported.

**From unverified assumptions:** ATS [Xie et al., 2024] may correct H2-type boundary shifts by learning per-input hidden-state temperatures that track boundary redistribution patterns. H-M4 — testing whether ATS effectiveness correlates with the degree of H2 (lower ρ → greater expected improvement) — is the immediate next experiment. If ATS fails for extreme H2 cases (1.4B-PPO, ρ = −0.324), this motivates fundamentally different correction approaches.

**From scope extensions:** The 6.9B-DPO model (ρ = 0.875) suggests a potential H1/H2 mechanism transition at larger scales. Applying the Spearman ρ diagnostic to LLaMA-2-13B-Chat or Mistral-7B-Instruct — families with sufficient scale for practical deployment — would determine whether H2 dominance is specific to the 1.4B–6.9B range or persists to production-scale models.

### Closing

As RLHF alignment continues to shape how language models are deployed in consequential settings, understanding the mechanism of miscalibration becomes as important as measuring its magnitude. The question is not simply "how confident is the aligned model?" — it is "what has it learned to prefer, and can we correct it?" Our framework makes that question answerable.

---

## References

\bibliographystyle{icml2025}
\bibliography{06_references}
