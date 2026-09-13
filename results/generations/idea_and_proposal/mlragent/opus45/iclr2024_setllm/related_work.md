1. **Title**: HATS: High-Accuracy Triple-Set Watermarking for Large Language Models (2512.19378)
   - **Authors**: Zhiqing Hu, Chenxu Zhao, Jiazhong Lu, Xiaolei Liu
   - **Summary**: This paper introduces a watermarking technique that partitions the vocabulary into three sets (Green/Yellow/Red) during text generation, restricting sampling to the Green and Yellow sets. Detection involves replaying these partitions and analyzing statistical deviations to identify watermarked content. The method achieves high detection accuracy while preserving text quality.
   - **Year**: 2025

2. **Title**: REMARK-LLM: A Robust and Efficient Watermarking Framework for Generative Large Language Models (2310.12362)
   - **Authors**: Ruisi Zhang, Shehzeen Samarah Hussain, Paarth Neekhara, Farinaz Koushanfar
   - **Summary**: REMARK-LLM presents a watermarking framework that embeds binary signatures into LLM-generated texts using a learning-based encoding module. It ensures semantic integrity and robustness against various attacks, effectively embedding more signature bits compared to prior methods.
   - **Year**: 2023

3. **Title**: StealthInk: A Multi-bit and Stealthy Watermark for Large Language Models (2506.05502)
   - **Authors**: Ya Jiang, Chuxiong Wu, Massieh Kordi Boroujeny, Brian Mark, Kai Zeng
   - **Summary**: StealthInk introduces a watermarking scheme that embeds multi-bit provenance data within LLM-generated text without altering its distribution. It enhances traceability and is resilient against various attacks, including paraphrasing and model inversion.
   - **Year**: 2025

4. **Title**: Robust Data Watermarking in Language Models by Injecting Fictitious Knowledge (2503.04036)
   - **Authors**: Xinyue Cui, Johnny Tian-Zheng Wei, Swabha Swayamdipta, Robin Jia
   - **Summary**: This approach injects coherent yet fictitious knowledge into training data, creating watermarks that are memorized by LLMs. These watermarks are designed to be robust against data preprocessing and can be evaluated even with API-only access.
   - **Year**: 2025

5. **Title**: Enhancing LLM Watermark Resilience Against Both Scrubbing and Spoofing Attacks
   - **Authors**: Baizhou Huang, Huanming Shen, Xiaojun Wan
   - **Summary**: The paper addresses vulnerabilities in LLM watermarking by introducing equivalent texture keys, allowing multiple tokens within a watermark window to support detection independently. This method improves resilience against both scrubbing and spoofing attacks.
   - **Year**: 2025

6. **Title**: Mark Your LLM: Detecting the Misuse of Open-Source Large Language Models via Watermarking
   - **Authors**: Yijie Xu, Aiwei Liu, Xuming Hu, Lijie Wen, Hui Xiong
   - **Summary**: This work defines misuse scenarios for open-source LLMs and explores watermarking techniques, including inference-time watermark distillation and backdoor watermarking, to detect unauthorized usage effectively.
   - **Year**: 2025

7. **Title**: Provable Robust Watermarking for AI-Generated Text
   - **Authors**: Xuandong Zhao, Yuheng Bu
   - **Summary**: The authors propose Unigram-Watermark, a method that embeds watermarks into AI-generated text with guarantees on generation quality and robustness against text editing and paraphrasing.
   - **Year**: 2023

8. **Title**: Robust Multi-bit Text Watermark with LLM-based Paraphrasers
   - **Authors**: Xiaojun Xu, Jinghan Jia, Yuanshun Yao, Yang Liu, Hang Li
   - **Summary**: This paper presents a multi-bit text watermarking method using fine-tuned LLM paraphrasers to embed watermarks at the sentence level, ensuring imperceptibility and robust detection.
   - **Year**: 2024

9. **Title**: Multi-use LLM Watermarking and the False Detection Problem
   - **Authors**: Zihao Fu, Chris Russell
   - **Summary**: The authors discuss the challenges of using the same embedding for both detection and user identification in LLM watermarking, proposing Dual Watermarking to jointly encode detection and identification watermarks into generated text.
   - **Year**: 2025

10. **Title**: Watermarking Diffusion Language Models
    - **Authors**: Thibaud Gloaguen, Robin Staab, Nikola Jovanović, Martin Vechev
    - **Summary**: This work introduces a watermarking method tailored for diffusion language models, enabling reliable watermarking by applying the watermark in expectation over the context, even when some context tokens are yet to be determined.
    - **Year**: 2025

**Key Challenges:**

1. **Robustness Against Adversarial Attacks**: Watermarking techniques must withstand various attacks, such as paraphrasing, synonym substitution, and model inversion, which can remove or alter the embedded watermarks.

2. **Maintaining Text Quality**: Embedding watermarks should not degrade the quality or coherence of the generated text, ensuring that the watermarked content remains indistinguishable from non-watermarked text.

3. **Detection in Black-Box Settings**: Verifying the presence of watermarks without access to the model's internal mechanisms or outputs poses a significant challenge, especially when dealing with third-party services.

4. **Scalability and Efficiency**: Watermarking methods need to be computationally efficient and scalable to handle large-scale deployments without introducing significant overhead.

5. **Balancing Imperceptibility and Detectability**: Achieving a balance between making watermarks imperceptible to users while ensuring they are detectable by authorized parties is crucial for effective watermarking. 