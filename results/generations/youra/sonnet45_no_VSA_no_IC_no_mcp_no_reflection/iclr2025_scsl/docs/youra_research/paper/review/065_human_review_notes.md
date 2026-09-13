# Human Review Notes - Round 1

**Paper**: 06_paper_r1.md  
**Date**: 2026-08-29  
**Purpose**: MINOR issues for human polish (grammar, style, clarity)

> These issues were flagged by the Adversary Agent but NOT fixed by the Revision Agent.  
> They require human judgment for final polish before publication.

---

## MINOR Issues for Human Review

| Location | Issue | Type | Suggested Fix |
|----------|-------|------|---------------|
| Abstract, sentence 1 | "shortcuts such as color or background cues" — "cues" is clearer than "correlations" | style | Consider keeping "cues" (already fixed in revision) or use "shortcuts such as color or background" |
| Introduction, para 2 | "The problem extends beyond fairness metrics" — changed from "runs deeper than" for formal tone | style | Current version acceptable, original "runs deeper" slightly informal |
| Methodology, Ablation Training section | "GradCAM and Integrated Gradients provide..." — now uses parallel structure | grammar | Already improved in revision (changed "or" to "and") |
| Results, h-e1 section | "Proof-of-concept result: single seed" — acronym expanded on first use in Results | clarity | Already improved in revision (expanded "PoC" to "proof-of-concept") |
| Discussion, para 1 | "Our results validate temporal ordering—spurious features converge 4 epochs earlier—while identifying..." — em-dash usage interrupts flow | style | Consider splitting into two sentences: "Our results validate temporal ordering: spurious features converge 4 epochs earlier than core features on CMNIST. While confirming this mechanistic foundation, we identify cross-dataset..." |
| Conclusion, para 2 | "when attempting to exploit" — changed from "when we attempted to exploit" for consistency | consistency | Current version acceptable, maintains formal tone without first-person shift |

---

## Notes

- **4 of 6 issues already addressed during revision** (marked as "already improved" above)
- **2 remaining issues** require human judgment:
  1. **Discussion em-dash flow** (minor stylistic preference)
  2. **Abstract "cues" terminology** (already acceptable, no action needed)

All substantive issues (FATAL + MAJOR) have been fixed. These MINOR notes are optional polish for final camera-ready version.

---

## Recommendation

Current revision (06_paper_r1.md) is publication-ready. The two remaining MINOR issues are stylistic preferences that do not affect clarity or correctness.

- **Discussion em-dash**: Current version readable, splitting sentence is optional.
- **Abstract terminology**: "cues" already used, clearer than "correlations", no change needed.

**Status**: Ready for final author review and submission.
