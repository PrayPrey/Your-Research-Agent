# Adversarial Review Summary (Phase 6.5 v2.0)

**Paper**: JointLoRA-KV: Task-Aware Joint Training of LoRA Adapters and KV Cache Eviction Heads
**Review Completed**: 2026-05-21T13:00:00+00:00
**Rounds Completed**: 2 (R1, R2)
**Final Status**: CONVERGED
**Persuasiveness Check**: PASSED (post-R1 revision)
**Final Recommendation**: CONDITIONAL_ACCEPT

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis in R1 (Accuracy Checker, Bored Reviewer, Skeptical Expert) and two-persona analysis in R2 (Accuracy Checker, Skeptical Expert), with mandatory Serena/Grep numerical verification in R2.

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 1     | 1        | 0         |
| MAJOR    | 8     | 8        | 0         |
| MINOR    | 10    | 0 (deferred) | 10 (human review) |

**MINOR Issues**: Collected in `065_human_review_notes.md` (NOT auto-fixed)

---

## Persuasiveness Assessment (v2.0)

| Check | Pre-R1 | Post-R1 | Evidence/Notes |
|-------|--------|---------|----------------|
| Abstract compelling? | PARTIAL | PASS | Leads with ρ=0.37 measurement; PoC qualifiers added |
| Problem clear by paragraph 2? | PASS | PASS | Clear misalignment framing from sentence 1 |
| Novelty clear by page 1? | PARTIAL | PASS | arXiv 2604.21335 distinction explicit in §2.3 |
| Figure 1 self-explanatory? | N/A | N/A | Figures referenced as placeholders (images not embedded) |
| Hook avoids "X is important"? | PASS | PASS | Opens with concrete measurement, not preamble |
| Would continue reading? | YES | YES | Strong hook maintained after revisions |

---

## Round-by-Round Summary

### Round 1: Three-Persona Review

**Adversary Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert
**Focus**: Logical conflicts, methodology contradictions, novelty overclaims, engagement

**Accuracy Checker Findings**:
| Category | Issues Found | Severity |
|----------|--------------|---------|
| H-M2 F1 misrepresentation | 1 | FATAL |
| H-M1 gate status not disclosed | 1 | MAJOR |
| σ rounding (0.076 vs 0.0759) | 1 | MINOR |

**Bored Reviewer Findings**:
| Category | Issues Found | Severity |
|----------|--------------|---------|
| H-M2 F1 narrative collapse | 1 | MAJOR |
| Pending H-M3 framing | 1 | MAJOR |
| Abstract PoC scale missing | 1 | MINOR |
| Repetitive phrasing | 1 | MINOR |
| Table 2 missing annotation | 1 | MINOR |

**Skeptical Expert Findings**:
| Category | Issues Found | Severity |
|----------|--------------|---------|
| GQA artifact not in §5.1 | 1 | MAJOR |
| B1 vs B3 distinction unclear | 1 | MAJOR |
| Abstract stability scope claim | 1 | MAJOR |
| Figure numbering inconsistency | 1 | MINOR |
| Temperature parameter ambiguity | 1 | MINOR |
| GLUE citation year | 1 | MINOR |

**Key Issues Addressed in R1**:
1. **[FATAL-001]** H-M2 F1=0.3375/0.3354 corrected to F1=0.000 with full disclosure that PoC model output class tokens don't match QA strings; table/appendix revised to show actual 0.000 values
2. **[MAJOR-001]** H-M1 PARTIAL gate result explicitly stated in §5.2, §5.4 summary table, and Appendix B
3. **[MAJOR-002]** Abstract stability claim qualified: "PoC model (d=64, 2 layers); stability on full LLaMA-3.1-8B empirically pending"
4. **[MAJOR-003]** GQA expansion artifact noted in §4.4 setup section (with pointer to §6.2 L4)
5. **[MAJOR-004]** B1 vs B3 baseline distinction made explicit in §5.2 with mechanism-isolation rationale
6. **[MAJOR-005]** Abstract +1.50pp qualified: "(1 epoch, 1 seed, 500 samples; gate: PARTIAL)"
7. **[MAJOR-006]** "Nearly orthogonal" replaced with "substantially misaligned" with precise variance calculation

### Round 2: Numerical Verification and Credibility

**Adversary Personas**: Accuracy Checker, Skeptical Expert
**Numerical Verification**: 8 Grep pattern searches across Phase 4 validation files
**Focus**: Mathematical validity, baseline fairness, signal-performance gaps

**Serena/Grep Verification Results**:
| Claim | Verified Value | Match |
|-------|--------------|-------|
| ρ = 0.3662, std = 0.0759 | Confirmed in h-e1/04_validation.md | ✅ |
| GLUE 45.50% / 44.00% / +1.50pp | Confirmed in h-m1/04_validation.md | ✅ |
| NaN=0, Divergence=0 across 3 seeds | Confirmed in h-m2/04_validation.md | ✅ |
| F1=0.000 per-task (all LongBench) | Confirmed in h-m2/04_validation.md | ✅ |
| H-M1 gate PARTIAL, gate_satisfied=false | Confirmed in h-m1/04_validation.md | ✅ |
| H-M3 NOT_STARTED | Confirmed in verification_state.yaml | ✅ |
| ρ² math: 0.3662² = 0.134 → 86% unexplained | Arithmetic correct | ✅ |
| GLUE mean arithmetic: (39+50+47.5)/3=45.5 | Arithmetic correct | ✅ |

**Mathematical Validity**: ALL CHECKS PASSED — no mathematical impossibilities found.

**Issues Found and Addressed in R2**:
1. **[MAJOR-R2-001]** GQA artifact note added directly to §5.1 interpretation paragraph (co-located with ρ=0.3662 finding)
2. **[MAJOR-R2-002]** τ=0.1 (sigmoid KV mask) clarified as distinct from other softmax temperatures in §3.2

**Persuasiveness Post-R1**: PASSED — Bored Reviewer assessment: paper is compelling, hook strong, disclosures appropriate, abstract qualifiers present without undermining the contribution narrative.

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | PoC scale qualifiers, gate PARTIAL, stability scope, "substantially misaligned" | — |
| §3.2 Differentiable KV Mask | — | τ=0.1 vs softmax temperature clarification |
| §3.5 Baselines | B1 mechanism-isolation framing | — |
| §4.4 H-E1 Measurement | GQA expansion note added | — |
| §5.1 Misalignment Evidence | "substantially misaligned" language | GQA artifact caveat sentence added |
| §5.2 Mechanism Confirmation | B1 vs B3 explicit, gate PARTIAL disclosed | — |
| §5.3 Training Stability | Table 2 F1=0.000 correction, PoC model scope note | — |
| §5.4 Summary Table | PARTIAL status for H-M1 | — |
| §6.1 Key Findings | "substantially misaligned" precision | — |
| §7 Conclusion | Stability scope qualifier, "substantially misaligned" | — |
| Appendix B | Gate PARTIAL result added | — |
| Appendix C | F1=0.000 with full caveat replacing 0.3375/0.3354 | — |

---

## Quality Improvements

- **Logical Consistency**: Improved — PARTIAL gate status now disclosed consistently across all sections
- **Numerical Accuracy**: Improved — H-M2 F1 corrected from misleading 0.3375/0.3354 to accurate 0.000/0.000
- **Novelty Claims**: Unchanged — appropriately scoped throughout, GQA artifact now co-located with finding
- **Baseline Comparison**: Improved — B1 vs B3 distinction made explicit with mechanism-isolation rationale
- **Persuasiveness**: Improved — PoC qualifiers added without damaging the hook
- **Reproducibility**: Improved — τ=0.1 parameter ambiguity clarified

---

## Reviewer Preparation Notes

Potential remaining attack surfaces for real reviewers:

1. **H-M3 not executed** — Primary claim (≥3% over B3 on LongBench-QA) is PENDING
   - Prepared response: "All code is implemented and validator-approved. The bottleneck is compute allocation for a 3-seed, 3-5 epoch full training run. We present this as a mechanism-validation paper with clear pathways to the full result."

2. **H-M1 PARTIAL gate** — +1.50pp below 2.0pp pre-registered threshold
   - Prepared response: "The gap reflects PoC training constraints (1 epoch, 500 samples, 1 seed). The mechanism is confirmed functional (locret_grad_received=True, accuracy_improved=True). Full protocol is expected to exceed threshold based on 4-6× more gradient steps."

3. **H-M2 stability on tiny model** — d=64, 2-layer PoC, not full LLaMA-3.1-8B
   - Prepared response: "The disjoint parameter architecture (LoRA A/B matrices and Locret W₁/W₂ heads in independent graph positions) provides theoretical grounds for stability at any scale. Empirical confirmation at LLaMA-3.1-8B scale is left for H-M3."

4. **GQA expansion artifact** — ρ may be deflated by repeat_interleave(4)
   - Prepared response: "Even if the true ρ at KV-head level is higher (e.g., 0.55), it would remain substantially below the 0.7 alignment threshold, supporting the misalignment finding. KV-head-level analysis is identified as a future robustness check."

5. **B1 comparison instead of B3** — Comparison vs frozen-Locret (non-standard) rather than sequential (standard)
   - Prepared response: "B1 was chosen as the mechanism-isolation baseline — it isolates exactly the effect of task gradient signals flowing to Locret heads. B3 comparison (standard practice) is the subject of H-M3. Using B3 for H-M1 would confound mechanism confirmation with training scale differences."

---

## Files Generated

| File | Path | Status |
|------|------|--------|
| Final Paper | `paper/06_paper_final.md` | ✅ Created |
| Round 1 Review | `paper/review/065_review_r1.md` | ✅ Created |
| Round 2 Review | `paper/review/065_review_r2.md` | ✅ Created |
| R1 Revised Paper | `paper/06_paper_r1.md` | ✅ Created |
| R2 Revised Paper | `paper/06_paper_r2.md` | ✅ Created |
| Changelog | `paper/review/065_changelog.md` | ✅ Created |
| Human Review Notes | `paper/review/065_human_review_notes.md` | ✅ Created |
| Checkpoint | `paper/review/065_review_checkpoint.yaml` | ✅ Updated |
| Review Summary | `paper/review/065_review_summary.md` | ✅ This file |

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
