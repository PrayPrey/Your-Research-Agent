---
source_paper: "arxiv_2406_17557.md"
generated_at: "2026-03-14T16:49:40.172508"
model: "gpt-4o-mini"
summary_chars: 6074
---

# The FineWeb Datasets

## Key Metadata
- **Authors:** Guilherme Penedo et al.
- **Year:** 2024
- **Venue:** 38th Conference on Neural Information Processing Systems (NeurIPS 2024) Track on Datasets and Benchmarks
- **Core Contribution:** Introduction of FineWeb datasets, a 15-trillion token dataset, and FineWeb-Edu, a 1.3-trillion token educational dataset, both optimized for training large language models (LLMs).

## Section Summaries

### Abstract
The performance of a large language model (LLM) depends heavily on the quality and size of its pretraining dataset. However, the pretraining datasets for state-of-the-art open LLMs like Llama 3 and Mixtral are not publicly available and very little is known about how they were created. In this work, we introduce FineWeb, a 15-trillion token dataset derived from 96 Common Crawl snapshots that produces better-performing LLMs than other open pretraining datasets. To advance the understanding of how best to curate high-quality pretraining datasets, we carefully document and ablate all of the design choices used in FineWeb, including in-depth investigations of deduplication and filtering strategies. In addition, we introduce FineWeb-Edu, a 1.3-trillion token collection of educational text filtered from FineWeb. LLMs pretrained on FineWeb-Edu exhibit dramatically better performance on knowledge- and reasoning-intensive benchmarks like MMLU and ARC. Along with our datasets, we publicly release our data curation codebase and all of the models trained during our ablation experiments.

### Introduction & Motivation
Large Language Models (LLMs) rely on expansive and high-quality pretraining datasets to perform effectively in various text-based tasks. However, existing public datasets often lack documentation regarding their curation processes, creating a significant gap in knowledge compared to proprietary datasets. The authors aim to fill this gap by releasing the FineWeb datasets, derived from 96 snapshots of Common Crawl, which contain high-quality filtering and deduplication methods. They also introduce FineWeb-Edu, an educational subset optimized for knowledge-intensive tasks, promoting transparency in the training of LLMs.

### Methodology
The methodology for creating the FineWeb dataset consists of multiple stages, focusing on an empirical approach to data ablation. FineWeb comprises 15 trillion tokens sourced from 96 Common Crawl snapshots, prepared to train a Chinchilla-optimal model. The model architecture used is based on the Llama design, with 1.71 billion parameters, a sequence length of 2048 tokens, and a global batch size of approximately 2 million tokens. 

Key hyperparameters include:
- Learning rate: \(3 \times 10^{-4}\)
- Epochs: 20
- Total training tokens: 28 billion for filtering ablations and 350 billion for deduplication processes.

The data extraction process utilized WARC files processed using the trafilatura library, noted for producing cleaner text than common WET files. Initial filtering was performed using a URL blocklist along with a fastText language classifier to maintain only English text. 

For deduplication, a MinHash technique was utilized, creating clusters of duplicates to retain high-quality documents. Distinct processing steps, including the integration of C4’s filters and additional heuristic filters based on statistical document metrics, contributed to the effectiveness of the dataset without excessively reducing the token count. 

Ultimately, the iterative dataset-building process provided significant performance improvements, as shown across various benchmarks. FineWeb-Edu emerged from FineWeb, utilizing a classifier developed from Llama-3 annotations to identify educational content optimized for various benchmarks.

### Experiments & Results
FineWeb was evaluated against multiple benchmarks to assess its performance. Notably, it outperformed other public datasets like C4 and RefinedWeb through various ablation studies. Training was performed over 80,000 H100 GPU hours, allowing for extensive evaluation on datasets such as CommonSense QA, ARC, and MMLU, which were truncated for efficiency.

Main results demonstrate FineWeb achieving notable aggregate performance, while FineWeb-Edu further advanced results in knowledge-intensive tasks. Table summarizing test scores:
| Benchmark  | FineWeb Aggregate Score | FineWeb-Edu Aggregate Score |
|------------|-------------------------|------------------------------|
| MMLU       | 33%                     | 37%                          |
| ARC        | 46%                     | 57%                          |
| OpenBookQA | 35%                     | Further improvements noted    |

An ablation study showed the most significant enhancements in performance following the application of various filtered datasets, with statistical significance corroborated through F1 scores across validation datasets.

### Discussion & Conclusion
The study highlights the significance of transparent dataset curation to improve language model training. FineWeb and FineWeb-Edu contribute significantly to advancing open datasets while identifying the potential for better performance through enhanced filtering and deduplication strategies. Future work should consider incorporating diverse data types and more extensive scales for additional impacts on performance.

## Key Contributions
- Release of FineWeb and FineWeb-Edu datasets with detailed curation strategies aimed at improving LLM training.
- Novel techniques for data extraction, filtering, and deduplication tailored for educational content.
- Publicly available models and methods supporting reproducibility and further research in dataset curation.

## Potential Relevance
The discussions around effective filtering, deduplication methods, and the creation of educational datasets from web sources may inform the development of hypotheses concerning dataset quality's impact on model performance. The extensive benchmark results provide a solid foundation to support future explorations in language model training efficacy.