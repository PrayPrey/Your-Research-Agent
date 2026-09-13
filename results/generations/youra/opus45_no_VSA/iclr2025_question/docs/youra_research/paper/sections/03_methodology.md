# 3. Methodology

## 3.1 Trajectory Metrics

We extract probability distributions at each layer using the logit lens technique \citep{nostalgebraist2020logitlens}: hidden states are projected through the final unembedding matrix to obtain per-layer token probabilities.

**Normalized Trajectory Instability (NTI)** measures entropy variance across layers, normalized by mean entropy:

$$\text{NTI} = \frac{\sigma(\{H_l\}_{l=24}^{31})}{\mu(\{H_l\}_{l=24}^{31}) + \epsilon}$$

where $H_l = -\sum_v p_l(v) \log p_l(v)$ is the Shannon entropy at layer $l$, and $\epsilon = 10^{-8}$ prevents division by zero.

**Convergence Monotonicity Index (CMI)** captures whether the model converges smoothly toward its final answer:

$$\text{CMI} = \frac{1}{L-1} \sum_{l=24}^{30} \mathbb{1}[s_{l+1} > s_l - \delta]$$

where $s_l$ measures similarity between layer-$l$ top prediction and the final answer, and $\delta = 0.01$ is a tolerance threshold.

**Representational Competition Index (RCI)** is a binary indicator of whether the top-predicted token changes between consecutive layers. We compute flip rate as the proportion of layer pairs showing a top-token change.

## 3.2 Model and Dataset

- **Model**: LLaMA-2-7B (meta-llama/Llama-2-7b-hf) with 32 transformer layers
- **Layers analyzed**: 24-31 (late layers where semantic content crystallizes)
- **Dataset**: TruthfulQA MC1 \citep{lin2021truthfulqa}, 817 questions with 4114 prompt-choice pairs
- **Labels**: Binary (correct/incorrect response selection)
- **Decoding**: Greedy (temperature = 0) for deterministic evaluation

## 3.3 Evaluation Protocol

- **Cross-validation**: 5-fold stratified CV with question-level splits (no question appears in both train and test)
- **Classifier**: Logistic regression with L2 regularization ($C = 1.0$)
- **Primary metric**: AUROC (area under ROC curve)
- **Statistical tests**: Likelihood ratio test for nested model comparison; DeLong test for AUROC differences

## 3.4 Sub-Hypotheses

| ID | Hypothesis | Success Criterion | Gate |
|----|------------|-------------------|------|
| h-e1 | NTI AUROC > 0.55 | Mean > 0.55, all folds > 0.52 | MUST_WORK |
| h-m1 | Combined gain ≥ 0.03 | LRT $p < 0.05$ | SHOULD_WORK |
| h-m2 | Low-entropy AUROC > 0.55 | CI lower bound > 0.50 | SHOULD_WORK |
| h-m3 | RCI flip separation ≥ 20pp | ≥30% halluc, <10% correct | SHOULD_WORK |
