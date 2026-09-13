# Related Work

## Pre-Training Data Curation

Large-scale pre-training datasets like C4 [Raffel et al., 2020], The Pile [Gao et al., 2020], and RedPajama apply deduplication, perplexity filtering, and language detection to web-scraped corpora. DataComp [Gadre et al., 2023] systematically explores filtering strategies for vision-language pre-training, demonstrating that curation quality significantly impacts downstream performance. These works establish best practices for pre-training but do not test whether discovered thresholds transfer to fine-tuning or RLHF stages. Our work extends this line by characterizing which pre-training curation decisions can be reused downstream.

## Fine-Tuning Data Selection

Instruction tuning research focuses on quality over quantity: LIMA [Zhou et al., 2023] achieves strong performance with only 1,000 high-quality examples, while Alpagasus [Chen et al., 2023] filters Alpaca-52k using ChatGPT-based scoring to remove low-quality instructions. These methods optimize for instruction-following tasks but do not leverage curation knowledge from pre-training. Our taxonomy shows that while task-specific filters require stage-specific tuning (5.04% transfer degradation), low-level hygiene operations can be transferred from pre-training (0.38% delta).

## RLHF and Preference Data Curation

RLHF pipelines curate preference data to align models with human values [Ouyang et al., 2022; Bai et al., 2022]. Constitutional AI [Bai et al., 2022] generates synthetic preference pairs, while Anthropic HH-RLHF manually curates helpfulness and harmlessness examples. This work treats RLHF curation independently from earlier stages. Our framework predicts that safety filters (universal hygiene) should transfer from pre-training, while preference alignment criteria (objective-dependent) require RLHF-specific tuning—a hypothesis we leave for future work.

## Transfer Learning in Foundation Models

Transfer learning literature studies how model parameters transfer across tasks [Howard and Ruder, 2018; Devlin et al., 2019; Brown et al., 2020]. Pre-trained representations generalize to downstream tasks with minimal fine-tuning. Our work applies transfer analysis to *data curation* rather than model parameters, asking which curation decisions exhibit similar cross-task robustness. We find that data hygiene operations (deduplication, outlier removal) transfer analogously to low-level feature representations: both address universal properties independent of specific objectives.

## Subset Selection and Coreset Methods

Coreset construction [Feldman and Langberg, 2011] and k-center greedy subset selection [Sener and Savarese, 2018] reduce dataset size while preserving representativeness. DataComp applies embedding-based subset selection for pre-training. Our h-m3 hypothesis extends this work by characterizing the quality-speed trade-off when embedding stage mismatches training stage: early-stage embeddings (MiniLM) are 6.9× faster than late-stage (Instructor) but incur 2.4% quality penalty, quantifying the Pareto frontier for two-stage curation pipelines.

## Our Position

Existing work optimizes curation per-stage without testing cross-stage transfer. We provide the first systematic characterization of which curation techniques transfer robustly (low-level hygiene) versus which require stage-specific tuning (high-level strategy). This taxonomy enables practitioners to reuse universal operations while focusing optimization resources on stage-dependent components, reducing redundant curation effort across the FM training pipeline.
