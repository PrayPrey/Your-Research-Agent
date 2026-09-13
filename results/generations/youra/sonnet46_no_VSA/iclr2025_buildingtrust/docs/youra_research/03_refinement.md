# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-07-29T12:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap1
- **Gap Title**: Lack of Controlled Architecture-Comparative Robustness Study Across Full NLP Benchmark Suite
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova (Creative Novelty Explorer), Prof. Vera (Rigorous Validation Architect), Dr. Sage (Research Impact Evaluator), Prof. Pax (Feasibility & Reality Checker), Dr. Ally (Hypothesis Strengthening Champion), Prof. Rex (Hypothesis Stress-Test Master)

**Total Exchanges**: 16

**Convergence Reason**: All 6 convergence criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS) after 16 exchanges via Tikitaka loop between external LLM (GPT-5.2) and Claude alternating persona assignments.

### Key Insights

1. The core reframing: architecture **topology** (attention direction) may define a characteristic perturbation vulnerability **profile** (Δ*-vector), not just a scalar robustness level. This is qualitatively different from prior work asking "is model X more robust than model Y?"

2. AdvGLUE's semantic validity curation (~10% retention, ≥4/5 annotator agreement) ensures Δ* measures genuine comprehension failure. The finding that robust training yields only +3-4 point improvements suggests robustness is structurally determined — architecture fingerprinting provides the structural explanation.

3. Surrogate bias in AdvGLUE (BERT/RoBERTa surrogates used for generation) is the key validity threat, resolved by a three-partition design with cross-partition classifier generalization as the primary falsification test.

### Breakthrough Moments

- **Exchange 2 (Dr. Nova)**: Shift from "which architecture is more robust" to "what is the architecture-specific perturbation signature" — the fingerprinting framing.
- **Exchange 3 (Prof. Rex)**: Surrogate bias identified as key threat → led to 3-partition cross-generalization design.
- **Exchange 7 (Prof. Vera)**: Pre-registration protocol with quantitative thresholds — transformed exploratory to confirmatory.
- **Exchange 9 (Prof. Rex)**: Specific ΔC_ℓ metric replacing vague "attention entropy" — made mechanism operationalizable.
- **Exchange 14 (Dr. Sage)**: Contribution hierarchy (descriptive → replicative → mechanistic → predictive) targeting levels 3+4.

---

## Final Hypothesis

### Title
Architecture-Family Robustness Fingerprinting in NLP: Attention Topology Predicts Perturbation Vulnerability Profiles

### Hypothesis ID
`H-ArchRobustFingerprint-v1`

### Core Claim

Under scale-matched conditions (~110-250M parameters), transformer language models exhibit architecture-family-specific perturbation vulnerability signatures — measurable as normalized Δ*-vectors across AdvGLUE/ANLI/CheckList attack categories — that replicate within architecture families across surrogate-diverse benchmark partitions and enable above-chance architecture-family classification (≥60% leave-one-model-out, 95% CI > 33%) from robustness profiles alone.

Formal: **Under scale-matched conditions on existing NLP benchmarks, if transformer models are grouped by architecture family and evaluated on AdvGLUE/ANLI/CheckList using Δ* = (Acc_clean − Acc_adv)/Acc_clean, then each architecture family will exhibit a characteristic Δ*-vector profile with greater within-family similarity than between-family similarity, because bidirectional (encoder-only) vs. causal (decoder-only) vs. cross-attention (encoder-decoder) topology constrains feature geometry differently under distribution shift.**

### Mechanism

4-step causal chain:
1. Attention topology (bidirectional/causal/cross-attention) shapes token representation aggregation during inference.
2. Under local perturbation: bidirectional attention redistributes globally to perturbed tokens (amplifies noise); causal attention processes perturbation locally.
3. The redistribution pattern determines feature geometry at the classification head under perturbation.
4. Systematic feature geometry difference → characteristic Δ*-vector per family → within-family similarity > between-family → above-chance classification.

**Testable via**: Attention concentration ΔC_ℓ = C_ℓ(adv, perturbed span) − C_ℓ(clean, same span) mediation analysis.

---

## Predictions

### P1 (Primary): Architecture × AttackType Interaction
- **Statement**: Architecture × AttackType interaction in Δ* is significant (p < 0.05, bootstrap CI excludes zero) after controlling for clean accuracy, objective, and tokenizer; replicates in ≥2/3 benchmark partitions.
- **Test**: Mixed-effects model Δ* ~ ArchFamily × AttackType + Objective + Tokenizer + CleanAccuracy + (1|Model)
- **Success**: p < 0.05; η² > 0.15 in ≥50% reliable attack categories (split-half r ≥ 0.7, ≥50 examples)
- **Falsification**: p ≥ 0.05 OR η² < 0.15 criterion fails in majority of reliable categories

### P2 (Secondary): Above-Chance Architecture Classification
- **Statement**: Δ*-vector classifier trained on one benchmark partition achieves ≥60% leave-one-model-out accuracy on held-out partition (95% CI entirely above 33%).
- **Test**: Cross-partition classification (train on automatic C1-C7, test on human-crafted C8-C11, and vice versa); leave-one-model-out CV
- **Success**: ≥60% accuracy, 95% bootstrap CI lower bound > 33%
- **Falsification**: ≤40% accuracy or CI overlaps 33% baseline

### P3 (Secondary): Attention Topology Mediation
- **Statement**: mean(ΔC) reduces Architecture × WordLevel coefficient magnitude ≥30% with bootstrap CI excluding zero.
- **Test**: Full model (with mean(ΔC)) vs. base model; bootstrap 1,000 iterations; Sobel mediation test
- **Success**: ≥30% coefficient reduction, CI excludes zero
- **Falsification**: <30% reduction or CI includes zero

---

## Novelty

### What's New
- **Architecture-family robustness fingerprinting**: Treating Δ*-vectors as architectural identity documents — first study to test whether robustness profiles cluster by architecture family with formal classification.
- **Cross-benchmark surrogate-diversity design**: Three-partition evaluation (auto-word / auto-sentence / human-crafted) systematically testing surrogate-bias explanations.
- **Attention topology mediation**: ΔC_ℓ as mechanistic bridge between architectural structure and vulnerability mode.

### How It Differs from Prior Work

| Prior Work | Limitation | Our Contribution |
|-----------|-----------|-----------------|
| EMNLP 2023 (3 models on GLUE) | No AdvGLUE/ANLI; 3 models only; no formal test | 8 models, full suite, formal interaction test + classification |
| TrustLLM [Sun et al., 2024] | Architecture not primary IV; no Δ-vector | Architecture-stratified, Δ*-vector fingerprint, classification |
| AdvGLUE [Wang et al., 2021] | Benchmark paper; no architecture stratification | Uses AdvGLUE as substrate; adds architecture analysis layer |
| Yang et al. [2024] | White-box attacks; not architecture-stratified | Semantic perturbations (AdvGLUE-compatible); architecture as primary IV |

---

## Experimental Design

### Models (7-8 base-scale, ~110-250M parameters)
| Model | Family | Objective | Tokenizer | Parameters |
|-------|--------|-----------|-----------|-----------|
| BERT-base | encoder-only | MLM | WordPiece | 110M |
| RoBERTa-base | encoder-only | MLM | BPE | 125M |
| ELECTRA-base | encoder-only | RTD | WordPiece | 110M |
| ALBERT-base-v2 | encoder-only | MLM | SentencePiece | ~11M eff. |
| GPT-2 | decoder-only | AR-LM | BPE | 117M |
| OPT-125M | decoder-only | AR-LM | GPT-2 BPE | 125M |
| T5-base | encoder-decoder | span-corruption | SentencePiece | 250M |
| BART-base | encoder-decoder | denoising | BPE | 140M |

### Datasets
- **AdvGLUE**: 4,978 curated adversarial cases; 5 tasks; 11 attack categories (C1-C11); adversarialglue.github.io
- **ANLI-R3**: 1,200 test examples; human adversarial; allennlp.org/anli
- **CheckList**: Template-based surrogate-free perturbations; pip install checklist
- **GLUE**: Clean training/validation for fine-tuning; HuggingFace datasets

### Statistical Analysis
- Mixed-effects model with bootstrap (1,000 iterations)
- Permutation MANOVA for between/within-family variance decomposition
- Leave-one-model-out cross-validation for classifier
- Sobel test / bootstrap for mediation

---

## Limitations

- **Scale scope**: Results at base scale (~110-250M) may not generalize to large models (7B+) where capacity effects may dominate architecture effects
- **Decoder-only family**: Only 2 models at base scale (GPT-2 + OPT-125M); leave-one-model-out is borderline — addition of OPT-350M recommended
- **AdvGLUE surrogate bias**: Automatic attacks generated with encoder surrogates; cross-partition generalization test is the primary control
- **ELECTRA-BERT contrast**: Imperfect (generator-discriminator training changes more than just the objective); treat as sensitivity analysis
- **AdvGLUE metadata**: Surrogate fooling count per example may not be in released dataset; attack-method stratification as proxy
- **Instruction-tuned models excluded**: RLHF fine-tuning decreases robustness (TREvaL confound); out of scope for this study

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All 6 criteria met after 16 exchanges |
| **Clarity Verified** | Yes |
| **Remaining Objections** | Decoder-only family needs 3rd model; ELECTRA-BERT contrast is sensitivity analysis only |
| **Feasibility** | CONFIRMED — ~2-3 weeks, public models + datasets |
| **Pipeline Constraints** | SATISFIED — no new benchmarks, no annotation, no synthetic data |
| **Phase 2B Ready** | YES |

---

*Phase: 2A — Hypothesis Generation (Self-Contained Tikitaka Loop)*
*Hypothesis ID: H-ArchRobustFingerprint-v1*
*Next Phase: 2B — Research Planning*
