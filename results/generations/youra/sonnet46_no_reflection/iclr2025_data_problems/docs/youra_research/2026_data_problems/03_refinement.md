# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-13T02:00:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap_1
- **Gap Title**: No Systematic Multi-Method, Multi-Benchmark Contamination Detection Comparison
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16
- **Hypothesis ID**: H-GeomRoute-v1

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 16

**Convergence Reason**: All 6 criteria met — SPECIFIC (three-zone phase diagram core claim), MECHANISM (logistic regression routing on geometry features), PREDICTIONS (3 falsifiable predictions with simulation-calibrated thresholds), NOVELTY (indeterminate zone + regime prediction rule), FEASIBILITY (24-48 GPU-hours, existing tools), OBJECTIONS (latent-variable, covariate shift, threshold arbitrariness all resolved)

### Key Insights

1. **Regime-mapping reframe** (Dr. Nova, Exchange 1): The comparison is not "which detector wins" but "which corpus geometry regime determines which detector wins" — transforms benchmarking into structural characterization.
2. **Latent-variable clarification** (Prof. Rex + Prof. Vera): All claims scoped to "detector sensitivity to observable corpus overlap," not causal memorization chains — sidesteps the corpus≠training-exposure gap without losing scientific validity.
3. **Indeterminate zone as primary finding** (Dr. Nova, Exchange 16): Items where no detector dominates are not a nuisance but a structural blind spot — mapping this zone is a field-level contribution independent of routing accuracy.
4. **Margin-based determinacy** (Dr. Ally, Exchange 14): Replace noisy argmax with margin criterion (≥ 0.05 F1 gap under bootstrap) — makes prediction target a well-defined, learnable function.
5. **Simulation-calibrated thresholds** (Prof. Vera, Exchange 11): Falsification thresholds derived from synthetic separability surfaces (Hidayat et al. protocol) — removes threshold arbitrariness.

### Breakthrough Moments

- **Exchange 10** (Dr. Nova): Reframe from "compare detectors" to "can geometry predict detector ordering?" — pivotal shift toward structural prediction hypothesis.
- **Exchange 13** (Prof. Rex): Margin criterion and MMD covariate shift control identified as the two remaining structural gaps — hypothesis tightened considerably.
- **Exchange 16** (Dr. Nova + orchestrator convergence signal): Three-zone diagram crystallized with indeterminate zone as the central structural contribution — discussion converged.

---

## Final Hypothesis

### Title
Geometry-Governed Contamination Detection: A Three-Zone Phase Diagram for Benchmark Audit Routing

### Core Claim (Under-If-Then-Because)

Under the setting of contamination detection for FM evaluation benchmarks (MMLU, HellaSwag, GSM8K) against real pretraining corpora (The Pile, C4, RedPajama) using open-weight models (Llama-2-7B, Mistral-7B, Pythia-7B), **if** corpus-side geometric signals (max 13-gram overlap count + SBERT cosine similarity to nearest corpus neighbor) are used to classify benchmark items into contamination geometry strata, **then** a logistic regression routing rule trained on one corpus will predict the top-performing detector family cross-corpus with accuracy > 40% (top-1) and Kendall's τ above a simulation-calibrated threshold on determinate items (F1 margin ≥ 0.05 under bootstrap), **because** contamination detection methods operate on fundamentally different signal types whose efficacy is structurally determined by which corpus overlap geometry dominates in each benchmark-corpus pair.

### Mechanism

1. Corpus-side geometry (13-gram overlap count, SBERT cosine similarity) determines which overlap signal dominates for each benchmark item — independently of any detector.
2. Each detector family's sensitivity is tied to its signal type: n-gram detectors → lexical matches; embedding detectors → semantic proximity; MIA-based (Min-K%++, DC-PDD) → likelihood perturbation on memorized token spans.
3. Because sensitivity aligns with signal type, the dominant geometry of a benchmark item structurally predicts which detector family will achieve the highest F1.
4. A logistic regression classifier trained on corpus-side geometry features on The Pile generalizes cross-corpus above chance (after MMD covariate shift control) — establishing the three-zone contamination phase diagram.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|------------------|---------------|
| **P1** (primary) | Corpus geometry predicts detector ordering cross-corpus above chance | Top-1 accuracy > 40% AND Kendall's τ > simulation-calibrated threshold on determinate items | Accuracy ≤ 40% OR τ ≤ threshold after MMD control |
| **P2** | N-gram recall collapses from lexical to semantic stratum; MIA methods show cross-corpus variance | N-gram: recall ≥ 0.80 lexical, ≤ 0.40 semantic; Min-K%++ F1 variance ≥ 0.15 cross-corpus | N-gram recall ≥ 0.60 in semantic stratum OR Min-K%++ variance < 0.10 |
| **P3** | Indeterminate zone exists with meaningful size | Indeterminacy rate in [10%, 50%] | Rate < 5% (no blind spot) OR > 50% (routing impractical) |

---

## Novelty

**What's new:**
- First systematic empirical test of whether contamination detection decomposes structurally across geometry regimes
- First geometry-based routing rule for detector selection — practitioners can select detector family from cheap corpus scan before expensive model forward passes
- First characterization of the indeterminate detection zone as a structural blind spot (not a method limitation)
- Three-zone contamination phase diagram as a new conceptual framework for the field

**How it differs from prior work:**
- Singh et al. [2024] *observe* inconsistent signals; we *explain* them via geometry decomposition
- Min-K%++, DC-PDD, ConStat each optimize internally; we compare them across orthogonal geometry strata
- Hidayat et al. [2025] test one injection regime; we test three and measure Kendall's τ across regimes

---

## Experimental Design

**Benchmarks**: MMLU (~14K), HellaSwag (~10K), GSM8K (~1.3K) — ~25K items total

**Corpora**: The Pile, C4, RedPajama (all publicly available)

**Models**: Llama-2-7B, Mistral-7B, Pythia-7B (open-weight, white-box access)

**Detectors**:
| Family | Tool | Access |
|--------|------|--------|
| N-gram overlap | EleutherAI/lm-evaluation-harness | Corpus-side |
| Embedding similarity | ntunlp/LLMSanitize + FAISS | Corpus-side |
| Min-K%++ | zjysteven/mink-plus-plus | White-box |
| DC-PDD | Zhang et al. 2024 (fixed reference) | White-box |
| ConStat | Dekoninck et al. 2024 | Black-box |

**Ground Truth**:
- Approach A: Known inclusion audit (Yang et al. 2023 verified contaminations; strong/weak positive stratification)
- Approach B: Hidayat et al. 2025 simulated leakage, 3 injection regimes (uniform, clustered, paraphrased)

**Compute**: ~24-48 GPU-hours on A100 total

**Pre-registered ablations**:
1. Indeterminacy rate as primary structural outcome (pass: < 50%; fail: > 50%)
2. DC-PDD ablation: retrain router without DC-PDD; routing accuracy drop < 0.05 confirms structural independence
3. 70% corpus proxy stress test: routing accuracy drop < 0.10 confirms reference stability
4. Prevalence shift analysis: routing accuracy stable (< 0.10 drop) across 5%/10%/30% contamination rates
5. Phase structure stability: Kendall's τ ≥ 0.7 across injection regimes

---

## Limitations

- All claims scoped to "detector sensitivity to observable corpus overlap" — not causal memorization chains
- Open-weight models only (Llama/Mistral/Pythia) — no proprietary API models
- Routing utility bounded by indeterminacy rate — if > 50%, routing is not practically useful
- Cross-corpus routing may degrade if geometry distributions are disjoint across corpora (MMD check required)
- DC-PDD requires fixed neutral-corpus reference model — deployment requires this model to be publicly available

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-GeomRoute-v1 |
| **Discussion Convergence** | All 6 criteria met after 16 exchanges |
| **Clarity Verified** | Yes |
| **Phase 2B Ready** | Yes |
| **Remaining Objections** | 3 pre-registration items (indeterminacy rate, DC-PDD ablation, 70% proxy) — design choices, not fatal flaws |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
*Gap: gap_1 | Exchanges: 16 | All 6 convergence criteria met*
