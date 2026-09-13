# Phase 2B Summary: HyperWave-TGN Hypothesis

**Hypothesis ID:** H-001
**Confidence Level:** 85% (HIGH)
**Date:** 2026-02-08
**Status:** Ready for Phase 2B Verification Planning

---

## Core Hypothesis Statement

For temporal graphs with heterogeneous temporal dynamics (where different nodes/edges evolve at vastly different timescales), embedding nodes in hyperbolic space with position-encoded temporal resolution combined with node-specific wavelet-based multi-scale attention will achieve comparable or superior predictive performance to fixed-resolution baselines while reducing temporal processing costs by 30-50%, as measured on synthetic heterogeneous-temporal graphs, brain network datasets (HCP), and molecular dynamics simulations.

---

## Key Innovation

**HyperWave-TGN** learns node-specific temporal resolutions by:
1. **Hyperbolic embeddings** in Poincaré ball (distance from origin = temporal resolution)
2. **3-scale wavelet decomposition** (fine/medium/coarse Morlet wavelets)
3. **Node-specific attention** over wavelet scales
4. **Adaptive compute allocation** (fast nodes → fine scales, slow nodes → coarse scales)

---

## Testable Predictions

**P1 (Primary): Pareto Improvement**
- HyperWave achieves ≥95% of best baseline accuracy while using ≤70% temporal FLOPs
- Success: ≥2 out of 4 datasets (synthetic, brain, molecular, social) with CV ≥ 2.0

**P2: Resolution Alignment**
- Learned hyperbolic distance correlates with ground-truth node frequency (Spearman ρ > 0.6)

**P3: Attention Specialization**
- High-frequency nodes assign >70% attention to fine wavelets
- Low-frequency nodes assign >60% attention to coarse wavelets

**P4: Scalability**
- Trains on 10⁶ node graphs in <24 hours on single A100 GPU

---

## Sub-Hypotheses for Phase 2B

**SH1 (Existence):** Hyperbolic embeddings encode temporal resolution (ρ < -0.5)
**SH2 (Mechanism):** Wavelet attention adapts to node frequency (>60% correct specialization)
**SH3 (Comparison):** Achieves Pareto improvement over baselines (P1 criterion)

---

## Contribution Summary

**Theoretical:**
- First framework for temporal scale hierarchies in hyperbolic space
- Multi-scale temporal attention theory bridging wavelets and GNNs
- Characterization of heterogeneous temporal dynamics (CV threshold)

**Methodological:**
- HyperWave-TGN architecture (hyperbolic + wavelet + attention)
- Wavelet-based temporal graph signal processing
- Synthetic heterogeneous-temporal graph generation protocol

**Practical:**
- 30-50% FLOPs reduction on high-heterogeneity graphs
- Billion-scale capability (inherited from Xu 2024)
- Cross-domain applicability (brain, molecular, social networks)

---

## Baselines

1. **SpikeNet** (Li 2022): Event-driven via spiking neurons, single resolution
2. **Hyperbolic STGN** (Xu 2024): Hyperbolic for spatial hierarchy, fixed temporal resolution
3. **Decoupled DSTG** (Wang 2024): Two-scale (trend/seasonal), uniform across nodes

---

## Key Assumptions

1. Temporal dynamics have scale hierarchy (testable via multi-exponential autocorrelation)
2. Morlet wavelets suitable for graph signals (testable via reconstruction error)
3. Hyperbolic curvature learnable (validated by Xu 2024)
4. Node temporal characteristics relatively stationary (testable via stability analysis)
5. FLOPs reduction translates to wall-clock speedup (GPU-dependent, measure both)

---

## Scope

**IN-SCOPE:**
- Temporal graphs with discrete timesteps and heterogeneous dynamics (CV ≥ 2.0)
- Node classification, link prediction tasks
- Scales: 10³ to 10⁹ nodes
- Domains: Synthetic, brain networks, molecular dynamics, social networks

**OUT-OF-SCOPE:**
- Continuous-time graphs (irregular timestamps)
- Homogeneous temporal dynamics (CV < 0.5)
- Graph generation tasks
- Graphs with <100 nodes (hyperbolic overhead unjustified)

---

## Falsification Criteria

**Hypothesis is FALSIFIED if:**
1. HyperWave accuracy <90% of best baseline on ≥3/4 datasets (no Pareto improvement)
2. Resolution alignment ρ < 0.2 on synthetic graphs (mechanism explanation invalid)
3. Attention distribution uniform/random (no adaptive specialization)
4. Scalability failure: OOM or >72h training on 10⁶ nodes (scalability claim invalid)

---

## Implementation Roadmap (6 Months)

**Months 1-2:** Core implementation (hyperbolic + wavelet + attention)
**Month 3:** Synthetic validation (ground-truth resolution alignment)
**Months 4-5:** Real-world validation (HCP brain, JODIE social networks)
**Month 6:** Analysis, ablations, scalability tests

**Resources:** 1 A100 GPU, PyTorch Geometric, geoopt, PyWavelets
**Difficulty:** MEDIUM (hyperbolic expertise required, libraries available)

---

## Open Questions for Phase 2B

**Scientific:**
1. Optimal curvature initialization strategy (relationship to CV?)
2. Mapping wavelet scales to domain-specific temporal resolutions
3. Handling bursty dynamics (fast AND slow nodes)
4. Theoretical characterization of computational savings

**Engineering:**
5. Hyperbolic vs Euclidean attention mechanism
6. Fixed vs learnable wavelet parameters
7. Node position initialization (random, degree-based, transfer)
8. Efficient batched wavelet transform implementation

**Validation:**
9. Synthetic graph ground-truth generation protocol
10. Brain network evaluation task (HCP cognitive score prediction?)
11. Fair computational cost measurement (FLOPs vs wall-clock vs memory)
12. Cross-domain validation strategy (minimum 3/4 domains)

---

## Next Steps

**Immediate:** Proceed to Phase 2B - Verification Planning
- Decompose into detailed sub-hypotheses (SH1-SH3)
- Design experiments for each sub-hypothesis
- Prioritize verification order (SH1 → SH2 → SH3)
- Identify dependencies and blocking experiments

**Phase 2C:** Experiment Design (after Phase 2B approval)
- Specify datasets, baselines, hyperparameters
- Create synthetic graph generation code
- Design ablation study matrix
- Pre-register experimental protocol

---

*Full details: 02a_extended_hypothesis_full.md*
*Generated: 2026-02-08*
*Status: ✅ READY FOR PHASE 2B*
