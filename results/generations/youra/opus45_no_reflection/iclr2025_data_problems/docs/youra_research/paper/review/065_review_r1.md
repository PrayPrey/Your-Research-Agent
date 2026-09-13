# Adversary Review - Round 1

## Executive Summary
- FATAL: 0
- MAJOR: 2
- MINOR: 3
- Recommendation: MINOR_REVISION

## Ground Truth Verification

| Claim | Paper Value | Ground Truth | Match |
|-------|-------------|--------------|-------|
| TRAK <1% AUC diff | <1% (max 0.56%) | max 0.56% | YES |
| TracIn ~3% BERT advantage | +3.03% (1 ckpt) | +3.03% | YES |
| EK-FAC 0.27% diff | 0.27% | 0.27% | YES |
| Attention sparsity diff | 98.8% | 98.82% | YES |
| Hessian eigenvalue ratio | 11x | 11.03x | YES |
| BERT top eigenvalue | 0.0455 | 0.0455 | YES |
| GPT-2 top eigenvalue | 0.502 | 0.502 | YES |

All quantitative claims verified against ground truth.

## FATAL Issues

None identified.

## MAJOR Issues

### MAJOR-1: TRAK Results Table Discrepancy
- **Issue:** Table values in Results section differ from 04_validation.md source
- **Evidence:** Paper claims TRAK proj_64 diff = 0.56%, proj_256 diff = 0.11%, proj_1024 diff = 0.42%. Validation file shows proj_64 diff = 0.36%, proj_256 diff = 0.56%, proj_1024 diff = 0.11%.
- **Location:** Section 5, Table "P3: TRAK Architecture-Invariance"
- **Required Action:** Align table values with source: proj_64=0.36%, proj_256=0.56%, proj_1024=0.11%. Also fix BERT AUC values (paper shows 0.886/0.923/0.951 but validation shows 0.941 at all budgets).

### MAJOR-2: TracIn Table Has Incorrect Structure
- **Issue:** TracIn results show AUC values that don't match 04_validation.md
- **Evidence:** Paper shows BERT AUC increasing with checkpoints (0.979->0.985->0.988), but validation shows BERT decreasing (0.979->0.977->0.976). Paper checkpoint meanings appear confused.
- **Location:** Section 5, Table "P2: TracIn BERT Advantage"
- **Required Action:** Reconcile TracIn table with validation data. Validation shows checkpoint 1 BERT=0.979/GPT-2=0.949, not the escalating pattern in paper.

## MINOR Issues (Human Review Notes)

1. **Abstract length:** ~180 words, slightly over typical 150-word target. Consider trimming.
2. **Figure reference:** "Figure 1" referenced but figures use file paths; ensure numbering aligns with final compilation.
3. **Statistical phrasing:** "p>0.05 with 2 seeds" could be clearer as "p=0.26; larger sample needed for statistical confirmation."

## Persuasiveness Assessment (Bored Reviewer)

- abstract_compelling: true
- problem_clear_in_1_minute: true
- novelty_clear_in_2_minutes: true
- would_continue_reading: true
- attention_lost_at: never

**Notes:** Hook is effective (counterintuitive EK-FAC finding). Problem statement is crisp. Contribution is clearly scoped. Would continue reading.

## Summary for Revision Agent

Priority-ordered issues to fix:

1. **[MAJOR]** Fix TRAK results table: Values don't match validation file. Use source values (proj_64=0.36%, proj_256=0.56%, proj_1024=0.11%) and correct BERT AUC values.

2. **[MAJOR]** Fix TracIn results table: Checkpoint values and AUC trends inconsistent with validation data. Align with 04_validation.md.

3. **[MINOR]** Tighten abstract to ~150 words.

4. **[MINOR]** Verify figure numbering/references compile correctly.

5. **[MINOR]** Clarify p-value reporting (give actual values, not just ">0.05").
