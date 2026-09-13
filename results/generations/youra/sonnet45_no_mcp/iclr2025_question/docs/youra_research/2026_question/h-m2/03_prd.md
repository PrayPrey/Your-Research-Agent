---
stepsCompleted: [requirements-gathering, functional-requirements, non-functional-requirements, success-criteria]
status: completed
generatedAt: "2026-04-22T10:00:00Z"
hypothesis: h-m2
hypothesisType: MECHANISM
---

# Product Requirements Document: h-m2 - Error Type Signature Analysis

**Date:** 2026-04-22  
**Author:** Anonymous
**Hypothesis:** h-m2 (MECHANISM)  
**Version:** 1.0

---

## Executive Summary

This PRD specifies the implementation requirements for hypothesis h-m2, which analyzes whether different error types (knowledge gaps vs confident misconceptions) produce distinct uncertainty signatures when measured by semantic diversity and sampling agreement metrics.

**Key Objective:** Compare uncertainty signatures across two error types by measuring semantic diversity and sampling agreement on NaturalQuestions (knowledge gaps) versus TruthfulQA (confident misconceptions) datasets using Mistral-7B-v0.1.

**Success Gate:** SHOULD_WORK - Knowledge gaps show statistically significantly higher semantic diversity than misconceptions (p < 0.05)

---

## Problem Statement

### Research Question
Do different error types (knowledge gaps vs confident misconceptions) produce distinct uncertainty signatures that can be characterized by semantic diversity and sampling agreement patterns?

### Hypothesis Statement
Under comparison between NaturalQuestions (knowledge gaps) and TruthfulQA (confident misconceptions), if we measure semantic diversity and sampling agreement for correct vs incorrect answers, then knowledge gaps will show high semantic diversity + low agreement while confident misconceptions will show low diversity + high agreement on wrong answer, because different error types arise from different failure modes in the model.

### Context from Previous Work
- **h-e1 (COMPLETED - PASS):** Validated semantic entropy implementation with K=10 sampling, AUROC 0.78
- **h-m1 (COMPLETED - FAIL with SHOULD_WORK):** Validated semantic entropy and self-consistency implementations, optimized to K=5 sampling
- **Proven Components:** Semantic diversity (h-e1), sampling agreement (h-m1), Mistral-7B-v0.1 inference, NaturalQuestions dataset
- **Optimal Hyperparameters:** Temperature=0.7, K=5 samples, single GPU (~8GB VRAM)

---

## Functional Requirements

### FR-1: Dataset Preparation - NaturalQuestions (Knowledge Gaps)
**Priority:** P0 (Critical)  
**Description:** Load and preprocess NaturalQuestions dataset representing knowledge-gap errors

**Acceptance Criteria:**
- Load NaturalQuestions validation split from HuggingFace (`natural_questions`)
- Select 100 examples using shuffle(seed=42) for statistical comparison
- Extract question text for model input
- No additional preprocessing (direct text input to LLM)
- Save preprocessed dataset to hypothesis folder

**Dependencies:** HuggingFace datasets library

**Data Specification:**
- **Source:** `natural_questions` (HuggingFace)
- **Split:** validation
- **Sample Size:** 100 examples (minimum for statistical power)
- **Purpose:** Knowledge-gap error type (expected: high diversity, low agreement)
- **Format:** JSON with fields: question
- **Storage:** `{hypothesis_folder}/data/natural_questions_100.json`

**Loading Code:**
```python
from datasets import load_dataset
dataset_nq = load_dataset("natural_questions", split="validation")
dataset_nq = dataset_nq.shuffle(seed=42).select(range(100))
```

---

### FR-2: Dataset Preparation - TruthfulQA (Confident Misconceptions)
**Priority:** P0 (Critical)  
**Description:** Load and preprocess TruthfulQA dataset representing confident-misconception errors

**Acceptance Criteria:**
- Load TruthfulQA generation split from HuggingFace (`truthful_qa`, "generation" config)
- Select 100 examples using shuffle(seed=42) matching NaturalQuestions sample size
- Extract question text for model input
- No additional preprocessing (direct text input to LLM)
- Save preprocessed dataset to hypothesis folder

**Dependencies:** HuggingFace datasets library

**Data Specification:**
- **Source:** `truthful_qa` (HuggingFace, Lin et al. 2022)
- **Split:** validation
- **Sample Size:** 100 examples (matching NaturalQuestions)
- **Purpose:** Confident-misconception error type (expected: low diversity, high agreement on wrong answer)
- **Format:** JSON with fields: question, best_answer, correct_answers, incorrect_answers
- **Storage:** `{hypothesis_folder}/data/truthful_qa_100.json`

**Loading Code:**
```python
from datasets import load_dataset
dataset_tqa = load_dataset("truthful_qa", "generation", split="validation")
dataset_tqa = dataset_tqa.shuffle(seed=42).select(range(100))
```

---

### FR-3: Model Loading and Configuration
**Priority:** P0 (Critical)  
**Description:** Load pretrained Mistral-7B-v0.1 model with validated hyperparameters from h-m1

**Acceptance Criteria:**
- Load Mistral-7B-v0.1 from HuggingFace (`mistralai/Mistral-7B-v0.1`)
- Configure for inference: device_map="auto", torch_dtype="auto"
- Set temperature=0.7, K=5 sampling (optimized from h-m1)
- Verify model loads successfully on single GPU (~8GB VRAM)

**Dependencies:** transformers, torch

**Model Specification:**
- **Architecture:** Mistral-7B-v0.1 (decoder-only transformer)
- **Parameters:** 7B
- **Context Length:** 8192 tokens
- **Sampling Configuration:** Temperature=0.7, K=5 samples per question
- **Device:** CUDA (single GPU)

**Loading Code:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    device_map="auto",
    torch_dtype="auto"
)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
```

---

### FR-4: Answer Generation Pipeline
**Priority:** P0 (Critical)  
**Description:** Generate K=5 diverse answer samples per question for both datasets

**Acceptance Criteria:**
- For each question in NaturalQuestions (100) and TruthfulQA (100)
- Generate K=5 answer samples with temperature=0.7
- Use consistent prompt format across both datasets
- Store samples for subsequent diversity/agreement analysis
- Total: 200 questions × 5 samples = 1000 generated answers

**Dependencies:** transformers (model inference)

**Generation Specification:**
- **Samples per Question:** K=5
- **Temperature:** 0.7 (from h-m1 validation)
- **Top-p:** 0.9
- **Max Length:** 512 tokens
- **Batch Size:** 1 (sequential generation)
- **Seed:** 42 (reproducibility)

**Output:** Dictionary mapping question_id → List[5 answer strings]

---

### FR-5: Semantic Diversity Measurement
**Priority:** P0 (Critical)  
**Description:** Measure semantic diversity via entropy over semantic clusters (reused from h-e1)

**Acceptance Criteria:**
- For each question's K=5 samples, embed answers using sentence-transformers
- Use `all-MiniLM-L6-v2` model (validated in h-e1)
- Cluster embeddings with agglomerative clustering (distance_threshold=0.5)
- Compute entropy: H = -Σ p(c) log p(c) over cluster distribution
- Return diversity score for each question

**Dependencies:** sentence-transformers, sklearn.cluster.AgglomerativeClustering, numpy

**Algorithm Reference:**
```python
# From h-e1 validated implementation (Kuhn et al. 2023)
# 1. Embed K=5 answers → 2. Cluster semantically → 3. Compute entropy
def measure_semantic_diversity(samples, embedder):
    embeddings = embedder.encode(samples)
    clusters = agglomerative_clustering(embeddings, threshold=0.5)
    cluster_probs = count_clusters(clusters) / len(samples)
    entropy = -sum(p * log(p) for p in cluster_probs if p > 0)
    return entropy
```

**Output:**
- `nq_diversity_scores`: Array of 100 entropy scores (NaturalQuestions)
- `tqa_diversity_scores`: Array of 100 entropy scores (TruthfulQA)

---

### FR-6: Sampling Agreement Measurement
**Priority:** P0 (Critical)  
**Description:** Measure sampling agreement via majority voting rate (reused from h-m1)

**Acceptance Criteria:**
- For each question's K=5 samples, count frequency of most common answer
- Compute agreement rate: count_max / K
- High agreement = low diversity (confident on answer)
- Return agreement score for each question

**Dependencies:** collections.Counter, numpy

**Algorithm Reference:**
```python
# From h-m1 validated implementation (self-consistency)
# 1. Sample K=5 answers → 2. Majority vote → 3. Agreement = count_max / K
def measure_sampling_agreement(samples):
    from collections import Counter
    vote_counts = Counter(samples)
    most_common_count = vote_counts.most_common(1)[0][1]
    agreement_rate = most_common_count / len(samples)
    return agreement_rate
```

**Output:**
- `nq_agreement_scores`: Array of 100 agreement rates (NaturalQuestions)
- `tqa_agreement_scores`: Array of 100 agreement rates (TruthfulQA)

---

### FR-7: Statistical Comparison Analysis
**Priority:** P0 (Critical)  
**Description:** Perform statistical tests to compare diversity and agreement across error types

**Acceptance Criteria:**
- Compute mean semantic diversity for NaturalQuestions and TruthfulQA
- Compute mean sampling agreement for NaturalQuestions and TruthfulQA
- Perform independent samples t-test on diversity scores (NQ vs TQA)
- Perform independent samples t-test on agreement scores (NQ vs TQA)
- Check significance: p < 0.05
- Verify gate condition: NQ diversity > TQA diversity (statistically significant)

**Dependencies:** scipy.stats.ttest_ind, numpy

**Statistical Tests:**
1. **Diversity Comparison:** t-test(nq_diversity, tqa_diversity)
2. **Agreement Comparison:** t-test(nq_agreement, tqa_agreement)

**Gate Validation:**
```python
from scipy.stats import ttest_ind
import numpy as np

diversity_ttest = ttest_ind(nq_diversity_scores, tqa_diversity_scores)
gate_pass = (diversity_ttest.pvalue < 0.05) and 
            (np.mean(nq_diversity_scores) > np.mean(tqa_diversity_scores))
```

**Output:** Statistical results saved to `{hypothesis_folder}/results/statistical_comparison.json`

---

### FR-8: Visualization Generation
**Priority:** P1 (High)  
**Description:** Generate visualizations to illustrate error type signature differences

**Acceptance Criteria:**
- **Mandatory Figure:** Gate metrics comparison (target vs actual bar chart)
- **Box Plots:** Diversity distribution comparison (NQ vs TQA)
- **Box Plots:** Agreement distribution comparison (NQ vs TQA)
- **Scatter Plot:** Diversity vs Agreement (2D signature space, colored by error type)
- Save all figures to `{hypothesis_folder}/figures/`

**Dependencies:** matplotlib, seaborn

**Figures:**
1. `gate_metrics_comparison.png` - Bar chart showing NQ vs TQA diversity means
2. `diversity_distribution.png` - Box plot comparing diversity distributions
3. `agreement_distribution.png` - Box plot comparing agreement distributions
4. `signature_space_2d.png` - Scatter plot showing error type clustering

**Optional Figure:**
5. `sample_answers_qualitative.png` - Example K=5 samples showing diversity difference

---

## Non-Functional Requirements

### NFR-1: Performance
**Requirement:** Complete experiment execution within reasonable time for PoC validation  
**Target:** < 2 hours total runtime
- Dataset loading: < 5 minutes
- Answer generation: < 60 minutes (200 questions × 5 samples)
- Metric computation: < 10 minutes
- Visualization: < 5 minutes

**Rationale:** K=5 sampling (reduced from K=10 in h-m1) for faster iteration while maintaining statistical validity

---

### NFR-2: Reproducibility
**Requirement:** All results must be reproducible with fixed seeds  
**Implementation:**
- Dataset shuffle: `seed=42`
- Model generation: `seed=42`
- Random operations: `numpy.random.seed(42)`, `torch.manual_seed(42)`

**Verification:** Running experiment twice produces identical results

---

### NFR-3: Code Reusability
**Requirement:** Reuse validated implementations from h-e1 and h-m1  
**Components:**
- Semantic diversity: h-e1 validated code
- Sampling agreement: h-m1 validated code
- Model loading: h-m1 validated code
- NaturalQuestions loading: h-e1 validated code

**Rationale:** Minimize new code, reduce implementation risk, leverage proven components

---

### NFR-4: Resource Constraints
**Requirement:** Single GPU execution with ~8GB VRAM  
**Configuration:**
- Model precision: Use `torch_dtype="auto"` for optimal memory usage
- Batch size: 1 (sequential generation)
- Device: Single GPU via `CUDA_VISIBLE_DEVICES`

**Verification:** Monitor GPU memory with `nvidia-smi` during execution

---

### NFR-5: Data Storage
**Requirement:** Organize outputs in hypothesis folder structure  
**Directory Structure:**
```
h-m2/
├── data/
│   ├── natural_questions_100.json
│   ├── truthful_qa_100.json
│   └── generated_answers.json
├── results/
│   ├── nq_diversity_scores.npy
│   ├── tqa_diversity_scores.npy
│   ├── nq_agreement_scores.npy
│   ├── tqa_agreement_scores.npy
│   └── statistical_comparison.json
└── figures/
    ├── gate_metrics_comparison.png
    ├── diversity_distribution.png
    ├── agreement_distribution.png
    └── signature_space_2d.png
```

---

## Success Criteria

### Primary Success Criterion (Gate Condition)
**SHOULD_WORK Gate:** Knowledge gaps show statistically significantly higher diversity than misconceptions

**Quantitative Metrics:**
- **Statistical Test:** Independent samples t-test
- **Significance Threshold:** p < 0.05
- **Directional Requirement:** mean(nq_diversity) > mean(tqa_diversity)

**Pass Condition:**
```python
gate_pass = (diversity_pvalue < 0.05) and (nq_diversity_mean > tqa_diversity_mean)
```

---

### Secondary Success Criteria

**SC-1: Agreement Inverse Relationship**
- **Expected:** TruthfulQA shows higher agreement than NaturalQuestions
- **Measurement:** mean(tqa_agreement) > mean(nq_agreement)
- **Rationale:** Confident misconceptions converge on wrong answer

**SC-2: PoC Validation**
- **Requirement:** Code runs without error
- **Requirement:** Generates all required outputs (data, results, figures)
- **Requirement:** Correct directional difference (even if not statistically significant)

**SC-3: Visualization Quality**
- **Requirement:** All mandatory figures generated
- **Requirement:** Clear visual separation between error types in plots
- **Requirement:** Gate metrics comparison shows expected pattern

---

## Dependencies

### External Libraries
- `transformers` (HuggingFace) - Model loading and inference
- `datasets` (HuggingFace) - Dataset loading (NaturalQuestions, TruthfulQA)
- `sentence-transformers` - Semantic embedding for diversity measurement
- `torch` - PyTorch for model execution
- `sklearn` - Agglomerative clustering
- `scipy` - Statistical tests (t-test)
- `numpy` - Numerical operations
- `matplotlib` - Visualization
- `seaborn` - Enhanced plotting (optional)

### Previous Hypotheses
- **h-e1:** Semantic diversity implementation, NaturalQuestions dataset loading
- **h-m1:** Sampling agreement implementation, optimized K=5 configuration

### Hardware Requirements
- **GPU:** Single CUDA-enabled GPU with ≥8GB VRAM
- **RAM:** ≥16GB system memory
- **Storage:** ~10GB for models and datasets

---

## Constraints and Assumptions

### Constraints
1. **Sample Size:** 100 examples per dataset (PoC scale, not full benchmark)
2. **Model:** Mistral-7B-v0.1 only (no model comparison)
3. **Metrics:** Two metrics only (semantic diversity, sampling agreement)
4. **Error Types:** Two categories only (knowledge gaps, confident misconceptions)

### Assumptions
1. **Dataset Validity:** NaturalQuestions represents knowledge gaps, TruthfulQA represents confident misconceptions
2. **Metric Validity:** Semantic entropy captures diversity, self-consistency captures agreement
3. **Statistical Power:** 100 samples per dataset sufficient for t-test with α=0.05
4. **Component Reusability:** h-e1 and h-m1 implementations transfer correctly to h-m2

---

## Risks and Mitigation

### R-1: Error Type Overlap
**Risk:** Datasets may not cleanly separate into knowledge gaps vs misconceptions  
**Mitigation:** Analyze verbalized confidence distribution to verify partition reliability  
**Severity:** MEDIUM

### R-2: Statistical Power
**Risk:** 100 samples may be insufficient for detecting small effect sizes  
**Mitigation:** Use directional test (one-tailed), focus on PoC validation not production claims  
**Severity:** LOW (SHOULD_WORK gate allows failure with insights)

### R-3: Implementation Divergence
**Risk:** Reused code from h-e1/h-m1 may not work correctly in h-m2 context  
**Mitigation:** Unit test each component independently before integration  
**Severity:** MEDIUM

### R-4: TruthfulQA Dataset Loading
**Risk:** New dataset (not used in h-e1/h-m1), loading code unvalidated  
**Mitigation:** Test dataset loading separately, verify HuggingFace access  
**Severity:** HIGH (new component)

---

## Acceptance Testing

### Test Case 1: Dataset Loading
**Input:** Load NaturalQuestions and TruthfulQA  
**Expected Output:** Two datasets with 100 examples each, question text extracted  
**Pass Criteria:** Files saved to `data/` folder, no loading errors

### Test Case 2: Model Inference
**Input:** Single question from NaturalQuestions  
**Expected Output:** 5 diverse answer samples with temperature=0.7  
**Pass Criteria:** Answers generated, length within bounds, no CUDA errors

### Test Case 3: Semantic Diversity
**Input:** 5 sample answers for one question  
**Expected Output:** Single entropy score (float > 0)  
**Pass Criteria:** Score computed, matches h-e1 implementation behavior

### Test Case 4: Sampling Agreement
**Input:** 5 sample answers for one question  
**Expected Output:** Single agreement rate (float in [0, 1])  
**Pass Criteria:** Score computed, matches h-m1 implementation behavior

### Test Case 5: Statistical Comparison
**Input:** nq_diversity_scores (100) and tqa_diversity_scores (100)  
**Expected Output:** t-test result with p-value and means  
**Pass Criteria:** p-value < 0.05, nq_mean > tqa_mean (gate condition)

### Test Case 6: End-to-End Execution
**Input:** Run full experiment script  
**Expected Output:** All outputs generated (data, results, figures), gate result reported  
**Pass Criteria:** No errors, outputs exist, gate condition evaluated

---

## Implementation Notes

### Code Organization
```
h-m2/code/
├── data_loader.py          # FR-1, FR-2: Dataset loading
├── model_loader.py         # FR-3: Model configuration
├── answer_generator.py     # FR-4: Sampling pipeline
├── semantic_diversity.py   # FR-5: Diversity measurement (from h-e1)
├── sampling_agreement.py   # FR-6: Agreement measurement (from h-m1)
├── statistical_analysis.py # FR-7: Comparison tests
├── visualizer.py          # FR-8: Figure generation
└── main.py                # Orchestration script
```

### Execution Order
1. Load datasets (NaturalQuestions, TruthfulQA)
2. Load model (Mistral-7B-v0.1)
3. Generate K=5 answers per question (200 questions total)
4. Compute diversity scores (200 values)
5. Compute agreement scores (200 values)
6. Perform statistical tests (t-tests)
7. Generate visualizations (4-5 figures)
8. Report gate condition result

---

## Appendix: Metrics Specification

### Semantic Diversity (Entropy)
- **Range:** [0, ∞), typically [0, 3] for K=5
- **Interpretation:** Higher = more diverse answers
- **Formula:** H = -Σ p(c) log p(c), where c = semantic clusters
- **Expected:** NQ > TQA

### Sampling Agreement (Majority Rate)
- **Range:** [0, 1]
- **Interpretation:** Higher = more agreement (lower diversity)
- **Formula:** agreement = max_count / K, where K=5
- **Expected:** TQA > NQ (inverse of diversity)

### Statistical Significance
- **Test:** Independent samples t-test (two-tailed)
- **Null Hypothesis:** No difference in mean diversity between NQ and TQA
- **Alternative:** NQ mean diversity > TQA mean diversity
- **Threshold:** α = 0.05

---

*Generated by Phase 3 Implementation Planning Workflow*  
*Based on Phase 2C Experiment Brief (02c_experiment_brief.md)*  
*Next Phase: Phase 3 Step 3 - Architecture Design*
