# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-21T00:00:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Gap ID**: gap-2-token-aggregation
- **Gap Title**: Systematic Comparison of Token-Level Uncertainty Aggregation Strategies Without Fine-Tuning
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 8

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 8

**Convergence Reason**: All 6 criteria met at Exchange 8 — SPECIFIC (directional per-benchmark predictions with AUROC thresholds), MECHANISM (hallucination type determines aggregation optimality), PREDICTIONS (P1-P3 with bootstrap CI), NOVELTY (first isolation + Type A/B taxonomy), FEASIBILITY (lm-polygraph + open-weight + existing splits; single pass), OBJECTIONS (tokenization, function redundancy, label noise — all addressed)

### Key Insights
1. **Hallucination type taxonomy**: Type A (imitative/uniform) vs. Type B (recall-failure/peaked) — a new classification axis with direct measurement implications. Recall failures produce a single highly uncertain token; imitative falsehoods produce uniformly high probability across all tokens.
2. **Min log-prob as signal**: The worst-case token uncertainty (min log-prob) is theoretically the optimal signal for recall-failure hallucinations — but no paper has tested this systematically as the sole variable.
3. **Mean wins on TruthfulQA**: Counter-intuitive finding from the discussion — TruthfulQA hallucinations are uniform high confidence (mean captures this); min log-prob would miss the signal because no single token is strongly uncertain.
4. **Geometric mean = mean for AUROC**: A monotone transform of mean produces identical AUROC rankings — reduces the ablation cleanly to 3 genuinely distinct functions (min, mean, raw-sum).
5. **lm-polygraph is the implementation**: All 3 aggregation functions are already implemented as distinct UE estimators; LLaMA-2 and Mistral are supported; this is an execution task.

### Breakthrough Moments
- **Exchange 6 (Prof. Rex)**: Reversed the initial naive prediction — TruthfulQA hallucinations are uniformly confident, not single-token-uncertain; mean wins, not min/max. This sharpened the hypothesis from "short answers → min" to "hallucination type → aggregation."
- **Exchange 7 (Dr. Nova)**: Synthesized the Type A/B taxonomy from Prof. Rex's insight; proved geometric mean is redundant; crystallized the directional prediction.
- **Exchange 2 (Prof. Vera)**: Established bootstrap CI methodology and H0 formulation; gave the study a rigorous statistical framework from the start.

---

## Final Hypothesis

### Title
Hallucination-Type-Dependent Token Aggregation (HDTA): Optimal Token Log-Prob Aggregation Function Is Determined by Hallucination Type on Existing Factual QA Benchmarks

### Hypothesis ID
H-TokenAgg-v1

### Core Claim
Under frozen open-weight LLMs (LLaMA-2-7B, Mistral-7B-v0.1) evaluated on existing factual QA benchmarks with binary correctness labels, if we vary only the token-level log-probability aggregation function (min, mean, raw-sum) applied to single-forward-pass output probabilities, then the AUROC for hallucination detection will differ significantly across aggregation functions in a benchmark-type-dependent pattern: **min log-prob achieves AUROC ≥ mean log-prob on factual recall benchmarks (TriviaQA, NQ) by ≥ 0.02**, while **mean log-prob achieves AUROC ≥ min log-prob on imitative-falsehood benchmarks (TruthfulQA) by ≥ 0.02**, because hallucination signal concentrates at the single most uncertain fact-token in recall failures but is distributed uniformly across all tokens in imitative falsehoods.

**H0 (Null)**: All three aggregation functions produce statistically equivalent AUROC (differences within bootstrap 95% CI, < 0.02) across all benchmarks.

### Mechanism
1. **Hallucination type → distribution shape**: Recall failures produce peaked uncertainty (single low log-prob fact-token). Imitative falsehoods produce flat high-probability wrong answers (all tokens uniformly high probability).
2. **Distribution shape → aggregation optimality**: Min log-prob captures the peaked distribution's bottleneck. Mean log-prob captures the elevated mean of flat distributions.
3. **Aggregation optimality → AUROC differential**: Better signal alignment → higher AUROC → benchmark-type-dependent pattern.

---

## Predictions

| ID | Primary | Statement | Success Criterion |
|----|---------|-----------|-------------------|
| P1 | ✅ | min log-prob AUROC ≥ mean log-prob AUROC + 0.02 on TriviaQA and NQ for both models | AUROC diff ≥ 0.02, bootstrap 95% CI lower bound > 0 |
| P2 | ❌ | mean log-prob AUROC ≥ min log-prob AUROC + 0.02 on TruthfulQA for both models | AUROC diff ≥ 0.02, bootstrap 95% CI lower bound > 0 |
| P3 | ❌ | raw-sum AUROC < min and mean on all three benchmarks | Directional; no threshold required |

**Statistical methodology**: Bootstrap CI (n=1000) on pairwise AUROC differences; Friedman test for global equivalence. Farquhar 2023 exact splits for TriviaQA/NQ; standard HuggingFace splits for TruthfulQA.

---

## Novelty

**Key Innovation**: First systematic ablation of token log-prob aggregation as the sole experimental variable, with mechanistic predictions grounded in a hallucination type taxonomy (Type A imitative vs. Type B recall failure).

**Differentiation from prior work**:
- Fadeeva 2024 (CCP): uses mean implicitly; never ablates min vs. mean vs. sum in isolation
- Farquhar 2023 (SE): multi-sample, not single-pass; sum within clusters; no function ablation
- Manakul 2023 (SelfCheckGPT): ad-hoc probability baselines; not a controlled study
- Liu 2025 (Survey): identifies this gap as open; our study fills it with theoretical grounding

---

## Experimental Design

**Models**: LLaMA-2-7B (meta-llama/Llama-2-7b-hf), Mistral-7B-v0.1 (mistralai/Mistral-7B-v0.1). Frozen weights; greedy decoding; single forward pass.

**Datasets**:
- TriviaQA — Farquhar 2023 splits (jlko/semantic_uncertainty) [confirmatory]
- Natural Questions — Farquhar 2023 splits (jlko/semantic_uncertainty) [confirmatory]
- TruthfulQA generation — HuggingFace truthful_qa [confirmatory, secondary]
- SciQ — HuggingFace sciq [exploratory]

**Aggregation functions**: (1) min log-prob, (2) mean log-prob (= length-normalized sum), (3) raw-sum log-prob

**Baselines for comparison**: Semantic Entropy (Farquhar 2023), SelfCheckGPT NLI (Manakul 2023), CCP mean (Fadeeva 2024), random (AUROC=0.5)

**Implementation**: lm-polygraph (IINemo/lm-polygraph) as primary harness; jlko/semantic_uncertainty for SE baseline; potsawee/selfcheckgpt for SelfCheckGPT baseline.

**Expected runtime**: Hours on a single A100 GPU per model; single forward pass eliminates sampling overhead for the main ablation.

---

## Limitations

- Tokenization granularity varies across model families; within-model is primary; cross-model is secondary replication
- P2 (TruthfulQA) may be weaker at 7B scale where imitative hallucination patterns are less pronounced than at 70B+
- Raw-sum being universally worst requires a length-controlled analysis to isolate length confound from uncertainty signal
- SciQ hallucination type (A or B) is uncertain; exploratory only
- Results apply to factual QA with binary correctness labels; do not generalize to long-form generation or code

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Hypothesis ID** | H-TokenAgg-v1 |
| **Discussion Convergence** | All 6 criteria met at Exchange 8 |
| **Clarity Verified** | Yes |
| **Phase 2B Ready** | Yes |
| **Remaining Objections** | TruthfulQA prediction at 7B scale (mitigated: secondary); 0.02 threshold justification needed |

---

*Phase 2A Complete — proceed to Phase 2B with 03_refinement.yaml as primary input*
