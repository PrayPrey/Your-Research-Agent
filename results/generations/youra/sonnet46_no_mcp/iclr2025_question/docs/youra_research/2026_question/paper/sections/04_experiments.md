# Experimental Setup

We design our experiments to answer three research questions that directly map to our contributions:

**RQ1:** Do token entropy, semantic entropy, and SelfCheckGPT-BERTScore produce measurably different AUROC for binary hallucination detection on HaluEval-QA with LLaMA-2-7B-chat under matched inference conditions?

**RQ2:** Is the correlation between token entropy and semantic entropy scores consistent with the claim that NLI clustering filters surface-form noise — or does the correlation structure suggest a different relationship?

**RQ3:** Does the NLI clustering mechanism of semantic entropy (deberta-large-mnli bidirectional entailment) successfully aggregate stochastic responses into semantic clusters on HaluEval-QA short factual QA responses?

RQ1 tests the main comparative claim (H-E1: EXISTENCE). RQ2 and RQ3 test the causal mechanism (H-M1: token-semantic divergence; H-M2: NLI aggregation). The mechanism questions are designed so that their answers causally explain the AUROC outcomes — making the results interpretable rather than descriptive.

## Dataset

**HaluEval-QA** [Li et al., 2023] (pminervini/HaluEval, QA subset): 2,000 stratified examples (1,000 hallucinated, 1,000 factual), sampled with seed=42 from the full dataset. Each example consists of a question, a factual reference answer, and a ChatGPT-generated hallucinated alternative answer. Binary labels: 1 = hallucinated, 0 = factual.

| Property | Value |
|----------|-------|
| Total examples | 2,000 |
| Hallucinated examples | 1,000 (50%) |
| Factual examples | 1,000 (50%) |
| Response length (typical) | 5–15 tokens |
| Label type | Binary (ChatGPT-generated) |
| Source | pminervini/HaluEval (HuggingFace) |

The 50% base rate ensures AUROC is directly interpretable as discrimination above 0.5 (random). The short response length (5–15 tokens) is the critical characteristic distinguishing HaluEval-QA from TriviaQA/NQ (typically 20–50 tokens), and is the primary reason we expect NLI clustering to behave differently.

## Model

**LLaMA-2-7B-chat** (meta-llama/Llama-2-7b-chat-hf): 7B parameter instruction-tuned language model in float16 precision. Run on a single NVIDIA H100 NVL GPU (CUDA_VISIBLE_DEVICES=4).

The same model produces all inference outputs reused across methods:
- **Greedy pass** (temperature=0.0, max\_new\_tokens=256): generates reference responses and token-level logits for token entropy
- **Stochastic passes** (temperature=1.0, N=5, max\_new\_tokens=256): generates 5 diverse responses for semantic entropy NLI clustering and SelfCheckGPT consistency scoring

All stochastic samples are generated once and cached to disk (JSONL format) — ensuring semantic entropy and SelfCheckGPT evaluate identical sets of samples, eliminating inference variance as a confound.

## UQ Methods (Compared)

| Method | Signal Type | Inference Cost | Implementation |
|--------|-------------|----------------|----------------|
| **Token Entropy (TE)** | Per-token Shannon entropy (mean) | 1× greedy | Local implementation (fp16-safe) |
| **Semantic Entropy (SE)** | NLI cluster entropy over N=5 stochastic samples | N+1× inference + NLI pairs | lorenzkuhn/semantic\_uncertainty |
| **SelfCheckGPT-BERTScore (SCG)** | BERTScore consistency (greedy vs. stochastic) | N+1× inference | potsawee/selfcheckgpt |

All methods share the greedy and stochastic inference outputs. The marginal cost difference (NLI pairwise classification for SE; BERTScore computation for SCG) is the only additional inference beyond the shared N+1 passes.

**Baselines rationale:** Token entropy (TE) is the theoretical lower bound for semantic entropy — if NLI filtering works, SE should strictly outperform TE. SelfCheckGPT (SCG) is an orthogonal approach (consistency-based vs. entropy-based) that serves as an out-of-family comparison. The three methods span the practical design space for zero-resource, training-free UQ-based hallucination detection.

## Implementation Details

| Hyperparameter | Value | Source |
|----------------|-------|--------|
| `greedy_temperature` | 0.0 | Standard deterministic inference |
| `stochastic_temperature` | 1.0 | Standard stochastic sampling (Manakul et al., 2023) |
| `max_new_tokens` | 256 | Sufficient for short QA responses |
| `n_stochastic_samples` (N) | 5 | Minimum budget validated by Manakul et al. (2023) |
| `nli_model_id` | microsoft/deberta-large-mnli | lorenzkuhn/semantic\_uncertainty default |
| `nli_batch_size` | 16 | Memory-efficient NLI inference |
| `n_bootstrap` | 1,000 | Bootstrap CI estimation |
| `bonferroni_k` | 3 | Number of pairwise comparisons |
| `alpha` | 0.05 (corrected: 0.0167) | Family-wise significance level |
| `min_auroc_gap` | 0.05 | Minimum effect size for qualifying pair |
| `seed` | 42 | Data stratification + bootstrap resampling |
| GPU | NVIDIA H100 NVL | Single GPU; CUDA\_VISIBLE\_DEVICES=4 |

Inference is checkpoint-resumable: greedy logits persist as .pt files per example, stochastic samples as JSONL, SelfCheckGPT scores as JSON. This was critical given SelfCheckGPT's ~5 seconds/example inference time (~2.7 hours for 2,000 examples on H100).

The NLI model (deberta-large-mnli) is unmodified from HuggingFace. Bidirectional entailment uses union-find clustering identical to the original lorenzkuhn/semantic\_uncertainty implementation.

## Evaluation Metrics

**Primary: AUROC** — Area Under the ROC Curve for binary hallucination vs. factual classification. AUROC measures discrimination ability across all operating thresholds without requiring threshold selection. Range [0, 1]; AUROC = 0.5 corresponds to random discrimination; AUROC > 0.5 indicates positive discrimination; AUROC < 0.5 indicates negative discrimination (inverted signal).

**Confidence intervals:** 95% bootstrap CIs (N=1,000 resamples, stratified by label, seed=42). Bootstrap CIs are distribution-free and directly applicable to AUROC without normality assumptions.

**Pairwise significance criterion:** A method pair qualifies as significantly different if (1) Δ AUROC ≥ 0.05 and (2) 95% bootstrap CIs are non-overlapping. Both conditions apply Bonferroni correction (α\_corrected = 0.05/3 = 0.0167 for 3 pairwise comparisons). This is a conservative criterion requiring both a minimum practical effect size and statistical non-overlap.

**Mechanism metrics:**
- *Pearson r(TE, SE)* (H-M1): correlation between token entropy and semantic entropy scores, with 95% bootstrap CI. Gate condition: CI upper bound < 0.9.
- *NLI aggregation rate* (H-M2): fraction of examples with NLI cluster count strictly less than N=5. Gate condition: ≥ 0.50 (PASS); < 0.30 CI lower bound (PIVOT). Bootstrap 95% CI (N=1,000 resamples).

## Sub-Hypothesis Structure

The three experiments are executed in dependency order:

```
H-E1 (EXISTENCE)  ──→  H-M1 (MECHANISM Step 1)  ──→  H-M2 (MECHANISM Step 2)
  AUROC comparison        TE-SE correlation                NLI aggregation rate
  Gate: MUST_WORK         Gate: MUST_WORK                  Gate: SHOULD_WORK
```

H-M1 reuses H-E1's stochastic sample outputs (zero new inference). H-M2 reuses H-M1's cluster distribution data. This cascade design maximizes computational efficiency while enabling causal attribution of the AUROC outcome to specific mechanism violations.
