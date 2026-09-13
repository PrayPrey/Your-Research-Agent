# Human Review Notes — R1 Minor Issues

**Paper:** The Coordinate System, Not the Symmetry Group
**Round:** R1
**Date:** 2026-08-05
**Source:** 065_review_r1.md Part 4

These are MINOR issues (typos, grammar, style, figure numbering) identified by the adversarial reviewer. They were NOT auto-fixed in 06_paper_r1.md. A human author should review each and decide.

---

| # | Location | Issue | Suggested Fix | Priority |
|---|----------|-------|---------------|----------|
| H1 | Section 2, Related Work, paragraph 3 | Citation "[Navon et al., 2026]" — 2026 is in the future relative to the paper date (2026-08-05, and Navon's work is ICML 2023). Likely a typo in a section file that did not propagate to the compiled paper (which correctly cites Navon 2023 in References). | Verify in source section file 02_related_work.md; fix to 2023 if present there | Medium |
| H2 | Section 2, Related Work, paragraph 3 | "ViT Model Zoo of [Zhu et al., 2025]" — the References list correctly cites Falk et al. 2025 (arXiv:2504.10231). "Zhu et al." appears only in section source file (02_related_work.md), not in the compiled 06_paper.md. If section files are the canonical source, this is an incorrect attribution. | Verify source section file; change to "Falk et al. 2025" if needed | Medium |
| H3 | Section 3.6, Methodology | Citation style inconsistency: body uses [Schurholt2024Towards] (no umlaut), while section source files may use [Schürholt et al., 2024] (with umlaut). Likely a compilation artifact. | Standardize to one citation key style across all section files and the compiled paper | Low |
| H4 | Sections 5.1 and 5.3 | Figure numbering inconsistency: Section 5.1 references "Figure 4 vs Figure 5 (tsne_equissl_seed0.png vs tsne_sane_seed0.png)" while Section 5.3 references "Figure 5 (fig3_tsne.png)" as a 4-panel t-SNE — different figures with the same number and different filenames. The Appendix also references both, creating a 3-way conflict. | Audit all figure references against actual generated figure files; assign consistent numbers and filenames throughout | High |
| H5 | References section | [Anonymous2025LayerNorm] is listed with "[UNVERIFIED]" inline — appropriate for a draft but must be resolved before final submission. Either verify the citation exists and remove the tag, or remove the citation entirely. | Verify arXiv:2510.08300 before submission; update or remove | High |
| H6 | Section 4, Datasets | "53 ViT-S/16 ImageNet checkpoint" — missing plural "checkpoints" | Fix to "checkpoints" | Low |

---

## Notes for Author

- **H4 (figure numbering)** is the highest-priority minor issue — a reviewer skimming Tables and then Figures will notice the inconsistency immediately. Recommend resolving before next submission round.
- **H5 (unverified citation)** is also time-sensitive — the body text has been hedged in R1, but the reference list entry needs resolution before submission.
- **H1 and H2** may only exist in section source files, not in 06_paper_r1.md (the compiled paper). Check section files before spending time fixing the compiled paper.

---

# R2 Minor Issues (from 065_review_r2.md)

**Round:** R2
**Date:** 2026-08-05
**Source:** 065_review_r2.md Section 7

| # | Location | Issue | Suggested Fix | Priority |
|---|----------|-------|---------------|----------|
| R2-H1 | Section 5.5, Table 4 | acc_latent = exactly 0.100 for ALL 501 pairs — this is exact random chance for CIFAR-10 (10 classes), not merely "near-random." The decoder outputs a constant distribution. Fixed in R2 to "exactly random chance (acc=0.100 = 1/10 for CIFAR-10, across all 501 pairs)." | Done in R2 | Medium |
| R2-H2 | References | [Anonymous2025LayerNorm] hedged with "citation unverified at time of submission" in 3 body locations and the References entry — confirmed sufficient by R2 review. No further action needed before R3. | No change needed | Low |
| R2-H3 | Appendix A / Section 5.4 | Appendix correctly shows mmd_comparison.png covers only SANE and EquiSSL (h-e1 data). After FATAL-001 fix in R2, Table 3 also has only SANE and EquiSSL — now consistent. Appendix description updated in R2 to note why EquiSSL-perm is absent. | Done in R2 | Low |
| R2-H4 | Related Work | "ICLR 2024 Oral" designation for Kofinas et al. — verify before final submission. ICLR 2024 Oral papers are publicly listed at iclr.cc. | Verify before submission | Medium |
| R2-H5 | Related Work | Ballerini citation arXiv:2502.09623 verified in Semantic Scholar; description matches. No change needed. | No change needed | Low |
| R2-H6 | Table 2 (h-m2) | SANE R²=0.072 in Table 2 is consistent with h-m1 value (0.07214606) — no discrepancy. | No change needed | Low |

## Notes for Author (R2 additions)

- **R2-H1** has been addressed automatically in R2 — "near-random chance" changed to "exactly random chance (acc=0.100 = 1/10)."
- **R2-H4** (Kofinas ICLR Oral) should be verified before camera-ready submission — the "Oral" designation changes acceptance prestige claims.
- The controlled EquiSSL ablation (training both models for 100 epochs) remains the most important scientific action item — without it, Table 2 cannot cleanly support the symmetry group claim.
