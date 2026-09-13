## Related Work

**Related Papers**

1. **Title**: AgentPoison: Red-teaming LLM Agents (Chen et al., 2024)
   - **Authors**: Chen et al.
   - **Summary**: Demonstrates memory poisoning attacks on LLM agents with 80%+ attack success rate through backdoor injection into knowledge base entries, evaluated across 4 agent frameworks, 2 LLMs, and 3 attack scenarios showing severe security risks from unverified memory manipulation.
   - **Year**: 2024
   - **Identifier**: SS ID: b6948a9e8b3eec5a56a80c69727154fcd7ececce
   - **Citations**: 191

2. **Title**: A-MEM: Agentic Memory for LLM Agents (Xu et al., 2025)
   - **Authors**: Wujiang Xu, Zujie Liang, Kai Mei, et al.
   - **Summary**: Zettelkasten-inspired memory organization system with dynamic memory networks that evolve during agent operation, using semantic links and knowledge graphs. Lacks security features and provenance tracking, making it vulnerable to memory poisoning attacks.
   - **Year**: 2025
   - **Identifier**: SS ID: 1f35a15fe9df43d24ec6c9766c17eccf
   - **Citations**: 223
   - **Implementation**: https://github.com/WujiangXu/A-mem (759 stars, 71 forks)

3. **Title**: Trust the Process: snarkGPT (Ganescu et al., 2024)
   - **Authors**: Ganescu et al.
   - **Summary**: Demonstrates practical zero-knowledge machine learning (ZKML) verification enabling independent validation with "modest overhead", showing that ZK proofs can be integrated into ML systems for cryptographic verification.
   - **Year**: 2024
   - **Identifier**: SS ID: 0bcbbe4a38b35ba3b7a8709eeed163917c2eb3ec
   - **Citations**: 16

4. **Title**: Enabling verifiability in federated learning with ZK and blockchain (Tian, 2025)
   - **Authors**: Tian
   - **Summary**: Combines zero-knowledge proofs with blockchain to achieve formal verification in federated learning systems with acceptable overhead, demonstrating multi-constraint ZK proof generation applicable to distributed systems.
   - **Year**: 2025
   - **Identifier**: SS ID: 04b21733c20059ec456da6b7fef43c207bcd1b2b
   - **Citations**: Not specified

5. **Title**: HAICOSYSTEM: LLM Safety Evaluation Framework (Zhou et al., 2024)
   - **Authors**: Zhou et al.
   - **Summary**: Comprehensive safety evaluation framework providing 92 scenarios across 7 domains (healthcare, finance, legal, education, social services, shopping, personal services) for testing LLM agent systems in realistic deployment contexts.
   - **Year**: 2024
   - **Identifier**: SS ID: 45101e8b40e89385f6a14a9bb24d1a989417182a
   - **Citations**: 31

6. **Title**: Personal LLM Agents: User Modeling and Preferences (Singh et al., 2024)
   - **Authors**: Singh et al.
   - **Summary**: Studies user satisfaction with LLM agents showing 74.4%-87.3% user preference rates for agents with ~500ms response times, establishing latency tolerance thresholds for interactive agent applications.
   - **Year**: 2024
   - **Identifier**: SS ID: 9718211346eff715e3f45239a174d0fe8b7a332c
   - **Citations**: 32

7. **Title**: NIST FIPS 180-4: SHA-256 Cryptographic Hash Standard
   - **Authors**: NIST (National Institute of Standards and Technology)
   - **Summary**: Federal Information Processing Standard defining SHA-256 cryptographic hash function providing collision resistance with 20+ years of field deployment and no practical collisions found.
   - **Year**: Not specified
   - **Identifier**: FIPS 180-4

8. **Title**: NIST FIPS 186-4: Digital Signature Standard (ECDSA)
   - **Authors**: NIST (National Institute of Standards and Technology)
   - **Summary**: Digital Signature Standard defining ECDSA (Elliptic Curve Digital Signature Algorithm) based on discrete logarithm problem hardness, with P-256 providing 128-bit security level requiring ~2^128 operations to break.
   - **Year**: Not specified
   - **Identifier**: FIPS 186-4

9. **Title**: RFC 6962: Certificate Transparency
   - **Authors**: IETF (Internet Engineering Task Force)
   - **Summary**: Public append-only log system with Merkle tree structure for TLS certificates, logging 100M+ certificates with efficient browser vendor auditing and real-world detection of fraudulent certificates.
   - **Year**: Not specified
   - **Identifier**: RFC 6962

10. **Title**: Git Version Control System
   - **Authors**: Not specified
   - **Summary**: Distributed version control using directed acyclic graph (DAG) structure with cryptographic hash-based integrity, providing 15+ years of field deployment with billions of commits worldwide and zero successful cryptographic forgeries.
   - **Year**: Not specified

11. **Title**: Bitcoin Blockchain
   - **Authors**: Not specified
   - **Summary**: Cryptocurrency system using Merkle trees for transaction verification across 750,000+ blocks with 1,000-3,000 transactions each, enabling O(log n) verification proofs for lightweight clients with <1ms verification time on mobile devices.
   - **Year**: Not specified

12. **Title**: cryptography.io Python Library
   - **Authors**: Not specified
   - **Summary**: Production-grade Python cryptography library providing ECDSA P-256 signing (~0.3ms), verification (~0.1ms), and SHA-256 hashing (~0.01ms per KB), with millions of downloads and widespread production use.
   - **Year**: Not specified
   - **Implementation**: https://cryptography.io

13. **Title**: SQLite Official Benchmarks
   - **Authors**: SQLite Development Team
   - **Summary**: Database system demonstrating 1M+ inserts/second with ACID guarantees for append-only logs on standard SSD hardware, validating suitability for provenance chain storage.
   - **Year**: Not specified
   - **Implementation**: https://sqlite.org/speed.html

**Key Challenges**

1. **Memory Poisoning Vulnerability**: Current LLM agent memory systems lack integrity verification, enabling attackers to inject backdoored memories with 80%+ success rate (AgentPoison attack), compromising agent behavior through direct memory manipulation.

2. **Absence of Provenance Tracking**: Existing memory systems (A-MEM, HMLR) provide no audit trails for memory operations, making it impossible to determine who created, modified, or deleted memories, when changes occurred, or why operations were performed.

3. **Regulatory Compliance Gap**: Current agent memory systems cannot meet GDPR (EU), HIPAA (US healthcare), or SOC2 (enterprise) requirements due to lack of complete audit trails and tamper-detection capabilities.

4. **Performance-Security Trade-off**: Cryptographic verification operations add computational overhead (0.3-7ms per operation), requiring careful architectural design to maintain real-time performance (<10ms) while providing security guarantees.

5. **Scalability of Audit Systems**: Traditional blockchain-style provenance systems have O(n) verification complexity, making audits impractical at scale (millions of memory operations). Need O(log n) verification approach like Merkle trees.

6. **Privacy vs. Auditability Tension**: Complete provenance chains reveal memory access patterns and timing information, potentially leaking sensitive information about agent behavior and user interactions, especially problematic in healthcare and finance domains.

7. **Integration Complexity**: Adding cryptographic provenance to existing memory systems requires extensible architecture to avoid complete codebase rewrites (>50% code change threshold makes implementation impractical).

8. **Storage Growth Management**: Provenance chains grow linearly with operations (256 bytes/transaction × 1M operations = 256MB), requiring tiered storage strategies balancing query latency against storage costs.

9. **Lack of Tampering Detection**: Current systems cannot detect if attackers modify stored memories, lacking cryptographic integrity checks to identify unauthorized changes in real-time.

10. **Cross-Domain Transfer Validation**: Need to validate that cryptographic techniques proven in version control (Git), blockchain (Bitcoin), and certificate systems (CT) can transfer effectively to LLM agent memory context with different access patterns and latency requirements.
