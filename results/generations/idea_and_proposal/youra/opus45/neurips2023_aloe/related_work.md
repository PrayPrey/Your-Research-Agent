## Related Work

**Related Papers**
1. **Title**: Emergent Complexity and Zero-shot Transfer via Unsupervised Environment Design (PAIRED)
   - **Authors**: Dennis, Jaques, Vinitsky, Bayen, Russell, Critch, Levine
   - **Summary**: Demonstrates that regret-based environment design produces natural curriculum and achieves higher zero-shot transfer performance. Establishes regret as a principled curriculum criterion.
   - **Year**: 2020

2. **Title**: Self-Improvement in Language Models: The Sharpening Mechanism
   - **Authors**: Huang, Block, Foster, Rohatgi, Zhang, Simchowitz, Ash, Krishnamurthy
   - **Summary**: Shows that LLMs are better at verification than generation, and that self-improvement sharpens the distribution toward quality outputs. Provides theoretical basis for using LLM confidence in curriculum selection.
   - **Year**: 2024

3. **Title**: Evolving Curricula with Regret-Based Environment Design (ACCEL)
   - **Authors**: Parker-Holder, Jiang, Dennis, Samvelyan, Foerster, Grefenstette, Rocktaschel
   - **Summary**: Demonstrates that evolutionary curriculum produces levels at the frontier of agent capability while maintaining theoretical benefits and improving empirical performance. Shows frontier-based selection enables complexity growth.
   - **Year**: 2022

4. **Title**: Self-Evolving Curriculum for LLM Reasoning
   - **Authors**: Chen et al.
   - **Summary**: Proposes using Multi-Armed Bandit for curriculum policy selection, outperforming random curriculum approaches. Selects curriculum by category rather than individual examples.
   - **Year**: 2025

5. **Title**: CORE-PO: Confident Reasoning Path Optimization
   - **Authors**: Jang et al.
   - **Summary**: Uses reasoning-level confidence for filtering correct reasoning paths, focusing on path filtering rather than curriculum selection for training.
   - **Year**: 2025

6. **Title**: EvaLearn: Quantifying Learning Capability and Efficiency of LLMs
   - **Authors**: Dou et al.
   - **Summary**: Demonstrates that LLMs show varied learning ability across tasks and that some exhibit negative transfer, highlighting the need for principled curriculum approaches.
   - **Year**: 2025

7. **Title**: Zone of Proximal Development
   - **Authors**: Vygotsky
   - **Summary**: Establishes that learning is most effective at the competence boundary when appropriate scaffolding is provided, a foundational concept in educational psychology.
   - **Year**: 1978

**Key Challenges**
1. **Lack of Principled Curriculum for LLM Self-Training**: Despite evidence that LLMs show varied learning abilities and can exhibit negative transfer, no principled curriculum approach for LLM self-training currently exists.
2. **ZPD Not Operationalized for LLM Training**: The Zone of Proximal Development concept, which identifies optimal learning at competence boundaries, has not been previously operationalized for LLM training contexts.
3. **Category-Level vs. Instance-Level Selection**: Existing curriculum methods like SEC select training examples by category rather than by individual example, potentially missing fine-grained optimization opportunities.
4. **Path Filtering vs. Curriculum Selection**: Current confidence-based approaches like CORE-PO focus on filtering which reasoning paths are correct rather than selecting which examples to train on.
