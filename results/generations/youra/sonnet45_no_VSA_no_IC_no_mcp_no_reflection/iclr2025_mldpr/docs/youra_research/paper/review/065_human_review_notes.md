# Human Review Notes: MINOR Issues (Not Auto-Fixed)

**Paper Version**: `06_paper_r1.md`  
**Generated**: 2026-08-28  
**Purpose**: Collect MINOR (typography, style, formatting) issues for human batch-fixing

---

## Typography Issues

### H1: Word Count Metadata in Paper Text
**Location**: End of each section (Abstract, Introduction, Related Work, etc.)  
**Issue**: Lines like `**Word count:** ~725 words` appear in paper text  
**Fix**: Delete all word count metadata lines before submission  
**Effort**: 30 seconds (Find: `**Word count:**`, Delete all)  
**Priority**: LOW (trivial copy-paste artifact, zero substance impact)

---

### H2: CI Format Inconsistency
**Location**: Results §5.1 Table 1  
**Current**: `83.3%-100.0%` (% on both bounds)  
**Standard**: `83.3-100.0%` (% only on second bound)  
**Fix**: Standardize to one format throughout Table 1  
**Effort**: 10 seconds (three table cells)  
**Priority**: LOW (pure style, no accuracy impact)  
**Note**: R1 revision did NOT touch this—original inconsistency persists

---

### H3: P-value Precision Inconsistency
**Location**: Results §5.3 Table 2  
**Issue**: Mixed notation formats:
- ImageNet: `1.5×10⁻⁸` (scientific notation, 2 sig figs)
- GLUE: `2.6×10⁻⁴` (scientific notation, 2 sig figs)
- SQuAD: `1.4×10⁻²` (scientific notation, 2 sig figs) ← **R1 FIXED from 0.014**

**Fix**: ALREADY CONSISTENT in R1 revision (all scientific notation now)  
**Status**: ✅ RESOLVED in R1  
**Action**: No further fix needed

---

## Redundancy Issues

### H4: Results §5.7 "Aggregate Results" Redundant
**Location**: Results §5.7  
**Issue**: Section restates pass/fail counts already shown in §5.1-5.6:
```
- Total hypotheses: 7
- Fully validated: 6
- Failed: 1 (h-m3 precision)
- Overall pass rate: 85.7%
```
This information is already obvious from reading prior sections.

**Fix Options**:
1. **Delete §5.7 entirely** (preferred—cleanest)
2. **Merge into Discussion §6.1 intro** (one sentence: "Six of seven hypotheses validated...")
3. **Keep but compress** (reduce from 6 lines to 1-2 sentences)

**Effort**: 1 minute  
**Priority**: MEDIUM (affects flow/pacing, though not blocking publication)  
**Note**: Bored Reviewer lost attention here—removal improves pacing

---

### H5: Discussion §6.3 "Broader Impact" Generic
**Location**: Discussion §6.3  
**Issue**: Content is generic anomaly detection boilerplate:
- Positive: reduces waste ✓
- Negative: premature deprecation risk ✓
- Mitigation: conservative thresholds ✓

Not specific to benchmark saturation—could apply to any detection system.

**Fix Options**:
1. **Delete §6.3** (preferred—bloat reduction)
2. **Compress to 2-3 sentences in Conclusion** (keep substance, cut padding)
3. **Add benchmark-specific details** (e.g., "gaming risk: researchers avoid new saturated benchmark Foo to chase Bar leaderboard")

**Effort**: 2 minutes  
**Priority**: LOW (box-checking content, but harmless)  
**Note**: Adversary flagged as generic but not blocking—safe to defer

---

### H6: Discussion §6.4 "Unexpected Findings" Redundant
**Location**: Discussion §6.4  
**Issue**: Repeats content from Results §5.6 (citation precision failure) and Limitation L4 (per-benchmark calibration)

**Current content**:
- Per-benchmark calibration unexpected → synthetic artifact (already in L4)
- Citation precision failure → window misalignment (already in §5.6 and L3)

**Fix**: Delete §6.4 entirely (information covered elsewhere)  
**Effort**: 30 seconds  
**Priority**: LOW (redundant but not harmful)

---

## Clarity Issues

### H7: Abstract FAIR-B Acronym Unexplained
**Location**: Abstract (original paper)  
**Status**: ✅ RESOLVED in R1—"FAIR-B framework" terminology removed entirely  
**Action**: No further fix needed

---

## Summary Table

| Issue | Location | Severity | Status | Effort | Priority |
|-------|----------|----------|--------|--------|----------|
| H1 | All sections | Style | OPEN | 30s | LOW |
| H2 | Results §5.1 | Style | OPEN | 10s | LOW |
| H3 | Results §5.3 | Style | FIXED | - | - |
| H4 | Results §5.7 | Flow | OPEN | 1min | MEDIUM |
| H5 | Discussion §6.3 | Substance | OPEN | 2min | LOW |
| H6 | Discussion §6.4 | Redundancy | OPEN | 30s | LOW |
| H7 | Abstract | Clarity | FIXED | - | - |

**Total Open**: 5 issues  
**Estimated Fix Time**: 4 minutes total  
**Recommended Batch Fix Order**: H4 (best ROI for pacing) → H6 → H5 → H1 → H2

---

## Detailed Fix Checklist

When batch-fixing, execute in this order:

### Step 1: Delete Redundant Sections (High ROI)
- [ ] Delete Results §5.7 entirely
- [ ] Delete Discussion §6.4 entirely
- [ ] Delete Discussion §6.3 OR compress to 2 sentences in Conclusion

### Step 2: Clean Metadata (Fast)
- [ ] Find all `**Word count:**` lines and delete (7 instances across sections)
- [ ] Standardize Table 1 CI format: `83.3-100.0%` (3 table cells)

### Total Time: ~4 minutes  
### Impact: Improves pacing (H4 removal), reduces bloat (H5-H6 removal), polishes presentation (H1-H2)

---

## Notes for Human Reviewer

1. **H3 already fixed**: R1 revision standardized p-values to scientific notation
2. **H7 already fixed**: R1 revision removed FAIR-B terminology
3. **Priority inversion**: H4 (MEDIUM priority) has better ROI than H1-H2 (LOW priority trivial fixes)
4. **Optional**: Could leave H5-H6 intact if journal has minimum section requirements (unlikely for Discussion subsections)

---

## Why Not Auto-Fixed in R1?

**Ponytail Mode Principle**: Don't waste agent effort on trivial style fixes human can batch in <5 minutes. Focus revision budget on substance (FATAL/MAJOR issues). 

MINOR issues are:
- Non-blocking (won't cause rejection)
- Low-value (no substance change)
- Fast for human (batch Find & Replace, section deletion)
- High cost for agent (requires multiple Edit calls, careful line counting, verification reads)

Human batch-fix effort: 4 minutes  
Agent auto-fix effort: 15-20 minutes (6-8 Edit calls, verification reads)  

**ROI ratio**: 4:1 in favor of human batch-fixing

---

**Human Review Notes Completed**: 2026-08-28  
**Recommendation**: Batch-fix H4, H6, H1 before final submission (5 minutes total). H2, H5 optional.
