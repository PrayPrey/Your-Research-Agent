## Related Work

**Related Papers**
1. **Title**: Energy Transformer (arXiv:2302.07253)
   - **Authors**: Hoover, Liang, Pham, Panda, Strobelt, Chau, Zaki, Krotov
   - **Summary**: Establishes the connection between attention mechanisms and energy functions via Hopfield networks, demonstrating that the forward pass can be interpreted as gradient descent on an energy function.
   - **Year**: 2023

2. **Title**: Beyond Scaling Laws: Understanding Transformer Performance with Associative Memory (arXiv:2405.08707)
   - **Authors**: Niu, Bai, Deng, Han
   - **Summary**: Models Transformers using Hopfield networks, showing that a temperature parameter controls memory capacity and that energy functions can explain attention behavior.
   - **Year**: 2024

3. **Title**: Entropy-Lens: Uncovering Decision Strategies in LLMs (arXiv:2502.16570)
   - **Authors**: Ali, Caso, Irwin, Liò
   - **Summary**: Uses entropy profiles to uncover layer-wise token prediction dynamics, revealing family-specific entropy trajectories and demonstrating that entropy patterns are characteristic of task types.
   - **Year**: 2025

4. **Title**: Attention Is All You Need
   - **Authors**: Vaswani et al.
   - **Summary**: Introduces the original Transformer architecture with the √d_k scaling factor chosen empirically for gradient stability, which forms the foundation for thermodynamic interpretations of this design choice.
   - **Year**: 2017

5. **Title**: PDE-Transformer
   - **Authors**: Zhang
   - **Summary**: Demonstrates that physics-based interpretation of Transformers is viable through a reaction-diffusion PDE perspective.
   - **Year**: 2025

6. **Title**: Attention Entropy methodology
   - **Authors**: Soni
   - **Summary**: Demonstrates that entropy collapse in attention mechanisms causes training instability.
   - **Year**: 2024

**Key Challenges**
1. **Lack of Thermodynamic Framework**: Existing work on attention entropy identifies instability issues but does not connect these observations to a thermodynamic framework involving temperature.
2. **Dynamical vs. Thermodynamic Perspectives**: Current physics-based interpretations of Transformers (e.g., PDE-Transformer) adopt dynamical perspectives rather than thermodynamic ones, leaving a gap in understanding temperature-based phenomena.
3. **Empirical Design Choices Without Theoretical Justification**: The √d_k scaling in the original Transformer was chosen empirically for gradient stability, lacking a principled theoretical foundation.
4. **Architecture Redesign vs. Interpretation**: Existing energy-based approaches (e.g., Energy Transformer) focus on designing new architectures rather than providing thermodynamic interpretations of existing Transformer mechanisms.
