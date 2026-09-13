# Phase 6.5 Adversarial Review Summary

**Generated:** 2026-08-20  
**Rounds completed:** 2 (R1 + R2)  
**Final status:** CONVERGED  

---

## Review Outcome

| Category | R1 | R2 | Final |
|----------|----|----|-------|
| FATAL issues | 0 | 1 (found + fixed) | 0 |
| MAJOR issues | 3 (found + fixed) | 0 | 0 |
| MINOR issues | 4 (collected) | 0 | 4 (human review) |
| Converged | No | Yes | ✓ |

---

## Issues Found and Fixed

### R1: Three-Persona Review

**Accuracy Checker:**
- All η² values verified against h-m1/04_validation.md ✓
- All Spearman values verified against h-m2/04_validation.md ✓
- Panel OLS code metrics verified against h-m3/04_validation.md ✓
- h-e1 gate metrics verified against h-e1/04_validation.md ✓

**Bored Reviewer:**
- Abstract compelling — clear novelty hook ✓
- Novelty clear within 2 minutes ✓
- MINOR: "three nested layers" claim with only two elaborated (MINOR-01)

**Skeptical Expert:**
- MAJOR-01: Contribution #1 claim "first direct demonstration" oversold for synthetic text → Fixed with qualifier
- MAJOR-02: Baselines table implied execution without noting none ran → Fixed with explicit note
- MAJOR-03: Results 5.1 lacked inline synthetic text caveat → Fixed

### R2: Numerical Verification (MANDATORY)

**FATAL discovered and fixed:**
- Per-domain std table in Section 5.2 had systematically wrong values for 8 of 10 domains. Specific errors:
  - DM Mathematics: paper had 0.0187, ground truth is 0.00102
  - USPTO Backgrounds: paper had 0.0163, ground truth is 0.00578
  - FreeLaw: paper had 0.0157, ground truth is 0.00256
  - ArXiv: paper had 0.0121, ground truth is 0.00128
  - NIH ExPorter: paper had 0.0114, ground truth is 0.00130
  - PubMed Central: paper had 0.0092, ground truth is 0.00288
  - StackExchange: paper had 0.0068, ground truth is 0.01496
  - PubMed Abstracts: paper had 0.0017, ground truth is 0.01485
- All corrected to match h-e1/04_validation.md ground truth values
- Domain ordering corrected (sorted by actual std descending)
- 06_paper.md in-text citation of Pile-CC/Wikipedia std also corrected

---

## Numerical Accuracy Verification (Final)

All key claims verified against source files:

| Claim | Ground Truth | Paper | Status |
|-------|-------------|-------|--------|
| η²(entity density) | 0.9915 | 0.9915 | ✓ |
| F(entity density) | 24,310 | 24,310 | ✓ |
| η²(narrative coherence) | 0.9142 | 0.9142 | ✓ |
| F(narrative coherence) | 2,227 | 2,227 | ✓ |
| η²(formal syntax) | 0.9821 | 0.9821 | ✓ |
| F(formal syntax) | 11,462 | 11,462 | ✓ |
| Wikipedia entity_density | 0.2553 | 0.2553 | ✓ |
| BookCorpus2 entity_density | 0.0075 | 0.0075 | ✓ |
| Mean difference | +0.2478 | +0.2478 | ✓ |
| BookCorpus2 narrative_coherence | 0.0190 | 0.0190 | ✓ |
| n_domains_passing | 10/22 | 10/22 | ✓ |
| Pile-CC std | 0.02657 | 0.02657 | ✓ |
| Wikipedia std | 0.00858 | 0.00858 | ✓ |
| StackExchange std | 0.01496 | 0.01496 | ✓ |
| Cross-scale Spearman | 1.0 | 1.0 | ✓ |
| ρ(Wikipedia, MMLU) | -0.391 | -0.391 | ✓ |
| ρ(Wikipedia, HellaSwag) | +0.423 | +0.423 | ✓ |
| Fisher z | -1.923 | -1.923 | ✓ |
| p-value (P1 H1) | 0.973 | 0.973 | ✓ |
| h-m3 code lines | 2,943 | 2,943 | ✓ |
| h-m3 tests passing | 21/24 | 21/24 | ✓ |
| zero-variance domains | 6 | 6 | ✓ |
| 70M checkpoints | 10/154 | 10/154 | ✓ |
| 1B checkpoints | 2/154 | 2/154 | ✓ |
| 6.9B checkpoints | 0/154 | 0/154 | ✓ |

---

## Persuasiveness Assessment

- Primary empirical findings (η²>0.91, 10/22 domains) clearly communicated ✓
- Honest framing of negative results (Books3=0, blocked regression) ✓
- Infrastructure contribution clearly articulated ✓
- Limitations L1-L4 all present in Discussion ✓
- Preliminary result (70M reversal) appropriately hedged ✓

**Persuasiveness: PASSED**

---

## Minor Issues for Human Review

See `065_human_review_notes.md` for 4 minor issues requiring human judgment:
1. MINOR-01: "Three nested layers" with only two elaborated
2. MINOR-02: Wikipedia std rounding inconsistency  
3. MINOR-03: Pile-CC confound missing from Section 5.3
4. MINOR-04: "Books" vs "BookCorpus2" terminology consistency
