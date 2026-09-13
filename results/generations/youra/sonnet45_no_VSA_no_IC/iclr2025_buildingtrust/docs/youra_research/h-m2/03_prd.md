# Product Requirements Document: H-M2 Coupling Generalization Validator

**Date:** 2026-08-19  
**Hypothesis:** H-M2 (MECHANISM - Generalization Breadth)  
**Version:** 1.0  
**Status:** Ready for Implementation

---

## Overview

### Purpose
Validate whether coupling between trustworthiness dimensions generalizes beyond the 2 pairs found in h-e1, by demonstrating ≥2 models exhibit ≥3 dimension pairs with medium-to-strong coupling (phi ≥ 0.3).

### Success Criteria
**Gate Condition (SHOULD_WORK):**
- ≥2 models show ≥3 dimension pairs with:
  - Phi coefficient ≥ 0.3 (medium effect size)
  - Bonferroni-adjusted p < 0.01

**Failure Acceptable:** SHOULD_WORK gate → Phase 5 eligibility NOT blocked

---

## Functional Requirements

### FR1: Data Acquisition
**Priority:** MUST  
**Description:** Download and cache TrustLLM dataset from Huggingface

**Acceptance Criteria:**
- Dataset downloaded to `h-m2_code/data/trustllm_cache/`
- 5 dimensions accessible: truthfulness, safety, fairness, robustness, privacy
- Sample sizes verified: truthfulness (~800), safety (~600), fairness (~500), robustness (~500), privacy (~676)
- Cache reused across models (no duplicate downloads)

---

### FR2: Stratified Sampling
**Priority:** MUST  
**Description:** Generate balanced 500-instance sample (100 per dimension × 5 dimensions)

**Acceptance Criteria:**
- Random seed = 42 (reproducibility)
- Stratified sampling within each dimension
- Same 500 instances used across all 3 models
- Sample saved to `h-m2_code/data/samples.csv`

---

### FR3: Model Evaluation
**Priority:** MUST  
**Description:** Evaluate 3 models (gpt-4-turbo, claude-3-5-sonnet, llama-3.1-70b-instruct) on 500 instances

**Acceptance Criteria:**
- API calls use `.env` credentials (OPENAI_API_KEY, ANTHROPIC_API_KEY, TOGETHER_API_KEY)
- Exponential backoff retry (max 3 retries) on API failures
- Binary labels (0/1) per dimension per model
- Progress logged every 50 instances
- Checkpoint saved every 50 instances (resume on failure)
- Results saved to `h-m2_code/results/model_labels_{model}.csv`

**Non-Functional:**
- API cost ≤ $5 (estimated $2.54)
- Runtime ≤ 70 minutes (parallel API calls, 10 concurrent requests)

---

### FR4: Phi Coefficient Computation
**Priority:** MUST  
**Description:** Compute phi coefficient for all 10 dimension pairs × 3 models = 30 tests

**Acceptance Criteria:**
- Use scipy.stats.chi2_contingency for chi-square test
- Phi = sqrt(chi2 / n) where n=500
- Validate expected cell counts ≥5 (chi-square assumption)
- Output: 30 rows (model, dim1, dim2, phi, p_value, table)
- Results saved to `h-m2_code/results/coupling_matrix.csv`

---

### FR5: Multiple Testing Correction
**Priority:** MUST  
**Description:** Apply Bonferroni correction for 30 tests

**Acceptance Criteria:**
- Use statsmodels.stats.multitest.multipletests
- Method: 'bonferroni'
- Alpha: 0.01
- Adjusted alpha: 0.01/30 ≈ 0.000333
- Output: p_adjusted, reject (boolean array)
- Results appended to coupling_matrix.csv

**Optional:**
- Bonferroni-Holm sensitivity analysis (less conservative)

---

### FR6: Pair Counting
**Priority:** MUST  
**Description:** Count significant pairs per model

**Acceptance Criteria:**
- Count pairs with phi ≥ 0.3 AND p_adjusted < 0.01
- Output: {model_name: pair_count} dictionary
- Identify specific dimension pairs meeting criteria per model
- Results saved to `h-m2_code/results/summary_stats.json`

---

### FR7: Gate Evaluation
**Priority:** MUST  
**Description:** Determine PASS/FAIL for SHOULD_WORK gate

**Acceptance Criteria:**
- Count models with ≥3 significant pairs
- Gate PASS if ≥2 models meet threshold
- Gate result logged with rationale
- Results saved to `h-m2_code/results/gate_result.json`

**Output Format:**
```json
{
  "gate": "SHOULD_WORK",
  "result": "PASS" | "FAIL",
  "models_meeting_threshold": 2,
  "pair_counts": {
    "gpt-4-turbo": 4,
    "claude-3-5-sonnet": 3,
    "llama-3.1-70b-instruct": 2
  },
  "significant_pairs_per_model": {
    "gpt-4-turbo": [
      ["truthfulness", "robustness"],
      ["fairness", "safety"],
      ...
    ]
  },
  "rationale": "2 models (gpt-4-turbo, claude-3-5-sonnet) show ≥3 pairs → PASS"
}
```

---

### FR8: Visualizations
**Priority:** SHOULD  
**Description:** Generate 4 publication-ready figures

**Figure 1: Coupling Heatmaps (3 plots)**
- One 5×5 heatmap per model
- Color scale: phi coefficient [0, 1]
- Annotations: phi values + significance stars (* p < 0.01)
- Files: `h-m2_code/figures/heatmap_{model}.png`

**Figure 2: Pair Count Bar Chart**
- X-axis: Model names
- Y-axis: Count of significant pairs (max 10)
- Horizontal line: Threshold (3 pairs)
- Colors: Green (≥3), Red (<3)
- File: `h-m2_code/figures/pair_counts.png`

**Figure 3: Effect Size Distribution**
- Violin plot: Phi distribution per model
- Overlay: Individual dimension pairs (scatter)
- Horizontal lines: 0.1, 0.3, 0.5 (effect size thresholds)
- File: `h-m2_code/figures/effect_size_distribution.png`

**Figure 4: Significance vs Effect Size Scatter**
- X-axis: Phi coefficient
- Y-axis: -log10(p_adjusted)
- Color: Model
- Shape: Significant (circle) vs Non-significant (triangle)
- Quadrant lines: phi=0.3, p=0.01
- File: `h-m2_code/figures/significance_scatter.png`

---

## Non-Functional Requirements

### NFR1: Reproducibility
- Fixed random seed (42) for all sampling
- Deterministic evaluation order (sorted by instance ID)
- All intermediate results logged to CSV/JSON
- Git-trackable outputs (no binary-only formats)

### NFR2: Error Handling
- API failures: Exponential backoff (1s, 2s, 4s), max 3 retries
- Checkpoint: Save progress every 50 instances
- Resume: Load checkpoint on script restart
- Validation: Assert expected cell counts ≥5 before accepting phi

### NFR3: Performance
- Parallel API calls: 10 concurrent requests per model
- Total runtime: ≤70 minutes (API-dominated)
- API cost: ≤$5

### NFR4: Code Quality
- Type hints for all functions
- Docstrings (Google style)
- Unit tests for phi_coefficient function
- Logging at INFO level (progress) and ERROR level (failures)

---

## Out of Scope

### Excluded from h-m2
- **Partial correlation analysis:** Not required for gate evaluation (h-m1 already validated difficulty control)
- **Baseline comparison:** Occurs at Phase 5 (not Phase 4)
- **New models:** Only 3 models (GPT-4, Claude 3.5, Llama 3.1) as specified in h-e1
- **Additional dimensions:** Only 5 TrustLLM dimensions (no MultiTrust or custom dimensions)

---

## Dependencies

### External APIs
- OpenAI API (gpt-4-turbo)
- Anthropic API (claude-3-5-sonnet)
- Together API (llama-3.1-70b-instruct)

### Python Libraries
```
datasets>=2.14.0          # Huggingface TrustLLM
scipy>=1.11.0             # chi2_contingency
numpy>=1.24.0
pandas>=2.0.0
statsmodels>=0.14.0       # multipletests
matplotlib>=3.7.0
seaborn>=0.12.0
openai>=1.0.0
anthropic>=0.18.0
together>=0.2.0
python-dotenv>=1.0.0
```

---

## Acceptance Checklist

**Data Pipeline:**
- [ ] TrustLLM dataset downloaded and cached
- [ ] 500 instances sampled (100 per dimension, seed=42)
- [ ] Same instances used across all 3 models

**Model Evaluation:**
- [ ] 1500 API calls completed (500 × 3 models)
- [ ] Binary labels generated (5 dimensions × 500 instances × 3 models)
- [ ] API cost ≤ $5

**Statistical Analysis:**
- [ ] 30 phi coefficients computed (10 pairs × 3 models)
- [ ] Bonferroni correction applied (α_adjusted ≈ 0.000333)
- [ ] Expected cell counts ≥5 validated for all 30 tables

**Gate Evaluation:**
- [ ] Pair counts per model computed
- [ ] Gate result determined (PASS/FAIL)
- [ ] Rationale documented in gate_result.json

**Visualizations:**
- [ ] 3 heatmaps generated (one per model)
- [ ] Pair count bar chart generated
- [ ] Effect size distribution plot generated
- [ ] Significance scatter plot generated

**Code Quality:**
- [ ] Unit tests pass for phi_coefficient function
- [ ] All results logged to CSV/JSON
- [ ] Reproducible (seed=42, deterministic order)

---

## Deliverables

1. **Code:** `h-m2_code/` directory with src/, scripts/, data/, results/, figures/
2. **Results:** coupling_matrix.csv, gate_result.json, summary_stats.json
3. **Visualizations:** 7 PNG files (3 heatmaps + 4 aggregate plots)
4. **Validation Report:** 04_validation.md (Phase 4 output)

---

**PRD Status:** COMPLETE  
**Next Step:** Architecture Design (03_architecture.md)
