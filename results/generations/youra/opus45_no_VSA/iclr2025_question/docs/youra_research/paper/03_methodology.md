# 3. Methodology

## 3.1 Problem Formulation

Given a question-answer pair (q, a) and a decoder-only LLM with L layers, we extract per-layer probability distributions p_l over the vocabulary V using the logit lens. Our goal is to compute single-pass features that discriminate correct from incorrect responses.

Let H_l = -Σ_v p_l(v) log p_l(v) denote the entropy at layer l. We focus on late layers (24-31 for LLaMA-2-7B) where logit lens provides reliable distributions.

## 3.2 Trajectory Metrics

### Normalized Trajectory Instability (NTI)

NTI measures the variability of entropy across layers relative to its mean:

$$\text{NTI} = \frac{\sigma(\{H_l\}_{l=24}^{31})}{\mu(\{H_l\}_{l=24}^{31}) + \epsilon}$$

where σ and μ denote standard deviation and mean, and ε = 1e-8 prevents division by zero.

**Intuition**: Factual retrieval converges smoothly, producing low entropy variance. Fabrication involves cross-layer reorientation, producing high variance.

### Convergence Monotonicity Index (CMI)

CMI captures whether the answer probability increases monotonically across layers. Let s_l denote the probability assigned to the chosen answer token at layer l. Then:

$$\text{CMI} = \frac{1}{L-1} \sum_{l=24}^{30} \mathbb{1}[s_{l+1} > s_l - \delta]$$

where δ = 0.002 provides tolerance for numerical noise.

**Intuition**: Factual retrieval should show monotonic convergence (CMI → 1); fabrication may show non-monotonic oscillation.

### Representational Competition Index (RCI)

RCI measures whether the top-1 token changes between consecutive layers:

$$\text{RCI}_l = \mathbb{1}[\arg\max p_l \neq \arg\max p_{l-1}]$$

We aggregate into a "flip pattern" indicator: whether the top token changes at least once in layers 24-31.

**Intuition**: We hypothesized that hallucinations show more flip patterns (competition between alternatives). This was falsified---flip patterns are near-universal.

## 3.3 Model and Dataset

**Model**: LLaMA-2-7B (meta-llama/Llama-2-7b-hf), a 32-layer decoder-only transformer with hidden dimension 4096.

**Dataset**: TruthfulQA MC1 (Lin et al., 2021), comprising 817 questions with binary correctness labels. Each question has multiple candidate answers; we construct prompt-choice pairs and evaluate per-choice predictions.

**Evaluation Protocol**:
- 5-fold stratified cross-validation with question-level splits
- Logistic regression classifier (C=1.0, max_iter=1000)
- Primary metric: AUROC
- Statistical test: Likelihood Ratio Test for nested models

## 3.4 Sub-Hypotheses

We decompose the main hypothesis into testable sub-hypotheses with pre-registered success criteria:

| ID | Hypothesis | Success Criterion | Gate |
|----|------------|-------------------|------|
| h-e1 | NTI AUROC > 0.55 | Mean > 0.55, all folds > 0.52 | MUST_WORK |
| h-m1 | [H_L+NTI+CMI] improves over H_L | Gain ≥ 0.03, LRT p < 0.05 | SHOULD_WORK |
| h-m2 | Trajectory metrics work on low-entropy subset | AUROC > 0.55, CI LB > 0.50 | SHOULD_WORK |
| h-m3 | RCI flip in ≥30% halluc, <10% correct | Separation ≥ 20pp | SHOULD_WORK |

Gate types determine workflow: MUST_WORK failure stops the pipeline; SHOULD_WORK failure is recorded as a limitation.
