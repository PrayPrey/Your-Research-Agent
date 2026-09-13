# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - ImmunFL)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ImmunFL-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under cross-device federated learning with potentially malicious clients [C], if bio-inspired decomposition (verifiable self-assessment + secure reputation aggregation + hierarchical filtering) is applied [X intervention], then simultaneous differential privacy (ε≤8), Byzantine resilience (40% malicious tolerance), and million-scale deployment will be achieved [Y outcome] because pre-aggregation Byzantine detection through privacy-preserving self-assessment resolves the fundamental conflict between privacy-preserving aggregation and Byzantine detection [Z mechanism].

**Alternative Hypothesis (H0):**
H0: Bio-inspired decomposition does not improve the privacy-robustness-scalability tradeoff compared to existing approaches. Specifically, either (a) pre-aggregation self-assessment fails to detect Byzantine clients with ≥85% accuracy, (b) the privacy budget for self-assessment (ε/4) significantly degrades gradient utility, or (c) hierarchical filtering introduces exploitable attack surfaces that reduce Byzantine tolerance below 30%.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| health_signature_dimension | Independent | Dimension of DP-noised gradient statistics vector (norm, variance, layer consistency) | d ∈ {8, 16, 32} |
| reputation_rounds | Independent | Number of rounds for trust score accumulation before Byzantine exclusion | r ∈ {3, 5, 10} |
| hierarchy_depth | Independent | Number of hierarchical layers = ceil(log₁₀(n)) for n clients | L ∈ {3, 4, 5, 6} for n ∈ {1K, 10K, 100K, 1M} |
| privacy_budget_epsilon | Independent | Total DP budget split: ε/4 for self-assessment, 3ε/4 for gradient release | ε ∈ {2, 4, 8} |
| byzantine_tolerance_rate | Dependent | Max fraction of malicious clients while maintaining <5% accuracy drop | Target: ≥40% |
| model_accuracy | Dependent | Test accuracy on held-out data under Byzantine attack | CIFAR-10: ≥75%, FEMNIST: ≥80% |
| communication_overhead | Dependent | Ratio of ImmunFL total communication to FedAvg baseline | Target: ≤1.5× |
| client_scale | Controlled | Fixed number of clients for scalability evaluation | n = 1,000,000 |
| dataset | Controlled | Standard FL benchmarks for evaluation | CIFAR-10 (IID), FEMNIST (non-IID) |

### 1.3 Causal Mechanism

**4-Step Causal Chain (N=4):**

```
[Verifiable Self-Assessment] → [Early Byzantine Detection] → [Reputation Scores] → [Hierarchical Filtering] → [Privacy-Preserving Byzantine-Resilient Aggregation]
```

**Step 1: Verifiable Self-Assessment → Early Byzantine Detection**
- Clients compute DP health signatures from gradient statistics (norm, variance, layer consistency)
- Cryptographic commitments submitted BEFORE gradient submission
- 5% random spot-checking provides probabilistic verification
- *Falsification*: Fails if Byzantine clients generate fake signatures passing spot-checks

**Step 2: Early Byzantine Detection → Reputation Scores**
- Detection results update trust scores via secure aggregation of scalars
- Verification failures propagate reputation penalties across rounds
- Multi-round accumulation (reputation_rounds) increases detection confidence
- *Falsification*: Fails if reputation aggregation leaks individual behavior

**Step 3: Reputation Scores → Hierarchical Filtering**
- Low-reputation clients filtered at intermediate aggregators
- Hierarchy depth = log₁₀(n) ensures O(log n) complexity
- Stateless aggregators run Byzantine-resilient algorithms (Krum, Trimmed-Mean)
- *Falsification*: Fails if intermediate nodes collude or become attack targets

**Step 4: Hierarchical Filtering → Clean Aggregation**
- Filtered clients undergo standard secure aggregation with DP guarantees
- Privacy-robustness conflict resolved by separating detection from aggregation
- Final model achieves ε≤8 DP with 40% Byzantine tolerance
- *Falsification*: Fails if privacy budget exhaustion leaves insufficient budget for gradients

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Xiang et al. (2023) | DP noise can be LEVERAGED for Byzantine detection, achieving 90% tolerance | Strong |
| Step2 → Step3 | Li et al. (2024) | Commitment + masking enables verifiable aggregation without information leakage | Strong |
| Step3 → Step4 | ABD-HFL (2024) | Hierarchical structure achieves 49% Byzantine tolerance with O(log n) complexity | Strong |
| Step4 → Outcome | SEAR (2022), Blades benchmark | SGX-based approach validates feasibility; Blades provides evaluation framework | Medium |

**Key Tension:**

**Tension:** Xiang et al. (2023) achieves 90% Byzantine tolerance but requires centralized aggregation that doesn't scale to 1M clients. ABD-HFL (2024) achieves scalability with hierarchy but lacks differential privacy guarantees.

**Resolution:** ImmunFL resolves this by decomposing Byzantine detection into self-assessment (scalable, DP-compatible) while using hierarchy for efficient filtering (scalable) and secure aggregation for final privacy (DP-guaranteed). This verification plan tests whether the decomposition preserves the benefits of both approaches.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|---------------------|------------------------|
| A1 | Gradient statistics (norm, variance, layer consistency) contain sufficient signal to distinguish Byzantine from honest updates | Xiang 2023 shows DP noise reveals Byzantine patterns; SEAR uses gradient inspection | Self-assessment fails, Byzantine detection accuracy <50%, entire framework collapses |
| A2 | Secure aggregation of scalar reputation scores has negligible computational overhead | Li 2024 shows efficient verifiable aggregation; scalar vs vector aggregation | Communication overhead exceeds 2×, scalability benefit lost |
| A3 | Hierarchical structure with stateless intermediate nodes does not create exploitable attack bottlenecks | ABD-HFL 2024 achieves 49% Byzantine tolerance with hierarchy | Intermediate node attacks reduce tolerance below 30%, single point of failure |
| A4 | Spot-checking rate of 5% provides sufficient deterrence for fake health signatures | SEAR sampling-based detection principle; game-theoretic deterrence | Fake signature attacks succeed >20% of time, Byzantine detection bypassed |
| A5 | Privacy budget can be split (ε/4 for assessment, 3ε/4 for gradients) without significant utility loss | Privacy composition theorems; gradient utility literature | Accuracy drop >10% from budget split, privacy-utility tradeoff worsens |

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Cross-device federated learning with heterogeneous, potentially malicious clients
- Large-scale deployments (10K - 1M+ clients)
- Privacy-sensitive domains requiring DP guarantees (healthcare, finance, mobile)
- Scenarios where up to 40% of clients may be compromised or Byzantine

**Where Hypothesis Does NOT Apply:**
- Fully trusted enterprise FL (cross-silo) - ImmunFL overhead is unnecessary
- Single-client or small-scale scenarios (<100 clients) - hierarchy overhead not justified
- Scenarios requiring ε<2 privacy (stronger privacy needs different approaches)
- Real-time training with <100ms latency requirements (commitment overhead)

**Known Limitations:**
- 5-10% computational overhead from cryptographic commitments
- Requires commitment infrastructure (hash functions, random beacons for spot-check selection)
- Privacy budget split may be suboptimal for specific use cases
- Hierarchy construction assumes stable client participation for aggregator assignment

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Byzantine Tolerance vs SOTA ~35% unified baseline):**
ImmunFL will achieve Byzantine tolerance ≥40% while maintaining test accuracy within 5% of clean baseline AND ε≤8 differential privacy.

*Measurement:*
- Byzantine tolerance rate achieving <5% accuracy drop from clean, with p < 0.05
- Statistical test: Paired t-test across attack types (label-flip, gradient scaling, backdoor)
- Required runs: n ≥ 25 per configuration

*Basis:*
- SEAR (2022): 30% Byzantine, no DP, O(n²) - not unified
- ABD-HFL (2024): 49% Byzantine, no DP, O(log n) - not unified
- Xiang 2023: 90% Byzantine, ε-DP, limited scale - partially unified
- **Target: 40% Byzantine + ε≤8 DP + O(log n) = first fully unified**

*Success Criteria for Phase 2B:*
- Primary: Byzantine tolerance ≥40% with accuracy drop <5% (p < 0.05)
- Falsification: Byzantine tolerance <30% OR accuracy drop >10% triggers rejection

**Secondary Predictions:**

**P2 (Scalability - Communication Overhead):**
ImmunFL will achieve communication overhead ≤1.5× FedAvg at 1M client scale.

*Measurement:* Total bytes transmitted per round / FedAvg baseline bytes
*Success Criteria:* Overhead ratio ≤1.5× with hierarchy depth = 6 for n=1M

**P3 (Self-Assessment Detection Accuracy):**
Verifiable self-assessment will achieve Byzantine detection accuracy ≥85% (precision + recall average) with spot-check rate of 5%.

*Measurement:* F1 score of Byzantine client detection per round
*Success Criteria:* F1 ≥0.85 averaged over 100 rounds

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure - Byzantine Tolerance:** Byzantine tolerance <30% (= below SEAR baseline)
   - Indicates self-assessment mechanism insufficient for Byzantine detection

2. **Primary Failure - Privacy:** Achieved ε >12 for comparable accuracy (50% above target)
   - Indicates privacy budget split fundamentally flawed

3. **Mechanism Failure - Detection:** Self-assessment F1 <0.70 (below random baseline with prior)
   - Indicates gradient statistics don't carry Byzantine signal

4. **Scalability Failure:** Communication overhead >2.5× FedAvg at 1M scale
   - Indicates hierarchy introduces unacceptable overhead

5. **Comparative Failure:** No improvement on any dimension vs best existing unified approach
   - Indicates bio-inspired decomposition provides no benefit

### 1.7 SOTA Baseline (SOTA Comparison Mode)

**SOTA Comparison Summary:**

| Method | Privacy (DP) | Byzantine Tolerance | Scalability | Year | Unified? |
|--------|--------------|---------------------|-------------|------|----------|
| SEAR | ❌ None | 30% | O(n²) limited | 2022 | ❌ |
| Xiang et al. | ε-DP | 90% | O(n) centralized | 2023 | Partial |
| ABD-HFL | ❌ None | 49% | O(log n) | 2024 | ❌ |
| PRIVFED-AD | ε-DP | 30% | O(n) limited | 2025 | Partial |
| **ImmunFL (Target)** | **ε≤8** | **40%** | **O(log n)** | 2026 | **✅ Yes** |

**Analysis:**
- Performance Tier: Medium (current SOTA fragmented, no unified solution)
- Best Byzantine (Xiang 2023): 90% but limited scalability
- Best Scalability (ABD-HFL): O(log n) but no privacy
- **Gap:** No existing method achieves DP + Byzantine + Scalability simultaneously
- **ImmunFL Target:** First unified framework achieving all three requirements

**Improvement Strategy:** Unified Capability (not incremental improvement on single metric)
- ImmunFL doesn't need to beat Xiang's 90% Byzantine tolerance
- ImmunFL needs to demonstrate all three capabilities together at acceptable levels

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.6 (medium-large, unified capability vs fragmented baselines)
- Required runs: n ≥ 25 per configuration
- Statistical power: 0.8 (β = 0.2)
- Configurations: 3 Byzantine rates × 3 ε values × 3 attack types = 27 configurations

**Test Specification:**
- Method: Paired t-test (same random seeds across methods)
- Significance level: α = 0.05 (one-tailed for improvement claims)
- Multiple comparison correction: Bonferroni for 3 primary metrics
- Report format: Mean difference, 95% CI, Cohen's d, p-value

**Evaluation Framework:**
- Benchmarks: Blades (Byzantine attacks), ATR-Bench (Trust evaluation)
- Datasets: CIFAR-10 (IID), FEMNIST (non-IID heterogeneous)
- Attack types: Label-flip, gradient scaling, backdoor (Blades implementations)
- Scale testing: 1K → 10K → 100K → 1M clients (simulation + selective real deployment)

**Reproducibility Requirements:**
- Fixed random seeds for all experiments
- Public codebase with Flower + Opacus integration
- Docker containers for environment consistency
- Checkpoint saving at each round for debugging

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Foundation):**
"Does verifiable self-assessment using DP gradient statistics enable pre-aggregation Byzantine detection with ≥85% accuracy while preserving ε≤8 differential privacy?"
- Maps to: Primary prediction P1 and P3 (detection accuracy)
- Verification type: Empirical experiment
- Critical: MUST PASS - if self-assessment fails, entire framework collapses

**SH2 (Mechanism - Core, N=4 Sub-Hypotheses in Phase 2B):**
"Is the bio-inspired 4-step decomposition (self-assessment → detection → reputation → filtering) the actual mechanism enabling unified privacy-robustness-scalability?"

Phase 2B will decompose into 4 mechanism sub-hypotheses:
- **H-M1:** Verifiable self-assessment produces Byzantine-distinguishing signals
- **H-M2:** Detection results enable meaningful reputation score updates
- **H-M3:** Reputation-based hierarchical filtering removes Byzantine clients efficiently
- **H-M4:** Filtered aggregation achieves target DP + accuracy guarantees

Verification type: Causal analysis with ablation studies
Critical: Determines explanatory power of bio-inspired decomposition

**SH3 (Comparison - Validation):**
"Does ImmunFL achieve unified privacy-robustness-scalability that no existing method (SEAR, Xiang 2023, ABD-HFL) provides?"
- Maps to: Secondary predictions P2 (scalability) and SOTA comparison table
- Verification type: Comparative empirical (head-to-head benchmarking)
- Critical: Determines practical value and novelty claim validity

**Total Sub-Hypotheses in Phase 2B:** 6 (1 + 4 + 1)

### Readiness Checklist

| # | Requirement | Status | Notes |
|---|-------------|--------|-------|
| 1 | Hypothesis in "Under [C], if [X], then [Y] because [Z]" format | ✅ | Section 1.1 |
| 2 | Hypothesis ID assigned | ✅ | H-ImmunFL-v1 |
| 3 | Confidence level specified | ✅ | 0.82 |
| 4 | Alternative hypothesis (H0) defined | ✅ | Three specific failure modes |
| 5 | All variables have operationalization | ✅ | 9 variables with ranges |
| 6 | Causal mechanism has evidence at each step | ✅ | 4 steps, evidence table |
| 7 | Causal chain length determined | ✅ | N=4 (Complex) |
| 8 | Key tension identified with resolution | ✅ | Xiang vs ABD-HFL scalability |
| 9 | Key assumptions list consequences | ✅ | 5 assumptions with consequences |
| 10 | At least 2 testable predictions | ✅ | P1 (primary), P2, P3 |
| 11 | Falsification criteria defined | ✅ | 5 rejection criteria |
| 12 | Baselines identified for comparison | ✅ | SEAR, Xiang, ABD-HFL, PRIVFED-AD |
| 13 | SH1, SH2, SH3 clear starting points | ✅ | 6 total sub-hypotheses |

**Status: ALL 13 REQUIREMENTS MET ✅**

### Open Questions

**Questions for Phase 2B Verification Planning:**

1. **Resource Requirements:**
   - GPU compute: Estimate 4× A100 for 1M client simulation (can start with 10K prototype)
   - Time: 2-3 months for prototype, 6 months for full validation
   - Data: CIFAR-10 and FEMNIST publicly available; no access concerns

2. **Technical Feasibility Concerns:**
   - Commitment scheme implementation: Can leverage existing crypto libraries (libsodium)
   - Flower + Opacus integration: Both are mature; integration complexity is main risk
   - 1M client simulation: May need hierarchical simulation rather than full deployment

3. **Priority Verification Order:**
   - **First:** SH1 (Existence) - validate self-assessment mechanism works at small scale (1K clients)
   - **Second:** H-M1 → H-M2 (Mechanism steps 1-2) - verify detection → reputation pipeline
   - **Third:** H-M3 → H-M4 (Mechanism steps 3-4) - verify filtering → aggregation
   - **Fourth:** SH3 (Comparison) - full benchmark vs baselines at increasing scale
   - **Rationale:** Early exit if SH1 fails; mechanism validation before expensive comparisons

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
