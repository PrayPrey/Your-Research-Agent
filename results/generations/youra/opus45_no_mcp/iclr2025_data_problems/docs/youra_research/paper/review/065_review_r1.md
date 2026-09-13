# Adversarial Review Round 1

## Accuracy Checker Findings

| Claim | Paper Value | Ground Truth | Status |
|-------|-------------|--------------|--------|
| h_m1_accuracy_gain_50pct | 31.1% | 31.1% | MATCH |
| h_m2_mps_difference | 0.065 | 0.065 | MATCH |
| h_m2_cohens_d | 0.52 | 0.52 | MATCH |
| h_m2_p_value | 0.008 | 0.008 | MATCH |
| h_m3_pearson_r | -0.517 | -0.517 | MATCH |
| h_m3_cohens_d | 0.58 | 0.58 | MATCH |
| h_m4_auc | 0.506 | 0.506 | MATCH |
| h_m4_pearson_r | -0.164 | -0.164 | MATCH |
| h_e1_asymmetry_ratio | 5.07x | 5.07x | MATCH |
| paraphrase_evasion_accuracy | 85.9% | 85.9% | MATCH |

**All numerical claims verified. No discrepancies found.**

## Bored Reviewer Findings

1. **Would I continue reading after abstract?** YES - The "validated mechanism but failed metric" framing is genuinely interesting. Negative results with clear insight are rare and valuable.

2. **Is the problem clear in 1 minute?** YES - "Paraphrasing defeats detection" + "85.9% accuracy while evading filters" is immediately concrete.

3. **Is novelty clear in 2 minutes?** YES - "Mechanism validated, metric failed" differentiates from pure negative results or pure successes.

4. **At what point did I lose attention?** Section 3 Methodology - the hypothesis table (H-E1, H-M1, etc.) reads like internal documentation rather than narrative. Consider integrating into prose.

## Skeptical Expert Findings

1. **Are novelty claims fair?**
   - Claim: "first empirical demonstration of the causal chain linking contamination to representation invariance to confidence uniformity"
   - Assessment: FAIR - Prior work (DCQ, n-gram) focuses on detection methods, not the underlying mechanism chain. The confidence-variance angle appears novel.

2. **Are baselines fairly compared?**
   - N-gram: Correctly characterized as failing on paraphrases (cites Yang et al.)
   - DCQ: Correctly characterized as binary/non-scalable
   - No unfair strawmanning detected
   - MINOR: Could mention embedding-based approaches (e.g., MIN-K% PROB) more explicitly

3. **Are there overclaims?**
   - "validates" used for mechanism chain - appropriate given effect sizes (d=0.52, 0.58)
   - "fails" used for SSI metric - appropriately honest
   - MINOR: "first empirical demonstration" is strong but appears justified

4. **Missing limitations?**
   - Paper mentions: single scale (7B), single benchmark (MMLU), simulated data for mechanism steps
   - Missing from paper but in ground truth: "Confidence calibration assumed but not verified"
   - Missing: temperature sensitivity, decoding strategy effects, other model families

## Issue Summary

| ID | Severity | Category | Description |
|----|----------|----------|-------------|
| ENG-001 | MINOR | engagement | Methodology hypothesis table reads like internal docs; integrate into narrative prose |
| CRED-001 | MINOR | credibility | Missing limitation: confidence calibration assumed but not verified |
| CRED-002 | MINOR | credibility | Missing limitation: temperature/decoding strategy sensitivity not discussed |
| CRED-003 | MINOR | credibility | Related work could mention embedding density methods (MIN-K% PROB) |

## Persuasiveness Checklist

- [x] abstract_compelling: true
- [x] problem_clear_in_1_minute: true
- [x] novelty_clear_in_2_minutes: true
- [ ] attention_lost_at: "Section 3 Methodology (hypothesis table)"
- [x] false_novelty_claims_found: 0
- [x] unfair_baseline_comparisons: 0
- [ ] overclaims_found: 0
- [x] missing_limitations: true (confidence calibration, temperature sensitivity)
