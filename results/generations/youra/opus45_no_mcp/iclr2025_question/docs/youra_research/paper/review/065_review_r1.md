# Adversarial Review Round 1

## Accuracy Checker Findings

All quantitative claims verified against ground truth:

| Claim | Paper Value | Ground Truth | Status |
|-------|-------------|--------------|--------|
| Consistency AUROC | 0.81 | 0.8081 (rounded 0.81) | OK |
| Entropy AUROC | 0.65 | 0.6454 (rounded 0.65) | OK |
| Consistency d | 1.19 | 1.1883 (rounded 1.19) | OK |
| Entropy d | 0.47 | 0.4661 (rounded 0.47) | OK |
| Correlation r | -0.54 | -0.5427 (rounded -0.54) | OK |
| H-M1 p-value | 0.0246 | 0.0246 | OK |
| H-M2 p-value | 0.0083 | 0.0083 | OK |
| Optimal weights | alpha=0, beta=0.1 | alpha=0.0, beta=0.1 | OK |
| N for H-M1 | 100 | 100 | OK |
| N for H-M2/H-M3 | 20 | 20 | OK |

**MINOR discrepancy (not fatal):**
- Paper Results Table (line 219-220): Shows entropy-only AUROC=0.675, consistency-only=0.812. H-M3 validation shows AUROC=0.6750 and 0.8125 respectively. The paper says 0.65 for entropy elsewhere (H-M1 with N=100 got 0.6454). The 0.675 in the fusion table is from the N=20 H-M3 run, not H-M1. This is **consistent** but could confuse readers since different N.

**No FATAL accuracy issues found.**

## Bored Reviewer Findings

### Persuasiveness Checks
- abstract_compelling: true (concrete numbers, clear finding, honest about limits)
- problem_clear_in_1_minute: true (hallucination problem well-established in intro)
- novelty_clear_in_2_minutes: true ("first systematic comparison" stated clearly)
- figure_1_self_explanatory: N/A (no figures in text)
- would_continue_reading: true
- attention_lost_at: "never"

### Engagement Issues
None. Paper is well-paced with clear structure.

## Skeptical Expert Findings

### Novelty Claims

| Claim | Assessment |
|-------|------------|
| "First direct AUROC comparison" | PLAUSIBLE - Prior work (Kuhn, Manakul) indeed studied signals separately. Paper correctly positions as systematic comparison on same benchmark/model. |
| "First quantified effect sizes" | PLAUSIBLE - Prior work didn't report Cohen's d comparisons. |
| "Important negative result on fusion" | VERIFIED - H-M3 shows no improvement. Honest about small N limitation. |

### Baseline Fairness

**MAJOR (Severity: MAJOR)**
- **Location:** Methodology/Results
- **Issue:** Entropy baseline uses raw token entropy, not semantic entropy (Kuhn et al. 2023). The paper compares against a weaker entropy baseline than the state-of-the-art. Semantic entropy achieves "AUROC in the range 0.75-0.85" per the Related Work section (line 59), which would make the comparison closer.
- **Evidence:** Paper acknowledges this in Related Work ("we find it underperforms consistency even without semantic clustering") but this is framed as a feature rather than a limitation.
- **Recommendation:** Add explicit limitation that semantic entropy was not tested; the 0.65 AUROC is for raw token entropy only.

### Missing Limitations

1. **MAJOR:** Paper does not mention that consistency requires 10x more inference cost (10 samples vs 1). This is critical for practitioners weighing entropy vs consistency. Entropy can be computed from a single forward pass; consistency requires 10.

2. **MINOR:** No discussion of embedding model choice impact (all-MiniLM-L6-v2). Different embedding models might yield different consistency scores.

3. **MINOR:** Temperature 0.7 is somewhat arbitrary. Higher temp would increase variance, potentially affecting consistency signal.

## Summary

| Persona | FATAL | MAJOR | MINOR |
|---------|-------|-------|-------|
| Accuracy Checker | 0 | 0 | 1 |
| Bored Reviewer | 0 | 0 | 0 |
| Skeptical Expert | 0 | 2 | 2 |

**Total: 0 FATAL, 2 MAJOR, 3 MINOR**

## Issues for Human Review (MINOR only)

1. **Line 219-220:** H-M3 fusion table shows entropy AUROC=0.675, but abstract/results report 0.65. These are from different N (20 vs 100). Consider clarifying in table caption.

2. **Line 126:** "all-MiniLM-L6-v2" embedding model choice not discussed as potential limitation.

3. **Temperature 0.7:** Not discussed whether this is optimal or how results would vary with different temperatures.
