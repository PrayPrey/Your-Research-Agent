## Related Work

**Related Papers**
1. **Title**: Rigging the Lottery: Making All Tickets Winners (arXiv:1911.11134)
   - **Authors**: Evci et al.
   - **Summary**: Introduces dynamic sparse training (RigL) that matches dense network performance while maintaining sparsity throughout training, demonstrating that structural plasticity is viable for deep neural networks.
   - **Year**: 2019

2. **Title**: Top-KAST: Top-K Always Sparse Training (arXiv:2106.03517)
   - **Authors**: Jayakumar et al.
   - **Summary**: Proposes differentiable top-k sparse training with exploration loss that enables stable grow/prune operations at ImageNet scale.
   - **Year**: 2021

3. **Title**: Correcting Biased CKA Measures in Biological and Artificial Neural Networks (arXiv:2405.01012)
   - **Authors**: Murphy, Zylberberg, Fyshe
   - **Summary**: Demonstrates that debiased CKA is necessary for reliable alignment measurement in low-data regimes, as biased CKA produces spurious similarity results.
   - **Year**: 2024

4. **Title**: Human alignment of neural network representations (Semantic Scholar ID: 7ed0b9e3c058a0)
   - **Authors**: Muttenthaler et al.
   - **Summary**: Establishes that training objective matters more than architecture for human alignment, providing a baseline for loss-based intervention approaches.
   - **Year**: 2022

5. **Title**: RE-CONTROL representation editing
   - **Authors**: Not specified
   - **Summary**: Presents an alternative approach to alignment that edits representations rather than network structure, serving as a comparison point for different intervention paradigms.
   - **Year**: 2024

6. **Title**: Getting aligned on representational alignment
   - **Authors**: Sucholutsky et al.
   - **Summary**: Demonstrates that no unified intervention framework exists for controllable alignment in neural networks.
   - **Year**: 2023

**Key Challenges**
1. **Lack of Unified Intervention Framework**: No standardized framework exists for controllable alignment interventions, making systematic approaches to neural network alignment difficult.
2. **Systematic Intervention Methods**: Developing systematic methods for intervening in neural network representations remains a key open problem in the field.
3. **Reliable Alignment Measurement**: Standard CKA measures produce biased results in low-data regimes, requiring debiased alternatives for accurate alignment assessment.
4. **Structural vs. Loss-Based Interventions**: Existing approaches primarily focus on loss-based interventions or representation editing, leaving structural plasticity-based methods underexplored for alignment purposes.
