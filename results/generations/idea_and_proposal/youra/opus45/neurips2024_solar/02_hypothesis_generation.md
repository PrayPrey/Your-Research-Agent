# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CSASA-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of multilingual LLM deployment, if linguistically-principled code-switching augmentation is applied during safety alignment training (using sociolinguistic patterns: inter-sentential, intra-sentential, tag-switching), then the model will develop language-invariant safety representations that reduce code-switching attack success rates by ≥30% and improve low-resource language safety by ≥40%, because contrastive learning on diverse surface forms forces the safety encoder to learn semantic intent rather than surface linguistic form.

**Alternative Hypothesis (H0):**
Linguistically-principled code-switching augmentation during safety training does NOT produce language-invariant safety representations, and safety performance on code-switched or low-resource language inputs will not significantly differ from models trained on monolingual English data alone.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Training data augmentation type | Independent | Three conditions: (1) Monolingual English only, (2) Random code-switching, (3) Linguistically-principled code-switching following sociolinguistic patterns | Categorical: 3 levels |
| Code-switching pattern type | Independent | Inter-sentential (switch at sentence boundaries), intra-sentential (within sentences at grammatical points), tag-switching (short phrases/tags) | Categorical: 3 types + combinations |
| Language pairs included | Independent | 5 strategic pairs: English-Chinese, English-Spanish, English-Hindi, English-Arabic, English-Swahili | 5 pairs covering Indo-European, Sino-Tibetan, Indo-Aryan, Semitic, Niger-Congo |
| Attack success rate (ASR) | Dependent | Percentage of code-switched adversarial prompts eliciting unsafe responses on CSRT benchmark | Baseline ~70% (CSRT); Target: ≤40% |
| Safety classification accuracy | Dependent | F1 score on multilingual safety benchmarks (LinguaSafe, SGToxicGuard) | Baseline varies by language; Target: ≥40% improvement on low-resource |
| False refusal rate (FRR) | Dependent | Percentage of benign multilingual queries incorrectly refused | Target: ≤5% increase vs English-only |
| Cross-lingual transfer gap | Dependent | Performance difference between high-resource and low-resource languages | Baseline: ~20-30% gap; Target: ≤10% gap |
| Base model architecture | Controlled | XLM-R or similar multilingual encoder backbone | Fixed across conditions |
| Training compute budget | Controlled | GPU hours and batch size | Fixed across conditions |
| Evaluation benchmarks | Controlled | CSRT, LinguaSafe, SGToxicGuard | Held constant |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Linguistically-Principled Code-Switching Generation
    ↓ (generates diverse but semantically equivalent training data)
Step 2: Contrastive Learning on Code-Switched Variants
    ↓ (forces language-invariant embeddings via semantic equivalence constraint)
Step 3: Language-Invariant Safety Representations
    ↓ (enables cross-lingual safety transfer)
Outcome: Improved Cross-Lingual Safety Generalization
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Smaglii et al. (2025) | Code-switching follows predictable patterns serving pragmatic functions | Strong |
| Step1 → Step2 | CSRT (Yoo et al., 2024) | Automated code-switching generation is tractable; 46.7% more attacks | Strong |
| Step2 → Step3 | Shen et al. (2024) | Cross-lingual alignment bottleneck needs representation-level changes | Strong |
| Step3 → Outcome | CSRT inverse | Training on attack patterns should create robustness | Medium |

**Key Tension:**
- **Tension:** Shen et al. (2024) suggests bottleneck is in *pretraining*, not fine-tuning. Our approach focuses on *fine-tuning*.
- **Resolution:** We target safety alignment specifically, not general multilingual capability. Contrastive learning creates safety-specific language-invariant representations. Phase 2B will test whether fine-tuning intervention is sufficient.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|--------------------|-----------------------|
| A1 | Code-switching patterns can be automatically generated with sufficient linguistic validity | Smaglii et al. (2025); CSRT automated generation | Generated data noisy; contrastive learning fails |
| A2 | Contrastive learning on diverse surface forms produces language-invariant representations | Standard contrastive learning theory; XLM-R alignment | Embeddings remain language-specific |
| A3 | Safety is semantic/intent-level, separable from surface form | CSRT shows same intent elicits different responses | Cultural safety norms differ fundamentally |
| A4 | XLM-R provides adequate cross-lingual base representations | XLM-R cross-lingual transfer on NLU tasks | Need different backbone architecture |

### 1.5 Scope & Boundaries

**Applies to:**
- Text-based LLM safety alignment
- Languages with adequate tokenizer coverage in XLM-R
- Cross-culturally consistent safety categories (explicit harm, violence, illegal activities)
- Code-switching between the 5 target language pairs

**Does NOT apply to:**
- Speech/audio safety
- Languages without adequate tokenizer coverage
- Culturally-specific safety norms
- Multimodal safety

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Attack Success Rate Reduction):**
Models trained with CSASA will achieve ASR on code-switched prompts ≥30% lower than English-only trained models.

*Measurement:* CSRT benchmark ASR; two-proportion z-test, n ≥ 500; p < 0.05
*Success:* ASR(CSASA) ≤ 0.7 × ASR(English-only)

**Secondary Predictions:**

**P2 (Low-Resource Safety):**
CSASA achieves ≥40% higher safety F1 on low-resource languages vs English-only.

**P3 (Principled vs Random):**
Linguistically-principled code-switching outperforms random by ≥15%.

**Falsification Criteria:**

1. **Primary Failure:** ASR reduction < 15%
2. **Mechanism Failure:** Embeddings remain language-specific
3. **Comparative Failure:** Principled ≤ random code-switching
4. **Trade-off Failure:** False refusal rate increases >10%

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 500 test cases per condition
**Tests:** Two-proportion z-test (P1), paired t-test (P2), independent t-test (P3)
**Significance:** α = 0.05
**Power:** 0.80

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does linguistically-principled code-switching augmentation during safety training reduce attack success rate on code-switched prompts?"
- Maps to: Primary prediction P1
- Verification: Empirical comparison
- Critical: MUST PASS

**SH2 (Mechanism):**
"Is the 3-step mechanism the actual cause of improved cross-lingual safety?"

Decomposes to 3 sub-hypotheses (H-M1 to H-M3):
- H-M1: Code-switching generation produces valid, semantically equivalent variants
- H-M2: Contrastive training produces language-invariant safety embeddings
- H-M3: Language-invariant embeddings improve safety on unseen languages

**SH3 (Comparison):**
"Does linguistically-principled code-switching outperform alternatives?"
- Maps to: P3
- Verification: Comparative empirical

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-CSASA-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism: N=3 steps with evidence
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions (primary marked)
- [x] 4 falsification criteria
- [x] Baselines: English-only, random code-switching
- [x] SH1, SH2, SH3 defined

### Open Questions

1. **Resource Requirements:** Estimate 4-8 GPU days on A100 for contrastive encoder training
2. **Data Availability:** May need to generate multilingual safety preference pairs
3. **Evaluation Infrastructure:** Need native speaker validation subset
4. **Priority Order:** Start with SH1 (existence) before mechanism (SH2)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*2026-02-13*
