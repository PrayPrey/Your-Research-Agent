---
source_paper: "arxiv_2411_12372.md"
generated_at: "2026-07-30T06:13:32.858792"
model: "openai/gpt-5.2"
summary_chars: 10996
---

# RedPajama: an Open Dataset for Training Large Language Models

## Key Metadata
- **Authors:** Maurice Weber et al.
- **Year:** 2024
- **Venue:** NeurIPS 2024 (Track on Datasets and Benchmarks) + arXiv
- **Core Contribution:** Releases RedPajama-V1 (open reproduction of the LLaMA-1 pretraining mix) and RedPajama-V2 (a 100T+ token web-only corpus with per-document quality signals/metadata to enable transparent, customizable filtering for LLM pretraining).

## Section Summaries

### Abstract
Large language models are increasingly becoming a cornerstone technology in
artificial intelligence, the sciences, and society as a whole, yet the optimal strate-
gies for dataset composition and filtering remain largely elusive. Many of the
top-performing models lack transparency in their dataset curation and model devel-
opment processes, posing an obstacle to the development of fully open language
models. In this paper, we identify three core data-related challenges that must
be addressed to advance open-source language models. These include (1) trans-
parency in model development, including the data curation process, (2) access
to large quantities of high-quality data, and (3) availability of artifacts and meta-
data for dataset curation and analysis. To address these challenges, we release
RedPajama-V1, an open reproduction of the LLaMA training dataset. In addition,
we release RedPajama-V2, a massive web-only dataset consisting of raw, unfiltered
text data together with quality signals and metadata. Together, the RedPajama
datasets comprise over 100 trillion tokens spanning multiple domains and with
their quality signals facilitate the filtering of data, aiming to inspire the develop-
ment of numerous new datasets. To date, these datasets have already been used
in the training of strong language models used in production, such as Snowflake
Arctic, Salesforce’s XGen and AI2’s OLMo. To provide insight into the quality of
RedPajama, we present a series of analyses and ablation studies with decoder-only
language models with up to 1.6B parameters. Our findings demonstrate how quality
signals for web data can be effectively leveraged to curate high-quality subsets of
the dataset, underscoring the potential of RedPajama to advance the development
of transparent and high-performing language models at scale.

### Introduction & Motivation
Pretraining data composition and filtering are critical for LLM quality, but state-of-the-art models often provide little transparency about their training corpora, making results hard to reproduce and limiting open research on dataset design. Even open-weights models (e.g., LLaMA-1) do not release the data, and replicating dataset ablations is expensive. The paper targets three gaps: (1) transparent documentation and code for curation, (2) access to large quantities of high-quality data, and (3) release of artifacts/metadata that make filtering and analysis cheap. RedPajama addresses this via (i) an open “best-effort” reproduction of the LLaMA-1 data mix (V1) and (ii) a massive web-only raw corpus with many per-document “quality signals” (V2) so researchers can build their own filtered datasets rather than accepting a single prescribed filter recipe.

### Methodology
RedPajama contributes *datasets plus filtering/analysis infrastructure* rather than a new model architecture. **RedPajama‑V1** reproduces the 7-way LLaMA‑1 mixture using public sources: CommonCrawl processed by **CCNet** (perplexity-based buckets “head/middle/tail” from a 5‑gram Kneser–Ney LM trained on Wikipedia), C4 (`c4_en`), GitHub (license + heuristic file filtering), Wikipedia dumps, books (PG19; Books3 removed later for copyright), arXiv LaTeX (strip preamble/comments/bibliography; expand macros), and StackExchange (28 largest sites; HTML stripped; answers sorted by score). For CommonCrawl, they additionally train a **fastText** unigram Wikipedia-reference classifier: crawl **300K** pages from **38M** Wikipedia URLs, train on CCNet-cleaned references, and filter documents by score **≥ 0.25** to match LLaMA-scale.

**RedPajama‑V2** is web-only: **84 CommonCrawl snapshots (2014–Apr 2023)**, starting from `.wet` text and passing through CCNet with *all* perplexity buckets retained, keeping **English/French/German/Italian/Spanish**. Crucially, V2 is released largely *unfiltered*, paired with **46 quality signals** to enable downstream filtering: (i) natural-language heuristics (e.g., caps fraction, terminal punctuation, unique-word fraction), (ii) repetitiveness metrics (fractions of characters in frequent/duplicated word n‑grams), (iii) content filters (LDNOOBW blocklist counts; UT1 blocked domain flag), (iv) ML heuristics via fastText classifiers and DSIR importance weights, and (v) dedup metadata: MinHash signatures (fuzzy dedupe) and Bloom-filter exact-duplicate IDs (1% error). DSIR-style weights follow a log-likelihood ratio form, \(w(x)=\log \frac{p_{\text{target}}(x)}{p_{\text{source}}(x)}\), with target domains such as Wikipedia/books/OpenWebText for English.  

### Experiments & Results
The paper evaluates RedPajama mainly through (A) training RedPajama‑INCITE models on V1 to test faithfulness to LLaMA’s recipe and (B) controlled **dataset-filtering ablations** on V2 using small decoder-only Transformers.

**(A) RedPajama‑INCITE (V1-based) training.** Models were trained on the **Summit** supercomputer (Power9 + V100), requiring recompilation of modern PyTorch stacks and **fp16** training (no bf16) with **loss scaling**. Reported learning rates were lowered vs. LLaMA: **1.6×10⁻⁴ (3B)** and **1.2×10⁻⁴ (7B)**; LR decayed linearly after warmup. Parallelism: **3B** uses **256 nodes (1536 GPUs)**; **7B** uses **512 nodes (3072 GPUs)**; global batch size **4M tokens**. Pipeline parallelism: **6-way (3B)**, **12-way (7B)**; tensor parallelism **2-way**. Training tokens: **800B** (3B) and **1.001T** (7B). Evaluation uses **HELM classic** (average over 16 scenarios) and **EleutherAI LM Evaluation Harness** tasks. Findings: INCITE‑3B exceeds GPT‑Neo and Pythia‑2.8B by **+3–5 HELM points** and **+2–7 points** on harness subsets; INCITE‑7B trails **Falcon‑7B by 1.0** and **LLaMA‑7B by 4.1** on HELM classic, with gaps concentrated in *logprob-based* tasks.

**(B) V2 filtering ablations (web-only).** Data scale/statistics: V2 contains **113.3B documents** and an estimated **123.7T tokens** (Mistral BPE tokenizer; token counts estimated from an i.i.d. sample of **100M** docs). CCNet partitions: **head+middle 32.8B docs / 50.7T tokens**, **tail 80.5T tokens**; head+middle after dedupe: **14.5B docs / 20.8T tokens** (total across languages). Models: Llama‑2-style decoder-only with **468M** and **1.6B** params, **24 layers**, **16 heads**, **seq len 2048**, MLP expansion **4.0** (hidden size **1024** for 468M; **2048** for 1.6B). Training: **100B tokens** (468M) and **350B tokens** (1.6B) per dataset recipe; optimizer **AdamW**, weight decay **0.1**, max LR **5e‑3** (468M) / **5e‑4** (1.6B), cosine decay with **1% warmup**. Distributed training used **OLMo** + **FSDP** on up to **5 H100 nodes**. Evaluation: aggregated benchmark suite (ANLI, ARC-e/c, Winogrande, Hellaswag, LAMBADA, CoQA, MMLU, OpenBookQA, PIQA, PubMedQA, SciQ, SocialIQA, TruthfulQA) with metrics including **acc**, **acc_norm**, and **F1** (CoQA), summarized as average score, normalized average, and a rank-based aggregate; plus validation perplexity on **Paloma** and **Pile** val sets.

**Key quantitative results (from Tables 5–6; aggregated):**

| Setting / Dataset recipe | Model | Notable filtering components | Agg. BM-Eval Avg ↑ | Norm. Avg ↑ | Rank-score ↑ |
|---|---:|---|---:|---:|---:|
| RefinedWeb | 468M | curated web dataset baseline | 37.9 | 0.165 | 0.650 |
| **RPv2 (2023‑14) + fuzzy dedupe + full Gopher** | 468M | MinHash + “Gopher rules” | **37.6** | **0.160** | **0.700** |
| RPv2 (2023‑14) + fuzzy dedupe + Gopher-natlang | 468M | natlang-focused subset | 37.2 | 0.154 | 0.639 |
| RPv2 (2023‑14) + fuzzy dedupe + Gopher-rep | 468M | repetition-focused subset | 36.2 | 0.138 | 0.472 |
| **RefinedWeb** | 1.6B | curated web dataset baseline | **52.0** | 0.139 | — |
| RPv2 (full) + fuzzy dedupe + full Gopher | 1.6B | Gopher + dedupe | 50.0 | 0.106 | — |
| RPv2 (full) + fuzzy dedupe + Gopher-natlang | 1.6B | natlang-only | 47.9 | 0.089 | — |

Ablation takeaways reported by the authors: (1) **full Gopher + fuzzy deduplication** gives the strongest and most consistent V2-derived recipe, often matching or exceeding other open web corpora depending on aggregation; (2) **Gopher “natlang”** filters outperform **Gopher repetition-only** filters; (3) **fastText vs. DSIR** filtering yields *no significant difference* at this scale; (4) **C4 line-level filters** reduce perplexity but have *negligible* effect on aggregated benchmark performance.

### Discussion & Conclusion
RedPajama argues that open LLM progress is blocked not just by missing data access, but by missing *metadata and artifacts* that enable rapid, principled filtering studies. V1 enables best-effort reproduction of LLaMA-style mixtures but still shows performance gaps at 7B, plausibly due to fp16 constraints and/or unreported LLaMA data details. V2’s main limitation is that evaluations are at small model scales (≤1.6B) and the release does not yet include thorough benchmark decontamination or PII analyses; the authors position V2 as a foundation for future filtering and compositional research rather than a final “clean” dataset.

## Key Contributions
- **RedPajama‑V1:** Fully open, documented reproduction of the LLaMA‑1 pretraining mixture (≈ **1.2T tokens** total; e.g., CommonCrawl **878B**, C4 **175B**, GitHub **59B**, Books **26B**, ArXiv **28B**, Wikipedia **24B**, StackExchange **20B**).
- **RedPajama‑INCITE models + systems report:** Training details and lessons from building 3B/7B models on **Summit** (V100, fp16), including concrete parallelism/batch/LR choices and benchmark comparisons (HELM + LM harness).
- **RedPajama‑V2:** A **100T+ token**, multi-year, **web-only** corpus across **5 languages**, released raw with **46 per-document quality signals** (heuristics, ML-based scores, dedup metadata) enabling transparent, user-defined filtering; demonstrated via systematic ablations.

## Potential Relevance
For hypothesis development on “data quality vs. scale,” RedPajama‑V2 provides a uniquely large *raw* substrate plus *standardized quality signals* (C4/Gopher/RefinedWeb-style, DSIR, dedup) that can be recombined to test causal claims about filtering choices. The ablation findings suggest strong interactions between **deduplication + comprehensive rule-based filtering** and downstream benchmark robustness, which is useful for designing controlled experiments on dataset curation pipelines. V1 and the INCITE results also highlight how *compute/training precision constraints* (fp16 vs bf16) can confound conclusions about “dataset fidelity” when reproducing proprietary data recipes.