1. **Title**: Unifying Attention Heads and Task Vectors via Hidden State Geometry in In-Context Learning (arXiv:2505.18752)
   - **Authors**: Haolin Yang, Hakaze Cho, Yiqiao Zhong, Naoya Inoue
   - **Summary**: This paper investigates the internal mechanisms of in-context learning (ICL) by analyzing the geometric properties of hidden state representations. The authors identify a two-stage process where separability emerges in early layers and alignment develops in later layers, driven by specific attention heads and task vectors.
   - **Year**: 2025

2. **Title**: Instant Policy: In-Context Imitation Learning via Graph Diffusion (arXiv:2411.12633)
   - **Authors**: Vitalis Vosylius, Edward Johns
   - **Summary**: The authors introduce "Instant Policy," a framework that enables robots to learn new tasks instantly from minimal demonstrations. By modeling in-context imitation learning as a graph generation problem with a learned diffusion process, the approach allows for structured reasoning over demonstrations, observations, and actions.
   - **Year**: 2024

3. **Title**: Leveraging In-Context Learning for Language Model Agents (arXiv:2506.13109)
   - **Authors**: Shivanshu Gupta, Sameer Singh, Ashish Sabharwal, Tushar Khot, Ben Bogin
   - **Summary**: This study explores the application of in-context learning (ICL) to agentic tasks requiring sequential decision-making. The authors propose an algorithm that uses large language models with retries and demonstrations to annotate agentic tasks, improving performance, reliability, robustness, and efficiency of language model agents.
   - **Year**: 2025

4. **Title**: On the Relationship Between the Choice of Representation and In-Context Learning (arXiv:2510.08372)
   - **Authors**: Ioana Marinescu, Kyunghyun Cho, Eric Karl Oermann
   - **Summary**: This paper examines how the representation of in-context demonstrations affects in-context learning (ICL) performance. The authors find that while the choice of representation sets a baseline accuracy, learning from additional demonstrations improves performance, and these two aspects are largely independent.
   - **Year**: 2025

5. **Title**: A Simple Generalisation of the Implicit Dynamics of In-Context Learning (arXiv:2512.11255)
   - **Authors**: [Authors not specified]
   - **Summary**: The authors generalize previous findings on the implicit weight-update mechanisms in in-context learning (ICL) to all sequence positions, transformer blocks, and architectures with skip connections and layer normalization. They empirically verify their theory on in-context linear regression tasks, bringing the theory closer to practical large-scale models.
   - **Year**: 2025

6. **Title**: Density Estimation with LLMs: A Geometric Investigation of In-Context Learning Trajectories
   - **Authors**: Toni J. B. Liu, Nicolas Boullé, Raphaël Sarfati, Christopher J. Earls
   - **Summary**: This work investigates large language models' (LLMs) ability to estimate probability density functions from in-context data. Using Intensive Principal Component Analysis (InPCA), the authors visualize and analyze the in-context learning dynamics of LLaMA-2 models, revealing that LLMs follow similar learning trajectories distinct from traditional density estimation methods.
   - **Year**: 2024

7. **Title**: From Memories to Maps: Mechanisms of In-Context Reinforcement Learning in Transformers (arXiv:2506.19686)
   - **Authors**: [Authors not specified]
   - **Summary**: This study explores how episodic memory enables rapid in-context reinforcement learning in transformers. By training decision-pretrained transformers on planning tasks, the authors show that rapid adaptation arises from memory-based computations stored in context-memory tokens, with representations exhibiting in-context structure learning and cross-context alignment.
   - **Year**: 2025

8. **Title**: ICLR: In-Context Learning of Representations (arXiv:2501.00070)
   - **Authors**: [Authors not specified]
   - **Summary**: The authors investigate whether in-context exemplars can override pretrained semantic structures in large language models. They present a graph-tracing task and demonstrate that with sufficient in-context examples, representations reorganize to reflect the graph structure, suggesting that scaling context can unlock novel, context-specified representations and capabilities in LLMs.
   - **Year**: 2024

9. **Title**: In-Context Reinforcement Learning via Communicative World Models
   - **Authors**: Fernando Martinez, Tao Li, Yingdong Lu, Juntao Chen
   - **Summary**: This work formulates in-context reinforcement learning (ICRL) as a two-agent emergent communication problem. The authors introduce CORAL (Communicative Representation for Adaptive RL), a framework that learns a transferable communicative context by decoupling latent representation learning from control, enhancing agents' ability to generalize to new tasks and contexts without parameter updates.
   - **Year**: 2025

10. **Title**: Mimic In-Context Learning for Multimodal Tasks (arXiv:2504.08851)
    - **Authors**: Yuchu Jiang, Jiale Fu, Chenduo Hao, Xinting Hu, Yingzhe Peng, Xin Geng, Xu Yang
    - **Summary**: The authors propose "Mimic In-Context Learning" (MimIC) to enhance in-context learning (ICL) performance in large multimodal models. By learning stable and generalizable shift effects from in-context demonstrations, MimIC aims to improve the robustness and generalization of ICL across various multimodal tasks.
    - **Year**: 2025

**Key Challenges:**

1. **Understanding Representation Dynamics**: Deciphering how hidden representations evolve during in-context learning (ICL) remains complex, particularly in identifying the mechanisms that lead to successful task adaptation.

2. **Example Selection Strategies**: Determining which in-context examples are most effective for ICL is challenging, as the optimal selection can significantly influence learning outcomes.

3. **Generalization Across Tasks**: Ensuring that models can generalize ICL capabilities across diverse tasks without extensive retraining is a significant hurdle.

4. **Theoretical Grounding**: Establishing a solid theoretical framework that explains the emergent capabilities observed in ICL is still an open area of research.

5. **Practical Prompt Engineering**: Developing principled methods for prompt design that consistently yield high ICL performance is a non-trivial task requiring further exploration. 