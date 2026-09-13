1. **Title**: FPGA Co-Design for Efficient N:M Sparse and Quantized Model Inference (arXiv:2512.24713)
   - **Authors**: Fen-Yu Hsieh, Yun-Chang Teng, Ding-Yong Hong, Jan-Jan Wu
   - **Summary**: This paper introduces an automation framework that applies N:M structured pruning and 4-bit integer quantization to large language models (LLMs). The authors present a hardware-software co-design method that generates accelerators on FPGA platforms, achieving up to 4× reduction in weight storage and a 1.71× speedup in matrix multiplication.
   - **Year**: 2025

2. **Title**: Aggressive Post-Training Compression on Extremely Large Language Models (arXiv:2409.20094)
   - **Authors**: Zining Zhang, Yao Chen, Bingsheng He, Zhenjie Zhang
   - **Summary**: The authors propose a network pruning technique utilizing over 70% sparsity combined with sub-8-bit quantization. This approach enables rapid compression of prevailing LLMs within hours, maintaining relatively small accuracy loss, thereby facilitating deployment on personal devices.
   - **Year**: 2024

3. **Title**: FineQ: Software-Hardware Co-Design for Low-Bit Fine-Grained Mixed-Precision Quantization of LLMs (arXiv:2504.19746)
   - **Authors**: Xilong Xie, Liang Wang, Limin Xiao, Meng Han, Lin Sun, Shuai Zheng, Xiangrong Xu
   - **Summary**: FineQ introduces a co-design framework that partitions weights into fine-grained clusters, applying low-bit mixed-precision quantization. The approach balances model accuracy and memory overhead, achieving higher accuracy compared to state-of-the-art mixed-precision quantization algorithms, with up to 1.79× energy efficiency and a 61.2% reduction in systolic array area.
   - **Year**: 2025

4. **Title**: Effective Interplay between Sparsity and Quantization: From Theory to Practice (arXiv:2405.20935)
   - **Authors**: Simla Burcu Harma, Ayan Chakraborty, Elizaveta Kostenok, Danila Mishin, Dongho Ha, Babak Falsafi, Martin Jaggi, Ming Liu, Yunho Oh, Suvinay Subramanian, Amir Yazdanbakhsh
   - **Summary**: This paper provides a mathematical proof that sparsity and quantization are non-orthogonal and their combined use can introduce additional errors. The authors demonstrate that the order of applying these methods affects accuracy and offer insights into best practices for combining them to maximize hardware efficiency without compromising accuracy.
   - **Year**: 2024

5. **Title**: QQQ: Quality Quattuor-Bit Quantization for Large Language Models (arXiv:2406.09904)
   - **Authors**: Ying Zhang, Peng Zhang, Mincong Huang, Jingyang Xiang, Yujie Wang, Chao Wang, Yineng Zhang, Lei Yu, Chuan Liu, Wei Lin
   - **Summary**: QQQ presents a 4-bit weight and 8-bit activation quantization method employing adaptive smoothing and Hessian-based compensation. The approach enhances performance of quantized models without extensive training and includes specialized GEMM kernels, achieving up to 2.24× speed boosts over FP16.
   - **Year**: 2024

6. **Title**: Outlier Weighed Layerwise Sparsity (OWL) (arXiv:2310.05175)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: OWL introduces a layerwise sparsity method that aligns with the model's layerwise outlier distribution (LOD). By assigning distinct pruning ratios for each Transformer block, OWL achieves substantial reductions in perplexity scores across various LLMs, demonstrating effectiveness in high-sparsity scenarios.
   - **Year**: 2023

7. **Title**: Pruning Small Pre-Trained Weights Irreversibly and Monotonically Impairs (arXiv:2310.02277)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: This study investigates the impact of pruning small-magnitude weights in pre-trained models, revealing that such pruning can cause irreversible performance degradation, especially on complex tasks. The findings highlight the importance of careful pruning strategies to preserve essential knowledge in LLMs.
   - **Year**: 2023

8. **Title**: Extreme Compression of Large Language Models via Additive Quantization (arXiv:2401.06118)
   - **Authors**: [Authors not specified in the provided excerpt]
   - **Summary**: The authors present AQLM, an additive quantization method targeting LLM compression, achieving significant improvements in low-bit quantization. AQLM enables accurate and efficient execution of massive LLMs using minimal memory, with up to 4× faster inference relative to FP32 on CPUs.
   - **Year**: 2024

**Key Challenges:**

1. **Non-Orthogonality of Sparsity and Quantization**: Combining sparsity and quantization is not straightforward, as their interplay can introduce additional errors, affecting model accuracy. Understanding and mitigating these compounded errors is crucial.

2. **Optimal Order of Application**: The sequence in which sparsity and quantization are applied influences the final model performance. Determining the optimal order requires careful consideration to preserve model integrity.

3. **Hardware Compatibility**: Developing compression methods that align with hardware capabilities is challenging. Ensuring that sparsity and quantization techniques are effectively supported by existing hardware architectures is essential for practical deployment.

4. **Maintaining Model Accuracy**: Aggressive compression strategies, such as high sparsity levels and low-bit quantization, often lead to significant accuracy degradation. Balancing compression rates with acceptable performance loss remains a key challenge.

5. **Efficient Training and Fine-Tuning**: Implementing compression techniques that do not require extensive retraining or fine-tuning is desirable. Developing methods that achieve significant compression with minimal additional training effort is an ongoing research focus. 