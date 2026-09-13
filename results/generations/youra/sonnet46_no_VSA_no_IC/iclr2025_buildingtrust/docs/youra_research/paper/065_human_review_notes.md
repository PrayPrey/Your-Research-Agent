# Phase 6.5 — Human Review Notes (MINOR Issues)

These issues were identified during adversarial review but NOT auto-fixed.
They require human judgment — style, framing, or external verification.

---

## MN-1: Abstract sentence ordering

**Location:** Abstract, sentence 3  
**Issue:** The finding "contrary to our original hypothesis" is buried in the middle of a compound sentence. Bored reviewer persona flagged: moving this to the opening sentence would maximize impact.  
**Current:** "Contrary to our original hypothesis that adversarial benchmark construction disrupts rank stability, we find that..."  
**Suggestion:** Open the abstract with: "Contrary to our original hypothesis, we find that both fairness and adversarial robustness rankings are highly stable..."  
**Reason not auto-fixed:** Abstract tone is a human judgment call; current version is not incorrect.

---

## MN-2: Gevers & Daelemans [2026] — independent verification needed

**Location:** Section 2.4, References  
**Issue:** Citation flagged as "PLAUSIBLE — pending verification." A 2026 citation in a 2026 paper raises simultaneous-submission concerns.  
**Action needed:** Author must verify this citation exists (preprint or published), or remove/replace if unverifiable.  
**Risk if unverified:** Fabricated citation = desk rejection.

---

## MN-3: Yang et al. 2023 GLUE-X — independent verification needed

**Location:** References  
**Issue:** Tagged [UNVERIFIED] in references. GLUE-X is a real paper (ACL 2023 Findings) — this tag should be removed after author confirms details.  
**Action needed:** Verify author list, title, venue, year; remove [UNVERIFIED] tag.

---

## MN-4: Figure 4 description lacking concrete detail

**Location:** Section 5.1  
**Issue:** "Figure 4 shows this collapse" — description says "three panels" in section file but assembled paper is vaguer. A reader who can't see the figure needs one sentence describing what collapse looks like.  
**Suggestion:** Add: "In the left panels, raw ρ values cluster near 0.98 for all three dimensions, visually indistinguishable; in the right panels, partial ρ values spread to 0.68–0.96, revealing the fairness-robustness differential."  
**Reason not auto-fixed:** Requires author to confirm figure layout.

---

## MN-5: N=13 model list discrepancy (internal, non-paper-facing)

**Location:** h-m2/04_validation.md  
**Issue:** h-m2 lists Falcon-40B in its 13-model set, but h-e1 enumerates 16 models without Falcon-40B. This suggests h-m2 used a different model set than h-e1's canonical 16. Does not affect any number in the paper (N=13 total is correct either way), but could affect replication.  
**Action needed:** Author to verify which 13 models were actually used in h-m2/h-m3 computation.

---

## MN-6: "First computation" novelty claim

**Location:** Introduction contribution (1), Conclusion contribution 1  
**Issue:** "First computation of partial Spearman ρ..." claim depends on Gevers & Daelemans [2026] being the only predecessor — if MN-2 reveals that citation is unverifiable, the claim scope must be re-evaluated.  
**Action needed:** Verify after MN-2 resolved.
