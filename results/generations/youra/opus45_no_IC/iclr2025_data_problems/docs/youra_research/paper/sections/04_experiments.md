# Experimental Setup

We design experiments to answer two core questions that test our central claims about contamination-inflation correlation:

**RQ1:** Does a statistically significant correlation exist between n-gram contamination exposure and benchmark score inflation?

**RQ2:** Is n-gram overlap reliably detectable in standard benchmarks using established methodology?

## Models and Checkpoints

We use the Pythia model family [Biderman et al., 2023] for its unique combination of training transparency, checkpoint availability, and documented corpus:

| Size | Parameters | Checkpoints | Training Steps |
|------|------------|-------------|----------------|
| 410M | 405M | 12 | 0 - 143,000 |
| 1B | 1.0B | 12 | 0 - 143,000 |
| 1.4B | 1.4B | 12 | 0 - 143,000 |
| 2.8B | 2.8B | 12 | 0 - 143,000 |
| 6.9B | 6.9B | 12 | 0 - 143,000 |
| 12B | 11.8B | 12 | 0 - 143,000 |

**Total:** 72 checkpoint-benchmark pairs (6 sizes × 12 checkpoints)

**Why Pythia:** Unlike most model families, Pythia provides documented training data (The Pile), deterministic training order across all sizes, and publicly available intermediate checkpoints—enabling ground-truth contamination measurement.

## Benchmarks

We evaluate on four standard language model benchmarks representing diverse task types:

| Benchmark | Samples | Task Type | Contamination Relevance |
|-----------|---------|-----------|-------------------------|
| MMLU | 14,042 | Multiple-choice QA | High (factual overlap likely) |
| ARC-Challenge | 1,172 | Science QA | Medium (reasoning focus) |
| HellaSwag | 10,042 | Sentence completion | Medium (synthetic generation) |
| WinoGrande | 1,267 | Coreference resolution | Low (minimal verbatim overlap expected) |

**Why these benchmarks:** MMLU contains factual content likely present in web corpora; ARC-Challenge tests science reasoning; HellaSwag's synthetic generation may reduce contamination; WinoGrande's coreference format provides a low-contamination control.

## Capability Baseline

**WikiText-103 perplexity** serves as our contamination-independent capability measure:
- Source: Wikipedia (distinct from The Pile's benchmark-relevant content)
- Metric: Perplexity (lower = better capability)
- Purpose: Detrend benchmark scores to isolate contamination effects

## Contamination Measurement

**N-gram overlap (13-gram):** Following Brown et al. [2020], we compute 13-gram overlap between benchmark items and The Pile training corpus.

**Implementation:**
- Extract all 13-grams from benchmark test items
- Query against pre-computed Pile n-gram index (EleutherAI decontamination scripts)
- Compute per-item and per-benchmark overlap percentages

**Corpus coverage note:** Due to computational constraints, we analyze a 50,000 document subset of The Pile (0.006% of full corpus). This limits corpus-wide statistics but validates the detection mechanism.

## Evaluation Protocol

**Benchmark evaluation:** lm-evaluation-harness [Gao et al., 2023] with standard settings:
- 0-shot evaluation for MMLU, ARC-Challenge, HellaSwag, WinoGrande
- Auto-selected batch size per checkpoint
- Deterministic evaluation (seed = 1)

**Capability measurement:** WikiText-103 perplexity evaluated at each checkpoint.

## Statistical Analysis

**Primary metric:** Spearman rank correlation between contamination exposure and inflation residual.

**Success criteria:**
- Minimum threshold: r > 0.2 with p < 0.05 (weak-to-moderate correlation)
- Primary target: r > 0.5 (strong correlation)

**Why Spearman:** Rank-based correlation is robust to non-linear relationships and appropriate when contamination-inflation may follow non-linear dynamics.

## Implementation Details

**Hardware:** Single NVIDIA A100 GPU (80GB)

**Evaluation time:** ~2 GPU-hours per checkpoint × 72 checkpoints ≈ 144 GPU-hours total

**N-gram indexing:** ~48 CPU-hours (one-time computation)

**Correlation analysis:** <1 minute (statistical computation only)

**Code availability:** Evaluation and analysis scripts provided in supplementary materials.
