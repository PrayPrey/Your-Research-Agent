## Related Work

**Related Papers**
1. **Title**: Machine Unlearning using Forgetting Neural Networks (arXiv:2410.22374)
   - **Authors**: Hatua, Nguyen, Cano, Sung
   - **Summary**: Demonstrates that multiplicative decay factors with per-neuron forgetting rates achieve targeted unlearning on MNIST/Fashion-MNIST datasets, with MIA confirming effectiveness.
   - **Year**: 2024

2. **Title**: FadeMem: Biologically-Inspired Forgetting for Efficient Agent Memory (arXiv:2601.18642)
   - **Authors**: Wei et al.
   - **Summary**: Proposes differential decay rates across memory hierarchy with semantic relevance modulation, achieving 45% storage reduction while preserving retrieval quality.
   - **Year**: 2026

3. **Title**: LoRA: Low-Rank Adaptation of Large Language Models
   - **Authors**: Hu et al.
   - **Summary**: Introduces low-rank adapter matrices that capture task-specific knowledge efficiently, establishing the foundation for the parameter-efficient fine-tuning (PEFT) ecosystem.
   - **Year**: 2021

4. **Title**: MIAU: Membership Inference Attack Unlearning Score
   - **Authors**: Not specified
   - **Summary**: Proposes a principled metric comparing unlearned model behavior to retrained baseline with normalized scoring for interpretable evaluation of unlearning effectiveness.
   - **Year**: 2025

5. **Title**: LUNE
   - **Authors**: Not specified
   - **Summary**: Implements LoRA-based unlearning via fine-tuning as a post-hoc approach to machine unlearning.
   - **Year**: 2025

6. **Title**: AdapterSwap
   - **Authors**: Not specified
   - **Summary**: Proposes adapter removal as a mechanism for unlearning, though it lacks verification guarantees.
   - **Year**: 2024

7. **Title**: A Survey on Machine Unlearning
   - **Authors**: Liu et al.
   - **Summary**: Comprehensive survey noting that LLM unlearning remains an open challenge and that SISA-based approaches do not scale effectively.
   - **Year**: 2024

8. **Title**: Statistical MIA
   - **Authors**: Sun et al.
   - **Summary**: Presents a training-free MIA framework and demonstrates that existing MIA-based auditing approaches have statistical limitations.
   - **Year**: 2026

**Key Challenges**
1. **LLM Unlearning Scalability**: Current approaches like SISA do not scale effectively to large language models, leaving LLM unlearning as an open challenge.
2. **Verification Guarantees**: Existing methods such as AdapterSwap lack robust verification guarantees to confirm that unlearning has been successfully achieved.
3. **Statistical Limitations of MIA-based Auditing**: Current membership inference attack-based auditing methods have inherent statistical limitations that affect their reliability for evaluating unlearning.
4. **Post-hoc Nature of Existing Approaches**: Methods like LUNE operate as post-hoc solutions rather than integrated unlearning mechanisms, potentially limiting their effectiveness and efficiency.
