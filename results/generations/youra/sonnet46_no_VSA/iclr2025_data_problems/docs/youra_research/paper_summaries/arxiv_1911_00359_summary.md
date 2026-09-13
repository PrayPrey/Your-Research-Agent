---
source_paper: "arxiv_1911_00359.md"
generated_at: "2026-07-30T06:10:38.290613"
model: "openai/gpt-5.2"
summary_chars: 12964
---

# CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data

## Key Metadata
- **Authors:** Guillaume Wenzek et al.
- **Year:** 2019 (arXiv:1911.00359)
- **Venue:** arXiv
- **Core Contribution:** A scalable, multilingual pipeline (CCNet) that deduplicates, language-identifies, and optionally filters Common Crawl documents using Wikipedia-trained LM perplexity to produce massive, higher-quality monolingual corpora.

## Section Summaries

### Abstract
Pre-training text representations have led to signiﬁcant improvements in many areas of natural language processing. The quality of these
models beneﬁts greatly from the size of the pretraining corpora as long as its quality is preserved. In this paper, we describe an automatic
pipeline to extract massive high-quality monolingual datasets from Common Crawl for a variety of languages. Our pipeline follows
the data processing introduced in fastText (Mikolov et al., 2017; Grave et al., 2018), that deduplicates documents and identiﬁes their
language. We augment this pipeline with a ﬁltering step to select documents that are close to high quality corpora like Wikipedia.
Keywords: Common Crawl, web data

### Introduction & Motivation
Modern pretraining (Transformers, BERT) benefits strongly from scaling text corpora, but gains depend on maintaining data quality rather than raw size alone. Existing “high-quality” corpora (e.g., Wikipedia concatenations) are hard to replicate for low-resource languages due to limited curated text. Common Crawl offers massive multilingual web text but is noisy, duplicated, and language-mixed. The paper addresses this gap with an automatic, scalable pipeline that (i) preserves document structure (for paragraph/document-level LMs like BERT) and (ii) optionally filters documents by similarity to a high-quality in-domain corpus (Wikipedia) using LM perplexity.

### Methodology
CCNet processes one Common Crawl monthly snapshot (WET text files) into monolingual JSON corpora with optional quality strata. **(1) Sharding & parsing:** each snapshot (e.g., 20–30TB uncompressed; ~3B pages) is regrouped into **5GB shards** (Feb 2019: **1600 shards**), each shard stored as JSON with one entry per web page/document while preserving document boundaries and paragraph structure. **(2) Paragraph deduplication (cross-document):** paragraphs are normalized by lowercasing, replacing digits with a placeholder (“0”), and removing Unicode punctuation and accent marks. For each paragraph, CCNet computes a key = first **64 bits of SHA-1** over normalized text; hashes are saved to binary files. Deduplication then removes repeated paragraphs by comparing a shard against hashes from **N shards** (a tunable recall–RAM trade-off; authors use **N=50** shards ≈ **3%** of the corpus as default). **(3) Language ID (LID):** after dedup, documents are classified with the **fastText** LID model (character n-grams + hierarchical softmax; **176 languages**). The predicted language is kept only if the confidence score **> 0.5**; otherwise the document is discarded. **(4) LM-based quality scoring (optional):** to rank/filter documents toward a target domain (Wikipedia), for each language they train a **SentencePiece** tokenizer and a **5-gram Kneser–Ney LM** (KenLM). Each document/paragraph is tokenized and scored by perplexity:
\[
\mathrm{PPL}(w_{1:N})=\exp\left(-\frac{1}{N}\sum_{i=1}^N \log p(w_i \mid w_{i-4:i-1})\right).
\]
Languages are split into **three equal-sized terciles** (head/middle/tail) by PPL (language-specific thresholds). **(5) Output & reproducibility tools:** documents are regrouped by language (and by tercile where available) into gzip-concatenable chunks; an auxiliary tool can reproduce outputs from a list of URLs without rerunning the full pipeline. Reported end-to-end cost: ~**9 hours** per snapshot on **5000 CPU cores** (hash pass + processing pass).

### Experiments & Results
**Data processed:** Feb. 2019 Common Crawl snapshot (**24TB** text; ~**3B** pages; **1600×5GB** shards). After preprocessing, output is **3.2TB compressed**, **174 languages**, with LM filtering available for **48 languages** (Wikipedia-trained SentencePiece + KenLM models released). **Scale highlights (post-filtering / “head”+overall as described):** English: **706M docs**, **532B tokens**; Russian: **167M docs**, **101B tokens**; Chinese: **92B tokens**. They report **11 languages >10B tokens**, **27 languages >1B tokens**; **12 languages >10M docs**, **29 languages >1M docs**. Low-resource examples: Afrikaans **160MB**, Gujarati **190MB**, Khmer **154MB**, Burmese **440MB**, exceeding the corresponding Wikipedia sizes (e.g., Gujarati Wikipedia **88MB**).

**Ablations (pipeline design):**
- **Order of operations:** doing **Dedup → LID** (instead of **LID → Dedup**) increases retained documents especially for low-resource languages because dedup removes English boilerplate that otherwise causes misclassification or low-confidence discards.
- **Dedup scope vs remaining text:** within one shard, remaining characters drop from **42%** (dedup within 1 shard) to **28%** (dedup across 100 shards). Loading hashes for **50 shards** corresponds to **1.5B unique hashes** (~**13.5GB** on disk) and fits in ~**40GB RAM** with a memory-efficient hash set; authors choose **50 shards** as a practical trade-off.

**Quality validation via representation learning:**
1) **fastText embeddings** (300-dim) trained on English/Polish head/mid/tail (by PPL) and evaluated on analogy benchmarks show monotonic quality improvements toward head:

| Language | Split | Total | Sem | Syn |
|---|---:|---:|---:|---:|
| en | head | 77.9 | 81.2 | 75.3 |
| en | mid. | 74.2 | 79.0 | 70.4 |
| en | tail | 62.0 | 68.1 | 57.3 |
| pl | head | 65.3 | 66.5 | 64.1 |
| pl | mid. | 62.8 | 62.7 | 63.0 |
| pl | tail | 59.9 | 59.8 | 60.1 |

2) **BERT-BASE pretraining** (no NSP) on **Wikipedia vs CCNet head** for {en, ru, zh, ur}; early-stopped after **2 days** on **16× Volta32 GPUs** with the same number of steps. Evaluated on **XNLI dev accuracy** (training data in each language): CCNet improves **+3.3 avg points** and enables Urdu gains where Wikipedia is too small.

| Pretrain data | en | ru | zh | ur | Avg (∆) |
|---|---:|---:|---:|---:|---:|
| Wikipedia | 82.8 | 73.3 | 77.0 | 57.3 | 72.6 |
| CCNet | 85.0 | 76.4 | 77.9 | 64.3 | 75.9 |

**Compute profiling (one shard):** hashing pass ~**600 docs/s/core**; second pass uses ~17 processes; workers ~**40 docs/s**; time share: dedup **40%**, LID **12.5%**, SentencePiece **33%**, LM scoring **13%**.

### Discussion & Conclusion
CCNet demonstrates that large-scale web crawl text can be transformed into massive, language-separated corpora with improved quality using document-level deduplication plus optional Wikipedia-targeted perplexity ranking. The authors emphasize that LM tail data may still be useful (domain jargon, informal speech) and therefore avoid hard removal by default, instead providing terciles. Limitations include dependence on Wikipedia size for LM calibration (perplexity distribution variance) and imperfect LID recall for low-resource languages, suggesting future work on better multilingual LID and more robust domain-quality models.

## Key Contributions
- **A production-scale, multilingual Common Crawl extraction pipeline that preserves document structure and aggressively removes boilerplate duplication (paragraph-level) to improve downstream usability.**  
  CCNet operationalizes a two-pass design tailored to the realities of Common Crawl snapshots (tens of TB, billions of pages). The core engineering contribution is *paragraph-level deduplication across documents at snapshot scale* while retaining document boundaries necessary for training paragraph/document models (e.g., BERT), unlike some prior pipelines focused on sentence-level or bag-of-text outputs. The method normalizes paragraphs (case-folding; digit canonicalization; punctuation/diacritic removal), computes compact identifiers (first 64 bits of SHA‑1), and uses binary hash stores to enable distributed comparisons. The paper characterizes the key system trade-off: widening dedup scope increases quality/uniqueness but drives RAM and I/O; empirically, comparing against 50 shards (≈3% of the corpus) is a workable point (1.5B unique hashes; ~13.5GB on disk; ~40GB RAM with an efficient hash set). They also document end-to-end throughput and parallelization boundaries: the pipeline is “massively parallelizable” but necessarily staged because dedup requires global-ish hash access. Concretely, they report ~9 hours per snapshot on 5000 CPU cores, with a breakdown showing dedup as the largest time consumer (40%) and tokenization/LM scoring as substantial additional costs. This contribution is not just conceptual; it is a reproducible recipe (5GB shard abstraction; gzip-concatenable outputs; URL-based reconstruction tool) that turns CC from a raw crawl into practical monolingual corpora at scale (Feb 2019: 174 languages; 3.2TB compressed).

- **A simple, language-agnostic “quality scoring” mechanism for web documents based on in-domain LM perplexity (Wikipedia), yielding controllable quality–diversity trade-offs.**  
  The algorithmic novelty relative to fastText/CommonCrawl preprocessing baselines is the optional LM-based filtering step that ranks documents by closeness to a trusted corpus. For each language, CCNet trains (i) a SentencePiece tokenizer and (ii) an efficient 5‑gram Kneser–Ney LM (KenLM) on the target domain (Wikipedia), then scores each document/paragraph by perplexity:
  \[
  \mathrm{PPL}(w_{1:N})=\exp\left(-\frac{1}{N}\sum_{i=1}^N \log p(w_i \mid w_{i-4:i-1})\right).
  \]
  Low perplexity indicates lexical/structural similarity to Wikipedia-style text; high perplexity tends to capture keyword lists, spam, or very non-Wikipedia domains. Importantly, the authors do **not** impose a single global threshold; instead, they split each language into **equal-sized terciles** (head/middle/tail) using language-specific cut points, motivated by the observation that perplexity distributions vary widely, partly due to uneven Wikipedia sizes (e.g., English LM trained on 534M text vs Gujarati on 12M). This design yields a *tunable* dataset: “head” supports high-quality pretraining; “tail” retains out-of-domain content (forums, informal text, jargon) that may benefit robustness or domain adaptation. This is a pragmatic alternative to brittle rule-based filtering (often English-only) and provides a reusable interface: users can swap the target corpus, retrain tokenizer/LM, and recompute terciles. The release of pretrained models for 48 languages makes this immediately actionable.

- **Empirical evidence that CCNet’s dedup-first design and LM-based ranking measurably improve representation learning, especially for low-resource languages.**  
  Beyond building the pipeline, the paper validates that its “quality controls” correlate with downstream embedding/LM performance. First, they show that *ordering matters*: **Dedup → LID** improves language identification outcomes because boilerplate English text is removed before classification; low-resource languages see the largest relative document gains (their Figure 3). Second, they quantify quality improvements from LM ranking via **fastText** analogy accuracy: for both English and Polish, moving from tail→mid→head yields consistent gains (e.g., English total 62.0→74.2→77.9; semantic 68.1→79.0→81.2), supporting perplexity as a useful proxy for “pretraining-relevant” cleanliness/well-formedness. Third, they demonstrate *task-level benefits* with **BERT-BASE** pretraining (no NSP, matched steps, 2-day budget on 16×Volta32 GPUs) evaluated on **XNLI dev**: CCNet-trained models outperform Wikipedia-trained counterparts for en/ru/zh/ur, with a **+3.3 average accuracy point** improvement (72.6→75.9). The Urdu case is particularly diagnostic: Wikipedia-only pretraining is effectively too small (57.3, comparable to random initialization per authors), while CCNet raises accuracy to **64.3** (+7.0), showing that web-scale extraction + filtering can unlock monolingual pretraining where curated corpora fail. Finally, they provide dataset-scale statistics (e.g., English 706M docs, 532B tokens; 174 languages total) that contextualize the magnitude of the contribution and make clear why these improvements matter for multilingual and low-resource research.

## Potential Relevance
CCNet is directly useful if your hypothesis depends on scaling monolingual pretraining data while controlling for noise: it offers a concrete dedup+LID+perplexity-ranking recipe, plus ablation-backed guidance (dedup before LID; dedup scope vs RAM). The head/middle/tail stratification can support experiments on how domain “cleanliness” vs diversity affects downstream generalization, and the reported BERT/XNLI gains (notably Urdu +7.0) provide strong baselines for web-data filtering methods in low-resource settings.