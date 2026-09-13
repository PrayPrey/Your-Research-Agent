# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-03-17T07:55:00Z
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: No Observational Study Linking Documented LLM Curation Choices to Benchmark Variance
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 criteria met — SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS addressed

### Key Insights
1. Binary feature extraction (YES/NO for 4 curation dimensions) is more defensible than a continuous CDOI score — resolves inter-annotator agreement concerns
2. Architecture family fixed effects replace structural scaling curve fitting — handles leaderboard heterogeneity correctly
3. Conditional interpretation pathways (Q-mechanism vs. organizational competence) prevent post-hoc rationalization
4. Bridge validation doubles as an independent secondary hypothesis on model card fidelity
5. LLM Documentation-Benchmark Registry is a reusable dataset contribution regardless of primary hypothesis outcome

### Breakthrough Moments
- Exchange 4: Prof. Rex proposed scaling-law residual framework — aligning study with Subramanyam et al. (2025)
- Exchange 9: Prof. Pax identified architecture FE as simpler, more valid alternative to structural scaling curve fitting
- Exchange 13: Dr. Ally synthesized complete pre-registered design with 4 success criteria
- Exchange 15: Dr. Nova recognized LLM Documentation-Benchmark Registry as independent contribution

---

## Final Hypothesis

### Title
Curation Documentation as Benchmark Performance Predictor: An Observational Study of Open-Weight LLMs

### Hypothesis ID
H-DocCuration-v1

### Core Claim
Under the set of open-weight LLMs on the Open LLM Leaderboard v1, if models have documented pretraining data curation practices (binary indicators: deduplication, perplexity filtering, domain composition reporting, decontamination), then those models exhibit ≥0.5 percentage points higher performance on MMLU (knowledge-recall) relative to a scale-and-architecture baseline, because documented curation practices proxy for higher effective data quality Q, which reduces loss preferentially on knowledge-intensive tasks.

### H0 (Null Hypothesis)
No significant difference in MMLU performance between documented and undocumented models after controlling for log(N), log(D), and architecture family fixed effects (β_docs = 0).

### Mechanism
1. Documentation reflects implementation — labs documenting curation have implemented it rigorously
2. Implemented curation increases effective data quality Q (Subramanyam et al. 2025: Q = 1−CR or Q = e^{−Δ})
3. Higher Q preferentially reduces loss on knowledge-recall benchmarks vs. reasoning benchmarks
**Conditional**: if bridge validation fails → interpret as organizational competence proxy, not Q mechanism

---

## Predictions

### P1 (Primary)
Models with ≥3 of 4 documentation features score ≥0.5 pp higher on MMLU within matched architecture-scale bands.
- **Success**: Adjusted mean difference ≥0.5 pp AND permutation p < 0.01 within bins
- **Failure**: Difference < 0.2 pp OR permutation p ≥ 0.05

### P2 (Secondary)
Documentation coefficient is larger for MMLU/ARC than HellaSwag/WinoGrande.
- **Success**: β_docs(MMLU) > β_docs(HellaSwag) with F-test p < 0.05
- **Failure**: Coefficients indistinguishable across benchmark types

### P3 (Secondary)
Documentation block explains ≥3% of residual MMLU variance (partial R² ≥ 0.03).
- **Success**: Partial R² ≥ 0.03 with 95% CI lower bound > 0.01
- **Failure**: Partial R² < 0.01

---

## Novelty
This is the first systematic observational study linking documented pretraining data curation practices (binary indicators from model cards) to benchmark performance variance across deployed LLMs. Prior work used computed perplexity (Thrush et al. 2024) or controlled experimental manipulation (Subramanyam et al. 2025) — neither used human-written documentation as a quality proxy at scale. The LLM Documentation-Benchmark Registry (new dataset) is a lasting contribution.

---

## Experimental Design

**Dataset**: Open LLM Leaderboard v1 static snapshot + Hugging Face model cards

**Sample**: ~500-2000 open-weight LLMs with non-missing benchmark scores and accessible model cards

**Independent Variables**: 4 binary documentation features (dedup, perplexity_filter, domain_pct, decontam)

**Dependent Variables**: Benchmark accuracy scores (MMLU primary; ARC, HellaSwag, TruthfulQA, WinoGrande secondary)

**Controls**: log(N), log(D), architecture family fixed effects

**Analysis**: OLS regression + within-bin permutation (1,000 shuffles) + leave-one-family-out stability + verbosity placebo

**Bridge Validation (secondary)**: Test whether documented deduplication predicts lower duplication rate and lower cross-entropy under reference model in accessible training corpora

---

## Limitations
- Organizational competence confound cannot be fully eliminated without natural experiment or IV design
- Bridge validation limited to open-weight models with accessible training corpora (<50% of leaderboard)
- Binary feature extraction may miss nuanced documentation specificity
- Results limited to Open LLM Leaderboard v1 protocol (ARC, HellaSwag, MMLU, TruthfulQA, WinoGrande, GSM8K)
- Scope limited to pretraining curation; post-training quality practices excluded

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | CONVERGE — all 6 criteria met at exchange 15 |
| **Clarity Verified** | Yes |
| **Feasibility Confirmed** | Yes (OLS on public data, no GPU/corpus streaming) |
| **Remaining Objections** | Organizational competence confound (limitation, not blocker) |

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
