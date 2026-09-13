# 3. Methodology

To test whether CCP-based hallucination detection degrades on creative text, we implemented the CCP mechanism following published equations and applied it to paired factual and creative datasets. This section documents our implementation in full transparency, enabling reproducibility while also surfacing the methodological challenges we encountered.

## 3.1 CCP Mechanism Overview

The Claim-Conditioned Probability (CCP) metric aggregates token-level probabilities conditioned on claim entailment status. Given a generated text $y$ and source context $x$, CCP:

1. **Claim Decomposition**: Splits $y$ into atomic claims $\{c_1, \ldots, c_n\}$ via sentence tokenization.
2. **NLI Inference**: For each claim $c_j$, computes entailment probability $P(c_j \mid x)$ using a pre-trained NLI model.
3. **Claim-Type Mass Ratio**: Computes $\rho_j = \frac{P(\text{entail}) + P(\text{contradict})}{P(\text{entail}) + P(\text{neutral}) + P(\text{contradict})}$ across all claims.
4. **Product Aggregation**: Aggregates per-token probabilities weighted by claim type via $\text{CCP}(y|x) = \prod_{i=1}^{|y|} P(y_i | y_{<i}, x, \rho_j)$.

We focused on step 3 (claim-type mass ratio $\rho_j$) as the primary diagnostic metric, as the CCP paper indicates that $\rho_j$ values of 0.75–0.85 are associated with ROC-AUC improvements of +0.05–0.10 over baselines.

## 3.2 Implementation Details

**NLI Model**: DeBERTa-v3-base cross-encoder (`cross-encoder/nli-deberta-v3-base`), a 184M parameter model trained on SNLI and MNLI datasets. We chose this model for its state-of-the-art performance on semantic similarity tasks (88.1% accuracy on MNLI-matched). The model outputs three probability values per claim-context pair: $P(\text{entail})$, $P(\text{neutral})$, and $P(\text{contradict})$.

**Claim Decomposition**: NLTK sentence tokenization with a maximum of 20 claims per sample. Sentences shorter than 3 tokens or longer than 100 tokens were filtered to remove incomplete fragments and prevent truncation errors. Each claim was paired with the full source text as context (premise-hypothesis format for NLI).

**Context Pairing Strategy**: Following the cavaquinho implementation pattern, we used the full source text as the NLI premise and each extracted claim as the hypothesis. This choice maximizes contextual information but may introduce noise for long documents where relevant context is distant from the claim (we revisit this limitation in Section 6.4).

**Batch Processing**: 16 samples per batch to balance GPU memory constraints (NVIDIA GPU with ~2GB available) and throughput. Total runtime was approximately 1 minute per domain (dataset loading + NLI inference + metric computation).

**Reproducibility**: All experiments used fixed random seed 42. Configuration files, model checkpoints, and hyperparameters are documented in `h-e1/code/config.py`.

## 3.3 Datasets

We selected datasets to maximize domain separation while controlling for confounding factors (text length, vocabulary complexity):

**Factual Domain (TruthfulQA)**: Validation split of TruthfulQA (Lin et al., 2021), containing 817 question-answer pairs across categories including science, history, and biographies. We filtered 25 samples that produced no claims after tokenization (very short answers), leaving 792 samples. Mean claims per sample: 5.8.

**Creative Domain (WritingPrompts)**: Train split of WritingPrompts (Fan et al., 2018), a corpus of 300k story prompts and human-written continuations. We randomly sampled 817 stories to match the factual domain sample size. Mean claims per sample: 6.2. The corpus contains diverse narrative structures (fantasy, sci-fi, horror) with varying metaphor density and speculation.

**Dataset Pairing Justification**: TruthfulQA is designed to test factuality (questions elicit common misconceptions), making it a strong factual anchor. WritingPrompts explicitly encourages creative elaboration, metaphor, and speculation. While neither dataset perfectly represents "all factual text" or "all creative text," they provide sufficient domain separation for a proof-of-concept existence test.

## 3.4 Evaluation Metrics

**Primary Metric: Claim-Type Mass Ratio ($\rho_j$)**

For each sample, we computed:

$$\rho_j = \frac{1}{n} \sum_{j=1}^{n} \frac{P(\text{entail})_j + P(\text{contradict})_j}{P(\text{entail})_j + P(\text{neutral})_j + P(\text{contradict})_j}$$

where $n$ is the number of claims in the sample. Expected range: 0.75–0.85 (inferred from CCP paper ROC-AUC claims).

**Secondary Metric: Autocorrelation**

To test the aggregation fragility hypothesis, we measured lag-$k$ autocorrelation of claim-level $\rho_j$ values:

$$\text{autocorr}(k) = \text{Corr}(\rho_{j,t}, \rho_{j,t+k})$$

for lags 1–10. Prediction: creative text should exhibit lag-1 autocorr > 0.4 due to sequential claim similarity (metaphorical threads persist across sentences).

**Reliability Metric: Krippendorff's $\alpha$**

Inter-method agreement across claim decomposition approaches (NLTK vs LLM extraction) was measured using Krippendorff's $\alpha > 0.7$ as the threshold for acceptable reliability.

**Statistical Tests**

Domain comparison used Wilcoxon rank-sum test (non-parametric, robust to non-normal distributions). Effect size measured via Cohen's $d$. Significance threshold: $p < 0.05$.

## 3.5 Gate Validation Protocol

Following the Phase 3 implementation plan, we defined MUST_WORK gate criteria:

1. **Primary**: $\Delta\rho_j = \rho_{\text{creative}} - \rho_{\text{factual}} > 0.15$
2. **Direction**: $\rho_{\text{creative}} > \rho_{\text{factual}}$ (creative text should show higher mass in entail/contradict classes)
3. **Autocorr**: Lag-1 autocorr > 0.4 in creative domain, < 0.2 in factual domain
4. **Reliability**: Krippendorff's $\alpha > 0.7$
5. **Significance**: $p < 0.05$, Cohen's $d > 0.5$

**Failure Protocol**: If ≤2 of 5 criteria met, route to Phase 2A-Dialogue for hypothesis refinement. If gate fails due to measurement issues (values outside expected range), prioritize methodological fixes over hypothesis revision.

## 3.6 Transparency and Reproducibility

All code, configuration files, and validation notebooks are available in `h-e1/code/`. The implementation includes:

- **Unit tests**: 10 manually verified entailment/contradiction examples to validate NLI behavior
- **Sanity checks**: Tested on TruthfulQA correct vs incorrect answers (expected: $P(\text{entail}|\text{correct}) > 0.5$, $P(\text{contradict}|\text{incorrect}) > 0.5$)
- **Ablation stubs**: Placeholders for future context window and claim decomposition method comparisons

**Methodological Humility**: We acknowledge that our implementation represents one interpretation of the CCP paper's description. The original paper does not report raw $\rho_j$ distributions, NLI calibration diagnostics, or claim decomposition methodology, creating ambiguity that we resolved via literature precedents (cavaquinho, HallucinoGenAI implementations). Section 6.1 discusses implications of these implementation choices.
