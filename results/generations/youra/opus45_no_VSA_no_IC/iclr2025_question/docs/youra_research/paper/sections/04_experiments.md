# Experimental Setup

We design experiments to test whether uncertainty probes generalize across LLM families. Specifically, we address three research questions:

**RQ1:** Does a probe trained on one model family detect hallucinations when applied to another family's hidden states?

**RQ2:** Does affine alignment enable transfer between models with different hidden dimensions?

**RQ3:** What is the maximum transfer gap across all family pairs, and does it stay below the 0.10 threshold?

## Dataset

**TruthfulQA** [Lin et al., 2022]. We evaluate on the generation subset containing 817 questions designed to elicit plausible but incorrect answers from language models. The benchmark covers 38 categories including health, law, finance, and politics. Ground truth correctness labels enable direct AUROC computation for hallucination detection.

We split the dataset 80/20 into training (653 questions) and validation (164 questions) using a fixed seed (42). The training split is used to compute semantic entropy labels and train probes; the validation split is held out for all transfer evaluations.

| Split | Questions | Usage |
|-------|-----------|-------|
| Train | 653 | SE label computation, probe training, aligner fitting |
| Validation | 164 | Transfer evaluation (all reported metrics) |

**Rationale.** TruthfulQA is the standard benchmark for hallucination detection used in both the original semantic entropy [Farquhar et al., 2024] and SEP [Kossen et al., 2024] papers. Using the same benchmark enables direct comparison with prior work.

## Models

We test three instruction-tuned LLMs from different organizations:

| Model | Provider | Parameters | Hidden Dim | Layers |
|-------|----------|------------|------------|--------|
| Llama-3-8B-Instruct | Meta | 8B | 4096 | 32 |
| Mistral-7B-Instruct-v0.2 | Mistral AI | 7B | 4096 | 32 |
| Qwen-2-7B-Instruct | Alibaba | 7B | 3584 | 28 |

**Rationale.** These models represent the three major open-weight LLM families with accessible hidden states. All are in the 7–8B parameter range to control for scale effects. Llama and Mistral share hidden dimensions (4096) while Qwen differs (3584), enabling both same-dimension and cross-dimension transfer tests.

## Baselines

**Multi-sample Semantic Entropy** [Farquhar et al., 2024]. The gold-standard for hallucination detection. For each question, we generate 5 responses at temperature 0.7, cluster them by semantic equivalence using DeBERTa-v3-large-mnli-fever-anli-ling-wanli NLI model, and compute entropy over cluster distributions. This provides training labels for SEPs and serves as the performance ceiling.

**Token-level Entropy.** Average entropy of next-token distributions during generation. This cheap baseline achieves AUROC ~0.55 and serves as a lower bound.

**Direct (Untransferred) Probe.** Each model's SEP evaluated on its own hidden states. This provides the baseline AUROC from which we measure transfer gaps.

## Implementation Details

**Hardware.** All experiments run on NVIDIA H100 NVL GPUs. Models are loaded in float16 precision with device_map="auto".

**Hidden State Extraction.** We extract at layer 2/3 depth: layer 21 for Llama/Mistral (32 layers), layer 18 for Qwen (28 layers). Hidden states are taken at the last token position (SLT) following Kossen et al. [2024].

**Probe Training.** Logistic regression with L2 regularization (C=1.0), LBFGS solver, max_iter=1000. Labels are binarized semantic entropy (threshold at median).

**Affine Alignment.** Least-squares fit on training hidden states. For Qwen (3584) to Llama/Mistral (4096) transfer, we learn W ∈ R^{3584×4096} and b ∈ R^{4096}.

**Caching.** Hidden states cached as NumPy arrays to enable rapid multi-probe evaluation.

## Evaluation Metrics

**AUROC.** Primary metric for hallucination detection. Measures the probability that a randomly chosen correct answer has lower predicted uncertainty than a randomly chosen incorrect answer.

**Transfer Gap.** For source model i and target model j:
$$\text{gap}_{i \to j} = \text{AUROC}_{i \to i} - \text{AUROC}_{i \to j}$$

Positive gap indicates transfer degradation. We report mean gap and max gap across all 6 off-diagonal pairs.

**Success Criteria.** Pre-registered thresholds:
- Mean gap < 0.05: Strong evidence for architecture-invariant encoding
- Max gap < 0.10: No pair shows prohibitive transfer degradation
- Max gap < 0.15: Weak evidence (fallback threshold)
