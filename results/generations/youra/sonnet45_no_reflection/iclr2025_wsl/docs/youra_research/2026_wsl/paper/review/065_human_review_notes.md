# Human Review Notes

> **Purpose:** Minor issues collected during adversarial review for human review.
> **v2.0:** These issues are NOT auto-fixed by AI to preserve author voice and subjective judgment.

**Generated**: 2026-05-12T11:30:00Z
**Rounds Completed**: 2
**Total MINOR Issues**: 10

---

## Summary by Category

| Category | Count | Priority |
|----------|-------|----------|
| Clarity | 3 | HIGH |
| Style | 2 | MEDIUM |
| Formatting | 2 | LOW |
| Terminology | 3 | MEDIUM |

---

## Round 1 Issues (6 MINOR)

### Clarity Issues

**MINOR-1: Jargon Without Initial Definition**
- **Location**: Introduction, line 14
- **Issue**: "factor out architecture-specific coordinate conventions" uses jargon without definition
- **Suggested Fix**: Add parenthetical: "coordinate conventions (neuron ordering, layer indexing)"
- **Priority**: MEDIUM

**MINOR-2: "Kernel Robustness" Opaque Name**
- **Location**: Methodology, line 162
- **Issue**: Metric name not self-explanatory
- **Suggested Fix**: Add parenthetical: "Kernel Robustness (permutation invariance test)"
- **Priority**: LOW

### Style Issues

**MINOR-3: Redundant Figure Reference**
- **Location**: Results, line 290
- **Issue**: "Figure 1 shows training curves" then caption "Figure 1: Training curves showing..."
- **Suggested Fix**: Simplify one or the other
- **Priority**: LOW

### Formatting Issues

**MINOR-4: Formula Formatting Inconsistency**
- **Location**: Throughout, especially line 94
- **Issue**: Inconsistent `\left \right` sizing usage
- **Priority**: LOW

**MINOR-5: Metadata in Paper Body**
- **Location**: Final line 477
- **Issue**: "Result Type: Negative Result with Systematic Failure Analysis" appears as text
- **Suggested Fix**: Remove from main text or move to YAML frontmatter
- **Priority**: HIGH

### Terminology Issues

**MINOR-6: Speculative Presented as Fact**
- **Location**: Discussion, line 402
- **Issue**: "Obstacle 1: Permutation groups may be incompatible" - no proof provided
- **Suggested Fix**: Add "Potential" qualifier
- **Priority**: MEDIUM

---

## Round 2 Issues (4 MINOR)

### Clarity Issues

**MINOR-7: Statistical Significance Discussion Missing**
- **Location**: Results section (lines 264-356)
- **Issue**: Frozen-K 0.31pp gap acknowledged as "could reflect noise" but not quantified
- **Suggested Addition**: "Without multiple runs or statistical significance testing, we cannot definitively attribute the 0.31pp gap to architecture embeddings rather than random variation."
- **Priority**: HIGH

### Terminology Issues

**MINOR-8: Error Distribution Statistics Incomplete**
- **Location**: Results, line 314
- **Issue**: "12% (best case) to 35% (worst case)" - unclear if min/max or percentiles
- **Suggested Fix**: Clarify as "12% (minimum) to 35% (maximum)"
- **Priority**: MEDIUM

**MINOR-9: Single-Seed Sensitivity Caveat Missing**
- **Location**: Experiments line 259, Limitations line 416
- **Issue**: Paper states "fixed random seeds (seed=42)" but no seed sensitivity discussion
- **Suggested Addition to Limitation 2**: "While the 0% kernel robustness failure is unlikely seed-dependent given its magnitude, the marginal frozen-K result (0.31pp gap) may be sensitive to initialization."
- **Priority**: MEDIUM

**MINOR-10: Task Scope Limitation Not Listed**
- **Location**: Discussion Limitations section (lines 410-430)
- **Issue**: Ground truth mentions "classification tasks" but paper Limitations doesn't
- **Suggested Addition**: "Our synthetic model zoo uses classification-task structures; weight-space properties may differ for generative models, reinforcement learning policies, or other task families."
- **Priority**: LOW

---

## Recommended Priority for Human Review

### Priority 1: Fix First (High Visibility or Scientific Rigor)
1. **MINOR-5**: Remove metadata from paper body (line 477)
2. **MINOR-7**: Add statistical significance caveat for frozen-K result

### Priority 2: Fix Second (Clarity and Precision)
3. **MINOR-1**: Define "coordinate conventions" jargon
4. **MINOR-6**: Add "Potential" to speculative obstacle
5. **MINOR-9**: Add seed sensitivity caveat to Limitations

### Priority 3: Consider Fixing (Readability)
6. **MINOR-8**: Clarify error distribution terminology
7. **MINOR-10**: Add task scope limitation

### Priority 4: Optional (Aesthetic)
8. **MINOR-2**: Add parenthetical to "Kernel Robustness"
9. **MINOR-3**: Fix redundant figure reference
10. **MINOR-4**: Standardize formula formatting

---

## Implementation Guide

**Estimated Time**: 30-45 minutes for Priority 1-2
**Word Count Impact**: ~80-130 words (+0.12-0.19%)

**Workflow**:
1. Address Priority 1 (metadata, statistical caveat)
2. Address Priority 2 (definitions, qualifiers)
3. Evaluate Priority 3-4 based on word count budget

---

**Publication Readiness**: 95% - Ready after MINOR issue review
