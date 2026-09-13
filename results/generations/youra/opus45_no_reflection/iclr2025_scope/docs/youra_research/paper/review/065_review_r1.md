# Adversarial Review Round 1

## Executive Summary
Paper claims 5x drift stability for token-level vs matrix-level distillation. Numerical claims match ground truth. Engagement is strong through Section 3, weakens in Results due to sparse detail. H-M3 FAIL acknowledged but understated. Overall: solid contribution with minor accuracy concerns and moderate engagement issues.

FATAL: 0 | MAJOR: 3 | MINOR: 5

## Persona 1: Accuracy Checker

### FATAL Issues
None. All core numerical claims match ground truth.

### MAJOR Issues
1. **MOHAWK drift ratio claim vague**: Section 5.3 says ">2.0" but no exact value given. Ground truth shows CAB=1.34 (confirmed) but MOHAWK exact ratio not stated anywhere. This looks like hiding unfavorable precision.

2. **H-M3 failure understated**: Paper says "attributed to PoC mode" but p=0.881 is far from significant. Should explicitly state this hypothesis was not supported, not explain it away.

### MINOR Issues
- Line 198: "95% CI (slope)" brackets are nice but source data not shown
- Line 182: H-M3 gate says "MUST_WORK" but result is FAIL - inconsistency in table design
- Abstract says "5x" but text alternates between "5x" and "5.0x" - pick one
- Line 227: "p=0.881" should clarify this means NO effect, not weak effect
- Missing: exact sample sizes for drift measurements (says 500 samples but not confirmed in results)

## Persona 2: Bored Reviewer

### Engagement Assessment
- **Would continue reading after abstract?** YES - clear problem, quantified claim (5x), practical relevance
- **Problem clear in 1 minute?** YES - Section 1.1-1.2 nail it
- **Novelty clear in 2 minutes?** YES - "first controlled comparison" stated early
- **Figure 1 standalone?** PARTIAL - needs caption to explain shaded regions
- **Attention lost at?** Section 5.3-5.4 - results become a list without narrative

### FATAL Issues
None.

### MAJOR Issues
1. **Results section is dry**: Section 5 reads like a report card. No "aha" moment, no walking reader through what the numbers mean. The 5x finding deserves more buildup.

### MINOR Issues
- Section 6.2 limitations dump feels defensive rather than insightful
- Future work (Section 7) is generic - "full training", "more teachers", "hybrid objectives" could be any paper
- No intuitive explanation of WHY position-agnostic supervision helps (the mechanism claim is stated but not explained)

## Persona 3: Skeptical Expert

### Novelty Assessment
Claim "first controlled comparison" is reasonable - prior work (MOHAWK, CAB) focused on performance, not length stability. Contribution is incremental but valid.

### Baseline Fairness
Concern: MOHAWK and CAB compared using "PoC mode" (1M tokens). Neither method is fully trained. This is fair for relative comparison but limits absolute claims.

### Overclaim Detection
1. "Suggests superior generalization potential" (Abstract) - OVERCLAIM. Drift stability != task performance. Paper acknowledges this but buries it in limitations.
2. "Mechanistic advantage" (line 15) - OVERCLAIM. No mechanistic analysis performed; correlation shown, not causation.

### Missing Limitations
- No statistical power analysis for H-M3 (why did it fail?)
- No discussion of CAB's computational overhead (bridges add parameters)
- No ablation on layer selection (why layers 8, 12, 16?)
- Single dataset (C4) - no domain generalization tested

### FATAL Issues
None.

### MAJOR Issues
1. **Mechanism claim unsupported**: Paper repeatedly claims "position-agnostic supervision" as mechanism but provides no direct evidence. This is hypothesis, not finding.

### MINOR Issues
- "Bounded vs unbounded drift" (5.3) - "unbounded" is strong word for 2x ratio over 4 length points
- References incomplete ("See 06_references.bib" is not acceptable for submission)

## Summary
| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 3 |
| MINOR | 5 |

## Persuasiveness Check Results
- abstract_compelling: true
- problem_clear_in_1_minute: true
- novelty_clear_in_2_minutes: true
- would_continue_reading: true
- attention_lost_at: "Section 5.3-5.4"
