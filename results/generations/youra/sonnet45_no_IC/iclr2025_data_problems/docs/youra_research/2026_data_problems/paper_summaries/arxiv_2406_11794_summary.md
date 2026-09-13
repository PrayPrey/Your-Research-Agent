# DataComp-LM: In search of the next generation of training sets for language models

## Key Metadata
- **Authors:** Jeffrey Li et al.
- **Year:** 2024
- **Venue:** arXiv preprint
- **Core Contribution:** A standardized benchmark for controlled language model training dataset experiments, enabling systematic comparison of data curation strategies.

## Section Summaries

### Abstract
We introduce DataComp for Language Models (DCLM), a testbed for controlled dataset experiments with the goal of improving language models. As part of DCLM, we provide a standardized corpus of 240T tokens extracted from Common Crawl, effective pretraining recipes based on the OpenLM framework, and a broad suite of 53 downstream evaluations. Participants can experiment with data curation strategies such as deduplication, filtering, and data mixing at model scales ranging from 412M to 7B parameters. The resulting dataset, DCLM-BASELINE, enables training a 7B parameter language model to 64% 5-shot accuracy on MMLU with 2.6T training tokens, representing a 6.6 percentage point improvement on MMLU while being trained with 40% less compute than MAP-Neo, the previous state-of-the-art in open-data language models.

### Introduction & Motivation
Large training datasets drive progress in language modeling, but researchers lack controlled comparisons for data curation strategies. The challenge: disentangling dataset quality from architecture, compute, and hyperparameter effects. Training set details are becoming scarce even for open-weight models (Llama, Mistral, Gemma). The gap: no standardized benchmark exists to quantify which data curation strategies work best across scales.

### Methodology
DCLM provides: (1) DCLM-POOL: 240T tokens from Common Crawl (200B documents, 370TB compressed); (2) Five competition scales (400M-1x to 7B-2x) spanning 600× compute range; (3) Two tracks: filtering (select from pool) and mixing (add external sources); (4) Fixed training recipes using decoder-only Transformers via OpenLM framework; (5) Standardized evaluation on 53 downstream tasks.

**Data Curation Pipeline (DCLM-BASELINE):**
1. Text extraction via resiliparse from HTML
2. Heuristic filtering (English, URL, page length, word removal ratio, repetition, word-length, ellipsis, stop words)
3. Bloom filter deduplication
4. Model-based filtering using FastText classifier with positive (OpenWebText, Wikipedia) and negative (4chan, BitChute) examples
5. Final mixing with high-quality sources

**Training:** GPT-NeoX tokenizer, decoder-only Transformer, AdamW optimizer ($\beta_1=0.9, \beta_2=0.95$), cosine learning rate schedule with warmup, gradient clipping, mixed precision (bfloat16).

**Evaluation:** MMLU 5-shot, CORE (22 tasks, centered accuracy 0-1), EXTENDED (all 53 tasks, centered accuracy).

### Experiments & Results
**Key Finding:** Model-based filtering outperforms heuristics significantly. Simple bigram FastText classifier (positive: OpenWebText, Wikipedia; negative: 4chan, BitChute) performs best among tested classifiers.

**Main Results (7B scale, 280B tokens):**
| Dataset | MMLU 5-shot | CORE | Compute vs Llama 3 8B |
|---------|-------------|------|----------------------|
| DCLM-BASELINE | 44% | 39.9 | 7× less |
| RefinedWeb | 38% | 35.7 | - |
| C4 | 35% | 32.4 | - |
| Dolma v1 | 37% | 34.5 | - |

**Scaling Results (7B, 2.6T tokens):**
- DCLM-BASELINE 7B: 64% MMLU (state-of-the-art for open-data models)
- Comparable to Mistral-7B-v0.3 (63%) and Llama 3 8B (66%) with 6.6× less compute
- 6.6pp improvement over MAP-Neo with 40% less compute

**Ablations:**
- Text extraction: resiliparse > trafilatura > Common Crawl's pre-extracted (+2-3pp MMLU)
- Deduplication: Bloom filter dedup gains 1-2pp MMLU
- Model filtering: FastText (bigram) > perplexity-based > heuristic-only (+9pp MMLU gain for best model filter vs heuristic-only)
- Human quality judgments have limited value for identifying high-quality training data

**Scaling Transfer:** High rank correlation between small (400M) and large (7B) scales (Pearson's r=0.838 to 0.982), enabling efficient iteration at small scales.

### Discussion & Conclusion
Dataset design is critical for training efficient language models. DCLM-BASELINE achieves state-of-the-art performance among open-data models with significantly less compute. Key takeaway: systematic data curation (especially model-based filtering) enables training models comparable to closed-source alternatives at a fraction of the cost. Limitations: DCLM-POOL is English-focused; contamination analysis ongoing. Future: expand to multilingual, explore synthetic data integration, investigate curriculum learning.

## Key Contributions
- DCLM benchmark: first large-scale standardized testbed for LM training data curation (240T token pool, 5 scales, 53 eval tasks)
- DCLM-BASELINE: state-of-the-art open-data training set enabling 7B model to reach 64% MMLU with 40% less compute than prior SOTA
- Systematic ablations identifying model-based filtering as key to high-quality dataset construction (FastText bigram classifier optimal)

## Potential Relevance
Model-based filtering approach directly applicable to RAG corpus curation (hypothesis: use similar positive/negative examples for retrieval quality). The multi-scale evaluation framework provides methodology for testing RAG-specific curation strategies. FastText classifier architecture and positive/negative example selection strategy may transfer to RAG domain filtering. Baseline for comparing quality metrics (perplexity, diversity, human judgment) in retrieval contexts.
