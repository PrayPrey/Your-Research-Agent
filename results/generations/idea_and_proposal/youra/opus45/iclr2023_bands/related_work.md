## Related Work

**Related Papers**
1. **Title**: Engineering Trustworthy Machine-Learning Operations with Zero-Knowledge Proofs (arXiv:2505.20136)
   - **Authors**: Scaramuzza et al.
   - **Summary**: Validates ZKP applicability to training process verification through the ZKMLOps framework, establishing foundations for trustworthy ML operations.
   - **Year**: 2025

2. **Title**: zkDL: Efficient Zero-Knowledge Proofs of Deep Learning Training (eprint:2023/1174)
   - **Authors**: Sun et al., University of Waterloo
   - **Summary**: Achieves efficient proof generation with less than 1 second per batch for models with 10 million parameters, demonstrating practical ZKP for deep learning training.
   - **Year**: 2023

3. **Title**: DSperse: A Framework for Targeted Verification in Zero-Knowledge ML (arXiv:2508.06972)
   - **Authors**: Ivanov et al.
   - **Summary**: Introduces strategic slice verification that avoids full-model circuitization costs, enabling more efficient targeted verification in zero-knowledge ML settings.
   - **Year**: 2025

4. **Title**: Spectral Signatures in Backdoor Attacks
   - **Authors**: Tran et al.
   - **Summary**: Demonstrates that backdoors create detectable statistical anomalies in layer representations, providing a foundation for spectral-based backdoor detection methods.
   - **Year**: 2018

5. **Title**: CRFL: Certifiably Robust Federated Learning (SS ID: db7991d7fda0)
   - **Authors**: Xie et al.
   - **Summary**: Proposes the first certified federated learning defense using clipping and smoothing techniques to provide output-level robustness bounds.
   - **Year**: 2021

6. **Title**: BagFlip: A Certified Defense against Data Poisoning (SS ID: e651e095f73c)
   - **Authors**: Zhang et al.
   - **Summary**: Provides model-agnostic certification against data poisoning attacks, though at significant computational expense.
   - **Year**: 2022

7. **Title**: Neural Cleanse: Identifying and Mitigating Backdoor Attacks (SS ID: 42658c812d60)
   - **Authors**: Wang et al.
   - **Summary**: Introduces trigger reverse engineering as a heuristic approach for detecting and mitigating backdoor attacks in neural networks.
   - **Year**: 2019

8. **Title**: On the Vulnerability of Backdoor Defenses for FL (SS ID: efaab402913d)
   - **Authors**: Fang et al.
   - **Summary**: Demonstrates that existing certified defenses in federated learning can be bypassed by adaptive attacks, revealing fundamental vulnerabilities.
   - **Year**: 2023

9. **Title**: FLIP: Provable Defense Framework for Backdoor Mitigation (SS ID: 20916aae7121)
   - **Authors**: Zhang et al.
   - **Summary**: Proposes a provable defense framework for backdoor mitigation, though with guarantees limited to fixed attack models.
   - **Year**: 2022

**Key Challenges**
1. **Vulnerability to Adaptive Attacks**: Existing certified defenses for federated learning can be bypassed by adaptive attacks, undermining their security guarantees.
2. **Limited Attack Model Coverage**: Provable defense frameworks provide guarantees only for fixed attack models, failing to generalize to novel or evolving threats.
3. **Computational Expense of Certification**: Model-agnostic certification approaches incur significant computational costs, limiting practical deployment.
4. **Heuristic Detection Limitations**: Current backdoor detection methods like trigger reverse engineering rely on heuristics rather than formal guarantees.
5. **Full-Model Circuitization Costs**: Zero-knowledge verification of entire models is computationally prohibitive, necessitating strategic or targeted verification approaches.
6. **Output-Level vs. Process-Level Guarantees**: Existing certified defenses provide only output-level bounds rather than verifying the integrity of the training process itself.
