# Experimental Setup

We structure our evaluation around two sequential research questions that test the
alignment fingerprint from existence to mechanism:

**RQ1 (h-e1 — Fingerprint Existence):** Is the 4D trustworthiness benchmark profile
of DPO-aligned 7B models systematically separable from SFT-aligned models, at
statistically significant leave-one-out classification accuracy (≥67%, permutation p≤0.05)?

**RQ2 (h-m1 — Discriminative Dimensions):** Which benchmark dimension drives the
alignment fingerprint? Does DPO show a systematic fairness advantage on BBQ and WinoGender
(≥4/6 pairs, one-sided binomial p≤0.125)?

These questions directly map to contributions C1 and C2 from the Introduction.
RQ1 tests whether alignment fingerprinting is feasible; RQ2 tests whether the mechanism
matches the dominant theoretical prediction (DPO improves fairness).

## Models

We evaluate 12 publicly available 7B-parameter models across 6 DPO/SFT matched pairs
(Table 1). Models were selected to maximize base-model control while reaching the minimum
n=6 pairs required for permutation significance.

**Table 1: Model pairs evaluated.**

| Pair | SFT Model | DPO Model | Base Model |
|------|-----------|-----------|------------|
| P1 | Mistral-7B-Instruct-v0.1 | zephyr-7b-alpha | Mistral-7B-v0.1 |
| P2 | OpenHermes-2.5-Mistral-7B | zephyr-7b-beta | Mistral-7B-v0.1 |
| P3 | tulu-2-7b | tulu-2-dpo-7b | LLaMA-2-7B |
| P4 | Llama-2-7b-chat (RLHF) | neural-chat-7b-v3-1 | LLaMA-2-7B |
| P5 | openchat_3.5 | Starling-LM-7B-alpha | Mistral-7B-v0.1 |
| P6 | Mistral-7B-Instruct-v0.3 | neural-chat-7b-v3-3 | Mistral-7B-v0.1 |

The primary controlled pair (P1: zephyr-alpha/beta from the Alignment Handbook) shares
both base model and training data; community pairs (P2-P6) are matched on base model
where documentation permits. One pair (P4) includes Llama-2-chat, labeled as RLHF/SFT
in our dataset despite RLHF alignment — we report this label assignment and its
implications in Results.

## Benchmark Suite

Each model is evaluated on four benchmarks via `lm-evaluation-harness v0.4.3`:

**Table 2: Benchmark suite.**

| Benchmark | Task | Metric | Dimension | Predicted DPO Direction |
|-----------|------|--------|-----------|------------------------|
| TruthfulQA MC2 | `truthfulqa_mc2` | MC2 acc. (log-prob) | Truthfulness | Neutral-to-lower |
| BBQ | `bbq` | Accuracy | Social fairness | Higher (primary signal) |
| WinoGrande | `winogrande` | Accuracy | Commonsense | Neutral |
| WinoGender | `winograd_wsc` | Accuracy | Gender fairness | Higher |

The predicted direction column reflects the original mechanism hypothesis: DPO's
preference data rewards bias-avoidance (raising fairness) without explicit factual
reward (leaving truthfulness neutral). This prediction is explicitly tested by RQ2.

## Evaluation Protocol

All models are evaluated with `--batch_size 8`, `--dtype bfloat16`, `--limit 100`
samples per task on 5× NVIDIA H100 NVL GPUs. The 100-sample limit is a PoC speed
constraint; the critical null result in RQ2 is far from threshold and robust to this
limitation (Section 6.2).

## Classification Protocol (RQ1)

Each model's evaluation yields a 4-dimensional score vector `x_i ∈ [0,1]^4`. We
construct design matrix `X ∈ R^{12×4}` with binary labels `y ∈ {0=SFT, 1=DPO}^{12}`.

**Classifier:** k-NN (k=1, Euclidean distance) with leave-one-out cross-validation
(LOO-CV) over n=12 models. LOO-CV is chosen over k-fold for small n to maximize
training data per fold.

**Significance:** Permutation test (1000 shuffles, seed=42) of label assignment.
Null hypothesis: LOO accuracy ≤ chance (50%). Significance threshold: one-tailed p≤0.05.

We also report sensitivity over k=1,3,5 to verify that results do not depend on
k-selection.

## Mechanism Analysis Protocol (RQ2)

For each benchmark j independently, we compute:

1. **Fisher's linear discriminant criterion:** `Fisher(j) = (μ_DPO,j − μ_SFT,j)² / (σ²_DPO,j + σ²_SFT,j)`
2. **Paired sign test:** `k_j` = number of pairs where DPO > SFT; one-sided binomial p-value under H₀: k ~ Binomial(6, 0.5)

The primary test for RQ2 is `k_BBQ ≥ 4/6` and `p_BBQ ≤ 0.125`. The Fisher criterion
analysis identifies which dimension carries the most discriminative signal and whether
it matches the theoretical prediction.

## Baseline

The natural baseline for RQ1 is the permutation null distribution — random label
assignment. For RQ2, the baseline is binomial chance (50% of pairs show DPO>SFT).
No external model baselines are needed for fingerprinting classification.
