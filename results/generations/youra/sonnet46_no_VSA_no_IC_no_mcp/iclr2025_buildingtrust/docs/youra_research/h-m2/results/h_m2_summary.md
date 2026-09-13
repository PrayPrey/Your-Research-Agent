# H-M2 Summary: Confidence-Accuracy Decoupling

**Gate Result:** EXPLORE
**Pass Rate:** 0.0000 (0/5 cells)
**Mean ΔAcc:** -0.0105
**Mean conf_wrong_adv:** 0.6162

## Top 3 Cells by Accuracy Drop
| Model | Task | ΔAcc | conf_wrong_adv | Pass |
|-------|------|------|----------------|------|
| Llama-2-7b-hf | advglue_mnli | -0.0675 | 0.6494 | NO |
| Llama-2-7b-hf | anli_r3 | -0.0550 | 0.6084 | NO |
| Llama-2-7b-hf | anli_r2 | -0.0150 | 0.6163 | NO |

## ANLI Difficulty Gradient
- anli_r1: ΔAcc = 0.0150
- anli_r2: ΔAcc = -0.0150
- anli_r3: ΔAcc = -0.0550
- Direction confirmed (R3 ≤ R1): True

## Ablation: Threshold Sensitivity
- A1_loose_acc_-0.05: gate_pass_rate = 0.0000
- A2_strict_acc_-0.15: gate_pass_rate = 0.0000
- A3_loose_conf_0.60: gate_pass_rate = 0.0000
- baseline_-0.10_0.70: gate_pass_rate = 0.0000
