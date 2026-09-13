---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: Phase 3 - Implementation Planning
generated: 2026-05-11
status: COMPLETE
---

# Product Requirements Document (PRD)
## Hypothesis h-e1: Policy-Layer Capability Decoupling Validation

**Version:** 1.0  
**Date:** 2026-05-11  
**Author:** Anonymous
---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis h-e1: Policy-Layer Capability Decoupling. The experiment tests whether Constitutional AI or system-prompted LLMs can modulate compliance strength (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}) while maintaining invariant base capability metrics (MMLU, HumanEval). This is a MUST_WORK gate experiment with statistical rigor requirements (ICC > 0.95, ANOVA p > 0.05, Cohen's f < 0.10).

**Success Criteria:**
- ICC (Intraclass Correlation Coefficient) > 0.95 across all λ conditions
- One-way ANOVA p-value > 0.05 (no significant variation)
- Cohen's f effect size < 0.10 (negligible effect)

**Failure Action:** ABORT entire verification chain → Route to Phase 0 for architecture re-selection

---

## Problem Statement

### Research Question
Can base model capability remain invariant while policy-layer compliance strength is modulated across multiple levels?

### Hypothesis Statement
Under conditions where Constitutional AI or system-prompted LLMs are evaluated across multiple compliance strength levels (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}), if base model capability is held frozen while policy-layer rules are varied, then base capability metrics (MMLU, HumanEval) will remain invariant (ICC > 0.95, ANOVA p > 0.05), because the architectural separation between base weights and policy layer allows compliance modulation without capability degradation.

### Background
This is a foundational EXISTENCE hypothesis (MUST_WORK gate). No prerequisites. Validates the core assumption that policy-layer and capability-layer are architecturally decoupled in modern LLMs.

---

## Functional Requirements

### FR-1: Dataset Preparation

**FR-1.1: MMLU Dataset Loading**
- Load full MMLU test set from HuggingFace `cais/mmlu`
- All 57 subjects, approximately 14,000 questions
- Preserve standard splits (dev for few-shot examples, test for evaluation)
- Format: 4-choice multiple-choice questions

**FR-1.2: HumanEval Dataset Loading**
- Install and load HumanEval from `openai/human-eval` repository
- All 164 hand-written programming problems
- Format: Function signature + docstring → complete implementation
- Unit test availability for functional correctness checking

### FR-2: Model Configuration

**FR-2.1: API-Based LLM Access**
- Support both Anthropic API (Claude 3 Opus) OR OpenAI API (GPT-4)
- Lock specific model version to ensure frozen base weights:
  - Claude: `claude-3-opus-20240229`
  - GPT-4: `gpt-4-0613`
- API key management via environment variables

**FR-2.2: Policy-Layer Compliance Modulation**
- Implement 5 compliance levels (λ = 0.2, 0.4, 0.6, 0.8, 1.0)
- Map each λ to system prompt compliance strength:
  - λ=0.2: Minimal compliance ("Answer directly and concisely")
  - λ=0.4: Moderate compliance ("Be helpful and accurate")
  - λ=0.6: Standard compliance ("Provide helpful, accurate, and well-reasoned responses")
  - λ=0.8: Strong compliance ("Be extremely careful, ethical, and thorough")
  - λ=1.0: Maximum compliance ("Follow all constitutional principles")
- Temperature: 0.0 (deterministic evaluation)

### FR-3: Evaluation Pipeline

**FR-3.1: MMLU Evaluation**
- Few-shot prompting with 4-5 examples from dev split
- Exact match scoring (predicted letter A/B/C/D vs ground truth)
- Per-subject accuracy calculation
- Overall average accuracy across all 57 subjects
- Run evaluation for each λ condition

**FR-3.2: HumanEval Evaluation**
- Generate completions for all 164 problems
- Execute unit tests in sandbox environment
- Calculate pass@1 metric (proportion of problems with ≥1 correct solution)
- Run evaluation for each λ condition

**FR-3.3: Data Collection**
- Store results in long-format DataFrame with columns:
  - `lambda`: Compliance level (0.2-1.0)
  - `subject` or `problem_id`: MMLU subject or HumanEval problem
  - `accuracy` or `pass`: Binary correctness indicator
- Save raw results to CSV for reproducibility

### FR-4: Statistical Analysis

**FR-4.1: Intraclass Correlation Coefficient (ICC)**
- Compute ICC2 (two-way mixed effects, absolute agreement)
- Input: Long-format scores with targets='subject', raters='lambda'
- Library: `pingouin.intraclass_corr()`
- Gate threshold: ICC > 0.95

**FR-4.2: One-Way ANOVA**
- Group accuracy scores by λ condition
- Perform one-way ANOVA with Bonferroni correction (α = 0.05)
- Library: `scipy.stats.f_oneway()`
- Gate threshold: p-value > 0.05

**FR-4.3: Cohen's f Effect Size**
- Calculate from F-statistic and degrees of freedom
- Formula: η² = (df1 × F) / (df1 × F + df2), then Cohen's f = √(η² / (1 - η²))
- Gate threshold: f < 0.10

**FR-4.4: Gate Validation**
- Check all three conditions: (ICC > 0.95) AND (p > 0.05) AND (f < 0.10)
- Binary pass/fail result
- Save gate result to validation report

### FR-5: Visualization

**FR-5.1: Gate Metrics Comparison (MANDATORY)**
- Bar chart: Target vs actual values for ICC, ANOVA p-value, Cohen's f
- Include gate thresholds as reference lines
- Save to `{hypothesis_folder}/figures/gate_metrics.png`

**FR-5.2: Capability Consistency Plot**
- Line plot: MMLU/HumanEval accuracy vs λ conditions
- Error bars showing standard deviation across subjects/problems
- Save to `{hypothesis_folder}/figures/capability_consistency.png`

**FR-5.3: Per-Subject Heatmap**
- Heatmap: MMLU subject (rows) × λ condition (columns)
- Color intensity: Accuracy (0-100%)
- Visualizes invariance across all subjects
- Save to `{hypothesis_folder}/figures/subject_heatmap.png`

**FR-5.4: Distribution Violin Plot**
- Violin plots: Accuracy distributions for each λ condition
- Shows variance structure within each compliance level
- Save to `{hypothesis_folder}/figures/accuracy_distributions.png`

### FR-6: Results Reporting

**FR-6.1: Validation Report Generation**
- Generate `04_validation.md` with:
  - Hypothesis statement
  - Gate success criteria
  - Experimental results (ICC, ANOVA, Cohen's f)
  - Pass/Fail decision
  - Figure references
  - Raw data location
- Follow Phase 4 validation report template

**FR-6.2: Metrics Logging**
- Save all metrics to structured format (JSON or YAML)
- Include: λ values, MMLU accuracy per subject, HumanEval pass rates, statistics
- Timestamp and model version metadata

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Pin exact model versions (API model IDs)
- Set deterministic evaluation (temperature=0.0)
- Use fixed random seed if dataset sampling is required
- Save all hyperparameters to config file

### NFR-2: Performance
- Expected runtime: ~4 hours total
  - MMLU: ~30-45 min per λ (5 × 35min ≈ 3 hours)
  - HumanEval: ~15-20 min per λ (5 × 17min ≈ 1.5 hours)
- API rate limiting: Implement retry logic with exponential backoff
- Parallel evaluation not required (sequential by λ is acceptable)

### NFR-3: Code Quality (Minimal Infrastructure - LIGHT tier)
- Configuration: Hardcoded constants or argparse CLI arguments
- Logging: Print statements + CSV output for results
- Testing: Smoke test only (verify API connection, load datasets)
- No YAML config files, no structured logging, no unit tests required

### NFR-4: Error Handling
- API call failures: Retry up to 3 times with 15-second delay
- Dataset loading errors: Fail fast with clear error messages
- Statistical computation errors: Validate input data shapes before analysis

### NFR-5: Data Management
- Store raw API responses for audit trail
- Save intermediate results after each λ evaluation
- Keep results separate by dataset (MMLU vs HumanEval)
- Total storage: ~100MB (text responses + results)

---

## Dependencies

### External Dependencies

**Python Libraries:**
- `anthropic` or `openai` (API clients)
- `datasets` (HuggingFace datasets for MMLU)
- `pingouin` (ICC calculation)
- `scipy` (ANOVA, effect sizes)
- `pandas` (data manipulation)
- `numpy` (numerical operations)
- `matplotlib` or `seaborn` (visualization)

**External Services:**
- Anthropic API (Claude) OR OpenAI API (GPT-4)
- API key required via environment variable

**Datasets:**
- MMLU: `cais/mmlu` (HuggingFace)
- HumanEval: `git+https://github.com/openai/human-eval.git`

### Internal Dependencies
- None (FOUNDATION hypothesis, no prerequisites)

---

## Data Specifications

### Input Data

**MMLU:**
- Source: HuggingFace `datasets.load_dataset("cais/mmlu", "all")`
- Size: ~14,000 questions across 57 subjects
- Format: Multiple-choice (4 options)
- Splits: dev (5 per subject), test (main evaluation)

**HumanEval:**
- Source: `pip install git+https://github.com/openai/human-eval.git`
- Size: 164 programming problems
- Format: Function signature + docstring + unit tests
- No splits (single test set)

### Output Data

**Results DataFrame (Long Format):**
```
Columns: ['lambda', 'dataset', 'item_id', 'prediction', 'ground_truth', 'correct']
Rows: (14,000 MMLU + 164 HumanEval) × 5 λ = ~71,000 rows
Storage: CSV file, ~5MB
```

**Statistics Summary:**
```
Columns: ['metric', 'value', 'threshold', 'pass']
Rows: 3 (ICC, ANOVA_p, Cohens_f)
Storage: JSON or YAML, <1KB
```

**Figures:**
- 4 PNG files (~500KB each, total ~2MB)
- Resolution: 300 DPI for publication quality

---

## Success Criteria

### Primary Success Criteria (Gate Validation)
1. **ICC > 0.95**: Capability scores are highly consistent across λ conditions
2. **ANOVA p > 0.05**: No statistically significant variation in capability across λ
3. **Cohen's f < 0.10**: Effect size of λ on capability is negligible

**ALL THREE must pass for hypothesis success.**

### Secondary Success Criteria
- All 57 MMLU subjects evaluated successfully (no API failures)
- All 164 HumanEval problems evaluated successfully
- Figures generated and saved to output folder
- Validation report generated

### Expected Baseline Performance
- MMLU accuracy: 85-90% (Claude 3 Opus), ~86% (GPT-4)
- HumanEval pass@1: 84-88% (Claude 3 Opus), ~67% (GPT-4)

---

## Out of Scope

- Training or fine-tuning models (evaluation-only experiment)
- Comparison with alternative alignment methods (future work)
- Human evaluation of compliance quality
- Multi-model comparison beyond single base model choice
- Temporal stability of results (single-shot evaluation)

---

## Risks and Mitigations

### Risk 1: API Cost Overruns
- **Impact:** Budget exceeded due to large evaluation scale
- **Likelihood:** Medium
- **Mitigation:** Estimate costs upfront (~14k MMLU + 164 HE × 5 λ ≈ 71k API calls), set API budget limits

### Risk 2: API Rate Limiting
- **Impact:** Evaluation interrupted or slowed significantly
- **Likelihood:** High (large-scale evaluation)
- **Mitigation:** Implement exponential backoff retry, save progress after each λ, resume capability

### Risk 3: Statistical Assumptions Violated
- **Impact:** ICC/ANOVA invalid if data distributions are non-normal
- **Likelihood:** Low (large sample sizes, central limit theorem applies)
- **Mitigation:** Check normality assumptions, report violations if found

### Risk 4: Gate Failure (MUST_WORK)
- **Impact:** Entire hypothesis chain aborted, return to Phase 0
- **Likelihood:** Low (hypothesis grounded in established Constitutional AI architecture)
- **Mitigation:** None (gate failure is informative, not a bug)

---

## Appendix A: API Call Estimation

**MMLU:**
- 14,000 questions × 5 λ = 70,000 API calls
- Est. tokens per call: 200 input + 50 output = 250 tokens
- Total: 70k × 250 = 17.5M tokens

**HumanEval:**
- 164 problems × 5 λ = 820 API calls
- Est. tokens per call: 400 input + 200 output = 600 tokens
- Total: 820 × 600 = 492k tokens

**Grand Total:** ~18M tokens

**Cost Estimate (Claude 3 Opus pricing):**
- Input: ~$15/M tokens → 18M × $15/M ≈ $270
- Output: ~$75/M tokens → 18M × $75/M ≈ $1,350
- **Total: ~$1,620** (upper bound, actual likely lower with cached prompts)

---

## Appendix B: File Structure

```
docs/youra_research/20260511_bi_align/h-e1/
├── 02c_experiment_brief.md       # Input (Phase 2C)
├── 03_prd.md                      # This document (Phase 3)
├── 03_architecture.md             # To be generated
├── 03_logic.md                    # To be generated
├── 03_config.md                   # To be generated
├── 03_tasks.yaml                  # To be generated
├── 04_validation.md               # Output (Phase 4)
├── results/
│   ├── mmlu_raw_results.csv
│   ├── humaneval_raw_results.csv
│   └── statistics_summary.json
└── figures/
    ├── gate_metrics.png
    ├── capability_consistency.png
    ├── subject_heatmap.png
    └── accuracy_distributions.png
```

---

**Document Status:** COMPLETE  
**Next Phase:** Architecture Design (Step 3)
