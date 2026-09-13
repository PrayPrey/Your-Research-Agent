## Title
Safety-Aware Data Selection (SADS): Preemptive Safety Filtering for Multimodal Foundation Model Pre-training

## Motivation
Current approaches to multimodal model safety rely heavily on post-hoc interventions like RLHF, which are computationally expensive and reactive. While recent work (LARF) demonstrates that safety-degrading features can be detected in fine-tuning data, no systematic approach exists for filtering safety risks at the pre-training stage—where problematic patterns first become encoded into model representations. This gap perpetuates the costly cycle of training unsafe models then patching them afterward.

## Main Idea
We propose Safety-Aware Data Selection (SADS), integrating multi-dimensional safety classification into pre-training data curation. The core hypothesis: filtering training samples based on composite safety scores (toxicity, bias, NSFW, violence) before pre-training prevents safety-problematic patterns from being encoded into model representations, reducing downstream vulnerabilities more efficiently than post-hoc alignment.

The methodology employs an ensemble of safety classifiers to score web-scale text-image data, filtering samples exceeding tunable thresholds. We will train matched multimodal models on SADS-filtered versus quality-only filtered data, measuring safety violation rates on MMDT benchmarks while ensuring capability preservation (within 2% on MMLU/HellaSwag).

Expected outcomes include ≥5 percentage point reduction in safety violations and reduced post-hoc alignment requirements. This establishes proactive, resource-efficient safety principles for responsible foundation model development.