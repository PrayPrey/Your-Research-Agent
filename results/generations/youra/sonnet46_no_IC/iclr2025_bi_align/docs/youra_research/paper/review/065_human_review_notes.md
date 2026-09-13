# Human Review Notes — Phase 6.5 Adversarial Review
# Paper: "Capability or Verbosity? Disentangling the Drivers of Length-Debiased Preference in LLM Evaluation"
# Date: 2026-08-04
# Purpose: MINOR issues for human review — NOT auto-fixed

> These issues do not block paper acceptance but improve quality and credibility.
> Review before final submission.

---

## Summary by Category

| Category | Count |
|----------|-------|
| Clarity | 5 |
| Style/Precision | 4 |
| Formatting/Structure | 1 |
| Methodology (minor) | 2 |
| **Total** | **12** |

---

## Round 1 Issues

### Clarity

**HRN-001** (AC-001)  
**Section**: Abstract, Section 5.1, and table headers  
**Issue**: CI notation "Bootstrap 95% CI [0.976, 0.988]" appears without "bootstrap" qualifier in prose sentences. Pingouin also outputs a parametric CI [0.980, 1.000] which is different. Without the qualifier, readers may confuse which CI is reported.  
**Suggestion**: In every prose sentence mentioning the CI, write "bootstrap 95% CI" explicitly.  
**Example fix**: "...with bootstrap 95% CI [0.976, 0.988]" (already correct in most tables, but not in all prose).

**HRN-002** (BR-002)  
**Section**: Section 5.1  
**Issue**: "Figure 1 shows the bivariate scatter (ρ = 0.966)" — this number appears without explanation. Readers familiar with Dubois 2024 (who reported 0.94) will wonder why the bivariate is 0.966 in this paper.  
**Suggestion**: Add one sentence: "Our sample yields a bivariate Spearman ρ = 0.966 (N=223), higher than Dubois et al.'s reported 0.94, reflecting a larger and more diverse model set; our partial correlation (0.985) exceeds both."

**HRN-003** (SE-003)  
**Section**: Abstract, Introduction  
**Issue**: The comparison "partial (0.985) exceeds bivariate (0.94)" uses Dubois' 0.94, not our sample's bivariate (0.966). This is valid — it's comparing to the established baseline — but should be explicit that 0.94 is Dubois' number, not ours.  
**Suggestion**: In the abstract, change "higher than the 0.94 bivariate correlation previously reported" to "higher than both the 0.94 bivariate correlation previously reported by Dubois et al. [2024] and our own sample bivariate of 0.966."

**HRN-004** (SE-005)  
**Section**: Section 5.6 (Summary Table)  
**Issue**: H-M3 is listed as "PASS" without noting that Dunn Q1 vs Q4 p = 1.0 (non-significant). The paper correctly discusses this in Section 5.5, but the summary table is incomplete.  
**Suggestion**: In Section 5.6 summary table, change H-M3 "Key Metric" to: "KW p = 5.97e-05; Dunn Q1 vs Q4 n.s. (p=1.0)" to make the partial nature of the pass visible at a glance.

---

### Style/Precision

**HRN-005** (AC-004)  
**Section**: Abstract  
**Issue**: "capability explains ~5× more LC variance than verbosity" — actual ratio is 4.88× (|β_win|/|β_len| = 21.34/4.37). While ~5× is a reasonable approximation, the body consistently uses 4.88×.  
**Suggestion**: Change abstract to "~4.9×" for closer consistency with body, or keep "~5×" and add footnote.

**HRN-006** (AC-005)  
**Section**: Introduction, Discussion  
**Issue**: Introduction says "factor of ~4.9" (correct); Abstract says "~5×"; Discussion says "factor of ~5". Minor inconsistency across sections.  
**Suggestion**: Unify to "~4.9×" (or "~5×" consistently) throughout all sections.

**HRN-007** (SE-004)  
**Section**: Section 3.5  
**Issue**: ε² formula used (H − k + 1)/(N − k) is stated without citation. Some reviewers may question the formula or prefer a different KW effect size.  
**Suggestion**: Add citation, e.g., "ε² = (H − k + 1)/(N − k), following Tomczak & Tomczak [2014]" (or appropriate reference).

---

### Formatting/Structure

**HRN-008** (BR-001)  
**Section**: Section 4 (Experimental Setup)  
**Issue**: Section 4 partially duplicates information already in Section 3 (Methodology). Specifically:
  - Section 3.1 and Section 4.1 both describe the AlpacaEval 2.0 dataset
  - Section 3.2–3.5 and Section 4 both describe the analysis design
  - For an 8-page conference paper, this redundancy reduces information density.
**Suggestion**: Consider collapsing Section 4 into 1–2 paragraphs that frame the RQs, with a forward pointer to Section 3 for setup details. The RQ framing (RQ1–RQ5) is valuable but doesn't need its own full section.

---

### Methodology (minor)

**HRN-009** (SE-002)  
**Section**: Section 3.1, 5.1  
**Issue**: "VIF = 1.764 (threshold: VIF < 5.0), confirming OLS coefficients and partial correlations are interpretable." — The VIF < 5 threshold is an OLS heuristic. For Spearman partial correlation, VIF is not a direct diagnostic. The paper correctly uses VIF for the OLS path (H-M1) but the claim that it makes "partial correlations interpretable" is slightly overstated for the Spearman case.  
**Suggestion**: Split: "VIF = 1.764 (< 5.0) confirms OLS coefficients are interpretable (Figure 4). The low VIF also indicates low rank-correlation between win_rate and avg_length, supporting the Spearman partial correlation analysis."

---

## Priority Recommendation

1. **High Priority**: HRN-002, HRN-003 (bivariate 0.966 vs 0.94 — reviewer confusion risk)
2. **High Priority**: HRN-004 (H-M3 summary table — transparency)
3. **Medium**: HRN-005, HRN-006 (precision inconsistency)
4. **Medium**: HRN-007 (ε² citation)
5. **Lower**: HRN-001, HRN-008, HRN-009 (prose style, structure, VIF note)

---

## Round 2 Issues (from Serena MCP numerical verification)

### Clarity

**HRN-010** (AC2-002)  
**Section**: Discussion §6.1  
**Issue**: "ρ(win_rate, avg_length) ≈ 0.63" — this value is inferred from R²(win_rate ~ avg_length) = 0.4331 in H-M2 log. Pearson R = sqrt(0.4331) ≈ 0.658; Spearman ≈ 0.63 is plausible but not directly reported in any Phase 4 output.  
**Suggestion**: Add source: "ρ(win_rate, avg_length) ≈ 0.63 (inferred from OLS R²=0.433 in H-M2 residualization)" or directly compute and report Spearman ρ between win_rate and avg_length.

### Style/Precision

**HRN-011** (SE2-002)  
**Section**: §5.4  
**Issue**: "ε² = 0.883 means ~88% of LC_winrate variance...is explained by capability quartile membership" — ε² is an effect-size estimator analogue for KW, not an exact R² variance decomposition. The shorthand "variance explained" is conventional but imprecise.  
**Suggestion**: Optionally add "(effect size analogue, not exact variance partition)" as a footnote.

### Methodology (minor)

**HRN-012** (AC2-003)  
**Section**: Throughout  
**Note**: H-E1 checkpoint p_val = 1.6906e-170, H-M2 Pingouin p = 3.3813e-170 (≈2×) confirmed as one-tailed vs two-tailed. Fixed in R2 revision. This item is for completeness only — no further action needed.

---

## Updated Priority Recommendation

1. **High Priority**: HRN-002, HRN-003 (bivariate 0.966 vs 0.94 distinction)
2. **High Priority**: HRN-004 (H-M3 summary table transparency)  
3. **High Priority**: HRN-010 (source the ρ≈0.63 claim)
4. **Medium**: HRN-005, HRN-006 (precision consistency ~5× vs 4.88×)
5. **Medium**: HRN-007 (ε² formula citation)
6. **Lower**: HRN-001, HRN-008, HRN-009, HRN-011, HRN-012

---

*These issues do not block paper acceptance but improve overall quality and reduce reviewer friction.*
