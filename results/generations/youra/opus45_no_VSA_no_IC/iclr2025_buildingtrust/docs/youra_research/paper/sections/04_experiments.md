# Experimental Setup

We design experiments to answer four research questions, organized hierarchically from existence to mechanism validation.

## Research Questions

**RQ1 (H-E1):** Do inter-benchmark correlations between TruthfulQA, HaluEval, and FactScore fall in the moderate range (baseline < r < 0.7)?

**RQ2 (H-M1):** Is TruthfulQA distinct from general knowledge as measured by MMLU?

**RQ3 (H-M2):** Is HaluEval's generation coherence dimension distinct from TruthfulQA's misconception resistance?

**RQ4 (H-M3):** Is FactScore's factual precision distinct from both TruthfulQA and HaluEval, and does factor analysis support multi-dimensional structure?

Each question maps directly to a hypothesis with defined success criteria.

## Model Population

We evaluate N=50 models from the Open LLM Leaderboard, selected for diversity across multiple dimensions:

| Dimension | Coverage | Rationale |
|-----------|----------|-----------|
| **Architecture** | 7 families (Llama, Mistral, Falcon, Phi, Qwen, Gemma, Yi) | Cover major decoder-only designs |
| **Scale** | 4 tiers (7B, 13B, 34B, 70B) | Test whether correlations vary with scale |
| **Training Variant** | 4 types (Base, Instruct, Chat, DPO) | Include fine-tuning diversity |

This selection ensures robust correlation estimates not confounded by population homogeneity. Figure 1 shows the diversity distribution across architectures and scales.

## Benchmarks

| Benchmark | Metric | Samples | Dimension Tested |
|-----------|--------|---------|------------------|
| **TruthfulQA-MC2** | Accuracy | 817 | Misconception resistance |
| **HaluEval** | Detection accuracy | 35,000 | Generation coherence |
| **FactScore** | Atomic precision | Varies | Factual precision |
| **MMLU** | Accuracy | 14,000 | General knowledge (baseline) |

**Why these benchmarks?** Each uses a fundamentally different evaluation paradigm—multiple choice, binary detection, and atomic fact verification—enabling us to test whether paradigm differences translate to independent capability dimensions.

## Baselines and Reference Points

### Unrelated-Benchmark Baseline
To establish a floor for meaningful correlation, we compute r(MMLU-Physics, HaluEval). These benchmarks measure clearly distinct constructs (domain knowledge vs. hallucination detection), so their correlation should approach zero.

### Intra-Benchmark Reference
To establish a ceiling, we compute correlations among MMLU subjects. If truthfulness benchmarks measure a single construct, their inter-correlations should approach this intra-benchmark level.

## Evaluation Protocol

1. **Score Collection:** Extract benchmark scores from Open LLM Leaderboard for all 50 models.

2. **Correlation Computation:** Compute Spearman correlation for all benchmark pairs (15 unique pairs). Spearman was chosen for robustness to non-normal distributions.

3. **Significance Testing:** Apply Bonferroni correction for multiple comparisons (α = 0.05/6 = 0.0083 for truthfulness benchmark pairs).

4. **Confidence Intervals:** Generate 95% CIs via 1,000 bootstrap iterations.

5. **Factor Analysis:** Apply PCA to standardized scores; count components needed for 80% cumulative variance.

## Hypothesis Gates

| Hypothesis | Gate Type | Pass Condition | If Fail |
|------------|-----------|----------------|---------|
| H-E1 | MUST_WORK | 0.10 < r < 0.7 for all pairs | Stop pipeline |
| H-M1 | MUST_WORK | r(TQA, MMLU) < r(MMLU internal) | Document limitation |
| H-M2 | SHOULD_WORK | r(HE, TQA) < 0.7 | Continue with caveat |
| H-M3 | SHOULD_WORK | r(FS, TQA) < 0.7 AND r(FS, HE) < 0.7 | Continue with caveat |

MUST_WORK gates require passing for the overall hypothesis to be supported. SHOULD_WORK gates allow continuation with documented caveats.

## Implementation

All experiments were implemented in Python using scipy.stats for correlation computation and sklearn.decomposition for PCA. Code, data extraction scripts, and analysis notebooks are available in the supplementary materials.
