## Related Work

**Related Papers**

1. **Title**: Eye Tracking-Enhanced Deep Learning for Medical Image Analysis: A Systematic Review on Data Efficiency, Interpretability, and Multimodal Integration
   - **Authors**: Duan et al.
   - **Summary**: Unified framework positioning eye tracking as (1) data efficiency optimizer via weak supervision, (2) interpretability validator comparing machine-human attention, and (3) multimodal alignment supervisor for VLMs. Validates gaze as interpretability ground truth and identifies lack of bidirectional frameworks.
   - **Year**: 2025

2. **Title**: Shedding light on ai in radiology: A systematic review and taxonomy of eye gaze-driven interpretability in deep learning
   - **Authors**: Neves et al.
   - **Summary**: Taxonomy of eye gaze-driven interpretability methods and benchmarks for gaze data quality verification and model-clinician attention alignment. Establishes medical imaging as primary application domain with all reviewed approaches being unidirectional.
   - **Year**: 2024

3. **Title**: Gender Recognition Using a Gaze-Guided Self-Attention Mechanism Robust Against Background Bias in Training Samples
   - **Authors**: Nishiyama et al.
   - **Summary**: Introduces Gaze-Guided Self-Attention (GSA) mechanism using human gaze distribution to assign spatially suitable attention weights, demonstrating robustness against background bias. Operates during training only.
   - **Year**: 2022

4. **Title**: Analyzing Interpretability of Summarization Model with Eye-gaze Information
   - **Authors**: Ikhwantri et al.
   - **Summary**: Uses eye-gaze to analyze and validate attention mechanisms in text summarization models, demonstrating gaze-attention correlation in NLP tasks. Analysis-only approach without bidirectional refinement.
   - **Year**: 2024

5. **Title**: Privacy-Preserving Gaze Data Streaming in Immersive Interactive Virtual Reality
   - **Authors**: Wilson et al.
   - **Summary**: Benchmarks privacy mechanisms (blurring, noising, downsampling, iris style transfer) in VR environments, reducing re-identification to 14% while maintaining usability for privacy-preserving gaze processing.
   - **Year**: 2024

6. **Title**: REFLACX Dataset
   - **Authors**: Johnson et al.
   - **Summary**: Dataset containing 3,940 chest X-ray images with radiologist eye-tracking annotations, providing baseline correspondence between gaze coordinates and diagnostic attention patterns for training gaze-attention mapping functions.
   - **Year**: 2021

7. **Title**: MIMIC-CXR Dataset
   - **Authors**: Johnson et al.
   - **Summary**: Large-scale dataset with 227,835 chest X-ray images accompanied by radiology reports and 14 pathology labels, serving as primary resource for fine-tuning and evaluation in medical diagnosis tasks.
   - **Year**: 2019

8. **Title**: An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale (Vision Transformer)
   - **Authors**: Dosovitskiy et al.
   - **Summary**: Standard transformer architecture adapted for images with O(N²) attention complexity, establishing foundation for vision transformers in medical imaging applications.
   - **Year**: 2020

9. **Title**: Swin Transformer: Hierarchical Vision Transformer using Shifted Windows
   - **Authors**: Liu et al.
   - **Summary**: Hierarchical transformer architecture with shifted windows that reduces computational complexity compared to standard Vision Transformers while maintaining performance.
   - **Year**: 2021

10. **Title**: Shared Autonomy in Assistive Robotics
   - **Authors**: Not specified
   - **Summary**: Foundational work on bidirectional human-robot control loops with confidence-based handoff for wheelchair navigation and robotic arm teleoperation. Introduces arbitration functions that blend human intent with autonomous control and convergence protocols for task completion.
   - **Year**: Not specified

**Key Challenges**

1. **Lack of Bidirectional Frameworks**: Current eye tracking and deep learning integration is predominantly unidirectional—either gaze used for training supervision or post-hoc validation, but no real-time interactive collaboration during inference.

2. **Real-time Computational Constraints**: Achieving low latency (<100ms) for interactive gaze-attention systems requires computational optimization beyond standard transformer architectures with O(N²) complexity.

3. **Convergence Guarantees**: Bidirectional control loops between human gaze and model attention need formal convergence criteria and mechanisms to ensure stable alignment within practical time and iteration limits.

4. **Cognitive Load Management**: Uncertainty-guided visual cues must provide helpful guidance without inducing excessive cognitive burden or distraction that could degrade diagnostic performance.

5. **Cross-Domain Transfer**: Gaze-attention mapping functions trained in one domain (e.g., medical imaging) may not generalize to other domains (e.g., document analysis, visual QA) without domain-specific retraining.

6. **Hardware Generalization**: Eye tracking systems vary in accuracy and specifications across manufacturers, requiring device-specific calibration that limits practical deployment scalability.

7. **Privacy-Preserving Deployment**: Clinical deployment at scale requires privacy-preserving gaze data processing mechanisms that maintain real-time performance while protecting sensitive biometric information.

8. **Expert vs Novice Differences**: Gaze patterns differ significantly between novice and expert users, potentially requiring separate models or adaptive mechanisms to accommodate different expertise levels.

9. **Limited Benchmark Datasets**: Few publicly available datasets combine high-quality medical images with expert radiologist gaze annotations suitable for training and evaluating bidirectional gaze-attention systems.

10. **Clinical Workflow Integration**: Seamless integration with existing Picture Archiving and Communication Systems (PACS) and clinical workflows remains a practical barrier to adoption despite technical feasibility.
