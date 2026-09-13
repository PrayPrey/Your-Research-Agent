# Phase 6.5 Adversarial Review Summary

**Hypothesis:** h-e1  
**Review date:** 2026-08-27  
**Rounds completed:** 2 (R1: three-persona + R2: numerical verification)  
**Final status:** CONVERGED — FATAL=0, MAJOR=0 after R1 fixes

---

## Review Outcome

| Severity | Found | Fixed | Deferred |
|----------|-------|-------|----------|
| FATAL | 0 | 0 | 0 |
| MAJOR | 4 | 4 | 0 |
| MINOR | 5 | 0 | 5 (human_review_notes) |

---

## FATAL Issues (none)

No fatal issues found. All numerical claims verified against ground truth. Paper does not claim results it did not produce. INCONCLUSIVE framing is accurate and consistently maintained.

---

## MAJOR Issues Fixed

### M1: Page count inconsistency in stats block
- **Found:** Paper stats block listed `estimated_pages: ~8` while the inline formula computed ~11.6 pages, contradicting ICML 8-page limit discussion.
- **Fix:** Corrected `estimated_pages: ~11` with explicit over-limit warning.
- **Location:** `06_paper.md` paper statistics block.

### M2: Novelty defense insufficient (argued by absence, not affirmative value)
- **Found:** §2.4 argued the failure mode was novel because no prior paper used post-hoc reconstruction — but did not articulate *why* documenting it matters.
- **Fix:** Added explicit affirmative value statement: researchers building unified KV benchmarks (the field's gap) will encounter this failure via documented HuggingFace API, losing GPU hours to a silent degenerate run. Paper short-circuits that waste.
- **Location:** `06_paper.md` §2.4, `02_related_work.md` §2.4.

### M3: M0 sanity argument depended on unverified citation as primary evidence
- **Found:** §5.1 validated M0 is working by citing LongBench Figure 2 for expected F1 range — but this citation is marked [UNVERIFIED] in ground truth. A circular argument if the citation is wrong.
- **Fix:** Made qualitative evidence primary (non-empty, non-repetitive, partial-overlap text = F1 > 0 on all 4 tasks); demoted citation to "corroborating context only."
- **Location:** `06_paper.md` §5.1, `05_results.md` §5.1.

### M4: Corrected protocol presented as "validated" when not tested in this pipeline
- **Found:** §3.5 described LlamaAttention.forward() override as "validated by SnapKV's reference codebase" — implying validation in this pipeline, which did not occur.
- **Fix:** Added explicit disclaimer: "proposed based on SnapKV reference implementation design — not executed or validated in this paper's pipeline due to experiment termination."
- **Location:** `06_paper.md` §3.5, `03_methodology.md` §3.5.

---

## Numerical Verification (R2)

All values verified against 04_validation.md and 065_ground_truth.yaml:

| Metric | Paper | Ground Truth | Status |
|--------|-------|-------------|--------|
| M0 macro-F1 | 0.0875 | 0.0875 | ✓ |
| NarrativeQA M0 | 0.09 | 0.09 | ✓ |
| HotpotQA M0 | 0.09 | 0.09 | ✓ |
| 2WikiMQA M0 | 0.11 | 0.11 | ✓ |
| MuSiQue M0 | 0.06 | 0.06 | ✓ |
| M1 F1 (3 tasks) | 0.00 | 0.00 | ✓ |
| Layers confirmed | 32/32 | 32/32 | ✓ |
| KV retention k | 2048/4096 | 2048/4096 | ✓ |
| W (obs. window) | 16 | 16 | ✓ |
| retention_ratio | 0.50 | 0.50 | ✓ |
| seed | 42 | 42 | ✓ |
| max_new_tokens | 50 | 50 | ✓ |
| examples/task | 100 | 100 | ✓ |
| Gate criterion | ≥0.02 raw | ≥0.02 raw | ✓ |
| Citations | 7 total, 0 verified | 7 / 0 verified | ✓ |

No numerical discrepancies found.

---

## Persuasiveness Assessment

- **Abstract:** Compelling. Counter-intuitive opening (correct shapes, broken generation). Novelty claim specific and verifiable. ✓
- **Novelty defense:** Strengthened (M2 fix). Affirmative value now explicit. ✓
- **Causal chain:** Clear diagnostic elimination in Table 3. ✓
- **Limitations:** Honest. INCONCLUSIVE framing consistent. ✓
- **Remaining weakness (MINOR, human decision):** No figures; no qualitative output examples; page count ~11 > ICML limit.

---

## Files Generated

- `06_paper_final.md` — post-review paper (all MAJOR fixes applied)
- `065_review_summary.md` — this file
- `065_changelog.md` — change log
- `065_human_review_notes.md` — MINOR issues for human review
