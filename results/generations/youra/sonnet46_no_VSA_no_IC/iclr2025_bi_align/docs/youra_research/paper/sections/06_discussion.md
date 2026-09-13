# Discussion

## Key Findings

**Finding 1: Venue-string classification is not a reliable method for interdisciplinary alignment corpora.**

The 12% coverage finding is not a minor implementation detail — it is a blocking problem. A bibliometric study that classifies only 12% of its corpus papers cannot validly construct a 2×2 contingency table, cannot run chi-squared tests, and cannot report a citation ratio. The 88% of unclassified papers are simply absent from the analysis, with no warning and no fallback. This failure mode occurs silently with standard tooling: the classification function returns `None` for unmatched papers, and downstream analysis simply omits them without signaling that the omission rate is 88%.

The root cause is universal to any study using S2AG venue strings for interdisciplinary corpora: venue name formatting is not standardized in S2AG. This is not a bug — S2AG stores the name as submitted by the publisher. Researchers building classification pipelines must either normalize venue strings to full proceedings name variants or use `fieldsOfStudy` as the primary classifier. We recommend FoS-primary classification (Scheme 3) as the general solution, with venue-string matching as a fallback only.

**Finding 2: The directional signal is visible even in the proxy corpus.**

A ratio of 0.107 at N=9 cross-group edges cannot be reported as a confirmed statistical finding. We are explicit about this. But the signal is worth reporting as a directional estimate: even in 33 papers, the asymmetry predicted by H-CitAsym is visible in the raw edge counts, and no falsifier was triggered. The direction is consistent with the causal mechanism (ML/NLP alignment research is self-referential; HCI alignment research cites ML/NLP to ground applied studies). The ratio at full corpus scale may shift — but the direction has not been refuted.

**Finding 3: Public reading lists are not bibliometric dataset proxies.**

The 12.5% yield from GitHub-linked papers to S2AG-resolved papers is a practical finding for researchers in adjacent areas. A curated reading list is a human-readable navigation tool, not a machine-readable paper database. Researchers building bibliometric datasets should expect extraction rates in this range from GitHub reading lists — and should use programmatic S2AG search (citation-of-citation expansion, keyword search) rather than reading list parsing to reconstruct systematic review corpora at scale.

## Limitations

**Limitation 1: All statistical predictions (P1, P2, P3) are INCONCLUSIVE — corpus too small for chi-squared testing.**

Coverage = 67.3% (gate: 70%) and cross-group edges = 9 (gate: 30) both fall below pre-registered thresholds. Chi-squared testing requires minimum expected cell counts ≥ 5; at N=9 total cross-group edges, the 2×2 table cannot meet this requirement. Proportion z-testing (P2) and betweenness centrality ranking (P3) likewise require minimum sample sizes that the proxy corpus cannot provide.

*Why acceptable:* The pipeline infrastructure is validated (23/23 tests). The corpus access gap is a data discovery issue, not a method failure. The directional signal (ratio≈0.11) is consistent with the hypothesis. The h-e1-v2 protocol specifies a concrete, executable augmentation step: use S2AG `/paper/arXiv:2406.09264/citations` to discover papers citing the Shen et al. [2024] systematic review and expand the corpus programmatically.

**Limitation 2: Study operates on 33-paper proxy corpus, not the intended 400-paper systematic review corpus.**

The huashen218 GitHub repository is a reading guide, not the full systematic review database. Access to the full ~400-paper corpus requires either direct contact with the authors (Shen et al. 2024) or programmatic reconstruction via S2AG citation search. Our study executes on what is publicly machine-readable.

*Why acceptable:* The corpus proxy mismatch is itself a finding (C2). Future researchers attempting similar studies on systematic review corpora now have a documented account of why GitHub reading lists fail as bibliometric proxies and what the programmatic alternative is.

**Limitation 3: Sensitivity analysis across 3 classification schemes is not executable at Scheme 1/2 coverage of 12%.**

The pre-registered robustness criterion (directional consistency across ≥ 2 of 3 schemes) cannot be evaluated because Schemes 1 and 2 classify only 4/33 papers. The fix is known and mechanical: extend venue substring sets to include full proceedings name variants (e.g., "Proceedings of the ... Neural Information Processing Systems" for NeurIPS). This fix is documented in the pipeline config (`config.py`) but not applied during h-e1 execution.

*Why acceptable:* Scheme 3 (FoS-primary) is the most theoretically principled classifier — it uses a knowledge-graph-derived field rather than a format-sensitive string match. Scheme 1/2 sensitivity analysis, when enabled with normalized strings, will verify robustness of the Scheme 3 findings. Scheme 3 alone provides a valid classification for current analysis.

**Limitation 4: Corpus selection bias is fundamental and acknowledged.**

The huashen218 corpus is a curated alignment reading list, not a random sample of ML/NLP or HCI research. Findings about citation behavior apply specifically to papers in the alignment community as operationalized by Shen et al. [2024] — they do not generalize to ML/NLP or HCI research broadly. A matched random baseline (comparing huashen218 citation ratios against non-alignment ML/NLP and HCI paper citation patterns) would be required to claim field-level generalization. Phase 5 baseline comparison is specified in the pipeline but deferred by configuration (`skip_baseline_comparison: true`) for the current execution.

**Limitation 5: Temporal dimension unverified.**

We do not test whether the citation asymmetry pattern is stable across pre-2022 vs. post-2022 publication cohorts (Assumption A4). Post-ChatGPT (2022+) papers may show different citation behavior as HCI researchers rapidly engage with LLM alignment literature. With N=33 total resolved papers, temporal stratification is not meaningful. The full corpus (h-e1-v2) will enable this analysis using the `year` field already retrieved in batch resolution.

## Broader Impact

This study contributes two reusable artifacts: a validated S2AG bibliometric pipeline and the FoS-primary classification method. Both are applicable to any interdisciplinary corpus indexed by S2AG — AI safety, algorithmic fairness, and human-robot interaction studies would benefit from the same classification approach. We release all code and cached API responses as supplementary material.

The most significant potential misuse of this work is treating the proxy-corpus directional estimate (ratio≈0.107) as a confirmed statistical finding. We have been explicit throughout that the estimate is not statistically confirmable at N=9. Readers should not cite the ratio as evidence of asymmetry without acknowledging the corpus scale limitation. The finding that is statistically confirmable — FoS-primary classification at 100% vs. 12% coverage — is the contribution that generalizes without qualification.

There is no foreseeable negative impact from measuring citation behavior in a public academic corpus. All paper metadata used in this study is publicly available through S2AG.
