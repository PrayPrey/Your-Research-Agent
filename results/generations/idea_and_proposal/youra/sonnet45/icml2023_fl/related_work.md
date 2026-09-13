## Related Work

**Related Papers**
1. **Title**: Federated Learning in Practice: Reflections and Projections (Semantic Scholar ID: dd9ef76fb9d6b3fe1e55fd1a0b796a45820b0b5e)
   - **Authors**: Daly et al., Google Research
   - **Summary**: Identifies "verifying server-side DP guarantees" as a critical production challenge in federated learning systems, highlighting the gap in third-party verification capabilities.
   - **Year**: 2024

2. **Title**: A Hassle-free Algorithm for Strong Differential Privacy in Federated Learning Systems (Semantic Scholar ID: 0d7914be9e5d15c53bb879a927dab379353e2d97)
   - **Authors**: McMahan et al.
   - **Summary**: Introduces BLT-DP-FTRL algorithm that achieves ε-DP with enhanced privacy-utility trade-off in federated learning systems.
   - **Year**: 2024

3. **Title**: Trustworthy and Scalable Federated Edge Learning (Semantic Scholar ID: f7c7cd537ec76a30786730113d802f0dcc5415fb)
   - **Authors**: Zhang et al.
   - **Summary**: FLBC Framework demonstrating blockchain non-tampering property and traceability for preventing data and model tampering in federated learning.
   - **Year**: 2024

4. **Title**: Privacy Auditing in Differential Private Machine Learning
   - **Authors**: Not specified
   - **Summary**: Demonstrates that empirical auditing approaches provide lower bounds rather than formal guarantees for differential privacy verification.
   - **Year**: 2024

5. **Title**: NIST Differential Privacy Guidelines
   - **Authors**: Not specified
   - **Summary**: Establishes regulatory requirements for differential privacy parameter documentation and compliance standards.
   - **Year**: 2024

**Key Challenges**
1. **Verification of Server-Side DP Guarantees**: Current federated learning systems lack capability for third-party verification of differential privacy guarantees without accessing sensitive model gradients or relying on server self-reporting (Google Research, 2024).

2. **Trust-Based Privacy Accounting**: Existing FL systems rely on trust-based approaches where auditors cannot independently verify privacy claims without violating data confidentiality requirements.

3. **Hardware-Dependent Verification Limitations**: TEE-based (Trusted Execution Environment) verification approaches require trusting hardware manufacturers and remain vulnerable to side-channel attacks (Spectre, Meltdown).

4. **Empirical vs. Formal Guarantees Gap**: Current privacy auditing methods provide empirical lower bounds through attack-based testing rather than formal cryptographic guarantees of differential privacy compliance.

5. **Regulatory Compliance Documentation**: GDPR Article 25 (data protection by design) and HIPAA Security Rule require technical safeguards and documentation that current FL systems struggle to provide without compromising privacy.

6. **Blockchain-FL Integration Gap**: While blockchain has been applied to FL data integrity (FLBC Framework), no existing work combines blockchain audit trails with zero-knowledge proofs for privacy guarantee verification.

7. **ZK Proof Application Mismatch**: zkML research (2023-2024) focuses on inference privacy rather than differential privacy mechanism verification during training.

8. **Retroactive Budget Modification Risk**: Absence of tamper-proof privacy budget accounting allows potential retroactive modification of reported privacy consumption, undermining audit integrity.
