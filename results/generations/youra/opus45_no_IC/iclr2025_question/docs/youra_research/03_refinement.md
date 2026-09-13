# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-10T21:45:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap-1-cross-benchmark-transfer
- **Gap Title**: Cross-Benchmark Domain Transfer of Uncertainty-Based Detectors
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 criteria met; all 6 personas participated with genuine challenge/refinement

### Key Insights
- Reframed from "threshold transfer" to "structural property transfer"
- Benchmark clustering discovers families empirically, avoiding post-hoc bias
- Error type similarity (recall vs. reasoning) may mediate transfer success
- JS-divergence provides actionable practitioner guidance

### Breakthrough Moments
- Exchange 7: Data-driven clustering proposed instead of assumed categories
- Exchange 11: Conditional transfer hypothesis synthesized
- Exchange 13: Train/test protocol operationalized to avoid circularity

---

## Final Hypothesis

### Title
Conditional Transfer of Uncertainty-Based Hallucination Detectors

### Hypothesis ID
H-ConditionalTransfer-v1

### Core Claim
Under the scope of factual QA and claim verification benchmarks, if a semantic entropy-based hallucination detector is calibrated on one benchmark and tested on another, then transfer success (AUROC degradation ≤ 0.08) depends on uncertainty distribution similarity between benchmarks, because similar error-generation processes produce similar uncertainty distributions.

### Mechanism
1. LLMs generate uncertainty signals reflecting specific error-generation processes
2. Benchmarks testing similar processes exhibit similar uncertainty distributions (low JS-divergence)
3. Calibration thresholds effective for one distribution transfer to similar distributions
4. Dissimilar distributions (high JS-divergence) require recalibration

---

## Predictions

| ID | Prediction | Success Criterion | Falsification |
|----|------------|-------------------|---------------|
| P1 | Benchmarks cluster meaningfully | Silhouette > 0.5 | Silhouette < 0.3 |
| P2 | Within-cluster transfer succeeds | Degradation ≤ 0.08 | Degradation > 0.15 |
| P3 | Cross-cluster transfer fails | Degradation > 0.15 | Degradation < 0.08 |
| P4 | Clustering beats random | p < 0.05 | p > 0.10 |
| P5 | Clusters align with error types | ARI > 0.6 | ARI < 0.3 |

---

## Novelty

**Key Innovation**: First systematic investigation of cross-benchmark transfer for uncertainty-based hallucination detectors, introducing empirical benchmark taxonomy via distribution clustering.

**Differentiation**:
- Kuhn 2023: Evaluated single benchmarks; no transfer analysis
- SelfCheckGPT: WikiBio only; no cross-benchmark evaluation
- Xue 2025: Cross-model focus; same benchmark per model

---

## Experimental Design

### Datasets
TriviaQA, Natural Questions, HaluEval-QA, FEVER, PopQA, SQuAD

### Models
Llama-2-7B, Mistral-7B

### Baselines
- Random cluster assignment (100 permutations)
- In-distribution AUROC (Kuhn 2023)

### Protocol
- 70% train (clustering) / 30% test (AUROC evaluation)
- 10 generations per query, 1,000 queries per benchmark
- JS-divergence matrix + hierarchical clustering
- Permutation test for clustering validity

---

## Limitations

- Single-turn QA setting only
- 7B-scale models; larger models may differ
- Semantic entropy requires model logits; not applicable to black-box APIs
- English-language benchmarks only

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None |

---

## Phase 2B Readiness

- **SH1 (Existence)**: Uncertainty distributions cluster with silhouette > 0.5
- **SH2 (Mechanism)**: Within-cluster degradation < cross-cluster degradation
- **SH3 (Comparison)**: Discovered clustering outperforms random baseline

**Status**: READY for Phase 2B verification protocol design
