# Experimental Setup

We design five experiments to test our contamination-correction hypothesis and its
methodological prerequisites. The first two address the core predictions (P1: existence,
P2: contamination-accuracy correlation); the third tests the memorization mechanism
(H-M2); the fourth validates the methodological confound-control choice (H-M4); and
the fifth provides mechanistic support by characterizing the documents removed by
deduplication (H-M1).

## Research Questions

**RQ1 (Existence):** Does training corpus deduplication produce a statistically significant
per-benchmark accuracy differential between Pile and dedup-Pile Pythia models at
token-count-matched checkpoints?

**RQ2 (Correlation):** Does the per-benchmark accuracy differential correlate positively
with estimated n-gram contamination between the Pile corpus and each benchmark's test set?

**RQ3 (Mechanism):** Do Pile-trained models show higher min-k\% probability scores on
benchmark test items than dedup-Pile models, consistent with greater near-memorization?

**RQ4 (Methodology):** Does token-count matching recover a stronger contamination signal
than step-matching for the Pile/dedup-Pile comparison?

**RQ5 (Documents):** Do documents removed by Pile deduplication show significantly higher
n-gram overlap with benchmark test sets than documents retained in dedup-Pile?

## Models and Checkpoints

We evaluate on four Pythia model sizes: **160M**, **410M**, **1B**, and **6.9B** parameters.
For each size, we compare:
- **Pile:** Checkpoint at step 99,000 ($T_{\text{Pile}} \approx 207$B tokens; $< 0.30\%$ mismatch)
- **dedup-Pile:** Final checkpoint at step 143,000 ($T_{\text{dedup}} \approx 207$B tokens)

This gives us 4 model sizes $\times$ 2 corpora $= 8$ model checkpoints for the primary
existence and correlation analyses. All Pythia models use identical GPT-NeoX architecture,
identical optimizer, context length 2,048 tokens, and identical lm-eval evaluation setup.

| Size | Pile Step | dedup-Pile Step | Token Mismatch |
|------|-----------|-----------------|----------------|
| 160M | 99,000 | 143,000 | $<$0.30\% |
| 410M | 99,000 | 143,000 | $<$0.30\% |
| 1B | 99,000 | 143,000 | $<$0.30\% |
| 6.9B | 99,000 | 143,000 | $<$0.30\% |

## Benchmarks

We evaluate on four standard NLP benchmarks using lm-evaluation-harness (greedy decoding,
deterministic):

| Benchmark | Task Type | Shots | 13-gram Contamination (Pile) | Source |
|-----------|-----------|-------|-------------------------------|--------|
| MMLU | General knowledge | 5 | 5.5\% | Lee et al., 2022 |
| HellaSwag | Commonsense completion | 0 | 20.0\% | Lee et al., 2022 |
| ARC-Challenge | Science reasoning | 25 | 8.5\% | GPT-4 TR |
| WinoGrande | Commonsense pronouns | 5 | 2.5\% | GPT-4 TR |

These benchmarks are selected to span the estimated contamination range (2.5\%--20\%)
while covering diverse task types, enabling a meaningful contamination-accuracy correlation.
All four appear in the Pythia evaluation suite, ensuring consistent evaluation infrastructure.

## Hypothesis-Level Experimental Design

### H-E1: Existence of Benchmark Signature

**Design:** Paired $t$-test across 4 model sizes for each benchmark, testing whether the mean
dedup-Pile minus Pile accuracy difference is significantly different from zero.

**Statistical test:** Two-tailed paired $t$-test, $n = 4$ model sizes per benchmark.
Bonferroni correction for 4 benchmarks: $\alpha_{\text{corrected}} = 0.0125$.

**Gate criterion:** $\geq 1$ benchmark with $p < 0.0125$ across 4 model sizes.

### H-M3: Contamination-Accuracy Correlation

**Design:** Pearson $r$ and Spearman $\rho$ computed over $n = 16$ observations
(4 benchmarks $\times$ 4 model sizes), with 13-gram contamination rate as the predictor
and per-benchmark accuracy differential as the outcome. Bootstrap confidence intervals
($B = 1000$ resamples) characterize uncertainty.

**Gate criterion:** Pearson $r \geq 0.5$, $p < 0.05$.

### H-M2: Min-k\% Memorization Differential

**Design:** Min-k\% probability scores [Shi et al., 2023] computed for Pythia-1B on
500 items per benchmark from each corpus. Primary $k = 20$; robustness analysis at
$k \in \{10, 20, 40\}$. One-tailed paired $t$-test (Pile $>$ dedup-Pile direction).

**Gate criterion:** $\geq 2/4$ benchmarks significant at $p < 0.0125$ (SHOULD\_WORK).

### H-M4: Token-Count vs Step-Matching

**Design:** Compare the contamination-accuracy Pearson $r$ under two matching conditions:
(1) token-count matching (Pile step 99K vs dedup step 143K), and
(2) step-matching (both at step 143K, using a Chinchilla-calibrated log-linear volume-effect
model for the step-matched differential). Compute $\Delta r = r_{\text{token}} - r_{\text{step}}$.

**Gate criterion:** $\Delta r > 0$ (token-count matching yields higher correlation).

### H-M1: N-gram Overlap of Removed Documents

**Design:** Streaming hash-difference pipeline comparing 13-gram overlap distributions
between deduplication-removed documents and retained documents. Mann-Whitney $U$-tests
(non-parametric, Bonferroni-corrected) per benchmark.

**Dry-run PoC:** $n = 200$ per group (synthetic corpus sample).
**Full experiment:** $n = 10{,}000$ per group (production Pile corpus; running at submission time).

**Gate criterion:** $\geq 2/4$ benchmarks significant at $p < 0.0125$ in full experiment.

## Evaluation Metrics

**Primary metrics:**
- Per-benchmark few-shot accuracy (lm-eval, greedy decoding)
- Accuracy differential $\Delta_b = \text{acc}^{\text{dedup}}_b - \text{acc}^{\text{Pile}}_b$
- Pearson $r$ between 13-gram contamination rate and $\Delta_b$ across $n = 16$ observations

**Statistical metrics:**
- Paired $t$-statistic and $p$-value for existence test (H-E1)
- Bootstrap 95\% CI on Pearson $r$ (H-M3)
- Cohen's $d$ for effect sizes (H-M2)

**Methodological validation:**
- $\Delta r$ for token-count vs step-matching (H-M4)
- Uniform bias (mean differential across all benchmarks) to detect volume-effect offset (H-M4)

## Implementation

All Pythia evaluations used lm-evaluation-harness (EleutherAI, v0.4.x) with
the following configuration:
- Decoding: greedy (temperature=0, deterministic)
- MMLU: 5-shot, normalized log-likelihood scoring
- HellaSwag: 0-shot, normalized log-likelihood continuation scoring
- ARC-Challenge: 25-shot, multiple choice log-likelihood
- WinoGrande: 5-shot, partial scoring

Models were loaded in half-precision (float16) with GPU inference. Each (model, corpus,
size, checkpoint) combination was evaluated independently. Checkpoint-to-token-count
mapping was computed from the Pythia training configuration
(2048 tokens per sequence $\times$ batch size per step).
