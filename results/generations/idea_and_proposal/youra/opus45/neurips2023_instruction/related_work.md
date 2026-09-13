## Related Work

**Related Papers**
1. **Title**: Least-to-Most Prompting Enables Complex Reasoning in Large Language Models (arXiv:2205.10625)
   - **Authors**: Zhou et al.
   - **Summary**: Demonstrates that decomposition via prompting achieves 99% accuracy on SCAN with 14 exemplars compared to 16% with Chain-of-Thought, proving that decomposition-based approaches are effective for compositional generalization.
   - **Year**: 2022

2. **Title**: Chain-of-Instructions: Compositional Instruction Tuning on Large Language Models (arXiv:2402.11532)
   - **Authors**: Hayati et al.
   - **Summary**: Shows that training on chained instructions improves generalization to unseen instruction chains, representing a related approach that focuses on output supervision rather than representation supervision.
   - **Year**: 2024

3. **Title**: A Theoretical Analysis of Compositional Generalization in Neural Networks (arXiv:2505.02627)
   - **Authors**: Li
   - **Summary**: Provides theoretical foundation establishing that computational graphs must match compositional structure as a necessary and sufficient condition for compositional generalization.
   - **Year**: 2025

4. **Title**: Motor-Evoked Potentials for Early Individual Elements of an Action Sequence During Planning
   - **Authors**: Behmer, Crump, Jantzen
   - **Summary**: Identifies graded activation patterns during action planning through a competitive queuing mechanism, providing cross-domain inspiration for hierarchical activation supervision approaches.
   - **Year**: 2023

5. **Title**: FLAN: Finetuned Language Models Are Zero-Shot Learners
   - **Authors**: Wei et al.
   - **Summary**: Establishes that instruction tuning enables zero-shot generalization, providing the foundational paradigm upon which representation-level supervision approaches can build.
   - **Year**: 2021

6. **Title**: CompoST Benchmark
   - **Authors**: Schmidt et al.
   - **Summary**: Demonstrates that LLMs struggle with compositional interpretation, with F1 scores degrading from 0.45 to 0.09 as compositional complexity increases.
   - **Year**: 2025

**Key Challenges**
1. **Decomposition as Training Objective Gap**: The intersection of decomposition mechanisms and training objectives remains underexplored, with most work focusing on either inference-time decomposition or standard output supervision.
2. **Compositional Complexity Degradation**: Current LLMs show severe performance degradation on compositional tasks as complexity increases, with F1 scores dropping dramatically.
3. **Inference-Time Dependency**: Best-performing approaches like Least-to-Most prompting require explicit decomposition prompts at inference time rather than learning compositional structure during training.
4. **Output vs. Representation Supervision**: Existing instruction tuning methods supervise outputs rather than internal representations, potentially missing opportunities to enforce compositional structure in learned representations.
