## Related Work

**Related Papers**

1. **Title**: SAFEFLOW: A Principled Protocol for Trustworthy and Transactional Autonomous Agent Systems
   - **Authors**: Peiran Li, Xinkai Zou, et al.
   - **Summary**: Information flow control (IFC) with transactional execution enables reliable multi-agent coordination; workflow-based composition prevents circular dependencies and validates that safety mechanisms can coordinate through centralized substrate.
   - **Year**: 2025

2. **Title**: Privacy-preserving Prompt Personalization in Federated Learning for Multimodal Large Language Models (SecFPP)
   - **Authors**: Sizai Hou, Songze Li, Baturalp Buyukates
   - **Summary**: Secret-sharing-based adaptive clustering achieves formal privacy guarantees with hierarchical adaptation (domain-level + class-level); demonstrates formal provability for multi-granular coordination.
   - **Year**: 2025

3. **Title**: ShieldAgent: Shielding Agents via Verifiable Safety Policy Reasoning
   - **Authors**: Zhaorun Chen, Mintong Kang, Bo Li
   - **Summary**: Probabilistic rule circuits with multi-layer defense-in-depth achieve 90.1% recall; provides formal verification of safety policy compliance and validates that multi-layer safety architectures prevent cascading failures.
   - **Year**: 2025

4. **Title**: Unified Multimodal Understanding and Generation Models: Advances, Challenges, and Opportunities
   - **Authors**: Xinjie Zhang, Jintao Guo, Shanshan Zhao, et al.
   - **Summary**: Survey of unified multimodal architectures (diffusion-based, autoregressive, hybrid); demonstrates cross-component coordination feasibility at scale and validates standardized interface assumptions.
   - **Year**: 2025

5. **Title**: Designing for Meaningful Oversight: Human and Organisational Agency in Multimodal AI Systems
   - **Authors**: Liming Zhu
   - **Summary**: Capability-based governance framework for meaningful human oversight; demonstrates that oversight mechanisms can be systematized for agentic AI systems.
   - **Year**: 2025

6. **Title**: Trustworthy Orchestration AI with Control-Plane Governance
   - **Authors**: Kang et al.
   - **Summary**: Control plane for AI governance focusing on audit trails, provenance tracking, and semantic coherence for post-hoc analysis and compliance.
   - **Year**: 2025

7. **Title**: Enterprise Agentic Architecture Framework
   - **Authors**: Venkiteela
   - **Summary**: Control plane for agent lifecycle management including orchestration, policy management, and observability for operational management.
   - **Year**: 2026

8. **Title**: AI Safety in Generative AI Large Language Models: A Survey
   - **Authors**: Jaymari Chua, Yun Li, et al.
   - **Summary**: Comprehensive survey identifying dimension-specific safety approaches but finding no cross-dimension coordination mechanisms, validating the research gap.
   - **Year**: 2024

9. **Title**: Trustworthy AI: Safety, Bias, and Privacy -- A Survey
   - **Authors**: Xingli Fang, Jianwei Li, et al.
   - **Summary**: Establishes trustworthiness requirements including safety alignment, bias mitigation, and privacy across dimensions; informs safety orchestrator conflict resolution policy.
   - **Year**: 2025

10. **Title**: MetaTransformer (GitHub Implementation)
    - **Authors**: invictus717 (GitHub repository)
    - **Summary**: Unified architecture for multiple modalities (Image, Audio, Hyper-spectrum, Graph) demonstrating substrate-level coordination architectural pattern; validates that unified abstractions enable cross-component functionality at scale.
    - **Year**: Not specified

11. **Title**: ShieldGemma 2 (Referenced Implementation)
    - **Authors**: Not specified
    - **Summary**: Multimodal Integrity Validator used as dimension-specific safety mechanism for multimodal perception safety.
    - **Year**: Not specified

**Key Challenges**

1. **Cross-Dimension Safety Gaps**: Current safety approaches are dimension-isolated (multimodal, agentic, edge) with no coordination mechanisms, creating safety gaps at dimension boundaries where individual dimensions appear safe but combinations are unsafe.

2. **Error Propagation Risk**: Substrate-level coordination could amplify errors if a failed dimension-specific mechanism propagates incorrect safety constraints to all dependent dimensions via the safety coordination layer, potentially making safety worse than isolated approaches.

3. **Compositional Complexity**: Safety constraints may lack compositional structure, leading to exponential complexity in propagation and limiting scalability beyond 2-3 dimensions without formal guarantees.

4. **Coordination Overhead**: AI safety involves stateful semantic reasoning (more expensive than SDN's stateless packet forwarding), requiring validation that substrate overhead remains under 15% to justify deployment.

5. **Standardized Interface Design**: Heterogeneous dimension-specific mechanisms (multimodal, agentic, edge) require significant engineering effort to expose standardized API contracts for constraint exchange and propagation.

6. **Formal Verification Scalability**: Extending formal verification methods from single-domain settings to multi-dimension compositional settings may prove intractable, limiting trustworthiness for safety-critical deployment.

7. **Adversarial Test Suite Coverage**: Existing adversarial test suites may not cover all possible cross-dimension attack vectors targeting dimension boundaries, limiting validation comprehensiveness.

8. **Real-Time Latency Requirements**: Safety coordination requires <100ms constraint propagation latency for real-time operation, which is challenging for stateful semantic reasoning across heterogeneous dimensions.
