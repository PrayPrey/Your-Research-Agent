# Verification Plan: Contamination-Aware Training with Geometric Detection

**Date:** 2026-05-11
**Hypothesis ID:** H-ContamGeometry-v1
**Confidence:** 0.80
**Total Hypotheses:** 5

---

## 0. Established Facts & Scope Reduction

### 0.1 Established Facts Registry (BUILD_ON - DO NOT RE-VERIFY)

The following claims are established by prior literature and form the foundation of our hypothesis. **Phase 2B-4 should NOT generate experiments to re-verify these.**

| Claim | Status | Evidence | Action |
|-------|--------|----------|--------|
| MIA fails during pretraining (AUC≈50%) because models learn distributions, not instances | BUILD_ON | Fu et al. (2024) arxiv:2410.18966 - tested across Pythia and OLMO-2 models | Skip verification |
| MIA succeeds during finetuning (up to 99.4% AUC) due to structured memorization | BUILD_ON | Fu et al. (2024) arxiv:2410.18966 - same paper, finetuning experiments | Skip verification |
| EAL-style paraphrasing evades semantic detection (TPR<2% @ 1%FPR) while achieving ~15% gains | BUILD_ON | Dekoninck et al. (2024) arxiv:2402.02823 - EAL attack validation | Skip verification |
| Continuous temporal monitoring is computationally feasible at scale | BUILD_ON | LiveCodeBench (2024) arxiv:2403.07974 - 400+ problems weekly collection | Skip verification |

### 0.2 Claims Requiring Verification (PROVE_NEW)

| Claim | Status | Rationale |
|-------|--------|-----------|
| Geometric detection (gradient/Hessian analysis) can reveal contamination when instance detection fails | PROVE_NEW | Core hypothesis - requires validation |
| Task Signature Graphs provide paraphrase-invariant task representations | PROVE_NEW | Novel contribution - requires TSG extraction validation |
| Differential alignment separates contamination from general skill transfer | PROVE_NEW | Novel metric - requires experimental validation |

**Scope Reduction:** 40% (4 out of 7 total claims are established, leaving 3 to prove)

**Phase 2B-4 Instructions:**
Established facts 1-4 should be treated as prior evidence supporting the architecture.
Do NOT re-prove that MIA fails in pretraining or that EAL evades detection.
Focus Phase 2B verification on:
- Geometric detection efficacy (NEW claim)
- TSG paraphrase-invariance (NEW claim)
- Differential alignment validity (NEW claim)
- Pareto frontier inevitability (NEW claim)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under finetuning conditions with ≤5% targeted benchmark injection (EAL-style paraphrased contamination),
if we apply a three-tier detection architecture combining data-layer filters, Task Signature Graph probes, and geometric trajectory auditing,
then we achieve ≥80% combined detection power at <5% false positive rate even against adaptive adversaries,
because contamination-induced benchmark gains (≥10% accuracy improvement) necessarily produce detectable geometric signatures (gradient subspace alignment, Hessian anisotropy, representational compression) that cannot be suppressed without sacrificing the performance advantage (Pareto constraint).

### 1.2 Alternative Hypothesis (H0)

For training runs achieving ≥10% benchmark performance gains from ≤5% targeted data injection, the combined three-tier detection system achieves ≤20% detection power at 5% false positive rate, indicating contamination-induced gains do not produce reliably detectable multi-layer signatures distinguishable from clean training.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | GSM8K + Math Reasoning Datasets (standard) | Target benchmark for contamination (GSM8K) + clean background training data (MATH, other math datasets) enables controlled EAL-protocol replication |
| **Model** | Llama-2-7B or Mistral-7B | 7B scale enables controlled experiments with N=20 runs, gradient/Hessian computation feasible, matches EAL paper experimental setup |

**Dataset Details:**
- Source: HuggingFace datasets, official benchmark repositories
- Path: Standard splits (GSM8K test set as contamination target, background math datasets for clean training)

**Model Details:**
- Type: Decoder-only transformer (7B parameters)
- Source: HuggingFace model hub (meta-llama/Llama-2-7b-hf or mistralai/Mistral-7B-v0.1)

### 1.4 Baseline Methods (Related Work)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Membership Inference Attacks (MIA) | AUC≈50% pretraining, up to 99.4% finetuning | Pythia, OLMO-2 models | Fails under paraphrasing; detects memorization, not task learning |
| Semantic Similarity / Text Matching | TPR<2% @ 1%FPR against EAL | EAL-contaminated models | Evaded by GPT-4-level rephrasing while task knowledge preserved |
| LiveCodeBench (Continuous Fresh Benchmarks) | 100% contamination prevention | HumanEval-style code problems | Requires constant benchmark creation, fragments evaluation landscape |

### 1.5 Key Assumptions

| ID | Assumption | Testability | Risk if Violated |
|----|------------|-------------|------------------|
| A1 | Contamination gains arise from task-specific parameter alignment, not general capability transfer | HIGH (Differential alignment test) | Tier 2 detection fails; but Tier 3 geometric signals may still detect |
| A2 | Achieving ≥10% benchmark gains from ≤5% injection requires parameter updates correlated with benchmark gradients | HIGH (Adaptive adversary Pareto frontier) | Geometric inevitability claim collapses; hypothesis fails |
| A3 | Task Signature Graphs can be extracted for structured domains (code, math) with sufficient paraphrase-invariance | MEDIUM (Invariant-breaking ablation) | Tier 2 detection degrades to instance similarity (which EAL evades) |
| A4 | Probe families are task-complete (span benchmark manifold) such that suppressing all probes collapses gains | MEDIUM (Adaptive adversary with probe access) | Adversary finds blind spots in probe coverage; detection power <80% |
| A5 | Finetuning (not pretraining) is the dominant contamination risk for benchmark manipulation | LOW (based on prior evidence) | Hypothesis scope limited; pretraining contamination remains unaddressed |

### 1.6 Research Gap & Novelty

**Paradigm Shift:**
- From: Instance-level similarity detection (MIA, text matching)
- To: Learning-trajectory geometric invariants (gradient alignment, Hessian anisotropy)
- Impact: Addresses fundamental failure mode: instance detection achieves AUC≈50% in pretraining, TPR<2% against EAL

**Technical Innovations:**
1. **Task Signature Graphs (TSG):** Abstract constraint manifolds extracted via program synthesis/canonicalization, paraphrase-invariant
2. **Differential Alignment Metric (Δ):** Separates contamination-specific from general skill transfer via Δ = (ΔL_invariant - ΔL_neighbor)
3. **Geometric Inevitability Theorem:** Contamination gains require detectable parameter-space alignment; Pareto constraint limits evasion
4. **Multi-tier Complementary Architecture:** Three layers handle accidental (data), behavioral (manifold), geometric (trajectory) signals

**Ecosystem Contribution:** Cryptographic audit infrastructure (signed trajectories, Evaluation Registry, pre-registered predictions) enables stable benchmarks vs. LiveCodeBench's constant benchmark churn

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | Mechanism | MUST_WORK | H-E1 | BLOCKED |
| H-M3 | Mechanism | MUST_WORK | H-E1 | BLOCKED |
| H-M4 | Mechanism | SHOULD_WORK | H-M1, H-M2, H-M3 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Three-Tier Detection System Achieves Target Performance

**Type:** EXISTENCE

**Statement:** Under finetuning conditions with 1-5% EAL-style paraphrased benchmark injection, if we apply the three-tier detection architecture (data-layer filters, TSG probes, geometric trajectory auditing), then we achieve ≥80% combined detection power at <5% false positive rate, because contamination-induced gains necessarily produce detectable multi-layer signatures across at least one tier.

**Rationale:** This hypothesis validates that the proposed detection system achieves the target performance envelope. It tests the core claim that contamination cannot evade all three tiers simultaneously when producing meaningful benchmark gains. Success demonstrates practical viability; failure indicates fundamental architecture flaws.

**Variables:**
- Independent: Contamination Rate (0%, 1%, 5%), Contamination Type (accidental vs adversarial)
- Dependent: Combined Detection Power, False Positive Rate
- Controlled: Base Model (Llama-2-7B/Mistral-7B), Hyperparameters (lr=2e-5, batch=64, epochs≤3)

**Verification Protocol:**
1. Replicate EAL protocol: train N=20 runs each for clean baseline, 1% injection, 5% injection
2. Apply all three detection tiers independently to each run
3. Compute combined detection power (OR logic: detected by ANY tier) and FPR on clean runs
4. Statistical test: combined power ≥80% at α=0.05 significance level
5. Disaggregate results by tier to identify which tiers contribute most to detection

**Success Criteria (PoC):**
- Primary: Combined detection power ≥80% for 5% injection @ <5% FPR
- Secondary: At least 2 of 3 tiers show >0% detection power (complementary architecture validated)

**Gate:** MUST_WORK
- If Fail: PIVOT to single-tier optimization or ABANDON multi-tier approach

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.1 (Core Statement), Section 1.6 Prediction P1

---

#### H-M1: Tier 1 Data-Layer Filters Catch Accidental Contamination

**Type:** MECHANISM

**Statement:** Under controlled injection conditions, if we apply Tier 1 data-layer filters (temporal isolation + LSH-based structural fingerprinting), then we catch ≥95% of accidental web-scraped contamination but <10% of EAL-style adversarial contamination, because exact/near-duplicate matches are detectable via hashing while paraphrased content evades data-layer similarity.

**Rationale:** Validates Tier 1's design goal: high recall on accidental contamination, expected blindness to adversarial attacks. Confirms that data-layer alone is insufficient (motivating Tier 2-3), while establishing its complementary value for catching unintentional leakage.

**Variables:**
- Independent: Contamination Type (accidental exact match vs EAL paraphrased)
- Dependent: Tier 1 Detection Rate per type
- Controlled: LSH parameters (hash size, band count), temporal threshold (data timestamp < benchmark release)

**Verification Protocol:**
1. Create two contamination conditions: (A) exact GSM8K train samples, (B) GPT-4 paraphrased
2. Apply temporal filter: flag if data timestamp ≥ GSM8K release date
3. Apply LSH fingerprinting: compute MinHash signatures, detect near-duplicates vs GSM8K corpus
4. Measure detection rates separately for accidental vs adversarial conditions
5. Confirm differential: accidental ≥95%, adversarial <10%

**Success Criteria (PoC):**
- Primary: Tier 1 detects ≥95% of accidental contamination
- Secondary: Tier 1 detects <10% of adversarial contamination (confirms paraphrasing evades data-layer)

**Gate:** MUST_WORK
- If Fail: EXPLORE alternative data-layer fingerprinting methods or adjust LSH parameters

**Dependencies:** H-E1 (EAL replication established)

**Source:** Phase 2A Section 1.3 (Causal Mechanism - Tier 1), Prediction P1

---

#### H-M2: Tier 2 TSG Probes Detect Behavioral Dynamics via Differential Alignment

**Type:** MECHANISM

**Statement:** Under EAL contamination conditions (1-5% injection), if we construct Task Signature Graph probe families (invariant, neighbor, broken-control) and track probe loss trajectories during finetuning, then differential alignment Δ = (ΔL_invariant - ΔL_neighbor) exceeds clean baseline by ≥2σ for 5% injection, because contamination accelerates learning on benchmark-aligned probes while having minimal effect on neighbor probes, revealing task-specific learning vs general skill transfer.

**Rationale:** Tests the novel differential alignment metric's ability to separate contamination from legitimate training. TSG paraphrase-invariance is critical: if Δ signal persists under GPT-4 rephrasing, it validates that we're measuring task structure (not surface similarity). Failure suggests TSG extraction quality issues or insufficient probe coverage.

**Variables:**
- Independent: Contamination Rate (0%, 1%, 5%)
- Dependent: Differential Alignment Δ (measured in standard deviations from clean baseline)
- Controlled: Probe family composition (1000 invariant, 1000 neighbor, 1000 broken-control), probe sampling distribution

**Verification Protocol:**
1. Extract TSG constraints for GSM8K via program synthesis (extract equation structures, reasoning patterns)
2. Generate probe families: invariant (GSM8K-like structure), neighbor (general math), broken (violated constraints)
3. Log probe loss every 100 finetuning steps for all runs (clean, 1%, 5% injection)
4. Compute Δ = (ΔL_invariant - ΔL_neighbor) for each run, measure z-score vs clean distribution
5. Statistical test: contaminated runs show Δ > 2σ at α=0.05

**Success Criteria (PoC):**
- Primary: Δ exceeds clean baseline by ≥2σ for 5% injection
- Secondary: Δ shows dose-response (1% injection: ≥1.5σ, 5% injection: ≥2σ)

**Gate:** MUST_WORK
- If Fail: EXPLORE TSG extraction quality via invariant-breaking ablation or PIVOT to alternative manifold representations

**Dependencies:** H-E1 (EAL contamination produces gains)

**Source:** Phase 2A Section 1.3 (Causal Mechanism - Tier 2), Prediction P4

---

#### H-M3: Tier 3 Geometric Metrics Reveal Parameter-Space Trajectory Signatures

**Type:** MECHANISM

**Statement:** Under contamination conditions producing ≥10% benchmark gains, if we measure geometric trajectory signatures (gradient subspace overlap, Hessian spectral concentration, CKA representational alignment, information efficiency), then ≥2 of 4 metrics exceed pre-registered thresholds for contaminated runs, because achieving task-specific gains requires low-dimensional parameter alignment toward benchmark manifolds, leaving detectable geometric signatures.

**Rationale:** Validates the geometric inevitability claim's foundation: contamination gains manifest as measurable parameter-space geometry changes. Tests whether gradient/Hessian analysis can detect what instance-level methods miss. Failure challenges the core theoretical framework that gains require geometric alignment.

**Variables:**
- Independent: Contamination Presence (clean vs 5% injection)
- Dependent: Geometric Metrics Count (out of 4 exceeding thresholds)
- Controlled: Threshold calibration (set on pilot data for target FPR), Hessian approximation method (Lanczos)

**Verification Protocol:**
1. For each finetuning run, log gradients and compute Hessian approximation every 100 steps
2. Measure 4 metrics: (a) cosine similarity between parameter updates and benchmark gradients, (b) top-10 eigenvalue concentration in benchmark subspace, (c) CKA between contaminated and clean representations, (d) gain-per-1000-tokens z-score
3. Set thresholds on pilot clean runs to achieve <5% FPR: gradient overlap +0.10, Hessian ratio 1.5×, CKA Δ ≥0.15, efficiency z≥2.5
4. Count metrics exceeding thresholds for each contaminated run
5. Statistical test: ≥2 metrics exceed for ≥80% of contaminated runs

**Success Criteria (PoC):**
- Primary: ≥2 of 4 geometric metrics exceed thresholds for 5% injection
- Secondary: At least one metric (gradient overlap or Hessian concentration) shows strong signal (>90% detection)

**Gate:** MUST_WORK
- If Fail: EXPLORE metric refinement or PIVOT to alternative geometric measures (Fisher Information, loss landscape curvature)

**Dependencies:** H-E1 (benchmark gains established)

**Source:** Phase 2A Section 1.3 (Causal Mechanism - Tier 3), Prediction P1

---

#### H-M4: Pareto Frontier Shows Convex Tradeoff (Geometric Inevitability)

**Type:** MECHANISM

**Statement:** Under adaptive adversary training with objective max(BenchmarkAcc - λ·DetectionSignal) and varying λ ∈ {0, 0.1, 0.5, 1.0, 2.0}, if we measure the empirical Pareto frontier between benchmark gains and Tier 2-3 detection probability, then suppressing detection signals by 50% reduces benchmark gains by ≥30% and no flat region (high gain + low signal) exists, because contamination gains fundamentally arise from parameter alignment with benchmark tasks, which is geometrically inseparable from detection signals.

**Rationale:** Tests the geometric inevitability theorem's core prediction: evasion is bounded by a convex Pareto constraint. This is the strongest test of our theoretical framework—if an adaptive adversary can achieve high gains with low detection, the entire geometric detection premise collapses. Success proves structural limits on evasion.

**Variables:**
- Independent: Adversary Regularization Weight λ (0, 0.1, 0.5, 1.0, 2.0)
- Dependent: Benchmark Accuracy Gain, Detection Probability (Tier 2+3 combined), Pareto Frontier Slope
- Controlled: Probe access (adversary sees TSG probes and geometric metrics during training), base contamination rate (5%)

**Verification Protocol:**
1. Implement adaptive adversary loss: L_task + λ·(ProbeSignal + GeometrySignal) where signals = Tier 2 Δ + Tier 3 metrics
2. Train N=20 runs for each λ value with 5% EAL contamination
3. For each run, measure final GSM8K accuracy gain and Tier 2+3 detection probability
4. Plot Pareto frontier: gains (y-axis) vs detection probability (x-axis) across λ sweep
5. Test convexity: measure slope (gain loss / signal reduction) at multiple λ points, verify monotonic tradeoff

**Success Criteria (PoC):**
- Primary: Suppressing signals by 50% costs ≥30% of gains (slope validation)
- Secondary: No flat region exists (no λ achieves ≥10% gains with <5% detection probability)

**Gate:** SHOULD_WORK
- If Fail: EXPLORE whether flat region is due to incomplete probe coverage or fundamental architecture flaw; may require acceptance that geometric detection has evasion modes

**Dependencies:** H-M1, H-M2, H-M3 (all tiers validated)

**Source:** Phase 2A Section 1.3 (Geometric Inevitability), Prediction P2

---

---

## 3. Risk Analysis

### 3.1 Risk Identification

**Risk R1: Task-Agnostic Contamination Gains**

**Source Assumption:** A1 - Contamination gains arise from task-specific parameter alignment, not general capability transfer

**Description:** If contamination produces gains through general capability improvements rather than task-specific alignment, differential alignment Δ will fail to discriminate (both invariant and neighbor probes improve equally), collapsing Tier 2 detection.

**Affected Hypotheses:** H-E1, H-M2

**Severity:** HIGH (Tier 2 detection fails, but Tier 3 geometric signals may still work)

**Mitigation Strategy:**
1. **Prevention:** Design probe families with explicit task-structure constraints (TSGs) and broad neighbor coverage to maximize discrimination
2. **Detection:** Monitor Δ during pilot runs; if |Δ| < 0.5σ despite gains, flag early warning
3. **Response:**
   - PIVOT: Rely on Tier 3 geometric detection as primary signal
   - SCOPE: Narrow to domains where task-specific learning is unavoidable (e.g., code with strict syntax)
   - ABORT: If Tier 3 also fails to discriminate, fundamental hypothesis failure

**Early Warning Indicators:**
- Δ values near zero despite >10% benchmark gains in pilot runs
- Neighbor probes improve at same rate as invariant probes under contamination

---

**Risk R2: Smooth Evasion via Geometric Orthogonalization**

**Source Assumption:** A2 - Achieving ≥10% benchmark gains from ≤5% injection requires parameter updates correlated with benchmark gradients

**Description:** Adaptive adversary discovers optimization path orthogonal to benchmark gradients that still produces gains (flat Pareto region), invalidating geometric inevitability claim and enabling high-gain + low-signal evasion.

**Affected Hypotheses:** H-E1, H-M3, H-M4

**Severity:** CRITICAL (Core theoretical framework collapses; hypothesis fails)

**Mitigation Strategy:**
1. **Prevention:** Implement comprehensive geometric measurement (4 complementary metrics: gradient, Hessian, CKA, efficiency) to cover multiple alignment dimensions
2. **Detection:** Phase 3 adaptive adversary experiments directly test for flat region existence
3. **Response:**
   - PIVOT: If partial flat region exists (gain reduction < 30% for 50% signal suppression), tighten detection thresholds and increase probe coverage
   - SCOPE: Accept that geometric detection has bounded efficacy (e.g., 60-70% vs target 80%)
   - ABORT: If full flat region exists (≥10% gains with <5% detection), geometric approach fundamentally invalid

**Early Warning Indicators:**
- Pareto frontier shows sub-linear tradeoff (slope < 0.6) in pilot adaptive adversary runs
- Hessian eigenvalues remain isotropic despite benchmark gains

---

**Risk R3: TSG Extraction Quality Insufficient**

**Source Assumption:** A3 - Task Signature Graphs can be extracted for structured domains (code, math) with sufficient paraphrase-invariance

**Description:** TSG extraction for math reasoning tasks fails to capture deep structure, instead learning surface artifacts, causing Tier 2 to degrade to instance similarity (which EAL evades).

**Affected Hypotheses:** H-M2

**Severity:** HIGH (Tier 2 fails for math domain; may still work for code)

**Mitigation Strategy:**
1. **Prevention:** Validate TSG quality via invariant-breaking ablation: perturb TSG constraints and verify detection degrades
2. **Detection:** Test paraphrase-invariance directly: GPT-4 rephrase invariant probes, measure whether they remain clustered with originals
3. **Response:**
   - PIVOT: Use code domain (HumanEval) where TSG extraction via AST parsing is more reliable
   - SCOPE: Document math domain as higher-risk, rely more on Tier 3 geometric signals
   - ABORT: If invariant-breaking ablation shows TSGs don't encode structure, redesign Tier 2

**Early Warning Indicators:**
- Invariant probes show low similarity to each other despite structural commonality
- Paraphrased invariant probes cluster with neighbor probes instead of original invariants
- Tier 2 detection rate < 30% on 5% injection (below minimum viable threshold)

---

**Risk R4: Incomplete Probe Coverage (Adversary Blind Spots)**

**Source Assumption:** A4 - Probe families are task-complete (span benchmark manifold) such that suppressing all probes collapses gains

**Description:** Adversary finds undersampled regions of benchmark manifold not covered by probe families, achieving gains on these "blind spots" while suppressing probe signals.

**Affected Hypotheses:** H-M2, H-M4

**Severity:** MEDIUM (Reduces detection power but doesn't invalidate entire approach)

**Mitigation Strategy:**
1. **Prevention:** Generate probe families via diversity sampling (cluster GSM8K problems, sample from each cluster) to maximize coverage
2. **Detection:** Adaptive adversary with probe access (Phase 3) empirically tests coverage via gain-vs-suppression curves
3. **Response:**
   - PIVOT: Augment probe families iteratively based on adversary-discovered blind spots
   - SCOPE: Accept reduced detection power (70-75% vs 80%) if blind spots are limited
   - ABORT: If adversary achieves >50% gains while suppressing all probes, coverage fundamentally inadequate

**Early Warning Indicators:**
- Adaptive adversary (λ>0) maintains >10% gains while reducing probe signals to near-zero
- Large variance in per-problem detection rates (some problems never detected)

---

**Risk R5: Scope Limitation to Finetuning Phase**

**Source Assumption:** A5 - Finetuning (not pretraining) is the dominant contamination risk for benchmark manipulation

**Description:** Hypothesis scope explicitly excludes pretraining contamination (where MIA AUC≈50%), limiting real-world applicability if pretraining contamination becomes prevalent attack vector.

**Affected Hypotheses:** All (scope boundary, not failure risk)

**Severity:** LOW (Acknowledged limitation, not invalidation)

**Mitigation Strategy:**
1. **Prevention:** N/A (scope decision based on prior evidence from Fu et al.)
2. **Detection:** Monitor field developments for pretraining contamination evidence
3. **Response:**
   - SCOPE: Document as known limitation in paper; suggest future work on pretraining geometric detection
   - PIVOT: If pretraining contamination becomes critical field problem, extend geometric approach to pretrain phase (higher measurement overhead)

**Early Warning Indicators:**
- N/A (scope limitation, not active risk)

---

### 3.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Likelihood |
|------|--------|---------------------|----------|------------|
| R1: Task-Agnostic Gains | A1 | H-E1, H-M2 | HIGH | Medium |
| R2: Smooth Evasion (Pareto Flat Region) | A2 | H-E1, H-M3, H-M4 | CRITICAL | Low |
| R3: TSG Extraction Quality | A3 | H-M2 | HIGH | Medium |
| R4: Incomplete Probe Coverage | A4 | H-M2, H-M4 | MEDIUM | Medium |
| R5: Finetuning Scope Limitation | A5 | All (scope boundary) | LOW | N/A |

### 3.3 Mitigation Strategies Summary

**Proactive Measures:**
1. **TSG Quality Validation (R3):** Invariant-breaking ablation + paraphrase clustering tests before main experiments
2. **Probe Diversity Sampling (R4):** Cluster-based probe generation to maximize manifold coverage
3. **Multi-Metric Geometric Coverage (R2):** 4 complementary metrics reduce single-dimension evasion risk
4. **Pilot Differential Alignment Check (R1):** Early detection via Δ monitoring on small-scale runs

**Adaptive Responses:**
- If R1 materializes → pivot to Tier 3-dominant detection
- If R2 materializes → tighten thresholds or accept reduced efficacy (60-70%)
- If R3 materializes → shift to code domain (HumanEval) where TSG more reliable
- If R4 materializes → iterative probe augmentation based on adversary blind spots

**Decision Gates:**
- ABORT if R2 shows full flat region (geometric inevitability falsified)
- ABORT if R3 + R1 both occur (Tier 2 fails + no task-specific learning)
- PIVOT if only R3 or R1 occur individually (Tier 3 or Tier 2 can compensate)

### 3.4 Risk Summary Table

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Task-Agnostic Gains | A1 | HIGH | H-E1, H-M2 | Pilot Δ monitoring, pivot to Tier 3 if fails |
| R2 | Pareto Flat Region | A2 | CRITICAL | H-E1, H-M3, H-M4 | Phase 3 adversary testing, ABORT if flat |
| R3 | TSG Quality | A3 | HIGH | H-M2 | Invariant-breaking ablation, pivot to code |
| R4 | Probe Coverage Gaps | A4 | MEDIUM | H-M2, H-M4 | Diversity sampling, iterative augmentation |
| R5 | Finetuning Scope | A5 | LOW | All (boundary) | Document limitation, future work |

**Risk Distribution:**
- Critical Risks: 1 (R2 - Pareto flat region)
- High Risks: 2 (R1, R3 - task-agnostic gains, TSG quality)
- Medium Risks: 1 (R4 - probe coverage)
- Low Risks: 1 (R5 - scope limitation)

**Critical Path:** R2 (geometric inevitability) is hypothesis-critical. Phase 3 adaptive adversary experiments directly test this risk.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## 4. Execution Plan

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
        DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════════════

[Level 0 - Foundation]
┌─────────────────────────────────────────────────────────────────┐
│ H-E1: Three-Tier Detection Achieves ≥80% Power @ <5% FPR       │
│ Gate: MUST_WORK                                                  │
│ Prerequisites: None                                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
[Level 1 - Tier Validation (Parallel)]
┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐
│ H-M1: Tier 1        │  │ H-M2: Tier 2        │  │ H-M3: Tier 3         │
│ Data-Layer          │  │ TSG + Diff Align    │  │ Geometric Sigs       │
│ Gate: MUST_WORK     │  │ Gate: MUST_WORK     │  │ Gate: MUST_WORK      │
│ Prereq: H-E1        │  │ Prereq: H-E1        │  │ Prereq: H-E1         │
└─────────────────────┘  └─────────────────────┘  └──────────────────────┘
                            │           │                  │
                            └───────────┴──────────────────┘
                                        ▼
[Level 2 - Robustness Testing]
┌─────────────────────────────────────────────────────────────────┐
│ H-M4: Pareto Frontier Convexity (Geometric Inevitability)      │
│ Gate: SHOULD_WORK                                                │
│ Prerequisites: H-M1, H-M2, H-M3 (all tiers validated)          │
└─────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → {H-M1, H-M2, H-M3} → H-M4
Total Depth: 3 levels
Parallelization: H-M1, H-M2, H-M3 can run concurrently after H-E1
═══════════════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

**Verification Order:**

**Phase 1: Foundation Establishment**
- H-E1: Three-tier system achieves target detection power
  - Status: READY (no prerequisites)
  - Gate: MUST_WORK - If fails, entire approach is invalid
  - Blocks: All other hypotheses

**Phase 2: Tier-Specific Validation (Parallel After H-E1)**
- H-M1: Tier 1 Data-Layer Detection
  - Status: BLOCKED (waiting on H-E1)
  - Gate: MUST_WORK - Tier 1 must catch accidental contamination
  - Prerequisites: H-E1 (EAL replication established)
  
- H-M2: Tier 2 TSG + Differential Alignment
  - Status: BLOCKED (waiting on H-E1)
  - Gate: MUST_WORK - Core novel contribution (paraphrase-invariant detection)
  - Prerequisites: H-E1 (contamination produces gains)
  - Risk: R3 (TSG quality) - high severity
  
- H-M3: Tier 3 Geometric Signatures
  - Status: BLOCKED (waiting on H-E1)
  - Gate: MUST_WORK - Validates geometric detection premise
  - Prerequisites: H-E1 (benchmark gains established)
  - Risk: R1, R2 (task-agnostic gains, Pareto evasion)

**Phase 3: Robustness Against Adaptive Adversaries**
- H-M4: Pareto Frontier Convexity
  - Status: BLOCKED (waiting on H-M1, H-M2, H-M3)
  - Gate: SHOULD_WORK - Strong test, but not hypothesis-critical
  - Prerequisites: All tier validations (H-M1, H-M2, H-M3)
  - Risk: R2 (CRITICAL) - tests geometric inevitability claim
  - Failure Mode: If flat region exists, document bounded efficacy

**Dependency Analysis:**
- **Total Hypotheses:** 5
- **Dependency Depth:** 3 levels (H-E1 → Tier validation → Robustness)
- **Critical Path Length:** H-E1 → H-M{1,2,3} → H-M4
- **Parallelization Potential:** High (3 tier hypotheses run concurrently)
- **Blocking Relationships:**
  - H-E1 blocks all (foundation)
  - H-M1, H-M2, H-M3 block H-M4 (require tier validation before adversary testing)
  
**Gate Failure Consequences:**
- H-E1 fails → ABORT (entire hypothesis invalid)
- H-M1 fails → PIVOT (Tier 1 optional, focus on Tier 2-3)
- H-M2 fails → EXPLORE (TSG quality issue, try code domain)
- H-M3 fails → PIVOT (geometric detection doesn't work, rely on behavioral)
- H-M4 fails → DOCUMENT (bounded evasion exists, detection still useful)

### 4.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
      VERIFICATION TIMELINE - 5 Hypotheses (Parallelized Tier Validation)
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ Week 1-2 │ Week 3   │ Week 4   │ Week 5   │ Week 6   │
─────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation
  H-E1 (3-Tier PoC)  │ ████████ │          │          │          │          │
  [Gate 1]           │          │ ◆        │          │          │          │
─────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Tier Validation (Parallel)
  H-M1 (Tier 1)      │          │ ████████ │          │          │          │
  H-M2 (Tier 2 TSG)  │          │ ████████ │          │          │          │
  H-M3 (Tier 3 Geo)  │          │ ████████ │          │          │          │
  [Gate 2]           │          │          │ ◆        │          │          │
─────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 3: Robustness
  H-M4 (Pareto)      │          │          │ ████████ │ ████████ │          │
  [Gate 3]           │          │          │          │          │ ◆        │
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point

Total Duration: 5 weeks
  - Sequential Path: 2 weeks (H-E1) + 1 week (Tiers parallel) + 2 weeks (H-M4)
  - Parallelization Benefit: 3 weeks saved (3 tiers × 1 week each → 1 week parallel)
═══════════════════════════════════════════════════════════════════════════════
```

### 4.4 Critical Path Analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Critical Path:** H-E1 → {H-M1 || H-M2 || H-M3} → H-M4

**Total Duration:** 5 weeks
- Phase 1 (Foundation): 2 weeks
  - H-E1: EAL replication + 3-tier detection validation
  - Gate 1: MUST_WORK - If fails, ABORT entire hypothesis
  
- Phase 2 (Tier Validation): 1 week (parallelized)
  - H-M1, H-M2, H-M3 run concurrently
  - Gate 2: All three tiers must show detection signal
  - Failure Mode: Individual tier failure documented, not blocking
  
- Phase 3 (Robustness): 2 weeks
  - H-M4: Adaptive adversary Pareto frontier measurement
  - Gate 3: SHOULD_WORK - Bounded evasion acceptable
  
**Parallelization Analysis:**
- Sequential Baseline: 2 + 3 + 2 = 7 weeks (if tiers run sequentially)
- Parallelized Schedule: 2 + 1 + 2 = 5 weeks (3 tiers concurrent)
- Time Saved: 2 weeks (29% reduction)

**Slack Analysis:**
- H-E1: 0 weeks slack (blocks all downstream)
- H-M1, H-M2, H-M3: Concurrent execution, no inter-tier dependencies
- H-M4: 0 weeks slack (final hypothesis)

**Gate Decision Points:**
- **Week 2 - Gate 1:** H-E1 must achieve ≥80% combined power @ <5% FPR
  - Pass → Continue to Phase 2
  - Fail → ABORT (hypothesis invalid)
  
- **Week 4 - Gate 2:** At least 2 of 3 tiers show >0% detection
  - Pass → Continue to H-M4
  - Fail → PIVOT (reassess tier architecture)
  
- **Week 6 - Gate 3:** Pareto frontier shows convex tradeoff
  - Pass → Strong evidence for geometric inevitability
  - Fail → Document bounded efficacy, proceed to writing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 4.5 Resource Summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Total Hypotheses:** 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0 (domain boundaries = constraints, not testable)

**Computational Resources:**
- GPU Requirements: 1× GPU per run (7B model finetuning)
- Parallel Runs: N=20 per condition → 20 GPUs for 1-week experiments
- Total GPU-Weeks: ~60 GPU-weeks (H-E1: 20, Phase 2: 20, H-M4: 20)

**Experiment Scale:**
- H-E1: 3 conditions × 20 runs = 60 training runs
- H-M1: 2 conditions × 20 runs = 40 runs (accidental vs adversarial)
- H-M2: 3 conditions × 20 runs = 60 runs (clean, 1%, 5%)
- H-M3: 2 conditions × 20 runs = 40 runs (clean vs 5%)
- H-M4: 5 λ values × 20 runs = 100 runs (adaptive adversary sweep)
- **Total Training Runs:** ~300 finetuning experiments

**Data Requirements:**
- GSM8K: Standard benchmark (train/test splits)
- Background Math: MATH, other reasoning datasets (~50K examples)
- Probe Families: 3000 probes per experiment (1K invariant, 1K neighbor, 1K control)

**Personnel:**
- Lead Researcher: 1 FTE (hypothesis design, analysis, writing)
- ML Engineer: 0.5 FTE (infrastructure, experiment orchestration)
- Compute Support: As needed (GPU cluster management)

**Timeline Flexibility:**
- Best Case: 4 weeks (if H-E1 completes Week 1, aggressive parallelization)
- Expected: 5 weeks (baseline schedule)
- Conservative: 7 weeks (sequential tier validation if infrastructure limits)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 4.6 Execution Order

**Execution Sequence (Optimized for Parallelization):**

1. **Week 1-2: Foundation (Sequential)**
   - H-E1: Replicate EAL protocol (clean, 1%, 5% injection)
   - Validate: Combined 3-tier detection achieves ≥80% power @ <5% FPR
   - Deliverable: Baseline contamination runs, detection power metrics
   - **Gate 1 Decision (Week 2):** MUST_WORK - Continue or ABORT

2. **Week 3: Tier Validation (Parallel)**
   - **Concurrent Execution:**
     - H-M1: Test Tier 1 on accidental vs adversarial contamination
     - H-M2: Measure TSG differential alignment Δ across clean/contaminated
     - H-M3: Compute 4 geometric metrics, count thresholds exceeded
   - Deliverable: Per-tier detection rates, mechanism validation
   - **Gate 2 Decision (Week 4):** ≥2 tiers show signal - Continue or PIVOT

3. **Week 4-5: Robustness Testing (Sequential)**
   - H-M4: Adaptive adversary training across λ ∈ {0, 0.1, 0.5, 1.0, 2.0}
   - Measure: Empirical Pareto frontier (gains vs detection probability)
   - Deliverable: Convexity analysis, geometric inevitability validation
   - **Gate 3 Decision (Week 6):** Convex tradeoff - Strong/Weak evidence

**Optimization Notes:**
- Phase 2 parallelization critical: 3 tiers run simultaneously (requires 60 GPUs)
- If GPU-limited: Run H-M1→H-M2→H-M3 sequentially (adds 2 weeks)
- H-M4 can begin after any 1 tier completes if early evidence needed

**Contingency Paths:**
- Gate 1 Fail → ABORT, no Phase 2
- Gate 2 Fail (0-1 tiers work) → PIVOT to single-tier architecture
- Gate 2 Partial (2 tiers work) → Continue, document tier failures
- Gate 3 Fail → Document bounded efficacy, proceed to paper

---

## 5. Dialectical Analysis

### 5.1 Thesis Statement

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Core Claim:** Under finetuning conditions with ≤5% targeted benchmark injection (EAL-style paraphrased contamination), if we apply a three-tier detection architecture combining data-layer filters, Task Signature Graph probes, and geometric trajectory auditing, then we achieve ≥80% combined detection power at <5% false positive rate even against adaptive adversaries, because contamination-induced benchmark gains (≥10% accuracy improvement) necessarily produce detectable geometric signatures (gradient subspace alignment, Hessian anisotropy, representational compression) that cannot be suppressed without sacrificing the performance advantage (Pareto constraint).

**Supporting Evidence:**
1. **Established Failure of Prior Methods:** MIA achieves AUC≈50% (random) in pretraining, TPR<2% against EAL paraphrasing (Fu et al., Dekoninck et al.) - instance-level detection demonstrably fails
2. **Geometric Alignment Necessity:** Achieving task-specific gains from limited data requires low-dimensional parameter alignment toward task manifolds (information-theoretic argument: 5% data → 15% gains implies efficient learning)
3. **Multi-Layer Complementary Architecture:** Tiers target independent signals (temporal/structural, behavioral dynamics, trajectory geometry) - evasion requires simultaneous suppression across orthogonal measurement dimensions

**Strengths:**
- **Paradigm Shift:** Moves from instance similarity (which fails) to learning-trajectory invariants (harder to evade)
- **Falsifiability:** 5 testable hypotheses with explicit quantitative thresholds and adaptive adversary validation
- **Theoretical Foundation:** Geometric inevitability provides structural limits on evasion (Pareto constraint), not just empirical cat-and-mouse
- **Practical Feasibility:** <2% training overhead, leverages existing infrastructure (timestamps, LSH), scales to 7B models

**Expected Outcomes:**
- Primary: Combined 3-tier detection ≥80% power @ <5% FPR on EAL-style contamination
- Secondary: Tier-specific differential (Tier 1: 95% accidental, <10% adversarial; Tier 2: Δ > 2σ; Tier 3: ≥2/4 metrics)
- Tertiary: Pareto frontier convexity (50% signal reduction → ≥30% gain loss)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 5.2 Antithesis Development

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Null Hypothesis (H0):** For training runs achieving ≥10% benchmark performance gains from ≤5% targeted data injection, the combined three-tier detection system achieves ≤20% detection power at 5% false positive rate, indicating contamination-induced gains do not produce reliably detectable multi-layer signatures distinguishable from clean training.

**Counter-Arguments:**

1. **Contamination Via General Capability Transfer (violates A1):**
   - Argument: Gains arise from broad reasoning improvements, not task-specific alignment
   - Evidence: If Δ = (ΔL_invariant - ΔL_neighbor) ≈ 0 despite gains, both probe types improve equally
   - Implication: Tier 2 differential alignment fails; geometric signatures may also be task-agnostic
   - Baseline Precedent: Transfer learning often produces broad improvements indistinguishable from targeted training

2. **Smooth Evasion via Geometric Orthogonalization (violates A2 - CRITICAL):**
   - Argument: Adaptive adversary discovers optimization path orthogonal to benchmark gradients that still produces gains
   - Evidence: Flat Pareto region (high gain + low signal) exists if alignment is not geometrically inevitable
   - Implication: Geometric inevitability theorem collapses; core theoretical framework invalid
   - Baseline Precedent: Adversarial training often finds unexpected evasion modes missed by theory

3. **TSG Extraction Captures Surface Artifacts (violates A3):**
   - Argument: TSG probes learn surface patterns (keyword co-occurrence, syntactic structure) rather than deep task constraints
   - Evidence: If paraphrased invariant probes cluster with neighbor probes instead of original invariants, TSGs encode shallow features
   - Implication: Tier 2 degrades to instance similarity, which EAL already evades (TPR<2%)
   - Baseline Precedent: Embedding-based detection fails under paraphrasing (documented in EAL paper)

4. **Probe Coverage Incompleteness (violates A4):**
   - Argument: Benchmark manifold has undersampled "blind spots" not covered by probe families
   - Evidence: Adaptive adversary with probe access maintains >10% gains while suppressing all probe signals
   - Implication: Detection power limited to ~60% even without geometric orthogonalization
   - Baseline Precedent: Adversarial examples often exploit distribution gaps in validation sets

**Potential Failure Points (Mapped to Risks):**
- **R2 (CRITICAL):** Pareto flat region exists - geometric inevitability falsified, H0 supported
- **R1 + R3 (HIGH):** Task-agnostic gains + TSG quality failure - both Tier 2 and Tier 3 fail, ≤20% power
- **R4 (MEDIUM):** Incomplete probe coverage reduces power to 50-60%, below 80% threshold

**Conditions Under Which H0 Would Be Supported:**
- If H-E1 fails: Combined detection <80% OR FPR >5% on baseline EAL replication
- If H-M4 fails critically: Flat Pareto region (adaptive adversary achieves ≥10% gains @ <5% detection)
- If H-M2 + H-M3 both fail: Tier 2 differential Δ < 2σ AND Tier 3 geometric metrics <2/4 thresholds
- If assumption violations compound: A1 + A3 both false (task-agnostic gains + TSG surface artifacts)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 5.3 Synthesis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Balanced Assessment:**

The hypothesis H-ContamGeometry-v1 presents a testable claim that contamination-induced gains produce detectable multi-layer geometric signatures due to inevitable parameter-space alignment with benchmark tasks. However, the null hypothesis raises valid concerns regarding whether gains can arise through task-agnostic pathways (violating geometric inevitability) or whether detection signals can be evaded via smooth optimization (Pareto flat region).

**Resolution Path:**

The verification plan addresses this dialectic through structured experimentation:

1. **Foundation Verification (H-E1, Week 1-2):**
   - Establishes existence before mechanism testing
   - Directly tests combined detection power claim (≥80% @ <5% FPR)
   - **Gate 1 (MUST_WORK):** If H-E1 fails, supports H0 → ABORT
   
2. **Tier-Specific Validation (H-M1-3, Week 3):**
   - Tests each detection layer independently to identify failure modes
   - Enables localization: Is failure in data-layer, behavioral, or geometric?
   - **Gate 2:** ≥2 tiers must show signal; if 0-1 tiers work, supports H0 partial validity
   
3. **Robustness Testing (H-M4, Week 4-5):**
   - Adaptive adversary directly tests geometric inevitability via Pareto frontier
   - Falsification-focused: Actively searches for flat region (evasion mode)
   - **Gate 3 (SHOULD_WORK):** Convex tradeoff confirms thesis; flat region supports H0

**Conditions for Thesis Support:**
- **Full Validation:** All 3 MUST_WORK gates pass (H-E1, H-M1-3 majority, H-M4 convex)
  - Combined detection ≥80%
  - At least 2 of 3 tiers show independent signals
  - Pareto frontier shows ≥0.6 slope (50% signal → 30% gain loss)
  - **Conclusion:** Geometric detection is viable; enables training-side monitoring
  
- **Strong Partial:** H-E1 passes, ≥2 tiers work, H-M4 weak (slope 0.4-0.6)
  - Detection works but bounded evasion exists
  - **Conclusion:** Geometric detection useful but not inevitable; document limits

**Conditions for Antithesis Support (H0):**
- **Critical Failure:** H-E1 fails (combined <80% OR FPR >5%)
  - **Conclusion:** Multi-tier architecture doesn't achieve target performance; H0 supported
  
- **Mechanism Breakdown:** H-M4 fails critically (flat Pareto region exists)
  - **Conclusion:** Geometric inevitability falsified; adversaries can evade; H0 supported
  
- **Cascading Failure:** H-M2 + H-M3 both fail (Tier 2 Δ < 2σ AND Tier 3 <2/4 metrics)
  - **Conclusion:** Novel contributions (TSG, geometric) don't work; only Tier 1 survives; H0 partially supported

**Nuanced Outcome Possibilities:**

1. **Full Thesis Validation (Expected Confidence: 0.60):**
   - All hypotheses pass gates, Pareto convex
   - **Action:** Proceed to Phase 6 paper writing with strong claims
   
2. **Partial Validation - Tier Subset (Expected Confidence: 0.25):**
   - H-E1 passes, but only 2 of 3 tiers work (e.g., Tier 1+3 work, Tier 2 TSG fails)
   - **Action:** Document working tiers, scope paper to proven mechanisms, recommend future TSG work
   
3. **Bounded Efficacy (Expected Confidence: 0.10):**
   - H-E1 passes at lower threshold (70% power), H-M4 shows weak convexity (slope 0.4)
   - **Action:** Accept reduced claims, emphasize complementary value with LiveCodeBench
   
4. **Hypothesis Falsification (Expected Confidence: 0.05):**
   - H-E1 fails OR H-M4 shows flat region
   - **Action:** ABORT paper, publish negative result, redirect to single-tier optimization

**Key Insight from Dialectic:**

The thesis-antithesis tension centers on **geometric inevitability** (R2 - CRITICAL risk). If contamination gains can be achieved via pathways orthogonal to detection signals, the entire theoretical framework collapses to H0. Phase 3 adaptive adversary experiments (H-M4) are designed as a *falsification test* - they actively search for the flat Pareto region that would support H0. This makes the verification plan genuinely adversarial to our own hypothesis, increasing credibility if thesis survives.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 5.4 Robustness Assessment

**Verification Plan Robustness:**

1. **Falsifiability:** ✅ Strong
   - 5 hypotheses with explicit quantitative thresholds
   - H-M4 adaptive adversary actively searches for counterexamples
   - Gate conditions provide early detection of H0 support
   - No ambiguous outcomes: Either ≥80% or <80%, either convex or flat

2. **Risk Mitigation:** ✅ Comprehensive
   - All 5 key assumptions (A1-A5) mapped to specific risks (R1-R5)
   - Proactive measures (TSG quality validation, probe diversity) before main experiments
   - Adaptive responses defined for each failure mode (PIVOT, SCOPE, ABORT)
   - Critical path testing: R2 (geometric inevitability) tested directly in H-M4

3. **Scope Appropriateness:** ✅ Realistic
   - Scoped to finetuning (where signals strongest per Fu et al.)
   - Scoped to structured domains (code/math where TSG reliable)
   - Scoped to 1-70B models (computational feasibility)
   - Acknowledged limitations (pretraining, open-NLP, <0.1% injection) upfront

4. **Dialectical Balance:** ✅ Adversarial
   - H0 integrated as antithesis throughout verification
   - Adaptive adversary experiments (H-M4) designed to falsify thesis
   - Multiple failure modes considered (not just binary pass/fail)
   - Nuanced outcomes acknowledged (full/partial/bounded/falsified)

5. **Resource Feasibility:** ✅ Achievable
   - 5 weeks total (parallelized)
   - ~300 training runs (60 GPU-weeks)
   - Standard infrastructure (7B models, existing datasets)
   - Personnel: 1 FTE researcher + 0.5 FTE ML engineer

**Identified Weaknesses:**

1. **TSG Extraction Quality (R3):** High-risk assumption with medium testability
   - Mitigation: Invariant-breaking ablation, pivot to code domain if math fails
   
2. **Single Domain Initial Validation:** Only testing GSM8K math reasoning
   - Mitigation: Domain generalization (P3) deferred to future work, scoped appropriately
   
3. **Pareto Inevitability:** Core theoretical claim rests on unproven geometric argument
   - Mitigation: H-M4 adaptive adversary provides empirical test; falsification-focused

**Overall Assessment:** The verification plan is robustly designed with strong falsifiability, comprehensive risk mitigation, and adversarial testing of core claims. The dialectical framework ensures that H0 support is detectable at multiple gate points rather than only after full experiment completion.

---

## 6. Summary & Conclusions

### 6.1 Executive Summary

**Main Hypothesis:** Three-tier contamination detection architecture (data + manifold + geometry layers) achieves ≥80% detection power @ <5% FPR on EAL-style paraphrased contamination, validated via geometric inevitability constraint (Pareto frontier convexity)

- **ID:** H-ContamGeometry-v1
- **Confidence:** 0.80
- **Scope Reduction:** 40% (4 established claims skipped, focus on 3 novel contributions)

**Verification Structure:**
- **Mode:** Incremental (Phase 2A pre-mapped structure)
- **Sub-Hypotheses:** 5 total (H-E1: Existence, H-M1-4: Mechanism tiers + robustness)
- **Timeline:** 3 phases over 5 weeks (parallelized tier validation Week 3)
- **Critical Gates:** 3 decision points (Foundation, Tier Validation, Pareto Testing)
- **Experimental Scale:** ~300 finetuning runs, 60 GPU-weeks

**Risk Assessment:** MEDIUM-HIGH
- **Critical Risk (R2):** Geometric inevitability unproven - Pareto flat region would falsify core claim
- **High Risks (R1, R3):** Task-agnostic gains, TSG extraction quality
- **Mitigation:** Adaptive adversary testing (H-M4), invariant-breaking ablation, code domain pivot

**Success Criteria:**
- All 3 MUST_WORK gates pass (H-E1, H-M1-3 majority, H-M4 convex)
- Combined detection ≥80%, at least 2 tiers independently signal, Pareto slope ≥0.6

**Immediate Action:** Phase 1 (Week 1-2) - Replicate EAL protocol, validate H-E1 combined detection

---

### 6.2 Verification Roadmap

**Phase 1: Foundation Establishment (Week 1-2)**
- **H-E1:** Three-tier system achieves ≥80% combined detection @ <5% FPR
  - Experimental Setup: N=20 runs × 3 conditions (clean, 1%, 5% injection)
  - Deliverable: Baseline contamination runs, per-tier detection rates
  - **Gate 1 (Week 2):** MUST_WORK - Continue or ABORT

**Phase 2: Tier-Specific Validation (Week 3, Parallel)**
- **H-M1:** Tier 1 data-layer catches ≥95% accidental, <10% adversarial
- **H-M2:** Tier 2 TSG differential alignment Δ > 2σ for 5% injection
- **H-M3:** Tier 3 geometric metrics ≥2 of 4 exceed thresholds
  - Concurrent Execution: 3 hypotheses run simultaneously (60 GPUs)
  - **Gate 2 (Week 4):** ≥2 tiers show signal - Continue or PIVOT

**Phase 3: Robustness Testing (Week 4-5)**
- **H-M4:** Adaptive adversary Pareto frontier shows convex tradeoff
  - Experimental Setup: λ ∈ {0, 0.1, 0.5, 1.0, 2.0} × 20 runs
  - Deliverable: Empirical Pareto curve, geometric inevitability validation
  - **Gate 3 (Week 6):** Convex tradeoff confirmed - Strong/Weak evidence

**Critical Path Dependencies:**
```
H-E1 (Week 1-2) → {H-M1 || H-M2 || H-M3} (Week 3) → H-M4 (Week 4-5)
```

---

### 6.3 Key Findings from Planning

**Theoretical Contributions:**
1. **Paradigm Shift:** Instance-level detection (fails: MIA AUC≈50%, TPR<2% vs EAL) → Learning-trajectory geometry (inevitable if gains require alignment)
2. **Geometric Inevitability Theorem:** Contamination gains fundamentally coupled to detectable parameter-space signatures (Pareto constraint limits evasion)
3. **Differential Alignment Metric:** Δ = (ΔL_invariant - ΔL_neighbor) separates contamination from general skill transfer
4. **Task Signature Graphs:** Paraphrase-invariant constraint manifolds for behavioral probing

**Experimental Design Strengths:**
- **Falsification-Focused:** H-M4 adaptive adversary actively searches for counterexamples (flat Pareto region)
- **Multi-Gate Structure:** Early detection of H0 support (Week 2, 4, 6) prevents wasted effort
- **Tier Independence:** Parallel validation (Week 3) enables localization of failure modes
- **Scope Reduction:** 40% efficiency gain by building on established facts (MIA failure, EAL evasion)

**Identified Challenges:**
- **TSG Quality (R3 - HIGH):** Math domain TSG extraction may capture surface artifacts; mitigation via code domain pivot
- **Geometric Inevitability (R2 - CRITICAL):** Core theoretical claim unproven; empirical Pareto test required
- **Probe Coverage (R4 - MEDIUM):** Adversary may find manifold blind spots; iterative augmentation needed

**Decision Framework:**
- **Full Validation (60% expected):** All gates pass → Proceed to paper with strong claims
- **Partial Validation (25% expected):** 2 of 3 tiers work → Document working subset, scope paper
- **Bounded Efficacy (10% expected):** 70% power, weak Pareto → Accept reduced claims
- **Falsification (5% expected):** H-E1 or H-M4 critical fail → ABORT, publish negative result

---

### 6.4 Recommendations

**Pre-Experiment Preparation:**
1. **TSG Quality Validation (Before Week 1):**
   - Run invariant-breaking ablation on pilot GSM8K probes
   - Test paraphrase clustering: Do GPT-4 rephrased invariants cluster with originals?
   - Decision: If quality low, pivot to HumanEval (code domain) for main experiments

2. **Threshold Calibration (Week 1):**
   - Use clean baseline runs to set Tier 3 geometric thresholds (target <5% FPR)
   - Pre-register thresholds before contaminated runs to prevent p-hacking

3. **Infrastructure Setup:**
   - GPU cluster: 60 concurrent runs for Phase 2 parallelization
   - Probe generator: Automated TSG extraction + diversity sampling
   - Logging: Gradient/Hessian checkpoints every 100 steps (~2% overhead)

**Contingency Plans:**
- **If H-E1 fails (≤80% power):** Analyze per-tier breakdown; if 1 tier fails, explore single-tier optimization before ABORT
- **If H-M2 fails (Δ < 2σ):** Check TSG quality via ablation; pivot to code domain or geometric-only detection
- **If H-M4 shows flat region:** Document bounded efficacy; position as "partial evasion exists but detection still useful"

**Post-Experiment Extensions:**
- **Domain Generalization:** Validate on HumanEval (code) and MATH (formal reasoning) after GSM8K
- **Pretraining Extension:** If finetuning validation succeeds, explore scaled geometric detection for pretrain phase
- **Ecosystem Pilot:** Partner with 1-2 benchmark leaderboards for audit trail adoption (e.g., HumanEval competition)

---

### 6.5 Appendices

**Appendix A: Hypothesis Inventory Quick Reference**

| ID | Type | Statement (Brief) | Gate | Prerequisites | Duration |
|----|------|-------------------|------|---------------|----------|
| H-E1 | Existence | 3-tier ≥80% power @ <5% FPR | MUST_WORK | None | 2 weeks |
| H-M1 | Mechanism | Tier 1: 95% accidental, <10% adversarial | MUST_WORK | H-E1 | 1 week |
| H-M2 | Mechanism | Tier 2: Δ > 2σ for 5% injection | MUST_WORK | H-E1 | 1 week |
| H-M3 | Mechanism | Tier 3: ≥2 of 4 metrics exceed | MUST_WORK | H-E1 | 1 week |
| H-M4 | Mechanism | Pareto convex (slope ≥0.6) | SHOULD_WORK | H-M1-3 | 2 weeks |

**Appendix B: Risk Matrix**

| Risk | Severity | Likelihood | Affected | Mitigation | Abort Condition |
|------|----------|------------|----------|------------|-----------------|
| R1: Task-Agnostic Gains | HIGH | Medium | H-E1, H-M2 | Pilot Δ monitoring | A1 + A3 both false |
| R2: Pareto Flat Region | CRITICAL | Low | H-E1, H-M3, H-M4 | Adaptive adversary test | Flat region exists |
| R3: TSG Quality | HIGH | Medium | H-M2 | Invariant-breaking ablation | TSG = surface artifacts |
| R4: Probe Coverage | MEDIUM | Medium | H-M2, H-M4 | Diversity sampling | >50% gains @ 0 signal |
| R5: Finetuning Scope | LOW | N/A | All | Document limitation | N/A (scope boundary) |

**Appendix C: Experimental Conditions Summary**

| Hypothesis | Conditions | Runs per Condition | Total Runs | GPU-Weeks |
|------------|------------|-------------------|------------|-----------|
| H-E1 | Clean, 1%, 5% | 20 | 60 | 20 |
| H-M1 | Accidental, Adversarial | 20 | 40 | 13 |
| H-M2 | Clean, 1%, 5% | 20 | 60 | 20 |
| H-M3 | Clean, 5% | 20 | 40 | 13 |
| H-M4 | λ = {0, 0.1, 0.5, 1.0, 2.0} | 20 | 100 | 33 |
| **TOTAL** | | | **~300** | **~99** |

Note: GPU-week estimates assume 7B model, 3 epochs, ~1 GPU-day per run

**Appendix D: Glossary of Key Terms**

- **EAL (Evading Data Contamination Detection):** Attack technique using GPT-4 paraphrasing to inject benchmark data while evading semantic similarity detection (Dekoninck et al. 2024)
- **TSG (Task Signature Graph):** Abstract constraint manifold extracted via program synthesis, designed to be paraphrase-invariant
- **Differential Alignment (Δ):** Metric = (ΔL_invariant - ΔL_neighbor), separates contamination-specific from general learning
- **Geometric Inevitability:** Theoretical claim that achieving task-specific gains requires detectable parameter-space alignment (Pareto constraint)
- **Pareto Frontier:** Empirical tradeoff curve between benchmark gains and detection probability under adaptive adversary training

---

## 7. Pipeline Status

### 7.1 Verification State

**verification_state.yaml Status:** ✅ CREATED

- **File Location:** `docs/youra_research/20260511_data_problems/verification_state.yaml`
- **Schema Version:** v3.0
- **Total Sub-Hypotheses:** 5
- **Ready for Execution:** h-e1 (no prerequisites)
- **Blocked (awaiting prerequisites):** h-m1, h-m2, h-m3 (waiting on h-e1), h-m4 (waiting on h-m1, h-m2, h-m3)

**State File Structure:**
```yaml
sub_hypotheses:
  h-e1: {status: READY, gate: MUST_WORK, prerequisites: []}
  h-m1: {status: NOT_STARTED, gate: MUST_WORK, prerequisites: [h-e1]}
  h-m2: {status: NOT_STARTED, gate: MUST_WORK, prerequisites: [h-e1]}
  h-m3: {status: NOT_STARTED, gate: MUST_WORK, prerequisites: [h-e1]}
  h-m4: {status: NOT_STARTED, gate: SHOULD_WORK, prerequisites: [h-m1, h-m2, h-m3]}
```

**Next Action:** Execute hypothesis-loop or hypothesis-next skill to begin Phase 2C → 3 → 4 verification cycle for h-e1

### 7.2 Pipeline Tasks

**Archon Pipeline Tasks Updated:**

| Task | Previous Status | New Status | Task ID |
|------|----------------|------------|---------|
| Phase 2B - Planning | doing | ✅ **done** | d268a70d-8cb5-4675-b712-94d2a37a95f2 |
| Phase 2C - Experiment | todo | ✅ **doing** | 308929c1-3fd2-4c5c-88ca-7b78d20756e0 |

**Pipeline Project:** Anonymous Pipeline: Data Problems in Foundation Models (ID: 1ffd7e3a-2ec3-4c75-a523-e72f0340d0b3)

### 7.3 Hypothesis Tasks

**Hypothesis Tasks Created in Archon:**

| Hypothesis | Task ID | Status | Description |
|------------|---------|--------|-------------|
| H-E1 | f059f21b-132c-4fe7-9945-ab1790bbc0d6 | todo | Three-tier detection ≥80% power @ <5% FPR |
| H-M1 | f507a6bf-0109-482e-85c6-819c673def3b | todo | Tier 1: ≥95% accidental, <10% adversarial |
| H-M2 | 47402101-ac76-4425-aa69-e27a6c2cabe6 | todo | Tier 2: Δ > 2σ for 5% injection |
| H-M3 | 426caa6b-b2ed-48e6-bd0b-71f394444e82 | todo | Tier 3: ≥2 of 4 metrics exceed thresholds |
| H-M4 | 050e972f-58ae-4333-923b-71d0d70adf59 | todo | Pareto convex: 50% signal → ≥30% gain loss |

**Task-Hypothesis Mapping:** Stored in verification_state.yaml metadata for Phase 2C-4 tracking

---

## ✅ Phase 2B Planning Complete

**Generated Artifacts:**
1. ✅ `02b_verification_plan.md` (this file) - Complete verification roadmap
2. ✅ `verification_state.yaml` - Hypothesis state tracker for automation
3. ✅ 5 Hypothesis tasks in Archon Pipeline Project
4. ✅ Pipeline status updated: Phase 2B → done, Phase 2C → doing

**Key Achievements:**
- 5 sub-hypotheses defined with explicit gates and dependencies
- 40% scope reduction via established facts (BUILD_ON claims)
- 5-week parallelized timeline (vs 7 weeks sequential)
- Risk analysis complete with 5 risks mapped to mitigation strategies
- Dialectical evaluation (thesis-antithesis-synthesis) validates robustness

**Next Phase:** Phase 2C - Experiment Design
- Command: `/hypothesis-next` or `/hypothesis-loop` to begin automated verification cycle
- First Hypothesis: H-E1 (READY - no prerequisites)
- Expected Output: Detailed experiment specification document for H-E1
