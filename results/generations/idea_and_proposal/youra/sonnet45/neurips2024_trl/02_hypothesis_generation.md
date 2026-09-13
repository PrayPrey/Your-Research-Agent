# Phase 2A Extended: Hypothesis Summary

**Date:** 2026-02-06
**Hypothesis ID:** H-TRL-001
**Confidence:** 82% (FEASIBLE)
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

A federated split-learning architecture can enable **privacy-preserving multimodal table understanding** through hybrid retrieval (combining homomorphic encryption for semantic search with secure enclave execution for SQL queries), achieving **≥90% of centralized TableRAG performance** while maintaining **HIPAA/GDPR compliance** for sensitive healthcare and financial applications.

**Key Innovation:** The 80/20 hybrid retrieval architecture resolves the privacy-SQL trade-off by using strict homomorphic encryption for 80% of queries (semantic similarity) and secure enclave (Intel SGX) for 20% of queries (complex SQL), enabling privacy-preserving multimodal table RAG that was previously impossible.

---

## Core Hypothesis

### Main Claim

A federated split-learning architecture can enable privacy-preserving multimodal table understanding through hybrid retrieval, achieving ≥90% of centralized TableRAG performance while maintaining HIPAA/GDPR compliance.

### Alternative Hypothesis (H0)

Federated multimodal table RAG systems cannot achieve both privacy preservation and high accuracy simultaneously—either privacy-preserving techniques degrade accuracy below 80%, or achieving ≥90% accuracy requires centralized data that violates HIPAA/GDPR.

### Causal Mechanism

```
[Local PPFLE Encoding] → [Privacy-Preserved Embeddings]
    → [Hybrid Retrieval: 80% HE Semantic + 20% Enclave SQL]
        → [SMPC Secure Aggregation + DP Noise]
            → [Federated LLM Reasoning]
                → [≥90% Accuracy + ≤55% Attack Success]
```

**Key Tension Resolution:** Strict homomorphic encryption (HE) provides strongest privacy but cannot execute SQL queries. The hybrid approach uses HE for 80% of queries (semantic search) and accepts secure enclave trust for 20% of queries (complex SQL), making the trade-off explicit and measurable.

---

## Testable Predictions

| ID | Prediction | Measurement | Success Criterion |
|----|-----------|-------------|------------------|
| **P1** | Accuracy preservation | F1 on BioASQ medical table QA | ≥90% of centralized TableRAG (F1 ≥ 0.72 if baseline is 0.80) |
| **P2** | Privacy guarantee | Membership inference attack success rate | ≤55% (near random guess) with ε=10 differential privacy |
| **P3** | Latency | p95 end-to-end query time | ≤30s (semantic), ≤60s (SQL) for 10K table corpus |
| **P4** | Scalability | Schema matching convergence time | ≤10 minutes for 20 institutions with 50-80% column overlap |
| **P5** | Compliance | HIPAA technical safeguards audit | ≥95% pass rate (19/20 criteria) |

**Falsification:** Hypothesis is FALSIFIED if **ANY TWO** predictions fail their thresholds.

---

## Key Variables

**Independent Variables:**
- Privacy architecture type (Pure HE, Hybrid HE+Enclave, Pure Enclave)
- Privacy budget ε (differential privacy parameter: 1-20)
- Number of federated institutions (3-50)
- Query type distribution (% semantic vs SQL)

**Dependent Variables:**
- RAG accuracy (F1 score on table QA benchmarks)
- Privacy leakage (membership inference attack success rate)
- Query latency (p50, p95, p99 percentiles)
- Compliance score (HIPAA audit pass rate)

**Controlled Variables:**
- Base model: T5-Large (770M parameters)
- Dataset size: 10,000 tables per institution
- Schema heterogeneity: 70% column overlap
- Adversarial ratio: <50% malicious institutions (honest majority)

---

## Contributions

### Theoretical

**Privacy-Multimodality Equivalence Theorem:** For a federated multimodal table RAG system with ε-differential privacy and hybrid retrieval, accuracy preservation ρ ≥ 1 - O(ε⁻¹), proving privacy and multimodal capability are compatible (not mutually exclusive).

### Methodological

1. **PPFLE-based table serialization** for federated encoding (extends SecurityBERT to multimodal tables)
2. **Homomorphic cosine similarity retrieval** over encrypted table embeddings (first HE application to table RAG)
3. **Verifiable Shamir secret sharing** for SMPC initialization (reduces trusted setup attack surface)
4. **Privacy-preserving schema matching** via DP hashing (enables cross-institution retrieval)
5. **Federated vision learning** for chart privacy (CLIP local deployment with encrypted aggregation)

### Practical

- **Production-deployable architecture:** Docker containers, Kubernetes orchestration, HIPAA audit trails
- **Domain enablement:** Healthcare (federated EHR+radiology QA), Finance (cross-bank fraud detection), Legal (contract precedent search)
- **Evaluation benchmarks:** BioASQ (medical), FinQA (financial), LegalBench (legal) with privacy/latency/compliance metrics

---

## Architecture Overview

**Local Components (per institution):**
- SecurityBERT encoder (16.7MB) for table PPFLE encoding
- CLIP vision encoder (350MB) for chart encoding
- LoRA adapters (5MB) for domain-specific fine-tuning
- Homomorphic encryption library (SEAL)

**Central Components:**
- Encrypted vector database (Milvus with HE plugin)
- Secure enclave aggregator (Intel SGX for SQL)
- Federated orchestrator (PySyft)

**Hybrid Retrieval Protocol:**
1. **80% queries (semantic):** HE-encrypted similarity search → Top-K encrypted chunks
2. **20% queries (SQL):** Secure enclave SQL execution → Encrypted results
3. **Aggregation:** SMPC-based secure aggregation with ε-DP noise injection
4. **Reasoning:** Federated LLM (T5) fine-tuned on synthetic tables

---

## Key Assumptions

1. **Honest Majority:** <50% malicious institutions (standard SMPC assumption)
2. **Sufficient Compute:** Each institution has GPU for SecurityBERT (16.7MB)
3. **Network Bandwidth:** ~1KB per embedding transfer (acceptable for enterprise networks)
4. **TEE Trust:** Intel SGX sufficiently secure for 20% SQL queries (known vulnerabilities accepted)
5. **Schema Alignment:** ≥70% column overlap enables DP-based schema matching
6. **Synthetic Data Quality:** ε-DP prevents gradient leakage during federated fine-tuning

**Critical Path:** If honest majority (1), TEE trust (4), OR schema alignment (5) fails → hypothesis may be falsified.

---

## Scope & Boundaries

**In-Scope:**
- Structured/semi-structured tables with multimodal context (charts, text)
- Healthcare (HIPAA), Finance (SOX/GDPR), Legal domains
- Batch query processing (5-50 institutions)
- Table QA, text-to-SQL, multimodal retrieval

**Out-of-Scope:**
- Unstructured text-only documents
- Real-time streaming (<1s latency)
- Adversarial majority (>50% malicious)
- Public non-sensitive data
- Complex SQL edge cases (recursive CTEs, large window functions)

---

## Related Work Positioning

| System | Accuracy | Privacy | Multimodal | SQL | Compliance |
|--------|----------|---------|------------|-----|------------|
| **TableRAG** (Centralized) | 0.78 F1 | ❌ None | ✅ Yes | ✅ Full | ❌ HIPAA violation |
| **VDocRAG** (Centralized) | N/A | ❌ None | ✅ Yes | ❌ No | ❌ GDPR violation |
| **Federated Imaging** | 98.6% | ✅ ε-DP + HE | ❌ Images only | N/A | ✅ HIPAA |
| **SecurityBERT** | 98.2% | ✅ PPFLE | ❌ No | N/A | ✅ Privacy |
| **Ours** | ≥90% | ✅ ε-DP + HE + Enclave | ✅ Yes | ✅ Hybrid | ✅ HIPAA + GDPR |

**Unique Position:** ONLY system combining federated learning + strong privacy + multimodal + table reasoning + SQL + regulatory compliance.

---

## Phase 2B Decomposition Preview

The main hypothesis will decompose into 5 sub-hypotheses for verification:

1. **SH1 (Existence):** Local PPFLE + HE semantic retrieval achieves ≥85% accuracy with ε-DP privacy
2. **SH2 (Mechanism):** Hybrid 80/20 retrieval preserves ≥90% accuracy with <30s latency overhead
3. **SH3 (Comparison):** Multimodal extension (charts) maintains ≥90% accuracy without degrading table-only performance
4. **SH4 (Scalability):** Schema matching converges in ≤10 minutes for 20 institutions
5. **SH5 (Deployment):** System passes ≥95% HIPAA technical safeguards audit

**Dependency Chain:** SH1 → SH2 → SH3 → SH4 → SH5 (sequential validation)

---

## Known Limitations

1. **Latency Overhead:** HE adds 10-30x overhead (30s vs 1s centralized)
2. **Accuracy Degradation:** ε-DP degrades accuracy by ~5-7%
3. **Enclave Vulnerability:** Intel SGX has known side-channel attacks (Spectre, Meltdown)
4. **Setup Complexity:** Schema matching requires 5-10 minute one-time setup
5. **SQL Coverage:** Complex queries (recursive CTEs) may exceed enclave memory limits
6. **Multimodal Infrastructure:** Requires CLIP deployment at each institution

---

## Open Questions for Phase 2B

**Critical (Must Resolve):**
1. Differential privacy budget allocation (ε_encode, ε_agg, ε_schema)
2. Secure enclave failure recovery protocol
3. Multimodal fusion strategy (concat vs cross-attention)

**Important (Affects Interpretation):**
4. Schema matching convergence criteria formalization
5. Baseline selection for healthcare domain
6. Membership inference attack design (which method?)

**Future Work (Nice-to-Have):**
7. Extension to other domains beyond healthcare/finance/legal
8. Comparison to federated NLP baselines

---

## Statistical Verification Design

- **Design:** Randomized controlled trial with 4 groups (Control: Centralized TableRAG, Treatment 1-3: Pure HE, Hybrid, Pure Enclave)
- **Sample Size:** n=600 queries (141 per group for 95% CI, 80% power, 10% detectable difference)
- **Tests:** Paired t-test (accuracy), Chi-square (privacy), Mann-Whitney U (latency), Linear regression (scalability), Binomial test (compliance)
- **Confound Controls:** Stratified sampling by query complexity, fixed schema overlap, controlled cloud environment, fixed base model
- **Reproducibility:** Open-source code, public datasets (MIMIC-III, FinQA, BioASQ), fixed random seeds, documented hardware

---

## Timeline Estimate

- **Phase 2B Planning:** 2-3 weeks (verification experiment design)
- **Phase 2C Experiment Design:** 3-4 weeks (detailed implementation specs)
- **Phase 3 Implementation Planning:** 4-6 weeks (PRD, Architecture, PRP)
- **Phase 4 Prototype Development:** 6-9 months (implementation + validation)
- **Phase 5 Paper Writing:** 2-3 months (academic paper preparation)

**Total Pipeline:** 9-12 months from hypothesis to publication-ready research

---

## Key Sources

**Foundation:**
- TableRAG (Yu et al. 2025) - SQL-based retrieval architecture
- VDocRAG (Tanaka et al. 2025) - Multimodal RAG framework

**Methodology:**
- SecurityBERT (Ferrag et al. 2023) - PPFLE encoding
- Federated Medical Imaging (Muthalakshmi et al. 2024) - Federated split-learning + DP + HE
- SMPC Credit Systems (Patel 2025) - Secure multi-party computation

**Cross-Domain Inspiration:**
- Federated Healthcare (98.6% accuracy with privacy)
- Cryptographic SMPC (production-deployed multi-party computation)

---

## Next Steps

1. **Proceed to Phase 2B:** Decompose into SH1-SH5 with detailed verification plans
2. **Address Critical Open Questions:** DP budget allocation, enclave fallback, fusion strategy
3. **Establish Baselines:** Run centralized TableRAG on BioASQ to confirm 90% target feasibility
4. **Resource Planning:** Estimate GPU hours, MIMIC-III data access, compliance audit costs

---

**Status:** ✅ READY FOR PHASE 2B VERIFICATION PLANNING

**Full Documentation:** See `02a_extended_hypothesis_full.md` for complete analysis (variables, mechanisms, evidence, statistical design)

---

*Generated using YouRA Phase 2A Extended Workflow*
*Date: 2026-02-06*
*Researcher: Pray*
*Topic: Table Representation Learning - Privacy-Preserving Multimodal RAG*
