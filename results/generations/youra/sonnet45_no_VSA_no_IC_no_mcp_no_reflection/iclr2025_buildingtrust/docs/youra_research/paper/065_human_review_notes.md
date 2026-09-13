# Human Review Notes — MINOR Issues
**Date:** 2026-08-28  
**Round:** 1  
**Status:** FOR HUMAN REVIEW (do NOT auto-fix)

---

## MINOR Issues Deferred to Human Editor

### MINOR-B3: Competing explanations section placement
**Location:** paper/sections/05_results.md line 83 (Section 5.3)  
**Issue:** "Why r > 0.99?" appears in Results section 5.3 after clustering details. Most interesting question buried.  
**Severity:** MINOR (structure)  
**Suggestion:** Move competing explanations teaser to Introduction (after line 10): "This coupling admits two explanations: unified construct (benchmarks measure the same thing) or insufficient resolution (3 benchmarks cannot distinguish dimensions). We test these via 10-benchmark future work."  
**Action:** Human editor decide whether to reorder sections.

---

### MINOR-S4: "First large-scale" claim overstated
**Location:** paper/sections/01_introduction.md line 16 (Contribution 1)  
**Claim:** "First large-scale empirical evidence..."  
**Issue:** n=20 models × 3 benchmarks = 60 observations. Is this "large-scale"? HELM evaluates 50+ benchmarks × 30+ models.  
**Severity:** MINOR (claim inflation)  
**Fix Options:**  
  - Remove "large-scale" → "First empirical evidence..."  
  - Qualify: "First cross-benchmark correlation analysis (20 models, 3 dimensions)..."  
**Action:** Already auto-fixed in R1 (changed to "First empirical evidence"). Human can re-add "large-scale" if justified.

---

### MINOR-S5: Dual-use section feels tacked on
**Location:** paper/sections/06_discussion.md lines 93-99 (Section 6.6 Broader Impact, Dual-Use paragraph)  
**Issue:** "understanding coupling structure could inform adversarial attacks" — generic boilerplate. If no concrete dual-use risk, delete it.  
**Severity:** MINOR (filler)  
**Fix Options:**  
  - Delete Dual-Use paragraph entirely  
  - Make concrete: "Adversaries could exploit coupling — if attacking TrustfulQA transfers to AdvBench at r=0.998, one adversarial training dataset could compromise multiple benchmarks simultaneously."  
**Action:** Human editor decide whether to delete or make concrete.

---

## Grammar/Style Issues (if any)

(None flagged in Round 1 — add here if human reviewer finds typos/grammar issues)

---

## Next Steps

- Human reviewer read these 3 MINOR issues and decide:
  - Accept as-is (leave paper unchanged)
  - Apply suggested fix
  - Revise differently

- After human review, proceed to Round 2 adversarial review if convergence not achieved.
