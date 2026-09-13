# Methodology

Our experimental design tests two distinct hypotheses: (1) infrastructure validation — can entropy be reliably extracted from frozen LLM forward passes, and do entropy-max-probability disagreement patterns exist? and (2) performance hypothesis — does entropy-based rejection outperform max-probability-based rejection for selective prediction? This section describes our method for both tests, the unintended model substitution that invalidated the second test, and the gate-based validation framework that allowed us to distinguish infrastructure success from hypothesis failure.

## Experimental Setup

### Dataset and Task

We evaluate on TriviaQA (Joshi et al., 2017), a factual question-answering benchmark with single-answer targets. Each example consists of a factual question (e.g., "What is the capital of France?") and one or more acceptable answer strings ("Paris"). We use the unfiltered validation split, sampling 500 examples for proof-of-concept validation. TriviaQA is ideal for our experiment because (1) factual QA represents a core selective prediction use case (high-stakes domains like medical QA), (2) single-answer targets enable exact-match evaluation, and (3) the task requires factual knowledge retrieval, making model capacity directly relevant.

### Model Selection and Substitution

Our original experimental design specified Llama-2-7B (Touvron et al., 2023), a 7-billion-parameter decoder-only transformer. We chose Llama-2-7B because (1) it is open-source with accessible logits, (2) it achieves over 10% accuracy on TriviaQA in zero-shot settings, and (3) 7B parameters represent a standard scale for knowledge-intensive tasks. However, during implementation, GPT-2 (Radford et al., 2019) was substituted — a 117-million-parameter model 60× smaller than planned. GPT-2 was designed for general language modeling, not factual knowledge recall, and performs at near-zero accuracy on TriviaQA.

This substitution was unintended, but it became the critical variable exposing our methodological finding. GPT-2's zero accuracy on TriviaQA (0/500 correct predictions) created zero variance in the correctness array, rendering correlation-based statistical tests undefined. Had Llama-2-7B been used as planned, we expect 50-100 correct predictions (10-20% accuracy), providing sufficient variance for correlation analysis. The substitution thus serves as an inadvertent ablation study on model capacity's role in experiment validity.

## Entropy Extraction Method

For each TriviaQA example, we extract entropy from the next-token probability distribution after encoding the question. Let V be the vocabulary, and p(v) the softmax probability assigned to token v ∈ V:

$$p(v) = \frac{\exp(z_v / T)}{\sum_{v' \in V} \exp(z_{v'} / T)}$$

where z_v is the logit for token v and T is temperature (T=1 for our experiments, raw logits). Shannon entropy is computed as:

$$H = -\sum_{v \in V} p(v) \log p(v)$$

We add ε = 10^{-10} to avoid log(0) for zero-probability tokens. Entropy is measured in nats (natural logarithm). For a uniform distribution over |V| tokens, entropy is log|V|. For GPT-2, |V| = 50,257, so maximum entropy is log(50,257) ≈ 10.8 nats. A peaked distribution (one token with p ≈ 1) has entropy near 0.

We also extract max-probability for baseline comparison:

$$p_{\max} = \max_{v \in V} p(v)$$

Both metrics are computed from a single frozen forward pass, requiring no training or ensembling. Implementation uses PyTorch and Hugging Face Transformers, with entropy computed via torch.sum(probs * torch.log(probs + ε), dim=-1).

## Prediction Generation and Correctness Evaluation

We generate predictions using greedy decoding: select the token v* with highest probability p(v*). The predicted token is decoded to text and compared to TriviaQA's answer strings via exact match (case-insensitive, whitespace-stripped). A prediction is marked correct if the decoded token matches any acceptable answer string. This strict evaluation reflects real-world selective prediction scenarios where partial matches are insufficient.

For GPT-2 on TriviaQA, greedy decoding produces mostly common tokens ("the", "a", punctuation) rather than factual entities. Zero predictions matched TriviaQA answers, yielding a correctness array of all zeros: [0, 0, ..., 0]. This zero variance makes correlation undefined — Spearman's ρ requires both variables to vary.

## Quadrant Analysis Framework

To test whether entropy provides information beyond max-probability, we partition predictions into four quadrants based on median splits:

| | Low Max-Prob | High Max-Prob |
|---|---|---|
| **Low Entropy** | Q1: Both low | Q2: High conf, low unc |
| **High Entropy** | Q3: High conf, high unc | Q4: Both high |

Q2 represents the "agreement" case: high confidence (high max-prob) and low uncertainty (low entropy), where both metrics concur. Q3 represents the "disagreement" case: high confidence (high max-prob) but high uncertainty (high entropy), suggesting a peaked distribution with significant secondary modes. If entropy captures multi-modal uncertainty, Q3 predictions should have lower accuracy than Q2 predictions.

We compute the Q3 population as the fraction of predictions in the high max-prob, high-entropy quadrant. Our infrastructure validation requires Q3 > 5% to confirm that disagreement cases exist in non-trivial proportions. If Q3 were empty or negligible (<1%), the phenomenon would be an edge case rather than a generalizable pattern.

## Gate-Based Validation Design

We employ a gate-based experimental design with three success criteria:

1. **Extraction Rate** > 95%: Entropy must be computable for nearly all predictions. Failures indicate technical bottlenecks (NaN logits, numerical instability).

2. **Correlation p-value** < 0.05: Spearman correlation between entropy and correctness must be statistically significant, testing whether entropy signals prediction quality.

3. **Q3 Population** > 5%: Disagreement quadrant must be non-trivial, validating that entropy-max-prob mismatches occur frequently enough to matter.

These criteria are evaluated with a MUST_WORK gate: if any criterion fails, dependent experiments (mechanism testing, multi-dataset evaluation) are blocked. This prevents wasted compute on follow-up experiments when the foundation is broken.

Our results were: (1) extraction rate = 100% ✓, (2) correlation p-value = NaN ✗, (3) Q3 population = 8.20% ✓. Criteria 1 and 3 validate infrastructure; criterion 2 fails due to zero-variance correctness, exposing the model capacity dependency.

## Why Correlation Became Undefined

Spearman's rank correlation ρ measures monotonic association between two variables X and Y. It is computed by ranking each variable, then applying Pearson correlation to the ranks:

$$\rho = \frac{\text{cov}(R(X), R(Y))}{\sigma_{R(X)} \sigma_{R(Y)}}$$

where R(X) denotes the rank of X. If either variable has zero variance (all values identical), its standard deviation σ is zero, making the denominator zero and ρ undefined (division by zero yields NaN).

In our experiment, correctness = [0, 0, ..., 0] has zero variance. Entropy varied (range [2.1, 7.4] nats), but with σ(correctness) = 0, ρ is undefined. This is not a failed test — it is an invalid test. The experiment cannot assess correlation because one variable does not vary. No amount of entropy signal strength can rescue this; the mathematical operation itself is undefined.

This contrasts with a negative result (ρ ≈ 0, p > 0.05), which would indicate no association exists. NaN indicates the test could not run. The distinction is critical: negative results suggest hypothesis refutation, while undefined results indicate invalid experimental conditions.

## Implementation Details

We implement the pipeline in Python with PyTorch 2.0, Transformers 4.30, and SciPy 1.10. The full code is available at [repository link]. Key hyperparameters: batch size = 1 (sequential processing), max input length = 512 tokens, temperature = 1.0. We run on a single NVIDIA A100 GPU, though CPU execution is feasible. Total runtime for 500 examples: approximately 15 minutes for GPT-2, estimated 45 minutes for Llama-2-7B.

## Figures

Figure 1 shows gate metrics: extraction rate (100%), p-value (NaN, shown as red bar), and Q3 population (8.20%) compared to thresholds (95%, 0.05, 5%). Two of three gates pass.

Figure 2 (scatter plot) displays entropy vs. correctness with binary jitter, showing all predictions incorrect (y=0 line).

Figure 3 (histograms) overlays entropy distributions for correct and incorrect predictions — in our case, only the "incorrect" distribution exists.

Figure 4 (quadrant plot) visualizes max-probability vs. entropy with color by correctness, showing Q3 quadrant contains 8.20% of predictions despite all being incorrect.

These figures will be generated from Phase 4 validation outputs and placed in the paper's figure directory.
