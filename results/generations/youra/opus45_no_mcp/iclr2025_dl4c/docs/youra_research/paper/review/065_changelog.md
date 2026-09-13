# Phase 6.5 Changelog

## Round 1 Revisions (06_paper.md → 06_paper_r1.md)

### MAJOR Fixes

#### 1. Added RLTF Baseline Comparison Clarification
- **Location:** Section 4.4 (Model)
- **Issue:** Missing explanation for why paper doesn't compare directly to RLTF reported numbers
- **Fix:** Added paragraph explaining:
  - RLTF uses CodeT5-large (770M), we use CodeT5-small (60M)
  - 13× parameter difference makes absolute comparison uninformative
  - Within-setup comparison (fine-gated vs fine-always) provides cleaner causal evidence
  - Mechanism expected to transfer due to architecture-agnostic nature

### No Other Changes
- All numerical claims verified accurate
- All required limitations already present
- No FATAL issues found

## Round 2 Revisions (06_paper_r1.md → 06_paper_r2.md)

No changes required. Round 2 verified:
- All 16 numerical claims match Phase 4 validation files
- R1 fix properly implemented
- Methodology sound

## Final Version (06_paper_final.md)

Identical to 06_paper_r1.md (converged after R1 revision + R2 verification).

---

## Issues NOT Fixed (Human Review Required)

See `065_human_review_notes.md`:

1. **Figure numbering:** Figure 1 (Section 3.1) and Figure 3 (Section 5.2) both reference `accuracy_bar.png`
2. **Abstract length:** ~250 words (slightly above typical ICML preference)

---

*Generated: 2026-08-19*
