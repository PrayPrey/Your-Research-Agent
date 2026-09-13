# Validation Report: h-c1
date: 2026-08-25T18:30:04.073739Z
gate_result: FAILED

## Gate Metrics
- moderation_rate: 0.7500 (threshold: 0.6)
- ddece_nli: -0.0256 (threshold: 0.01)
- gate_result: FAILED

## Consistency Check (vs H-E1)
- he1_base_ece_clean_nli expected: 0.279 ± 0.005, observed: 0.2860
- he1_base_delta_ece_nli expected: 0.071 ± 0.005, observed: 0.0648
- consistency_ok: False

## Per-Cell Results
| cell_id | ΔECE_base | ΔECE_chat | ΔΔECE | moderation_confirmed |
|---------|-----------|-----------|-------|---------------------|
| NLI-AdvGLUE | 0.0648 | 0.0904 | -0.0256 | False |
| NLI-ANLI-R1 | -0.0165 | -0.1314 | 0.1149 | True |
| NLI-ANLI-R2 | 0.0017 | -0.1458 | 0.1474 | True |
| NLI-ANLI-R3 | -0.0112 | -0.0537 | 0.0425 | True |

## Mechanism Indicators
- base_ece_valid: True
- chat_ece_valid: True
- models_differ: True
- moderation_direction: False

## Key Findings
- moderation_rate=0.7500 ≥ threshold=0.6 → PASS
- ΔΔECE_NLI=-0.0256 ≤ threshold=0.01 → FAIL
