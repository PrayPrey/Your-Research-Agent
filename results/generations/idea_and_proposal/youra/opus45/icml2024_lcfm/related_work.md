## Related Work

**Related Papers**
1. **Title**: Mamba: Linear-Time Sequence Modeling with Selective State Spaces (arXiv:2312.00752)
   - **Authors**: Albert Gu, Tri Dao
   - **Summary**: Introduces selective state space models that achieve 5x throughput improvement with linear complexity, enabling content-based reasoning through input-dependent parameters.
   - **Year**: 2023

2. **Title**: VMamba: Visual State Space Model (arXiv:2401.10166)
   - **Authors**: Yue Liu et al.
   - **Summary**: Proposes 2D Selective Scan (SS2D) to bridge 1D SSM and 2D vision data, demonstrating the applicability of state space models to computer vision tasks.
   - **Year**: 2024

3. **Title**: Gated Linear Attention Transformers with Hardware-Efficient Training (arXiv:2312.06635)
   - **Authors**: Songlin Yang et al.
   - **Summary**: Demonstrates that linear attention can be competitive with LLaMA, achieving length generalization from 2K to 20K+ tokens while being faster than FlashAttention-2.
   - **Year**: 2023

4. **Title**: The Role of Temporal Hierarchy in Spiking Neural Networks (arXiv:2407.18838)
   - **Authors**: Filippo Moro et al.
   - **Summary**: Shows that hierarchy of time constants improves temporal task performance by 4.1% and that temporal hierarchy emerges during optimization.
   - **Year**: 2024

5. **Title**: TransMamba
   - **Authors**: Li et al.
   - **Summary**: Proposes fixed layer-level alternation between Transformer and Mamba architectures for hybrid sequence modeling.
   - **Year**: 2025

6. **Title**: Mamba-2-Hybrid
   - **Authors**: NVIDIA
   - **Summary**: Presents an 8B hybrid model that exceeds Transformer performance by +2.65 points, serving as a benchmark for efficiency-accuracy trade-offs.
   - **Year**: 2024

7. **Title**: LongBench v2
   - **Authors**: Bai et al.
   - **Summary**: Introduces challenging long-context evaluation tasks where human experts achieve only 53.7% accuracy, highlighting the difficulty of long-context understanding.
   - **Year**: 2024

8. **Title**: PyTorch SDPA / FlashAttention
   - **Authors**: Not specified
   - **Summary**: Provides implementation patterns demonstrating that kernel selection improves efficiency and supports hybrid mechanism approaches.
   - **Year**: Not specified

**Key Challenges**
1. **Arbitrary Hybrid Architecture Design**: Existing approaches like TransMamba use fixed layer-level alternation between Transformer and Mamba without principled allocation strategies for determining when each mechanism should be applied.

2. **Long-Context Understanding Limitations**: Current architectures struggle with challenging long-context tasks, as evidenced by human experts achieving only 53.7% on LongBench v2, demonstrating the need for better long-context architectures.

3. **Efficiency-Accuracy Trade-off**: Balancing computational efficiency with model accuracy remains challenging, requiring hybrid approaches that can leverage the strengths of both linear-complexity models and attention mechanisms.
