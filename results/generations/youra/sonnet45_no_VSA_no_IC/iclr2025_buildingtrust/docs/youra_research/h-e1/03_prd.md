# Product Requirements Document: H-E1

**Date:** 2026-08-19
**Hypothesis:** At least one model exhibits statistically significant coupling (phi ≥ 0.3, p < 0.01) for at least one dimension pair
**Type:** EXISTENCE (PoC)
**Author:** Anonymous

---

## Executive Summary

Implement statistical analysis system to test behavioral coupling across LLM trustworthiness dimensions. System evaluates 3 API-based models (GPT-4, Claude 3, Llama 3) on MultiTrust benchmark (500 instances) and computes phi coefficients for 10 dimension pairs. Success: ≥1 model shows ≥1 pair with phi ≥ 0.3, p < 0.01.

---

## Problem Statement

No prior work measures cross-dimension coupling in LLM trustworthiness evaluation. Standard frameworks (MultiTrust, TrustLLM) evaluate dimensions independently. This experiment tests whether trustworthiness dimensions exhibit statistically significant behavioral coupling.

---

## Functional Requirements

### FR1: Dataset Loading
- Load MultiTrust dataset from HuggingFace (thu-ml/MultiTrust)
- Extract 500 instances per model
- Parse 5 dimensions: truthfulness, robustness, fairness, safety, privacy
- Generate binary pass/fail labels per dimension

### FR2: API Model Evaluation
- Integrate 3 API endpoints:
  - GPT-4 via OpenAI API
  - Claude 3 via Anthropic API
  - Llama 3 via Together AI/Replicate
- Fixed config: temperature=0.0, max_tokens=512, seed=42
- Batch processing with rate limit handling (batch_size=10)

### FR3: Coupling Analysis
- Construct 10 pairwise 2×2 contingency tables per model
- Compute phi coefficient using scipy.stats.chi2_contingency
- Compute chi-square p-values
- Verify via sklearn.metrics.matthews_corrcoef

### FR4: Results Output
- Generate coupling heatmap (5×5 matrix per model)
- Generate significance scatter plot (phi vs p-value)
- Save results to CSV: model, dim1, dim2, phi, p_value
- Generate figures to h-e1/figures/

---

## Non-Functional Requirements

### NFR1: Reproducibility
- Fixed random seed (42)
- Deterministic API calls (temperature=0.0)
- Version pinning: scipy≥1.11.0, sklearn≥1.3.0

### NFR2: API Cost Control
- Batch size = 10 (rate limit compliance)
- 500 instances × 3 models = 1500 API calls total
- Estimated cost: ~$15 (GPT-4 dominant)

### NFR3: Execution Time
- API calls: ~30-45 minutes (rate limited)
- Statistical analysis: <1 minute
- Total runtime: ~45-60 minutes

---

## Data Specifications

### Input Data
- **Dataset:** MultiTrust (HuggingFace)
- **Format:** JSON with text prompts + dimension labels
- **Size:** 500 instances per model
- **Dimensions:** 5 (truthfulness, robustness, fairness, safety, privacy)

### Output Data
- **Results file:** h-e1/results/coupling_results.csv
- **Figures:** h-e1/figures/heatmap_{model}.png, h-e1/figures/significance_scatter.png
- **Logs:** h-e1/logs/experiment.log

---

## Success Criteria

### Gate Condition (MUST_WORK)
- ≥1 model shows ≥1 dimension pair with:
  - phi ≥ 0.3 (medium effect size)
  - p < 0.01 (statistical significance)

### Mechanism Verification
- Log contains "Computing phi coefficient" for all 10 pairs
- All phi values ∈ [0, 1]
- All p-values ∈ [0, 1]
- Contingency tables constructed for all pairs

---

## Dependencies

### Python Libraries
- scipy >= 1.11.0 (chi2_contingency)
- sklearn >= 1.3.0 (matthews_corrcoef)
- numpy >= 1.24.0
- pandas >= 2.0.0
- matplotlib >= 3.7.0
- huggingface_hub >= 0.16.0

### API Access
- OpenAI API key (GPT-4)
- Anthropic API key (Claude 3)
- Together AI/Replicate API key (Llama 3)

### Hardware
- No GPU required (API-based evaluation)
- Minimal RAM: 4GB
- Storage: ~100MB (dataset + results)

---

## Out of Scope

- Training new models (statistical analysis only)
- Internal state analysis (API-only evaluation)
- >3 model families (budget constraint)
- >5 dimensions (MultiTrust scope)
- Causal analysis (correlation only)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits | Execution delay | Batch size = 10, exponential backoff |
| API cost overrun | Budget | Fixed sample size (500), cost estimate upfront |
| Insufficient coupling | MUST_WORK failure | Expected based on literature (0.20-0.49 correlation range) |
| Invalid chi-square | Statistical error | Verify ≥5 observations per cell before test |

---

## Appendix: Phase 2C Traceability

| Requirement | Phase 2C Source |
|-------------|-----------------|
| Dataset selection | MultiTrust (02c_experiment_brief.md:167-189) |
| Baseline models | GPT-4, Claude 3, Llama 3 (02c_experiment_brief.md:195-233) |
| Sample size (500) | Phase 2B specification (02c_experiment_brief.md:187) |
| Phi coefficient | scipy implementation (02c_experiment_brief.md:68-84) |
| Success criteria | phi ≥ 0.3, p < 0.01 (02c_experiment_brief.md:323-327) |

---

**Status:** Draft
**Next Phase:** Phase 3 - Architecture (Epic tasks, module structure)
