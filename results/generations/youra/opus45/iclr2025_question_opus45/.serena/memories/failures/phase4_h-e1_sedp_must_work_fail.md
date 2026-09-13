# Failure Record: h-e1 (SEDP MUST_WORK FAIL)

## Metadata
- **Hypothesis ID:** h-e1
- **Type:** EXISTENCE
- **Phase:** Phase 4
- **Gate Type:** MUST_WORK
- **Gate Result:** FAIL
- **Recorded At:** 2026-03-29T00:00:00Z
- **Research Folder:** /home/anonymous/YouRA_results_new_4_sonnet45/TEST_question_opus45/docs/youra_research/20260325_question

## Hypothesis Statement
A probe trained on hidden states with semantic similarity auxiliary signal produces meaningful SE predictions (rho >= 0.3) on the same model it was trained on.

## Failure Details

### Gate Check
- **Criterion:** SEDP rho >= 0.3
- **Threshold:** 0.3
- **Actual:** 0.0843
- **Passed:** false

### Metrics
| Metric | SEP (Baseline) | SEDP (Proposed) | Delta |
|--------|----------------|-----------------|-------|
| Spearman rho | 0.0835 | 0.0843 | +0.0009 |
| AUROC | 0.5214 | 0.5219 | +0.0004 |
| p-value | 0.288 | 0.283 | - |

### Key Findings
1. SEDP achieved rho=0.0843, far below 0.3 threshold
2. Both SEP and SEDP perform near random (AUROC ~0.52)
3. SEDP marginally outperforms SEP (+0.0009 rho) but effect is negligible
4. Hidden states at layer 25 do not capture semantic entropy signal
5. Similarity features provide minimal additional information

## Root Cause Analysis
1. Layer 25 hidden states may lack SE-relevant information
2. TBG token position may not be optimal for SE prediction
3. Logistic regression probe may be too simple
4. 4-dimensional similarity features insufficient

## Routing Decision
- **Trigger:** MUST_WORK_FAIL
- **Action:** Route to Phase 0
- **Reason:** PoC shows methodology doesn't work - hidden states don't encode SE at detectable levels

## Lessons Learned
1. **Hidden state SE encoding is not straightforward:** The assumption that hidden states contain easily extractable SE information was not validated. Future approaches should consider alternative representations.
2. **Probe architecture matters:** A simple logistic regression may be insufficient. Consider deeper architectures or different feature engineering.
3. **Layer selection is critical:** Layer 25 was chosen based on assumptions. Systematic layer ablation should be performed before committing to a single layer.
4. **Similarity features alone are not enough:** The 4-dimensional similarity features added minimal information. Consider richer semantic representations.

## Impact on Dependent Hypotheses
- **h-m1:** CASCADE_FAILED (prerequisite h-e1 failed)
- **h-m2:** CASCADE_FAILED (prerequisite chain broken)
- **h-m3:** CASCADE_FAILED (prerequisite chain broken)

## Recommendations for Phase 0 Restart
1. Reconsider the fundamental assumption that SE can be predicted from single-pass hidden states
2. Explore ensemble methods across multiple layers
3. Consider attention-based probes instead of MLP
4. Investigate whether SE signal exists in other model components (attention weights, residual streams)
5. Consider alternative uncertainty quantification approaches beyond SE
