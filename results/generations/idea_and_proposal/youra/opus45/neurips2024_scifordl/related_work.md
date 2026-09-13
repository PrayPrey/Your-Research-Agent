## Related Work

**Related Papers**
1. **Title**: Progress measures for grokking via mechanistic interpretability (arXiv:2023)
   - **Authors**: Nanda, Chan, Lieberum, Smith, Steinhardt
   - **Summary**: Demonstrates progress measures methodology for tracking circuit formation during training, providing a template for extending such measures to inference-time analysis.
   - **Year**: 2023

2. **Title**: Transformers as Statisticians: Provable In-Context Learning with In-Context Algorithm Selection
   - **Authors**: Bai, Chen, Wang, Xiong, Mei
   - **Summary**: Proves that transformers possess algorithm selection capability in in-context learning, serving as a primary theoretical prediction target for mechanistic validation.
   - **Year**: 2023

3. **Title**: Transformers learn to implement preconditioned gradient descent for in-context learning
   - **Authors**: Ahn, Cheng, Daneshmand, Sra
   - **Summary**: Proves that the global minimum of transformer training implements preconditioned gradient descent, providing specific circuit behavior predictions for in-context learning.
   - **Year**: 2023

4. **Title**: Data Distributional Properties Drive Emergent In-Context Learning in Transformers
   - **Authors**: Chan, Santoro, Lampinen, Wang, Singh, Richemond, McClelland, Hill
   - **Summary**: Demonstrates that in-context learning emergence is driven by data distribution properties, informing experimental design for studying ICL mechanisms.
   - **Year**: 2022

5. **Title**: Decoding In-Context Learning: Neuroscience-inspired Analysis of Representations in Large Language Models (arXiv:2310.00313)
   - **Authors**: Yousefi, Betthauser, Hasanbeig, Millière, Momennejad
   - **Summary**: Introduces representational similarity analysis (RSA) methodology for analyzing in-context learning, providing cross-domain inspiration from neuroscience.
   - **Year**: 2023

6. **Title**: Induction head formation circuits
   - **Authors**: Singh et al.
   - **Summary**: Investigates induction head formation circuits with a focus on copying behavior mechanisms in transformers.
   - **Year**: 2024

7. **Title**: Multi-phase circuit emergence
   - **Authors**: Minegishi et al.
   - **Summary**: Studies multi-phase circuit emergence with a focus on training dynamics rather than inference-time behavior.
   - **Year**: 2025

**Key Challenges**
1. **Missing ICL-Mechanistic Bridge**: Extensive theoretical work on in-context learning (Bai, Ahn) exists separately from extensive mechanistic interpretability work (Nanda), with no circuit-level validation connecting ICL theory to mechanistic understanding.

2. **Limited Progress Measures for Inference**: Existing progress measures, such as those developed for grokking, focus exclusively on training dynamics; no analogous measures exist for tracking algorithm selection during inference time.

3. **Focus on Training vs. Inference**: Current mechanistic studies primarily examine circuit formation during training rather than activation patterns during model use, leaving a gap in understanding inference-time algorithm selection mechanisms.

4. **Induction Head vs. Algorithm Selection**: Existing circuit analysis focuses on induction head copying behavior rather than post-ICL validation mechanisms and algorithm selection circuits.
