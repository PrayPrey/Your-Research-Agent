# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-24T15:15:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: Limited Qwen-Family Calibration Studies
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: Established falsifiable cross-family test of RLHF-induced discriminative degradation with hierarchical mechanism framework

### Key Insights

1. **AUROC-based discriminative degradation is the linchpin** - prioritize over ECE metrics. If margin predicts correctness less well in instruct models, RLHF corrupted the signal.

2. **Percentile normalization distinguishes geometry from scale** - comparing raw margins conflates scale differences with shape differences. Z-scoring margins within each model isolates geometric distortion.

3. **Cross-family consistency validates RLHF causation** - if effect appears only in one family, it's vendor-specific. Low heterogeneity (I² < 50%) across Qwen/Llama/Mistral supports RLHF as the causal factor.

4. **Domain structure claim is conditional** - must survive lexical controls (token length, answer entropy) to be considered evidence of representational anisotropy rather than surface-form artifacts.

### Breakthrough Moments

- **Exchange 8**: Prof. Rex demanded AUROC to prove signal degradation vs. rescaling - reframed the entire hypothesis
- **Exchange 9**: Dr. Nova proposed logit-gap vs. accuracy correlation as novel mechanistic test
- **Exchange 12**: Prof. Vera formulated unified hypothesis H* with β_percentile as key metric
- **Exchange 13**: Dr. Ally synthesized six-hypothesis hierarchy (H-E, H-M1-3, H-C1-2) with explicit pass criteria

---

## Final Hypothesis

### Title

RLHF-Induced Discriminative Degradation of Confidence Signals in LLMs

### Core Claim

Under multiple-choice QA evaluation on instruction-tuned LLMs, if RLHF instruction tuning is applied, then the discriminative quality of confidence signals degrades (AUROC for margin-based correctness prediction drops and margin-accuracy monotonicity weakens under percentile normalization), because preference optimization rewards decisive responses regardless of correctness, inflating logit margins even for incorrect predictions.

### Mechanism

1. **RLHF preference optimization** rewards decisive, confident-sounding responses via Bradley-Terry model
2. **Selection pressure inflates logit margins** uniformly - including for incorrect predictions
3. **Margin inflation decouples confidence-correctness relationship**, degrading discriminative signal
4. **Distortion is geometric (probability landscape shape)** rather than scalar (temperature-like rescaling)

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1 (Primary)** | AUROC_instruct < AUROC_base across 3 families | Non-overlapping 95% CIs; I² < 50% | AUROC_instruct >= AUROC_base or I² > 75% |
| **P2** | β_percentile_instruct < β_percentile_base | p < 0.05 across prompt formats | Difference vanishes under controls |
| **P3** | E[margin \| incorrect]_instruct > E[margin \| incorrect]_base | Permutation p < 0.05 | Distributions indistinguishable |
| **P4** | Domain coefficients significant in T_opt regression | F-test p < 0.05 after lexical controls | Domain loses significance |
| **P5** | Domain-conditioned scaling achieves Pareto improvement | AURC_domain < AURC_global; worst-case reduced | Helps average but harms any domain |

---

## Novelty

**Key Innovation**: First systematic test of discriminative degradation (AUROC-based) under RLHF with percentile-normalized geometry analysis

**Differentiation from Prior Work**:
- **Guo et al. 2017**: Applied temperature scaling to CNNs; we test whether it suffices for RLHF-induced LLM distortion
- **Tian et al. 2023**: Documented RLHF overconfidence; we measure discriminative degradation (AUROC) not just calibration shift (ECE)
- **DACA/CCPS 2025**: Method performance; we test cross-family generalizability and mechanistic claims

---

## Experimental Design

**Models**:
- Qwen2.5-7B (Base + Instruct)
- Llama-2-7B (Base + Instruct)
- Mistral-7B-v0.1 (Base + Instruct)

**Datasets**: MMLU (~14,000 samples), TruthfulQA (~800 samples)

**Evaluation Design**: 2×2 factorial (base/instruct × zero/few-shot)

**Baselines**: Uncalibrated (T=1), Global Temperature Scaling, Domain-Conditioned Scaling

**Compute**: ~36 GPU hours on single A100

---

## Limitations

1. **Base vs. instruct comparison confounds**: Mitigated by 2×2 prompt design
2. **MMLU domains may correlate with difficulty**: Controlled via stratification by base model accuracy
3. **7B scale may not generalize**: Explicitly scoped to 7B models
4. **Results may be dataset-specific**: Multiple benchmarks (MMLU + TruthfulQA) used

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Established falsifiable cross-family test with hierarchical mechanism framework |
| **Clarity Verified** | Yes |
| **Remaining Objections** | H-C1 domain structure conditional on lexical controls |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
