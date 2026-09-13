# Conclusion

We set out to measure whether ML/NLP and HCI alignment researchers cite each other symmetrically within the huashen218 bidirectional alignment corpus. We found that the measurement infrastructure was missing — and built it. We then discovered that the "corpus" available through the public GitHub reading list contains 49 extractable paper identifiers, not the ~400 papers in the full systematic review. In the 33 papers we could resolve, the asymmetry we hypothesized was already visible: a directed citation ratio of 0.107, with HCI alignment papers allocating 100% of their within-corpus outgoing citations to ML/NLP work. The full statistical test awaits a larger corpus. The pipeline to run it is validated and ready.

## Summary

This work addressed the absence of validated bibliometric infrastructure for directed citation analysis in interdisciplinary alignment corpora. Our key insight — that FoS-primary classification using S2AG's `fieldsOfStudy` tags achieves complete label coverage where venue-string classification fails — resolves the fundamental technical barrier that blocked the measurement.

We contribute three things. First, a validated S2AG bibliometric pipeline: every component from corpus ingestion to gate evaluation is implemented, tested (23/23 unit tests, 0.85 seconds), and cached for zero-API re-execution. Second, FoS-primary classification (Scheme 3): a method that achieves 100% paper coverage on the huashen218 corpus compared to 12% for venue-string approaches — a direct consequence of S2AG's venue field format. This classification method is general and applicable to any interdisciplinary corpus indexed by S2AG. Third, the first directional citation measurement within the huashen218 alignment corpus: ML/NLP→HCI proportion = 10.6%, HCI→ML/NLP proportion = 100%, ratio ≈ 0.107 in the 33-paper resolved set — directionally consistent with asymmetric epistemic dependency.

We also document a practical finding for researchers building bibliometric datasets: curated reading lists from systematic reviews yield extraction rates around 12% of the described corpus size. Programmatic S2AG citation-of-citation search — not GitHub markdown parsing — is the viable approach for reconstructing systematic review corpora at bibliometric scale.

## Future Directions

The most immediate extension is corpus augmentation (h-e1-v2): using the S2AG `/paper/arXiv:2406.09264/citations` endpoint to discover papers citing the Shen et al. [2024] systematic review, recovering 200+ papers and enabling full statistical testing of P1 (chi-squared asymmetry), P2 (within-group siloing), and P3 (bridge paper analysis). All pipeline components required for h-e1-v2 are already implemented and validated; corpus augmentation is the remaining step.

From the unverified assumptions, temporal analysis (pre-/post-2022 citation behavior) becomes tractable with a larger corpus. The `year` field is already retrieved in batch resolution — stratified chi-squared testing requires only the additional sample size. Post-ChatGPT (2022+) HCI alignment papers may show a different citation pattern as LLM alignment literature proliferates in HCI venues.

From scope extensions, venue string normalization for Schemes 1 and 2 (extending substring sets to cover full proceedings name variants) enables the pre-registered 3-scheme robustness analysis, which would provide the strongest evidence for or against H-CitAsym under the planned experimental design. This is a single configuration change.

The measurement of directed citation asymmetry within the alignment community is the first step toward a structural account of whether "bidirectional alignment" is operationally bidirectional. We hope this work provides both the methodology and the motivation for completing that measurement.
