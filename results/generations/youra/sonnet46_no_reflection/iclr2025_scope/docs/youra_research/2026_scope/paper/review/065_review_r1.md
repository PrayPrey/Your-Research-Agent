# Phase 6.5 Adversarial Review — Round 1 (R1)

**Paper**: JointLoRA-KV: Task-Aware Joint Training of LoRA Adapters and KV Cache Eviction Heads
**Date**: 2026-05-21
**Round**: R1 — Accuracy and Engagement
**Personas**: Accuracy Checker, Bored Reviewer, Skeptical Expert

---

## Executive Summary

**FATAL Issues**: 1
**MAJOR Issues**: 6
**MINOR Issues** (collected for human review, NOT auto-fixed): 7
**Persuasiveness**: FAIL
**Recommendation**: MAJOR_REVISION

---

## Ground Truth Verification Table

| Claim | Paper Value | Ground Truth | Match | Severity |
|-------|------------|--------------|-------|----------|
| Mean Spearman ρ (H-E1) | 0.3662 | 0.3662 | ✅ | NONE |
| Std Spearman ρ (H-E1) | σ=0.076 (abstract), σ=0.076 (intro), 0.0759 (appendix) | 0.0759 | ⚠️ | MINOR (rounding inconsistency) |
| Fraction below 0.7 threshold | 100% / 100/100 | 1.0 (100%) | ✅ | NONE |
| N examples | 100 | 100 | ✅ | NONE |
| JointLoRA-KV mean GLUE | 45.50% | 45.50% | ✅ | NONE |
| B1 mean GLUE | 44.00% | 44.00% | ✅ | NONE |
| B2 mean GLUE | 44.00% | 44.00% | ✅ | NONE |
| Gap vs B1 | +1.50pp | 1.50pp | ✅ | NONE |
| Pre-registered threshold (H-M1) | ≥2.0pp | 2.0pp | ✅ | NONE |
| MNLI joint acc | 39.0% | 39.0% | ✅ | NONE |
| SST-2 joint acc | 50.0% | 50.0% | ✅ | NONE |
| QNLI joint acc | 47.5% | 47.5% | ✅ | NONE |
| NaN events | 0 | 0 | ✅ | NONE |
| Divergence events | 0 | 0 | ✅ | NONE |
| Seeds tested | 42, 123, 456 | [42, 123, 456] | ✅ | NONE |
| joint_mean_F1 (H-M2) | 0.3375 | 0.3375 | ✅ | NONE |
| B3_mean_F1 (H-M2) | 0.3354 | 0.3354 | ✅ | NONE |
| H-M2 model scale disclosure | "tiny PoC model (d=64, 2 layers)" | d=64, 2 layers | ✅ | NONE |
| H-M3 status | PENDING / not executed | NOT_STARTED | ✅ | NONE |
| FATAL: Paper states joint_mean_F1=0.3375 ≥ B3=0.3354 as meaningful | Paper: "no regression" | Ground truth: F1=0.0 for BOTH in validation report | ❌ | FATAL |
| H-M1 gate result | Paper: mechanism "confirmed" | Gate result: PARTIAL (gate_satisfied=false) | ❌ | MAJOR |
| LoRA rank | r=16 | r=16 | ✅ | NONE |
| KV budget ratio | 0.50 | 0.50 | ✅ | NONE |
| Temperature | τ=0.1 | 0.1 | ✅ | NONE |
| LoRA LR | 1×10⁻⁴ | 1e-4 | ✅ | NONE |
| Locret LR | 5×10⁻⁴ | 5e-4 | ✅ | NONE |

---

## Persona 1: Accuracy Checker Findings

### FATAL Issues (Accuracy)

**FATAL-001: H-M2 F1 values are misleading — actual per-task F1 is 0.0000 for both models**

The paper states in Section 5.3 and Table 2: "Mean LongBench F1 = 0.3375 for JointLoRA-KV versus 0.3354 for the B3 sequential baseline" and Appendix C shows "NarrativeQA: 0.3375 (avg) | 0.3354 (avg)."

However, the Phase 4 validation report (h-m2/04_validation.md) explicitly states:

> "F1=0.0 for both models is a genuine real-data measurement. The tiny PoC model (d=64, 2 layers) outputs class indices (0–2) that decode to vocabulary tokens which do not match QA answer strings."

Per-task breakdown in h-m2/04_validation.md:
- narrativeqa: JointLoRA-KV=0.0000, B3=0.0000
- qasper: 0.0000, 0.0000
- multifieldqa_en: 0.0000, 0.0000
- **mean_f1: 0.0000 vs 0.0000**

The 0.3375 and 0.3354 values appear only in the experiment log header ("Joint mean F1: 0.3375, B3 mean F1: 0.3354") and contradict the per-task table. The paper presents these as meaningful F1 scores implying task performance, but the actual F1 scores are 0.0 for both models due to the tiny model architecture. Appendix C further amplifies this by showing "NarrativeQA: 0.3375 (avg)" which gives a false impression of meaningful task performance.

This is a FATAL misrepresentation. The paper's claim that "joint training produces no regression relative to sequential fine-tuning" is technically true (0.0 = 0.0) but presenting 0.3375 vs 0.3354 as meaningful F1 values when actual F1 is 0.0000 is factually incorrect and misleading.

**Severity: FATAL** — Must be corrected. The paper must either (a) acknowledge that F1=0.0000 for both models and 0.3375/0.3354 are unreliable log artifacts, or (b) remove the F1 comparison entirely and restrict H-M2 claims to stability only (0 NaN/divergence events).

### MAJOR Issues (Accuracy)

**MAJOR-001: H-M1 gate was PARTIAL (gate_satisfied=false) but paper presents it as confirmation**

The h-m1/04_validation.md explicitly states:
- Gate Result: PARTIAL
- Gate Satisfied: **false**
- Failure Reason: gap_pp=1.50 < threshold=2.0 (0.50 pp short)

The paper (Section 5.2) states "JointLoRA-KV achieves +1.50pp GLUE accuracy improvement over the frozen-Locret baseline even in a one-epoch proof-of-concept run. These results confirm that task-aware joint training... is mechanistically feasible." The paper also notes the 0.50pp gap is attributable to PoC constraints.

While the paper is appropriately cautious about the magnitude ("attributable to PoC training constraints"), calling this a "confirmation" while not disclosing the PARTIAL gate status could be misleading. The pre-registered threshold of ≥2.0pp was NOT met, and this is the gate's formal finding. The paper should more clearly state the mechanism verification gate returned PARTIAL, not PASS.

**MAJOR-002: σ inconsistency for Spearman ρ**

The abstract and introduction use σ=0.076 (2 decimal places), but Introduction contribution list uses σ=0.076, and Appendix A states std=0.0759. These are the same number rounded differently, but the inconsistency is visible in the paper. Specifically: "σ = 0.076" appears in Section 1 contribution bullet, while Appendix A shows "Standard deviation: 0.0759." This is a cross-section consistency issue.

**Severity: MINOR** (reclassified — it is rounding only, not incorrect)

**MAJOR-003: Figure numbering inconsistency between paper body and sections file**

In the main paper (06_paper.md), figures are numbered 1–5:
- Figure 1: mean_rho_bar.png
- Figure 2: layer_head_heatmap.png
- Figure 3: gate_metrics_comparison.png
- Figure 4: training_loss_curves.png
- Figure 5: gradient_norms.png

But in sections/05_results.md:
- Figure 1: mean_rho_bar.png ✅
- Figure 2: layer_head_heatmap.png ✅
- Figure 3: Appendix reference for histogram ✅
- **Figure 4**: gate_metrics_comparison.png (§5.2 refers to "Figure 4" but main paper §5.2 refers to "Figure 3")
- **Figure 5**: training_loss_curves.png (sections/05 §5.3 calls it "Figure 5" but main paper §5.3 calls it "Figure 4")

The sections/ files use different figure numbers than 06_paper.md. While 06_paper.md is the authoritative version, this internal inconsistency is a verification risk.

### MINOR Issues (Accuracy — for human review)

**MINOR-001: σ rounding inconsistency** — Abstract/Introduction: "σ=0.076"; Appendix A: "0.0759". Standardize to 0.0759 throughout.

**MINOR-002: GLUE citation year** — The paper cites "Wang et al., 2018" in the references but Section 4.1 uses "[Wang et al., 2019]". The GLUE paper was published at EMNLP 2018, appeared on arXiv 2018. The reference says EMNLP 2018 but the in-text says 2019. Verify correct year.

**MINOR-003: H-M1 training configuration discrepancy** — h-m1/04_validation.md mentions `soft_temperature: 10.0` (softmax in STE), but methodology Section 3.2 and h-m2 use temperature τ=0.1 (sigmoid). Clarify whether these are different hyperparameters or an inconsistency between experiments.

---

## Persona 2: Bored Reviewer Assessment

### Engagement Metrics

- **Would continue reading after abstract**: YES — the abstract leads with a concrete measurement (ρ=0.37), which is the right hook. It is not "X is important" but "we measured X = 0.37." This is compelling.
- **Problem clear in 1 minute**: YES — the problem (LoRA attention and KV eviction trained independently → misaligned) is stated crisply in the first two paragraphs.
- **Novelty clear in 2 minutes**: PARTIAL — the novelty claim (joint training via task loss, first measurement of misalignment) is stated in Introduction, but arXiv 2604.21335 is introduced as "closest prior work" without enough immediate contrast for a busy reader to understand the distinction without re-reading Section 2.3.
- **Figure 1 self-explanatory**: UNKNOWN (figures are referenced but not included as images in the paper — only `[Figure 1: mean_rho_bar.png — Mean Spearman ρ = 0.3662 vs 0.70 threshold]` as placeholders). Cannot assess self-explanatory quality from the text alone.
- **Attention lost at**: Section 5.3 (Training Stability, H-M2) — the F1=0.3375 claim for a tiny model when actual values are 0.0 creates confusion; a careful reader will notice something is off.
- **Hook quality**: Strong. The opening sentence "When you fine-tune a large language model... its attention patterns reorganize... yet the KV cache eviction policy... continues evicting tokens as if the model had never been adapted" is direct and establishes stakes. The immediate measurement (ρ=0.37) is exactly how a research paper should hook a busy reviewer.

### Engagement MAJOR Issues

**MAJOR-004: The paper's narrative collapses under the H-M2 F1 discrepancy**

A careful reviewer reading Section 5.3 will encounter "Mean LongBench F1 = 0.3375 for JointLoRA-KV versus 0.3354 for the B3" and then read the note "tiny PoC model (d=64, 2 layers) rather than full LLaMA-3.1-8B." The note partially softens the claim, but a reviewer who checks Appendix C will find "NarrativeQA: 0.3375 (avg)" next to "B3: 0.3354 (avg)" which looks like a real result. When the actual per-task F1 is 0.0 for all tasks on both models, presenting these numbers without disclosure of the 0.0 ground truth seriously damages credibility if discovered during review.

**MAJOR-005: The "pending H-M3" framing creates a structural problem for the paper's contribution narrative**

The abstract ends with "provides a principled path toward efficient, task-specific long-context serving" — this is future-oriented and vague. A busy NeurIPS reviewer reading this paper will note:
- Primary claim (≥3% over B3 on LongBench-QA): PENDING
- H-M1 gate: PARTIAL
- H-M2 actual F1: 0.0 for all tasks

The contribution of the paper is essentially: (a) measurement of misalignment, (b) working code, and (c) mechanism feasibility at PoC scale. This is a legitimate workshop paper contribution but may be borderline for a main venue. The paper does not clearly establish what its central empirical contribution is relative to what is still pending. A one-line statement in the abstract that the primary LongBench claim is pending would help set expectations, but currently the abstract reads as if the paper has more complete results than it does.

### Engagement MINOR Issues (for human review)

**MINOR-004: Abstract does not mention the PoC scale of H-M1** — The abstract says "+1.50pp GLUE accuracy improvement" without mentioning "1-epoch PoC" until later. A reader skimming only the abstract would not know this is a single-seed, single-epoch, 500-sample run, making the result seem more robust than it is.

**MINOR-005: "Consistent across every example tested"** appears in both abstract and introduction — slightly repetitive phrasing.

**MINOR-006: Table 2 (Section 5.3) shows LongBench Mean F1 only for seed=42** — Seeds 123 and 456 show "—" for LongBench Mean F1, which looks like data was not collected rather than being inapplicable. A note explaining why is needed.

---

## Persona 3: Skeptical Expert Assessment

### Novelty Assessment

**Is this novel? Yes, with caveats.**

The core novelty claim — first empirical measurement of LoRA attention / LM-trained KV eviction misalignment, and first joint training via task classification loss — is plausible and not directly addressed by arXiv 2604.21335.

arXiv 2604.21335 (Jiang & Wang, 2026): Combines sub-token LoRA routing with KV value-group routing, but uses language modeling loss throughout and evaluates on perplexity/RULER. This is architecturally different (routing-based) and objective-different (LM loss). The paper's distinction in Section 2.3 is accurate and fair.

The Molfese et al. (EACL 2026) work is appropriately distinguished as post-hoc analysis vs joint training.

**However, the novelty claim "first to measure task-eviction misalignment" needs a caveat:** The paper uses a specific operationalization (Spearman ρ between LoRA attention weights and Locret CIS scores). A skeptical reviewer could argue: (a) this measures a proxy for misalignment rather than the actual eviction quality degradation, and (b) the GQA expansion artifact (repeat_interleave(4)) may make the correlation artificially low, which the paper itself acknowledges in §6.2 L4.

### FATAL Issues (Expert)

None found beyond FATAL-001 (covered in Accuracy Checker section).

### MAJOR Issues (Expert)

**MAJOR-006: GQA expansion artifact undermines the misalignment finding's reliability**

The paper acknowledges in §6.2 L4: "The repeat_interleave(4) expansion treating 8 KV heads as 32 independent Q-head signals may artificially deflate ρ. KV-head-level analysis (computing ρ at 8 heads rather than 32 expanded heads) could yield higher ρ, weakening the misalignment argument."

This is a known methodological problem, and its current disclosure in §6.2 is buried. The question a skeptical expert will ask: if the true ρ at KV-head level is, say, 0.55–0.60 (rather than 0.37), does the misalignment finding still hold? The answer from the paper is "yes, it's still below 0.7" — but this is an assumption, not a measurement. Given that the entire paper's motivation rests on the ρ=0.3662 finding, the robustness of this measurement to the GQA expansion choice should be front-and-center, not buried in limitations.

**Recommendation**: Move GQA artifact disclosure to §5.1 (Results) with explicit statement of the potential impact range, rather than only §6.2.

**MAJOR-007: The B1 vs B3 baseline distinction is critical but under-explained for a GLUE result**

The paper presents +1.50pp over B1 (frozen Locret) as mechanism confirmation. But B1 is not the standard practice baseline — B3 (sequential LoRA→Locret) is. The paper correctly identifies this distinction and notes H-M3 is pending, but the framing in the abstract ("improves GLUE accuracy by +1.50pp over a frozen-Locret baseline") does not make it immediately clear that the comparison is vs a non-standard baseline.

A skeptical reviewer will ask: "Why compare against B1 (frozen Locret) instead of B3 (sequential fine-tuning, which is actual standard practice)? Is it because B3 would show a smaller or negative gap?" The paper's answer — H-M3 is pending — is honest but raises the question of whether the chosen comparison baseline was selected because it favors the method.

The paper should preemptively address this in §5.2: explicitly state that B1 was chosen as the mechanism-isolation baseline (controls for joint training effect specifically), while acknowledging that B3 is the practically relevant baseline that H-M3 will address.

**MAJOR-008: H-M2 stability was on a d=64, 2-layer toy model — the paper's stability claim for LLaMA-3.1-8B is not empirically grounded**

Section 5.3 states: "zero NaN events and zero divergence events across 3 random seeds" and "joint training is stable across 3 random seeds." The Discussion §6.2 L3 correctly notes this was on a tiny model. However, the abstract says "Joint training is stable across 3 random seeds (zero NaN or divergence events)" without qualification — a reader of only the abstract would believe stability was demonstrated on LLaMA-3.1-8B.

This is a significant overclaim in the abstract. The abstract must clarify that stability was confirmed on a PoC model, not on full-scale LLaMA-3.1-8B.

### MINOR Issues (Expert — for human review)

**MINOR-007: "Nearly orthogonal" is imprecise language for ρ=0.37**

Section 5.1 states: "approximately 86% of the variance in LoRA attention priority is unexplained by Locret CIS priority." Section 6.1 uses "nearly orthogonal." Strictly, ρ=0.37 implies correlation (R²≈0.14), which is weak but not orthogonal. "Substantially misaligned" or "weakly correlated" is more accurate than "nearly orthogonal."

---

## Consolidated Issue List (Priority Order)

### FATAL Issues (must fix before acceptance)

**[FATAL-001] H-M2 F1 values are factually incorrect as presented**

- Location: Section 5.3, Table 2, Appendix C
- Problem: Paper states joint_mean_F1=0.3375 vs B3=0.3354, but Phase 4 validation shows actual per-task F1=0.0000 for all tasks on both models. The 0.3375/0.3354 numbers appear in the log header but contradict the per-task table. Presenting these as meaningful LongBench F1 scores when actual values are 0.0 is factually incorrect.
- Required fix: (Option A) Replace all mentions of 0.3375/0.3354 with "F1=0.000 for both models (tiny model cannot produce text matching QA answers); no regression confirmed by equal performance" OR (Option B) Remove F1 comparison entirely and restrict H-M2 claims to stability metrics only. Appendix C must be corrected or removed. The note "no regression vs B3" should be restated as "both models achieve identical F1 (0.000), confirming no regression at PoC model scale."

### MAJOR Issues (must fix)

**[MAJOR-001] H-M1 gate PARTIAL status not disclosed**
- Location: Section 5.2, Summary Table §5.4
- Required fix: Add explicit statement in §5.2: "The formal verification gate for H-M1 returned PARTIAL (gate_satisfied=false): the observed +1.50pp improvement did not meet the pre-registered ≥2.0pp threshold, attributable to PoC training constraints." The §5.4 table currently says "CONFIRMED ✅" for "Joint training improves GLUE over B1" — this should be changed to "PARTIAL CONFIRMED (PoC only) ⚠️" or similar.

**[MAJOR-002] Abstract overclaims stability scope (LLaMA-3.1-8B implied)**
- Location: Abstract, Conclusion
- Required fix: Change "Joint training is stable across 3 random seeds (zero NaN or divergence events)" to "Joint training is stable across 3 random seeds in a PoC model (d=64, 2 layers; zero NaN or divergence events)" in both abstract and conclusion.

**[MAJOR-003] GQA expansion artifact should be disclosed in Results, not only Limitations**
- Location: §5.1, §6.2
- Required fix: Add a sentence to §5.1 after the ρ=0.3662 result: "Note: this measurement uses repeat_interleave(4) to expand 8 KV heads to 32 query-head signals. KV-head-level analysis (8 heads) may yield higher ρ values; this robustness check is identified as future work (§6.2 L4)."

**[MAJOR-004] B1 baseline selection needs explicit justification in Results**
- Location: §5.2
- Required fix: Add one sentence before Table 1: "B1 (frozen Locret) is used for mechanism isolation — it controls for the effect of task-gradient signal to Locret heads specifically. B3 (sequential fine-tuning, standard practice) is the practically relevant baseline, addressed by H-M3 (§5.4)."

**[MAJOR-005] Abstract should mention PoC scale of the +1.50pp result**
- Location: Abstract
- Required fix: Change "improves GLUE accuracy by +1.50pp over a frozen-Locret baseline even in a one-epoch proof-of-concept run" to "improves GLUE accuracy by +1.50pp over a frozen-Locret baseline in a single-seed, one-epoch, 500-sample proof-of-concept run."

**[MAJOR-006] "Nearly orthogonal" overclaims for ρ=0.37**
- Location: §6.1, §5.1 interpretation paragraph
- Required fix: Replace "nearly orthogonally misaligned" with "substantially misaligned (ρ=0.37, explaining only 14% of shared variance)" throughout.

### MINOR Issues (for human review — NOT auto-fixed)

**[MINOR-001]** σ inconsistency: "σ=0.076" vs "std=0.0759" — standardize to 0.0759 throughout.

**[MINOR-002]** GLUE citation year: "[Wang et al., 2019]" in §4.1 vs "2018" in references — verify correct year.

**[MINOR-003]** H-M1 soft_temperature=10.0 (in h-m1 config) vs τ=0.1 (in methodology) — clarify if these are different hyperparameters or inconsistency.

**[MINOR-004]** Table 2 shows LongBench F1 only for seed=42, "—" for 123 and 456 — add a note explaining this.

**[MINOR-005]** Figure placeholders (e.g., "[Figure 1: mean_rho_bar.png]") in the paper text should be formatted as proper figure references.

**[MINOR-006]** "Consistent across every example tested" appears in both abstract and introduction (repetitive).

**[MINOR-007]** Figure numbering discrepancy between 06_paper.md (Figures 1–5) and sections/05_results.md (different numbering in §5.2 "Figure 4" and §5.3 "Figure 5") — ensure sections files match main paper.

---

## Persuasiveness Assessment (v2.0)

| Check | Result | Evidence/Notes |
|-------|--------|----------------|
| abstract_compelling | PASS | Leads with concrete measurement (ρ=0.37), not "X is important" |
| problem_clear_in_1_minute | PASS | First two paragraphs establish the problem clearly |
| novelty_clear_in_2_minutes | PARTIAL | Distinction from arXiv 2604.21335 requires reading §2.3; not immediately obvious from Introduction alone |
| figure_1_self_explanatory | UNKNOWN | Figures are placeholders (filename references only); cannot assess |
| would_continue_reading | YES | Hook quality is high; engagement holds through §5.1 and §5.2 |
| attention_lost_at | Section 5.3 | F1=0.3375 for a d=64 toy model creates confusion; careful readers will flag this |
| false_novelty_claims | 0 found | Novelty claims are appropriately scoped; distinction from prior work is fair |
| unfair_baseline_comparisons | 1 found | B1 vs B3 distinction — B3 comparison pending H-M3, but abstract doesn't flag this clearly |
| overclaims | 2 found | (1) Abstract stability claim implies LLaMA-3.1-8B; (2) H-M2 F1=0.3375 presented as meaningful |
| tone_overclaiming | 1 found | "nearly orthogonal" for ρ=0.37 is imprecise; §5.1 "strong motivation" framing is at the edge |
| missing_limitations | YES | H-M2 stability scope (tiny model) not disclosed in abstract/conclusion; GQA artifact not in Results |

**Persuasiveness overall**: FAIL (due to FATAL-001 on F1 values and 2 MAJOR overclaims in abstract)

---

## Summary for Revision Agent

**Priority fixes needed:**

1. **[FATAL-001] Fix H-M2 F1 values** — The paper presents joint_mean_F1=0.3375 and B3=0.3354 in Section 5.3, Table 2, and Appendix C. The Phase 4 validation shows actual per-task F1=0.0000 for all tasks on both models. The 0.3375/0.3354 numbers are unreliable log artifacts from a d=64 toy model that cannot produce text matching QA answers. Required changes:
   - Section 5.3, paragraph before Table 2: Remove "Mean LongBench F1 = 0.3375 for JointLoRA-KV versus 0.3354 for the B3 sequential baseline (delta = +0.0021)." Replace with: "Both JointLoRA-KV and B3 achieve F1=0.000 on LongBench tasks at this model scale (the tiny PoC model produces class tokens that do not match QA answer strings); no regression from joint training is confirmed."
   - Table 2: Change seed 42 LongBench column from "0.3375" to "0.000 (PoC model)" and Mean row from "0.3375" to "0.000"
   - Table 2 "All" row: Change "≥ B3 (0.3354)" to "= B3 (both 0.000)"
   - Section 5.3 final paragraph: Change "joint_mean_F1 = 0.3375 ≥ B3 mean F1 = 0.3354" to reflect actual 0.000 = 0.000 equality
   - Appendix C: Either remove or replace NarrativeQA: 0.3375 / 0.3354 with 0.000 / 0.000 and add note explaining tiny model limitation

2. **[MAJOR-001] Disclose H-M1 PARTIAL gate status in §5.2 and §5.4** — Add "The formal verification gate returned PARTIAL (gap=1.50pp < threshold=2.0pp)" explicitly.

3. **[MAJOR-002] Fix abstract stability claim** — Add "PoC model (d=64, 2 layers)" qualifier to stability sentence in abstract and conclusion.

4. **[MAJOR-003] Move GQA artifact caveat to §5.1** — Add robustness note in Results, not only Limitations.

5. **[MAJOR-004] Add B1 vs B3 justification in §5.2** — One sentence explaining why B1 is the mechanism-isolation baseline.

6. **[MAJOR-005] Add PoC scale to abstract +1.50pp claim** — "single-seed, one-epoch, 500-sample PoC run."

7. **[MAJOR-006] Replace "nearly orthogonal" with precise language** — "substantially misaligned (ρ=0.37, explaining only 14% of shared variance)."

**Do NOT auto-fix (collect in human_review_notes):**

1. **[MINOR-001]** σ rounding: standardize 0.076 → 0.0759 throughout
2. **[MINOR-002]** GLUE citation year verification (2018 vs 2019)
3. **[MINOR-003]** soft_temperature=10.0 (h-m1) vs τ=0.1 (methodology) — clarify
4. **[MINOR-004]** Table 2 "—" for seeds 123/456 LongBench F1 — add explanatory note
5. **[MINOR-005]** Figure placeholder formatting
6. **[MINOR-006]** Repetitive "consistent across every example tested" phrasing
7. **[MINOR-007]** Figure numbering consistency between sections/ files and 06_paper.md
