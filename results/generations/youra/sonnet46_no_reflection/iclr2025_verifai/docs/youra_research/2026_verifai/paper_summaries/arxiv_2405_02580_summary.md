---
source_paper: "arxiv_2405_02580.md"
generated_at: "2026-05-20T07:24:05.828817"
model: "gpt-4.1-mini"
summary_chars: 9948
---

# PropertyGPT: LLM-driven Formal Verification of Smart Contracts

## Key Metadata
- **Authors:** Ye Liu et al.
- **Year:** 2025
- **Venue:** NDSS Symposium 2025
- **Core Contribution:** Introduces PropertyGPT, a novel retrieval-augmented large language model (LLM) system that automatically generates comprehensive formal verification properties for smart contracts, improving vulnerability detection substantially over prior methods.

## Section Summaries

### Abstract
Formal verification can prove correctness of systems against specifications and is critical for security-sensitive smart contracts. Despite advances in static verification tools, automatic generation of comprehensive properties (invariants, pre-/post-conditions, rules) remains missing, leading to manual efforts by expert auditors. PropertyGPT leverages state-of-the-art LLMs like GPT-4, combined with retrieval-augmented in-context learning from a vector database of human-written properties, to generate customized properties for unknown smart contract code. It iteratively refines properties via compilation feedback and ranks them by a novel similarity-weighted algorithm, finally verifying them with a dedicated prover. Experiments show 80% recall on ground truth properties, detection of 26 out of 37 real-world CVEs/attacks, and discovery of 12 zero-day vulnerabilities rewarded with $8,256 in bug bounties.

### Introduction & Motivation
Smart contracts automate digital agreements on blockchains but are prone to vulnerabilities due to coding and logical bugs. Formal verification—checking if a contract meets precise specifications like invariants and pre-/post-conditions—can provide security guarantees. However, a fundamental bottleneck is the absence of automated generation of such comprehensive properties, which still largely rely on manual expert creation (e.g., Certora’s human-crafted properties). Existing property inference methods either depend on runtime transaction data or focus on limited property types (mainly invariants). With advances in LLMs and their in-context learning, the authors aim to leverage these to transfer knowledge from existing human-written properties and automatically generate rich formal properties for new contracts, overcoming manual scalability issues.

### Methodology
PropertyGPT’s core methodology integrates retrieval-augmented generation (RAG) with formal verification in a closed-loop pipeline:

- **Core Algorithm: Retrieval-Augmented Property Generation with Refinement**
  1. **Knowledge Base Construction:** Embed the critical code snippets related to 623 human-written properties from 23 Certora-audited projects into a vector database using OpenAI’s text-embedding-ada-002.
  2. **Querying & Retrieval:** Embed the target code under verification and retrieve top 10-20 similar code snippets and their associated reference properties based on a similarity threshold (~0.8).
  3. **In-context Learning (ICL):** For each retrieved property, use GPT-4 with tailored prompt templates to generate new properties for the target code (function-level pre-/post-conditions or cross-function rules in their Property Specification Language).
  4. **Iterative Compilability Refinement:** Use feedback from a custom PSL compiler and static analysis oracle to iteratively revise generated properties until they compile correctly or a maximum of nine attempts is reached. Prompts instruct GPT-4 to fix compilation errors and ensure the property meaningfully tests the intended function.
  5. **Weighted Ranking & Final Selection:** Compute a weighted similarity score for each generated property considering four metrics:
     \[
     \text{Score}(f, \phi_1) = \alpha \times X_{\text{raw}}(f,g) + \beta \times X_{\text{summary}}(f,g) + \gamma \times Y_{\text{raw}}(\phi_1, \phi_2) + \eta \times Y_{\text{summary}}(\phi_1, \phi_2)
     \]
     where \(f\) is unknown code, \(g\) is reference code, \(\phi_1\), \(\phi_2\) are properties, and \(\alpha, \beta, \gamma, \eta\) are learned weights (\(0.134, 0.556, 0.141, 0.168\)). The top-K (typically top-2) properties are selected for verification.
  6. **Formal Verification:** A dedicated prover conducts source-level symbolic execution based on small-step operational semantics, performing strongest postcondition analysis for modular verification. Violated properties trigger bounded model checking and counterexample generation, identifying vulnerabilities.

- **Model Architecture & Inputs:**
  - Use GPT-4-turbo (API) with temperature=0.8, top-p=1 for property generation and revision.
  - Input: Solidity smart contract code snippets (typically a function) and a pulled reference property.
  - Output: Formal properties in the Property Specification Language (PSL), a Solidity-extended intermediate language supporting invariants, pre-/post-conditions, and rules.
  - PSL syntax supports expressions over contract state variables, parameters, and constants, easing formal reasoning and symbolic execution.

- **Training & Optimization:**
  - No model fine-tuning; rely entirely on in-context learning with carefully designed one-shot prompt templates for rule properties and function conditions.
  - For ranking, train a linear regression model minimizing difference between the computed weighted score and a ground truth property equivalence signal.

- **Novel Components:**
  - Designing PSL tailored to express contracts’ diverse properties while easy to generate and verify.
  - Iterative compilation error-guided property repair leveraging LLM prompts.
  - Weighted multi-metric property ranking combining code and property semantic and syntactic similarities.
  - End-to-end formal verification pipeline combining symbolic execution with bounded model checking on source-level Solidity code.

### Experiments & Results
- **Datasets:**
  - 23 Certora audited projects with 623 human-written properties, of which 90 properties from 9 projects formed the testing set.
  - Well-known 13 smart contract CVEs spanning access control, integer overflow, logic errors, etc.
  - 24 real-world attack incidents curated from SmartInv benchmark.
  - 4 real-world bounty projects for zero-day discovery.

- **Evaluation Metrics:**
  - For property generation: Recall, Precision, F1-score based on human-expert judged equivalence.
  - For vulnerability detection: Number of detected known CVEs and attack incidents.
  - Additional measurements: Compilation success rate, repair attempts, code similarity metrics (cosine + Word Mover's Distance).

- **Baselines:**
  - SmartInv (concurrent LLM-based property generation for invariants).
  - GPTScan (LLM-augmented static analysis).
  - Slither (static analysis).
  - Mythril, Manticore (symbolic execution tools).

- **Main Results:**

| Task                      | PropertyGPT       | Best Baseline       | Notes                       |
|---------------------------|-------------------|---------------------|-----------------------------|
| Property Generation Recall | 80%               | N/A                 | Precision 64%, F1 71%       |
| CVE Detection             | 9/13 detected     | GPTScan+ 5/13       | Outperforms Slither, Mythril |
| Attack Incident Detection | 17/24 detected    | SmartInv qualitative | PropertyGPT generates ~16 properties/project with ~12 min gen time, 34s verification time |
| Zero-day Bounty Finds     | 12 confirmed bugs | N/A                 | Earned $8,256 in bounties   |

- **Ablation & Analysis:**
  - Without iterative refinement, GPT-4 had only 63% compile success vs 87% with PropertyGPT’s repair.
  - 74% of properties needed no or a single revision; 84% fixed within 5 attempts.
  - Top-2 ranked properties yield the best recall/precision tradeoff based on tuning.
  - Code similarity in successful versus failed generated cases does not significantly differ (~0.67–0.68), indicating strong generalizability.
  
- **Case Studies:**
  - Detected subtle zero-day vulnerabilities such as a function incorrectly aggregating validator fee withdrawals and a function overwriting storage due to missing uniqueness checks.
  - Generated formal properties that precisely captured the flaws, confirmed and repaired by vendors.

- **Computational Cost:**
  - Property generation times per project: range from ~1 to 34 minutes depending on project complexity.
  - Verification runtime typically less than 1 minute using Z3 SMT solver.

### Discussion & Conclusion
PropertyGPT demonstrates that LLMs, combined with retrieval-augmented learning and a dedicated formal prover, can automate the generation of comprehensive formal verification properties for smart contracts, significantly advancing state-of-the-art vulnerability detection beyond existing static and ML-based tools. Limitations include unsupported runtime contexts and partial coverage of access control subtleties. Future work aims for richer contract context integration (e.g., documentation), expanded property types (liveness), and continuous knowledge base updates for improved transfer learning.

## Key Contributions
- A novel PropertyGPT system combining LLM-driven retrieval-augmented property generation and iterative refinement for automated formal verification of smart contracts.
- Introduction of the Property Specification Language (PSL) and a source code level prover employing small-step symbolic execution and bounded model checking.
- Extensive evaluation demonstrating 80% recall on expert properties, outperforming state-of-the-art tools on CVEs and attack benchmarks, and uncovering numerous zero-days with real monetary impact.

## Potential Relevance
PropertyGPT’s approach to retrieval-augmented in-context learning for property generation and its integration of iterative compile-time feedback offer a promising methodology for automating formal specification generation in other code verification contexts. Its weighted multi-metric property ranking and source-level symbolic execution prover may serve as