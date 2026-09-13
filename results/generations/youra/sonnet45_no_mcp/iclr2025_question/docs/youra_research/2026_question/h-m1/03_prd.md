---
stepsCompleted: [requirements-gathering, functional-requirements, non-functional-requirements, success-criteria]
status: completed
generatedAt: "2026-04-22T03:00:00Z"
hypothesis: h-m1
hypothesisType: MECHANISM
---

# Product Requirements Document: h-m1 - Uncertainty Method Mechanism Analysis

**Date:** 2026-04-22  
**Author:** Anonymous
**Hypothesis:** h-m1 (MECHANISM)  
**Version:** 1.0

---

## Executive Summary

This PRD specifies the implementation requirements for hypothesis h-m1, which analyzes the computational mechanisms of four uncertainty quantification methods (semantic entropy, self-consistency, token variance, verbalized confidence) to determine whether they capture distinct uncertainty dimensions or measure the same signal with different scales.

**Key Objective:** Implement and evaluate four uncertainty methods on NaturalQuestions dataset using Mistral-7B-v0.1 to compute pairwise correlation matrix and verify orthogonality (correlations < 0.7).

**Success Gate:** SHOULD_WORK - All pairwise correlations between methods < 0.7

---

## Problem Statement

### Research Question
Do the four uncertainty quantification methods (semantic entropy, self-consistency, token variance, verbalized confidence) measure distinct uncertainty dimensions, or do they capture the same underlying signal with different computational approaches?

### Hypothesis Statement
Under systematic evaluation, if we analyze the four uncertainty methods using their distinct computational mechanisms, then each method will capture a different uncertainty dimension (semantic diversity, sampling agreement, distributional sharpness, introspective calibration), because the methods are algorithmically designed to measure different statistical properties of model outputs.

### Context from Previous Work (h-e1)
- **Validated Components:** Semantic entropy with K=10 sampling, temperature=0.7, NaturalQuestions dataset, Mistral-7B-v0.1
- **Proven Hyperparameters:** K=10, temperature=0.7, agglomerative clustering for semantic similarity
- **Baseline Performance:** Semantic entropy AUROC 0.78 vs ensemble baseline 0.69

---

## Functional Requirements

### FR-1: Dataset Preparation
**Priority:** P0 (Critical)  
**Description:** Load and preprocess NaturalQuestions dataset for uncertainty analysis

**Acceptance Criteria:**
- Load NaturalQuestions validation split from HuggingFace (`google-research-datasets/natural_questions`)
- Filter to 100 examples for statistically meaningful evaluation
- Extract question text and answer candidates
- Tokenize for Mistral-7B (max length 512 tokens)
- Save preprocessed dataset to hypothesis folder

**Dependencies:** HuggingFace datasets library, transformers tokenizer

**Data Specification:**
- **Source:** `google-research-datasets/natural_questions`
- **Split:** validation
- **Sample Size:** 100 examples (minimum for statistical power)
- **Format:** JSON with fields: question, answers, tokenized_input
- **Storage:** `{hypothesis_folder}/data/natural_questions_100.json`

---

### FR-2: Model Loading and Configuration
**Priority:** P0 (Critical)  
**Description:** Load pretrained Mistral-7B-v0.1 model with validated hyperparameters from h-e1

**Acceptance Criteria:**
- Load Mistral-7B-v0.1 from HuggingFace (`mistralai/Mistral-7B-v0.1`)
- Configure for inference: torch.bfloat16, device_map="auto"
- Set temperature=0.7, K=10 sampling (from h-e1)
- Verify model loads successfully and can generate text

**Dependencies:** transformers, torch

**Model Specification:**
- **Architecture:** Mistral-7B-v0.1 (decoder-only transformer)
- **Parameters:** 7B
- **Precision:** bfloat16
- **Context Length:** 8192 tokens
- **Sampling:** Temperature=0.7, top-p=0.9, K=10 samples per question

---

### FR-3: Semantic Entropy Implementation
**Priority:** P0 (Critical)  
**Description:** Implement semantic entropy method following Kuhn et al. 2023 specification

**Acceptance Criteria:**
- Generate K=10 answers per question with temperature=0.7
- Embed answers using sentence-transformers (`all-MiniLM-L6-v2`)
- Cluster embeddings using agglomerative clustering (distance_threshold=0.5)
- Compute entropy over semantic clusters: H = -Σ p(c) log p(c)
- Return entropy score for each question

**Dependencies:** sentence-transformers, sklearn.cluster.AgglomerativeClustering, numpy

**Algorithm Reference:**
```python
# Kuhn et al. 2023: github.com/lorenzkuhn/semantic_uncertainty
# 1. Sample K answers → 2. Embed → 3. Cluster → 4. Entropy
```

**Output:** Array of 100 entropy scores (one per question)

---

### FR-4: Self-Consistency Implementation
**Priority:** P0 (Critical)  
**Description:** Implement self-consistency method following Wang et al. 2022 specification

**Acceptance Criteria:**
- Generate K=10 diverse answers per question with temperature=0.7
- Apply majority voting to find most common answer
- Compute agreement score: frequency of majority answer / K
- Return agreement score for each question (high agreement = low uncertainty)

**Dependencies:** collections.Counter, numpy

**Algorithm Reference:**
```python
# Wang et al. 2022: github.com/dj-sorry/self_consistency
# 1. Sample K answers → 2. Majority vote → 3. Agreement = count_max / K
```

**Output:** Array of 100 agreement scores (one per question)

---

### FR-5: Token Variance Implementation
**Priority:** P0 (Critical)  
**Description:** Implement token-level variance method based on ToKUR framework

**Acceptance Criteria:**
- For each question, collect token probability distributions across K=10 samples
- Compute variance of token probabilities across samples
- Aggregate token-level variances (mean across vocabulary)
- Return variance score for each question

**Dependencies:** torch, numpy

**Algorithm Reference:**
```python
# ToKUR framework (arXiv:2505.11737)
# 1. Get logits for K samples → 2. Softmax → 3. Variance across samples
```

**Output:** Array of 100 variance scores (one per question)

---

### FR-6: Verbalized Confidence Implementation
**Priority:** P0 (Critical)  
**Description:** Implement verbalized confidence elicitation following VCE methodology

**Acceptance Criteria:**
- Prompt model with: "{question}\n\nProvide your answer and confidence (0-100%):"
- Extract numeric confidence from response using regex
- Parse percentage value and normalize to [0, 1]
- Return confidence score for each question (high confidence = low uncertainty)

**Dependencies:** re (regex), transformers

**Algorithm Reference:**
```python
# VCE methodology (arXiv:2306.13063)
# 1. Prompt for answer + confidence → 2. Extract percentage → 3. Normalize
```

**Output:** Array of 100 confidence scores (one per question)

---

### FR-7: Correlation Analysis
**Priority:** P0 (Critical)  
**Description:** Compute pairwise Pearson correlation matrix for all four methods

**Acceptance Criteria:**
- Collect scores from all four methods (4 × 100 arrays)
- Compute Pearson correlation for all 6 method pairs
- Generate 4×4 correlation matrix (symmetric with diagonal = 1.0)
- Verify all off-diagonal correlations < 0.7 (gate condition)

**Dependencies:** scipy.stats.pearsonr, numpy

**Correlation Pairs:**
1. semantic_entropy × self_consistency
2. semantic_entropy × token_variance
3. semantic_entropy × verbalized_confidence
4. self_consistency × token_variance
5. self_consistency × verbalized_confidence
6. token_variance × verbalized_confidence

**Output:** 4×4 correlation matrix saved to `{hypothesis_folder}/results/correlation_matrix.npy`

---

### FR-8: Visualization Generation
**Priority:** P0 (Critical)  
**Description:** Generate correlation heatmap and additional analysis plots

**Acceptance Criteria:**
- **Mandatory:** 4×4 correlation heatmap with diverging colormap, annotated values, 0.7 threshold line
- **Additional:** Method distribution plots, scatter matrix, ranking comparison
- Save all figures to `{hypothesis_folder}/figures/`
- Use publication-quality formatting (300 DPI, readable fonts)

**Dependencies:** matplotlib, seaborn, numpy

**Figure Specifications:**
- `correlation_heatmap.png`: 8×8 inches, diverging colormap (RdBu_r), annot=True
- `method_distributions.png`: 2×2 subplot grid, histograms with KDE
- `scatter_matrix.png`: 6-panel pairwise scatter plots
- `dimension_analysis.png`: PCA/t-SNE visualization (optional)

---

### FR-9: Results Logging and Reporting
**Priority:** P0 (Critical)  
**Description:** Log all method scores, correlation matrix, and gate verification

**Acceptance Criteria:**
- Save individual method scores to CSV: `{hypothesis_folder}/results/method_scores.csv`
- Log correlation matrix with p-values
- Print gate verification: "PASS" if all correlations < 0.7, else "FAIL"
- Generate summary report with key statistics

**Dependencies:** pandas, numpy, logging

**Output Files:**
- `method_scores.csv`: 100 rows × 4 columns (one per method)
- `correlation_results.json`: Correlation matrix + p-values + gate status
- `experiment_log.txt`: Timestamped execution log

---

### FR-10: Reproducibility Infrastructure
**Priority:** P1 (High)  
**Description:** Ensure full reproducibility with seed control and logging

**Acceptance Criteria:**
- Set random seeds: `torch.manual_seed(42)`, `np.random.seed(42)`
- Log all hyperparameters to config file
- Save model/dataset versions
- Enable deterministic GPU operations

**Dependencies:** torch, numpy, random

**Configuration File:**
```yaml
# config.yaml
experiment_id: h-m1
model: mistralai/Mistral-7B-v0.1
dataset: google-research-datasets/natural_questions
sample_size: 100
k_samples: 10
temperature: 0.7
seed: 42
methods: [semantic_entropy, self_consistency, token_variance, verbalized_confidence]
```

---

## Non-Functional Requirements

### NFR-1: Performance
- Dataset loading: < 2 minutes
- Model loading: < 5 minutes (single GPU)
- Inference per question: < 30 seconds (K=10 samples)
- Total experiment runtime: < 1 hour (100 questions × 4 methods)

### NFR-2: Resource Constraints
- GPU Memory: < 16 GB (single GPU, bfloat16 precision)
- Disk Space: < 20 GB (model + dataset + outputs)
- RAM: < 32 GB

### NFR-3: Code Quality
- Modular design: Separate class per uncertainty method
- Type hints for all functions
- Docstrings following NumPy style
- Unit tests for correlation computation (if time permits)

### NFR-4: Logging and Debugging
- Structured logging with timestamps
- Progress bars for long operations (tqdm)
- Debug mode for sample-level inspection
- Error handling for HuggingFace API failures

---

## Success Criteria

### Primary Success Metric
**Gate Condition:** All pairwise correlations < 0.7

**Verification:**
```python
correlation_matrix = compute_correlations(scores)
off_diagonal = correlation_matrix[~np.eye(4, dtype=bool)]
gate_pass = np.all(np.abs(off_diagonal) < 0.7)
```

### Secondary Success Metrics
1. All four methods successfully compute uncertainty scores for 100 questions
2. Method scores show variance (not all identical or constant)
3. Correlation heatmap clearly visualizes method relationships
4. Results align with research expectations (methods measure distinct dimensions)

### Failure Modes
- Any method fails to compute scores → Implementation error
- All correlations > 0.9 → Methods measure same signal (hypothesis fails)
- Correlations unstable across subsets → Insufficient sample size

---

## Dependencies and Constraints

### External Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| torch | ≥2.0.0 | Model inference |
| transformers | ≥4.30.0 | Mistral-7B loading |
| datasets | ≥2.12.0 | NaturalQuestions loading |
| sentence-transformers | ≥2.2.0 | Semantic embeddings |
| scikit-learn | ≥1.2.0 | Clustering |
| scipy | ≥1.10.0 | Correlation analysis |
| numpy | ≥1.24.0 | Numerical operations |
| pandas | ≥2.0.0 | Data management |
| matplotlib | ≥3.7.0 | Visualization |
| seaborn | ≥0.12.0 | Heatmap |

### Hardware Requirements
- GPU: NVIDIA GPU with ≥16 GB VRAM (e.g., V100, A100, RTX 3090)
- CPU: ≥8 cores (for data preprocessing parallelization)
- Storage: ≥20 GB free space

### Constraints from h-e1
- **Must reuse:** K=10, temperature=0.7, NaturalQuestions dataset, Mistral-7B-v0.1
- **Must not change:** Sampling strategy, embedding model for semantic entropy
- **Rationale:** Controlled experiment - only uncertainty methods vary

---

## Implementation Scope

### In Scope
- Four uncertainty method implementations
- Correlation analysis on 100 NaturalQuestions examples
- Visualization and reporting
- Gate verification

### Out of Scope
- Fine-tuning Mistral-7B (inference only)
- Testing on other datasets (TruthfulQA reserved for h-m2)
- Calibration analysis (not part of h-m1 hypothesis)
- Comparison with h-e1 ensemble baseline (already validated)

---

## Risk Assessment

### High-Priority Risks
1. **Semantic clustering diverges from Kuhn 2023:** Use official implementation or exact algorithm replication
2. **Verbalized confidence extraction fails:** Implement robust regex + fallback parsing
3. **GPU OOM with K=10 sampling:** Use gradient checkpointing or reduce batch size
4. **Correlations ≥ 0.7 (gate fails):** Document findings, proceed to EXPLORE routing per verification_state.yaml

### Mitigation Strategies
- **Risk 1:** Reference lorenzkuhn/semantic_uncertainty GitHub for exact clustering parameters
- **Risk 2:** Test VCE prompts on sample questions, validate extraction accuracy
- **Risk 3:** Monitor GPU memory, use `torch.cuda.empty_cache()` between batches
- **Risk 4:** Analyze correlation patterns, check if methods cluster into subgroups

---

## Validation Plan

### Unit-Level Validation
- Test each method on 5 sample questions
- Verify output ranges: entropy [0, ∞), agreement [0, 1], variance ≥ 0, confidence [0, 1]
- Check semantic clustering produces ≥ 1 cluster

### Integration Validation
- Run full pipeline on 10 questions (smoke test)
- Verify correlation computation produces symmetric 4×4 matrix
- Check all output files are created

### PoC Gate Validation
1. Code runs without error on 100 questions
2. All four methods return valid scores
3. Correlation matrix computed successfully
4. Gate condition evaluated: correlations < 0.7

---

## Deliverables

### Code Artifacts
1. `uncertainty_methods.py`: Four method implementations
2. `run_experiment.py`: Main experiment script
3. `config.yaml`: Hyperparameter configuration
4. `requirements.txt`: Dependency specifications

### Data Artifacts
1. `data/natural_questions_100.json`: Preprocessed dataset
2. `results/method_scores.csv`: All method scores
3. `results/correlation_matrix.npy`: Correlation matrix
4. `results/correlation_results.json`: Gate verification

### Visualization Artifacts
1. `figures/correlation_heatmap.png`: Mandatory heatmap
2. `figures/method_distributions.png`: Score distributions
3. `figures/scatter_matrix.png`: Pairwise scatter plots

### Documentation
1. `README.md`: Experiment overview and reproduction instructions
2. `experiment_log.txt`: Execution log with timestamps
3. `04_validation.md`: Results summary (generated in Phase 4)

---

## Timeline and Effort Estimate

**Note:** Per workflow rules, no time estimates provided. Implementation proceeds at natural pace through Phase 4.

**Task Sequence:**
1. Environment setup (dependencies, GPU check)
2. Dataset preparation (FR-1)
3. Model loading (FR-2)
4. Method implementations (FR-3, FR-4, FR-5, FR-6)
5. Correlation analysis (FR-7)
6. Visualization (FR-8)
7. Results logging (FR-9)
8. Validation and gate check

---

## Appendix: Research Sources

### Core Papers
- **Semantic Entropy:** Kuhn et al., "Semantic Uncertainty", ICLR 2023 ([arXiv:2302.09664](https://arxiv.org/abs/2302.09664))
- **Self-Consistency:** Wang et al., "Self-Consistency Improves Chain of Thought", ICLR 2023 ([arXiv:2203.11171](https://arxiv.org/abs/2203.11171))
- **Token Variance:** ToKUR framework ([arXiv:2505.11737](https://arxiv.org/html/2505.11737v1))
- **Verbalized Confidence:** VCE methodology ([arXiv:2306.13063](https://arxiv.org/html/arXiv:2306.13063))

### Implementation References
- [lorenzkuhn/semantic_uncertainty](https://github.com/lorenzkuhn/semantic_uncertainty)
- [dj-sorry/self_consistency](https://github.com/dj-sorry/self_consistency)
- [google-research-datasets/natural_questions](https://huggingface.co/datasets/google-research-datasets/natural_questions)
- [mistralai/Mistral-7B-v0.1](https://huggingface.co/mistralai/Mistral-7B-v0.1)

---

**Document Status:** ✅ Complete  
**Next Phase:** Architecture Design (Step 3)  
**Generated:** 2026-04-22 via Phase 3 Implementation Planning Workflow
