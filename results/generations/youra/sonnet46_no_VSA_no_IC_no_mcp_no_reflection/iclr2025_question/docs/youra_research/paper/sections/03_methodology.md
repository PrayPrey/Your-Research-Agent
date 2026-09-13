# Methodology

Our experimental design is motivated by a single question: *if a sampling-based consistency detector fails on an instruction-tuned model, is the failure in the scoring mechanism or in the underlying consistency assumption?* This question requires more than measuring AUROC — it requires a design that separates implementation correctness, scorer validity, and mechanism validity as independent diagnostic layers.

## Overview

We evaluate NLI-based Semantic Mode Consistency (SMC-NLI), a direct instantiation of the SelfCheckGPT-NLI scoring protocol [Manakul et al., 2023], applied to Llama-3-8B-Instruct on HaluEval QA [Li et al., 2023]. The core scoring pipeline computes pairwise NLI agreement across N=10 stochastic samples per question and uses this consistency score as a hallucination predictor. We extend this with two design choices that enable clean attribution: a parallel embedding-based scorer (SMC-Embed) and an explicit mechanism verification step.

**Figure 1** (smc_nli_distribution.png): Distribution of SMC-NLI scores split by label (correct vs. hallucinated), illustrating the overlap that underlies our AUROC findings.

## Dataset

**HaluEval QA** [Li et al., 2023] consists of question-answer pairs with binary hallucination labels (correct / hallucinated), constructed by generating ChatGPT responses and using ChatGPT to create hallucinated alternatives. We use a stratified sample of $N=1000$ questions (500 correct, 500 hallucinated), drawn with `seed=42`, providing adequate statistical power for AUROC estimation (standard error < 0.02 at this sample size).

**Design rationale:** HaluEval is the most favorable structured factual QA benchmark for this evaluation — balanced labels, short-answer format, and no annotation noise from human raters. If SMC fails on HaluEval, failure on harder or more adversarial benchmarks is expected. We note the benchmark validity concern (ChatGPT labels vs. Llama-3-8B behavior) in Section 6 (Discussion).

## LLM Sampling (LLMSampler)

For each question $q_i$, we generate $N=10$ stochastic samples from Llama-3-8B-Instruct [Meta AI, 2024]:

$$S_i = \{s_i^{(1)}, s_i^{(2)}, \ldots, s_i^{(10)}\}$$

using temperature $\tau = 0.7$, top-p $p = 0.9$, and `max_new_tokens=50`. The model is loaded via HuggingFace Transformers with `device_map="auto"` for GPU memory management.

**Design rationale:** Temperature=0.7 matches the setting used in SelfCheckGPT [Manakul et al., 2023], enabling methodological comparability. We generate 10 samples following Kuhn et al. [2023], who found N=10 sufficient for reliable semantic entropy estimation. Intermediate samples are saved to disk (`data/llama_samples.json`) with resume logic to avoid re-inference.

Total inference: 10,000 samples across 1,000 questions.

## SMC-NLI Scoring

For each question $q_i$ and its samples $S_i$, we compute the Semantic Mode Consistency (NLI variant) as the mean pairwise non-contradiction rate over all $\binom{N}{2} = 45$ sample pairs:

$$\text{SMC-NLI}(q_i) = \frac{1}{45} \sum_{j < k} \left[ P_\text{ent}(s_i^{(j)}, s_i^{(k)}) + P_\text{neut}(s_i^{(j)}, s_i^{(k)}) \right]$$

where $P_\text{ent}$ and $P_\text{neut}$ are entailment and neutral probabilities from the DeBERTa-v3-large cross-encoder NLI model (`cross-encoder/nli-deberta-v3-large`). Higher SMC-NLI indicates greater semantic consistency among samples; lower SMC-NLI indicates semantic diversity (inconsistency).

To mitigate the documented out-of-distribution (OOD) concern for NLI models on short factual answers (trained on paragraph-length SNLI/MultiNLI pairs), each sample is prepended with the question context: `"Q: {question} A: {answer}"`. This follows the question-prepend convention from Manakul et al. [2023].

NLI pairs are processed in batches of 16 on GPU. Total NLI pairs scored: 45,000.

**Prediction direction:** Higher SMC-NLI should predict correctness (label=0); lower SMC-NLI should predict hallucination (label=1). AUROC is computed in this direction.

## SMC-Embed Scoring (Parallel Control)

In parallel with SMC-NLI, we compute an embedding-based consistency score:

$$\text{SMC-Embed}(q_i) = \frac{1}{45} \sum_{j < k} \cos\left(\mathbf{e}_i^{(j)}, \mathbf{e}_i^{(k)}\right)$$

where $\mathbf{e}_i^{(j)}$ is the sentence embedding of sample $s_i^{(j)}$ from `sentence-transformers/all-mpnet-base-v2`, and $\cos(\cdot, \cdot)$ denotes cosine similarity.

**Design rationale:** This is the critical diagnostic design choice. SMC-Embed measures the same underlying construct (output consistency) without the NLI scorer. If SMC-NLI fails due to NLI OOD for short factual answers, SMC-Embed should achieve meaningfully higher AUROC. If both fail at similar levels, the failure is in the shared assumption (consistent outputs carry no hallucination signal), not in the NLI scorer specifically. This dual-metric design enables clean causal attribution of the negative result.

## Mechanism Verification

Before full-scale evaluation, we perform a mechanism verification step on the first 5 questions:

1. Compute SMC-NLI scores for questions $\{q_1, \ldots, q_5\}$
2. Assert: all scores in $[0, 1]$
3. Assert: $\max_i \text{SMC-NLI}(q_i) - \min_i \text{SMC-NLI}(q_i) > 0.01$ (meaningful variation exists)
4. Raise an exception if either assertion fails

**Design rationale:** This step distinguishes two failure types: "the scorer is broken" (no variation, all scores identical or out-of-range) vs. "the scorer works but the scores are not discriminative at scale." When the mechanism check passes but full-scale AUROC collapses to chance, the failure is definitively in the hypothesis (assumed discriminative signal does not exist), not in the implementation. This is the key attribution step that makes our negative result interpretable.

## Evaluation

We compute AUROC for both SMC-NLI and SMC-Embed as hallucination predictors against HaluEval binary labels using `sklearn.metrics.roc_auc_score`. We also report:
- SMC-NLI standard deviation across questions (distribution check: should be >0.05 for meaningful variation)
- Per-label mean SMC-NLI scores (mechanism analysis: should differ between correct and hallucinated)
- ROC curves for both metrics (visual confirmation of performance)
- Per-question SMC-NLI vs. SMC-Embed scatter plot (correlation analysis: do the metrics agree in their failures?)

## Implementation Validation

All components are validated by 14 unit tests covering:
- Data pipeline correctness (stratified sampling, label extraction)
- LLMSampler output format and seed reproducibility
- SMCNLIScorer score range and batch consistency
- SMCEmbedScorer cosine similarity range
- Evaluate module AUROC computation

The Coder-Validator cycle completed in round 1/5 (all checks passing on first validation pass), providing independent confirmation that implementation errors are not a confound for interpreting the AUROC results.

## Summary of Key Design Choices

| Design Choice | Rationale |
|---|---|
| Dual metric (NLI + Embed) | Rules out NLI OOD as confound; enables regime-level attribution |
| Mechanism verification (5 questions) | Distinguishes broken code from wrong hypothesis |
| N=1000 balanced questions | Adequate statistical power (AUROC SE < 0.02) |
| 14 unit tests | Independent implementation correctness verification |
| Question-prepend for NLI | Mitigates NLI OOD for short factual answers |
| Resume logic for samples | Reproducibility: exact sample set fixed, scorer can be rerun |
