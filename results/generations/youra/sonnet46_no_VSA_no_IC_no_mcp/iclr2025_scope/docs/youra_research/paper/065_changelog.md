# Phase 6.5 Changelog

**Generated:** 2026-08-27  
**Review phase:** Phase 6.5 Adversarial Review (R1 + R2)

---

## Changes Applied

### [MAJOR-M1] Fix page count inconsistency in stats block
- **File:** `06_paper.md` (paper statistics block)
- **Before:** `estimated_pages: ~8`
- **After:** `estimated_pages: ~11` with explicit over-limit warning
- **Reason:** Internal formula computed ~11.6; listing ~8 was contradicted by inline comment and would mislead authors about ICML compliance.

### [MAJOR-M2] Strengthen novelty defense in §2.4
- **Files:** `06_paper.md` §2.4, `02_related_work.md` §2.4
- **Change:** Added explicit affirmative value statement explaining why documenting this failure mode is useful: researchers building unified KV benchmarks will encounter it via the documented HuggingFace API, losing GPU time to a silent degenerate run.
- **Reason:** "absent from prior literature" argued by absence only; affirmative value needed to answer "why is this a paper, not a GitHub issue?"

### [MAJOR-M3] Demote unverified LongBench citation to corroborating context in §5.1
- **Files:** `06_paper.md` §5.1, `05_results.md` §5.1
- **Change:** Made qualitative evidence primary (M0 produces coherent non-empty partial-overlap text on all 4 tasks = F1 > 0 = pipeline working). Cited LongBench Figure 2 as "corroborating context only, unverified."
- **Reason:** Load-bearing argument for M0 correctness should not depend on a citation marked [UNVERIFIED] in ground truth.

### [MAJOR-M4] Add disclaimer to corrected protocol (§3.5)
- **Files:** `06_paper.md` §3.5, `03_methodology.md` §3.5
- **Change:** Added "Important: this corrected protocol is proposed based on the SnapKV reference implementation design — it was not executed or validated in this paper's pipeline due to experiment termination."
- **Reason:** Describing the fix as "validated" when it was not run in this pipeline is misleading; prior wording implied experimental confirmation.

---

## No Changes (confirmed correct)

- All numerical values in Tables 1, 2, 3 verified against ground truth — no changes.
- INCONCLUSIVE framing of h-e1 gate — correct, no changes.
- DynamicCache API usage (`ddp_cache_data`) description — correct, no changes.
- All 7 citations preserved as [UNVERIFIED] — no changes (verification requires external tools unavailable in this session).
- Abstract — no changes (passes adversarial review).

---

## Deferred to Human Review

See `065_human_review_notes.md` for 5 MINOR issues not auto-applied.
