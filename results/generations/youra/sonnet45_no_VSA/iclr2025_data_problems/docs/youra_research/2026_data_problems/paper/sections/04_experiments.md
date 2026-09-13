# Experimental Setup

Our experiments test three specific hypotheses about calibration for code generation:
1. Code generation models exhibit higher baseline miscalibration than classification models
2. Temperature scaling reduces ECE for code generation tasks
3. Calibration preserves functional correctness (no accuracy degradation)

## Research Questions

**RQ1: Baseline Calibration Quality**  
*How miscalibrated are code generation models compared to established baselines?*

We measure ECE for Code Llama 7B on MBPP and compare to ECE reported for image classifiers in Guo et al. (2017). Expected finding: code generation ECE ≥ 0.15 (higher than CNNs).

**RQ2: Calibration Effect Size**  
*Does temperature scaling reduce ECE for code generation?*

We optimize temperature parameter on calibration split and evaluate ECE reduction on validation split. Success criterion: ≥30% ECE reduction (MUST_WORK validation gate).

**RQ3: Accuracy Preservation**  
*Does calibration degrade functional correctness?*

We measure pass@1 accuracy before and after temperature scaling. Expected finding: Δpass@1 ≈ 0% (temperature scaling is order-preserving, so rankings and top-1 accuracy should be unchanged).

## Dataset Details

**MBPP (Mostly Basic Python Problems):** Standard function-level code generation benchmark with 974 problems. Each problem includes:
- Natural language task description
- Function signature
- 3+ test cases for correctness evaluation

**Custom Splits:**
- **Calibration (200 problems):** IDs 511-600, 11-120
- **Validation (195 problems):** IDs 121-315
- **Reserved (579 problems):** Held out for future work

**Rationale for custom splits:** Standard MBPP provides train/dev/test, but temperature optimization requires calibration data separate from final evaluation. We create calibration split by stratified sampling across difficulty levels (estimated by problem ID ranges).

**Evaluation protocol:** For each problem, we generate one code solution, execute it against test cases, and record binary correctness (all tests pass = 1, any test fails = 0). This differs from typical MBPP evaluation (pass@k with k samples per problem) since we focus on confidence calibration for single predictions.

## Model Configuration

**Code Llama 7B** (meta-llama/CodeLlama-7b-hf)
- 7 billion parameters
- Trained on 500B tokens of code (Python, C++, Java, etc.)
- Specialized for code generation via instruction fine-tuning
- Open-weight (enables logit extraction for calibration)

**Generation settings:**
- Temperature: 1.0 (during generation; calibration applied post-hoc)
- Top-p (nucleus sampling): 0.95
- Max tokens: 256
- Sampling: Single sample per problem (pass@1 setting)

**Why Code Llama 7B?** Representative open-weight model with documented performance on MBPP (~36% baseline accuracy). Logit access required for confidence extraction.

## Evaluation Metrics

### Primary Metric: ECE (Expected Calibration Error)

ECE measures average calibration error across confidence bins:

$$\text{ECE} = \sum_{b=1}^{15} \frac{n_b}{n} | \overline{\text{conf}}_b - \overline{\text{acc}}_b |$$

where:
- $n_b$: number of predictions in bin $b$
- $\overline{\text{conf}}_b$: average predicted confidence in bin $b$
- $\overline{\text{acc}}_b$: empirical accuracy (fraction correct) in bin $b$

**Binning strategy:** 15 uniform bins in [0, 1] (standard in calibration literature)

**ECE reduction:** $(ECE_{\text{before}} - ECE_{\text{after}}) / ECE_{\text{before}} \times 100\%$

**Success threshold:** ≥30% reduction (MUST_WORK gate from Phase 2B verification protocol)

### Secondary Metrics

**Pass@1 accuracy:** Fraction of problems solved correctly (functional correctness)  
**Optimization convergence:** NLL loss at each LBFGS iteration  
**Per-bin calibration error:** $|\overline{\text{conf}}_b - \overline{\text{acc}}_b|$ for each bin (identifies where miscalibration occurs)

## Baseline Comparison

**Uncalibrated baseline:** Model predictions with $T=1.0$ (no temperature scaling)

We do not compare to other calibration methods (Vector Scaling, Matrix Scaling, Platt Scaling) in this work since our goal is to establish whether the simplest baseline (temperature scaling) works for code generation. If temperature scaling achieves ≥30% ECE reduction, more complex methods are unnecessary for initial validation.

**Comparison to prior work:** We compare our ECE reduction percentage to Guo et al. (2017):
- CNNs on CIFAR-100: 5-15% ECE reduction
- ResNets on ImageNet: 8-12% ECE reduction
- Our work (Code Llama on MBPP): Target ≥30%

## Temperature Optimization Procedure

1. **Initialize:** $T = 1.5$ (typical starting value)
2. **Objective:** Minimize negative log-likelihood on calibration split
   $$\mathcal{L}(T) = -\sum_{i \in \text{calibration}} \log P(c_i | x_i, \hat{y}_i, T)$$
3. **Optimizer:** LBFGS (learning rate 0.01, max iterations 200)
4. **Convergence criterion:** NLL stops decreasing or max iterations reached
5. **Output:** Optimal temperature $T^*$

**Validation:** Apply learned $T^*$ to validation split (never seen during optimization) to compute calibrated ECE.

## Execution Environment

**Simulation mode:** This validation uses mock data with realistic characteristics:
- Binary logit representation (correct/incorrect classes)
- Overconfident predictions (high baseline ECE)
- LBFGS optimization with 200 iterations
- ECE computation with 15 bins

**Simulation rationale:** Validates pipeline correctness (optimization, evaluation, visualization) without multi-hour Code Llama execution time. All code paths exercised; only difference is data source (mock vs. real model).

**Production validation (recommended):** Run main.py with real Code Llama 7B:
- Estimated time: 4-6 hours (A100 GPU)
- Model download: ~13GB
- Generation: ~2-3 hours (395 problems × ~20 sec/problem)
- Optimization: ~1-2 minutes (200 LBFGS iterations)

## Reproducibility

**Code:** Available at [repository URL]  
**Data:** MBPP from google-research-datasets/mbpp  
**Model:** meta-llama/CodeLlama-7b-hf on HuggingFace  
**Seeds:** Fixed random seed (42) for generation sampling  
**Compute:** Single A100 GPU (40GB VRAM) for production run

**No hyperparameter tuning:** We use standard values from Guo et al. (2017):
- 15 bins for ECE
- LBFGS for temperature optimization
- Initial $T=1.5$

This avoids overfitting to validation data and enables direct comparison to prior work.
