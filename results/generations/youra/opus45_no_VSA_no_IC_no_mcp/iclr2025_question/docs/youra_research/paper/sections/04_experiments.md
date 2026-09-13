# Experimental Setup

We design experiments to answer the following research questions:

**RQ1:** Do token entropy and N-sample consistency individually predict factual correctness? (Validates that each signal carries useful information.)

**RQ2:** Are entropy and consistency signals orthogonal? (Tests whether combining them could provide complementary value.)

**RQ3:** Do discordant cases—where methods disagree—show differential predictive value? (Validates practical complementarity.)

## Dataset

**TruthfulQA (Generation Split):** A benchmark designed to evaluate truthfulness in language model responses (Lin et al., 2022).

| Property | Value |
|----------|-------|
| Questions | 817 |
| Format | Open-ended generation |
| Labels | Binary (correct/incorrect via BERTScore) |
| Design | Adversarial (questions crafted to elicit falsehoods) |

**Why TruthfulQA:** It provides ground-truth factuality labels for closed-book QA, exactly what our hypothesis requires. The adversarial design ensures non-trivial hallucination rates, enabling meaningful comparison of detection methods. Unlike WikiBio (used for SelfCheckGPT) or NLG tasks (used for semantic entropy), TruthfulQA directly measures factual correctness.

## Model

**LLaMA-2-7B:** A publicly available decoder-only LLM (Meta, 2023).

| Property | Value |
|----------|-------|
| Parameters | 7 billion |
| Architecture | Decoder-only transformer |
| Precision | float16 |
| Access | Open weights with logit access |

**Why LLaMA-2-7B:** It provides full logit access for entropy computation (unlike API-only models). The 7B scale is representative of deployable models while being computationally tractable for our experimental setup.

## Baselines and Conditions

We compare three uncertainty quantification conditions:

| Condition | Description | Signal Type |
|-----------|-------------|-------------|
| **Token Entropy** | Mean entropy over generated tokens | Epistemic uncertainty |
| **N-Sample Consistency** | Mean pairwise cosine similarity of N=5 responses | Generation stability |
| **Random Baseline** | Uniform random scores | Chance-level reference |

We do not include a hybrid detector in this study—our goal is first to establish whether orthogonality and complementarity exist, which justifies future hybrid development.

## Implementation Details

**Token Entropy:**
- Greedy decoding with `output_scores=True`
- Maximum response length: 100 tokens
- Entropy: $H = -\sum p \log p$ per token, mean aggregation
- Numerical stability: `clamp(min=1e-10)`

**N-Sample Consistency:**
- Temperature: 1.0 (maximizes sampling diversity)
- N = 5 independent samples per question
- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- Similarity: Pairwise cosine, mean aggregation

**Ground Truth Labeling:**
- BERTScore F1 ≥ 0.5 with reference answer → Correct
- BERTScore F1 < 0.5 → Incorrect

**Compute Resources:**
- 5× NVIDIA H100 NVL (95GB each)
- Python 3.10, PyTorch 2.6.0+cu124
- Approximate runtime: 30s/question (~7 hours total)

## Evaluation Metrics

**Primary Metric: AUROC**
- Area under the receiver operating characteristic curve
- Measures ranking quality for hallucination detection
- Higher is better; random baseline = 0.5

**Effect Size: Cohen's d**
- Standardized mean difference between correct and incorrect groups
- Threshold: d > 0.2 indicates meaningful effect
- Used to assess mechanism strength (H-M1, H-M2)

**Orthogonality: Pearson Correlation**
- Correlation between entropy and (1-consistency) scores
- Threshold: r < 0.3 indicates orthogonal signals (< 9% shared variance)

**Complementarity Analysis:**
- Discordant proportion: Fraction of questions where entropy and consistency ranks differ by >50 percentile points
- Subset AUROC: AUROC for each method on its "winning" discordant subset
- Thresholds: >15% discordant, winning-method AUROC >0.6

**Statistical Significance:**
- Mann-Whitney U test (one-sided) for group comparisons
- Bootstrap confidence intervals (1000 iterations)
- Significance level: p < 0.05

## Hypotheses Tested

| ID | Hypothesis | Gate | Success Criterion |
|----|------------|------|-------------------|
| H-M1 | Entropy correlates with incorrectness | MUST_WORK | Cohen's d > 0.2, direction: incorrect > correct |
| H-M2 | Consistency correlates with correctness | MUST_WORK | Cohen's d > 0.2, direction: correct > incorrect |
| H-M3 | Signals are orthogonal with complementary value | MUST_WORK | r < 0.3, discordant > 15%, subset AUROC > 0.6 |
