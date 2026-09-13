---
source_paper: "arxiv_2406_11794.md"
generated_at: "2026-03-14T16:48:39.000202"
model: "gpt-4o-mini"
summary_chars: 6490
---

# DataComp-LM (DCLM)

## Key Metadata
- **Authors:** Jeffrey Li et al.
- **Year:** 2024
- **Venue:** arXiv
- **Core Contribution:** The paper introduces DataComp for Language Models (DCLM), a testbed for dataset experiments that leads to the development of DCLM-BASELINE, a new high-quality dataset for training language models.

## Section Summaries

### Abstract
We introduce DataComp for Language Models (DCLM), a testbed for controlled dataset experiments with the goal of improving language models. As part of DCLM, we provide a standardized corpus of 240T tokens extracted from Common Crawl, effective pretraining recipes based on the OpenLM framework, and a broad suite of 53 downstream evaluations. Participants in the DCLM benchmark can experiment with data curation strategies such as deduplication, filtering, and data mixing at model scales ranging from 412M to 7B parameters. As a baseline for DCLM, we conduct extensive experiments and find that model-based filtering is key to assembling a high-quality training set. The resulting dataset, DCLM-BASELINE, enables training a 7B parameter language model from scratch to 64% 5-shot accuracy on MMLU with 2.6T training tokens. Compared to MAP-Neo, the previous state-of-the-art in open-data language models, DCLM-BASELINE represents a 6.6 percentage point improvement on MMLU while being trained with 40% less compute. Our baseline model is also comparable to Mistral-7B-v0.3 and Llama 3 8B on MMLU (63% & 66%), and performs similarly on an average of 53 natural language understanding tasks while being trained with 6.6× less compute than Llama 3 8B. Our results highlight the importance of dataset design for training language models and offer a starting point for further research on data curation. We release the DCLM benchmark, framework, models, and datasets at https://datacomp.ai/dclm.

### Introduction & Motivation
Large training datasets are critical drivers of advancements in language modeling. As training costs escalate, improving datasets to enable efficient generalization on diverse downstream tasks is increasingly important. Existing proposals for data improvement are hindered by uncontrolled comparisons across varying architectures, computes, or hyperparameters, making it difficult to pinpoint effective data curation strategies. DCLM addresses these gaps by providing a controlled benchmark for language model training data curation, allowing for the evaluation of new datasets and algorithms through standardized methods.

### Methodology
The DCLM framework consists of a comprehensive experimental testbed and structured evaluations. The core component, DCLM-POOL, comprises 240 trillion tokens derived from Common Crawl. Participants select a competition scale (400M to 7B parameters), apply either a filtering (to curate datasets from DCLM-POOL) or mixing (combining DCLM-POOL with other sources) track, and train a language model using a fixed recipe. The model architecture uses a decoder-only Transformer, performed with settings including a learning rate of 2e-5, a batch size of 256, and up to 4 epochs of training. The effective training loss is computed using the cross-entropy loss function, formulated as:

\[
\text{Loss} = -\sum_{i=1}^{n}y_i \log(p_i)
\]

Key novel filtering strategies utilize a fastText classifier to discern quality data, particularly effective at retaining the top 10% of documents based on classifier score. Environments are created with OpenLM, ensuring consistency across varying scales. The input format also standardizes preprocessing through document extraction from HTML via a tool, resiliparse.

### Experiments & Results
DCLM consisted of 416 baseline experiments utilizing datasets such as C4 and RefinedWeb, with training and evaluation metrics focused on MMLU 5-shot accuracy and CORE scores. The main dataset, DCLM-BASELINE, yielded a model achieving 64% on MMLU with 2.6 trillion training tokens—improving on MAP-Neo's previous performance and reducing training compute by 40%. Detailed benchmarking across various scales showed a correlation of performance with dataset quality, quantified through improvements in CORE scores from model-based filtering (MMLU scores ranged from 35%-44% based on configurations). Significant results are summarized below:

| Model               | Parameters | Compute       | MMLU 5-shot Accuracy | CORE Score |
|---------------------|------------|---------------|-----------------------|------------|
| DCLM-BASELINE       | 7B         | 2.6T tokens   | 64%                   | 44.1       |
| MAP-Neo             | 7B         | 4.1T tokens   | 57.4%                 | 39.5       |
| Llama 3 8B          | 8B         | 15T tokens    | 66%                   | 45.8       |

The effectiveness of data mixing was also explored, finding that while incorporating high-quality sources can enhance lower-performing datasets, it could detract from the already optimized DCLM-BASELINE performance. Importantly, a decontamination analysis determined that performance improvements were not skewed by contamination with the test sets used in evaluations.

### Discussion & Conclusion
DCLM establishes a systematic approach to dataset design in language model training, yielding state-of-the-art results and valuable insights into the factors influencing performance. Limitations encountered include compute constraints that prevented a thorough exploration of all potential data curation strategies and the application of various tokenization methods across languages. Future directions include expanding the DCLM testbed to enhance capabilities in code and math, while tackling issues of bias, multilinguality, and safety.

## Key Contributions
- Development of the DCLM benchmark for controlled dataset experiments aimed at improving language model performance.
- Introduction of the DCLM-BASELINE dataset leading to significant advancements in language model accuracy and efficiency.
- Systematic exploration of data curation methodologies, emphasizing model-based filtering as a key factor for effective dataset quality.

## Potential Relevance
The comprehensive methodology and findings of this paper can inform future studies on data curation strategies, particularly in the context of language modeling. The results emphasizing the importance of dataset design and the DCLM framework can serve as a pivotal reference for enhancing the performance of existing language models and developing new data-centric research approaches.