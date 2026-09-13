# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-31T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (independent-controller ablation)
- **Gap ID**: gap-1
- **Gap Title**: Lack of Systematic Black-Box UQ Benchmark Comparison Across Factual QA Datasets
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 8

**Convergence Reason**: All six convergence criteria met at Exchange 8. Prof. Vera issued convergence vote after SPECIFIC/MECHANISM/PREDICTIONS/NOVELTY/FEASIBILITY/OBJECTIONS all satisfied.

### Key Insights
- The core gap is not whether sampling-based consistency works (it does on WikiBio/TriviaQA/NQ) — it's whether it works across all four factual QA benchmarks under identical controlled conditions
- TruthfulQA is the critical hard case: adversarially designed to produce confident, consistent wrong answers that may suppress the SMC signal
- The baseline must be verbalized confidence (black-box), not token log-probability (white-box oracle) — this sharpens the experimental design significantly
- NLI scorer is potentially OOD for very short factual answers; embedding cosine similarity serves as parallel robustness check

### Breakthrough Moments
- Prof. Vera's clarification that baseline must be verbalized confidence (not log-probability) resolved a fundamental experimental design ambiguity
- Prof. Rex's NLI OOD concern was converted into a design choice: run both SMC-NLI and SMC-Embed in parallel
- Dr. Ally's AUROC ordering prediction (HaluEval > TriviaQA/NQ > TruthfulQA) turned a potential failure mode into a falsifiable prediction

---

## Final Hypothesis

### Title
**Semantic Mode Consistency (SMC) as a Black-Box Hallucination Predictor Across Factual QA Benchmarks**

### Hypothesis ID: H-SMC-v1

### Core Claim (Under-If-Then-Because)
Under factual question-answering with black-box LLMs (no logit access), if we compute NLI-based Semantic Mode Consistency (SMC) across N=10 stochastic samples per question using a local DeBERTa-v3-large NLI scorer, then this consistency score will serve as a reliable hallucination predictor (AUROC ≥ 0.70) across all four existing factual QA benchmarks (TriviaQA, NaturalQuestions, HaluEval, TruthfulQA), because factually grounded answers produce semantically convergent sample distributions while hallucinated answers exhibit semantic divergence, reflecting the model's internal uncertainty manifesting as multimodal semantic output.

**Null Hypothesis:** There is no significant difference in hallucination prediction AUROC between SMC-NLI (N=10 samples) and verbalized confidence baseline. SMC-NLI AUROC < 0.65 on ≥ 2 of 4 benchmarks.

### Mechanism
1. **Factual certainty → concentrated semantic probability mass**: When an LLM has strong parametric knowledge, its distribution concentrates over a narrow semantic cluster — multiple stochastic samples remain semantically equivalent.
2. **Hallucination → multimodal semantic distribution**: When the model hallucinates, sampling spreads across multiple incompatible semantic clusters — different samples produce contradictory claims.
3. **NLI pairwise agreement → SMC scalar**: For N=10 samples, 45 pairwise NLI classifications. SMC = fraction of consistent pairs. Low SMC → high hallucination probability.

**Key tension**: TruthfulQA's adversarial design may produce high-consistency wrong answers, suppressing SMC signal on that benchmark specifically.

---

## Predictions

| ID | Statement | Success Criterion | Falsification |
|----|-----------|-------------------|---------------|
| **P1** (primary) | SMC-NLI (N=10) achieves AUROC ≥ 0.70 on all 4 benchmarks | AUROC ≥ 0.70 on TriviaQA, NQ, HaluEval, TruthfulQA | AUROC < 0.65 on ≥ 2 benchmarks OR < 0.60 on any single benchmark |
| **P2** | AUROC ordering: HaluEval > TriviaQA ≈ NQ > TruthfulQA | Non-overlapping 95% CI: AUROC(HaluEval) > AUROC(TruthfulQA) | TruthfulQA AUROC ≥ HaluEval AUROC |
| **P3** | N-efficiency elbow at N ≤ 10 | AUROC(N=10) ≥ 0.95 × AUROC(N=20) on TriviaQA ablation | AUROC(N=20) > 1.05 × AUROC(N=10) |

---

## Novelty

**What's new**: First systematic multi-benchmark evaluation of black-box sampling consistency as hallucination predictor. SMC framing (semantic mode characterization) positions method relative to Semantic Entropy (requires logits) and SelfCheckGPT (WikiBio only). N-efficiency analysis on factual QA is novel. Dual NLI+embedding consistency comparison is novel.

**Key differentiation**:
- vs. SelfCheckGPT: 4 factual QA benchmarks vs. WikiBio only; modern instruction-tuned model; N-ablation
- vs. Semantic Uncertainty: strictly black-box (no logits); HaluEval/TruthfulQA coverage; verbalized confidence comparison
- vs. Self-Consistency: hallucination classification (AUROC) vs. reasoning accuracy; factual QA domain

---

## Experimental Design

**Prerequisite (before main study):**
- N-ablation: 200 TriviaQA questions, N ∈ {1,3,5,10,20}, SMC-NLI only
- Confirm elbow at N ≤ 10; if elbow > 10, revise main study to N=20

**Main Experiment:**
- **Primary model**: Llama-3-8B-Instruct (local, HuggingFace)
- **Primary benchmark**: HaluEval (balanced binary labels)
- **Secondary benchmarks**: TriviaQA, NaturalQuestions, TruthfulQA-MC
- **Questions**: 1000 per benchmark, stratified sampling
- **Sampling**: N=10 at temperature=0.7
- **Consistency metrics**: SMC-NLI (DeBERTa-v3-large) + SMC-Embed (all-mpnet-base-v2)
- **Baselines**: Verbalized confidence, SelfCheckGPT replication, N=1 degenerate
- **Evaluation**: AUROC + AUPRC + bootstrap 95% CIs

**Secondary validation**: GPT-4o on 200-question subset (HaluEval + TruthfulQA)

---

## Limitations

- Hypothesis tested on single model (Llama-3-8B-Instruct) — cross-model generalization deferred to Gap 3
- No multimodal extension — deferred to Gap 3
- NLI scorer OOD for very short answers (<5 words) — mitigated by SMC-Embed parallel metric
- N=10 is hypothesis-driven; N-ablation prerequisite validates before main study
- English language only
- TruthfulQA adversarial questions may suppress SMC signal (predicted, not a confound)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-SMC-v1 |
| **Discussion Convergence** | Exchange 8, unanimous (8 exchanges, 6 personas) |
| **Clarity Verified** | Yes |
| **Feasibility Confirmed** | Yes (Prof. Pax) |
| **Remaining Objections** | NLI OOD (mitigated), N=10 assumption (prerequisite N-ablation) |
| **Phase 2B Readiness** | READY |

---

*Phase 2A complete. Proceed to Phase 2B for experimental planning.*
