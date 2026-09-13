## Related Work

**Related Papers**
1. **Title**: A model of autonomous interactions between hippocampus and neocortex driving sleep-dependent memory consolidation (PNAS 119(44), e2123432119)
   - **Authors**: Singh, D., Norman, K. A., & Schapiro, A. C.
   - **Summary**: Proposes that NREM sleep creates tight hippocampal-neocortical coupling for memory replay while REM sleep allows free exploration, establishing a dual-phase consolidation architecture.
   - **Year**: 2022

2. **Title**: SYNAPSE: Empowering LLM Agents with Episodic-Semantic Memory via Spreading Activation (arXiv:2601.02744)
   - **Authors**: Jiang, Y., et al.
   - **Summary**: Demonstrates that spreading activation with lateral inhibition and temporal decay outperforms embedding-only retrieval for LLM memory systems, using triple hybrid retrieval mechanisms.
   - **Year**: 2026

3. **Title**: AriGraph: Learning Knowledge Graph World Models with Episodic Memory (NeurIPS 2024)
   - **Authors**: Anokhin, P., et al.
   - **Summary**: Shows that integrating episodic and semantic memory in a knowledge graph structure improves agent decision-making through hybrid graph representations.
   - **Year**: 2024

4. **Title**: Let Them Sleep: Sleep Cycle-Inspired Memory Consolidation for Language Model Agents (arXiv preprint)
   - **Authors**: McCrae, J., et al.
   - **Summary**: Proposes a sleep-cycle metaphor combined with LoRA fine-tuning for memory consolidation in language model agents.
   - **Year**: 2025

5. **Title**: Language Models Need Sleep (ICLR 2026 submission)
   - **Authors**: Not specified
   - **Summary**: Combines sleep metaphor with reinforcement learning dreaming and parameter updates for memory consolidation in language models.
   - **Year**: 2026

6. **Title**: Active Dreaming Memory
   - **Authors**: Vali, et al.
   - **Summary**: Proposes counterfactual verification during the consolidation process for memory management in agents.
   - **Year**: 2025

7. **Title**: RAG (Retrieval-Augmented Generation)
   - **Authors**: Not specified
   - **Summary**: Uses embedding similarity for memory retrieval without any consolidation mechanism.
   - **Year**: Not specified

8. **Title**: MemGPT
   - **Authors**: Not specified
   - **Summary**: Implements hierarchical paging for memory management with manual trigger-based consolidation.
   - **Year**: Not specified

**Key Challenges**
1. **Lack of Active Consolidation**: Existing systems like SYNAPSE and AriGraph focus on retrieval or passive memory storage without active consolidation mechanisms to strengthen important memories over time.

2. **Parameter Update Dependencies**: Approaches using LoRA fine-tuning or RL training loops (e.g., "Let Them Sleep", "Language Models Need Sleep") require gradient computation, risk catastrophic forgetting of base LLM knowledge, and demand GPU resources.

3. **Computational Overhead of Counterfactual Methods**: Counterfactual verification approaches for consolidation selection are computationally expensive compared to spreading activation dynamics.

4. **Manual Consolidation Triggers**: Systems like MemGPT rely on manual triggers for consolidation rather than automated, principled consolidation mechanisms.

5. **Limited Long-term Recall**: Pure retrieval-based systems (RAG) without consolidation suffer from degraded long-term recall performance.

6. **Interpretability of Memory Operations**: Parameter-based consolidation methods lack transparency compared to inspectable graph-based memory structures.
