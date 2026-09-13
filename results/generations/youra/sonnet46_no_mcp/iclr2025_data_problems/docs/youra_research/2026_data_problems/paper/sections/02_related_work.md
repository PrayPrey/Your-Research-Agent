# 2. Related Work

## 2.1 N-gram Contamination Measurement

The systematic study of training data contamination in language models began with GPT-3 [CITE:brown2020gpt3], which reported n-gram overlap between test sets and training data and applied decontamination filters. However, GPT-3's analysis was limited to its own (closed) training corpus and did not provide a structured, per-sub-task breakdown.

The most directly relevant prior work is WIMBD (What's In My Big Data?) [CITE:elazar2023wimbd], which provides open-source tooling for 13-gram containment analysis on The Pile v1. WIMBD demonstrates that contamination rates vary significantly across MMLU sub-tasks within The Pile and establishes 13-gram containment as the standard methodology. Our work builds directly on WIMBD: we adopt its 13-gram methodology, validate our pipeline against its published rates (Spearman ρ=0.721), and extend its single-corpus analysis to a three-corpus comparison for the first time. WIMBD's key limitation for our purposes is scope — it covers The Pile only, leaving C4 and RedPajama uncharacterized.

The GPT-4 Technical Report [CITE:openai2023gpt4] reports contamination analysis using Jaccard similarity (rather than 13-gram containment) for select benchmarks against GPT-4's training data. This work confirms that contamination is measurable and worth reporting, but uses a closed corpus, a different metric, and does not provide systematic per-sub-task breakdowns across multiple open corpora. The relationship between 13-gram containment and Jaccard similarity rankings remains an open question (our h-m3 hypothesis, not yet executed).

Riddell et al. [CITE:riddell2024contamination] apply n-gram contamination analysis to code generation benchmarks, demonstrating the methodology's generality. Benchmarks as Microscopes [CITE:burnell2023benchmarks] calls for contamination-aware evaluation practices and notes the absence of systematic cross-corpus contamination studies — a gap our work directly addresses.

## 2.2 Corpus Documentation and Curation

The three training corpora we analyze have each been documented in separate papers, but none provides a systematic comparison against the same benchmarks with the same methodology.

Gao et al. [CITE:gao2020pile] introduce The Pile v1, a diverse 825GB corpus assembled from 22 high-quality sub-sources including PubMed Central, ArXiv, FreeLaw, and Common Crawl. The deliberate inclusion of domain-aligned academic sources is the key feature that distinguishes The Pile from quality-filtered web corpora — and, as our results show, produces the highest benchmark contamination rates among the three corpora.

Dodge et al. [CITE:dodge2021c4] document C4 (Colossal Clean Crawled Corpus), derived from Common Crawl with aggressive quality filtering. Their paper documents that C4 contains less benchmark overlap than unfiltered web data, but does not provide systematic contamination rates against MMLU, HellaSwag, or BIG-Bench Hard. Our cross-corpus comparison provides this missing characterization and quantifies the contamination reduction effect of C4's filtering (38% lower mean than The Pile).

TogetherComputer [CITE:togethercomputer2023redpajama] introduce RedPajama-v1 as an open reproduction of LLaMA's training data, combining Common Crawl, C4, GitHub, Wikipedia, Books, ArXiv, and StackExchange. The corpus's Common Crawl component creates structural overlap with The Pile's web sources — a similarity our results confirm statistically (Dunn p=0.810 for Pile vs RedPajama contamination distributions).

## 2.3 Contamination and Performance Inflation

Magar and Schwartz [CITE:magar2022contamination] provide the theoretical framework connecting contamination to performance inflation: models memorize training examples and this memorization inflates benchmark scores. Their work motivates contamination measurement but does not provide an empirical cross-corpus contamination study. We provide the missing measurement that Magar and Schwartz's framework requires.

Several subsequent works have studied contamination effects empirically, focusing on specific model families or benchmarks [CITE:riddell2024contamination, CITE:burnell2023benchmarks]. None provides a systematic cross-corpus comparison across the three most widely-used open training corpora with consistent methodology and full sub-task granularity.

## 2.4 Benchmark Design and Sub-task Characterization

MMLU [CITE:hendrycks2021mmlu] was designed to cover diverse academic domains across 57 sub-tasks, but contamination rates were not characterized at release. BIG-Bench Hard [CITE:srivastava2023bigbench] similarly provides 27 challenging sub-tasks without systematic contamination profiles. HellaSwag [CITE:zellers2019hellaswag] focuses on commonsense completion, representing a different contamination risk profile from academic sub-tasks.

Our work complements benchmark design by providing the post-hoc contamination characterization that these benchmarks lack — revealing which sub-tasks carry the highest contamination risk across major training corpora.

## 2.5 Positioning

Our work occupies a distinct position relative to each line of prior work: we **extend** WIMBD's single-corpus analysis to three corpora; we **characterize** C4 and RedPajama contamination profiles that corpus documentation papers left unmeasured; we **provide** the empirical cross-corpus measurement that contamination-inflation theory requires; and we **reveal** corpus composition as the primary predictor of contamination profiles, a mechanistic finding not previously established. The unified 59-sub-task × 3-corpus contamination matrix is our primary artifact.
