# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-04-19T13:43:00
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: GAP-1
- **Gap Title**: Validated Ground Truth Labels for Misalignment Detection
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 15

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 15

**Convergence Reason**: All 6 convergence criteria met: specific core claim formulated (geometric manifold of alignment failures), causal mechanism explained (4-step chain from human judgments to stable structure), testable predictions defined (3 primary with falsification criteria), novelty articulated (paradigm shift from reward modeling to geometric alignment maps), feasibility validated (12-experiment design with existing datasets), major objections addressed (base-rate audit, encoder robustness, reward model differentiation)

### Key Insights

1. **Paradigm Shift from Detection to Geometry**: The discussion evolved from "can we detect misalignment" to "does RLHF data encode geometric structure of alignment failures." This reframing elevates contribution from incremental detection to fundamental discovery about alignment space.

2. **Base-Rate Audit as Gate Experiment**: Prof. Pax and Prof. Vera identified that the entire geometric framing depends on Experiment 0 showing p ≥ 0.40 genuine violations in rejected samples. This became the crucial gate that determines whether to pursue geometric analysis or pivot to preference prediction.

3. **Separability ≠ Manifold Structure**: Prof. Rex's critique distinguished mere classification separability from genuine manifold structure. This led to Experiments 10-12 proving continuous geometry (severity-distance correlation), reward model differentiation, and encoder robustness.

4. **Four-Tier Success Framework**: Dr. Sage's contribution tiering (Detection → Semantic → Transfer → Geometry) ensures value at multiple levels, from incremental tools to paradigm-shifting discoveries.

### Breakthrough Moments

1. **Exchange 5**: Prof. Pax asked "is it even plausible that pairwise preferences induce a stable alignment manifold?" - shifted focus from classification to geometric structure.

2. **Exchange 11**: Dr. Nova reframed as "reverse-engineering human alignment intuition from preference data" - introducing alignment archaeology metaphor.

3. **Exchange 13**: Dr. Ally synthesized complete 12-experiment design with pre-registered thresholds addressing all critiques.

4. **Exchange 14-15**: Prof. Rex and Dr. Sage separated separability from manifold claims via continuous structure tests (severity-distance correlation).

---

## Final Hypothesis

### Title
Geometric Structure of Alignment Failures in RLHF Preference Data

### Hypothesis ID
H-GeomAlign-v1

### Core Claim

Under the scope of RLHF harmless-preference evaluation, if we analyze the HH-RLHF dataset's chosen/rejected response pairs in embedding space, then we will discover a multi-dimensional geometric manifold where rejected responses cluster along interpretable failure axes with distances encoding violation severity, because human annotators consistently detect implicit alignment violations that induce stable structure across 160K+ pairwise judgments.

### Alternative Hypothesis (H0)

There is no statistically significant geometric structure in rejected vs. chosen responses beyond what is explained by surface lexical patterns, model-specific stylistic artifacts, or a single dominant toxicity axis.

### Mechanism

**4-Step Causal Chain:**

1. **Human Judgment**: Annotators evaluate response pairs under helpfulness/harmlessness criteria, rejecting responses that violate safety principles (implicit or explicit violations)

2. **High-Density Sampling**: Aggregation of 160K+ rejection judgments creates comprehensive sampling of the alignment failure space with diverse violation types and severities

3. **Geometric Emergence**: In embedding space, rejected responses form clusters with geometric properties: (a) distance from chosen distribution encodes violation severity, (b) principal component directions encode violation types (toxicity, misinformation, instruction-following)

4. **Cross-Model Stability**: This structure is stable across different encoders (RoBERTa, DeBERTa, SentenceTransformers) and generalizes to new model families, indicating data-intrinsic rather than model-specific structure

---

## Predictions

### P1: Continuous Severity Structure (PRIMARY)

**Statement**: Euclidean distance in embedding space between rejected and chosen responses correlates with human-judged violation severity (Spearman ρ ≥ 0.65)

**Test Method**: Sample 300 triplets (low, medium, high severity) from rejected responses; measure manifold distance to chosen centroid; compute Spearman correlation with human severity ranks

**Success Criterion**: Spearman ρ ≥ 0.65 AND triplet ordering preserved in ≥80% of cases

**Falsification**: If ρ < 0.50 or ordering preservation <60%, continuous structure claim is rejected

### P2: Multi-Type Separability (PRIMARY)

**Statement**: Rejected responses cluster along ≥3 orthogonal axes corresponding to distinct violation types (toxicity, misinformation, instruction-following)

**Test Method**: MANOVA on embeddings labeled by violation type; compute effect sizes for each principal component

**Success Criterion**: ≥3 PCs with Cohen's d ≥ 0.5; no single PC explains >80% variance

**Falsification**: If only 1-2 PCs with d ≥ 0.5, or single PC >80% variance, multi-dimensional claim is rejected

### P3: Encoder Robustness

**Statement**: Geometric structure is intrinsic to data, not encoder-specific (PC alignment across RoBERTa, DeBERTa, SentenceTransformer)

**Test Method**: Extract PCs from three different encoders; compute pairwise cosine similarity of corresponding PC directions

**Success Criterion**: Top-3 PC cosine similarity ≥ 0.70 for all encoder pairs

**Falsification**: If any pair <0.60, structure is representation-dependent artifact

---

## Novelty

### Preserved Novelty

First work to frame RLHF preference data as containing discoverable geometric structure of alignment failures, enabling reusable cross-model safety evaluation without new annotation.

### Key Innovation

Transition from black-box reward modeling to interpretable geometric alignment maps with explicit semantic axes:
- **Distance = Severity**: Euclidean distance from chosen distribution encodes violation severity
- **Direction = Type**: Principal component directions encode violation categories
- **Reusable Structure**: Generalizes across models without retraining

### Differentiation from Prior Work

| Prior RLHF Research | Our Approach |
|---------------------|--------------|
| Trains reward models (black box) | Extracts interpretable geometric structure |
| Requires retraining per model | Manifold structure generalizes cross-model |
| Consumes preference data for training | Treats preference data as persistent benchmark |
| No geometric interpretability | Explicit semantic axes with geometric meaning |

---

## Experimental Design

### 12-Experiment Program with 4-Tier Success Framework

**Tier 1: Detection (Experiments 0-4)**
- Exp 0: Base-rate audit (p ≥ 0.40 genuine violations)
- Exp 1: Surface baseline (TF-IDF + features, F1 < 0.65)
- Exp 2: Semantic detection (RoBERTa-base, F1 ≥ 0.60, ΔF1 ≥ 0.15)
- Exp 3: Cross-model transfer (F1 ≥ 0.65 bidirectional)
- Exp 4: Error analysis (<30% benign rejections)

**Tier 2: Semantic Robustness (Experiments 5-7)**
- Exp 5: Lexical ablation (A_m ≥ 0.60, drop ≤ 0.10)
- Exp 6: Per-violation transfer (recall ≥ 0.60 on 3+ categories)
- Exp 7: Paraphrastic invariance (confidence drop ≤ 0.15)

**Tier 3: Cross-Model Transfer (Experiments 8-9)**
- Exp 8: Geometric separability (≥3 PCs, d ≥ 0.5, no single axis >80%)
- Exp 9: Graceful degradation (linear F1 decline, no cliff >0.15)

**Tier 4: Manifold Geometry (Experiments 10-12)**
- Exp 10: Continuous structure (Spearman ρ ≥ 0.65 severity-distance)
- Exp 11: Reward model comparison (≥20% divergence cases)
- Exp 12: Encoder robustness (PC cosine ≥ 0.70 across encoders)

### Datasets & Models

**Datasets**: HH-RLHF harmless subset (primary), WebGPT, Summarization from Feedback (transfer validation)

**Models**: RoBERTa-base (primary), DeBERTa-v3-base, SentenceTransformer all-mpnet-base-v2 (encoder robustness)

**Baselines**: TF-IDF logistic regression, Bradley-Terry reward model, random classifier

### Evaluation Protocol

- 80/20 stratified train/test split (by violation type)
- 3-seed reproducibility (42, 123, 456)
- Report mean ± std across seeds
- Zero-shot cross-dataset transfer (no retraining)

---

## Key Assumptions

**A1 (Base-Rate Sufficiency)**: HH-RLHF harmless subset contains ≥40% genuine policy violations enabling geometric structure emergence. *Consequence if violated*: Label noise dominates, manifold cannot be learned.

**A2 (Semantic Encoding)**: Pretrained LM embeddings capture alignment-relevant features beyond surface patterns. *Validated by*: Lexical ablation tests (Exp 5, 7).

**A3 (Cross-Model Stability)**: Alignment failures are sufficiently model-agnostic to transfer. *Validated by*: Cross-dataset experiments (Exp 3, 6).

**A4 (Encoder Invariance)**: Geometric structure is data-intrinsic, not encoder artifact. *Validated by*: Cross-encoder PC alignment (Exp 12).

**A5 (Violation Orthogonality)**: Different failure types occupy distinct embedding regions. *Validated by*: Multi-axis separability test (Exp 8).

---

## Scope & Limitations

### Applies To
- RLHF datasets with harmlessness annotations (HH-RLHF, WebGPT, Summarization from Feedback)
- Conversational AI safety evaluation using pretrained encoders
- Cross-model harmlessness assessment without new annotation
- Violation types present in training data (toxicity, misinformation, instruction-following)

### Does Not Apply To
- Helpfulness-only preferences (outside harmlessness scope)
- Novel violation types not in HH-RLHF (jailbreak attacks, prompt injection)
- Non-conversational tasks (code generation, reasoning)
- Extreme distribution shifts (highly verbose vs. concise models)

### Known Limitations
1. Requires base-rate ≥40% genuine violations for structure emergence
2. Transfer degrades under extreme distribution shift (graceful degradation monitored)
3. Annotation bias from HH-RLHF annotator pool may limit cultural/temporal generalization
4. Single-language analysis (English only)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 15 exchanges |
| **Clarity Verified** | Yes - hypothesis, mechanism, predictions all explicit |
| **Remaining Objections** | Base-rate dependency, reward model differentiation, style entanglement (all addressed via experiments) |

### Remaining Concerns (Prof. Rex)

1. **Base-Rate Dependency**: Entire program depends on Experiment 0 showing p ≥ 0.40. *Mitigation*: Run with multiple thresholds, report sensitivity analysis.

2. **Reward Model Redundancy**: Without Experiment 11 comparison, may rediscover reward model structure. *Mitigation*: Make Exp 11 non-negotiable for publication.

3. **Style Entanglement**: Graceful degradation could reflect style vs. content. *Mitigation*: Add stylistic normalization controls to Exp 9.

### Field-Level Impact

**If Tier 4 Success**: Discover that RLHF preference data encodes reusable geometric structure of alignment failures, enabling:
- Zero-shot violation detection via geometric proximity
- Severity calibration without additional annotation
- Model safety profiling via manifold position
- Alignment principle archaeology across model generations

**Publication Target**: "Geometric Structure of Alignment Failures: Discovering Reusable Safety Manifolds in RLHF Preference Data"

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
