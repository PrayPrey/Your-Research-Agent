## Related Work

**Related Papers**
1. **Title**: Advances and Open Problems in Federated Learning (arXiv:1912.04977)
   - **Authors**: Kairouz et al.
   - **Summary**: Foundational survey that established the privacy-utility-robustness tradeoff as a fundamental open problem in federated learning, accumulating over 7,730 citations.
   - **Year**: 2019

2. **Title**: Practical Differentially Private and Byzantine-resilient Federated Learning (DOI: 10.1145/3589264)
   - **Authors**: Xiang et al.
   - **Summary**: Demonstrated that differential privacy noise can be leveraged (not just tolerated) for Byzantine detection, achieving 90% Byzantine tolerance.
   - **Year**: 2023

3. **Title**: An Efficient Verifiable Aggregation Scheme with Privacy-Enhanced in Federated Learning (DOI: 10.1109/ICCC62609.2024.10942200)
   - **Authors**: Li et al.
   - **Summary**: Proposed commitment and masking techniques that enable verifiable computation without information leakage in federated learning.
   - **Year**: 2024

4. **Title**: SEAR: Secure and Efficient Aggregation for Byzantine-Robust Federated Learning (DOI: 10.1109/TDSC.2021.3093711)
   - **Authors**: Zhao et al.
   - **Summary**: Developed SGX-based Byzantine detection with sampling that achieves 4-6× efficiency improvement over prior methods.
   - **Year**: 2022

5. **Title**: ABD-HFL: Byzantine-resistant Decentralized Hierarchical FL (HAL: hal-04627430)
   - **Authors**: Not specified
   - **Summary**: Demonstrated that hierarchical structure can achieve 49% Byzantine tolerance with O(log n) complexity without differential privacy.
   - **Year**: 2024

6. **Title**: Blades: A Unified Benchmark Suite for Byzantine Attacks and Defenses (arXiv:2206.05359)
   - **Authors**: Li et al.
   - **Summary**: Provided a comprehensive benchmark with approximately 1500 trials and a standardized evaluation framework for Byzantine attacks and defenses.
   - **Year**: 2023

7. **Title**: Adaptive and Privacy-Preserving Security for FL Using Biological Immune System Principles
   - **Authors**: Olarinde et al.
   - **Summary**: Showed that immune system mechanisms including anomaly detection and dynamic response can be applied to federated learning security.
   - **Year**: 2024

8. **Title**: Human Immune System Inspired Security for FL-Empowered IoT (DOI: 10.1145/3722562)
   - **Authors**: Uprety et al.
   - **Summary**: Proposed B-cell analogy for detecting malicious nodes via reinforcement learning and immune memory for threat tracking in IoT federated learning.
   - **Year**: 2025

**Key Challenges**
1. **Privacy-Utility-Robustness Tradeoff**: Achieving simultaneous privacy guarantees, model utility, and Byzantine robustness remains a fundamental open problem in federated learning.

2. **Byzantine Detection Without Privacy Leakage**: Existing Byzantine-robust methods often require access to raw model updates, compromising client privacy during the detection process.

3. **Scalability of Byzantine Defenses**: Many Byzantine-resilient approaches suffer from high computational complexity, limiting their applicability to large-scale federated systems.

4. **Integration of Differential Privacy with Byzantine Resilience**: Bio-inspired security approaches for federated learning have shown promise but lack integration with differential privacy mechanisms.

5. **Verifiable Computation Under Privacy Constraints**: Enabling servers to verify client computations without accessing sensitive information remains technically challenging.
