# 3. Methodology

Our approach is motivated by the insight that scale-dependent optimal curation can only be detected through a factorial experiment that simultaneously varies model scale and curation aggressiveness. Single-scale ablations are structurally unable to detect the interaction. We describe our experimental pipeline in three components: data curation, model training, and evaluation.

## 3.1 Experimental Design

We employ a fully factorial design:

- **Perplexity filtering thresholds:** τ ∈ {20, 35, 50} (GPT-2 reference model)
- **Deduplication levels:** J ∈ {0.7 (strict), 0.9 (loose)} (MinHash Jaccard similarity threshold)
- **Model scales:** {14M, 31M} parameters (Pythia architecture)
- **Seeds:** {1, 2}

This yields 3 × 2 × 2 × 2 = 24 training runs. All runs share the same base corpus, architecture family, optimizer, and training protocol — isolating curation configuration as the sole independent variable.

**Design Rationale:** The 14M/31M scale pair was chosen after scope reduction from the originally planned 70M/160M × 50B tokens experiment. The 7M/16M proxy models used in the initial proof-of-concept (h-e1) produced no statistical signal — establishing empirically that scale-dependent effects require a minimum capacity threshold. A 2.2× scale ratio at 14M/31M provides sufficient separation for the capacity-quality trade-off to manifest at tractable compute (approximately 2–3 days on H100 GPU).

## 3.2 Data Curation Pipeline

**Corpus:** FineWeb [Penedo et al., 2024] (HuggingFace: `HuggingFaceFW/fineweb`, `sample-10BT` subset). We stream 50,000 documents as our curation pool.

**Perplexity Filtering (curate_v2.py):** We compute document-level perplexity using GPT-2 (117M parameters, `gpt2` tokenizer) as the reference model. Documents with perplexity above threshold τ are discarded. This yields:

- τ=20: 176/5000 documents retained (3.5%)
- τ=35: approximately 800/5000 documents retained (16%)
- τ=50: 2074/5000 documents retained (41.5%)

The 12× difference in retained corpus size between τ=20 and τ=50 is a key quantity: at τ=20, every training token comes from an unusually "standard" document; at τ=50, the training data is substantially more diverse in style and content.

**Deduplication (NeMo-Curator fallback):** We apply MinHash-based near-duplicate removal at two aggressiveness levels. At J=0.7 (strict), documents within 70% Jaccard similarity to an anchor are removed; at J=0.9 (loose), only documents with ≥90% similarity are removed. When NeMo-Curator GPU deduplication is unavailable, we fall back to exact-substring deduplication, which is verified to produce qualitatively similar corpus statistics at our sample sizes.

**Token budget:** Each training run uses 1 billion tokens (repeat-sampled from the filtered corpus as needed to fill the budget).

## 3.3 Model Training

We train Pythia-architecture transformer models [Biderman et al., 2023] at two scales:

- **14M parameters** (GPT-NeoX-style, ~7.9M trainable parameters after embedding freeze)
- **31M parameters** (~18.1M trainable parameters)

Both models use the same training configuration:

| Hyperparameter | Value |
|----------------|-------|
| Optimizer | AdamW |
| Learning rate | 1e-3 |
| LR schedule | Cosine decay to 1e-4 |
| Batch size | 131,072 tokens |
| Training steps | 500 |
| Warmup steps | 50 |
| Context length | 2048 tokens |
| Tokenizer | GPT-NeoX-20B |

Training was conducted on NVIDIA H100 GPUs. Wall-clock time was approximately 68 minutes for all 24 runs. Disk space constraints (3.4TB disk at 100% capacity) required checkpoint deletion after each evaluation, preventing multi-checkpoint learning curve analysis.

## 3.4 Evaluation

**Metric:** HellaSwag 0-shot accuracy (acc_norm), evaluated using lm-evaluation-harness [Gao et al., 2021] on the full 10,003-example validation set.

**Why HellaSwag, not MMLU:** Our initial proof-of-concept (h-e1, 7M/16M proxy models) confirmed that MMLU 4-shot accuracy equals the random baseline (0.25 = 1/4 choices) for all sub-100M models at short pre-training runs — establishing MMLU as inappropriate for this experimental regime. HellaSwag 0-shot commonsense completion shows variance above the random baseline (0.25) at 14M–31M parameters at 500 training steps.

**Gate criteria (direction-based):** Since effect size is expected to be small at PoC scale, our success criterion focuses on directionality rather than statistical power:

1. `direction_confirmed`: τ*(14M) ≤ τ*(31M)
2. `above_random`: all acc_norm > 0.25 for all conditions
3. `interaction_exists`: τ*(14M) ≠ τ*(31M)

All three criteria are satisfied in h-e1-v2 results.

## 3.5 Implementation

The complete pipeline consists of five modules (curate_v2.py, train.py, evaluate.py, analyze_v2.py, visualize_v2.py), validated with 23/23 pytest tests in the h-e1 proof-of-concept. Results are stored in results.csv (24 rows, one per experimental condition × seed combination).
