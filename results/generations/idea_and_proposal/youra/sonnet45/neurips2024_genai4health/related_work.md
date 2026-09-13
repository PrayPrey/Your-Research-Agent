## Related Work

**Related Papers**

1. **Title**: Towards a HIPAA Compliant Agentic AI System in Healthcare
   - **Authors**: Neupane, Mitra, Mittal, Rahimi
   - **Summary**: Demonstrates HIPAA-compliant Agentic AI framework with Attribute-Based Access Control (ABAC) for Protected Health Information (PHI) governance, hybrid PHI sanitization, and immutable audit trails. Validates that technical compliance mechanisms can be formalized and provides baseline for ABAC rules and audit logging automation.
   - **Year**: 2025

2. **Title**: An Agentic Framework for Compliant, Ethical and Trustworthy GenAI Applications in Healthcare
   - **Authors**: Menezes, Chowdhury, Mahmood
   - **Summary**: Proposes CAM framework to translate EU AI Act and WHO guidelines into compliance mechanisms. Explicitly acknowledges "a deficiency remains in translating policy into effective compliance mechanisms," identifying the organizational coordination gap between policy and implementation.
   - **Year**: 2025

3. **Title**: Large language models and generative AI in telehealth: a responsible use lens
   - **Authors**: Pool, Indulska, Sadiq
   - **Summary**: Scoping review identifying need for multidisciplinary collaboration (policymakers, developers, security experts) in LLM telehealth applications. Finds transparency, explainability, and accountability lacking, validating multistakeholder coordination requirements.
   - **Year**: 2024

4. **Title**: A DevSecOps Policy-as-Code Model for Compliance Automation in Lakehouse Environments
   - **Authors**: Okare et al.
   - **Summary**: Policy-as-Code enables automated compliance enforcement through machine-readable policy definitions integrated into CI/CD pipelines. Provides paradigm source for cross-domain transfer from DevOps to Healthcare for automated policy enforcement.
   - **Year**: 2024

5. **Title**: Automating Compliance in Cloud Data Platforms Using Policy-as-Code
   - **Authors**: Rebbana
   - **Summary**: Automated policy lifecycle management with versioning, testing, and deployment enables continuous compliance validation across distributed systems. Informs iterative refinement methodology for false positive handling and A/B testing approaches.
   - **Year**: 2025

6. **Title**: Secure DevOps Pipelines (referenced as "Secure DevOps Pipelines")
   - **Authors**: Gummadi
   - **Summary**: Multi-stage validation architecture catches violations earlier than end-of-pipeline audits through continuous enforcement versus checkpoint reviews. Demonstrates effectiveness of distributed validation gates in development pipelines.
   - **Year**: 2024

**Key Challenges**

1. **Policy-to-Mechanism Translation Gap**: Healthcare regulations (HIPAA/GDPR) exist as natural language policies, but there is a deficiency in translating these policies into effective, machine-executable compliance mechanisms that can be automated.

2. **Multistakeholder Coordination Complexity**: Healthcare GenAI systems require collaboration between policymakers, developers, security experts, and clinical stakeholders, but coordination processes remain underspecified and manual-intensive.

3. **Organizational vs. Technical Compliance Disconnect**: Existing work focuses on technical compliance mechanisms (ABAC, encryption, access controls) but lacks automated organizational coordination processes, creating a gap between technical capability and practical stakeholder collaboration.

4. **Regulatory Nuance Loss Risk**: Machine-readable policy formalization may lose critical regulatory nuances when translating interpretive requirements into boolean logic, potentially creating compliance gaps or over-specification.

5. **Transparency and Explainability for Non-Technical Stakeholders**: Policy enforcement systems often operate as "black boxes" that lack adequate explainability layers for non-technical stakeholders (policymakers, clinical staff), hindering adoption and trust.

6. **Manual Coordination Overhead**: Current healthcare AI compliance practices rely on manual asynchronous processes (meetings, email threads, periodic audits) that create significant coordination costs measured in meeting frequency (8-12/month), email volume (50-100/week), and audit preparation hours (40-60 hours/cycle).

7. **Late-Stage Violation Detection**: Manual compliance reviews typically detect violations at deployment (Stage 3) or post-deployment audits (Stage 4) rather than at earlier lifecycle stages (data collection, training), increasing remediation costs and risks.

8. **Incomplete Audit Evidence**: Manual documentation processes result in partial attestation completeness (40-60% of compliance decisions documented) with retrospective evidence compilation that is time-consuming and error-prone.

9. **MLOps Integration Friction**: Integrating automated compliance validation into existing MLOps pipelines (Kubeflow, MLflow, SageMaker) may require significant platform modifications or may be infeasible in brownfield environments with legacy systems.

10. **Regulatory Acceptance Uncertainty**: Limited precedent exists for automated policy enforcement and audit trails being accepted by regulators (HHS Office for Civil Rights for HIPAA, national DPAs for GDPR) as sufficient compliance evidence, creating adoption risk.

11. **Stakeholder Adoption Resistance**: Conservative healthcare organizations may resist cultural shifts from manual to automated compliance processes, potentially maintaining parallel manual processes that double overhead rather than reducing it.
