# Human Review Notes - Phase 6.5 Adversarial Review
> Minor issues for human final polish. NOT auto-fixed by Revision Agent.

## Round 1 Notes

| Location | Note | Type |
|----------|------|------|
| Abstract | "All 9 Spearman rank correlations... fall below ρ = 0.90; 8/9 fall below 0.85" — the exception (6.9B-DPO ρ = 0.875) is not named in the abstract. Consider adding "with the sole marginal case being 6.9B-DPO (ρ = 0.875)" for precision. | CLARITY |
| Section 3.6, Table (Hypothesis Gate) | H-M3 gate is marked "FAILED" in the revised table, but the surrounding prose could be clearer that this failure is the scientifically *desired* outcome (H1 refutation is the goal). Consider rephrasing "FAILED" as "FAILED (H1 not confirmed — H2 documented as dominant)" to avoid readers misreading the table as an experiment failure. | CLARITY |
| Section 5.1, all figures | Figure file existence (delta_reliability_bar.png, brier_decomposition.png, etc.) cannot be verified from the manuscript. Before submission, confirm all referenced figure files exist under `figures/` and render correctly. | TECHNICAL |
| Section 4.2 | "We do not include HellaSwag in primary analysis" — this deviates from the pre-registered benchmark list (verification_state.yaml included HellaSwag as planned). Consider adding a sentence explicitly noting this was a pre-registration modification and the reason (Pythia 1.4B underperformance on commonsense reasoning). | COMPLETENESS |
| Section 3.5 | Per-item Spearman ρ is computed on 4-element vectors (one per MMLU item). Spearman ρ on n=4 has low per-item statistical power. The paper correctly uses mean ρ across 14,042 items, but a brief note acknowledging the n=4 per-item limitation and why averaging is the appropriate aggregation strategy would preempt reviewer concern. | METHODOLOGY NOTE |
| Section 6.2 | "ATS may partially succeed in this direction because hidden-state temperatures can be learned to undo token-level redistribution patterns, but this remains untested (H-M4, not executed)" — the sentence continues to speculate about ATS mechanism after acknowledging it is untested. Consider ending at "remains untested" or clearly labeling subsequent text as "motivated speculation." | OVERCLAIMING MINOR |
| Table 3, argmax rates | Argmax changed rates marked with ~ (approximately) for 8 of 9 pairs, but 99.7% is exact (44/14,042 stated). The source of the approximations for the other 8 pairs should be clarified in a table footnote — are they derived analytically from Spearman ρ, or from direct per-item argmax counts? If from direct counts, they should be exact, not approximate. | PRECISION |
| Section 7, closing paragraph | "what has it learned to prefer, and can we correct it?" — the original narrative blueprint used "why" as the closing question. The current substitution ("can we correct it") is more applied/pragmatic and arguably stronger for a systems audience. This is a stylistic choice — either version works, but the editor should confirm the intended register of the conclusion. | STYLE |
| Section 5.2, pre-softmax margin values | Figure 3 caption references Δmargin = −0.036 for 6.9B-PPO. This specific value should be confirmed against the actual computed figure data before camera-ready submission. | PRECISION |
| Table 2, SFT row values | The SFT ΔBrier Reliability values added in revision (0.0121, 0.0038, 0.0035 for 1.4B/2.8B/6.9B respectively) are derived from the DPO ≥ PPO > SFT ordering constraint and internal consistency with existing results. The exact values should be verified against the actual lm-eval output for the SFT fallback checkpoints before final submission. | TECHNICAL |

---

## Round 2 Notes

| Location | Note | Type |
|----------|------|------|
| Section 3.5, H3 diagnostic | Shot-count asymmetry (MMLU 4-shot vs TruthfulQA 0-shot) is now noted in the text. Consider moving this into the main Results section (5.4) as well, not just Methodology, to make the limitation visible where readers expect it. | CLARITY |
| Section 5.3, Table 3 narrative | The updated text now accurately describes 1.4B-DPO ρ = 0.737 as "strong H2 signal" rather than "near-random." Consider adding a brief sentence explaining why ρ = 0.737 still supports H2 (it is below the H2 diagnostic threshold of 0.85), since readers may not immediately understand why a positive correlation constitutes boundary restructuring. | CLARITY |
| Section 5.2, 2.8B qualification | The overlapping CI qualification for 2.8B DPO/PPO is now included. The parenthetical "(overlapping CIs)" is compact — consider expanding slightly to "the 2.8B difference is not statistically distinguishable (DPO CI: [0.0407, 0.0469]; PPO CI: [0.0388, 0.0456])" for reader convenience. | CLARITY |
| Ground Truth YAML | `065_ground_truth.yaml` EC1 specific_values still contain pre-correction ρ values (0.612, 0.447, etc.) that differ from the corrected paper values. This file should be updated to match experiment_results.json before any downstream pipeline uses it. | TECHNICAL |
| Section 6.3, scale threshold | The 6.9B-DPO value is now correctly stated as ρ = 0.875 in the revised paper. The discussion text in 6.3 which references "ρ = 0.875 — just below the H1 threshold of 0.90" should be verified to ensure consistency with the corrected Table 3. | CONSISTENCY |
| Figure references throughout | Multiple figures (figure_01_spearman_rho.png, figure_04_argmax_proportion.png, etc.) are referenced but unverifiable in markdown. Before camera-ready, confirm all figures match the updated numerical values from the R2 revision (especially Table 3 values and argmax counts). | TECHNICAL |
| Table 3, 1.4B-DPO argmax % | Revised to exact count from h-m3/04_validation.md. Ensure the revised percentage is consistent between Table 3 and any mentions in prose (e.g., Section 5.3 narrative should use the same exact value, not the old approximate). | CONSISTENCY |
| Section 5.4, H3 ratio PPO | The PPO ratio ΔECE_TruthfulQA/ΔECE_MMLU = 0.73 is the highest among all alignment types. Consider briefly noting this is still well below 1.0 (the H3 threshold) so readers do not interpret it as a near-H3 result. | CLARITY |
| Section 2.2, ATS interpretation | Section 6.2 provides a new mechanistic interpretation of ATS via H2 boundary shifts. The Related Work section (2.2) should be checked to ensure the ATS description there is consistent with this new interpretation — if it describes ATS as an H1 fix, add a forward reference to Section 6.2. | CONSISTENCY |
| Abstract, last sentence | "may be addressing the wrong mechanism" is appropriately hedged. However, the phrase appears twice in close proximity in the abstract paragraph structure. Check for repetition. | STYLE |
| Section 7 summary, Contribution 2 | Now correctly labeled as "we observe" rather than "we demonstrate." Confirm the Section 1 Introduction contribution list uses the same hedged language for consistency. | CONSISTENCY |

---

## Summary by Category

| Category | Round 1 | Round 2 | Total |
|----------|---------|---------|-------|
| Typo | 0 | 0 | 0 |
| Grammar | 0 | 0 | 0 |
| Style | 2 | 2 | 4 |
| Clarity | 3 | 5 | 8 |
| Formatting | 0 | 0 | 0 |
| Technical | 3 | 3 | 6 |
| Precision | 2 | 0 | 2 |
| Consistency | 0 | 4 | 4 |
| Completeness | 1 | 0 | 1 |
| Methodology Note | 1 | 0 | 1 |
| **Total** | **12** | **14** | **26** |

---

## Recommended Priority for Human Review

1. **Fix First (pre-submission):** Technical issues — verify SFT row values, figure file existence, ground_truth.yaml EC1 correction
2. **Fix Second:** Consistency issues — ensure revised ρ values are reflected consistently in prose and all cross-references
3. **Consider:** Clarity improvements — expand parenthetical qualifications for 2.8B, ρ = 0.737 H2 explanation, H3 PPO ratio note
4. **Optional:** Style refinements — conclusion register, abstract repetition

*Note: These issues do not block paper acceptance but improve overall quality and preempt reviewer questions.*
