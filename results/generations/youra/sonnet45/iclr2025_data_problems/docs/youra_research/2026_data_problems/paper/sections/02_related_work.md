# 2. Related Work

Our work sits at the intersection of four bodies of literature: quality-aware
scaling laws, perplexity-based data selection, benchmark evaluation methodology,
and model documentation standards. We review each and clarify how our contribution
differs.

## 2.1 Data Quality in Pretraining and Scaling Laws

The dominant framework for understanding LLM performance is the Chinchilla
scaling law [Hoffmann et al., 2022], which characterizes loss as a function of
model size N and training data volume D, assuming fixed data quality. Subramanyam
et al. [2025] extend this framework to include a dimensionless data quality scalar Q,
yielding L(N, D, Q) = A/N^α + B/(D^β Q^γ) + E with γ_CLM ≈ 0.39. This
formalization is theoretically important but operationally limited: Q must be
measured through controlled noise injection experiments, not observationally
from deployed models.

A parallel literature studies how domain composition affects benchmark performance.
Myntti et al. [2025] show that text register (opinion, news, web) differentially
affects benchmark scores, with opinion-register documents improving and news-register
documents hurting performance. Diao et al. [2025] (Nemotron-CLIMB) demonstrate that
automated domain mixture optimization yields 5% improvement on target-domain
benchmarks. These studies establish that data composition is a meaningful determinant
of benchmark performance — but they require corpus access to compute composition,
which is unavailable for most deployed models.

**Our difference:** We operationalize data quality through observable documentation
indicators (binary presence/absence in model cards) rather than requiring corpus
access. This approach scales to thousands of models but measures intent rather than
implementation — a limitation we explicitly acknowledge.

## 2.2 Perplexity and Corpus-Level Quality Proxies

Thrush et al. [2025] provide the most direct predecessor to our work: using the Open
LLM Leaderboard (90 models), they estimate perplexity-benchmark rank correlations
(γ_j statistic) across 26,000 web domains to identify high-quality data sources for
pretraining. Their method achieves average rank 1.375 vs. DSIR's 4.500, demonstrating
that perplexity-benchmark correlations are actionable.

Shum et al. [2025] (Predictive Data Selection) build on this: FastText-based data
selection using pre-computed loss-benchmark correlations achieves 10× compute
reduction. Messmer et al. [2025] show model-based filtering on MMLU can match
rule-based filtering with 15% of training tokens.

**Our difference:** These methods require either inference access to compute model
perplexity or actual training runs to measure filtering effects. Our documentation
proxy requires only model card scraping — scales to 4,493 models with no inference
compute. The trade-off is precision: documented practices are a weaker signal than
computed perplexity, but are accessible at ecosystem scale.

## 2.3 Benchmark Evaluation and Contamination

The benchmark ecosystem against which we measure models matters. Zhu et al. [2024]
show benchmark contamination inflates MMLU scores by ~19% via decontamination at
inference time. Wu et al. [2024] (AntiLeak-Bench) propose constructing contamination-
free benchmarks from new knowledge. These studies establish that documented
decontamination practices — which we track as one binary feature — are non-trivial:
contaminated training data measurably inflates benchmark performance.

The Open LLM Leaderboard v2 benchmarks we use (IFEval, BBH, MATH Lvl 5, GPQA,
MUSR, MMLU-PRO) are substantially harder than v1 (MMLU, ARC, HellaSwag, WinoGrande,
TruthfulQA, GSM8K), measuring reasoning, mathematics, and instruction-following
rather than saturating on scale. This affects our baseline R² (0.42 vs. expected
0.60–0.75): V2 benchmarks are harder to predict from scale alone.

**Our difference:** We study documentation of decontamination as a training-time
covariate in predicting benchmark scores, complementary to inference-time
contamination detection methods.

## 2.4 Model Documentation Standards

Mitchell et al. [2019] introduce model cards as a transparency mechanism for AI
systems, recommending documentation of training data, evaluation results, and use
cases. Gebru et al. [2021] propose datasheets for datasets as complementary
documentation artifacts. These proposals have been widely adopted: HuggingFace
requires model cards for all model submissions and has made them a standard practice.

Despite wide adoption, model cards have primarily been studied qualitatively or
for completeness (presence/absence of required sections) rather than for their
relationship to independently measured outcomes. Several audits [CITATION NEEDED]
find that documentation quality varies substantially across model families.

**Our difference:** We are the first to quantitatively link model card curation
documentation to independently measured benchmark performance at scale (n = 4,493).
This transforms model cards from transparency artifacts into empirical objects
amenable to hypothesis testing.

## 2.5 Summary of Positioning

| Work | Data Source | Models | Documentation Signal | Performance Signal |
|---|---|---|---|---|
| Thrush et al. [2025] | Web domain perplexity | 90 | Computed (inference) | OLL Leaderboard v1 |
| Subramanyam et al. [2025] | Noise injection | Synthetic | Controlled (training) | Held-out loss |
| Myntti et al. [2025] | Corpus text register | Few | Direct corpus access | Benchmark scores |
| **This work** | **Model card text** | **4,493** | **Human-written (cards)** | **OLL Leaderboard v2** |

Our registry is unique in combining documentation-based proxies with leaderboard-scale
benchmark coverage, at the cost of weaker signal strength compared to computed quality measures.
