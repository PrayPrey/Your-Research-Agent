# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-31T00:00:00
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1
- **Gap Title**: Absence of Systematic Quantification of Filtering Stringency → Benchmark Generalization Relationship Across Existing Model Suites
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 12

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 12

**Convergence Reason**: All 6 criteria met at Exchange 12 (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

### Key Insights
1. Reframing Pythia from "training dynamics testbed" to "corpus quality variation testbed" reveals an unexploited experimental opportunity — all required data, checkpoints, and tools already exist publicly
2. The matched-token-count design using intermediate checkpoints is the methodological key to a defensible cross-suite comparison
3. OOD/ID generalization balance ratios (MMLU/HellaSwag, ARC-Challenge/Easy delta) are more meaningful dependent variables than average benchmark performance for testing curation effects
4. The temporal trajectory analysis (comparing performance gaps at 143B and 300B tokens) provides a signature to distinguish data quality effects from architectural effects — widening gap implicates data, constant gap implicates architecture
5. GPT-2-xl perplexity is a style proxy, not a quality proxy — domain-neutral metrics (n-gram repetition rate, Flesch-Kincaid grade level, fastText language ID confidence) are the correct operationalization

### Breakthrough Moments
- **Exchange 4**: Prof. Pax distinguished "applied curation stringency" from "source-intrinsic quality," clarifying the hypothesis
- **Exchange 6**: Prof. Rex identified GPT-2-xl perplexity as invalid, leading to the composite domain-neutral quality proxy
- **Exchange 7**: Dr. Nova proposed intermediate checkpoint matching as the solution to the token-count confound
- **Exchange 11**: Dr. Ally introduced temporal trajectory analysis as an elegant architecture confound bounding strategy

---

## Final Hypothesis

### Title
**Corpus Quality as a Predictor of Generalization Balance: A Matched-Scale Analysis of Pythia and OLMo**

### Hypothesis ID
`H-CorpusQualityGenBalance-v1`

### Core Claim
Under a controlled matched-training-scale comparison (~300B tokens) between foundation models trained on corpora of differing curation quality, if corpus curation quality is higher (as measured by n-gram repetition rate, Flesch-Kincaid grade level, and language ID confidence applied to representative domain samples), then models will show better OOD-to-ID generalization balance (higher MMLU/HellaSwag performance ratio and higher ARC-Challenge/Easy performance delta), because higher-quality data contains less noise and fewer style-specific artifacts, allowing the model to learn more generalizable representations rather than domain-specific statistical patterns.

### Mechanism (4-Step Causal Chain)
1. **Noise Reduction**: Higher corpus curation quality reduces training noise (less n-gram repetition, more syntactically complex text, higher language purity)
2. **Representation Learning**: Reduced noise allows gradient updates to encode generalizable semantic/syntactic patterns rather than domain-specific shortcuts
3. **Task Transfer**: More generalizable representations produce better transfer across diverse task types (knowledge vs. commonsense vs. reasoning)
4. **Temporal Accumulation**: The quality advantage accumulates with training tokens, producing a widening performance gap (temporal trajectory signature)

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (Primary) | OLMo-7B MMLU/HellaSwag ratio > Pythia-6.9B ratio at ~300B training tokens | Ratio difference > 0.02, Cohen's d > 0.2, p < 0.05 | Ratio difference ≤ 0.02 OR CI overlap at α=0.05 |
| **P2** | OLMo-7B ARC-Challenge/Easy delta > Pythia-6.9B delta at matched token count | Directional effect, p < 0.10 | OLMo delta ≤ Pythia delta |
| **P3** | Pile sub-domain quality proxy scores correlate positively with Pythia-6.9B benchmark performance | Pearson r > 0.3, p < 0.05 across ≥3/5 benchmarks | r < 0.3 or p > 0.05 for all 5 benchmarks |

---

## Novelty

**What's New:**
- First matched-scale comparison between Pythia-6.9B and OLMo-7B using intermediate checkpoints
- First multi-proxy corpus quality index (n-gram + Flesch-Kincaid + language ID) applied to OOD generalization balance
- First temporal trajectory analysis to bound architecture vs. data quality confound
- First archival experiment (no new training) to test curation quality → generalization balance hypothesis

**Differentiation from Prior Work:**
- vs. RefinedWeb [Penedo et al., 2023]: different architecture (Falcon), no matched token count, no OOD/ID balance metric
- vs. D4 [Abbas et al., 2023]: different architecture and benchmarks, no cross-suite comparison
- vs. Pythia dedup [Biderman et al., 2023]: only one curation dimension, no high-curation baseline comparison
- vs. Scaling Laws [Muennighoff et al., 2023]: quantity-quality tradeoff focus, no multi-proxy index, no OLMo comparison

---

## Experimental Design

**Models:**
- Primary: Pythia-6.9B (EleutherAI/pythia-6.9b) vs. OLMo-7B (allenai/OLMo-7B-hf) at intermediate checkpoints (~300B tokens)
- Baselines: Pythia-6.9b-dedup (within-suite dedup ablation), GPT-J-6B (architectural null)
- Temporal: Both models at ~143B and ~300B token checkpoints

**Evaluation:** lm-evaluation-harness — MMLU (5-shot), HellaSwag (0-shot), ARC-Easy/Challenge (25-shot), WinoGrande (5-shot), TruthfulQA (0-shot, mc2)

**Quality Proxy Computation:**
- 10K documents sampled per sub-domain from The Pile and per source from Dolma
- Metrics: n-gram repetition rate (1 - bigram repetition fraction), Flesch-Kincaid grade level (normalized), fastText language ID confidence
- Composite: unweighted average (pre-specified; sensitivity analysis recommended)

**Secondary Analysis:** Min-K% Prob contamination audit on MMLU, HellaSwag, ARC, WinoGrande, TruthfulQA for both models

---

## Limitations

1. **Architecture confound**: GPT-Neo (Pythia) vs. LLaMA-style (OLMo) differences cannot be fully eliminated; temporal trajectory bounds but does not eliminate this
2. **Two-point comparison**: Only two corpora compared — cannot establish a continuous curation-performance curve
3. **Approximate token matching**: "~300B tokens" is approximate; exact checkpoint verification required before execution
4. **Quality index construct validity**: n-gram + Flesch-Kincaid + language ID may not capture the most relevant quality dimensions for downstream generalization

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met at Exchange 12 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Architecture confound (bounded), token count matching (verifiable), index weights (pre-specified) |
| **Phase 2B Readiness** | READY |

---

*Generated by Phase 2A Self-Contained Tikitaka Loop (Independent Controller Ablation)*
*All 6 personas participated: Dr. Nova (🔭), Prof. Vera (🔬), Dr. Sage (🎯), Prof. Pax (⚙️), Dr. Ally (🛡️), Prof. Rex (🔍)*
