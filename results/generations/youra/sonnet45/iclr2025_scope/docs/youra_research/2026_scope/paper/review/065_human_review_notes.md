# Human Review Notes
# Phase 6.5 Adversarial Review - MINOR Issues Collection

**Purpose:** Collect minor typos, grammar, style, and clarity issues for human review.
**Protocol:** v2.0 - MINOR issues are NOT auto-fixed, only collected for later human attention.

**Date:** 2026-03-18
**Paper:** "Measuring What LoRA Leaves Implicit"
**Total MINOR Issues:** 7

---

## Overview

All MINOR issues identified during adversarial review are listed below. These are **NOT blocking** for paper acceptance and should be addressed by human reviewers during final polish.

**Categories:**
- Typo: 1
- Grammar: 3
- Style: 1
- Clarity: 2
- Formatting: 0

---

## MINOR Issues (Round 1)

### 1. Clarity - Abstract

**Location:** Abstract, sentence 3

**Current Text:**
> "Contrary to the hypothesis, we find effective ranks of 1554-1647..."

**Issue:** "the hypothesis" could be more specific

**Suggestion:** Consider "Contrary to our hypothesis" or "Contrary to the low-rank hypothesis" for clarity

**Severity:** MINOR (Clarity)
**Blocking:** No

---

### 2. Grammar - Section 1, Paragraph 3

**Location:** Section 1, Introduction, paragraph 3

**Current Text:**
> "Parameter-efficient fine-tuning methods like LoRA have demonstrated..."

**Issue:** Subject-verb agreement (LoRA is singular)

**Suggestion:** Consider "demonstrates" if referring to LoRA specifically, or keep "have" if referring to "methods" broadly

**Severity:** MINOR (Grammar)
**Blocking:** No

---

### 3. Typo/Grammar - Section 2.1

**Location:** Section 2.1, Related Work, line 5

**Current Text:**
> "Hu et al. [2021] do not claim..."

**Issue:** Possible subject-verb agreement (author citation as singular)

**Suggestion:** Consider "does not claim" if treating citation as singular reference, or keep "do not" if treating as authors (plural)

**Severity:** MINOR (Grammar/Typo)
**Blocking:** No

---

### 4. Formatting - Section 3.1, Equation

**Location:** Section 3.1, Methodology, effective rank equation

**Current Text:**
> "Σ_{i=1}^r σ_i² / Σ_{i=1}^{rank(W)} σ_i² ≥ τ"

**Issue:** Ensure subscript/superscript formatting is consistent across all equations in paper

**Suggestion:** Check LaTeX rendering for consistency (especially in compiled PDF)

**Severity:** MINOR (Formatting)
**Blocking:** No

---

### 5. Clarity - Section 4.2, Model Description

**Location:** Section 4.2, Experimental Setup, Model subsection

**Current Text:**
> "Pre-training: Not publicly documented, but follows LLaMA-style pre-training"

**Issue:** Vague statement without citation

**Suggestion:** If Mistral paper exists, cite it. Otherwise, consider "Pre-training data not disclosed by authors" for precision

**Severity:** MINOR (Clarity)
**Blocking:** No

---

### 6. Style - Section 5.5, Rhetorical Question

**Location:** Section 5.5, Results, "Unexpected Finding" subsection

**Current Text:**
> "Why is this surprising?"

**Issue:** Informal rhetorical question style for academic paper

**Suggestion:** Consider rephrasing to "The magnitude of this discrepancy is surprising for the following reasons:" or similar formal structure

**Severity:** MINOR (Style)
**Blocking:** No

---

### 7. Grammar - Section 6, Limitations List

**Location:** Section 6, Discussion, limitations bullet list

**Current Text:** (Various limitation statements)

**Issue:** Check parallelism in bulleted list structure

**Suggestion:** Ensure all limitation bullets start with consistent grammatical structure (e.g., all noun phrases or all complete sentences)

**Severity:** MINOR (Grammar)
**Blocking:** No

---

## Summary by Category

| Category | Count | Examples |
|----------|-------|----------|
| **Clarity** | 2 | "the hypothesis" → "our hypothesis"; "Not publicly documented" vague |
| **Grammar** | 3 | Subject-verb agreement, list parallelism |
| **Style** | 1 | Rhetorical question informality |
| **Typo** | 1 | Possible citation grammar |
| **Formatting** | 0 | N/A |

**Total:** 7 MINOR issues

---

## Recommendations for Human Reviewer

1. **Priority:** All issues are cosmetic/polish-level, not blocking
2. **Timing:** Can be addressed during final camera-ready preparation
3. **Scope:** Focus on consistency (grammar, formatting) and precision (clarity)
4. **No Auto-Fix:** These were intentionally collected, not auto-fixed, per v2.0 protocol

---

## Protocol Notes (v2.0)

**Why NOT auto-fix MINOR issues?**
- Typos/grammar may be stylistic choices by authors
- Clarity suggestions are subjective
- Formatting may be template/venue-specific
- Over-aggressive auto-fixing can introduce new errors

**When to address:**
- During final human polish before submission
- After major revisions (if any) are complete
- As part of camera-ready preparation

**Do NOT block convergence on MINOR issues.**

---

**Generated:** 2026-03-18
**Review Round:** R1
**Status:** Collected for human review
