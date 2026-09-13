# Human Review Notes — R1 MINOR Issues

**Paper:** `06_paper_r1.md`
**For:** Human reviewer — issues NOT auto-fixed in R1 revision
**Date:** 2026-08-22

These issues were flagged by the adversarial review (065_review_r1.md) as MINOR and collected here for human decision. None were auto-fixed to avoid unintended changes. Each entry includes the issue, location, and recommended action.

---

## M1: "< 1 GPU-hour" vs "~1 GPU-hour" timing inconsistency

**Source:** R1 review, Persona 1 Minor Issues
**Location:** Abstract vs Section 4.5

The abstract says "100 sequences, single GPU, < 1 GPU-hour." Section 4.5 says "approximately 20–30 GPU-minutes per subset on H100. Total calibration: approximately 1 GPU-hour for all three subsets."

The abstract refers to the single-subset entropy scoring pass used for deployment, which is genuinely < 1 GPU-hour (20-30 min). The "~1 GPU-hour total" in 4.5 covers all three subsets including stability validation, which is a one-time research cost.

**Recommended action:** Add a clarifying parenthetical in the abstract: "(< 1 GPU-hour per calibration pass)" and in Section 4.5 make clear "Total calibration including three subsets for stability validation: ~1 GPU-hour." The distinction is correct and important — practitioners only need one subset (20-30 min); the three subsets are for the stability analysis.

---

## M2: h-e2/code/ listing creates impression code is complete

**Source:** R1 review, Persona 1 Minor Issues
**Location:** Section 3.6 Code Structure

The code structure listing shows h-e2/code/ with four files. The R1 revision added "[designed; execution pending]" annotation to this block. If even stronger clarity is desired, consider adding a comment within the code block itself, e.g.:

```
h-e2/code/  # [Implementation complete; experiment execution pending]
```

**Recommended action:** Human reviewer should decide if the "[designed; execution pending]" annotation in the header is sufficient, or whether inline code comments are needed. Current state in 06_paper_r1.md uses the header annotation.

---

## M3: "Pmlr 2026" citation is incomplete

**Source:** R1 review, Persona 1 Minor Issues
**Location:** Section 2.4 (Calibration-Based Model Analysis), last sentence

The citation `[Pmlr 2026]` in "The use of Spearman rank correlation for stability validation follows calibration quality analysis approaches [Pmlr 2026]..." has no author, title, or paper ID in the references section. It is not in the references list at all.

**Recommended action:** Either (a) identify the actual paper being cited and add a proper reference entry, or (b) remove the citation and rephrase to not cite a specific paper. This must be resolved before submission. The sentence can stand without the citation: "The use of Spearman rank correlation for stability validation is standard practice in calibration quality analysis."

---

## M4: Gini formula ambiguity — what does w_i represent?

**Source:** R1 review, Persona 1 Minor Issues
**Location:** Section 4.4 (Evaluation Metrics, Gini Coefficient)

The R1 revision clarified w_i as "per-token attention weights (summed across heads and head positions to produce a per-token scalar)." However, the specific aggregation procedure (sum over heads first, then over positions? or sum over positions first?) is still potentially ambiguous for a reader implementing the metric.

**Recommended action:** Add a one-sentence clarification: "Specifically, w_i is computed by summing the attention weight at token position i across all heads and all query positions, producing a single concentration scalar per token position per layer." If implementation code is released, link to the relevant function in entropy.py.

---

## M5: XiaoStreamingLLM is UNVERIFIED

**Source:** R1 review, Persona 1 Minor Issues; also flagged in references section
**Location:** References section

The Xiao et al. [2024] StreamingLLM citation is marked UNVERIFIED in the references BibTeX block. The arXiv ID is 2309.17453.

**Recommended action:** Before submission, verify via Semantic Scholar: search for "Efficient Streaming Language Models with Attention Sinks" by Guangxuan Xiao et al. The paper is widely cited and likely verifiable; this is a formality but required for the verification protocol.

---

## M6: Figure 1 caption not self-explanatory

**Source:** R1 review, Persona 2 Minor Issues
**Location:** Section 5.2, Figure 1 reference

The paper references "Figure 1 (rank_correlation_scatter.png)" but does not provide a caption in the text that explains axis semantics (x-axis = subset A per-layer entropy values, y-axis = subset B or C per-layer entropy values, each point = one of 32 layers).

**Recommended action:** When typesetting the paper with actual figures, ensure the Figure 1 caption explicitly states: "Scatter plot of per-layer entropy scores between calibration subsets A and B (left) and A and C (right). Each point represents one of the 32 transformer layers. Spearman ρ is annotated. Strong correlation confirms selection stability."

---

## M7: Abstract length — dense for ICML format

**Source:** R1 review, Persona 2 Minor Issues
**Location:** Abstract

The abstract is approximately 250 words, which is on the dense side for ICML format (typical limit ~150-200 words).

**Recommended action:** Consider trimming the pooling comparison sentence in the abstract or condensing the final two sentences. The core message (calibration-based characterization + stability + 32% pooling gap + open question on h-e2) can be tightened. This is a style/submission-format issue, not a correctness issue.

---

## M8: Hook framing nearly identical to SWAA [Yu et al., 2025]

**Source:** R1 review, Persona 2 Minor Issues
**Location:** Abstract, first sentence

"Zero-shot conversion of pre-trained transformers to sliding window attention fails catastrophically when applied to all layers" is very close to the SWAA framing. Since SWAA is cited and is the direct prior work establishing this failure mode, this is defensible — but a reviewer who has just read SWAA may notice.

**Recommended action:** Consider a minor rephrase of the abstract opening to differentiate the angle. E.g., open with the structural observation (concentration) rather than the failure mode: "Attention weight in Llama-2-7B concentrates in fewer than 10% of tokens across all layers — yet zero-shot conversion to sliding window attention fails catastrophically when applied uniformly." This leads with the positive finding rather than the failure mode, which is also the paper's key contribution.

---

## M9: Michel 2019 description overstates finding

**Source:** R1 review, Persona 3 Minor Issues
**Location:** Section 2.2

The R1 revision changed "a large fraction of attention heads can be removed" to "a subset of attention heads can be removed" — this was applied as a minor fix during revision. The human reviewer should verify this wording adequately represents Michel 2019's nuanced finding (the paper title is "Are Sixteen Heads Really Better than One?" — the answer is model/task dependent). If more precision is desired, add: "a task-dependent subset of attention heads."

**Recommended action:** Confirm current wording in 06_paper_r1.md is accurate. Current text: "Michel et al. [2019] demonstrate that a subset of attention heads can be removed at test time without significant accuracy loss."

---

## M10: SWARR citation in L4 — verify interpretation

---

# R2 MINOR Issues (appended from R2 adversarial review)

**Paper:** `06_paper_r2.md`
**Review source:** `065_review_r2.md`
**Date:** 2026-08-22

---

## R2-M1 (INHERITED from R1-M5): StreamingLLM citation year discrepancy

**Source:** R2 review, R2-M1
**Location:** References section, Xiao2024StreamingLLM entry

The Xiao et al. StreamingLLM paper (arXiv:2309.17453) was submitted to arXiv in September 2023 but published at ICLR 2024. The citation year "2024" is technically correct for conference publication but the arXiv ID is from 2023. The citation remains UNVERIFIED via Semantic Scholar.

**Recommended action:** Before submission, verify via Semantic Scholar: search for "Efficient Streaming Language Models with Attention Sinks" by Guangxuan Xiao et al. Confirm arXiv ID 2309.17453. If citing the conference paper, update to @inproceedings with ICLR 2024 venue; if citing the arXiv version, update year to 2023.

---

## R2-M2 (NEW): Gini formula implementation details — aggregation order ambiguity

**Source:** R2 review, R2-M2
**Location:** Section 4.4 (Evaluation Metrics, Gini Coefficient)

Section 4.4 defines w_i as "per-token attention weights (summed across heads and head positions to produce a per-token scalar)." The specific aggregation order (sum over heads first, then over query positions? or simultaneous sum?) is not stated precisely enough for reproducibility.

**Recommended action:** Add one sentence: "Specifically, w_i is computed by summing the attention weight at token position i across all heads and all query positions, producing a single concentration scalar per token position per layer." If code is released, link to the relevant function in entropy.py.

---

## R2-M3 (NEW): Awkward phrasing in Conclusion — "32% higher relative to head-mean"

**Source:** R2 review, R2-M3
**Location:** Section 7 (Conclusion), Summary item (2)

Current text: "head-mean Gini exceeds head-max Gini by 32% relative to head-mean"

This is correct but the phrase "relative to head-mean" after "exceeds" is slightly self-referential and awkward.

**Recommended action:** Rephrase to: "head-mean Gini (0.681) exceeds head-max Gini (0.466) by a 32% relative margin (computed with head-mean as denominator)" or simply drop the "relative to head-mean" clause since the Table 3 footnote already documents both denominator framings.

---

## R2-M4 (INHERITED, resolved): SWARR citation interpretation — R2 confirms resolved

**Source:** R2 review, R2-M4
**Status:** RESOLVED in R1 revision. R2 review confirms the fix is accurate.

No further action needed on this item.

---

## R2-M5 (INHERITED from R1-M2): h-e2/code/ listing impression of complete tested code

**Source:** R2 review, R2-M5
**Location:** Section 3.6 Code Structure

The h-e2/code/ module listing with "[designed; execution pending]" annotation is the current state. R2 review notes that presenting full file listings for unexecuted code could still mislead reviewers.

**Recommended action:** Human reviewer should decide if the header annotation is sufficient, or whether adding a prose disclaimer before the code block is warranted: e.g., "The following module structure is designed and implemented but has not been tested end-to-end, as h-e2 experiment execution is pending."

**Source:** R1 review, Persona 3 Minor Issues
**Location:** Section 6.3 L4

The R1 revision updated the SWARR citation to note that SWARR demonstrates "SFT alone is insufficient after SWA conversion — which underscores the challenge of fine-tuning-free conversion but does not directly speak to the residual stream compensation mechanism in the selective (4-of-32 layers) setting."

**Recommended action:** Human reviewer should verify this interpretation of Liu et al. [2026] is accurate. The original paper claimed SWARR "supports" the compensation argument; R1 revision correctly notes it does not directly support it. If the reviewer finds a better citation for the compensation mechanism, replace or remove the SWARR reference from L4.
