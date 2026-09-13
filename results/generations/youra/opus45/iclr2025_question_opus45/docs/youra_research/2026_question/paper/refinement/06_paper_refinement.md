# Configuration Sensitivity in Semantic Entropy Probing: A Negative Result

## Abstract

Semantic entropy (SE) provides effective hallucination detection in large language models but requires computationally expensive multi-sample generation. Semantic Entropy Probes (SEPs) have been proposed as efficient single-pass estimators that extract uncertainty information from hidden states, with published results reporting AUROC approximately 0.85 on TruthfulQA. This work attempted to extend the SEP approach with similarity-augmented training, hypothesizing that semantic similarity features would enable cross-model transfer. The experiment yielded negative results: the proposed SE-Distilled Probe (SEDP) achieved Spearman correlation rho = 0.0843 with true semantic entropy (p = 0.283), statistically indistinguishable from zero, and AUROC = 0.52, indistinguishable from random classification. The baseline SEP achieved comparable performance (rho = 0.0835, AUROC = 0.5214). These results represent a 39% AUROC gap relative to published benchmarks. The experiment tested a single configuration: layer 25 of Llama-3-8B-Instruct, Token-Before-Generation position, and logistic regression probe architecture. The failure may reflect configuration sensitivity rather than fundamental limitations of the probing approach. This work documents the negative result to highlight that SE probe deployment may require systematic validation across layers, token positions, and architectures.

## 1. Introduction

Semantic entropy (SE) has emerged as an effective approach for hallucination detection in large language models, achieving AUROC values between 0.76 and 0.97 across various benchmarks (Farquhar et al., 2024). SE measures uncertainty by clustering semantically equivalent responses and computing entropy over these clusters. However, SE computation requires generating 10-20 diverse responses per query and performing pairwise entailment checks via natural language inference models, resulting in substantial computational overhead that limits real-time deployment.

Semantic Entropy Probes (SEPs) address this limitation by training lightweight probes on LLM hidden states to predict SE in a single forward pass (Kossen et al., 2024). Published results indicate that SEPs achieve AUROC within 2-3% of full SE on TruthfulQA.

This work attempted to extend the SEP approach with SE-Distilled Probes (SEDP), which incorporate semantic similarity features as auxiliary training signals. The hypothesis was that similarity structure, computed on output text rather than internal representations, would provide model-agnostic regularization enabling cross-model transfer. The initial experiment tested whether SEDP could achieve meaningful SE correlation (Spearman rho >= 0.3) on same-model evaluation as an existence proof.

The experiment produced negative results. SEDP achieved Spearman rho = 0.0843 with true SE (p = 0.283), failing to reach the threshold of 0.3 by a margin of 72%. Both SEDP and the baseline SEP achieved AUROC approximately 0.52, effectively indistinguishable from random classification. The delta between SEDP and SEP was +0.0009 in correlation and +0.0004 in AUROC, indicating negligible contribution from similarity features.

The 39% gap between the achieved AUROC (0.52) and published benchmarks (approximately 0.85) represents a substantial discrepancy. This gap may arise from configuration sensitivity—the experiment tested layer 25, Token-Before-Generation (TBG) position, and logistic regression architecture without systematic ablation across alternative configurations.

This work makes the following contributions:

1. Documentation of SE probe failure under a specific configuration (layer 25, TBG position, logistic regression, Llama-3-8B-Instruct, TruthfulQA), demonstrating that this configuration does not yield meaningful SE prediction.

2. Identification of a replication gap between the experimental results and published benchmarks, suggesting that configuration details may significantly affect SE probe performance.

3. A negative result that may inform future work on SE probing by highlighting the need for systematic configuration validation.

## 2. Related Work

### 2.1 Semantic Entropy

Farquhar et al. (2024) introduced semantic entropy as an uncertainty measure that accounts for semantic equivalence among generated responses. SE clusters responses using bidirectional natural language inference and computes entropy over cluster proportions. The method achieves AUROC 0.76-0.97 for hallucination detection across TruthfulQA, TriviaQA, and other benchmarks.

SE computation requires generating N=10-20 responses per query with temperature sampling, embedding each response, and performing O(N²) pairwise entailment checks using a DeBERTa-v3 NLI model (He et al., 2021). This computational overhead limits deployment in latency-sensitive applications.

### 2.2 Semantic Entropy Probes

Kossen et al. (2024) proposed Semantic Entropy Probes (SEPs) as lightweight classifiers trained on LLM hidden states to predict SE labels. SEPs extract hidden states from specific layers and token positions, then train logistic regression probes to map these representations to SE predictions. Published results report that SEPs achieve AUROC within 2-3% of full SE on TruthfulQA while requiring only a single forward pass.

The SEP approach assumes that SE-relevant information is encoded in hidden states at particular layers and positions. The present work tested this assumption under one specific configuration.

### 2.3 Related Uncertainty Estimation Approaches

Kernel Language Entropy (KLE) constructs positive semidefinite kernels over response sets for uncertainty quantification (Nikitin et al., 2024). KLE demonstrates that similarity structure contains uncertainty-relevant information, which motivated the similarity augmentation approach tested in this work.

First-token entropy uses the entropy of the initial token distribution as an uncertainty proxy. Prior experiments in this research pipeline found rho = 0.13 correlation between first-token entropy and true SE, indicating limited effectiveness of token-level metrics for capturing semantic uncertainty.

## 3. Method

### 3.1 Overview

SE-Distilled Probes (SEDP) extend SEPs by incorporating semantic similarity features as auxiliary inputs during training. The approach combines two information sources: hidden state representations from the LLM and summary statistics computed from pairwise similarities among generated responses.

The training pipeline consists of:
1. Response generation: N=20 responses per question using temperature sampling
2. SE label computation: Clustering responses via NLI entailment and computing semantic entropy
3. Feature extraction: Hidden states from layer 25 at TBG position, plus similarity statistics
4. Probe training: Logistic regression on concatenated features

### 3.2 Semantic Entropy Labels

SE labels were computed following Farquhar et al. (2024). For each question, N=20 responses were generated using temperature T=0.7. Responses were clustered by semantic equivalence using DeBERTa-v3-large-MNLI, where two responses were considered equivalent if bidirectional entailment probability exceeded 0.5.

Given clusters C_1, ..., C_k with sizes n_1, ..., n_k, semantic entropy was computed as:

H_SE = -sum(p_i * log(p_i))

where p_i = n_i / N. SE labels were binarized using the median threshold for probe training.

### 3.3 Hidden State Extraction

Hidden states were extracted from layer 25 of Llama-3-8B-Instruct (32 layers total) at the Token-Before-Generation (TBG) position—the last token of the prompt before generation begins. This configuration was selected based on published guidance that middle-to-late layers contain SE-relevant information.

### 3.4 Similarity Feature Extraction

For each question's response set:
1. All N=20 responses were embedded using sentence-transformers (all-MiniLM-L6-v2)
2. Pairwise cosine similarity matrix S was computed
3. Summary statistics were extracted from the upper triangle: [mean, std, min, max]

This produced a 4-dimensional similarity feature vector per question.

### 3.5 Probe Architecture

The baseline SEP used logistic regression on hidden states (4096 dimensions):

y_hat = sigmoid(W_h * h + b)

SEDP extended this by concatenating similarity features:

y_hat = sigmoid(W * [h; s] + b)

where s is the 4-dimensional similarity vector, yielding 4100 input dimensions. Both probes used sklearn's LogisticRegression with L2 regularization (C=1.0) and LBFGS optimizer.

### 3.6 Training Protocol

The experiment used TruthfulQA (Lin et al., 2022) with an 80/20 train/test split (approximately 653/164 questions) and fixed random seed 42. No hyperparameter search was performed; the experiment was designed as an existence proof to determine whether the approach produces meaningful SE correlation.

### 3.7 Evaluation Metrics

Two metrics were used:

- Spearman correlation (rho): Rank correlation between predicted SE probabilities and true continuous SE values. The threshold for the existence proof was rho >= 0.3.

- AUROC: Binary classification performance for detecting high-uncertainty questions. Random baseline is 0.50.

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1 (Existence Proof):** Does SEDP achieve Spearman rho >= 0.3 with true semantic entropy?

**RQ2 (Similarity Benefit):** Does SEDP (hidden + similarity) outperform SEP (hidden only)?

### 4.2 Dataset

TruthfulQA contains 817 questions designed to elicit false beliefs from language models, spanning 38 categories including health, law, finance, and politics (Lin et al., 2022).

| Property | Value |
|----------|-------|
| Total questions | 817 |
| Train split | 653 (80%) |
| Test split | 164 (20%) |
| Split method | Random, seed=42 |

### 4.3 Model Configuration

**Language Model:** Llama-3-8B-Instruct (meta-llama/Meta-Llama-3-8B-Instruct)
- Architecture: Decoder-only transformer, 32 layers
- Hidden dimension: 4096
- Precision: float16

**Generation Settings:**
- Responses per question: N = 20
- Temperature: T = 0.7
- Max new tokens: 100

**Hidden State Extraction:**
- Layer: 25 of 32
- Token position: TBG (Token Before Generation)

**Entailment Model:** DeBERTa-v3-large-MNLI
- Entailment threshold: 0.5 (bidirectional)

**Similarity Embedding:** all-MiniLM-L6-v2

### 4.4 Baselines

**SEP (Semantic Entropy Probe):** Logistic regression on hidden states only (4096 features).

**Random Baseline:** AUROC = 0.50, Spearman rho = 0.0.

### 4.5 Implementation

- Probe: sklearn LogisticRegression, C=1.0, LBFGS optimizer, max_iter=1000
- Hardware: Single NVIDIA A100 (40GB)
- Response generation: approximately 2-4 hours
- SE label computation: approximately 1 hour
- Probe training: under 1 minute

## 5. Results

### 5.1 Main Results

Table 1 presents results on the TruthfulQA test set.

**Table 1: Results on TruthfulQA Test Set**

| Method | Spearman rho | p-value | AUROC |
|--------|------------|---------|-------|
| SEP (baseline) | 0.0835 | 0.288 | 0.5214 |
| SEDP (proposed) | 0.0843 | 0.283 | 0.5219 |
| Delta (SEDP - SEP) | +0.0009 | — | +0.0004 |
| Threshold (existence proof) | >= 0.30 | < 0.05 | — |
| Random baseline | 0.00 | — | 0.50 |

The existence proof threshold was not met. SEDP achieved rho = 0.0843, falling short of the 0.3 threshold by 72%. The p-value of 0.283 indicates that the correlation is not statistically significant; the null hypothesis that the true correlation is zero cannot be rejected.

Both methods achieved AUROC approximately 0.52, marginally above the random baseline of 0.50. For practical hallucination detection, this performance provides no useful signal.

SEDP marginally outperformed SEP (+0.0009 rho, +0.0004 AUROC). While the effect direction is consistent with the hypothesis that similarity features provide additional information, the magnitude is negligible.

### 5.2 Comparison with Published Results

**Table 2: Comparison with Published Benchmarks**

| Source | AUROC on TruthfulQA |
|--------|---------------------|
| Kossen et al. (2024) | ~0.85 |
| This work (SEP baseline) | 0.52 |
| Gap | 39% |

The 39% gap between the achieved AUROC and published results is substantial. The experiment followed published guidance: layer 25 falls within the recommended middle-to-late range, TBG is a standard token position, and logistic regression matches the published probe architecture.

Possible explanations for this gap include:

1. **Layer selection:** Layer 25 may not be optimal for Llama-3-8B-Instruct; systematic ablation across layers 20-31 was not performed.

2. **Token position:** Alternative positions (SLT, pooling) may capture different information.

3. **Implementation differences:** Subtle variations in response generation, SE computation, or preprocessing may contribute to the gap.

4. **Model-specific factors:** Published results may use different model versions or configurations.

### 5.3 Effect of Similarity Augmentation

Despite the overall failure, the effect direction was examined:

| Metric | SEP | SEDP | Delta |
|--------|-----|------|-------|
| Spearman rho | 0.0835 | 0.0843 | +0.0009 |
| AUROC | 0.5214 | 0.5219 | +0.0004 |

The positive delta is consistent with the hypothesis that similarity features contribute information. However, the magnitude is less than 1% relative improvement, providing no practical benefit. When the base signal is absent, auxiliary features cannot compensate.

### 5.4 Visualization

Figure 1 presents the Spearman correlation for both methods with the existence proof threshold.

![Gate Metrics](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question_opus45/docs/youra_research/20260325_question/h-e1/figures/gate_metrics.png)

*Figure 1: Spearman correlation (rho) for SEP and SEDP. The horizontal dashed line indicates the existence proof threshold (rho = 0.3). Both methods achieved rho approximately 0.08, far below the threshold.*

Figure 2 shows the scatter plot of predicted versus true SE values.

![Scatter Plot](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question_opus45/docs/youra_research/20260325_question/h-e1/figures/scatter.png)

*Figure 2: Predicted SE probability versus true semantic entropy for both methods. No discernible correlation is visible.*

Figure 3 presents ROC curves for both methods.

![ROC Curves](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question_opus45/docs/youra_research/20260325_question/h-e1/figures/roc_curves.png)

*Figure 3: ROC curves for SEP and SEDP. Both curves lie close to the diagonal, indicating near-random classification performance (AUROC approximately 0.52).*

## 6. Discussion

### 6.1 Interpretation

The results indicate that hidden states at layer 25 of Llama-3-8B-Instruct, extracted at the TBG position, do not encode semantic entropy information accessible to logistic regression probes under the tested configuration.

Three competing explanations for this failure are:

**Layer localization:** SE-relevant information may be concentrated in layers other than layer 25. Published work reports optimal configurations without characterizing failure modes of suboptimal choices.

**Token position sensitivity:** The TBG position captures the model state before generation. SE information may emerge during generation and be better captured at alternative positions.

**Implementation factors:** Accumulated differences in response generation, SE computation, or preprocessing relative to published implementations may contribute to the performance gap.

The experiment cannot distinguish among these explanations.

### 6.2 Similarity Augmentation

The hypothesis that similarity features would improve SE prediction was directionally supported (positive delta) but the effect was negligible. Contributing factors may include:

1. **Feature dimensionality imbalance:** 4 similarity features relative to 4096 hidden state dimensions limits the influence of similarity information.

2. **Absence of base signal:** When hidden states contain no extractable SE information, auxiliary features cannot compensate.

3. **Linear probe limitations:** Logistic regression may not capture complex interactions between hidden states and similarity features.

### 6.3 Limitations

This work has several limitations that constrain the conclusions:

**Single layer tested:** Only layer 25 of 32 was evaluated. SE information may exist at other layers.

**Single token position:** Only TBG was tested. Alternative positions (SLT, pooled representations) were not explored.

**Single dataset:** TruthfulQA is adversarial by design; results may not generalize to other benchmarks.

**Linear probe architecture:** Logistic regression may be insufficient; MLP probes may capture patterns missed by linear models.

**SE label quality not validated:** DeBERTa NLI clustering was assumed to produce valid SE labels without explicit quality verification.

**Single random seed:** No variance estimation across multiple seeds.

These limitations are acknowledged as acceptable for an existence proof: the experiment tested whether a reasonable configuration works, and it did not. Systematic exploration remains for future work.

### 6.4 Implications

For practitioners considering SE probe deployment:

1. Published configurations may not transfer across implementations or model versions.
2. Systematic validation across layers, token positions, and probe architectures may be necessary.
3. AUROC close to 0.50 on held-out data should trigger configuration review before deployment.

### 6.5 Future Directions

The negative result suggests several directions for investigation:

1. **Layer ablation:** Test layers 20-31 to locate where, if anywhere, SE information resides in Llama-3-8B-Instruct.

2. **Token position comparison:** Compare TBG, SLT, and pooled representations.

3. **Nonlinear probes:** Test MLP architectures with hidden layers.

4. **SE label validation:** Inspect semantic clustering quality before probe training.

5. **Multi-dataset evaluation:** Validate on TriviaQA and SQuAD to assess generalization.

## 7. Conclusion

This work attempted to develop efficient semantic entropy proxies via similarity-augmented hidden state probes. The experiment produced negative results: the tested configuration (layer 25, TBG position, logistic regression, Llama-3-8B-Instruct) achieved Spearman correlation rho = 0.0843 with true SE, statistically indistinguishable from zero, and AUROC = 0.52, indistinguishable from random classification.

The 39% AUROC gap between these results and published benchmarks indicates substantial configuration sensitivity. The experiment tested one configuration without systematic ablation; the negative result applies to this specific setup rather than to SE probing in general.

The contributions of this work are:

1. Documentation of SE probe failure under a specific configuration, demonstrating that this configuration does not yield meaningful SE prediction on TruthfulQA.

2. Identification of a replication gap that highlights potential configuration sensitivity in SE probing.

3. A negative result that may inform future work by emphasizing the need for systematic configuration validation.

The failure of this configuration does not preclude success under alternative configurations. Systematic layer ablation, token position comparison, and probe architecture exploration remain as future work that may identify configurations where SE probing succeeds.

## References

Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. *Nature*. https://doi.org/10.1038/s41586-024-07421-0

He, P., Liu, X., Gao, J., & Chen, W. (2021). DeBERTa: Decoding-enhanced BERT with Disentangled Attention. In *Proceedings of ICLR*.

Kossen, J., Han, J., Razzak, M., Schut, L., Malik, S. A., & Gal, Y. (2024). Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs. *arXiv preprint arXiv:2406.15927*.

Lin, S. C., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. In *Proceedings of ACL*.

Nikitin, A., Kossen, J., Gal, Y., & Marttinen, P. (2024). Kernel Language Entropy: Fine-grained Uncertainty Quantification for LLMs from Semantic Similarities. In *Advances in NeurIPS*.

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. In *Proceedings of EMNLP*.

Touvron, H., et al. (2023). LLaMA: Open and Efficient Foundation Language Models. *arXiv preprint arXiv:2302.13971*.
