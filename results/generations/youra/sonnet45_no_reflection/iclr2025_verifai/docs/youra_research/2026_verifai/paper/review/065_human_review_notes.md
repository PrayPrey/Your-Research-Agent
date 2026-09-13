# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI.

**Generated**: 2026-05-12T07:30:00Z
**Rounds Completed**: 1

---

## Summary by Category

| Category | Count |
|----------|-------|
| Typo | 0 |
| Grammar | 0 |
| Style | 2 |
| Clarity | 4 |
| Formatting | 1 |

---

## Round 1 Issues

### Accuracy Checker MINOR Issues

**ACC-MINOR-001**: Table 1 Values Lack Precision Context
- **Location**: Results section, Table 1 (per-instance values)
- **Issue**: Per-instance values shown (e.g., "SAT-001: d/n=0.467, H=2.692") without indicating precision
- **Suggestion**: Add note: "Values shown to 3 decimal places"
- **Impact**: Minor confusion about measurement precision

**ACC-MINOR-002**: IQR Inconsistency in Terminology
- **Location**: Results section (d/n and entropy IQR statements)
- **Issue**: Paper states "IQR = 0.265" for d/n and "IQR = 0.309" for entropy, but earlier uses "range" to mean Q3-Q1
- **Suggestion**: Use "IQR" consistently or clarify "range" = "IQR" on first usage
- **Impact**: Minor terminological inconsistency

**ACC-MINOR-003**: Training Convergence Claim Slightly Overstated
- **Location**: Results section (training convergence discussion)
- **Issue**: "matching the theoretical minimum for balanced binary classification" overstates slightly—this is the loss for random predictions, not necessarily the minimum achievable
- **Suggestion**: Clarify: "converged to loss 0.693 ≈ log(2), consistent with balanced binary classification baseline"
- **Impact**: Minor technical imprecision

### Bored Reviewer MINOR Issues

**BORE-MINOR-001**: Introduction Opening Could Be Stronger
- **Location**: Introduction first paragraph
- **Issue**: Opens with "Neural SAT solvers like NeuroSAT achieve approximately 85%"—a statement of fact, not a hook
- **Suggestion**: Start with the gap itself: "Why do neural SAT solvers plateau at 85% satisfaction? We show the gap stems from..." Put the mystery first
- **Impact**: Minor loss of engagement potential in opening seconds

**BORE-MINOR-002**: Related Work Section Placement Disrupts Flow
- **Location**: Related Work appears between Introduction and Methodology
- **Issue**: Momentum from Introduction's compelling setup is interrupted by dense citation section before reader sees the methodology
- **Suggestion**: Consider moving Related Work after Results (common in ML conferences) to maintain momentum from problem → method → results
- **Impact**: Minor engagement drop mid-paper

### Skeptical Expert MINOR Issues

**SKEP-MINOR-001**: Mechanistic Explanation Untested
- **Location**: Discussion (mechanistic explanation)
- **Issue**: Paper claims "deterministic LSTM message-passing with single initialization causes structural homogeneity" but provides no ablation study
- **Suggestion**: Add: "Ablation studies with multiple training seeds would confirm this mechanistic hypothesis."
- **Impact**: Minor—claim is hedged as explanation, not proof

**SKEP-MINOR-002**: Threshold Selection Arbitrary
- **Location**: Methodology (gate criteria)
- **Issue**: Why d/n range > 0.20 and entropy range > 2.0? Paper states these are "gate criteria" but provides no justification
- **Suggestion**: Add footnote: "Thresholds selected based on pilot analysis to distinguish meaningful heterogeneity (IQR > 0.20) from noise."
- **Impact**: Minor—thresholds are clear and stated upfront, but lack rationale

**SKEP-MINOR-003**: "First Quantitative Evidence" Claim Overreach
- **Location**: Conclusion (Note: Already addressed in MAJOR revision as part of PoC framing)
- **Issue**: "First quantitative evidence" implies comprehensive validation, but this is PoC-scale (8 instances)
- **Suggestion**: Replace with "diagnostic demonstration" or qualify with "proof-of-concept"
- **Impact**: Minor phrasing overstatement
- **Status**: RESOLVED in R1 revision as part of BORE-MAJOR-001 fix

---

## Formatting Issues

**FORMAT-001**: Table 1 Formatting
- **Location**: Results section, Table 1
- **Issue**: Column alignment could be improved for readability
- **Suggestion**: Consider adding more spacing or horizontal rules between instance groups
- **Impact**: Minor visual clarity improvement

---

## Recommended Priority

1. **Fix First**: ACC-MINOR-001, ACC-MINOR-002, ACC-MINOR-003 (technical precision in Results section)
2. **Consider**: SKEP-MINOR-002 (threshold justification would strengthen methodology)
3. **Optional**: BORE-MINOR-001, BORE-MINOR-002 (narrative flow improvements, subjective)
4. **Low Priority**: FORMAT-001 (pure formatting polish)

---

*Note: These issues do not block paper acceptance but improve overall quality and rigor.*
