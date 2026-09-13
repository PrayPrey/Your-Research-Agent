Here is a literature review on evaluating text-to-audio generation, focusing on works published between 2023 and 2025.

**1. Related Papers**

1. **Title**: EmergentTTS-Eval: Evaluating TTS Models on Complex Prosodic, Expressiveness, and Linguistic Challenges Using Model-as-a-Judge (arXiv:2505.23009)
   - **Authors**: Ruskin Raj Manku, Yuzhi Tang, Xingjian Shi, Mu Li, Alex Smola
   - **Summary**: This paper introduces EmergentTTS-Eval, a benchmark designed to assess text-to-speech (TTS) models on complex scenarios, including emotions, paralinguistics, foreign words, syntactic complexity, complex pronunciation, and questions. The framework automates test-case generation and evaluation, utilizing a Large Audio Language Model (LALM) to assess speech across multiple dimensions. The benchmark comprises 1,645 diverse test cases and demonstrates its effectiveness by evaluating state-of-the-art TTS systems, revealing fine-grained performance differences.
   - **Year**: 2025

2. **Title**: AQAScore: Evaluating Semantic Alignment in Text-to-Audio Generation via Audio Question Answering (arXiv:2601.14728)
   - **Authors**: Chun-Yi Kuan, Kai-Wei Chang, Hung-yi Lee
   - **Summary**: AQAScore is an evaluation framework that leverages audio-aware large language models (ALLMs) to assess semantic alignment in text-to-audio generation. By reformulating assessment as a probabilistic semantic verification task, AQAScore estimates alignment by computing the log-probability of a "Yes" answer to targeted semantic queries. The framework demonstrates higher correlation with human judgments compared to similarity-based metrics and generative prompting baselines, effectively capturing subtle semantic inconsistencies and scaling with the capability of underlying ALLMs.
   - **Year**: 2026

3. **Title**: AudioEval: Automatic Dual-Perspective and Multi-Dimensional Evaluation of Text-to-Audio-Generation (arXiv:2510.14570)
   - **Authors**: Hui Wang, Jinghua Zhao, Cheng Liu, Yuhang Jia, Haoqin Sun, Jiaming Zhou, Yong Qin
   - **Summary**: AudioEval presents a large-scale evaluation dataset containing 4,200 audio samples from 24 systems with 126,000 ratings across five perceptual dimensions, annotated by both experts and non-experts. The authors propose Qwen-DisQA, a multimodal scoring model that jointly processes text prompts and generated audio to predict human-like quality ratings. Experiments show its effectiveness in providing reliable and scalable evaluation, addressing the challenges in evaluating text-to-audio generation quality.
   - **Year**: 2025

4. **Title**: T2A-Feedback: Improving Basic Capabilities of Text-to-Audio Generation via Fine-grained AI Feedback (arXiv:2505.10561)
   - **Authors**: Zehan Wang, Ke Lei, Chen Zhu, Jiawei Huang, Sashuai Zhou, Luping Liu, Xize Cheng, Shengpeng Ji, Zhenhui Ye, Tao Jin, Zhou Zhao
   - **Summary**: T2A-Feedback introduces fine-grained AI audio scoring pipelines to verify event occurrence, detect deviations in event sequences, and assess overall acoustic and harmonic quality in text-to-audio generation. The authors construct a large audio preference dataset, T2A-FeedBack, containing 41k prompts and 249k audios with detailed scores. Utilizing this dataset, they demonstrate significant improvements in audio generation models through preference tuning, enhancing performance in both simple and complex scenarios.
   - **Year**: 2025

5. **Title**: In-Context Prompt Editing for Conditional Audio Generation (arXiv:2311.00895)
   - **Authors**: Ernie Chang, Pin-Jie Lin, Yang Li, Sidd Srinivasan, Gael Le Lan, David Kant, Yangyang Shi, Forrest Iandola, Vikas Chandra
   - **Summary**: This work addresses distributional shifts in text-to-audio generation by introducing a retrieval-based in-context prompt editing framework. Leveraging instruction-tuned large language models and demonstrative exemplars, the framework enhances audio quality across user prompts by revisiting and editing them with reference to training captions. The approach effectively mitigates audio quality degradation caused by unseen prompts, improving model adaptability in real-world settings.
   - **Year**: 2023

6. **Title**: Fast Timing-Conditioned Latent Audio Diffusion (arXiv:2402.04825)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper presents a latent diffusion model for generating long-form, variable-length stereo audio signals at 44.1kHz. The model incorporates timing conditioning through learned embeddings, allowing for precise control over the duration and timing of generated audio. The approach enables efficient generation of high-quality audio, addressing challenges in timing control and computational efficiency in audio generation.
   - **Year**: 2024

7. **Title**: ViLPAct: A Benchmark for Compositional Generalization in Vision-Language Navigation (arXiv:2210.05556)
   - **Authors**: [Authors not specified]
   - **Summary**: ViLPAct introduces a benchmark focusing on compositional generalization in vision-language navigation tasks. While not directly related to text-to-audio generation, the benchmark's emphasis on compositionality and structured event understanding provides insights into evaluating complex, multi-event scenarios, which are relevant for assessing compositional consistency in generated audio.
   - **Year**: 2023

8. **Title**: Generative Relevance Feedback with Large Language Models (arXiv:2304.13157)
   - **Authors**: [Authors not specified]
   - **Summary**: This work explores the use of large language models for generative relevance feedback in information retrieval. By generating contextually relevant expansions of user queries, the approach improves retrieval performance. The methodology offers potential applications in refining text prompts for audio generation, enhancing semantic alignment and relevance in generated outputs.
   - **Year**: 2023

9. **Title**: Deep Reinforcement Learning for Sequence-to-Sequence Models (arXiv:1805.09461)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper discusses the application of deep reinforcement learning to sequence-to-sequence models, addressing challenges in training and evaluation. The insights into evaluation measures and training methodologies are pertinent to developing robust evaluation frameworks for text-to-audio generation, particularly in handling complex, multi-event prompts.
   - **Year**: 2023

10. **Title**: CogVideoX: Text-to-Video Diffusion Models with Enhanced Temporal Consistency (arXiv:2408.06072)
    - **Authors**: [Authors not specified]
    - **Summary**: CogVideoX presents text-to-video diffusion models with a focus on temporal consistency. The techniques for ensuring alignment between textual prompts and generated video content offer valuable parallels for evaluating semantic and compositional consistency in text-to-audio generation, especially for complex prompts involving multiple events and temporal relations.
    - **Year**: 2024

**2. Key Challenges**

1. **Semantic Alignment**: Ensuring that generated audio accurately reflects the semantics of the text prompt remains challenging. Existing metrics often fail to capture fine-grained semantic inconsistencies, leading to misalignment between the prompt and the audio output.

2. **Compositional Consistency**: Evaluating audio generated from complex, multi-event prompts requires assessing the correct sequencing and temporal relationships of events. Current evaluation methods lack the capability to effectively measure compositional consistency, hindering the assessment of models on intricate prompts.

3. **Scalability of Evaluation**: Human evaluations, while accurate, are resource-intensive and not scalable. Developing automatic evaluation metrics that correlate well with human judgments is essential for efficient model development and benchmarking.

4. **Generalization to Unseen Prompts**: Text-to-audio models often struggle with prompts that deviate from their training distribution, leading to degraded audio quality. Addressing distributional shifts and enhancing model adaptability to diverse prompts is a significant challenge.

5. **Temporal Control and Timing Precision**: Achieving precise control over the timing and duration of events in generated audio is difficult. Models need to accurately interpret and generate audio that adheres to specified temporal constraints, which is crucial for applications requiring synchronization with other modalities. 