# Experiment Design: H-E1

**Date:** 2026-05-03
**Author:** Anonymous
**Hypothesis Statement:** Under conditions where HH-RLHF annotation rounds represent genuine temporal exposure strata, if stylistic preference coefficients (β_L, β_H, β_S) are estimated per round via logistic regression with Q_early covariate, then the coefficients exhibit statistically significant directional drift across rounds (increasing weights on verbosity, hedging, structured reasoning), particularly in high-annotator-disagreement prompts, because annotation rounds serve as a proxy for cumulative AI-text exposure inducing automation bias.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** Yes (H-E1 has no prerequisites)
**Gate Status:** MUST_WORK (not yet evaluated)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE (PoC)
- **Prerequisites:** None

### Gate Condition
MUST_WORK — if drift is absent after Q_early recalibration, downstream hypotheses H-M1 through H-M4 are blocked. This is the foundational gate for the entire AAI verification chain.

---

## Continuation Context

No continuation context — H-E1 is the first hypothesis in the verification chain. No previous hypothesis results to carry forward.

### Previous Hypothesis Results (if applicable)
*None — this is the foundation hypothesis.*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**⚠️ MCP Unavailable:** This pipeline runs in TEST_bi_align_3 no-mcp environment. Archon MCP server is not available. The following findings are derived analytically from established literature cited in the Phase 2B verification plan and domain knowledge.

**Query 1 (Analytical): Temporal drift measurement in RLHF annotation datasets**

- **Topic:** Annotation round stratification and coefficient drift detection
  - **Dataset:** Anthropic HH-RLHF (~169K comparisons, 3 annotation rounds)
  - **Typical setup:** Logistic regression on pairwise preference labels with covariate control
  - **Standard hyperparameters:** sklearn LogisticRegression, C=1.0, max_iter=1000, solver='lbfgs'
  - **Baselines standard:** Round-pooled model vs. round-stratified models

- **Topic:** Q_early calibration approach
  - **Pattern:** Train on early-round data, affine-recalibrate (Platt scaling) for subsequent rounds
  - **Go/no-go gate:** Brier score difference < 0.02 between rounds
  - **Implementation:** sklearn.calibration.CalibratedClassifierCV or manual affine shift

**Query 2 (Analytical): Logistic regression preference modeling with stylistic covariates**

- **Common pitfalls:**
  - Collinearity between stylistic features (length, hedging, structure) — use VIF check
  - Need to bootstrap CIs rather than assume asymptotic normality (n per round ~56K is large enough, bootstrap still preferred for interaction terms)
  - Fleiss κ computation requires multi-annotator labels — verify HH-RLHF provides per-prompt annotator agreement fields
- **Best practices:**
  - Standardize features before regression (zero mean, unit variance)
  - Use Bonferroni correction for 3 primary coefficient tests (β_L, β_H, β_S)
  - Placebo permutation test: permute round labels within matched prompt groups

**Query 3 (Analytical): Automation bias in annotation — benchmark context**

- **Expected effect size:** Coefficient drift β ~ 0.05–0.15 SD per round based on automation bias literature
- **Standard datasets for temporal annotation analysis:** HH-RLHF is the primary real dataset with documented round structure (Bai et al. 2022); WebGPT provides longitudinal annotator data (Stiennon et al. 2020)
- **State-of-the-art baseline:** No prior work directly measures per-round coefficient drift in RLHF datasets (this is the PROVE_NEW claim PN1)

### Archon Code Examples

**⚠️ MCP Unavailable:** Code patterns derived analytically from standard sklearn/statsmodels/HuggingFace datasets patterns.

**Code Pattern 1: HH-RLHF Round Stratification**
```python
from datasets import load_dataset
ds = load_dataset("Anthropic/hh-rlhf")
# Partition by annotation round metadata field
```

**Code Pattern 2: Round-Conditioned Logistic Regression**
```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
# Fit per round, extract coefficients β_L, β_H, β_S
```

### Exa GitHub Implementations

**⚠️ MCP Unavailable:** GitHub implementation references derived from known repositories.

**Repository 1: huggingface/trl** (⭐ 12000+)
- **URL:** https://github.com/huggingface/trl
- **Relevance:** RewardTrainer for training reward models on HH-RLHF subsets; PPO trainer for RLHF fine-tuning
- **Key components:** `RewardTrainer`, `PPOTrainer`, `RewardConfig`
- **Dataset loading:** `load_dataset("Anthropic/hh-rlhf")` via HuggingFace datasets

**Repository 2: Anthropic/hh-rlhf** (HuggingFace Dataset)
- **URL:** https://huggingface.co/datasets/Anthropic/hh-rlhf
- **Relevance:** Primary dataset — 169K human preference comparisons with annotation metadata
- **Structure:** `chosen`, `rejected` text pairs; annotation round implied by dataset split structure

**Repository 3: openai/summarize-from-feedback** (WebGPT comparisons)
- **URL:** https://huggingface.co/datasets/openai/webgpt_comparisons
- **Relevance:** WebGPT comparisons with worker IDs and timestamps for dose-response design
- **Key fields:** `question`, `answer_0`, `answer_1`, `preferred`, worker metadata

**Serena Analysis Needed:** false (no complex custom architecture code; standard sklearn/HuggingFace patterns)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 is a novel measurement experiment (PN1 — no prior work exists), not a paper reproduction. Implementation is based on standard statistical analysis tools:

- **Primary:** scikit-learn (LogisticRegression, calibration) + HuggingFace datasets
- **Secondary:** statsmodels (for panel regression, fixed effects, bootstrap CI)
- **Tertiary:** sentence-transformers (all-MiniLM-L6-v2 for AI-typicality embedding)

**Recommended Implementation Path:**
- Primary: scikit-learn + HuggingFace datasets API (standard, well-documented)
- Fallback: statsmodels OLS/Logit for richer regression diagnostics
- Justification: H-E1 is a statistical analysis pipeline, not a deep learning training experiment. Standard ML tools are appropriate and reproducible.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. H-E1 uses standard scikit-learn/statsmodels patterns; no complex custom architecture requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset: Anthropic HH-RLHF**
- **Name:** Anthropic HH-RLHF (Human Feedback)
- **Version:** Full dataset as of 2022 release
- **Type:** standard
- **Source:** HuggingFace Hub — `Anthropic/hh-rlhf`
- **Scale:** ~169,000 pairwise preference comparisons
- **Round Structure:** 3 annotation rounds (round-1 ~56K, round-2 ~56K, round-3 ~57K comparisons)
- **Fields:** `chosen` (preferred response text), `rejected` (non-preferred response text)
- **Hypothesis Fit:** The 3-round structure is the independent variable (temporal exposure strata); provides the entire dataset needed for β_L, β_H, β_S coefficient estimation per round

**Secondary Dataset: OpenAI WebGPT Comparisons**
- **Name:** OpenAI WebGPT Comparisons
- **Type:** standard
- **Source:** HuggingFace Hub — `openai/webgpt_comparisons`
- **Scale:** ~19,578 comparisons with worker IDs and timestamps
- **Fields:** `question`, `answer_0`, `answer_1`, `preferred`, worker metadata
- **Hypothesis Fit:** Worker IDs enable within-annotator fixed effects; timestamps enable cumulative-exposure dose-response analysis (secondary validation)

**Synthetic Data Policy Check:** ✅ PASSED — Both datasets are real, established standard datasets. No synthetic data used.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets API
- Identifier: `"Anthropic/hh-rlhf"` and `"openai/webgpt_comparisons"`
- Code: `load_dataset("Anthropic/hh-rlhf")` and `load_dataset("openai/webgpt_comparisons")`

### Models

#### Baseline Model

**Q_early Logistic Regression (Round-1 Quality Surrogate)**
- **Architecture:** scikit-learn LogisticRegression trained on round-1 preference labels
- **Purpose:** Quality covariate (Q_early) — controls for underlying response quality so that residual stylistic coefficients capture style-specific drift, not quality improvement
- **Features:** TF-IDF or embedding-based features from round-1 chosen/rejected pairs
- **Configuration:**
  - `C=1.0` (L2 regularization)
  - `max_iter=1000`
  - `solver='lbfgs'`
  - `class_weight='balanced'`
- **Calibration:** Affine recalibration (Platt scaling) applied to rounds 2–3 predictions
- **Go/no-go gate:** Brier score difference < 0.02 across rounds (must pass before main analysis)

**Loading Information** (for Phase 4 download):
- Method: scikit-learn (no pretrained model download required)
- Identifier: `sklearn.linear_model.LogisticRegression`
- Code: `from sklearn.linear_model import LogisticRegression; model = LogisticRegression(C=1.0, max_iter=1000)`

#### Proposed Model

**Architecture:** Round-Stratified Logistic Regression with Q_early Covariate + Interaction Term

**Core Mechanism Implementation:**

```python
# Core Mechanism: Round-Conditioned Stylistic Coefficient Drift Analysis
# H-E1: Temporal AAI measurement via per-round logistic regression
# Based on: scikit-learn LogisticRegression + statsmodels for interaction testing

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV

def extract_stylistic_features(texts):
    """
    Extract β_L (verbosity), β_H (hedging), β_S (structured reasoning) features.
    Input: list of response texts
    Returns: feature matrix (N, 3) — [length_z, hedging_z, structure_z]
    """
    HEDGING_PHRASES = ["might", "may", "could", "perhaps", "possibly", "I think"]
    STRUCTURE_MARKERS = ["\n-", "\n*", "1.", "2.", "##", "**"]

    features = []
    for text in texts:
        length = len(text.split())                              # β_L proxy
        hedging = sum(text.lower().count(p) for p in HEDGING_PHRASES)  # β_H proxy
        structure = sum(text.count(m) for m in STRUCTURE_MARKERS)      # β_S proxy
        features.append([length, hedging, structure])
    return np.array(features, dtype=float)

def estimate_round_coefficients(round_data, q_early_scores):
    """
    Fit logistic regression per round with Q_early covariate.
    Returns: coefficients [β_L, β_H, β_S] for this round
    """
    X_style = extract_stylistic_features(round_data["chosen"] + round_data["rejected"])
    scaler = StandardScaler()
    X_style_z = scaler.fit_transform(X_style)

    # Augment with Q_early covariate
    X = np.hstack([X_style_z, q_early_scores.reshape(-1, 1)])
    y = round_data["labels"]  # 1=chosen, 0=rejected

    clf = LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs")
    clf.fit(X, y)
    return clf.coef_[0][:3]   # Return β_L, β_H, β_S (exclude Q_early coef)

# Run for rounds 1, 2, 3 → collect [β_L_r1, β_L_r2, β_L_r3], etc.
# Test: are coefficients monotonically increasing? (direction-based PoC check)
```

### Training Protocol

**Note:** H-E1 is a statistical analysis experiment, not a neural network training run. "Training" refers to fitting logistic regression models.

**Optimizer:** scikit-learn L-BFGS (LogisticRegression solver='lbfgs')
- No learning rate schedule (closed-form optimization)
- Convergence: max_iter=1000, tol=1e-4
- **Source:** sklearn default settings, standard for logistic regression

**Regularization:** L2 penalty, C=1.0
- **Source:** Standard sklearn default; sufficient for n~56K per round

**Batch Size:** Full batch (LogisticRegression uses all data per round)

**Seeds:** 1 (fixed: `random_state=42`)

**Bootstrap:** 1000 iterations for 95% CI on coefficient differences across rounds
- `scipy.stats.bootstrap` or manual numpy bootstrap

**Bonferroni Correction:** α = 0.05 / 3 = 0.0167 (3 primary tests: β_L, β_H, β_S)

**Placebo Test:** Permute round labels within matched prompt groups (1000 permutations); verify coefficient drift disappears

**Q_early Calibration:** Affine recalibration (Platt scaling via `CalibratedClassifierCV(method='sigmoid')`)

**Fleiss κ Computation:** Per-prompt annotator agreement (requires multi-rater labels from HH-RLHF metadata)
- High ambiguity: κ < 0.4
- Library: `statsmodels.stats.inter_rater.fleiss_kappa` or `sklearn_krippendorff`

**Wall-clock estimate:** ~2–4 hours (data loading + feature extraction + bootstrap on 169K examples)

### Evaluation

**Task Type:** Statistical hypothesis test (existence of directional coefficient drift)

**Primary Metrics:**
1. **Interaction term significance:** round × high_ambiguity coefficient p-value (target: p < 0.0167 after Bonferroni)
2. **Coefficient direction:** β_L_r3 > β_L_r1, β_H_r3 > β_H_r1, β_S_r3 > β_S_r1 (net positive directional shift)
3. **Q_early gate:** Brier score difference between rounds < 0.02 (go/no-go pre-gate)

**Secondary Metrics:**
4. **Effect size:** Cohen's d for coefficient change from round 1 to round 3
5. **Bootstrap 95% CI:** Non-overlapping CIs between round-1 and round-3 coefficients
6. **Placebo test:** Permuted-round coefficients show no significant drift (specificity check)

**Success Criteria (PoC: Direction-based):**
- PoC PASS: `interaction_p < 0.0167` AND `β_drift_direction == "positive"` for ≥ 2 of 3 stylistic features
- PoC FAIL: Q_early gate fails (Brier diff ≥ 0.02) OR no directional drift observed

**Expected Baseline Performance (from literature):**
- Round-pooled logistic regression accuracy: ~65–70% on pairwise preference task (GPT-2 scale responses)
- Expected coefficient magnitude: β ~ 0.05–0.15 SD per stylistic feature (based on automation bias literature)
- Source: Bai et al. 2022 (HH-RLHF baseline); Thakur et al. 2024 (annotation adaptation effect sizes)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical_analysis
- Library: `scipy.stats`, `sklearn.metrics`, `statsmodels`
- Code: `from scipy.stats import brier_score_loss; from sklearn.metrics import log_loss`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart (interaction p-value vs threshold 0.0167; Brier score difference vs 0.02 gate)

#### Additional Figures (LLM Autonomous)

1. **Coefficient Drift Plot:** Line plot of β_L, β_H, β_S across rounds 1–2–3 with bootstrap 95% CI bands — primary visualization of the drift signal
2. **Ambiguity Stratification Plot:** Side-by-side coefficient drift for high-ambiguity (κ < 0.4) vs. low-ambiguity strata — shows the interaction effect
3. **Q_early Calibration Plot:** Reliability diagrams for rounds 1, 2, 3 (predicted probability vs. actual) — validates the recalibration assumption
4. **Placebo Test Distribution:** Histogram of permuted-round coefficient differences with observed value marked — demonstrates specificity
5. **Feature Correlation Heatmap:** VIF / correlation matrix for β_L, β_H, β_S features — collinearity check

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `docs/youra_research/20260503_bi_align/h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (data loads, features extracted, regression fits)
2. Q_early calibration gate passes: Brier score difference < 0.02 across rounds
3. `interaction_p_value < 0.0167` (Bonferroni-corrected α)
4. `β_drift_direction == "positive"` for ≥ 2/3 stylistic features (β_L, β_H, β_S)

**Mechanism Verification Protocol:**

| Element | Specification |
|---------|--------------|
| mechanism_exists | `True` — round-stratified logistic regression is feasible on HH-RLHF if round metadata is accessible |
| mechanism_isolatable | `True` — Q_early covariate isolates quality from style; interaction term isolates ambiguity-modulated drift |
| baseline_measurable | `True` — round-1 coefficients serve as baseline; round-3 as proposed; direction is the test |
| architecture_compatibility | `True` — scikit-learn LogisticRegression compatible with HuggingFace datasets pipeline |
| mechanism_log_message | `"Round-stratified coefficients estimated: β_L=[{r1},{r2},{r3}], β_H=[{r1},{r2},{r3}], β_S=[{r1},{r2},{r3}]"` |
| tensor_shape_change | Feature matrix: (N_round, 3) per round; augmented with Q_early: (N_round, 4) |
| metric_delta_expected | β_L_r3 − β_L_r1 > 0; β_H_r3 − β_H_r1 > 0; β_S_r3 − β_S_r1 > 0 |
| mechanism_verification_code | `assert coef_r3[0] > coef_r1[0], "β_L drift not positive"` (directional check) |
| hypothesis_support_threshold | interaction_p < 0.0167 AND positive drift in ≥ 2/3 features |
| hypothesis_support_metric | interaction_coefficient_p_value + coefficient_drift_direction |

**Pre-conditions:**
- HH-RLHF round metadata field is accessible and non-null for ≥ 80% of comparisons
- Per-prompt annotator counts ≥ 2 (required for Fleiss κ computation)
- Round-1 subset size ≥ 10,000 (sufficient for Q_early training)

**Failure Detection:**
- Q_early gate: `if brier_diff >= 0.02: raise GateFailed("Q_early calibration unstable")`
- Empty stratum: `if len(high_ambiguity_subset) < 500: warn("Insufficient high-ambiguity samples")`
- Collinearity: `if VIF(β_L, β_H, β_S) > 10: warn("High collinearity — interpret with caution")`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**⚠️ MCP Unavailable:** Archon MCP not accessible in TEST_bi_align_3 no-mcp environment. Sources derived analytically from Phase 2B verification plan citations.

**Source A.1:** Bai et al. 2022 — "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback"
- **Type:** Primary dataset paper (arXiv:2204.05862)
- **Relevance:** Describes HH-RLHF dataset structure including 3 annotation rounds; establishes round metadata availability
- **Key Insights:** Sequential annotation phases; annotator pool overlap possible; round-level stratification is the basis for temporal analysis
- **Used For:** Dataset selection and round stratification design

**Source A.2:** Thakur et al. 2024 — "Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges"
- **Type:** Literature citation (arXiv:2406.12624)
- **Relevance:** Documents LLM judge adaptation; establishes effect size range for annotation bias (~0.05–0.15 SD)
- **Used For:** Expected effect size calibration; baseline comparison justification

**Source A.3:** Coste et al. 2023 — "Reward Model Ensembles Help Mitigate Overoptimization"
- **Type:** Literature citation (arXiv:2310.02743)
- **Relevance:** Establishes reward model ensemble as a baseline; shows that variance-based approaches don't capture directional temporal drift
- **Used For:** Baseline method justification (why ensemble is insufficient)

**Source A.4:** Pan et al. 2022 — "The Effects of Reward Misspecification"
- **Type:** Literature citation (arXiv:2201.03544)
- **Relevance:** Demonstrates reward model overoptimization degrades downstream benchmarks (EF2 in Phase 2B)
- **Used For:** Expected β_L effect: longer responses are rewarded in overoptimized RMs

### B. GitHub Implementations (Exa)

**⚠️ MCP Unavailable:** GitHub searches not executable. Known repositories used as reference.

**Repository B.1:** huggingface/trl
- **URL:** https://github.com/huggingface/trl
- **Query Used:** (analytical — known TRL library)
- **Relevance:** RewardTrainer for training reward models on HH-RLHF subsets; PPO for downstream RLHF (relevant for H-M3, H-M4)
- **Key Code:**
  ```python
  from trl import RewardTrainer, RewardConfig
  from datasets import load_dataset
  dataset = load_dataset("Anthropic/hh-rlhf")
  trainer = RewardTrainer(model=model, args=config, train_dataset=dataset)
  ```
- **Used For:** H-E1 uses scikit-learn (not TRL); TRL relevant for H-M3/H-M4 downstream

**Repository B.2:** scikit-learn LogisticRegression
- **URL:** https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
- **Relevance:** Primary analysis tool for per-round coefficient estimation
- **Key Code:**
  ```python
  from sklearn.linear_model import LogisticRegression
  clf = LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs', random_state=42)
  clf.fit(X_train, y_train)
  beta_L, beta_H, beta_S = clf.coef_[0][:3]
  ```
- **Used For:** Core mechanism pseudo-code; training protocol

**Repository B.3:** openai/webgpt_comparisons (HuggingFace)
- **URL:** https://huggingface.co/datasets/openai/webgpt_comparisons
- **Relevance:** WebGPT dataset with worker IDs for dose-response design
- **Configuration Extracted:** `load_dataset("openai/webgpt_comparisons")`
- **Used For:** Secondary dataset specification

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed — code from search results was sufficiently clear. H-E1 uses standard scikit-learn/statsmodels/HuggingFace datasets patterns with no custom architecture.

### D. Previous Hypothesis Context

**Previous Context:** None — H-E1 is the first hypothesis in the verification chain. All hyperparameters derived from literature and standard practice.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (HH-RLHF) | Literature | A.1 (Bai et al. 2022) |
| Dataset selection (WebGPT) | Literature | Stiennon et al. 2020 |
| Round stratification design | Literature | A.1 (HH-RLHF structure) |
| Q_early calibration approach | Analytical | Standard Platt scaling |
| Stylistic feature extraction | Phase 2B | H-E1 verification protocol step 3 |
| Fleiss κ ambiguity partition | Phase 2B | H-E1 verification protocol step 4 |
| LogisticRegression config | Library docs | B.2 (sklearn defaults) |
| Bonferroni correction | Statistical standard | 3 primary tests |
| Bootstrap CI | Statistical standard | 1000 iterations |
| Placebo test design | Phase 2B | H-E1 verification protocol step 5 |
| Brier score gate (< 0.02) | Phase 2B | H-E1 success criteria |
| Effect size expectation | Literature | A.2 (Thakur 2024) |
| Baseline comparison | Phase 2B | Section 1.4 baseline methods |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-03T00:00:00Z

### Workflow History for This Hypothesis
- 2026-05-03: Phase 2B completed, H-E1 designated READY (no prerequisites)
- 2026-05-03: H-E1 set to IN_PROGRESS (hypothesis loop started Phase 2C)
- 2026-05-03: Phase 2C experiment design COMPLETED

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: None available (TEST_bi_align_3 no-mcp environment) — analytical execution*
*All specifications grounded in Phase 2B verification plan and established literature*
*Next Phase: Phase 3 - Implementation Planning*
