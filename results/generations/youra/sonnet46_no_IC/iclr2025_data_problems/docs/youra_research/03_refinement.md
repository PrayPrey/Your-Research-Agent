# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-04T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap-1
- **Gap Title**: Causal Attribution of Curation Choices to Benchmark Outcomes Is Unestablished
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met at exchange 15 (min_exchanges=15). All 6 personas participated. Self-judged CONVERGED.

### Key Insights
- PPL/ICL misalignment (DataMan, Peng et al. 2025) is the foundational empirical clue: perplexity-optimal data is not ICL-optimal, and this gap is plausibly scale-dependent
- SoftDedup's finding (near-duplicate down-weighting outperforms hard removal for few-shot performance) directly supports the P3 mechanism — near-duplicates carry ICL-relevant frequency patterns
- WebOrganizer's super-additive domain mixing + quality filtering finding motivates treating distributional diversity as a distinct, orthogonal axis from quality — relevant to why large models prefer looser filtering
- Na et al.'s modular approximation method bridges tractable small-scale experiments to larger-scale extrapolation

### Breakthrough Moments
- **Exchange 5**: First consolidated H-CurationScale-v1 hypothesis (Under-If-Then-Because)
- **Exchange 7**: P2 (benchmark variance) and P3 (opposite dedup sign) — two entirely novel predictions
- **Exchange 13**: Data efficiency reframing (tokens-to-peak, learning curve λ) — dissolves token budget problem and adds P4
- **Exchange 14**: Log-linear learning curve formalization with pre-registered statistical test for P4

---

## Final Hypothesis

### Title
Scale-Dependent Optimal Curation: Perplexity Filtering and Deduplication Aggressiveness Have Opposite Scale Interactions in Pre-training

### Hypothesis ID
H-CurationScale-v1

### Core Claim
Under fixed model architecture family (Pythia-style, trained from scratch) and fixed tokens-seen budget on open corpora (Dolma, FineWeb replication), if we independently vary perplexity filtering threshold τ ∈ {20, 35, 50} and deduplication aggressiveness d ∈ {strict: MinHash Jaccard=0.7, loose: MinHash Jaccard=0.9}, then downstream benchmark scores (MMLU 4-shot + HellaSwag 0-shot) will show significant Scale × Curation interaction effects — specifically: smaller models (70M) achieve peak performance at lower PPL thresholds and benefit from aggressive deduplication, while larger models (160M+) achieve peak performance at higher PPL thresholds and are harmed by aggressive deduplication — because smaller models lack sufficient capacity to extract signal from high-diversity noisier distributions (requiring stronger quality filtering), while larger models rely on near-duplicate pattern frequency for in-context learning ability (which aggressive deduplication removes).

### Mechanism
1. **Curation changes corpus token distribution**: PPL filtering removes high-diversity/noisy documents; dedup removes near-duplicate frequency patterns
2. **Capacity determines optimal distribution**: Small models need clean, predictable distributions (low capacity → benefit from quality filtering + dedup). Large models leverage diversity + frequency patterns for ICL (high capacity → hurt by aggressive dedup, benefit from diversity)
3. **Scale × Curation interaction manifests**: Measurable interaction effects in benchmark scores and learning curve shapes across curation conditions at different model scales

---

## Predictions

| ID | Statement | Test | Success Criterion |
|----|-----------|------|-------------------|
| **P1** (primary) | τ*(70M) ∈ [20,35] < τ*(160M) ∈ [35,50] | 2-way ANOVA Scale × PPL-threshold | p < 0.05, partial η² ≥ 0.15, directional |
| **P2** | Var(benchmarks, 70M) > Var(benchmarks, 160M) across PPL conditions | Levene's test | p < 0.05, one-tailed |
| **P3** | Sign(B(strict)-B(loose)) positive at 70M, non-positive at 160M | 2-way ANOVA Scale × Dedup | p < 0.05, sign change confirmed |
| **P4** | Convergence rate λ higher at (70M, τ=20) than (160M, τ=20) | ANOVA on λ from log-linear curve fit | p < 0.05, directional |

---

## Novelty

**Key Innovation**: First controlled factorial measurement of Scale × Curation interaction effects in pre-training data quality filtering. Prior work (ProX, REWIRE, DataMan, WebOrganizer, SoftDedup) each vary one curation axis at one scale. No prior work measures the scale × curation interaction.

**Most Novel Finding (if confirmed)**: P3 — aggressive deduplication hurts large models while helping small models. This directly challenges universal dedup practice adopted in every major curation pipeline since 2021 (google/deduplicate-text-datasets, NeMo-Curator, FineWeb pipeline).

**Secondary Novel Finding**: P4 — learning curve convergence rate λ as a data efficiency outcome, connecting to Chinchilla-style scaling laws for data quality.

---

## Experimental Design

**Corpora**: Dolma v1.7 (primary), FineWeb (replication) — both fully open, documented filtering pipelines

**Models**: Pythia-architecture 70M and 160M, trained from scratch using GPT-NeoX code

**Filtering conditions**: 3 PPL thresholds (τ ∈ {20, 35, 50}) × 2 dedup levels (J ∈ {0.7, 0.9}) = 6 conditions per corpus

**Training runs**: 2 scales × 6 conditions × 2 corpora × 3 seeds = 72 total

**Evaluation**: lm-evaluation-harness, MMLU 4-shot + HellaSwag 0-shot, at 10 checkpoints per run (every 5B tokens out of 50B)

**Tools**:
- Corpus preparation: NVIDIA/NeMo-Curator
- Training: EleutherAI/gpt-neox
- Evaluation: EleutherAI/lm-evaluation-harness
- Contamination: lm-sys/llm-decontaminator
- Deduplication: google-research/deduplicate-text-datasets (MinHash)

**Compute estimate**: ~96 A100-hours for primary design (72 runs × ~4h each at 70M/160M scale on 4×A100s per run) — tractable with academic compute

---

## Limitations
- Single architecture family (Pythia-style) — OLMo replication conditional on compute availability
- Primary study at 70M and 160M only; 1B+ extrapolated via Na et al. (2024) modular approximation
- English-language corpora only; multilingual dynamics may differ
- GPT-2 as PPL reference model may not be optimal for all corpora
- If FineWeb and Dolma results diverge, conclusion is corpus-specific

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at exchange 15 (min_exchanges satisfied) |
| **Clarity Verified** | Yes |
| **All Personas Participated** | Yes — Dr. Nova (3×), Prof. Vera (3×), Dr. Sage (3×), Prof. Pax (2×), Dr. Ally (2×), Prof. Rex (2×) |
| **Feasibility Confirmed** | Yes — 96 A100-hours, existing open-source tools only |
| **Remaining Objections** | 3 (low/medium severity, all mitigated or pre-specified) |

---

*Phase: 2A-Dialogue | Architecture: Self-Play Loop (Claude-only, IC-ablation)*
*Generated: 2026-08-04 | Ready for Phase 2B*
