# Human Review Notes - Round 1 MINOR Issues

**Paper:** Gradient-Based Jacobian Stable Rank Regularization Fails Catastrophically  
**Date:** 2026-05-12  
**Status:** 7 MINOR issues collected for human review (NOT auto-fixed)

---

## Overview

These issues involve style, clarity, formatting, and presentation decisions that require human judgment. Per adversarial review protocol, MINOR issues were NOT auto-fixed by the Revision Agent. All MAJOR issues (M1-M3) have been resolved in the R1 revision.

---

## MIN-1: Introduction Length

**Severity:** MINOR - Clarity/Readability  
**Location:** Section 1 (Introduction)

**Issue:**
Section 1 spans 7 dense paragraphs. Paragraphs 4-5 (root cause preview) may be skimmed by bored reviewers.

**Current Text (Paragraphs 4-5):**
> Root cause analysis revealed three compounding failure modes. First, Hutchinson trace estimation with 10 probes proved insufficient for 768-dimensional embeddings—theoretical analysis establishes O(1/ε²) sample complexity for ε-accuracy, which for our target coefficient of variation below 15% implies approximately 100+ probes, but our implementation returned degenerate zero values. Second, randomized power iteration with 5 iterations failed to converge for residual-corrected Jacobians in the presence of LayerNorm and attention nonlinearities. Third, and most critically, differentiating through the spectral estimation procedure via PyTorch autodiff introduced gradient pathologies in deep computation graphs—the regularization term's gradient magnitude exceeded the cross-entropy loss by orders of magnitude, overwhelming adaptive lambda tuning and causing training collapse.
>
> Despite this comprehensive implementation failure, the negative result carries positive scientific value...

**Reviewer Suggestion:**
Consider condensing paragraphs 4-5 or adding subheadings like:
- "Failure Modes Preview"
- "Contributions"

**Human Decision Required:**
1. Keep current structure (comprehensive intro with all details upfront)
2. Add subheadings for scanability
3. Condense root cause preview to 2-3 sentences with forward reference: "We identify three root causes (Section 6.1): Hutchinson variance explosion, power iteration non-convergence, and autodiff gradient pathologies."

**Recommendation:** Option 3 (condense) improves readability without losing content.

---

## MIN-2: Related Work Positioning

**Severity:** MINOR - Structure  
**Location:** Section 2 (Related Work)

**Issue:**
The "Positioning Our Work" subsection appears at the END of Section 2 (after 3 pages). Bored readers want to know "how is this different?" immediately.

**Current Structure:**
1. Spectral Normalization
2. Low-Rank Adaptation
3. KV Cache Compression
4. Hutchinson Trace
5. State Space Models
6. **Positioning Our Work** (at end)

**Reviewer Suggestion:**
Front-load positioning subsection to appear second (after a brief overview paragraph).

**Human Decision Required:**
1. Keep current order (traditional background-then-positioning)
2. Move "Positioning Our Work" to beginning of Section 2
3. Add brief positioning summary at start, keep full subsection at end

**Recommendation:** Option 3 (brief summary upfront, full details at end) balances engagement with completeness.

---

## MIN-3: Acronym Overload

**Severity:** MINOR - Readability  
**Locations:** Multiple sections

**Issue:**
Several acronyms used without first defining or used heavily:
- **CLM** (causal language modeling) - first used in Section 3.6 without definition
- **CV** (coefficient of variation) - defined but used heavily, occasionally substitute "variance" for readability
- **PoC** (proof of concept) - used without spelling out at first use

**Current Text Examples:**
> "The optimizer effectively ignored the CLM loss (magnitude ~10)..." [Section 5.3]

> "PoC budget" [Section 3.2]

**Human Decision Required:**
1. Add first-use definitions for all acronyms
2. Reduce acronym usage (spell out occasionally for variety)
3. Keep as-is (assumes informed ML audience)

**Recommendation:** Option 1 (define all acronyms at first use) for ICML submission standards.

**Specific Fixes Needed:**
- CLM: Define as "causal language modeling (CLM)" at first use
- PoC: Define as "proof-of-concept (PoC)" at first use
- CV: Consider occasionally using "measurement variance" or "estimation reliability" for variety

---

## MIN-4: Figure Caption Length

**Severity:** MINOR - Formatting  
**Locations:** Figures 3 and 4

**Issue:**
Figure 3 and 4 captions are verbose (6+ lines), making them harder to scan.

**Current Text - Figure 3:**
> "Training loss evolution over 5000 steps. Baseline (blue) exhibits smooth monotonic decrease characteristic of convergent language model training. Regularized model (red) shows catastrophic loss explosion to negative values, driven by regularization term overwhelming causal language modeling loss. Note the log-scale y-axis—the actual deviation spans orders of magnitude."

**Current Text - Figure 4:**
> "Validation perplexity trajectories. Baseline (blue) converges smoothly from initial randomness to 59.34. Regularized model (red) explodes catastrophically to 45,792.62, diverging from baseline by 77,065\%. The ±1\% target envelope (gray shaded) highlights the extreme deviation. Perplexity explosion begins early (step ~1000) and accelerates, indicating instability is not a late-training phenomenon but a fundamental incompatibility."

**Reviewer Suggestion:**
Move some caption details to main text, keep captions concise (<3 lines).

**Human Decision Required:**
1. Keep current captions (self-contained figures)
2. Shorten captions, move detail to main text
3. Keep as-is but reformat for better line breaks

**Recommendation:** Option 2 (shorten captions) for cleaner presentation.

**Suggested Shortened Captions:**

**Figure 3:**
> "Training loss evolution over 5000 steps. Baseline (blue) converges smoothly, while regularized model (red) exhibits catastrophic loss explosion to negative values. Note log-scale y-axis."

**Figure 4:**
> "Validation perplexity trajectories. Baseline (blue) converges to 59.34, while regularized model (red) explodes to 45,792.62 (+77,065% deviation). Gray shaded region shows ±1% target envelope."

---

## MIN-5: Repetition in Discussion

**Severity:** MINOR - Conciseness  
**Location:** Section 6.1 (Discussion - Failure Mode Analysis)

**Issue:**
Section 6.1 repeats some root cause content already previewed in Section 1 (Introduction).

**Current Structure:**
- Section 1, Paragraph 6: "Root cause analysis revealed three compounding failure modes. First, Hutchinson... Second, power iteration... Third, autodiff..."
- Section 6.1: Full detailed analysis of the same three root causes

**Reviewer Suggestion:**
Forward reference in Introduction: "We identify three root causes (Section 6.1)..." and expand only in Discussion.

**Human Decision Required:**
1. Keep current repetition (reinforces key findings)
2. Condense intro preview, expand only in Discussion
3. Add explicit cross-reference: "As previewed in Introduction, we now detail..."

**Recommendation:** Option 2 (condense intro) reduces redundancy. The Introduction should hook and overview; Discussion should analyze deeply.

---

## MIN-6: Notation Inconsistency

**Severity:** MINOR - Mathematical Consistency  
**Locations:** Multiple sections

**Issue:**
Inconsistent use of J_ℓ (full Jacobian) vs J̃_ℓ (residual-corrected Jacobian) without clear transition.

**Current Pattern:**
- Section 3.1 defines J̃_ℓ = J_ℓ - I
- Earlier sections use J_ℓ generically
- Sometimes unclear which is meant

**Reviewer Suggestion:**
After defining J̃_ℓ in Section 3.1, always use J̃_ℓ for residual-corrected version. When referring to uncorrected Jacobian, explicitly note "full Jacobian J_ℓ (with identity component)".

**Human Decision Required:**
1. Audit all uses of J_ℓ vs J̃_ℓ for consistency
2. Add inline notes when switching notation
3. Keep as-is (assumes reader tracks from context)

**Recommendation:** Option 1 (audit and fix) for mathematical rigor.

**Locations to Check:**
- Section 2: Generic Jacobian discussion (before residual correction introduced)
- Section 3: Should use J̃_ℓ after definition
- Section 5-6: Should consistently use J̃_ℓ when discussing implementation

---

## MIN-7: Citation Style Inconsistency

**Severity:** MINOR - Formatting (Camera-Ready)  
**Locations:** Throughout paper

**Issue:**
Inconsistent citation formatting:
- Sometimes: "Bekas et al., 2007"
- Sometimes: "Bekas et al. (2007)"
- Conference proceedings: "In X" vs "X" inconsistent

**Examples:**
> "Bekas et al., 2007" [Section 2]  
> "Bekas et al. (2007)" [Section 3]

> "In *Neural Information Processing Systems*" [References]  
> "*arXiv preprint arXiv:...*" [References]

**Human Decision Required:**
1. Standardize to ICML style guide (parenthetical vs narrative citations)
2. Defer to camera-ready formatting phase
3. Keep as-is (close enough for review)

**Recommendation:** Option 2 (defer to camera-ready) since this is R1 review phase, not final submission.

**Note for Camera-Ready:**
- Use parenthetical (Author, Year) in prose
- Use narrative Author (Year) when author is subject
- Standardize conference proceedings format

---

## Summary for Human Reviewer

| Issue | Type | Priority | Estimated Time |
|-------|------|----------|----------------|
| MIN-1 | Clarity | Medium | 10 min |
| MIN-2 | Structure | Medium | 15 min |
| MIN-3 | Readability | High | 5 min |
| MIN-4 | Formatting | Low | 10 min |
| MIN-5 | Conciseness | Medium | 10 min |
| MIN-6 | Math Notation | High | 20 min |
| MIN-7 | Formatting | Low | Camera-ready |

**Total Estimated Time:** ~1 hour for MIN-1 through MIN-6, defer MIN-7 to camera-ready.

**Priority Order:**
1. **MIN-3** (Acronyms) - Quick fix, high impact on readability
2. **MIN-6** (Notation) - Mathematical rigor for ML audience
3. **MIN-1** (Intro Length) - Improves engagement
4. **MIN-5** (Repetition) - Reduces redundancy
5. **MIN-2** (Related Work) - Structure improvement
6. **MIN-4** (Captions) - Polish for figures
7. **MIN-7** (Citations) - Defer to camera-ready

---

**Notes Generated by:** Revision Agent  
**Date:** 2026-05-12  
**Status:** Ready for human copy-editing phase
