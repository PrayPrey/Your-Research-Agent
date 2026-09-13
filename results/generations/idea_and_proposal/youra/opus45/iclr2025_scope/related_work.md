## Related Work

**Related Papers**
1. **Title**: FSC-Net: Fast-Slow Consolidation Networks for Continual Learning (arXiv:2511.11707)
   - **Authors**: El Gorrim
   - **Summary**: Demonstrates that dual-timescale consolidation achieves +4.27pp retention gain, showing that methodology matters more than architecture complexity for continual learning.
   - **Year**: 2025

2. **Title**: PEARL: Parameter Efficient Continual Learning with Dynamic Low-Rank Adaptation (Semantic Scholar ID: 8d6089586595)
   - **Authors**: Bhat et al.
   - **Summary**: Proposes dynamic rank allocation based on task proximity to improve continual learning performance.
   - **Year**: 2025

3. **Title**: Entropy-Lens: Uncovering Decision Strategies in LLMs (arXiv:2502.16570)
   - **Authors**: Ali et al.
   - **Summary**: Reveals that attention entropy can uncover computational strategies and decision-making patterns in large language models, validating attention entropy as a complexity measure.
   - **Year**: 2025

4. **Title**: C-LoRA: Continual Low-Rank Adaptation
   - **Authors**: Zhang et al.
   - **Summary**: Introduces orthogonality constraints to prevent interference between tasks in continual learning with low-rank adaptation.
   - **Year**: 2025

5. **Title**: CL-LoRA: Continual Low-Rank Adaptation
   - **Authors**: He et al.
   - **Summary**: Proposes a dual-adapter architecture with task-shared and task-specific components for continual learning.
   - **Year**: 2025

6. **Title**: Attention Entropy is a Key Factor
   - **Authors**: Zhang et al.
   - **Summary**: Demonstrates that attention entropy affects parallel context encoding performance, validating entropy as a key factor for adapter routing decisions.
   - **Year**: 2025

7. **Title**: ChunkKV: Semantic-Preserving KV Cache Compression
   - **Authors**: Liu et al.
   - **Summary**: Shows that semantic density varies across inputs, supporting the concept of complexity-based resource allocation.
   - **Year**: 2025

**Key Challenges**
1. **Static Resource Allocation**: Existing approaches like PEARL allocate resources based on task-level proximity rather than adapting to per-input context complexity.
2. **Lack of Consolidation in Dual-Adapter Methods**: Current dual-adapter architectures (e.g., CL-LoRA) separate task-shared and task-specific components but do not incorporate consolidation mechanisms.
3. **Complexity-Aware Routing**: Prior work validates attention entropy as a meaningful signal, but integrating it for dynamic adapter routing in continual learning remains unexplored.
4. **Balancing Retention and Adaptation**: Achieving knowledge retention while enabling adaptation to new tasks requires mechanisms beyond simple orthogonality constraints.
