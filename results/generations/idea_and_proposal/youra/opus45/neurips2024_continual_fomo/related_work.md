## Related Work

**Related Papers**
1. **Title**: Learning Fast, Learning Slow: CLS-ER (arXiv:2201.12604)
   - **Authors**: Elahe Arani, Fahad Sarfraz, Bahram Zonooz
   - **Summary**: Proposes a dual-memory system combining short-term and semantic memory with episodic replay, achieving state-of-the-art continual learning performance and validating Complementary Learning Systems theory for neural networks.
   - **Year**: 2022

2. **Title**: CL-LoRA: Continual Low-Rank Adaptation (SS ID: ebec1faf19f194767b3ef226ee3b7c978bebda44)
   - **Authors**: Jiangpeng He, Zhihao Duan, F. Zhu
   - **Summary**: Introduces a dual-adapter architecture with task-shared and task-specific components using gradient reassignment for continual learning with low-rank adaptation.
   - **Year**: 2025

3. **Title**: LoRA⁻: Drift-Resistant Space (SS ID: 507ea86df158af2f07875ec79a8625136c8a3700)
   - **Authors**: Xuan Liu, Xiaobin Chang
   - **Summary**: Demonstrates that weight subtraction creates a drift-resistant space, achieving state-of-the-art performance for long task sequences in continual learning.
   - **Year**: 2025

4. **Title**: PIECE: Parameter Importance Estimation (SS ID: 803ae7f92170d9e874ec058613aa25ef488d3030)
   - **Authors**: Lingxiang Wang, Hainan Zhang, Zhiming Zheng
   - **Summary**: Proposes second-order normalization combining gradient and curvature information to identify critical parameters, finding that only 0.1% of parameters are essential.
   - **Year**: 2025

5. **Title**: ShareLoRA
   - **Authors**: Song et al.
   - **Summary**: Focuses on efficiency in LoRA-based continual learning, achieving 44-96% parameter reduction compared to standard approaches.
   - **Year**: 2024

6. **Title**: Recent Advances of FLM-based CL: A Survey (SS ID: eaac29467de2dd223d32cc3d3a77b637ef2bc4b3)
   - **Authors**: Yang et al.
   - **Summary**: Documents the fragmentation in the LoRA-based continual learning landscape and identifies that no unified framework currently exists for this domain.
   - **Year**: 2024

7. **Title**: Merge before Forget
   - **Authors**: Qiao et al.
   - **Summary**: Shows that orthogonal initialization enables sequential merging of adapters, though consolidation mechanisms remain unexplored.
   - **Year**: 2025

**Key Challenges**
1. **Fragmented LoRA-CL Landscape**: The field lacks a unified framework for LoRA-based continual learning, with existing methods addressing isolated aspects without integration.
2. **Dual-Adapter Limitations**: Current dual-adapter architectures like CL-LoRA lack consolidation mechanisms to transfer knowledge between task-specific and shared components.
3. **Drift-Resistance Without Importance Weighting**: Methods like LoRA⁻ achieve drift resistance through subtraction but do not incorporate parameter importance estimation for selective protection.
4. **Unexplored Consolidation Mechanisms**: While sequential merging through orthogonal initialization has been demonstrated, systematic consolidation strategies remain underexplored.
5. **Integration of Complementary Approaches**: Existing methods separately address memory systems, drift resistance, and parameter importance, but no approach unifies these complementary strategies.
