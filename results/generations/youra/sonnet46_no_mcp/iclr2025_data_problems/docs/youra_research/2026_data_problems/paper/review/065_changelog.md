# Phase 6.5 Adversarial Review Changelog

## Round 1 Changes (2026-05-04)

### M1: Domain Ratio Correction
- **Locations changed:** Abstract (Contribution 3 sentence), Section 1 Introduction Contribution 3 bullet, Section 5.3 finding header, Section 5.3 body text, Section 5.3 observed ratio note (new), Section 7 Conclusion item (3)
- **Before:** "2-3× higher contamination than commonsense benchmarks" / "2–3× higher"
- **After:** "approximately 1.9× higher contamination rates than commonsense benchmarks" / "nearly 2× higher"
- **Rationale:** Actual ratio from Table 3 is 6.64% / 3.57% = 1.860×, which falls below the stated floor of 2×. The "2-3×" claim was a factual overclaim. Added explicit ratio note in Section 5.3: "The observed ratio for The Pile column is 6.64% / 3.57% = approximately 1.86× — nearly 2× higher for academic sub-tasks."

### M2: h-m2 Gate Failure Qualifier Added
- **Locations changed:** Abstract (end of abstract, new sentence added), Introduction Contribution 3 bullet (added "(exploratory)" label and parenthetical qualifier), Section 5.3 finding header (added "exploratory" qualifier), Section 6.2 L3 (added "should be treated as exploratory" sentence)
- **Before:** Abstract ended without any caveat on domain stratification. Contribution 3 presented as confirmed finding. Section 5.3 header stated "2-3× higher" without pre-registration failure note.
- **After:** Abstract now ends with: "— supported by an interaction test (H=22.08, p=0.0005) but not confirmed by a pre-registered directional test due to insufficient category granularity (n=2 commonsense sub-tasks)." Contribution 3 is now labeled "(exploratory)" and includes parenthetical explaining the Mann-Whitney failure and pending replication need. Section 5.3 finding header and body add "exploratory" qualifier.
- **Rationale:** Section 5.3 and Table 4 already disclosed the Mann-Whitney failure, but Abstract and Introduction presented domain stratification without caveat, creating an inconsistency. Abstract and Introduction now match the existing disclosure in Section 5.3.

### M3: Novelty Claim Differentiation
- **Locations changed:** Introduction Contribution 1 bullet (title changed, differentiation paragraph added inline), Section 2.4 Positioning (differentiation sentence added)
- **Before:** Contribution 1 titled "The Cross-Corpus Contamination Atlas: The first unified 59-sub-task × 3-corpus…". Section 2.4 described positioning without explicitly contrasting scope with WIMBD.
- **After:** Contribution 1 retitled "The Cross-Corpus Contamination Matrix: The first systematic 59-sub-task × 3-corpus…". Added explicit differentiation paragraph within Contribution 1: "While WIMBD [Elazar et al., 2023] provides contamination analysis for The Pile against individual datasets, and corpus documentation papers [Gao et al., 2020; Dodge et al., 2021; TogetherComputer, 2023] characterize individual corpus properties, no prior work has systematically mapped 13-gram contamination rates for 59 sub-tasks simultaneously across three major open training corpora in a unified matrix. Our work is the first to enable direct corpus-vs-corpus contamination comparison at sub-task granularity." Section 2.4 also reinforced with explicit scope contrast sentence.
- **Rationale:** "First unified cross-corpus contamination atlas" is a strong novelty claim that requires explicit differentiation from WIMBD and corpus documentation papers. The differentiation now appears at the point of claim.

### M4: Causal Language Softened
- **Locations changed:** Abstract (central finding sentence), Introduction paragraph 4 (key insight sentence), Introduction Contribution 2 bullet, Section 3 opening paragraph, Section 6.1 (C4 paragraph, new sentence added), Section 7 Conclusion item (2), Section 2.4 Positioning
- **Before:** "corpus source composition — not scale — determines contamination profiles" (multiple occurrences); "not scale" as absolute negation.
- **After:** "corpus source composition — more than merely corpus scale — is associated with contamination profile differences"; "not merely corpus scale"; "is associated with" replaces "determines". In Section 6.1, added: "We note that C4's lower contamination may reflect both its quality filtering methodology and its distinct source composition relative to The Pile — formal decomposition of these effects would require a larger factorial study of corpus construction choices."
- **Rationale:** With only 3 corpora and confounded variables (quality filtering, deduplication, shared ancestry), causal language ("determines", "not scale") is unsupported. The softer association language accurately reflects what the observational study can establish.

### M5: C4 38% Uncertainty Caveat Added

- **Locations changed:** Abstract (38% claim), Section 5.2 RQ2 body (38% claim), Section 3.3 Corpus Indexing (scaling factor paragraph extended), Section 6.1 Discussion (38% reference), Section 7 Conclusion item (2), Introduction Contribution 2 bullet
- **Before:** "C4's quality filtering reduces mean contamination by 38% relative to The Pile" with no uncertainty qualification.
- **After:** "reduces mean contamination by 38% relative to The Pile (assuming literature-calibrated scaling factors; directional ordering robust to ρ>0.995 sensitivity analysis)". In Section 3.3, added: "The scaling factor uncertainty (estimated ±10–20% from literature) propagates to an approximate ±4–8 percentage point uncertainty in absolute contamination figures such as the 38% reduction estimate; the directional ordering (C4 < Pile) remains robust to all plausible scaling values (ρ>0.995 sensitivity analysis)." Section 6.2 L2 expanded with: "The scaling factor uncertainty propagates to an approximate ±4–8 percentage point uncertainty in the absolute 38% reduction figure; the directional ordering (C4 < Pile) remains robust to all plausible scaling values."
- **Rationale:** The 38% figure rests on 10% samples scaled by literature-derived factors. Reporting without uncertainty is misleading; the caveat clarifies what is robust (directional ordering) vs. what carries uncertainty (absolute figure).

---

## Round 2 Changes (2026-05-04)

### MAJOR-1: Cross-Source Rate Asymmetry Disclosure Added

- **Locations changed:** Section 6.2 — new limitation L2b added between L2 and L3
- **Before:** L2 disclosed scaling factor uncertainty (±4–8 pp) but did not explicitly flag that the 38% reduction compares a WIMBD-published Pile rate against a pipeline-computed C4 rate (cross-source comparison).
- **After:** Added L2b: "We note that the 38% contamination reduction comparing C4 to The Pile involves a cross-source comparison: The Pile rate is a published WIMBD baseline while C4's rate is independently computed from a 10% sample. Although our pipeline validates against WIMBD (Spearman ρ=0.721), the systematic comparison between a published rate and a sample-computed rate introduces additional uncertainty beyond the sampling variance alone. The directional finding (C4 < Pile) is robust across all plausible scaling values."
- **Rationale:** The cross-source nature of the 38% comparison is a distinct methodological limitation beyond scaling uncertainty. A reader must know that the Pile baseline comes from a peer-reviewed external source (WIMBD) rather than from this pipeline's own measurement, as the two sources may differ in MinHash parameters, document coverage, and other methodology details. Explicit disclosure is required for methodological integrity.

### MAJOR-2: KW Interaction H=22.08 Disclosure Consistency Fixed

- **Locations changed:** Section 5.3 finding header/body (parenthetical added after H=22.08 citation); Abstract (parenthetical added after H=22.08 citation); Section 6.2 L3 (updated to note KW test shares n=2 limitation)
- **Before:** Section 5.3 cited "H=22.08, p=0.0005" without noting that the 6-group KW test is equally affected by the n=57 vs n=2 group-size imbalance. The n=2 caveat was applied to Mann-Whitney but not to KW interaction, creating an inconsistency in disclosure.
- **After:** Added parenthetical after H=22.08 in Section 5.3: "(noting that the 6-group KW test is also affected by the severe group-size imbalance — n=57 academic vs. n=2 commonsense per corpus — meaning the significant H statistic primarily reflects variance within the large academic group rather than a confirmed between-domain contrast)". Same parenthetical added in Abstract. L3 updated to explicitly note: "The KW interaction test (H=22.08) shares the same n=2 group-size limitation — with 6 groups where 3 have n=2 and 3 have n=57, the significant H statistic is predominantly driven by variance within the large academic groups across corpora rather than a clean domain × corpus interaction."
- **Rationale:** The KW interaction test with n=57 academic vs n=2 commonsense groups cannot cleanly separate the domain effect from academic-side variance. Applying the n=2 caveat to Mann-Whitney but not to KW creates an inconsistency that overstates the strength of KW as domain stratification evidence. Consistent disclosure is required for research integrity.

---

## Final Summary

Total revisions: R1 (5 MAJOR) + R2 (2 MAJOR) = 7 MAJOR fixes applied
Human review notes: 10 items (6 from R1 + 4 from R2)
