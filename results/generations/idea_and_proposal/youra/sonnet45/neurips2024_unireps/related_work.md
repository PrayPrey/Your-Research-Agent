## Related Work

**Related Papers**

1. **Title**: The Platonic Representation Hypothesis (Huh et al., 2024)
   - **Authors**: Not specified
   - **Summary**: Establishes foundational framework demonstrating that AI model representations converge toward shared statistical model of reality across different domains and modalities.
   - **Year**: 2024

2. **Title**: Universality of Representation in Biological and Artificial Neural Networks (Hosseini et al., 2024)
   - **Authors**: Not specified
   - **Summary**: Provides empirical evidence for convergence universality between biological and artificial neural networks but lacks mechanistic explanation for why convergence occurs.
   - **Year**: 2024

3. **Title**: Deep Spiking Neural Networks with High Representation Similarity (Huang et al., 2023)
   - **Authors**: Not specified
   - **Summary**: Demonstrates that spiking neural networks (SNNs) achieve 6.6% higher bio-similarity to visual cortex compared to standard CNNs, establishing critical baseline for bio-plausible architectures.
   - **Year**: 2023

4. **Title**: Bio-Constraints for Training Stability (Oja et al., 2024)
   - **Authors**: Not specified
   - **Summary**: Uses Oja's rule based on Hebbian learning principles to achieve training stability in neural networks through bio-plausible local learning mechanisms.
   - **Year**: 2024

5. **Title**: Sparse Excitatory Networks (Stricker et al., 2024)
   - **Authors**: Not specified
   - **Summary**: Enforces Dale's law and sparse connectivity for bio-plausibility, achieving sparsity through architectural design rather than training objectives.
   - **Year**: 2024

6. **Title**: A Review of Neuroscience-Inspired Machine Learning (Ororbia et al., 2024)
   - **Authors**: Not specified
   - **Summary**: Comprehensive survey of bio-plausible credit assignment algorithms, providing implementation guidance for local learning mechanisms in machine learning systems.
   - **Year**: 2024

7. **Title**: Local Identifiability of Deep ReLU Neural Networks: the Theory (Bona-Pellissier et al., 2022)
   - **Authors**: Not specified
   - **Summary**: Provides mathematical foundation for identifiability in neural networks through static analysis of parameter recovery from function mappings.
   - **Year**: 2022

8. **Title**: Leveraging Task Structures for Improved Identifiability (Chen et al., 2023)
   - **Authors**: Not specified
   - **Summary**: Demonstrates that task distribution defines conditional prior that reduces equivalence classes, improving identifiability in multi-task learning settings.
   - **Year**: 2023

9. **Title**: An Empirically Grounded Identifiability Theory (Reizinger et al., 2025)
   - **Authors**: Not specified
   - **Summary**: Proposes Singular Identifiability Theory (SITh) to explain the Platonic Representation Hypothesis in self-supervised learning contexts.
   - **Year**: 2025

10. **Title**: Correcting Biased Centered Kernel Alignment Measures (Murphy et al., 2024)
    - **Authors**: Not specified
    - **Summary**: Develops debiased Centered Kernel Alignment (CKA) method for accurate similarity measurement in low-data high-dimensionality regimes, particularly for neural data comparisons.
    - **Year**: 2024

11. **Title**: MOMA: Masked Orthogonal Matrix Alignment (Kong et al., 2024)
    - **Authors**: Not specified
    - **Summary**: Addresses representation misalignment in model merging via orthogonal transformations, enabling better post-hoc alignment of neural network representations.
    - **Year**: 2024

12. **Title**: Multi-Task Model Fusion via Adaptive Merging (Chen et al., 2025)
    - **Authors**: Not specified
    - **Summary**: Uses representation bias as constraint for model fusion, enabling effective integration of models trained on diverse tasks.
    - **Year**: 2025

13. **Title**: Sparse Coding (Olshausen & Field, 1996)
    - **Authors**: Olshausen & Field
    - **Summary**: Foundational neuroscience work on sparse coding hypothesis, establishing principles of efficient neural representations in visual cortex.
    - **Year**: 1996

14. **Title**: Efficient Coding Hypothesis (Barlow, 1961; Simoncelli & Olshausen, 2001)
    - **Authors**: Barlow; Simoncelli & Olshausen
    - **Summary**: Establishes theoretical framework for efficient coding in biological sensory systems, proposing that sensory systems optimize information representation under resource constraints.
    - **Year**: 1961; 2001

15. **Title**: Centered Kernel Alignment (CKA) (Kornblith et al., 2019)
    - **Authors**: Kornblith et al.
    - **Summary**: Introduces Centered Kernel Alignment metric for measuring representational similarity between neural network layers and models.
    - **Year**: 2019

16. **Title**: Hebbian Learning (Hebb, 1949)
    - **Authors**: Hebb
    - **Summary**: Foundational work establishing principles of synaptic plasticity and local learning rules in biological neural systems.
    - **Year**: 1949

17. **Title**: Energy Efficiency in Biological Computation (Attwell & Laughlin, 2001; Lennie, 2003)
    - **Authors**: Attwell & Laughlin; Lennie
    - **Summary**: Examines metabolic constraints and energy efficiency principles in biological neural computation, particularly in visual cortex processing.
    - **Year**: 2001; 2003

18. **Title**: ImageNet Dataset (Deng et al., 2009)
    - **Authors**: Deng et al.
    - **Summary**: Large-scale visual recognition dataset containing 1.28M images across 1000 classes, standard benchmark for computer vision tasks.
    - **Year**: 2009

19. **Title**: THINGS fMRI Dataset (Hebart et al., 2019)
    - **Authors**: Hebart et al.
    - **Summary**: Neuroimaging dataset containing fMRI responses from human subjects (n=3) to 1854 natural images, enabling comparison between artificial and biological visual representations.
    - **Year**: 2019

20. **Title**: Allen Brain Observatory (de Vries et al., 2020)
    - **Authors**: de Vries et al.
    - **Summary**: Large-scale neural recording dataset from mouse visual cortex (V1), providing calcium imaging data for studying biological visual processing.
    - **Year**: 2020

21. **Title**: CNN-Cortex Correspondence (Yamins & DiCarlo, 2016)
    - **Authors**: Yamins & DiCarlo
    - **Summary**: Establishes correspondence between convolutional neural network layers and hierarchical visual cortex regions, providing framework for layer mapping in bio-artificial alignment studies.
    - **Year**: 2016

**Key Challenges**

1. **Bridging Biological and Artificial Representation Convergence**: Prior work (Hosseini et al. 2024, Huh et al. 2024) observes that convergence occurs between biological and artificial neural systems but lacks mechanistic explanation for WHY both domains converge to similar representations despite fundamentally different implementations.

2. **Static vs. Dynamic Identifiability Theory Gap**: Existing identifiability theory (Bona-Pellissier 2022, Chen 2023) addresses static representational analysis ("given data X, can we uniquely recover latent Z?"), while practical training requires understanding dynamic convergence ("will SGD training under constraints converge to unique Z?").

3. **Incomplete Bio-Constraint Sets**: Current bio-plausible methods focus on individual constraints (sparse coding in Stricker 2024, local learning in Oja 2024) rather than unified frameworks combining multiple biological constraints with theoretical grounding.

4. **Bio-Similarity Without Spiking Architecture**: Spiking neural networks (Huang et al. 2023) achieve superior bio-similarity but require specialized neuromorphic hardware. Challenge is to achieve comparable bio-similarity using standard architectures and auxiliary training objectives.

5. **Measurement Artifacts in Low-Sample Neural Data**: Standard CKA metrics exhibit sampling bias in neural data comparisons with small sample sizes (n=3 subjects typical in fMRI), requiring debiased methods (Murphy et al. 2024) for valid similarity measurements.

6. **Energy Metric Calibration Gap**: Biological systems optimize for ATP consumption while artificial systems measure FLOPs, creating challenge in establishing valid correspondence between biological metabolic efficiency and computational efficiency.

7. **Task Performance vs. Bio-Similarity Trade-off**: Bio-inspired constraints may reduce task performance (regularization effect), requiring careful balance to maintain practical utility while achieving bio-alignment.

8. **Limited Generalizability Across Domains**: Most bio-alignment work focuses on visual domain; unclear whether findings extend to language, audio, or reinforcement learning contexts with different biological computational principles.

9. **Layer-to-Cortex Mapping Complexity**: CNNs have discrete convolutional layers while visual cortex has complex 3D hierarchical structure, creating ambiguity in establishing precise correspondence for similarity measurements.

10. **Reproducibility Challenges**: Stochastic training processes (random initialization, data shuffling, augmentation) combined with small sample sizes in neural datasets create challenges for robust statistical validation and reproducibility.
