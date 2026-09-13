# 4. Experiments

## 4.1 Research Questions

This work investigates uncertainty quantification for hallucination detection in large language models through four research questions:

**RQ1 (Feasibility):** Can token-level entropy and semantic consistency metrics be reliably computed from LLM outputs at inference time?

**RQ2 (Entropy Signal):** Does higher token entropy correlate with incorrect answers, enabling entropy-based hallucination detection?

**RQ3 (Consistency Signal):** Does lower semantic consistency across multiple responses correlate with incorrect answers?

**RQ4 (Fusion Benefit):** Does combining entropy and consistency signals improve predictive performance over either metric alone?

## 4.2 Hypotheses and Gates

We structure our investigation around four hypotheses with explicit pass/fail gates to ensure rigorous validation:

**H-E1 (Existence):** Token entropy and semantic consistency can be computed for all generated responses.
- Gate type: MUST_WORK
- Criteria: >99% computation success rate for both metrics

**H-M1 (Entropy Correlation):** Token entropy from Llama-2-7B-chat correlates with answer correctness on TriviaQA.
- Gate type: MUST_WORK
- Criteria: p < 0.05, AUROC > 0.55, mean entropy for incorrect > correct

**H-M2 (Consistency Correlation):** Semantic consistency across multiple responses discriminates between correct and incorrect outputs.
- Gate type: SHOULD_WORK
- Criteria: p < 0.05, AUROC > 0.55, mean consistency for correct > incorrect

**H-M3 (Linear Fusion):** Linear combination of inverse entropy and consistency outperforms the best single metric.
- Gate type: SHOULD_WORK
- Criteria: AUROC_combined > max(AUROC_entropy, AUROC_consistency)

The distinction between MUST_WORK and SHOULD_WORK gates reflects research maturity: MUST_WORK hypotheses establish foundational capabilities that must succeed for the research program to proceed, while SHOULD_WORK hypotheses test promising but uncertain extensions that inform rather than invalidate the approach.

## 4.3 Experimental Setup

### Model and Dataset

We conduct experiments using Llama-2-7B-chat (Touvron et al., 2023), a 7-billion parameter instruction-tuned model representative of modern open-weight LLMs. We evaluate on TriviaQA (Joshi et al., 2017) using the rc.nocontext validation split, which provides factual questions without supporting passages, requiring the model to rely on parametric knowledge.

### Generation Protocol

For each question, we generate N=10 independent responses using temperature sampling (T=0.7). This temperature balances response diversity against coherence, enabling meaningful consistency measurement while avoiding degenerate outputs. We use a fixed random seed (42) for reproducibility.

### Metric Computation

**Token Entropy:** We compute the mean token-level entropy across all generated tokens:
$$H = -\sum_{t} p(t) \log p(t)$$
where p(t) is the softmax probability of each token. Higher entropy indicates greater model uncertainty.

**Semantic Consistency:** We embed all N responses using Sentence-BERT (all-MiniLM-L6-v2) and compute mean pairwise cosine similarity:
$$C = \frac{2}{N(N-1)} \sum_{i<j} \cos(\mathbf{e}_i, \mathbf{e}_j)$$
where e_i is the embedding of response i. Higher consistency indicates stable model behavior.

**Answer Correctness:** We determine correctness via exact-match comparison against TriviaQA's gold answers, using majority voting across the 10 responses per question.

### Sample Sizes

H-M1 uses N=100 questions for statistical power in establishing the foundational entropy signal. H-M2 and H-M3 use N=20 questions as a proof-of-concept validation, sufficient to detect large effects but acknowledged as a limitation (Section 6).

## 4.4 Evaluation Protocol

### Statistical Tests

We assess hypothesis validity using multiple complementary measures:

**Welch's t-test:** Tests whether mean metric values differ significantly between correct and incorrect answer groups. We report one-sided p-values aligned with directional hypotheses.

**Effect Size (Cohen's d):** Quantifies practical significance independent of sample size. We interpret d < 0.2 as negligible, 0.2-0.5 as small, 0.5-0.8 as medium, and > 0.8 as large (Cohen, 1988).

**AUROC:** Area under the receiver operating characteristic curve measures discriminative ability. AUROC = 0.5 indicates random performance; values > 0.55 suggest meaningful signal.

**Pearson Correlation:** For H-M3, we measure entropy-consistency correlation to assess signal complementarity.

### Fusion Methodology

For H-M3, we evaluate linear fusion scores of the form:
$$S = \alpha \cdot (1 - H) + \beta \cdot C$$
where H is normalized entropy and C is consistency. We perform grid search over alpha, beta in [0, 1] with step 0.1 using a 10%/90% validation/test split, selecting weights that maximize validation AUROC. We compute 95% confidence intervals via 1000-sample bootstrap.

### Success Criteria Summary

| Hypothesis | Primary Metric | Threshold |
|------------|---------------|-----------|
| H-E1 | Computation success | > 99% |
| H-M1 | AUROC | > 0.55 |
| H-M2 | AUROC | > 0.55 |
| H-M3 | AUROC improvement | > 0 |

All hypotheses additionally require p < 0.05 for statistical significance and correct directionality (entropy higher for incorrect, consistency higher for correct).
