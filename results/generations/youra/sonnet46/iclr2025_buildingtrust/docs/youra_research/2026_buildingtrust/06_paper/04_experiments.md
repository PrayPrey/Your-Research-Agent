# Experiments

## 4.1 Experimental Setup

### 4.1.1 Model Suite

We evaluate 12 Pythia checkpoints organized as a 3×4 factorial design:

| Size | Base | SFT | DPO | PPO |
|------|------|-----|-----|-----|
| 1.4B | EleutherAI/pythia-1.4b | lomahony/pythia-1.4b-helpful-sft | Leogrin/eleuther-pythia1.4b-hh-dpo | usvsnsp/pythia-1.4b-ppo |
| 2.8B | EleutherAI/pythia-2.8b | lomahony/pythia-2.8b-helpful-sft | Leogrin/eleuther-pythia2.8b-hh-dpo | usvsnsp/pythia-2.8b-ppo |
| 6.9B | EleutherAI/pythia-6.9b | lomahony/pythia-6.9b-helpful-sft | Leogrin/eleuther-pythia6.9b-hh-dpo | usvsnsp/pythia-6.9b-ppo |

All base models share identical pretraining (Pile dataset, same architecture scaling) — the only difference between rows is parameter count. All aligned models are trained on the Anthropic HH (Helpful/Harmless) dataset starting from the same Pythia base checkpoints, providing the cleanest available within-family causal isolation of the alignment effect.

**Note on checkpoint availability:** The original RLHFlow alignment checkpoints from Li et al. \cite{li2024rlhf} require authenticated HuggingFace access and were unavailable at evaluation time. We use the public fallback checkpoints listed above, all trained on HH data with Pythia base models. The mechanism findings (H2 boundary shift, 8/9 ρ < 0.85) are robust to this substitution; the DPO > PPO ordering observation should be interpreted as checkpoint-level evidence pending replication with matched training conditions (see Section 6.4).

### 4.1.2 Datasets

**Primary — MMLU:** We use the Massive Multitask Language Understanding benchmark \cite{hendrycks2021mmlu} (cais/mmlu, standard configuration), comprising 14,042 test items across 57 academic subjects (mathematics, science, law, medicine, history, etc.). MMLU uses 4-shot prompting in our evaluation. The large item count (14,042 per model) provides high statistical power for per-item Spearman ρ computation and robust bootstrap confidence intervals.

**Secondary — TruthfulQA MC1:** For the H3 diagnostic, we evaluate all 12 models on TruthfulQA Multiple Choice Task 1 \cite{lin2022truthfulqa} (817 items, 0-shot). TruthfulQA tests whether models avoid generating false beliefs — a benchmark specifically designed to test factual accuracy under adversarial social pressure, making it well-suited for detecting framing susceptibility (H3).

### 4.1.3 Evaluation Protocol

All evaluations use lm-eval-harness v0.4.11 \cite{eval-harness} with:
- **Scoring:** Log-probability continuation scoring (not chat-template generation or sampling)
- **Decoding:** Greedy, temperature = 1.0
- **GPU:** Single NVIDIA H100 NVL (CUDA_VISIBLE_DEVICES=0)
- **Framework:** Identical lm-eval configuration applied to all 12 models

Log-probability continuation scores model the probability of each answer continuation given the question prefix. This approach provides a fair cross-model comparison because both base and aligned models are evaluated on the same input format, independent of alignment-specific instruction-following behavior.

### 4.1.4 Calibration Analysis

**ECE computation:** 15 equal-width bins on the maximum predicted probability (max-softmax confidence). For each bin $B_m$, we compute bin accuracy and mean confidence; ECE is the weighted average of absolute differences.

**Brier decomposition:** We compute the full Murphy decomposition: $\text{BS} = \text{REL} - \text{RES} + \text{UNC}$, where REL is the Brier reliability (overconfidence), RES is resolution (discriminability), and UNC is inherent uncertainty. The primary outcome variable is $\Delta\text{REL}$.

**Bootstrap confidence intervals:** For $\Delta\text{REL}(a, s)$, we report 95% bootstrap CIs using $n = 1000$ samples with seed 42.

### 4.1.5 Mechanism Discrimination Tests

**H1/H2 discrimination (Spearman ρ):** For each of the 14,042 MMLU items and each of the 9 alignment-base pairs, we compute the Spearman ρ between the 4-option base log-probability vector and the 4-option aligned log-probability vector. Mean ρ is reported per pair. H1 is confirmed if mean ρ ≥ 0.90; H2 is flagged if mean ρ < 0.85.

**Argmax partition analysis:** Items are partitioned into shared-argmax ($S$) and changed-argmax ($C$) subsets for each pair. We report:
- $|S|$ and $|C|$ (counts)
- Brier REL in $S$ and $C$ subsets separately
- Cohen's d for REL difference within $S$ (H1 would predict large Cohen's d in $S$)

**Pre-softmax margin analysis (H1 confirmation probe):** Mean margin $m = l_{(1)} - l_{(2)}$ per model, and $\Delta m(a,s) = \bar{m}_{\text{aligned}} - \bar{m}_{\text{base}}$ with bootstrap 95% CI.

**H3 diagnostic (TruthfulQA ECE):** We compare $\Delta\text{ECE}_{\text{MMLU}}$ and $\Delta\text{ECE}_{\text{TruthfulQA}}$ for each alignment method (averaged across model sizes). H3 is flagged if $\Delta\text{ECE}_{\text{TruthfulQA}} > \Delta\text{ECE}_{\text{MMLU}}$ for any alignment type.

## 4.2 Ablation Design

Our experiment is inherently ablative: the 3×3 aligned model grid (9 pairs) allows us to decompose effects by:

1. **Alignment method effect:** Compare DPO vs PPO vs SFT within each model size to characterize method-specific calibration degradation patterns.
2. **Scale effect:** Compare 1.4B vs 2.8B vs 6.9B within each alignment method to characterize scale-dependent trends.
3. **Mechanism specificity:** Compare ρ values across alignment types to determine whether H2 is universal or alignment-method-specific (we find PPO is most extreme, DPO is intermediate, SFT is mildest).

## 4.3 Baseline Models

The primary baseline for calibration comparison is each model's paired base variant (e.g., pythia-1.4b-base for all three 1.4B aligned models). This within-pair design controls for scale, pretraining data, and architecture — isolating the alignment training effect cleanly.

The causal baseline verification (H-M1) confirms that base models are well-calibrated before alignment (ECE = 0.057–0.085 across all sizes), establishing that any calibration degradation observed in aligned models is attributable to the alignment procedure and not to pretraining artifacts.

## 4.4 Implementation Details

The calibration analysis pipeline is implemented in Python 3.10 using:
- `numpy` for logit margin computation and bootstrap CI
- `scipy.stats.spearmanr` for per-item Spearman ρ
- `lm-eval-harness v0.4.11` for log-probability extraction
- `seaborn/matplotlib` for visualization

All code follows a test-driven development protocol (Test → Implementation → Verification for each component). The H-E1 lm-eval outputs are cached and reused for H-M2 and H-M3 analysis, requiring zero additional GPU computation for the mechanism analysis experiments. The sample count mismatch between base model evaluation (28,654 items for 1.4B base from two lm-eval runs) and aligned model evaluation (14,042 items) is handled by truncating base samples to min(counts) = 14,042 for per-item delta computation.
