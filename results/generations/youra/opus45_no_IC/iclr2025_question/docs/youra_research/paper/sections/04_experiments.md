# Experimental Setup

We design experiments to test each prediction of our hypothesis. Each sub-hypothesis maps to specific experimental questions with quantified success criteria.

## Research Questions and Sub-Hypotheses

| ID | Question | Success Criterion | Failure Criterion |
|----|----------|-------------------|-------------------|
| H-E1 | Do benchmarks cluster meaningfully by uncertainty distribution? | Silhouette > 0.5 | Silhouette < 0.3 |
| H-M1 | Does semantic entropy correlate with errors? | p < 0.05, Cohen's d > 0.3 | p > 0.10 or d < 0.1 |
| H-M2 | Do same-family benchmarks have similar distributions? | Same-family JS < 0.15 | JS > 0.30 |
| H-M3 | Does within-cluster transfer succeed? | Degradation ≤ 0.08 | Degradation > 0.15 |
| H-M4 | Does cross-cluster transfer fail? | Degradation > 0.15 | Degradation < 0.08 |

## Datasets

We evaluate six benchmarks spanning factual QA and claim verification:

**Factual QA Benchmarks:**
- **TriviaQA** (Joshi et al., 2017): Trivia questions with web/Wikipedia evidence
- **Natural Questions** (Kwiatkowski et al., 2019): Real Google search queries
- **SQuAD** (Rajpurkar et al., 2016): Reading comprehension from Wikipedia

**Entity/Claim Benchmarks:**
- **PopQA** (Mallen et al., 2023): Long-tail entity knowledge questions
- **HaluEval-QA** (Li et al., 2023): Hallucination-annotated QA samples
- **FEVER** (Thorne et al., 2018): Claim verification against Wikipedia

We sample 100-1000 queries per benchmark for proof-of-concept validation, with full-scale evaluation (6000 samples) planned for camera-ready.

## Model Configuration

We use Llama-2-7B-Chat as our primary model:
- Open-weight access enables logit extraction for entropy computation
- 7B scale is representative of deployable models
- Chat fine-tuning provides instruction-following capability

Generation parameters: temperature 0.7, N=10 generations per query, max length 128 tokens.

## Evaluation Metrics

**Clustering quality:**
- Silhouette score: Measures within-cluster cohesion vs between-cluster separation
- Optimal k selection: Maximize silhouette across k ∈ {2, 3, 4, 5}

**Signal validation (H-M1):**
- Mann-Whitney U test for entropy separation (correct vs incorrect)
- Cohen's d effect size
- AUROC for hallucination detection

**Distribution comparison (H-M2):**
- Mann-Whitney U comparing same-family vs cross-family JS-divergence
- Cliff's delta effect size

**Transfer evaluation (H-M3, H-M4):**
- AUROC degradation when applying source threshold to target
- 95% confidence intervals via bootstrap

## Baseline Comparisons

We compare our discovered clustering against:
- **Random cluster assignment**: 100 permutations of benchmark-to-cluster mapping
- **In-distribution AUROC**: Single-benchmark performance from prior work (Kuhn et al., 2023)

Success requires our clustering to significantly outperform random assignment in predicting transfer success.

## Implementation Details

All experiments use:
- Hardware: Single NVIDIA A100 40GB GPU
- NLI model: DeBERTa-v3-large-MNLI (Hugging Face)
- KDE: Gaussian kernel with Scott's rule bandwidth
- Clustering: scipy hierarchical clustering with Ward linkage

Code and data will be released upon publication.
