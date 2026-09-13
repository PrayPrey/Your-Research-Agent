# Experimental Setup

Our experiments are designed to test the three-step mechanism hypothesis in order of increasing specificity: first establishing that aggregation function choice matters (h-e1), then verifying the distributional mechanism (h-m1), then confirming rank-level predictions (h-m2), and finally quantifying threshold-level AUROC differentials (h-m3). Each experiment answers a specific research question that maps directly to a claim in the Introduction.

**RQ1** (h-e1): Does the choice of token log-probability aggregation function produce statistically different AUROC values on factual QA benchmarks?

**RQ2** (h-m1): Do recall-failure hallucinations produce peaked token probability distributions compared to correct responses on TriviaQA?

**RQ3** (h-m2): Does rank-order correlation (Spearman ρ) confirm the directional advantage of min over mean on factual recall and mean over min on imitative falsehood, at the signal level?

**RQ4** (h-m3): Do AUROC threshold differentials confirm the directional predictions (P1, P2) with ≥0.02 margin and bootstrap 95% CI excluding zero?

## Datasets

| Dataset | Type | N (per model) | Label Protocol | Hallucination Class |
|---------|------|---------------|----------------|---------------------|
| TriviaQA | Factual recall | ~488–500 | Exact match vs. reference answers [Farquhar 2023 splits] | Recall-failure |
| TruthfulQA (gen. subset) | Imitative falsehood | ~810–817 | ROUGE-L ≥ 0.3 vs. best reference [Fadeeva 2024 protocol] | Imitative-falsehood |

**TriviaQA** [Joshi et al., 2017], accessed via the Farquhar 2023 semantic_uncertainty splits (`jlko/semantic_uncertainty`), provides reproducible binary-correctness labels for factual recall. We subsample to ≈488–500 questions due to cache-efficient inference. This split is the standard in the uncertainty estimation literature and enables direct comparison to Fadeeva et al. [2024] and Farquhar et al. [2023].

**TruthfulQA** [Lin et al., 2021], using the HuggingFace generation subset, provides the imitative-falsehood evaluation. Binary correctness is assigned by ROUGE-L ≥ 0.3 against the best reference answer, following Fadeeva et al. [2024]. The full generation subset (810–817 questions) is used without subsampling.

The two benchmark types are selected to represent the two poles of the hallucination-type taxonomy: factual recall (uncertainty concentrated at fact-token) vs. imitative falsehood (uncertainty distributed across all tokens). NQ (Natural Questions), a second factual recall benchmark, was planned but is unavailable due to a data cache gap in h-e1 (inference ran but .npz was not persisted).

## Models

All experiments use frozen open-weight LLMs at 7B parameter scale:

- **LLaMA-2-7B** (`meta-llama/Llama-2-7b-hf`): Llama architecture, 2T token pretraining.
- **Mistral-7B-v0.1** (`mistralai/Mistral-7B-v0.1`): Sliding-window attention, 7.3T token pretraining.

Both models are evaluated under identical inference conditions. Cross-architecture replication — consistent directional effects across LLaMA and Mistral — is the primary generalizability evidence within the 7B parameter scale.

## Implementation Details

**Inference:** Single greedy forward pass (`do_sample=False`, `max_new_tokens=30`, `batch_size=1`). Batch size 1 is mandatory for numerical correctness of per-token log-probability extraction under flash_attention_2. Model weights are frozen throughout (no fine-tuning, no LoRA). Precision: fp16, `device_map=auto`. Hardware: H100 NVL GPU (24GB VRAM).

**Aggregation functions:**
```
min(logprobs):   minimum token log-probability (worst-case token)
mean(logprobs):  mean token log-probability (length-normalized)
sum(logprobs):   unnormalized sum (= sequence-level log P(answer))
```
All three are applied to generated tokens only (not prompt tokens). Scores are negated before AUROC computation (more negative → higher uncertainty → predicted hallucinated).

**Custom implementation:** lm-polygraph [Fadeeva et al., 2024] was evaluated but found incompatible with the target hardware environment. We implement aggregation and evaluation directly. All 22 unit tests pass, verifying correctness of log-probability extraction, aggregation arithmetic, and AUROC computation.

**Reproducibility:** Seed 42 throughout. Bootstrap resampling with n=1000. Farquhar 2023 evaluation splits used as-is from the `jlko/semantic_uncertainty` repository.

## Evaluation Metrics

**AUROC** (Area Under ROC Curve): Primary metric. Threshold-independent; standard in the uncertainty estimation literature. Scores are compared against binary correctness labels.

**Spearman ρ** (rank-order correlation): Used in h-m2 as the mechanism-level metric. Measures whether uncertainty scores rank hallucinated responses above correct responses, independent of threshold or absolute score scale. ρ > 0 indicates correct ranking direction.

**Bootstrap 95% CI for pairwise differentials**: Percentile bootstrap with n=1000 resamples. Reported as (CI_lower, CI_upper) for AUROC(A)−AUROC(B) and ρ(A)−ρ(B). A CI excluding zero indicates statistical significance at the 5% level.

**Peakedness ratio**: Used in h-m1 for distributional analysis. Composite score combining response kurtosis and max-to-mean log-probability ratio. Higher peakedness = more concentrated (peaked) distribution.

## Baselines

The comparison in this work is an internal ablation — three aggregation functions applied to the same model output, not a comparison of distinct methods. External literature baselines provide reference points for absolute AUROC values:

| Method | Inference Cost | Published AUROC (TriviaQA) | Source |
|--------|---------------|---------------------------|--------|
| Mean log-prob (CCP) | 1 forward pass | 0.72–0.80 | Fadeeva et al. [2024] |
| Predictive entropy (sum, normalized) | 1 forward pass | ~0.72 | Farquhar et al. [2023] |
| Semantic Entropy | 10 forward passes | ~0.79 | Farquhar et al. [2023] |
| SelfCheckGPT (NLI variant) | 20 forward passes | 0.72–0.78 | Manakul et al. [2023] |

These are literature baselines — they are not re-implemented in the same pipeline. We report our single-pass results alongside these published figures to contextualize the practical significance of our findings.
