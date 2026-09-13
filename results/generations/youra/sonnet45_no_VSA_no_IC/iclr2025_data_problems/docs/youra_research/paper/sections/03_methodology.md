# Methodology

Building on our observation that sequential curation creates compositional interactions, we design experiments to test three hypotheses: (1) quality filtering shows diminishing returns with scale, (2) diversity sampling maintains effectiveness with scale, and (3) ordering (QD vs DQ) produces measurably different outcomes. We conduct systematic GPT-2 training across four log-spaced dataset scales (10K, 100K, 1M, 10M tokens) with five curation strategies.

## Experimental Design

### Dataset Scales and Sampling

**Rationale**: Log-spaced scales (10K, 100K, 1M, 10M) capture saturation and persistence trajectories as continuous functions. Linear spacing (10K, 20K, 30K...) would miss log-scale dynamics; fewer scales (2-3) would not establish trajectory confidence.

We sample from **C4 realnewslike** (Common Crawl-derived), a standard language model pretraining corpus. Single-source sampling controls for domain shift—if 10K samples were Wikipedia-like and 10M were Reddit-like, observed effects could reflect domain change rather than scale dependence.

### Curation Strategies

We evaluate five strategies to isolate individual effects and test compositional interactions:

1. **Baseline**: Random 49% sampling (size control)
2. **Q-only**: V-Information filtering to 70%, then random sample to 49%
3. **D-only**: FAC-based diverse sampling to 70%, then random sample to 49%
4. **QD (Quality-First)**: V-Information to 70%, then FAC on that subset to 49%
5. **DQ (Diversity-First)**: FAC to 70%, then V-Information on that subset to 49%

**Fixed reduction rates** (70% first step, 49% final) control for dataset size confounds—all strategies output the same token count, isolating ordering effect from reduction magnitude. Adaptive reduction rates may be optimal but introduce confounds (is performance difference due to ordering or reduction schedule?).

## Quality and Diversity Metrics

### V-Information (Quality)

V-Information [arXiv:2507.00038] measures pointwise information content:

$$
\text{V-Info}(x) = -\log p_{\text{model}}(x)
$$

We use a reference GPT-2 model trained on a broad corpus to compute perplexity-based scores. Documents with V-Info above the 70th percentile are retained as "high quality." This metric captures informativeness: rare but coherent patterns score high, while common noise patterns score low.

### Feature Activation Coverage (FAC, Diversity)

FAC [arXiv:2602.10388] measures feature space coverage using intermediate layer activations. For a batch of documents, we compute:

$$
\text{FAC} = \frac{|\bigcup_{i} \text{active\_features}(d_i)|}{|\text{total\_features}|}
$$

where active features are those exceeding a threshold. FAC correlates ρ=0.90 with downstream performance and preserves long-tail patterns. We select documents that maximize incremental FAC gain (greedy coverage optimization).

**Independence assumption**: V-Info uses pointwise information content, FAC uses feature activation coverage—different criteria in principle. If quality filtering systematically removes diverse documents (correlation artifact), observed QD weakness could be spurious. We verify orthogonality by measuring correlation between V-Info and FAC scores on sampled data.

## Model Training

### Proxy Model Selection

We use **GPT-2 Small (124M parameters)** as our proxy model. **Rationale**: Data Mixing Laws [arXiv:2403.16952] and RegMix [arXiv:2407.01492] validated that small proxy models predict large-scale mixture performance with high correlation. This enables computational feasibility—4 scales × 5 strategies × 3 random seeds would require 400+ GPU-hours on Llama 3 8B but only ~80 GPU-hours on GPT-2 Small.

**Alternative considered**: Larger models (Llama 3 8B, GPT-3.5) would be more convincing but computationally infeasible for proof-of-concept validation. We acknowledge this as a limitation and plan frontier model replication as future work.

### Training Configuration

All models train with identical hyperparameters:
- **Epochs**: 5 (V-Information spec; validated as sufficient for convergence)
- **Optimizer**: AdamW with learning rate 5e-4
- **Batch size**: 32
- **Context length**: 1024 tokens

**Rationale for 5 epochs**: Previous pilot experiments showed 1 epoch insufficient for models to converge; 5 epochs balances convergence with training time. We monitor validation perplexity to detect early stopping triggers but enforce 5-epoch minimum for consistency.

## Evaluation Benchmarks

We evaluate on three diverse downstream tasks to reduce single-task overfitting risk:

1. **MMLU** (Massive Multitask Language Understanding): General capability, 5-shot accuracy
2. **BEIR** (Benchmark for Information Retrieval): Retrieval performance, nDCG@10, 0-shot
3. **GSM8K** (Grade School Math): Reasoning capability, exact match accuracy, 0-shot

**Primary metric**: Average performance across all three benchmarks. This composite metric balances knowledge recall (MMLU), retrieval (BEIR), and reasoning (GSM8K).

**Contamination risk**: Benchmarks may overlap with C4 training data. We acknowledge this limitation and defer contamination detection (ConStat, DyePack) to future work. Standard evaluation protocol minimizes risk: 5-shot/0-shot settings, no fine-tuning on test data.

## Hypothesis Testing

### H-E1: Quality Saturation (Existence)

**Hypothesis**: Q-only improvement over baseline decreases monotonically with scale.

**Test**: Train GPT-2 on Q-only vs Baseline at all 4 scales. Measure ΔQ = (Q-only − Baseline). Fit linear regression to ΔQ vs log(scale). Success: negative slope, p < 0.05.

### H-E2: Diversity Persistence (Existence)

**Hypothesis**: D-only improvement over baseline increases with scale.

**Test**: Train GPT-2 on D-only vs Baseline at all 4 scales. Measure ΔD = (D-only − Baseline). Fit linear regression to ΔD vs log(scale). Success: positive slope, p < 0.05.

### H-M1: Compositional Ordering (Mechanism)

**Hypothesis**: Sequential ordering (QD vs DQ) produces statistically different performance.

**Test**: Train GPT-2 on QD vs DQ at all 4 scales. Measure Cohen's d for (QD − DQ). Success: d > 0.5 at all scales, indicating medium-to-large effect sizes.

### H-C1: Coefficient Trajectories (Causal Model)

**Hypothesis**: Quality coefficient α_Q decreases with scale, diversity coefficient α_D increases.

**Test**: Fit compositional model assuming Performance ≈ α_Q·Q + α_D·D. Extract α_Q and α_D at each scale via regression. Success: α_Q slope negative (p<0.05), α_D slope positive (p<0.05), coefficients cross over at medium scale.

## Implementation Details

All code uses PyTorch 2.0 with Hugging Face Transformers. V-Information scores computed with GPT-2 Medium reference model. FAC features extracted from layer 6 activations (mid-depth representations balance specificity and generality). Training runs execute on NVIDIA A100 GPUs with mixed-precision (fp16) for efficiency. We set 3 random seeds per condition for statistical robustness, reporting mean and standard deviation.

**Reproducibility**: All hyperparameters, data splits, and random seeds are logged. Code and preprocessed datasets will be released upon publication to enable replication and extension.
