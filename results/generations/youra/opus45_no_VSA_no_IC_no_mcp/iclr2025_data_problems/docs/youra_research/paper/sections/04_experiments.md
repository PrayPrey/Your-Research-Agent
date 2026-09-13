# Experimental Setup

We design experiments to answer the following research questions:

**RQ1:** Does a non-monotonic dose-response relationship exist between perplexity filtering thresholds and benchmark performance?

**RQ2:** Does the noise dilution mechanism explain why intermediate thresholds outperform extremes?

**RQ3:** Where is the optimal perplexity threshold, and how precisely can it be identified?

**RQ4:** Do optimal thresholds transfer across model scales (125M to 1B)?

**RQ5:** Does CPDR-optimized configuration outperform industry-standard RedPajama defaults?

## Dataset

We use RedPajama-v2 [Together Computer, 2023], a large-scale web corpus representative of modern LLM training data. The dataset provides raw text samples with quality annotations enabling controlled filtering experiments.

| Property | Value |
|----------|-------|
| Source | Common Crawl + curated sources |
| Total Documents | 30B+ |
| Our Sample | 10B tokens (target); 5M-10M tokens (PoC) |
| Language | English |
| Quality Signal | KenLM 5-gram perplexity |

**Why RedPajama:** The dataset is (1) representative of production LLM training data, (2) provides raw quality signals enabling threshold experimentation, and (3) has established baseline configurations in the literature for comparison.

## Baselines

We compare against:

**No Filtering (p0):** Raw corpus without perplexity filtering. Included to establish lower bound and test noise dilution hypothesis.

**RedPajama Defaults:** Literature-standard perplexity and deduplication thresholds from RedPajama documentation. Represents current industry practice.

**CPDR-Optimized:** Curation parameters selected via our dose-response sweep methodology. Tests whether systematic optimization improves over heuristic choices.

## Implementation Details

**Model Architecture:** GPT-2 variants (125M, 350M, 1B parameters) using HuggingFace Transformers implementation.

**Training Configuration:**
- Learning rate: 6e-4 with cosine decay
- Batch size: 512 sequences
- Warmup: 2000 steps
- Training tokens: 10B (target), 5M-10M (PoC validation)
- Random seeds: 42 (primary), 123, 456 (variance estimation)

**Compute Resources:** Training performed on 4×A100 GPUs. Single 125M configuration requires approximately 8 GPU-hours at PoC scale.

**Perplexity Scoring:** KenLM 5-gram model trained on Wikipedia following CCNet methodology [Wenzek et al., 2020]. Samples filtered by percentile threshold (p0 through p90).

## Evaluation Protocol

**Benchmark Ensemble:** We evaluate on four reasoning benchmarks: HellaSwag, ARC-Easy, PIQA, and WinoGrande. Following scaling laws literature, we compute a benchmark ensemble score as the first principal component (PC1) of accuracy scores, reducing noise from individual benchmark variance.

| Benchmark | Task Type | Metric |
|-----------|-----------|--------|
| HellaSwag | Commonsense reasoning | Accuracy |
| ARC-Easy | Science QA | Accuracy |
| PIQA | Physical reasoning | Accuracy |
| WinoGrande | Coreference resolution | Accuracy |

**Contamination Verification:** We apply Min-K%++ [Shi et al., 2024] membership inference to verify evaluation set integrity before reporting scores.

**Statistical Analysis:** Polynomial regression with AIC/BIC model selection for dose-response characterization. Bootstrap resampling (1000 iterations) for confidence intervals on optimal threshold estimates.

## Experimental Procedure

For each hypothesis (H-E1 through H-C1), we follow a standardized procedure:

1. **Data Preparation:** Filter RedPajama-v2 at specified threshold levels
2. **Model Training:** Train GPT-2 125M with fixed hyperparameters
3. **Evaluation:** Compute benchmark ensemble scores
4. **Analysis:** Fit polynomial models, extract metrics
5. **Validation:** Verify results against success criteria
