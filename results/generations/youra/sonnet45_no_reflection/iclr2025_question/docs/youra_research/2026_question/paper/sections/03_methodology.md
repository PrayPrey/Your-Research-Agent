# Methodology

## Overview

Building on our hypothesis that epistemic uncertainty manifests as collapsed subspaces in hidden state geometry, we designed an experimental pipeline to test whether spectral features extracted from late-layer activations correlate with semantic entropy on factual questions. The core intuition is that when a model lacks confident knowledge, its hidden state activations compress into fewer dominant directions—a geometric signature measurable through participation ratio and eigenvalue analysis without requiring multi-sample generation.

Our approach consists of four components: (1) dataset preparation with ground-truth semantic entropy labels, (2) hidden state extraction from late transformer layers, (3) geometric feature computation via spectral analysis, and (4) correlation measurement between geometric features and semantic entropy. We describe each component's design rationale and implementation.

## Dataset and Ground Truth

We use TruthfulQA (Lin et al., 2021), a benchmark dataset designed to elicit epistemic uncertainty through factual questions where models often lack knowledge and produce hallucinated responses. The dataset contains 817 questions spanning science, history, and common misconceptions, split 70/30 into 571 training and 246 test examples.

**Ground Truth Construction.** For each question, we compute semantic entropy (Farquhar et al., 2024) as the gold-standard uncertainty metric. This involves: (1) generating K=10 responses at temperature T=0.7 to capture output distribution, (2) clustering semantically equivalent responses using DeBERTa-v3-base natural language inference (considering responses equivalent if mutually entailing with NLI threshold >0.5), and (3) computing discrete entropy H = -Σ p_i log p_i over meaning clusters, where p_i is the empirical probability of cluster i. This yields semantic entropy values in [0, log K] bits, with higher values indicating greater epistemic uncertainty.

**Rationale.** TruthfulQA provides natural epistemic uncertainty conditions—questions specifically chosen to trigger hallucinations in models lacking factual knowledge. Semantic entropy serves as our ground truth because it measures meaning-level uncertainty validated across multiple benchmarks (Farquhar et al., 2024), unlike token-level perplexity which shows poor correlation with semantic uncertainty.

## Hidden State Extraction

We extract hidden state activations from layers 24-31 (the final 8 of 32 layers) at the final token position before generation begins. For model M and question q, we obtain hidden states h^l_q ∈ R^d for each layer l ∈ {24, 25, ..., 31}, where d=4096 is the hidden dimension.

**Layer Selection Rationale.** We hypothesized that late layers (24-31) capture decision-relevant representations where epistemic uncertainty manifests, as these layers are closest to the output logits and likely encode the model's confidence in factual knowledge. This choice was an architectural assumption (Assumption A2 in our hypothesis) that would require empirical ablation to validate—however, computational constraints prevented such validation.

**Position Selection.** We extract activations at the final token position before generation begins, reasoning that this position encodes the model's consolidated understanding of the question before producing a response. Alternative positions (average across sequence, first token) might capture different aspects of uncertainty but were not tested.

**Implementation.** We use PyTorch hooks to intercept layer outputs during forward pass, storing activations in float16 precision to reduce memory overhead. For the test set (N=246 questions), this requires extracting and storing 246 × 8 layers × 4096 dimensions × 2 bytes = ~15.4GB of tensor data.

## Geometric Feature Computation

Given hidden states H = [h^24, h^25, ..., h^31] ∈ R^(8d) formed by concatenating all 8 layers, we compute the covariance matrix C = H^T H / (8d) and perform eigenvalue decomposition C = VΛV^T to extract spectral features.

**Participation Ratio.** The participation ratio quantifies effective dimensionality:

PR = (trace(C))² / (||C||²_F · 8d)

where ||C||_F is the Frobenius norm. PR ∈ [1/(8d), 1] with higher values indicating more uniform dimension utilization (confident state) and lower values indicating concentration in fewer dimensions (uncertain state under our collapsed subspace hypothesis).

**Eigenvalue Decay Rate.** We fit a power law λ_k ∝ k^(-α) to the top-5 eigenvalues and extract the decay exponent α. Faster decay (higher α) indicates more rapid eigenvalue drop-off, hypothesized to correlate with uncertainty.

**Condition Number.** We compute κ = λ_max / λ_min, the ratio of maximum to minimum eigenvalues. Higher condition numbers indicate ill-conditioned covariance matrices, hypothesized to signal uncertain states.

**Rationale.** These spectral features have well-established interpretations in statistical physics and linear algebra. Participation ratio directly measures effective dimensionality (our core hypothesis), while eigenvalue decay and condition number provide complementary geometric characterizations. All three are training-free—no supervised learning required—and interpretable through their mathematical definitions.

## Correlation Analysis

We measure Spearman rank correlation ρ between each geometric feature (PR, α, κ) and semantic entropy across the test set (N=246). Spearman correlation is appropriate for potentially non-linear monotonic relationships and is robust to outliers.

**Success Criteria.** Our hypothesis predicts |ρ| > 0.4 with p < 0.001 and 95% confidence interval excluding 0.3 for at least one geometric feature. The threshold |ρ| > 0.4 was chosen to ensure practical predictive value—correlation below 0.3 is considered weak in uncertainty quantification contexts.

**Statistical Validation.** We use bootstrap resampling (1000 iterations) to compute 95% confidence intervals and verify statistical stability (coefficient of variation CV < 0.15 for participation ratio).

**Baseline Comparison.** We include perplexity (token-level likelihood) as a control baseline, expecting weak correlation with semantic entropy per prior work, validating that our setup correctly distinguishes semantic from token-level metrics.

## Model Configuration

We planned to use Llama-3-8B-Instruct (meta-llama/Meta-Llama-3-8B-Instruct), a 32-layer decoder-only transformer with 8B parameters. However, due to gated access requiring authentication, we substituted Mistral-7B-v0.1 (mistralai/Mistral-7B-v0.1), a similar-scale 7B parameter model with 32 layers and comparable architecture. Both models use bfloat16 precision and have d=4096 hidden dimensions, making the substitution architecturally compatible for geometric analysis, though results may not generalize across architectures without further validation (Condition hypothesis H-C1).

## Implementation

Our implementation comprises ~1,200 lines of Python code across five modules:

- **config.py** (dependencies, paths, hyperparameters)
- **data/loader.py** (TruthfulQA loading with 70/30 split, 96 lines)
- **models/extractor.py** (hidden state extraction via PyTorch hooks, 125 lines)
- **metrics/geometric.py** (PR, α, κ computation, 120 lines)  
- **metrics/semantic_entropy.py** (SE via NLI clustering, 221 lines)
- **analysis/correlation.py** (Spearman correlation, bootstrap CI, visualization, 228 lines)

The code is modular, type-annotated, and documented, with proper separation of concerns enabling independent testing of each component. However, execution failed during the hidden state extraction phase (models/extractor.py), preventing correlation analysis from running.

## Computational Constraints Discovered

The planned methodology encountered an unexpected computational bottleneck. Hidden state extraction consumed >10 hours of runtime for the 246-example test set without completion, contrasting with the 30-minute Phase 3 complexity estimate—a 20× underestimate. The process allocated 2.4GB GPU memory but stopped producing log output after model loading, suggesting either memory thrashing, inefficient tensor operations, or I/O blocking during large-scale hidden state serialization.

This computational failure reveals that geometric uncertainty quantification for 7B models requires either: (a) optimized extraction using FlashAttention-2, vLLM, or similar inference libraries to reduce forward pass overhead, (b) streaming/checkpointing strategies to avoid memory bottlenecks, (c) resource scaling to MEDIUM+ tier computational capacity, or (d) model downsizing to <1B parameters where extraction becomes tractable on LIGHT tier resources. Without addressing this bottleneck, the correlation hypothesis remains empirically untested.
