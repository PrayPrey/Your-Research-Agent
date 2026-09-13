## Related Work

**Related Papers**
1. **Title**: The RefinedWeb Dataset for Falcon LLM
   - **Authors**: Penedo et al.
   - **Summary**: Demonstrates that properly filtered web data alone can produce powerful language models, extracting 5 trillion tokens from CommonCrawl and establishing methodology for large-scale data curation.
   - **Year**: 2023

2. **Title**: Enhancing Multilingual LLM Pretraining with Model-Based Data Selection
   - **Authors**: Messmer et al.
   - **Summary**: Shows that 15% of training tokens can match baseline performance, demonstrating significant filtering headroom and supporting the feasibility of additional safety filtering without capability loss.
   - **Year**: 2025

3. **Title**: Layer-Aware Representation Filtering (LARF) (arXiv:2507.18631)
   - **Authors**: Li et al.
   - **Summary**: Demonstrates that safety-degrading features in fine-tuning data can be detected via layer-aware representations, providing direct evidence that safety properties are detectable in training data.
   - **Year**: 2025

4. **Title**: RepBend: Representation Bending for Large Language Model Safety
   - **Authors**: Yousefpour et al.
   - **Summary**: Achieves 95% attack success rate reduction via inference-time representation steering, serving as a primary post-hoc baseline for safety alignment comparison.
   - **Year**: 2025

5. **Title**: Post-hoc RLHF Alignment
   - **Authors**: Not specified
   - **Summary**: Standard approach for safety alignment after pre-training, representing the resource-intensive methodology that preemptive approaches aim to reduce reliance upon.
   - **Year**: Not specified

6. **Title**: OutSafe-Bench: Multimodal Offensive Content Detection
   - **Authors**: Yan et al.
   - **Summary**: Provides 18,000+ test samples across 4 modalities and 9 risk categories, revealing persistent safety vulnerabilities in current multimodal large language models.
   - **Year**: 2025

7. **Title**: SafeBench: Safety Evaluation Framework for MLLMs
   - **Authors**: Ying et al.
   - **Summary**: Offers a comprehensive safety benchmark with 23 risk scenarios and 2,300 harmful query pairs for evaluating multimodal large language model safety.
   - **Year**: 2025

8. **Title**: MMSafeAware: Benchmarking Multimodal Safety Awareness
   - **Authors**: Wang et al.
   - **Summary**: Reveals that GPT-4V misclassifies 36% of unsafe inputs and 60% of benign inputs, demonstrating that current models lack robust safety awareness.
   - **Year**: 2025

**Key Challenges**
1. **Persistent Safety Vulnerabilities in MLLMs**: Current multimodal large language models exhibit persistent safety vulnerabilities across multiple modalities and risk categories, as evidenced by comprehensive benchmarking efforts.

2. **Lack of Robust Safety Awareness**: State-of-the-art models like GPT-4V demonstrate poor discrimination between safe and unsafe content, with high misclassification rates for both unsafe and benign inputs.

3. **Resource-Intensive Post-hoc Alignment**: Standard RLHF-based safety alignment approaches require significant computational resources and are applied after pre-training, motivating the need for preemptive safety measures during data curation.

4. **Gap Between Data Filtering and Safety Integration**: While large-scale data curation methodologies exist for capability optimization, extending these approaches to incorporate safety-aware filtering during pre-training remains underexplored.

5. **Detecting Safety-Degrading Content in Training Data**: Identifying training data that may degrade model safety properties requires sophisticated detection mechanisms that can operate at scale during the data curation phase.
