# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1: FEASIBLE ✅)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H1-1-EXT
**Confidence Level:** 0.82 (High Confidence)

**Main Hypothesis:**
A federated pluralistic alignment system using LoRA adapters (rank r=32) trained locally at stakeholder sites (N=10-100 pilot, scaling to 1000+), aggregated via weighted FedAvg with value clustering (k=5-10), and routed via mixture-of-experts (MoE) achieves production-scale deployment (<10ms inference latency) while preserving privacy (ε-differential privacy with ε=0.5-1.0, membership inference attack success <55%) and maintaining value diversity (per-group win rate ≥90% of centralized PAL baseline).

**Alternative Hypothesis (H0):**
Federated LoRA adapter training either (1) fails to converge to useful adapters due to extreme heterogeneity across stakeholder groups (per-group win rate <70% of centralized baseline), OR (2) cannot achieve production performance metrics (inference latency >50ms or privacy leakage with membership inference success >70%), OR (3) degrades value diversity through weighted aggregation (per-group satisfaction variance increases >50% vs. centralized approach).

### 1.2 Variables

| Variable Type | Variable Name | Definition | Measurement | Range/Values |
|--------------|---------------|------------|-------------|--------------|
| **Independent** | Number of stakeholder groups (N) | Count of distinct value-based groups participating in federation | Group count | Pilot: 10-100, Scale: 1000+ |
| **Independent** | LoRA adapter rank (r) | Rank of low-rank decomposition matrices in adapter layers | Integer hyperparameter | 16, 32, 64 |
| **Independent** | Privacy budget (ε) | Differential privacy epsilon parameter for adapter aggregation | Privacy parameter | 0.5, 0.75, 1.0 |
| **Independent** | Value clustering granularity (k) | Number of stakeholder clusters for weighted FedAvg | Integer hyperparameter | 5, 7, 10 |
| **Independent** | Federated training rounds (T) | Number of communication rounds between local training and aggregation | Integer | 10, 20, 50 |
| **Dependent** | Inference latency | End-to-end response generation time from query to output | Milliseconds (p95) | Target: <10ms, Failure: >50ms |
| **Dependent** | Per-group win rate | Fraction of responses preferred over baseline for each stakeholder group | Percentage vs. PAL baseline | Success: ≥90%, Failure: <70% |
| **Dependent** | Privacy leakage | Membership inference attack success rate on adapter parameters | Attack accuracy | Success: <55%, Failure: >70% |
| **Dependent** | Router accuracy | MoE router's correctness in selecting appropriate adapter(s) for query | Percentage correct routing | Target: >85% |
| **Dependent** | Training cost per group | GPU-hours required for local LoRA adapter training | GPU-hours | Target: <1 GPU-hour |
| **Dependent** | Communication overhead | Total data transmitted per training round (all groups) | MB per round | Acceptable: <100MB for 100 groups |
| **Controlled** | Base LLM architecture | Foundation model used for adapter attachment | Model family | Llama-3-8B or similar 7B-13B model |
| **Controlled** | Preference dataset size per group | Number of preference pairs available for local training | Integer count | ≥100 preference pairs |
| **Controlled** | Hardware infrastructure | Cloud federation platform for distributed training | Platform | TensorFlow Federated or PySyft |
| **Controlled** | Aggregation algorithm | Method for combining adapter parameters across groups | Algorithm | Weighted FedAvg with clustering |

### 1.3 Causal Mechanism

**Mechanism Diagram:**
```
[Stakeholder Group Value Data]
    ↓ (local training)
[LoRA Adapter Parameters]
    ↓ (encrypted upload with ε-DP noise)
[Clustered Weighted FedAvg Aggregation]
    ↓ (value similarity clustering)
[Federated Adapter Pool]
    ↓ (MoE routing based on query/user metadata)
[Value-Conditioned Response Generation]
```

**Step 1: Local Adapter Training → Value Specialization**
- **Mechanism:** Each stakeholder group trains LoRA adapter (rank r=32, ~500K parameters) on local preference dataset (≥100 pairs) using Direct Preference Optimization (DPO)
- **Why this causes effect:** LoRA's low-rank factorization learns group-specific value patterns in parameter space without modifying base model weights. DPO directly optimizes for preference alignment without requiring reward model training.
- **Evidence:** Hu et al. (2021) demonstrates LoRA adapters capture task-specific patterns with 0.01% trainable parameters. VPL (Poddar et al., NeurIPS 2024) shows personalized LoRA adapters achieve quick adaptation without retraining base model.

**Step 2: Weighted FedAvg + Clustering → Privacy-Preserving Value Aggregation**
- **Mechanism:** Stakeholder groups upload encrypted adapter parameters with ε-DP noise (ε=0.5-1.0). Central server clusters groups by preference embedding similarity (k=5-10 clusters), applies weighted FedAvg within/across clusters.
- **Why this causes effect:** Clustering prevents extreme heterogeneity from degrading FedAvg convergence (addresses non-IID data challenge). Weights balance representation across diverse group sizes. ε-DP noise prevents individual preference reconstruction.
- **Evidence:** McMahan et al. (2017) proves FedAvg convergence for distributed neural network training. Kairouz et al. (2021) demonstrates differential privacy in federated settings prevents membership inference. PAL (Chen et al., 2024) shows value-group separation preserves diversity vs. averaging.

**Step 3: MoE Routing → Dynamic Value Selection**
- **Mechanism:** Lightweight router network (100M parameters) trained with multi-source signals (user demographics, explicit stakeholder selection, query embedding similarity) selects 1-3 adapters to activate for each query.
- **Why this causes effect:** MoE architecture enables conditional computation - only relevant value adapters contribute to response generation. Multi-source routing signals provide rich context for value alignment matching.
- **Evidence:** Mixtral (Shazeer et al.) demonstrates MoE routing achieves SOTA with sparse activation. Modular Pluralism (Feng et al., 2024) validates pluggable community LMs work for pluralistic alignment. GDPO (Yao et al., 2024) shows belief-conditioned preferences outperform averaged models.

**Evidence for Causal Links:**

1. **Local Training → Value Specialization:**
   - [SCHOLAR] LoRA paper (Hu et al., 2021): 0.1-1% parameters sufficient for task adaptation
   - [SCHOLAR] VPL (Poddar et al., 2024): Personalized adapters achieve quick value alignment
   - [EXA] PEFT library: Production-stable LoRA implementation with 5-10x faster training

2. **Weighted Aggregation → Privacy + Diversity:**
   - [SCHOLAR] Federated Learning survey (Kairouz et al., 2021): ε-DP prevents individual data leakage
   - [SCHOLAR] PAL (Chen et al., 2024): Value-group separation preserves heterogeneous preferences
   - [ARCHON] InstructGPT case: Production RLHF demonstrates alignment scalability exists

3. **MoE Routing → Dynamic Selection:**
   - [EXA] Mixtral implementation: MoE routing proven at production scale
   - [SCHOLAR] Modular Pluralism (Feng et al., 2024): Pluggable community LMs validate modular architecture
   - [SCHOLAR] GDPO (Yao et al., 2024): Belief-conditioned preferences outperform averaging

**Key Tension:**
The fundamental tension is between **privacy preservation** (requiring ε-DP noise addition) and **value diversity preservation** (requiring faithful representation of group preferences). Stronger privacy (lower ε) adds more noise to adapter parameters, potentially degrading per-group alignment quality. Weighted FedAvg with clustering is proposed to mitigate this by grouping similar value systems before aggregation, but empirical validation is needed to confirm the privacy-diversity trade-off is acceptable (hypothesis predicts ≥90% baseline performance with ε=0.5-1.0).

### 1.4 Key Assumptions

1. **Stakeholder Group Definability:** Meaningful value-based groups can be identified through participatory workshops + demographic proxies + opt-in communities. Groups have sufficient internal value coherence (intra-group preference agreement >60%) and inter-group distinctiveness (cross-group agreement <40%).

2. **Preference Data Availability:** Each stakeholder group can collect ≥100 preference pairs via crowdsourcing, surveys, or synthetic generation. Preference data quality is sufficient for DPO training (clear win/loss signals, not ambiguous ties).

3. **FedAvg Convergence for LoRA:** Federated averaging algorithm proven for neural network weights extends to LoRA adapter parameters. Weighted FedAvg with value clustering (k=5-10) prevents extreme heterogeneity from blocking convergence.

4. **Privacy-Utility Trade-off Acceptability:** ε-DP noise with ε=0.5-1.0 provides meaningful privacy guarantees (membership inference <55%) while preserving sufficient adapter quality (≥90% baseline performance). This specific range is testable assumption.

5. **Router Training Signal Quality:** User metadata + preference embeddings + explicit stakeholder selection provide sufficient routing signals for >85% router accuracy. Poor routing degrades system to baseline performance (fallback assumption: ensemble routing as safety mechanism).

6. **Base LLM Capability Foundation:** 7B-13B parameter foundation model (Llama-3-8B or similar) provides sufficient general capability for value-conditioned response generation. Adapter modifications can steer values without requiring larger base model.

7. **Network Bandwidth Feasibility:** Cloud infrastructure supports 10MB adapter uploads per group per round (total: 100MB for 100 groups, 10GB for 1000 groups). Communication cost is acceptable for federated training economics.

8. **Stakeholder Participation Willingness:** Stakeholder groups participate if ε-DP privacy guarantees provided. Privacy preservation is primary blocker to participation, not coordination costs or technical complexity.

### 1.5 Scope & Boundaries

**Applies to:**
- Multi-stakeholder value alignment scenarios with ≥10 distinct groups (e.g., political orientations, cultural communities, professional domains, religious traditions)
- Cloud-deployed LLM systems with network connectivity for federated training
- Text-based preference optimization using DPO/PPO methods
- Domains where privacy is critical: political values, religious beliefs, cultural norms, sensitive moral judgments
- Production environments requiring <10ms inference latency and ≥90% value satisfaction

**Does NOT apply to:**
- Single-stakeholder or universal alignment (use standard RLHF - federated overhead unjustified)
- Edge deployment without network connectivity (cannot perform federated aggregation)
- Non-text modalities (image/video generation - adapter mechanisms may differ)
- <10 stakeholder groups (centralized training may be more efficient at small scale)
- Extremely latency-sensitive applications requiring <1ms response (MoE routing adds overhead)
- Domains where privacy is not a concern (centralized PAL/GDPO may be simpler)

**Known Limitations:**

1. **Cold Start Problem:** New stakeholder groups joining federation require ≥100 preference pairs. Mitigation: Warm-start from similar existing groups (transfer learning) or use synthetic preference generation.

2. **Router Quality Criticality:** MoE router failure (poor routing accuracy) negates modular architecture benefits. System degrades to averaged adapter performance. Mitigation: Ensemble routing or default adapter fallback.

3. **Privacy-Utility Trade-off:** Stronger privacy (lower ε) reduces adapter quality. Hypothesis predicts acceptable trade-off at ε=0.5-1.0 but this is empirical claim requiring validation.

4. **Value Clustering Dependency:** Weighted FedAvg assumes value similarity can be approximated via preference embedding clustering. If stakeholder values are truly orthogonal (not clusterable), aggregation may fail.

5. **Stakeholder Group Boundary Ambiguity:** Real-world value boundaries are fuzzy (individuals belong to multiple overlapping groups). Hypothesis assumes clean group definitions, but deployment requires governance mechanisms for multi-group membership.

6. **Communication Overhead Scaling:** Linear growth in bandwidth (10MB × N groups × T rounds). At 1000 groups with 50 rounds: 500GB total communication. May require batch aggregation strategies or longer intervals between rounds.

7. **Temporal Value Drift:** Stakeholder values may change over time. Hypothesis focuses on snapshot alignment, not longitudinal value evolution. Requires periodic adapter retraining mechanisms.

8. **Incommensurable Value Systems:** Some value conflicts may be genuinely irreconcilable (e.g., absolute religious principles vs. secular pluralism). Hypothesis assumes value diversity can be preserved through separation, but some conflicts may require explicit meta-framework for resolution.

### 1.6 Testable Predictions

**Primary Prediction (P1):**
**IF** federated LoRA system deployed with r=32, ε=0.75, k=7 clusters, N=50 stakeholder groups, T=20 training rounds on cloud infrastructure (TensorFlow Federated),
**THEN** per-group win rate ≥90% of centralized PAL baseline (measured via pairwise preference evaluation with 100 held-out test queries per group) AND inference latency p95 <10ms AND membership inference attack success <55% (tested with 1000 synthetic membership queries per group).

**Measurement Protocol:** Deploy pilot system with 50 stakeholder groups from 5 domains (political: 10 groups, cultural: 10 groups, professional: 10 groups, religious: 10 groups, generational: 10 groups). Collect ≥100 preference pairs per group. Train centralized PAL baseline on pooled data. Train federated system with specified hyperparameters. Evaluate on held-out test set with human preference ratings (500 raters per group, balanced demographics). Measure latency on production hardware (A100 GPUs). Run membership inference attacks using Yeom et al. (2018) methodology.

**Secondary Predictions:**

**P2 (Training Efficiency):**
**IF** LoRA rank r=32 used for local adapter training,
**THEN** training cost per group <1 GPU-hour on A100 (8-bit quantized training, batch size 8, 3 epochs over 100 preference pairs).

**Measurement:** Log GPU-hours during local training phase across all 50 pilot groups. Report mean, median, p95 training time.

**P3 (Router Accuracy):**
**IF** MoE router trained with multi-source signals (user demographics + query embedding similarity to group preferences + explicit stakeholder selection when available),
**THEN** routing accuracy >85% (measured as fraction of queries where activated adapter(s) match ground-truth stakeholder group membership, validated on 1000 labeled test queries with known stakeholder affiliation).

**Measurement:** Construct test set with explicit stakeholder labels. Compare router selections to ground truth. Report top-1 accuracy, top-3 accuracy, and confusion matrix across stakeholder groups.

**P4 (Privacy-Utility Trade-off):**
**IF** differential privacy budget ε varies in range [0.5, 0.75, 1.0],
**THEN** per-group win rate decreases monotonically as ε decreases (stronger privacy → lower utility), BUT remains ≥90% baseline even at ε=0.5.

**Measurement:** Train 3 federated systems with identical settings except ε. Plot per-group win rate vs. ε. Conduct paired t-tests between ε configurations. Verify monotonic relationship and threshold condition.

**P5 (Scalability):**
**IF** system scaled from N=50 pilot groups to N=500 groups,
**THEN** inference latency increases <2x (from ~8ms to <16ms, remaining below 10ms target with optimized MoE routing) AND communication overhead per round remains <5GB (500 groups × 10MB).

**Measurement:** Simulate 500-group deployment using adapter replication (sample from pilot group adapters to create synthetic 500-group pool). Measure latency with varying active adapter counts. Estimate bandwidth from adapter size × group count.

**Falsification Criteria:**

The hypothesis is **FALSIFIED** if any of the following occur:

1. **Value Diversity Failure:** Per-group win rate <70% of centralized PAL baseline for >20% of stakeholder groups (indicating federated approach fundamentally degrades value representation)

2. **Privacy Failure:** Membership inference attack success >70% (near-deterministic privacy leakage, indicating ε-DP insufficient)

3. **Performance Failure:** Inference latency p95 >50ms on production hardware (indicating MoE routing overhead is prohibitive for real-time applications)

4. **Convergence Failure:** Weighted FedAvg fails to converge within 100 training rounds (training loss plateau or divergence, indicating extreme heterogeneity breaks aggregation)

5. **Router Failure:** MoE routing accuracy <60% (near-random selection, indicating routing signals insufficient)

**Partial Success Scenarios:**
- If per-group win rate is 80-89% baseline: Hypothesis partially supported, requires optimization (higher r, different aggregation weighting, etc.)
- If latency is 10-20ms: Acceptable for non-real-time applications, requires engineering optimization for interactive use cases
- If privacy leakage is 55-70%: Privacy guarantees weaker than claimed but may be acceptable depending on stakeholder risk tolerance

### 1.7 SOTA Baseline

**Benchmark Systems:**

1. **PAL (Chen et al., 2024) - Centralized Ideal Point Model**
   - Architecture: Centralized training with ideal point model capturing heterogeneous preferences via MLP layers
   - Performance: Competitive accuracy with efficient neural architecture
   - Limitation: Centralized data requirement (all preference data pooled), no privacy guarantees
   - Comparison: Hypothesis predicts ≥90% of PAL's per-group win rate while adding privacy (ε-DP) and scalability (federated architecture)

2. **GDPO (Yao et al., 2024) - Group Distributional Preference Optimization**
   - Architecture: Centralized belief-conditioned preference optimization with statistical estimation of group distributions
   - Performance: Outperforms DPO on pluralistic alignment benchmarks
   - Limitation: Centralized training, requires access to all group belief distributions
   - Comparison: Hypothesis predicts comparable or better value diversity (per-group satisfaction) with added privacy through federated training

3. **VPL (Poddar et al., 2024, NeurIPS Spotlight) - Variational Preference Learning**
   - Architecture: Personalized reward models for diverse users, LoRA-based quick adaptation
   - Performance: Learns "what different users want" without averaging over underrepresented groups
   - Limitation: Centralized personalization, individual-level not stakeholder-group level
   - Comparison: Hypothesis extends VPL's LoRA personalization to federated multi-stakeholder setting with privacy guarantees

4. **Modular Pluralism (Feng et al., 2024) - Multi-LLM Collaboration**
   - Architecture: Base LLM + pool of specialized community LMs, three pluralism modes (Overton, steerable, distributional)
   - Performance: Compatible with black-box LLMs, modular control for adding community LMs
   - Limitation: No privacy mechanism discussed, centralized community LM training assumed
   - Comparison: Hypothesis uses similar modular adapter architecture but adds federated training for privacy and explicit ε-DP guarantees

**SOTA Performance Targets:**

| Metric | PAL Baseline | GDPO Baseline | VPL Baseline | Modular Pluralism | **Hypothesis Target** |
|--------|--------------|---------------|--------------|-------------------|---------------------|
| Per-group win rate | 100% (reference) | ~105% of DPO | High personalization | High pluralism score | ≥90% of PAL |
| Privacy guarantee | None (centralized) | None (centralized) | None (centralized) | None documented | ε-DP (ε=0.5-1.0), MI attack <55% |
| Inference latency | ~5-8ms (standard LLM) | ~5-8ms | ~5-8ms | ~10-15ms (multi-LLM routing) | <10ms (MoE routing optimized) |
| Training cost | High (full centralized) | High (centralized) | Medium (LoRA) | Medium (community LMs) | Low (<1 GPU-hour per group) |
| Scalability | Limited by centralization | Limited by centralization | Limited by centralization | Modular but no federation | 1000+ groups via federation |

**Competitive Positioning:**
The hypothesis aims for **Pareto improvement** over existing SOTA:
- **Privacy:** Novel contribution (no existing pluralistic alignment work provides ε-DP)
- **Scalability:** Federated architecture enables 1000+ groups (vs. centralized bottleneck)
- **Value Diversity:** Targeting ≥90% of PAL performance (minor trade-off for major privacy/scalability gains)
- **Efficiency:** LoRA adapters reduce training cost vs. full finetuning

**If hypothesis achieves targets:** First production-ready pluralistic alignment system with privacy guarantees and proven scalability.

**If hypothesis falls short:** Still contributes federated learning methodology to pluralistic alignment field, even if performance gap to centralized baselines is larger than predicted.

### 1.8 Statistical Verification Design

**Study Design:** Randomized controlled trial with within-subjects design (each stakeholder group evaluated on both federated and centralized systems)

**Sample Size Calculation:**
- **Stakeholder groups:** N=50 pilot groups (power analysis: detect ≥10% performance difference with 80% power, α=0.05)
- **Preference pairs per group:** ≥100 training pairs + 100 held-out test pairs
- **Human raters:** 500 raters per group for test evaluation (balanced demographics to match group composition)
- **Total preference evaluations:** 50 groups × 100 test queries × 500 raters = 2,500,000 pairwise comparisons

**Primary Outcome Measure:**
**Per-group win rate** = (Responses preferred over PAL baseline) / (Total test queries) per stakeholder group

**Statistical Tests:**

1. **Primary Hypothesis Test (P1):**
   - **Null hypothesis (H0):** Mean per-group win rate across 50 groups ≤ 80% of PAL baseline
   - **Alternative hypothesis (H1):** Mean per-group win rate ≥ 90% of PAL baseline
   - **Test:** One-sample t-test (comparing mean win rate to 90% threshold)
   - **Significance level:** α = 0.05
   - **Expected effect size:** Cohen's d ≈ 0.5 (medium effect)

2. **Privacy Verification (P1):**
   - **Null hypothesis (H0):** Membership inference attack success ≥ 70% (severe privacy leakage)
   - **Alternative hypothesis (H1):** Membership inference attack success < 55% (near-random guessing)
   - **Test:** Binomial test (attack success rate vs. random baseline 50%)
   - **Significance level:** α = 0.01 (stricter for privacy claims)

3. **Router Accuracy Test (P3):**
   - **Null hypothesis (H0):** Router top-1 accuracy ≤ 75%
   - **Alternative hypothesis (H1):** Router top-1 accuracy > 85%
   - **Test:** One-sample proportion test
   - **Significance level:** α = 0.05

4. **Privacy-Utility Trade-off (P4):**
   - **Design:** Repeated measures ANOVA with ε as within-subjects factor (3 levels: 0.5, 0.75, 1.0)
   - **Dependent variable:** Per-group win rate
   - **Post-hoc:** Tukey HSD for pairwise comparisons between ε levels
   - **Expected:** Monotonic decrease in win rate as ε decreases, but all ≥90% threshold

**Confounding Control:**

1. **Base LLM capability:** Fixed Llama-3-8B model for all conditions (federated and centralized)
2. **Preference dataset:** Same data used for centralized and federated training (only aggregation method differs)
3. **Evaluation protocol:** Blinded human raters (do not know which system generated response)
4. **Hardware:** Controlled cloud infrastructure (A100 GPUs) for consistent latency measurements
5. **Randomization:** Random assignment of test queries to federated/centralized conditions for each group

**Data Collection Protocol:**

1. **Training Phase:**
   - Collect ≥100 preference pairs per stakeholder group via crowdsourcing (Prolific/MTurk, filtered by group membership criteria)
   - Log all training metrics: GPU-hours, communication overhead (MB per round), convergence curves (loss over rounds)

2. **Evaluation Phase:**
   - Generate responses from both federated and centralized systems for 100 held-out test queries per group
   - Recruit 500 human raters per group (matched demographics: age, gender, location, values)
   - Blinded pairwise comparison: "Which response better aligns with [Group] values?" (forced choice)
   - Collect latency measurements: 1000 inference trials per configuration, report p50, p95, p99

3. **Privacy Audit Phase:**
   - Implement Yeom et al. (2018) membership inference attack on adapter parameters
   - Generate 1000 synthetic queries per group with known membership (500 in training set, 500 not)
   - Train attack model to distinguish members from non-members
   - Report attack accuracy (baseline: 50% random guessing)

**Statistical Power:**
- **Per-group win rate:** With N=50 groups, 100 test queries per group, 500 raters, power >0.95 to detect ≥10% difference from 90% threshold (two-sided test, α=0.05)
- **Privacy:** With 1000 attack queries per group, power >0.90 to detect attack success >55% (binomial test, α=0.01)

**Expected Challenges:**
1. **Recruitment:** Finding 500 raters per group matching stakeholder demographics may be difficult for niche groups (e.g., specific religious sects). Mitigation: Use synthetic group definitions based on demographic proxies for pilot.
2. **Evaluation subjectivity:** "Value alignment" is inherently subjective. Mitigation: Multi-rater consensus (500 raters) and within-subjects design (each rater evaluates both systems).
3. **Temporal effects:** Stakeholder values may drift during study. Mitigation: Complete data collection within 3-month window to minimize drift.

---

## 2. Contribution Summary

### Theoretical Contribution

**Framework:** First formal connection between federated learning's privacy-scalability guarantees and pluralistic alignment's value diversity preservation requirements.

**Key Insight:** Distributed training architectures can achieve production-scale multi-stakeholder AI systems while maintaining individual stakeholder autonomy through cryptographic privacy guarantees (ε-differential privacy) combined with modular value representation (LoRA adapters).

**Theoretical Advance:**
1. **Privacy-Diversity Trade-off Formalization:** Establishes empirical relationship between differential privacy budget (ε) and per-group value satisfaction. Hypothesis predicts acceptable trade-off exists (ε=0.5-1.0 achieves <55% privacy leakage while maintaining ≥90% value diversity).

2. **Federated Pluralism Convergence:** Extends FedAvg convergence theory to extremely heterogeneous (non-IID) preference distributions via weighted aggregation with value clustering. Provides methodology for handling stakeholder value heterogeneity without centralized data pooling.

3. **Modular Value Separation Principle:** Demonstrates that value diversity can be preserved through architectural separation (independent adapters per group) rather than statistical aggregation (averaging preferences). Aligns with PAL's finding that value-group separation outperforms averaging, but extends to federated setting.

**Differentiation from Existing Theory:**
- **vs. PAL (Chen et al., 2024):** PAL's ideal point model operates on centralized data. Hypothesis introduces federated variant with privacy guarantees, requiring new aggregation methodology (weighted FedAvg + clustering).
- **vs. Federated Learning Theory (McMahan et al., 2017):** Standard FL assumes mildly non-IID data. Hypothesis addresses extreme heterogeneity (stakeholder values fundamentally different) through clustering and weighted aggregation.
- **vs. Value Pluralism Philosophy (Rudschies et al., 2021):** Provides technical operationalization of philosophical pluralism principle - shows how privacy-preserving systems can respect value autonomy while enabling collective AI alignment.

### Methodological Contribution

**Novel Method:** Federated LoRA training protocol with clustered weighted FedAvg aggregation and stakeholder-conditioned MoE routing for privacy-preserving pluralistic alignment.

**Algorithm Components:**

1. **Local LoRA Training (Algorithm 1):**
   - Input: Stakeholder group preference dataset D_i (≥100 pairs), base LLM, LoRA rank r
   - Process: DPO training on D_i with LoRA layers (rank r=32, ~500K parameters)
   - Output: Group-specific adapter parameters θ_i
   - Innovation: Adapts VPL's personalized RLHF to stakeholder groups, uses DPO instead of PPO for efficiency

2. **Clustered Weighted FedAvg (Algorithm 2):**
   - Input: Adapter parameters {θ_1, ..., θ_N} from N groups, privacy budget ε, cluster count k
   - Process:
     - Cluster groups by preference embedding similarity (k-means, k=5-10)
     - Add ε-DP noise to each θ_i
     - Compute weighted average within clusters (weights proportional to group size or trust score)
     - Compute weighted average across clusters
   - Output: Aggregated adapter pool {φ_1, ..., φ_k}
   - Innovation: Combines value clustering (addresses heterogeneity) with differential privacy (addresses privacy), weighted aggregation (addresses representation balance)

3. **Multi-Source MoE Routing (Algorithm 3):**
   - Input: Query q, user metadata u, stakeholder selection s (optional)
   - Process:
     - Embed query: e_q = Encoder(q)
     - Compute routing logits from multi-source signals:
       - Demographic signal: Router_demo(u)
       - Semantic signal: Similarity(e_q, {preference_embeddings})
       - Explicit signal: Router_explicit(s) if available
     - Softmax over routing logits to select top-3 adapters
   - Output: Activated adapter subset and mixing weights
   - Innovation: Multi-source routing combines implicit (embeddings) and explicit (user selection) signals for robust adapter selection

**Methodological Differentiation:**

| Aspect | Existing Methods | Hypothesis Method | Advantage |
|--------|------------------|-------------------|-----------|
| **Preference Aggregation** | Centralized pooling (PAL, GDPO, VPL) | Federated aggregation with ε-DP | Privacy preservation (no raw data sharing) |
| **Heterogeneity Handling** | Standard FedAvg or no federation | Weighted FedAvg + value clustering | Prevents extreme heterogeneity from breaking convergence |
| **Value Representation** | Ideal points (PAL), belief distributions (GDPO), individual users (VPL) | Stakeholder-group LoRA adapters | Modular, extensible (add/remove groups without retraining) |
| **Routing** | Fixed model selection (Modular Pluralism) or no routing (centralized) | Multi-source MoE routing | Adaptive value selection per query/user |
| **Privacy** | No privacy guarantees | ε-differential privacy (ε=0.5-1.0) | Provable privacy bounds, membership inference resistance |

**Ablation Study Design:**

To validate methodological contributions, hypothesis proposes ablation studies:

1. **Ablation 1: Standard FedAvg vs. Weighted FedAvg with Clustering**
   - Compare per-group win rate under both aggregation methods
   - Hypothesis: Weighted clustering improves performance by 5-10% on heterogeneous groups

2. **Ablation 2: Single-Source vs. Multi-Source Routing**
   - Compare routing accuracy with (a) demographics only, (b) embeddings only, (c) multi-source
   - Hypothesis: Multi-source achieves +15% routing accuracy over single-source

3. **Ablation 3: ε-DP Impact**
   - Vary ε from 0.0 (no noise) to 2.0 (weak privacy)
   - Measure per-group win rate and membership inference attack success
   - Hypothesis: ε=0.5-1.0 provides optimal privacy-utility trade-off

**Implementation Artifacts:**

- **Open-source implementation:** Code release on GitHub with TensorFlow Federated integration
- **Benchmark dataset:** Curated preference dataset with 50 stakeholder groups (pilot scale)
- **Evaluation toolkit:** Membership inference attack implementation + human evaluation interface

### Practical Contribution

**Production Deployment Architecture:**

```
[Stakeholder Sites (N=1000+ groups)]
    ↓ Local LoRA Training (TensorFlow or PyTorch + PEFT)
    ↓ Encrypted Adapter Upload (ε-DP noise added)
[Central Federation Coordinator (TensorFlow Federated / PySyft)]
    ↓ Clustered Weighted FedAvg Aggregation
    ↓ Adapter Pool Distribution
[Inference Servers (Cloud or Edge)]
    ↓ MoE Router (100M params, low latency)
    ↓ Base LLM (Llama-3-8B) + Active Adapters (1-3 selected)
    ↓ <10ms response generation
[End Users with Value-Conditioned Responses]
```

**Infrastructure Requirements:**

1. **Stakeholder Sites:**
   - Compute: 1 GPU (consumer-grade RTX 4090 or cloud A100) per group for local training
   - Storage: ~10GB for base model + 100MB preference dataset
   - Network: 10MB upload bandwidth for adapter transmission

2. **Central Coordinator:**
   - Compute: 4-8 GPUs for aggregation and router training
   - Storage: ~50GB for N=1000 groups (10MB per adapter × 1000)
   - Network: 1Gbps for handling 100-1000 concurrent adapter uploads

3. **Inference Servers:**
   - Compute: 1 A100 GPU per server (can serve 100+ req/sec with <10ms latency)
   - Storage: ~10GB base model + 500MB adapter pool (k=50 clustered adapters)
   - Scaling: Horizontal scaling (multiple servers behind load balancer)

**Deployment Phases:**

**Phase 1: Pilot (10-100 stakeholder groups) - Months 1-6**
- Objective: Validate technical feasibility, measure baselines
- Tasks:
  1. Stakeholder recruitment via participatory workshops (political, cultural, professional groups)
  2. Preference data collection (crowdsourcing, surveys: 100-200 pairs per group)
  3. Infrastructure setup (TensorFlow Federated on Google Cloud)
  4. Local adapter training (parallel across groups)
  5. Federated aggregation (20-50 rounds, monitor convergence)
  6. Human evaluation (500 raters per group, pairwise preference comparisons)
- Success Criteria: ≥90% PAL baseline, <10ms latency, <55% MI attack success, <1 GPU-hour training cost
- Budget: ~$50K (cloud compute + crowdsourcing + human evaluation)

**Phase 2: Scale Validation (100-500 groups) - Months 7-12**
- Objective: Stress-test scalability, optimize infrastructure
- Tasks:
  1. Expand stakeholder coverage (add regional, generational, organizational groups)
  2. Infrastructure optimization (batch aggregation, adapter compression, router distillation)
  3. Governance framework design (stakeholder onboarding, conflict resolution, adapter versioning)
  4. Real-world application deployment (content moderation, healthcare decision support)
- Success Criteria: Maintain performance at 500 groups, latency <15ms, linear cost scaling
- Budget: ~$200K (larger infrastructure, expanded evaluation)

**Phase 3: Production Deployment (1000+ groups) - Months 13-24**
- Objective: Full-scale production system, open platform
- Tasks:
  1. Open platform launch (any stakeholder group can join federation)
  2. Automated onboarding (self-service preference collection, adapter training)
  3. Multi-application integration (content platforms, healthcare, education, policy)
  4. Longitudinal monitoring (value drift detection, adapter retraining triggers)
- Success Criteria: 1000+ active groups, <10ms latency maintained, self-sustaining governance
- Budget: ~$500K (production infrastructure, ongoing maintenance)

**Application Domains:**

1. **Content Moderation:** Different cultural/political groups have divergent moderation norms. Federated system allows platform to serve diverse communities without centralized content policy imposing single value system.

2. **Healthcare Decision Support:** Regional/cultural differences in medical ethics (end-of-life care, reproductive health). Privacy-preserving federation enables culturally appropriate AI guidance.

3. **Educational AI:** Different pedagogical values (rote learning vs. discovery learning, collectivist vs. individualist classroom norms). Adapters represent diverse educational philosophies.

4. **Policy Recommendation:** Democratic processes require representing conflicting political values. Federated system enables transparent multi-stakeholder policy analysis.

**Infrastructure Cost Analysis:**

| Phase | Groups | Training Cost | Inference Cost (monthly) | Evaluation Cost | Total |
|-------|--------|---------------|-------------------------|-----------------|-------|
| Pilot (1-6mo) | 50 | $5K (50 GPU-hours) | $2K (2 A100 servers) | $40K (human eval) | ~$50K |
| Scale (7-12mo) | 500 | $25K (500 GPU-hours) | $10K (10 A100 servers) | $100K (expanded eval) | ~$200K |
| Production (13-24mo) | 1000+ | $50K (1000 GPU-hours) | $50K (50 A100 servers, 12mo) | $50K (ongoing monitoring) | ~$500K |

**Open-Source Contribution:**

1. **federated-pluralistic-alignment library** (Python, Apache 2.0 license)
   - TensorFlow Federated integration for LoRA adapter training
   - Weighted FedAvg with clustering implementation
   - ε-DP noise addition utilities
   - Multi-source MoE router
   - Deployment scripts for cloud platforms (GCP, AWS, Azure)

2. **Benchmark Dataset:** 50-group pilot dataset (anonymized preference pairs, demographic metadata)

3. **Evaluation Toolkit:** Membership inference attack implementation, human evaluation interface

**Impact Potential:**

- **Unblocks Real-World Pluralistic Alignment:** First system with proven deployment path from prototype to production (addresses Gap 1 from Phase 1 research)
- **Enables Privacy-Preserving Value Diversity:** Stakeholders can participate without revealing sensitive preferences (addresses Gap 3)
- **Scales Democratic AI Governance:** Infrastructure for 1000+ stakeholder groups makes large-scale participatory AI feasible
- **Cross-Domain Application:** Architecture generalizes to any multi-stakeholder AI system (content, healthcare, education, policy)

**If hypothesis fails to achieve targets:** Still contributes practical federated learning infrastructure for pluralistic alignment research, even if performance gap to centralized baselines requires further optimization. Negative results inform privacy-utility trade-off boundaries for future work.

---

## 3. Key Related Work

### Foundational Work

**1. Federated Learning (McMahan et al., 2017)**
- Paper: "Communication-Efficient Learning of Deep Networks from Decentralized Data"
- URL: https://arxiv.org/abs/1602.05629
- Contribution: FedAvg algorithm for distributed training without centralizing data
- Relation: **Foundation** - Hypothesis applies FedAvg to pluralistic alignment domain, extends with weighted aggregation and value clustering for extreme heterogeneity

**2. LoRA: Low-Rank Adaptation (Hu et al., 2021)**
- Paper: "LoRA: Low-Rank Adaptation of Large Language Models"
- URL: https://arxiv.org/abs/2106.09685
- Contribution: Parameter-efficient finetuning with 0.01% trainable parameters
- Relation: **Methodology** - Core technical mechanism for value-specific adapter training. Hypothesis uses LoRA for local stakeholder group adaptation.

**3. Differential Privacy in Federated Learning (Kairouz et al., 2021)**
- Paper: "Advances and Open Problems in Federated Learning"
- URL: https://arxiv.org/abs/1912.04977
- Contribution: ε-DP guarantees in federated settings, secure aggregation protocols
- Relation: **Foundation** - Provides privacy theory for adapter aggregation. Hypothesis applies ε-DP to pluralistic value collection.

### Pluralistic Alignment Methods

**4. PAL: Pluralistic Alignment Framework (Chen et al., 2024)**
- Paper: "PAL: Pluralistic Alignment Framework for Learning from Heterogeneous Preferences"
- Semantic Scholar ID: 696d2a133e56772a46626480e1e60402d227b120
- Citations: 36
- Contribution: Ideal point model for capturing plurality of preferences
- Relation: **Extension** - Hypothesis federates PAL's value-group separation principle, adds privacy guarantees. PAL is centralized baseline for comparison (target: ≥90% PAL performance).

**5. GDPO: Group Distributional Preference Optimization (Yao et al., 2024)**
- Semantic Scholar ID: afc7c6da6d22ac999633394f18345749a2ad5397
- Citations: 17
- Contribution: Belief-conditioned preference optimization for group distributions
- Relation: **Extension** - Hypothesis distributes GDPO's belief optimization across federated stakeholder sites. GDPO informs local adapter training objectives (DPO on group beliefs).

**6. Modular Pluralism (Feng et al., 2024)**
- Paper: "Modular Pluralism: Pluralistic Alignment via Multi-LLM Collaboration"
- URL: https://arxiv.org/html/2406.15951v2
- Contribution: Pluggable community LM architecture with three pluralism modes
- Relation: **Inspiration** - Modular adapter design inspired by Modular Pluralism's pluggable LMs. Hypothesis extends with federated training and ε-DP privacy.

**7. VPL: Variational Preference Learning (Poddar et al., 2024, NeurIPS)**
- URL: https://weirdlabuw.github.io/vpl/
- Venue: NeurIPS 2024 Spotlight
- Contribution: Personalized LoRA-based RLHF for diverse users
- Relation: **Extension** - Hypothesis extends VPL's LoRA personalization from individual users to stakeholder groups, adds federated training for privacy.

### Value Pluralism Theory

**8. Value Pluralism in AI Ethics (Rudschies et al., 2021)**
- Semantic Scholar ID: 4b13561ca2dc9b55bfdf22ddc9f8c5b41a240419
- Citations: 25
- Contribution: Analysis of value divergences across actor types (public, expert, private)
- Relation: **Inspiration** - Philosophical grounding for stakeholder group organization. Hypothesis operationalizes value pluralism technically.

**9. Normative Moral Pluralism for AI (Yaacov, 2025)**
- Semantic Scholar ID: fe4254a1f043e49c9b9ff9aa325a1701b334dab0
- Citations: 1
- Contribution: Dual-hybrid structure (universal + local layers) for culturally specific values
- Relation: **Inspiration** - Local value layers concept informs stakeholder-specific adapter design.

**10. Aggregation Problems in AI Alignment (Baum & Slavkovik, 2025)**
- Semantic Scholar ID: b2f78087c968cda5f2ae746c301e4d936198accc
- Citations: 1
- Contribution: Distinguishes moral vs. social aggregation, exposes blind spots under disagreement
- Relation: **Theoretical Context** - Hypothesis addresses social aggregation problem (across stakeholder groups) via federated separation rather than centralized aggregation.

### Annotation Disagreement & Preference Learning

**11. Diverging Preferences (Zhang et al., 2024)**
- Semantic Scholar ID: 3f062cfb7762e45f82cc703a5b093f4fc9c9a9f3
- Citations: 32
- Contribution: Taxonomy of 10 disagreement sources, shows Bradley-Terry model limitations
- Relation: **Methodological Context** - Informs preference dataset design. Hypothesis preserves disagreement through separate adapters vs. averaging.

**12. Human Label Variation as Selbstzweck (Xu et al., 2025)**
- Semantic Scholar ID: 47ed9953a1a905525b98ac212955920dc2edf0dc
- Citations: 0
- Contribution: Reframes HLV as intrinsic value for pluralism, not noise
- Relation: **Philosophical Alignment** - Hypothesis preserves HLV via modular adapters, avoiding noise reduction through averaging.

### Governance & Deployment

**13. Multi-Stakeholder Alignment (Uchoa et al., 2025)**
- Semantic Scholar ID: 88949bc5d2247b3d865e915c601a46d4436c5a02
- Citations: 0
- Contribution: Advisory Governance Layer for distributed stakeholder participation
- Relation: **Governance Framework** - Informs stakeholder organization methodology. Hypothesis provides technical implementation of privacy-preserving multi-stakeholder system.

**14. Democratizing AI Governance (Ter-Minassian, 2025)**
- Semantic Scholar ID: 609afda5c3e72dd35563dd5bc20c1ed29433c14e
- Citations: 3
- Contribution: Balancing expertise with public participation in democratic AI governance
- Relation: **Policy Context** - Informs deployment governance. Hypothesis enables participatory governance at scale (1000+ groups).

### Implementation Resources

**15. TensorFlow Federated**
- URL: https://www.tensorflow.org/federated
- Type: Production framework
- Contribution: Google's production-ready federated learning infrastructure
- Relation: **Foundation** - Deployment infrastructure for hypothesis. Provides secure aggregation, differential privacy, client coordination.

**16. Hugging Face PEFT Library**
- URL: https://github.com/huggingface/peft
- Type: Production library
- Contribution: Parameter-efficient finetuning (LoRA, AdaLoRA, X-LoRA)
- Relation: **Foundation** - Implementation library for local LoRA adapter training. Proven stable and widely adopted.

**17. LibMOON: Multi-Objective Optimization**
- URL: https://github.com/xzhang2523/libmoon
- Type: Research library
- Contribution: Gradient-based multi-objective optimization in PyTorch
- Relation: **Methodology** - Can be used for MoE router training with multi-objective balancing (per-group satisfaction objectives).

**18. PRISM Framework**
- URL: https://www.prismframework.ai/
- Type: Production framework
- Contribution: Seven-worldview framework with hosted demo
- Relation: **Comparison** - Demonstrates pluralistic alignment feasibility. Hypothesis extends with privacy (ε-DP) and scalability (federation).

### Relation Matrix Summary

| Related Work | Relation Type | Hypothesis Contribution |
|--------------|---------------|------------------------|
| Federated Learning (McMahan et al.) | Foundation | Extends to extreme heterogeneity with weighted clustering |
| LoRA (Hu et al.) | Methodology | Applies to stakeholder-group value adaptation |
| ε-DP in FL (Kairouz et al.) | Foundation | Applies to pluralistic value collection |
| PAL (Chen et al.) | Extension | Federates centralized ideal point model, adds privacy |
| GDPO (Yao et al.) | Extension | Distributes belief optimization across sites |
| Modular Pluralism (Feng et al.) | Inspiration | Adds federated training to modular architecture |
| VPL (Poddar et al.) | Extension | Extends personalization to stakeholder groups + federation |
| Value Pluralism Theory (Rudschies et al.) | Inspiration | Operationalizes philosophically |
| Normative Moral Pluralism (Yaacov) | Inspiration | Implements local value layers technically |
| Aggregation Problems (Baum & Slavkovik) | Context | Addresses via separation not aggregation |
| Diverging Preferences (Zhang et al.) | Context | Preserves disagreement via modular adapters |
| HLV as Selbstzweck (Xu et al.) | Alignment | Preserves variation, doesn't reduce as noise |
| Multi-Stakeholder Alignment (Uchoa et al.) | Framework | Implements governance technically |
| Democratizing AI Governance (Ter-Minassian) | Context | Enables participatory governance at scale |
| TensorFlow Federated | Infrastructure | Deployment platform |
| PEFT Library | Infrastructure | Adapter training library |
| LibMOON | Methodology | Multi-objective router training |
| PRISM | Comparison | Extends with privacy + federation |

**What's Novel:**

1. **First federated approach to pluralistic alignment** - No prior work decentralizes training for privacy
2. **Cross-domain transfer from distributed ML to value alignment** - Applies proven federated learning to new domain
3. **Privacy-scalability simultaneous solution** - Previous work chooses centralized (PAL, GDPO, VPL) or lacks privacy (Modular Pluralism)
4. **Production deployment path with concrete architecture** - Moves from theoretical frameworks to engineering implementation

**Citation Gaps to Address in Full Paper:**
- Recent federated learning work on non-IID data (2023-2025)
- MoE routing implementation details (Mixtral, Switch Transformers)
- Stakeholder participation frameworks (participatory design, democratic AI)
- Privacy-preserving ML surveys

---

## 4. Phase 2B Readiness

### Decomposition Preview

The hypothesis naturally decomposes into three testable sub-hypotheses following standard empirical validation structure:

**SH1 (Existence): Federated LoRA Adapters Capture Value Diversity**

**Statement:** Local LoRA adapter training (rank r=32, DPO on ≥100 preference pairs per group) produces group-specific adapters that achieve ≥85% win rate vs. random baseline when evaluated on held-out preferences from the same stakeholder group.

**Verification Method:** Train adapters for 50 pilot groups, evaluate on within-group held-out test sets (100 queries per group, 200 human raters per group). Compare responses from (1) base LLM only, (2) base LLM + group adapter, (3) base LLM + random adapter from different group.

**Success Criteria:** Group-specific adapter outperforms random adapter by ≥30 percentage points (e.g., 85% vs. 55% win rate).

**Rationale:** This validates the foundational claim that LoRA adapters can specialize to stakeholder values. Without this, the entire federated approach is pointless. Isolates local training effectiveness from aggregation complexity.

---

**SH2 (Mechanism): Weighted FedAvg + Clustering Preserves Value Diversity Under Privacy Constraints**

**Statement:** Weighted FedAvg aggregation with value clustering (k=5-10) and ε-DP noise (ε=0.5-1.0) produces federated adapter pool that maintains ≥90% of centralized PAL baseline performance (per-group win rate) while achieving membership inference attack success <55%.

**Verification Method:**
1. Train centralized PAL baseline on pooled data from all 50 groups (reference performance)
2. Train federated system with weighted FedAvg + clustering + ε-DP (ε=0.5, 0.75, 1.0)
3. Evaluate both on same held-out test set (100 queries × 50 groups, 500 raters per group)
4. Run membership inference attacks on both systems (1000 attack queries per group)

**Success Criteria:**
- Federated system achieves ≥90% of PAL's per-group win rate across ≥40/50 groups
- Membership inference attack success <55% for federated (vs. likely >80% for centralized PAL)

**Rationale:** This validates the core aggregation mechanism. Tests whether weighted FedAvg + clustering + ε-DP can balance privacy and utility as claimed. Directly addresses the key tension identified in Section 1.3.

---

**SH3 (Comparison): Federated System Achieves Production Performance vs. Centralized SOTA**

**Statement:** End-to-end federated pluralistic alignment system (local training + weighted FedAvg + MoE routing) achieves inference latency p95 <10ms on production hardware (A100 GPU) AND per-group win rate ≥90% of centralized PAL baseline AND membership inference attack success <55%, simultaneously.

**Verification Method:**
1. Deploy full federated system (N=50 groups, r=32, ε=0.75, k=7, MoE router with multi-source signals)
2. Deploy centralized PAL baseline on same hardware
3. Latency benchmark: 1000 inference trials per system, measure p50/p95/p99 latency
4. Value diversity benchmark: Same evaluation as SH2 (per-group win rates)
5. Privacy benchmark: Same membership inference attacks as SH2
6. Router accuracy: 1000 labeled test queries, measure top-1/top-3 routing accuracy

**Success Criteria:**
- Latency p95 <10ms for federated system
- Per-group win rate ≥90% of PAL (same as SH2 but with MoE routing overhead)
- Membership inference attack <55% (same as SH2)
- Router accuracy >85% (from Prediction P3)

**Rationale:** This validates the complete system vs. SOTA baselines. Combines SH1 + SH2 + routing overhead to test whether production targets are achievable. Provides evidence for practical deployment viability.

---

### Readiness Checklist

**Hypothesis Clarity:**
- ✅ Core statement is specific and quantitative (r=32, ε=0.5-1.0, k=5-10, ≥90% baseline, <10ms latency, <55% MI attack)
- ✅ Variables defined with measurement protocols (Table in Section 1.2)
- ✅ Causal mechanism explicit with evidence (Section 1.3)
- ✅ Assumptions listed and testable (Section 1.4)
- ✅ Scope boundaries clear (Section 1.5)

**Testability:**
- ✅ 5 testable predictions with measurement protocols (Section 1.6)
- ✅ Falsification criteria explicit (per-group win rate <70%, latency >50ms, MI attack >70%, convergence failure, router accuracy <60%)
- ✅ Statistical verification design complete (sample size, tests, power analysis - Section 1.8)
- ✅ SOTA baselines identified (PAL, GDPO, VPL, Modular Pluralism - Section 1.7)

**Decomposition:**
- ✅ Three sub-hypotheses cover existence (SH1), mechanism (SH2), comparison (SH3)
- ✅ Sub-hypotheses are independently testable
- ✅ Sub-hypotheses build incrementally (SH1 validates local training → SH2 validates aggregation → SH3 validates full system)

**Resources:**
- ✅ Infrastructure specified (TensorFlow Federated, PEFT, A100 GPUs)
- ✅ Budget estimated ($50K pilot, $200K scale, $500K production - Section 2)
- ✅ Timeline planned (6-month pilot, 12-month scale, 24-month production)
- ✅ Data collection protocol defined (crowdsourcing, human evaluation, privacy audits)

**Related Work:**
- ✅ 18 key papers/resources identified with relation types (Section 3)
- ✅ Differentiation from SOTA clear (federated vs. centralized, privacy guarantees novel)
- ✅ Novelty claims substantiated (first federated pluralistic alignment)

**Open Questions (for Phase 2B Planning):**
- ⚠️ Stakeholder group definition methodology needs refinement (participatory workshops protocol, demographic proxy validation)
- ⚠️ Value clustering metric selection (k-means on which embeddings? preference-based? demographic-based?)
- ⚠️ Router training data collection (how to get ground-truth stakeholder labels for routing supervision?)
- ⚠️ Adapter versioning strategy (how to handle stakeholder value drift over time?)

**Ready for Phase 2B:** ✅ YES

Hypothesis is sufficiently clarified with testable predictions, clear decomposition into sub-hypotheses, and concrete verification methodology. Open questions are implementation details that can be addressed during Phase 2B verification planning and Phase 3 implementation design.

### Open Questions

**For Phase 2B Verification Planning:**

1. **Stakeholder Group Organization:**
   - Q: What is the concrete participatory workshop protocol for defining stakeholder groups?
   - Approach: Design facilitated workshop format (2-hour sessions, value elicitation exercises, group consensus building)
   - Validation: Measure within-group value coherence (intra-group preference agreement >60%) and between-group distinctiveness (cross-group agreement <40%)

2. **Value Clustering Method:**
   - Q: Which embedding model and distance metric for preference clustering (k-means)?
   - Options: (a) Sentence-BERT on preference pair text, (b) Reward model embeddings, (c) Demographic feature vectors
   - Approach: Compare all three via silhouette score, select method with highest cluster quality
   - Ablation: Test k=5, 7, 10 clusters, select via elbow method on within-cluster variance

3. **Router Training Data:**
   - Q: How to collect ground-truth stakeholder labels for router supervision?
   - Approach:
     - Explicit labels: Ask users "Which stakeholder group do you identify with?" (multi-select allowed)
     - Implicit labels: Infer from preference patterns (which group's adapter has highest win rate for this user?)
     - Hybrid: Combine explicit + implicit with confidence weighting
   - Dataset size: 10,000 labeled queries (200 per stakeholder group × 50 groups)

4. **Adapter Versioning & Value Drift:**
   - Q: When to trigger adapter retraining as stakeholder values evolve?
   - Approach:
     - Monitor per-group satisfaction drift (monthly preference evaluations)
     - Trigger retraining if win rate drops >10% from baseline
     - Incremental retraining (warm-start from previous adapter)
   - Governance: Stakeholder groups vote on retraining triggers (democratic control)

5. **Privacy Audit Methodology:**
   - Q: Which membership inference attack is most relevant for adapter parameters?
   - Options: (a) Yeom et al. (2018) loss-based attack, (b) Shokri et al. (2017) shadow model attack, (c) Carlini et al. (2022) LiRA attack
   - Approach: Implement all three, report worst-case attack success (conservative privacy estimate)

6. **Multi-Group Membership:**
   - Q: How to handle users who belong to multiple overlapping stakeholder groups?
   - Approach: MoE router activates top-3 adapters with mixing weights (not forced single-group selection)
   - Validation: Test on users with known multi-group membership, measure satisfaction vs. single-group users

7. **Cross-Cultural Validation (Gap 2 from Phase 1):**
   - Q: How to extend pilot (Western-centric) to cross-cultural validation?
   - Approach:
     - Phase 1 Pilot: Western stakeholder groups (US/EU political/cultural groups)
     - Phase 2 Extension: Add Asian stakeholder groups (Confucian, Buddhist, Islamic value systems)
     - Validation: Measure whether federated approach works across fundamentally different cultural frameworks
   - Open question: Are privacy norms themselves culturally specific (ε acceptable in West but not Asia?)

8. **Economic Sustainability:**
   - Q: Who pays for federated infrastructure (cloud compute, coordinator servers)?
   - Options: (a) Platform provider (content platforms subsidize pluralism), (b) Stakeholder groups (federated cost-sharing), (c) Public funding (democratic AI as public good)
   - Governance: Transparent cost allocation, democratic decision-making on infrastructure investment

**Critical Questions Requiring Validation Before Full Deployment:**

- **Stakeholder Engagement:** Will 1000+ real stakeholder groups actually participate? Pilot validates technical feasibility, but governance/participation feasibility is separate question.
- **Adversarial Stakeholders:** What if stakeholder group has malicious values (hate speech, disinformation)? Hypothesis assumes value pluralism is desirable, but needs meta-framework for value exclusion boundaries.
- **Regulatory Compliance:** Does federated training comply with GDPR, AI Act, other regulations? Privacy claims need legal validation, not just technical ε-DP proofs.

**For Phase 2C Experiment Design:**

These open questions will inform detailed experiment specifications in Phase 2C:
- Precise stakeholder recruitment protocol
- Preference dataset construction guidelines
- Router training data collection workflow
- Adapter versioning policy
- Privacy audit implementation details
- Multi-group membership handling
- Cross-cultural extension roadmap

**For Phase 3 Implementation Planning:**

- Detailed architecture diagrams (TensorFlow Federated deployment)
- API specifications (stakeholder onboarding, adapter upload, inference endpoints)
- Monitoring and observability (value drift detection, privacy leakage alerts)
- Governance smart contracts (stakeholder voting, cost allocation)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-08*
