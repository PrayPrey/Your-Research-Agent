# Methodology

## Connection to the Key Insight

If commission-type hallucinations are the target — fabricated entities, factual substitutions, direct contradictions of grounding context — then NLI contradiction scoring is the natural detection mechanism. The NLI task trains a model to classify whether a *hypothesis* is entailed by, contradicted by, or neutral with respect to a *premise*. A hallucinated response that fabricates a fact or substitutes a correct answer with an incorrect one will, by definition, contradict the grounding context. The NLI model's P(contradiction) score becomes a hallucination score without any task-specific fine-tuning.

The key design question is not *whether* NLI can detect hallucinations, but *how to extract the signal optimally*: which scoring framing, which aggregation granularity, and which context windowing strategy best surface the contradiction signal across diverse task formats.

## NLI Model

We use `cross-encoder/nli-deberta-v3-large` (He et al., 2021), a cross-encoder architecture trained on MNLI with 304M parameters. The model takes a concatenated (premise, hypothesis) pair and outputs a 3-class softmax over {contradiction, neutral, entailment}. Cross-encoders allow full token-level interaction between premise and hypothesis, enabling fine-grained contradiction detection that bi-encoders — which encode texts independently — cannot achieve. This is critical for detecting subtle factual substitutions where the hallucinated claim uses similar vocabulary to the truth but contradicts specific entity attributes.

The model is used *frozen* (inference-only, no gradients). This is deliberate: the goal is to characterize the detection capability encoded in the model's MNLI training, not to introduce task-specific supervision.

## Net-Contradiction Framing

The model outputs three probabilities: P(contradiction), P(neutral), P(entailment). Rather than using P(contradiction) alone, we use **net-contradiction framing**:

```
score = P(contradiction) - P(entailment)
```

This design choice follows from the insight: commission-type hallucinations should *increase* P(contradiction) *and* decrease P(entailment). Net-contradiction amplifies both signals simultaneously, providing greater discrimination than either alone. Neutral responses — grounding contexts with neither explicit support nor contradiction — are pushed toward zero, avoiding false positives from uninformative (context, response) pairs. While we did not ablate alternative framings in the current experiment, the theoretical motivation is grounded in the commission detection objective.

## Sentence-Level Aggregation

Hallucinations are often localized: a single sentence in a multi-sentence response may contain the hallucinated claim while surrounding sentences are accurate. Response-level NLI — treating the full response as a single hypothesis — dilutes this signal with accurate content. We apply **sentence-level max aggregation**:

1. Tokenize the response into individual sentences using standard sentence boundary detection
2. Compute the net-contradiction score for each (context, sentence) pair independently
3. Take the **maximum** score across all sentences as the response-level hallucination score

Max aggregation follows the multiple-instance learning intuition: a response is hallucinated if *any* of its sentences is contradicted by the grounding context [Laban et al., 2022]. This prevents correct sentences from masking hallucinated ones.

## Task-Specific Context Configuration

The three HaluEval task types have fundamentally different (context, response) structures, requiring task-specific premise construction:

**Dialogue**: Multi-turn conversation history. We use a **last-3-turn window** as the premise: the three most recent dialogue turns preceding the response under evaluation. This bounds the premise length to avoid token overflow while preserving the most relevant local context. Hallucinations in dialogue typically contradict facts established in recent turns, not the full conversation history.

**QA**: Question-answer pairs with a knowledge grounding passage. The full grounding passage serves as the premise; the candidate answer is the hypothesis. QA responses are typically short (one to three sentences), so no windowing is applied.

**Summarization**: Long source document paired with an abstractive summary. The full source document serves as the premise; the summary is the hypothesis. For summarization, response-level NLI (treating the full summary as hypothesis) is used rather than sentence-level, as summarization hallucinations manifest at the document level — specific sentences may be accurate while the summary as a whole misrepresents the source.

## Dataset

We evaluate on HaluEval [Li et al., 2023], using all three tasks: dialogue, QA, and summarization. Each task provides 20,000 balanced pairs (10,000 hallucinated, 10,000 non-hallucinated), for 60,000 total evaluation pairs. The balanced label distribution ensures AUROC is not affected by class imbalance, and the large sample size provides high statistical power for DeLong's variance test.

## Evaluation Protocol

We evaluate using **AUROC** (Area Under the ROC Curve) as the primary metric, measuring the model's ability to rank hallucinated responses above non-hallucinated ones. AUROC is threshold-independent and directly interpretable: AUROC = 0.5 is random; AUROC = 1.0 is perfect. Statistical significance is assessed using the **fastDeLong test** [DeLong et al., 1988], which provides a variance estimate for the AUROC statistic, enabling formal hypothesis testing against the 0.5 (chance) baseline.

Effect size is quantified using **Cohen's d** on the contradiction score distributions of hallucinated vs. non-hallucinated responses, providing a scale-independent measure of discrimination magnitude.

## Mechanism Verification

Beyond existence testing, we verify that the NLI signal reflects a genuine *mechanism* — graded support sensitivity — rather than spurious correlation. Two tests are applied to the pre-computed score distributions:

**Wilcoxon rank-sum test**: Tests whether the distributions of contradiction scores for hallucinated vs. non-hallucinated responses are stochastically different, without assuming distribution shape. A significant result (p < 0.05) indicates the model's scores monotonically track hallucination labels in expectation.

**KL divergence from uniform**: Measures how far the per-class score distributions deviate from uniform. A high KL divergence (threshold: 0.05) indicates that the model assigns meaningfully concentrated — rather than spread — scores within each class, consistent with graded sensitivity rather than near-random scoring.

Both tests are applied to the 20,000 pre-computed scores per task, yielding a total of 60,000 pairs analyzed for mechanism verification. This analysis is computationally lightweight (CPU-only, < 60 seconds), using the scores already computed in the existence experiment.

## Implementation

The NLI inference pipeline runs on a single NVIDIA H100 NVL GPU (CUDA_VISIBLE_DEVICES=0). The cross-encoder model is loaded in float32 with batch size 64. Total inference time for 60,000 pairs is approximately 3.5 hours. The full pipeline — from raw HaluEval data to per-example contradiction scores — is reproducible with a single script. All code follows a flat module layout with explicit relative imports, enabling direct inspection and reproducibility without package installation.

The full experimental code is available alongside this paper.
