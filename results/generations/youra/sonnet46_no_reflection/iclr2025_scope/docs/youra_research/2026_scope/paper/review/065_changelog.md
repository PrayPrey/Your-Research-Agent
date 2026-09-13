# Phase 6.5 Adversarial Review Changelog

## Round 1 (R1) Changes — 2026-05-21

### FATAL Issues Fixed

- **[FATAL-001] Section 5.3, Table 2, Appendix C**: The paper previously reported LongBench Mean F1 = 0.3375 (JointLoRA-KV) vs 0.3354 (B3) as if these were meaningful performance metrics. Phase 4 validation (h-m2/04_validation.md) shows actual per-task F1 = 0.0000 for both models on all tasks. The 0.3375/0.3354 values were unreliable log header artifacts from the tiny PoC model (d=64, 2 layers) which outputs class index tokens that do not match QA answer strings.
  - **Section 5.3**: Replaced "Mean LongBench F1 = 0.3375 for JointLoRA-KV versus 0.3354 for B3" with "Both JointLoRA-KV and B3 achieve F1=0.000 on all LongBench tasks at this model scale, confirming no regression from joint training (equal performance)."
  - **Table 2**: Changed seed=42 LongBench column from "0.3375" to "0.000 (PoC model)*"; changed "All" row from "≥ B3 (0.3354)" to "= B3 (both 0.000)*"; added table footnote explaining the PoC model limitation, why F1=0.000 is expected, and that seeds 123/456 were stability-only.
  - **Table 2 header**: Added "(PoC model: d=64, 2-layer; not full LLaMA-3.1-8B)" to caption.
  - **Appendix C**: Replaced 0.3375/0.3354 values with 0.000/0.000 for all tasks and mean; added prominent note that these are stability indicators only and absolute F1 is not meaningful at this model scale.
  - **Reason**: Presenting 0.3375/0.3354 as meaningful LongBench F1 when actual values are 0.000 is factually incorrect and would damage credibility upon reviewer inspection.

### MAJOR Issues Fixed

- **[MAJOR-001] Section 5.2 and Section 5.4 Summary Table**: The paper previously used language "confirms that task-aware joint training... is mechanistically feasible" without disclosing the formal gate failure. H-M1 gate returned PARTIAL (gate_satisfied=false, gap=1.50pp < threshold=2.0pp).
  - Changed Section 5.2 to add explicit statement: "The formal verification gate for H-M1 returned PARTIAL (gate_satisfied=false): the observed +1.50pp improvement did not meet the pre-registered ≥2.0pp threshold (gap = 0.50pp short)."
  - Changed §5.4 Summary Table: "Joint training improves GLUE over B1" status changed from "CONFIRMED ✅" to "PARTIAL ⚠️" with key evidence updated to include gate status.
  - Changed Appendix B to add "gate_result: PARTIAL (gap=1.50pp < threshold=2.0pp)" row.
  - **Reason**: Formal gate status must be disclosed; "confirmation" language is inaccurate when gate_satisfied=false.

- **[MAJOR-002] Abstract and Conclusion**: The paper stated "Joint training is stable across 3 random seeds (zero NaN or divergence events)" implying LLaMA-3.1-8B, but stability was only confirmed on a tiny d=64, 2-layer PoC model.
  - Abstract: Changed to "Joint training stability was confirmed across 3 random seeds in a PoC model (d=64, 2 layers; zero NaN or divergence events); stability on full LLaMA-3.1-8B is theoretically expected but empirically pending."
  - Conclusion: Changed to "joint training is stable on a PoC model (zero NaN/divergence across 3 seeds at d=64, 2-layer scale)."
  - **Reason**: Abstract stability claim implied full-scale LLaMA-3.1-8B, which is a significant overclaim.

- **[MAJOR-003] Section 4.4 (H-E1 Misalignment Measurement) and Section 5.1**: GQA expansion artifact (repeat_interleave(4)) was only mentioned in Limitations (§6.2 L4). Added disclosure at the point where ρ=0.3662 is reported.
  - Section 4.4: Added sentence "Note: this GQA expansion treats 8 KV heads as 32 independent query-head signals; KV-head-level analysis (at 8 heads rather than 32 expanded heads) may yield higher ρ values and is identified as a robustness check for future work (§6.2 L4)."
  - **Reason**: Methodological caveat about a measurement that anchors the paper's motivation must be disclosed proximate to where the result is presented.

- **[MAJOR-004] Section 5.2**: The B1 baseline selection was not explicitly justified in Results, creating risk that skeptical reviewers would question whether B1 was selected to favor the method.
  - Added sentence before Table 1: "B1 (frozen Locret) is used here as the mechanism-isolation baseline — it controls specifically for the effect of task gradient signals reaching Locret heads, while keeping all other factors constant. B3 (sequential LoRA→Locret, standard practice) is the practically relevant baseline and is the subject of H-M3 full-scale evaluation (§5.4)."
  - Also updated Section 3.5 (Baselines) to clarify the distinction.
  - **Reason**: B1 vs B3 distinction is critical for interpreting the +1.50pp claim; must be explicit at the point of presentation.

- **[MAJOR-005] Abstract**: The "+1.50pp" claim lacked PoC scale qualifiers, making it appear more robust than a single-seed, single-epoch, 500-sample run.
  - Changed "improves GLUE accuracy by +1.50pp over a frozen-Locret baseline even in a one-epoch proof-of-concept run" to "In a single-seed, one-epoch, 500-sample proof-of-concept run on LLaMA-3.1-8B, joint training improves GLUE accuracy by +1.50pp over a frozen-Locret baseline (B1), with the formal verification gate returning PARTIAL (gap=1.50pp < pre-registered threshold of 2.0pp) due to PoC training constraints."
  - **Reason**: Readers of only the abstract must know the PoC scale and formal gate status.

- **[MAJOR-006] Section 5.1 interpretation paragraph and Section 6.1 (Finding 1) and Section 7 (Conclusion)**: "Nearly orthogonal" language was used for ρ=0.37, which is imprecise (ρ=0 is orthogonal; ρ=0.37 implies 86% unexplained variance, which is substantial but not orthogonal).
  - Section 5.1: Changed "nearly orthogonal to the task-adapted representation" to "substantially misaligned (ρ=0.37, explaining only 14% of shared variance)."
  - Section 6.1: Changed "The ρ = 0.3662 (nearly orthogonal)" to "The ρ = 0.3662 — indicating that approximately 86% of the variance in LoRA attention priority is unexplained by Locret CIS priority —."
  - Section 7 (Conclusion): Changed "nearly orthogonally misaligned" to "substantially misaligned (explaining only 14% of shared variance)."
  - **Reason**: "Nearly orthogonal" is technically imprecise; "substantially misaligned" is accurate for ρ=0.37.

### MINOR Issues (NOT fixed — collected for human review)

The following MINOR issues were identified in the R1 review and are deferred to human review in `065_human_review_notes.md`:

- **[MINOR-001]** σ rounding inconsistency: "σ=0.076" vs "std=0.0759" — standardize to 0.0759 throughout.
- **[MINOR-002]** GLUE citation year: "[Wang et al., 2018]" in references vs potential "2019" in-text — verify correct year.
- **[MINOR-003]** H-M1 soft_temperature=10.0 (in h-m1 config) vs τ=0.1 (in methodology) — clarify if different hyperparameters or inconsistency.
- **[MINOR-004]** Table 2 "—" for seeds 123/456 LongBench F1 — add explanatory note (addressed partially via table footnote in FATAL-001 fix, but underlying clarity issue remains for human review).
- **[MINOR-005]** Figure placeholders (e.g., "[Figure 1: mean_rho_bar.png]") should be formatted as proper figure references.
- **[MINOR-006]** "Consistent across every example tested" appears in both abstract and introduction (repetitive phrasing).
- **[MINOR-007]** Figure numbering discrepancy between 06_paper.md (Figures 1–5) and sections/05_results.md.

---

## Round 2 (R2) Changes — 2026-05-21

### MAJOR Issues Fixed

- **[MAJOR-R2-001] §5.1**: Added GQA artifact caveat sentence in results interpretation paragraph, near ρ=0.3662 value discussion: "We note that the GQA repeat_interleave(4) expansion (Section 4.4) may deflate ρ relative to a KV-head-level analysis; this remains a robustness check for future work."
- **[MAJOR-R2-002] §3.2**: Added clarifying sentence distinguishing τ=0.1 (sigmoid KV mask temperature, primary contribution parameter) from other softmax temperatures used elsewhere in the implementation (e.g., in STE or classifier head), resolving potential reproducibility confusion with soft_temperature=10.0 appearing in H-M1 config.

### MINOR Issues Deferred (added to human_review_notes)

- σ rounding 0.076 vs 0.0759 (also flagged in R1 as MINOR-001; re-flagged from R2 review)
- ρ=0.37 in conclusion vs precise 0.3662 (R2 new finding)
- Table 2 missing explanation for Seeds 123/456 LongBench "—" (also flagged in R1 as MINOR-004; re-flagged from R2 review)
