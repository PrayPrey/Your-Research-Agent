# 4. Experimental Setup

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
