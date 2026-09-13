# Revision Changelog — R1, R2, and Final

**Revised paper:** `06_paper_r1.md`
**Source paper:** `06_paper.md`
**Review source:** `065_review_r1.md`
**Date:** 2026-08-22

---

## FATAL-001 Fix: Table 3 "+46.1%" vs prose "32%" contradiction

**Location:** Section 5.3, Table 3 row "Relative difference"

**Before:**
```
| Relative difference | **+46.1%** | Head-mean substantially more concentrated |
```

**After:**
```
| Relative difference | **−32%** (head-max vs head-mean) | Head-mean substantially more concentrated |
```

**Added footnote to Table 3:**
> Footnote: The −32% figure is computed as (0.681 − 0.466) / 0.681 = 31.6% ≈ 32%, using head-mean as the reference denominator. This means switching from head-mean to head-max reduces measured Gini by 32% relative to head-mean. Equivalently, head-mean Gini is +46.1% higher than head-max Gini when computed with head-max as denominator: (0.681 − 0.466) / 0.466 = 46.1%. All prose in this paper uses the head-mean-denominator framing ("32% relative reduction") for consistency.

**Rationale:** Both percentages are arithmetically correct but use different denominators. Table 3 now matches the prose framing (head-mean denominator = 32%) and explains the +46.1% figure in the footnote so readers understand both framings.

---

## MAJOR-001 Fix: Spearman rho exact values missing

**Location:** Section 5.2, Table 2 note

**Before:**
```
*Note: Direct ρ values confirmed in h-e2 continuation context as ρ ≥ 0.8 across all pairs; specific numerical values were reported in h-e1 implementation but primary reporting emphasized Gini/top-10% concentration metrics.*
```

**After:**
```
*Note: Gate criterion satisfied (min ρ ≥ 0.8 confirmed). Individual ρ values from implementation confirm this bound; point estimates were not separately tabulated in h-e1 results reporting — only the gate outcome was recorded. Exact per-pair values will be re-extracted and reported in the h-e2 companion results.*
```

**Rationale:** More transparent about what was and was not recorded. Honest that exact values are missing from primary reporting without fabricating numbers. Commits to reporting exact values in the h-e2 companion.

---

## MAJOR-002 Fix: "First layer-level characterization" overclaim vs Ali 2025

**Locations modified:**
- Abstract: Changed "first layer-level entropy characterization of Llama-2-7B" to "first systematic application of per-layer head-mean entropy pooling to identify SWA-safe layers in Llama-2-7B"
- Introduction Contribution (1): Changed "first systematic layer-level characterization of attention concentration in Llama-2-7B using head-mean entropy pooling" to "first systematic application of per-layer head-mean entropy pooling to characterize attention concentration in Llama-2-7B, specifically targeting layer selection for SWA conversion"
- Conclusion Summary (1): Updated to match narrowed framing
- Section 2.2 (Related Work, Entropy-Based Analysis): Added explicit sentence distinguishing our contribution from Ali 2025: "Notably, Entropy-Lens focuses on understanding decision strategies in LLMs, not on layer selection for SWA conversion; our work is the first to apply head-mean per-layer entropy pooling to identify SWA-safe layers in Llama-2-7B specifically."

**Rationale:** Ali et al. [2025] (Entropy-Lens) does analyze per-layer entropy profiles. The "first" claim is narrowed to what is genuinely novel: head-mean pooling applied specifically for SWA-safe layer identification in Llama-2-7B causal decoder.

---

## MAJOR-003 Fix: ICML2025 venue mismatch with interim/pending status

**Locations modified:**
- Abstract: Added explicit framing sentence: "This paper reports a complete, confirmatory study of the entropy criterion's validity as a layer characterization tool. Whether converting the 4 highest-entropy layers to sliding window attention preserves perplexity within 2 points of the full-attention baseline remains an open empirical question (the natural follow-up, h-e2)..."
- Introduction: Added "Paper scope" paragraph explicitly framing the paper as a prerequisite validation study, distinguishing confirmed contributions from planned follow-up.
- Introduction Contribution (4): Renamed from "Entropy-Guided Selective SWA Framework (Methodological, Pending Validation)" to "Entropy-Guided Selective SWA Framework (Design, Planned Validation)" with explicit wording: "This contribution documents the framework design, not a validated outcome."
- RQ4/RQ5/RQ6: Changed "pending" qualifier context for RQ5 from "superior to baselines" framing to "produces lower degradation than" (no superiority claim pre-execution).
- Section 4.3 Baselines: Added note: "Note: these comparisons are designed for h-m1 and have not yet been executed; no superiority claims are made at this stage."

**Rationale:** Frames the paper as a "prerequisite validation" paper rather than a methods paper with pending results, setting correct reviewer expectations.

---

## MAJOR-004 Fix: Figure 6 "preliminary perplexity comparison from available data" is misleading

**Location:** Section 5.5, paragraph after Table 5

**Before:**
> Figure 6 (ppl_comparison.png) shows a preliminary perplexity comparison plot from available data.

**After:**
> Figure 6 (ppl_comparison.png) is a schematic illustration of the planned comparison structure — a placeholder figure showing the intended result layout (conditions on x-axis, PPL on y-axis, with the 2-point threshold line). It does not contain real experimental data, as h-e2 has not been executed.

**Rationale:** h-e2 has not been executed. Calling Figure 6 a "preliminary perplexity comparison from available data" is misleading. It is now explicitly labeled as a schematic placeholder.

---

## MAJOR-005 Fix: Section 5.5 "Pending Results" section reframing

**Section header changed:**
- Before: "## 5.5 Pending Results: h-e2, h-m1, h-m2"
- After: "## 5.5 Planned Experiments and Expected Result Structure"

**Opening paragraph added:**
> We describe the planned h-e2, h-m1, and h-m2 experiments below, including the result structure we will report upon completion. These experiments have been fully designed and implemented in code; they await execution.

**Table 5 row values:**
- Changed all "PPL: TBD" and "Δ: TBD" to "PPL: pending execution" and "Δ: pending execution"
- Changed table caption from "Planned Result Structure (Pending)" to "Planned Result Structure (Execution Pending)"

**Rationale:** Reframes as planned experimental design rather than "pending results." Reduces the impression of a broken results section.

---

## MAJOR-006 Fix: No baseline comparison executed — remove superiority claims

**Locations audited and modified:**

- Abstract: No superiority claim present — confirmed clean.
- Introduction: No "outperforms" language — confirmed clean.
- Section 4.3 Baselines: Added explicit note that baselines have not been executed and no superiority claims are made.
- Section 5.4 (exploratory probe): Added explicit hedge: "does not constitute evidence for the h-m1 hypothesis" and "No superiority claim is made at this stage."
- Section 6.2 (formerly 6.2 "Open Questions from Pending Experiments"): Changed heading to "Open Questions and Motivation for Pending Experiments." Changed "Does entropy outperform random selection?" framing to use "produce lower degradation" rather than "outperform"; added "No superiority claim is made at this stage."
- Section 6.3 L1: Added explicit sentence: "The paper does not claim that entropy selection outperforms any baseline — only that the prerequisite criterion is stable and well-characterized."
- Conclusion: No superiority claims — confirmed clean.

**Rationale:** Systematic sweep to ensure no "outperforms" or "better than" framing for comparisons that have not been executed.

---

## MAJOR-007 Fix: Table 4 (non-significant QA F1 proxy) demoted from main Results

**Section 5.4 restructured:**
- Before: Full results subsection titled "Preliminary Directional Evidence for Selection Criterion Superiority (RQ5 Proxy, Non-Significant)" with Table 4 as a prominent results table.
- After: Renamed to "Exploratory Selection Criterion Probe (RQ5 Proxy, Non-Significant, for Transparency)." Table 4 removed and replaced with inline prose reporting the same numbers. Opening sentence: "reported only for transparency and does not constitute evidence for the h-m1 hypothesis."

**Rationale:** A non-significant result (p=0.4507) using a proxy operation and different metric does not belong as a full results table. Demoted to transparent prose note.

---

## Additional minor fixes applied during revision

- Section 2.2: Michel 2019 description softened from "a large fraction of attention heads can be removed" to "a subset of attention heads can be removed" to more accurately reflect the paper's nuanced finding.
- Section 3.6: h-e2/code/ listing annotated with "[designed; execution pending]" to clarify its status.
- Section 4.4 Gini Coefficient: Clarified what w_i represents — "per-token attention weights (summed across heads and head positions to produce a per-token scalar)" — to reduce ambiguity about how Gini is computed over the full attention tensor.
- Section 6.3 L4 (SWARR citation): Added clarification that SWARR demonstrates SFT is insufficient "which underscores the challenge of fine-tuning-free conversion but does not directly speak to the residual stream compensation mechanism in the selective (4-of-32 layers) setting." Removed the assertion that SWARR "supports" the compensation argument.
- Abstract: "< 1 GPU-hour" for calibration changed to consistent phrasing (single subset is ~20-30 min; total three subsets is ~1 GPU-hour; the abstract refers to single subset entropy computation, which is < 1 GPU-hour, so claim is preserved but ambiguity noted in MINOR for human review).

---

# R2 Revision Changelog

**Revised paper:** `06_paper_r2.md`
**Source paper:** `06_paper_r1.md`
**Review source:** `065_review_r2.md`
**Date:** 2026-08-22

---

## R2-MAJOR-001 Fix: Table 2 Spearman ρ exact values — honest footnote and new Limitation L5

**Locations modified:**
- Section 5.2, Table 2 footnote: Updated to explicitly state that exact per-pair ρ values were recorded during h-e1 but not separately tabulated in this interim report; final submission will include them.
- Section 6.3: Added new limitation L5 explicitly flagging that only the gate outcome (min ρ ≥ 0.8) is reported, not exact per-pair values, and that reviewers cannot assess whether stability is marginally or substantially above threshold.

**Before (Table 2 footnote):**
> Gate criterion satisfied (min ρ ≥ 0.8 confirmed). Individual ρ values from implementation confirm this bound; point estimates were not separately tabulated in h-e1 results reporting — only the gate outcome was recorded. Exact per-pair values will be re-extracted and reported in the h-e2 companion results.

**After (Table 2 footnote):**
> Note: Exact per-pair ρ values were recorded during h-e1 implementation but not separately tabulated in this interim report. The gate criterion (min ρ ≥ 0.8) is confirmed. Final submission will include per-pair values from completed h-e1 implementation logs.

**After (L5 in Section 6.3):**
> L5: Exact Spearman ρ per-pair values are not tabulated in this interim report. The gate criterion (min ρ ≥ 0.8) is confirmed from h-e1 implementation, but exact per-pair point estimates were not separately tabulated in the primary h-e1 results reporting. Reviewers cannot distinguish whether stability is narrowly above threshold (e.g., ρ ≈ 0.80–0.82) or substantially above it (e.g., ρ ≈ 0.93–0.96), which affects interpretation of the stability claim's strength. Final submission will include exact per-pair ρ values extracted from h-e1 implementation logs.

**Rationale:** Cannot fabricate exact values. Honest disclosure of what was and was not tabulated, with explicit limitation and commitment to include in final submission.

---

## R2-MAJOR-002 Fix: Phantom "[Pmlr 2026]" citation removed from Section 2.4

**Location:** Section 2.4 (Calibration-Based Model Analysis), last paragraph

**Before:**
> The use of Spearman rank correlation for stability validation follows calibration quality analysis approaches [Pmlr 2026] that assess how consistently a given measurement criterion ranks model components across different data subsets.

**After:**
> The use of Spearman rank correlation for stability validation is standard practice in calibration quality analysis, assessing how consistently a given measurement criterion ranks model components across different data subsets.

**Rationale:** The citation key "[Pmlr 2026]" was a non-functional placeholder with no corresponding bibliography entry. The sentence makes a valid methodological point that stands without citation — the choice of Spearman ρ for stability validation is standard practice and does not require a specific citation.

---

## R2-MAJOR-003 Fix: GPU-time arithmetic inconsistency resolved

**Locations modified:**
- Introduction: Changed "< 1 GPU-hour" (referring to calibration) to "≈ 20–30 GPU-minutes for a single calibration pass"
- Section 3.2.2: Changed "requiring only ≈ 20–30 GPU-minutes for 100 forward passes" — kept as-is (accurate for single subset)
- Section 3.6: Changed "completing calibration (h-e1) in < 1 GPU-hour" to "completing calibration for one subset (h-e1) in ≈ 20–30 GPU-minutes; three subsets for full stability validation take approximately 1–1.5 GPU-hours"
- Section 4.5: Changed "Total calibration: approximately 1 GPU-hour for all three subsets" to "Total calibration (three subsets for stability validation): approximately 1–1.5 GPU-hours"

**Rationale:** 3 subsets × 30 GPU-min = 90 min = 1.5 GPU-hours, which exceeds the original "< 1 GPU-hour" claim. The per-subset figure (20–30 min on H100 for 100 sequences through 7B parameters) is kept as a realistic estimate; the total is changed to "approximately 1–1.5 GPU-hours" which is arithmetically consistent with the per-subset range.

---

## R2-MAJOR-004 Fix: Contribution 4 visual differentiation from confirmed contributions

**Locations modified:**
- Introduction contributions list: Added horizontal divider and framing sentence before Contribution 4: "The following contribution describes the designed framework, pending h-e2 confirmation:" and labeled it "(Design Only — Experimental Validation Pending)"
- Abstract: Added explicit sentence that the fourth contribution is design-only pending h-e2 experimental validation
- Conclusion Summary: Added note after the three confirmed contributions: "Note: Contribution (4) — the entropy-guided selective SWA framework — is a complete design and implementation artifact; its experimental validation (h-e2) is pending and not reported in this paper."

**Rationale:** Contribution 4 is categorically different from Contributions 1–3 — it is a design document, not an experimental result. The visual separation and explicit "(Design Only — Experimental Validation Pending)" label prevent a rushed reviewer from treating all four contributions as equivalent.

---

## R2-MAJOR-005 Fix: "Architectural invariant" language softened in Sections 5.1 and 6.1

**Location:** Section 5.1, paragraph 3

**Before:**
> This universality suggests attention concentration is an architectural invariant of Llama-2-7B's trained weights, not an artifact of specific input sequences.

**After:**
> This universality suggests attention concentration is a consistent structural property of Llama-2-7B's trained weights within the WikiText-103 calibration domain, not an artifact of specific input sequences.

**Location:** Section 6.1, Finding 1

**Before:**
> [Finding header] "Attention concentration is a near-universal structural property of Llama-2-7B."
> "it suggests that heavy-hitter attention concentration is an architectural invariant trained into Llama-2-7B's weights, not an input-specific phenomenon"

**After:**
> [Finding header] "Attention concentration is a near-universal structural property of Llama-2-7B within the WikiText-103 evaluation domain."
> "it suggests that heavy-hitter attention concentration is a consistent structural property of Llama-2-7B's trained weights, not an input-specific phenomenon within this evaluation domain"

**Location:** Section 6.1, Finding 1 broader implication

**Before:**
> If attention concentration is architecturally grounded rather than input-driven, then the entropy criterion may generalize across input domains (beyond WikiText-103 calibration). Cross-domain calibration stability remains an open question (see Limitations), but the near-universal in-domain finding is a strong signal.

**After:**
> Our in-domain results are consistent with the possibility that attention concentration may be architecturally grounded rather than purely input-driven, but cross-domain validation is required to confirm this. If the concentration pattern does generalize across input domains, then the entropy criterion may apply beyond WikiText-103 calibration. Cross-domain calibration stability remains an open question (see Limitations L2 and L5), and this generalization should not be assumed without empirical verification.

**Location:** Conclusion Future Directions

**Before:**
> re-running entropy scoring with SST-2 or code-domain calibration sequences would test whether the layer rankings are universal architectural properties or domain-specific phenomena.

**After:**
> re-running entropy scoring with SST-2 or code-domain calibration sequences would test whether the layer rankings are consistent structural properties or domain-specific phenomena.

**Rationale:** The evidence base (n=200 examples from WikiText-103 only) does not support calling the observed concentration an "architectural invariant." An invariant should hold across domains; cross-domain validation is explicitly listed as an open question. The softened language ("consistent structural property within the WikiText-103 evaluation domain") is accurate to the evidence while preserving the finding's significance.

---

## Final Summary

**Total Revisions Made**: 12 MAJOR + 1 FATAL addressed across 2 rounds
**Sections Modified**: Abstract, Introduction, Related Work (2.2, 2.4), Methodology (3.2.2, 3.6), Experimental Setup (4.3, 4.5), Results (5.1, 5.2, 5.3, 5.4, 5.5), Discussion (6.1, 6.3), Conclusion, Future Directions

**Review Process:**
- Started: 2026-08-22
- Completed: 2026-08-22
- Rounds: 2
- Personas Used: accuracy_checker, bored_reviewer, skeptical_expert

**Files Generated:**
- 06_paper_final.md (final paper, copy of 06_paper_r2.md)
- 065_review_summary.md (consolidated review summary)
- 065_human_review_notes.md (MINOR issues for human review)
- 065_review_r1.md, 065_review_r2.md (round reports)
- 065_changelog.md (this file)

**Next Phase**: Phase 6.5.1 (Overleaf LaTeX/PDF generation)
