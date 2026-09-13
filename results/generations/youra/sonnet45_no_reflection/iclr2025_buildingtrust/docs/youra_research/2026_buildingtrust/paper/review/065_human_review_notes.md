# Human Review Notes - Phase 6.5

**Paper:** Selective Cross-Dimensional Coupling in Language Model Trustworthiness  
**Generated:** 2026-05-11T11:39:00Z  
**Purpose:** Minor issues for human review (NOT auto-fixed by Revision Agent)

---

## Overview

This document collects **16 minor issues** identified during Phase 6.5 Adversarial Review that should be addressed by a human reviewer during final polish. These issues were intentionally NOT auto-fixed by the Revision Agent, as human judgment produces better results for style, clarity, and formatting improvements.

**Issue Breakdown:**
- Clarity: 8 issues
- Style: 4 issues
- Formatting: 2 issues
- Grammar: 1 issue
- Typo: 1 issue

---

## Clarity Issues (8)

### 1. Abstract - Model Enumeration
**Location:** Abstract, line 13  
**Current:** "Fine-tuning transformer models for truthfulness..."  
**Note:** Consider restoring "three transformer models (GPT-2, OPT, Pythia)" for specificity vs. keeping generic "transformer models" for flow  
**Decision:** Human choice based on journal style preference

### 2. Introduction - Redundant Phrase
**Location:** Introduction, paragraph 2  
**Current:** "This evaluation culture treats dimensions as if they were independent features"  
**Suggestion:** Remove "as if they were" → "treats dimensions as independent features"  
**Rationale:** More direct, clearer

### 3. Methodology - Repeated Phrase
**Location:** Methodology, paragraph 1 (and elsewhere)  
**Current:** "perturbation-based correlation analysis transforms benchmark variance from noise into signal" (appears 3×)  
**Note:** Phrase repeated verbatim in multiple locations  
**Suggestion:** Keep first instance, rephrase subsequent occurrences

### 4. Experiments - Duplicate Definition
**Location:** Experiments, H-M2 section  
**Current:** "Centered Kernel Alignment (CKA) similarity" defined here  
**Note:** CKA already defined in Methodology section  
**Suggestion:** Remove definition here, use "CKA similarity" only

### 5. Methodology - Replicate Count Inconsistency
**Location:** Methodology, paragraph 3  
**Current:** "N=3-5 replicates per configuration"  
**Note:** Later sections specify "3 replicates" (H-E1, H-M3) vs "5 replicates" (H-M4)  
**Suggestion:** Specify range rationale or use consistent count

### 6. Experiments - Vague Pipeline Description
**Location:** Experiments, General Protocol  
**Current:** "lm-evaluation-harness for baselines, consistent inference pipelines for post-intervention"  
**Note:** "Consistent inference pipelines" is vague  
**Suggestion:** Clarify what these pipelines are or cite implementation

### 7. Discussion - Missing Citation
**Location:** Discussion, Broader Impact section  
**Current:** "Defenses against such attacks (multi-objective monitoring, robust evaluation suites) are standard practice"  
**Note:** "Standard practice" claim unsupported  
**Suggestion:** Add citation or rephrase as "emerging practice"

### 8. Discussion - Paragraph Transitions
**Location:** Discussion, Limitations section  
**Note:** Five limitation paragraphs lack smooth transitions  
**Suggestion:** Add transition phrases between limitation items

---

## Style Issues (4)

### 9. Introduction - Informal Tone
**Location:** Introduction, paragraph 4  
**Current:** "The mechanism behind selective coupling offers an intuitive explanation"  
**Note:** "Offers an intuitive explanation" slightly informal for academic paper  
**Suggestion:** "The mechanism underlying selective coupling provides a theoretical explanation"

### 10. Discussion - Emphasis
**Location:** Discussion, paragraph 1  
**Current:** "partial representation subspace overlap"  
**Note:** Key theoretical claim could benefit from emphasis  
**Suggestion:** Italicize or bold for emphasis

### 11. Results - Code Syntax
**Location:** Results, H-M2 section  
**Current:** "blocks.{0-11}.attn.hook_pattern"  
**Note:** Code syntax in academic paper  
**Suggestion:** Rephrase as "attention layers 0-11" or "attention patterns across 12 layers"

### 12. Conclusion - Not Reviewed
**Location:** Conclusion section  
**Note:** Conclusion was not included in review excerpt  
**Action:** Human should review Conclusion for consistency with revised Abstract

---

## Formatting Issues (2)

### 13. Results - Repeated Values
**Location:** Results, H-E1 section  
**Current:** "ρ=1.000, p<0.0001" appears 3× in same paragraph  
**Note:** Redundant repetition  
**Suggestion:** Consolidate into single statement or table

### 14. Results - Seed Data Format
**Location:** Results, H-M3 section  
**Current:** "seed 42: fairness +0.2%, seed 43: +0.8%, seed 44: +0.8%"  
**Note:** Inline data hard to read  
**Suggestion:** Use table format for per-seed results

---

## Grammar Issues (1)

### 15. Abstract - Nested Parenthetical
**Location:** Abstract, line 14  
**Current:** "(100% layer coverage, mean CKA change = 0.143)"  
**Note:** Parenthetical within sentence already containing subordinate clause creates confusion  
**Suggestion:** Rephrase to avoid nested structure

---

## Typo Issues (1)

### 16. Results - Dataset Name Capitalization
**Location:** Results, H-M4 section  
**Current:** "(EleutherAI's deduplicated pile vs. standard web text)"  
**Issue:** "pile" should be capitalized as "Pile" (proper dataset name)  
**Correction:** "EleutherAI's deduplicated Pile"

---

## Recommendations for Human Reviewer

### High Priority (Affects Clarity)
1. Fix nested parenthetical in Abstract (#15)
2. Resolve replicate count inconsistency (#5)
3. Clarify "consistent inference pipelines" (#6)
4. Add transitions between limitation paragraphs (#8)

### Medium Priority (Improves Readability)
5. Consolidate repeated correlation values (#13)
6. Table format for seed data (#14)
7. Remove "as if they were" (#2)
8. Deduplicate CKA definition (#4)

### Low Priority (Polishing)
9. Repeated phrase variation (#3)
10. Code syntax → prose (#11)
11. Informal tone revision (#9)
12. Emphasis on key terms (#10)

### Quick Fixes
13. Capitalize "Pile" dataset name (#16)
14. Citation or rephrase "standard practice" (#7)
15. Review Conclusion consistency (#12)
16. Model enumeration style choice (#1)

---

## Final Note

These issues were identified by the v2.0 Adversarial Review system but intentionally left for human review. AI auto-fixing of style and clarity issues can introduce new errors or alter authorial voice. Human review ensures polishing maintains paper quality while preserving intended meaning.

**Status:** Ready for human review after convergence check confirms no FATAL/MAJOR issues remain.
