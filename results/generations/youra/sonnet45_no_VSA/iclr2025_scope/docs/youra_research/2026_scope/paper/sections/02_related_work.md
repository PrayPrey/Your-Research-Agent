# Related Work

Our work builds on reproducibility measurement in ML systems and property-based testing methodologies, applying behavioral validation specifically to the ML API layer. We position our contributions relative to four research areas.

## Reproducibility Measurement and Challenges

Recent empirical studies have quantified reproducibility gaps in ML research. Jiang et al. [1] analyzed 348 bugs from PyTorch-based systems, finding that 88% of environment defects are interface-related and 46% specifically involve API mismatches. Their temporal analysis revealed that 68% of defects surface during training rather than at environment-setup, establishing the lifecycle mismatch we address. Wolter et al. [2] surveyed ML reproducibility practices, reporting that 75% of repositories lack automated testing and fewer than 50% specify dependencies with version constraints. Collberg and Proebsting [3] found that only 54% of published systems could be built from source, with environment configuration being the primary barrier.

While these studies characterize the problem space, they do not provide concrete interventions. Our work translates their empirical findings into actionable tooling: we operationalize Jiang et al.'s interface defect taxonomy as contractable invariant categories and target the 75% of repositories (Wolter et al.) that lack testing infrastructure.

## Dependency Management and Environment Isolation

The standard approach to ML reproducibility relies on dependency pinning (pip freeze, conda environments, Docker containers) to stabilize library versions across environments [4, 5]. However, version pinning addresses *which* versions are used, not *whether* those versions behave as expected. Two limitations motivate our approach: (1) pinning cannot validate behavioral invariants across adjacent versions—a library update may preserve the API surface while violating mathematical properties, and (2) pinned environments do not detect assumption violations within a single version (e.g., undocumented device placement requirements in PyTorch-CUDA-HuggingFace stacks).

Our contracts complement version pinning by validating behavioral invariants that *should* hold regardless of specific versions, while our version-stability experiments (Section 5.4) quantify false-positive rates across ±2 minor releases.

## Integration Testing and Continuous Integration

Repository-level integration tests (pytest [6], tox [7]) provide regression detection for specific codebases. However, integration tests are repo-specific artifacts that encode usage patterns for particular projects rather than reusable library-level behavioral specifications. The key distinction: pytest tests validate "*does this code work in this repository?*" while contracts validate "*does this library behave as documented?*" The latter generalizes across repositories using the same library.

Pham et al. [8] studied CI adoption in open-source projects, finding that CI primarily catches syntax errors and obvious crashes but struggles with subtle semantic violations. Our metamorphic contracts (Section 3.2) target precisely these subtle invariant violations that execute successfully but produce incorrect behavior.

## Property-Based Testing and Metamorphic Testing

Property-based testing frameworks (QuickCheck [9], Hypothesis [10]) validate software by generating random inputs and checking that specified properties hold. Metamorphic testing [11] validates systems by asserting mathematical relations between inputs and outputs (e.g., softmax probabilities must sum to 1.0). Both approaches have been applied to ML systems: Pei et al. [12] used metamorphic testing to detect inconsistencies in DNN implementations, and Zhang et al. [13] applied property-based testing to model quantization.

We build on these foundations but differ in scope and deployment: (1) we target documented API invariants specifically in ML libraries rather than general software properties, (2) we enforce a <10-second execution constraint suitable for environment-setup validation, and (3) we deploy contracts at the library level for cross-repository reuse rather than within individual test suites. Our composition contracts (Section 3.3) extend metamorphic testing principles to multi-library interactions, introducing bidirectional propagation mechanisms not present in single-library validation.

## Design-by-Contract and Formal Verification

The Design-by-Contract paradigm [14] integrates preconditions, postconditions, and invariants as first-class language constructs (e.g., Eiffel, Spec#). Dependent type systems (Coq [15], Idris [16]) enable compile-time verification of behavioral properties. While these approaches provide stronger guarantees than our contracts, they require significant annotation burden and are not widely adopted in ML workflows due to (1) most ML libraries are written in Python, which lacks native contract support, and (2) formal verification scales poorly to probabilistic behaviors and floating-point numerics common in ML.

Our approach trades formal completeness for pragmatic deployability: contracts are lightweight Python decorators that validate documented invariants without requiring type-system integration or formal proofs. This positions contracts as an intermediate tier between ad-hoc testing (low assurance, low cost) and formal verification (high assurance, high cost).

## Positioning Summary

| Approach | Scope | Reusability | Behavioral Validation | ML-Specific |
|----------|-------|-------------|----------------------|-------------|
| Version pinning | Library versions | ✓ | ✗ | ✗ |
| Integration tests | Repository | ✗ | Limited | ✗ |
| Property-based testing | General software | ✓ | ✓ | ✗ |
| Formal verification | Language-level | ✓ | ✓✓ | ✗ |
| **API Contracts (Ours)** | Library APIs | ✓ | ✓ | ✓ |

Our contributions address an underserved niche: library-level behavioral validation tailored to ML API patterns, deployable at environment-setup time with <10-second overhead.

---

**References (Section 2 only - full list in Section 7)**

[1] Jiang et al. (2023). An Empirical Study of Bugs in PyTorch-Based Deep Learning Systems.  
[2] Wolter et al. (2025). Reproducibility Practices in Machine Learning Research.  
[3] Collberg & Proebsting (2016). Repeatability in Computer Systems Research.  
[4] Gruening et al. (2018). Bioconda: Sustainable Package Management for Bioinformatics.  
[5] Merkel (2014). Docker: Lightweight Linux Containers for Consistent Development.  
[6] Krekel et al. (2021). pytest: Helps You Write Better Programs.  
[7] Holger et al. (2020). tox: Command Line Driven CI Frontend.  
[8] Pham et al. (2013). Creating a Shared Understanding of Testing Culture.  
[9] Claessen & Hughes (2000). QuickCheck: A Lightweight Tool for Random Testing.  
[10] MacIver et al. (2019). Hypothesis: A Practical Test Framework for Python.  
[11] Chen et al. (1998). Metamorphic Testing: A New Approach for Generating Test Cases.  
[12] Pei et al. (2017). DeepXplore: Automated Whitebox Testing of DNNs.  
[13] Zhang et al. (2020). Property-Based Testing for Model Quantization.  
[14] Meyer (1992). Applying Design by Contract.  
[15] Bertot & Castéran (2004). Interactive Theorem Proving with Coq.  
[16] Brady (2013). Idris: Dependent Types for Real Programs.
