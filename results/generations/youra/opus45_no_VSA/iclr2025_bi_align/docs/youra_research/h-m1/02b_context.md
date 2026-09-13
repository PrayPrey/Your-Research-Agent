# Phase 2B Context: H-M1

**Hypothesis ID:** H-M1
**Type:** MECHANISM
**Statement:** BAI remains decodable from model hidden states (AUROC ≥0.7) after adversarial gradient reversal removes reward-predictive variance, while reward probe R² degrades <2%.

## Gate Condition
- **Type:** MUST_WORK
- **Threshold:** AUROC ≥0.7 for BAI probe after gradient reversal
- **Secondary:** Reward probe R² degrades <2%

## Prerequisites
- **H-E1:** COMPLETED (PASS) - Agency proxies validated with mean AUROC 0.9836

## Experimental Setup (from Phase 2B)

### Dataset
- **Primary:** HH-RLHF (Anthropic), RewardBench (Allen AI)
- **Evaluation samples:** Full test sets (minimum 500+ per model)

### Models
- Llama-3-8B
- Mistral-7B
- Qwen-2-7B

## Key Technical Components
1. **Hidden state extraction:** Extract activations from transformer layers
2. **BAI computation:** Use validated agency proxies from H-E1
3. **Gradient reversal layer:** Adversarial training to remove reward-predictive variance
4. **Probing classifiers:** Linear probes for BAI decodability and reward prediction

## Success Criteria
- BAI probe AUROC ≥0.7 after gradient reversal
- Reward probe R² degradation <2% (verifies gradient reversal effectiveness)

## Previous Hypothesis Results (H-E1)
- Mean AUROC: 0.9836
- All 4 proxies > baseline (0.5)
- Clarifying Question: 0.9949
- Option Enumeration: 0.9840
- Epistemic Hedging: 0.9880
- Explicit Deferral: 0.9676
