## Related Work

**Related Papers**
1. **Title**: Sparse Plus Low Rank Matrix Decomposition: A Discrete Optimization Approach
   - **Authors**: Bertsimas, Cory-Wright, Johnson
   - **Summary**: Demonstrates that alternating minimization provides high-quality solutions for sparse+low-rank decomposition problems, with semidefinite relaxation bounds for solution quality.
   - **Year**: 2023

2. **Title**: HASSLE-free: A unified Framework for Sparse plus Low-Rank Matrix Decomposition for LLMs
   - **Authors**: Makni et al.
   - **Summary**: Proposes a layer-wise reconstruction error objective for sparse plus low-rank decomposition in large language models, achieving 12% perplexity reduction for LLaMA-3-8B.
   - **Year**: 2025

3. **Title**: Bernoulli-LoRA: A Theoretical Framework for Randomized Low-Rank Adaptation
   - **Authors**: Sokolov et al.
   - **Summary**: Establishes convergence guarantees for multiple LoRA optimization variants including gradient descent, SGD, PAGE, MVR, QGD, MARINA, and EF21.
   - **Year**: 2025

4. **Title**: Dynamic Low-Rank Sparse Adaptation (LoSA)
   - **Authors**: Huang et al.
   - **Summary**: Introduces RMI-based layer importance metrics for dynamic rank adjustment, achieving 68.73 perplexity reduction on LLaMA-2-7B.
   - **Year**: 2025

5. **Title**: Understanding Learning Dynamics of LoRA
   - **Authors**: Xu et al.
   - **Summary**: Provides gradient flow analysis with spectral initialization strategies for improved convergence in low-rank adaptation methods.
   - **Year**: 2025

6. **Title**: RoseLoRA
   - **Authors**: Not specified
   - **Summary**: Focuses on row and column-wise sparse low-rank adaptation, emphasizing within-layer sparsity patterns.
   - **Year**: Not specified

7. **Title**: SaRA
   - **Authors**: Not specified
   - **Summary**: Employs nuclear-norm relaxation for progressive sparse low-rank adaptation in neural networks.
   - **Year**: Not specified

8. **Title**: HuggingFace PEFT Library
   - **Authors**: Not specified
   - **Summary**: Provides implementations of multiple parameter-efficient fine-tuning methods but lacks unified selection criteria for choosing between sparse and low-rank approaches.
   - **Year**: Not specified

**Key Challenges**
1. **Lack of Unified Selection Criteria**: Existing PEFT libraries offer multiple methods (sparse, low-rank) but provide no principled framework for selecting between them based on task or model characteristics.

2. **Debugging Difficulty for Practitioners**: Community discussions reveal that practitioners struggle to debug LoRA implementations, with no systematic methods available for diagnosing allocation issues.

3. **Heuristic-Based Layer Importance**: Current approaches like LoSA rely on heuristic metrics (RMI) for layer importance rather than theoretically grounded allocation strategies.

4. **Absence of Systematic Allocation Methods**: No existing work provides systematic methods for determining optimal parameter allocation across layers for sparse versus low-rank components.
