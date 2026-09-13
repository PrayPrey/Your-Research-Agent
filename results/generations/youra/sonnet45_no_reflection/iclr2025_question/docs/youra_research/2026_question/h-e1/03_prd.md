---
name: Product Requirements Document
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
created_at: 2026-05-12
author: Phase 3 Implementation Planning
phase: Phase 3
stepsCompleted: ['executive_summary', 'problem_statement', 'functional_requirements', 'nfrs', 'success_criteria', 'dependencies']
---

# Product Requirements Document: H-E1 Geometric Uncertainty Correlation

**Hypothesis:** Under epistemic uncertainty conditions (TruthfulQA factual questions), if we extract geometric features (participation ratio, eigenvalue spectrum, condition number) from layers 24-31 hidden states at pre-generation final token position, then these features will achieve Spearman |ρ| > 0.4 correlation with ground-truth semantic entropy, because uncertain model states exhibit measurable geometric signatures.

**Gate Type:** MUST_WORK
**Prerequisites:** None (foundation hypothesis)

---

## 1. Executive Summary

### Purpose
Validate whether geometric properties of hidden state representations can serve as single-pass proxies for epistemic uncertainty in large language models, offering a computationally efficient alternative to multi-sample semantic entropy computation.

### Success Definition
Achieve Spearman correlation |ρ| > 0.4 (p < 0.001, 95% CI excludes 0.3) between at least one geometric feature (participation ratio, eigenvalue decay rate, or condition number) and ground-truth semantic entropy on TruthfulQA questions.

### Key Deliverables
1. Hidden state extraction pipeline for Llama-3-8B-Instruct (layers 24-31)
2. Geometric feature computation module (PR, eigenvalue decay, condition number)
3. Semantic entropy ground truth computation (K=10 samples, DeBERTa NLI clustering)
4. Correlation analysis with bootstrap validation
5. Validation report (04_validation.md) with gate evaluation

---

## 2. Problem Statement

### Current State
- Semantic entropy (SE) requires K=10+ generations for uncertainty quantification (~1500ms overhead)
- Single-pass uncertainty proxies (perplexity, entropy) correlate poorly with semantic uncertainty
- No validated geometric approach exists for epistemic uncertainty detection

### Desired State
- Single forward pass extracts geometric features from hidden states
- Features achieve |ρ| > 0.4 correlation with semantic entropy
- Computational cost < 50ms per query (vs. 1500ms for multi-sample SE)

### Gap Analysis
Research shows geometric signatures exist in neural representations, but no prior work validates correlation with semantic entropy in LLMs. This experiment establishes feasibility before mechanism investigation.

---

## 3. Functional Requirements

### FR-1: Data Preparation
**Priority:** P0 (MUST_WORK gate dependency)

- **FR-1.1:** Load TruthfulQA dataset from HuggingFace (`truthful_qa/generation`)
  - 817 total questions
  - Split: 70/30 train/test (572 train, 245 test)
  - Tokenize with Llama-3 tokenizer
  
- **FR-1.2:** Load Llama-3-8B-Instruct model
  - Source: `meta-llama/Meta-Llama-3-8B-Instruct`
  - Precision: float16 for inference
  - Device: Single GPU (CUDA_VISIBLE_DEVICES set)
  - Configuration: `output_hidden_states=True`

- **FR-1.3:** Verify data quality
  - All questions tokenizable
  - No corrupted entries
  - Final token position identifiable for each question

### FR-2: Hidden State Extraction
**Priority:** P0 (Core mechanism)

- **FR-2.1:** Extract hidden states from layers 24-31
  - Position: Final token before generation
  - Shape per layer: [N, 4096] where N = batch size
  - Store all 8 layer outputs
  
- **FR-2.2:** Implement extraction via forward pass
  - Use HuggingFace transformers API
  - Access via `model(inputs, output_hidden_states=True).hidden_states`
  - Extract indices 24-31 from hidden_states tuple

### FR-3: Geometric Feature Computation
**Priority:** P0 (Independent variable)

- **FR-3.1:** Participation Ratio (PR)
  - Formula: PR = (Σλᵢ)² / (Σλᵢ²)
  - Input: Covariance matrix eigenvalues
  - Range: [1, D] where D=4096
  - Implementation: Use NerVE repository pattern
  
- **FR-3.2:** Eigenvalue Decay Rate (α)
  - Formula: Slope of log(λᵢ) vs. index
  - Fit: Linear regression on log-eigenvalue spectrum
  - Range: [0, ∞)
  
- **FR-3.3:** Condition Number (κ)
  - Formula: κ = λ_max / λ_min
  - Numerical stability: Add ε=1e-12 to denominator
  - Range: [1, ∞)
  
- **FR-3.4:** Covariance computation
  - Concatenate hidden states across 8 layers: [N×8, 4096]
  - Mean-center: X_centered = X - mean(X, dim=0)
  - Compute: C = (X_centered^T @ X_centered) / (N×8 - 1)
  - Use `torch.linalg.eigvalsh` for symmetric matrix

### FR-4: Semantic Entropy Ground Truth
**Priority:** P0 (Dependent variable)

- **FR-4.1:** Generate K=10 samples per question
  - Temperature: T=0.7
  - Sampling: nucleus/top-p sampling
  - Store generation likelihoods
  
- **FR-4.2:** Semantic clustering via NLI
  - Model: DeBERTa-v3-base-mnli-fever-anli
  - Cluster semantically equivalent generations
  - Implementation: Use `jlko/semantic_uncertainty` repository
  
- **FR-4.3:** Compute semantic entropy
  - Formula: SE = -Σ p_i log(p_i)
  - p_i = cluster_count_i / K
  - Range: [0, log(K)] ≈ [0, 2.3] bits

### FR-5: Correlation Analysis
**Priority:** P0 (Success criteria)

- **FR-5.1:** Spearman correlation computation
  - Test set only (N=245)
  - Compute for each feature (PR, α, κ) vs. SE
  - Use `scipy.stats.spearmanr`
  
- **FR-5.2:** Statistical validation
  - p-value < 0.001 threshold
  - Bootstrap 95% confidence intervals (1000 resamples)
  - Verify CI excludes 0.3
  
- **FR-5.3:** Visualization
  - Scatter plots: Each feature vs. SE with regression line
  - Distribution plots: Feature distributions for high/low SE
  - Correlation heatmap
  - Bootstrap CI plot

### FR-6: Evaluation and Reporting
**Priority:** P0 (Gate validation)

- **FR-6.1:** Gate evaluation
  - Check: |ρ| > 0.4 for at least one feature
  - Check: p < 0.001
  - Check: 95% CI excludes 0.3
  - Result: PASS or FAIL
  
- **FR-6.2:** Generate 04_validation.md
  - Include correlation results table
  - Include all required visualizations
  - Include gate evaluation decision
  - Include statistical test details

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Single-GPU execution (A100 40GB or V100 32GB)
- Total runtime < 4 hours for full dataset
- Memory usage < 30GB
- Feature extraction < 50ms per question (amortized)

### NFR-2: Reproducibility
- Fixed random seed: 42
- Deterministic sampling where possible
- Version pinning: transformers, torch, scipy
- Document all hyperparameters

### NFR-3: Code Quality (LIGHT tier - minimal infrastructure)
- Configuration: Hardcoded constants or argparse
- Logging: Print statements + CSV output
- Testing: Smoke test only (single question validation)
- No WandB integration required

### NFR-4: Numerical Stability
- Eigenvalue computation: float32 precision
- Epsilon values: 1e-12 for division safety
- Use `torch.linalg.eigvalsh` for symmetric matrices
- Handle degenerate cases (all-zero hidden states)

---

## 5. Success Criteria

### Primary Success Criteria (Gate Validation)
1. **Correlation Threshold:** |ρ| > 0.4 for at least one geometric feature
2. **Statistical Significance:** p < 0.001
3. **Confidence Interval:** 95% CI excludes 0.3
4. **Code Execution:** All steps complete without errors

### Secondary Success Criteria
1. **Statistical Stability:** Bootstrap CV < 0.15 for participation ratio
2. **Expected Direction:** Negative correlation for PR, positive for κ
3. **Visualization Quality:** All required plots generated
4. **Computational Efficiency:** Feature extraction < 50ms per sample

### Failure Criteria (Gate FAIL)
- |ρ| < 0.3 for all features
- p > 0.05 for all features
- Code execution errors preventing completion
- Numerical instability (NaN/Inf values)

---

## 6. Dependencies and Constraints

### Software Dependencies
**Core Libraries:**
- Python 3.9+
- PyTorch 2.0+ (CUDA 11.8+)
- transformers 4.36+ (HuggingFace)
- datasets (HuggingFace)

**Numerical/Statistical:**
- numpy 1.24+
- scipy 1.11+
- scikit-learn 1.3+

**NLI Model:**
- DeBERTa-v3-base-mnli-fever-anli (HuggingFace)

**Visualization:**
- matplotlib 3.7+
- seaborn 0.12+

### Hardware Constraints
- Single GPU required (CUDA-capable)
- Minimum 32GB GPU memory (for Llama-3-8B + DeBERTa)
- Recommended: A100 40GB or V100 32GB

### Dataset Constraints
- TruthfulQA: 817 questions (fixed dataset)
- No data augmentation
- 70/30 split enforced
- English language only

### Model Constraints
- Llama-3-8B-Instruct (fixed architecture)
- Frozen weights (no fine-tuning)
- Layers 24-31 only (final 25% of network)
- Single forward pass per question + K=10 samples for SE

### Time Constraints
- Phase 4 implementation: As needed for completion
- Experiment runtime: < 4 hours
- No external dependencies on other hypotheses

---

## 7. Reference Implementations

### Primary References (Official Code)
1. **NerVE** (nerve-eigenspectrum/NerVE)
   - Participation ratio computation
   - Eigenvalue analysis patterns
   - Covariance computation
   - URL: https://github.com/nerve-eigenspectrum/NerVE

2. **Semantic Uncertainty** (jlko/semantic_uncertainty)
   - Semantic entropy computation
   - NLI clustering implementation
   - Generation sampling
   - URL: https://github.com/jlko/semantic_uncertainty

3. **TruthfulQA** (sylinrl/TruthfulQA)
   - Official dataset
   - HuggingFace: `truthful_qa/generation`

### Integration Strategy
- Copy NerVE geometric metrics functions directly
- Integrate semantic_uncertainty SE computation
- Custom glue code for hidden state extraction
- Correlation analysis using scipy

---

## 8. Data Specifications

### Input Data
**TruthfulQA Questions:**
- Format: Text strings
- Count: 817 (572 train, 245 test)
- Fields: question, best_answer, correct_answers, incorrect_answers
- Source: HuggingFace datasets

### Intermediate Data
**Hidden States:**
- Shape: [N, 8, 4096] per batch
- Precision: float16 (inference), float32 (computation)
- Storage: In-memory during processing

**Generated Samples:**
- K=10 per question
- Format: Text strings
- Total: 8,170 generations for full dataset

### Output Data
**Geometric Features (per question):**
- PR: scalar float
- α: scalar float
- κ: scalar float

**Semantic Entropy (per question):**
- SE: scalar float [0, 2.3] bits

**Correlation Results:**
- ρ values: 3 floats (one per feature)
- p-values: 3 floats
- 95% CI: 3 intervals [lower, upper]

---

## 9. Environment Setup

### GPU Selection
```bash
# Check available GPUs
nvidia-smi

# Set single empty GPU
export CUDA_VISIBLE_DEVICES=<empty_gpu_id>  # e.g., 0, 1, 2
```

### Installation
```bash
# Create environment
conda create -n h-e1 python=3.9
conda activate h-e1

# Install dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers datasets scipy scikit-learn matplotlib seaborn
```

### Model Downloads
- Llama-3-8B-Instruct: Auto-download via transformers
- DeBERTa-v3-base: Auto-download via transformers
- TruthfulQA: Auto-download via datasets

---

## 10. Risks and Mitigations

### Risk 1: Low Correlation (Gate FAIL)
- **Impact:** Hypothesis invalidated, MUST_WORK gate fails
- **Likelihood:** Medium (novel approach)
- **Mitigation:** None - this is the fundamental hypothesis test
- **Contingency:** Abandon hypothesis per gate logic

### Risk 2: Numerical Instability
- **Impact:** NaN/Inf values in eigenvalue computation
- **Likelihood:** Low with proper epsilon handling
- **Mitigation:** Use float32, add ε=1e-12, use eigvalsh for symmetric matrices

### Risk 3: GPU Memory Overflow
- **Impact:** OOM errors during batch processing
- **Likelihood:** Low with A100/V100
- **Mitigation:** Reduce batch size, use float16 for inference, clear cache between batches

### Risk 4: Semantic Entropy Computation Errors
- **Impact:** Invalid ground truth, cannot evaluate hypothesis
- **Likelihood:** Low (using official implementation)
- **Mitigation:** Validate SE outputs, check for degenerate cases (all same generation)

---

## Appendix A: Task Budget Summary

**Tier:** LIGHT (EXISTENCE hypothesis)
**Total Max Tasks:** 15
**Epic Task Range:** 4-8
**Infrastructure Level:** Minimal (hardcoded config, print logging, smoke test)

**Expected Task Breakdown:**
- Data Preparation: 2 tasks
- Environment Setup: 1 task
- Epic Tasks: 4-8 tasks (hidden state extraction, geometric features, SE computation, correlation analysis)
- Subtasks: 0-4 tasks (helpers, utilities)
- Failsafe: 0-2 tasks (error handling, validation)

---

## Appendix B: Phase 2C Completeness Check

✅ **Dataset:** TruthfulQA (standard) - Captured in FR-1.1
✅ **Model:** Llama-3-8B-Instruct - Captured in FR-1.2
✅ **Evaluation Metrics:** Spearman correlation, p-value, 95% CI - Captured in FR-5
✅ **Custom Metrics:** Participation ratio, eigenvalue decay, condition number - Captured in FR-3
✅ **Ground Truth:** Semantic entropy via K=10 sampling + NLI - Captured in FR-4
✅ **Ablation Variants:** N/A (PoC experiment, no ablations)
✅ **Baseline Models:** N/A (correlation experiment, not comparison)

**All Phase 2C requirements captured in PRD.**

---

*Generated by Phase 3 Implementation Planning*
*Date: 2026-05-12*
*Hypothesis: h-e1 (EXISTENCE)*
*Next: Architecture Design (Step 3)*
