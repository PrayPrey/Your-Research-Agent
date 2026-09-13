# Experimental Setup

Our experimental design tests three core predictions: quality filtering effectiveness decreases with scale (H-E1), diversity sampling effectiveness increases with scale (H-E2), and sequential ordering creates compositional interactions (H-M1). We organize experiments by hypothesis and describe dataset construction, training procedures, and evaluation protocols.

## Datasets and Scales

We sample from C4 realnewslike at four log-spaced scales: 10K, 100K, 1M, and 10M tokens. For each scale, we construct five datasets corresponding to our curation strategies (Baseline, Q-only, D-only, QD, DQ). Sampling uses stratified random selection to maintain temporal and domain balance within C4.

**Size control**: All strategies output exactly 49% of the original corpus size. This ensures performance differences reflect curation quality, not token count variations. Intermediate filtering steps (Q-only, D-only in two-stage strategies) produce exactly 70% of original size before final reduction to 49%.

## Curation Pipeline Implementation

### Quality Filtering (V-Information)

We compute V-Information scores using a GPT-2 Medium reference model trained on a broad web corpus. For each document d, we calculate:

1. Tokenize d with GPT-2 tokenizer
2. Compute per-token log-probabilities: log p(t_i | t_{<i})
3. Average across tokens: V-Info(d) = -mean(log p)
4. Retain documents with V-Info ≥ 70th percentile

**Computational cost**: ~2 GPU-hours per 10M tokens on A100.

### Diversity Sampling (FAC)

Feature Activation Coverage extraction:

1. Pass document through GPT-2 Small (frozen, pretrained)
2. Extract activations from layer 6 (mid-depth, 768 dimensions)
3. Average-pool across sequence length
4. Binarize with threshold τ=0.1·max(activation)
5. Track cumulative feature coverage across selected documents

**Greedy selection**: Iteratively select documents maximizing incremental FAC gain until reaching target size (70% or 49%). This approximates optimal coverage with O(n²) complexity.

**Computational cost**: ~5 GPU-hours per 10M tokens on A100.

## Training Configuration

All models use GPT-2 Small (124M parameters) with identical hyperparameters:

- **Architecture**: 12 layers, 768 hidden size, 12 attention heads
- **Training**: 5 epochs, batch size 32, sequence length 1024
- **Optimization**: AdamW (β₁=0.9, β₂=0.999, ε=1e-8), learning rate 5e-4, linear warmup (500 steps), cosine decay
- **Regularization**: Weight decay 0.01, gradient clipping at norm 1.0
- **Precision**: Mixed-precision (fp16) for efficiency

**Hardware**: NVIDIA A100 40GB GPUs. Training time ranges from ~30 minutes (10K scale) to ~20 hours (10M scale) per model.

**Random seeds**: We train 3 independent runs per condition with seeds {42, 123, 456} for statistical robustness. Reported metrics are mean ± standard deviation across seeds.

## Evaluation Protocol

We evaluate trained models on three downstream benchmarks without fine-tuning:

### MMLU (General Capability)

- **Task**: 57-subject multiple-choice questions (STEM, humanities, social sciences)
- **Protocol**: 5-shot in-context learning
- **Metric**: Exact match accuracy (%)
- **Subset**: We evaluate on the validation split (1,540 examples) for computational efficiency

### BEIR (Information Retrieval)

- **Task**: Document retrieval across 18 diverse datasets
- **Protocol**: 0-shot, encode queries and documents with mean-pooled embeddings
- **Metric**: nDCG@10 (normalized discounted cumulative gain at rank 10)
- **Subset**: We evaluate on 5 representative datasets (NQ, HotpotQA, FiQA, ArguAna, SciFact)

### GSM8K (Mathematical Reasoning)

- **Task**: Grade-school math word problems
- **Protocol**: 0-shot, extract numeric answer from generated text
- **Metric**: Exact match accuracy (%)
- **Subset**: Full test set (1,319 examples)

**Primary metric**: Average performance across all three benchmarks. We normalize each benchmark to [0, 1] before averaging to ensure equal weighting.

## Statistical Analysis

### Trajectory Fitting (H-E1, H-E2)

For saturation and persistence tests, we fit linear regressions:

- **Model**: ΔMetric = β₀ + β₁·log₁₀(scale) + ε
- **Significance**: Two-tailed t-test on β₁ coefficient
- **Effect size**: R² (coefficient of determination)

Success criteria: |β₁| > 0 with p < 0.05, R² > 0.8 (strong linear trend).

### Ordering Effects (H-M1)

For compositional interaction tests, we compute Cohen's d:

- **Effect size**: d = (mean_QD − mean_DQ) / pooled_std
- **Interpretation**: |d| > 0.5 (medium effect), |d| > 0.8 (large effect)
- **Significance**: Two-sample t-test (3 seeds per condition)

Success criteria: d > 0.5 at all scales with p < 0.05.

### Coefficient Extraction (H-C1)

For compositional model fitting:

- **Model**: Performance ≈ α_Q·Q_score + α_D·D_score + β₀
- **Method**: Ordinary least squares regression at each scale
- **Trajectory**: Fit α_Q and α_D vs log(scale)

Success criteria: α_Q slope < 0 (p<0.05), α_D slope > 0 (p<0.05).

## Validation and Controls

**Contamination check**: We plan to run ConStat [CITATION_NEEDED] contamination detection on final camera-ready version. For this submission, we acknowledge contamination risk and use standard evaluation protocols (few-shot, no test-time tuning) to minimize impact.

**Hyperparameter sensitivity**: We validated 5-epoch training via pilot experiments showing convergence plateau by epoch 4-5 across all scales. Alternative hyperparameters (learning rate 1e-4, 3 epochs) produced similar trends but weaker absolute performance.

**Metric independence**: We verify V-Info and FAC scores have low correlation (ρ < 0.3) on held-out data, confirming they measure orthogonal dimensions.
