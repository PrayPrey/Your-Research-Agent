# Adversarial Review Summary

**Paper**: Entropy-Guided Selective Sliding Window Attention Conversion in Llama-2-7B: A Zero-Shot Prerequisite Validation
**Review Completed**: 2026-08-22
**Rounds Completed**: 2
**Final Status**: CONVERGED (all auto-fixable issues resolved)
**Persuasiveness Check**: CONDITIONAL PASS (interim paper scope acknowledged; venue fitness requires h-e2 execution)

---

## Executive Summary

This paper underwent 2 rounds of adversarial review with three-persona analysis (accuracy_checker, bored_reviewer, skeptical_expert).

| Severity | Found | Resolved | Remaining |
|----------|-------|----------|-----------|
| FATAL    | 1     | 1        | 0         |
| MAJOR    | 12    | 12       | 0         |

**MINOR Issues**: 15 collected in `065_human_review_notes.md` (NOT auto-fixed)

**Remaining concerns requiring experimental execution (not text-fixable):**
1. Exact Spearman ρ per-pair values (requires h-e1 log extraction or re-run; < 1 GPU-hour)
2. StreamingLLM [Xiao 2024] citation unverified (manual check of arXiv 2309.17453)
3. Venue fit for ICML main track (requires h-e2 execution to confirm P1)

---

## Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Specific Gini numbers ground the hook immediately |
| Problem clear by paragraph 2? | PASS | Tension (layers already local → why pay O(n²)?) is clear |
| Novelty clear by page 1? | PASS (after R1 fix) | "First application of..." claim narrowed; distinct from Entropy-Lens |
| Figure 1 self-explanatory? | CONDITIONAL | rank_correlation_scatter.png: needs caption to stand alone |
| Hook avoids "X is important"? | PASS | Opens with finding (Gini=0.6829), not generic motivation |
| Would bored reviewer continue reading? | YES (with caveat) | Interim status framed clearly; reader knows what's confirmed |
| Attention lost at? | Section 5.5 (planned results) | TBD table slows reader; mitigated by R1 reframing |

---

## Round-by-Round Summary

### Round 1: Three-Persona Full Review

**Accuracy Checker Findings:**

| Category | Issues Found |
|----------|--------------|
| FATAL: Table 3 "+46.1%" vs prose "32%" contradiction | 1 |
| Missing exact Spearman ρ values | 1 (MAJOR) |
| GPU-time arithmetic inconsistency | 1 (caught R2; MAJOR) |

**Bored Reviewer Findings:**

| Category | Issues Found |
|----------|--------------|
| Section 5.5 "Pending Results" table of TBDs | 1 (MAJOR) |
| Table 4 non-significant proxy in main results | 1 (MAJOR) |
| Contribution 4 insufficient differentiation | 1 (MAJOR) |

**Skeptical Expert Findings:**

| Category | Issues Found |
|----------|--------------|
| "First characterization" overclaim vs Ali 2025 | 1 (MAJOR) |
| ICML venue mismatch with interim paper | 1 (MAJOR) |
| Figure 6 placeholder presented as real data | 1 (MAJOR) |

**Key Issues Addressed in R1:**
1. FATAL-001: Table 3 now shows −32% with footnote explaining both 32% and 46.1% framings
2. MAJOR-002: "First" claims narrowed throughout to "first application of head-mean pooling for SWA layer selection in Llama-2-7B"
3. MAJOR-003: Paper reframed explicitly as "prerequisite validation" study
4. MAJOR-004: Figure 6 labeled as schematic placeholder
5. MAJOR-005: Section 5.5 reframed as "Planned Experiments and Expected Result Structure"
6. MAJOR-006: All superiority-claim language removed; no "outperforms" without executed baselines
7. MAJOR-007: Table 4 removed; Section 5.4 demoted to transparent prose paragraph

### Round 2: Numerical Verification and Credibility

**Accuracy Checker (Deep Numerical Verification):**

| Claim | Paper Value | Ground Truth | Match |
|-------|------------|--------------|-------|
| Gini Coefficient | 0.6829 (std=0.0117) | 0.6829 (std=0.0117) | ✓ |
| Top-10% Token Share | 0.7172 (std=0.0196) | 0.7172 (std=0.0196) | ✓ |
| Top-10% as percentage | 71.72% | 0.7172 × 100 | ✓ |
| Head-mean Gini | 0.681 | 0.681 | ✓ |
| Head-max Gini | 0.466 | 0.466 | ✓ |
| 32% relative reduction | (0.681−0.466)/0.681 = 31.6% ≈ 32% | Correct | ✓ |
| 46.1% ratio (Table 3 footnote) | (0.681−0.466)/0.466 = 46.1% | Correct | ✓ |
| k=4/32 = 12.5% of layers | 12.5% | 4/32 = 12.5% | ✓ |
| Subset indices A/B/C | 0-99, 100-199, 200-299 | As designed | ✓ |
| n=200 examples, 100% satisfaction | 200/200 | h-e1 confirmed | ✓ |
| QA F1 proxy values | -0.43pp vs -0.67pp, p=0.4507 | Ground truth | ✓ |

**New Issues Found in R2 and Fixed:**
1. R2-MAJOR-001: Table 2 footnote updated with honest disclosure on missing exact ρ values; L5 added to Limitations
2. R2-MAJOR-002: Phantom "[Pmlr 2026]" citation removed from Section 2.4
3. R2-MAJOR-003: GPU-time corrected to "≈ 1–1.5 GPU-hours for all three subsets"
4. R2-MAJOR-004: Contribution 4 separated with visual divider and "(Design Only — Experimental Validation Pending)" header
5. R2-MAJOR-005: "Architectural invariant" replaced with "consistent structural property within the WikiText-103 calibration domain" throughout

---

## Sections Modified

| Section | R1 Modifications | R2 Modifications |
|---------|-----------------|-----------------|
| Abstract | Prerequisite validation framing; Contribution 4 disclosure | Design-only note for Contribution 4 |
| Introduction | Scope paragraph; Contribution 4 reframe; narrowed "first" claim | Visual separator; GPU-time fix |
| Related Work (2.2) | Entropy-Lens distinction added | — |
| Related Work (2.4) | — | Phantom [Pmlr 2026] removed |
| Methodology (3.2.2) | — | GPU-time per-subset clarified |
| Methodology (3.6) | — | GPU-time total corrected |
| Experimental Setup (4.3) | No-superiority statement | — |
| Experimental Setup (4.5) | — | GPU-time total corrected |
| Results (5.1) | — | "Architectural invariant" replaced |
| Results (5.2) | Table 2 gate note | Table 2 footnote: exact ρ disclosure |
| Results (5.3) | Table 3: −32% + footnote | — |
| Results (5.4) | Table 4 removed; demoted to prose | — |
| Results (5.5) | Reframed as planned experiments | — |
| Discussion (6.1) | — | "Architectural invariant" softened; cross-domain conditioning |
| Discussion (6.3) | — | L5 added (missing exact Spearman ρ) |
| Conclusion | Narrowed "first" claim | Design-only note; domain-scoped wording |
| Future Directions | — | "Universal architectural properties" softened |

---

## Quality Improvements

- **Logical Consistency**: IMPROVED — Table 3/prose 32% vs 46.1% contradiction resolved
- **Numerical Accuracy**: IMPROVED — all confirmed numbers verified; phantom citation removed; GPU-time corrected
- **Novelty Claims**: REFINED — "first" claims narrowed to specific scope
- **Baseline Comparison**: CONTEXTUALIZED — no superiority claims without executed baselines
- **Persuasiveness**: IMPROVED — interim paper identity clarified; TBD tables reframed
- **Hook Quality**: UNCHANGED (already strong — opens with Gini=0.6829 finding)
- **Venue Framing**: IMPROVED — prerequisite validation identity strengthened

---

## Reviewer Preparation Notes

**Potential remaining attack surfaces for real reviewers:**

1. **"Why ICML main track with 4/5 hypotheses pending?"**
   Prepared response: "This paper reports a complete confirmatory study of the entropy characterization prerequisite (h-e1), which is a standalone empirical contribution. The concentration finding, pooling ablation, and stability validation are independently publishable. We explicitly scope to this contribution and describe h-e2 as future work. Workshops on efficient transformers would also be appropriate venues."

2. **"Exact Spearman ρ values are missing from Table 2."**
   Prepared response: "Gate result is confirmed (min ρ ≥ 0.8 across all pairs). Per-pair point estimates will be included in the camera-ready version from h-e1 implementation logs. The gate confirmation is the scientifically load-bearing result."

3. **"Head-mean entropy analysis was done before (Entropy-Lens [Ali 2025])."**
   Prepared response: "Entropy-Lens analyzes per-layer entropy as a decision-strategy signature across transformer layers. We perform the first application of per-layer head-mean entropy pooling as a *selection criterion* for zero-shot SWA conversion — a distinct operation (modifying attention mechanism, not analyzing it) with distinct design considerations (window coverage, calibration protocol, stability validation)."

4. **"The 'architectural invariant' language is too strong for single-domain evidence."**
   Prepared response: "Agreed — we revised to 'consistent structural property within the WikiText-103 calibration domain.' Cross-domain generalization is explicitly listed as future work."

5. **"StreamingLLM [Xiao 2024] citation is unverified."**
   Prepared response: "This requires manual verification of arXiv 2309.17453 before final submission. The claim it supports (sink token patterns) is well-established; the citation is a standard reference."
