1. **Title**: gRNAde: Geometric Deep Learning for 3D RNA Inverse Design (arXiv:2305.14749)
   - **Authors**: Chaitanya K. Joshi, Arian R. Jamasb, Ramon Viñas, Charles Harris, Simon V. Mathis, Alex Morehead, Rishabh Anand, Pietro Liò
   - **Summary**: gRNAde introduces a geometric deep learning pipeline that operates on 3D RNA backbones to design sequences accounting for structure and dynamics. It employs a multi-state Graph Neural Network to generate RNA sequences conditioned on 3D structures, achieving higher native sequence recovery rates compared to traditional methods like Rosetta.
   - **Year**: 2023

2. **Title**: RDesign: Hierarchical Data-efficient Representation Learning for Tertiary Structure-based RNA Design (arXiv:2301.10774)
   - **Authors**: Cheng Tan, Yijie Zhang, Zhangyang Gao, Bozhen Hu, Siyuan Li, Zicheng Liu, Stan Z. Li
   - **Summary**: RDesign presents a hierarchical data-efficient representation learning framework for RNA design, leveraging contrastive learning at both cluster and sample levels to fully utilize limited data. It incorporates secondary structures with base pairs as prior knowledge, demonstrating effectiveness in RNA design tasks.
   - **Year**: 2023

3. **Title**: RiboGen: RNA Sequence and Structure Co-Generation with Equivariant MultiFlow (arXiv:2503.02058)
   - **Authors**: Dana Rubin, Allan dos Santos Costa, Manvitha Ponnapati, Joseph Jacobson
   - **Summary**: RiboGen introduces a deep learning model that simultaneously generates RNA sequences and all-atom 3D structures. It utilizes Euclidean Equivariant neural networks and combines Flow Matching with Discrete Flow Matching in a multimodal data representation, efficiently generating chemically plausible and self-consistent RNA samples.
   - **Year**: 2025

4. **Title**: Deep Learning Framework for RNA Inverse Folding with Geometric Structure Potentials (arXiv:2601.00895)
   - **Authors**: Annabelle Yao
   - **Summary**: This framework integrates Geometric Vector Perceptron layers with a Transformer architecture to enable end-to-end RNA design. It constructs a dataset of experimentally solved RNA 3D structures and achieves state-of-the-art performance in sequence recovery and structural fidelity across diverse RNA families.
   - **Year**: 2025

5. **Title**: Hierarchical Diffusion Models for Singing Voice Neural Vocoder (arXiv:2210.07508)
   - **Authors**: Naoya Takahashi, Mayank Kumar Singh, Yuki Mitsufuji
   - **Summary**: This paper proposes a hierarchical diffusion model consisting of multiple diffusion models operating at different sampling rates. The approach progressively generates data from low to high sampling rates, focusing on accurate low-frequency components and high-frequency details, resulting in high-quality singing voice generation.
   - **Year**: 2022

6. **Title**: Matryoshka Diffusion Models (arXiv:2310.15111)
   - **Authors**: Not specified
   - **Summary**: Matryoshka Diffusion Models introduce a multi-resolution diffusion process in an extended space, utilizing nested architectures and training procedures. This approach enables efficient high-resolution generation by exploiting the hierarchical structure of data formation.
   - **Year**: 2023

7. **Title**: BindGPT: A Scalable Framework for 3D Molecular Design via Language Modeling and Reinforcement Learning (arXiv:2406.03686)
   - **Authors**: Artem Zholus, Maksim Kuznetsov, Roman Schutski, Rim Shayakhmetov, Daniil Polykovskiy, Sarath Chandar, Alex Zhavoronkov
   - **Summary**: BindGPT presents a generative model that creates 3D molecules within a protein's binding site by producing molecular graphs and conformations jointly. It leverages language modeling and reinforcement learning, demonstrating competitive performance with existing diffusion models and graph neural networks.
   - **Year**: 2024

8. **Title**: Deep Generative Model and Its Applications in Efficient Wireless Network Management (arXiv:2303.17114)
   - **Authors**: Not specified
   - **Summary**: This paper discusses the applications of deep generative models, including diffusion models, in various fields such as wireless network management. It highlights the potential of these models in generating high-fidelity samples and their applicability beyond content generation.
   - **Year**: 2023

9. **Title**: Fast Timing-Conditioned Latent Audio Diffusion (arXiv:2402.04825)
   - **Authors**: Not specified
   - **Summary**: This work focuses on generating high-quality audio using latent diffusion models conditioned on timing information. It addresses challenges in generating variable-length, long-form audio efficiently, demonstrating advancements in audio synthesis.
   - **Year**: 2024

10. **Title**: Preprint. Under review. (arXiv:2406.03686)
    - **Authors**: Not specified
    - **Summary**: This preprint discusses a scalable framework for 3D molecular design using language modeling and reinforcement learning. It emphasizes the generation of 3D molecules within protein binding sites, highlighting the integration of generative models with reinforcement learning techniques.
    - **Year**: 2024

**Key Challenges**:

1. **Data Scarcity**: Limited availability of high-quality, experimentally validated RNA structures hampers the training of robust generative models.

2. **Complex Structure-Function Relationship**: Capturing the intricate relationship between RNA sequence, secondary/tertiary structure, and function remains a significant challenge.

3. **Multi-Scale Modeling**: Developing models that effectively integrate information across multiple scales—from base-pairing interactions to 3D conformations—is complex.

4. **Controllable Generation**: Enabling precise control over generated RNA properties, such as binding affinity and stability, requires advanced conditioning techniques.

5. **Experimental Validation**: Integrating computational predictions with wet-lab experiments for iterative model refinement is resource-intensive and technically demanding. 