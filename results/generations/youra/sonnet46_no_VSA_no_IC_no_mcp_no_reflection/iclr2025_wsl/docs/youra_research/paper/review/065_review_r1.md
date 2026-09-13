# Adversarial Review Report — Round 1
**Paper:** Can Weight-Space Encoders Predict Generalization Gap? A Controlled Study of Equivariant Architectures
**Round:** R1 — Accuracy, Engagement, Structural Issues
**Date:** 2026-08-31T10:30:00+00:00
**Mode:** UNATTENDED (three-persona inline review)

---

## Ground Truth Verification Summary

All 12 numerical claims in `065_ground_truth.yaml` verified against paper — **all match:true**.

| Metric | Ground Truth | Paper | Match |
|--------|-------------|-------|-------|
| FlatMLP gap Spearman | 0.5567 (h-e1) | 0.5567 | ✅ |
| DWSNet gap Spearman | 0.5104 | 0.5104 | ✅ |
| NFT gap Spearman | 0.5752 | 0.5752 | ✅ |
| NFT CI | [0.5339, 0.6158] | [0.5339, 0.6158] | ✅ |
| GNN gap Spearman | 0.3747 | 0.3747 | ✅ |
| DWSNet Δ | −0.2212 | −0.2212 | ✅ |
| NFT Δ | −0.1589 | −0.1589 | ✅ |
| GNN Δ | −0.2272 | −0.2272 | ✅ |
| P3 r | 0.7305 | 0.7305 | ✅ |
| P3 p | 1.60×10⁻¹⁶⁷ | 1.60×10⁻¹⁶⁷ | ✅ |
| A1 | −0.142 | −0.142 | ✅ |
| Zoo N/D | 10000/33890 | 10000/33890 | ✅ |

**Note:** FlatMLP gap CI from h-m1 = [0.4850, 0.5801] exists but is NOT reported in paper Table 1 (shown as "—").

---

## Executive Summary

| Severity | Count | Status |
|----------|-------|--------|
| FATAL | 1 | Must fix |
| MAJOR | 2 | Must fix |
| MINOR | 2 | Collected for human review |

**Recommendation:** REVISE — fix FATAL and MAJOR issues, then proceed to R2.

---

## FATAL Issues

### SKEP-FATAL-001: Non-Overlapping CI Claim is Incorrect

**Location:** Introduction (Contribution 2), §5.2 (Results RQ2)
**Severity:** FATAL
**Persona:** Skeptical Expert

**Evidence:**
- NFT 95% CI: [0.5339, 0.6158] (ground truth: h-m1/04_validation.md)
- FlatMLP 95% CI: [0.4850, 0.5801] (ground truth: h-m1/04_validation.md)
- Overlap region: [0.5339, 0.5801] — the CIs DO overlap

**Paper claims (Introduction, Contribution 2):**
> "NFT achieves the highest gap Spearman (r = 0.5752, 95% CI: [0.5339, 0.6158]) with a non-overlapping confidence interval from FlatMLP."

**Paper claims (§5.2):**
> "NFT achieves the highest gap Spearman (r = 0.5752) with a 95% CI of [0.5339, 0.6158] that is non-overlapping with FlatMLP's confidence band."

**Why FATAL:** The non-overlapping CI claim is the statistical basis for claiming NFT is significantly better than FlatMLP on gap prediction (RQ2). If CIs overlap, the statistical confidence claim is false. A reviewer will immediately check this and reject.

**Fix required:** Replace "non-overlapping confidence interval from FlatMLP" with accurate language. Options:
1. Report FlatMLP CI in Table 1 and reframe: "NFT's lower bound (0.5339) is above FlatMLP's point estimate (0.5330), suggesting meaningful advantage, though CIs overlap at the margin ([0.4850, 0.5801] ∩ [0.5339, 0.6158] = [0.5339, 0.5801])"
2. Use a proper test: since NFT lower CI > FlatMLP point estimate, the difference is directionally strong but not statistically non-overlapping
3. Report FlatMLP CI [0.4850, 0.5801] in Table 1 and let readers assess

---

## MAJOR Issues

### ACCR-MAJOR-001: FlatMLP Gap Spearman Reported Inconsistently

**Location:** Abstract, Introduction Contributions, Table 1 vs. Table 2 / §5.4
**Severity:** MAJOR
**Persona:** Accuracy Checker

**Evidence:**
- Table 1 FlatMLP gap Spearman: 0.5567 (from h-e1)
- Table 2 Δ computation uses FlatMLP gap baseline: 0.5330 (from h-m1)
- §5.4 explicitly: "gap improvement: 0.488 − 0.533 = −0.045" confirms 0.5330 used in Δ

**Problem:** Two different FlatMLP gap values are used in the same paper. Table 1 shows 0.5567 (h-e1) and the Δ table implicitly uses 0.5330 (h-m1) as the baseline. There is a footnote in Table 1 saying "FlatMLP gap CI not separately reported (from h-e1; NFT/DWS/GNN CIs from h-m1 bootstrap)" but no explicit explanation that TWO DIFFERENT RUNS with different results are being mixed.

**Fix required:** Add explicit clarification — either:
1. Add a column to Table 1 distinguishing h-e1 vs h-m1 FlatMLP values
2. Add a note: "FlatMLP gap Spearman: 0.5567 in h-e1 (existence run), 0.5330 in h-m1 (architecture comparison run). Δ computation in Table 2 uses h-m1 value as the control baseline for consistency with CIs."
3. The paper already has a footnote in Table 1 but it does not explicitly state the h-m1 FlatMLP gap value used in Table 2.

---

### BORE-MAJOR-001: Section Numbering Collision Between Results and Discussion

**Location:** Entire paper structure (Results §5.1-§5.4 and Discussion §5.1-§5.4)
**Severity:** MAJOR
**Persona:** Bored Reviewer

**Evidence:**
- Results section has: §5.1 RQ1, §5.2 RQ2, §5.3 RQ3, §5.4 RQ4
- Discussion section has: §5.1 What Results Tell Us, §5.2 FlatMLP Anomaly, §5.3 Limitations, §5.4 Broader Impact

**Problem:** Both Results and Discussion are subsections within "Chapter 5" with identical numbering (§5.1, §5.2, §5.3, §5.4). The Abstract says "Section 5 discusses mechanism interpretation, limitations" but the reader will find two §5.1s. The Conclusion refers to "Section 5.3" which is ambiguous (Limitations in Discussion, or P3 in Results?).

**Fix required:** Renumber sections so Results = §5 (with §5.1-§5.4 subsections) and Discussion = §6 (with §6.1-§6.4), then renumber Conclusion = §7 and References = §8. OR renumber Discussion subsections as §5.5-§5.8 within the same chapter, then adjust Conclusion accordingly.

---

## MINOR Issues (Collected for Human Review)

### ACCR-MINOR-001: FlatMLP Gap CI Omitted from Table 1

**Location:** Table 1
FlatMLP CI from h-m1: [0.4850, 0.5801] exists but is shown as "—" in Table 1. Fixing SKEP-FATAL-001 will naturally require adding this CI. Once FATAL is fixed, this minor issue resolves automatically.

### BORE-MINOR-001: Citation Verification Status Not Disclosed

**Location:** References section
Ground truth notes: `citations_verified_mcp: 0`. Paper does not disclose that citations are unverified via MCP. The references.bib note says "UNVERIFIED via MCP". Not a factual error (arXiv IDs appear correct from pipeline artifacts), but a process transparency issue. Low priority.

---

## Persuasiveness Assessment (R1)

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling? | PASS | Strong hook with concrete asymmetry claim |
| Problem clear in 1 minute? | PASS | "Gap in existing work" paragraph clear and crisp |
| Novelty clear in 2 minutes? | PASS | "First controlled comparison" and partial Spearman stated explicitly |
| Figure 1 self-explanatory? | PARTIAL | Caption adequate but figure file not verified |
| Would continue reading? | YES | Strong opening, clear problem motivation |
| Attention lost at? | Discussion (numbering confusion) | Section numbering collision disorienting |
| False novelty claims? | 0 | Claims checked against literature, acceptable |
| Unfair baselines? | 0 | All four encoders trained with identical protocol |
| Overclaims? | 0 | Null result reported transparently |
| Tone overclaiming? | 0 | No hype language detected |
| Missing limitations? | NO | 4 limitations explicitly listed |

**Persuasiveness: PARTIAL** — abstract and intro strong, but FATAL CI claim and section numbering confusion undermine credibility.

---

## Summary for Revision Agent

**Priority 1 (FATAL — fix immediately):**
- SKEP-FATAL-001: Remove "non-overlapping confidence interval from FlatMLP" claim. Replace with accurate statement about FlatMLP CI [0.4850, 0.5801] and how NFT CI [0.5339, 0.6158] compares — they overlap but NFT's lower bound exceeds FlatMLP's point estimate, providing directional evidence rather than strict non-overlap.

**Priority 2 (MAJOR — fix in R1 revision):**
- ACCR-MAJOR-001: Add explicit footnote/clarification distinguishing h-e1 FlatMLP (0.5567, Table 1) from h-m1 FlatMLP (0.5330, Δ baseline in Table 2).
- BORE-MAJOR-001: Renumber Discussion sections to avoid collision with Results §5.x numbering.

**Priority 3 (MINOR — collect for human review):**
- ACCR-MINOR-001: Will resolve naturally with FATAL fix (add FlatMLP CI to Table 1).
- BORE-MINOR-001: Optional disclosure about citation verification status.
