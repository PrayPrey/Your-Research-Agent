# 3. Methodology

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
