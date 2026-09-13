# Adversarial Review - Round {N}

**Paper**: {paper_title}
**Reviewer**: Adversary Agent
**Date**: {ISO8601}
**Round Focus**: {focus_areas}

---

## Executive Summary

- **FATAL Issues**: {count}
- **MAJOR Issues**: {count}
- **MINOR Issues**: {count}
- **Recommendation**: {MAJOR_REVISION / MINOR_REVISION / ACCEPT_WITH_CHANGES}

### Overall Assessment

{2-3 sentence summary of paper's main strengths and weaknesses}

---

## FATAL Issues (Must Fix)

> Issues that would cause immediate rejection if not addressed

### FATAL-001: {Short Title}

**Location**: Section {X.Y}, Line {N}
**Category**: {logical_conflict / methodology_contradiction / novelty_overclaim / ...}

**The Claim**:
> "{exact quote from paper}"

**The Problem**:
{Clear explanation of why this is fundamentally wrong or contradictory}

**Evidence**:
- {Citation or cross-reference 1}
- {Citation or cross-reference 2}

**Why This is FATAL**:
{Explain why this cannot be ignored - e.g., "This contradicts the paper's core contribution"}

**Suggested Fix**:
{Specific recommendation for how to resolve}

---

### FATAL-002: {Short Title}

{Same format}

---

## MAJOR Issues (Should Fix)

> Issues that significantly weaken the paper but are addressable

### MAJOR-001: {Short Title}

**Location**: Section {X.Y}
**Category**: {baseline_fairness / numerical_inconsistency / overclaim / ...}

**The Claim**:
> "{exact quote from paper}"

**The Problem**:
{Clear explanation of the issue}

**Evidence**:
- {Source 1}
- {Source 2}

**Impact on Paper**:
{How this weakens the contribution if not addressed}

**Suggested Fix**:
{Recommendation - may be simpler than FATAL fixes}

---

### MAJOR-002: {Short Title}

{Same format}

---

## MINOR Issues (Optional Fix)

> Issues that are noticeable but don't significantly impact the paper

### MINOR-001: {Short Title}

**Location**: Section {X.Y}
**Issue**: {Brief description}
**Suggested Fix**: {Brief suggestion}

### MINOR-002: {Short Title}

**Location**: Section {X.Y}
**Issue**: {Brief description}
**Suggested Fix**: {Brief suggestion}

---

## Issues NOT Found (Clean Areas)

The following aspects of the paper passed review without issues:

- **{Section/Aspect 1}**: {Why it's solid}
- **{Section/Aspect 2}**: {Why it's solid}
- **{Section/Aspect 3}**: {Why it's solid}

---

## Cross-Reference Analysis

### Claims vs Evidence Matrix

| Claim | Location | Supporting Evidence | Verdict |
|-------|----------|---------------------|---------|
| {Claim 1} | Section X | {Evidence location} | {SUPPORTED / WEAK / UNSUPPORTED} |
| {Claim 2} | Section Y | {Evidence location} | {SUPPORTED / WEAK / UNSUPPORTED} |

### Section Consistency Check

| Section A | Section B | Consistency | Notes |
|-----------|-----------|-------------|-------|
| Introduction | Methodology | {YES / CONFLICT} | {details} |
| Methodology | Experiments | {YES / CONFLICT} | {details} |
| Abstract | Results | {YES / CONFLICT} | {details} |

---

## Summary for Revision Agent

### Priority Order for Fixes

1. **FATAL-001**: {title} - {one-line description}
2. **FATAL-002**: {title} - {one-line description}
3. **MAJOR-001**: {title} - {one-line description}
4. **MAJOR-002**: {title} - {one-line description}
...

### Key Conflicts to Resolve

- {Conflict 1}: Section {A} claims X, but Section {B} claims Y
- {Conflict 2}: {description}

### Numbers to Verify/Fix

- {Number 1}: Currently {X}, should be {Y} or explained
- {Number 2}: Currently {X}, inconsistent with {source}

### Sections Requiring Most Work

1. **Section {X}**: {reason}
2. **Section {Y}**: {reason}

---

## Reviewer Confidence

| Aspect | Confidence | Notes |
|--------|------------|-------|
| Structural issues found | {HIGH / MEDIUM / LOW} | {explanation} |
| Numerical issues found | {HIGH / MEDIUM / LOW} | {explanation} |
| No false positives | {HIGH / MEDIUM / LOW} | {explanation} |

---
