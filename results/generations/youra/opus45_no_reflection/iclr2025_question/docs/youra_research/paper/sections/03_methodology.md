# Methodology

We present a simple approach: extract hidden states from transformer middle layers during answer generation, then train a linear probe to predict factual correctness. Each design choice follows from our core insight that middle-layer representations encode knowledge confidence distinct from output-level confidence.

## Problem Setup

Given a question $q$ and model-generated answer $a$, we seek a function $f: (q, a) \rightarrow [0, 1]$ predicting correctness probability. Ground-truth labels $y \in \{0, 1\}$ come from exact-match evaluation against reference answers.

## Hidden State Extraction

**Model.** We use Llama-3-8B-Instruct (32 layers, 4096 hidden dimensions) as a representative modern instruction-tuned LLM with accessible hidden states.

**Forward pass with hooks.** During generation, we register PyTorch forward hooks on transformer layer outputs. For a target layer $\ell$, we capture the hidden state $h_\ell \in \mathbb{R}^{T \times d}$ where $T$ is sequence length and $d = 4096$ is hidden dimension. Hooks extract states without modifying the forward pass—we verify 100% output identity and <5% runtime overhead (H-M1 validation: -3.4% overhead observed).

**Aggregation.** We extract the hidden state at the last generated token position, $h_\ell^{\text{last}} \in \mathbb{R}^d$. This position aggregates context from the full question-answer sequence through causal attention.

**Layer selection.** We target middle layers (50–60% depth). For Llama-3-8B's 32 layers, this corresponds to layers 15–19. We empirically validate this choice through systematic layer sweep (Section 4).

## Probe Architecture

**Linear probe.** We train a logistic regression classifier:
$$P(\text{correct} | h_\ell^{\text{last}}) = \sigma(w^\top h_\ell^{\text{last}} + b)$$
where $w \in \mathbb{R}^d$, $b \in \mathbb{R}$, and $\sigma$ is the sigmoid function.

**Why linear?** Three reasons justify this choice:
1. *Interpretability*: Linear probes reveal which hidden dimensions encode correctness.
2. *Literature precedent*: Kossen et al. (2024) find MLP probes add <1 percentage point over linear.
3. *Generalization*: Simpler probes are less prone to overfitting to training distribution artifacts.

**Training details.** We use sklearn's LogisticRegression with L2 regularization ($C = 10^{-3}$), balanced class weights, and LBFGS solver. Training converges in ~60 iterations on 9,500 samples.

## Baseline Methods

We compare against output-level uncertainty metrics computed from the same generation:

**Token entropy.** Average entropy of next-token distributions during generation:
$$H_{\text{token}} = -\frac{1}{T}\sum_{t=1}^{T} \sum_v P(v_t) \log P(v_t)$$

**Sequence NLL.** Negative log-likelihood of the generated sequence:
$$\text{NLL} = -\sum_{t=1}^{T} \log P(a_t | a_{<t}, q)$$

Both baselines measure output-level confidence. High entropy or NLL indicates model uncertainty, which correlates negatively with correctness.

## Evaluation Protocol

**Datasets.** Training on TriviaQA (9,500 train / 1,700 validation), which provides large-scale factual QA with exact-match ground truth.

**Metrics.** Primary: AUROC (area under ROC curve) for binary correct/incorrect classification. AUROC measures discriminative ability independent of threshold selection.

**Layer sweep.** We evaluate probes at 8 layer depths (layers 3, 7, 11, 15, 18, 23, 27, 31) to characterize the layer-AUROC relationship and validate the inverted-U hypothesis.
