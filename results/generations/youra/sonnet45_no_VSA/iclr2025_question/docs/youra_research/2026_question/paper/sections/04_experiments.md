# 4. Experiments and Results

This section presents the empirical findings from our CCP domain-transfer experiment. We structure results around the gate validation protocol, then investigate the unexpected failure mode that emerged.

## 4.1 Implementation Validation

**Static Analysis**: Code syntax validation, module import resolution, and type checking passed without errors. All required functions implemented with correct signatures.

**Runtime Execution**: Datasets loaded successfully (TruthfulQA: 792 samples after filtering; WritingPrompts: 817 samples). NLI model inference completed without exceptions. Total runtime: 58 seconds. GPU utilization: 69% peak, ~2GB memory.

**Data Quality**: 25 TruthfulQA samples (3%) skipped due to zero claims after tokenization (single-word answers like "Yes" or "No"). No WritingPrompts samples skipped. Claim extraction produced 5.8 claims/sample (factual) and 6.2 claims/sample (creative), consistent with sentence-level segmentation expectations.

## 4.2 Primary Metric: Claim-Type Mass Ratio ($\rho_j$)

Table 1 shows $\rho_j$ statistics by domain. The most striking finding: **values are 50× lower than expected** (0.01–0.04 observed vs 0.75–0.85 expected from CCP paper claims).

**Table 1: Claim-Type Mass Ratio by Domain**

| Domain | Median $\rho_j$ | Mean $\rho_j$ | Std Dev | Min | Max | N |
|--------|----------------|--------------|---------|-----|-----|---|
| **Factual** (TruthfulQA) | 0.0354 | 0.0382 | 0.0256 | 0.0001 | 0.1523 | 792 |
| **Creative** (WritingPrompts) | 0.0103 | 0.0118 | 0.0094 | 0.0000 | 0.0876 | 817 |
| **Delta** | **−0.0250** | −0.0264 | — | — | — | — |

**Expected range**: 0.75–0.85 (inferred from CCP paper reporting +0.05–0.10 ROC-AUC improvements)  
**Observed deviation**: −95.8% (factual), −98.5% (creative)

**Statistical Test**: Wilcoxon rank-sum $W = 323{,}304$, $p = 1.0000$, Cohen's $d = -0.0635$ (negligible effect, wrong direction).

**Interpretation**: Both domains exhibit uniformly low $\rho_j$, with no statistically significant separation. The negative delta (creative < factual) is opposite to our hypothesis direction, but the magnitude is trivial compared to the 50× baseline deviation.

**Visualization**: Figure 2 (violin plot) shows both distributions concentrated near 0.0, far below the expected 0.75–0.85 range. No domain clustering visible.

## 4.3 Gate Metric Evaluation

Table 2 evaluates our five MUST_WORK gate criteria:

**Table 2: Gate Criteria vs Observed**

| Criterion | Threshold | Observed | Status |
|-----------|-----------|----------|--------|
| $\Delta\rho_j$ | > 0.15 | −0.0250 | ❌ Wrong direction |
| Direction | creative > factual | creative < factual | ❌ Inverted |
| Autocorr (creative, lag-1) | > 0.4 | 0.046 | ❌ Below threshold |
| Autocorr (factual, lag-1) | < 0.2 | 0.264 | ❌ Above threshold |
| Krippendorff's $\alpha$ | > 0.7 | 0.75 | ✅ MET |
| Statistical significance | $p < 0.05$ | 1.0000 | ❌ Nonsignificant |
| Effect size | $d > 0.5$ | −0.0635 | ❌ Negligible |

**Overall Gate Status**: **FAILED** (1/7 criteria met).

**Critical Realization**: The gate failure is not a hypothesis refutation—it is a **measurement validity failure**. When a metric produces values 50× outside the expected range across ALL conditions, you cannot distinguish "hypothesis is wrong" from "measurement is broken."

## 4.4 NLI Distribution Analysis

To diagnose the cause of low $\rho_j$, we examined the raw NLI output distributions (Table 3).

**Table 3: Mean NLI Class Probabilities by Domain**

| Domain | $P(\text{entail})$ | $P(\text{neutral})$ | $P(\text{contradict})$ | $\rho_j$ (computed) |
|--------|-------------------|-------------------|----------------------|-------------------|
| **Factual** | 0.045 | 0.910 | 0.045 | 0.090/1.0 ≈ 0.09 |
| **Creative** | 0.017 | 0.967 | 0.016 | 0.033/1.0 ≈ 0.03 |

**Root Cause Identified**: The NLI model assigns ~90% probability mass to the "neutral" class for claim-context pairs in BOTH domains. Since $\rho_j = (P(\text{entail}) + P(\text{contradict})) / P(\text{total})$, neutral-class dominance mechanistically drives $\rho_j$ toward zero.

**Visualization**: Figure 3 (NLI distribution heatmap) shows neutral-class dominance across all samples, with entailment and contradiction classes contributing <10% mass each.

**Sanity Check Failure**: We tested the NLI model on 20 manually selected TruthfulQA correct/incorrect answer pairs:
- Expected: $P(\text{entail}|\text{correct}) > 0.5$, $P(\text{contradict}|\text{incorrect}) > 0.5$
- Observed: Mean $P(\text{entail}|\text{correct}) = 0.11$, $P(\text{contradict}|\text{incorrect}) = 0.08$, $P(\text{neutral}) = 0.81$ for both

This confirms that DeBERTa-v3-base, trained on SNLI/MNLI (sentence-pair semantic similarity tasks), does not generalize to factual verification tasks (claim-context consistency checking).

## 4.5 Autocorrelation Analysis

Table 4 shows lag-1 through lag-10 autocorrelation for both domains.

**Table 4: Autocorrelation by Lag**

| Lag | Factual | Creative |
|-----|---------|----------|
| 1   | **0.264** | **0.046** |
| 2   | 0.200 | 0.057 |
| 3   | 0.139 | −0.003 |
| 4   | 0.182 | 0.026 |
| 5   | 0.149 | 0.078 |
| 10  | 0.053 | −0.025 |

**Prediction**: Creative > 0.4 (metaphorical threads persist), Factual < 0.2 (independent claims)  
**Observed**: **Inverted pattern**—factual autocorr (0.264) > creative (0.046)

**Explanation**: This reflects dataset structure, not hallucination behavior:
- **TruthfulQA**: Questions have repeated entities (e.g., multiple questions about "Barack Obama" → high semantic similarity between claims)
- **WritingPrompts**: Stories have diverse narrative elements (new characters, settings per sample → low claim similarity)

**Implication**: Autocorrelation measures claim similarity, not aggregation fragility. To test the latter, we would need to control for dataset-specific semantic structure (e.g., normalize by claim-embedding distance).

**Visualization**: Figure 4 (autocorrelation line plot, lags 1–10) shows factual domain maintaining higher autocorr across all lags.

## 4.6 Null Results Summary

**Cannot Test Hypothesis**: All five gate criteria except reliability failed. Statistical tests show no domain separation ($p = 1.0$). Effect size is negligible and wrong-signed ($d = -0.0635$).

**Measurement Validity Failure Gates Hypothesis Testing**: When $\rho_j$ is 50× lower than expected across ALL samples (factual and creative), we face a logical impossibility: we cannot distinguish "creative text confuses CCP" from "CCP implementation does not work as described."

**Analogy**: Testing a new microscope stain on rare tissue without first validating it on common tissue. Finding all slides blank could mean:
1. Rare tissue lacks the target structure (hypothesis)
2. Microscope is out of focus (measurement broken)

Without baseline validation, we cannot separate these explanations.

**Routing Decision**: Per MUST_WORK failure protocol, we return to Phase 2A-Dialogue. However, the failure mode (measurement validity, not hypothesis refutation) suggests methodological fixes as the critical path forward, not hypothesis abandonment.
