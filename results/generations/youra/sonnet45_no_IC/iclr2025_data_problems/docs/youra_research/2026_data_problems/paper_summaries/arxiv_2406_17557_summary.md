# The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale

## Key Metadata
- **Authors:** Guilherme Penedo et al. (Hugging Face)
- **Year:** 2024
- **Venue:** NeurIPS 2024 Track on Datasets and Benchmarks
- **Core Contribution:** FineWeb (15T tokens) and FineWeb-Edu (1.3T educational subset) datasets with comprehensive ablation studies of deduplication and filtering strategies for LLM pretraining.

## Section Summaries

### Abstract
FineWeb is a 15-trillion token dataset derived from 96 Common Crawl snapshots that produces better-performing LLMs than other open pretraining datasets. The paper carefully documents and ablates all design choices including deduplication and filtering strategies. FineWeb-Edu, a 1.3-trillion token collection of educational text filtered from FineWeb, shows dramatically better performance on knowledge- and reasoning-intensive benchmarks like MMLU and ARC. Released with full data curation codebase (datatrove) and all ablation models under permissive ODC-By License.

### Introduction & Motivation
LLM performance depends heavily on pretraining dataset quality and size, but state-of-the-art open models (Llama 3, Mixtral) don't release pretraining data. Curation strategies are trade secrets, creating a gap between proprietary and public knowledge. The gap: lack of access to high-quality large-scale pretraining datasets and documentation of curation decisions. This work aims to minimize the gap by releasing FineWeb datasets with full documentation of filtering and deduplication pipelines.

### Methodology
**Experimental Setup:**
- Data ablation models: 1.71B parameters, Llama architecture, sequence length 2048, batch size ~2M tokens, GPT-2 tokenizer
- Training: 28B tokens for filtering ablations, 350B tokens for deduplication ablations
- Evaluation: CommonSenseQA, HellaSwag, OpenBookQA, PIQA, SIQA, WinoGrande, ARC, MMLU (truncated to 1000 samples)
- 2 models per dataset version with different random seeds to minimize variance
- 70+ models trained, 80,000 H100 GPU hours total

**FineWeb Pipeline:**
1. **Text Extraction:** trafilatura on WARC files (not WET) — removes boilerplate/menu text better than htmlparser
2. **Base Filtering:** URL blocklist for adult content, fastText language classifier (English ≥0.65 score), MassiveText quality/repetition filters → 36T tokens
3. **Deduplication:** MinHash with 5-grams, 112 hash functions (14 buckets × 8 hashes), 75% similarity threshold. **Key finding:** Individual per-snapshot deduplication (20T tokens) outperforms global deduplication (4T tokens) — global dedup upsamples low-quality data from older crawls → 20T tokens
4. **Additional Filtering:** C4 filters (curly bracket, word lengths, lorem_ipsum, javascript, policy) + custom FineWeb filters (line dedup, short lines, punctuation) → 15T tokens FineWeb

**FineWeb-Edu Pipeline:**
- Educational quality classifier trained on samples manually labeled for educational value
- LightGBM model with fastText embeddings + heuristic features (word count, fraction of capitalized/numeric chars, ellipsis/hashtag counts, etc.)
- Filtering threshold: retain top 30% by educational score → 1.3T tokens

**Key Design Decision — Deduplication Strategy:**
- Global deduplication: removed 90% of oldest snapshots, resulting in worse model performance (ads, keyword spam retained in "kept" 10%)
- Individual deduplication: each snapshot deduplicated independently, matches RefinedWeb performance
- Hypothesis: Large duplicate clusters (100K+ docs) should be removed, but over-deduplicating small clusters (<100 duplicates across snapshots) harms quality

### Experiments & Results

**Main Results (1.8B model, 350B tokens):**
| Dataset | Aggregate Acc | HellaSwag | MMLU | ARC |
|---------|--------------|-----------|------|-----|
| FineWeb | ~47% | ~47% | - | - |
| FineWeb-Edu | - | - | +5.0pp | +4.5pp |
| RefinedWeb | ~46% | ~45% | - | - |
| C4 | ~44% | ~46% | - | - |
| Dolma | ~43% | ~42% | - | - |

**FineWeb-Edu Dramatic Gains (knowledge/reasoning benchmarks):**
- MMLU: +5.0 percentage points vs FineWeb baseline
- ARC-Challenge: +4.5pp
- ARC-Easy: +3.5pp
- Educational filtering trades off some performance on other benchmarks but yields large gains on knowledge-intensive tasks

**Ablation Findings:**
- Text extraction (trafilatura vs WET): +2-3pp aggregate accuracy
- Base filtering (RefinedWeb-style): +4-5pp
- Individual deduplication vs global: +2pp (global dedup performs WORSE than no dedup for older crawls)
- C4 terminal punctuation filter alone: +3pp HellaSwag but removes 30% of tokens (not used)
- C4 filters (except terminal punct): +1pp while removing only 7%
- Custom FineWeb filters (line dedup, short lines, punctuation): +2pp aggregate
- Tested 50+ candidate filters; final FineWeb uses 12 high-signal filters

**Scaling Validation:**
- Trained larger models (up to 7B scale) on FineWeb vs baselines — performance advantages hold at scale
- FineWeb-trained models competitive with or better than RefinedWeb, Dolma, C4, RedPajama across scales

### Discussion & Conclusion
Systematic ablation methodology reveals: (1) text extraction quality matters significantly; (2) deduplication strategy (individual vs global) has large impact — global dedup can harm quality by upsampling low-quality content from older crawls; (3) educational filtering (FineWeb-Edu) provides dramatic gains on knowledge/reasoning benchmarks at cost of general performance. Limitations: English-focused, evaluation at relatively small scale (1.8B models for ablations). Future: multilingual extension, additional quality-targeted filters, domain-specific subsets. Released datatrove library enables community to reproduce and extend.

## Key Contributions
- FineWeb: 15T token dataset outperforming all public web-based pretraining datasets on aggregate benchmarks (RefinedWeb, C4, Dolma, RedPajama)
- FineWeb-Edu: 1.3T educational subset with +5.0pp MMLU, +4.5pp ARC gains vs FineWeb baseline
- Comprehensive deduplication strategy comparison: individual per-snapshot deduplication superior to global deduplication (counter-intuitive finding)
- datatrove: open-source data processing library with 50+ candidate filters, 70+ ablation models publicly released

## Potential Relevance
FineWeb-Edu's educational quality classifier approach directly applicable to RAG corpus quality assessment (hypothesis: train classifier to identify "retrieval-quality" documents using positive/negative examples). Individual deduplication strategy may apply to RAG corpus construction (avoid over-deduplicating retrieval sources to preserve coverage). Educational classifier features (word count, capitalization, punctuation) could inform RAG document quality metrics. Ablation methodology (train small models on filtered subsets, measure retrieval performance) provides template for testing RAG-specific filtering strategies. FineWeb vs FineWeb-Edu trade-off illustrates domain-specific filtering gains at cost of general performance — relevant for RAG corpus specialization decisions.
