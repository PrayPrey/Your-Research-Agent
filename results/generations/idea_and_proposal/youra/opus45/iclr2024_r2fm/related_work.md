## Related Work

**Related Papers**
1. **Title**: LLM Internal States Reveal Hallucination Risk (arXiv:2407.03282)
   - **Authors**: Ji, Chen, Ishii, Cahyawijaya, Bang, Wilie, Fung
   - **Summary**: Demonstrates that probing estimators can achieve 84.32% hallucination detection accuracy by analyzing final-layer hidden states of LLMs.
   - **Year**: 2024

2. **Title**: Metacognition and Confidence: A Review and Synthesis (DOI: 10.1146/annurev-psych-022423-032425)
   - **Authors**: Fleming
   - **Summary**: Establishes that metacognitive judgments are inferential in nature, with separate monitoring and control systems enabling real-time behavioral adjustment.
   - **Year**: 2023

3. **Title**: Unsupervised Real-Time Hallucination Detection (MIND) (arXiv:2403.06448)
   - **Authors**: Su, Wang, Ai, Hu, Wu, Zhou, Liu
   - **Summary**: Demonstrates the feasibility of real-time hallucination detection using internal states without requiring manual annotations.
   - **Year**: 2024

4. **Title**: SelfCheckGPT
   - **Authors**: Manakul et al.
   - **Summary**: Provides post-generation verification for hallucination detection, operating after text generation rather than in real-time.
   - **Year**: 2023

5. **Title**: RLHF-V: Trustworthy MLLMs via Fine-Grained Correctional Feedback
   - **Authors**: Yu et al.
   - **Summary**: Shows that segment-level corrections can reduce hallucination by 34.8%, though the approach is applied at training time rather than during inference.
   - **Year**: 2023

6. **Title**: HalluLens Benchmark
   - **Authors**: Bang, Ji, et al.
   - **Summary**: Provides a comprehensive hallucination benchmark that distinguishes between extrinsic and intrinsic hallucination types, though it does not evaluate real-time mitigation approaches.
   - **Year**: 2025

**Key Challenges**
1. **Detection Without Intervention**: Existing methods like MIND focus solely on hallucination detection without providing mechanisms for intervention or correction during generation.
2. **Lack of Real-Time Operation**: Approaches such as SelfCheckGPT perform post-generation verification, making them unsuitable for real-time hallucination mitigation during the generation process.
3. **Training-Time vs. Inference-Time Solutions**: Methods like RLHF-V achieve hallucination reduction through training-time corrections, but do not address the need for inference-time intervention.
4. **Absence of Real-Time Mitigation Evaluation**: Comprehensive benchmarks like HalluLens evaluate hallucination types but do not assess real-time mitigation strategies.
