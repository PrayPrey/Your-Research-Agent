# Product Requirements Document: h-m1

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis:** Under factual prompts where memorization is expected, if reliability and robustness are measured on the same model outputs, then positive correlation r>0.3 (p<0.05) emerges, because shared training dynamics create correlations between factual correctness (reliability) and consistent retrieval (robustness) for memorized content.
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

This PRD specifies the implementation requirements for testing the h-m1 hypothesis, which examines the correlation between reliability and robustness metrics under factual prompts. The experiment will measure whether shared training dynamics in LLMs create predictable correlations between factual correctness (reliability) and consistent retrieval (robustness) for memorized content.

**Key Objectives:**
1. Generate model outputs on TruthfulQA factual stratum using Llama-2 models (7B, 13B, 70B)
2. Measure reliability via GPT-4-as-judge scoring
3. Measure robustness via paraphrase consistency
4. Compute Pearson correlation coefficients with statistical significance tests
5. Validate hypothesis: r > 0.3, p < 0.05

**Success Criteria:**
- Primary: Pearson r > 0.3, p < 0.05, 95% CI lower bound > 0.2
- Secondary: At least one model shows r > 0.4 (strong coupling)

---

## Problem Statement

### Background
Prior hypothesis h-e1 established that synchronized multi-dimensional trustworthiness measurements show sufficient variance (σ>0.2) for correlation analysis. Building on this foundation, h-m1 investigates the specific mechanism underlying reliability-robustness correlation on factual prompts.

### Research Question
Do factual prompts, where memorization is expected, show positive correlation between reliability (factual correctness) and robustness (consistent retrieval) due to shared training dynamics?

### Constraints
- Sample size: ~400 factual prompts from TruthfulQA
- Statistical power: α=0.05, target effect size r>0.3
- Prerequisite: h-e1 PASS (sufficient variance confirmed)

---

## Functional Requirements

### FR-1: Dataset Preparation
**Priority:** P0 (Critical)

Load and prepare TruthfulQA dataset:
- Source: HuggingFace `truthful_qa` (generation split)
- Total prompts: 817
- Filter: Extract factual stratum (~400 prompts based on question category)
- Preprocessing: Clean prompts, ensure consistent formatting
- Output: Filtered factual prompt dataset

**Acceptance Criteria:**
- Dataset loads successfully from HuggingFace
- Factual stratum filtering yields 350-450 prompts
- Prompts are deduplicated and valid

### FR-2: Model Loading
**Priority:** P0 (Critical)

Load Llama-2 chat models for generation:
- Models: meta-llama/Llama-2-7b-chat-hf, Llama-2-13b-chat-hf, Llama-2-70b-chat-hf
- Source: HuggingFace transformers
- Configuration: Use pretrained checkpoints as-is (no training)

**Acceptance Criteria:**
- All three models load successfully
- Tokenizers initialized correctly
- Models ready for inference

### FR-3: Output Generation
**Priority:** P0 (Critical)

Generate model outputs with controlled parameters:
- Temperature: 0.7
- top_p: 0.9
- max_tokens: 256
- seed: Fixed per prompt (for reproducibility)
- Total outputs: 3 models × ~400 prompts = ~1,200 samples

**Acceptance Criteria:**
- All outputs generated successfully
- Generation parameters match specification
- Outputs saved with prompt IDs for tracking

### FR-4: Paraphrase Generation for Robustness
**Priority:** P0 (Critical)

Generate paraphrased versions of each prompt for robustness measurement:
- Method: Back-translation (English → French → English)
- Tool: MarianMT or Google Translate API
- Validation: Pilot n=20 with semantic preservation check
- Re-generate outputs: Each model generates outputs for paraphrased prompts

**Acceptance Criteria:**
- Paraphrases maintain semantic meaning
- All ~400 prompts have paraphrased versions
- Model outputs generated for paraphrased prompts

### FR-5: Reliability Measurement
**Priority:** P0 (Critical)

Score reliability using GPT-4-as-judge:
- Metric: Binary correct/incorrect (0 or 1)
- Judge: OpenAI GPT-4 API
- Ground truth: TruthfulQA reference answers
- Output: np.array of shape (N,) with values in [0, 1]

**Acceptance Criteria:**
- GPT-4 API integration working
- Reliability scores computed for all ~1,200 outputs
- Scores saved with output IDs

### FR-6: Robustness Measurement
**Priority:** P0 (Critical)

Score robustness via paraphrase consistency:
- Metric: Cosine similarity between original and paraphrased output embeddings
- Embeddings: Sentence-transformers (e.g., all-MiniLM-L6-v2)
- Output: np.array of shape (N,) with values in [0, 1]

**Acceptance Criteria:**
- Embeddings computed for all outputs
- Cosine similarity scores in [0, 1] range
- Scores saved with output IDs

### FR-7: Correlation Analysis
**Priority:** P0 (Critical)

Compute Pearson correlation with statistical tests:
- Method: scipy.stats.pearsonr
- Per-model analysis: Separate correlation for each model size
- Confidence intervals: 95% CI via Fisher z-transform
- Permutation test: 1,000 random shuffles for null distribution

**Acceptance Criteria:**
- Pearson r computed for each model
- p-values calculated (two-tailed test)
- 95% confidence intervals computed
- Permutation test validates significance

### FR-8: Visualization Generation
**Priority:** P1 (High)

Generate figures for analysis:
1. **Gate Metrics Comparison** (mandatory): Target r>0.3 vs actual correlation bar chart
2. **Scatter Plot**: Reliability vs Robustness with regression line
3. **Distribution Plot**: Correlation values across 3 models
4. **Permutation Test Plot**: Observed r vs null distribution
5. **Confidence Interval Plot**: Forest plot with r ± 95% CI

**Acceptance Criteria:**
- All figures generated and saved to `docs/youra_research/h-m1/figures/`
- Figures include clear labels, legends, and statistical annotations

### FR-9: Validation Report Generation
**Priority:** P0 (Critical)

Generate 04_validation.md report:
- Hypothesis gate evaluation (MUST_WORK)
- Observed correlations vs success criteria
- Statistical test results
- Key findings summary
- Pass/Fail determination

**Acceptance Criteria:**
- Report follows Phase 4 validation template
- All metrics documented
- Clear gate evaluation result

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds must be fixed
- Generation parameters documented
- Dataset versions pinned

### NFR-2: Performance
- Total experiment runtime: Target < 4 hours on standard GPU
- Model inference: Batch processing where possible

### NFR-3: Data Quality
- Output validation: Check for empty or malformed generations
- Metric validation: Scores must be in expected ranges [0, 1]

### NFR-4: Statistical Rigor
- Significance level: α = 0.05
- Confidence intervals: 95%
- Permutation test iterations: 1,000

---

## Data Requirements

### Input Data
1. **TruthfulQA Dataset**
   - Source: HuggingFace `truthful_qa`
   - Split: generation
   - Size: 817 prompts (filter to ~400 factual)

2. **Llama-2 Models**
   - 7B variant: meta-llama/Llama-2-7b-chat-hf
   - 13B variant: meta-llama/Llama-2-13b-chat-hf
   - 70B variant: meta-llama/Llama-2-70b-chat-hf

### Output Data
1. **Generated Outputs**
   - Format: JSON with {prompt_id, model, output_text}
   - Location: `{hypothesis_folder}/outputs/`

2. **Metric Scores**
   - Format: CSV with columns [prompt_id, model, reliability, robustness]
   - Location: `{hypothesis_folder}/metrics/`

3. **Analysis Results**
   - Format: JSON with {model, r, p_value, ci_lower, ci_upper}
   - Location: `{hypothesis_folder}/results/correlation_results.json`

---

## Dependencies

### External Libraries
- transformers (HuggingFace)
- datasets (HuggingFace)
- scipy (statistical analysis)
- numpy (numerical computation)
- sentence-transformers (embeddings)
- openai (GPT-4 API)
- matplotlib/seaborn (visualization)

### External Services
- OpenAI API (GPT-4 for reliability scoring)
- HuggingFace Hub (dataset and model downloads)

### Environment
- Python 3.8+
- CUDA-capable GPU (recommended for 70B model)
- Minimum 80GB GPU memory for 70B model (or use model parallelism)

---

## Success Criteria

### Primary Success Criteria (Gate: MUST_WORK)
1. **Correlation Magnitude:** Pearson r > 0.3 for at least one model
2. **Statistical Significance:** p < 0.05 (two-tailed)
3. **Confidence Interval:** 95% CI lower bound > 0.2

### Secondary Success Criteria
1. At least one model shows r > 0.4 (strong coupling)
2. Correlation increases with model size (7B < 13B < 70B)
3. Permutation test confirms observed r exceeds 95th percentile of null distribution

### PoC Success Check
1. Code runs without errors
2. Observed correlation r > 0 (directional improvement over null hypothesis)

---

## Risks and Mitigation

### Risk 1: GPT-4 API Rate Limits
**Mitigation:** Implement exponential backoff, cache results, batch requests

### Risk 2: 70B Model Memory Requirements
**Mitigation:** Use model parallelism or cloud GPU with sufficient memory

### Risk 3: Paraphrase Quality
**Mitigation:** Pilot validation (n=20) with manual review, adjust method if needed

### Risk 4: Low Correlation (Hypothesis Failure)
**Mitigation:** Gate allows exploration of alternative mechanisms (retrieval quality, model calibration)

---

## Timeline and Milestones

**Phase 4 Implementation:** Estimated 2-4 hours development + 2-4 hours execution

1. **Environment Setup** (30 min)
   - Install dependencies
   - Configure API keys
   - Test model loading

2. **Data Preparation** (45 min)
   - Load TruthfulQA
   - Filter factual stratum
   - Generate paraphrases

3. **Output Generation** (1-2 hours)
   - Generate outputs for all models
   - Generate paraphrased outputs

4. **Metric Computation** (1-1.5 hours)
   - Reliability scoring (GPT-4)
   - Robustness scoring (embeddings)

5. **Analysis** (30 min)
   - Correlation computation
   - Statistical tests
   - Visualization generation

6. **Validation Report** (30 min)
   - Generate 04_validation.md
   - Gate evaluation

---

## Traceability

### Phase 2C Source
- File: `docs/youra_research/h-m1/02c_experiment_brief.md`
- Section references:
  - Dataset: Section "Dataset"
  - Models: Section "Models"
  - Training Protocol: Section "Training Protocol" (generation parameters)
  - Evaluation: Section "Evaluation"

### Prerequisite Results
- h-e1 validation: `docs/youra_research/h-e1/04_validation.md`
  - Reliability variance: σ=0.224 ✓
  - Robustness variance: σ=0.202 ✓

---

## Appendix: Phase 2C Key Items

**Extracted from 02c_experiment_brief.md:**

1. **Dataset:** TruthfulQA (factual stratum), ~400 prompts
2. **Models:** Llama-2-chat (7B, 13B, 70B)
3. **Evaluation Metrics:**
   - Primary: Pearson r (correlation)
   - Statistical: p-value, 95% CI
   - Validation: Permutation test
4. **Success Criteria:** r>0.3, p<0.05, CI>0.2
5. **Measurement Methods:**
   - Reliability: GPT-4-as-judge
   - Robustness: Paraphrase consistency (back-translation)
