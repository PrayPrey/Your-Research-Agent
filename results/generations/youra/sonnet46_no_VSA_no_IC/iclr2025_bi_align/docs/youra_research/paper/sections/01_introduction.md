# Introduction

When we constructed the first directed citation graph of the huashen218 bidirectional alignment corpus, we discovered that the publicly available reading list contained 49 extractable paper identifiers — not the ~400 from the underlying systematic review. What we could measure, however, told a striking story: every HCI alignment paper in our resolved set cited ML/NLP work as its sole within-corpus outgoing reference, while ML/NLP alignment papers directed only 10.6% of their outgoing citations toward HCI. A directed citation ratio of 0.107. The infrastructure to detect this asymmetry is now validated. The full statistical test awaits a larger corpus.

The framing of "bidirectional AI alignment" — the idea that ML/NLP and HCI communities should mutually adapt to one another — rests on an implicit assumption: that these communities are intellectually coupled. Cross-community citation behavior is a structural indicator of epistemic integration. If alignment researchers from ML/NLP and HCI communities genuinely engage with each other's work, their citation networks should reflect symmetric knowledge flow. If citation is asymmetric — HCI researchers consistently citing ML/NLP but not vice versa — then bidirectionality may be more aspirational than structural.

This question is newly tractable. Shen et al. [2024] assembled the huashen218 corpus: a curated systematic bibliography of 400+ interdisciplinary alignment papers spanning NeurIPS, ICML, CHI, CSCW, and adjacent venues. The corpus operationalizes the "bidirectional alignment community" as a named set of papers. Measuring directed citation behavior *within* this corpus is the first empirical test of whether the community is citation-integrated.

The measurement, however, exposes a deeper problem. Standard bibliometric approaches — classifying papers by venue name substring matching — achieve only **12% label coverage** on this corpus. The reason is mundane but consequential: the Semantic Scholar Academic Graph (S2AG), the public API for directed citation data, returns full proceedings names ("Proceedings of the 36th Annual Conference on Neural Information Processing Systems") rather than abbreviated venue strings ("NeurIPS"). Substring matching silently fails on the long-form variants, leaving 88% of papers unclassified and the measurement impossible.

This failure points to the gap: there is no validated pipeline or classification method for constructing directed citation graphs within interdisciplinary alignment corpora. Venue-string approaches, the default in most bibliometric tools, are not suitable here. The classification infrastructure must be built before any citation asymmetry can be measured.

**Our key insight:** Switching the primary classifier from venue name strings to S2AG's `fieldsOfStudy` tags — which encode disciplinary assignment at the knowledge-graph level, independent of venue name formatting — achieves **100% paper coverage** on the same corpus, compared to 12% for venue strings. This is a three-line change with an eight-fold coverage improvement.

Building on this insight, we make the following contributions:

1. **A validated S2AG bibliometric pipeline** for within-corpus directed citation analysis: batch ID resolution via POST `/paper/batch`, FoS-primary classification (Scheme 3), within-corpus DiGraph construction using NetworkX, and gate-controlled evaluation. The pipeline passes 23/23 unit tests and is fully cached for zero-API re-execution.

2. **FoS-primary classification (Scheme 3)**: a method that uses S2AG `fieldsOfStudy[0]` as the primary venue-group classifier, achieving 100% label coverage on the huashen218 corpus vs. 12% for venue-string-only approaches. The method is domain-general and applicable to any interdisciplinary corpus indexed by S2AG.

3. **The first directional citation measurement within the huashen218 alignment corpus**: in the 33-paper resolved proxy, ML/NLP→HCI proportion = 10.6%, HCI→ML/NLP proportion = 100%, ratio ≈ 0.107 — directionally consistent with asymmetric epistemic dependency. No statistical falsifier was triggered; full statistical testing requires the augmented corpus (h-e1-v2).

4. **A methodological finding on corpus proxy construction**: the huashen218 GitHub reading list yields 49 extractable identifiers from ~130 linked papers — 12.5% of the target corpus. Public reading lists from systematic reviews are insufficient bibliometric dataset proxies; programmatic S2AG citation-of-citation search is the viable reconstruction approach.

We organize the paper as follows. Section 2 situates our work in the context of prior cross-community citation analysis and bibliometric infrastructure. Section 3 describes the pipeline design and the classification schemes. Section 4 presents experimental setup. Section 5 reports results. Section 6 discusses implications and limitations. Section 7 concludes.
