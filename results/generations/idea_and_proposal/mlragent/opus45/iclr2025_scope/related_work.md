1. **Title**: FAEDKV: Infinite-Window Fourier Transform for Unbiased KV Cache Compression (arXiv:2507.20030)
   - **Authors**: Runchao Li, Yao Fu, Mu Sheng, Xianxuan Long, Haotian Yu, Pan Li
   - **Summary**: This paper introduces FAEDKV, a training-free KV cache compression framework that transforms the KV cache into the frequency domain using an Infinite-Window Fourier Transform. This method ensures unbiased information retention by equalizing the contribution of all tokens, effectively preserving both early and recent contextual information.
   - **Year**: 2025

2. **Title**: KVzip: Query-Agnostic KV Cache Compression with Context Reconstruction (arXiv:2505.23416)
   - **Authors**: Jang-Hyun Kim, Jinuk Kim, Sangwoo Kwon, Jae W. Lee, Sangdoo Yun, Hyun Oh Song
   - **Summary**: KVzip presents a query-agnostic KV cache eviction method that quantifies the importance of each KV pair by reconstructing the original context from cached KV pairs. It evicts less important pairs, achieving a 3-4× reduction in KV cache size and approximately 2× decrease in decoding latency with minimal performance loss across various tasks.
   - **Year**: 2025

3. **Title**: KVComp: A High-Performance, LLM-Aware, Lossy Compression Framework for KV Cache (arXiv:2509.00579)
   - **Authors**: Bo Jiang, Taolue Yang, Youyuan Liu, Chengming Zhang, Xubin He, Sian Jin
   - **Summary**: KVComp introduces a lossy compression framework tailored for KV cache data characteristics. It employs novel compression techniques co-designed with system architecture to achieve significant memory reduction with minimal accuracy degradation, enhancing computational efficiency during long-text generation.
   - **Year**: 2025

4. **Title**: KV-Distill: Nearly Lossless Learnable Context Compression for LLMs (arXiv:2503.10337)
   - **Authors**: Vivek Chari, Guanghui Qin, Benjamin Van Durme
   - **Summary**: KV-Distill proposes a Transformer compression framework that distills long-context KV caches into shorter representations in a question-independent manner. It treats compressed-uncompressed caches as student-teacher pairs and applies a KL-type divergence to match outputs, achieving significant compression while preserving downstream performance.
   - **Year**: 2025

5. **Title**: xKV: Cross-Layer SVD for KV-Cache Compression (arXiv:2503.18893)
   - **Authors**: Chi-Chih Chang, Chien-Yu Lin, Yash Akhauri, Wei-Cheng Lin, Kai-Chiang Wu, Luis Ceze, Mohamed S. Abdelfattah
   - **Summary**: xKV identifies alignment in dominant singular vectors across multiple layers of the KV cache and introduces a method that applies Singular Value Decomposition (SVD) across layers. This approach consolidates the KV cache into a shared low-rank subspace, achieving up to 8× reduction in KV cache size while maintaining accuracy.
   - **Year**: 2025

6. **Title**: GEAR: An Efficient KV Cache Compression Recipe for Near-Lossless Generative Inference of LLM (arXiv:2403.05527)
   - **Authors**: Hao Kang, Qingru Zhang, Souvik Kundu, Geonhwa Jeong, Zaoxing Liu, Tushar Krishna, Tuo Zhao
   - **Summary**: GEAR introduces a KV cache compression framework that combines quantization, low-rank approximation, and sparse matrix techniques. This integration exploits their synergistic potentials to achieve near-lossless 4-bit KV cache compression, resulting in significant throughput improvement and memory size reduction.
   - **Year**: 2024

7. **Title**: Model Tells You What to Discard: Adaptive KV Cache Compression for LLMs (arXiv:2310.01801)
   - **Authors**: Suyu Ge, Yunan Zhang, Liyuan Liu, Minjia Zhang, Jiawei Han, Jianfeng Gao
   - **Summary**: This study introduces an adaptive KV cache compression method that reduces memory footprint during generative inference. By profiling attention modules, it constructs the KV cache adaptively, evicting or retaining tokens based on attention head emphasis, without requiring resource-intensive fine-tuning or retraining.
   - **Year**: 2023

8. **Title**: R-KV: Redundancy-aware KV Cache Compression for Reasoning Models (arXiv:2505.24133)
   - **Authors**: Yifang Chen, Xiaoyu Li, Yingyu Liang, Zhenmei Shi, Zhao Song, Yu Tian
   - **Summary**: R-KV addresses the memory burden of long chain-of-thought reasoning by targeting redundancy in decoding-time KV caches. It combines attention-based importance scoring with a semantic-redundancy estimator to select non-redundant, informative tokens for retention, achieving near full KV performance using a fraction of the cache.
   - **Year**: 2025

9. **Title**: KVzap: Fast, Adaptive, and Faithful KV Cache Pruning (arXiv:2601.07891)
   - **Authors**: Simon Jegou, Maximilian Jeblick
   - **Summary**: KVzap introduces a fast, input-adaptive approximation of KVzip that leverages lightweight surrogate models trained on hidden states to predict the importance of KV pairs. It enables efficient pruning during both prefilling and decoding, achieving 2–4× KV cache compression with negligible accuracy loss across multiple large language models.
   - **Year**: 2026

10. **Title**: Limits of KV Cache Compression for Tensor Attention based Autoregressive Transformers (arXiv:2503.11108)
    - **Authors**: Yifang Chen, Xiaoyu Li, Yingyu Liang, Zhenmei Shi, Zhao Song, Yu Tian
    - **Summary**: This work analyzes the fundamental space complexity barriers in tensor attention mechanisms for autoregressive transformers. It provides a theoretical foundation for understanding the compression-expressivity tradeoff in tensor attention mechanisms and offers perspectives on developing more memory-efficient transformer architectures.
    - **Year**: 2025

**Key Challenges**:

1. **Balancing Compression and Information Retention**: Achieving significant KV cache compression without degrading model performance remains a critical challenge.

2. **Adaptability to Diverse Queries**: Developing compression methods that are effective across various tasks and queries without requiring task-specific tuning is complex.

3. **Computational Overhead**: Implementing compression techniques that do not introduce substantial computational overhead during inference is essential for practical deployment.

4. **Handling Long Contexts**: Efficiently managing and compressing KV caches in models processing long contexts without losing important information is challenging.

5. **Generalizability Across Models**: Ensuring that compression methods are effective across different model architectures and sizes without extensive retraining is a significant hurdle. 