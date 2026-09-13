# 4. Experimental Setup

We design our experiments to answer three specific research questions about the Scale × Curation interaction:

**RQ1:** Does the optimal perplexity filtering threshold differ between 14M and 31M Pythia-architecture models trained on the same FineWeb corpus?

**RQ2:** Is the directional ordering of optimal thresholds (τ*(14M) vs. τ*(31M)) consistent across random seeds and deduplication conditions?

**RQ3:** Do all experimental conditions produce HellaSwag accuracy above the random baseline, confirming that genuine learning occurs across all curation configurations?

These questions map directly to the three gate criteria: direction_confirmed, interaction_exists, and above_random.

## 4.1 Dataset

**FineWeb** (HuggingFace: `HuggingFaceFW/fineweb`, `sample-10BT`): a high-quality English web corpus derived from 96 CommonCrawl dumps with heuristic quality filtering and deduplication already applied. We stream 50,000 documents as our curation pool, then apply our own perplexity and deduplication filters to produce the experimental training corpora.

FineWeb was chosen because (1) it has a well-characterized quality distribution from its own preprocessing, (2) HuggingFace streaming API enables reproducible sampling, and (3) it is a standard reference corpus in recent pre-training curation literature [He et al., 2024; Penedo et al., 2025]. Note that FineWeb already applies baseline quality filters — our GPT-2 PPL filtering operates on top of this, creating a two-stage quality signal.

**Corpus statistics after filtering:**

| PPL Threshold (τ) | Documents Retained | Retention Rate | Tokens (approx.) |
|-------------------|-------------------|----------------|------------------|
| 20 | 176 / 5000 | 3.5% | ~350K |
| 35 | ~800 / 5000 | ~16% | ~1.6M |
| 50 | 2074 / 5000 | 41.5% | ~4.1M |

All training runs use 1 billion tokens via repeat-sampling from the filtered corpus.

## 4.2 Models

We train Pythia-architecture language models at two scales:

| Model | Parameters | Trainable Params | Architecture |
|-------|-----------|-----------------|--------------|
| Pythia-14M | 14M | ~7.9M | 6 layers, 4 heads, d_model=256 |
| Pythia-31M | 31M | ~18.1M | 6 layers, 8 heads, d_model=512 |

Both models are trained from random initialization (no pre-training checkpoint). The 2.2× scale ratio (14M/31M) is sufficient to manifest the capacity-quality trade-off while remaining computationally tractable.

## 4.3 Curation Conditions

The factorial design covers 6 curation conditions per model scale:

| Condition | PPL Threshold (τ) | Dedup Level (J) | Corpus Size |
|-----------|-------------------|-----------------|-------------|
| C1 | 20 | 0.7 (strict) | 3.5% of pool |
| C2 | 20 | 0.9 (loose) | 3.5% of pool |
| C3 | 35 | 0.7 (strict) | ~16% of pool |
| C4 | 35 | 0.9 (loose) | ~16% of pool |
| C5 | 50 | 0.7 (strict) | 41.5% of pool |
| C6 | 50 | 0.9 (loose) | 41.5% of pool |

For each condition × scale combination, we train 2 random seeds, yielding 24 total training runs.

## 4.4 Evaluation Protocol

**Metric:** HellaSwag 0-shot accuracy (acc_norm), the normalized accuracy on the sentence completion task. acc_norm is normalized by the log-likelihood per character, accounting for completion length differences. Random baseline = 0.25 (4 choices).

**Why HellaSwag:** MMLU 4-shot accuracy is at the random baseline (0.25) for all sub-100M models at 500 training steps — confirmed in our h-e1 proof-of-concept. HellaSwag 0-shot commonsense completion is sensitive to early language modeling capability at this scale.

**Evaluation tool:** lm-evaluation-harness [Gao et al., 2021], full 10,003-example HellaSwag validation set. We use `CUDA_VISIBLE_DEVICES` assignment to allow parallel evaluation on the H100 GPU.

## 4.5 Training Protocol

All models are trained with identical hyperparameters (see Section 3.3, Table 1). Training duration is 500 steps, corresponding to approximately 65.5 million tokens per pass (131,072 token batch × 500 steps). With repeat-sampling, each model sees approximately 1 billion tokens total (15.3 passes over the filtered corpus for τ=50; 2857 passes for τ=20, since the τ=20 corpus is small).

**Infrastructure:** NVIDIA H100 80GB GPU. Wall-clock time: approximately 68 minutes total for all 24 runs. Disk management: model checkpoints are deleted after evaluation to manage the 3.4TB disk (at 100% capacity during experiments). This prevents per-checkpoint learning curve analysis (single final checkpoint only).
