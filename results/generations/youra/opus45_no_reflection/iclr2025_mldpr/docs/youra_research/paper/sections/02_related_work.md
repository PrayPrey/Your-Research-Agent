# Related Work

Our work connects three research areas: benchmark concentration studies, foundation model impact analysis, and meta-science of machine learning. We position our contribution against each.

## Benchmark Concentration Studies

Koch et al. (2021) provide the most directly relevant prior work, documenting benchmark concentration patterns from 2015-2020 using Papers With Code and Semantic Scholar data. They found Gini coefficients of 0.6-0.7, demonstrating that research concentrates on fewer datasets over time, with elite institutions (Stanford, MIT, Google) dominating influential dataset creation. Their work established that benchmark concentration exists and is increasing.

However, Koch et al.'s analysis ends at 2020—precisely when foundation models began transforming the landscape. Their methodology uses static snapshots rather than time-series analysis, precluding detection of structural breaks. Our work extends their temporal coverage through 2024 and introduces change-point detection to identify *when* concentration dynamics shifted, not just *that* they exist.

Raji et al. (2021) critiqued benchmark practices from a construct validity perspective, arguing that benchmarks framed as measuring "general" AI progress often lack construct validity. Their work explains *why* benchmark overuse is problematic but does not quantify concentration dynamics. Similarly, Bechler-Speicher et al. (2025) argued for benchmark proliferation in graph ML as a response to concentration, but provided qualitative arguments rather than quantitative hypothesis testing.

## Foundation Model Impact Analysis

Extensive work documents foundation model capabilities and limitations. Brown et al. (2020) demonstrated GPT-3's few-shot learning; Dosovitskiy et al. (2020) showed Vision Transformers matching CNNs on image classification; Devlin et al. (2019) established BERT's transfer learning paradigm. These papers analyze what foundation models *can do*.

Our work addresses a different question: how did foundation models change research *evaluation practices*? We treat foundation model emergence as an independent variable affecting the dependent variable of benchmark concentration dynamics. This meta-scientific perspective complements capability analysis by documenting second-order effects on the research ecosystem.

## Meta-Science of Machine Learning

A growing body of work examines ML research practices scientifically. Vincent and Hecht (2021) surveyed dataset development practices, documenting incentive structures that favor benchmark reuse over creation. Birhane and Prabhu (2021) examined quality concerns in large-scale image datasets. Boyd (2021) proposed datasheets for datasets as an intervention to improve documentation.

This meta-scientific work is primarily qualitative or intervention-focused. We contribute a quantitative hypothesis-testing approach: defining testable predictions, specifying falsification criteria, and executing statistical tests. Our methodology—applying PELT change-point detection to bibliometric time series—provides a template for rigorous meta-science.

## Our Position

We build on Koch et al.'s foundation while addressing three limitations: (1) temporal coverage through 2024, (2) dynamic rather than static analysis via change-point detection, and (3) mechanism verification beyond descriptive statistics. Unlike prior meta-scientific work, we test falsifiable hypotheses with pre-specified success criteria, enabling definitive claims about what foundation models did and did not cause in the benchmark ecosystem.
