## Related Work

**Related Papers**
1. **Title**: An active inference model of hierarchical action understanding, learning and imitation
   - **Authors**: Proietti, Pezzulo, Tessari
   - **Summary**: Demonstrates that hierarchical active inference provides a unified account of action observation, understanding, learning and imitation through predictive processing, with oculomotor active sampling supporting kinematic inference.
   - **Year**: 2021

2. **Title**: ASNets: Deep Learning for Generalised Planning
   - **Authors**: Toyer, Thiébaux, Trevizan, Xie
   - **Summary**: Shows that neural network architectures exploiting PDDL relational structure can learn generalizable policies that transfer across problem instances within a domain.
   - **Year**: 2020

3. **Title**: Metagent-P: A Neuro-Symbolic Planning Agent with Metacognition
   - **Authors**: Zhou et al.
   - **Summary**: Demonstrates that neural-symbolic hierarchical representation enables 34% fewer replanning episodes and validates that combining LLM knowledge with symbolic reasoning achieves human-level planning performance.
   - **Year**: 2025

4. **Title**: JARVIS: Neuro-Symbolic Reasoning for Embodied Agents
   - **Authors**: Zheng et al.
   - **Summary**: Uses pretrained LLM knowledge for symbolic reasoning in embodied agents.
   - **Year**: 2022

5. **Title**: NeSyPr: Neurosymbolic Proceduralization
   - **Authors**: Choi et al.
   - **Summary**: Approaches neurosymbolic planning but requires symbolic tools at compile time rather than learning from raw experience traces.
   - **Year**: 2025

6. **Title**: RePReL: Integrating Relational Planning and RL
   - **Authors**: Kokel et al.
   - **Summary**: Shows that relational state abstractions enable transfer in planning, though the action space remains fixed.
   - **Year**: 2021

7. **Title**: Learning Neural Search Policies for Classical Planning
   - **Authors**: Gomoluch et al.
   - **Summary**: Demonstrates that neural policies can guide classical planning, establishing the feasibility of neural-classical integration.
   - **Year**: 2021

**Key Challenges**
1. **Fixed Action Space Limitation**: Existing approaches like RePReL enable transfer through relational state abstractions but maintain a fixed action space, limiting adaptability to new domains.
2. **Compile-Time Symbolic Dependency**: Methods such as NeSyPr require symbolic tools at compile time rather than learning domain models from raw experience traces.
3. **Reliance on Pretrained Knowledge**: Approaches like JARVIS depend on pretrained LLM knowledge for symbolic reasoning rather than learning domain models directly from experience.
4. **Gap Between Neural and Symbolic Integration**: While neural policies can guide classical planning, achieving seamless integration that learns from raw experience while maintaining symbolic reasoning capabilities remains challenging.
