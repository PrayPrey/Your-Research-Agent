# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SHAM-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under conditions of diverse adversarial attack patterns (including novel attacks unseen during training), if LLM safety guardrails employ Semantic Harm Affinity Maturation (SHAM) architecture combining contrastive semantic harm encoding with evolutionary affinity maturation, then the benchmark-to-novel attack detection gap will reduce from >50% to <30% because semantic encoding captures harm intent rather than surface patterns, and evolutionary boundary expansion enables recognition of novel attack variants sharing semantic similarity with known attacks.

**Alternative Hypothesis (H0):**
SHAM architecture provides no significant improvement in benchmark-to-novel generalization gap compared to traditional classifier-based guardrails; any observed improvement is attributable to increased model capacity, additional training data, or random variation rather than the proposed semantic encoding and affinity maturation mechanisms.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Guardrail Architecture | Independent | SHAM (semantic encoding + affinity maturation) vs. traditional classifier-based guardrails (Qwen3Guard, LlamaGuard, Granite-Guardian) | Binary: SHAM vs. Baseline |
| Training Methodology | Independent | Evolutionary affinity maturation with fitness-based selection vs. standard supervised fine-tuning | Binary: Evolutionary vs. Standard |
| Benchmark-to-Novel Gap | Dependent | Percentage point difference between accuracy on public benchmark prompts and accuracy on novel/unseen attack prompts | 0-100 pp; Target: <30 pp |
| Novel Attack Detection Accuracy | Dependent | Percentage of novel adversarial prompts correctly classified as harmful (true positive rate on unseen attacks) | 0-100%; Target: >60% |
| Semantic Clustering Purity | Dependent | Purity score (0-1) measuring how well attacks with same harmful intent cluster together in embedding space | 0-1; Target: >0.7 |
| False Positive Rate | Dependent | Percentage of benign prompts incorrectly classified as harmful | 0-100%; Target: <baseline + 5% |
| Base LLM Model | Controlled | Fixed to specific model (e.g., Llama-3.1-8B) across all experiments | Fixed |
| Attack Categories | Controlled | 21 attack categories from Young (2025) evaluation framework | Fixed: 21 categories |
| Evaluation Metrics | Controlled | Accuracy, precision, recall, F1, gap calculation methodology from Young (2025) | Standardized |
| Computational Budget | Controlled | Fixed at <4 GPU-hours on A100-equivalent for affinity maturation | <4 GPU-hours |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Contrastive Learning → Semantic Harm Embedding
    ↓
Step 2: Semantic Clustering → Surface-Invariant Recognition
    ↓
Step 3: Evolutionary Affinity Maturation → Boundary Expansion
    ↓
Step 4: Dual-Layer Detection → Reduced Generalization Gap
    ↓
Outcome: Benchmark-to-Novel Gap < 30%
```

**Step 1: Contrastive Learning → Semantic Harm Embedding**
- Mechanism: Train contrastive encoder (InfoNCE loss) on attack-intent pairs where positive pairs share harmful intent but differ in surface expression
- Evidence: SimCLR and CLIP demonstrate contrastive learning creates meaningful semantic embeddings; RoboGuard's semantic understanding achieves <2.5% unsafe execution
- Falsification: If clustering purity <0.5 on held-out attacks, semantic encoding assumption is invalid

**Step 2: Semantic Clustering → Surface-Invariant Recognition**
- Mechanism: Attacks with same harmful intent cluster together regardless of typos, ciphers, paraphrasing
- Evidence: Wei et al. (2023) "mismatched generalization" shows safety fails on semantically equivalent inputs, implying intent is separable from surface
- Falsification: If surface mutations (typos, ciphers) bypass detection at same rate as baselines

**Step 3: Evolutionary Affinity Maturation → Boundary Expansion**
- Mechanism: Evolutionary optimization (CMA-ES or genetic algorithm) on classifier boundaries using held-out attack variants as fitness signal
- Evidence: TextFooler/BERT-Attack validate evolutionary optimization in NLP; RAILS achieves 5-12% robustness improvement using immune-inspired approach
- Falsification: If optimization produces degenerate solutions or requires >10x computational budget

**Step 4: Dual-Layer Detection → Reduced Generalization Gap**
- Mechanism: Combine fast semantic similarity (innate) with evolved classifiers (adaptive) for final decision
- Evidence: Young (2025) shows Granite-Guardian achieves 6.5% gap through better generalization; trained immunity literature shows dual-layer defense is more robust
- Falsification: If combined system achieves gap >40% (only modest improvement)

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | RoboGuard (2025), SimCLR | Semantic understanding enables safer behavior; contrastive clustering works for conceptual similarity | Strong |
| Step2 → Step3 | Wei et al. (2023), Wang et al. (2024) | Mismatched generalization proves intent/surface separability; innate-adaptive synergy in immunity | Medium |
| Step3 → Step4 | RAILS (2021), TextFooler | 5-12% robustness improvement; evolutionary optimization effective in NLP | Medium |
| Step4 → Outcome | Young (2025), Granite-Guardian | 6.5% gap achievable; dual-layer approach has theoretical grounding | Medium |

**Key Tension:**
- **Tension:** Young (2025) shows semantic understanding alone (Granite-Guardian) achieves 6.5% gap, while RAILS achieved only 5-12% improvement on simpler image tasks. It's unclear whether SHAM's combination will provide additive or synergistic benefits in the more complex LLM domain.
- **Resolution:** The pilot study (Phase 2B SH1) will test semantic encoding on text classification first. If clustering purity >0.7 achieved, proceed to full SHAM. The staged approach allows early detection of domain transfer failure.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|--------------------|-----------------------|
| A1 | Harmful intent can be represented in a learnable semantic embedding space distinct from surface-level patterns | Wei et al. (2023) mismatched generalization; RoboGuard semantic understanding | Core hypothesis fails; must pivot to alternative approaches (e.g., ensemble methods, data augmentation) |
| A2 | Adversarial attacks with same intent share detectable semantic features regardless of surface expression | Contrastive learning success in vision/language (CLIP); harm taxonomy consistency | Semantic encoder ineffective; would need explicit intent annotation or different clustering approach |
| A3 | Evolutionary optimization can meaningfully expand boundaries in high-dimensional embedding space | TextFooler/BERT-Attack evolutionary search; RAILS 5-12% improvement | Affinity maturation component fails; could fall back to semantic encoding only |
| A4 | Contrastive learning on attack-intent pairs produces separable harm category clusters | SimCLR/MoCo success on conceptual similarity | Dual-layer architecture degrades to single classifier; reduced but possible benefit |
| A5 | Computational cost of maturation (<4 GPU-hours) is sufficient for meaningful boundary expansion | RAILS achieved improvements in similar budget | May need larger budget or more efficient algorithms; increases deployment barrier |

### 1.5 Scope & Boundaries

**Where Hypothesis APPLIES:**
- Text-based adversarial attacks on LLM guardrails
- Prompt injection attacks
- Jailbreaking attempts (role-playing, hypothetical scenarios, veiled language)
- Surface variation attacks (typos, ciphers, paraphrasing, encoding)
- High-stakes deployment contexts (healthcare, finance, legal)

**Where Hypothesis Does NOT Apply:**
- Multimodal attacks involving images, audio, or video
- Model extraction or membership inference attacks
- Training data poisoning attacks
- Attacks exploiting entirely novel harm categories not represented in training
- Real-time systems requiring <10ms latency (evolutionary maturation adds overhead)

**Known Limitations:**
1. Cannot create new semantic harm categories - only expands boundaries of known intent clusters
2. May miss attacks exploiting semantic ambiguity where harm is context-dependent
3. Requires diverse attack training data for effective contrastive learning
4. Computational overhead of dual-layer system may impact inference latency

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Benchmark-to-Novel Gap vs SOTA 57.2% ± ~15%)**:
SHAM architecture will achieve benchmark-to-novel detection gap < 30 percentage points on the Young (2025) evaluation framework.

*Measurement*:
- Gap = |Accuracy_benchmark - Accuracy_novel| < 30 pp with p < 0.05
- Statistical test: Paired t-test across 21 attack categories, n ≥ 25 runs

*Basis*:
SOTA Qwen3Guard achieves 57.2% gap; Granite-Guardian achieves 6.5% gap.
Our target (<30% gap) represents meaningful improvement over worst performers while being more conservative than best-in-class.

*Success Criteria for Phase 2B*:
- Primary: Gap < 30 pp (p < 0.05)
- Falsification: Gap ≥ 45 pp triggers rejection (only marginal improvement over baseline)

**Secondary Predictions:**

**P2 (Semantic Clustering Quality)**:
Contrastive semantic harm encoder will achieve clustering purity > 0.7 and silhouette score > 0.3 on held-out attack variants, demonstrating that harmful intent is captured in embedding space.

**P3 (False Positive Rate Preservation)**:
SHAM will maintain false positive rate within 5 percentage points of baseline guardrails on benign prompts.

**P4 (Evolutionary Improvement)**:
Affinity maturation will improve novel attack detection by >10 percentage points over semantic encoding alone.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: Benchmark-to-novel gap ≥ 45 pp
2. **Mechanism Failure (Semantic)**: Clustering purity < 0.5
3. **Mechanism Failure (Evolutionary)**: Affinity maturation improvement < 5 pp over semantic-only baseline
4. **Selectivity Failure**: False positive rate > baseline + 10%
5. **Efficiency Failure**: Affinity maturation requires > 20 GPU-hours (5x budget)

### 1.7 SOTA Baseline (SOTA Comparison Mode)

| Method | Overall Accuracy | Benchmark Acc | Novel Acc | Gap | Year |
|--------|-----------------|---------------|-----------|-----|------|
| Qwen3Guard-8B | 85.3% | 91.0% | 33.8% | 57.2 pp | 2025 |
| Granite-Guardian-3.2-5B | ~75% | ~78% | ~71% | 6.5 pp | 2025 |

**Target:** Accuracy comparable to Qwen3Guard (~85%) with gap comparable to Granite-Guardian (<30 pp)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 25 runs per condition
**Statistical Test:** Paired t-test (SHAM vs. baseline on same attack set)
**Significance Level:** α = 0.05 (one-tailed)
**Effect Size:** Cohen's d ~0.8 expected
**Report Format:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does semantic harm encoding produce meaningful clusters where attacks with same harmful intent group together regardless of surface variation?"
- Maps to: Primary prediction P2 (clustering purity)
- Verification type: Empirical pilot study on text classification
- Critical: MUST PASS before proceeding to full SHAM implementation

**SH2 (Mechanism):**
"Is the proposed 4-step causal chain (contrastive encoding → semantic clustering → affinity maturation → dual-layer detection) the actual mechanism producing improved generalization?"
- Maps to: Causal mechanism (N=4 steps → H-M1 through H-M4)
- Verification type: Ablation studies isolating each component
- Expected sub-hypotheses: 4 (one per causal step)

**SH3 (Comparison):**
"Does SHAM outperform baseline guardrails (Qwen3Guard, Granite-Guardian) on the benchmark-to-novel generalization gap metric?"
- Maps to: Primary prediction P1
- Verification type: Comparative empirical study

**Total Sub-Hypotheses for Phase 2B:** 2 + 4 = 6

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-SHAM-v1
- [x] Confidence level: 0.80
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with N=4 steps, evidence table complete
- [x] Key tension identified with resolution
- [x] Key assumptions with consequences
- [x] 4 testable predictions (primary marked)
- [x] 5 falsification criteria defined
- [x] Baselines identified (Qwen3Guard, Granite-Guardian)
- [x] SH1, SH2, SH3 clear

**Status:** ALL PASSED ✓

### Open Questions

1. **Data Availability:** What attack datasets can be used for contrastive training? Are public datasets with harm-intent annotations available?

2. **Computational Feasibility:** Can evolutionary affinity maturation converge within 4 GPU-hour budget on realistic-scale embeddings?

3. **Verification Priority:** Should SH1 (existence/pilot) complete before SH2 work begins, or can some mechanism experiments run in parallel?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
