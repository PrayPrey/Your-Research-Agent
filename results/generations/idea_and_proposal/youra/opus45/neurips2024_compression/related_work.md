## Related Work

**Related Papers**
1. **Title**: Radio: Rate-Distortion Optimization for LLM Compression (arXiv:2505.03031)
   - **Authors**: Sean I. Young
   - **Summary**: Establishes rate-distortion theory foundations for model quantization and proves that RD optimization scales to 100B+ parameters.
   - **Year**: 2025

2. **Title**: Rate Distortion For Model Compression: From Theory To Practice (arXiv:1810.06401)
   - **Authors**: Gao, Wang, Oh
   - **Summary**: Proves the rate-distortion lower bound for model compression and develops an optimal compression scheme for 1-hidden-layer ReLU networks.
   - **Year**: 2018

3. **Title**: One is All: Unified Rate-Distortion-Complexity Framework (Semantic Scholar ID: 38082ee0b7af08d13b8a2542e4e970ca86ded778)
   - **Authors**: Chao Li et al.
   - **Summary**: Demonstrates a unified rate-distortion-complexity framework for image compression featuring a scalable entropy model.
   - **Year**: 2025

4. **Title**: Neural Estimation of the Rate-Distortion Function (NERD) (arXiv:2204.01612)
   - **Authors**: Eric Lei, Hamed Hassani, Shirin Saeedi Bidokhti
   - **Summary**: Proposes a neural rate-distortion estimator for real datasets, showing that DNN compressors can achieve performance within bits of the RD function.
   - **Year**: 2022

5. **Title**: CompressAI
   - **Authors**: InterDigital
   - **Summary**: Provides a data compression baseline implementation with hyperprior entropy model for learned image compression.
   - **Year**: Not specified

6. **Title**: TorchAO
   - **Authors**: PyTorch
   - **Summary**: Offers model compression baseline capabilities with INT4/INT8 quantization support.
   - **Year**: Not specified

7. **Title**: Intel Neural Compressor
   - **Authors**: Intel
   - **Summary**: Provides a unified compression framework for neural networks, though without joint rate-distortion optimization.
   - **Year**: Not specified

8. **Title**: Information Bottleneck Analysis of DNNs via Lossy Compression
   - **Authors**: Not specified
   - **Summary**: Validates the information-theoretic compression approach for neural networks through information bottleneck analysis.
   - **Year**: 2023

9. **Title**: Optimal Neural Compressors for RDP Tradeoff (arXiv:2503.17558)
   - **Authors**: Not specified
   - **Summary**: Demonstrates lattice coding with shared dithering for rate-distortion-perception optimality and validates the benefit of shared randomness in compression.
   - **Year**: 2025

**Key Challenges**
1. **Lack of Joint Rate-Distortion Optimization**: Existing unified compression frameworks like Intel Neural Compressor do not incorporate joint rate-distortion optimization, limiting their theoretical optimality.
2. **Scalability of RD Theory to Large Models**: While recent work has begun addressing RD optimization for large language models, extending these theoretical foundations to 100B+ parameter models remains an emerging challenge.
3. **Bridging Theory and Practice**: The gap between theoretical RD bounds for model compression and practical implementation, particularly for complex architectures beyond simple 1-hidden-layer networks, requires further investigation.
4. **Unified Framework Across Compression Domains**: Integrating rate-distortion-complexity considerations across both data compression and model compression within a single framework remains underexplored.
