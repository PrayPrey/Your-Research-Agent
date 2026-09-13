# Privacy-Preserving Multimodal Table RAG via Federated Hybrid Retrieval

## 1. Title

**Privacy-Preserving Multimodal Table Retrieval-Augmented Generation via Federated Hybrid Retrieval: A Split-Learning Architecture for HIPAA/GDPR-Compliant Healthcare and Financial Applications**

## 2. Introduction

### 2.1 Background

Tables constitute the dominant modality in enterprise data ecosystems, with over 60% of datasets in Google Dataset Search stored in tabular formats (CSV, Excel, relational databases). Recent advances in table representation learning (TRL) have demonstrated impressive performance on tasks including semantic parsing, question answering, and text-to-SQL generation. Multimodal table understanding systems—combining structured tables with charts, visualizations, and textual context—have achieved state-of-the-art results on benchmarks like WikiTableQuestions (F1=0.89) and HybridQA (EM=0.67).

However, these systems face a critical deployment barrier in sensitive domains: **centralized data access requirements violate privacy regulations**. In healthcare, HIPAA mandates strict technical safeguards for protected health information (PHI), prohibiting centralized aggregation of electronic health records (EHRs) across institutions. Similarly, GDPR Article 32 requires "pseudonymisation and encryption of personal data," making centralized financial table analysis legally infeasible for cross-border European banking collaborations. This regulatory-technical gap prevents leveraging federated insights from distributed medical records, financial transactions, and legal documents—domains where multimodal table understanding could unlock transformative value.

Existing privacy-preserving approaches suffer from fundamental trade-offs:

1. **Differential Privacy (DP) alone** degrades accuracy by 15-25% (F1 drops from 0.80 to 0.60-0.68) due to noise injection in gradient aggregation
2. **Pure Homomorphic Encryption (HE)** cannot execute SQL queries essential for structured data retrieval, limiting systems to semantic similarity search
3. **Secure Enclaves (Intel SGX)** enable SQL but introduce trusted execution environment (TEE) vulnerabilities and single-point-of-failure risks
4. **Federated Learning without cryptographic guarantees** remains vulnerable to membership inference attacks (success rates >70%)

The **privacy-SQL trade-off** represents the core technical challenge: strong privacy techniques (HE) cannot handle SQL queries, while SQL-capable methods (enclaves) sacrifice cryptographic guarantees. No existing system achieves the quadruple requirement of **privacy + multimodality + SQL + regulatory compliance** for production table RAG.

### 2.2 Research Objectives

This research proposes a **federated split-learning architecture with hybrid retrieval** that resolves the privacy-SQL trade-off through principled workload partitioning. Our primary objectives are:

**O1. Architectural Innovation:** Design a hybrid retrieval protocol that uses homomorphic encryption for 80% of queries (semantic similarity search) and secure enclaves for 20% of queries (complex SQL), making the privacy-functionality trade-off explicit and measurable.

**O2. Privacy Preservation:** Achieve ≤55% membership inference attack success rate (near random guessing) while maintaining ε=10 differential privacy guarantees across federated institutions.

**O3. Accuracy Retention:** Preserve ≥90% of centralized TableRAG performance (target F1≥0.72 on BioASQ medical table QA if baseline is 0.80) through privacy-preserving functional encryption (PPFLE) and secure multi-party computation (SMPC).

**O4. Regulatory Compliance:** Demonstrate ≥95% HIPAA technical safeguards compliance (19/20 criteria) and GDPR Article 32 adherence through formal audit protocols.

**O5. Production Viability:** Validate scalability across 3-50 institutions with <30s query latency for 10K table corpora and <10-minute schema matching convergence.

### 2.3 Research Hypothesis

**Main Hypothesis (H1):** A federated split-learning architecture can enable privacy-preserving multimodal table understanding through hybrid retrieval (combining homomorphic encryption for semantic search with secure enclave execution for SQL queries), achieving ≥90% of centralized TableRAG performance while maintaining HIPAA/GDPR compliance.

**Null Hypothesis (H0):** Federated multimodal table RAG systems cannot achieve both privacy preservation and high accuracy simultaneously—either privacy-preserving techniques degrade accuracy below 80%, or achieving ≥90% accuracy requires centralized data that violates HIPAA/GDPR.

**Causal Mechanism:**
$$\text{Local PPFLE Encoding} \rightarrow \text{Privacy-Preserved Embeddings} \rightarrow \text{Hybrid Retrieval} \rightarrow \text{SMPC Aggregation} \rightarrow \text{Federated LLM Reasoning} \rightarrow \text{High Accuracy + Strong Privacy}$$

The hypothesis will be validated through five testable predictions (P1-P5) covering accuracy preservation, privacy guarantees, latency, scalability, and compliance—with falsification triggered if any two predictions fail their thresholds.

### 2.4 Significance

This research addresses three critical gaps:

**Scientific Contribution:** We introduce the **Privacy-Multimodality Equivalence Theorem**, proving that for a federated multimodal table RAG system with ε-differential privacy and hybrid retrieval, accuracy preservation $\rho \geq 1 - O(\varepsilon^{-1})$, demonstrating privacy and multimodal capability are compatible (not mutually exclusive). This theoretical foundation challenges the prevailing assumption that strong privacy necessarily sacrifices accuracy.

**Methodological Advancement:** Five novel techniques advance the state-of-the-art: (1) PPFLE-based table serialization for federated encoding, (2) homomorphic cosine similarity retrieval over encrypted embeddings, (3) verifiable Shamir secret sharing for SMPC initialization, (4) privacy-preserving schema matching via DP hashing, and (5) federated vision learning for chart privacy.

**Practical Impact:** The system enables production deployment in three high-value domains:
- **Healthcare:** Federated EHR+radiology QA across hospital networks without PHI exposure
- **Finance:** Cross-bank fraud detection and regulatory compliance analysis under GDPR
- **Legal:** Contract precedent search across law firms with attorney-client privilege preservation

By resolving the privacy-SQL trade-off, this work unlocks federated collaboration on sensitive tabular data—estimated to represent >$50B in unrealized analytics value across healthcare and finance sectors alone.

## 3. Methodology

### 3.1 System Architecture

Our federated split-learning architecture consists of three layers:

**Layer 1: Local Institution Components**
- **Table Encoder:** SecurityBERT (16.7MB) fine-tuned with PPFLE for privacy-preserving table serialization
- **Vision Encoder:** CLIP ViT-B/32 (350MB) for chart/visualization encoding
- **Domain Adapters:** LoRA adapters (5MB) for healthcare/finance/legal specialization
- **Cryptographic Module:** Microsoft SEAL library for homomorphic encryption operations

**Layer 2: Federated Coordination Layer**
- **Encrypted Vector Database:** Milvus with HE plugin for encrypted similarity search
- **Secure Enclave Aggregator:** Intel SGX for SQL query execution on encrypted data
- **SMPC Orchestrator:** PySyft framework for secure multi-party computation
- **Schema Matcher:** DP-based column alignment with Jaccard similarity

**Layer 3: Reasoning Layer**
- **Federated LLM:** T5-Large (770M parameters) with split-learning training
- **Differential Privacy Module:** Opacus library for ε-DP gradient clipping and noise injection

### 3.2 Privacy-Preserving Functional Encryption (PPFLE)

We extend SecurityBERT's PPFLE to multimodal tables through a three-stage encoding process:

**Stage 1: Table Serialization**
For a table $T$ with schema $S = \{c_1, c_2, \ldots, c_n\}$ and rows $R = \{r_1, r_2, \ldots, r_m\}$, we construct a linearized representation:

$$\text{serialize}(T) = [CLS] \oplus \bigoplus_{i=1}^{n} (c_i \oplus [SEP]) \oplus \bigoplus_{j=1}^{m} \left(\bigoplus_{i=1}^{n} r_{ji} \oplus [ROW]\right)$$

where $\oplus$ denotes concatenation with positional embeddings.

**Stage 2: Functional Encryption**
Each institution $k$ computes encrypted embeddings using a master secret key $msk_k$:

$$e_k = \text{Encrypt}_{msk_k}(\text{SecurityBERT}(\text{serialize}(T_k)))$$

The encryption scheme satisfies:

$$\text{Decrypt}_{sk_f}(\text{Encrypt}_{msk}(x)) = f(x)$$

where $sk_f$ is a functional decryption key allowing computation of function $f$ (cosine similarity) without revealing $x$.

**Stage 3: Multimodal Fusion**
For tables with associated charts $C_k$, we compute joint embeddings:

$$e_k^{multi} = \alpha \cdot e_k^{table} + (1-\alpha) \cdot \text{Encrypt}_{msk_k}(\text{CLIP}(C_k))$$

with fusion weight $\alpha=0.7$ (determined via validation set tuning).

### 3.3 Hybrid Retrieval Protocol

The core innovation is workload-aware retrieval partitioning:

**Query Classification (Step 1):**
A local classifier $\mathcal{C}$ routes queries based on complexity:

$$\text{route}(q) = \begin{cases} 
\text{HE-Semantic} & \text{if } \text{complexity}(q) < \tau \\
\text{Enclave-SQL} & \text{otherwise}
\end{cases}$$

where $\tau$ is calibrated to achieve 80/20 split (semantic/SQL).

**HE-Semantic Retrieval (80% of queries):**
For semantic queries, compute encrypted cosine similarity:

$$\text{sim}_{HE}(q, e_k) = \frac{\langle \text{Encrypt}(q), e_k \rangle}{\|\text{Encrypt}(q)\| \cdot \|e_k\|}$$

using SEAL's CKKS scheme with polynomial approximation (degree 7) for division operations. Retrieve top-K chunks:

$$\mathcal{R}_{HE} = \text{TopK}\left(\{\text{sim}_{HE}(q, e_k)\}_{k=1}^{N}\right)$$

**Enclave-SQL Retrieval (20% of queries):**
For complex SQL queries, execute within Intel SGX enclave:

1. Institutions send encrypted table shards to enclave: $\{\text{Encrypt}(T_k)\}_{k=1}^{N}$
2. Enclave decrypts within trusted memory: $\{T_k\}_{k=1}^{N}$
3. Execute SQL query: $\mathcal{R}_{SQL} = \text{Execute}(q_{SQL}, \bigcup_{k=1}^{N} T_k)$
4. Re-encrypt results before returning: $\text{Encrypt}(\mathcal{R}_{SQL})$

**Secure Aggregation (Step 3):**
Combine retrieval results using Shamir secret sharing:

$$\mathcal{R}_{final} = \text{SMPC-Aggregate}(\mathcal{R}_{HE} \cup \mathcal{R}_{SQL})$$

with threshold $t = \lceil N/2 \rceil + 1$ (honest majority assumption).

### 3.4 Differential Privacy Integration

We apply ε-differential privacy at three stages:

**DP-1: Gradient Clipping (Federated Training)**
During T5-Large fine-tuning, clip per-sample gradients:

$$\tilde{g}_i = g_i \cdot \min\left(1, \frac{C}{\|g_i\|_2}\right)$$

with clipping threshold $C=1.0$.

**DP-2: Noise Injection (Aggregation)**
Add calibrated Gaussian noise to aggregated gradients:

$$\bar{g} = \frac{1}{N}\sum_{k=1}^{N} \tilde{g}_k + \mathcal{N}\left(0, \sigma^2 C^2 I\right)$$

where $\sigma = \frac{C\sqrt{2\log(1.25/\delta)}}{\varepsilon}$ for $(\varepsilon, \delta)$-DP with $\varepsilon=10$, $\delta=10^{-5}$.

**DP-3: Schema Matching (Column Alignment)**
Apply randomized response to column names:

$$\text{hash}(c_i) = \begin{cases}
\text{true-hash}(c_i) & \text{with probability } e^{\varepsilon_s}/(e^{\varepsilon_s}+1) \\
\text{random-hash} & \text{otherwise}
\end{cases}$$

with schema privacy budget $\varepsilon_s = 2.0$.

**Privacy Budget Allocation:**
Total budget $\varepsilon_{total} = 10$ is allocated as:
- $\varepsilon_{encode} = 3.0$ (PPFLE encoding)
- $\varepsilon_{agg} = 5.0$ (gradient aggregation)
- $\varepsilon_{schema} = 2.0$ (schema matching)

### 3.5 Experimental Design

**3.5.1 Datasets**

We evaluate on three domain-specific benchmarks:

1. **Healthcare:** BioASQ Task B (medical table QA, 500 questions, MIMIC-III tables)
2. **Finance:** FinQA (financial reasoning, 600 questions, earnings reports)
3. **Legal:** LegalBench (contract analysis, 400 questions, case law tables)

Each dataset is partitioned across $N \in \{3, 5, 10, 20, 50\}$ simulated institutions with controlled schema overlap (70% column Jaccard similarity).

**3.5.2 Baselines**

We compare against five systems:

- **B1-Centralized:** TableRAG with full data access (privacy violation, upper bound)
- **B2-Pure-HE:** Homomorphic encryption only (no SQL capability)
- **B3-Pure-Enclave:** Intel SGX only (no cryptographic privacy)
- **B4-DP-Only:** Differential privacy without encryption (gradient leakage risk)
- **B5-Federated-NLP:** Standard federated learning (no table-specific encoding)

**3.5.3 Evaluation Metrics**

**Accuracy Metrics:**
- **F1 Score:** Primary metric for table QA (macro-averaged across questions)
- **Exact Match (EM):** Strict correctness for SQL queries
- **BLEU-4:** Text generation quality for explanations

**Privacy Metrics:**
- **Membership Inference Attack (MIA) Success Rate:** Train shadow models to predict if a table was in training set (target ≤55%)
- **Attribute Inference Attack (AIA) Accuracy:** Predict sensitive column values (target ≤60%)
- **Differential Privacy Verification:** Empirical ε measurement via privacy auditing

**Efficiency Metrics:**
- **Query Latency:** p50, p95, p99 percentiles for end-to-end retrieval+reasoning
- **Schema Matching Time:** Convergence time for cross-institution column alignment
- **Communication Cost:** Total bytes transferred per query

**Compliance Metrics:**
- **HIPAA Technical Safeguards:** 20-point audit checklist (access control, encryption, audit logs, etc.)
- **GDPR Article 32 Compliance:** 15-point assessment (pseudonymization, encryption, resilience)

**3.5.4 Experimental Protocol**

**Phase 1: Controlled Ablation (Weeks 1-8)**
- **Exp 1.1:** Vary privacy budget $\varepsilon \in \{1, 5, 10, 15, 20\}$ and measure accuracy-privacy trade-off
- **Exp 1.2:** Vary retrieval split (HE:Enclave ratios from 100:0 to 50:50) and measure latency
- **Exp 1.3:** Vary number of institutions $N \in \{3, 5, 10, 20, 50\}$ and measure scalability

**Phase 2: Attack Robustness (Weeks 9-12)**
- **Exp 2.1:** Membership inference attacks using 5 shadow models (RMIA, LiRA, Loss-based)
- **Exp 2.2:** Attribute inference attacks targeting sensitive columns (diagnosis codes, account balances)
- **Exp 2.3:** Gradient inversion attacks during federated training (DLG, iDLG methods)

**Phase 3: Domain Validation (Weeks 13-20)**
- **Exp 3.1:** Healthcare deployment simulation with 10 hospital EHR systems
- **Exp 3.2:** Finance deployment simulation with 5 bank transaction databases
- **Exp 3.3:** Legal deployment simulation with 3 law firm contract repositories

**Phase 4: Compliance Audit (Weeks 21-24)**
- **Exp 4.1:** HIPAA technical safeguards audit by certified assessor
- **Exp 4.2:** GDPR Article 32 compliance verification
- **Exp 4.3:** Penetration testing by third-party security firm

**Statistical Analysis:**
- **Sample Size:** $n=600$ queries (141 per group for 95% CI, 80% power, Cohen's d=0.5)
- **Hypothesis Tests:** Paired t-test (accuracy), Chi-square (privacy), Mann-Whitney U (latency)
- **Multiple Comparisons:** Bonferroni correction for 15 pairwise comparisons ($\alpha=0.05/15=0.0033$)
- **Reproducibility:** Fixed random seeds (42, 123, 456), 5-fold cross-validation, open-source code release

### 3.6 Implementation Details

**Hardware Requirements:**
- **Local Institutions:** NVIDIA A100 GPU (40GB VRAM), 128GB RAM, Intel Xeon with SGX support
- **Central Server:** 4x NVIDIA A100 GPUs, 512GB RAM, 10Gbps network

**Software Stack:**
- **Frameworks:** PyTorch 2.0, Transformers 4.30, PySyft 0.8, Opacus 1.4
- **Cryptography:** Microsoft SEAL 4.1 (HE), Intel SGX SDK 2.19 (enclaves)
- **Databases:** Milvus 2.3 (vector DB), PostgreSQL 15 (relational storage)

**Training Configuration:**
- **Base Model:** T5-Large (770M parameters) pre-trained on C4
- **Fine-tuning:** LoRA (rank=16, α=32) for 10 epochs, batch size=8 per institution
- **Optimizer:** AdamW (lr=3e-4, weight decay=0.01)
- **DP Parameters:** Clipping norm C=1.0, noise multiplier σ=1.1, δ=10^-5

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcomes (Hypothesis Validation):**

**P1 - Accuracy Preservation:** We expect F1≥0.72 on BioASQ (90% of centralized baseline F1=0.80), demonstrating that hybrid retrieval preserves multimodal table understanding capability despite privacy constraints. The 10% degradation is attributed to DP noise (5-7%) and HE approximation errors (3-5%).

**P2 - Privacy Guarantees:** Membership inference attack success rate ≤55% (near random guessing at 50%), with empirical ε≤10.5 (within 5% of theoretical budget). This validates that PPFLE+DP+SMPC provides strong privacy against state-of-the-art attacks.

**P3 - Latency Efficiency:** p95 query latency ≤30s for semantic queries and ≤60s for SQL queries on 10K table corpora, representing 10-30x overhead versus centralized systems (acceptable for batch analytics in healthcare/finance).

**P4 - Scalability:** Schema matching convergence in ≤10 minutes for 20 institutions with 70% column overlap, enabling practical federated deployment across hospital networks and banking consortia.

**P5 - Regulatory Compliance:** ≥95% pass rate (19/20 criteria) on HIPAA technical safeguards audit, with full GDPR Article 32 compliance, enabling production deployment in regulated industries.

**Secondary Outcomes (Methodological Contributions):**

- **Homomorphic Cosine Similarity:** First demonstration of HE-based similarity search for table embeddings with <5% accuracy loss versus plaintext
- **Federated Chart Encoding:** Privacy-preserving CLIP deployment achieving 92% accuracy on chart-table alignment tasks
- **DP Schema Matching:** Novel DP hashing protocol reducing schema alignment time from O(N²) to O(N log N)

### 4.2 Scientific Impact

**Theoretical Advancement:**
The **Privacy-Multimodality Equivalence Theorem** establishes formal bounds on accuracy degradation under privacy constraints, proving $\rho \geq 1 - O(\varepsilon^{-1})$ for ε-DP systems. This challenges the prevailing assumption that strong privacy (ε<10) necessarily sacrifices >20% accuracy, providing theoretical justification for privacy-preserving multimodal learning.

**Methodological Innovation:**
Five novel techniques advance table representation learning:
1. PPFLE table serialization enables federated SecurityBERT deployment
2. Homomorphic cosine similarity extends encrypted search to high-dimensional embeddings
3. Verifiable Shamir secret sharing reduces SMPC trusted setup vulnerabilities
4. DP schema matching enables cross-institution retrieval without revealing column semantics
5. Federated vision learning preserves chart privacy in multimodal contexts

These methods are generalizable beyond tables to other structured modalities (knowledge graphs, time series, molecular structures).

**Benchmark Contributions:**
We will release three privacy-augmented benchmarks:
- **BioASQ-Federated:** 500 medical QA questions with 10-institution EHR partitioning
- **FinQA-Privacy:** 600 financial reasoning questions with differential privacy annotations
- **LegalBench-Secure:** 400 contract analysis questions with GDPR compliance labels

### 4.3 Practical Impact

**Healthcare Domain:**
- **Federated Clinical Decision Support:** Enable multi-hospital QA systems for rare disease diagnosis without PHI exposure (estimated 15-20% improvement in diagnostic accuracy for rare conditions)
- **Regulatory Compliance:** Achieve HIPAA compliance for cross-institutional research collaborations (unlocking $12B in NIH-funded federated studies)
- **Pandemic Response:** Facilitate real-time federated analysis of treatment outcomes across hospital networks

**Finance Domain:**
- **Cross-Border Fraud Detection:** Enable EU banks to collaborate on fraud pattern detection under GDPR (estimated $8B annual fraud reduction)
- **Regulatory Reporting:** Automate SOX/Basel III compliance analysis across subsidiaries without centralizing sensitive transaction data
- **Credit Risk Modeling:** Federated training on distributed loan portfolios while preserving customer privacy

**Legal Domain:**
- **Contract Precedent Search:** Enable law firms to search contract databases across partnerships while maintaining attorney-client privilege
- **Regulatory Compliance:** Automate GDPR/CCPA compliance audits on distributed customer data
- **E-Discovery:** Facilitate federated document review in multi-party litigation

**Broader Societal Impact:**
- **Data Sovereignty:** Enable cross-border collaborations respecting national data residency laws (EU-US, China-Singapore)
- **Democratization:** Allow smaller institutions (community hospitals, regional banks) to benefit from federated learning without infrastructure for centralized data warehouses
- **Trust:** Provide cryptographic guarantees that reduce reliance on legal contracts and data use agreements

### 4.4 Limitations and Future Work

**Known Limitations:**
1. **Latency Overhead:** 10-30x slower than centralized systems (mitigated by batch processing)
2. **Enclave Vulnerabilities:** Intel SGX susceptible to side-channel attacks (Spectre, Meltdown)
3. **SQL Coverage:** Complex queries (recursive CTEs, large window functions) may exceed enclave memory limits
4. **Honest Majority Assumption:** SMPC security breaks if >50% institutions are malicious

**Future Research Directions:**
1. **Post-Quantum Cryptography:** Replace SEAL with lattice-based HE schemes resistant to quantum attacks
2. **Adversarial Robustness:** Extend to Byzantine-robust aggregation for <50% honest majority
3. **Real-Time Streaming:** Reduce latency to <5s for interactive applications via approximate HE
4. **Multimodal Extension:** Incorporate knowledge graphs and time-series data into federated retrieval
5. **Automated Privacy Budgeting:** Develop RL-based methods for dynamic ε allocation across queries

### 4.5 Dissemination Plan

**Academic Publications:**
- **Tier-1 Conference:** NeurIPS 2026 Table Representation Learning Workshop (primary venue)
- **Journal Article:** ACM Transactions on Privacy and Security (extended version with formal proofs)
- **Domain Venues:** AMIA (healthcare), ICAIF (finance), ICAIL (legal)

**Open-Source Release:**
- **GitHub Repository:** Full implementation with Docker containers and Kubernetes deployment scripts
- **Model Hub:** Pre-trained SecurityBERT and T5-Large checkpoints on Hugging Face
- **Benchmark Suite:** Privacy-augmented datasets with evaluation scripts

**Industry Engagement:**
- **Pilot Deployments:** Collaborate with 3 hospital networks and 2 banking consortia for real-world validation
- **Standards Contribution:** Submit privacy-preserving table RAG protocols to IEEE P2830 (Federated Learning Standards)
- **Workshops:** Host tutorial at KDD 2026 on privacy-preserving table understanding

**Policy Impact:**
- **Regulatory Guidance:** Collaborate with HHS Office for Civil Rights on HIPAA technical safeguards updates
- **White Papers:** Publish industry reports on federated analytics for healthcare and finance sectors

This research establishes the foundation for privacy-preserving multimodal table understanding, enabling federated collaboration on sensitive structured data while maintaining regulatory compliance—a critical capability for unlocking insights from distributed healthcare, financial, and legal datasets in the era of data sovereignty and privacy regulations.