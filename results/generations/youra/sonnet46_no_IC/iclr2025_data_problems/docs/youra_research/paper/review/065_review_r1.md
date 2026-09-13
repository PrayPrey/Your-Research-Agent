# Adversarial Review - Round 1

**Paper:** One Size Does Not Fit All: Scale-Dependent Optimal Perplexity Filtering for Language Model Pre-training
**Reviewed:** 2026-08-04
**Reviewer:** Adversary Agent v2

---

## Executive Summary

| Category | FATAL | MAJOR | Status |
|----------|-------|-------|--------|
| Accuracy | 1 | 2 | NEEDS_WORK |
| Engagement | 0 | 1 | NEEDS_WORK |
| Credibility | 0 | 3 | NEEDS_WORK |
| **TOTAL** | **1** | **6** | NEEDS_WORK |

**Recommendation:** MAJOR_REVISION

---

## Part 1: Accuracy Check (Persona 1)

### Ground Truth Verification Table

| Metric | Paper Claims | Ground Truth | Match? |
|--------|--------------|--------------|--------|
| τ*(14M) | 20 | 20 | ✓ |
| τ*(31M) | 50 | 50 | ✓ |
| 14M C1 acc_norm | 0.2556 ± 0.001 | 0.2556 | ✓ |
| 31M C6 acc_norm | 0.2548 ± 0.001 | 0.2548 | ✓ |
| 31M C1 acc_norm (worst) | 0.2524 ± 0.001 | 0.2524 | ✓ |
| τ=20 retention rate | 3.5% (176/5000) | 3.5% (176/5000) | ✓ |
| τ=50 retention rate | 41.5% (2074/5000) | 41.5% (2074/5000) | ✓ |
| Effect size Δacc_norm | ≈0.003 | ≈0.003 | ✓ |
| 23/23 pytest tests | 23/23 pass | 23/23 (ground truth) | ✓ |
| Wall-clock time | ~68 minutes "for all 24 runs" | ~68 min "for 22 new runs" | ✗ INACCURATE |
| Curation pool size | 5000 docs | 50,000 streamed | ✗ FATAL INCONSISTENCY |
| Model parameter count | "14M and 31M" | 7.9M and 18.1M actual (04_validation.md) | ✗ MAJOR |
| Total runs | 24 = 3×2×2×2 | 24 confirmed | ✓ |
| HellaSwag split | 10,003-example full validation | 10,003 | ✓ |
| GPT-2 reference model | 117M parameters | 117M | ✓ |

### FATAL Issues - Accuracy

**ACC-FATAL-001: Internal inconsistency in corpus pool size**

Section 3.2 states: "We stream 50,000 documents as our curation pool." One paragraph later it states: "τ=20: 176/5000 documents retained (3.5%)." The retention fractions (176/5000 = 3.5%, 2074/5000 = 41.5%) are all computed against a denominator of 5,000 — not 50,000. The ground truth YAML lists `documents_streamed: 50000` and `tau20_docs: 176, tau50_docs: 2074, pool_size: 5000`.

So either (a) 50,000 documents were streamed but only 5,000 were used as the PPL-scored pool, or (b) 5,000 documents were streamed. The paper presents both numbers without explaining their relationship. A reviewer who reads Section 3.2 carefully will immediately notice that 176/50000 = 0.35%, not 3.5%, but 176/5000 = 3.5% — making the denominator ambiguous. This is a FATAL factual inconsistency that an ICML reviewer will flag on first reading.

**Required fix:** Clarify whether 50,000 documents were streamed and 5,000 selected as the PPL-scored pool (perhaps top-5000 by some criterion?), or whether the 50,000 figure is itself incorrect. All retention rate fractions must use a consistent denominator with explicit description.

### MAJOR Issues - Accuracy

**ACC-MAJOR-001: Wall-clock claim is imprecise and slightly misleading**

Section 4.1 states: "total wall-clock time ~68 minutes for all 24 runs." The Phase 4 validation report (04_validation.md) states: "~68 minutes for 22 new runs (2 pre-completed 14M runs + 22 new runs including 31M scale)." The paper's claim that ~68 minutes covers "all 24 runs" is technically imprecise — the 68-minute wall-clock included 22 runs in a single batch, with 2 pre-completed runs from an earlier session. Whether the 2 earlier runs are included in the 68-minute window is unclear. The claim is not wrong enough to be fatal but could invite questions from artifact reviewers.

**Required fix:** Change to "~68 minutes for the h-e1-v2 experiment batch (22 runs; 2 additional 14M runs pre-completed in earlier session)" or simply "~68 minutes" without the qualifying "for all 24 runs."

**ACC-MAJOR-002: Model size labeling diverges from actual parameter counts**

The paper consistently refers to "14M-parameter" and "31M-parameter" models. However, 04_validation.md reports "7.9M and 18.1M actual params" in its Key Findings section. The nominal Pythia model sizes are 14M and 31M (as labeled by the Pythia suite), but actual parameter counts differ. While the use of nominal model names (Pythia-14M, Pythia-31M) is conventional in the field, the paper makes quantitative ratio arguments ("2.2× scale difference") based on the nominal names. The actual ratio is 18.1M / 7.9M = 2.29×, which is close but the paper should either use actual parameter counts consistently or note that "14M" and "31M" are the Pythia suite nominal names.

This is particularly relevant in Section 6.2 (L1 limitation) where the paper discusses the scale ratio, and in Section 2.3 where the paper states "below approximately 14M parameters" as the capacity threshold — a claim derived from a model whose actual parameter count is 7.9M.

**Required fix:** Add a footnote at first use of "14M" and "31M": "Following the Pythia nomenclature; actual parameter counts are approximately 7.9M and 18.1M respectively." Adjust the feasibility threshold claim in Section 6 accordingly.

---

## Part 2: Engagement Check (Persona 2)

### Bored Reviewer Verdict

| Check | Result | Notes |
|-------|--------|-------|
| Abstract compelling first 2 sentences? | ✗ | Opens with "Pre-training data curation recipes..." — a topic framing, not a finding. The hook is buried in sentence 3. |
| Problem clear in 1 min? | ✓ | Yes, once past the abstract and into Introduction §1. |
| Novelty clear by end of Introduction? | ✓ | Contributions are clearly listed in §1.3. |
| Figure 1 self-explanatory from caption? | ~ | Caption gives condition mapping (C1/C2 → τ=20; C5/C6 → τ=50) but requires knowing the condition table (Section 4.1) to decode. Not fully self-explanatory. |
| Would continue reading after abstract? | ✓ | Yes — the τ*(14M) vs τ*(31M) result is interesting; Introduction solidifies the hook. |
| Abstract tells you problem, approach, result, significance? | ✓ (partial) | Problem and result: yes. Significance: hinted. Approach: compressed but present. |

**Attention Lost At:** The abstract's first sentence is the weakest opening for a results-forward paper. A bored reviewer scanning abstracts may not reach the punchline. Specifically: "Pre-training data curation recipes — perplexity filtering thresholds, deduplication aggressiveness — are typically developed at a single model scale and applied universally, with the implicit assumption that the optimal recipe transfers across model sizes." This is 38 words of setup before any finding is stated. The actual counterintuitive finding ("filtering at τ=20 is best for 14M, worst for 31M") should be in the first two sentences.

The narrative blueprint explicitly flagged this: it recommended leading with the counterintuitive finding ("same corpus, different model sizes, different optimal filtering thresholds"). The paper's Introduction does this correctly (first paragraph), but the Abstract does not. For a 100-paper ICML pile, the abstract is the triage point.

### FATAL Issues - Engagement

No FATAL engagement issues found. The paper recovers in the Introduction. A motivated reader will continue.

### MAJOR Issues - Engagement

**ENG-MAJOR-001: Abstract structure buries the lede**

The first two sentences of the abstract are setup; the finding arrives in sentence 3. For a results-forward paper where the main contribution is a surprising empirical observation (τ*(14M) ≠ τ*(31M) in the opposite direction practitioners expect), the finding should lead. Compare the Introduction's first paragraph — which opens with the observation directly and is far more compelling — to the abstract. The abstract should mirror the Introduction's opening.

**Suggested revision (not required, but strongly recommended):**
> "Filtering the same FineWeb corpus at perplexity threshold τ=20 maximizes HellaSwag performance for a 14M-parameter model — but is the *worst* configuration for a 31M-parameter model, which peaks at τ=50. This reversal, consistent across all 24 experimental conditions, challenges the standard assumption that pre-training data curation recipes transfer across model scales."

The current abstract would earn a "pass" from a motivated reader but risks losing an inattentive one at the 5-second scan.

---

## Part 3: Credibility Check (Persona 3)

### Novelty Claims Audit

| Claim | Location | Verified? | Notes |
|-------|----------|-----------|-------|
| "first controlled factorial experiment testing the Scale × Curation interaction" | Abstract, §1.2, §2.4, §7.1 | PLAUSIBLE but unverified | No prior work cited to refute; but absence of evidence ≠ no prior work |
| "first empirical evidence that optimal curation thresholds are model-scale-dependent" | §2.4 | PLAUSIBLE | DataMan (2025) shows PPL/ICL misalignment at single scale; not directly contradicted |
| τ*(14M)=20, τ*(31M)=50 direction claim | §5.1 | CONFIRMED by gate check | Consistent across 24 runs per validation report |
| "training cascades covering multiple model scales should employ scale-specific curation" | Abstract | OVERCLAIM relative to evidence | From 14M/31M PoC; applicability to 7B/13B/70B cascades is speculative |
| "proxy models below approximately 14M parameters fail to exhibit this interaction" | Abstract, §5.4 | PLAUSIBLE at 200–500 steps | Based on h-e1 (7M/16M, 200 steps) alone — very limited evidence for a general threshold claim |

### MAJOR Issues - Credibility

**CRED-MAJOR-001: "First controlled factorial experiment" claim is asserted without systematic prior work search**

The claim "We contribute the first controlled factorial experiment that directly tests the Scale × Curation interaction in LLM pre-training" appears in four locations (Abstract, §1.2, §2.4, §7.1). This is the paper's central novelty claim. However, the paper does not systematically rule out prior work — it relies on the observation that existing cited papers (ProX, DataMan, SoftDedup, FineWeb2) each evaluate at a single scale. This is a weak negative result: the cited works are not the universe of possible prior work.

A skeptical reviewer will immediately ask: does the DataComP-LM benchmark (Gururangan et al., 2024) or related DataComp work include multi-scale ablations? Does any of the C4/DCLM/RedPajama curation work include scale comparisons? The FineWeb and FineWeb2 papers — which are cited — involve substantial multi-scale ablation work for curation decisions. The authors need to engage more carefully with the FineWeb2 paper (Penedo et al., 2025) in particular, which reports "multi-language curation ablations including deduplication tuning" — whether this includes multi-scale model comparisons for a given corpus is not addressed.

The claim may well be correct, but as written it has not been defended rigorously. An ICML reviewer in data-curation will probe this.

**Required fix:** Either (a) add a more explicit statement of what prior work does and does not cover — specifically addressing FineWeb2 and any DataComp work — or (b) soften to "to our knowledge, the first" with a footnote listing the specific prior works reviewed and why they do not satisfy the factorial experiment criteria.

**CRED-MAJOR-002: The proxy model feasibility boundary claim overclaims from extremely limited evidence**

Section 5.4 and the Abstract state: "proxy models below approximately 14M parameters fail to exhibit this interaction, establishing a feasibility boundary for scalable curation ablation methodology."

This claim is derived from a single data point: h-e1 with 7M/16M proxy models at 200 training steps. The evidence base is one experiment that also suffered from MMLU floor effects (the metric itself was unusable, not just the interaction). The conclusion drawn — a general "approximately 14M parameter" threshold — implies a precision that the data does not support.

Specifically:
- Did the h-e1 proxy models fail due to insufficient scale, insufficient training steps, or metric choice (MMLU at floor)?
- The paper itself documents that HellaSwag shows variance at 14M–31M but MMLU does not. Was HellaSwag evaluated in h-e1? If not, the failure of h-e1 may be a metric failure, not a capacity failure.
- One proxy experiment at 7M/16M does not establish "approximately 14M parameters" as a threshold — it establishes that 7M/16M at 200 steps with MMLU fails. The actual threshold could be 10M or 12M or depends on the scale ratio rather than absolute parameter count.

The phrase "establishing a feasibility boundary" implies a general, reproducible finding. A 10-year veteran of the field will find this claim weakly supported.

**Required fix:** Soften to: "our h-e1 proof-of-concept experiment with 7M/16M proxy models at 200 training steps produced no signal (p=1.0, η²≈0), suggesting a minimum scale requirement; we provisionally set this at approximately 14M parameters based on h-e1-v2 results, though the exact threshold likely depends on scale ratio and training duration." Remove "establishing a feasibility boundary" — that phrase implies a calibrated, generalizable result.

**CRED-MAJOR-003: Overclaiming practical implication from PoC-scale results**

The Abstract concludes: "Our findings suggest that training cascades covering multiple model scales should employ scale-specific curation rather than a universal recipe."

The Discussion (§6.1) and Conclusion (§7.3) escalate this further, discussing applicability to "7B, 13B, 70B" parameter training cascades (§7.3). The paper's results cover only 14M/31M at 500 training steps / 1B tokens — which is explicitly 50× smaller than the original target scale (70M/160M × 50B tokens, per the ground truth YAML).

The capacity-quality trade-off hypothesis provides theoretical support for scale generalization, but this is a hypothesis, not evidence. A reviewer will note:
- The optimal τ* values (20 and 50) are specific to this scale, corpus, and training configuration.
- At 70M/160M scale, the optimal τ* values could differ substantially — potentially converging (both scales preferring τ=50) or showing no interaction at GPT-2 PPL scoring resolution.
- "Training cascades covering multiple model scales should employ scale-specific curation" as a prescriptive recommendation is not warranted from 14M/31M PoC data.

The paper does acknowledge scope limitations in §6.2 (L1), but the prescriptive framing in the Abstract and Conclusion creates a credibility gap — the limitations section contradicts the conclusion's tone.

**Required fix:** The Abstract should end with "at PoC scale (14M/31M)" explicitly. The Conclusion's §7.3 reference to 7B/13B/70B cascades should be marked as extrapolation requiring validation: "If this interaction holds at production scale, training cascades at 7B/13B/70B should consider scale-specific curation — a hypothesis our full-scale pipeline (23/23 tests passing) is positioned to test."

---

## Part 4: Human Review Notes

| Location | Note | Type |
|----------|------|------|
| §3.5, A.2: "23/23 pytest tests" | Tests are from h-e1 pipeline, not h-e1-v2. The paper says "h-e1-v2 pipeline validated end-to-end" but the 23/23 test count is attributed to h-e1. If h-e1-v2 has its own test count, it should be reported separately. Minor labeling ambiguity. | MINOR |
| §2.3: Na et al. (2024) comparison | The paper says Na et al. report "Spearman r=0.81 correlation" — this number should be verified against the actual paper. The claim is used as a foil to dismiss proxy models, so accuracy matters. Not verifiable from provided artifacts. | MINOR |
| References: "Gao et al. (2021)" marked "[UNVERIFIED in Scholar]" | The paper itself flags this in the references section. An anonymous submission should remove this annotation before submission — it reveals that a citation verification tool was used. | MINOR |
| §5.1, Table 1: std values "±0.001" for all conditions | All conditions show identical ±0.001 std. This is plausible (only 2 seeds), but reviewers may ask whether std was calculated or is a placeholder. With n=2, std should vary across conditions — identical ±0.001 for all 12 entries (6 conditions × 2 scales) looks like a rounded estimate rather than computed values. | MINOR |
| §3.2: "approximately 800/5000 documents retained (16%)" for τ=35 | The word "approximately" for τ=35 but exact counts for τ=20 and τ=50 implies the τ=35 count was not reported in the ground truth. Asymmetry between exact and approximate values within the same table should be resolved. | MINOR |
| §6.2 L1: "23/23 pytest tests passing" in limitations | The limitations section mentions the pipeline is validated and "requiring only compute to run at 70M/160M × 50B tokens." This implicitly promises future work that may not materialize. For ICML submission, this is a credibility risk if the paper is accepted and the full-scale validation is not completed. | MINOR |
| §4.1: "Each condition run for 2 model scales × 2 seeds = 24 total runs" | The math is: 6 conditions × 2 scales × 2 seeds = 24. But Section 3.1 defines 24 as 3 PPL × 2 dedup × 2 scales × 2 seeds = 24. Both are correct (6 conditions = 3 PPL × 2 dedup) but the notation shift is slightly confusing. | MINOR |
| Abstract: "consistent across all 24 experimental conditions" | Strictly speaking there are 24 runs but only 3 PPL thresholds × 2 dedup = 6 conditions. "Consistent across all 24 runs" is more precise. | MINOR |

---

## Summary for Revision Agent

### Priority Fix List

1. **[FATAL] ACC-FATAL-001: Corpus pool size inconsistency (50,000 vs 5,000).** Section 3.2 says "stream 50,000 documents as our curation pool" but then computes retention rates against 5,000. This is internally inconsistent and will be caught by any careful reviewer. Fix: add a sentence explaining the relationship (e.g., "We stream 50,000 documents and apply initial preprocessing, resulting in a 5,000-document PPL-scored pool") or correct the 50,000 figure throughout.

2. **[MAJOR] CRED-MAJOR-003: Overclaiming practical implication tone.** Abstract and Conclusion (§7.3) recommend scale-specific curation for training cascades in a prescriptive voice not warranted by 14M/31M PoC results. Add "at PoC scale" qualifiers to Abstract recommendation; reframe §7.3 cascade discussion as an extrapolation hypothesis.

3. **[MAJOR] CRED-MAJOR-001: Novelty claim "first factorial experiment" needs prior work defense.** Specifically, the paper needs to address whether FineWeb2 and DataComp-LM family of work includes multi-scale curation ablations. Add explicit statement or soften to "to our knowledge."

4. **[MAJOR] CRED-MAJOR-002: Proxy model threshold claim overclaims.** "Establishing a feasibility boundary for scalable curation ablation methodology" is too strong for one data point. Soften to provisional observation.

5. **[MAJOR] ACC-MAJOR-002: Model parameter count labeling.** Add a footnote clarifying actual vs. nominal parameter counts (7.9M/18.1M vs. 14M/31M) since quantitative ratio arguments depend on this.

6. **[MAJOR] ENG-MAJOR-001: Abstract buries the lede.** Rewrite to lead with the finding in the first two sentences, mirroring the Introduction's opening.

7. **[MAJOR] ACC-MAJOR-001: Wall-clock claim precision.** Change "~68 minutes for all 24 runs" to accurately reflect that 68 minutes covered the h-e1-v2 batch (22 runs), not all 24 runs in a single session.

### Key Concerns

- The 50,000 vs 5,000 document inconsistency is a hard accuracy bug that will cost credibility with any reviewer who does the arithmetic on retention rates.
- The "first factorial experiment" claim is the central novelty claim but is asserted rather than defended — the paper needs to explicitly engage with FineWeb2 as a potential counter-example.
- The gap between PoC scale (14M/31M) and prescriptive conclusions for 7B/13B/70B cascades undermines credibility for an expert reviewer.

### What's Working

- Table 1 numerical values match ground truth exactly — no fabrication of results.
- The paper is honest about its scope limitations in §6.2, listing L1–L5 explicitly. The problem is that the tone in Abstract/Conclusion does not match the honest limitations section.
- The factorial design (24 runs, 3×2×2×2) is internally consistent and correctly described.
- The decision to use HellaSwag over MMLU is well-justified and documented.
- Related work (§2) is organized as an argument rather than a survey — effective structure for positioning.
- The proxy model finding (§5.4) is a genuinely interesting negative result that adds value beyond the main claim.
