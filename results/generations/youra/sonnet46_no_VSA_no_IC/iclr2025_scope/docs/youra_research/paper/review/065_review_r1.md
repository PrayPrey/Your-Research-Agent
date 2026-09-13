# Adversarial Review Round 1

## Ground Truth Summary

| Metric | Value | Confidence |
|--------|-------|------------|
| Gini Coefficient (h-e1) | 0.6829 (std=0.0117, n=200) | HIGH |
| Top-10% Token Share | 0.7172 (std=0.0196, n=200) | HIGH |
| Both criteria satisfied | 100% (200/200) | HIGH |
| Head-mean Gini | 0.681 | HIGH |
| Head-max Gini | 0.466 | HIGH |
| Relative diff (head-mean→head-max, denominator=head-mean) | 31.6% ≈ 32% | HIGH |
| Relative diff (head-max as base) | +46.1% | HIGH |
| Spearman ρ across subsets | ≥ 0.8 (all pairs) | MEDIUM (no exact values) |
| QA F1 entropy vs random | -0.43pp vs -0.67pp, p=0.4507 | LOW (non-significant) |
| h-e2/h-m1/h-m2/h-c1 | NOT EXECUTED | — |

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 1 |
| MAJOR | 4 |
| MINOR | 5 (collected for human review) |

Recommendation: **MAJOR_REVISION**

---

## Persona 1: Accuracy Checker

### FATAL Issues

**FATAL-001: Contradictory percentage in Table 3 vs surrounding prose**

Table 3 (Section 5.3) introduces the "+46.1% relative difference" label in the "Relative difference" row, but every other location in the paper — Abstract, Introduction (Section 1), Methodology (Section 3.2.1), and Discussion (Section 6.2) — consistently states "32% relative reduction." These are both arithmetically correct but describe different reference frames:

- 32% = (0.681 − 0.466) / 0.681 (head-mean as denominator — "reduction from head-mean")
- 46.1% = (0.681 − 0.466) / 0.466 (head-max as denominator — "gain over head-max")

The paper uses "32% relative reduction" in all prose but then drops "+46.1%" into Table 3 as the label for the same quantity, without noting it uses a different denominator. A reviewer reading Table 3 will see 46.1% and immediately catch this inconsistency with the 32% stated in the abstract and everywhere else. This is not a display-only inconsistency — it will be cited as evidence of sloppy analysis and will trigger a reproducibility concern.

**Required fix:** Pick one framing and use it everywhere, or explicitly state both with denominator context in Table 3. The ground truth confirms both are arithmetically correct but they measure different things.

### MAJOR Issues

**MAJOR-001: Exact Spearman ρ values never reported**

Table 2 shows only "≥ 0.8" for all three pairs. No actual numerical values (e.g., ρ_AB = 0.94) are reported. The footnote admits "specific numerical values were reported in h-e1 implementation but primary reporting emphasized Gini/top-10% concentration metrics." This is a critical gap: the stability claim is the foundational gating criterion for the entire paper, and a reviewer will demand exact values. "≥ 0.8" reads as a gate result, not a result. If the values were 0.81, 0.80, 0.82, the stability is borderline; if 0.95+, it is strong. This ambiguity is attackable.

**Required fix:** Report exact ρ values for each pair. If unavailable (log lost), re-run the entropy scoring — it is < 1 GPU-hour.

**MAJOR-002: "First layer-level characterization" claim is potentially overclaimed**

The paper claims this is "the first systematic layer-level entropy characterization of Llama-2-7B using head-mean entropy pooling" (Section 5.1) and "the first layer-level entropy characterization of Llama-2-7B" (Abstract). The qualifier "using head-mean pooling" in one location but not the other creates inconsistency. More importantly: Entropy-Lens [Ali et al., 2025] analyzes per-layer entropy profiles as "information signatures across transformer layers" — the paper itself cites this in Section 2.2. A skeptical reviewer will ask: does Ali 2025 characterize Llama-2-7B layers with per-layer entropy? If yes, the "first" claim is false. If no (different model family, or only head-level), the paper must explicitly state why Ali 2025 does not satisfy the "first" criterion.

**Required fix:** Qualify the "first" claim precisely: specify what is novel — head-mean pooling in causal decoder, or Llama-2-7B specifically, or zero-shot characterization — and explicitly distinguish from Ali 2025 in a sentence.

**MAJOR-003: Interim paper with 4/5 hypotheses pending is structurally problematic for ICML2025 format**

The paper is formatted as ICML2025 but openly states h-e2, h-m1, h-m2, h-c1 are all PENDING. The status field says "INTERIM." ICML does not accept interim papers — it expects complete experimental results. The paper attempts to frame h-e1 as sufficient standalone contribution, which is defensible only if the contribution framing is airtight. Currently, Contributions 1–3 are confirmed but Contribution 4 is "Pending Validation" — it is listed as a contribution of the paper but lacks experimental support. A reviewer reading the introduction sees four contributions, then finds the fourth is a framework not yet validated. This will trigger a desk rejection or strong reject.

**Required fix:** Either (a) reframe the paper as "prerequisite validation" with three confirmed contributions only, removing Contribution 4 from the contribution list; or (b) execute h-e2 before submitting. Contribution 4 should move to Future Work or be reframed as "framework design" without claiming it as a paper contribution.

**MAJOR-004: Figure 6 (ppl_comparison.png) is described as "preliminary perplexity comparison from available data" but h-e2 has not been executed**

Section 5.5 states "Figure 6 (ppl_comparison.png) shows a preliminary perplexity comparison plot from available data." If h-e2 has not been executed, there is no perplexity data. This suggests Figure 6 either (a) contains synthetic/placeholder data presented as real, (b) is from a prior run not described in the methodology, or (c) is mislabeled. Any of these would be a serious issue. If the figure exists and contains real data, the source must be identified. If it is a placeholder, it should be labeled explicitly as "planned figure (data pending)" not "preliminary perplexity comparison."

**Required fix:** Either identify and describe the exact source of Figure 6's data in the caption, or explicitly label it as a placeholder/schematic.

### MINOR Issues (for human review only)

- M1: "< 1 GPU-hour" claim in abstract vs "approximately 20–30 GPU-minutes per subset" × 3 subsets = ~1 GPU-hour in methodology — borderline consistency.
- M2: Section 3.6 code structure listing (h-e1/code/ and h-e2/code/) creates the impression the code is complete; h-e2 code is listed as if implemented.
- M3: "Pmlr 2026" citation in Section 2.4 is incomplete — no author, title, or paper ID provided.
- M4: Gini formula in Section 4.4 is correctly stated but not connected to how it is computed over the full attention tensor (all heads, all positions) — ambiguity about what w_i represents.
- M5: XiaoStreamingLLM is UNVERIFIED (noted in references) — flag for pre-submission check.

### Ground Truth Verification Log

| Claim | Paper Value | Ground Truth | Match |
|-------|------------|--------------|-------|
| Gini coefficient | 0.6829 (std=0.0117) | 0.6829 (std=0.0117) | MATCH |
| Top-10% token share | 0.7172 (std=0.0196) | 0.7172 (std=0.0196) | MATCH |
| Both criteria: 100% of 200 | 100% (200/200) | 100% (200/200) | MATCH |
| Head-mean Gini | 0.681 | 0.681 | MATCH |
| Head-max Gini | 0.466 | 0.466 | MATCH |
| Pooling relative difference (prose) | "32% relative reduction" | 31.6% ≈ 32% (head-mean denominator) | MATCH |
| Pooling relative difference (Table 3) | "+46.1%" | 46.1% (head-max denominator) | CONFLICT with prose framing |
| QA F1: entropy | -0.43pp | -0.43pp | MATCH |
| QA F1: random | -0.67pp | -0.67pp | MATCH |
| p-value | 0.4507 | 0.4507 | MATCH |
| h-e2/h-m1/h-m2 status | "Pending" | NOT EXECUTED | MATCH (correctly stated) |

---

## Persona 2: Bored Reviewer

### Persuasiveness Assessment

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Opens with paradox, specific numbers early, problem clear |
| Problem clear in 1 minute? | PASS | First paragraph states the tension cleanly |
| Novelty clear in 2 minutes? | BORDERLINE PASS | Head-mean vs head-max distinction is the real novelty but undersold in abstract |
| Would continue reading? | CONDITIONAL | Yes if framed as prerequisite paper; confusion about completeness kills it |
| Attention lost at? | Section 5.5 | "Pending results" section is a dead end that breaks momentum |

### FATAL Issues

None from this persona — the writing is competent.

### MAJOR Issues

**MAJOR-005: The "pending results" section (5.5) actively harms persuasiveness**

Section 5.5 is titled "Pending Results: h-e2, h-m1, h-m2" and presents a table of future planned experiments with "TBD" entries throughout. For a bored reviewer with 5 papers to read, hitting an entire results section filled with "TBD" after reading detailed methodology for those experiments is a credibility-destroying experience. It signals: "this paper should not have been submitted yet." The honest framing of pending work is respected in a workshop setting but will generate a reject at a top-tier venue if any of the key hypotheses are TBD.

This is not a writing problem — it is a submission timing problem. The paper needs h-e2 results to be complete.

### MINOR Issues (for human review only)

- M6: Figure 1 (rank_correlation_scatter.png) is not self-explanatory from the caption alone — the caption should state what the x-axis (subset A entropy values) and y-axis (subset B/C entropy values) represent.
- M7: The abstract at 250 words is on the dense side for ICML format — consider trimming the pooling comparison sentence.
- M8: The hook "Zero-shot conversion of pre-trained transformers to sliding window attention fails catastrophically" is effective but not original — nearly identical framing appears in SWAA [Yu et al., 2025].

---

## Persona 3: Skeptical Expert

### Novelty Assessment

The paper makes three confirmed contributions:
1. Attention concentration characterization (Gini=0.6829) in Llama-2-7B — this IS novel as stated, with the caveat about Ali 2025 and Entropy-Lens noted above.
2. Head-mean vs head-max pooling ablation — this is a genuine methodological finding with clear implications.
3. Ranking stability confirmation (ρ ≥ 0.8) — this is a necessary sanity check, not a novel result in itself.

The main hypothesis (entropy-guided selective SWA conversion) has no experimental results. The paper's core value proposition is unverified.

### FATAL Issues

None beyond FATAL-001 (percentage inconsistency).

### MAJOR Issues

**MAJOR-006: No actual baseline comparison is executed — the baselines described are entirely hypothetical**

Section 4.3 describes three baselines (full-attention k=0, random-k=4, last-k=4) but none are executed. The entire comparative claim — that entropy selection outperforms random or heuristic selection — rests on the non-significant, proxy QA F1 result (p=0.4507) using a different operation (top-k retention vs SWA masking). This means the paper cannot claim its method works better than any alternative. For a conversion-efficiency paper, "our method is better than doing nothing or doing it randomly" is the minimum bar, and it is uncleared.

The paper correctly acknowledges this (Section 6.2, Limitation L1). However, the severity must be understood: without h-m1, the paper is a characterization study, not a method paper. Characterization papers have different contribution bars — they must show the characterization is useful and predictive, which requires some downstream task result.

**MAJOR-007: The QA F1 proxy result (Table 4) should not appear in the main results section**

Table 4 is placed in Section 5 (Results) despite being explicitly non-significant (p=0.4507), using a proxy operation (top-k retention not SWA), and measuring a different metric (QA F1 not perplexity). Including it in Results creates the impression of a result where none exists. It belongs in an appendix or in the Discussion as a motivation for h-m1. As positioned, a reviewer will interpret it as an attempt to pad results — which damages credibility.

**Required fix:** Move Table 4 to Discussion Section 6.2 ("Open Questions") or Appendix, with clearer framing as exploratory motivation rather than a result.

### Minor Issues (for human review only)

- M9: Section 2.2 states Michel 2019 shows "a large fraction of attention heads can be removed" — Michel 2019 actually shows only a subset can be removed without significant degradation (the paper's title asks "Are Sixteen Heads Really Better than One?" — the answer is nuanced). The claim slightly overstates the Michel 2019 finding.
- M10: The "residual stream compensation" mechanism (Section 6.2, L4) is described as "supported by transformer architecture theory and consistent with SWARR findings" — SWARR [Liu et al., 2026] actually demonstrates that SFT alone is INSUFFICIENT, which weakens rather than supports the compensation argument. The citation may be misread.

---

## Summary for Revision Agent

Priority fix list:

1. **FATAL-001 (HIGHEST):** Resolve 32% vs 46.1% inconsistency. Choose one denominator framing and apply it consistently everywhere, including Table 3. Add a footnote explaining both framings if both are needed.

2. **MAJOR-001:** Report exact Spearman ρ values for all three subset pairs (A-B, A-C, B-C). "≥ 0.8" is insufficient — re-extract from logs or re-run (< 1 GPU-hour).

3. **MAJOR-003:** Remove Contribution 4 from the contribution list (or reframe as "framework design" without claiming validation). Add a paragraph in the Introduction explicitly framing this as a prerequisite/checkpoint paper to set correct reviewer expectations before they hit Section 5.5.

4. **MAJOR-005 + MAJOR-007:** Move Table 4 (non-significant QA F1) from Section 5 to Section 6.2 as a motivation for h-m1. Consider removing or substantially shrinking Section 5.5 — replace with a brief forward pointer rather than a detailed pending-results table.

5. **MAJOR-004:** Clarify Figure 6 source. If ppl_comparison.png is a schematic or placeholder, label it explicitly. If it contains real data, cite the source in the caption.

6. **MAJOR-002:** Add one sentence in Section 5.1 explicitly distinguishing from Ali 2025 (Entropy-Lens) — specify that Ali 2025 does not cover Llama-2-7B decoder at layer level with head-mean pooling (verify this claim first).

7. **MAJOR-006:** Acknowledged as a known limitation (L1). No fix possible without h-e2/h-m1 execution. Ensure framing throughout the paper does not claim method superiority — check every occurrence of "outperforms" or "better than."

8. **MINOR (M3):** Fix the incomplete "Pmlr 2026" citation in Section 2.4.

9. **MINOR (M10):** Verify SWARR citation in Section 6.3 L4 — does it support or contradict the residual stream compensation argument?
