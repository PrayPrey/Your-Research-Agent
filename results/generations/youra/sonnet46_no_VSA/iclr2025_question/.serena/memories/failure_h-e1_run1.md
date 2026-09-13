# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-02T08:08:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MECHANISM_CONFOUNDED_BY_LENGTH

## Hypothesis Statement

Under white-box access to open-weight LLMs (Llama 3.3 70B, Qwen 2.5 32B, Mistral 8x7B) on TriviaQA dev (2500 prompts), H_spec (last-4-layer rank-64 SVD, greedy decode) predicts SNNE-above-median with AUROC >= 0.85 and partial Spearman rho > 0.6 after length control, because semantic ambiguity activates competing modes in hidden-state space leaving a spectral trace.

## Performance Gap

| Metric | Actual | Target | Status |
|--------|--------|--------|--------|
| AUROC | 0.5378 | ≥ 0.85 | FAIL |
| Partial Spearman ρ | -0.0467 | > 0.60 | FAIL |
| TPU AUROC (lower-bound ref) | 0.9746 | (reference) | — |
| Decoding invariance r | 1.0000 | > 0.70 | PASS |
| H_spec vs length raw rho | 0.952 | (diagnostic) | — |

## Root Cause Analysis

1. **Length dominates H_spec**: H_spec (Shannon entropy of rank-64 singular values of last-4-layer hidden trajectory) correlates 0.952 with token count. The matrix H_traj has shape (k*T, d) = (4*T, d); its singular value structure is dominated by sequence length T, not semantic content.

2. **After length residualization, no signal remains**: Partial Spearman ρ = -0.047 (not significantly different from zero). H_spec provides no information about SNNE beyond what sequence length provides.

3. **AUROC at chance level**: AUROC = 0.537 ≈ 0.50 after accounting for any length correlation. The spectral entropy of the trajectory matrix does not encode semantic uncertainty.

4. **Correct diagnostic but wrong signal**: TPU AUROC = 0.975 confirms SNNE IS predictable from model internals (log-prob predicts it very well). The mechanism just fails to capture the right signal.

5. **Root assumption invalidated**: A1 assumption ("semantic ambiguity activates competing modes in hidden-state space leaving a spectral trace") is incorrect for this formulation. The trajectory concatenation H = [H_{L-4}; H_{L-3}; H_{L-2}; H_{L-1}] (k*T, d) creates a length-dominated matrix.

## What Worked

- Code infrastructure complete and functional
- H_spec is computable (variance > 0)
- Decoding invariance r=1.00 (H_spec is deterministic under greedy decode as expected)
- SNNE computation pipeline works correctly (binarization, NLI clustering)
- Experiment framework runs end-to-end

## Lessons Learned

1. Concatenating hidden layers along the token dimension creates a matrix whose singular structure is dominated by sequence length, not semantic content — AVOID this aggregation pattern for uncertainty quantification
2. Always include H_spec vs length diagnostic BEFORE full evaluation; this would have caught the issue early
3. TPU (log-prob) AUROC = 0.975 suggests SNNE is essentially captured by log-probability, not hidden state geometry
4. Per-token or per-layer aggregation (e.g., mean pooling then SVD, or Gram matrix approach) may avoid the length confound
5. The GLU approach (Gram matrix K = H H^T ∈ R^{T×T} with 1+log(T) normalization) explicitly handles length normalization — this should be explored as fallback

## Feedback for Phase 0 (Pivot Direction)

### Suggested Modifications for New Hypothesis
- Try token log-probability trajectory variance (already confirmed predictive via TPU AUROC = 0.975)
- Try Gram matrix approach: K = H H^T / (1 + log T), then eigenspectrum entropy (GLU approach)
- Try per-last-token hidden state (not trajectory concatenation) with SVD across layers
- Try semantic entropy probes (supervised linear probe on last hidden state) — OATML/semantic-entropy-probes shows AUROC ~0.80-0.85

### What NOT To Do
- Do NOT concatenate hidden layers along token dimension for SVD — length dominates
- Do NOT use H_spec as-is without length normalization
- Do NOT expect trajectory-level spectral entropy to encode uncertainty without length correction

### What Showed Promise
- SNNE itself (as target signal) is reliable and predictable (TPU captures it well)
- Decoding invariance is perfect (H_spec deterministic under greedy) — useful property for any replacement
- The evaluation framework (AUROC, partial Spearman ρ after OLS residualization) is correct and reusable
- Code infrastructure (data loading, evaluation metrics, figures) is reusable for any replacement hypothesis

---
*For cross-phase reference*
*Written at: 2026-08-02T08:08:00Z*
