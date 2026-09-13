# Product Requirements Document: H-E1 Confidence-Timeout Correlation Experiment

**Date:** 2026-04-20  
**Author:** Anonymous
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Status:** Planning

---

## Executive Summary

This PRD specifies the implementation requirements for validating the foundational hypothesis that LLM confidence derivatives (std dev of softmax entropy) correlate with proof timeout outcomes in neural theorem proving. The experiment uses LeanDojo ReProver on 100 extended-timeout experiments (300s per theorem) to test whether confidence instability predicts non-termination (r > 0.3 OR ρ > 0.3).

**Success Criteria:** Correlation coefficient r > 0.3 OR ρ > 0.3 (MUST_WORK gate)

---

## Problem Statement

### Research Question
Can LLM confidence trajectories predict proof search non-termination in neural theorem proving?

### Hypothesis
Under neural theorem proving with LeanDojo ReProver, if we extract confidence derivatives (std dev of softmax entropy) from the first 15 proof steps, then these derivatives correlate with eventual timeout outcomes (r > 0.3), because confidence instability reflects the model's uncertainty about unfamiliar proof states.

### Gate Condition
- **Type:** MUST_WORK
- **Pass:** r > 0.3 OR ρ > 0.3
- **Fail:** STOP entire hypothesis chain

### Experiment Type
EXISTENCE (PoC) - No training required, evaluation-only on pre-trained model

---

## Functional Requirements

### FR-1: Dataset Management
**Priority:** CRITICAL

**Requirements:**
- Load LeanDojo Benchmark dataset (98,734 theorems from Lean mathlib)
- Randomly sample 100 theorems from test set
- Use fixed random seed for reproducibility
- Verify dataset integrity and theorem accessibility

**Source:** Yang et al., 2023 - https://github.com/lean-dojo/LeanDojo

**Implementation Details:**
```python
from lean_dojo import LeanGitRepo, Theorem
# Load benchmark theorems
repo = LeanGitRepo("https://github.com/leanprover-community/mathlib", "commit_hash")
theorems = load_benchmark_theorems()
# Random sample with seed
np.random.seed(42)
sample_theorems = np.random.choice(test_theorems, 100, replace=False)
```

### FR-2: Baseline Model Evaluation
**Priority:** CRITICAL

**Requirements:**
- Load pre-trained LeanDojo ReProver (ByT5-based retrieval-augmented transformer)
- Baseline performance: 48.9% success rate on held-out theorems
- No fine-tuning or modifications to base model
- Run proof search with extended timeout (300s per theorem, 100× normal budget)

**Configuration:**
- Model: ByT5 encoder-decoder transformer
- Retrieval: Dense retrieval for premise selection
- Search: Best-first search strategy
- Default step limit: 30 steps (≈3s) → Extended to 300s

**Source:** Yang et al., 2023 - https://github.com/lean-dojo/LeanDojo

**Loading:**
```python
from lean_dojo import Dojo, LeanGitRepo
repo = LeanGitRepo(url, commit)
dojo = Dojo(theorem)
```

### FR-3: Confidence Trajectory Extraction
**Priority:** CRITICAL

**Requirements:**
- Extract softmax probabilities from get_tactics() during proof search
- Compute Shannon entropy for each proof step
- Track entropy values for first 15 proof steps
- Calculate confidence derivative (std dev of entropy trajectory)
- Non-invasive monitoring (no changes to proof search process)

**Pseudo-code:**
```python
class ConfidenceTrajectoryExtractor:
    def __init__(self, window_size=15):
        self.window_size = window_size
    
    def extract_confidence_trajectory(self, proof_search_session):
        entropies = []
        for step_num in range(self.window_size):
            tactics_with_probs = proof_search_session.get_tactics()
            probs = np.array([np.exp(logprob) for _, logprob in tactics_with_probs])
            probs = probs / probs.sum()  # Normalize
            step_entropy = entropy(probs)
            entropies.append(step_entropy)
            if proof_search_session.is_done():
                break
        confidence_derivative = np.std(entropies)
        return confidence_derivative, entropies
```

### FR-4: Experiment Execution
**Priority:** CRITICAL

**Requirements:**
- Run 100 extended-timeout experiments (300s per theorem)
- Extract confidence derivatives for each theorem
- Label outcomes: success (0) vs. timeout (1) at 300s
- Store results: theorem_id, confidence_derivative, outcome, execution_time

**Ground Truth:**
- Success: Proof completes within 300s
- Timeout: Proof does not complete within 300s (proxy for non-termination)

### FR-5: Correlation Analysis
**Priority:** CRITICAL

**Requirements:**
- Compute Pearson correlation (r) between confidence derivatives and timeout labels
- Compute Spearman correlation (ρ) for rank-based robustness
- Calculate p-values for statistical significance
- Binary classification metrics (supplementary): ROC-AUC

**Libraries:**
```python
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import roc_auc_score

r, p_value_r = pearsonr(confidence_derivatives, timeout_labels)
rho, p_value_rho = spearmanr(confidence_derivatives, timeout_labels)
auc = roc_auc_score(timeout_labels, confidence_derivatives)
```

**Success Gate:** r > 0.3 OR ρ > 0.3

### FR-6: Visualization Generation
**Priority:** HIGH

**Required Figures:**
1. **Gate Metrics Comparison** (MANDATORY): Bar chart showing target (r=0.3) vs actual correlation
2. **Scatter Plot**: Confidence derivative vs. timeout outcome (binary)
3. **Distribution Comparison**: Histograms for success vs. timeout groups
4. **Trajectory Examples**: Entropy time series for 2-3 successes and 2-3 timeouts
5. **ROC Curve**: Binary classification performance (supplementary)

**Output Location:** `{hypothesis_folder}/figures/`

**Requirements:**
- All figures auto-generated in experiment code
- High-resolution PNG format
- Clear labels and legends
- Saved with descriptive filenames

### FR-7: Results Logging
**Priority:** MEDIUM

**Requirements:**
- Save raw results to CSV: theorem_id, confidence_derivative, outcome, execution_time
- Log correlation metrics: r, ρ, p-values, AUC
- Generate summary statistics: mean/std of confidence derivatives by outcome
- Store experiment metadata: date, sample_size, timeout_budget, random_seed

**Output Files:**
- `results_raw.csv`
- `metrics_summary.json`
- `experiment_metadata.json`

---

## Non-Functional Requirements

### NFR-1: Performance
- **Execution Time:** ~8.3 hours total (100 theorems × 300s max + overhead)
- **Memory:** Sufficient for ByT5 model + 100 theorem batch
- **GPU:** Single GPU required for LeanDojo ReProver inference

### NFR-2: Reproducibility
- Fixed random seed for theorem sampling
- Deterministic proof search (if supported by LeanDojo)
- Version pinning: LeanDojo, numpy, scipy, sklearn
- Results stored with full experiment configuration

### NFR-3: Code Quality (Minimal - EXISTENCE tier)
- **Configuration:** Hardcoded or argparse (no YAML required)
- **Logging:** Print statements + CSV output
- **Testing:** Smoke test only (verify code runs end-to-end)
- **Error Handling:** Basic try-except for LeanDojo API calls

### NFR-4: Documentation
- Inline comments for complex entropy calculations
- README with usage instructions
- Clear output file descriptions

---

## Success Criteria

### Primary Success (MUST_WORK Gate)
- [ ] Pearson r > 0.3 OR Spearman ρ > 0.3
- [ ] p-value < 0.05 for statistical significance
- [ ] Code runs without errors

### Secondary Success
- [ ] Visual cluster separation in scatter plot
- [ ] Timeouts show higher confidence variance than successes
- [ ] All figures generated successfully

### Failure Conditions
- r < 0.3 AND ρ < 0.3 → STOP hypothesis chain, reassess approach
- Code does not run → Fix bugs, re-run
- Dataset inaccessible → Use alternative theorem proving dataset

---

## Dependencies

### External Dependencies
- **LeanDojo:** Official implementation (Yang et al., 2023)
  - Repository: https://github.com/lean-dojo/LeanDojo
  - Components: LeanGitRepo, Dojo, get_tactics()
  - Pre-trained ReProver model
- **LeanDojo Benchmark:** 98,734 theorems from Lean mathlib
- **Python Libraries:** numpy, scipy, sklearn, matplotlib

### Infrastructure
- **Compute:** Single GPU (CUDA-enabled)
- **Storage:** ~1GB for model + dataset + results
- **Environment:** Python 3.8+, CUDA support

### No Internal Dependencies
- This is a foundation hypothesis (no prerequisites)
- No baseline repository comparison required

---

## Data Specifications

### Input Data
- **Source:** LeanDojo Benchmark test set
- **Format:** Lean theorem objects via LeanDojo API
- **Sample Size:** 100 theorems (random sample)
- **Seed:** 42 (fixed for reproducibility)

### Output Data
- **Confidence Derivatives:** Float array (100 values)
- **Timeout Labels:** Binary array (100 values, 0=success, 1=timeout)
- **Execution Times:** Float array (100 values, seconds)
- **Entropy Trajectories:** List of float arrays (100 × up to 15 steps)

### Metrics Schema
```json
{
  "correlation_pearson": {"r": float, "p_value": float},
  "correlation_spearman": {"rho": float, "p_value": float},
  "classification_auc": float,
  "gate_result": "PASS" | "FAIL",
  "sample_size": 100,
  "timeout_budget_seconds": 300,
  "confidence_window_steps": 15
}
```

---

## Implementation Constraints

### Constraints
- **No Training:** Use pre-trained ReProver only (EXISTENCE experiment)
- **No Architectural Changes:** Non-invasive confidence extraction
- **Fixed Sample Size:** 100 theorems (statistically meaningful, not trivial)
- **Extended Timeout:** 300s per theorem (100× normal budget)
- **Single GPU:** Must use CUDA_VISIBLE_DEVICES for single GPU

### Assumptions
- LeanDojo API provides stable get_tactics() interface
- 300s timeout is sufficient proxy for non-termination
- First 15 proof steps capture early confidence patterns
- Pre-trained ReProver is accessible and functional

### Out of Scope
- Training or fine-tuning models
- Ablation studies (single experiment design)
- Comparison with other theorem provers
- Optimization for execution time

---

## Acceptance Criteria

### Code Execution
- [ ] Environment setup script runs successfully
- [ ] Dataset loads without errors
- [ ] ReProver model initializes correctly
- [ ] All 100 experiments complete (success or timeout)
- [ ] No crashes or unhandled exceptions

### Metrics Validation
- [ ] Correlation values computed correctly
- [ ] p-values reported
- [ ] AUC calculated (supplementary)
- [ ] Gate condition evaluated: PASS/FAIL

### Output Completeness
- [ ] All required figures generated
- [ ] CSV results file exists with 100 rows
- [ ] Metrics summary JSON exists
- [ ] Experiment metadata saved

### Gate Evaluation
- [ ] If r > 0.3 OR ρ > 0.3: Mark hypothesis as PASSED
- [ ] If r ≤ 0.3 AND ρ ≤ 0.3: Mark hypothesis as FAILED → STOP

---

## Timeline & Milestones

**Note:** EXISTENCE tier - lightweight implementation

- **Environment Setup:** Install LeanDojo, dependencies, verify GPU
- **Dataset Preparation:** Download benchmark, sample 100 theorems
- **Baseline Evaluation:** Run ReProver on sample, verify functionality
- **Confidence Extraction:** Implement ConfidenceTrajectoryExtractor
- **Experiment Execution:** Run 100 extended-timeout experiments (~8.3 hours)
- **Analysis:** Compute correlations, generate figures
- **Gate Evaluation:** Check r > 0.3 OR ρ > 0.3

---

## Traceability

| Specification | Source |
|--------------|--------|
| Dataset: LeanDojo Benchmark | Phase 2C experiment brief, Yang et al. 2023 |
| Model: LeanDojo ReProver | Phase 2C experiment brief, Yang et al. 2023 |
| Sample Size: 100 | Phase 2C extended-timeout protocol |
| Timeout: 300s | Phase 2C (100× normal 3s budget) |
| Confidence Window: 15 steps | Phase 2C specification |
| Metrics: r, ρ | Phase 2C gate condition |
| Pseudo-code: ConfidenceTrajectoryExtractor | Phase 2C Core Mechanism Implementation |

---

## Appendix: Reference Implementations

### LeanDojo Official Repository
- **URL:** https://github.com/lean-dojo/LeanDojo
- **Priority:** ⭐⭐⭐ HIGHEST (author's official implementation)
- **Key API:** get_tactics() returns [(tactic, logprob), ...]
- **Baseline Performance:** 48.9% success rate
- **Used For:** All baseline model specifications

### Phase 2C Experiment Brief
- **File:** h-e1/02c_experiment_brief.md
- **Used For:** All functional requirements, success criteria, experimental protocol

---

*Generated for Phase 3 Implementation Planning | Next: Architecture Design*
