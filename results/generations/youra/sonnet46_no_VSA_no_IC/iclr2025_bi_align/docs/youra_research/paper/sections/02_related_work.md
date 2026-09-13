# Related Work

Our work combines three research streams — alignment bibliography, cross-community citation analysis, and S2AG bibliometric infrastructure — none of which, taken alone, addresses the problem of measuring directed citation asymmetry within an interdisciplinary alignment corpus.

## The huashen218 Alignment Corpus

Shen et al. [2024] introduced the position that AI alignment research is bidirectional: ML/NLP alignment (aligning AI behavior with human values) and HCI alignment (adapting humans to AI systems) are distinct but mutually dependent. Their systematic review assembled the huashen218 corpus — 400+ papers from NeurIPS, ICML, ICLR, ACL, EMNLP, CHI, CSCW, IUI, and adjacent venues — as the operational definition of the bidirectional alignment community [arXiv:2406.09264]. The ICLR 2025 Workshop on Bidirectional Human-AI Alignment further validated this framing, identifying ML/NLP and HCI as the primary disciplinary clusters.

Critically, Shen et al. [2024] characterize the community through paper authorship and venue affiliation, not through citation structure. No prior work has constructed a directed citation graph within the huashen218 corpus or tested whether the claimed bidirectionality manifests in how papers from the two communities actually cite each other. Our work is the first to do so.

## Cross-Community Citation Asymmetry

The closest methodological precedent is Wahle et al. [2023], who analyzed cross-field citation influence in NLP at scale using S2AG bulk data [arXiv:2310.14870, EMNLP 2023]. Their analysis of 77,000 NLP papers found strong within-field citation preference and measurable cross-field asymmetry, validating the use of S2AG directed citation edges and 2×2 contingency tables for cross-community citation analysis. We adopt the same statistical framework (chi-squared test on directed citation proportions) but apply it to an interdisciplinary alignment-specific corpus rather than a single-field corpus.

Chen [2024] analyzed HCI community self-citation rates using the X-index metric across CHI, UIST, and CSCW papers from 2010–2020 [arXiv:2303.07539, CHI EA 2024]. They find HCI self-citation rates increasing over time — consistent with community siloing. Our finding that HCI alignment papers in the huashen218 proxy show HCI→HCI = 0 within-corpus citations is complementary but distinct: alignment-specific HCI papers appear to cite ML/NLP work exclusively as within-corpus outgoing references, suggesting that alignment HCI is citation-dependent on ML/NLP rather than self-referential within the alignment community. This is consistent with Chen [2024]'s broader HCI self-citation trend but distinct in the alignment-specific context.

Neither Wahle et al. [2023] nor Chen [2024] addresses the classification problem for interdisciplinary corpora spanning both ML/NLP and HCI communities. Both operate on single-community corpora where venue-string classification is unambiguous. Our work is the first to encounter and solve the cross-community classification failure mode.

## Bibliometric Classification Methods

Standard bibliometric classification relies on venue name matching: a paper published at "NeurIPS" or "ACL" is labeled ML/NLP; a paper at "CHI" or "CSCW" is labeled HCI. This approach is adequate for single-community corpora where venue names appear in abbreviated form. However, S2AG returns full proceedings names — "Proceedings of the 37th Annual Conference on Neural Information Processing Systems," "Proceedings of the 2023 ACM CHI Conference on Human Factors in Computing Systems" — making substring matching against abbreviated venue strings unreliable.

The S2AG API documentation [Wade et al. 2022] notes the `fieldsOfStudy` field as a tag-based disciplinary classifier derived from S2AG's knowledge graph, populated independently of venue name formatting. Prior bibliometric work using S2AG has employed this field for paper categorization [Wahle et al. 2023] but has not explicitly reported it as a solution to venue name format mismatch in interdisciplinary corpora. We formalize FoS-primary classification as a distinct scheme, report its 100% vs. 12% coverage advantage on the huashen218 corpus, and document the root cause (format mismatch, not corpus composition) to support replication.

## Positioning

Our contribution is additive rather than competitive. We take Shen et al. [2024]'s corpus as input, apply Wahle et al. [2023]'s statistical framework to it, and discover that FoS-primary classification is required to make this combination work. The methodological gap — robust classification for interdisciplinary alignment corpora — is the contribution we fill, alongside the first empirical citation asymmetry measurement in the huashen218 corpus.
