# Experimental Setup

Our experimental design aimed to answer three questions: (P1) Do geometric features correlate with semantic entropy? (P2) Does a multi-feature ensemble outperform individual features? (P3) Do geometric features add value beyond perplexity? We describe the planned experimental protocol and report execution status for each question.

## Research Questions

**P1: Geometric-Entropy Correlation.** We tested whether participation ratio, eigenvalue decay rate, or condition number extracted from layers 24-31 hidden states achieve Spearman |ρ| > 0.4 correlation with semantic entropy on TruthfulQA test set (N=246 examples). Success required |ρ| > 0.4 with p < 0.001 and 95% confidence interval excluding 0.3, establishing practical predictive value for uncertainty estimation.

**P2: Multi-Feature Ensemble.** Given geometric features as input variables, we planned to train a simple linear classifier (logistic regression) for binary classification of high vs. low uncertainty (median SE split). Success required AUROC > 0.70 with 95% CI excluding 0.65, demonstrating that geometric features contain sufficient information for uncertainty classification.

**P3: Value Beyond Perplexity.** We designed a hierarchical comparison: perplexity-only baseline → add geometric features, measuring ΔAUROC improvement. Success required ΔAUROC ≥ 0.05 with DeLong test statistical significance (p < 0.05), showing geometric features provide information beyond token-level likelihood.

## Dataset Configuration

We used TruthfulQA generation task (Lin et al., 2021) from HuggingFace datasets (truthful_qa, generation config), containing 817 questions spanning science, history, law, and common misconceptions. The dataset was split 70/30 stratified by question category into 571 training and 246 test examples. Only the test set was used for correlation analysis to avoid overfitting—the training set was reserved for potential supervised learning baselines not pursued in this investigation.

## Model and Hardware

**Model.** Mistral-7B-v0.1 (mistralai/Mistral-7B-v0.1), a 32-layer decoder-only transformer with 7B parameters, 32 attention heads, and hidden dimension d=4096. We used bfloat16 precision for memory efficiency and loaded the model with PyTorch 2.0. The model was substituted from the originally planned Llama-3-8B-Instruct due to gated access restrictions.

**Hardware.** Single CUDA GPU (GPU 0) with batch size 2 for hidden state extraction. Total tensor storage requirement: 246 examples × 8 layers × 4096 dimensions × 2 bytes (float16) = ~15.4GB for hidden states plus ~2.4GB model memory.

## Semantic Entropy Configuration

For each test example, semantic entropy was computed via:
- **Sampling.** K=10 responses generated at temperature T=0.7 with nucleus sampling (top-p=0.9)
- **Clustering.** Bidirectional entailment checking using DeBERTa-v3-base (microsoft/deberta-v3-base) fine-tuned on MNLI, FEVER, and ANLI. Two responses considered semantically equivalent if mutual NLI entailment probability >0.5.
- **Entropy.** Discrete entropy H = -Σ p_i log p_i over meaning clusters, where p_i is empirical cluster probability

This configuration follows Farquhar et al. (2024) validated parameters ensuring semantic entropy convergence with K=10 samples.

## Geometric Feature Configuration

**Layer Selection.** Layers 24-31 (final 8 of 32 layers), concatenated into 8d-dimensional representation before covariance computation. This choice was motivated by proximity to output logits, though no ablation study validated optimality.

**Position Selection.** Final token position before generation (EOS token of prompt), capturing consolidated question representation.

**Features Extracted.**
- Participation ratio: PR = trace(C)² / (||C||²_F · 8d)
- Eigenvalue decay rate: α from power law fit λ_k ∝ k^(-α) to top-5 eigenvalues
- Condition number: κ = λ_max / λ_min

**Numerical Stability.** Eigenvalue decomposition used double precision (float64) intermediate computation with regularization term ε = 1e-6 added to diagonal of covariance matrix to prevent numerical issues with near-zero eigenvalues.

## Baseline Methods

**Perplexity.** Token-level perplexity computed as exp(average negative log-likelihood) over question tokens. Included as sanity check—prior work shows weak correlation with semantic entropy, validating that our experimental setup correctly distinguishes semantic from token-level uncertainty.

**Semantic Entropy Probes (Reference).** Kossen et al. (2024) reported AUROC ~0.80 on TruthfulQA using trained probes on hidden states. While we did not implement this baseline (no supervised training), we reference it as the aspirational target performance.

## Evaluation Metrics

**Correlation.** Spearman rank correlation ρ with two-tailed significance test (p-value). Spearman chosen for robustness to non-linear monotonic relationships and outliers.

**Classification.** Area under ROC curve (AUROC) for binary classification (high SE vs. low SE, median split). AUROC preferred over accuracy due to class balance and calibration interpretability.

**Statistical Validation.** Bootstrap resampling (1000 iterations) for 95% confidence intervals on all metrics. Coefficient of variation (CV) computed for participation ratio to verify statistical stability (success requires CV < 0.15).

## Execution Status

**Data Loading.** ✓ Successfully loaded 817 questions with verified 571/246 train/test split. All questions validated as non-empty with proper formatting.

**Model Loading.** ✓ Successfully loaded Mistral-7B-v0.1 in 9 seconds with 2.4GB GPU memory allocation. Model inference functional (test forward pass completed).

**Hidden State Extraction.** ✗ Process hung after >10 hours runtime without producing output. Extraction consumed 590 CPU minutes in "Running" state but generated no hidden state tensors. Log file shows successful model loading followed by silence, suggesting either memory thrashing, inefficient tensor operations, or I/O blocking during serialization.

**Geometric Metrics.** ⏸️ Not executed (blocked by extraction failure). Code implemented (~120 lines) and unit-tested on synthetic data, but no real hidden states available.

**Semantic Entropy.** ⏸️ Not executed (blocked by extraction failure). Code implemented (~221 lines) with DeBERTa model loaded successfully, but no questions processed.

**Correlation Analysis.** ⏸️ Not executed (blocked by extraction failure). Code implemented (~228 lines) with visualization templates, but no correlation measurements obtained.

## Questions Not Answered

All three research questions (P1, P2, P3) remain **empirically untested**. We cannot report whether geometric features correlate with semantic entropy (P1: UNTESTED), whether ensemble classification achieves AUROC > 0.70 (P2: UNTESTED), or whether geometric features add value beyond perplexity (P3: UNTESTED). The experimental design was sound and implementation complete, but computational constraints prevented execution from reaching the analysis phase.
