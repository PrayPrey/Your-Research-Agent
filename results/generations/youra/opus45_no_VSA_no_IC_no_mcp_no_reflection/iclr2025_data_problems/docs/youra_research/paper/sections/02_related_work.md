# Related Work

We position EDMP against three lines of prior work: domain mixing optimization methods that require training, embedding-based selection approaches for fine-tuning, and perplexity-based data filtering. Our approach combines the task-grounding of embedding methods with the pretraining focus of mixing optimization—while eliminating the training requirement.

## Domain Mixing Optimization

Recent work has established that domain mixing ratios significantly affect downstream LLM performance. DoReMi [Xie et al., 2023] optimizes domain weights using distributionally robust optimization over a proxy model, achieving 2-3% improvements over heuristic mixing on benchmarks including MMLU. However, DoReMi requires training both a reference model and a proxy model before determining optimal weights—a substantial computational overhead.

SlimPajama [Soboleva et al., 2023] and RedPajama [Together AI, 2023] provide domain-labeled pretraining corpora with carefully curated mixing ratios, but these ratios are determined through expensive ablation studies rather than predicted a priori.

The Pile [Gao et al., 2020] established the multi-domain pretraining paradigm with 22 labeled domains, enabling controlled experiments on domain composition effects. Follow-up work confirmed that equal-weight mixing is suboptimal, motivating principled optimization approaches.

**Limitation:** All current domain mixing optimization methods require training runs (proxy models or full ablations) to evaluate domain utility. No training-free prediction method exists.

## Embedding-Based Data Selection

DSIR [Xie et al., 2023] introduced importance sampling for fine-tuning data selection, using embedding similarity to select samples aligned with target tasks. This work demonstrated that embedding space proximity correlates with transfer performance, providing theoretical grounding for our approach.

Task-adaptive pretraining [Gururangan et al., 2020] showed that domain-relevant data improves downstream performance, using document-level classification to identify relevant pretraining data. However, this approach requires labeled domain data and focuses on single-task optimization.

Data selection via language model scoring [Marion et al., 2023] uses perplexity to filter pretraining data, implicitly selecting for data distribution alignment. This approach is training-dependent and lacks task grounding.

**Limitation:** Existing embedding-based selection focuses on fine-tuning data, not pretraining domain mixing. These methods select individual samples rather than ranking entire domains.

## Perplexity-Based Selection

Perplexity filtering has become standard in LLM data curation, with models like GPT-4 and Llama using perplexity thresholds to filter low-quality text. However, perplexity is model-dependent—the same text may have different perplexity under different models—and lacks explicit grounding in downstream task requirements.

The Chinchilla scaling laws [Hoffmann et al., 2022] emphasized data quality alongside quantity, motivating principled data curation. However, "quality" is typically defined via heuristic filtering (perplexity, repetition, language classification) rather than task-grounded metrics.

**Limitation:** Perplexity-based selection is model-dependent and ungrounded in specific downstream tasks. It filters individual documents rather than optimizing domain mixing.

## Our Position

EDMP bridges these approaches by applying embedding-based similarity scoring to the domain mixing problem. Unlike DoReMi, EDMP requires no training—only frozen embedder inference. Unlike DSIR, EDMP targets pretraining domain ranking rather than fine-tuning sample selection. Unlike perplexity filtering, EDMP explicitly grounds scoring in downstream task exemplars.

The key question we investigate is whether the correlation between embedding similarity and transfer performance—established in fine-tuning contexts—extends to pretraining domain utility prediction. If so, EDMP could provide the training-free domain mixing optimization that current methods lack.
