# Human Review Notes — Phase 6.5 Adversarial Review

Generated: 2026-08-20
Phase 6.5 Round: R1

These are MINOR issues not auto-fixed. Require human judgment.

---

## MINOR-01: "Three nested layers" claim inconsistency

**Location:** Introduction, paragraph 2, first sentence.  
**Issue:** "The problem has three nested layers." But only two layers are labeled explicitly — "At the surface" (layer 1) and "Beneath this surface lies a deeper gap" (layer 2). No third layer is identified.  
**Options:**
  - Change "three" to "two" nested layers.
  - Add a third explicit layer (e.g., the measurement/infrastructure gap as layer 3).

---

## MINOR-02: Wikipedia std rounding inconsistency

**Location:** Section 5.2, top-variance domain table.  
**Issue:** Wikipedia std shown as 0.0086 but ground truth value is 0.00858. Pile-CC is shown as 0.0266 (4 sig figs). Inconsistent precision.  
**Options:**
  - Change Wikipedia to 0.00858 for consistency.
  - Or change Pile-CC to 0.027 for uniform 2 sig fig presentation.

---

## MINOR-03: Pile-CC confound caveat missing from Section 5.3

**Location:** Section 5.3, preliminary 70M result interpretation.  
**Issue:** Pile-CC multicollinearity confound (Pile-CC has highest variance 0.0266 and co-varies with Wikipedia) is discussed in Section 6.1 discussion but not mentioned at the point where the 70M result is interpreted in Section 5.3.  
**Options:**
  - Add one sentence in Section 5.3 after N=10 artifact explanation: "Additionally, Pile-CC (std=0.0266, highest variance domain) co-varies with Wikipedia in training, meaning univariate Spearman ρ(Wikipedia, benchmark) conflates Wikipedia and Pile-CC effects."

---

## MINOR-04: "Books" vs "BookCorpus2" terminology

**Location:** Introduction paragraph 5 ("entity density distinguishes Wikipedia from Books"), Results 5.1 table ("Wikipedia (0.2553) >> Books (0.0075)").  
**Issue:** The paper alternates between "Books" (shorthand) and "BookCorpus2" (precise domain name). "Books3" is a different domain (the one with zero exposure). Using "Books" for both BookCorpus2 (in h-m1) and as shorthand for Books3 (in h-m2/h-m3 context) could confuse readers.  
**Options:**
  - Use "BookCorpus2" consistently when referring to the h-m1 analysis domain.
  - Add parenthetical clarification on first use: "Books (BookCorpus2)".

---

*Auto-fixed MAJOR issues in this round:*
- *Contribution #1 claim qualified to "upper bounds on η²" for synthetic text*
- *Baselines section (4.4) now explicitly states none were executed*
- *Results 5.1 now contains inline caveat about synthetic text source*
